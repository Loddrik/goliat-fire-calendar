"""Protocol23: frozen-policy context weighting; no destination-based selection."""
import argparse
import json
import math
import platform
from datetime import datetime,timezone
from pathlib import Path

import numpy as np
import pandas as pd

from scientific_audit import ROOT,DATA,TRAIN,AuditData,sha
from cold_region_audit import (REGIMES,FEATURES,KEYS,fixed_panel,fit_source,raw_predictions,
                               predict_all as baseline_predict,fingerprint)
from context_cdf_model import ContextCDF,FACTORS,cdf_equal
from coherent_allocation import reconcile,means,expected_risk,kkt_residual
from frozen_temporal_audit import publication_metadata

OUT=DATA/'context_cdf_audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-15-science-protocol-23.md'
DEADLINE=datetime(2026,11,15,11,30,tzinfo=timezone.utc)
SCENARIOS=(('PRIMARY_2010_alltypes',2010,'alltypes'),('SECONDARY_2001_alltypes',2001,'alltypes'),('SECONDARY_2010_type0',2010,'type0'))
METHODS=('M1','B','PARENT21',*FACTORS,'C00_mean','C11_mean','C00_coherent','C11_coherent','C00_proportional','C11_proportional','PARENT21_coherent')
SOURCE21=DATA/'cold_region_audit';SOURCE22=DATA/'landcover_context_audit'
CODE=[ROOT/'pipeline'/n for n in ['context_cdf_model.py','context_cdf_audit.py','cold_region_audit.py','hurdle_model.py','coherent_allocation.py','scientific_audit.py','affine_experiment.py']]
CODE += [ROOT/'tests'/n for n in ['test_context_cdf_model.py','test_context_cdf_audit.py']]


def deadline_check():
    if datetime.now(timezone.utc)>=DEADLINE:raise TimeoutError('Authorized23 deadline reached')


def inputs():
    return [PROTOCOL,ROOT/'docs/reviews/2026-11-14-science-protocol-21.md',ROOT/'docs/reviews/2026-11-15-science-protocol-22.md',
      *[SOURCE21/n for n in ['models.json','predictions.parquet','candidate_mask.csv','manifest.json']],
      *[SOURCE22/n for n in ['features.csv','class_areas.csv','summary.json','manifest.json']],
      *[DATA/n for n in ['detections.parquet','celldays.parquet','cells_comuna.parquet']]]


def freeze_code():
    deadline_check();OUT.mkdir(parents=True,exist_ok=True)
    record={'status':'code-and-inputs-frozen-before-new23-metrics','frozen_utc':datetime.now(timezone.utc).isoformat(),
      'deadline_utc':DEADLINE.isoformat(),'code_sha256':{str(p.relative_to(ROOT)):sha(p) for p in CODE},
      'input_sha256':{str(p.relative_to(ROOT)):sha(p) for p in inputs()},'scenarios':list(SCENARIOS),'alpha':.5,'bandwidth':.25,'kappa':10}
    (OUT/'code-freeze.json').write_text(json.dumps(record,indent=2)+'\n');print('Code/input freeze complete:',sha(OUT/'code-freeze.json'),flush=True)
    return record


def validate_freeze():
    record=json.loads((OUT/'code-freeze.json').read_text())
    for group in ['code_sha256','input_sha256']:
        for name,digest in record[group].items():
            if sha(ROOT/name)!=digest:raise ValueError('Frozen23 code/input changed: '+name)
    return record


def protected_snapshot():
    paths=[p for p in DATA.rglob('*') if p.is_file() and OUT not in p.parents]
    paths += list((ROOT/'web/public/data').rglob('*.json'))+list((ROOT/'observed/dist/data/publication').glob('*.json'))
    return {str(p.relative_to(ROOT)):sha(p) for p in paths}


