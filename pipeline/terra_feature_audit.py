"""Protocol 14: separate Aqua/Terra predictors and a training-only seasonal ablation."""
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from scientific_audit import ROOT,DATA,TRAIN,AuditData,fit_models,predict,score,summarize,sha
from affine_experiment import LAMBDAS,fit_affine,predict_affine,choose_policies,candidate_values,paired_bootstrap
from robust_affine_experiment import check_deadline
from temporal_transport_audit import validate_split
from frozen_temporal_audit import KEYS,load_frozen,signature,publication_metadata

OUT=DATA/'terra_feature_audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-14-science-protocol-14.md'
METHODS=('M0','M1','M2','M1_B','M1_C','M1_B_C','M1_B_D')
SPLITS={'forward_four':(tuple(range(2012,2016)),tuple(range(2016,2020))),
        'backward_four':(tuple(range(2016,2020)),tuple(range(2012,2016))),
        'forward_six':(tuple(range(2012,2018)),(2018,2019)),
        'backward_six':(tuple(range(2014,2020)),(2012,2013))}


class TerraData(AuditData):
    def __init__(self):super().__init__();self.terra_cache={}

    def terra_monthly(self,mask,start=2012,end=2019):
        key=(tuple(sorted(mask)),start,end)
        if key not in self.terra_cache:
            self.con.register('terra_mask',pd.DataFrame(sorted(mask),columns=['cell_x','cell_y']).astype('int64'))
            self.terra_cache[key]=self.con.execute(f"""select cut,season,m,count(*) terra,count(*) filter(any_nrt) terra_nrt
                from days d where sat='Terra' and season between {int(start)} and {int(end)}
                and not exists(select 1 from terra_mask s where s.cell_x=d.cell_x and s.cell_y=d.cell_y) group by 1,2,3""").df()
        return self.terra_cache[key].copy()

    def monthly(self,policy,allowed):
        base=super().monthly(policy,allowed)
        x=base.merge(self.terra_monthly(self.mask(policy,allowed)),on=KEYS,how='left',validate='one_to_one').fillna({'terra':0,'terra_nrt':0})
        if x.terra_nrt.sum():raise ValueError('Unexpected Terra NRT in training pool')
        return x


def name(mode,lam):return f'{mode}_{lam:g}'


def solve_faces(h,q):
    """Exact constrained quadratic minimum: intercept free, two slopes >=0."""
    solutions=[];objectives=[]
    for free in [(0,1,2),(0,1),(0,2),(0,)]:
        solution=np.zeros_like(q)
        solution[:,free]=np.linalg.solve(h[:,free,:][:,:,free],q[:,free,None])[:,:,0]
        feasible=(solution[:,1:]>=0).all(axis=1)
        objective=np.einsum('ni,nij,nj->n',solution,h,solution)-2*np.einsum('ni,ni->n',q,solution)
        objective[~feasible]=np.inf;solutions.append(solution);objectives.append(objective)
    stack=np.stack(solutions);choice=np.argmin(np.stack(objectives),axis=0);selected=stack[choice,np.arange(len(q))]
    gradient=np.einsum('nij,nj->ni',h,selected)-q
    kkt=np.maximum(np.abs(gradient[:,0]),np.max(np.where(selected[:,1:]>1e-10,np.abs(gradient[:,1:]),np.maximum(0,-gradient[:,1:])),axis=1))
    if not np.isfinite(selected).all() or kkt.max()>1e-6:raise ValueError('Terra quadratic fails KKT/finite check')
    return selected,kkt


