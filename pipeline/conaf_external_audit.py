"""Protocol 9: external seasonal-rank contrast; no satellite model fitting."""
import json
import math
import re
import subprocess
import sys
import unicodedata
from numbers import Real
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import openpyxl
from openpyxl import load_workbook

from scientific_audit import ROOT, DATA, sha
from robust_affine_experiment import check_deadline
from platform_bridge_audit import requested_days, season_dates

OUT=DATA/'conaf_external_audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-14-science-protocol-9.md'
SOURCE=ROOT/'data/raw/external/conaf-1985-2024.xlsx'
METADATA=DATA/'external_sources/conaf-download.json'
COMMUNES=ROOT/'observed/dist/data/communes.json'
SEASONS=tuple(range(2012,2024))
SOURCE_HASH='1d92971eab0b8c73bae139f2d5228589370b72641917c630dde8eb0c9b16aad0'
SEED=20261114


def normalize_name(name):
    return ''.join(c for c in unicodedata.normalize('NFKD',name.upper()) if c.isascii() and c.isalnum())


def name_mapping(communes):
    mapping={}
    for c in communes:
        name=normalize_name(c['name'])
        if name in mapping:raise ValueError('Ambiguous normalized commune name')
        mapping[name]=c['cut']
    if len(set(mapping.values()))!=len(mapping):raise ValueError('Duplicate CUT')
    return mapping


def parse_season(text):
    match=re.fullmatch(r'\s*(\d{4})\s*-\s*(\d{4})\s*',str(text))
    if not match or int(match[2])!=int(match[1])+1:raise ValueError('Invalid season header')
    return int(match[1])


def parse_count(value, formula=False):
    if value is None:return None,'formula_without_cached_value' if formula else 'blank_unknown'
    if isinstance(value,bool) or not isinstance(value,Real) or not math.isfinite(value) or value<0 or int(value)!=value:
        raise ValueError('Invalid CONAF occurrence count')
    return int(value),'numeric_cached_formula' if formula else 'numeric'


def extract_workbook(path,communes,seasons):
    mapping=name_mapping(communes);records=[];found=set()
    cached=load_workbook(path,read_only=True,data_only=True,keep_links=False)
    formulas=load_workbook(path,read_only=True,data_only=False,keep_links=False)
    try:
        for sheet in cached:
            if not re.fullmatch(r'\s*\d{4}\s*-\s*\d{4}\s*',sheet.title):continue
            season=parse_season(sheet.title)
            if season not in seasons:continue
            if season in found:raise ValueError('Duplicate season worksheet')
            found.add(season)
            rows=sheet.iter_rows(values_only=True)
            rawrows=formulas[sheet.title].iter_rows()
            seen=set()
            for number,(row,raw) in enumerate(zip(rows,rawrows,strict=True),1):
                if number==3 and parse_season(row[0])!=season:raise ValueError('Worksheet/header season mismatch')
                if number==4:
                    labels=[normalize_name(str(v)) for v in row[:4]]
                    if labels!=['REGION','PROVINCIA','COMUNA','NUMEROINCENDIOS']:
                        raise ValueError('Unsupported CONAF count columns')
                if number<7 or len(row)<4 or not isinstance(row[2],str):continue
                key=normalize_name(row[2])
                if key not in mapping:continue
                cut=mapping[key]
                if cut in seen:raise ValueError('Duplicate commune within season')
                seen.add(cut)
                value,state=parse_count(row[3],raw[3].data_type=='f')
                records.append({'cut':cut,'season':season,'sheet':sheet.title,'excel_row':number,
                    'source_name':row[2],'conaf_occurrences':value,'value_state':state})
            if seen!=set(mapping.values()):raise ValueError('Unmatched expected communes: '+str(sorted(set(mapping.values())-seen)))
        if found!=set(seasons):raise ValueError('Missing season worksheet')
    finally:
        cached.close();formulas.close()
    return pd.DataFrame(records).sort_values(['cut','season']).reset_index(drop=True)


