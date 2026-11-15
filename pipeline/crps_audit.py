"""39: CRPS audit of frozen21 marginal distributions, no fits or solvers."""
import argparse,gzip,hashlib,importlib.metadata,json,math,platform,resource,sys,unittest
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from scientific_audit import ROOT,DATA,sha
from cold_region_audit import raw_predictions,FEATURES,REGIMES,fingerprint
from frozen_temporal_audit import KEYS,publication_metadata
from crps_score import prepare,score_prepared

SOURCE=DATA/'cold_region_audit';OUT=DATA/'crps_audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-15-crps-protocol.md'
EXPECTED_PROTOCOL='ef2be85264a1e91b334e4aabcc6e28feceeaf2556f002946a43f52737cc2bd38'
START='2026-11-15T08:43:00+00:00';CHECKPOINT='2026-11-15T09:03:00+00:00';END='2026-11-15T10:13:00+00:00'
FORECASTS=('F21','delta_B')


def now():return datetime.now(timezone.utc)
def dump(path,obj):path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def check(checkpoint=False):
    if now()>=datetime.fromisoformat(CHECKPOINT if checkpoint else END):raise TimeoutError('39 absolute cap')
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024)
    if rss>2*1024**3:raise MemoryError('2GiB cap')
    if OUT.exists() and sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())>100*1024**2:raise RuntimeError('100MiB output cap')
    return rss


def snapshot():return {str(p.relative_to(ROOT)):sha(p) for p in list(DATA.rglob('*'))+list((ROOT/'web/public/data').rglob('*.json')) if p.is_file() and OUT not in p.parents}


def freeze():
    check(checkpoint=True)
    if sha(PROTOCOL)!=EXPECTED_PROTOCOL:raise ValueError('Authorized protocol changed')
    if OUT.exists():raise FileExistsError('39 exclusive directory exists')
    source=json.loads((SOURCE/'manifest.json').read_text())
    for name in ('models.json','predictions.parquet','candidate_mask.csv'):
        if sha(SOURCE/name)!=source['output_sha256'][name]:raise ValueError('Frozen21 input changed')
    code=[Path(__file__),ROOT/'pipeline/crps_score.py',ROOT/'tests/test_crps_score.py',ROOT/'pipeline/cold_region_audit.py',ROOT/'pipeline/hurdle_model.py',ROOT/'pipeline/coherent_allocation.py',ROOT/'pipeline/scientific_audit.py',ROOT/'pipeline/affine_experiment.py']
    inputs=list(SOURCE.iterdir())+[ROOT/'uv.lock',ROOT/'pyproject.toml']
    OUT.mkdir(parents=True)
    record={'created_utc':now().isoformat(),'protocol_sha256':sha(PROTOCOL),'code_sha256':{str(p.relative_to(ROOT)):sha(p) for p in code},'input_sha256':{str(p.relative_to(ROOT)):sha(p) for p in inputs if p.is_file()},'protected_sha256':snapshot(),'environment':{'python':platform.python_version(),'platform':platform.platform(),'packages':{name:importlib.metadata.version(name) for name in ('numpy','pandas','pyarrow','duckdb','shapely')},'uv_lock_sha256':sha(ROOT/'uv.lock')},'cap':{'start':START,'checkpoint':CHECKPOINT,'end':END},'resource_limits':{'export_rows':1000000,'physical_bytes':100*1024**2,'RSS_bytes':2*1024**3,'fits':0,'solvers':0,'science_downloads':0},'source_schema':str(pq.read_schema(SOURCE/'predictions.parquet')),'actual_CDF_and_scores_not_yet_reconstructed':True}
    dump(OUT/'code-freeze.json',record)
    sys.path.insert(0,str(ROOT/'tests'))
    suite=unittest.defaultTestLoader.loadTestsFromName('test_crps_score');result=unittest.TextTestRunner(verbosity=1).run(suite)
    dump(OUT/'fixtures.json',{'completed_utc':now().isoformat(),'tests':result.testsRun,'passed':result.wasSuccessful(),'oracle':'independent CDF integral plus Fraction double-sum analytic fixtures','only_synthetic_Y':True,'fits':0,'solvers':0})
    if not result.wasSuccessful():raise ValueError('CRPS/oracle fixtures failed')
    print('39 code freeze before fixtures/data:',sha(OUT/'code-freeze.json'),flush=True)


