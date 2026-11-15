"""Protocol20: fail-closed observed/research contract audit, never fit models."""
import csv
import hashlib
import json
import math
import platform
import subprocess
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from scientific_audit import ROOT, DATA, sha
from frozen_temporal_audit import KEYS, publication_metadata
from publish_observed import grid as observed_grid
from robust_affine_experiment import check_deadline

OUT = DATA/'contract_gap_audit'
BASE = ROOT/'observed/dist'
SOURCE = DATA/'platform_target_audit/paired_predictions.parquet'
PROTOCOL = ROOT/'docs/reviews/2026-11-14-science-protocol-20.md'
VARIANTS = ('O0', 'Ogrid', 'Omask', 'Omap', 'Cmaskedtype0', 'Cmaskedall')


def research_grid(lon, lat):
    return math.floor(lon/.01), math.floor(lat/.01)


def validate_csv(payload, segment, commune, source):
    if hashlib.sha256(payload).hexdigest() != segment['sha256'] or len(payload) != segment['bytes']:
        raise ValueError('Observed CSV hash/size mismatch')
    rows = list(csv.DictReader(payload.decode().splitlines()))
    if len(rows) != segment['rows']:
        raise ValueError('Observed CSV row count mismatch')
    files = {f['filename'] for f in source['files']}
    for row in rows:
        acquired = date.fromisoformat(row['acq_date'])
        if (row['cut_com'] != commune['cut'] or row['comuna'] != commune['name'] or
            row['daynight'] != 'D' or row['type'] != '0' or row['instrument'] != 'VIIRS' or
            row['satellite'] != 'N20' or row['confidence'].lower() not in ('n','h') or
            row['source_file'] not in files or acquired.year not in source['available_years']):
            raise ValueError('Observed CSV identity/filter provenance mismatch')
        if observed_grid(float(row['longitude']),float(row['latitude'])) != (int(row['grid_x']),int(row['grid_y'])):
            raise ValueError('Observed grid did not reproduce')
    return rows


def verify_series(rows, series):
    detections = Counter(r['acq_date'][:7] for r in rows)
    cells = defaultdict(set)
    for r in rows:
        cells[r['acq_date'][:7]].add((r['acq_date'],int(r['grid_x']),int(r['grid_y'])))
    if len({r['month'] for r in series}) != len(series):
        raise ValueError('Duplicate observed series month')
    for row in series:
        if row['cell_days'] is None or row['detections'] is None:
            if detections[row['month']]:
                raise ValueError('Observed missing-file month has CSV records')
        elif row['cell_days'] != len(cells[row['month']]) or row['detections'] != detections[row['month']]:
            raise ValueError('Observed CSV/series do not reproduce exactly')
    if set(detections)-{r['month'] for r in series}:
        raise ValueError('CSV dates outside observed series')


def attach_observed_support(panel, series):
    """Missing published/source months stay unknown; never fill them with zero."""
    x = panel[KEYS].copy()
    x['month'] = [f'{int(s if m>=7 else s+1):04d}-{int(m):02d}' for s,m in x[['season','m']].to_numpy()]
    if series.duplicated(['cut','month']).any():
        raise ValueError('Duplicate observed support keys')
    x = x.merge(series, on=['cut','month'], how='left', validate='one_to_one')
    x['available'] = x.O0.notna()
    return x


def observed_variants(rows, mapping, mask):
    """Fixed sequential mechanical transformations; unavailable map is explicit."""
    sets = {v:set() for v in ('O0','Ogrid','Omask','Omap')}
    diagnostic = Counter()
    for r in rows:
        acquired = date.fromisoformat(r['acq_date']);m=acquired.month
        season=acquired.year if m>=7 else acquired.year-1
        cut=r['cut_com'];day=r['acq_date']
        ox,oy=int(r['grid_x'])-18000,int(r['grid_y'])-9000
        cx,cy=research_grid(float(r['longitude']),float(r['latitude']))
        diagnostic['detection_rows'] += 1
        if (ox,oy)!=(cx,cy):diagnostic['grid_disagreement_rows'] += 1
        if abs(float(r['longitude'])/.01-round(float(r['longitude'])/.01))<1e-8 or abs(float(r['latitude'])/.01-round(float(r['latitude'])/.01))<1e-8:
            diagnostic['near_literal_grid_border_rows'] += 1
        sets['O0'].add((cut,season,m,day,ox,oy))
        sets['Ogrid'].add((cut,season,m,day,cx,cy))
        if (cx,cy) in mask:continue
        sets['Omask'].add((cut,season,m,day,cx,cy))
        mapped=mapping.get((cx,cy))
        if mapped is None:
            diagnostic['mapping_unavailable_detection_rows'] += 1
            continue
        if mapped!=cut:diagnostic['moved_cut_detection_rows'] += 1
        sets['Omap'].add((mapped,season,m,day,cx,cy))
    return sets,dict(diagnostic)


