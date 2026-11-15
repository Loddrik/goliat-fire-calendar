"""Protocol 17: two-part distributions and fixed-kappa marginal-gain ablations.

Uses observed S-NPP counts as response, never physical fire occurrence. The
runner only writes hurdle_audit/ and keeps production and earlier studies fixed.
"""
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd

from scientific_audit import ROOT,DATA,TRAIN,AuditData,fit_models,predict,score,sha
from affine_experiment import LAMBDAS,b_name,fit_affine,predict_affine,candidate_values,paired_bootstrap
from robust_affine_experiment import check_deadline
from temporal_transport_audit import validate_split
from frozen_temporal_audit import KEYS,load_frozen,signature as baseline_signature,publication_metadata
from reproduce_research import STAGES

OUT=DATA/'hurdle_audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-14-science-protocol-17.md'
KAPPAS=(3,10,30)
FACTORIAL=('E00_10','E10_10','E01_10','E11_10')
HURDLE_METHODS=('E00_10','E10_10','E01_10','E11_3','E11_10','E11_30')
METHODS=('M0','M1','M2','M1_B',*HURDLE_METHODS,'B_E')
PROBABILITIES=('p_parent','p_local_10')
SPLITS={'forward_four':(tuple(range(2012,2016)),tuple(range(2016,2020))),
        'backward_four':(tuple(range(2016,2020)),tuple(range(2012,2016))),
        'forward_six':(tuple(range(2012,2018)),(2018,2019)),
        'backward_six':(tuple(range(2014,2020)),(2012,2013))}
TOLERANCE=1e-10


def choose(frame):
    columns=['M1',*[b_name(l) for l in LAMBDAS],*[f'E11_{k}' for k in KAPPAS]]
    if not np.isfinite(frame[['snpp',*columns]].to_numpy()).all():raise ValueError('Nonfinite selection observations')
    losses=pd.DataFrame({c:(frame[c]-frame.snpp).abs() for c in columns})
    losses['cut']=frame.cut.to_numpy();losses=losses.groupby('cut').mean()
    choices={'M1_B':{},'B_E':{}}
    for cut,row in losses.iterrows():
        lam=min(LAMBDAS,key=lambda l:(row[b_name(l)],-l));b=b_name(lam)
        base=b if row[b]<.99*row.M1 else 'M1'
        k=min(KAPPAS,key=lambda k:(row[f'E11_{k}'],-k));e=f'E11_{k}'
        choices['M1_B'][cut]=base
        choices['B_E'][cut]=e if row[e]<.99*row[base] else base
    return choices,losses


def apply_choices(frame,choices):
    out=frame.copy()
    for policy,mapping in choices.items():
        if set(mapping)!=set(out.cut.unique()):raise ValueError('Incomplete commune selection')
        out[policy]=candidate_values(out,mapping);out[policy+'_chosen']=out.cut.map(mapping)
    if not np.isfinite(out[list(METHODS)].to_numpy()).all():raise ValueError('Nonfinite hurdle estimates')
    return out


def fit_predict(data,allowed,destination):
    """Every fitted quantity, including the mask and CDFs, uses allowed only."""
    from hurdle_model import fit_hurdle,predict_hurdle
    check_deadline();validate_split(allowed,destination)
    full=data.monthly('fold_fitted',tuple(allowed))
    tr=full[full.season.isin(allowed)].copy();te=full[full.season.isin(destination)].copy()
    if set(tr.season)!=set(allowed) or set(te.season)!=set(destination):raise ValueError('Missing fold season')
    ref=fit_models(tr);affine=fit_affine(tr,ref);hurdle=fit_hurdle(tr,ref)
    features=te.drop(columns='snpp')
    out=predict_hurdle(predict_affine(predict(features,ref),affine),hurdle)
    out=out.merge(te[[*KEYS,'snpp']],on=KEYS,how='left',validate='one_to_one')
    return out,affine,hurdle


