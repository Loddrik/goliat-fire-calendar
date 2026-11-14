"""Protocol 11: fit on 2012–19 once; descriptive future discrepancy and bands."""
import calendar
import hashlib
import json
import re
import subprocess
from datetime import date,timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from scientific_audit import ROOT,DATA,TRAIN,AuditData,fit_models,predict,score,sha,band_metrics
from affine_experiment import fit_affine,predict_affine
from robust_affine_experiment import fit_huber,predict_huber,choose as choose_huber,check_deadline
from piecewise_experiment import fit_piecewise,predict_piecewise,choose as choose_piecewise
from temporal_transport_audit import apply_choices,METHODS
from platform_bridge_audit import requested_days,season_dates

OUT=DATA/'frozen_temporal_audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-14-science-protocol-11.md'
BAND_POLICIES=('M1','M1_B','M1_H','M1_P','M1_B_P')
KEYS=['cut','season','m']


def join_oof(piecewise,huber):
    for frame in [piecewise,huber]:
        if frame.duplicated(KEYS).any():raise ValueError('Duplicated OOF keys')
    a=piecewise.sort_values(KEYS).reset_index(drop=True)
    b=huber.sort_values(KEYS).reset_index(drop=True)
    if not a[KEYS].equals(b[KEYS]):raise ValueError('Mismatched OOF keys')
    for col in ['aqua','snpp','M1','M1_B']:
        equal=np.array_equal(a[col],b[col]) if col in ['aqua','snpp'] else np.allclose(a[col],b[col],atol=1e-10,rtol=0,equal_nan=False)
        if not equal:raise ValueError('Mismatched OOF control '+col)
    for col in [c for c in b if c.startswith('H_d') or c in ['M1_H','M1_H_chosen']]:
        a[col]=b[col].to_numpy()
    return a


def calibrate_radii(oof):
    records=[]
    for cut,g in oof.groupby('cut'):
        active=g[g.snpp>0]
        for policy in BAND_POLICIES:
            errors=(active[policy]-active.snpp).abs()
            records.append({'cut':cut,'policy':policy,'n_active_calibration':len(errors),
                'abs80_radius':float(errors.quantile(.8)) if len(errors) else np.nan,
                'active_mae':float(errors.mean()) if len(errors) else np.nan})
    return pd.DataFrame(records)


def freeze(training,oof):
    if set(training.season)!=set(TRAIN) or set(oof.season)!=set(TRAIN):raise ValueError('Frozen fit/selection must use exactly 2012–2019')
    if training.duplicated(KEYS).any() or oof.duplicated(KEYS).any():raise ValueError('Duplicated training/OOF keys')
    if not training[KEYS].sort_values(KEYS).reset_index(drop=True).equals(oof[KEYS].sort_values(KEYS).reset_index(drop=True)):
        raise ValueError('Training and OOF grids differ')
    columns=[c for c in oof if c.startswith(('A_','B_','H_d','P_')) or c in BAND_POLICIES]
    if not np.isfinite(oof[columns].to_numpy()).all():raise ValueError('Nonfinite OOF candidate predictions')
    reference=fit_models(training);affine=fit_affine(training,reference)
    huber,numerics=fit_huber(training,affine);piecewise=fit_piecewise(training,affine)
    choices,loss=choose_piecewise(oof);hchoices,hloss=choose_huber(oof)
    choices['M1_H']=hchoices['M1_H'];selection=[]
    for policy,mapping in choices.items():
        table=hloss if policy=='M1_H' else loss
        for cut,candidate in mapping.items():
            selection.append({'cut':cut,'policy':policy,'candidate':candidate,'oof_mae':float(table.loc[cut,candidate])})
    return {'reference':reference,'affine':affine,'huber':huber,'piecewise':piecewise,
            'choices':choices,'selection':pd.DataFrame(selection),'radii':calibrate_radii(oof),'numerics':numerics}


def signature(model):
    digest=hashlib.sha256()
    digest.update(json.dumps({'ratio':model['reference']['ratio'],'choices':model['choices']},sort_keys=True,allow_nan=False).encode())
    for name in ['regional','local','climatology']:
        digest.update(name.encode()+model['reference'][name].sort_index().to_csv().encode())
    for name in ['affine','huber','piecewise','radii','selection']:
        digest.update(name.encode()+model[name].sort_index().to_csv().encode())
    return digest.hexdigest()


