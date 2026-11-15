"""Protocol 17: a coherent empirical hurdle CDF, fitted on origin data only.

Probabilities concern a positive *recorded S-NPP count*, not physical fire or
observation opportunity. Point predictions are mixture medians for MAE; their
sum is not an estimate of the predictive mean of a regional total.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

KAPPAS = (3, 10, 30)
METHODS = ('E00_10', 'E10_10', 'E01_10', 'E11_3', 'E11_10', 'E11_30')
PROBABILITIES = ('p_parent', 'p_local_10')
TRAINING_POOL = frozenset(range(2012, 2020))


def _key(*parts):
    return json.dumps(list(parts), separators=(',', ':'), ensure_ascii=False)


def _finite_nonnegative(frame, columns):
    try:
        values = frame[list(columns)].to_numpy(dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError('Invalid hurdle observations') from exc
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError('Hurdle observations must be finite and nonnegative')


def _identifiers(frame):
    if frame[['cut', 'g']].isna().any().any():
        raise ValueError('Missing hurdle group identifiers')
    if any(not str(v) for c in ['cut', 'g'] for v in frame[c]):
        raise ValueError('Empty hurdle group identifiers')
    keys = ['cut', 'season', 'm']
    if set(keys) <= set(frame) and frame.duplicated(keys).any():
        raise ValueError('Duplicate hurdle observation keys')


def _positive(values):
    return sorted(float(v) for v in values if v > 0)


def fit_hurdle(training, reference):
    """Return a JSON-serializable origin model, without any destination query.

    `reference` is the same origin-only fit_models result used by the B control.
    The caller fits the static mask inside its origin before calling this helper.
    """
    required = {'cut', 'g', 'aqua', 'snpp', 'season'}
    if not required <= set(training) or not len(training):
        raise ValueError('Missing or empty hurdle training observations')
    _identifiers(training)
    _finite_nonnegative(training, ['aqua', 'snpp'])
    seasons = set(training.season)
    if not seasons or not seasons <= TRAINING_POOL:
        raise ValueError('Hurdle fitting must stay within seasons 2012–2019')
    t = training[['cut', 'g', 'aqua', 'snpp']].copy()
    t['cut'] = t.cut.map(str)
    t['g'] = t.g.map(str)
    ratios = {str(g): float(r) for g, r in reference['regional']['rR'].items()
              if str(g) in set(t.g)}
    if set(ratios) != set(t.g) or not all(np.isfinite(r) and r >= 0 for r in ratios.values()):
        raise ValueError('Missing or invalid origin regional ratio')
    t['state'] = (t.aqua > 0).astype(int)
    scale = 1 + t.aqua.to_numpy(dtype=float) * t.g.map(ratios).to_numpy(dtype=float)
    if not np.isfinite(scale).all() or (scale < 1).any():
        raise ValueError('Invalid hurdle normalization')
    t['z'] = t.snpp.to_numpy(dtype=float) / scale
    global_positive = _positive(t.z)
    if any(v <= 0 or not np.isfinite(v) for v in global_positive):
        raise ValueError('Invalid normalized positive support')
    global_data = {'n': int(len(t)), 'm': int((t.snpp > 0).sum()),
                   'positive': global_positive}
    all_zero = not global_positive
    parents = {}
    for g in sorted(ratios):
        for state in (0, 1):
            source = t[(t.g == g) & (t.state == state)]
            source_n = int(len(source))
            source_m = int((source.snpp > 0).sum())
            effective = source if source_n else t
            n = int(len(effective))
            m = int((effective.snpp > 0).sum())
            positives = _positive(effective.z)
            probability_source = 'regional' if source_n else 'global_no_parent'
            positive_source = probability_source
            if not positives and not all_zero:
                positives = global_positive.copy()
                positive_source = 'global_no_positive'
            parents[_key(g, state)] = {
                'source_n': source_n, 'source_m': source_m,
                'n': n, 'm': m, 'p': 0.0 if all_zero else float((m + .5) / (n + 1)),
                'positive': positives, 'probability_source': probability_source,
                'positive_source': positive_source,
            }
    locals_ = {}
    for (cut, g, state), group in t.groupby(['cut', 'g', 'state'], sort=True):
        locals_[_key(str(cut), str(g), int(state))] = {
            'n': int(len(group)), 'm': int((group.snpp > 0).sum()),
            'positive': _positive(group.z),
        }
    model = {
        'schema_version': 1, 'training_seasons': sorted(int(s) for s in seasons),
        'kappas': list(KAPPAS), 'regional_ratio': dict(sorted(ratios.items())),
        'all_zero': all_zero, 'global': global_data,
        'parents': parents, 'locals': locals_,
    }
    # Reject accidentally non-serializable/non-finite fitted state immediately.
    signature(model)
    return model


def weighted_quantile(values, weights, probability):
    """Lower quantile of a finite weighted discrete distribution, no interpolation."""
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if (values.ndim != 1 or values.shape != weights.shape or not len(values)
            or not np.isfinite(values).all() or not np.isfinite(weights).all()
            or (weights < 0).any() or not weights.sum() > 0
            or not np.isfinite(probability) or not 0 <= probability <= 1):
        raise ValueError('Invalid weighted quantile')
    keep = weights > 0
    values, weights = values[keep], weights[keep]
    order = np.argsort(values, kind='stable')
    values, weights = values[order], weights[order]
    # Combining equal atoms makes ties independent of order within a tied value.
    values, starts = np.unique(values, return_index=True)
    weights = np.add.reduceat(weights, starts)
    cumulative = np.cumsum(weights)
    position = int(np.searchsorted(cumulative, probability * cumulative[-1], side='left'))
    return float(values[min(position, len(values) - 1)])


def mixture_median(probability, positive_values, positive_weights, scale=1.0):
    """Median of mass 1-p at zero plus max(1, scale * positive residual)."""
    if (not np.isfinite(probability) or not 0 <= probability <= 1
            or not np.isfinite(scale) or scale < 1):
        raise ValueError('Invalid hurdle mixture')
    values = np.asarray(positive_values, dtype=float)
    weights = np.asarray(positive_weights, dtype=float)
    if probability > 0 and (not len(values) or values.shape != weights.shape
            or not np.isfinite(values).all() or (values <= 0).any()
            or not np.isfinite(weights).all() or (weights < 0).any() or not weights.sum() > 0):
        raise ValueError('Missing or invalid strictly positive hurdle support')
    if probability <= .5:
        return 0.0
    level = (probability - .5) / probability
    q = weighted_quantile(values, positive_weights, level)
    answer = max(1.0, float(scale) * q)
    if not np.isfinite(answer):
        raise ValueError('Non-finite hurdle median')
    return answer


def _components(model, cut, g, state, kappa):
    """Return coherent parent/local probabilities and conditional positive CDFs."""
    parent = model['parents'][_key(g, state)]
    local = model['locals'].get(_key(cut, g, state), {'n': 0, 'm': 0, 'positive': []})
    pp = float(parent['p'])
    parent_values = np.asarray(parent['positive'], dtype=float)
    parent_weights = np.ones(len(parent_values), dtype=float)
    if model['all_zero']:
        return 0.0, 0.0, parent_values, parent_weights, parent_values, parent_weights
    if not local['n']:
        return pp, pp, parent_values, parent_weights, parent_values, parent_weights
    pl = float((local['m'] + kappa * pp) / (local['n'] + kappa))
    # With no local positive mass, the conditional positive distribution remains
    # exactly the parent. Avoid rounding artifacts from canceling its common mass.
    if not local['m']:
        return pp, pl, parent_values, parent_weights, parent_values, parent_weights
    local_values = np.asarray(local['positive'], dtype=float)
    prior_weight = kappa * pp / len(parent_values)
    combined_values = np.r_[local_values, parent_values]
    combined_weights = np.r_[np.ones(len(local_values)), np.full(len(parent_values), prior_weight)]
    return pp, pl, parent_values, parent_weights, combined_values, combined_weights


def predict_hurdle(frame, model):
    """Add the fixed factorial and secondary medians; destination labels are ignored."""
    if model.get('schema_version') != 1 or model.get('kappas') != list(KAPPAS):
        raise ValueError('Unknown hurdle model schema')
    if not {'cut', 'g', 'aqua'} <= set(frame):
        raise ValueError('Missing hurdle prediction features')
    _identifiers(frame)
    _finite_nonnegative(frame, ['aqua'])
    groups = [(str(cut), str(g), int(aqua > 0))
              for cut, g, aqua in zip(frame.cut, frame.g, frame.aqua)]
    if not set(str(g) for g in frame.g) <= set(model['regional_ratio']):
        raise ValueError('Unknown calendar group: no origin normalization')
    cache = {}
    for cut, g, state in sorted(set(groups)):
        info = {}
        for kappa in KAPPAS:
            pp, pl, pv, pw, lv, lw = _components(model, cut, g, state, kappa)
            if kappa == 10:
                # Store normalized positive quantiles, not scale=1 medians:
                # clipping before a later scale would be mathematically wrong.
                info['p_parent'], info['p_local_10'] = pp, pl
                info['E00_10'] = _normalized_median(pp, pv, pw)
                info['E10_10'] = _normalized_median(pl, pv, pw)
                info['E01_10'] = _normalized_median(pp, lv, lw)
            info[f'E11_{kappa}'] = _normalized_median(pl, lv, lw)
        cache[(cut, g, state)] = info
    out = frame.copy()
    scale = 1 + np.asarray(frame.aqua, dtype=float) * np.array([model['regional_ratio'][str(g)] for g in frame.g])
    if not np.isfinite(scale).all():
        raise ValueError('Non-finite destination normalization')
    for method in METHODS:
        q = np.array([cache[key][method] for key in groups], dtype=float)
        out[method] = np.where(q == 0, 0.0, np.maximum(1.0, scale * q))
    for probability in PROBABILITIES:
        out[probability] = np.array([cache[key][probability] for key in groups], dtype=float)
    if not np.isfinite(out[[*METHODS, *PROBABILITIES]].to_numpy()).all():
        raise ValueError('Non-finite hurdle predictions')
    return out


def _normalized_median(probability, values, weights):
    if probability <= .5:
        return 0.0
    return weighted_quantile(values, weights, (probability - .5) / probability)


def signature(model):
    """Stable semantic hash, independent of dict insertion order and file whitespace."""
    raw = json.dumps(model, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def write_hurdle(model, path):
    path = Path(path)
    payload = {'schema_version': 1, 'model_sha256': signature(model), 'model': model}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n')
    return payload['model_sha256']


def load_hurdle(path):
    payload = json.loads(Path(path).read_text())
    if payload.get('schema_version') != 1 or payload.get('model_sha256') != signature(payload['model']):
        raise ValueError('Hurdle model hash mismatch or unknown schema')
    model = payload['model']
    if model.get('schema_version') != 1 or model.get('kappas') != list(KAPPAS):
        raise ValueError('Unknown hurdle model schema')
    return model
