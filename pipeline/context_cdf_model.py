"""Protocol23: empirical source-only context weights over frozen sufficient stats."""
import json
import math

import numpy as np
import pandas as pd

from hurdle_model import _components, mixture_median
from coherent_allocation import _canonical

FACTORS=('C00','C10','C01','C11')
FEATURES=['cut','season','m','g','aqua']


def composition(values,available=True):
    if values is None and not available:return None
    x=np.asarray(values,dtype=float)
    if x.shape!=(18,) or not np.isfinite(x).all() or (x < -1e-12).any() or (x > 1+1e-12).any() or abs(float(x.sum())-1)>1e-8:
        raise ValueError('invalid_input: composition is not a valid18-simplex within closure tolerance')
    x=np.clip(x,0.,1.);x=x/x.sum()
    return x if available else None


def hellinger_squared(a,b):
    value=.5*math.fsum(float(v)**2 for v in np.sqrt(a)-np.sqrt(b))
    if not -1e-12<=value<=1+1e-12:raise ValueError('Invalid simplex Hellinger distance')
    return min(1.,max(0.,value))


def normalized_atoms(p,z,w,scale):
    z=np.asarray(z,dtype=float);w=np.asarray(w,dtype=float)
    if p==0:return np.array([0.]),np.array([1.])
    if not 0<p<=1 or not len(z) or not np.isfinite(z).all() or (z<=0).any() or not np.isfinite(w).all() or (w<0).any() or not w.sum()>0:
        raise ValueError('Invalid mixture components')
    return np.r_[0.,np.maximum(1.,scale*z)],np.r_[1-p,p*w/w.sum()]


def cdf_equal(a,b,tolerance=1e-12):
    av,aw=_canonical(a);bv,bw=_canonical(b)
    points=np.unique(np.r_[av,bv])
    def cdf(v,w):
        cum=np.r_[0.,np.cumsum(w)];return cum[np.searchsorted(v,points,side='right')]
    return bool(np.allclose(cdf(av,aw),cdf(bv,bw),rtol=0,atol=tolerance))


