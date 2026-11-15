"""Protocol 8: fixed-family temporal transport, with origin-only selection."""
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from scientific_audit import ROOT, DATA, TRAIN, AuditData, fit_models, predict, score, summarize, sha
from affine_experiment import fit_affine, predict_affine, candidate_values, paired_bootstrap
from robust_affine_experiment import fit_huber, predict_huber, choose as choose_huber, check_deadline
from piecewise_experiment import fit_piecewise, predict_piecewise, choose as choose_piecewise

OUT = DATA / 'temporal_transport_audit'
PROTOCOL = ROOT / 'docs/reviews/2026-11-14-science-protocol-8.md'
SPLITS = {'forward': ((2012,2013,2014,2015),(2016,2017,2018,2019)),
          'backward': ((2016,2017,2018,2019),(2012,2013,2014,2015))}
METHODS = ('M0','M1','M2','M1_B','M1_H','M1_P','M1_B_P')


def validate_split(origin, destination):
    if len(origin)!=len(set(origin)) or len(destination)!=len(set(destination)):
        raise ValueError('Repeated season')
    if len(origin)<3 or not destination or set(origin)&set(destination):
        raise ValueError('Origin and destination must be nonempty and disjoint')
    if not (set(origin)|set(destination)).issubset(TRAIN):
        raise ValueError('Season outside frozen development pool')


def apply_choices(frame, choices):
    result=frame.copy()
    for policy,mapping in choices.items():
        if set(mapping)!=set(result.cut.unique()):raise ValueError('Incomplete commune selection')
        result[policy]=candidate_values(result,mapping)
        result[policy+'_chosen']=result.cut.map(mapping)
    if not np.isfinite(result[list(METHODS)].to_numpy()).all():raise ValueError('Nonfinite predictions')
    return result


def fit_predict(data, allowed, held):
    """Every statistic and mask is fitted on allowed seasons only."""
    check_deadline()
    validate_split(allowed,held)
    full=data.monthly('fold_fitted',tuple(allowed))
    tr=full[full.season.isin(allowed)].copy()
    te=full[full.season.isin(held)].copy()
    if set(tr.season)!=set(allowed) or set(te.season)!=set(held):raise ValueError('Missing requested seasons')
    reference=fit_models(tr)
    affine=fit_affine(tr,reference)
    huber,numerics=fit_huber(tr,affine)
    piecewise=fit_piecewise(tr,affine)
    result=predict_piecewise(predict_huber(predict_affine(predict(te,reference),affine),huber),piecewise)
    # Keep all fitted coefficients for reviewing extrapolation, without publication.
    params=affine.join(huber.drop(columns=[c for c in huber if c in affine]),how='left')
    params=params.join(piecewise.drop(columns=[c for c in piecewise if c in params]),how='left')
    params.attrs["huber_numerics"]=numerics
    return result,params


def transport(data, origin, destination, fit=fit_predict):
    validate_split(origin,destination)
    inner_parts=[]
    for held in origin:
        allowed=tuple(s for s in origin if s!=held)
        prediction,_=fit(data,allowed,(held,))
        inner_parts.append(prediction)
    inner=pd.concat(inner_parts,ignore_index=True)
    if set(inner.season)!=set(origin):raise ValueError('Selection data crossed temporal boundary')
    choices,loss=choose_piecewise(inner)
    hchoices,hloss=choose_huber(inner)
    choices['M1_H']=hchoices['M1_H']
    external,params=fit(data,tuple(origin),tuple(destination))
    selected=[]
    for policy,mapping in choices.items():
        for cut,candidate in mapping.items():
            table=hloss if policy=='M1_H' else loss
            selected.append({'cut':cut,'policy':policy,'candidate':candidate,
                             'internal_mae':float(table.loc[cut,candidate]),
                             'origin_seasons':';'.join(map(str,origin))})
    return apply_choices(external,choices),pd.DataFrame(selected),params