def contexts_for_year(year,features=None,classes=None):
    features=pd.read_csv(SOURCE22/'features.csv',dtype={'cut':str}) if features is None else features.copy()
    classes=pd.read_csv(SOURCE22/'class_areas.csv',dtype={'cut':str,'class_code':str}) if classes is None else classes.copy()
    condition=lambda f:(f.year==year)&(f.geography=='legacy')&(f.policy=='retained')
    f=features[condition(features)];c=classes[condition(classes)];result={}
    if len(f)!=54 or f.cut.nunique()!=54:raise ValueError('Frozen22 context domain incomplete')
    for row in f.itertuples():
        values=c[c.cut==row.cut].set_index('class_code')
        if len(values)!=18 or set(values.index)!={*map(str,range(1,18)),'unknown'}:raise ValueError('Frozen22 composition incomplete')
        if not isinstance(row.context_available,(bool,np.bool_)):raise ValueError('Invalid frozen availability flag')
        if not hasattr(row,'layout_valid') or not bool(row.layout_valid):raise ValueError('Frozen22 layout validity missing/false')
        result[str(row.cut)]={'available':bool(row.context_available),'vector':[float(values.loc[str(k),'fraction_total']) for k in range(1,18)]+[float(values.loc['unknown','fraction_total'])]}
    # Validate including roundoff before any model query.
    from context_cdf_model import composition
    for row in result.values():composition(row['vector'],row['available'])
    return result


def load_type0_panel(data,mask):
    data.con.register('context23_mask',pd.DataFrame(sorted(mask),columns=['cell_x','cell_y']).astype('int64'))
    data.con.execute("""create or replace temp view context23_type0_days as
      select d.sat,c.cut,d.cell_x,d.cell_y,d.acq_date,
      case when month(d.acq_date)>=7 then year(d.acq_date) else year(d.acq_date)-1 end season,month(d.acq_date) m
      from det d join read_parquet('"""+str(DATA/'cells_comuna.parquet')+"""') c using(cell_x,cell_y)
      where d.sat in ('Aqua','SNPP') and d.type=0 and d.acq_date>=date '2012-07-01' and d.acq_date<date '2020-07-01'
      and not exists(select 1 from context23_mask z where z.cell_x=d.cell_x and z.cell_y=d.cell_y)
      group by 1,2,3,4,5,6,7""")
    counts=data.con.execute("""select cut,season,m,count(*) filter(where sat='Aqua') aqua,
        count(*) filter(where sat='SNPP') snpp from context23_type0_days group by 1,2,3""").df()
    grid=pd.MultiIndex.from_product([data.cuts,TRAIN,range(1,13)],names=KEYS).to_frame(index=False)
    x=grid.merge(counts,on=KEYS,how='left',validate='one_to_one').fillna({'aqua':0,'snpp':0})
    x[['aqua','snpp']]=x[['aqua','snpp']].astype('int64');x['g']=x.m.map(lambda m:'JJA' if m in (6,7,8) else str(m))
    return x


def infer(features,model,contexts,cuts):
    deadline_check();base,old_dist,parent_dist=raw_predictions(features,model)
    context=ContextCDF(model['hurdle'],contexts);x,d0,d1=context.predict(features)
    x['M1']=base.M1;x['B']=base.B;x['PARENT21']=base.E00
    x['C00_mean']=means(d0);x['C11_mean']=means(d1)
    if not np.allclose(x.C00,base.E11,rtol=0,atol=1e-10) or not np.allclose(x.C00_mean,base.E11_mean,rtol=0,atol=1e-10):raise ValueError('Uniform C00 point/mean does not reproduce base21')
    for a,b in zip(d0,old_dist):
        if not cdf_equal(a,b,1e-12):raise ValueError('Uniform C00 full CDF does not reproduce base21')
    for name in ['C00_coherent','C11_coherent','PARENT21_coherent','C00_proportional','C11_proportional']:x[name]=np.nan
    checks=[]
    for key,group in x.groupby(['season','m'],sort=True):
        deadline_check()
        if len(group)!=54 or len(cuts)!=54 or set(group.cut)!=set(cuts):raise ValueError('Context allocation requires exact54 CUT domain')
        ix=group.index.to_numpy();b=group.B.to_numpy(dtype=float);total=math.fsum(b)
        for name,distributions in [('C00_coherent',d0),('C11_coherent',d1),('PARENT21_coherent',parent_dist)]:
            ds=[distributions[i] for i in ix];a=reconcile(ds,b);rb,ra=expected_risk(ds,b),expected_risk(ds,a);kkt=kkt_residual(ds,a);error=math.fsum(a)-total
            if abs(error)>1e-10*max(1,total) or ra>rb+1e-8*max(1,rb) or kkt>1e-8:raise ValueError('Context allocation budget/risk/KKT gate failed')
            x.loc[ix,name]=a;checks.append(dict(season=int(key[0]),m=int(key[1]),method=name,budget=total,budget_error=error,baseline_expected_risk=rb,allocated_expected_risk=ra,kkt_residual=kkt))
        for method in ['C00','C11']:
            med=group[method].to_numpy(dtype=float);a=med*(total/math.fsum(med)) if math.fsum(med) else b.copy()
            if abs(math.fsum(a)-total)>1e-10*max(1,total):raise ValueError('Context proportional budget gate failed')
            x.loc[ix,method+'_proportional']=a
    if not np.isfinite(x[list(METHODS)+['p0','p1']].to_numpy()).all() or (x[list(METHODS)]<0).any().any():raise ValueError('Invalid context decisions')
    return x,checks,context.diagnostics


