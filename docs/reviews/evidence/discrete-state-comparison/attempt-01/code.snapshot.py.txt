"""33: frozen nominal point owners enriched by native ID; no geometry/refit."""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math,resource,shutil,sys
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from observation_qa import decode_mask
from observation_native_qa import local_screen

ROOT=Path(__file__).resolve().parents[1]
GEO=ROOT/'docs/reviews/evidence/point-ownership-audit/attempt-01'
OLD=ROOT/'docs/reviews/evidence/observation-ownership-ledger'
NATIVE=ROOT/'.runtime/observation-ownership-ledger'
OUT=ROOT/'docs/reviews/evidence/discrete-state-comparison/attempt-01'
PROTOCOL=ROOT/'docs/reviews/2026-11-15-discrete-state-comparison-protocol.md'
REF=OLD/'references.json'
START='2026-11-15T06:48:00+00:00';END='2026-11-15T07:48:00+00:00'
CASES=('2019','2023');PRODUCTS=('MYD14','VNP14IMG');VERSIONS={'MYD14':'061','VNP14IMG':'002'}
ALLOW=('case','product','row','col','mask_class','algorithm_QA','geographic_flag','surface','screen_sensitivity_state','screen_exclusion_reasons','screen_unresolved_reasons','M13_non_nominal')
CAT_ALLOW=ALLOW+('scope',)
NINE=('00','10','01','11','0U','1U','U0','U1','UU')
GEO_STATES=('identified_owner','boundary_unidentified','time_unidentified','same_scan_ambiguous','no_nominal_support')
ACTIVE_BUDGET=None

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def dump(path,obj):Path(path).write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n')
def csv_write(path,rows,fields):
    with Path(path).open('wb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as z:
        with io.TextIOWrapper(z,encoding='utf8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
def csv_projection(path,columns):
    """Tokenize CSV bytes, immediately retain only fixed native columns.

    Non-allowlisted field strings are transient parser tokens, never interpreted
    numerically/semantically or retained; protocol pre-data amendment755b68e.
    """
    with gzip.open(path,'rt',newline='') as f:
        reader=csv.reader(f);header=next(reader)
        if len(header)!=len(set(header)) or any(c not in header for c in columns):raise ValueError('Schema incompatible with fixed allowlist')
        indices=[header.index(c) for c in columns]
        for values in reader:
            if len(values)!=len(header):raise ValueError('Malformed native CSV row')
            yield {name:values[i] for name,i in zip(columns,indices)}
def parse_int(value,maximum,nullable=True):
    if value=='':
        if nullable:return None
        raise ValueError('Missing native index')
    if not value.isdigit():raise ValueError('Non-integer native scalar')
    n=int(value)
    if not 0<=n<=maximum:raise ValueError('Native scalar outside field range')
    return n
def parse_record(raw,case,product,shape):
    if raw['case']!=case or raw['product']!=product:raise ValueError('Native case/product mismatch')
    result=dict(raw)
    for name,maximum,nullable in [('row',shape[0]-1,False),('col',shape[1]-1,False),('mask_class',255,True),('algorithm_QA',2**32-1,True),('geographic_flag',255,True)]:result[name]=parse_int(raw[name],maximum,nullable)
    b=raw['M13_non_nominal']
    if b not in {'True','False',''}:raise ValueError('Unknown exported M13 boolean')
    result['M13_non_nominal']=None if b=='' else b=='True'
    if product=='VNP14IMG' and result['algorithm_QA'] is not None and result['M13_non_nominal'] is not None and result['M13_non_nominal']!=bool(result['algorithm_QA']&(1<<6)):raise ValueError('M13 export contradicts raw algorithm bit')
    if product=='MYD14' and result['M13_non_nominal'] is True:raise ValueError('M13 not applicable to MODIS')
    return result
def native_key(record):return record['row'],record['col']
def base_state(product,mask):
    if mask is None:return 'U','native_mask_null'
    m=decode_mask(product,VERSIONS[product],mask)
    if m['detection']:return '1','registered_detection'
    if m['no_detection']:return '0',m['classification']
    return 'U',m['classification']
def normalized_surface(raw):
    if raw in {'land','land_mask_class5'}:return 'land'
    if raw in {'water','water_mask_class3'}:return 'water'
    if raw=='coast':return 'coast'
    return 'unknown'
def surface_pair(a,b):
    if 'unknown' in {a,b}:return 'surface_unknown'
    if 'coast' in {a,b}:return 'coast'
    return 'land_land' if a==b=='land' else ('water_water' if a==b=='water' else 'land_water_conflict')
def inspect_qa(product,record):
    missing=[name for name in ['mask_class','algorithm_QA','geographic_flag'] if record[name] is None]
    if product=='VNP14IMG' and record['M13_non_nominal'] is None:missing.append('M13_non_nominal')
    expected=None
    if not any(record[k] is None for k in ['mask_class','algorithm_QA','geographic_flag']):expected=local_screen(product,VERSIONS[product],record['mask_class'],record['algorithm_QA'],record['geographic_flag'])
    excluded=record['screen_exclusion_reasons'].split('|') if record['screen_exclusion_reasons'] else []
    unresolved=record['screen_unresolved_reasons'].split('|') if record['screen_unresolved_reasons'] else []
    verified=expected is not None and expected['state']==record['screen_sensitivity_state'] and expected['excluded']==excluded and expected['unresolved']==unresolved
    causes=[]
    known_exclusion=verified and bool(excluded)
    m13=record['M13_non_nominal'] if product=='VNP14IMG' else 'not_applicable'
    if known_exclusion:causes+=excluded
    if m13 is True:causes.append('M13_non_nominal')
    incomplete=['missing_'+k for k in missing]
    if not verified:incomplete.append('screen_not_verified_against_frozen_decoder')
    if record['screen_sensitivity_state']=='unresolved':incomplete+=unresolved or ['screen_unresolved_missing_cause']
    if known_exclusion or m13 is True:status='non_nominal'
    elif missing or not verified or record['screen_sensitivity_state']!='local_candidate' or unresolved:status='unknown'
    else:status='nominal_in_inspected_fields'
    return {'qa_status':status,'qa_causes':'|'.join(causes),'qa_incompleteness':'|'.join(incomplete),'screen_verified':verified,'M13':m13}
def qa_pair(a,b):
    return 'some_non_nominal' if 'non_nominal' in {a,b} else ('QA_unknown' if 'unknown' in {a,b} else 'both_nominal_in_inspected_fields')
def enrich_native(product,record):
    state,reason=base_state(product,record['mask_class']);qa=inspect_qa(product,record);surface=normalized_surface(record['surface'])
    provenance='MYD14_algorithm_QA_surface_bits0_1_via24B_export' if product=='MYD14' else ('24B_surface_geo_land_water_branch_by_frozen_source_policy' if record['surface'] in {'land','water','coast'} else '24B_export_geo_unknown_or_native_mask_fallback')
    return {**record,'basic_state':state,'basic_reason':reason,**qa,'surface_normalized':surface,'surface_provenance':provenance}
def summarize_nine(counts):
    nine={k:int(counts.get(k,0)) for k in NINE};n=sum(nine.values());five={k:nine[k] for k in NINE[:4]};five['U']=sum(nine[k] for k in NINE[4:]);den=nine['11']+nine['10']+nine['01']
    if sum(five.values())!=n:raise ValueError('Five/nine partition mismatch')
    return {'Ntotal':n,'nine':nine,'five':five,'fractions_total':{k:(v/n if n else None) for k,v in nine.items()},'Nknown':sum(nine[k] for k in NINE[:4]),'n1U':nine['1U'],'nU1':nine['U1'],'Jaccard_known':nine['11']/den if den else None,'Jaccard_denominator':den,'Jaccard_null_reason':None if den else 'no_known_positive_union'}
def retention_category(has_quad,included,strict,owned):
    if not has_quad:return 'quad_unavailable_geometry_null'
    if not included:return 'quad_outside32A_universe'
    if strict==0:return 'included_quad_without_strict_interior_query'
    if owned==0:return 'strict_interior_present_without_ownership'
    return 'represented_owner'

class Budget:
    def __init__(self):self.rows=0;self.joins=0;self.roster_rows=0;self.retention_rows=0;self.calls=0;self.peak=0
    def check(self,force=False):
        self.calls+=1
        if force or self.calls%1000==0:
            if datetime.now(timezone.utc)>=datetime.fromisoformat(END):raise TimeoutError('33 fixed cap reached')
            rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024);self.peak=max(self.peak,rss)
            if rss>2*1024**3:raise RuntimeError('RSS resource_limit')
            if OUT.exists() and sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())>200*1024**2:raise RuntimeError('output resource_limit')
    def join(self,n=1):
        self.joins+=n
        if self.joins>2_000_000:raise RuntimeError('native joins resource_limit')
        self.check()
    def row(self,n=1):
        self.rows+=n
        if self.rows>1_000_000:raise RuntimeError('final rows resource_limit')
        self.check()

