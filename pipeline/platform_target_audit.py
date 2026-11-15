"""Protocol 19: frozen predictions, external-platform discrepancy, no fitting."""
import calendar
import hashlib
import json
import platform
import subprocess
from datetime import date, timedelta
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from scientific_audit import ROOT, DATA, TRAIN, AuditData, sha
from platform_bridge_audit import requested_days
from frozen_temporal_audit import KEYS, publication_metadata
from coherent_experiment import METHODS
from robust_affine_experiment import check_deadline

OUT = DATA / 'platform_target_audit'
SOURCE = DATA / 'coherent_audit/later_predictions.parquet'
PROTOCOL = ROOT / 'docs/reviews/2026-11-14-science-protocol-19.md'


def month_requests(frame, coverage):
    """Inventory documents requests, never actual useful observing opportunity."""
    records = []
    for season, month in sorted(set(map(tuple, frame[['season', 'm']].to_numpy()))):
        year = int(season if month >= 7 else season+1)
        first = date(year, int(month), 1)
        expected = {first+timedelta(days=i) for i in range(calendar.monthrange(year, int(month))[1])}
        row = {'season': int(season), 'm': int(month), 'y': year,
               'expected_requested_days': len(expected)}
        for sat in ('SNPP', 'NOAA20'):
            row[sat+'_missing_requested_days'] = len(expected-coverage[sat])
        row['complete_both_requested'] = all(row[s+'_missing_requested_days'] == 0 for s in ('SNPP', 'NOAA20'))
        records.append(row)
    return pd.DataFrame(records)


def attach_targets(predictions, monthly, requests):
    """Zero-fill detection counts only after an explicitly complete requested month."""
    if predictions.duplicated(KEYS).any():
        raise ValueError('Duplicate source prediction keys')
    if requests.duplicated(['season', 'm']).any():
        raise ValueError('Duplicate requested-month keys')
    if monthly.duplicated([*KEYS, 'sat']).any():
        raise ValueError('Duplicate platform aggregate keys')
    status = predictions.merge(requests[['season', 'm', 'complete_both_requested']],
                               on=['season', 'm'], how='left', validate='many_to_one')
    if status.complete_both_requested.isna().any():
        raise ValueError('Missing requested-month provenance')
    x = status[status.complete_both_requested].drop(columns='complete_both_requested').copy()
    for sat, target in [('SNPP', 'snpp_reproduced'), ('NOAA20', 'noaa20')]:
        selected = monthly[monthly.sat == sat][[*KEYS, 'cell_days', 'provisional']]
        selected = selected.rename(columns={'cell_days': target, 'provisional': target+'_nrt'})
        x = x.merge(selected, on=KEYS, how='left', validate='one_to_one')
        x[target] = x[target].fillna(0).astype('int64')
        x[target+'_nrt'] = x[target+'_nrt'].fillna(False).astype(bool)
    if not np.array_equal(x.snpp.to_numpy(), x.snpp_reproduced.to_numpy()):
        bad = x.loc[x.snpp != x.snpp_reproduced, [*KEYS, 'snpp', 'snpp_reproduced']]
        raise ValueError('S-NPP target did not reproduce exactly: '+bad.head().to_json(orient='records'))
    if x[KEYS].duplicated().any() or len(x) != len(predictions.merge(requests[requests.complete_both_requested][['season', 'm']], on=['season', 'm'])):
        raise ValueError('Target key alignment changed')
    for method in METHODS:
        source = predictions.set_index(KEYS).loc[pd.MultiIndex.from_frame(x[KEYS]), method].to_numpy()
        if not np.array_equal(source, x[method].to_numpy()):
            raise ValueError('Frozen predictions changed during target attachment')
    return x.sort_values(KEYS).reset_index(drop=True)


def metrics(frame, target):
    result = {'n': len(frame), 'target_sum': int(frame[target].sum()), 'methods': {}}
    for method in METHODS:
        error = frame[method]-frame[target]
        totals = frame.groupby(['season', 'm'])[[method, target]].sum()
        result['methods'][method] = {
            'mae': float(error.abs().mean()) if len(frame) else None,
            'mse': float((error**2).mean()) if len(frame) else None,
            'bias': float(error.mean()) if len(frame) else None,
            'prediction_sum': float(frame[method].sum()),
            'regional_monthly_mae': float((totals[method]-totals[target]).abs().mean()) if len(totals) else None}
    result['ranking_by_mae'] = sorted(METHODS, key=lambda m: (result['methods'][m]['mae'], m)) if len(frame) else []
    return result


def make_reports(frame, enabled):
    reports = {}; flat = []
    for target in ('snpp', 'noaa20'):
        reports[target] = {}
        periods = {'all_later': frame}
        periods.update({str(k): g for k, g in frame.groupby('block')})
        periods.update({str(k): g for k, g in frame.groupby('orbit_epoch')})
        nrt_col = 'snpp_reproduced_nrt' if target == 'snpp' else 'noaa20_nrt'
        periods.update({'with_positive_NRT': frame[frame[nrt_col]], 'without_positive_NRT': frame[~frame[nrt_col]]})
        for period, f in periods.items():
            reports[target][period] = {}
            for group, x in [('all54', f), ('published14', f[f.cut.isin(enabled)]), ('remaining40', f[~f.cut.isin(enabled)])]:
                strata = {'all_months': x, 'positive_reference': x[x[target]>0],
                          'zero_reference': x[x[target]==0],
                          'aqua_zero_reference_positive': x[(x.aqua==0)&(x[target]>0)],
                          'both_observed_zero': x[(x.aqua==0)&(x[target]==0)],
                          'reference_50_plus': x[x[target]>=50]}
                reports[target][period][group] = {}
                for population, y in strata.items():
                    value = metrics(y, target)
                    reports[target][period][group][population] = value
                    for method, scores in value['methods'].items():
                        flat.append(dict(reference=target, period=period, group=group, population=population,
                                         method=method, n=len(y), target_sum=value['target_sum'], **scores))
    return reports, pd.DataFrame(flat)


