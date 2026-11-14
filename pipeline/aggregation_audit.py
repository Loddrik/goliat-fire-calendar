"""Descriptive concentration of existing OOF error reductions, no fitting."""
import json
from pathlib import Path
import subprocess
import numpy as np
import pandas as pd
from scientific_audit import ROOT,DATA,sha
from frozen_temporal_audit import KEYS,join_oof
from reproduce_research import STAGES
from robust_affine_experiment import check_deadline
OUT=DATA/'aggregation_audit'
TOL=1e-10


def summarize(frame):
 benefit=frame.benefit.to_numpy();positive=np.sort(benefit[benefit>TOL])[::-1];negative=benefit[benefit < -TOL]
 baseline=float(frame.mae_M1.mean());candidate=float(frame.mae_candidate.mean())
 return {'communes':len(frame),'better':int((benefit>TOL).sum()),'worse':int((benefit < -TOL).sum()),'equal':int((np.abs(benefit)<=TOL).sum()),
  'mae_M1':baseline,'mae_candidate':candidate,'improvement_pct':100*(1-candidate/baseline) if baseline else None,
  'benefit_median':float(np.median(benefit)),'benefit_p25':float(np.quantile(benefit,.25)),'benefit_p75':float(np.quantile(benefit,.75)),
  'gross_benefit_sum':float(positive.sum()),'gross_deterioration_sum':float(-negative.sum()),'net_benefit_sum':float(benefit.sum()),
  'top5_share_of_gross_benefit':float(positive[:5].sum()/positive.sum()) if positive.sum()>0 else None}


def run():
 check_deadline();protected=list((ROOT/'web/public/data').rglob('*.json'))
 protected += [DATA/x for x in ['detections.parquet','cells_comuna.parquet','celldays.parquet','static_mask.parquet','params.json','gates.csv','eval_loso.csv','eval_final.csv','inventory.csv']]
 for _,directory in STAGES:protected+=list((DATA/directory).glob('*'))
 before={str(p.relative_to(ROOT)):sha(p) for p in protected if p.is_file()}
 read=lambda d:pd.read_csv(DATA/d/'outer_predictions.csv',dtype={'cut':str})
 frame=join_oof(read('piecewise_audit'),read('robust_affine_audit')).sort_values(KEYS).reset_index(drop=True)
 affine=read('affine_audit').sort_values(KEYS).reset_index(drop=True)
 if len(frame)!=5184 or not frame[KEYS].equals(affine[KEYS]):raise ValueError('OOF keys changed')
 for c in ['aqua','snpp','M1','M1_B']:
  if not np.allclose(frame[c],affine[c],rtol=0,atol=TOL):raise ValueError('OOF control changed '+c)
 index=json.loads((ROOT/'web/public/data/index.json').read_text());enabled={c['cut'] for c in index['comunas'] if c['enabled']}
 names={c['cut']:c['name'] for c in json.loads((ROOT/'observed/dist/data/communes.json').read_text())['communes']}
 records=[];summary={}
 sources={'M1_B':'affine_audit','M1_H':'robust_affine_audit','M1_B_P':'piecewise_audit'}
 for policy,directory in sources.items():
  x=pd.DataFrame({'cut':frame.cut,'base':(frame.M1-frame.snpp).abs(),'candidate':(frame[policy]-frame.snpp).abs()})
  local=x.groupby('cut').agg(n=('base','size'),mae_M1=('base','mean'),mae_candidate=('candidate','mean')).reset_index()
  if len(local)!=54 or not local.n.eq(96).all():raise ValueError('Incomplete aggregation grid')
  local['benefit']=local.mae_M1-local.mae_candidate;local['policy']=policy;local['commune']=local.cut.map(names);local['published']=local.cut.isin(enabled)
  if local.commune.isna().any():raise ValueError('Missing official name')
  original=json.loads((DATA/directory/'summary.json').read_text())['scores']
  if abs(local.mae_candidate.mean()-original[policy]['mean_monthly_mae'])>TOL or abs(local.mae_M1.mean()-original['M1']['mean_monthly_mae'])>TOL:raise ValueError('Global score did not reconcile')
  summary[policy]={name:summarize(group) for name,group in [('all54',local),('published14',local[local.published]),('other40',local[~local.published])]}
  records.append(local)
 if before!={k:sha(ROOT/k) for k in before}:raise ValueError('Protected artifact changed')
 check_deadline();OUT.mkdir(parents=True,exist_ok=True);pd.concat(records,ignore_index=True).to_csv(OUT/'commune_errors.csv',index=False)
 (OUT/'summary.json').write_text(json.dumps({'scope':'Retrospective aggregation diagnosis; no new policy or independent validation','tolerance':TOL,'global_controls_reconciled':True,'policies':summary},indent=2,allow_nan=False)+'\n')
 manifest={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'code_sha256':sha(Path(__file__)),
  'protocol_sha256':sha(ROOT/'docs/reviews/2026-11-14-aggregation-protocol.md'),'protected_sha256':before,'original_unchanged':True,
  'output_sha256':{p.name:sha(p) for p in OUT.glob('*') if p.name!='manifest.json'}}
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n');print(json.dumps(summary,indent=2))
 return summary

if __name__=='__main__':run()