def fit_multi(training,affine):
    if not np.isfinite(training[['aqua','terra','snpp']].to_numpy()).all() or (training[['aqua','terra','snpp']]<0).any().any():raise ValueError('Invalid Terra training data')
    params=affine[['scale','prior_beta','n']].rename(columns={'scale':'scale_a','prior_beta':'prior_a'}).copy()
    scale_t=training.assign(t2=training.terra**2).groupby('g').t2.mean().pow(.5).clip(lower=1)
    params['scale_t']=scale_t.reindex(params.index.get_level_values('g')).to_numpy()
    climatology=training.groupby(['cut','m']).terra.median().rename('terra_clim')
    t=training.merge(params[['scale_a','scale_t']],on=['cut','g'],validate='many_to_one').merge(climatology,on=['cut','m'],validate='many_to_one')
    for mode in ['C','D']:
        z=t[['cut','g']].copy();z['z0']=1.;z['z1']=t.aqua/t.scale_a
        z['z2']=(t.terra if mode=='C' else t.terra_clim)/t.scale_t
        for i in range(3):
            for j in range(i,3):z[f'h{i}{j}']=z[f'z{i}']*z[f'z{j}']
            z[f'q{i}']=z[f'z{i}']*t.snpp
        moments=z.groupby(['cut','g']).mean().reindex(params.index)
        h=np.zeros((len(params),3,3));q=np.zeros((len(params),3));prior=np.zeros_like(q);prior[:,1]=params.prior_a
        for i in range(3):
            q[:,i]=moments[f'q{i}']
            for j in range(i,3):h[:,i,j]=h[:,j,i]=moments[f'h{i}{j}']
        for lam in LAMBDAS:
            solution,kkt=solve_faces(h+lam*np.eye(3)[None,:,:],q+lam*prior);prefix=name(mode,lam)
            params[prefix+'_a']=solution[:,0];params[prefix+'_bA']=solution[:,1]/params.scale_a
            params[prefix+'_bT']=solution[:,2]/params.scale_t;params[prefix+'_kkt']=kkt
    return params,climatology


def predict_multi(frame,params,climatology):
    x=frame.merge(params,on=['cut','g'],how='left',validate='many_to_one').merge(climatology,on=['cut','m'],how='left',validate='many_to_one')
    if x[['scale_a','scale_t','terra_clim']].isna().any().any():raise ValueError('Missing Terra training group')
    for mode in ['C','D']:
        feature=x.terra if mode=='C' else x.terra_clim
        for lam in LAMBDAS:
            prefix=name(mode,lam)
            x[prefix+'_terra_component']=x[prefix+'_bT']*feature
            x[prefix+'_aqua_component']=x[prefix+'_bA']*x.aqua
            x[prefix+'_intercept_component']=x[prefix+'_a']
            x[prefix]=np.maximum(0,x[prefix+'_intercept_component']+x[prefix+'_aqua_component']+x[prefix+'_terra_component'])
    if not np.isfinite(x[[name(mode,l) for mode in ['C','D'] for l in LAMBDAS]].to_numpy()).all():raise ValueError('Invalid Terra estimates')
    return x.drop(columns=[*params.columns,'terra_clim'])


def choose(inner):
    previous,_=choose_policies(inner)
    cols=['M1',*[f'B_{l:g}' for l in LAMBDAS],*[name(mode,l) for mode in ['C','D'] for l in LAMBDAS]]
    losses=pd.DataFrame({c:(inner[c]-inner.snpp).abs() for c in cols});losses['cut']=inner.cut.to_numpy();losses=losses.groupby('cut').mean()
    choices={'M1_B':previous['M1_B'],'M1_C':{},'M1_B_C':{},'M1_B_D':{}}
    for cut,row in losses.iterrows():
        c=name('C',min(LAMBDAS,key=lambda l:(row[name('C',l)],-l)));d=name('D',min(LAMBDAS,key=lambda l:(row[name('D',l)],-l)))
        old=previous['M1_B'][cut]
        choices['M1_C'][cut]=c if row[c]<.99*row.M1 else 'M1'
        choices['M1_B_C'][cut]=c if row[c]<.99*row[old] else old
        choices['M1_B_D'][cut]=d if row[d]<.99*row[old] else old
    return choices,losses