def transport(data,origin,destination,fit=fit_predict):
    validate_split(origin,destination);parts=[];calls=[]
    def checked(allowed,held):
        if set(allowed)&set(destination):raise ValueError('Destination entered model fitting')
        x,params,model=fit(data,tuple(allowed),tuple(held))
        if set(x.season)!=set(held):raise ValueError('Unexpected held season')
        calls.append({'allowed':';'.join(map(str,allowed)),'held':';'.join(map(str,held))})
        return x,params,model
    for held in origin:
        x,_,_=checked(tuple(s for s in origin if s!=held),(held,));parts.append(x)
    inner=pd.concat(parts,ignore_index=True)
    if set(inner.season)!=set(origin):raise ValueError('Selection crossed origin')
    choices,losses=choose(inner);external,params,model=checked(tuple(origin),tuple(destination))
    rows=[]
    for policy,mapping in choices.items():
        for cut,candidate in mapping.items():
            rows.append({'cut':cut,'policy':policy,'candidate':candidate,'internal_mae':float(losses.loc[cut,candidate]),
                         'training_seasons':';'.join(map(str,origin))})
    return apply_choices(external,choices),pd.DataFrame(rows),params,model,calls,losses


def verify_controls(actual,previous):
    a=actual.sort_values(KEYS).reset_index(drop=True);b=previous.sort_values(KEYS).reset_index(drop=True)
    if a.duplicated(KEYS).any() or b.duplicated(KEYS).any() or not a[KEYS].equals(b[KEYS]):raise ValueError('Control keys changed')
    for c in ['aqua','snpp','M0','M1','M2','M1_B']:
        if not np.allclose(a[c],b[c],rtol=0,atol=TOLERANCE,equal_nan=False):raise ValueError('Control changed '+c)


def attach_piecewise(actual,previous):
    out=actual.merge(previous[[*KEYS,'M1_B_P']],on=KEYS,how='left',validate='one_to_one')
    if out.M1_B_P.isna().any():raise ValueError('Missing B/P comparator')
    return out


def metrics(frame):
    available=[*METHODS,*(['M1_B_P'] if 'M1_B_P' in frame else [])]
    result={'n':len(frame),'target_sum':float(frame.snpp.sum()),'methods':{}}
    for method in available:
        error=frame[method]-frame.snpp
        totals=frame.groupby(['season','m'])[[method,'snpp']].sum()
        result['methods'][method]={'mae':float(error.abs().mean()) if len(frame) else None,
            'bias':float(error.mean()) if len(frame) else None,'prediction_sum':float(frame[method].sum()),
            'absolute_error_sum':float(error.abs().sum()),
            'regional_monthly_mae':float((totals[method]-totals.snpp).abs().mean()) if len(totals) else None}
    return result


def probability_metrics(frame):
    result={};edges=np.array([0.,.2,.4,.6,.8,1.])
    for name in PROBABILITIES:
        p=frame[name].to_numpy(dtype=float)
        if not np.isfinite(p).all() or ((p<0)|(p>1)).any():raise ValueError('Invalid probability')
        valid=frame.snpp.notna().to_numpy();x=p[valid];y=(frame.snpp.to_numpy()[valid]>0).astype(float)
        bins=np.clip(np.searchsorted(edges,x,side='right')-1,0,4);calibration=[]
        for b in range(5):
            selected=bins==b
            calibration.append({'lower':float(edges[b]),'upper':float(edges[b+1]),'upper_inclusive':b==4,
                'n':int(selected.sum()),'mean_probability':float(x[selected].mean()) if selected.any() else None,
                'positive_fraction':float(y[selected].mean()) if selected.any() else None})
        result[name]={'n':len(x),'unknown_targets':int((~valid).sum()),'brier':float(np.mean((x-y)**2)) if len(x) else None,'bins':calibration}
    return result


