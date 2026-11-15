"""39: CRPS of an emitted finite weighted CDF; no fair-ensemble correction."""
import math
import numpy as np

WEIGHT_TOLERANCE=1e-12
ROUND_TOLERANCE=1e-10


def prepare(values,weights):
    x=np.asarray(values,dtype=float);w=np.asarray(weights,dtype=float)
    if x.ndim!=1 or w.shape!=x.shape or not len(x) or not np.isfinite(x).all() or not np.isfinite(w).all() or (w<0).any():raise ValueError('Invalid finite weighted CDF')
    total=math.fsum(float(v) for v in w)
    if total<=0 or abs(total-1)>WEIGHT_TOLERANCE:raise ValueError('Weights do not sum to one within1e-12')
    # Exactly one numerical normalization; no dropping, clamping or merging atoms.
    return x.copy(),np.asarray([float(v)/total for v in w]),total


def add_compensated(total,correction,value):
    new=total+value
    error=(total-new)+value if abs(total)>=abs(value) else (value-new)+total
    return new,math.fsum((correction,error))


def finalize(raw,y,eabsx):
    tolerance=ROUND_TOLERANCE*max(1.,abs(y),eabsx)
    if not math.isfinite(raw) or raw < -tolerance:raise ValueError('Negative/nonfinite CRPS beyond roundoff tolerance')
    return {'score':0. if raw<0 else raw,'raw_score':raw,'tolerance':tolerance,'negative_roundoff_clamped':bool(raw<0)}


def score_prepared(values,weights,y):
    """Weights already normalized ONCE by prepare; this function never divides."""
    x=np.asarray(values,dtype=float);w=np.asarray(weights,dtype=float);y=float(y)
    if x.ndim!=1 or w.shape!=x.shape or not len(x) or not np.isfinite(x).all() or not np.isfinite(w).all() or (w<0).any() or not math.isfinite(y):raise ValueError('Invalid prepared CDF/response')
    if abs(math.fsum(float(a) for a in w)-1)>WEIGHT_TOLERANCE:raise ValueError('Prepared weights invalid')
    order=np.argsort(x,kind='stable');x=x[order];w=w[order]
    terms=[];tw=cw=ts=cs=0.
    for value,weight in zip(x,w):
        value=float(value);weight=float(weight)
        beforew=math.fsum((tw,cw));befores=math.fsum((ts,cs))
        terms.append(weight*math.fsum((value*beforew,-befores)))
        tw,cw=add_compensated(tw,cw,weight)
        ts,cs=add_compensated(ts,cs,weight*value)
    eabs=math.fsum(float(a)*abs(float(v)-y) for v,a in zip(x,w))
    eabsx=math.fsum(float(a)*abs(float(v)) for v,a in zip(x,w))
    half=math.fsum(terms);raw=math.fsum((eabs,-half))
    result=finalize(raw,y,eabsx)
    return dict(result,expected_absolute_error=eabs,half_pair_term=half,EabsX=eabsx)


def crps(values,weights,y):
    x,w,total=prepare(values,weights)
    return dict(score_prepared(x,w,y),original_weight_sum=total)