def metrics(frame):
    return {'n':len(frame),'methods':{m:{
        'mae':float((frame[m]-frame.snpp).abs().mean()) if len(frame) else None,
        'bias':float((frame[m]-frame.snpp).mean()) if len(frame) else None,
        'prediction_sum':float(frame[m].sum())} for m in METHODS}}


def run():
    check_deadline()
    protected=sorted((ROOT/'web/public/data').rglob('*.json'))
    protected += [DATA/f for f in ['detections.parquet','celldays.parquet','static_mask.parquet','params.json','gates.csv','eval_loso.csv','eval_final.csv']]
    for directory in ['scientific_audit','affine_audit','robust_affine_audit','piecewise_audit','geography_audit','platform_bridge_audit']:
        protected+=sorted((DATA/directory).glob('*'))
    before={str(p.relative_to(ROOT)):sha(p) for p in protected}
    data=AuditData();predictions=[];selections=[];coefficients=[];masks=[];report={}
    for direction,(origin,destination) in SPLITS.items():
        frame,selection,params=transport(data,origin,destination)
        frame['direction']=direction;selection['direction']=direction
        predictions.append(frame);selections.append(selection)
        coefficients.append(params.reset_index().assign(direction=direction))
        for allowed in [tuple(s for s in origin if s!=h) for h in origin]+[origin]:
            for x,y in sorted(data.fit_mask(allowed)):
                masks.append({'direction':direction,'allowed':';'.join(map(str,allowed)),'cell_x':x,'cell_y':y})
        scores=score(frame,METHODS)
        report[direction]={'origin':list(origin),'destination':list(destination),
            'scores':summarize(scores),
            'contrasts':[paired_bootstrap(frame,a,b) for a,b in [('M1_B','M1'),('M1_H','M1'),('M1_P','M1'),('M1_B_P','M1'),('M1_B_P','M1_B')]],
            'subgroups':{k:metrics(v) for k,v in {
                'both_observed_zero':frame[(frame.aqua==0)&(frame.snpp==0)],
                'aqua_zero_viirs_positive':frame[(frame.aqua==0)&(frame.snpp>0)],
                'viirs_50_plus':frame[frame.snpp>=50]}.items()},
            'choices':{p:g.candidate.value_counts().astype(int).to_dict() for p,g in selection.groupby('policy')},
            'origin_mask_size':len(data.fit_mask(origin)), 'huber_numerics':params.attrs['huber_numerics']}
        print('Transport complete:',direction,flush=True)
    result=pd.concat(predictions,ignore_index=True)
    if len(result)!=5184 or result.duplicated(['cut','season','m']).any():raise ValueError('Transport grid missing or duplicated')
    if before!={str(p.relative_to(ROOT)):sha(p) for p in protected}:raise ValueError('Protected files changed')
    OUT.mkdir(parents=True,exist_ok=True)
    combined_scores=pd.concat([score(g,METHODS).assign(direction=d) for d,g in result.groupby('direction')],ignore_index=True)
    combined_scores['absolute_error_sum']=combined_scores.mae*combined_scores.n
    for filename,frame in [('predictions.csv',result),('selection.csv',pd.concat(selections,ignore_index=True)),
                           ('coefficients.csv',pd.concat(coefficients,ignore_index=True)),('masks.csv',pd.DataFrame(masks)),('scores.csv',combined_scores)]:
        frame.to_csv(OUT/filename,index=False)
    (OUT/'summary.json').write_text(json.dumps({'status':'retrospective-temporal-stress','external_validation':False,'directions':report},indent=2,allow_nan=False)+'\n')
    helpers=['scientific_audit.py','affine_experiment.py','robust_affine_experiment.py','piecewise_experiment.py']
    manifest={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'code_sha256':sha(Path(__file__)),'protocol_sha256':sha(PROTOCOL),
              'helpers_sha256':{f:sha(ROOT/'pipeline'/f) for f in helpers},'protected_sha256':before,
              'production_and_previous_unchanged':True,
              'output_sha256':{p.name:sha(p) for p in sorted(OUT.glob('*')) if p.name!='manifest.json'}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n')
    return report


if __name__=='__main__':run()