def verify():
    check();f=json.loads((OUT/'code-freeze.json').read_text())
    if sha(PROTOCOL)!=f['protocol_sha256']:raise ValueError('Protocol changed')
    for group in ('code_sha256','input_sha256','protected_sha256'):
        for key,value in f[group].items():
            if sha(ROOT/key)!=value:raise ValueError('Frozen source changed: '+key)
    return f


def checkpoint():
    verify();check(checkpoint=True)
    if (OUT/'checkpoint.json').exists():raise FileExistsError('Checkpoint exists')
    fixtures=json.loads((OUT/'fixtures.json').read_text())
    if not fixtures['passed']:raise ValueError('Oracle fixtures absent')
    cols=['regime',*FEATURES,'role','B','E11','E11_mean']
    control=pd.read_parquet(SOURCE/'predictions.parquet',columns=cols)
    if len(control)!=10368 or control.duplicated(['regime',*KEYS]).any():raise ValueError('Fixed21 keys changed')
    models=json.loads((SOURCE/'models.json').read_text());source=json.loads((SOURCE/'manifest.json').read_text())
    identities=[];roster=[];rowid=0;natoms=0;held_checks=0
    with (OUT/'forecast-CDFs.jsonl.gz').open('wb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as compressed:
        for label in REGIMES:
            check(checkpoint=True);base=models[label]
            if fingerprint(base)!=source['model_sha256'][label]:raise ValueError('Model21 changed')
            frame=control[control.regime==label].reset_index(drop=True)
            x,ds,parents=raw_predictions(frame[FEATURES],base)
            for name,ref in [('B','B'),('E11','E11'),('E11_mean','E11_mean')]:
                if not np.allclose(x[name],frame[ref],atol=1e-10,rtol=0):raise ValueError('Frozen control identity failed: '+name)
            role=np.where(x.cut.isin(base['source_cuts']),'SOURCE','held')
            if not np.array_equal(role,frame.role):raise ValueError('Role roster changed')
            for _,group in x.groupby(['season','m']):
                if len(group)!=54 or len(set(group.cut))!=54:raise ValueError('54-CUT monthly roster failed')
            maxima={'B':0.,'median':0.,'mean':0.}
            for i,row in x.iterrows():
                if rowid%100==0:check(checkpoint=True)
                values,rawweights=ds[i];values,weights,rawsum=prepare(values,rawweights)
                if (values<0).any():raise ValueError('Negative SNP-scale atom')
                mean=math.fsum(float(a)*float(v) for v,a in zip(values,weights))
                if abs(mean-float(row.E11_mean))>1e-10:raise ValueError('Normalized-CDF mean identity failed')
                # Median uses original21 zero-mass/positive lower-quantile convention.
                # Normalization by a few ulps must not redefine a p=.5 boundary.
                median=float(row.E11)
                if role[i]=='held':
                    if not np.array_equal(values,parents[i][0]) or not np.array_equal(rawweights,parents[i][1]):raise ValueError('Held E11/parent CDF identity failed')
                    held_checks+=1
                maxima['B']=max(maxima['B'],abs(float(row.B)-float(frame.B.iloc[i])))
                maxima['median']=max(maxima['median'],abs(median-float(frame.E11.iloc[i])))
                maxima['mean']=max(maxima['mean'],abs(mean-float(frame.E11_mean.iloc[i])))
                record={'row_id':rowid,'regime':label,'cut':str(row.cut),'season':int(row.season),'m':int(row.m),'g':str(row.g),'aqua':int(row.aqua),'role':str(role[i]),'B':float(row.B),'F21_median':median,'F21_mean':mean,'original_E11_mean':float(row.E11_mean),'model_sha256':fingerprint(base),'original_weight_sum':rawsum,'atoms':values.tolist(),'original_weights':rawweights.tolist(),'normalized_weights':weights.tolist()}
                compressed.write((json.dumps(record,separators=(',',':'),allow_nan=False)+'\n').encode())
                roster.append({k:v for k,v in record.items() if k not in ('atoms','original_weights','normalized_weights')})
                natoms+=len(values);rowid+=1
            identities.append({'regime':label,'rows':len(frame),'max_abs_identity_errors':maxima,'full_CDF_restored_without_fit_or_solver':True})
            print('39 restored:',label,flush=True)
    if rowid!=10368:raise ValueError('CDF roster incomplete')
    pd.DataFrame(roster).to_parquet(OUT/'forecast-roster.parquet',index=False)
    verify();check(checkpoint=True)
    dump(OUT/'checkpoint.json',{'completed_utc':now().isoformat(),'all_identities_and_fixtures_passed':True,'identities':identities,'rows':rowid,'atom_elements':natoms,'held_E11_parent_exact_checks':held_checks,'original_weight_policy':'preserve zero/tied atoms; normalize rawweights once by fsum','CDF_snapshot_sha256':sha(OUT/'forecast-CDFs.jsonl.gz'),'roster_sha256':sha(OUT/'forecast-roster.parquet'),'code_freeze_sha256':sha(OUT/'code-freeze.json'),'no_real_response_join_or_score_yet':True,'fits':0,'solvers':0,'science_downloads':0,'peak_RSS_bytes':check(checkpoint=True)})
    print('39 CHECKPOINT/full-CDF freeze:',sha(OUT/'checkpoint.json'),flush=True)


def metrics(frame):
    return {'n':len(frame),'forecasts':{name:{'sum_CRPS':math.fsum(float(v) for v in frame['CRPS_'+name]),'mean_CRPS':float(frame['CRPS_'+name].mean()) if len(frame) else None} for name in FORECASTS},'mean_difference_F21_minus_delta_B':float((frame.CRPS_F21-frame.CRPS_delta_B).mean()) if len(frame) else None}


def evaluate():
    verify();cp=json.loads((OUT/'checkpoint.json').read_text())
    if not cp['all_identities_and_fixtures_passed'] or sha(OUT/'forecast-CDFs.jsonl.gz')!=cp['CDF_snapshot_sha256'] or sha(OUT/'forecast-roster.parquet')!=cp['roster_sha256']:raise ValueError('CDF/roster freeze absent or changed')
    if (OUT/'summary.json').exists():raise FileExistsError('Refuse score overwrite')
    firstY=now().isoformat();roster=pd.read_parquet(OUT/'forecast-roster.parquet')
    labels=pd.read_parquet(SOURCE/'predictions.parquet',columns=['regime',*KEYS,'snpp'])
    if not np.isfinite(labels.snpp).all() or (labels.snpp<0).any():raise ValueError('Invalid response')
    grp=labels.groupby(KEYS).snpp
    if not grp.size().eq(2).all() or not grp.nunique().eq(1).all():raise ValueError('Duplicate target copies disagree')
    x=roster.merge(labels,on=['regime',*KEYS],validate='one_to_one')
    if len(x)!=10368 or x.snpp.isna().any():raise ValueError('Evaluation keys changed')
    x=x.sort_values('row_id').reset_index(drop=True);score_rows=[]
    with gzip.open(OUT/'forecast-CDFs.jsonl.gz','rt') as stream:
        for line in stream:
            record=json.loads(line);i=record['row_id'];r=x.iloc[i]
            if i%100==0:check()
            if (record['regime'],record['cut'],record['season'],record['m'])!=(r.regime,r.cut,int(r.season),int(r.m)):raise ValueError('Frozen CDF/query mismatch')
            value=score_prepared(record['atoms'],record['normalized_weights'],float(r.snpp))
            # delta_B has unit weight, so no second normalization is required.
            delta=score_prepared([float(r.B)],[1.],float(r.snpp))
            mae=abs(float(r.B)-float(r.snpp))
            if abs(delta['score']-mae)>delta['tolerance']:raise ValueError('Delta CRPS != baseline MAE')
            score_rows.append({'row_id':i,'CRPS_F21':value['score'],'CRPS_delta_B':delta['score'],'F21_raw_score':value['raw_score'],'F21_tolerance':value['tolerance'],'F21_negative_roundoff_clamped':value['negative_roundoff_clamped'],'F21_Eabs':value['expected_absolute_error'],'F21_half_pair_term':value['half_pair_term'],'F21_EabsX':value['EabsX'],'delta_B_MAE':mae})
    if len(score_rows)!=10368:raise ValueError('Score roster incomplete')
    x=x.merge(pd.DataFrame(score_rows),on='row_id',validate='one_to_one')
    enabled,_=publication_metadata(sorted(x.cut.unique()));enabled=set(enabled)
    reports={};primary=[];percut=[];worst=[]
    for label,f in x.groupby('regime',sort=True):
        groups={'all54':f,'SOURCE':f[f.role=='SOURCE'],'held':f[f.role=='held'],'published14':f[f.cut.isin(enabled)],'remaining40':f[~f.cut.isin(enabled)]}
        for role in ('SOURCE','held'):
            groups[role+'_published14']=f[(f.role==role)&f.cut.isin(enabled)];groups[role+'_remaining40']=f[(f.role==role)&~f.cut.isin(enabled)]
        reports[label]={}
        for name,g in groups.items():
            strata={'all_months':g,'zero_reference':g[g.snpp==0],'positive_reference':g[g.snpp>0],'aqua_zero_reference_positive':g[(g.aqua==0)&(g.snpp>0)],'both_zero':g[(g.aqua==0)&(g.snpp==0)],'reference_50_plus':g[g.snpp>=50]}
            reports[label][name]={k:metrics(v) for k,v in strata.items()}
        h=reports[label]['held']['all_months'];primary.append({'regime':label,'n':h['n'],'mean_CRPS_F21':h['forecasts']['F21']['mean_CRPS'],'mean_CRPS_delta_B':h['forecasts']['delta_B']['mean_CRPS'],'difference_F21_minus_delta_B':h['mean_difference_F21_minus_delta_B']})
        rows=[]
        for cut,g in f.groupby('cut',sort=True):
            mm=metrics(g);rr={'regime':label,'cut':cut,'role':str(g.role.iloc[0]),'n':len(g),'mean_CRPS_F21':mm['forecasts']['F21']['mean_CRPS'],'mean_CRPS_delta_B':mm['forecasts']['delta_B']['mean_CRPS'],'difference':mm['mean_difference_F21_minus_delta_B']};rows.append(rr);percut.append(rr)
        selected=min([r for r in rows if r['role']=='held'],key=lambda r:(-r['mean_CRPS_delta_B'],r['cut']))
        worst.append({'regime':label,'cut':selected['cut'],'selection':'worst original held B MAE; lex CUT tie; no CDF affected','metrics':metrics(f[f.cut==selected['cut']])})
    summary={'status':'retrospective-frozen21-marginal-CDF-CRPS-audit','primary':{'definition':'equal-four held CRPS(F21)-MAE(B); lower better','regimes':primary,'equal_four_difference':float(np.mean([p['difference_F21_minus_delta_B'] for p in primary])),'row_weighted_difference':float(sum(p['difference_F21_minus_delta_B']*p['n'] for p in primary)/sum(p['n'] for p in primary)),'dependent_regimes_not_IID':True},'reports':reports,'worst_CUT_fixed_from_original_B_MAE':worst,'fits':0,'solvers':0,'science_downloads':0,'independent_validation':False,'gate1_physical':False,'calibration_or_pure_spread_claim':False,'joint54_CDF_claim':False,'forecasts_only':['F21','delta_B'],'first_real_response_join_utc':firstY,'negative_roundoff_clamped_rows':int(x.F21_negative_roundoff_clamped.sum()),'prior23_35_37_negative_unchanged':True}
    x.to_parquet(OUT/'scored-queries.parquet',index=False);pd.DataFrame(primary).to_csv(OUT/'primary-contrasts.csv',index=False);pd.DataFrame(percut).to_csv(OUT/'per-CUT.csv',index=False);dump(OUT/'summary.json',summary)
    verify();check();files=[p for p in OUT.iterdir() if p.is_file()]
    dump(OUT/'manifest.json',{'completed_utc':now().isoformat(),'output_sha256':{p.name:sha(p) for p in files},'code_freeze_sha256':sha(OUT/'code-freeze.json'),'CDF_freeze_sha256':sha(OUT/'checkpoint.json'),'protected_unchanged':True,'fits':0,'solvers':0,'science_downloads':0,'exported_query_rows':len(x),'atom_elements':cp['atom_elements'],'physical_bytes_before_manifest':sum(p.stat().st_size for p in files),'peak_RSS_bytes':check(),'cap_end_utc':END})
    print('39 evaluation complete',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','checkpoint','evaluate']);a=p.parse_args()
    {'freeze':freeze,'checkpoint':checkpoint,'evaluate':evaluate}[a.action]()