def estimate(frame,model):
    x=predict_piecewise(predict_huber(predict_affine(predict(frame,model['reference']),model['affine']),model['huber']),model['piecewise'])
    x=apply_choices(x,model['choices'])
    for policy in BAND_POLICIES:
        radii=model['radii'][model['radii'].policy==policy].set_index('cut').abs80_radius
        x[policy+'_abs80_radius']=x.cut.map(radii)
    return x


def calendar_labels(frame):
    if not set(frame.season)<=set(range(2020,2026)) or not frame.m.between(1,12).all():raise ValueError('Invalid destination calendar')
    x=frame.copy();x['y']=np.where(x.m>=7,x.season,x.season+1)
    x['block']=np.where(x.season<=2021,'legacy_2020_2021','diagnostic_2022_2025')
    x['orbit_epoch']=np.where(x.y<2022,'before_calendar_2022','calendar_2022_onward')
    return x[~((x.y==2020)&x.m.isin([8,9]))].copy()


def requested_modis_days(paths):
    days=set()
    for path in paths:
        if '/firms_country/modis/' in path:
            match=re.search(r'modis_(\d{4})_Chile\.csv$',path)
            if match:
                year=int(match[1]);start=date(year,1,1)
                days.update(start+timedelta(days=n) for n in range(366 if calendar.isleap(year) else 365))
        if '/MODIS_SP/' in path:
            match=re.search(r'_(\d{4}-\d{2}-\d{2})_(\d+)d\.csv$',path)
            if not match:raise ValueError('Unrecognized MODIS SP inventory path')
            start=date.fromisoformat(match[1]);days.update(start+timedelta(days=n) for n in range(int(match[2])))
    return days


def future_monthly(data):
    mask=data.fit_mask(TRAIN)
    data.con.register('frozen_mask',pd.DataFrame(sorted(mask),columns=['cell_x','cell_y']).astype('int64'))
    counts=data.con.execute("""select cut,season,m,count(*) filter(sat='Aqua') aqua,
        count(*) filter(sat='SNPP') snpp,count(*) filter(any_nrt) provisional_cell_days
        from days d where season between 2020 and 2025 and sat in ('Aqua','SNPP')
        and not exists(select 1 from frozen_mask s where s.cell_x=d.cell_x and s.cell_y=d.cell_y)
        group by 1,2,3""").df()
    grid=pd.MultiIndex.from_product([data.cuts,range(2020,2026),range(1,13)],names=KEYS).to_frame(index=False)
    frame=grid.merge(counts,on=KEYS,how='left',validate='one_to_one').fillna({'aqua':0,'snpp':0,'provisional_cell_days':0})
    frame[['aqua','snpp','provisional_cell_days']]=frame[['aqua','snpp','provisional_cell_days']].astype('int64')
    frame['g']=frame.m.map(lambda m:'JJA' if m in (6,7,8) else str(m))
    if frame.provisional_cell_days.sum():raise ValueError('Unexpected NRT in complete diagnostic panel')
    result=calendar_labels(frame)
    if len(result)!=3780:raise ValueError('Unexpected diagnostic panel size')
    return result


def metrics(frame,regional=True):
    baseline=float((frame.M1-frame.snpp).abs().mean()) if len(frame) else None
    report={}
    for method in METHODS:
        error=frame[method]-frame.snpp
        record={'n':len(frame),'mae':float(error.abs().mean()) if len(frame) else None,
                'bias':float(error.mean()) if len(frame) else None,'absolute_error_sum':float(error.abs().sum()),
                'improvement_pct_vs_M1':float((1-error.abs().mean()/baseline)*100) if baseline and baseline>0 else None}
        if regional:
            totals=frame.groupby(['y','m'])[[method,'snpp']].sum()
            record['regional_monthly_mae']=float((totals[method]-totals.snpp).abs().mean()) if len(totals) else None
        report[method]=record
    return report


