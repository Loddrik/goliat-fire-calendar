"""37 driver: frozen historical controls, SOURCE-filtered fits, label-safe phases."""
import argparse
import json
import math
import platform
import resource
import sys
import unittest
from datetime import datetime,timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

import daily_context_model as context
from scientific_audit import ROOT,DATA,sha
from cold_region_audit import raw_predictions,FEATURES,REGIMES,fingerprint
from coherent_allocation import reconcile,expected_risk,kkt_residual
from frozen_temporal_audit import KEYS,publication_metadata

SOURCE=DATA/'cold_region_audit';CUBE=DATA/'daily_adjacency_audit';OUT=DATA/'daily_context_audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-15-daily-context-model-protocol.md'
START='2026-11-15T08:07:07+00:00';CHECKPOINT='2026-11-15T08:32:07+00:00';END='2026-11-15T09:07:07+00:00'
METHODS=('B','G','Q_real','Q_placebo');MAX_FITS=64;MAX_SOLVERS=3000


def now():return datetime.now(timezone.utc)
def dump(path,obj):path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def check(checkpoint=False):
    if now()>=datetime.fromisoformat(CHECKPOINT if checkpoint else END):raise TimeoutError('37 absolute cap')
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024)
    if rss>2*1024**3:raise MemoryError('2GiB cap')
    if OUT.exists() and sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())>100*1024**2:raise RuntimeError('100MiB cap')
    return rss


def snapshot():return {str(p.relative_to(ROOT)):sha(p) for p in list(DATA.rglob('*'))+list((ROOT/'web/public/data').rglob('*.json')) if p.is_file() and OUT not in p.parents}


def freeze():
    check(checkpoint=True)
    if OUT.exists():raise FileExistsError('37 exclusive output exists')
    prior=json.loads((SOURCE/'manifest.json').read_text());cube=json.loads((CUBE/'manifest.json').read_text())
    if not cube['all_cube_integrity_gates_passed']:raise ValueError('Cube gates absent')
    for name in ('models.json','predictions.parquet','candidate_mask.csv'):
        if sha(SOURCE/name)!=prior['output_sha256'][name]:raise ValueError('21 frozen input mismatch')
    if sha(CUBE/'cube.parquet')!=cube['files']['cube.parquet']['sha256']:raise ValueError('36 cube changed')
    review=ROOT/'docs/reviews/evidence/daily-adjacency-independent-review/summary.json'
    if not review.exists():raise ValueError('36 independent review absent')
    # No feature/target values, candidate fits or predictions precede this record.
    code=[Path(__file__),ROOT/'pipeline/daily_context_model.py',ROOT/'tests/test_daily_context_model.py',ROOT/'pipeline/cold_region_audit.py',ROOT/'pipeline/hurdle_model.py',ROOT/'pipeline/coherent_allocation.py']
    OUT.mkdir(parents=True)
    record={'created_utc':now().isoformat(),'protocol_sha256':sha(PROTOCOL),'code_sha256':{str(p.relative_to(ROOT)):sha(p) for p in code},'input_sha256':{str(p.relative_to(ROOT)):sha(p) for p in list(SOURCE.iterdir())+list(CUBE.iterdir()) if p.is_file()},'protected_sha256':snapshot(),'cap':{'start':START,'checkpoint':CHECKPOINT,'end':END},'limits':{'candidatefits':MAX_FITS,'reconcile':MAX_SOLVERS,'rows':1000000,'physical_bytes':100*1024**2,'RSS_bytes':2*1024**3},'schema21':str(pq.read_schema(SOURCE/'predictions.parquet')),'schema36':str(pq.read_schema(CUBE/'cube.parquet')),'no_candidatefit_or_prediction_yet':True}
    dump(OUT/'code-freeze.json',record)
    sys.path.insert(0,str(ROOT/'tests'))
    suite=unittest.defaultTestLoader.loadTestsFromName('test_daily_context_model')
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    dump(OUT/'synthetic-tests.json',{'tests':result.testsRun,'passed':result.wasSuccessful(),'candidate_fit_calls':context.FIT_CALLS,'solver_calls':0,'code_freeze_sha256':sha(OUT/'code-freeze.json'),'completed_utc':now().isoformat()})
    if not result.wasSuccessful():raise ValueError('Synthetic gates failed')
    print('CODE FROZEN before candidate fixtures:',sha(OUT/'code-freeze.json'),flush=True)


