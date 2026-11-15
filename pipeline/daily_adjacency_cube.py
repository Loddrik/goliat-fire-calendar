"""36: canonical Aqua same-cell adjacency cube; no responses or fitting."""
from __future__ import annotations
import argparse,ast,calendar,csv,gzip,hashlib,io,json,resource,shutil,sys
from collections import Counter,defaultdict
from datetime import date,datetime,timezone
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/processed';PARENT=DATA/'cold_region_audit';OUT=DATA/'daily_adjacency_audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-15-daily-adjacency-protocol.md';DESIGN=ROOT/'docs/reviews/2026-11-15-daily-adjacency-design.md'
CODE21=ROOT/'pipeline/cold_region_audit.py';PREFIX='goliat-daily-adjacency-v1|'
START='2026-11-15T07:48:23+00:00';CHECKPOINT='2026-11-15T08:03:23+00:00';END='2026-11-15T08:33:23+00:00'
FEATURE_COLUMNS=['regime','cut','season','m','aqua'];DAY_COLUMNS=['sat','cut','cell_x','cell_y','acq_date','season','m']
ACTIVE=None
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def dump(path,obj):Path(path).write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n')
def write_csv(path,rows,fields,budget=None):
    with Path(path).open('wb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as z:
        with io.TextIOWrapper(z,encoding='utf8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
            for row in rows:
                if budget:budget.row()
                w.writerow(row)
def read_csv(path):
    with gzip.open(path,'rt',newline='') as f:return list(csv.DictReader(f))
class Budget:
    def __init__(self):self.rows=0;self.calls=0;self.peak=0
    def check(self,force=False):
        self.calls+=1
        if force or self.calls%1000==0:
            if datetime.now(timezone.utc)>=datetime.fromisoformat(END):raise TimeoutError('36 fixed cap reached')
            rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024);self.peak=max(self.peak,rss)
            if rss>1024**3:raise RuntimeError('RSS resource_limit')
            if OUT.exists() and sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())>50*1024**2:raise RuntimeError('output resource_limit')
    def row(self):
        self.rows+=1
        if self.rows>1_000_000:raise RuntimeError('export row resource_limit')
        self.check()
def calendar_year(season,month):
    if not 1<=month<=12:raise ValueError('Invalid calendar month')
    return season if month>=7 else season+1
def season_of(day):return day.year if day.month>=7 else day.year-1
def month_columns(events,year,month):
    columns=[set() for _ in range(calendar.monthrange(year,month)[1])];seen=set()
    for cell,day in events:
        if not 1<=day<=len(columns) or (cell,day) in seen:raise ValueError('Duplicate/out-of-month canonical cell-day')
        seen.add((cell,day));columns[day-1].add(cell)
    return [frozenset(c) for c in columns]
def hash_permutation(cut,year,month):
    length=calendar.monthrange(year,month)[1];yyyymm=f'{year:04d}{month:02d}'
    return sorted(range(1,length+1),key=lambda d:(hashlib.sha256((PREFIX+cut+'|'+yyyymm+'|'+f'{d:02d}').encode('utf8')).digest(),d))
def permute_columns(columns,origin_to_dest):
    if sorted(origin_to_dest)!=list(range(1,len(columns)+1)):raise ValueError('Permutation not full-calendar bijection')
    out=[frozenset() for _ in columns]
    for origin,dest in enumerate(origin_to_dest):out[dest-1]=columns[origin]
    return out
def adjacency(columns):
    pairs=sum(len(a&b) for a,b in zip(columns,columns[1:]));return int(pairs>0),pairs
def preserve(columns,other):
    per_cell=lambda cols:Counter(c for column in cols for c in column)
    if len(columns)!=len(other) or Counter(columns)!=Counter(other) or per_cell(columns)!=per_cell(other) or sorted(map(len,columns))!=sorted(map(len,other)):raise ValueError('Placebo full-calendar/cell/cooccurrence invariant failed')
    return True