def type_cell_days(detections):
    """Type0 is selected BEFORE cell-day dedup; mixed days counted only once."""
    keys=['cut','cell_x','cell_y','acq_date']
    all_days=detections[keys].drop_duplicates()
    zero=detections[detections.type.eq(0)][keys].drop_duplicates()
    flags=detections.assign(type0=detections.type.eq(0), other=detections.type.notna()&~detections.type.eq(0), unknown=detections.type.isna())
    mix=flags.groupby(keys,dropna=False)[['type0','other','unknown']].any().reset_index()
    return all_days,zero,mix


def close_deltas(frame):
    x=frame.copy()
    for left,right,name in [('Ogrid','O0','delta_grid'),('Omask','Ogrid','delta_mask'),('Omap','Omask','delta_map_support'),('Cmaskedtype0','Omap','residual_cohort'),('Cmaskedall','Cmaskedtype0','delta_type_within_C')]:
        x[name]=x[left]-x[right]
    x['gap']=x.Cmaskedall-x.O0
    x['closure_error']=x.gap-x[['delta_grid','delta_mask','delta_map_support','residual_cohort','delta_type_within_C']].sum(axis=1)
    if not x.closure_error.eq(0).all():raise ValueError('Algebraic closure failed')
    return x


def run():
    check_deadline()
    protected=[p for p in DATA.rglob('*') if p.is_file() and OUT not in p.parents]
    protected += [p for p in BASE.rglob('*') if p.is_file()]
    protected += list((ROOT/'web/public/data').rglob('*.json'))
    geometry=ROOT/'observed/data/processed/communes-full.geojson';protected.append(geometry)
    before={str(p.relative_to(ROOT)):sha(p) for p in protected}
    summary={'status':'pending-gates','fits':0,'new_downloads':0,'model_scoring':False,
             'independent_validation':False,'observation_coverage':'unknown',
             'causal_attribution':False,'observed_assignment':'cell-centre',
             'research_assignment':'cell-centre; different frozen legacy geography', 'gates':{}}
    artifacts={}
    try:
        prior=json.loads((DATA/'platform_target_audit/manifest.json').read_text())
        if sha(SOURCE)!=prior['output_sha256'][SOURCE.name]:raise ValueError('Source19 panel hash mismatch')
        panel=pd.read_parquet(SOURCE)
        if len(panel)!=3780 or panel.duplicated(KEYS).any():raise ValueError('Source19 domain changed')
        for name in ('detections.parquet','celldays.parquet','cells_comuna.parquet','static_mask.parquet'):
            p=DATA/name
            if sha(p)!=prior['protected_sha256'][str(p.relative_to(ROOT))]:raise ValueError('Source19 input hash changed: '+name)
        manifest=json.loads((BASE/'data/history-manifest.json').read_text())
        if sha(geometry)!=manifest['geography']['geometry_sha256']:raise ValueError('DPA geometry hash mismatch')
        if manifest['grid']['assignment']!='cell-centre':raise ValueError('Observed geography assignment changed')
        index=json.loads((BASE/'data/publication/index.json').read_text())
        if index['source_manifest_sha256']!=sha(BASE/'data/history-manifest.json'):raise ValueError('Observed publication manifest mismatch')
        source=next(s for s in manifest['sources'] if s['id']=='noaa20-history')
        if set(c['cut'] for c in manifest['communes'])!=set(panel.cut):raise ValueError('Observed commune domain mismatch')
        monthly=json.loads((BASE/'data/observed-monthly.json').read_text())
        rows=[];support=[]
        for commune in manifest['communes']:
            cut=commune['cut'];segment=next(s for s in source['communes'] if s['cut']==cut)
            selected=validate_csv((BASE/segment['url']).read_bytes(),segment,commune,source)
            expected=next(c for c in index['communes'] if c['cut']==cut)
            publication=BASE/'data/publication'/f'{cut}.json'
            if sha(publication)!=expected['sha256']:raise ValueError('Published commune hash mismatch')
            doc=json.loads(publication.read_text());published=next(s for s in doc['sources'] if s['id']==source['id'])
            series=[r for r in monthly if r['source_id']==source['id'] and r['cut']==cut]
            verify_series(selected,series);verify_series(selected,published['series'])
            if {r['month'] for r in series}!={r['month'] for r in published['series']}:raise ValueError('Published/source month domain differs')
            support += [dict(cut=cut,month=r['month'],O0=r['cell_days']) for r in series]
            rows += selected
        summary['gates']['observed_csv_hash_filters_series_exact']=True
        con=duckdb.connect()
        con.execute(f"create view mapped as select d.*,c.cut from read_parquet('{DATA}/detections.parquet') d join read_parquet('{DATA}/cells_comuna.parquet') c using(cell_x,cell_y) where sat='NOAA20' and not exists(select 1 from read_parquet('{DATA}/static_mask.parquet') z where z.cell_x=d.cell_x and z.cell_y=d.cell_y)")
        reconstructed=con.execute("""select cut,case when month(acq_date)>=7 then year(acq_date) else year(acq_date)-1 end season,month(acq_date) m,
          count(distinct (cell_x,cell_y,acq_date)) Cmaskedall from mapped group by 1,2,3""").df()
        check=panel[KEYS+['noaa20']].merge(reconstructed,on=KEYS,how='left',validate='one_to_one').fillna({'Cmaskedall':0})
        if not np.array_equal(check.noaa20.to_numpy(),check.Cmaskedall.to_numpy()):raise ValueError('Research detections did not reproduce source19 Cmaskedall exactly')
        summary['gates']['research_Cmaskedall_reproduces19_exact']=True
        aligned=attach_observed_support(panel,pd.DataFrame(support))
        artifacts['observed_domain.csv']=aligned
        missing=aligned[~aligned.available]
        summary['gates']['observed_available_on_all3780_rows']=missing.empty
        summary['observed_source_end']=source['end']
        summary['domain_rows']=len(panel)
        summary['unavailable_rows']=len(missing)
        summary['unavailable_calendar_months']=sorted(missing.month.unique().tolist())
        if not missing.empty:
            summary['status']='blocked-contract-domain-incompatibility'
            summary['reason']='Fixed19 panel includes months absent from observed source/publication; no zero fill, domain reduction, transformation quantities, or causal decomposition were performed.'
        else:
            raise ValueError('Full common support unexpectedly available; stop before implementing unreviewed production transformation path')
    except (ValueError,KeyError,StopIteration,FileNotFoundError) as exc:
        summary['status']='blocked-reproduction-gate'
        summary['reason']=str(exc)
        summary['gates']['all_required_reproductions']=False
    if before!={str(p.relative_to(ROOT)):sha(p) for p in protected}:raise ValueError('Protected sources changed')
    OUT.mkdir(parents=True,exist_ok=True)
    for name,frame in artifacts.items():frame.to_csv(OUT/name,index=False)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    code=[Path(__file__),ROOT/'pipeline/publish_observed.py',ROOT/'pipeline/build_detections.py',ROOT/'pipeline/build_monthly.py']
    out_manifest={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  'protocol_sha256':sha(PROTOCOL),'code_sha256':{str(p.relative_to(ROOT)):sha(p) for p in code},
                  'environment':{'python':platform.python_version(),'pandas':pd.__version__,'duckdb':duckdb.__version__},
                  'protected_sha256':before,'all_previous_artifacts_unchanged':True,
                  'output_sha256':{p.name:sha(p) for p in OUT.glob('*') if p.name!='manifest.json'}}
    (OUT/'manifest.json').write_text(json.dumps(out_manifest,indent=2,allow_nan=False)+'\n')
    print(json.dumps(summary,indent=2),flush=True)
    return summary


if __name__=='__main__':run()