def apply_choices(frame,choices):
    x=frame.copy()
    for policy,mapping in choices.items():
        x[policy]=candidate_values(x,mapping);x[policy+'_chosen']=x.cut.map(mapping)
        records=x.to_dict('records');selected=x.cut.map(mapping)
        for component in ['aqua','terra','intercept']:
            x[policy+'_'+component+'_component']=[(r['M1'] if component=='aqua' else 0.) if method=='M1' else r[method+'_'+component+'_component'] for r,method in zip(records,selected)]
    return x


def predict_all(frame,reference,affine,params,clim):
    x=predict_affine(predict(frame,reference),affine)
    index=pd.MultiIndex.from_frame(x[['cut','g']])
    for lam in LAMBDAS:
        prefix=f'B_{lam:g}'
        x[prefix+'_aqua_component']=affine[prefix+'_b'].reindex(index).to_numpy()*x.aqua
        x[prefix+'_intercept_component']=affine[prefix+'_a'].reindex(index).to_numpy()
        x[prefix+'_terra_component']=0.
    return predict_multi(x,params,clim)


def fit_predict(data,allowed,destination):
    check_deadline();validate_split(allowed,destination)
    full=data.monthly('fold_fitted',allowed);tr=full[full.season.isin(allowed)];te=full[full.season.isin(destination)]
    reference=fit_models(tr);affine=fit_affine(tr,reference);multi,clim=fit_multi(tr,affine)
    if not hasattr(data,'fit_diagnostics'):data.fit_diagnostics=[]
    data.fit_diagnostics.append({'allowed':';'.join(map(str,allowed)),'held':';'.join(map(str,destination)),
        'max_kkt':float(multi[[c for c in multi if c.endswith('_kkt')]].max().max())})
    return predict_all(te,reference,affine,multi,clim),multi,clim


def transport(data,origin,destination):
    validate_split(origin,destination)
    inner=pd.concat([fit_predict(data,tuple(s for s in origin if s!=h),(h,))[0] for h in origin],ignore_index=True)
    choices,loss=choose(inner);point,params,clim=fit_predict(data,origin,destination)
    selection=pd.DataFrame([{'cut':cut,'policy':p,'candidate':c,'internal_mae':float(loss.loc[cut,c])} for p,m in choices.items() for cut,c in m.items()])
    return apply_choices(point,choices),selection,params


def verify_points(actual,previous):
    a=actual.sort_values(KEYS).reset_index(drop=True);b=previous.sort_values(KEYS).reset_index(drop=True)
    if not a[KEYS].equals(b[KEYS]):raise ValueError('Terra baseline keys differ')
    for c in ['aqua','snpp','M0','M1','M2','M1_B']:
        equal=np.array_equal(a[c],b[c]) if c in ['aqua','snpp'] else np.allclose(a[c],b[c],atol=1e-10,rtol=0)
        if not equal:raise ValueError('Terra baseline differs '+c)


def metrics(frame):
    baseline=float((frame.M1-frame.snpp).abs().mean()) if len(frame) else None
    result={}
    for method in METHODS:
        error=frame[method]-frame.snpp;regional=frame.groupby(['season','m'])[[method,'snpp']].sum()
        result[method]={'n':len(frame),'mae':float(error.abs().mean()) if len(frame) else None,
            'bias':float(error.mean()) if len(frame) else None,'absolute_error_sum':float(error.abs().sum()),
            'regional_monthly_mae':float((regional[method]-regional.snpp).abs().mean()) if len(regional) else None,
            'improvement_pct_vs_M1':float((1-error.abs().mean()/baseline)*100) if baseline and baseline>0 else None}
    return result


