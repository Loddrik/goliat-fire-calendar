"""Protocol 15: minimize clipped interval loss in original units, fixed points."""
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from scientific_audit import ROOT,DATA,TRAIN,AuditData,sha
from robust_affine_experiment import check_deadline
from temporal_transport_audit import fit_predict
from affine_experiment import candidate_values
from frozen_temporal_audit import KEYS,join_oof,load_frozen,signature,publication_metadata
from scaled_band_audit import outer_fold,scale,interval_loss
from asymmetric_band_audit import calibrate as empirical_calibrate,population_metrics as base_metrics

OUT=DATA/'interval_loss_fit_audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-14-science-protocol-15.md'
POLICIES=('M1','M1_B')
TOLERANCE=1e-12


def risk(point,y,ql,qu):
    s=scale(point,.5)
    return float(interval_loss(y,np.maximum(0,np.asarray(point)+s*ql),np.maximum(0,np.asarray(point)+s*qu)).mean())


def fit_extremes(point,y):
    point=np.asarray(point,dtype=float);y=np.asarray(y,dtype=float)
    if len(y)==0 or point.shape!=y.shape or not np.isfinite(y).all() or (y<0).any():raise ValueError('Invalid endpoint calibration')
    s=scale(point,.5);knots=np.unique(np.r_[(y-point)/s,-point/s,0.])
    bounds=np.maximum(0,point[:,None]+s[:,None]*knots[None,:])
    lower_cost=(-bounds+10*np.maximum(bounds-y[:,None],0)).mean(axis=0)
    upper_cost=(bounds+10*np.maximum(y[:,None]-bounds,0)).mean(axis=0)
    minimum=float(np.min(np.minimum.accumulate(lower_cost)+upper_cost))
    # Prefix minima give the optimum value. This scan implements the declared
    # lexicographic tie rule among all pairs within the absolute tolerance.
    selected=None
    for i in range(len(knots)):
        candidates=np.flatnonzero(lower_cost[i]+upper_cost[i:]<=minimum+TOLERANCE)
        if len(candidates):selected=(i,i+int(candidates[0]));break
    if selected is None:raise ValueError('No ordered endpoint optimum')
    ql,qu=map(float,knots[list(selected)])
    actual=risk(point,y,ql,qu)
    if ql>qu or abs(actual-minimum)>1e-9:raise ValueError('Endpoint objective reconstruction failed')
    return ql,qu,{'knots':len(knots),'calibration_is':actual,'grid_minimum':minimum}


def calibrate(frame):
    original=empirical_calibrate(frame);records=[]
    for row in original.to_dict('records'):
        cut,policy,cohort=row['cut'],row['policy'],row['calibration_cohort']
        g=frame[frame.cut==cut];source=g[g.snpp>0] if cohort=='active' else g
        if row['shape']=='symmetric':
            if cohort=='active':
                row.update(fit_mode='symmetric_active_reference',optimizer_knots=0,
                    calibration_is=risk(source[policy],source.snpp,row['q_lower'],row['q_upper']) if len(source) else np.nan)
                records.append(row)
            continue
        empirical=dict(row,fit_mode='empirical_quantiles',optimizer_knots=0,
            calibration_is=risk(source[policy],source.snpp,row['q_lower'],row['q_upper']) if len(source) else np.nan)
        records.append(empirical);optimal=dict(row,fit_mode='minimum_interval_score',optimizer_knots=0,calibration_is=np.nan)
        if len(source):
            ql,qu,diagnostic=fit_extremes(source[policy],source.snpp)
            optimal.update(q_lower=ql,q_upper=qu,optimizer_knots=diagnostic['knots'],calibration_is=diagnostic['calibration_is'])
            if optimal['calibration_is']>empirical['calibration_is']+1e-9:raise ValueError('Fitted interval loses to empirical interval in calibration')
        records.append(optimal)
    return pd.DataFrame(records)