def regimes_from_code(text):
    node=next((n.value for n in ast.parse(text).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REGIMES' for t in n.targets)),None)
    if node is None or any(isinstance(n,(ast.Call,ast.Attribute,ast.Subscript,ast.Lambda)) for n in ast.walk(node)):raise ValueError('Unexpected nonliteral REGIMES expression')
    regimes=eval(compile(ast.Expression(node),'<frozen21REGIMES>','eval'),{'__builtins__':{}},{})
    if set(regimes)!={'08_forward','08_backward','16_forward','16_backward'}:raise ValueError('Unexpected four-regime contract')
    return regimes
def freeze():
    b=Budget();b.check(True)
    if OUT.exists():raise FileExistsError('36 output already exists')
    manifest=json.loads((PARENT/'manifest.json').read_text())
    paths=[DATA/'celldays.parquet',PARENT/'candidate_mask.csv',PARENT/'predictions.parquet',PARENT/'manifest.json',CODE21,PROTOCOL,DESIGN,ROOT/'docs/reviews/2026-11-14-science-protocol-21.md',ROOT/'tests/test_daily_adjacency_cube.py']
    if sha(DATA/'celldays.parquet')!=manifest['protected_sha256']['data/processed/celldays.parquet']:raise ValueError('Canonical source hash changed')
    for name in ['candidate_mask.csv','predictions.parquet']:
        if sha(PARENT/name)!=manifest['output_sha256'][name]:raise ValueError('Frozen21 artifact changed')
    if sha(CODE21)!=manifest['code_sha256']['pipeline/cold_region_audit.py']:raise ValueError('Frozen21 code changed')
    OUT.mkdir(parents=True)
    dump(OUT/'freeze.json',{'frozen_utc':now(),'protocol_commit':'f6e45cc','code_sha256':sha(__file__),'inputs_sha256':{str(p.relative_to(ROOT)):sha(p) for p in paths},'columns':{'celldays':DAY_COLUMNS,'prediction_control':FEATURE_COLUMNS},'response_columns_requested':[],'cap':{'start':START,'checkpoint':CHECKPOINT,'end':END},'permutation_prefix_literal':PREFIX,'mapping':'ORIGINday d -> rankedDays[d-1] DESTday','features_calculated':False,'permutations_calculated':False})
    for p,name in [(Path(__file__),'code.snapshot.py.txt'),(PROTOCOL,'protocol.snapshot.md.txt'),(DESIGN,'design.snapshot.md.txt'),(ROOT/'tests/test_daily_adjacency_cube.py','tests.snapshot.py.txt')]:shutil.copyfile(p,OUT/name)
    print(json.dumps({'code_sha256':sha(__file__),'freeze_sha256':sha(OUT/'freeze.json')}))
def verify(b=None):
    global ACTIVE
    b=b or Budget();ACTIVE=b;b.check(True);f=json.loads((OUT/'freeze.json').read_text())
    if sha(__file__)!=f['code_sha256']:raise ValueError('Code changed after freeze')
    for p,h in f['inputs_sha256'].items():
        if sha(ROOT/p)!=h:raise ValueError('Protected input changed: '+p)
    return b,f
def checkpoint():
    b,f=verify()
    if datetime.now(timezone.utc)>=datetime.fromisoformat(CHECKPOINT):raise TimeoutError('Identity checkpoint expired; STOP partial')
    if (OUT/'checkpoint.json').exists():raise FileExistsError('Checkpoint already exists')
    regimes=regimes_from_code(CODE21.read_text());control=pq.read_table(PARENT/'predictions.parquet',columns=FEATURE_COLUMNS).to_pandas()
    if list(control.columns)!=FEATURE_COLUMNS or len(control)!=10368 or control.duplicated(['regime','cut','season','m']).any():raise ValueError('Prediction FEATURE-only projection contract invalid')
    if any(not isinstance(c,str) or len(c)!=5 for c in control.cut) or set(control.regime)!=set(regimes):raise ValueError('CUT/regime metadata changed')
    if control[['season','m','aqua']].isna().any().any() or (control.aqua<0).any() or not (control.aqua==control.aqua.astype('int64')).all():raise ValueError('Invalid Aqua feature scalar')
    keys=['cut','season','m'];grouped=control.groupby(keys,sort=True).aqua
    if not (grouped.nunique()==1).all() or not (grouped.size()==2).all():raise ValueError('Contradictory/missing duplicated Aqua controls')
    cuts=sorted(control.cut.unique());expected={(c,s,m) for c in cuts for s in range(2012,2020) for m in range(1,13)}
    counts_control={tuple(k):int(v) for k,v in grouped.first().items()}
    if len(cuts)!=54 or sum(c.startswith('08') for c in cuts)!=33 or sum(c.startswith('16') for c in cuts)!=21 or set(counts_control)!=expected or len(expected)!=5184:raise ValueError('Fixed5184 calendar/CUT domain changed')
    for r in control.itertuples(index=False):
        if int(r.season) not in regimes[r.regime][2]:raise ValueError('Prediction feature outside frozen destination domain')
    mask_frame=pd.read_csv(PARENT/'candidate_mask.csv',usecols=['cell_x','cell_y']);mask=[tuple(map(int,r)) for r in mask_frame.itertuples(index=False,name=None)]
    if len(mask)!=6 or len(set(mask))!=6:raise ValueError('Mask not frozen6 unique cells')
    mask=set(mask)
    table=pq.read_table(DATA/'celldays.parquet',columns=DAY_COLUMNS,filters=[('sat','=','Aqua')]);days=table.to_pandas(date_as_object=True)
    if list(days.columns)!=DAY_COLUMNS or not (days.sat=='Aqua').all() or days.duplicated(['sat','cut','cell_x','cell_y','acq_date']).any():raise ValueError('Canonical Aqua uniqueness/satellite contract failed')
    if days.groupby(['cell_x','cell_y']).cut.nunique().max()>1:raise ValueError('Canonical cell-to-CUT assignment conflict')
    support=[];monthly=Counter()
    for r in days.itertuples(index=False):
        b.check();d=r.acq_date
        if not isinstance(d,date) or isinstance(d,datetime) or int(r.season)!=season_of(d) or int(r.m)!=d.month:raise ValueError('UTC date/season/month mismatch')
        if r.cut not in cuts:raise ValueError('Canonical CUT outside frozen panel')
        if not 2012<=int(r.season)<=2019:continue
        cell=(int(r.cell_x),int(r.cell_y))
        if cell in mask:continue
        key=(r.cut,int(r.season),int(r.m));monthly[key]+=1
        support.append({'cut':r.cut,'season':int(r.season),'m':int(r.m),'cell_x':cell[0],'cell_y':cell[1],'acq_date_UTC':d.isoformat(),'year':d.year,'day':d.day})
    if any(monthly.get(k,0)!=v for k,v in counts_control.items()):raise ValueError('Canonical monthly Aqua differs from21 feature control')
    comparison=[]
    for r in control.itertuples(index=False):
        key=(r.cut,int(r.season),int(r.m));comparison.append({'regime':r.regime,'cut':r.cut,'season':int(r.season),'m':int(r.m),'aqua21':int(r.aqua),'aqua_rebuilt':monthly.get(key,0),'equal':monthly.get(key,0)==int(r.aqua)})
    write_csv(OUT/'canonical_Aqua_support.csv.gz',sorted(support,key=lambda r:(r['cut'],r['acq_date_UTC'],r['cell_x'],r['cell_y'])),['cut','season','m','cell_x','cell_y','acq_date_UTC','year','day'],b)
    write_csv(OUT/'Aqua21_feature_projection.csv.gz',control.to_dict('records'),FEATURE_COLUMNS,b)
    write_csv(OUT/'monthly_identity_all10368.csv.gz',comparison,list(comparison[0]),b);shutil.copyfile(PARENT/'candidate_mask.csv',OUT/'mask6.csv');b.rows+=6;dump(OUT/'regime_contract.json',regimes)
    if datetime.now(timezone.utc)>=datetime.fromisoformat(CHECKPOINT):raise TimeoutError('Identity artifacts not ready by checkpoint; STOP partial')
    dump(OUT/'checkpoint.json',{'completed_utc':now(),'checkpoint_deadline':CHECKPOINT,'all_identity_gates_passed':True,'unique_keys':5184,'prediction_feature_rows':10368,'mask_cells':6,'canonical_Aqua_rows_all_dates':len(days),'unmasked_support_rows_study_domain':len(support),'monthly_matches_each_control_row':True,'duplicate_canonical_records':0,'source_cell_CUT_unique':True,'D_or_permutations_computed':False,'response_columns_read':[],'source_projection_columns':FEATURE_COLUMNS,'output_rows_so_far':b.rows,'files_sha256':{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name not in {'checkpoint.json'}}})
    print(json.dumps({'checkpoint_passed':True,'keys':5184,'all10368_Aqua_equal':True,'support_rows':len(support),'checkpoint_sha256':sha(OUT/'checkpoint.json')}))
def summary_counts(rows):
    return {'n':len(rows),'D_real_1':sum(r['D_real'] for r in rows),'D_placebo_1':sum(r['D_placebo'] for r in rows),'D_discordant':sum(r['D_real']!=r['D_placebo'] for r in rows),'pair_diagnostic_real':sum(r['n_pairs_real'] for r in rows),'pair_diagnostic_placebo':sum(r['n_pairs_placebo'] for r in rows)}
def run():
    b,f=verify();cp=json.loads((OUT/'checkpoint.json').read_text())
    if not cp['all_identity_gates_passed'] or datetime.fromisoformat(cp['completed_utc'])>=datetime.fromisoformat(CHECKPOINT):raise ValueError('Checkpoint not accredited within cap')
    if (OUT/'summary.json').exists():raise FileExistsError('Cube already exists')
    for name,h in cp['files_sha256'].items():
        if sha(OUT/name)!=h:raise ValueError('Checkpoint input changed')
    b.rows=cp['output_rows_so_far'];support=read_csv(OUT/'canonical_Aqua_support.csv.gz');features=read_csv(OUT/'Aqua21_feature_projection.csv.gz');regimes=json.loads((OUT/'regime_contract.json').read_text());events=defaultdict(list);aqua={}
    for r in support:events[(r['cut'],int(r['season']),int(r['m']))].append(((int(r['cell_x']),int(r['cell_y'])),int(r['day'])))
    for r in features:aqua[(r['cut'],int(r['season']),int(r['m']))]=int(r['aqua'])
    cube=[];permutations=[];block_proofs=[]
    for (cut,season,m),count in sorted(aqua.items()):
        b.check();year=calendar_year(season,m);cols=month_columns(events[(cut,season,m)],year,m)
        if sum(map(len,cols))!=count:raise ValueError('Checkpoint support/Aqua mismatch')
        mapping=hash_permutation(cut,year,m);other=permute_columns(cols,mapping);preserve(cols,other);d,n=adjacency(cols);dp,npairs=adjacency(other)
        if (d or dp) and count<2:raise ValueError('D=>Aqua>=2 violated')
        g='JJA' if m in (6,7,8) else str(m);row={'cut':cut,'season':season,'m':m,'year':year,'g':g,'aqua':count,'D_real':d,'D_placebo':dp,'n_pairs_real':n,'n_pairs_placebo':npairs,'calendar_days':len(cols)};cube.append(row)
        for origin,dest in enumerate(mapping,1):permutations.append({'cut':cut,'year':year,'m':m,'origin_day':origin,'destination_day':dest,'origin_active_cells':len(cols[origin-1]),'destination_active_cells':len(other[dest-1])})
        block_proofs.append({'cut':cut,'season':season,'m':m,'fullcalendar_bijection':True,'cell_month_counts_preserved':True,'multiset_full_day_cell_sets_preserved':True,'daily_count_multiset_preserved':True,'mapping_sha256':hashlib.sha256(bytes(mapping)).hexdigest(),'D_may_be_unchanged':d==dp})
    if len(cube)!=5184:raise ValueError('Final cube domain changed')
    write_csv(OUT/'cube.csv.gz',cube,list(cube[0]),b);pd.DataFrame(cube).to_parquet(OUT/'cube.parquet',index=False);b.rows+=len(cube)
    write_csv(OUT/'fullcalendar_permutations.csv.gz',permutations,list(permutations[0]),b);write_csv(OUT/'block_invariants.csv.gz',block_proofs,list(block_proofs[0]),b)
    grouped={}
    for g in sorted(set(r['g'] for r in cube)):
        for positive in [False,True]:grouped[f'g={g}|Aqua>0={positive}']=summary_counts([r for r in cube if r['g']==g and (r['aqua']>0)==positive])
    roles={}
    for label,(region,origin,dest) in regimes.items():
        roles[label]={}
        for scope,rows in [('future_fit_SOURCE_ORIGIN',[r for r in cube if r['cut'].startswith(region) and r['season'] in origin]),('prediction_SOURCE_DEST',[r for r in cube if r['cut'].startswith(region) and r['season'] in dest]),('prediction_held_DEST',[r for r in cube if not r['cut'].startswith(region) and r['season'] in dest])]:
            roles[label][scope]={'all':summary_counts(rows),'by_g_and_Apositive':{f'g={g}|Aqua>0={a}':summary_counts([r for r in rows if r['g']==g and (r['aqua']>0)==a]) for g in sorted(set(r['g'] for r in cube)) for a in [False,True]}}
    verify(b);b.check(True);dump(OUT/'summary.json',{'completed_utc':now(),'all_cube_integrity_gates_passed':True,'checkpoint_sha256':sha(OUT/'checkpoint.json'),'cube_rows':len(cube),'support_rows':len(support),'fullcalendar_mapping_rows':len(permutations),'exported_rows':b.rows,'overall':summary_counts(cube),'by_g_and_Apositive':grouped,'regime_scope_support':roles,'peak_RSS_bytes':b.peak,'RSS_platform':sys.platform,'operator':'same canonical Aqua cell on consecutive UTC days strictly inside one calendar month','features':['D_real','D_placebo'],'pair_counts_are_diagnostic_only':True,'permutation_prefix_literal':PREFIX,'permutation_direction':'ORIGIN d -> rankedDays[d-1] DEST','raw_acquisition_reproducibility':'not established; frozen derived integrity is separate','no_registered_record_does_not_mean_physical_absence':True,'response_columns_read':[],'model_fitted':False,'loss_computed':False,'stage37_authorized':False,'gate1_passed':False})
    dump(OUT/'manifest.json',{'files':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='manifest.json'},'all_cube_integrity_gates_passed':True,'model_fitted':False,'response_columns_read':[]})
    print(json.dumps({'cube_integrity_passed':True,'rows':len(cube),'exported_rows':b.rows,'peak_RSS_bytes':b.peak}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['freeze','checkpoint','run']);args=p.parse_args()
    try:{'freeze':freeze,'checkpoint':checkpoint,'run':run}[args.stage]()
    except Exception as e:
        if OUT.exists():dump(OUT/f'failure-{args.stage}.json',{'failed_utc':now(),'error_type':type(e).__name__,'error':str(e),'code_sha256':sha(__file__),'cube_integrity_passed':False,'model_fitted':False,'response_columns_read':[]})
        raise