def factorial(frame,bootstrap=False):
    if not len(frame):return {'n':0,'losses':None,'delta_probability':None,'delta_positive_distribution':None,'interaction':None,'per_season':[]}
    losses={m:(frame[m]-frame.snpp).abs().to_numpy() for m in FACTORIAL}
    delta_p=losses['E10_10']-losses['E00_10'];delta_f=losses['E01_10']-losses['E00_10']
    interaction=losses['E11_10']-losses['E10_10']-losses['E01_10']+losses['E00_10']
    block=frame[['season']].assign(delta_probability=delta_p,delta_positive_distribution=delta_f,interaction=interaction).groupby('season').mean()
    result={'n':len(frame),'losses':{m:float(v.mean()) for m,v in losses.items()},
            'delta_probability':float(delta_p.mean()),'delta_positive_distribution':float(delta_f.mean()),
            'interaction':float(interaction.mean()),'per_season':block.reset_index().to_dict('records')}
    if bootstrap:
        if set(block.index)!=set(TRAIN):raise ValueError('Factorial bootstrap requires the eight development seasons')
        rng=np.random.default_rng(20261114);draws=rng.integers(0,len(block),size=(5000,len(block)))
        result['bootstrap']={'blocks':len(block),'replicates':5000,'seed':20261114,'exploratory':True,
            'intervals_95':{c:[float(v) for v in np.quantile(block[c].to_numpy()[draws].mean(axis=1),[.025,.975])] for c in block}}
    return result


def report(frame,enabled,bootstrap=False):
    result={}
    for label,cuts in [('all54',None),('published14',enabled)]:
        x=frame if cuts is None else frame[frame.cut.isin(cuts)]
        populations={'all_months':x,'active_months':x[x.snpp>0],'zero':x[x.snpp==0],
            'aqua_zero_viirs_positive':x[(x.aqua==0)&(x.snpp>0)],'both_observed_zero':x[(x.aqua==0)&(x.snpp==0)],
            'aqua_positive':x[x.aqua>0],'50_plus':x[x.snpp>=50]}
        result[label]={'populations':{name:metrics(g) for name,g in populations.items()},
                       'probabilities':probability_metrics(x),'factorial':factorial(x,bootstrap)}
    return result


