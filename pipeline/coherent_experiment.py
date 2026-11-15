"""Protocol 18: fixed-CDF decisions, no destination-dependent fitting."""
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from scientific_audit import ROOT, DATA, TRAIN, AuditData, sha
from hurdle_model import _components, predict_hurdle
from hurdle_experiment import (SPLITS, fit_predict, load_model, protected_snapshot,
                              model_signature)
from frozen_temporal_audit import KEYS, publication_metadata
from robust_affine_experiment import check_deadline
from affine_experiment import paired_bootstrap

OUT = DATA / 'coherent_audit'
SOURCE = DATA / 'hurdle_audit'
METHODS = ('M1', 'M1_B', 'E11_10', 'E_mean', 'E_coherent', 'E_proportional')
NEW = ('E_mean', 'E_coherent', 'E_proportional')
PROTOCOL = ROOT / 'docs/reviews/2026-11-14-science-protocol-18.md'


def distributions(frame, model):
    """Only features enter the predictive distribution; labels are inaccessible."""
    result = []
    for row in frame[['cut', 'g', 'aqua']].itertuples(index=False):
        cut, g = str(row.cut), str(row.g)
        _, p, _, _, z, w = _components(model, cut, g, int(row.aqua > 0), 10)
        if p == 0:
            result.append((np.array([0.]), np.array([1.])))
        else:
            s = 1 + float(row.aqua) * model['regional_ratio'][g]
            result.append((np.r_[0., np.maximum(1., s*z)], np.r_[1-p, p*w/w.sum()]))
    return result


def extend(frame, model):
    from coherent_allocation import reconcile, expected_risk, kkt_residual
    if frame.duplicated(KEYS).any():
        raise ValueError('Duplicate decision keys')
    features = frame[[*KEYS, 'g', 'aqua', 'M1_B', 'E11_10']].copy().reset_index(drop=True)
    restored = predict_hurdle(features[['cut', 'season', 'm', 'g', 'aqua']], model)
    if not np.allclose(restored.E11_10, features.E11_10, atol=1e-10, rtol=0):
        raise ValueError('Source median did not reproduce')
    ds = distributions(features, model)
    features['E_mean'] = [float(np.dot(v, w)) for v, w in ds]
    features['E_coherent'] = np.nan
    features['E_proportional'] = np.nan
    checks = []
    for key, group in features.groupby(['season', 'm'], sort=True):
        check_deadline()
        if len(group) != 54 or group.cut.nunique() != 54:
            raise ValueError('Reconciliation requires all 54 communes')
        ix = group.index.to_numpy(); b = group.M1_B.to_numpy(dtype=float)
        d = [ds[i] for i in ix]
        allocation = reconcile(d, b)
        med = group.E11_10.to_numpy(dtype=float)
        proportional = med * (b.sum()/med.sum()) if med.sum() else b.copy()
        tolerance = 1e-10 * max(1., b.sum())
        for a in (allocation, proportional):
            if not np.isfinite(a).all() or (a < 0).any() or abs(a.sum()-b.sum()) > tolerance:
                raise ValueError('Regional budget was not preserved')
        original_risk = expected_risk(d, b)
        allocated_risk = expected_risk(d, allocation)
        if allocated_risk > original_risk + 1e-8*max(1., original_risk):
            raise ValueError('Expected CDF risk exceeds feasible baseline')
        features.loc[ix, 'E_coherent'] = allocation
        features.loc[ix, 'E_proportional'] = proportional
        checks.append({'season': int(key[0]), 'm': int(key[1]), 'budget': float(b.sum()),
                       'baseline_expected_risk': float(original_risk),
                       'allocated_expected_risk': float(allocated_risk),
                       'kkt_residual': kkt_residual(d, allocation),
                       'allocations_above_support': sum(float(a) > float(v.max())+1e-10 for a,(v,w) in zip(allocation,d)),
                       'budget_error': float(allocation.sum()-b.sum())})
    out = frame.reset_index(drop=True).copy()
    out[list(NEW)] = features[list(NEW)]
    return out, checks


def metrics(frame):
    result = {'n': len(frame), 'methods': {}}
    for method in METHODS:
        e = frame[method]-frame.snpp
        totals = frame.groupby(['season', 'm'])[[method, 'snpp']].sum()
        result['methods'][method] = {
            'mae': float(e.abs().mean()) if len(e) else None,
            'mse': float((e*e).mean()) if len(e) else None,
            'bias': float(e.mean()) if len(e) else None,
            'prediction_sum': float(frame[method].sum()),
            'regional_monthly_mae': float((totals[method]-totals.snpp).abs().mean()) if len(totals) else None}
    return result