def universal_ids(g):
    return {tuple(map(int,n[:2])) for n,keep in zip(g['native'],g['included']) if keep}
def validate_universal(records,expected):
    if set(records)!=expected:raise ValueError('Expected included/universal native ID missing or unexpected; no catalogue fallback')

def freeze():
    budget=Budget();budget.check(True)
    if OUT.exists():raise FileExistsError('33 attempt already exists')
    gm=json.loads((GEO/'manifest.json').read_text());gs=json.loads((GEO/'summary.json').read_text());raw=json.loads((OLD/'raw-stage.json').read_text());oldmanifest=json.loads((OLD/'manifest.json').read_text())
    if not gm['all_GEO_gates_passed'] or not gs['all_GEO_gates_passed'] or gs['queries_total']!=198804:raise ValueError('32A scope/gates incompatible')
    inputs=[PROTOCOL,GEO/'manifest.json',OLD/'manifest.json',OLD/'raw-stage.json',REF,ROOT/'pipeline/observation_qa.py',ROOT/'pipeline/observation_native_qa.py',ROOT/'pipeline/observation_ownership_ledger.py',ROOT/'tests/test_discrete_state_comparison.py']
    for name,item in gm['files'].items():
        p=GEO/name
        if digest(p)!=item['sha256']:raise ValueError('32A file changed')
        inputs.append(p)
    schemas={}
    for case in CASES:
        for product in PRODUCTS:
            info=raw['cases'][case][product]
            for role,suffix in [('labels','labels'),('positives','all-positive-originals')]:
                p=NATIVE/f'{case}-{product}-{suffix}.csv.gz';expected=info['labels_sha256' if role=='labels' else 'positives_sha256']
                if digest(p)!=expected:raise ValueError('Native raw export hash mismatch')
                with gzip.open(p,'rt',newline='') as f:header=next(csv.reader(f))
                required=ALLOW if role=='labels' else CAT_ALLOW
                if any(c not in header for c in required):raise ValueError('Missing allowlisted native schema')
                schemas[str(p.relative_to(ROOT))]={'header':header,'projected_columns':required,'version':VERSIONS[product],'raw_file_sha256':info['input_sha256'][product],'shape':info['shape']};inputs.append(p)
            for priority in ['early','late']:
                p=OLD/f'{case}-{product}-{priority}-ledger.csv.gz'
                if digest(p)!=oldmanifest['files'][p.name]['sha256']:raise ValueError('Public native projection hash mismatch')
                with gzip.open(p,'rt',newline='') as f:header=next(csv.reader(f))
                if any(c not in header for c in ALLOW):raise ValueError('Public native projection schema missing')
                inputs.append(p)
    native_rows=sum(raw['cases'][c][p]['labels'] for c in CASES for p in PRODUCTS);catalogue=sum(raw['cases'][c][p]['original_positive_records_granule'] for c in CASES for p in PRODUCTS)
    roster_rows=4*sum(v['constructed_quads'] for v in json.loads((GEO/'geometry-certificate.json').read_text())['groups'].values());point_rows=2*gs['queries_total'];retention_rows=8*catalogue
    conservative_rows=point_rows+native_rows+roster_rows+retention_rows+catalogue
    if point_rows!=397608 or conservative_rows>1_000_000:raise ValueError('Preflight output domain outside cap')
    OUT.mkdir(parents=True)
    source_initial=json.loads((OLD/'initial-freeze.json').read_text())
    for name in ['observation_qa.py','observation_native_qa.py']:
        if digest(ROOT/'pipeline'/name)!=source_initial['files']['pipeline/'+name]:raise ValueError('Decoder changed since native export')
    if digest(ROOT/'pipeline/observation_ownership_ledger.py')!='058a60986c28efe3b96fb10dbb2fb872e87b2f460e477c65077f784b515ff2d5':raise ValueError('Native export source policy changed')
    inputs.append(OLD/'initial-freeze.json')
    dump(OUT/'freeze.json',{'frozen_utc':now(),'protocol_commit':'c6b5285','protocol_predata_amendment_commit':'755b68e','code_sha256':digest(__file__),'inputs_sha256':{str(p.relative_to(ROOT)):digest(p) for p in inputs},'schemas':schemas,'cap':{'start':START,'end':END},'preflight':{'point_rows':point_rows,'native_rows':native_rows,'roster_rows':roster_rows,'retention_rows':retention_rows,'catalogue_projection_rows':catalogue,'all_final_rows_upper_bound':conservative_rows,'point_native_joins':2*point_rows,'all_native_joins_upper_bound':2*point_rows+roster_rows+2*native_rows+catalogue+retention_rows},'QA_mapping':'protocol33; frozen local_screen verified against raw fields; nonnominal priority, unknown, inspected nominal','labels_values_read':False,'area_columns_retained_or_used':False,'CSV_tokenization':'nonallowlisted tokens transiently discarded without semantic/numeric interpretation','unit':'etiqueta nativa del quad nominal asignado al punto de consulta'})
    for source,name in [(Path(__file__),'code.snapshot.py.txt'),(PROTOCOL,'protocol.snapshot.md.txt'),(ROOT/'tests/test_discrete_state_comparison.py','tests.snapshot.py.txt')]:shutil.copyfile(source,OUT/name)
    print(json.dumps({'code_sha256':digest(__file__),'freeze_sha256':digest(OUT/'freeze.json'),'point_rows':point_rows,'all_rows_upper_bound':conservative_rows}))
