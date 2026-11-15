"""Conditional temporal-margin requirements from existing JSON summaries only.

Assumed reference-to-exposure margins are not calibrated physical error bounds.
No raw readers, new matching, fire classes, fitting, or decisions are used.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import math
from numbers import Real
from pathlib import Path
from observation_qa import temporal_relation

WINDOWS = (300, 600, 900)
EQUAL_MARGINS = (0, 1, 2, 5, 10, 30, 60, 120, 180, 300)
SOURCES = {
    '2019': 'docs/reviews/evidence/observation-geotiming/summary.json',
    '2023': 'docs/reviews/evidence/observation-case2023/result.json',
}
PROTOCOL = 'docs/reviews/2026-11-15-scan-reference-margin-protocol.md'
OUTPUT = 'docs/reviews/evidence/scan-reference-margins'


def nonnegative(value, name):
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value) or value < 0:
        raise ValueError(f'{name} must be finite and nonnegative')


def conditional_relation(delta_min, delta_max, window, margin_a=None, margin_v=None):
    """Bounds for already associated reference differences under explicit margins.

    Unknown physical margins produce no metric interval, including when one
    instrument's margin happens to be supplied. No missing margin becomes zero.
    """
    for name, value in [('delta_min', delta_min), ('delta_max', delta_max), ('window', window)]:
        nonnegative(value, name)
    if delta_min > delta_max:
        raise ValueError('delta_min must not exceed delta_max')
    for name, value in [('margin_a', margin_a), ('margin_v', margin_v)]:
        if value is not None:
            nonnegative(value, name)
    if margin_a is None or margin_v is None:
        return {'status': 'not_identified', 'metrics': None,
                'reason': 'reference_to_exposure_margin_unbounded_or_unknown'}
    budget = margin_a + margin_v
    lower, upper = max(0, delta_min - budget), delta_max + budget
    if not math.isfinite(budget) or not math.isfinite(upper):
        raise ValueError('conditional arithmetic overflow')
    state = ('forall_within' if upper <= window else
             'forall_outside' if lower > window else 'no_uniform_resolution')
    return {'status': 'conditional_on_assumed_margins',
            'metrics': {'lower_seconds': lower, 'upper_seconds': upper,
                        'margin_sum_seconds': budget, 'state': state}}


def tipping_requirements(delta_min, delta_max, window):
    conditional_relation(delta_min, delta_max, window)
    slack = window - delta_max
    outside = (delta_min - window) / 2 if delta_min > window else None
    return {'slack_within_seconds': slack,
            'within_m_equal_max_seconds': slack / 2 if slack >= 0 else None,
            'within_condition': 'm <= maximum (closed)' if slack >= 0 else None,
            'outside_m_equal_boundary_seconds': outside,
            'outside_condition': 'm < boundary (open)' if outside is not None else None}


def extract_sources(documents):
    """Read only declared summaries, with counts, time-scale and shape checks."""
    records = []
    for case in ('2019', '2023'):
        doc = documents[case]
        if doc['gate1_passed'] is not False or doc['pixel_exposure_times_verified'] is not False:
            raise ValueError('source gate/exposure state differs from frozen scope')
        if case == '2019':
            offsets = doc['scan_reference_offsets']
            count = doc['association_counts']['matched_Aqua_seeds']
            unknown = doc['association_counts']['associations_time_unknown']
        else:
            geo = doc['inspection']['geotiming']
            offsets = geo['reference_offsets']
            count = geo['matched_Aqua_seeds']
            unknown = geo['associations_unknown_reference_time']
        if type(count) is not int or count <= 0 or unknown != 0:
            raise ValueError('expected positive existing association count with known references')
        if set(offsets) != {'center_reference', 'start_reference'}:
            raise ValueError('unexpected reference definitions')
        for reference in sorted(offsets):
            entry = offsets[reference]
            if 'TAI93' not in entry['definition']:
                raise ValueError('same native TAI93 time scale required')
            absolute = entry['absolute_seconds']
            if absolute['count'] != count:
                raise ValueError('absolute-reference count mismatch')
            quantiles = absolute['quantiles']
            if set(quantiles) != {'0', '0.25', '0.5', '0.75', '1'}:
                raise ValueError('unexpected quantile summary shape')
            values = [quantiles[k] for k in ('0', '0.25', '0.5', '0.75', '1')]
            for value in values:
                nonnegative(value, 'absolute_reference_seconds')
            if values != sorted(values):
                raise ValueError('unordered absolute-reference quantiles')
            records.append({'case': case, 'reference': reference,
                            'existing_association_count': count,
                            'min_abs_reference_seconds': values[0],
                            'max_abs_reference_seconds': values[-1],
                            'units': 'native_TAI93_seconds',
                            'source': SOURCES[case], 'definition': entry['definition']})
    return records


def validate_edges():
    """Synthetic boundaries checked against the existing interval operator."""
    assert temporal_relation((0, 0), (300, 300), 300)['state'] == 'within'
    assert temporal_relation((0, 0), (301, 301), 300)['state'] == 'outside'
    for delta, margin, window in [(298, 1, 300), (302, 1, 300),
                                   (302, 0.5, 300), (0, 0, 0), (300, 1, 300)]:
        expected = temporal_relation((-margin, margin),
                                     (delta - margin, delta + margin), window)
        got = conditional_relation(delta, delta, window, margin, margin)['metrics']
        assert got['lower_seconds'] == expected['minimum_gap_seconds']
        assert got['upper_seconds'] == expected['maximum_gap_seconds']
        mapping = {'within': 'forall_within', 'outside': 'forall_outside',
                   'time_uncertain': 'no_uniform_resolution'}
        assert got['state'] == mapping[expected['state']]
    assert conditional_relation(0, 0, 300)['metrics'] is None
    assert conditional_relation(0, 0, 300, 0, None)['metrics'] is None
    assert tipping_requirements(302, 302, 300)['outside_m_equal_boundary_seconds'] == 1
    assert conditional_relation(302, 302, 300, 1, 1)['metrics']['state'] == 'no_uniform_resolution'
    assert tipping_requirements(298, 298, 300)['within_m_equal_max_seconds'] == 1
    assert conditional_relation(298, 298, 300, 1, 1)['metrics']['state'] == 'forall_within'
    for args in [(-1, 2, 300, 0, 0), (2, 1, 300, 0, 0), (0, math.inf, 300, 0, 0),
                 (0, 1, 300, -1, 0), (0, 1, True, 0, 0), (0, 1, 300, math.nan, None)]:
        try:
            conditional_relation(*args)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid conditional input accepted')


def build_report(documents):
    validate_edges()
    records = extract_sources(documents)
    rows, tipping = [], []
    for record in records:
        low, high = record['min_abs_reference_seconds'], record['max_abs_reference_seconds']
        for window in WINDOWS:
            tipping.append({**record, 'window_seconds': window,
                            **tipping_requirements(low, high, window)})
            previous = None
            for margin in EQUAL_MARGINS:
                metrics = conditional_relation(low, high, window, margin, margin)['metrics']
                if previous:
                    assert metrics['lower_seconds'] <= previous['lower_seconds']
                    assert metrics['upper_seconds'] >= previous['upper_seconds']
                    assert not (previous['state'] == 'no_uniform_resolution' and
                                metrics['state'] != 'no_uniform_resolution')
                previous = metrics
                rows.append({**record, 'window_seconds': window,
                             'assumed_margin_a_seconds': margin, 'assumed_margin_v_seconds': margin,
                             **metrics})
    assert len(rows) == 120 and len(tipping) == 12
    return {'scope': 'conditional_requirements_for_existing_center_associations_only',
            'physical_margins': {'status': 'not_identified', 'metrics': None},
            'physical_exposure_verified': False, 'gate1_passed': False,
            'margin_interpretation': 'assumed_not_calibrated_not_confidence_intervals',
            'rows': rows, 'tipping_requirements': tipping,
            'verification': {'synthetic_edges': 'passed', 'monotonicity': 'passed',
                             'source_shapes': 'passed', 'unknown_is_not_zero': 'passed'}}


def csv_text(rows):
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def main():
    root = Path(__file__).resolve().parents[1]
    documents = {case: json.loads((root / path).read_text()) for case, path in SOURCES.items()}
    report = build_report(documents)
    out = root / OUTPUT
    if out.exists():
        raise FileExistsError('refusing to overwrite existing evidence')
    payloads = {
        'result.json': json.dumps(report, indent=2, sort_keys=True) + '\n',
        'conditional-margins.csv': csv_text(report['rows']),
        'tipping-requirements.csv': csv_text(report['tipping_requirements']),
        'code-snapshot.py.txt': Path(__file__).read_text(),
        'helper-observation_qa.py.txt': (root / 'pipeline/observation_qa.py').read_text(),
        'protocol-snapshot.md.txt': (root / PROTOCOL).read_text(),
    }
    sources = list(SOURCES.values()) + [PROTOCOL, 'pipeline/scan_reference_margins.py',
                                       'pipeline/observation_qa.py']
    manifest = {'scope': report['scope'], 'source_sha256': {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in sources},
        'artifacts_sha256': {name: hashlib.sha256(body.encode()).hexdigest()
                             for name, body in payloads.items()},
        'inputs_are_existing_json_only': True, 'raw_opened': False,
        'gate1_passed': False, 'physical_exposure_verified': False,
        'reproduction': 'python3 pipeline/scan_reference_margins.py (new evidence directory only)'}
    out.mkdir(parents=True)
    for name, body in payloads.items():
        (out / name).write_bytes(body.encode())
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'rows': len(report['rows']), 'tipping_rows': len(report['tipping_requirements']),
                      'verification': report['verification'], 'output': OUTPUT}))


if __name__ == '__main__':
    main()