def spearman(x,y):
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float)
    if x.shape!=y.shape or x.ndim!=1 or np.isinf(x).any() or np.isinf(y).any():raise ValueError('Invalid rank inputs')
    valid=np.isfinite(x)&np.isfinite(y);x=x[valid];y=y[valid]
    if len(x)<2 or np.ptp(x)==0 or np.ptp(y)==0:return None
    a=pd.Series(x).rank(method='average').to_numpy();b=pd.Series(y).rank(method='average').to_numpy()
    return float(np.corrcoef(a,b)[0,1])


def bootstrap_rank(frame,replicates=5000):
    x=frame.snpp_cell_days.to_numpy(dtype=float);y=frame.conaf_occurrences.to_numpy(dtype=float)
    if not np.isfinite(x).all() or not np.isfinite(y).all() or len(x)<2:raise ValueError('Incomplete bootstrap panel')
    rng=np.random.default_rng(SEED);values=[]
    for _ in range(replicates):
        draw=rng.integers(0,len(x),size=len(x));value=spearman(x[draw],y[draw])
        if value is not None:values.append(value)
    return {'rho':spearman(x,y),'blocks':len(x),'replicates':replicates,'valid_replicates':len(values),
            'degenerate_replicates':replicates-len(values),'seed':SEED,
            'interval_95_percentile':[float(v) for v in np.quantile(values,[.025,.975])] if values else None}


def regional_panels(pairs):
    if pairs.duplicated(['cut','season']).any():raise ValueError('Duplicate panel records')
    cuts=sorted(pairs.cut.unique());seasons=sorted(pairs.season.unique())
    if len(pairs)!=len(cuts)*len(seasons):raise ValueError('Incomplete panel grid')
    complete_cuts=pairs.groupby('cut').conaf_occurrences.count()
    balanced=complete_cuts[complete_cuts==len(seasons)].index.tolist()
    complete_seasons=pairs.groupby('season').conaf_occurrences.count()
    all54=complete_seasons[complete_seasons==len(cuts)].index.tolist()
    if not balanced or len(all54)<2:raise ValueError('Insufficient complete regional panel')
    primary=pairs[pairs.cut.isin(balanced)].groupby('season')[['snpp_cell_days','conaf_occurrences']].sum(min_count=len(balanced)).reset_index()
    sensitivity=pairs[pairs.season.isin(all54)].groupby('season')[['snpp_cell_days','conaf_occurrences']].sum(min_count=len(cuts)).reset_index()
    primary['communes']=len(balanced);sensitivity['communes']=len(cuts)
    return primary,sensitivity,balanced


