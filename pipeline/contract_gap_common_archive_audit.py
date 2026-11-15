"""Protocol20A: metadata-defined common archive; mechanical contract differences."""
import json
import platform
import subprocess
from collections import Counter
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from scientific_audit import ROOT, DATA, sha
from frozen_temporal_audit import KEYS, publication_metadata
from robust_affine_experiment import check_deadline
from contract_gap_audit import (BASE, SOURCE, VARIANTS, validate_csv, verify_series,
                               observed_variants, close_deltas, research_grid)

OUT=DATA/'contract_gap_common_archive_audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-14-science-protocol-20a.md'


def common_archive(panel, source):
    x=panel.copy()
    x['month']=[f'{int(s if m>=7 else s+1):04d}-{int(m):02d}' for s,m in x[['season','m']].to_numpy()]
    x['archive_available']=(x.month>=source['start'])&(x.month<=source['end'])&x.month.str[:4].astype(int).isin(source['available_years'])
    return x[x.archive_available].drop(columns='archive_available'),x[~x.archive_available].drop(columns='archive_available')


def aggregate_sets(sets, panel):
    out=panel[KEYS].copy()
    for variant, records in sets.items():
        counts=Counter(r[:3] for r in records)
        out[variant]=[counts[tuple(r)] for r in out[KEYS].itertuples(index=False,name=None)]
    return out


def contrasts(frame, enabled):
    reports={};flat=[]
    periods={'all_common_archive':frame}
    periods.update({str(k):g for k,g in frame.groupby('block')})
    periods.update({str(k):g for k,g in frame.groupby('orbit_epoch')})
    changes=[('O0','Ogrid','grid'),('Ogrid','Omask','mask'),('Omask','Omap','mapping_and_support'),
             ('Omap','Cmaskedtype0','residual_cohort'),('Cmaskedtype0','Cmaskedall','type_within_C'),('O0','Cmaskedall','total_gap')]
    for period,f in periods.items():
        reports[period]={}
        for name,x in [('all54',f),('published14',f[f.cut.isin(enabled)]),('remaining40',f[~f.cut.isin(enabled)])]:
            value={'n':len(x),'sums':{v:int(x[v].sum()) for v in VARIANTS},'contrasts':{}}
            for left,right,label in changes:
                d=x[right]-x[left]
                item={'signed_sum':int(d.sum()),'absolute_difference_sum':int(d.abs().sum()),
                      'identical_commune_months':int(d.eq(0).sum()),'maximum_absolute_difference':int(d.abs().max()) if len(d) else None}
                value['contrasts'][label]=item
                flat.append(dict(period=period,group=name,n=len(x),contrast=label,**item))
            reports[period][name]=value
    return reports,pd.DataFrame(flat)