def apply_intervals(frame,calibration):
    keys=['cut','policy','calibration_cohort','fit_mode']
    if frame.duplicated(KEYS).any() or calibration.duplicated(keys).any():raise ValueError('Duplicate interval keys')
    records=[];metadata=[c for c in ['cut','season','m','y','block','orbit_epoch','aqua','snpp'] if c in frame]
    for (policy,cohort,mode),group in calibration.groupby(['policy','calibration_cohort','fit_mode']):
        c=group.set_index('cut')
        if not set(frame.cut)<=set(c.index):raise ValueError('Missing endpoint calibration')
        point=frame[policy].to_numpy(dtype=float);s=scale(point,.5)
        ql=frame.cut.map(c.q_lower).to_numpy();qu=frame.cut.map(c.q_upper).to_numpy()
        if np.isinf(ql).any() or np.isinf(qu).any() or (ql>qu).any():raise ValueError('Invalid ordered endpoints')
        x=frame[metadata].copy();x['policy']=policy;x['calibration_cohort']=cohort;x['fit_mode']=mode
        x['shape']='symmetric' if mode=='symmetric_active_reference' else 'asymmetric';x['point']=point
        x['n_calibration']=frame.cut.map(c.n_calibration).to_numpy()
        x['lower']=np.maximum(0,point+s*ql);x['upper']=np.maximum(0,point+s*qu)
        x['interval_score']=interval_loss(x.snpp,x.lower,x.upper) if 'snpp' in x else np.nan;records.append(x)
    return pd.concat(records,ignore_index=True)


def nested_fold(data,held,fit=fit_predict):
    inner=[]
    def capture(data,allowed,destination):
        if held in allowed:raise ValueError('External season entered endpoint fit')
        frame,params=fit(data,allowed,destination)
        if tuple(destination)!=(held,):inner.append(frame.copy())
        return frame,params
    point,_,_,calls,_=outer_fold(data,held,fit=capture);raw=pd.concat(inner,ignore_index=True)
    if set(raw.season)!=set(TRAIN)-{held}:raise ValueError('Endpoint calibration crossed external boundary')
    mapping=point.groupby('cut').M1_B_chosen.first().to_dict()
    selected=raw[[*KEYS,'aqua','snpp','M1']].copy();selected['M1_B']=candidate_values(raw,mapping)
    parameters=calibrate(selected)
    return apply_intervals(point,parameters),parameters,calls


def verify_controls(actual,previous):
    controls=actual[actual.fit_mode.isin(['empirical_quantiles','symmetric_active_reference'])]
    index=[*KEYS,'policy','calibration_cohort','shape']
    previous=previous[(previous['shape']=='asymmetric')|((previous['shape']=='symmetric')&(previous.calibration_cohort=='active'))]
    a=controls.sort_values(index).reset_index(drop=True);b=previous.sort_values(index).reset_index(drop=True)
    if not a[index].equals(b[index]):raise ValueError('Endpoint control keys differ')
    for c in ['point','lower','upper']:
        if not np.allclose(a[c],b[c],atol=1e-10,rtol=0,equal_nan=True):raise ValueError('Endpoint control differs '+c)


def population_metrics(frame,enabled,period):
    return pd.concat([base_metrics(g,enabled,period).assign(fit_mode=mode) for mode,g in frame.groupby('fit_mode')],ignore_index=True)


def contrasts(frame):
    records=[]
    for policy,g in frame.groupby('policy'):
        for cohort in ['active','all_months']:
            for population,pop in [('all_months',g),('active_months',g[g.snpp>0])]:
                selected=pop[(pop.calibration_cohort==cohort)&(pop.fit_mode!='symmetric_active_reference')]
                wide=selected.pivot(index=KEYS,columns='fit_mode',values='interval_score').dropna()
                delta=wide.minimum_interval_score-wide.empirical_quantiles;blocks=delta.groupby(level='season').mean()
                if set(blocks.index)!=set(TRAIN):raise ValueError('Missing endpoint contrast season')
                records.append({'policy':policy,'calibration_cohort':cohort,'population':population,'blocks':len(blocks),
                    'paired_rows':len(wide),'mean_season_delta_interval_score':float(blocks.mean()),'seasons_better':int((blocks<0).sum()),
                    'per_season_delta':{str(k):float(v) for k,v in blocks.items()}})
    return records


