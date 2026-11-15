"""29: exact fixed-origin translation, same WKB and GEOS3.14.1 expressions."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import gzip
import hashlib
import inspect
import json
from pathlib import Path
import shutil
import struct
import numpy as np
import shapely
import geometry_engine_diagnostic as previous

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'docs/reviews/evidence/geometry-engine-diagnostic'
INDEX=ROOT/'docs/reviews/evidence/observation-mesh-validation/export-index.json'
PROTOCOL=ROOT/'docs/reviews/2026-11-15-coordinate-origin-diagnostic-protocol.md'
CAP=ROOT/'.runtime/coordinate-origin-cap.json'
OUT=ROOT/'docs/reviews/evidence/coordinate-origin-diagnostic'
MAX_COORDS=2_000_000
MAX_OUTPUT=50*1024*1024

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def check_cap():
    cap=json.loads(CAP.read_text())
    if datetime.now(timezone.utc)>=datetime.fromisoformat(cap['end_utc']): raise TimeoutError('29 fixed cap reached')
    if OUT.exists() and sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())>MAX_OUTPUT: raise RuntimeError('output resource_limit')
def write(path,value):
    check_cap();Path(path).write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
def raw(path):
    b=Path(path).read_bytes();return gzip.decompress(b) if str(path).endswith('.gz') else b
def signature(g):
    if g.geom_type=='Polygon':return ['Polygon',len(g.exterior.coords),[len(r.coords) for r in g.interiors]]
    if hasattr(g,'geoms'):return [g.geom_type,[signature(p) for p in g.geoms]]
    return [g.geom_type,len(g.coords)]
def bits(coords):return np.asarray(coords,dtype=np.float64).view(np.uint64).tobytes()
def translate_certified(g,origin):
    """Certifies every coordinate, retaining all rings/parts/order; no overlay."""
    c=np.asarray(shapely.get_coordinates(g),dtype=np.float64)
    if shapely.get_coordinate_dimension(g)!=2 or shapely.has_z(g) or shapely.has_m(g) or not np.isfinite(c).all():
        return None,{'passed':False,'reason':'nonfinite_or_not_2D','coordinates':len(c)}
    o=np.asarray(origin,dtype=np.float64)
    translated=c-o;restored=translated+o
    failures=[];count=0
    for i,p in enumerate(c):
        if i%1000==0:check_cap()
        for axis in range(2):
            exact=Fraction.from_float(float(p[axis]))-Fraction.from_float(float(o[axis]))
            if exact!=Fraction.from_float(float(translated[i,axis])):
                count+=1
                if len(failures)<10:failures.append({'coordinate':i,'axis':axis,'reason':'subtraction_not_exact'})
    out=shapely.set_coordinates(g,translated)
    back=shapely.set_coordinates(out,restored)
    roundtrip=bits(restored)==bits(c)
    structure=signature(out)==signature(g) and signature(back)==signature(g)
    order=np.array_equal(shapely.get_coordinates(out),translated) and bits(shapely.get_coordinates(back))==bits(c)
    passed=count==0 and roundtrip and structure and order
    return out,{'passed':passed,'coordinates':len(c),'scalar_subtractions_tested':2*len(c),'fraction_failures':count,
        'first_failures':failures,'roundtrip_bits_identical':roundtrip,'structure_identical':structure,'order_and_closures_preserved':order,
        'original_coordinate_sha256':hashlib.sha256(bits(c)).hexdigest(),'translated_coordinate_sha256':hashlib.sha256(bits(translated)).hexdigest(),
        'original_signature':signature(g),'translated_signature':signature(out)}

def freeze():
    check_cap()
    if OUT.exists():raise FileExistsError('29 outputs already exist')
    source_manifest=json.loads((SOURCE/'manifest.json').read_text())
    index_manifest=json.loads((INDEX.parent/'manifest.json').read_text())
    if digest(INDEX)!=index_manifest['files'][INDEX.name]['sha256']:raise ValueError('unfrozen origin index')
    fixtures=json.loads((SOURCE/'fixtures.json').read_text())
    if [i['id'] for i in fixtures[:5]]!=list(previous.PAIRS) or len(fixtures)!=9:raise ValueError('unexpected fixtures')
    if shapely.__version__!='2.2.0' or shapely.geos_version_string!='3.14.1':raise ValueError('engine differs from protocol')
    OUT.mkdir(parents=True)
    for item in fixtures:
        for role in ['pixel','other_union']:
            name=item[role]
            if digest(SOURCE/name)!=source_manifest['files'][name]['sha256']:raise ValueError('source fixture changed')
            shutil.copyfile(SOURCE/name,OUT/name)
    origin=json.loads(INDEX.read_text())['center_xy']
    origin_record={'origin_xy':origin,'float_hex':[float(v).hex() for v in origin],'float64_bytes_hex':struct.pack('<dd',*origin).hex(),
        'source_index_sha256':digest(INDEX),'AOI_half_side_m':25000.,'AOI_CRS':'EPSG:32718'}
    # Rectangle construction is not overlay; use exactly the native AOI expression.
    cx,cy=origin;aoi=shapely.geometry.box(cx-25000,cy-25000,cx+25000,cy+25000)
    (OUT/'AOI.wkb').write_bytes(shapely.to_wkb(aoi))
    write(OUT/'origin.json',origin_record);write(OUT/'fixtures.json',fixtures)
    for source,name in [(Path(__file__),'code.snapshot.py.txt'),(PROTOCOL,'protocol.snapshot.md.txt'),(CAP,'cap.snapshot.json'),(SOURCE/'baseline-shapely.json','baseline27.snapshot.json'),(ROOT/'pipeline/geometry_engine_diagnostic.py','metrics-helper.snapshot.py.txt')]:shutil.copyfile(source,OUT/name)
    binaries=[Path(shapely.lib.__file__)]+sorted((Path(shapely.__file__).parent/'.dylibs').glob('*.dylib'))
    write(OUT/'freeze.json',{'frozen_utc':now(),'protocol_commit':'9f324a4','code_sha256':digest(__file__),'protocol_sha256':digest(PROTOCOL),'cap_sha256':digest(CAP),
        'metrics_helper_sha256':digest(previous.__file__),'finish_metrics_source_sha256':hashlib.sha256(inspect.getsource(previous.finish_metrics).encode()).hexdigest(),
        'source_manifest_sha256':digest(SOURCE/'manifest.json'),'engine':{'shapely':shapely.__version__,'GEOS':shapely.geos_version_string,'binary_sha256':{str(p):digest(p) for p in binaries}},
        'files_sha256':{p.name:digest(p) for p in sorted(OUT.iterdir()) if p.is_file()},'original_27_cap_not_used':True,
        'scope':'Pure finish_metrics reused; worker/run/DEADLINE of27 never invoked; cap29 checked separately','overlays_started':False})
    print(json.dumps({'code_sha256':digest(__file__),'freeze_sha256':digest(OUT/'freeze.json'),'origin_sha256':digest(OUT/'origin.json')}))
def verify():
    check_cap();f=json.loads((OUT/'freeze.json').read_text())
    if digest(__file__)!=f['code_sha256'] or digest(PROTOCOL)!=f['protocol_sha256'] or digest(CAP)!=f['cap_sha256'] or digest(previous.__file__)!=f['metrics_helper_sha256']:raise ValueError('freeze changed')
    for name,h in f['files_sha256'].items():
        if digest(OUT/name)!=h:raise ValueError('input changed: '+name)
    for name,h in f['engine']['binary_sha256'].items():
        if digest(name)!=h:raise ValueError('engine binary changed')
def certify():
    verify()
    if (OUT/'exactness-certificate.json').exists():raise FileExistsError('certificate exists')
    origin=json.loads((OUT/'origin.json').read_text())['origin_xy'];fixtures=json.loads((OUT/'fixtures.json').read_text());entries={};count=0
    names=sorted({i[r] for i in fixtures for r in ['pixel','other_union']})+['AOI.wkb']
    for name in names:
        g=shapely.from_wkb(raw(OUT/name));count+=len(shapely.get_coordinates(g))
        if count>MAX_COORDS:raise RuntimeError('coordinate resource_limit')
        shifted,record=translate_certified(g,origin);record['input_WKB_sha256']=hashlib.sha256(raw(OUT/name)).hexdigest()
        if shifted is not None:
            b=shapely.to_wkb(shifted);target='centered-'+name.removesuffix('.gz')
            (OUT/target).write_bytes(b);record['translated_WKB']=target;record['translated_WKB_sha256']=digest(OUT/target)
        entries[name]=record
    certificate={'completed_utc':now(),'code_sha256':digest(__file__),'freeze_sha256':digest(OUT/'freeze.json'),'total_coordinate_tuples_with_multiplicity':count,
        'all_passed':all(r['passed'] for r in entries.values()),'entries':entries,'translated_overlays_started':False,'gate1_passed':False}
    write(OUT/'exactness-certificate.json',certificate);print(json.dumps({'certificate_sha256':digest(OUT/'exactness-certificate.json'),'all_passed':certificate['all_passed'],'coordinate_tuples':count}))
def info(g):return {'area_m2':g.area,'type':g.geom_type,'valid':g.is_valid}
def evaluate(item,p,q,wkb_hashes):
    row={**item,'wkb_sha256':wkb_hashes,'p':info(p),'q':info(q)}
    extra={};finite=True;bounds=True;bboxes=True
    for suffix,left,right in [('pq',p,q),('qp',q,p)]:
        row['within_'+suffix]=left.within(right);row['covered_by_'+suffix]=left.covered_by(right)
        for name in ['intersection','difference','union']:
            check_cap();result=getattr(left,name)(right);row[name+'_'+suffix]=info(result)
            finite &= bool(np.isfinite(result.area) and (result.is_empty or np.isfinite(result.bounds).all()))
            if name=='intersection':
                bounds &= -1<=result.area<=min(left.area,right.area)+1
                if not result.is_empty:
                    lb,rb,ib=left.bounds,right.bounds,result.bounds
                    bboxes &= bool(ib[0]>=max(lb[0],rb[0]) and ib[1]>=max(lb[1],rb[1]) and ib[2]<=min(lb[2],rb[2]) and ib[3]<=min(lb[3],rb[3]))
            extra[name+'_'+suffix]={'bounds':None if result.is_empty else list(result.bounds),'dimension':int(shapely.get_dimensions(result)),'empty':result.is_empty}
    row=previous.finish_metrics(row)
    return row,{'outputs':extra,'finite_outputs':finite,'intersection_area_bounds_within_1m2':bounds,'intersection_bbox_exact_bounds':bboxes,'all_required_pass':bool(row['regression_checks_pass'] and finite and bounds and bboxes and row.get('control_expected_areas_pass',True))}
def run():
    verify()
    if (OUT/'results.json').exists():raise FileExistsError('results exist')
    cert=json.loads((OUT/'exactness-certificate.json').read_text())
    if not cert['all_passed']:raise ValueError('exactness gate failed; no overlays allowed')
    for name,r in cert['entries'].items():
        if digest(OUT/r['translated_WKB'])!=r['translated_WKB_sha256']:raise ValueError('translated WKB changed')
    fixtures=json.loads((OUT/'fixtures.json').read_text());baseline=json.loads((OUT/'baseline27.snapshot.json').read_text());original=[];centered=[];details=[]
    for item,expected in zip(fixtures,baseline['rows']):
        if item['id']!=expected['id']:raise ValueError('baseline fixture order differs')
        blobs={r:raw(OUT/item[r]) for r in ['pixel','other_union']};hashes={r:hashlib.sha256(b).hexdigest() for r,b in blobs.items()}
        a,ae=evaluate(item,*[shapely.from_wkb(blobs[r]) for r in ['pixel','other_union']],hashes)
        if a!=expected:raise ValueError('baseline27 not reproduced: '+item['id'])
        original.append(a)
        translated={r:cert['entries'][item[r]]['translated_WKB'] for r in ['pixel','other_union']}
        b,be=evaluate(item,*[shapely.from_wkb((OUT/translated[r]).read_bytes()) for r in ['pixel','other_union']],{r:digest(OUT/translated[r]) for r in translated})
        centered.append(b)
        area_differences={r:b[r]['area_m2']-a[r]['area_m2'] for r in ['p','q']}
        details.append({'id':item['id'],'baseline':ae,'centered':be,'input_area_differences_m2':area_differences,'input_area_invariance_within_1m2':all(abs(v)<=1 for v in area_differences.values())})
    result={'completed_utc':now(),'certificate_sha256':digest(OUT/'exactness-certificate.json'),'baseline27_reproduced_all9':True,'original':original,'centered':centered,'extended_checks':details,
        'all_centered_regression_checks_pass':all(d['centered']['all_required_pass'] and d['input_area_invariance_within_1m2'] for d in details),'selected_regressions':5,'controls':4,
        'same_engine':{'Shapely':shapely.__version__,'GEOS':shapely.geos_version_string},'fire_or_QA_read':False,'gate1_passed':False,'full_ledger_validated':False,'physical_exposure_verified':False}
    write(OUT/'results.json',result)
    write(OUT/'manifest.json',{'files':{p.name:{'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='manifest.json'},'gate1_passed':False})
    print(json.dumps({'all_centered_checks_pass':result['all_centered_regression_checks_pass'],'summary':[(r['id'],r['regression_checks_pass']) for r in centered]}))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['freeze','certify','run']);args=parser.parse_args();{'freeze':freeze,'certify':certify,'run':run}[args.stage]()
