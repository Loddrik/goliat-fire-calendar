"""Protocol 13: factorial calibration population × interval shape, fixed points."""
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

OUT=DATA/'asymmetric_band_audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-14-science-protocol-13.md'
POLICIES=('M1','M1_B')
COHORTS=('active','all_months')
SHAPES=('symmetric','asymmetric')


def calibrate(frame):
    if not np.isfinite(frame[['snpp',*POLICIES]].to_numpy()).all() or (frame.snpp<0).any():raise ValueError('Invalid calibration inputs')
    records=[]
    for cut,g in frame.groupby('cut'):
        for policy in POLICIES:
            for cohort in COHORTS:
                source=g[g.snpp>0] if cohort=='active' else g
                residual=(source.snpp-source[policy]).to_numpy()/scale(source[policy],.5)
                for shape in SHAPES:
                    lo=hi=np.nan
                    if len(source):
                        if shape=='symmetric':hi=float(pd.Series(np.abs(residual)).quantile(.8));lo=-hi
                        else:lo,hi=[float(v) for v in pd.Series(residual).quantile([.1,.9])]
                    records.append({'cut':cut,'policy':policy,'calibration_cohort':cohort,'shape':shape,
                        'n_calibration':len(source),'n_total_origin':len(g),'n_active_origin':int((g.snpp>0).sum()),
                        'q_lower':lo,'q_upper':hi})
    return pd.DataFrame(records)


def apply_recipes(frame,calibration):
    index=['cut','policy','calibration_cohort','shape']
    if frame.duplicated(KEYS).any() or calibration.duplicated(index).any():raise ValueError('Duplicate interval records')
    result=[];metadata=[c for c in ['cut','season','m','y','block','orbit_epoch','aqua','snpp'] if c in frame]
    for policy in POLICIES:
        for cohort in COHORTS:
            for shape in SHAPES:
                c=calibration[(calibration.policy==policy)&(calibration.calibration_cohort==cohort)&(calibration['shape']==shape)].set_index('cut')
                if not set(frame.cut)<=set(c.index):raise ValueError('Missing commune calibration')
                point=frame[policy].to_numpy(dtype=float);s=scale(point,.5)
                qlo=frame.cut.map(c.q_lower).to_numpy();qhi=frame.cut.map(c.q_upper).to_numpy()
                if np.isinf(qlo).any() or np.isinf(qhi).any() or (qlo>qhi).any():raise ValueError('Invalid interval quantiles')
                x=frame[metadata].copy();x['policy']=policy;x['calibration_cohort']=cohort;x['shape']=shape
                x['point']=point;x['n_calibration']=frame.cut.map(c.n_calibration).to_numpy()
                x['lower']=np.maximum(0,point+qlo*s);x['upper']=np.maximum(0,point+qhi*s)
                x['interval_score']=interval_loss(x.snpp,x.lower,x.upper) if 'snpp' in x else np.nan
                result.append(x)
    return pd.concat(result,ignore_index=True)


def nested_fold(data,held,fit=fit_predict):
    inner=[]
    def capture(data,allowed,destination):
        if held in allowed:raise ValueError('External season entered captured fit')
        frame,params=fit(data,allowed,destination)
        if tuple(destination)!=(held,):inner.append(frame.copy())
        return frame,params
    point,_,_,calls,numerics=outer_fold(data,held,fit=capture)
    raw=pd.concat(inner,ignore_index=True)
    if set(raw.season)!=set(TRAIN)-{held}:raise ValueError('Calibration crossed external boundary')
    chosen=point.groupby('cut').M1_B_chosen
    if not chosen.nunique().eq(1).all():raise ValueError('Point policy changed within commune')
    selected=raw[[*KEYS,'aqua','snpp','M1']].copy()
    selected['M1_B']=candidate_values(raw,chosen.first().to_dict())
    cal=calibrate(selected)
    return apply_recipes(point,cal),cal,calls,numerics


def verify_control(actual,previous):
    for policy in POLICIES:
        a=actual[(actual.policy==policy)&(actual.calibration_cohort=='active')&(actual['shape']=='symmetric')].sort_values(KEYS).reset_index(drop=True)
        b=previous[(previous.policy==policy)&(previous.power==.5)].sort_values(KEYS).reset_index(drop=True)
        if not a[KEYS].equals(b[KEYS]):raise ValueError('Symmetric active control keys differ')
        for column in ['point','lower','upper']:
            if not np.allclose(a[column],b[column],atol=1e-10,rtol=0,equal_nan=True):raise ValueError('Symmetric active control differs '+column)


def statistics(frame):
    x=frame[np.isfinite(frame.interval_score)];width=x.upper-x.lower
    return {'n':len(frame),'n_scored':len(x),'missing_calibration':int(frame.lower.isna().sum()),
        'coverage':float(((x.snpp>=x.lower)&(x.snpp<=x.upper)).mean()) if len(x) else None,
        'mean_width':float(width.mean()) if len(x) else None,'mean_interval_score':float(x.interval_score.mean()) if len(x) else None,
        'below_fraction':float((x.snpp<x.lower).mean()) if len(x) else None,'above_fraction':float((x.snpp>x.upper).mean()) if len(x) else None,
        'zero_width_fraction':float((width==0).mean()) if len(x) else None,'positive_lower_fraction':float((x.lower>0).mean()) if len(x) else None,
        'point_outside_fraction':float(((x.point<x.lower)|(x.point>x.upper)).mean()) if len(x) else None}