def run():
    check_deadline()
    protected=sorted((ROOT/'web/public/data').rglob('*.json'))
    protected+=[DATA/f for f in ['detections.parquet','celldays.parquet','static_mask.parquet','params.json','gates.csv','eval_loso.csv','eval_final.csv','inventory.csv']]
    for directory in ['scientific_audit','affine_audit','robust_affine_audit','piecewise_audit','geography_audit','platform_bridge_audit','temporal_transport_audit','conaf_external_audit','training_size_audit','frozen_temporal_audit','scaled_band_audit','asymmetric_band_audit','terra_feature_audit']:
        protected+=sorted((DATA/directory).glob('*'))
    before={str(p.relative_to(ROOT)):sha(p) for p in protected};data=AuditData();intervals=[];parameters=[];fits=[]
    for held in TRAIN:
        x,cal,calls=nested_fold(data,held);intervals.append(x);parameters.append(cal.assign(outer_held=held));fits.extend(calls)
        print('Loss-fit outer fold complete:',held,flush=True)
    historical=pd.concat(intervals,ignore_index=True);verify_controls(historical,pd.read_parquet(DATA/'asymmetric_band_audit/nested_intervals.parquet'))
    oof=join_oof(pd.read_csv(DATA/'piecewise_audit/outer_predictions.csv',dtype={'cut':str}),pd.read_csv(DATA/'robust_affine_audit/outer_predictions.csv',dtype={'cut':str}))
    final=calibrate(oof);model=load_frozen();fingerprint=signature(model)
    OUT.mkdir(parents=True,exist_ok=True);final.to_csv(OUT/'frozen_calibration.csv',index=False)
    (OUT/'frozen_band_config.json').write_text(json.dumps({'power':.5,'alpha':.2,'source_point_model_signature':fingerprint,'tolerance':TOLERANCE,
        'parameters_sha256':sha(OUT/'frozen_calibration.csv')},indent=2,allow_nan=False)+'\n');print('Fitted endpoints frozen before destination read',flush=True)
    future_points=pd.read_parquet(DATA/'frozen_temporal_audit/predictions.parquet');future=apply_intervals(future_points,final)
    verify_controls(future,pd.read_parquet(DATA/'asymmetric_band_audit/later_intervals.parquet'))
    enabled,_=publication_metadata(data.cuts);tables=[population_metrics(historical,enabled,'nested_2012_2019')]
    for season,g in historical.groupby('season'):tables.append(population_metrics(g,enabled,'season_'+str(season)))
    for block,g in future.groupby('block'):tables.append(population_metrics(g,enabled,block))
    legacy=future[future.block=='legacy_2020_2021'];tables.append(population_metrics(legacy[legacy.y<2022],enabled,'legacy_before_calendar_2022'));tables.append(population_metrics(legacy[legacy.y==2022],enabled,'legacy_jan_jun_2022'))
    metrics=pd.concat(tables,ignore_index=True)
    if len(historical)!=51840 or len(future)!=37800:raise ValueError('Endpoint grids incomplete')
    if signature(model)!=fingerprint:raise ValueError('Point model changed during endpoint fitting')
    check_deadline()
    if before!={str(p.relative_to(ROOT)):sha(p) for p in protected}:raise ValueError('Protected files changed')
    historical.to_parquet(OUT/'nested_intervals.parquet',index=False,compression='zstd');future.to_parquet(OUT/'later_intervals.parquet',index=False,compression='zstd')
    pd.concat(parameters,ignore_index=True).to_csv(OUT/'fold_calibration.csv',index=False);pd.DataFrame(fits).to_csv(OUT/'fit_seasons.csv',index=False);metrics.to_csv(OUT/'metrics.csv',index=False)
    summary={'status':'retrospective-original-unit-interval-loss-fit','independent_validation':False,'controls_reproduced':True,
        'source_point_model_signature':fingerprint,'fit_calls':len(fits),'nested_rows':len(historical),'later_rows':len(future),
        'contrasts':contrasts(historical),'metrics':json.loads(metrics[metrics.period.isin(['nested_2012_2019','legacy_2020_2021','diagnostic_2022_2025'])].to_json(orient='records',double_precision=15))}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    helpers=['scientific_audit.py','affine_experiment.py','robust_affine_experiment.py','piecewise_experiment.py','temporal_transport_audit.py','frozen_temporal_audit.py','scaled_band_audit.py','asymmetric_band_audit.py']
    manifest={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'protocol_sha256':sha(PROTOCOL),'code_sha256':sha(Path(__file__)),
        'helpers_sha256':{f:sha(ROOT/'pipeline'/f) for f in helpers},'environment_sha256':{f:sha(ROOT/f) for f in ['pyproject.toml','uv.lock']},
        'protected_sha256':before,'production_and_previous_unchanged':True,'output_sha256':{p.name:sha(p) for p in sorted(OUT.glob('*')) if p.name!='manifest.json'}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n');print('Interval-loss fit audit complete:',OUT,flush=True)
    return summary


if __name__=='__main__':run()