def verify(budget=None):
    global ACTIVE_BUDGET
    budget=budget or Budget();budget.check(True);ACTIVE_BUDGET=budget;f=json.loads((OUT/'freeze.json').read_text())
    if digest(__file__)!=f['code_sha256']:raise ValueError('Code changed after freeze')
    for name,h in f['inputs_sha256'].items():
        if digest(ROOT/name)!=h:raise ValueError('Protected source changed: '+name)
    return budget,f

def load_native(case,product,g,info,budget):
    records={};shape=info['shape']
    for raw in csv_projection(NATIVE/f'{case}-{product}-labels.csv.gz',ALLOW):
        record=parse_record(raw,case,product,shape);key=native_key(record)
        if key in records:raise ValueError('Duplicate universal native ID')
        records[key]=record
    validate_universal(records,universal_ids(g))
    for priority in ['early','late']:
        seen=set()
        for raw in csv_projection(OLD/f'{case}-{product}-{priority}-ledger.csv.gz',ALLOW):
            record=parse_record(raw,case,product,shape);key=native_key(record);budget.join()
            if key in seen or records.get(key)!=record:raise ValueError('Conflicting native projection across policies')
            seen.add(key)
        if seen!=set(records):raise ValueError('Incomplete native projection across policies')
    for key in records:records[key]=enrich_native(product,records[key])
    csv_write(OUT/f'{case}-{product}-universal-native.csv.gz',records.values(),ALLOW);budget.row(len(records))
    return records

