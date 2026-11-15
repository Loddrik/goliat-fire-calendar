"""Protocol16: isolate the cost of an intercept at a zero Aqua predictor."""
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np
import pandas as pd
from scientific_audit import ROOT,DATA,TRAIN,AuditData,fit_models,predict,sha
from affine_experiment import LAMBDAS,b_name,fit_affine,predict_affine,choose_policies,candidate_values,paired_bootstrap
from robust_affine_experiment import check_deadline
from temporal_transport_audit import validate_split
from frozen_temporal_audit import KEYS,publication_metadata
from reproduce_research import STAGES
OUT=DATA/'zero_anchor_audit'
POLICIES=('M1_B','Z_locked','B_Z_locked','M1_Z','B_Z_reselected')
METHODS=('M0','M1','M2',*POLICIES)
SPLITS={'forward_four':(tuple(range(2012,2016)),tuple(range(2016,2020))),
 'backward_four':(tuple(range(2016,2020)),tuple(range(2012,2016))),
 'forward_six':(tuple(range(2012,2018)),(2018,2019)),
 'backward_six':(tuple(range(2014,2020)),(2012,2013))}


def add_anchors(frame):
 x=frame.copy()
 for lam in LAMBDAS:x[f'Z_{lam:g}']=np.where(x.aqua>0,x[b_name(lam)],0.)
 return x


def fit_origin(data,allowed):
 check_deadline();full=data.monthly('fold_fitted',tuple(allowed));tr=full[full.season.isin(allowed)].copy()
 if set(tr.season)!=set(allowed):raise ValueError('Missing training seasons')
 reference=fit_models(tr);return full,{'reference':reference,'affine':fit_affine(tr,reference),'training_seasons':list(allowed)}


def raw_predict(frame,model):
 if frame.duplicated(KEYS).any():raise ValueError('Duplicate estimation keys')
 features=frame[[*KEYS,'g','aqua']].copy()
 x=add_anchors(predict_affine(predict(features,model['reference']),model['affine']))
 diagnostic=[c for c in frame if c not in x]
 return x.merge(frame[[*KEYS,*diagnostic]],on=KEYS,how='left',validate='one_to_one') if diagnostic else x


def fit_predict(data,allowed,destination):
 validate_split(allowed,destination);full,model=fit_origin(data,allowed)
 return raw_predict(full[full.season.isin(destination)].copy(),model),model


def choose(inner):
 base,_=choose_policies(inner);names=['M1',*[b_name(l) for l in LAMBDAS],*[f'Z_{l:g}' for l in LAMBDAS]]
 losses=pd.DataFrame({c:(inner[c]-inner.snpp).abs() for c in names}).assign(cut=inner.cut.to_numpy()).groupby('cut').mean()
 choices={p:{} for p in POLICIES}
 for cut,row in losses.iterrows():
  b=base['M1_B'][cut];locked='Z_'+b[2:] if b.startswith('B_') else 'M1'
  lam=min(LAMBDAS,key=lambda l:(row[f'Z_{l:g}'],-l));z=f'Z_{lam:g}'
  choices['M1_B'][cut]=b;choices['Z_locked'][cut]=locked
  choices['B_Z_locked'][cut]=locked if row[locked]<.99*row[b] else b
  choices['M1_Z'][cut]=z if row[z]<.99*row.M1 else 'M1'
  choices['B_Z_reselected'][cut]=z if row[z]<.99*row[b] else b
 return choices,losses


def apply_choices(frame,choices):
 x=frame.copy()
 for policy,mapping in choices.items():
  x[policy]=candidate_values(x,mapping);x[policy+'_chosen']=x.cut.map(mapping)
 if not np.isfinite(x[list(METHODS)]).all().all():raise ValueError('Nonfinite point')
 if not np.array_equal(x.loc[x.aqua>0,'Z_locked'],x.loc[x.aqua>0,'M1_B']):raise ValueError('Locked anchor changed positive predictor')
 if not x.loc[x.aqua==0,'Z_locked'].eq(0).all():raise ValueError('Anchor failed')
 return x


def transport(data,origin,destination,fit=fit_predict):
 validate_split(origin,destination);parts=[];calls=[]
 for held in origin:
  allowed=tuple(s for s in origin if s!=held);part,_=fit(data,allowed,(held,));parts.append(part)
  calls.append({'allowed':';'.join(map(str,allowed)),'held':str(held)})
 inner=pd.concat(parts,ignore_index=True);choices,_=choose(inner)
 point,model=fit(data,tuple(origin),tuple(destination));calls.append({'allowed':';'.join(map(str,origin)),'held':';'.join(map(str,destination))})
 model['choices']=choices
 return apply_choices(point,choices),inner,model,calls