def verify_legacy_controls(frame,previous):
    methods=['M0','M1','M2'];records=[]
    for cut,g in frame.groupby('cut'):
        for method in methods:
            error=g[method]-g.snpp
            records.append({'cut':cut,'method':method,'mae':float(error.abs().mean()),
                'bias':float(error.mean()),'n':len(g),'aqua_sum':float(g.aqua.sum())})
    actual=pd.DataFrame(records).set_index(['cut','method']).sort_index()
    expected=previous[previous.method.isin(methods)].set_index(['cut','method']).sort_index()
    if not actual.index.equals(expected.index) or not np.allclose(actual,expected[actual.columns],atol=1e-10,rtol=0):
        raise ValueError('Legacy published controls do not reproduce')


def publication_metadata(cuts):
    enabled=[];radii={}
    for cut in cuts:
        doc=json.loads((ROOT/'web/public/data/comunas'/f'{cut}.json').read_text())
        value=float(doc['gates']['band_mae'])
        if not np.isfinite(value) or value<0:raise ValueError('Invalid published radius')
        radii[cut]=value
        if doc['reconstruction_enabled']:enabled.append(cut)
    if len(enabled)!=14:raise ValueError('Published subgroup changed; do not silently replace')
    return enabled,radii


def bands(frame,enabled):
    result={}
    for policy in BAND_POLICIES:
        result[policy+'_nested_abs80']={label:band_metrics(frame.assign(M1=frame[policy]),policy+'_abs80_radius',cuts)
                                      for label,cuts in [('all54',None),('published14',enabled)]}
    result['M1_published_rounded_typical_error']={'published14':band_metrics(frame.assign(M1=frame.M1.map(lambda v:round(float(v),1))),'published_mae_radius',enabled)}
    return result


def write_frozen(model):
    OUT.mkdir(parents=True,exist_ok=True)
    files=[]
    for name in ['regional','local','climatology']:
        p=OUT/('reference_'+name+'.csv');model['reference'][name].to_csv(p);files.append(p)
    for name in ['affine','huber','piecewise','radii','selection']:
        p=OUT/('frozen_'+name+'.csv');model[name].to_csv(p,index=name in ['affine','huber','piecewise']);files.append(p)
    frozen={'training_seasons':list(TRAIN),'r_const':model['reference']['ratio'],'choices':model['choices'],
            'signature':signature(model),'artifacts_sha256':{p.name:sha(p) for p in files},'huber_numerics':model['numerics']}
    (OUT/'frozen_model.json').write_text(json.dumps(frozen,indent=2,allow_nan=False)+'\n')
    print('Model frozen before destination query:',frozen['signature'],flush=True)


