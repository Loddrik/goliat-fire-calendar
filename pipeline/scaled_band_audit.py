"""Protocol 12: fixed point estimates, nested scale-aware interval comparison."""
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from scientific_audit import ROOT,DATA,TRAIN,AuditData,sha
from robust_affine_experiment import check_deadline,choose as choose_huber
from piecewise_experiment import choose as choose_piecewise
from temporal_transport_audit import fit_predict,apply_choices
from frozen_temporal_audit import BAND_POLICIES,KEYS,join_oof,load_frozen,signature,publication_metadata

OUT=DATA/'scaled_band_audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-14-science-protocol-12.md'
POWERS=(0.,.5,1.)
ALPHA=.2


def scale(point,power):
    point=np.asarray(point,dtype=float)
    if power not in POWERS or not np.isfinite(point).all() or (point<0).any():raise ValueError('Invalid interval scale input')
    return (1+point)**power


def calibrate(frame):
    if not np.isfinite(frame[['snpp',*BAND_POLICIES]].to_numpy()).all() or (frame.snpp<0).any():raise ValueError('Invalid calibration observations')
    records=[]
    for cut,g in frame.groupby('cut'):
        active=g[g.snpp>0]
        for policy in BAND_POLICIES:
            errors=(active[policy]-active.snpp).abs().to_numpy()
            for power in POWERS:
                normalized=errors/scale(active[policy],power)
                records.append({'cut':cut,'policy':policy,'power':power,'n_calibration':len(active),
                    'q80':float(pd.Series(normalized).quantile(.8)) if len(active) else np.nan})
    return pd.DataFrame(records)


def interval_loss(y,lower,upper,alpha=ALPHA):
    if not 0<alpha<1:raise ValueError('Invalid interval alpha')
    y,lower,upper=np.broadcast_arrays(np.asarray(y,dtype=float),np.asarray(lower,dtype=float),np.asarray(upper,dtype=float))
    if any(np.isinf(v).any() for v in [y,lower,upper]) or (lower>upper).any():raise ValueError('Invalid interval bounds')
    return (upper-lower)+(2/alpha)*np.maximum(lower-y,0)+(2/alpha)*np.maximum(y-upper,0)


def apply_bands(frame,calibration):
    if frame.duplicated(KEYS).any() or calibration.duplicated(['cut','policy','power']).any():raise ValueError('Duplicate interval keys')
    frames=[]
    metadata=[c for c in ['cut','season','m','y','block','orbit_epoch','snpp'] if c in frame]
    for policy in BAND_POLICIES:
        for power in POWERS:
            c=calibration[(calibration.policy==policy)&(calibration.power==power)].set_index('cut')
            if not set(frame.cut)<=set(c.index):raise ValueError('Missing calibration commune')
            point=frame[policy].to_numpy(dtype=float)
            radius=frame.cut.map(c.q80).to_numpy()*scale(point,power)
            if (radius<0).any() or np.isinf(radius).any():raise ValueError('Invalid calibrated radius')
            x=frame[metadata].copy();x['policy']=policy;x['power']=power;x['point']=point
            x['n_calibration']=frame.cut.map(c.n_calibration).to_numpy();x['radius']=radius
            x['lower']=np.maximum(0,point-radius);x['upper']=point+radius
            x['interval_score']=interval_loss(x.snpp,x.lower,x.upper) if 'snpp' in x else np.nan
            frames.append(x)
    return pd.concat(frames,ignore_index=True)


def outer_fold(data,held,fit=fit_predict):
    allowed=tuple(s for s in TRAIN if s!=held);parts=[];calls=[]
    def checked_fit(origin,destination):
        if held in origin or set(origin)&set(destination):raise ValueError('External season entered fitting')
        frame,params=fit(data,tuple(origin),tuple(destination))
        if set(frame.season)!=set(destination):raise ValueError('Fit returned wrong held seasons')
        calls.append({'outer_held':held,'allowed':';'.join(map(str,origin)),'held':';'.join(map(str,destination))})
        return frame,params
    for inner_held in allowed:
        part,_=checked_fit(tuple(s for s in allowed if s!=inner_held),(inner_held,));parts.append(part)
    inner=pd.concat(parts,ignore_index=True)
    if set(inner.season)!=set(allowed):raise ValueError('Calibration seasons crossed external boundary')
    choices,_=choose_piecewise(inner);hchoices,_=choose_huber(inner);choices['M1_H']=hchoices['M1_H']
    selected_inner=apply_choices(inner,choices);cal=calibrate(selected_inner)
    test,params=checked_fit(allowed,(held,));test=apply_choices(test,choices)
    return test,cal,apply_bands(test,cal),calls,params.attrs.get('huber_numerics',[])