def load_geo(case,product,phase,step):
    prefix=f'{case}-{product}-phase{phase}-h{step}'
    with np.load(GEO/(prefix+'-points.npz'),allow_pickle=False) as f:g={k:f[k] for k in f.files}
    with np.load(GEO/(prefix+'-postings.npz'),allow_pickle=False) as f:postings=f['postings']
    n=len(g['states'])
    if g['causes'].shape!=(n,4) or g['roster'].shape!=(len(g['native']),5):raise ValueError('GEO shape contract changed')
    for key in ['owner_early_quad','owner_late_quad']:
        own=g[key]
        if own.shape!=(n,) or np.any(own < -1) or np.any(own>=len(g['native'])) or not np.array_equal(own>=0,g['states']==0):raise ValueError('Invalid GEO owner/sentinel')
        if not np.all(g['included'][own[own>=0]]):raise ValueError('Owner outside frozen included universe')
    for column,relation in [(0,None),(1,1),(2,0)]:
        q=postings[:,1] if relation is None else postings[postings[:,2]==relation,1]
        if not np.array_equal(np.bincount(q,minlength=len(g['native'])),g['roster'][:,column]):raise ValueError('Roster strict interior/boundary/candidates mismatch')
    for column,key in [(3,'owner_early_quad'),(4,'owner_late_quad')]:
        own=g[key];own=own[own>=0]
        if not np.array_equal(np.bincount(own,minlength=len(g['native'])),g['roster'][:,column]):raise ValueError('Roster ownership mismatch')
    return g