def mask_signature(mask):
    return hashlib.sha256(json.dumps(sorted(mask), separators=(',', ':')).encode()).hexdigest()


def run():
    check_deadline()
    protected = [p for p in DATA.rglob('*') if p.is_file() and OUT not in p.parents]
    protected += list((ROOT/'web/public/data').rglob('*.json'))
    before = {str(p.relative_to(ROOT)): sha(p) for p in protected}
    source_manifest = json.loads((DATA/'coherent_audit/manifest.json').read_text())
    if sha(SOURCE) != source_manifest['output_sha256'][SOURCE.name]:
        raise ValueError('Source18 later-prediction hash mismatch')
    bridge_manifest = json.loads((DATA/'platform_bridge_audit/manifest.json').read_text())
    for name in ('celldays.parquet', 'static_mask.parquet', 'inventory.csv'):
        key = str((DATA/name).relative_to(ROOT))
        current = sha(DATA/name)
        if current != source_manifest['protected_sha256'][key]:
            raise ValueError('Source18 input hash changed: '+name)
        if current != bridge_manifest['input_sha256'][key]:
            raise ValueError('Source7 input hash changed: '+name)
    predictions = pd.read_parquet(SOURCE)
    if len(predictions) != 3780 or predictions.cut.nunique() != 54:
        raise ValueError('Source18 later keys changed')
    data = AuditData()
    frozen_mask = data.fit_mask(TRAIN)  # identity verification only; no new mask choice
    if len(frozen_mask) != 223 or frozen_mask != data.published_mask:
        raise ValueError('Full TRAIN mask differs from published223 mask')
    enabled, _ = publication_metadata(data.cuts)
    paths = pd.read_csv(DATA/'inventory.csv').path.tolist()
    coverage = {sat: requested_days(paths, sat) for sat in ('SNPP', 'NOAA20')}
    requests = month_requests(predictions, coverage)
    data.con.register('audit19_mask', pd.DataFrame(sorted(frozen_mask), columns=['cell_x', 'cell_y']))
    monthly = data.con.execute("""select cut,season,m,sat,count(*) cell_days,bool_or(any_nrt) provisional
      from days d where sat in ('SNPP','NOAA20') and season between 2020 and 2025
      and not exists(select 1 from audit19_mask z where z.cell_x=d.cell_x and z.cell_y=d.cell_y)
      group by 1,2,3,4""").df()
    paired = attach_targets(predictions, monthly, requests)  # abort before any scoring if mismatch
    if paired.empty:
        raise ValueError('No identical requested-complete rows')
    for _, group in paired.groupby(['season', 'm']):
        if set(group.cut) != set(data.cuts):
            raise ValueError('Incomplete54-commune month')
    report, flat = make_reports(paired, enabled)
    summary = {'status': 'external-platform-reference-sensitivity', 'independent_validation': False,
               'fits': 0, 'new_downloads': 0, 'hyperparameter_searches': 0,
               'reference_truth_claim': False, 'observation_coverage': 'unknown',
               'exact_publication_observed_contract': False,
               'publication_contract_caveat': 'Research celldays use the fixed223 mask and cell-centroid geography; published observed also filters type0 and uses its own geography. This is platform sensitivity, not reproduction of published observed values.',
               'requested_completeness_is_observation_coverage': False,
               'source_rows': len(predictions), 'paired_rows': len(paired),
               'excluded_requested_months': requests.loc[~requests.complete_both_requested].to_dict('records'),
               'snpp_reproduces_source18_exactly': True, 'same_rows_for_both_references': True,
               'mask_cells': len(frozen_mask), 'mask_coordinate_sha256': mask_signature(frozen_mask),
               'regional_and_global_bias_equality_to_B_is_constructed': True,
               'positive_NRT_month_rows': {sat: int(paired[col].sum()) for sat, col in [('snpp','snpp_reproduced_nrt'), ('noaa20','noaa20_nrt')]},
               'NRT_caveat': 'Flags describe detected cell-days only; absent detections do not establish observation provenance or useful coverage.',
               'reports': report}
    after = {str(p.relative_to(ROOT)): sha(p) for p in protected}
    if before != after:
        raise ValueError('Protected sources changed')
    OUT.mkdir(parents=True, exist_ok=True)
    paired.to_parquet(OUT/'paired_predictions.parquet', index=False)
    requests.to_csv(OUT/'requested_months.csv', index=False)
    flat.to_csv(OUT/'metrics.csv', index=False)
    (OUT/'summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    code = [Path(__file__), ROOT/'pipeline/platform_bridge_audit.py', ROOT/'pipeline/scientific_audit.py',
            ROOT/'pipeline/coherent_experiment.py', ROOT/'pipeline/frozen_temporal_audit.py']
    manifest = {'source_head': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
                'protocol_sha256': sha(PROTOCOL), 'code_sha256': {str(p.relative_to(ROOT)): sha(p) for p in code},
                'environment': {'python': platform.python_version(), 'pandas': pd.__version__, 'numpy': np.__version__, 'duckdb': duckdb.__version__},
                'protected_sha256': before, 'all_previous_artifacts_unchanged': True,
                'output_sha256': {p.name: sha(p) for p in OUT.glob('*') if p.name != 'manifest.json'}}
    (OUT/'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False)+'\n')
    print('Platform target audit complete:', len(paired), 'rows; exact SNP reproduction', flush=True)
    return summary


if __name__ == '__main__':
    run()