def population_metrics(frame,enabled,period):
    rows=[]
    for (policy,calibration_cohort,shape),g in frame.groupby(['policy','calibration_cohort','shape']):
        for territory,cuts in [('all54',None),('published14',enabled)]:
            x=g if cuts is None else g[g.cut.isin(cuts)]
            populations={'all_months':x,'active_months':x[x.snpp>0],'zero':x[x.snpp==0],
                '1_to_9':x[(x.snpp>=1)&(x.snpp<10)],'10_to_49':x[(x.snpp>=10)&(x.snpp<50)],'50_plus':x[x.snpp>=50],
                'aqua_zero_viirs_positive':x[(x.aqua==0)&(x.snpp>0)],'both_observed_zero':x[(x.aqua==0)&(x.snpp==0)]}
            for name,pop in populations.items():rows.append(dict(period=period,territory=territory,population=name,policy=policy,
                calibration_cohort=calibration_cohort,shape=shape,**statistics(pop)))
    return pd.DataFrame(rows)


def factorial_contrasts(frame):
    # Change only one factor in every contrast.
    contrasts=[(('active','asymmetric'),('active','symmetric')),(('all_months','asymmetric'),('all_months','symmetric')),
               (('all_months','symmetric'),('active','symmetric')),(('all_months','asymmetric'),('active','asymmetric'))]
    result=[]
    for policy,g in frame.groupby('policy'):
        for population,pop in [('all_months',g),('active_months',g[g.snpp>0])]:
            wide=pop.pivot(index=KEYS,columns=['calibration_cohort','shape'],values='interval_score')
            for candidate,reference in contrasts:
                shared=wide[[candidate,reference]].dropna();difference=shared[candidate]-shared[reference]
                blocks=difference.groupby(level='season').mean()
                if set(blocks.index)!=set(TRAIN):raise ValueError('Missing factorial contrast season')
                result.append({'policy':policy,'population':population,'candidate':dict(zip(['calibration_cohort','shape'],candidate)),
                    'reference':dict(zip(['calibration_cohort','shape'],reference)),'mean_season_delta_interval_score':float(blocks.mean()),
                    'seasons_better':int((blocks<0).sum()),'blocks':len(blocks),'paired_rows':len(shared),
                    'per_season_delta':{str(k):float(v) for k,v in blocks.items()}})
    return result


def render_figure(metrics):
    import os
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.runtime/matplotlib'))
    import matplotlib
    matplotlib.use('Agg');matplotlib.rcParams['svg.hashsalt']='goliat-science-protocol13'
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
    order=[('active','symmetric'),('active','asymmetric'),('all_months','symmetric'),('all_months','asymmetric')]
    names=['Simétrica\nactivos','Asimétrica\nactivos','Simétrica\ntodos','Asimétrica\ntodos']
    for ax,population in zip(axes,['all_months','active_months']):
        source=metrics[(metrics.period=='nested_2012_2019')&(metrics.territory=='all54')&(metrics.population==population)]
        for j,(policy,color) in enumerate([('M1','#3568a8'),('M1_B','#c76824')]):
            values=[float(source[(source.policy==policy)&(source.calibration_cohort==c)&(source['shape']==s)].mean_interval_score.iloc[0]) for c,s in order]
            ax.bar(np.arange(4)+(j-.5)*.34,values,.34,label=policy,color=color,hatch='' if j==0 else '//',edgecolor='white')
        ax.set_xticks(np.arange(4),names);ax.set(ylabel='Pérdida de intervalo media (menor es mejor)',title='Todos los meses' if population=='all_months' else 'Solo meses activos observados')
        ax.grid(axis='y',alpha=.15);ax.legend()
    fig.suptitle('Diseño factorial · 54 comunas · puntos idénticos · evaluación anidada 2012–2019',fontsize=11)
    fig.savefig(OUT/'factorial_bands.png',dpi=170);fig.savefig(OUT/'factorial_bands.svg',metadata={'Date':None});plt.close(fig)


