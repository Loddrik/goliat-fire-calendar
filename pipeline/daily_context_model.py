"""37: SOURCE-only binary daily context, full-CDF mixtures in raw Z units."""
import hashlib
import json

import numpy as np
import pandas as pd

from hurdle_model import _components, _key, weighted_quantile

FIT_CALLS=0
KAPPA=10.0
KEYS=['cut','season','m']
FEATURES=KEYS+['g','aqua','D']


def signature(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def selected_training(frame,base):
    """Filter identifiers BEFORE inspecting any response; allows synthetic poisons."""
    required=set(FEATURES+['snpp'])
    if not required<=set(frame):raise ValueError('Training schema missing')
    selected=frame[frame.cut.astype(str).isin(base['source_cuts']) & frame.season.isin(base['origin_seasons'])][FEATURES+['snpp']].copy()
    if selected.empty or selected.duplicated(KEYS).any():raise ValueError('Empty or duplicate SOURCE training')
    values=selected[['aqua','snpp','D']].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values<0).any() or not set(selected.D)<=set((0,1)):raise ValueError('Invalid selected observations')
    if not set(selected.g.astype(str))<=set(base['regional_ratio']):raise ValueError('Unknown SOURCE calendar group')
    if ((selected.aqua<=1)&(selected.D!=0)).any():raise ValueError('D implies at least two registered cell-days')
    return selected


def sufficient(frame):
    z=frame.z.to_numpy(dtype=float)
    return {'n':int(len(z)),'m':int((z>0).sum()),'positive':sorted(float(v) for v in z if v>0)}


def fit_context(frame,base,variant='synthetic'):
    global FIT_CALLS
    FIT_CALLS+=1
    t=selected_training(frame,base)
    t['cut']=t.cut.astype(str);t['g']=t.g.astype(str);t['state']=(t.aqua>0).astype(int)
    scale=1+t.aqua.to_numpy(dtype=float)*t.g.map(base['regional_ratio']).to_numpy(dtype=float)
    t['z']=t.snpp.to_numpy(dtype=float)/scale
    pools={};locals_={}
    for g in sorted(base['regional_ratio']):
        for state in (0,1):
            group=t[(t.g==g)&(t.state==state)]
            values=sorted(int(v) for v in group.D.unique())
            active=len(values)>1
            pools[_key(g,state)]={'active':active,'observed_D':values,'n':len(group),'classes':{str(d):sufficient(group[group.D==d]) for d in (0,1)}}
            if active:
                for (cut,d),local in group.groupby(['cut','D'],sort=True):locals_[_key(cut,g,state,int(d))]=sufficient(local)
    roster=t[KEYS].sort_values(KEYS).to_dict(orient='records')
    model={'schema_version':1,'variant':variant,'kappa_parent':10,'kappa_local':10,'source_cuts':sorted(base['source_cuts']),'origin_seasons':sorted(base['origin_seasons']),'base_model_sha256':signature(base),'training_keys':roster,'training_rows':len(t),'pools':pools,'locals':locals_}
    signature(model)
    return model


def old_raw_distribution(base,cut,g,state,parent=False):
    pp,pl,pv,pw,lv,lw=_components(base['hurdle'],str(cut),str(g),int(state),10)
    p,z,w=(pp,pv,pw) if parent else (pl,lv,lw)
    if p==0:return np.array([0.]),np.array([1.])
    return np.r_[0.,z],np.r_[1-p,p*w/w.sum()]


def empirical_prior_mix(stats,prior):
    values,weights=prior
    n=int(stats['n']);m=int(stats['m']);positive=np.asarray(stats['positive'],dtype=float)
    if n<0 or not 0<=m<=n or len(positive)!=m or (positive<=0).any():raise ValueError('Invalid sufficient statistics')
    if n==0:return values.copy(),weights.copy()
    empirical=np.r_[np.zeros(n-m),positive]
    return np.r_[empirical,values],np.r_[np.full(n,1/(n+10.)),weights*(10./(n+10.))]


def raw_distribution(model,base,cut,g,aqua,d):
    if d not in (0,1) or not np.isfinite(aqua) or aqua<0:raise ValueError('Invalid query')
    g=str(g);cut=str(cut);state=int(aqua>0)
    if g not in base['regional_ratio']:raise ValueError('Unknown query group')
    pool=model['pools'][_key(g,state)]
    if not pool['active']:
        return old_raw_distribution(base,cut,g,state),{'fallback':'original_full_CDF_no_SOURCE_D_variation','parent_n':pool['n'],'local_n':None}
    oldparent=old_raw_distribution(base,cut,g,state,parent=True)
    stats=pool['classes'][str(d)]
    parent=empirical_prior_mix(stats,oldparent)
    empty={'n':0,'m':0,'positive':[]}
    local=model['locals'].get(_key(cut,g,state,d),empty) if cut in model['source_cuts'] else empty
    result=empirical_prior_mix(local,parent)
    return result,{'fallback':'contextual_parent' if not local['n'] else 'contextual_local','parent_n':stats['n'],'parent_m':stats['m'],'local_n':local['n'],'local_m':local['m'],'parent_borrowed_mass':10/(stats['n']+10),'local_borrowed_mass':10/(local['n']+10)}


def scale_distribution(distribution,scale):
    values,weights=distribution
    values=np.asarray(values,dtype=float);weights=np.asarray(weights,dtype=float)
    if not np.isfinite(scale) or scale<1:raise ValueError('Invalid query scale')
    out=np.where(values>0,np.maximum(1.,scale*values),0.)
    if not np.isfinite(out).all() or not np.isfinite(weights).all() or (weights<0).any() or abs(float(weights.sum())-1)>1e-10:raise ValueError('Invalid distribution')
    return out,weights.copy()


def distribution(model,base,cut,g,aqua,d):
    raw,diagnostic=raw_distribution(model,base,cut,g,aqua,d)
    return scale_distribution(raw,1+float(aqua)*base['regional_ratio'][str(g)]),diagnostic


def canonical(distribution):
    v,w=distribution;v=np.asarray(v);w=np.asarray(w);keep=w>0
    v=v[keep];w=w[keep];order=np.argsort(v,kind='stable');v=v[order];w=w[order]
    values,starts=np.unique(v,return_index=True)
    return values,np.add.reduceat(w,starts)


def same_cdf(a,b,tolerance=1e-10):
    av,aw=canonical(a);bv,bw=canonical(b)
    return np.array_equal(av,bv) and np.allclose(aw,bw,atol=tolerance,rtol=0)


def predict_distributions(features,model,base):
    if set(features)!=set(FEATURES) or features.duplicated(KEYS).any():raise ValueError('Inference requires exact feature whitelist/unique keys')
    ds=[];diagnostics=[];medians=[];probabilities=[]
    for row in features[FEATURES].itertuples(index=False,name=None):
        cut,season,m,g,aqua,d=row
        ds0,meta=distribution(model,base,str(cut),str(g),float(aqua),int(d))
        medians.append(weighted_quantile(*ds0,.5));probabilities.append(float(ds0[1][ds0[0]>0].sum()))
        ds.append(ds0);diagnostics.append(dict(cut=str(cut),season=int(season),m=int(m),g=str(g),D=int(d),**meta))
    return ds,np.asarray(medians),np.asarray(probabilities),diagnostics