def check_reproduction(points,intervals,piecewise,huber,affine):
    old=join_oof(piecewise,huber).sort_values(KEYS).reset_index(drop=True)
    actual=points.sort_values(KEYS).reset_index(drop=True)
    if not actual[KEYS].equals(old[KEYS]):raise ValueError('Historical point keys differ')
    for col in ['aqua','snpp',*BAND_POLICIES]:
        equal=np.array_equal(actual[col],old[col]) if col in ['aqua','snpp'] else np.allclose(actual[col],old[col],atol=1e-10,rtol=0)
        if not equal:raise ValueError('Historical point control differs '+col)
    for policy in BAND_POLICIES:
        source=huber if policy=='M1_H' else piecewise
        wanted=source.sort_values(KEYS).reset_index(drop=True)
        new=intervals[(intervals.policy==policy)&(intervals.power==0)].sort_values(KEYS).reset_index(drop=True)
        if not new[KEYS].equals(wanted[KEYS]) or not np.allclose(new.radius,wanted[policy+'_abs80_radius'],atol=1e-10,rtol=0,equal_nan=True):
            raise ValueError('Absolute radius control differs '+policy)
    for policy in ['M1','M1_B']:
        old=affine.sort_values(KEYS).reset_index(drop=True)
        new=intervals[(intervals.policy==policy)&(intervals.power==1)].sort_values(KEYS).reset_index(drop=True)
        if not new[KEYS].equals(old[KEYS]) or not np.allclose(new.radius,old[policy+'_scaled80_radius'],atol=1e-10,rtol=0,equal_nan=True):
            raise ValueError('Relative radius control differs '+policy)


def statistics(frame):
    x=frame[np.isfinite(frame.interval_score)]
    return {'n':len(frame),'n_scored':len(x),'missing_calibration':int(frame.radius.isna().sum()),
        'unknown_target':int(frame.snpp.isna().sum()) if 'snpp' in frame else len(frame),
        'coverage':float(((x.snpp>=x.lower)&(x.snpp<=x.upper)).mean()) if len(x) else None,
        'mean_width':float((x.upper-x.lower).mean()) if len(x) else None,
        'mean_interval_score':float(x.interval_score.mean()) if len(x) else None,
        'below_fraction':float((x.snpp<x.lower).mean()) if len(x) else None,
        'above_fraction':float((x.snpp>x.upper).mean()) if len(x) else None}


def population_metrics(intervals,enabled,period):
    rows=[]
    for (policy,power),g in intervals.groupby(['policy','power']):
        for cohort,cuts in [('all54',None),('published14',enabled)]:
            x=g if cuts is None else g[g.cut.isin(cuts)]
            populations={'all_months':x,'active_months':x[x.snpp>0],'zero':x[x.snpp==0],
                '1_to_9':x[(x.snpp>=1)&(x.snpp<10)],'10_to_49':x[(x.snpp>=10)&(x.snpp<50)],'50_plus':x[x.snpp>=50]}
            for name,pop in populations.items():rows.append(dict(period=period,cohort=cohort,population=name,policy=policy,power=power,**statistics(pop)))
    return pd.DataFrame(rows)


def paired_contrasts(intervals):
    results=[]
    for policy,g in intervals.groupby('policy'):
        for population,x in [('all_months',g),('active_months',g[g.snpp>0])]:
            wide=x.pivot(index=KEYS,columns='power',values='interval_score')
            for power in [.5,1.]:
                valid=wide[[0.,power]].dropna();difference=valid[power]-valid[0.]
                by_season=difference.groupby(level='season').mean()
                if set(by_season.index)!=set(TRAIN):raise ValueError('Missing season contrast')
                results.append({'policy':policy,'population':population,'candidate_power':power,'reference_power':0.,
                    'mean_season_delta_interval_score':float(by_season.mean()),'seasons_better':int((by_season<0).sum()),
                    'per_season_delta':{str(k):float(v) for k,v in by_season.items()},'paired_rows':len(valid),'blocks':len(by_season)})
    return results