def verify():
    check();f=json.loads((OUT/'code-freeze.json').read_text())
    if sha(PROTOCOL)!=f['protocol_sha256']:raise ValueError('Protocol changed')
    for group in ('code_sha256','input_sha256','protected_sha256'):
        for key,value in f[group].items():
            if sha(ROOT/key)!=value:raise ValueError('Frozen source changed: '+key)
    return f


def load_features():
    f=pd.read_parquet(SOURCE/'predictions.parquet',columns=['regime',*FEATURES])
    cube=pd.read_parquet(CUBE/'cube.parquet',columns=[*FEATURES,'D_real','D_placebo'])
    if len(f)!=10368 or len(cube)!=5184 or f.duplicated(['regime',*KEYS]).any() or cube.duplicated(KEYS).any():raise ValueError('Fixed key domain changed')
    q=f.merge(cube,on=KEYS,validate='many_to_one',suffixes=('_21','_36'))
    for key in ('aqua','g'):
        if not np.array_equal(q[key+'_21'].to_numpy(),q[key+'_36'].to_numpy()):raise ValueError('36/21 feature mismatch')
    q=q.rename(columns={'g_21':'g','aqua_21':'aqua'}).drop(columns=['g_36','aqua_36'])
    if ((q.aqua<=1)&((q.D_real!=0)|(q.D_placebo!=0))).any():raise ValueError('Adjacency structural gate')
    return q[['regime',*FEATURES,'D_real','D_placebo']],cube


def source_training(base,cube,label):
    """Physical Parquet predicate precedes response materialization for THIS regime."""
    cuts=list(base['source_cuts']);seasons=list(base['origin_seasons'])
    filters=[('cut','in',cuts),('season','in',seasons)]
    started=now().isoformat()
    table=pq.read_table(SOURCE/'predictions.parquet',columns=KEYS+['snpp'],filters=filters)
    labels=table.to_pandas()
    if not labels.cut.isin(cuts).all() or not labels.season.isin(seasons).all():raise ValueError('SOURCE predicate failed')
    if not np.isfinite(labels.snpp).all() or (labels.snpp<0).any():raise ValueError('Invalid selected SOURCE labels')
    grouped=labels.groupby(KEYS,sort=True).snpp
    if not grouped.size().eq(2).all() or not grouped.nunique().eq(1).all():raise ValueError('Conflicting/missing duplicated SOURCE response')
    unique=labels.drop_duplicates(KEYS).copy()
    features=cube[cube.cut.isin(cuts)&cube.season.isin(seasons)]
    train=features.merge(unique,on=KEYS,validate='one_to_one')
    if len(train)!=len(cuts)*len(seasons)*12 or len(train)!=len(unique):raise ValueError('SOURCE feature/response incomplete')
    log={'regime':label,'first_source_response_read_utc':started,'columns':KEYS+['snpp'],'parquet_filters':[['cut','in',cuts],['season','in',seasons]],'filter_applied_before_materialization':True,'duplicates_exact':True,'raw_rows':len(labels),'unique_rows':len(unique),'roster_sha256':context.signature(train[KEYS].sort_values(KEYS).to_dict(orient='records')),'source_only_per_regime_not_global_no_held_claim':True}
    return train,log


