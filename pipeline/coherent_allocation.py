"""Protocol 18: nonnegative, total-constrained expected absolute-loss decisions.

Only predictive distributions and nonnegative baseline decisions are inputs. The
regional total is inherited from the baseline, not estimated from target labels.
Numerically tied marginal slopes use a fixed 1e-12 tolerance; no tuning occurs.
"""
import math

import numpy as np

SLOPE_TOLERANCE = 1e-12
TOTAL_TOLERANCE = 1e-10
KKT_TOLERANCE = 1e-8


def _canonical(distribution):
    try:
        values, weights = distribution
        values = np.asarray(values, dtype=float)
        weights = np.asarray(weights, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError('Distribution must contain values and probability weights') from exc
    if (values.ndim != 1 or values.shape != weights.shape or not len(values)
            or not np.isfinite(values).all() or not np.isfinite(weights).all()
            or (values < 0).any() or (weights < 0).any()):
        raise ValueError('Invalid nonnegative finite predictive distribution')
    total = math.fsum(float(w) for w in weights)
    if not total > 0 or not math.isclose(total, 1., rel_tol=TOTAL_TOLERANCE, abs_tol=TOTAL_TOLERANCE):
        raise ValueError('Distribution probabilities must sum to one')
    keep = weights > 0
    order = np.argsort(values[keep], kind='stable')
    values, weights = values[keep][order], weights[keep][order] / total
    distinct, starts = np.unique(values, return_index=True)
    ends = np.r_[starts[1:], len(values)]
    mass = np.array([math.fsum(float(w) for w in weights[a:b]) for a,b in zip(starts,ends)])
    mass /= math.fsum(float(w) for w in mass)
    return distinct, mass


def _inputs(distributions, allocation):
    try:
        allocation = np.asarray(allocation, dtype=float)
        distributions = list(distributions)
    except (TypeError, ValueError) as exc:
        raise ValueError('Invalid allocation inputs') from exc
    if (allocation.ndim != 1 or not len(allocation) or len(distributions) != len(allocation)
            or not np.isfinite(allocation).all() or (allocation < 0).any()):
        raise ValueError('Allocation must be a nonempty finite nonnegative vector')
    parsed = [_canonical(d) for d in distributions]
    try:
        total = math.fsum(float(a) for a in allocation)
    except OverflowError as exc:
        raise ValueError('Allocation total overflows') from exc
    if not np.isfinite(total):
        raise ValueError('Allocation total must be finite')
    return parsed, allocation, total


def _risk(parsed, allocation):
    return math.fsum(math.fsum(float(w)*abs(float(v)-float(a)) for v,w in zip(values,weights))
                     for (values,weights),a in zip(parsed,allocation))


def risk(distributions, allocation):
    """Total expected absolute loss under the supplied predictive distributions."""
    parsed, allocation, _ = _inputs(distributions, allocation)
    return float(_risk(parsed, allocation))


expected_risk = risk


def means(distributions):
    """Exact means of finite discrete target-unit distributions."""
    return np.array([math.fsum(float(v)*float(w) for v,w in zip(*_canonical(d)))
                     for d in distributions], dtype=float)


def _project_baseline(baseline, lower, upper, total):
    """Euclidean projection onto a box intersected with a fixed-total plane."""
    lo_total = math.fsum(float(a) for a in lower)
    hi_total = math.fsum(float(a) for a in upper)
    tolerance = TOTAL_TOLERANCE * max(1., abs(total))
    if lo_total > total + tolerance or hi_total < total - tolerance:
        raise ValueError('Infeasible optimum face')
    if (baseline >= lower).all() and (baseline <= upper).all():
        return baseline.copy()
    if total <= lo_total:
        return lower.copy()
    if total >= hi_total:
        return upper.copy()
    left = float(np.min(lower-baseline))
    right = float(np.max(upper-baseline))
    for _ in range(100):
        middle = .5*left + .5*right
        candidate = np.clip(baseline+middle, lower, upper)
        value = math.fsum(float(a) for a in candidate)
        if value < total:
            left = middle
        else:
            right = middle
    answer = np.clip(baseline + (.5*left+.5*right), lower, upper)
    # Symmetric residual repair preserves permutation equivariance. This only
    # corrects floating error within the same optimum face, never its budget.
    for _ in range(3):
        residual = total - math.fsum(float(a) for a in answer)
        if residual == 0:
            break
        slack = upper-answer if residual > 0 else answer-lower
        capacity = math.fsum(float(s) for s in slack)
        if capacity <= 0:
            break
        answer = np.clip(answer + residual*(slack/capacity), lower, upper)
    return answer


def _kkt(parsed, allocation):
    lower_cost = -1.
    upper_cost = 1.
    for (values, weights), a in zip(parsed, allocation):
        tolerance = TOTAL_TOLERANCE*np.maximum(1., np.maximum(np.abs(values), abs(a)))
        left = 2*math.fsum(float(w) for w in weights[values < a-tolerance])-1
        right = 2*math.fsum(float(w) for w in weights[values <= a+tolerance])-1
        if a > TOTAL_TOLERANCE*max(1.,abs(a)):
            lower_cost = max(lower_cost, left)
        upper_cost = min(upper_cost, right)
    return float(max(0., lower_cost-upper_cost))


def kkt_residual(distributions, allocation):
    """Violation of the common marginal-cost condition, with atom tolerance."""
    parsed, allocation, _ = _inputs(distributions, allocation)
    return _kkt(parsed, allocation)


def reconcile(distributions, baseline):
    """Minimize sum E|Y_i-a_i| given a>=0 and sum(a)=sum(baseline).

    The primary objective is piecewise linear. Fill marginal segments in cost
    order. The active equal-cost face is a box with a fixed sum; project the
    baseline onto it to resolve ties without an extra statistical hyperparameter.
    """
    parsed, baseline, total = _inputs(distributions, baseline)
    if total == 0:
        return baseline.copy()
    segments = []
    for index,(values, weights) in enumerate(parsed):
        points = np.unique(np.r_[0., values[(values>0)&(values<total)], total])
        cumulative = np.clip(np.cumsum(weights),0.,1.)
        cumulative[-1] = 1.
        prefix = np.r_[0., cumulative]
        positions = np.searchsorted(values,points[:-1],side='right')
        slopes = 2*prefix[positions]-1
        for a,b,cost in zip(points[:-1],points[1:],slopes):
            if b>a:
                segments.append((float(cost),index,float(a),float(b)))
    segments.sort(key=lambda row: row[0])
    lower = np.zeros(len(baseline),dtype=float)
    start = 0
    answer = None
    while start<len(segments):
        end = start+1
        cost = segments[start][0]
        while end<len(segments) and segments[end][0]-cost<=SLOPE_TOLERANCE:
            end += 1
        upper = lower.copy()
        for _,index,_,right in segments[start:end]:
            upper[index] = max(upper[index],right)
        capacity = math.fsum(float(u-l) for u,l in zip(upper,lower))
        remaining = total-math.fsum(float(a) for a in lower)
        if remaining <= capacity:
            answer = _project_baseline(baseline,lower,upper,total)
            break
        lower = upper
        start = end
    if answer is None:
        raise ValueError('No feasible marginal-cost allocation')
    tolerance = TOTAL_TOLERANCE*max(1.,abs(total))
    if ((answer<0).any() or not np.isfinite(answer).all()
            or abs(math.fsum(float(a) for a in answer)-total)>tolerance):
        raise ValueError('Coherent allocation violates its total')
    if _kkt(parsed,answer)>KKT_TOLERANCE:
        raise ValueError('Coherent allocation fails KKT verification')
    expected = _risk(parsed,answer)
    reference = _risk(parsed,baseline)
    if expected > reference + KKT_TOLERANCE*max(1.,abs(reference)):
        raise ValueError('Coherent allocation loses to feasible baseline under its CDF')
    return answer