class ContextCDF:
    def __init__(self,hurdle,contexts,alpha=.5,bandwidth=.25,kappa=10):
        if not 0<=alpha<=1 or bandwidth<=0 or kappa!=10:raise ValueError('Invalid fixed context policy')
        self.hurdle=hurdle;self.alpha=float(alpha);self.bandwidth=float(bandwidth);self.kappa=kappa
        self.contexts={str(cut):composition(row.get('vector'),bool(row['available'])) for cut,row in contexts.items()}
        self.groups={};self.global_pool={};self.cache={};self.diagnostics=[]
        for key,stats in hurdle['locals'].items():
            cut,g,state=json.loads(key);cut,g=str(cut),str(g);state=int(state)
            n,m=int(stats['n']),int(stats['m']);z=np.asarray(stats['positive'],dtype=float)
            if n<0 or not 0<=m<=n or len(z)!=m or not np.isfinite(z).all() or (z<=0).any():raise ValueError('Invalid frozen local sufficient stats')
            if n:
                value={'n':n,'m':m,'positive':z}
                self.groups.setdefault((g,state),{})[cut]=value
                glob=self.global_pool.setdefault(cut,{'n':0,'m':0,'positive':[]})
                glob['n']+=n;glob['m']+=m;glob['positive'].extend(map(float,z))
        for v in self.global_pool.values():v['positive']=np.asarray(sorted(v['positive']),dtype=float)
        global_data=hurdle['global']
        if sum(v['n'] for v in self.global_pool.values())!=global_data['n'] or sum(v['m'] for v in self.global_pool.values())!=global_data['m']:
            raise ValueError('Frozen local/global counts do not reproduce')
        gathered=sorted(float(z) for v in self.global_pool.values() for z in v['positive'])
        if not np.array_equal(gathered,np.asarray(global_data['positive'],dtype=float)):raise ValueError('Frozen local/global positive atoms do not reproduce')
        for key,parent in hurdle['parents'].items():
            g,state=json.loads(key);pool=self.groups.get((str(g),int(state)),{})
            if sum(v['n'] for v in pool.values())!=parent['source_n'] or sum(v['m'] for v in pool.values())!=parent['source_m']:
                raise ValueError('Frozen parent/local counts do not reproduce')
        if bool(hurdle['all_zero'])!=(global_data['m']==0):raise ValueError('Frozen zero-support flag inconsistent')

    def weights(self,pool,query_cut,pool_label):
        cuts=sorted(pool);n=np.asarray([pool[c]['n'] for c in cuts],dtype=float)
        N=int(n.sum());q=self.contexts.get(str(query_cut));known=np.array([self.contexts.get(c) is not None for c in cuts])
        distances=np.array([hellinger_squared(q,self.contexts[c]) if q is not None and self.contexts.get(c) is not None else np.nan for c in cuts])
        K=np.array([math.exp(-d/(2*self.bandwidth**2)) if np.isfinite(d) else 0. for d in distances]);mass=math.fsum(float(k)*float(v) for k,v in zip(K,n))
        if self.alpha==0:reason='alpha_zero';w=np.ones(len(cuts))
        elif q is None:reason='query_context_unknown';w=np.ones(len(cuts))
        elif not mass>0:reason='no_context_mass_in_pool';w=np.ones(len(cuts))
        elif known.all() and np.all(K==K[0]):reason='constant_known_kernel';w=np.ones(len(cuts))
        else:reason='context_weighted';w=(1-self.alpha)+self.alpha*K*N/mass
        weighted_n=math.fsum(float(a)*float(b) for a,b in zip(w,n))
        if abs(weighted_n-N)>1e-10*max(1,N):raise ValueError('Context normalization does not preserve poolN')
        diagnostic={'query_cut':str(query_cut),'pool':pool_label,'N':N,'source_cuts':len(cuts),'known_context_source_cuts':int(known.sum()),
          'kernel_mass_n':float(mass),'weighted_N':float(weighted_n),'fallback':reason,
          'min_H_squared':float(np.nanmin(distances)) if np.isfinite(distances).any() else None,
          'min_H':float(np.sqrt(np.nanmin(distances))) if np.isfinite(distances).any() else None,
          'maximum_weight':float(w.max()) if len(w) else None,
          'ESS_observations':float(N*N/math.fsum(float(a*a*b) for a,b in zip(w,n))) if N else None,
          'ESS_CUT':float(N*N/math.fsum(float(a*b)**2 for a,b in zip(w,n))) if N else None,
          'weights':{c:float(v) for c,v in zip(cuts,w)}}
        return dict(zip(cuts,map(float,w))),diagnostic

    @staticmethod
    def positive_atoms(pool,weights):
        values=[];mass=[]
        for cut in sorted(pool):
            zs=pool[cut]['positive'];values.extend(map(float,zs));mass.extend([float(weights[cut])]*len(zs))
        z=np.asarray(values,dtype=float);w=np.asarray(mass,dtype=float)
        order=np.argsort(z,kind='stable');return z[order],w[order]

    def components(self,cut,g,state):
        cut,g=str(cut),str(g);state=int(state);key=(cut,g,state)
        if key in self.cache:return self.cache[key]
        if g not in self.hurdle['regional_ratio']:raise ValueError('Missing SOURCE calendar normalization')
        pp0,p0,pz0,pw0,z0,w0=_components(self.hurdle,cut,g,state,10)
        if self.hurdle['all_zero']:
            answer=((p0,z0,w0),(0.,z0,w0));self.cache[key]=answer
            self.diagnostics.append({'query_cut':cut,'g':g,'state':state,'pool':'all_zero','fallback':'global_degenerate_zero'})
            return answer
        pool=self.groups.get((g,state));probability_pool=f'group:{g}:{state}'
        if not pool:pool=self.global_pool;probability_pool='global_group_empty'
        weights,diag=self.weights(pool,cut,probability_pool)
        N=sum(v['n'] for v in pool.values());weighted_m=math.fsum(weights[c]*v['m'] for c,v in pool.items())
        pp1=float((weighted_m+.5)/(N+1))
        z,w=self.positive_atoms(pool,weights);diags=[diag]
        if not len(z):
            weights,global_diag=self.weights(self.global_pool,cut,'global_positive_fallback')
            z,w=self.positive_atoms(self.global_pool,weights);diags.append(global_diag)
        if not len(z) or not w.sum()>0:raise ValueError('Context parent positive support missing')
        # Exact original path when empirical weights make the same parent pair.
        parent_equal=pp1==pp0 and np.array_equal(z,pz0) and np.array_equal(w,np.ones(len(pz0)))
        if parent_equal:p1,z1,w1=p0,z0,w0
        else:
            local=self.hurdle['locals'].get(json.dumps([cut,g,state],separators=(',',':'),ensure_ascii=False),{'n':0,'m':0,'positive':[]})
            if not local['n']:p1,z1,w1=pp1,z,w
            else:
                p1=float((local['m']+10*pp1)/(local['n']+10))
                if not local['m']:z1,w1=z,w
                else:
                    z1=np.r_[np.asarray(local['positive'],dtype=float),z]
                    w1=np.r_[np.ones(local['m']),w/w.sum()*(10*pp1)]
        if not 0<=p1<=1:raise ValueError('Invalid contextual probability')
        for d in diags:d.update(g=g,state=state,parent_probability=pp1,final_probability=float(p1),positive_fallback_global=len(diags)>1)
        self.diagnostics.extend(diags)
        answer=((p0,z0,w0),(float(p1),z1,w1));self.cache[key]=answer
        return answer

    def predict(self,features):
        if set(features)!=set(FEATURES):raise ValueError('Context inference accepts feature columns only; target labels forbidden')
        if features.duplicated(['cut','season','m']).any():raise ValueError('Duplicate context query keys')
        if not np.isfinite(features.aqua.to_numpy(dtype=float)).all() or (features.aqua<0).any():raise ValueError('Invalid query Aqua')
        out=features[FEATURES].copy().reset_index(drop=True);values={m:[] for m in FACTORS};dist0=[];dist1=[];prob0=[];prob1=[]
        for row in out.itertuples(index=False):
            cut,season,month,g,aqua=row;pair0,pair1=self.components(cut,g,int(aqua>0))
            p0,z0,w0=pair0;p1,z1,w1=pair1;scale=1+float(aqua)*self.hurdle['regional_ratio'][str(g)]
            for method,(p,z,w) in zip(FACTORS,[(p0,z0,w0),(p1,z0,w0),(p0,z1,w1),(p1,z1,w1)]):
                values[method].append(mixture_median(p,z,w,scale))
            dist0.append(normalized_atoms(p0,z0,w0,scale));dist1.append(normalized_atoms(p1,z1,w1,scale))
            prob0.append(p0);prob1.append(p1)
        for method,values_ in values.items():out[method]=values_
        out['p0']=prob0;out['p1']=prob1
        return out,dist0,dist1