def allocate(distributions,baseline,budget):
    check()
    if budget['solver_calls']>=MAX_SOLVERS:raise RuntimeError('Solver cap')
    budget['solver_calls']+=1
    a=reconcile(distributions,baseline)
    total=math.fsum(float(v) for v in baseline);err=math.fsum(float(v) for v in a)-total
    rb=expected_risk(distributions,baseline);ra=expected_risk(distributions,a);kkt=kkt_residual(distributions,a)
    if abs(err)>1e-10*max(1,total) or ra>rb+1e-8*max(1,rb) or kkt>1e-8:raise ValueError('Own-CDF allocation gate failed')
    return a,{'budget':total,'budget_error':err,'own_CDF_risk_baseline':rb,'own_CDF_risk_allocated':ra,'kkt_residual':kkt}


def fit_checked(train,base,variant,budget):
    if budget['fit_calls']>=MAX_FITS:raise RuntimeError('Candidate fit cap')
    budget['fit_calls']+=1
    return context.fit_context(train,base,variant)


def checkpoint():
    check(checkpoint=True);verify()
    if (OUT/'checkpoint.json').exists():raise FileExistsError('Checkpoint already exists')
    tests=json.loads((OUT/'synthetic-tests.json').read_text())
    budget={'fit_calls':tests['candidate_fit_calls'],'solver_calls':tests['solver_calls']}
    models=json.loads((SOURCE/'models.json').read_text());features,cube=load_features()
    ref=pd.read_parquet(SOURCE/'predictions.parquet',columns=['regime',*KEYS,'B','E11_coherent'])
    parts=[];logs=[];checks=[];ids=[];constants={}
    for label in REGIMES:
        check(checkpoint=True)
        base=models[label];train,log=source_training(base,cube,label);logs.append(log)
        const=train[[*FEATURES,'snpp']].copy();const['D']=0
        cm=fit_checked(const,base,'constant-control',budget);constants[label]=cm
        ff=features[features.regime==label].reset_index(drop=True)
        x,ds,_=raw_predictions(ff[FEATURES],base)
        reference=ref[ref.regime==label].set_index(KEYS).loc[pd.MultiIndex.from_frame(x[KEYS])]
        if not np.allclose(x.B,reference.B,atol=1e-10,rtol=0):raise ValueError('B21 identity failed')
        # Every query, SOURCE locals and held, both seen/unseen D, retains full old atoms.
        for i,row in ff.iterrows():
            for d in (0,1):
                actual,_=context.distribution(cm,base,row.cut,row.g,float(row.aqua),d)
                if not np.array_equal(actual[0],ds[i][0]) or not np.array_equal(actual[1],ds[i][1]):raise ValueError('Constant FULL-CDF identity failed')
        cfeatures=ff[FEATURES].copy();cfeatures['D']=0
        cds,_,_,_=context.predict_distributions(cfeatures,cm,base)
        x['G']=np.nan;x['G_constant']=np.nan
        for key,g in x.groupby(['season','m'],sort=True):
            check(checkpoint=True)
            if len(g)!=54:raise ValueError('54 monthly domain failed')
            ix=g.index.to_numpy();b=g.B.to_numpy(dtype=float)
            for method,dist in [('G',ds),('G_constant',cds)]:
                a,audit=allocate([dist[i] for i in ix],b,budget);x.loc[ix,method]=a
                checks.append(dict(regime=label,season=int(key[0]),m=int(key[1]),method=method,**audit))
        if not np.allclose(x.G,reference.E11_coherent,atol=1e-10,rtol=0) or not np.array_equal(x.G,x.G_constant):raise ValueError('G/full constant allocation failed')
        x['regime']=label;x['role']=np.where(x.cut.isin(base['source_cuts']),'SOURCE','held')
        x=x.merge(ff[[*KEYS,'D_real','D_placebo']],on=KEYS,validate='one_to_one')
        parts.append(x[['regime',*FEATURES,'D_real','D_placebo','role','B','G']])
        ids.append({'regime':label,'rows':len(x),'full_CDF_query_checks':2*len(x),'B_max_abs':float(np.max(np.abs(x.B.to_numpy()-reference.B.to_numpy()))),'G_max_abs':float(np.max(np.abs(x.G.to_numpy()-reference.E11_coherent.to_numpy()))),'G_constant_exact':True,'source_selected_rows':len(train)})
        print('37 identity:',label,flush=True)
    out=pd.concat(parts,ignore_index=True);out.to_parquet(OUT/'features-controls.parquet',index=False)
    dump(OUT/'constant_models.json',constants);dump(OUT/'source-selectors-checkpoint.json',logs)
    pd.DataFrame(checks).to_csv(OUT/'control_allocation_checks.csv',index=False)
    check(checkpoint=True);verify()
    record={'completed_utc':now().isoformat(),'all_checkpoint_gates_passed':True,'identities':ids,'counts':budget,'code_freeze_sha256':sha(OUT/'code-freeze.json'),'feature_control_sha256':sha(OUT/'features-controls.parquet'),'no_evaluation_response_join':True,'SOURCE_labels_read_per_regime_only':True}
    dump(OUT/'checkpoint.json',record)
    print('37 CHECKPOINT:',sha(OUT/'checkpoint.json'),flush=True)