def verify_controls(actual,previous):
 a=actual.sort_values(KEYS).reset_index(drop=True);b=previous.sort_values(KEYS).reset_index(drop=True)
 if not a[KEYS].equals(b[KEYS]):raise ValueError('Control keys differ')
 for c in ['aqua','snpp','M0','M1','M2','M1_B']:
  if not np.allclose(a[c],b[c],atol=1e-10,rtol=0):raise ValueError('Control differs '+c)


def metrics(frame):
 result={}
 for method in METHODS:
  error=frame[method]-frame.snpp;totals=frame.groupby(['season','m'])[[method,'snpp']].sum()
  result[method]={'n':len(frame),'mae':float(error.abs().mean()) if len(frame) else None,'bias':float(error.mean()) if len(frame) else None,
   'prediction_sum':float(frame[method].sum()),'target_sum':float(frame.snpp.sum()),
   'regional_monthly_mae':float((totals[method]-totals.snpp).abs().mean()) if len(totals) else None}
 return result


def stratified(frame,enabled):
 return {name:metrics(g) for name,g in [('all54',frame),('published14',frame[frame.cut.isin(enabled)]),
  ('active',frame[frame.snpp>0]),('both_zero',frame[(frame.aqua==0)&(frame.snpp==0)]),
  ('aqua_zero_viirs_positive',frame[(frame.aqua==0)&(frame.snpp>0)]),('viirs50plus',frame[frame.snpp>=50]),('aqua_positive',frame[frame.aqua>0])]}


def oracle_bound(frame):
 baseline=(frame.M1_B-frame.snpp).abs();alternate=frame.snpp.abs()
 attainable=np.where(frame.aqua==0,np.minimum(baseline,alternate),baseline)
 return {'scope':'Retrospective lower loss bound for actions0orB only at Aqua0; not a model or validation',
  'baseline_mae':float(baseline.mean()),'oracle_mae':float(np.mean(attainable)),
  'max_gain_mae':float(baseline.mean()-np.mean(attainable)),'rows':len(frame)}


def freeze(model):
 if model['training_seasons']!=list(TRAIN):raise ValueError('Only full training model can be frozen')
 r=model['reference']
 return {'schema_version':1,'training_seasons':list(TRAIN),'ratio':float(r['ratio']),
  'regional':r['regional'].reset_index().to_dict('records'),'local':r['local'].reset_index().to_dict('records'),
  'climatology':r['climatology'].reset_index().to_dict('records'),
  'affine':model['affine'].reset_index().to_dict('records'),'choices':model['choices']}


def restore(frozen):
 if frozen['schema_version']!=1 or frozen['training_seasons']!=list(TRAIN):raise ValueError('Unknown frozen anchor model')
 return {'reference':{'ratio':frozen['ratio'],'regional':pd.DataFrame(frozen['regional']).set_index('g'),
  'local':pd.DataFrame(frozen['local']).set_index(['cut','g']),
  'climatology':pd.DataFrame(frozen['climatology']).set_index(['cut','m'])['clim']},
  'affine':pd.DataFrame(frozen['affine']).set_index(['cut','g']),'choices':frozen['choices'],'training_seasons':frozen['training_seasons']}


