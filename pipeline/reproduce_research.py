"""Re-run research from a separate, clean checkout without publishing data.

Inputs are the repository's pinned processed satellite tables and one pinned CONAF
workbook. This does not reconstruct the original FIRMS downloads or independently
validate the scientific target. The interpreter may belong to a fresh uv.lock env.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
STAGES=(('scientific_audit','scientific_audit'),('affine_experiment','affine_audit'),
 ('robust_affine_experiment','robust_affine_audit'),('piecewise_experiment','piecewise_audit'),
 ('geography_experiment','geography_audit'),('platform_bridge_audit','platform_bridge_audit'),
 ('temporal_transport_audit','temporal_transport_audit'),('conaf_external_audit','conaf_external_audit'),
 ('training_size_audit','training_size_audit'),('frozen_temporal_audit','frozen_temporal_audit'),
 ('scaled_band_audit','scaled_band_audit'),('asymmetric_band_audit','asymmetric_band_audit'),
 ('terra_feature_audit','terra_feature_audit'),('interval_loss_fit_audit','interval_loss_fit_audit'))
CONAF_HASH='1d92971eab0b8c73bae139f2d5228589370b72641917c630dde8eb0c9b16aad0'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def git(root,*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()


def validate_checkout(source,destination):
 source=source.resolve();destination=destination.resolve()
 if source==destination or source in destination.parents or destination in source.parents:
  raise ValueError('Reproduction checkout must be outside the source checkout')
 if not (destination/'.git').exists():raise ValueError('Missing separate Git checkout')
 if git(destination,'rev-parse','HEAD')!=git(source,'rev-parse','HEAD'):
  raise ValueError('Source and destination commits differ')
 if git(destination,'status','--porcelain'):
  raise ValueError('Reproduction checkout must start clean')
 return destination


def deadline_timestamp(value):
 parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
 if parsed.tzinfo is None:raise ValueError('Deadline requires a UTC offset')
 if parsed.timestamp()-time.time()<30:raise ValueError('Deadline reserve reached')
 return parsed.timestamp()


def run(destination,interpreter,report_dir,deadline,source=ROOT):
 source=source.resolve();destination=validate_checkout(source,destination)
 interpreter=Path(os.path.abspath(interpreter))
 limit=deadline_timestamp(deadline);report_dir=report_dir.resolve()
 if destination==report_dir or destination in report_dir.parents:
  raise ValueError('Keep the evidence directory outside the reproduction checkout')
 report_dir.mkdir(parents=True,exist_ok=True)
 raw=source/'data/raw/external/conaf-1985-2024.xlsx'
 if sha(raw)!=CONAF_HASH:raise ValueError('Pinned CONAF input mismatch')
 target=destination/raw.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(raw,target)
 protected=[*source.glob('web/public/data/**/*.json')]+[source/'data/processed'/x for x in
  ['detections.parquet','celldays.parquet','static_mask.parquet','params.json','gates.csv','eval_loso.csv','eval_final.csv','inventory.csv']]
 before={str(p.relative_to(source)):sha(p) for p in protected}
 baseline={str(p.relative_to(source)):sha(p) for _,d in STAGES for p in (source/'data/processed'/d).glob('*') if p.is_file()}
 record={'source_head':git(source,'rev-parse','HEAD'),'interpreter':str(interpreter),
  'scope':'Processed satellite inputs pinned by Git; no reconstruction from raw FIRMS downloads',
  'started_utc':datetime.now(timezone.utc).isoformat(),'raw_conaf_sha256':CONAF_HASH,
  'original_protected_sha256':before,'stages':[]}
 env=dict(os.environ,GOLIAT_RESEARCH_DEADLINE_UTC=deadline,MPLCONFIGDIR=str(report_dir/'matplotlib'))
 def save():
  (report_dir/'summary.json').write_text(json.dumps(record,indent=2,allow_nan=False)+'\n')
 def execute(command,name):
  remaining=limit-time.time()
  if remaining<30:raise RuntimeError('Deadline reserve reached before '+name)
  started=time.time();print('Starting',name,flush=True)
  with (report_dir/(name+'.log')).open('w') as stream:
   result=subprocess.run(command,cwd=destination,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=remaining-20)
  return result.returncode,round(time.time()-started,3)
 for script,directory in STAGES:
  code,seconds=execute([str(interpreter),'pipeline/'+script+'.py'],script)
  entry={'script':script,'exit_code':code,'seconds':seconds,'matches':[],'differences':[]}
  actual={str(p.relative_to(destination)):sha(p) for p in (destination/'data/processed'/directory).glob('*') if p.is_file()}
  expected={k:v for k,v in baseline.items() if Path(k).parent.name==directory}
  for key in sorted(set(actual)|set(expected)):
   item={'path':key,'expected':expected.get(key),'actual':actual.get(key)}
   entry['matches' if item['expected']==item['actual'] else 'differences'].append(item)
  record['stages'].append(entry);save()
  print('Finished',script,code,'differences',[x['path'] for x in entry['differences']],flush=True)
  if code:raise RuntimeError('Stage failed: '+script)
 code,seconds=execute([str(interpreter),'-m','unittest','discover','-s','tests'],'tests')
 record.update(tests_exit_code=code,tests_seconds=seconds,finished_utc=datetime.now(timezone.utc).isoformat(),
  original_protected_unchanged=before=={str(p.relative_to(source)):sha(p) for p in protected})
 record['original_research_unchanged']=baseline=={str(p.relative_to(source)):sha(p) for _,d in STAGES for p in (source/'data/processed'/d).glob('*') if p.is_file()}
 save()
 if code or not record['original_research_unchanged'] or not record['original_protected_unchanged']:raise RuntimeError('Final integrity/test check failed')
 return record


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--checkout',type=Path,required=True)
 parser.add_argument('--python',type=Path,required=True)
 parser.add_argument('--report-dir',type=Path,required=True)
 parser.add_argument('--deadline-utc',required=True)
 args=parser.parse_args()
 run(args.checkout,args.python,args.report_dir,args.deadline_utc)