def predictions():
    verify();cp=json.loads((OUT/'checkpoint.json').read_text())
    if not cp['all_checkpoint_gates_passed'] or sha(OUT/'features-controls.parquet')!=cp['feature_control_sha256']:raise ValueError('Missing valid checkpoint')
    if (OUT/'prediction-freeze.json').exists():raise FileExistsError('Prediction freeze exists')
    budget=dict(cp['counts']);models=json.loads((SOURCE/'models.json').read_text());features,cube=load_features()
    control=pd.read_parquet(OUT/'features-controls.parquet');out=[];saved={};logs=[];checks=[];support=[];proofs=[]
    for label in REGIMES:
        check();base=models[label];training,log=source_training(base,cube,label);logs.append(log)
        f=control[control.regime==label].reset_index(drop=True).copy();f['Q_real']=np.nan;f['Q_placebo']=np.nan
        saved[label]={}
        for variant,column in [('real','D_real'),('placebo','D_placebo')]:
            t=training[[*FEATURES,'snpp',column]].rename(columns={column:'D'})
            model=fit_checked(t,base,variant,budget)
            saved[label][variant]=model
            query=f[FEATURES+[column]].rename(columns={column:'D'})
            ds,med,prob,meta=context.predict_distributions(query,model,base)
            f['median_'+variant]=med;f['p_'+variant]=prob
            support.extend(dict(regime=label,variant=variant,**r) for r in meta)
            for key,g in f.groupby(['season','m'],sort=True):
                if len(g)!=54:raise ValueError('54 monthly domain failed')
                ix=g.index.to_numpy();a,audit=allocate([ds[i] for i in ix],g.B.to_numpy(dtype=float),budget)
                f.loc[ix,'Q_'+variant]=a
                checks.append(dict(regime=label,season=int(key[0]),m=int(key[1]),method='Q_'+variant,**audit))
            # Real-label SOURCE fit plus only SYNTHETIC forbidden labels; no actual held Y loaded.
            if variant=='real':
                forbidden=cube[~(cube.cut.isin(base['source_cuts'])&cube.season.isin(base['origin_seasons']))][FEATURES+[column]].rename(columns={column:'D'}).copy()
                forbidden['snpp']=np.where(np.arange(len(forbidden))%2==0,np.nan,999999.)
                poisoned=pd.concat([t,forbidden],ignore_index=True)
                checkmodel=fit_checked(poisoned,base,variant,budget)
                if context.signature(model)!=context.signature(checkmodel):raise ValueError('Forbidden-label poison changed SOURCE model')
                proofs.append({'regime':label,'variant':variant,'same_parameters_after_forbidden_synthetic_NaN_or_999999':True,'forbidden_rows':len(forbidden),'actual_forbidden_Y_loaded':False,'prediction_function_exact_feature_whitelist':True})
        if not np.isfinite(f[list(METHODS)].to_numpy()).all() or (f[list(METHODS)]<0).any().any():raise ValueError('Invalid candidate output')
        out.append(f);print('37 candidates:',label,flush=True)
    p=pd.concat(out,ignore_index=True)
    p.to_parquet(OUT/'predictions-before-evaluation-labels.parquet',index=False)
    dump(OUT/'candidate-models.json',saved);dump(OUT/'source-selectors-fit.json',logs);dump(OUT/'label-invariance.json',proofs)
    pd.DataFrame(support).to_csv(OUT/'query-support.csv',index=False);pd.DataFrame(checks).to_csv(OUT/'candidate_allocation_checks.csv',index=False)
    verify();check()
    record={'created_utc':now().isoformat(),'code_freeze_sha256':sha(OUT/'code-freeze.json'),'checkpoint_sha256':sha(OUT/'checkpoint.json'),'candidate_models_sha256':sha(OUT/'candidate-models.json'),'predictions_sha256':sha(OUT/'predictions-before-evaluation-labels.parquet'),'counts':budget,'all_gates_before_evaluation_passed':True,'no_evaluation_target_join_yet':True,'source_labels_per_regime_guarantee_not_global_noheldclaim':True,'rows':len(p),'peak_RSS_bytes':check()}
    dump(OUT/'prediction-freeze.json',record)
    print('37 PREDICTIONS FROZEN before evaluation:',sha(OUT/'prediction-freeze.json'),flush=True)


