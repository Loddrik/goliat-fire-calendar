"""Protocol21: source-only calibration transported across region and period.

Recorded S-NPP counts are responses; no observation opportunity or fire truth.
No labels from an uncalibrated CUT, or any destination season, enter fitting.
"""
import hashlib
import json
import math
import platform
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from scientific_audit import ROOT, DATA, TRAIN, AuditData, fit_models, sha
from affine_experiment import LAMBDAS, b_name, fit_affine, predict_affine
from hurdle_model import fit_hurdle, predict_hurdle, _components
from coherent_allocation import reconcile, expected_risk, kkt_residual, means
from frozen_temporal_audit import KEYS, publication_metadata
from robust_affine_experiment import check_deadline

OUT=DATA/'cold_region_audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-14-science-protocol-21.md'
METHODS=('M1','B','E00','E11','E11_mean','E11_coherent','E00_coherent','E11_proportional')
FEATURES=KEYS+['g','aqua']
REGIMES={f'{region}_{direction}':(region,origin,dest) for region in ('08','16')
         for direction,origin,dest in [('forward',(2012,2013,2014,2015),(2016,2017,2018,2019)),
                                       ('backward',(2016,2017,2018,2019),(2012,2013,2014,2015))]}


def fingerprint(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def mask_from_stats(stats):
    core={}
    for r in stats.itertuples(index=False):
        key=(int(r.cell_x),int(r.cell_y))
        if r.n_days>=30 and r.n_seasons>=8:core[key]=('A',int(r.n_days))
        elif r.n_days>=10 and pd.notna(r.p1) and r.p1>=.5:core[key]=('B',int(r.n_days))
        elif r.n_days>=15 and pd.notna(r.p2) and r.p2>=.6:core[key]=('C',int(r.n_days))
    mask=set(core)
    for (x,y),(rule,days) in core.items():
        radius=2 if rule=='B' else 1 if rule=='A' and days>=100 else 0
        mask.update((x+dx,y+dy) for dx in range(-radius,radius+1) for dy in range(-radius,radius+1))
    return mask


def build_mask(con):
    predicate="sat in ('Terra','Aqua') and acq_date < date '2012-01-01'"
    stats=con.execute(f"""select cell_x,cell_y,count(distinct acq_date) n_days,
      count(distinct case when month(acq_date)>=7 then year(acq_date) else year(acq_date)-1 end) n_seasons,
      avg(case when type is not null then (type=1)::int end) p1,
      avg(case when type is not null then (type=2)::int end) p2
      from det where {predicate} group by 1,2""").df()
    provenance=con.execute(f"select sat,count(*) n,min(acq_date) min_date,max(acq_date) max_date from det where {predicate} group by 1").df()
    return mask_from_stats(stats),stats,provenance


def fixed_panel(data,mask):
    data.con.register('cold_mask',pd.DataFrame(sorted(mask),columns=['cell_x','cell_y']).astype('int64'))
    counts=data.con.execute("""select cut,season,m,count(*) filter(where sat='Aqua') aqua,
       count(*) filter(where sat='SNPP') snpp from days d where season between 2012 and 2019
       and sat in ('Aqua','SNPP') and not exists(select 1 from cold_mask z where z.cell_x=d.cell_x and z.cell_y=d.cell_y)
       group by 1,2,3""").df()
    grid=pd.MultiIndex.from_product([data.cuts,TRAIN,range(1,13)],names=KEYS).to_frame(index=False)
    x=grid.merge(counts,on=KEYS,how='left',validate='one_to_one').fillna({'aqua':0,'snpp':0})
    x[['aqua','snpp']]=x[['aqua','snpp']].astype('int64')
    x['g']=x.m.map(lambda m:'JJA' if m in (6,7,8) else str(m))
    if len(x)!=5184 or x.duplicated(KEYS).any():raise ValueError('Incomplete fixed54 training-pool panel')
    return x


def training_only(panel,source_cuts,origin):
    if not set(origin)<=set(TRAIN) or len(origin)<2:raise ValueError('Invalid source years')
    x=panel.loc[panel.cut.isin(source_cuts)&panel.season.isin(origin),FEATURES+['snpp']].copy()
    if x.duplicated(KEYS).any() or set(x.cut)!=set(source_cuts) or set(x.season)!=set(origin):raise ValueError('Incomplete source calibration domain')
    if not np.isfinite(x[['aqua','snpp']].to_numpy()).all() or (x[['aqua','snpp']]<0).any().any():raise ValueError('Invalid SOURCE labels')
    expected=len(source_cuts)*len(origin)*12
    if len(x)!=expected or not all(set(g.m)==set(range(1,13)) for _,g in x.groupby(['cut','season'])):raise ValueError('Missing SOURCE month/group')
    return x


def affine_candidates(features,reference,params):
    x=features[FEATURES].copy();x['M1']=x.aqua*float(reference['ratio'])
    return predict_affine(x,params)


def fit_source(panel,source_cuts,origin):
    """The ONLY label read is a cut-and-year restricted training extraction."""
    check_deadline();tr=training_only(panel,source_cuts,origin)
    inner=[]
    for held in origin:
        train=tr[tr.season!=held];test=tr[tr.season==held]
        ref=fit_models(train);params=fit_affine(train,ref)
        prediction=affine_candidates(test[FEATURES],ref,params)
        prediction=prediction.merge(test[KEYS+['snpp']],on=KEYS,validate='one_to_one')
        prediction['inner_held']=int(held);inner.append(prediction)
    inner=pd.concat(inner,ignore_index=True)
    losses=pd.DataFrame({m:(inner[m]-inner.snpp).abs() for m in ['M1',*[b_name(l) for l in LAMBDAS]]})
    losses['cut']=inner.cut.to_numpy();losses=losses.groupby('cut').mean()
    choices={}
    for cut,row in losses.iterrows():
        lam=min(LAMBDAS,key=lambda l:(row[b_name(l)],-l));best=b_name(lam)
        choices[str(cut)]=best if row[best]<.99*row.M1 else 'M1'
    ref=fit_models(tr);params=fit_affine(tr,ref);hurdle=fit_hurdle(tr,ref)
    model={'schema_version':1,'source_cuts':sorted(map(str,source_cuts)),'origin_seasons':sorted(map(int,origin)),
           'global_ratio':float(ref['ratio']),'regional_ratio':{str(g):float(v) for g,v in ref['regional'].rR.items()},
           'affine':params.reset_index().to_dict('records'),'choices':choices,'hurdle':hurdle,
           'selection_loss':losses.reset_index().to_dict('records'),'affine_fit_count':len(origin)+1,'cdf_fit_count':1}
    fingerprint(model)
    return model,inner


def atom_distribution(model,cut,g,aqua,parent=False):
    pp,pl,pz,pw,lz,lw=_components(model['hurdle'],str(cut),str(g),int(aqua>0),10)
    p,z,w=(pp,pz,pw) if parent else (pl,lz,lw)
    if p==0:return np.array([0.]),np.array([1.])
    scale=1+float(aqua)*model['regional_ratio'][str(g)]
    return np.r_[0.,np.maximum(1.,scale*z)],np.r_[1-p,p*w/w.sum()]


def raw_predictions(features,model):
    if set(features)!=set(FEATURES):raise ValueError('Inference accepts FEATURES only, never target labels')
    if features.duplicated(KEYS).any():raise ValueError('Duplicate prediction keys')
    if not set(features.g.astype(str))<=set(model['regional_ratio']):raise ValueError('Missing SOURCE calendar normalization')
    x=features[FEATURES].copy().reset_index(drop=True)
    x['M1']=x.aqua*model['global_ratio'];x['B']=x.M1
    source=x.cut.isin(model['source_cuts'])
    if source.any():
        params=pd.DataFrame(model['affine']).set_index(['cut','g'])
        candidates=predict_affine(x.loc[source,FEATURES+['M1']],params).set_index(KEYS)
        for i,row in x[source].iterrows():
            choice=model['choices'][str(row.cut)];x.loc[i,'B']=float(candidates.loc[tuple(row[KEYS]),choice])
    pred=predict_hurdle(x[FEATURES],model['hurdle'])
    x['E00']=pred.E00_10;x['E11']=pred.E11_10
    ds=[];parents=[]
    for row in x.itertuples():
        ds.append(atom_distribution(model,row.cut,row.g,row.aqua))
        parents.append(atom_distribution(model,row.cut,row.g,row.aqua,parent=True))
    x['E11_mean']=means(ds)
    held=~source
    if not np.array_equal(x.loc[held,'B'],x.loc[held,'M1']):raise ValueError('B held fallback is not M1')
    if not np.array_equal(x.loc[held,'E11'],x.loc[held,'E00']):raise ValueError('Held medians differ from parents')
    for i in x.index[held]:
        if not all(np.array_equal(a,b) for a,b in zip(ds[i],parents[i])):raise ValueError('Held full CDF differs from parent')
    return x,ds,parents


def predict_all(features,model,all_cuts):
    x,ds,parents=raw_predictions(features,model);checks=[]
    for method in ('E11_coherent','E00_coherent','E11_proportional'):x[method]=np.nan
    for key,group in x.groupby(['season','m'],sort=True):
        check_deadline()
        if len(group)!=54 or set(group.cut)!=set(all_cuts) or len(all_cuts)!=54:raise ValueError('Allocation requires exact fixed54 CUT set')
        ix=group.index.to_numpy();b=group.B.to_numpy(dtype=float);budget=math.fsum(b)
        for name,distributions in [('E11_coherent',ds),('E00_coherent',parents)]:
            dist=[distributions[i] for i in ix];a=reconcile(dist,b)
            rb,ra=expected_risk(dist,b),expected_risk(dist,a)
            kkt=kkt_residual(dist,a);err=math.fsum(a)-budget
            if abs(err)>1e-10*max(1,budget) or ra>rb+1e-8*max(1,rb) or kkt>1e-8:raise ValueError('Allocation risk/budget/KKT check failed')
            x.loc[ix,name]=a
            checks.append(dict(season=int(key[0]),m=int(key[1]),method=name,budget=budget,budget_error=err,baseline_expected_risk=rb,allocated_expected_risk=ra,kkt_residual=kkt))
        med=group.E11.to_numpy(dtype=float);a=med*(budget/math.fsum(med)) if math.fsum(med) else b.copy()
        if abs(math.fsum(a)-budget)>1e-10*max(1,budget):raise ValueError('Proportional budget mismatch')
        x.loc[ix,'E11_proportional']=a
    if not np.isfinite(x[list(METHODS)].to_numpy()).all() or (x[list(METHODS)]<0).any().any():raise ValueError('Invalid fixed predictions')
    return x,checks


def invariance(panel,source_cuts,origin,features,model,predictions,all_cuts):
    permitted=panel.cut.isin(source_cuts)&panel.season.isin(origin)
    result={}
    for label,value in [('removed',np.nan),('changed',1234567.)]:
        altered=panel.copy();altered.loc[~permitted,'snpp']=value
        changed,_=fit_source(altered,source_cuts,origin)
        if fingerprint(model)!=fingerprint(changed):raise ValueError('Forbidden labels changed fitted model/choices')
        predicted,_=predict_all(features.copy(),changed,all_cuts)
        if not np.array_equal(predicted[list(METHODS)].to_numpy(),predictions[list(METHODS)].to_numpy()):raise ValueError('Forbidden labels changed54 predictions')
        result[label]={'model_and_choices_identical':True,'all54_predictions_identical':True}
    return result


def metrics(frame):
    result={'n':len(frame),'target_sum':float(frame.snpp.sum()),'methods':{}}
    for method in METHODS:
        e=frame[method]-frame.snpp;totals=frame.groupby(['season','m'])[[method,'snpp']].sum()
        result['methods'][method]={'mae':float(e.abs().mean()) if len(e) else None,'mse':float((e*e).mean()) if len(e) else None,
          'bias':float(e.mean()) if len(e) else None,'prediction_sum':float(frame[method].sum()),
          'absolute_error_sum':float(e.abs().sum()),'regional_monthly_mae':float((totals[method]-totals.snpp).abs().mean()) if len(totals) else None}
    return result


def report(frame,source,enabled):
    groups={'all54':frame,'SOURCE':frame[frame.cut.isin(source)],'held':frame[~frame.cut.isin(source)],
            'published14':frame[frame.cut.isin(enabled)],'remaining40':frame[~frame.cut.isin(enabled)]}
    for role,selected in [('SOURCE',frame.cut.isin(source)),('held',~frame.cut.isin(source))]:
        groups[role+'_published14']=frame[selected&frame.cut.isin(enabled)]
        groups[role+'_remaining40']=frame[selected&~frame.cut.isin(enabled)]
    return {name:{label:metrics(g) for label,g in {'all_months':x,'active':x[x.snpp>0],'zero':x[x.snpp==0],
      'aqua_zero_snpp_positive':x[(x.aqua==0)&(x.snpp>0)],'both_observed_zero':x[(x.aqua==0)&(x.snpp==0)],'50_plus':x[x.snpp>=50]}.items()} for name,x in groups.items()}


def run():
    check_deadline()
    protected=[p for p in DATA.rglob('*') if p.is_file() and OUT not in p.parents]+list((ROOT/'web/public/data').rglob('*.json'))
    before={str(p.relative_to(ROOT)):sha(p) for p in protected}
    data=AuditData();mask,mask_stats,mask_provenance=build_mask(data.con)
    panel=fixed_panel(data,mask);cuts=sorted(panel.cut.unique());enabled,_=publication_metadata(cuts)
    if sum(c.startswith('08') for c in cuts)!=33 or sum(c.startswith('16') for c in cuts)!=21:raise ValueError('Fixed regional CUT domains changed')
    summaries={};models={};predictions=[];checks=[];inner=[];primary=[];proofs={}
    for label,(region,origin,dest) in REGIMES.items():
        check_deadline();source=[c for c in cuts if c.startswith(region)];held=set(cuts)-set(source)
        if set(origin)&set(dest) or set(source)&held:raise ValueError('Source/destination overlap')
        model,oof=fit_source(panel,source,origin)
        features=panel.loc[panel.season.isin(dest),FEATURES].copy().reset_index(drop=True)
        x,audit=predict_all(features,model,cuts)
        proof=invariance(panel,source,origin,features,model,x,cuts)
        x=x.merge(panel[KEYS+['snpp']],on=KEYS,how='left',validate='one_to_one')
        x['regime']=label;x['source_region']=region;x['role']=np.where(x.cut.isin(source),'SOURCE','held')
        r=report(x,source,enabled);s=r['held']['all_months'];m=s['methods']
        primary.append(dict(regime=label,n=s['n'],source_n=len(source),held_n=len(held),M1_mae=m['M1']['mae'],parent_mae=m['E00']['mae'],delta_mae=m['E00']['mae']-m['M1']['mae'],absolute_error_delta=m['E00']['absolute_error_sum']-m['M1']['absolute_error_sum']))
        summaries[label]=r;models[label]=model;proofs[label]=proof
        predictions.append(x);checks += [dict(regime=label,**row) for row in audit];inner.append(oof.assign(regime=label))
        print('Cold-region regime complete:',label,flush=True)
    total_n=sum(p['n'] for p in primary)
    summary={'status':'retrospective-cold-region-and-time-transport','independent_validation':False,'ecological_context_hypothesis_tested':False,
      'mask_policy':"Terra/Aqua only; UTC before2012-01-01; A/B/C and radii inherited",'mask_cells':len(mask),'mask_coordinate_sha256':fingerprint(sorted(mask)),
      'legacy_map_support_not_zero_information':True,'opportunity_of_observation_known':False,'source_only_affine_fits_per_regime':5,'source_only_cdf_fits_per_regime':1,
      'invariance_additional_refits_per_regime':2,'kappa':10,'lambda_grid':list(LAMBDAS),'new_hyperparameter_searches':0,
      'regional_equality_to_B_is_constructed_only_for_all54':True,'fallback_B_M1_held_exact':True,'fallback_E11_E00_held_full_CDF_exact':True,
      'primary':{'definition':'held ΔMAE E00 minus M1 before reconciliation','regimes':primary,
        'equal_four_regime_delta_mae':float(np.mean([p['delta_mae'] for p in primary])),
        'row_weighted_delta_mae':float(sum(p['absolute_error_delta'] for p in primary)/total_n),'total_held_rows':total_n,'regimes_are_not_independent_replicates':True},
      'invariance':proofs,'reports':summaries}
    if before!={str(p.relative_to(ROOT)):sha(p) for p in protected}:raise ValueError('Protected inputs/previous artifacts changed')
    OUT.mkdir(parents=True,exist_ok=True)
    pd.concat(predictions,ignore_index=True).to_parquet(OUT/'predictions.parquet',index=False)
    pd.concat(inner,ignore_index=True).to_parquet(OUT/'source_inner_predictions.parquet',index=False)
    pd.DataFrame(checks).to_csv(OUT/'allocation_checks.csv',index=False)
    pd.DataFrame(primary).to_csv(OUT/'primary_contrasts.csv',index=False)
    pd.DataFrame(sorted(mask),columns=['cell_x','cell_y']).to_csv(OUT/'candidate_mask.csv',index=False)
    mask_stats.to_csv(OUT/'candidate_mask_statistics.csv',index=False);mask_provenance.to_csv(OUT/'candidate_mask_provenance.csv',index=False)
    (OUT/'models.json').write_text(json.dumps(models,indent=2,allow_nan=False)+'\n')
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    code=[Path(__file__),ROOT/'pipeline/scientific_audit.py',ROOT/'pipeline/affine_experiment.py',ROOT/'pipeline/hurdle_model.py',ROOT/'pipeline/coherent_allocation.py']
    manifest={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'protocol_sha256':sha(PROTOCOL),
      'code_sha256':{str(p.relative_to(ROOT)):sha(p) for p in code},'protected_sha256':before,'all_previous_artifacts_unchanged':True,
      'model_sha256':{k:fingerprint(v) for k,v in models.items()},'environment':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__},
      'output_sha256':{p.name:sha(p) for p in OUT.glob('*') if p.name!='manifest.json'}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n')
    print('Cold-region audit complete:',OUT,flush=True)
    return summary


if __name__=='__main__':run()
