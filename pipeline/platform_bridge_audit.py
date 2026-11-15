"""Protocol 7: descriptive VIIRS continuity, no coefficient changes."""
import calendar
import json
import re
import subprocess
from datetime import date,timedelta
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from scientific_audit import ROOT,DATA,sha
from robust_affine_experiment import check_deadline

OUT=DATA/'platform_bridge_audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-14-science-protocol-7.md'
PAIRS=(('NOAA20_vs_SNPP','SNPP','NOAA20',tuple(range(2018,2026))),
       ('NOAA21_vs_NOAA20','NOAA20','NOAA21',tuple(range(2023,2026))))


def season_dates(season):
    start,end=date(season,7,1),date(season+1,7,1)
    return {start+timedelta(days=n) for n in range((end-start).days)}


def requested_days(paths,satellite):
    source={'SNPP':'VIIRS_SNPP_SP','NOAA20':'VIIRS_NOAA20_SP','NOAA21':'VIIRS_NOAA21_SP'}[satellite]
    days=set()
    for path in paths:
        if satellite=='SNPP' and '/firms_country/viirs-snpp/' in path:
            match=re.search(r'viirs-snpp_(\d{4})_Chile\.csv$',path)
            if match:
                year=int(match[1]);start=date(year,1,1)
                days.update(start+timedelta(days=n) for n in range(366 if calendar.isleap(year) else 365))
        if '/'+source+'/' in path:
            match=re.search(r'_(\d{4}-\d{2}-\d{2})_(\d+)d\.csv$',path)
            if not match:raise ValueError('Unrecognized SP inventory path')
            start=date.fromisoformat(match[1]);days.update(start+timedelta(days=n) for n in range(int(match[2])))
    return days


def complete_seasons(seasons,reference_days,comparator_days):
    valid,excluded=[],[]
    for season in seasons:
        expected=season_dates(season);a=expected-reference_days;b=expected-comparator_days
        if not a and not b:valid.append(season)
        else:excluded.append({'season':season,'reference_missing_requested_days':len(a),'comparator_missing_requested_days':len(b)})
    return valid,excluded


def metrics(frame):
    reference=float(frame.reference.sum());comparator=float(frame.comparator.sum())
    return {'months':len(frame),'reference':reference,'comparator':comparator,
        'ratio':comparator/reference if reference else None,
        'relative_bias':(comparator-reference)/reference if reference else None,
        'wape':float((frame.comparator-frame.reference).abs().sum())/reference if reference else None,
        'active_pairs':int(((frame.reference>0)|(frame.comparator>0)).sum()),
        'provisional_months':int(frame.provisional.sum())}


def bootstrap_ratio(annual):
    if len(annual)<2:return {'blocks':len(annual),'interval':None,'reason':'fewer than two seasons'}
    rng=np.random.default_rng(20261114);indices=rng.integers(0,len(annual),size=(5000,len(annual)))
    ref=annual.reference.to_numpy()[indices].sum(axis=1);comp=annual.comparator.to_numpy()[indices].sum(axis=1)
    valid=ref>0;ratios=comp[valid]/ref[valid]
    return {'blocks':len(annual),'replicates':5000,'seed':20261114,'valid_replicates':int(valid.sum()),
        'interval':[float(v) for v in np.quantile(ratios,[.025,.975])] if len(ratios) else None}


def overlap(reference,comparator):
    intersection=len(reference&comparator);union=len(reference|comparator)
    return {'reference_cell_days':len(reference),'comparator_cell_days':len(comparator),'intersection':intersection,'union':union,
        'jaccard':intersection/union if union else None}


def paired_months(monthly,cuts,seasons,reference,comparator):
    grid=pd.MultiIndex.from_product([cuts,seasons,range(1,13)],names=['cut','season','m']).to_frame(index=False)
    for satellite,target in [(reference,'reference'),(comparator,'comparator')]:
        source=monthly[(monthly.sat==satellite)&monthly.season.isin(seasons)][['cut','season','m','cell_days','provisional']]
        grid=grid.merge(source.rename(columns={'cell_days':target,'provisional':target+'_nrt'}),on=['cut','season','m'],how='left',validate='one_to_one')
    grid['reference']=grid.reference.fillna(0).astype(int);grid['comparator']=grid.comparator.fillna(0).astype(int)
    grid['provisional']=grid.reference_nrt.fillna(False).astype(bool)|grid.comparator_nrt.fillna(False).astype(bool)
    grid['observation_coverage']='unknown'
    return grid.drop(columns=['reference_nrt','comparator_nrt'])