def metrics(frame):
    result={'n':len(frame),'target_sum':float(frame.snpp.sum()),'methods':{}}
    for method in METHODS:
        err=frame[method]-frame.snpp;totals=frame.groupby(['season','m'])[[method,'snpp']].sum()
        result['methods'][method]={'mae':float(err.abs().mean()) if len(frame) else None,'bias':float(err.mean()) if len(frame) else None,'prediction_sum':float(frame[method].sum()),'absolute_error_sum':float(err.abs().sum()),'regional_monthly_mae':float((totals[method]-totals.snpp).abs().mean()) if len(totals) else None}
    return result


def evaluate():
    verify();f=json.loads((OUT/'prediction-freeze.json').read_text())
    if not f['all_gates_before_evaluation_passed'] or sha(OUT/'predictions-before-evaluation-labels.parquet')!=f['predictions_sha256'] or sha(OUT/'candidate-models.json')!=f['candidate_models_sha256']:raise ValueError('Prediction/model freeze changed')
    if (OUT/'summary.json').exists():raise FileExistsError('Refuse evaluation overwrite')
    start=now().isoformat()
    p=pd.read_parquet(OUT/'predictions-before-evaluation-labels.parquet')
    y=pd.read_parquet(SOURCE/'predictions.parquet',columns=['regime',*KEYS,'snpp'])
    x=p.merge(y,on=['regime',*KEYS],validate='one_to_one')
    if len(x)!=10368 or not np.isfinite(x.snpp).all():raise ValueError('Evaluation join changed keys/labels')
    enabled,_=publication_metadata(sorted(x.cut.unique()));enabled=set(enabled)
    reports={};primary=[];percut=[];worst=[]
    for label,r in x.groupby('regime',sort=True):
        groups={'all54':r,'SOURCE':r[r.role=='SOURCE'],'held':r[r.role=='held'],'published14':r[r.cut.isin(enabled)],'remaining40':r[~r.cut.isin(enabled)]}
        for role in ('SOURCE','held'):
            for name,mask in [('published14',r.cut.isin(enabled)),('remaining40',~r.cut.isin(enabled))]:groups[role+'_'+name]=r[(r.role==role)&mask]
        reports[label]={}
        for name,g in groups.items():
            strata={'all_months':g,'zero_reference':g[g.snpp==0],'positive_reference':g[g.snpp>0],'aqua_zero_reference_positive':g[(g.aqua==0)&(g.snpp>0)],'both_zero':g[(g.aqua==0)&(g.snpp==0)],'reference_50_plus':g[g.snpp>=50]}
            reports[label][name]={k:metrics(v) for k,v in strata.items()}
        mm=reports[label]['held']['all_months'];scores=mm['methods']
        primary.append({'regime':label,'n':mm['n'],'B_mae':scores['B']['mae'],'G_mae':scores['G']['mae'],'real_mae':scores['Q_real']['mae'],'placebo_mae':scores['Q_placebo']['mae'],'delta_real_minus_placebo':scores['Q_real']['mae']-scores['Q_placebo']['mae'],'delta_real_minus_G':scores['Q_real']['mae']-scores['G']['mae']})
        rows=[]
        for cut,g in r.groupby('cut',sort=True):
            rr={'regime':label,'cut':cut,'role':str(g.role.iloc[0]),'n':len(g),**{k+'_mae':v['mae'] for k,v in metrics(g)['methods'].items()}};rows.append(rr);percut.append(rr)
        chosen=min([v for v in rows if v['role']=='held'],key=lambda v:(-v['G_mae'],v['cut']))
        worst.append({'regime':label,'cut':chosen['cut'],'selected_using':'historical frozen G MAE held; lexical tie; no prediction affected','metrics':metrics(r[r.cut==chosen['cut']])})
    meanrp=float(np.mean([p['delta_real_minus_placebo'] for p in primary]));meang=float(np.mean([p['delta_real_minus_G'] for p in primary]))
    n=sum(p['n'] for p in primary)
    summary={'status':'retrospective-SOURCE-only-daily-context-CDF','new_fits':f['counts']['fit_calls'],'counts':f['counts'],'independent_validation':False,'gate1_physical':False,'new_downloads':0,'new_hyperparameter_searches':0,'primary':{'regimes':primary,'equal_four_real_minus_placebo':meanrp,'equal_four_real_minus_G':meang,'both_required_contrasts_negative':bool(meanrp<0 and meang<0),'row_weighted_real_minus_placebo':float(sum(p['delta_real_minus_placebo']*p['n'] for p in primary)/n),'row_weighted_real_minus_G':float(sum(p['delta_real_minus_G']*p['n'] for p in primary)/n),'dependent_regimes_not_IID':True},'reports':reports,'worst_CUT_fixed_from_historical_G':worst,'SOURCE_guarantee_per_regime_not_global_noheld':True,'positive_count_is_registered_SNPP_not_physical_fire':True,'normalization_and_B_unchanged':True,'G21_original_and35_negative_unchanged':True,'first_evaluation_response_join_utc':start}
    x.to_parquet(OUT/'evaluated_predictions.parquet',index=False);pd.DataFrame(primary).to_csv(OUT/'primary_contrasts.csv',index=False);pd.DataFrame(percut).to_csv(OUT/'per_CUT.csv',index=False);dump(OUT/'summary.json',summary)
    verify();check();files=[p for p in OUT.iterdir() if p.is_file()]
    dump(OUT/'manifest.json',{'completed_utc':now().isoformat(),'protected_unchanged':True,'output_sha256':{p.name:sha(p) for p in files},'counts':f['counts'],'physical_bytes_before_manifest':sum(p.stat().st_size for p in files),'rows':len(x),'peak_RSS_bytes':check(),'RSS_unit':'bytes; darwin native/LinuxKiBconverted','code_freeze_sha256':sha(OUT/'code-freeze.json'),'prediction_freeze_sha256':sha(OUT/'prediction-freeze.json'),'cap_end_utc':END})
    print('37 evaluation complete',flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['freeze','checkpoint','predict','evaluate']);arg=ap.parse_args()
    {'freeze':freeze,'checkpoint':checkpoint,'predict':predictions,'evaluate':evaluate}[arg.action]()