def verify_original21(actual,old):
    a=actual.sort_values(KEYS).reset_index(drop=True);b=old.sort_values(KEYS).reset_index(drop=True)
    if a.duplicated(KEYS).any() or not a[KEYS].equals(b[KEYS]):raise ValueError('Original21 control keys changed')
    columns={'aqua':'aqua','M1':'M1','B':'B','PARENT21':'E00','C00':'E11','C00_mean':'E11_mean','C00_coherent':'E11_coherent','PARENT21_coherent':'E00_coherent','C00_proportional':'E11_proportional'}
    for left,right in columns.items():
        if not np.allclose(a[left],b[right],rtol=0,atol=1e-10):raise ValueError('Original21 frozen control changed: '+left)
    return True


def metrics(frame):
    result={'n':len(frame),'target_sum':float(frame.snpp.sum()),'methods':{}}
    for method in METHODS:
        error=frame[method]-frame.snpp;totals=frame.groupby(['season','m'])[[method,'snpp']].sum()
        result['methods'][method]={'mae':float(error.abs().mean()) if len(frame) else None,'mse':float((error*error).mean()) if len(frame) else None,'bias':float(error.mean()) if len(frame) else None,'prediction_sum':float(frame[method].sum()),'absolute_error_sum':float(error.abs().sum()),'regional_monthly_mae':float((totals[method]-totals.snpp).abs().mean()) if len(totals) else None}
    result['probability_product_Brier']={name:float(((frame[name]-(frame.snpp>0).astype(float))**2).mean()) if len(frame) else None for name in ['p0','p1']}
    losses={m:result['methods'][m]['mae'] for m in FACTORS}
    result['factorial']=None if not len(frame) else {'delta_P':losses['C10']-losses['C00'],'delta_F':losses['C01']-losses['C00'],'interaction':losses['C11']-losses['C10']-losses['C01']+losses['C00'],'joint':losses['C11']-losses['C00']}
    return result


def report(frame,source,enabled):
    groups={'all54':frame,'SOURCE':frame[frame.cut.isin(source)],'held':frame[~frame.cut.isin(source)],'published14':frame[frame.cut.isin(enabled)],'remaining40':frame[~frame.cut.isin(enabled)]}
    for role,selected in [('SOURCE',frame.cut.isin(source)),('held',~frame.cut.isin(source))]:
        for name,selected2 in [('published14',frame.cut.isin(enabled)),('remaining40',~frame.cut.isin(enabled))]:groups[role+'_'+name]=frame[selected&selected2]
    return {name:{label:metrics(g) for label,g in {'all_months':x,'active':x[x.snpp>0],'zero':x[x.snpp==0],'aqua_zero_snpp_positive':x[(x.aqua==0)&(x.snpp>0)],'both_observed_zero':x[(x.aqua==0)&(x.snpp==0)],'50_plus':x[x.snpp>=50]}.items()} for name,x in groups.items()}


def model_for(panel,unit,source,origin,frozen):
    return (json.loads(json.dumps(frozen)),None) if unit=='alltypes' else fit_source(panel,source,origin)