def run():
    check_deadline()
    inputs=[DATA/f for f in ['inventory.csv','celldays.parquet','static_mask.parquet']]
    protected=inputs+[DATA/f for f in ['params.json','gates.csv','eval_loso.csv','eval_final.csv']]
    protected+=sorted((ROOT/'web/public/data').rglob('*.json'))
    for directory in ['scientific_audit','affine_audit','robust_affine_audit','piecewise_audit','geography_audit']:protected+=sorted((DATA/directory).glob('*'))
    before={str(p.relative_to(ROOT)):sha(p) for p in protected}
    inventory=pd.read_csv(DATA/'inventory.csv')
    coverage={sat:requested_days(inventory.path.tolist(),sat) for sat in ['SNPP','NOAA20','NOAA21']}
    con=duckdb.connect()
    con.execute(f"""create view selected_days as select c.* from read_parquet('{DATA}/celldays.parquet') c
      where sat in ('SNPP','NOAA20','NOAA21') and not exists(
        select 1 from read_parquet('{DATA}/static_mask.parquet') m where m.cell_x=c.cell_x and m.cell_y=c.cell_y)""")
    monthly=con.execute('select cut,season,m,sat,count(*) cell_days,bool_or(any_nrt) provisional from selected_days group by all').df()
    index=json.loads((ROOT/'web/public/data/index.json').read_text());cuts=sorted(c['cut'] for c in index['comunas']);names={c['cut']:c['comuna'] for c in index['comunas']}
    report={'status':'descriptive-platform-audit','observation_coverage':'unknown','fixed_published_mask':True,'pairs':{}}
    pair_rows,annual_rows,month_rows,commune_rows,overlap_rows=[],[],[],[],[]
    for label,ref,comp,requested in PAIRS:
        check_deadline();seasons,excluded=complete_seasons(requested,coverage[ref],coverage[comp])
        if not seasons:raise ValueError(f'No documented complete requested window: {label}')
        paired=paired_months(monthly,cuts,seasons,ref,comp)
        annual=pd.DataFrame([{'season':int(s),**metrics(g)} for s,g in paired.groupby('season')])
        month=pd.DataFrame([{'m':int(m),**metrics(g)} for m,g in paired.groupby('m')])
        commune=pd.DataFrame([{'cut':cut,'commune':names[cut],**metrics(g)} for cut,g in paired.groupby('cut')])
        commune['sufficient_reference_signal']=commune.reference>=100
        commune['outside_screening_range']=commune.sufficient_reference_signal&((commune.ratio<.8)|(commune.ratio>1.25))
        selected=con.execute("select cut,cell_x,cell_y,acq_date,sat from selected_days where season in ("+','.join(map(str,seasons))+") and sat in (?,?)",[ref,comp]).fetchall()
        reference={r[:4] for r in selected if r[4]==ref};comparator={r[:4] for r in selected if r[4]==comp}
        if len(reference)!=int(paired.reference.sum()) or len(comparator)!=int(paired.comparator.sum()):raise ValueError('Set/monthly counts disagree')
        local_overlap=[{'cut':cut,**overlap({r for r in reference if r[0]==cut},{r for r in comparator if r[0]==cut})} for cut in cuts]
        flagged=commune.loc[commune.outside_screening_range,['cut','commune','reference','comparator','ratio']].to_dict('records')
        report['pairs'][label]={'reference_platform':ref,'comparator_platform':comp,'included_seasons':seasons,'excluded_requested_seasons':excluded,
            'aggregate':metrics(paired),'regional_ratio_bootstrap':bootstrap_ratio(annual),'positive_cell_day_overlap':overlap(reference,comparator),
            'annual_ratio_min':float(annual.ratio.min()),'annual_ratio_max':float(annual.ratio.max()),
            'screening':{'minimum_reference_total':100,'ratio_limits':[.8,1.25],'sufficient_signal_communes':int(commune.sufficient_reference_signal.sum()),'flagged':flagged}}
        pair_rows.append(paired.assign(pair=label));annual_rows.append(annual.assign(pair=label));month_rows.append(month.assign(pair=label));commune_rows.append(commune.assign(pair=label));overlap_rows.append(pd.DataFrame(local_overlap).assign(pair=label))
        print('Platform pair complete:',label,'seasons',seasons,flush=True)
    if before!={str(p.relative_to(ROOT)):sha(p) for p in protected}:raise ValueError('Protected sources/production changed')
    OUT.mkdir(parents=True,exist_ok=True)
    for filename,frames in [('paired_months.csv',pair_rows),('annual.csv',annual_rows),('calendar_months.csv',month_rows),('communes.csv',commune_rows),('cell_day_overlap.csv',overlap_rows)]:pd.concat(frames,ignore_index=True).to_csv(OUT/filename,index=False)
    (OUT/'summary.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    manifest={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'code_sha256':sha(Path(__file__)),'protocol_sha256':sha(PROTOCOL),
        'input_sha256':{str(p.relative_to(ROOT)):sha(p) for p in inputs},'protected_sha256':before,'production_and_previous_unchanged':True,
        'output_sha256':{p.name:sha(p) for p in sorted(OUT.glob('*')) if p.name!='manifest.json'}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n');print('Platform bridge audit complete:',OUT,flush=True)
    return report


if __name__=='__main__':run()