def render_figure(metrics):
    import os
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.runtime/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    matplotlib.rcParams['svg.hashsalt']='goliat-science-protocol12'
    selected=metrics[(metrics.period=='nested_2012_2019')&(metrics.cohort=='all54')&(metrics.population=='active_months')]
    colors={0.:'#3568a8',.5:'#c76824',1.:'#338055'};labels={0.:'Absoluto',.5:'Raíz cuadrada',1.:'Relativo'}
    fig,axes=plt.subplots(1,2,figsize=(11,4.6),layout='constrained')
    markers=['o','s','^','D','v']
    for policy,marker in zip(BAND_POLICIES,markers):
        g=selected[selected.policy==policy]
        for r in g.itertuples():axes[0].scatter(r.mean_width,100*r.coverage,c=colors[r.power],marker=marker,s=55,label=f'{policy}: {labels[r.power]}')
    axes[0].axhline(80,color='#777',ls='--',lw=1);axes[0].set(xlabel='Anchura media (celdas-día)',ylabel='Cobertura en meses activos (%)',title='54 comunas · evaluación anidada')
    axes[0].grid(alpha=.15)
    axes[0].legend(handles=[Line2D([],[],color='#333',ls='',marker=m,label=p) for p,m in zip(BAND_POLICIES,markers)],fontsize=7,ncol=2,loc='lower right')
    order=list(BAND_POLICIES);positions=np.arange(len(order));width=.24
    for j,power in enumerate(POWERS):
        values=[float(selected[(selected.policy==p)&(selected.power==power)].mean_interval_score.iloc[0]) for p in order]
        axes[1].bar(positions+(j-1)*width,values,width,color=colors[power],label=labels[power],hatch=['','//','xx'][j],edgecolor='white',linewidth=.4)
    axes[1].set_xticks(positions,order,rotation=25);axes[1].set(ylabel='Pérdida de intervalo media (menor es mejor)',title='Anchura y distancia de errores fuera de banda')
    axes[1].legend(fontsize=8);axes[1].grid(axis='y',alpha=.15)
    fig.suptitle('Bandas q80 · temporadas 2012–2019 · estimaciones puntuales idénticas',fontsize=12)
    fig.savefig(OUT/'nested_bands.png',dpi=170);fig.savefig(OUT/'nested_bands.svg',metadata={'Date':None});plt.close(fig)