def check_invariance(panel,unit,source,origin,features,model,contexts,cuts,actual,frozen):
    allowed=panel.cut.isin(source)&panel.season.isin(origin);proof={}
    for label,value in [('removed',np.nan),('changed',1234567.)]:
        altered=panel.copy();altered.loc[~allowed,'snpp']=value
        candidate,_=model_for(altered,unit,source,origin,frozen)
        if fingerprint(candidate)!=fingerprint(model):raise ValueError('Forbidden labels changed baseline coefficients/choices/CDF')
        predicted,_,_=infer(features,candidate,contexts,cuts)
        if not np.array_equal(predicted[list(METHODS)+['p0','p1']].to_numpy(),actual[list(METHODS)+['p0','p1']].to_numpy()):raise ValueError('Forbidden labels changed54 context predictions')
        proof[label]={'model_identical':True,'all54_predictions_identical':True}
    return proof


def primary_summary(rows):
    average00=float(np.mean([r['C00_mae'] for r in rows]));average11=float(np.mean([r['C11_mae'] for r in rows]));n=sum(r['n'] for r in rows)
    return {'regimes':rows,'equal_four_regime_MAE_C00':average00,'equal_four_regime_MAE_C11':average11,
      'equal_four_regime_delta_mae':average11-average00,'row_weighted_delta_mae':sum(r['absolute_error_delta'] for r in rows)/n,
      'relative_gain_from_equal_MAE':(average00-average11)/average00 if average00 else None,
      'exceeds_one_percent_working_margin':bool(average00 and (average00-average11)/average00>.01),
      'working_margin_is_not_NASA_or_significance':True,'total_held_rows':n,'regimes_not_independent':True}


