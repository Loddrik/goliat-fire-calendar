"""Protocol 10: all four-of-six origins, fixed targets, two mask contracts."""
import hashlib
import itertools
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from scientific_audit import ROOT,DATA,AuditData,score,sha
from temporal_transport_audit import transport,validate_split,METHODS
from robust_affine_experiment import check_deadline

OUT=DATA/'training_size_audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-14-science-protocol-10.md'
DIRECTIONS={'backward':(tuple(range(2014,2020)),(2012,2013)),
            'forward':(tuple(range(2012,2018)),(2018,2019))}
POLICIES=('pre_overlap','fold_fitted')


def cases():
    result=[]
    for policy in POLICIES:
        for direction,(full,destination) in DIRECTIONS.items():
            for origin in [*itertools.combinations(full,4),full]:
                validate_split(origin,destination)
                result.append({'case':policy+'_'+direction+'_'+'-'.join(map(str,origin)),
                    'mask_policy':policy,'direction':direction,'origin':origin,'destination':destination,'n_train':len(origin)})
    if len(result)!=64 or len({c['case'] for c in result})!=64:raise ValueError('Incomplete training design')
    return result


class MaskContract:
    def __init__(self,data,policy):
        if policy not in POLICIES:raise ValueError('Unknown mask contract')
        self.data,self.policy=data,policy
        self.calls=[]

    def monthly(self,requested,allowed):
        if requested!='fold_fitted':raise ValueError('Unexpected fitting interface')
        self.calls.append(tuple(allowed))
        return self.data.monthly(self.policy,tuple(allowed) if self.policy=='fold_fitted' else ())

    def mask(self,allowed):
        return self.data.fit_mask(tuple(allowed) if self.policy=='fold_fitted' else ())


def target_frame(frame):
    result=frame[['cut','season','m','aqua','snpp']].sort_values(['cut','season','m']).reset_index(drop=True)
    if result.duplicated(['cut','season','m']).any():raise ValueError('Duplicated target grid')
    return result


def require_same_target(expected,actual):
    if not target_frame(expected).equals(target_frame(actual)):raise ValueError('Primary target changed between origins')


def mask_digest(mask):
    return hashlib.sha256(json.dumps(sorted(mask),separators=(',',':')).encode()).hexdigest()


def aggregate(frame):
    baseline=float((frame.M1-frame.snpp).abs().mean())
    records=[]
    for method in METHODS:
        error=frame[method]-frame.snpp
        records.append({'method':method,'n':len(frame),'mae':float(error.abs().mean()),
            'bias':float(error.mean()),'absolute_error_sum':float(error.abs().sum()),
            'delta_mae_vs_M1':float(error.abs().mean()-baseline),
            'improvement_pct_vs_M1':float((1-error.abs().mean()/baseline)*100) if baseline>0 else None})
    return pd.DataFrame(records)


def distribution(aggregates):
    report={}
    for (policy,direction),group in aggregates.groupby(['mask_policy','direction']):
        result={}
        for method,g in group.groupby('method'):
            short=g[g.n_train==4];full=g[g.n_train==6]
            if len(short)!=15 or len(full)!=1:raise ValueError('Missing subset aggregates')
            result[method]={'six_seasons':full.iloc[0][['mae','bias','delta_mae_vs_M1','improvement_pct_vs_M1']].to_dict(),
                'four_season_subsets':{'n':15,'mae_median':float(short.mae.median()),'mae_min':float(short.mae.min()),'mae_max':float(short.mae.max()),
                    'improvement_pct_median':float(short.improvement_pct_vs_M1.median()),
                    'improvement_pct_min':float(short.improvement_pct_vs_M1.min()),'improvement_pct_max':float(short.improvement_pct_vs_M1.max()),
                    'subsets_better_than_M1':int((short.delta_mae_vs_M1<0).sum())}}
        report[policy+'_'+direction]={'target_identical_across_origins':policy=='pre_overlap','methods':result}
    return report