def run():
    check_deadline()
    protected=[p for p in DATA.rglob('*') if p.is_file() and OUT not in p.parents]
    protected += [p for p in BASE.rglob('*') if p.is_file()]
    protected += list((ROOT/'web/public/data').rglob('*.json'))
    geometry=ROOT/'observed/data/processed/communes-full.geojson';protected.append(geometry)
    before={str(p.relative_to(ROOT)):sha(p) for p in protected}
    strict_manifest=json.loads((DATA/'contract_gap_audit/manifest.json').read_text())
    for key, expected in strict_manifest['protected_sha256'].items():
        if sha(ROOT/key)!=expected:raise ValueError('Strict20 protected source changed: '+key)
    strict=json.loads((DATA/'contract_gap_audit/summary.json').read_text())
    if strict['status']!='blocked-contract-domain-incompatibility' or not strict['gates']['observed_csv_hash_filters_series_exact'] or not strict['gates']['research_Cmaskedall_reproduces19_exact']:
        raise ValueError('Strict20 prerequisite gates not established')
    manifest=json.loads((BASE/'data/history-manifest.json').read_text())
    if sha(geometry)!=manifest['geography']['geometry_sha256']:raise ValueError('Observed geometry hash mismatch')
    source=next(s for s in manifest['sources'] if s['id']=='noaa20-history')
    prior=json.loads((DATA/'platform_target_audit/manifest.json').read_text())
    if sha(SOURCE)!=prior['output_sha256'][SOURCE.name]:raise ValueError('Source19 hash changed')
    for name in ('detections.parquet','celldays.parquet','cells_comuna.parquet','static_mask.parquet'):
        p=DATA/name
        if sha(p)!=prior['protected_sha256'][str(p.relative_to(ROOT))]:raise ValueError('Source19 inputs changed')
    original=pd.read_parquet(SOURCE)
    panel,excluded=common_archive(original,source)
    if len(panel)!=3456 or len(excluded)!=324 or panel.month.nunique()!=64:raise ValueError('Common archive metadata domain differs from frozen20A')
    index=json.loads((BASE/'data/publication/index.json').read_text())
    monthly=json.loads((BASE/'data/observed-monthly.json').read_text())
    rows=[];published_counts={}
    for commune in manifest['communes']:
        cut=commune['cut'];segment=next(s for s in source['communes'] if s['cut']==cut)
        selected=validate_csv((BASE/segment['url']).read_bytes(),segment,commune,source)
        expected=next(c for c in index['communes'] if c['cut']==cut)
        publication=BASE/'data/publication'/f'{cut}.json'
        if sha(publication)!=expected['sha256']:raise ValueError('Publication hash mismatch')
        pub=next(s for s in json.loads(publication.read_text())['sources'] if s['id']==source['id'])
        series=[r for r in monthly if r['source_id']==source['id'] and r['cut']==cut]
        verify_series(selected,series);verify_series(selected,pub['series'])
        for r in pub['series']:
            if r['cell_days'] is not None:published_counts[(cut,r['month'])]=r['cell_days']
        rows += [r for r in selected if r['acq_date'][:7] in set(panel.month)]
    mapping_frame=pd.read_parquet(DATA/'cells_comuna.parquet')
    if mapping_frame.duplicated(['cell_x','cell_y']).any():raise ValueError('Scientific map is not unique')
    mapping={(int(r.cell_x),int(r.cell_y)):str(r.cut) for r in mapping_frame.itertuples()}
    mask_frame=pd.read_parquet(DATA/'static_mask.parquet');mask=set(map(tuple,mask_frame[['cell_x','cell_y']].to_numpy()))
    if len(mask)!=223:raise ValueError('Fixed223 mask changed')
    sets,diagnostics=observed_variants(rows,mapping,mask)
    counts=aggregate_sets(sets,panel)
    oexpected=np.array([published_counts.get((r.cut,r.month),np.nan) for r in panel.itertuples()])
    if not np.array_equal(counts.O0.to_numpy(),oexpected):raise ValueError('O0 does not reproduce exact common published series')
    con=duckdb.connect()
    con.execute(f"""create view research as select d.*,c.cut,
        case when month(acq_date)>=7 then year(acq_date) else year(acq_date)-1 end season,month(acq_date) m
        from read_parquet('{DATA}/detections.parquet') d join read_parquet('{DATA}/cells_comuna.parquet') c using(cell_x,cell_y)
        where sat='NOAA20' and not exists(select 1 from read_parquet('{DATA}/static_mask.parquet') z where z.cell_x=d.cell_x and z.cell_y=d.cell_y)""")
    typed=con.execute("""select cut,season,m,count(distinct(cell_x,cell_y,acq_date)) Cmaskedall,
        count(distinct(cell_x,cell_y,acq_date)) filter(where type=0) Cmaskedtype0 from research group by 1,2,3""").df()
    counts=counts.merge(typed,on=KEYS,how='left',validate='one_to_one').fillna({'Cmaskedall':0,'Cmaskedtype0':0})
    if not np.array_equal(counts.Cmaskedall.to_numpy(),panel.noaa20.to_numpy()):raise ValueError('Cmaskedall did not reproduce19 common rows')
    counts[['Cmaskedall','Cmaskedtype0']]=counts[['Cmaskedall','Cmaskedtype0']].astype('int64')
    counts=close_deltas(counts)
    counts=counts.merge(panel[KEYS+['month','block','orbit_epoch']],on=KEYS,validate='one_to_one')
    con.register('common_keys',panel[KEYS])
    mix=con.execute("""select r.cut,r.cell_x,r.cell_y,r.acq_date,bool_or(type=0) has_type0,
        bool_or(type is not null and type<>0) has_other,bool_or(type is null) has_unknown
        from research r join common_keys k on r.cut=k.cut and r.season=k.season and r.m=k.m group by 1,2,3,4""").df().fillna({'has_type0':False})
    cohorts=con.execute("""select source_kind,version,case when type=0 then 'type0' when type is null then 'unknown' else 'other' end type_state,
        count(*) detection_rows,count(distinct(r.cut,cell_x,cell_y,acq_date)) cell_days
        from research r join common_keys k on r.cut=k.cut and r.season=k.season and r.m=k.m group by 1,2,3""").df()
    details=[];missing_days=set();moved_days=set()
    for r in rows:
        x,y=research_grid(float(r['longitude']),float(r['latitude']))
        ox,oy=int(r['grid_x'])-18000,int(r['grid_y'])-9000
        mapped=mapping.get((x,y));key=(r['cut_com'],r['acq_date'],x,y)
        if (x,y) not in mask:
            if mapped is None:missing_days.add(key)
            elif mapped!=r['cut_com']:moved_days.add(key)
        border=abs(float(r['longitude'])/.01-round(float(r['longitude'])/.01))<1e-8 or abs(float(r['latitude'])/.01-round(float(r['latitude'])/.01))<1e-8
        if (x,y)!=(ox,oy) or border or ((x,y) not in mask and (mapped is None or mapped!=r['cut_com'])):
            details.append(dict(cut=r['cut_com'],acq_date=r['acq_date'],lon=r['longitude'],lat=r['latitude'],O_x=ox,O_y=oy,C_x=x,C_y=y,
                                near_border=bool(border),grid_disagrees=(x,y)!=(ox,oy),masked=(x,y) in mask,mapped_cut=mapped,
                                source_file=r['source_file'],version=r['version']))
    observed_cohorts=pd.DataFrame(rows).groupby(['source_file','version']).size().rename('detection_rows').reset_index()
    enabled,_=publication_metadata(sorted(panel.cut.unique()))
    report,flat=contrasts(counts,enabled)
    summary={'status':'common-archive-contract-description','independent_validation':False,'fits':0,'model_scoring':False,
             'source_rows19':len(original),'common_rows':len(panel),'common_months':64,'excluded_rows':len(excluded),
             'excluded_months':sorted(excluded.month.unique().tolist()),'exclusion_reason':'observed manifest start/end/available_years; no activity-dependent selection',
             'strict20_gate_remains_false':True,'O0_series_reproduced_exactly':True,'Cmaskedall_reproduces19_exactly':True,
             'closure_error_max':int(counts.closure_error.abs().max()),'mask_cells':len(mask),'observation_coverage':'unknown',
             'diagnostic_detection_rows':diagnostics,'mapping_unavailable_cell_days':len(missing_days),'moved_cut_cell_days':len(moved_days),
             'type_cell_day_patterns':mix.groupby(['has_type0','has_other','has_unknown'],dropna=False).size().reset_index(name='cell_days').to_dict('records'),
             'residual_is_not_causal_type_or_geography_effect':True,'reports':report}
    if before!={str(p.relative_to(ROOT)):sha(p) for p in protected}:raise ValueError('Protected sources changed')
    OUT.mkdir(parents=True,exist_ok=True)
    counts.to_parquet(OUT/'contract_counts.parquet',index=False)
    excluded[KEYS+['month']].to_csv(OUT/'excluded_archive_rows.csv',index=False)
    flat.to_csv(OUT/'contrasts.csv',index=False)
    pd.DataFrame(details).to_csv(OUT/'grid_mapping_diagnostics.csv',index=False)
    cohorts.to_csv(OUT/'research_cohorts.csv',index=False)
    observed_cohorts.to_csv(OUT/'observed_cohorts.csv',index=False)
    mix.to_parquet(OUT/'research_type_cell_days.parquet',index=False)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    code=[Path(__file__),ROOT/'pipeline/contract_gap_audit.py',ROOT/'pipeline/publish_observed.py',ROOT/'pipeline/build_detections.py',ROOT/'pipeline/build_monthly.py']
    out_manifest={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  'protocol_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'docs/reviews/2026-11-14-science-protocol-20.md',PROTOCOL]},
                  'code_sha256':{str(p.relative_to(ROOT)):sha(p) for p in code},'environment':{'python':platform.python_version(),'pandas':pd.__version__,'duckdb':duckdb.__version__},
                  'protected_sha256':before,'all_previous_artifacts_unchanged':True,
                  'output_sha256':{p.name:sha(p) for p in OUT.glob('*') if p.name!='manifest.json'}}
    (OUT/'manifest.json').write_text(json.dumps(out_manifest,indent=2,allow_nan=False)+'\n')
    print('Common archive contract audit complete:',len(panel),'rows',flush=True)
    return summary


if __name__=='__main__':run()