def report(frame,enabled):
    populations={'all54':frame,'published14':frame[frame.cut.isin(enabled)],'zero':frame[frame.snpp==0],
        '1_to_9':frame[(frame.snpp>=1)&(frame.snpp<10)],'10_to_49':frame[(frame.snpp>=10)&(frame.snpp<50)],'50_plus':frame[frame.snpp>=50],
        'aqua_zero_viirs_positive':frame[(frame.aqua==0)&(frame.snpp>0)],
        'aqua_zero_viirs_positive_terra_zero':frame[(frame.aqua==0)&(frame.snpp>0)&(frame.terra==0)],
        'aqua_zero_viirs_positive_terra_positive':frame[(frame.aqua==0)&(frame.snpp>0)&(frame.terra>0)],
        'aqua_zero_viirs_zero_terra_zero':frame[(frame.aqua==0)&(frame.snpp==0)&(frame.terra==0)],
        'aqua_zero_viirs_zero_terra_positive':frame[(frame.aqua==0)&(frame.snpp==0)&(frame.terra>0)],'aqua_positive':frame[frame.aqua>0]}
    return {label:metrics(g) for label,g in populations.items()}


def run():
    check_deadline()
    protected=sorted((ROOT/'web/public/data').rglob('*.json'))
    protected+=[DATA/f for f in ['detections.parquet','celldays.parquet','static_mask.parquet','params.json','gates.csv','eval_loso.csv','eval_final.csv','inventory.csv']]
    for directory in ['scientific_audit','affine_audit','robust_affine_audit','piecewise_audit','geography_audit','platform_bridge_audit','temporal_transport_audit','conaf_external_audit','training_size_audit','frozen_temporal_audit','scaled_band_audit','asymmetric_band_audit']:
        protected+=sorted((DATA/directory).glob('*'))
    before={str(p.relative_to(ROOT)):sha(p) for p in protected};data=TerraData();enabled,_=publication_metadata(data.cuts)
    predictions=[];selections=[];parameters=[]
    for held in TRAIN:
        origin=tuple(s for s in TRAIN if s!=held);point,selection,params=transport(data,origin,(held,))
        predictions.append(point);selections.append(selection.assign(outer_held=held));parameters.append(params.reset_index().assign(outer_held=held))
        print('Terra outer fold complete:',held,flush=True)
    nested=pd.concat(predictions,ignore_index=True);verify_points(nested,pd.read_csv(DATA/'affine_audit/outer_predictions.csv',dtype={'cut':str}))
    blocked=[];block_reports={}
    prior4=pd.read_csv(DATA/'temporal_transport_audit/predictions.csv',dtype={'cut':str});prior6=pd.read_parquet(DATA/'training_size_audit/predictions.parquet')
    for label,(origin,destination) in SPLITS.items():
        x,selection,_=transport(data,origin,destination);direction=label.split('_')[0]
        old=prior4[prior4.direction==direction] if label.endswith('four') else prior6[(prior6.direction==direction)&(prior6.n_train==6)&(prior6.mask_policy=='fold_fitted')]
        verify_points(x,old);blocked.append(x.assign(case=label));block_reports[label]=report(x,enabled)
        print('Terra temporal case complete:',label,flush=True)
    full=data.monthly('fold_fitted',TRAIN);reference=fit_models(full);affine=fit_affine(full,reference);params,clim=fit_multi(full,affine);choices,loss=choose(nested)
    data.fit_diagnostics.append({'allowed':';'.join(map(str,TRAIN)),'held':'full_fit',
        'max_kkt':float(params[[c for c in params if c.endswith('_kkt')]].max().max())})
    old_model=load_frozen();fingerprint=signature(old_model)
    if abs(reference['ratio']-old_model['reference']['ratio'])>1e-12 or choices['M1_B']!=old_model['choices']['M1_B']:raise ValueError('Frozen Aqua baseline changed')
    OUT.mkdir(parents=True,exist_ok=True);params.to_csv(OUT/'frozen_coefficients.csv');clim.to_csv(OUT/'frozen_terra_climatology.csv')
    affine.to_csv(OUT/'frozen_affine.csv')
    for label in ['regional','local','climatology']:reference[label].to_csv(OUT/('reference_'+label+'.csv'))
    (OUT/'frozen_model.json').write_text(json.dumps({'schema_version':1,'r_const':reference['ratio'],'training_seasons':list(TRAIN),'choices':choices,
        'source_baseline_signature':fingerprint,'coefficients_sha256':sha(OUT/'frozen_coefficients.csv'),'climatology_sha256':sha(OUT/'frozen_terra_climatology.csv'),
        'reference_sha256':{p.name:sha(p) for p in [OUT/'frozen_affine.csv',*[OUT/('reference_'+label+'.csv') for label in ['regional','local','climatology']]]}},indent=2,allow_nan=False)+'\n')
    print('Terra candidates frozen before destination read',flush=True)
    future=pd.read_parquet(DATA/'frozen_temporal_audit/predictions.parquet')
    # Remove previous estimates before computing them again from the frozen fit.
    features=future[[*KEYS,'y','g','aqua','snpp','block','orbit_epoch']].merge(data.terra_monthly(data.fit_mask(TRAIN),2020,2025),on=KEYS,how='left',validate='one_to_one').fillna({'terra':0,'terra_nrt':0})
    if features.terra_nrt.sum():raise ValueError('Unexpected Terra NRT in diagnostic period')
    later=apply_choices(predict_all(features,reference,affine,params,clim),choices);verify_points(later,future)
    later_reports={label:report(g,enabled) for label,g in later.groupby('block')}
    legacy=later[later.block=='legacy_2020_2021'];later_reports['legacy_before_calendar_2022']=report(legacy[legacy.y<2022],enabled);later_reports['legacy_jan_jun_2022']=report(legacy[legacy.y==2022],enabled)
    check_deadline()
    if before!={str(p.relative_to(ROOT)):sha(p) for p in protected}:raise ValueError('Protected files changed')
    for filename,frame in [('nested_predictions.parquet',nested),('blocked_predictions.parquet',pd.concat(blocked,ignore_index=True)),('later_predictions.parquet',later)]:frame.to_parquet(OUT/filename,index=False,compression='zstd')
    pd.concat(selections,ignore_index=True).to_csv(OUT/'nested_selection.csv',index=False);pd.concat(parameters,ignore_index=True).to_csv(OUT/'outer_coefficients.csv',index=False)
    scores=score(nested,METHODS);scores.to_csv(OUT/'scores.csv',index=False)
    pd.DataFrame(data.fit_diagnostics).to_csv(OUT/'fit_diagnostics.csv',index=False)
    summary={'status':'retrospective-terra-feature-experiment','independent_validation':False,'controls_reproduced':True,
        'nested':report(nested,enabled),'nested_scores':summarize(scores),'contrasts':[paired_bootstrap(nested,a,b) for a,b in [('M1_C','M1'),('M1_B_C','M1_B'),('M1_B_C','M1_B_D')]],
        'temporal_cases':block_reports,'later':later_reports,'choice_counts':{p:pd.Series(mapping).value_counts().astype(int).to_dict() for p,mapping in choices.items()},
        'source_baseline_signature':fingerprint,'max_kkt':float(max(d['max_kkt'] for d in data.fit_diagnostics)),'fits':len(data.fit_diagnostics),
        'terra_predictor_totals':{str(s):int(g.terra.sum()) for s,g in full.groupby('season')}}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    helpers=['scientific_audit.py','affine_experiment.py','robust_affine_experiment.py','temporal_transport_audit.py','frozen_temporal_audit.py']
    manifest={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'protocol_sha256':sha(PROTOCOL),'code_sha256':sha(Path(__file__)),
        'helpers_sha256':{f:sha(ROOT/'pipeline'/f) for f in helpers},'environment_sha256':{f:sha(ROOT/f) for f in ['pyproject.toml','uv.lock']},
        'protected_sha256':before,'production_and_previous_unchanged':True,'output_sha256':{p.name:sha(p) for p in sorted(OUT.glob('*')) if p.name!='manifest.json'}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n');print('Terra experiment complete:',OUT,flush=True)
    return summary


if __name__=='__main__':run()