def run():
    check_deadline()
    protected=sorted((ROOT/'web/public/data').rglob('*.json'))
    protected+=[DATA/f for f in ['detections.parquet','celldays.parquet','static_mask.parquet','params.json','gates.csv','eval_loso.csv','eval_final.csv','inventory.csv']]
    for directory in ['scientific_audit','affine_audit','robust_affine_audit','piecewise_audit','geography_audit','platform_bridge_audit','temporal_transport_audit','conaf_external_audit','training_size_audit','frozen_temporal_audit','scaled_band_audit']:
        protected+=sorted((DATA/directory).glob('*'))
    before={str(p.relative_to(ROOT)):sha(p) for p in protected}
    data=AuditData();folds=[];parameters=[];fits=[];numerics=[]
    for held in TRAIN:
        intervals,cal,calls,numeric=nested_fold(data,held);folds.append(intervals);parameters.append(cal.assign(outer_held=held));fits.extend(calls)
        numerics.extend([dict(outer_held=held,**n) for n in numeric]);print('Factorial outer fold complete:',held,flush=True)
    historical=pd.concat(folds,ignore_index=True)
    previous=pd.read_parquet(DATA/'scaled_band_audit/nested_intervals.parquet');verify_control(historical,previous)
    oof=join_oof(pd.read_csv(DATA/'piecewise_audit/outer_predictions.csv',dtype={'cut':str}),pd.read_csv(DATA/'robust_affine_audit/outer_predictions.csv',dtype={'cut':str}))
    final=calibrate(oof);old=pd.read_csv(DATA/'scaled_band_audit/frozen_radii.csv',dtype={'cut':str})
    for policy in POLICIES:
        a=final[(final.policy==policy)&(final.calibration_cohort=='active')&(final['shape']=='symmetric')].sort_values('cut')
        b=old[(old.policy==policy)&(old.power==.5)].sort_values('cut')
        if a.cut.tolist()!=b.cut.tolist() or not np.allclose(a.q_upper,b.q80,atol=1e-10,rtol=0,equal_nan=True):raise ValueError('Final symmetric root control differs')
    model=load_frozen();fingerprint=signature(model)
    OUT.mkdir(parents=True,exist_ok=True);final.to_csv(OUT/'frozen_calibration.csv',index=False)
    (OUT/'frozen_band_config.json').write_text(json.dumps({'policies':POLICIES,'cohorts':COHORTS,'shapes':SHAPES,'power':.5,'alpha':.2,
        'source_point_model_signature':fingerprint,'parameters_sha256':sha(OUT/'frozen_calibration.csv')},indent=2,allow_nan=False)+'\n')
    print('Eight recipes frozen before destination read',flush=True)
    future_points=pd.read_parquet(DATA/'frozen_temporal_audit/predictions.parquet');future=apply_recipes(future_points,final)
    verify_control(future,pd.read_parquet(DATA/'scaled_band_audit/later_intervals.parquet'))
    enabled,_=publication_metadata(data.cuts);tables=[population_metrics(historical,enabled,'nested_2012_2019')]
    for season,g in historical.groupby('season'):tables.append(population_metrics(g,enabled,'season_'+str(season)))
    for block,g in future.groupby('block'):tables.append(population_metrics(g,enabled,block))
    legacy=future[future.block=='legacy_2020_2021']
    tables.append(population_metrics(legacy[legacy.y<2022],enabled,'legacy_before_calendar_2022'))
    tables.append(population_metrics(legacy[legacy.y==2022],enabled,'legacy_jan_jun_2022'))
    metrics=pd.concat(tables,ignore_index=True);contrasts=factorial_contrasts(historical)
    if len(historical)!=41472 or len(future)!=30240:raise ValueError('Factorial interval grid incomplete')
    if signature(model)!=fingerprint:raise ValueError('Point model changed')
    check_deadline()
    if before!={str(p.relative_to(ROOT)):sha(p) for p in protected}:raise ValueError('Protected files changed')
    historical.to_parquet(OUT/'nested_intervals.parquet',index=False,compression='zstd');future.to_parquet(OUT/'later_intervals.parquet',index=False,compression='zstd')
    for name,frame in [('fold_calibration.csv',pd.concat(parameters,ignore_index=True)),('fit_seasons.csv',pd.DataFrame(fits)),('numerics.csv',pd.DataFrame(numerics)),('metrics.csv',metrics)]:frame.to_csv(OUT/name,index=False)
    summary={'status':'retrospective-factorial-band-diagnostic','independent_validation':False,'point_estimates_unchanged':True,
        'symmetric_active_controls_reproduced':True,'source_point_model_signature':fingerprint,'fit_calls':len(fits),
        'nested_rows':len(historical),'later_rows':len(future),'contrasts':contrasts,
        'metrics':json.loads(metrics[metrics.period.isin(['nested_2012_2019','legacy_2020_2021','diagnostic_2022_2025'])].to_json(orient='records',double_precision=15))}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n');render_figure(metrics)
    helpers=['scientific_audit.py','affine_experiment.py','robust_affine_experiment.py','piecewise_experiment.py','temporal_transport_audit.py','frozen_temporal_audit.py','scaled_band_audit.py']
    manifest={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'protocol_sha256':sha(PROTOCOL),'code_sha256':sha(Path(__file__)),
        'helpers_sha256':{f:sha(ROOT/'pipeline'/f) for f in helpers},'environment_sha256':{f:sha(ROOT/f) for f in ['pyproject.toml','uv.lock']},
        'protected_sha256':before,'production_and_previous_unchanged':True,'output_sha256':{p.name:sha(p) for p in sorted(OUT.glob('*')) if p.name!='manifest.json'}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n');print('Factorial band audit complete:',OUT,flush=True)
    return summary


if __name__=='__main__':run()