def run():
    check_deadline()
    protected=sorted((ROOT/'web/public/data').rglob('*.json'))
    protected += [DATA/f for f in ['detections.parquet','celldays.parquet','static_mask.parquet','params.json','gates.csv','eval_loso.csv','eval_final.csv','inventory.csv']]
    for directory in ['scientific_audit','affine_audit','robust_affine_audit','piecewise_audit','geography_audit','platform_bridge_audit','temporal_transport_audit','conaf_external_audit','training_size_audit']:
        protected+=sorted((DATA/directory).glob('*'))
    before={str(p.relative_to(ROOT)):sha(p) for p in protected}
    data=AuditData()
    if data.fit_mask(TRAIN)!=data.published_mask:raise ValueError('Full mask does not reproduce published cells')
    training=data.monthly('fold_fitted',TRAIN)
    oof=join_oof(pd.read_csv(DATA/'piecewise_audit/outer_predictions.csv',dtype={'cut':str}),
                 pd.read_csv(DATA/'robust_affine_audit/outer_predictions.csv',dtype={'cut':str}))
    if len(oof)!=5184:raise ValueError('OOF grid mismatch')
    model=freeze(training,oof)
    published=json.loads((DATA/'params.json').read_text())['r_const']
    if abs(model['reference']['ratio']-published)>1e-12:raise ValueError('Published M1 factor not reproduced')
    fingerprint=signature(model);write_frozen(model)
    paths=pd.read_csv(DATA/'inventory.csv').path
    snpp_days=requested_days(paths,'SNPP');modis_days=requested_modis_days(paths)
    if any(not season_dates(s)<=snpp_days or not season_dates(s)<=modis_days for s in range(2020,2026)):
        raise ValueError('Incomplete requested SP product windows')
    frame=future_monthly(data);x=estimate(frame,model)
    enabled,published_radii=publication_metadata(data.cuts);x['published_mae_radius']=x.cut.map(published_radii)
    periods={name:g.copy() for name,g in x.groupby('block')}
    legacy=x[x.block=='legacy_2020_2021']
    verify_legacy_controls(legacy,pd.read_csv(DATA/'eval_final.csv',dtype={'cut':str}))
    periods['legacy_before_calendar_2022']=legacy[legacy.y<2022]
    periods['legacy_jan_jun_2022']=legacy[legacy.y==2022]
    reports={};coverage=[]
    for period,g in periods.items():
        reports[period]={'metrics':{label:metrics(g if cuts is None else g[g.cut.isin(cuts)]) for label,cuts in [('all54',None),('published14',enabled)]},
            'bands':bands(g,enabled),'subgroups':{label:metrics(pop,False) for label,pop in {
                'both_observed_zero':g[(g.aqua==0)&(g.snpp==0)],'aqua_zero_viirs_positive':g[(g.aqua==0)&(g.snpp>0)],'viirs_50_plus':g[g.snpp>=50]}.items()}}
        for cut,h in g.groupby('cut'):
            for label,populations in bands(h,[cut] if cut in enabled else []).items():
                population=populations.get('published14') if label=='M1_published_rounded_typical_error' else populations['all54']
                if label=='M1_published_rounded_typical_error' and cut not in enabled:continue
                for state,values in population.items():coverage.append(dict(period=period,cut=cut,band=label,population=state,**values))
    if signature(model)!=fingerprint:raise ValueError('Frozen model changed during destination evaluation')
    check_deadline()
    if before!={str(p.relative_to(ROOT)):sha(p) for p in protected}:raise ValueError('Protected production/previous data changed')
    selected_cols=['cut','season','y','m','g','aqua','snpp','provisional_cell_days','block','orbit_epoch',*METHODS,
                   *[p+'_chosen' for p in model['choices']],*[p+'_abs80_radius' for p in BAND_POLICIES],'published_mae_radius']
    x[selected_cols].to_parquet(OUT/'predictions.parquet',index=False,compression='zstd')
    score(x,METHODS).to_csv(OUT/'scores.csv',index=False)
    season_scores=pd.DataFrame([dict(season=int(s),method=m,**v) for s,g in x.groupby('season') for m,v in metrics(g).items()])
    season_scores.to_csv(OUT/'season_aggregates.csv',index=False)
    pd.DataFrame(coverage).to_csv(OUT/'commune_band_coverage.csv',index=False)
    summary={'status':'frozen-fit-descriptive-temporal-audit','independent_validation':False,'published_factor_reproduced':True,'legacy_controls_reproduced':True,
        'model_signature_unchanged_after_evaluation':True,'signature':fingerprint,'published14':enabled,
        'n_pairs':len(x),'requested_product_windows_complete':True,'observation_coverage_known':False,
        'provisional_cell_days':0,'periods':reports,'choice_counts':{p:pd.Series(c).value_counts().astype(int).to_dict() for p,c in model['choices'].items()}}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    helpers=['scientific_audit.py','affine_experiment.py','robust_affine_experiment.py','piecewise_experiment.py','temporal_transport_audit.py','platform_bridge_audit.py']
    manifest={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'protocol_sha256':sha(PROTOCOL),'code_sha256':sha(Path(__file__)),
        'helpers_sha256':{f:sha(ROOT/'pipeline'/f) for f in helpers},'environment_sha256':{f:sha(ROOT/f) for f in ['pyproject.toml','uv.lock']},
        'protected_sha256':before,'production_and_previous_unchanged':True,
        'output_sha256':{p.name:sha(p) for p in sorted(OUT.glob('*')) if p.name!='manifest.json'}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n')
    print('Frozen temporal audit complete:',OUT,flush=True)
    return summary


if __name__=='__main__':run()