def run():
    check_deadline()
    protected=sorted((ROOT/'web/public/data').rglob('*.json'))
    protected+=[DATA/f for f in ['detections.parquet','celldays.parquet','static_mask.parquet','params.json','gates.csv','eval_loso.csv','eval_final.csv','inventory.csv']]
    for directory in ['scientific_audit','affine_audit','robust_affine_audit','piecewise_audit','geography_audit','platform_bridge_audit','temporal_transport_audit','conaf_external_audit','training_size_audit','frozen_temporal_audit']:
        protected+=sorted((DATA/directory).glob('*'))
    before={str(p.relative_to(ROOT)):sha(p) for p in protected}
    data=AuditData();all_points=[];all_intervals=[];fold_radii=[];fits=[];numerics=[]
    for held in TRAIN:
        point,cal,intervals,calls,numeric=outer_fold(data,held)
        all_points.append(point);all_intervals.append(intervals);fold_radii.append(cal.assign(outer_held=held));fits.extend(calls)
        numerics.extend([dict(outer_held=held,**n) for n in numeric]);print('Scale-band outer fold complete:',held,flush=True)
    points=pd.concat(all_points,ignore_index=True);historical=pd.concat(all_intervals,ignore_index=True)
    piecewise=pd.read_csv(DATA/'piecewise_audit/outer_predictions.csv',dtype={'cut':str})
    huber=pd.read_csv(DATA/'robust_affine_audit/outer_predictions.csv',dtype={'cut':str})
    affine=pd.read_csv(DATA/'affine_audit/outer_predictions.csv',dtype={'cut':str})
    check_reproduction(points,historical,piecewise,huber,affine)
    oof=join_oof(piecewise,huber);final_radii=calibrate(oof);model=load_frozen();fingerprint=signature(model)
    old=model['radii'].sort_values(['cut','policy']).reset_index(drop=True)
    new=final_radii[final_radii.power==0].sort_values(['cut','policy']).reset_index(drop=True)
    if not new[['cut','policy']].equals(old[['cut','policy']]) or not np.array_equal(new.q80,old.abs80_radius,equal_nan=True):raise ValueError('Frozen absolute radii differ')
    OUT.mkdir(parents=True,exist_ok=True);final_radii.to_csv(OUT/'frozen_radii.csv',index=False)
    (OUT/'frozen_band_config.json').write_text(json.dumps({'powers':POWERS,'alpha':ALPHA,'source_point_model_signature':fingerprint,
        'calibration_seasons':list(TRAIN),'radii_sha256':sha(OUT/'frozen_radii.csv')},indent=2,allow_nan=False)+'\n')
    print('All three band rules frozen before destination read',flush=True)
    future_points=pd.read_parquet(DATA/'frozen_temporal_audit/predictions.parquet')
    future=apply_bands(future_points,final_radii)
    enabled,_=publication_metadata(data.cuts)
    tables=[population_metrics(historical,enabled,'nested_2012_2019')]
    for season,g in historical.groupby('season'):tables.append(population_metrics(g,enabled,'season_'+str(season)))
    for block,g in future.groupby('block'):tables.append(population_metrics(g,enabled,block))
    legacy=future[future.block=='legacy_2020_2021']
    tables.append(population_metrics(legacy[legacy.y<2022],enabled,'legacy_before_calendar_2022'))
    tables.append(population_metrics(legacy[legacy.y==2022],enabled,'legacy_jan_jun_2022'))
    metrics=pd.concat(tables,ignore_index=True);contrasts=paired_contrasts(historical)
    if len(historical)!=77760 or len(future)!=56700:raise ValueError('Interval grids incomplete')
    if signature(model)!=fingerprint:raise ValueError('Point model changed')
    check_deadline()
    if before!={str(p.relative_to(ROOT)):sha(p) for p in protected}:raise ValueError('Protected inputs/production changed')
    historical.to_parquet(OUT/'nested_intervals.parquet',index=False,compression='zstd')
    future.to_parquet(OUT/'later_intervals.parquet',index=False,compression='zstd')
    for name,frame in [('fold_radii.csv',pd.concat(fold_radii,ignore_index=True)),('fit_seasons.csv',pd.DataFrame(fits)),
                       ('numerics.csv',pd.DataFrame(numerics)),('metrics.csv',metrics)]:frame.to_csv(OUT/name,index=False)
    summary={'status':'retrospective-scaled-band-comparison','independent_validation':False,'point_estimates_and_previous_radii_reproduced':True,
        'source_point_model_signature':fingerprint,'powers':POWERS,'alpha':ALPHA,'outer_folds':8,'fit_calls':len(fits),
        'nested_interval_rows':len(historical),'later_interval_rows':len(future),'contrasts':contrasts,
        'frozen_radii_absolute_exactly_reproduced':True,'missing_calibration_rows':int(historical.radius.isna().sum()),
        'metrics':json.loads(metrics[metrics.period.isin(['nested_2012_2019','legacy_2020_2021','diagnostic_2022_2025'])].to_json(orient='records',double_precision=15))}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n');render_figure(metrics)
    helpers=['scientific_audit.py','affine_experiment.py','robust_affine_experiment.py','piecewise_experiment.py','temporal_transport_audit.py','frozen_temporal_audit.py']
    manifest={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'protocol_sha256':sha(PROTOCOL),'code_sha256':sha(Path(__file__)),
        'helpers_sha256':{f:sha(ROOT/'pipeline'/f) for f in helpers},'environment_sha256':{f:sha(ROOT/f) for f in ['pyproject.toml','uv.lock']},
        'protected_sha256':before,'production_and_previous_unchanged':True,
        'output_sha256':{p.name:sha(p) for p in sorted(OUT.glob('*')) if p.name!='manifest.json'}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n');print('Scaled-band audit complete:',OUT,flush=True)
    return summary


if __name__=='__main__':run()