def run():
 check_deadline();protected=list((ROOT/'web/public/data').rglob('*.json'))
 protected += [DATA/f for f in ['detections.parquet','cells_comuna.parquet','celldays.parquet','static_mask.parquet','params.json','gates.csv','eval_loso.csv','eval_final.csv','inventory.csv']]
 for directory in [*[directory for _,directory in STAGES],'aggregation_audit']:protected+=list((DATA/directory).glob('*'))
 before={str(p.relative_to(ROOT)):sha(p) for p in protected if p.is_file()};data=AuditData();points=[];raw_oof=[];calls=[];selections=[]
 for held in TRAIN:
  origin=tuple(s for s in TRAIN if s!=held);point,_,model,fitcalls=transport(data,origin,(held,))
  points.append(point);raw_oof.append(point);calls.extend(dict(c,outer_held=held,stage='nested') for c in fitcalls)
  selections.extend({'outer_held':held,'policy':p,'cut':cut,'candidate':c} for p,mapping in model['choices'].items() for cut,c in mapping.items())
  print('Anchor outer fold complete:',held,flush=True)
 historical=pd.concat(points,ignore_index=True);verify_controls(historical,pd.read_csv(DATA/'affine_audit/outer_predictions.csv',dtype={'cut':str}))
 enabled,_=publication_metadata(data.cuts);summary={'status':'retrospective-zero-anchor-ablation','independent_validation':False,
  'nested':stratified(historical,enabled),'nested_fit_calls':len(calls),'controls_reproduced':True,
  'contrasts':[paired_bootstrap(historical,p,'M1_B') for p in POLICIES if p!='M1_B'],'oracle':oracle_bound(historical)}
 bp=pd.read_csv(DATA/'piecewise_audit/outer_predictions.csv',dtype={'cut':str}).sort_values(KEYS);a=historical.sort_values(KEYS)
 if not a[KEYS].reset_index(drop=True).equals(bp[KEYS].reset_index(drop=True)) or not np.allclose(a.snpp,bp.snpp,rtol=0,atol=0):raise ValueError('B/P target changed')
 summary['saved_B_P_mae']=float((bp.M1_B_P-bp.snpp).abs().mean())
 blocked=[]
 for label,(origin,destination) in SPLITS.items():
  x,_,_,temporal_calls=transport(data,origin,destination);calls.extend(dict(c,stage='temporal',split=label) for c in temporal_calls);blocked.append(x.assign(split=label));summary[label]=stratified(x,enabled)
  if label.endswith('four'):
   previous=pd.read_csv(DATA/'temporal_transport_audit/predictions.csv',dtype={'cut':str});previous=previous[previous.direction==label.split('_')[0]]
  else:
   previous=pd.read_parquet(DATA/'training_size_audit/predictions.parquet');case='fold_fitted_'+label.split('_')[0]+'_'+'-'.join(map(str,origin));previous=previous[previous['case']==case]
  verify_controls(x,previous);print('Anchor blocked complete:',label,flush=True)
 summary['temporal_fit_calls']=len(calls)-summary['nested_fit_calls'];summary['full_fit_calls']=1
 full,model=fit_origin(data,TRAIN);model['choices']=choose(pd.concat(raw_oof,ignore_index=True))[0];frozen=freeze(model)
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'frozen_model.json').write_text(json.dumps(frozen,indent=2,allow_nan=False)+'\n')
 restored=restore(json.loads((OUT/'frozen_model.json').read_text()));print('Anchor model frozen before destination read',flush=True)
 future=pd.read_parquet(DATA/'frozen_temporal_audit/predictions.parquet');later=apply_choices(raw_predict(future,restored),restored['choices']);verify_controls(later,future)
 for block,g in later.groupby('block'):summary[block]=stratified(g,enabled)
 if not np.array_equal(later[list(METHODS)].to_numpy(),apply_choices(raw_predict(future,model),model['choices'])[list(METHODS)].to_numpy()):raise ValueError('Frozen model failed exact restoration')
 communal=[]
 for policy in POLICIES:
  for cut,g in historical.groupby('cut'):
   base=float((g.M1_B-g.snpp).abs().mean());loss=float((g[policy]-g.snpp).abs().mean());communal.append({'cut':cut,'policy':policy,'mae_B':base,'mae':loss,'benefit':base-loss})
 check_deadline()
 if before!={k:sha(ROOT/k) for k in before}:raise ValueError('Protected files changed')
 historical.to_parquet(OUT/'outer_predictions.parquet',index=False,compression='zstd');pd.concat(blocked,ignore_index=True).to_parquet(OUT/'blocked_predictions.parquet',index=False,compression='zstd');later.to_parquet(OUT/'later_predictions.parquet',index=False,compression='zstd')
 pd.DataFrame(calls).to_csv(OUT/'fit_seasons.csv',index=False);pd.DataFrame(selections).to_csv(OUT/'selection.csv',index=False);pd.DataFrame(communal).to_csv(OUT/'commune_errors.csv',index=False)
 (OUT/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
 manifest={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'code_sha256':sha(Path(__file__)),
  'protocol_sha256':sha(ROOT/'docs/reviews/2026-11-14-science-protocol-16.md'),
  'helpers_sha256':{name:sha(ROOT/'pipeline'/name) for name in ['scientific_audit.py','affine_experiment.py','frozen_temporal_audit.py','temporal_transport_audit.py']},
  'environment_sha256':{name:sha(ROOT/name) for name in ['pyproject.toml','uv.lock']},'protected_sha256':before,'production_and_previous_unchanged':True,
  'output_sha256':{p.name:sha(p) for p in sorted(OUT.glob('*')) if p.name!='manifest.json'}}
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n');print('Anchor audit complete:',OUT,flush=True)
 return summary

if __name__=='__main__':run()