def run():
    check_deadline()
    if not SOURCE.exists():raise FileNotFoundError('Download pinned CONAF XLSX first; see external_sources/conaf-download.json')
    if sha(SOURCE)!=SOURCE_HASH:raise ValueError('Unexpected CONAF source version; do not silently replace benchmark')
    protected=sorted((ROOT/'web/public/data').rglob('*.json'))
    protected += [DATA/f for f in ['detections.parquet','celldays.parquet','static_mask.parquet','params.json','gates.csv','eval_loso.csv','eval_final.csv']]
    for directory in ['scientific_audit','affine_audit','robust_affine_audit','piecewise_audit','geography_audit','platform_bridge_audit','temporal_transport_audit']:
        protected+=sorted((DATA/directory).glob('*'))
    before={str(p.relative_to(ROOT)):sha(p) for p in protected}
    communes=json.loads(COMMUNES.read_text())['communes']
    if len(communes)!=54:raise ValueError('Expected canonical 54 communes')
    extracted=extract_workbook(SOURCE,communes,SEASONS)
    paths=pd.read_csv(DATA/'inventory.csv').path
    sp=requested_days(paths,'SNPP')
    if any(not season_dates(s)<=sp for s in SEASONS):raise ValueError('Missing requested SP source window')
    con=duckdb.connect()
    try:
        sat=con.execute(f"""select cut,season,count(*) snpp_cell_days,
            count(*) filter (any_nrt) provisional_cell_days
            from read_parquet('{DATA}/celldays.parquet') d
            where sat='SNPP' and season between 2012 and 2023
            and not exists(select 1 from read_parquet('{DATA}/static_mask.parquet') s
                           where s.cell_x=d.cell_x and s.cell_y=d.cell_y)
            group by 1,2""").df()
    finally:con.close()
    pairs=extracted.merge(sat,on=['cut','season'],how='left',validate='one_to_one')
    pairs[['snpp_cell_days','provisional_cell_days']]=pairs[['snpp_cell_days','provisional_cell_days']].fillna(0).astype('int64')
    if pairs.provisional_cell_days.sum():raise ValueError('Unexpected provisional cell-days in external panel')
    primary,sensitivity,balanced=regional_panels(pairs)
    local=[]
    for cut,g in pairs.groupby('cut'):
        known=g[g.conaf_occurrences.notna()];n=len(known)
        rho=spearman(known.snpp_cell_days,known.conaf_occurrences) if n>=8 else None
        status='defined' if rho is not None else 'insufficient_pairs' if n<8 else 'constant_series'
        local.append({'cut':cut,'name':next(c['name'] for c in communes if c['cut']==cut),'n_pairs':n,
                      'unknown_counts':int(g.conaf_occurrences.isna().sum()),'rho':rho,'status':status})
    local=pd.DataFrame(local);defined=local.rho.dropna()
    influence=pd.DataFrame([{'excluded_season':int(s),'n_pairs':len(primary)-1,
        'rho':spearman(primary[primary.season!=s].snpp_cell_days,primary[primary.season!=s].conaf_occurrences)} for s in primary.season])
    summary={'status':'external-descriptive-seasonal-rank-contrast','harmonization_validated':False,
        'model_fitted':False,'seasons':list(SEASONS),'primary':{'balanced_cuts':balanced,
        'excluded_cuts':sorted(set(pairs.cut)-set(balanced)),'statistics':bootstrap_rank(primary)},
        'sensitivity_all54':{'seasons':sensitivity.season.tolist(),'statistics':bootstrap_rank(sensitivity)},
        'missing_counts':pairs[pairs.conaf_occurrences.isna()][['cut','season','sheet','excel_row','value_state']].to_dict('records'),
        'local':{'defined':len(defined),'positive':int((defined>0).sum()),'nonpositive':int((defined<=0).sum()),
                 'median_rho':float(defined.median()) if len(defined) else None,
                 'q25_rho':float(defined.quantile(.25)) if len(defined) else None,
                 'q75_rho':float(defined.quantile(.75)) if len(defined) else None},
        'primary_leave_one_season_out':{'min':float(influence.rho.min()),'max':float(influence.rho.max())},
        'requested_source_windows_complete':True,'observation_coverage_known':False,'provisional_cell_days':0}
    check_deadline()
    if sha(SOURCE)!=SOURCE_HASH or before!={str(p.relative_to(ROOT)):sha(p) for p in protected}:raise ValueError('Protected source/production changed')
    OUT.mkdir(parents=True,exist_ok=True)
    for name,frame in [('extracted_counts.csv',extracted),('paired_seasons.csv',pairs),('regional_primary.csv',primary),
                       ('regional_sensitivity.csv',sensitivity),('commune_correlations.csv',local),('season_influence.csv',influence)]:
        frame.to_csv(OUT/name,index=False)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    helpers=['scientific_audit.py','robust_affine_experiment.py','platform_bridge_audit.py']
    manifest={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'protocol_sha256':sha(PROTOCOL),'code_sha256':sha(Path(__file__)),
        'helpers_sha256':{f:sha(ROOT/'pipeline'/f) for f in helpers},
        'input_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [SOURCE,METADATA,COMMUNES,DATA/'inventory.csv']},
        'environment_sha256':{f:sha(ROOT/f) for f in ['pyproject.toml','uv.lock']},
        'source_metadata':json.loads(METADATA.read_text()),'versions':{'python':sys.version,'openpyxl':openpyxl.__version__,'pandas':pd.__version__,'numpy':np.__version__,'duckdb':duckdb.__version__},
        'protected_sha256':before,'production_and_previous_unchanged':True,
        'output_sha256':{p.name:sha(p) for p in sorted(OUT.glob('*')) if p.name!='manifest.json'}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n')
    print('CONAF rank audit complete:',OUT,flush=True)
    return summary


if __name__=='__main__':run()
