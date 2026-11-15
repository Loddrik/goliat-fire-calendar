"""Protocol35: fixed-CDF group budgets; labels enter only after prediction freeze."""
import argparse
import hashlib
import json
import math
import platform
import resource
import subprocess
import sys
import unittest
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from scientific_audit import ROOT, DATA, sha
from cold_region_audit import raw_predictions, fingerprint, FEATURES, REGIMES
from coherent_allocation import reconcile, expected_risk, kkt_residual
from frozen_temporal_audit import KEYS, publication_metadata

OUT=DATA/'group_budget_audit'
SOURCE=DATA/'cold_region_audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-15-group-budget-protocol.md'
EXPECTED_PROTOCOL='a1107de9e9c1256f8e6a502d868e9d536fca5a624d50257d514750e7a73f778c'
CHECKPOINT='2026-11-15T07:34:05+00:00'
END='2026-11-15T08:04:05+00:00'
METHODS=('B','G','R','P','C')
TOTAL_SOLVER_CALLS=0


def now():return datetime.now(timezone.utc)
def clock_check(checkpoint=False):
    if now()>=datetime.fromisoformat(CHECKPOINT if checkpoint else END):raise TimeoutError('Absolute35 cap reached')
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes=rss if sys.platform=='darwin' else rss*1024
    if rss_bytes>2*1024**3:raise MemoryError('2GiB RSS cap')
    return rss_bytes


def write_json(path,obj):
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')


@dataclass
class Budget:
    calls:int=0
    limit:int=2000
    check:object=None

    def call(self,ds,b):
        global TOTAL_SOLVER_CALLS
        if self.check:self.check()
        if self.calls>=self.limit:raise RuntimeError('Solver call cap')
        self.calls+=1;TOTAL_SOLVER_CALLS+=1
        return reconcile(ds,b)


def allocate_groups(distributions,baseline,groups,budget=None):
    """Pure inputs only; no features, labels, clock or filesystem are consulted."""
    budget=Budget() if budget is None else budget
    b=np.asarray(baseline,dtype=float);groups=list(groups);ds=list(distributions)
    if b.ndim!=1 or len(b)!=len(ds) or len(groups)!=len(b) or not len(b):raise ValueError('Shape mismatch')
    if not np.isfinite(b).all() or (b<0).any():raise ValueError('Invalid baseline')
    result=np.full(len(b),np.nan);checks=[]
    for name in sorted(set(groups)):
        ix=np.array([i for i,g in enumerate(groups) if g==name],dtype=int)
        d=[ds[i] for i in ix];bb=b[ix];a=budget.call(d,bb)
        total=math.fsum(float(v) for v in bb);err=math.fsum(float(v) for v in a)-total
        if abs(err)>1e-10*max(1,total):raise ValueError('Group budget mismatch')
        residual=kkt_residual(d,a)
        if residual>1e-8:raise ValueError('Group KKT failed')
        before=expected_risk(d,bb);after=expected_risk(d,a)
        if after>before+1e-8*max(1,before):raise ValueError('Group risk exceeds baseline')
        result[ix]=a;checks.append({'group':str(name),'n':len(ix),'budget':total,'budget_error':err,'kkt_residual':float(residual),'risk_baseline':before,'risk_allocated':after})
    if not np.isfinite(result).all() or (result<0).any():raise ValueError('Invalid allocation')
    return result,checks


def partition(cuts):
    cuts=sorted(map(str,cuts))
    ranked=sorted(cuts,key=lambda c:(hashlib.sha256(('goliat-council35-partition-v1|'+c).encode()).digest(),c))
    return {c:('P33' if i<33 else 'P21') for i,c in enumerate(ranked)}


def protected_snapshot():
    paths=[p for p in DATA.rglob('*') if p.is_file() and OUT not in p.parents]
    paths+=list((ROOT/'web/public/data').rglob('*.json'))
    return {str(p.relative_to(ROOT)):sha(p) for p in paths}