def geo_row(case,phase,step,priority,pid,m,v,refs):
    row={'case':case,'phase_m':phase,'step_m':step,'priority':priority,'point_id':pid}
    for prefix,product,g in [('m','MYD14',m),('v','VNP14IMG',v)]:
        qi=int(g['owner_'+priority+'_quad'][pid]);row[prefix+'_quad_index']=qi;row[prefix+'_GEO_state']=int(g['states'][pid]);row[prefix+'_GEO_causes']=''.join('1' if x else '0' for x in g['causes'][pid])
        native=None if qi<0 else g['native'][qi];scan=None if native is None else int(native[2]);row[prefix+'_row']=None if native is None else int(native[0]);row[prefix+'_col']=None if native is None else int(native[1]);row[prefix+'_scan']=scan
        reference=refs['cases'][case][product];keys=['EV start time','EV center time'] if product=='MYD14' else ['scan_start_time','scan_end_time','ev_mid_time']
        for key in keys:row[prefix+'_'+key.replace(' ','_')]=None if scan is None else reference['fields'][key][scan]
    a,b=row['m_EV_center_time'],row['v_ev_mid_time'];row['scan_reference_delta_V_minus_M_s']=None if a is None or b is None else b-a;row['scan_reference_delta_reason']='no_unique_owner_or_reference' if a is None or b is None else 'scan_reference_only_not_pixel_exposure'
    return row
def label_fields(prefix,product,record,geo_state,global_flag):
    if record is None:
        return {prefix+'_state':'U',prefix+'_state_reason':'geometry_'+GEO_STATES[geo_state],prefix+'_mask':None,prefix+'_algorithm_QA':None,prefix+'_geographic_flag':None,prefix+'_surface_native':None,prefix+'_surface':'unknown',prefix+'_surface_provenance':'no_unique_owner',prefix+'_QA_status':'unknown',prefix+'_QA_causes':'no_unique_owner',prefix+'_QA_incompleteness':'no_unique_owner',prefix+'_M13':'not_applicable' if product=='MYD14' else None,prefix+'_screen':None,prefix+'_screen_excluded':None,prefix+'_screen_unresolved':None,prefix+'_global_flag':global_flag}
    return {prefix+'_state':record['basic_state'],prefix+'_state_reason':record['basic_reason'],prefix+'_mask':record['mask_class'],prefix+'_algorithm_QA':record['algorithm_QA'],prefix+'_geographic_flag':record['geographic_flag'],prefix+'_surface_native':record['surface'],prefix+'_surface':record['surface_normalized'],prefix+'_surface_provenance':record['surface_provenance'],prefix+'_QA_status':record['qa_status'],prefix+'_QA_causes':record['qa_causes'],prefix+'_QA_incompleteness':record['qa_incompleteness'],prefix+'_M13':record['M13'],prefix+'_screen':record['screen_sensitivity_state'],prefix+'_screen_excluded':record['screen_exclusion_reasons'],prefix+'_screen_unresolved':record['screen_unresolved_reasons'],prefix+'_global_flag':global_flag}