def report(frame, enabled):
    result = {}
    for name, cuts in [('all54', None), ('published14', set(enabled)),
                       ('remaining40', set(frame.cut)-set(enabled))]:
        x = frame if cuts is None else frame[frame.cut.isin(cuts)]
        result[name] = {label: metrics(g) for label, g in {
            'all_months': x, 'active_months': x[x.snpp>0], 'zero': x[x.snpp==0],
            'aqua_zero_viirs_positive': x[(x.aqua==0)&(x.snpp>0)],
            'both_observed_zero': x[(x.aqua==0)&(x.snpp==0)],
            '50_plus': x[x.snpp>=50]}.items()}
    return result


def run():
    check_deadline(); before = protected_snapshot()
    for directory in ('zero_anchor_audit', 'hurdle_audit'):
        before.update({str(p.relative_to(ROOT)): sha(p) for p in (DATA/directory).glob('*') if p.is_file()})
    data = AuditData(); enabled, _ = publication_metadata(data.cuts)
    models = json.loads((SOURCE/'outer_hurdle_models.json').read_text())
    source_nested = pd.read_parquet(SOURCE/'nested_predictions.parquet')
    pieces = []; checks = []
    for held in TRAIN:
        original = source_nested[source_nested.season == held].copy()
        x, audit = extend(original, models[str(held)])
        # Deliberately discard/change destination labels and check predictions.
        poisoned = original.drop(columns='snpp').copy()
        again, _ = extend(poisoned, models[str(held)])
        if not np.array_equal(x[list(NEW)], again[list(NEW)]):
            raise ValueError('Destination labels changed decisions')
        pieces.append(x); checks += [dict(c, stage='nested') for c in audit]
        print('Coherent nested complete:', held, flush=True)
    nested = pd.concat(pieces, ignore_index=True)
    blocked_source = pd.read_parquet(SOURCE/'blocked_predictions.parquet')
    blocked = []; transport_models = {}
    for label, (origin, destination) in SPLITS.items():
        raw, _, model = fit_predict(data, origin, destination)
        previous = blocked_source[blocked_source.case == label].copy()
        a = raw.sort_values(KEYS); b = previous.sort_values(KEYS)
        if not a[KEYS].reset_index(drop=True).equals(b[KEYS].reset_index(drop=True)) or not np.allclose(a.E11_10, b.E11_10, atol=1e-10, rtol=0):
            raise ValueError('Temporal CDF reconstruction changed')
        x, audit = extend(previous, model)
        blocked.append(x); checks += [dict(c, stage=label) for c in audit]
        transport_models[label] = model
        print('Coherent transport complete:', label, flush=True)
    frozen = load_model(SOURCE/'frozen_model.json'); fingerprint = model_signature(frozen)
    later, audit = extend(pd.read_parquet(SOURCE/'later_predictions.parquet'), frozen['hurdle'])
    checks += [dict(c, stage='later') for c in audit]
    if model_signature(frozen) != fingerprint:
        raise ValueError('Frozen model changed')
    for path, digest in before.items():
        if sha(ROOT/path) != digest:
            raise ValueError('Protected input changed: '+path)
    check_deadline(); OUT.mkdir(parents=True, exist_ok=True)
    blocked = pd.concat(blocked, ignore_index=True)
    for name, frame in [('nested', nested), ('blocked', blocked), ('later', later)]:
        frame.to_parquet(OUT/(name+'_predictions.parquet'), index=False, compression='zstd')
    pd.DataFrame(checks).to_csv(OUT/'allocation_checks.csv', index=False)
    (OUT/'transport_hurdle_models.json').write_text(json.dumps(transport_models, allow_nan=False)+'\n')
    summary = {'status': 'retrospective-fixed-cdf-decisions', 'independent_validation': False,
        'kappa': 10, 'new_hyperparameter_searches': 0, 'temporal_refits': 4,
        'destination_labels_invariant': True, 'regional_equality_is_constructed': True,
        'nested': report(nested, enabled),
        'temporal': {k: report(g, enabled) for k,g in blocked.groupby('case')},
        'later': {k: report(g, enabled) for k,g in later.groupby('block')},
        'contrasts': [paired_bootstrap(nested, m, 'M1_B') for m in NEW]}
    (OUT/'summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    manifest = {'source_head': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        'protected_sha256': before, 'protocol_sha256': sha(PROTOCOL),
        'code_sha256': {name: sha(ROOT/'pipeline'/name) for name in ['coherent_experiment.py', 'coherent_allocation.py', 'hurdle_model.py', 'hurdle_experiment.py']},
        'frozen_model_signature': fingerprint,
        'output_sha256': {p.name: sha(p) for p in OUT.glob('*') if p.name != 'manifest.json'}}
    (OUT/'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False)+'\n')
    print('Coherent decision experiment complete:', OUT, flush=True)
    return summary


if __name__ == '__main__':
    run()