def run():
    deadline_check();frozen_code=validate_freeze();before=protected_snapshot()
    original_models=json.loads((SOURCE21/'models.json').read_text());original_predictions=pd.read_parquet(SOURCE21/'predictions.parquet')
    metadata21=json.loads((SOURCE21/'manifest.json').read_text());metadata22=json.loads((SOURCE22/'manifest.json').read_text())
    for directory,manifest in [(SOURCE21,metadata21),(SOURCE22,metadata22)]:
        for name,digest in manifest['output_sha256'].items():
            if sha(directory/name)!=digest:raise ValueError('Frozen21/22 output hash changed')
    mask_frame=pd.read_csv(SOURCE21/'candidate_mask.csv');mask={tuple(map(int,row)) for row in mask_frame[['cell_x','cell_y']].to_numpy()}
    if len(mask)!=6:raise ValueError('Frozen6 mask changed')
    data=AuditData();panels={'alltypes':fixed_panel(data,mask),'type0':load_type0_panel(data,mask)};cuts=data.cuts;enabled,_=publication_metadata(cuts)
    a=panels['alltypes'].sort_values(KEYS);t=panels['type0'].sort_values(KEYS)
    if not a[KEYS].reset_index(drop=True).equals(t[KEYS].reset_index(drop=True)) or (t[['aqua','snpp']].to_numpy()>a[['aqua','snpp']].to_numpy()).any():raise ValueError('Type0 response/features not subsets of alltypes on identical keys')
    contexts={year:contexts_for_year(year) for year in [2010,2001]}
    predictions=[];allocation_checks=[];diagnostics=[];proofs={};used_models={};type0_inner=[];control_checks=[]
    for scenario,year,unit in SCENARIOS:
        for regime,(region,origin,dest) in REGIMES.items():
            deadline_check();panel=panels[unit];source=[c for c in cuts if c.startswith(region)];frozen=original_models[regime]
            if set(frozen['source_cuts'])!=set(source) or set(frozen['origin_seasons'])!=set(origin):raise ValueError('Frozen regime/source domains changed')
            model,inner=model_for(panel,unit,source,origin,frozen)
            features=panel.loc[panel.season.isin(dest),FEATURES].copy().reset_index(drop=True)
            x,checks,diags=infer(features,model,contexts[year],cuts)
            if unit=='alltypes':verify_original21(x,original_predictions[original_predictions.regime==regime])
            else:
                old,_=baseline_predict(features,model,cuts);verify_original21(x,old)
                type0_inner.append(inner.assign(regime=regime))
            control_checks.append({'scenario':scenario,'regime':regime,'uniform_CDF_and_points_reproduced':True,'original21_controls_reproduced':unit=='alltypes','unit_own_uniform_base_reproduced':True})
            proofs[scenario+'/'+regime]=check_invariance(panel,unit,source,origin,features,model,contexts[year],cuts,x,frozen)
            x=x.merge(panel[KEYS+['snpp']],on=KEYS,how='left',validate='one_to_one')
            if unit=='alltypes':
                old=original_predictions[original_predictions.regime==regime]
                if not np.array_equal(x.sort_values(KEYS).snpp.to_numpy(),old.sort_values(KEYS).snpp.to_numpy()):raise ValueError('Original21 target key/unit alignment changed')
            x['scenario']=scenario;x['regime']=regime;x['role']=np.where(x.cut.isin(source),'SOURCE','held')
            predictions.append(x);allocation_checks += [dict(scenario=scenario,regime=regime,**r) for r in checks]
            diagnostics += [dict(scenario=scenario,regime=regime,**r) for r in diags]
            used_models[scenario+'/'+regime]=model
            print('Context scenario inferred and uniform-controlled:',scenario,regime,flush=True)
    # No new destination metric is calculated before ALL control/invariance gates.
    combined=pd.concat(predictions,ignore_index=True);reports={};primary={}
    for scenario,year,unit in SCENARIOS:
        rows=[];reports[scenario]={}
        for regime,(region,origin,dest) in REGIMES.items():
            x=combined[(combined.scenario==scenario)&(combined.regime==regime)];source=[c for c in cuts if c.startswith(region)]
            result=report(x,source,enabled);reports[scenario][regime]=result
            held=result['held']['all_months'];m=held['methods']
            rows.append({'regime':regime,'n':held['n'],'C00_mae':m['C00']['mae'],'C11_mae':m['C11']['mae'],'delta_mae':m['C11']['mae']-m['C00']['mae'],'absolute_error_delta':m['C11']['absolute_error_sum']-m['C00']['absolute_error_sum'],'factorial':held['factorial']})
        primary[scenario]=primary_summary(rows)
    summary={'status':'retrospective-context-CDF-experiment','independent_validation':False,'physical_or_ecological_truth_validated':False,'asof2012_claim':False,
      'primary_scenario':SCENARIOS[0][0],'no_scenario_or_hyperparameter_selection':True,'alpha':.5,'Hellinger_bandwidth':.25,'kappa':10,
      'kernel_positive_is_not_statistical_support':True,'ESS_are_weight_diagnostics_not_posterior_or_independence':True,
      'primary_definition':'held C11 minus C00 before coherence; equal weight four regimes','primary_and_predeclared_sensitivities':primary,
      'type0_filters_both_Aqua_and_SNPP_before_cell_day_dedup':True,'type0_base_source_only_policy':'existing4lambda OOF policy and kappa10; no target retune',
      'all_uniform_controls_reproduced':True,'all_forbidden_label_invariances_passed':True,'regional_total_equality_to_B_is_constructed':True,
      'control_checks':control_checks,'invariance':proofs,'reports':reports}
    if before!=protected_snapshot():raise ValueError('Protected sources/publication/prior results changed')
    validate_freeze()
    OUT.mkdir(parents=True,exist_ok=True);combined.to_parquet(OUT/'predictions.parquet',index=False)
    pd.DataFrame(allocation_checks).to_csv(OUT/'allocation_checks.csv',index=False)
    pd.concat(type0_inner,ignore_index=True).to_parquet(OUT/'type0_source_inner_predictions.parquet',index=False)
    for name,obj in [('models_used.json',used_models),('contexts_used.json',contexts),('context_diagnostics.json',diagnostics),('summary.json',summary)]:
        (OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
    rows=[dict(scenario=k,**r) for k,v in primary.items() for r in v['regimes']]
    pd.DataFrame(rows).drop(columns='factorial').to_csv(OUT/'held_primary_contrasts.csv',index=False)
    manifest={'code_freeze_sha256':sha(OUT/'code-freeze.json'),'code_sha256':frozen_code['code_sha256'],'input_sha256':frozen_code['input_sha256'],
      'protected_sha256':before,'all_previous_artifacts_unchanged':True,'model_semantic_signatures':{k:fingerprint(v) for k,v in used_models.items()},
      'environment':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__},'output_sha256':{p.name:sha(p) for p in OUT.glob('*') if p.name!='manifest.json'}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n');print('Context CDF audit complete:',OUT,flush=True)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['freeze','run']);args=parser.parse_args()
    freeze_code() if args.action=='freeze' else run()
