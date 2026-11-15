"""30B: complete geometry-only ledger in certified local offsets; no FIRE/QA."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from fractions import Fraction
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import struct
import numpy as np
import shapely
from shapely.geometry import Polygon, GeometryCollection, box
from shapely.ops import unary_union
from shapely.strtree import STRtree
from observation_mesh import build_scan_mesh
from observation_mesh_validation import crop_columns, spacing_transitions, polygon_crosses_transition

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/reviews/evidence/centered-observation-ledger/attempt-01'
TEMP=ROOT/'.runtime/centered-observation-ledger/attempt-01'
GEO=ROOT/'.runtime/observation-mesh-validation'
OLD=ROOT/'docs/reviews/evidence/observation-ownership-ledger'
REF=OLD/'references.json'
CAP=ROOT/'.runtime/study30-cap.json'
PROTOCOL=ROOT/'docs/reviews/2026-11-15-centered-ledger-revalidation-protocol.md'
TOL=1.
MAX_TUPLES=2_000_000
MAX_CANDIDATES=5_000_000
MAX_ATOMS_GROUP=250_000
MAX_ATOMS_TOTAL=2_000_000
MAX_OUTPUT=200*1024*1024
CASES=('2019','2023')
PRODUCTS=(('MYD03','MYD14'),('VNP03IMG','VNP14IMG'))
HELPERS=('observation_mesh.py','observation_mesh_validation.py','observation_ownership_ledger.py')
ACTIVE_ENGINE=None

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def bytehash(value):return hashlib.sha256(value).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def dump(path,value):Path(path).write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
def read_table(path):
    with gzip.open(path,'rt',newline='') as f:return list(csv.DictReader(f))
def table(path,rows,fields):
    with Path(path).open('wb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as zipped:
        with io.TextIOWrapper(zipped,encoding='utf8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)

class Budget:
    def __init__(self):
        self.cap=json.loads(CAP.read_text());self.deadline=datetime.fromisoformat(self.cap['end_utc_B'])
        self.candidates=0;self.atoms=0;self.checks=0
    def checkpoint(self,force=False):
        self.checks+=1
        if force or self.checks%1000==0:
            if datetime.now(timezone.utc)>=self.deadline:raise TimeoutError('30B fixed cap reached')
            if OUT.exists() and sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())>MAX_OUTPUT:raise RuntimeError('output resource_limit')
    def candidate(self):
        self.candidates+=1
        if self.candidates>MAX_CANDIDATES:raise RuntimeError('candidate resource_limit')
        self.checkpoint()

def certify_coordinates(coords,origin,checkpoint=None):
    """Pure exactness check over every scalar and inverse bit pattern."""
    c=np.asarray(coords,dtype=np.float64)
    if c.ndim!=2 or c.shape[1]!=2 or not np.isfinite(c).all():raise ValueError('Only finite 2D coordinates')
    o=np.asarray(origin,dtype=np.float64)
    if o.shape!=(2,) or not np.isfinite(o).all():raise ValueError('Invalid fixed origin')
    local=c-o;back=local+o;failures=0;first=[]
    for i,p in enumerate(c):
        if checkpoint is not None and i%1000==0:checkpoint()
        for axis in range(2):
            if Fraction.from_float(float(p[axis]))-Fraction.from_float(float(o[axis]))!=Fraction.from_float(float(local[i,axis])):
                failures+=1
                if len(first)<10:first.append([i,axis])
    bits_equal=c.view(np.uint64).tobytes()==back.view(np.uint64).tobytes()
    return local,{'passed':failures==0 and bits_equal,'tuples':len(c),'scalar_subtractions':2*len(c),'fraction_failures':failures,
        'first_failures':first,'roundtrip_bits_identical':bits_equal,'world_coordinates_sha256':bytehash(c.tobytes()),'local_coordinates_sha256':bytehash(local.tobytes())}

def assert_close(a,b,label,tolerance=TOL):
    residual=float(a-b)
    if not np.isfinite(residual) or abs(residual)>tolerance:raise ValueError(label+': area closure failed '+str(residual))
    return residual

class GeometryChecks:
    """Checked local set operations; no coordinate modification or repair."""
    def __init__(self,checkpoint=None):self.checkpoint=checkpoint or (lambda:None);self.operations=Counter();self.max_residual=0.;self.last_operation=None
    def valid(self,g,label):
        self.checkpoint()
        if not g.is_valid or not np.isfinite(g.area) or g.area<0 or (not g.is_empty and not np.isfinite(g.bounds).all()):raise ValueError(label+': invalid/nonfinite output')
        return g
    def operation(self,name,p,q):
        self.last_operation=(name,p,q);self.operations[name]+=1;r=self.valid(getattr(p,name)(q),name)
        a,b,c=p.area,q.area,r.area
        if name=='intersection':
            if c>min(a,b)+TOL:raise ValueError('Intersection exceeds operand area')
            if not r.is_empty:
                pb,qb,rb=p.bounds,q.bounds,r.bounds
                if not (rb[0]>=max(pb[0],qb[0]) and rb[1]>=max(pb[1],qb[1]) and rb[2]<=min(pb[2],qb[2]) and rb[3]<=min(pb[3],qb[3])):raise ValueError('Intersection bbox exceeds operands')
            if p.covered_by(q):assert_close(c,a,'containment intersection')
            if p.disjoint(q):assert_close(c,0.,'disjoint intersection')
            if p.relate(q)[0]=='2' and (r.is_empty or shapely.get_dimensions(r)!=2 or c<=0):raise ValueError('Interior predicate vs intersection dimension')
        elif name=='difference':
            if c>a+TOL:raise ValueError('Difference exceeds operand area')
            if q.covers(p):assert_close(c,0.,'containment difference')
            if p.disjoint(q):assert_close(c,a,'disjoint difference')
            if not r.is_empty:
                pb,rb=p.bounds,r.bounds
                if not (rb[0]>=pb[0] and rb[1]>=pb[1] and rb[2]<=pb[2] and rb[3]<=pb[3]):raise ValueError('Difference bbox exceeds operand')
        elif name in {'union','symmetric_difference'}:
            if c>a+b+TOL or (name=='union' and c<max(a,b)-TOL):raise ValueError('Union/symmetric difference area bounds')
            if not r.is_empty:
                inputs=[g.bounds for g in [p,q] if not g.is_empty];rb=r.bounds
                if not (rb[0]>=min(v[0] for v in inputs) and rb[1]>=min(v[1] for v in inputs) and rb[2]<=max(v[2] for v in inputs) and rb[3]<=max(v[3] for v in inputs)):raise ValueError('Union bbox exceeds inputs')
        return r
    def union(self,geometries):
        geometries=list(geometries);self.operations['unary_union']+=1
        result=self.valid(unary_union(geometries),'unary_union')
        if result.area>sum(g.area for g in geometries)+TOL:raise ValueError('Unary union exceeds sum')
        return result
    def overlay(self,p,q):
        ip=self.operation('intersection',p,q);iq=self.operation('intersection',q,p)
        dp=self.operation('difference',p,q);dq=self.operation('difference',q,p)
        up=self.operation('union',p,q);uq=self.operation('union',q,p)
        residuals=[assert_close(p.area,ip.area+dp.area,'partitionP'),assert_close(q.area,iq.area+dq.area,'partitionQ'),
            assert_close(up.area,p.area+q.area-ip.area,'unionPQ'),assert_close(uq.area,p.area+q.area-iq.area,'unionQP'),assert_close(ip.area,iq.area,'intersection order'),assert_close(up.area,uq.area,'union order')]
        for left,right,label in [(ip,iq,'intersection sets'),(up,uq,'union sets'),(p,self.union([ip,dp]),'complement sets')]:
            residuals.append(assert_close(self.operation('symmetric_difference',left,right).area,0.,label))
        self.max_residual=max(self.max_residual,*map(abs,residuals));return ip,dp

def assign_ownership(rows,references,priority,engine):
    grouped=defaultdict(list)
    for r in rows:grouped[r['scan']].append(r)
    unions={s:engine.union(r['polygon'] for r in group) for s,group in grouped.items()}
    for s,group in grouped.items():assert_close(sum(r['polygon'].area for r in group),unions[s].area,'same-scan union')
    unknown=engine.union(u for s,u in unions.items() if references.get(s) is None)
    known=[s for s in grouped if references.get(s) is not None]
    if priority not in {'early','late'}:raise ValueError('Unknown priority')
    known.sort(key=lambda s:((references[s] if priority=='early' else -references[s]),s))
    claimed=GeometryCollection();owned={};unknown_area={}
    for s in known:
        available=engine.operation('difference',engine.operation('difference',unions[s],unknown),claimed)
        for r in grouped[s]:
            k=r['key'];owned[k]=engine.operation('intersection',r['polygon'],available);unknown_area[k]=engine.operation('intersection',r['polygon'],unknown).area
        claimed=engine.operation('union',claimed,engine.operation('difference',unions[s],unknown))
    for s in grouped:
        if references.get(s) is None:
            for r in grouped[s]:owned[r['key']]=None;unknown_area[r['key']]=r['polygon'].area
    union=engine.union(g for g in owned.values() if g is not None);original=engine.union(unions.values())
    residual=assert_close(original.area,union.area+unknown.area,'unknown/identified support')
    sum_residual=assert_close(sum(g.area for g in owned.values() if g is not None),union.area,'sum ownership')
    return owned,unknown_area,union,unknown,{'original_union_m2':original.area,'identified_union_m2':union.area,'unknown_time_union_m2':unknown.area,
        'union_partition_residual_m2':residual,'sum_owned_residual_m2':sum_residual,'scan_order':known,'unknown_scans':sorted(s for s in grouped if references.get(s) is None)}

def polygon_parts(g):
    if g.geom_type=='Polygon':
        if g.area>0:yield g
    elif hasattr(g,'geoms'):
        for p in g.geoms:yield from polygon_parts(p)

def disjoint_check(geometries,engine,budget=None,*,labels=None,records=None):
    gs=[g for g in geometries if g is not None and not g.is_empty];tree=STRtree(gs);overlap=0.;contacts=0;pairs=0
    for i,p in enumerate(gs):
        for j in sorted(map(int,tree.query(p))):
            if j<=i:continue
            if budget:budget.candidate()
            pairs+=1;r=engine.operation('intersection',p,gs[j]);overlap+=r.area;contacts+=r.area==0
            if records is not None:records.append({'left':json.dumps(labels[i] if labels is not None else i),'right':json.dumps(labels[j] if labels is not None else j),'area_m2':r.area,'type':r.geom_type})
            if overlap>TOL:raise ValueError('Owned/atom interiors overlap materially')
    return {'candidate_pairs':pairs,'contact_zero_area_pairs':contacts,'sum_overlap_m2':overlap}

def cross_owned_pairs(left,right,engine,budget=None,max_atoms=MAX_ATOMS_GROUP):
    """All bbox candidates, positive polygon components and zero contacts."""
    tree=STRtree([g for _,g in right]);atoms=[];candidates=[];per_m=defaultdict(float);per_v=defaultdict(float);contacts=0
    for mk,p in left:
        for j in sorted(map(int,tree.query(p))):
            if budget:budget.candidate()
            vk,q=right[j];intersection=engine.operation('intersection',p,q);parts=list(polygon_parts(intersection))
            candidates.append([*mk,*vk,intersection.area,intersection.geom_type,len(parts)])
            if intersection.area==0:contacts+=1
            for component,part in enumerate(parts):
                if budget:budget.atoms+=1
                if len(atoms)>=max_atoms or (budget and budget.atoms>MAX_ATOMS_TOTAL):raise RuntimeError('atom resource_limit')
                atoms.append({'m_row':mk[0],'m_col':mk[1],'v_row':vk[0],'v_col':vk[1],'component':component,'area_m2':part.area,'polygon':part})
                per_m[mk]+=part.area;per_v[vk]+=part.area
    return atoms,candidates,per_m,per_v,contacts

def freeze():
    budget=Budget();budget.checkpoint(True)
    if OUT.exists() or TEMP.exists():raise FileExistsError('30B attempt outputs already exist')
    if shapely.__version__!='2.2.0' or shapely.geos_version_string!='3.14.1':raise ValueError('Unexpected baseline engine')
    old=json.loads((OLD/'initial-freeze.json').read_text())
    for name in HELPERS:
        path=ROOT/'pipeline'/name;expected=old['files']['pipeline/'+name] if name!='observation_ownership_ledger.py' else '058a60986c28efe3b96fb10dbb2fb872e87b2f460e477c65077f784b515ff2d5'
        if digest(path)!=expected:raise ValueError('Frozen helper changed')
    index=json.loads((GEO/'index.json').read_text());public=ROOT/'docs/reviews/evidence/observation-mesh-validation/export-index.json'
    if digest(GEO/'index.json')!=digest(public) or digest(public)!='6cbcf6b06506c22330045119378639eca3f392b8125a72d36fb350dab4421cfb':raise ValueError('Origin/index changed')
    inputs=[GEO/'index.json',public,REF,OLD/'manifest.json',OLD/'geometry-stage.json',OLD/'initial-freeze.json',OLD/'serialization-fix-freeze.json',CAP,PROTOCOL]
    inputs += [ROOT/'pipeline'/name for name in HELPERS]
    for case in CASES:
        for geo,product in PRODUCTS:
            inputs += [OLD/f'{case}-{product}-geometry-states.csv.gz',OLD/f'{case}-{product}-early-geometry.csv.gz']
            for w in index['cases'][case+'_'+geo]['windows']:
                path=GEO/w['npz']
                if digest(path)!=w['sha256']:raise ValueError('NPZ hash mismatch')
                inputs.append(path)
    # Only named, immutable effective inputs are frozen; concurrent30A is excluded.
    inputs += [ROOT/'docs/reviews/evidence/coordinate-origin-diagnostic'/n for n in ['freeze.json','exactness-certificate.json','results.json','manifest.json']]
    OUT.mkdir(parents=True);TEMP.mkdir(parents=True)
    binaries=[Path(shapely.lib.__file__)]+sorted((Path(shapely.__file__).parent/'.dylibs').glob('*.dylib'))
    value={'frozen_utc':now(),'protocol_commit':'97dbd33','code_sha256':digest(__file__),'cap':budget.cap,'origin_xy':index['center_xy'],
        'inputs_sha256':{str(p.relative_to(ROOT)):digest(p) for p in inputs},'binary_sha256':{str(p):digest(p) for p in binaries},'engine':{'Shapely':shapely.__version__,'GEOS':shapely.geos_version_string},
        'coordinate_frame':'local_offsets','parent_crs':'EPSG:32718','overlays_started':False,'fire_or_QA_read':False}
    dump(OUT/'freeze.json',value);shutil.copyfile(__file__,OUT/'code.snapshot.py.txt');shutil.copyfile(PROTOCOL,OUT/'protocol.snapshot.md.txt')
    print(json.dumps({'code_sha256':digest(__file__),'freeze_sha256':digest(OUT/'freeze.json')}))
def verify():
    budget=Budget();budget.checkpoint(True);f=json.loads((OUT/'freeze.json').read_text())
    if digest(__file__)!=f['code_sha256']:raise ValueError('Code freeze changed')
    for path,h in f['inputs_sha256'].items():
        if digest(ROOT/path)!=h:raise ValueError('Input freeze changed: '+path)
    for path,h in f['binary_sha256'].items():
        if digest(path)!=h:raise ValueError('Engine freeze changed')
    return budget,f

def prepare():
    budget,frozen=verify()
    if (OUT/'exactness-certificate.json').exists():raise FileExistsError('Prepared geometry exists')
    index=json.loads((GEO/'index.json').read_text());origin=index['center_xy'];cx,cy=origin
    aoi_world=np.asarray(box(cx-25000,cy-25000,cx+25000,cy+25000).exterior.coords)
    aoi_local,aoi_cert=certify_coordinates(aoi_world,origin,lambda:budget.checkpoint(True))
    certificate={'started_utc':now(),'freeze_sha256':digest(OUT/'freeze.json'),'code_sha256':digest(__file__),'AOI':aoi_cert,'groups':{},'overlays_started':False,'all_passed':aoi_cert['passed'],'total_tuples':len(aoi_world)}
    np.save(OUT/'AOI-local.npy',aoi_local,allow_pickle=False)
    for case in CASES:
        for geo,product in PRODUCTS:
            item=index['cases'][case+'_'+geo];coordinates=[];native=[];full=[];included=[];states=[]
            for w in item['windows']:
                budget.checkpoint(True)
                with np.load(GEO/w['npz'],allow_pickle=False) as data:
                    x,y,valid=data['x'],data['y'],data['valid'];left,right=crop_columns(x,y,origin,40000)
                    x,y,valid=x[:,left:right],y[:,left:right],valid[:,left:right]
                    mesh=build_scan_mesh(x,y,valid,item['rows_per_scan']);gaps=spacing_transitions(x,y,valid)[0] if geo=='VNP03IMG' else None
                    bad=set()
                    for s in mesh['states']:
                        r,c=s['row'],s['col'];state=s['state']
                        if state=='nominal_core_polygon' and gaps is not None and polygon_crosses_transition(gaps,r,c):state='geometry_transition_unresolved';bad.add((r,c))
                        states.append({'row':w['native_row_start']+r,'col':w['native_col_start']+left+c,'state':state})
                    for p in mesh['polygons']:
                        r,c=p['row'],p['col'];coordinates.append(np.asarray(p['polygon'].exterior.coords));full.append(p['polygon'].area)
                        native.append([w['native_row_start']+r,w['native_col_start']+left+c,w['native_scan'],r])
                        included.append((r,c) not in bad and abs(x[r,c]-cx)<=40000 and abs(y[r,c]-cy)<=40000)
            coords=np.asarray(coordinates,dtype=np.float64);native=np.asarray(native,dtype=np.int64);full=np.asarray(full);included=np.asarray(included,dtype=bool)
            original_states={(int(r['row']),int(r['col'])):r['state'] for r in read_table(OLD/f'{case}-{product}-geometry-states.csv.gz')}
            state_map={(r['row'],r['col']):r['state'] for r in states}
            if len(state_map)!=len(states) or state_map!=original_states:raise ValueError('World CORE states/indices changed')
            old_rows=read_table(OLD/f'{case}-{product}-early-geometry.csv.gz');old_bykey={(int(r['row']),int(r['col'])):r for r in old_rows}
            keys=[tuple(r[:2]) for r,keep in zip(native,included) if keep]
            if len(keys)!=len(set(keys)) or set(keys)!=set(old_bykey):raise ValueError('Included native IDs changed')
            full_residuals=[assert_close(area,float(old_bykey[tuple(r[:2])]['area_full_nominal_m2']),'World full area') for r,area,keep in zip(native,full,included) if keep]
            assert_close(sum(full[included]),sum(float(r['area_full_nominal_m2']) for r in old_rows),'World sum full area')
            certificate['total_tuples']+=coords.size//2
            if certificate['total_tuples']>MAX_TUPLES:raise RuntimeError('coordinate resource_limit')
            local,cert=certify_coordinates(coords.reshape(-1,2),origin,lambda:budget.checkpoint(True));local=local.reshape(coords.shape)
            cert.update({'constructed_CORE_polygons':len(coords),'included_polygons':int(included.sum()),'world_index_sha256':bytehash(native.tobytes()),'world_full_area_sha256':bytehash(full.tobytes()),'world_full_area_max_abs_difference_m2':max(map(abs,full_residuals),default=0.),'all_states_and_indices_match24B':True,'structure':'Polygon arrays with five ordered ring coordinates, closure included'})
            if not np.array_equal(local[:,0],local[:,-1]):raise ValueError('Ring closures changed')
            np.savez_compressed(OUT/f'{case}-{product}-local-input.npz',coords=local,native=native,world_full_area=full,included=included)
            table(OUT/f'{case}-{product}-geometry-states.csv.gz',states,['row','col','state'])
            certificate['groups'][case+'_'+product]=cert;certificate['all_passed'] &= cert['passed'];budget.checkpoint(True)
    certificate['completed_utc']=now();certificate['local_files_sha256']={p.name:digest(p) for p in OUT.glob('*-local*')}
    dump(OUT/'exactness-certificate.json',certificate)
    print(json.dumps({'certificate_sha256':digest(OUT/'exactness-certificate.json'),'all_passed':certificate['all_passed'],'tuples':certificate['total_tuples']}))

def run():
    global ACTIVE_ENGINE
    budget,frozen=verify();cert=json.loads((OUT/'exactness-certificate.json').read_text())
    if (OUT/'geometry-result.json').exists():raise FileExistsError('Geometry result exists')
    if not cert['all_passed'] or cert['freeze_sha256']!=digest(OUT/'freeze.json') or cert['code_sha256']!=digest(__file__):raise ValueError('Exactness not accredited')
    for name,h in cert['local_files_sha256'].items():
        if digest(OUT/name)!=h:raise ValueError('Local geometry changed')
    engine=GeometryChecks(lambda:budget.checkpoint());ACTIVE_ENGINE=engine;aoi=Polygon(np.load(OUT/'AOI-local.npy',allow_pickle=False));refs=json.loads(REF.read_text())
    report={'started_utc':now(),'certificate_sha256':digest(OUT/'exactness-certificate.json'),'code_sha256':digest(__file__),'coordinate_frame':'local_offsets','parent_crs':'EPSG:32718','origin_xy':frozen['origin_xy'],'groups':{},'cross':{},'all_geometry_gates_passed':False,'gate1_passed':False,'physical_footprints_verified':False,'pixel_exposure_times_verified':False,'scientific_eligibility_certified':False,'fire_or_QA_read':False}
    for case in CASES:
        products={}
        for geo,product in PRODUCTS:
            with np.load(OUT/f'{case}-{product}-local-input.npz',allow_pickle=False) as d:
                coords,native,full,included=d['coords'],d['native'],d['world_full_area'],d['included']
                rows=[];local_full_sum=0.;old={(int(r['row']),int(r['col'])):r for r in read_table(OLD/f'{case}-{product}-early-geometry.csv.gz')}
                for c,n,area,keep in zip(coords,native,full,included):
                    budget.checkpoint();p=engine.valid(Polygon(c),'local CORE');assert_close(p.area,area,'Local/world full area')
                    if not keep:continue
                    local_full_sum+=p.area
                    clip,_=engine.overlay(p,aoi);key=tuple(map(int,n[:2]));clip_difference=clip.area-float(old[key]['area_AOI_m2'])
                    rows.append({'key':key,'scan':int(n[2]),'detector':int(n[3]),'polygon':clip,'full_area':float(area),'previous_clip_difference_m2':clip_difference})
                products[product]=rows
                assert_close(local_full_sum,sum(float(r['area_full_nominal_m2']) for r in old.values()),'Local/world sum full area')
                by_scan=defaultdict(list)
                for r in rows:
                    if not r['polygon'].is_empty:by_scan[r['scan']].append(r)
                scan_records=[];scan_checks={}
                for scan,group in by_scan.items():scan_checks[str(scan)]=disjoint_check([r['polygon'] for r in group],engine,budget,labels=[r['key'] for r in group],records=scan_records)
                table(OUT/f'{case}-{product}-same-scan-pairs.csv.gz',scan_records,['left','right','area_m2','type'])
                dump(OUT/f'{case}-{product}-same-scan-checks.json',scan_checks)
        for priority in ['early','late']:
            assignments={}
            for geo,product in PRODUCTS:
                reference=dict(enumerate(refs['cases'][case][product]['scan_reference_TAI93']))
                result=assign_ownership(products[product],reference,priority,engine);owned,unknown,union,unknown_union,summary=result
                active=[(k,g) for k,g in owned.items() if g is not None and not g.is_empty];pair_records=[]
                summary['disjointness']=disjoint_check([g for _,g in active],engine,budget,labels=[k for k,_ in active],records=pair_records)
                table(OUT/f'{case}-{product}-{priority}-owner-disjoint-pairs.csv.gz',pair_records,['left','right','area_m2','type'])
                assignments[product]=result;report['groups'][case+'_'+product+'_'+priority]=summary
            um,uv=[assignments[p][2] for p in ['MYD14','VNP14IMG']];common,_=engine.overlay(um,uv)
            by_id={};fragments={}
            for product,other in [('MYD14',uv),('VNP14IMG',um)]:
                own=assignments[product][0];by_id[product]={};parts=[]
                for key,p in own.items():
                    if p is None:by_id[product][key]=None;continue
                    i,d=engine.overlay(p,other);by_id[product][key]=i.area;parts.append(i)
                fragment_union=engine.union(parts);assert_close(sum(p.area for p in parts),common.area,'Sum common vs intersection unions')
                assert_close(fragment_union.area,common.area,'Fragment union vs common');assert_close(engine.operation('symmetric_difference',fragment_union,common).area,0.,'Common union sets')
                fragments[product]=fragment_union
            own_m,own_v=assignments['MYD14'][0],assignments['VNP14IMG'][0]
            left=[(k,g) for k,g in own_m.items() if g is not None and not g.is_empty];right=[(k,g) for k,g in own_v.items() if g is not None and not g.is_empty]
            atoms,candidate_rows,per_m,per_v,contacts=cross_owned_pairs(left,right,engine,budget)
            atom_union=engine.union(r['polygon'] for r in atoms);sum_atoms=sum(r['area_m2'] for r in atoms)
            atom_residual=assert_close(sum_atoms,common.area,'Atom sum vs common');assert_close(atom_union.area,common.area,'Atom union vs common')
            assert_close(engine.operation('symmetric_difference',atom_union,common).area,0.,'Atom union common sets')
            for product,per in [('MYD14',per_m),('VNP14IMG',per_v)]:
                for key,area in by_id[product].items():
                    if area is not None:assert_close(per.get(key,0.),area,'Per-native-ID expressions')
            atom_pair_records=[];atom_disjoint=disjoint_check((r['polygon'] for r in atoms),engine,budget,records=atom_pair_records)
            prefix=f'{case}-{priority}'
            table(OUT/f'{prefix}-atom-disjoint-pairs.csv.gz',atom_pair_records,['left','right','area_m2','type'])
            table(OUT/f'{prefix}-candidates.csv.gz',({'m_row':r[0],'m_col':r[1],'v_row':r[2],'v_col':r[3],'area_m2':r[4],'type':r[5],'atom_components':r[6]} for r in candidate_rows),['m_row','m_col','v_row','v_col','area_m2','type','atom_components'])
            table(OUT/f'{prefix}-atoms.csv.gz',({**{k:v for k,v in r.items() if k!='polygon'},'WKB_local_hex':r['polygon'].wkb_hex} for r in atoms),['m_row','m_col','v_row','v_col','component','area_m2','WKB_local_hex'])
            for geo,product in PRODUCTS:
                own,unknown,union,unknown_union,summary=assignments[product];ledger=[]
                for r in products[product]:
                    key=r['key'];p=own[key];area_common=by_id[product][key];owned_area=None if p is None else p.area;excluded=None if p is None else r['polygon'].area-unknown[key]-owned_area
                    if p is not None:assert_close(r['polygon'].area,unknown[key]+excluded+owned_area,'Native partition')
                    ledger.append({'case':case,'product':product,'priority':priority,'row':key[0],'col':key[1],'scan':r['scan'],'detector':r['detector'],'area_full_nominal_m2':r['full_area'],'area_AOI_m2':r['polygon'].area,'area_AOI_difference_24B_m2':r['previous_clip_difference_m2'],'area_time_unidentified_m2':unknown[key],'area_owned_m2':owned_area,'area_excluded_by_priority_m2':excluded,'area_common_m2':area_common,'area_owned_not_common_m2':None if p is None else owned_area-area_common,'WKB_owned_local_hex':None if p is None else p.wkb_hex})
                table(OUT/f'{case}-{product}-{priority}-geometry.csv.gz',ledger,list(ledger[0]))
            previous_common=json.loads((OLD/'geometry-stage.json').read_text())['cases'][case]['MYD14_'+priority]['common_nominal_union_m2']
            report['cross'][prefix]={'common_m2':common.area,'previous24B_common_m2':previous_common,'common_difference_24B_m2':common.area-previous_common,'atom_sum_m2':sum_atoms,'atom_union_m2':atom_union.area,'atom_sum_residual_m2':atom_residual,'cross_candidates':len(candidate_rows),'zero_area_contacts':contacts,'atoms':len(atoms),'atom_disjointness':atom_disjoint,'both_expressions_passed':True,'common_WKB_local_hex':common.wkb_hex}
            dump(OUT/'progress.json',{'completed_cross':list(report['cross']),'candidates_total':budget.candidates,'atoms_total':budget.atoms,'fire_or_QA_read':False});budget.checkpoint(True)
    report.update(completed_utc=now(),all_geometry_gates_passed=True,operations=dict(engine.operations),max_operation_identity_residual_m2=engine.max_residual,candidates_total=budget.candidates,atoms_total=budget.atoms,QA_replay_executed=False)
    dump(OUT/'geometry-result.json',report)
    dump(OUT/'manifest.json',{'files':{p.name:{'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='manifest.json'},'all_geometry_gates_passed':True,'gate1_passed':False})
    budget.checkpoint(True);print(json.dumps({'all_geometry_gates_passed':True,'atoms':budget.atoms,'candidates':budget.candidates,'QA_replay_executed':False}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['freeze','prepare','run']);args=parser.parse_args()
    try:{'freeze':freeze,'prepare':prepare,'run':run}[args.stage]()
    except Exception as exc:
        if OUT.exists():dump(OUT/f'failure-{args.stage}.json',{'failed_utc':now(),'stage':args.stage,'error_type':type(exc).__name__,'error':str(exc),'code_sha256':digest(__file__),'gate1_passed':False,'all_geometry_gates_passed':False,'QA_replay_executed':False})
        if OUT.exists() and ACTIVE_ENGINE is not None and ACTIVE_ENGINE.last_operation is not None:
            name,p,q=ACTIVE_ENGINE.last_operation
            for label,g in [('p',p),('q',q)]:
                with (OUT/f'last-operation-{label}.wkb.gz').open('wb') as f,gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as z:z.write(g.wkb)
            dump(OUT/'last-operation-context.json',{'operation':name,'not_necessarily_cause':True,'operations':dict(ACTIVE_ENGINE.operations)})
        raise