def point_row(geo,mrecord,vrecord,flags):
    row={**geo,**label_fields('m','MYD14',mrecord,geo['m_GEO_state'],flags[0]),**label_fields('v','VNP14IMG',vrecord,geo['v_GEO_state'],flags[1])}
    row['joint_state']=row['m_state']+row['v_state'];row['QA_pair_tier']=qa_pair(row['m_QA_status'],row['v_QA_status']);row['surface_pair']=surface_pair(row['m_surface'],row['v_surface'])
    return row
def hash_row(hasher,row,fields):hasher.update((json.dumps([row[k] for k in fields],separators=(',',':'),allow_nan=False)+'\n').encode())

def run():
    budget,frozen=verify()
    if (OUT/'summary.json').exists():raise FileExistsError('33 output already exists')
    raw=json.loads((OLD/'raw-stage.json').read_text());refs=json.loads(REF.read_text());summary={'scenarios':{},'native_retention':{},'nested':{},'unit':frozen['unit'],'all_structural_gates_passed':False,'gate1_passed':False,'continuous30B_repaired':False,'primary':'each case: phase0,h250,early','HDF_or_new_data_read':False,'time_reference_metadata':{'source_REF_sha256':digest(REF),'delta_definition':'VIIRS ev_mid_time minus MODIS EV center time; seconds on documented common TAI93 scale','epoch_and_scale':'TAI seconds since1993-01-01; original units/attributes preserved below','validity':'source finite ordered scan references, fill excluded; owner selection frozen32A','pixel_exposure_verified':False,'source_attributes':{c:{p:refs['cases'][c][p]['attributes'] for p in PRODUCTS} for c in CASES}},'native_source_metadata':{c:{p:{'version':VERSIONS[p],'raw_file_sha256':raw['cases'][c][p]['input_sha256'][p],'shape':raw['cases'][c][p]['shape'],'original_labels_sha256':raw['cases'][c][p]['labels_sha256'],'original_catalogue_sha256':raw['cases'][c][p]['positives_sha256']} for p in PRODUCTS} for c in CASES},'surface_provenance_limit':'Preserves24B exports and frozen conditional source code; GEO field not reinspected and raw land_water value was not exported.'};native={};geo_cache={}
    for case in CASES:
        for product in PRODUCTS:
            g=load_geo(case,product,0,250);native[case,product]=load_native(case,product,g,raw['cases'][case][product],budget)
    comparison_arrays={}
    for case in CASES:
        for phase in [0,125]:
            for step in [250,500]:
                m,v=[load_geo(case,p,phase,step) for p in PRODUCTS];geo_cache[case,phase,step,'MYD14']=m;geo_cache[case,phase,step,'VNP14IMG']=v
                count=len(m['states'])
                if len(v['states'])!=count:raise ValueError('GEO cohorts differ between instruments')
                for product,g in [('MYD14',m),('VNP14IMG',v)]:
                    records=native[case,product];roster_rows=[]
                    for qi,n in enumerate(g['native']):
                        budget.join();key=tuple(map(int,n[:2]));record=records.get(key)
                        if bool(g['included'][qi]) and record is None:raise ValueError('Expected native roster label missing')
                        roster_rows.append({'quad_index':qi,'row':key[0],'col':key[1],'scan':int(n[2]),'included':bool(g['included'][qi]),'strict_interior_points':int(g['roster'][qi,1]),'boundary_points':int(g['roster'][qi,2]),'owned_early_points':int(g['roster'][qi,3]),'owned_late_points':int(g['roster'][qi,4]),'mask_class':None if record is None else record['mask_class'],'label_scope':'outside_exported_universe' if record is None else 'universal_native_export'})
                    csv_write(OUT/f'{case}-{product}-phase{phase}-h{step}-native-roster.csv.gz',roster_rows,list(roster_rows[0]));budget.row(len(roster_rows));budget.roster_rows+=len(roster_rows)
                for priority in ['early','late']:
                    name=f'{case}-phase{phase}-h{step}-{priority}';geo_fields=list(geo_row(case,phase,step,priority,0,m,v,refs));before=hashlib.sha256();after=hashlib.sha256()
                    for pid in range(count):hash_row(before,geo_row(case,phase,step,priority,pid,m,v,refs),geo_fields)
                    nine=Counter();tiers=defaultdict(Counter);surfaces=defaultdict(Counter);unknown=defaultdict(Counter);signatures=[];flags=[raw['cases'][case][p]['global_quality_flag'] for p in PRODUCTS]
                    def rows():
                        for pid in range(count):
                            geo=geo_row(case,phase,step,priority,pid,m,v,refs);records=[]
                            for prefix,product in [('m','MYD14'),('v','VNP14IMG')]:
                                budget.join();key=None if geo[prefix+'_quad_index']<0 else (geo[prefix+'_row'],geo[prefix+'_col']);record=None if key is None else native[case,product].get(key)
                                if key is not None and record is None:raise ValueError('Expected native owner label missing; no U fallback')
                                records.append(record)
                            row=point_row(geo,*records,flags);hash_row(after,row,geo_fields);nine[row['joint_state']]+=1;tiers[row['QA_pair_tier']][row['joint_state']]+=1;surfaces[row['surface_pair']][row['joint_state']]+=1
                            for prefix in ['m','v']:
                                if row[prefix+'_state']=='U':unknown[prefix][row[prefix+'_state_reason']]+=1
                                if row[prefix+'_mask'] in {7,8,9} and row[prefix+'_state']!='1':raise ValueError('Positive erased by QA')
                            signatures.append(hashlib.sha256(json.dumps([row[k] for k in row if k not in {'step_m','point_id'}],sort_keys=False,allow_nan=False).encode()).digest())
                            budget.row();yield row
                    sample=point_row(geo_row(case,phase,step,priority,0,m,v,refs),None,None,flags)
                    csv_write(OUT/(name+'-points.csv.gz'),rows(),list(sample));comparison_arrays[case,phase,step,priority]=signatures
                    if before.digest()!=after.digest():raise ValueError('GEO projection changed by enrichment')
                    result=summarize_nine(nine)
                    if result['Ntotal']!=count or sum(sum(x.values()) for x in tiers.values())!=count or sum(sum(x.values()) for x in surfaces.values())!=count:raise ValueError('Scenario partition mismatch')
                    summary['scenarios'][name]={**result,'GEO_before_sha256':before.hexdigest(),'GEO_after_sha256':after.hexdigest(),'QA_tiers':{k:summarize_nine(c) for k,c in tiers.items()},'surface_strata':{k:summarize_nine(c) for k,c in surfaces.items()},'unknown_causes':{k:dict(c) for k,c in unknown.items()},'global_quality_flags':dict(zip(PRODUCTS,flags))}
            for priority in ['early','late']:
                fine=comparison_arrays[case,phase,250,priority];coarse=comparison_arrays[case,phase,500,priority];lo250=(-25000-phase)//250+1;lo500=(-25000-phase)//500+1;n250=199 if phase==0 else 200;n500=99 if phase==0 else 100;checked=0
                for j in range(lo500,lo500+n500):
                    for k in range(lo500,lo500+n500):
                        a=(2*j-lo250)*n250+(2*k-lo250);b=(j-lo500)*n500+(k-lo500)
                        if fine[a]!=coarse[b]:raise ValueError('Independent nested state/QA/surface/time mismatch')
                        checked+=1
                summary['nested'][f'{case}-phase{phase}-{priority}']={'checked_points':checked,'all_fields_identical_except_step_and_local_point_id':True}
    # Catalogue is read only after universal replay; never supplies point labels.
    for case in CASES:
        for product in PRODUCTS:
            info=raw['cases'][case][product];positive={}
            for rawrow in csv_projection(NATIVE/f'{case}-{product}-all-positive-originals.csv.gz',CAT_ALLOW):
                record=parse_record(rawrow,case,product,info['shape']);key=native_key(record)
                if key in positive or record['mask_class'] not in {7,8,9}:raise ValueError('Positive catalogue identity/state invalid')
                if record['scope'] not in {'centre_AOI','centre_halo15','outside_halo15','geographically_unassignable'}:raise ValueError('Unknown native catalogue scope')
                budget.join();canonical=native[case,product].get(key)
                if canonical is not None and any(record[c]!=canonical[c] for c in ALLOW):raise ValueError('Catalogue conflicts with universal native export')
                positive[key]=record
            if len(positive)!=info['original_positive_records_granule']:raise ValueError('Positive catalogue incomplete')
            csv_write(OUT/f'{case}-{product}-positive-catalogue-projection.csv.gz',positive.values(),CAT_ALLOW);budget.row(len(positive))
            summary['native_retention'][case+'_'+product]={}
            for phase in [0,125]:
                for step in [250,500]:
                    g=geo_cache[case,phase,step,product];lookup={tuple(map(int,n[:2])):i for i,n in enumerate(g['native'])}
                    for priority,column in [('early',3),('late',4)]:
                        records=[];counts=Counter();scopes=defaultdict(Counter)
                        for key,p in positive.items():
                            budget.join();qi=lookup.get(key);included=False if qi is None else bool(g['included'][qi]);strict=None if qi is None else int(g['roster'][qi,1]);boundary=None if qi is None else int(g['roster'][qi,2]);owned=None if qi is None else int(g['roster'][qi,column]);category=retention_category(qi is not None,included,strict,owned)
                            row={**{c:p[c] for c in CAT_ALLOW},'phase_m':phase,'step_m':step,'priority':priority,'quad_index':qi,'geometry_missing_null':qi is None,'included':included,'strict_interior_points':strict,'boundary_points':boundary,'owned_points':owned,'retention_category':category};records.append(row);counts[category]+=1;scopes[p['scope']][category]+=1
                        csv_write(OUT/f'{case}-{product}-phase{phase}-h{step}-{priority}-positive-retention.csv.gz',records,list(records[0]));budget.row(len(records));budget.retention_rows+=len(records)
                        summary['native_retention'][case+'_'+product][f'phase{phase}-h{step}-{priority}']={'native_positive_records':len(records),'partition':dict(counts),'scopes':{k:dict(v) for k,v in scopes.items()},'preproperty_unit':'STRICT_INTERIOR incidence; no bbox candidate retention'}
    point_rows=sum(v['Ntotal'] for v in summary['scenarios'].values())
    if len(summary['scenarios'])!=16 or point_rows!=397608:raise ValueError('Final fixed cohort size mismatch')
    verify(budget);budget.check(True);summary.update(completed_utc=now(),all_structural_gates_passed=True,point_rows=point_rows,all_final_data_rows=budget.rows,native_joins=budget.joins,roster_rows=budget.roster_rows,retention_rows=budget.retention_rows,peak_RSS_bytes=budget.peak,RSS_platform=sys.platform,QA_surface_policy='frozen native screen+raw fields; VIIRS surface export preserved with conditional historical provenance; not pure instrumental QA',area_columns_retained_or_used=False,positive_catalogue_used_for_backfill=False,offline_export_scope='Tracked allowlist universal/catalogue projections permit independent verification; original driver still requires frozen local sources and absolute cap, not unrestricted offline replay')
    dump(OUT/'summary.json',summary);dump(OUT/'manifest.json',{'files':{p.name:{'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='manifest.json'},'all_structural_gates_passed':True,'gate1_passed':False})
    print(json.dumps({'all_structural_gates_passed':True,'point_rows':point_rows,'all_final_rows':budget.rows,'native_joins':budget.joins,'peak_RSS_bytes':budget.peak}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['freeze','run']);args=p.parse_args()
    try:{'freeze':freeze,'run':run}[args.stage]()
    except Exception as exc:
        if OUT.exists():dump(OUT/f'failure-{args.stage}.json',{'failed_utc':now(),'error_type':type(exc).__name__,'error':str(exc),'code_sha256':digest(__file__),'all_structural_gates_passed':False,'gate1_passed':False,'counters':None if ACTIVE_BUDGET is None else {'rows':ACTIVE_BUDGET.rows,'joins':ACTIVE_BUDGET.joins,'peak_RSS_bytes':ACTIVE_BUDGET.peak}})
        raise