def model_signature(model):
    return hashlib.sha256(json.dumps(model,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def pack_model(reference,affine,hurdle,choices):
    return {'schema_version':1,'training_seasons':list(TRAIN),'r_const':reference['ratio'],
      'reference_regional':reference['regional'].reset_index().to_dict('records'),
      'reference_local':reference['local'].reset_index().to_dict('records'),
      'reference_climatology':reference['climatology'].rename('clim').reset_index().to_dict('records'),
      'affine':affine.reset_index().to_dict('records'),'hurdle':hurdle,'choices':choices}


def unpack_model(model):
    if model.get('schema_version')!=1:raise ValueError('Unknown frozen hurdle schema')
    ref={'ratio':model['r_const'],'regional':pd.DataFrame(model['reference_regional']).set_index('g'),
         'local':pd.DataFrame(model['reference_local']).set_index(['cut','g']),
         'climatology':pd.DataFrame(model['reference_climatology']).set_index(['cut','m'])['clim']}
    return ref,pd.DataFrame(model['affine']).set_index(['cut','g']),model['hurdle'],model['choices']


def estimate_frozen(frame,model):
    from hurdle_model import predict_hurdle
    if frame.duplicated(KEYS).any():raise ValueError('Duplicate frozen estimation keys')
    ref,affine,hurdle,choices=unpack_model(model)
    features=frame[[*KEYS,'g','aqua']].copy()
    out=apply_choices(predict_hurdle(predict_affine(predict(features,ref),affine),hurdle),choices)
    diagnostic=[c for c in ['snpp','y','block','orbit_epoch'] if c in frame]
    return out.merge(frame[[*KEYS,*diagnostic]],on=KEYS,how='left',validate='one_to_one') if diagnostic else out


def write_model(model,path):
    path=Path(path);fingerprint=model_signature(model)
    path.write_text(json.dumps({'model_sha256':fingerprint,'model':model},indent=2,allow_nan=False)+'\n')
    return fingerprint


def load_model(path):
    wrapper=json.loads(Path(path).read_text());model=wrapper['model']
    if model_signature(model)!=wrapper['model_sha256']:raise ValueError('Frozen hurdle hash mismatch')
    unpack_model(model)
    return model


def protected_snapshot():
    paths=list((ROOT/'web/public/data').rglob('*.json'))
    paths += [DATA/f for f in ['detections.parquet','cells_comuna.parquet','celldays.parquet','static_mask.parquet','params.json','gates.csv','eval_loso.csv','eval_final.csv','inventory.csv']]
    for directory in [*[directory for _,directory in STAGES],'aggregation_audit']:
        paths+=list((DATA/directory).glob('*'))
    return {str(p.relative_to(ROOT)):sha(p) for p in paths if p.is_file()}


def run():
    from hurdle_model import fit_hurdle
    check_deadline();before=protected_snapshot();data=AuditData();enabled,_=publication_metadata(data.cuts)
    predictions=[];selections=[];coefficients=[];models={};fit_calls=[];loss_tables=[]
    for held in TRAIN:
        origin=tuple(s for s in TRAIN if s!=held)
        x,selection,params,model,calls,loss=transport(data,origin,(held,))
        predictions.append(x);selections.append(selection.assign(outer_held=held));coefficients.append(params.reset_index().assign(outer_held=held))
        models[str(held)]=model;fit_calls += [dict(c,outer_held=held,stage='nested') for c in calls]
        loss_tables.append(loss.reset_index().assign(outer_held=held));print('Hurdle outer fold complete:',held,flush=True)
    nested=pd.concat(predictions,ignore_index=True)
    previous=pd.read_csv(DATA/'affine_audit/outer_predictions.csv',dtype={'cut':str});verify_controls(nested,previous)
    nested=attach_piecewise(nested,pd.read_csv(DATA/'piecewise_audit/outer_predictions.csv',dtype={'cut':str}))
    if len(nested)!=5184 or len(fit_calls)!=64:raise ValueError('Incomplete nested hurdle design')
    blocked=[];temporal={};prior4=pd.read_csv(DATA/'temporal_transport_audit/predictions.csv',dtype={'cut':str});prior6=pd.read_parquet(DATA/'training_size_audit/predictions.parquet')
    for label,(origin,destination) in SPLITS.items():
        x,selection,_,_,calls,_=transport(data,origin,destination)
        direction=label.split('_')[0]
        old=prior4[prior4.direction==direction] if label.endswith('four') else prior6[(prior6.direction==direction)&(prior6.n_train==6)&(prior6.mask_policy=='fold_fitted')]
        verify_controls(x,old);x=attach_piecewise(x,old);blocked.append(x.assign(case=label));temporal[label]=report(x,enabled)
        fit_calls += [dict(c,case=label,stage='temporal') for c in calls]
        selections.append(selection.assign(case=label));print('Hurdle temporal case complete:',label,flush=True)
    full=data.monthly('fold_fitted',TRAIN);reference=fit_models(full);affine=fit_affine(full,reference)
    hurdle=fit_hurdle(full,reference);choices,full_loss=choose(nested)
    previous_model=load_frozen();previous_fingerprint=baseline_signature(previous_model)
    if abs(reference['ratio']-previous_model['reference']['ratio'])>1e-12 or choices['M1_B']!=previous_model['choices']['M1_B']:raise ValueError('Frozen baseline differs')
    frozen=pack_model(reference,affine,hurdle,choices);fingerprint=model_signature(frozen)
    OUT.mkdir(parents=True,exist_ok=True);write_model(frozen,OUT/'frozen_model.json');restored=load_model(OUT/'frozen_model.json')
    if model_signature(restored)!=fingerprint:raise ValueError('Frozen hurdle restoration failed')
    print('Hurdle model frozen before destination read:',fingerprint,flush=True)
    future=pd.read_parquet(DATA/'frozen_temporal_audit/predictions.parquet')
    later=estimate_frozen(future,restored);verify_controls(later,future);later=attach_piecewise(later,future)
    if len(later)!=3780 or sum(len(x) for x in blocked)!=7776:raise ValueError('Incomplete temporal destination grid')
    actual=estimate_frozen(full,restored);expected=estimate_frozen(full,frozen)
    if not np.array_equal(actual[list(METHODS)],expected[list(METHODS)]):raise ValueError('Saved hurdle estimates do not restore exactly')
    later_reports={label:report(g,enabled) for label,g in later.groupby('block')}
    legacy=later[later.block=='legacy_2020_2021']
    later_reports['legacy_before_calendar_2022']=report(legacy[legacy.y<2022],enabled)
    later_reports['legacy_jan_jun_2022']=report(legacy[legacy.y==2022],enabled)
    if model_signature(frozen)!=fingerprint or baseline_signature(previous_model)!=previous_fingerprint:raise ValueError('Model changed during evaluation')
    check_deadline()
    if before!=protected_snapshot():raise ValueError('Protected inputs/previous results changed')
    for name,frame in [('nested_predictions.parquet',nested),('blocked_predictions.parquet',pd.concat(blocked,ignore_index=True)),('later_predictions.parquet',later)]:frame.to_parquet(OUT/name,index=False,compression='zstd')
    pd.concat(selections,ignore_index=True).to_csv(OUT/'selection.csv',index=False)
    pd.concat(coefficients,ignore_index=True).to_csv(OUT/'outer_affine.csv',index=False)
    pd.concat(loss_tables,ignore_index=True).to_csv(OUT/'inner_losses.csv',index=False)
    pd.DataFrame(fit_calls).to_csv(OUT/'fit_seasons.csv',index=False);full_loss.to_csv(OUT/'full_selection_losses.csv')
    (OUT/'outer_hurdle_models.json').write_text(json.dumps(models,allow_nan=False)+'\n')
    summary={'status':'retrospective-hurdle-factorial','independent_validation':False,'controls_reproduced':True,
       'nested_fit_calls':64,'temporal_fit_calls':len(fit_calls)-64,'full_fit_calls':1,'nested_rows':len(nested),'later_rows':len(later),
       'source_baseline_signature':previous_fingerprint,'frozen_model_signature':fingerprint,'saved_model_restores_exactly':True,
       'nested':report(nested,enabled,bootstrap=True),'temporal_cases':temporal,'later':later_reports,
       'contrasts':[paired_bootstrap(nested,a,b) for a,b in [('B_E','M1_B'),('E11_10','M1_B'),('E11_10','E00_10'),('B_E','M1')]],
       'choice_counts':{p:pd.Series(mapping).value_counts().astype(int).to_dict() for p,mapping in choices.items()}}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    helpers=['scientific_audit.py','affine_experiment.py','hurdle_model.py','temporal_transport_audit.py','frozen_temporal_audit.py','robust_affine_experiment.py','reproduce_research.py']
    manifest={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'code_sha256':sha(Path(__file__)),
       'protocol_sha256':sha(PROTOCOL),'helpers_sha256':{name:sha(ROOT/'pipeline'/name) for name in helpers},
       'environment_sha256':{name:sha(ROOT/name) for name in ['pyproject.toml','uv.lock']},'protected_sha256':before,
       'original_unchanged':True,'output_sha256':{p.name:sha(p) for p in OUT.glob('*') if p.name!='manifest.json'}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n')
    print('Hurdle experiment complete:',OUT,flush=True)
    return summary


if __name__=='__main__':run()