def run():
    check_deadline()
    protected=sorted((ROOT/'web/public/data').rglob('*.json'))
    protected += [DATA/f for f in ['detections.parquet','celldays.parquet','static_mask.parquet','params.json','gates.csv','eval_loso.csv','eval_final.csv']]
    for directory in ['scientific_audit','affine_audit','robust_affine_audit','piecewise_audit','geography_audit','platform_bridge_audit','temporal_transport_audit','conaf_external_audit']:
        protected+=sorted((DATA/directory).glob('*'))
    before={str(p.relative_to(ROOT)):sha(p) for p in protected}
    base=AuditData();predictions=[];selections=[];masks=[];scores=[];aggregates=[];seasons=[];numerics=[];targets={}
    for index,case in enumerate(cases(),1):
        check_deadline()
        data=MaskContract(base,case['mask_policy'])
        frame,selection,params=transport(data,case['origin'],case['destination'])
        origin=set(case['origin']);destination=set(case['destination'])
        if any(not set(allowed)<=origin or set(allowed)&destination for allowed in data.calls):raise ValueError('Mask/fitting crossed destination')
        if case['mask_policy']=='pre_overlap':
            if case['direction'] in targets:require_same_target(targets[case['direction']],frame)
            else:targets[case['direction']]=target_frame(frame)
        context={key:case[key] for key in ['case','direction','mask_policy','n_train']}
        predictions.append(frame[['cut','season','m','aqua','snpp',*METHODS]].assign(**context))
        selections.append(selection.assign(**context))
        s=score(frame,METHODS).assign(**context);s['absolute_error_sum']=s.mae*s.n;scores.append(s)
        aggregates.append(aggregate(frame).assign(**context))
        seasons.extend([aggregate(g).assign(season=int(season),**context) for season,g in frame.groupby('season')])
        for allowed in data.calls:
            mask=data.mask(allowed)
            masks.append({'case':case['case'],'allowed':';'.join(map(str,allowed)),
                'mask_training_seasons':';'.join(map(str,allowed)) if data.policy=='fold_fitted' else 'pre2012_only',
                'n_cells':len(mask),'sha256':mask_digest(mask)})
        numerics.extend([dict(case=case['case'],**n) for n in params.attrs['huber_numerics']])
        print(f"Training-size case {index}/64 complete: {case['case']}",flush=True)
    check_deadline()
    x=pd.concat(predictions,ignore_index=True);agg=pd.concat(aggregates,ignore_index=True)
    if len(x)!=82944 or x.duplicated(['case','cut','season','m']).any():raise ValueError('Missing/duplicated design predictions')
    if before!={str(p.relative_to(ROOT)):sha(p) for p in protected}:raise ValueError('Protected files changed')
    summary={'status':'retrospective-training-size-diagnostic','external_validation':False,'production_changed':False,
        'cases':64,'fixed_mask_size':len(base.fit_mask(())),'primary_targets_identical':True,
        'primary_target_sha256':{d:hashlib.sha256(f.to_csv(index=False).encode()).hexdigest() for d,f in targets.items()},
        'comparisons':distribution(agg),'final_huber_max_kkt':float(max(n['max_kkt'] for n in numerics))}
    OUT.mkdir(parents=True,exist_ok=True)
    x.to_parquet(OUT/'predictions.parquet',index=False,compression='zstd')
    pd.concat(scores,ignore_index=True).to_parquet(OUT/'scores.parquet',index=False,compression='zstd')
    for filename,frame in [('selection.csv',pd.concat(selections,ignore_index=True)),('masks.csv',pd.DataFrame(masks)),
                           ('aggregates.csv',agg),('season_aggregates.csv',pd.concat(seasons,ignore_index=True)),('numerics.csv',pd.DataFrame(numerics))]:
        frame.to_csv(OUT/filename,index=False)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    helpers=['scientific_audit.py','affine_experiment.py','robust_affine_experiment.py','piecewise_experiment.py','temporal_transport_audit.py']
    manifest={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'protocol_sha256':sha(PROTOCOL),'code_sha256':sha(Path(__file__)),
        'helpers_sha256':{f:sha(ROOT/'pipeline'/f) for f in helpers},
        'environment_sha256':{f:sha(ROOT/f) for f in ['pyproject.toml','uv.lock']},
        'protected_sha256':before,'production_and_previous_unchanged':True,
        'output_sha256':{p.name:sha(p) for p in sorted(OUT.glob('*')) if p.name!='manifest.json'}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n')
    print('Training-size diagnostic complete:',OUT,flush=True)
    return summary


if __name__=='__main__':run()