def freeze():
    clock_check(checkpoint=True)
    if sha(PROTOCOL)!=EXPECTED_PROTOCOL:raise ValueError('Protocol differs from authorized freeze')
    if OUT.exists() and any(OUT.iterdir()):raise ValueError('Refuse existing output directory')
    sys.path.insert(0,str(ROOT/'tests'))
    suite=unittest.defaultTestLoader.loadTestsFromName('test_group_budget_audit')
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():raise ValueError('Synthetic gates failed')
    OUT.mkdir(parents=True,exist_ok=True)
    models=json.loads((SOURCE/'models.json').read_text())
    prior=json.loads((SOURCE/'manifest.json').read_text())
    for name in ('models.json','predictions.parquet','candidate_mask.csv'):
        if sha(SOURCE/name)!=prior['output_sha256'][name]:raise ValueError('21 source hash mismatch: '+name)
    for key,value in prior['model_sha256'].items():
        if fingerprint(models[key])!=value:raise ValueError('Model signature mismatch')
    cuts=sorted(set(c for m in models.values() for c in m['source_cuts']))
    if len(cuts)!=54 or sum(c.startswith('08') for c in cuts)!=33 or sum(c.startswith('16') for c in cuts)!=21:raise ValueError('Fixed territory mismatch')
    mask=pd.read_csv(SOURCE/'candidate_mask.csv')
    if len(mask)!=6:raise ValueError('Mask6 mismatch')
    parts=partition(cuts)
    write_json(OUT/'partitions.json',{'hash_prefix':'goliat-council35-partition-v1|','real':{c:c[:2] for c in cuts},'artificial':parts,'cuts':cuts})
    import pyarrow.parquet as pq
    meta=pq.read_metadata(SOURCE/'predictions.parquet')
    code=[Path(__file__),ROOT/'tests/test_group_budget_audit.py',ROOT/'pipeline/cold_region_audit.py',ROOT/'pipeline/coherent_allocation.py',ROOT/'pipeline/hurdle_model.py',ROOT/'pipeline/affine_experiment.py',ROOT/'pipeline/scientific_audit.py']
    rec={'created_utc':now().isoformat(),'cap_start_utc':'2026-11-15T07:19:05Z','cap_end_utc':END,'checkpoint_utc':CHECKPOINT,'protocol_sha256':sha(PROTOCOL),'code_sha256':{str(p.relative_to(ROOT)):sha(p) for p in code},'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in SOURCE.iterdir() if p.is_file()},'protected_sha256':protected_snapshot(),'model_sha256':prior['model_sha256'],'partition_sha256':sha(OUT/'partitions.json'),'synthetic_solver_calls':TOTAL_SOLVER_CALLS,'synthetic_tests':result.testsRun,'schema':str(meta.schema),'source_rows':meta.num_rows,'no_predictions_or_targets_read':True}
    write_json(OUT/'code-freeze.json',rec)
    print('FROZEN before new predictions/target values:',sha(OUT/'code-freeze.json'),flush=True)
    return rec


def validate_freeze():
    rec=json.loads((OUT/'code-freeze.json').read_text())
    if sha(PROTOCOL)!=rec['protocol_sha256']:raise ValueError('Protocol changed')
    for group in ('code_sha256','source_sha256','protected_sha256'):
        for key,value in rec[group].items():
            if sha(ROOT/key)!=value:raise ValueError('Frozen input changed: '+key)
    if sha(OUT/'partitions.json')!=rec['partition_sha256']:raise ValueError('Partition changed')
    return rec


def predictions():
    clock_check(checkpoint=True);rec=validate_freeze()
    budget=Budget(calls=rec['synthetic_solver_calls'],check=lambda:clock_check(checkpoint=True))
    models=json.loads((SOURCE/'models.json').read_text());parts=json.loads((OUT/'partitions.json').read_text())
    # Parquet column projection never materializes target labels in this phase.
    features=pd.read_parquet(SOURCE/'predictions.parquet',columns=['regime',*FEATURES])
    reference=pd.read_parquet(SOURCE/'predictions.parquet',columns=['regime',*KEYS,'B','E11_coherent'])
    if len(features)!=10368 or features.duplicated(['regime',*KEYS]).any():raise ValueError('21 panel keys changed')
    features.to_parquet(OUT/'features-only.parquet',index=False)
    pieces=[];checks=[];diagnostics=[];identities=[]
    for label in REGIMES:
        clock_check(checkpoint=True)
        ff=features[features.regime==label][FEATURES].copy().reset_index(drop=True)
        model=models[label];signature=fingerprint(model)
        x,ds,_=raw_predictions(ff,model)
        ref=reference[reference.regime==label].set_index(KEYS).loc[pd.MultiIndex.from_frame(x[KEYS])]
        if not np.allclose(x.B,ref.B,atol=1e-10,rtol=0):raise ValueError('B failed21 identity')
        x['G']=np.nan;x['R']=np.nan;x['P']=np.nan
        source=set(model['source_cuts']);x['role']=np.where(x.cut.isin(source),'SOURCE','held')
        for key,g in x.groupby(['season','m'],sort=True):
            if len(g)!=54 or sorted(g.cut)!=parts['cuts']:raise ValueError('Incomplete54 month')
            ix=g.index.to_numpy();d=[ds[i] for i in ix];b=g.B.to_numpy(dtype=float)
            rr=[]
            for method,groups in [('G',['ALL']*54),('R',[c[:2] for c in g.cut]),('P',[parts['artificial'][c] for c in g.cut])]:
                a,audit=allocate_groups(d,b,groups,budget)
                x.loc[ix,method]=a
                checks.extend(dict(regime=label,season=int(key[0]),m=int(key[1]),method=method,**c) for c in audit)
                rr.append(expected_risk(d,a))
            rb=expected_risk(d,b);tol=1e-8*max(1,rb)
            if rr[0]>rr[1]+tol or rr[0]>rr[2]+tol or max(rr)>rb+tol:raise ValueError('Constrained CDF risk ordering failed')
            for method,risk in zip(('G','R','P'),rr):
                a=x.loc[ix,method].to_numpy(dtype=float);held=g.role.to_numpy()=='held'
                transfer_h=math.fsum(float(v) for v in (a-b)[held]);transfer_s=math.fsum(float(v) for v in (a-b)[~held])
                if abs(transfer_h+transfer_s)>1e-10*max(1,math.fsum(b)):raise ValueError('Transfer closure failed')
                if method=='R' and abs(transfer_h)>1e-10*max(1,math.fsum(b[held])):raise ValueError('R held transfer not zero')
                diagnostics.append(dict(regime=label,season=int(key[0]),m=int(key[1]),method=method,L1_to_B=float(np.abs(a-b).sum()),risk= risk,excess_risk_over_G=risk-rr[0],transfer_held=transfer_h,transfer_SOURCE=transfer_s))
        if not np.allclose(x.G,ref.E11_coherent,atol=1e-10,rtol=0):raise ValueError('G failed21 identity')
        if fingerprint(model)!=signature:raise ValueError('Model mutated')
        x['C']=(x.B+x.G)/2;x['regime']=label
        if not np.isfinite(x[list(METHODS)].to_numpy()).all():raise ValueError('Invalid fixed decisions')
        identities.append({'regime':label,'rows':len(x),'B_max_abs':float(np.max(np.abs(x.B.to_numpy()-ref.B.to_numpy()))),'G_max_abs':float(np.max(np.abs(x.G.to_numpy()-ref.E11_coherent.to_numpy()))),'model_unchanged':True})
        pieces.append(x[['regime',*FEATURES,'role',*METHODS]])
        print('IDENTITY ready:',label,flush=True)
    out=pd.concat(pieces,ignore_index=True)
    out.to_parquet(OUT/'predictions-before-labels.parquet',index=False)
    pd.DataFrame(checks).to_csv(OUT/'allocation_checks.csv',index=False)
    pd.DataFrame(diagnostics).to_csv(OUT/'decision_diagnostics.csv',index=False)
    clock_check(checkpoint=True)
    record={'created_utc':now().isoformat(),'checkpoint_deadline_utc':CHECKPOINT,'all_identities_passed':True,'identities':identities,'source_feature_sha256':sha(OUT/'features-only.parquet'),'code_freeze_sha256':sha(OUT/'code-freeze.json'),'predictions_sha256':sha(OUT/'predictions-before-labels.parquet'),'no_targets_materialized':True,'synthetic_solver_calls':rec['synthetic_solver_calls'],'real_solver_calls':budget.calls-rec['synthetic_solver_calls'],'total_solver_calls':budget.calls,'peak_RSS_bytes':clock_check(checkpoint=True),'rows':len(out),'group_count_checks':len(checks)}
    write_json(OUT/'prediction-freeze.json',record)
    validate_freeze()
    print('CHECKPOINT PASSED before labels:',sha(OUT/'prediction-freeze.json'),flush=True)
    return record


def metrics(frame):
    result={'n':len(frame),'target_sum':float(frame.snpp.sum()),'methods':{}}
    for method in METHODS:
        error=frame[method]-frame.snpp
        totals=frame.groupby(['season','m'])[[method,'snpp']].sum()
        result['methods'][method]={'mae':float(error.abs().mean()) if len(frame) else None,'bias':float(error.mean()) if len(frame) else None,'prediction_sum':float(frame[method].sum()),'absolute_error_sum':float(error.abs().sum()),'regional_monthly_mae':float((totals[method]-totals.snpp).abs().mean()) if len(totals) else None,'L1_to_B':float((frame[method]-frame.B).abs().sum())}
    return result


def evaluate():
    clock_check();rec=validate_freeze();predfreeze=json.loads((OUT/'prediction-freeze.json').read_text())
    if not predfreeze['all_identities_passed'] or sha(OUT/'predictions-before-labels.parquet')!=predfreeze['predictions_sha256']:raise ValueError('Missing valid prediction freeze')
    x=pd.read_parquet(OUT/'predictions-before-labels.parquet')
    labels=pd.read_parquet(SOURCE/'predictions.parquet',columns=['regime',*KEYS,'snpp'])
    x=x.merge(labels,on=['regime',*KEYS],validate='one_to_one')
    if len(x)!=10368 or x.snpp.isna().any():raise ValueError('Target join changed cohort')
    if not np.all(np.abs(x.C-x.snpp)<=.5*(np.abs(x.B-x.snpp)+np.abs(x.G-x.snpp))+1e-10):raise ValueError('Pointwise L1 convexity failed')
    enabled,_=publication_metadata(sorted(x.cut.unique()));enabled=set(enabled)
    reports={};primary=[];cuts=[];worst=[]
    for regime,f in x.groupby('regime',sort=True):
        clock_check();groups={'all54':f,'SOURCE':f[f.role=='SOURCE'],'held':f[f.role=='held'],'published14':f[f.cut.isin(enabled)],'remaining40':f[~f.cut.isin(enabled)]}
        for role in ('SOURCE','held'):
            groups[role+'_published14']=f[(f.role==role)&f.cut.isin(enabled)]
            groups[role+'_remaining40']=f[(f.role==role)&~f.cut.isin(enabled)]
        reports[regime]={}
        for name,g in groups.items():
            strata={'all_months':g,'zero_reference':g[g.snpp==0],'positive_reference':g[g.snpp>0],'aqua_zero_reference_positive':g[(g.aqua==0)&(g.snpp>0)],'both_zero':g[(g.aqua==0)&(g.snpp==0)],'reference_50_plus':g[g.snpp>=50]}
            reports[regime][name]={s:metrics(t) for s,t in strata.items()}
        h=reports[regime]['held']['all_months'];delta=h['methods']['R']['mae']-h['methods']['G']['mae']
        primary.append({'regime':regime,'n_held':h['n'],'G_mae':h['methods']['G']['mae'],'R_mae':h['methods']['R']['mae'],'delta_R_minus_G':delta,'absolute_error_delta':h['methods']['R']['absolute_error_sum']-h['methods']['G']['absolute_error_sum']})
        for cut,c in f.groupby('cut',sort=True):
            mm=metrics(c);cuts.append({'regime':regime,'cut':cut,'role':str(c.role.iloc[0]),'n':len(c),**{method+'_mae':mm['methods'][method]['mae'] for method in METHODS}})
        heldcuts=[c for c in cuts if c['regime']==regime and c['role']=='held']
        selected=min(heldcuts,key=lambda c:(-c['G_mae'],c['cut']))
        worst.append({'regime':regime,'selection':'worst historical G control held-CUT; lex CUT tie; selection affects no predictions','cut':selected['cut'],'metrics':metrics(f[f.cut==selected['cut']])})
    summary={'status':'retrospective-fixed-CDF-group-budget-decision-sensitivity','independent_validation':False,'gate1_physical':False,'ecological_or_causal_claim':False,'new_fits':0,'new_downloads':0,'new_hyperparameter_searches':0,'panel':'21 only; mask6','primary':{'definition':'equal-four held MAE(R)-MAE(G)','regimes':primary,'equal_four_delta_mae':float(np.mean([p['delta_R_minus_G'] for p in primary])),'row_weighted_delta_mae':float(sum(p['absolute_error_delta'] for p in primary)/sum(p['n_held'] for p in primary)),'dependent_regimes_not_IID':True},'reports':reports,'worst_CUT_fixed_from_historical_G':worst,'regional_equality_constructed':True,'P_and_C_not_regularization_matched':True,'positive_label_means_registered_SNPP_not_true_fire':True}
    x.to_parquet(OUT/'evaluated_predictions.parquet',index=False)
    pd.DataFrame(primary).to_csv(OUT/'primary_contrasts.csv',index=False);pd.DataFrame(cuts).to_csv(OUT/'per_CUT.csv',index=False)
    write_json(OUT/'summary.json',summary)
    validate_freeze();clock_check()
    files=[p for p in OUT.iterdir() if p.is_file()];physical=sum(p.stat().st_size for p in files)
    if physical>100*1024**2 or len(x)>1_000_000:raise RuntimeError('Output cap exceeded')
    write_json(OUT/'manifest.json',{'completed_utc':now().isoformat(),'code_freeze_sha256':sha(OUT/'code-freeze.json'),'prediction_freeze_sha256':sha(OUT/'prediction-freeze.json'),'protected_unchanged':True,'output_sha256':{p.name:sha(p) for p in files},'total_solver_calls':predfreeze['total_solver_calls'],'physical_output_bytes_before_manifest':physical,'peak_RSS_bytes':clock_check(),'RSS_units':'bytes (darwin native; Linux KiB converted)','cap_end_utc':END})
    print('Evaluation complete:',OUT,flush=True)
    return summary


if __name__=='__main__':
    sys.modules['group_budget_audit']=sys.modules[__name__]  # Fixtures share the same call counter.
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['freeze','predict','evaluate']);args=ap.parse_args()
    {'freeze':freeze,'predict':predictions,'evaluate':evaluate}[args.action]()
