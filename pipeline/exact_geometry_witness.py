"""30A: exact local intersection witnesses, stdlib only; never physical truth."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import gzip
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'docs/reviews/evidence/coordinate-origin-diagnostic'
OUT=ROOT/'docs/reviews/evidence/exact-geometry-witness'
PROTOCOL=ROOT/'docs/reviews/2026-11-15-exact-witness-protocol.md'
DESIGN=ROOT/'docs/reviews/2026-11-15-exact-witness-design.md'
CAP=ROOT/'.runtime/study30-cap.json'
PAIRS=('MYD14_early-818-1166','MYD14_late-833-1149','MYD14_late-844-1161','VNP14IMG_early-2051-3869','VNP14IMG_early-2076-3864')
MAX_BYTES=50*1024*1024

class LimitReached(RuntimeError):pass

class Budget:
    def __init__(self,max_segments=2_000_000,max_coordinates=2_000_000,check=None):
        self.max_segments=max_segments;self.max_coordinates=max_coordinates;self.segments=0;self.coordinates=0;self.check=check
    def segment(self):
        if self.segments>=self.max_segments:raise LimitReached('segment_evaluation_limit')
        self.segments+=1
        if self.check and self.segments%256==0:self.check()
    def coords(self,n):
        if n>self.max_coordinates-self.coordinates:raise LimitReached('coordinate_tuple_limit')
        self.coordinates+=n
        if self.check:self.check()

def rational(x):return {'numerator':x.numerator,'denominator':x.denominator}
def point_json(p):return [rational(v) for v in p]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def segments(ring):return zip(ring[:-1],ring[1:])

def parse_wkb(blob,budget=None):
    """Return polygons→rings→exact points. Reject unsupported layouts, never repair."""
    budget=budget or Budget();offset=0
    if len(blob)>MAX_BYTES:raise LimitReached('WKB_byte_limit')
    def unpack(fmt):
        nonlocal offset
        size=struct.calcsize(fmt)
        if offset+size>len(blob):raise ValueError('truncated_WKB')
        r=struct.unpack_from(fmt,blob,offset);offset+=size;return r
    def geometry(only_polygon=False):
        order=unpack('B')[0]
        if order not in (0,1):raise ValueError('byte_order')
        endian='<' if order else '>';kind=unpack(endian+'I')[0]
        if kind==3:
            nr=unpack(endian+'I')[0]
            if nr>budget.max_coordinates:raise LimitReached('ring_count_limit')
            rings=[]
            for _ in range(nr):
                n=unpack(endian+'I')[0]
                if n<4:raise ValueError('short_ring')
                budget.coords(n)
                if offset+16*n>len(blob):raise ValueError('truncated_coordinates')
                points=[]
                for _ in range(n):
                    x,y=unpack(endian+'dd')
                    if not(math.isfinite(x) and math.isfinite(y)):raise ValueError('nonfinite_coordinate')
                    points.append((F.from_float(x),F.from_float(y)))
                if points[0]!=points[-1]:raise ValueError('open_ring')
                rings.append(tuple(points))
            return [tuple(rings)] if rings else []
        if kind==6 and not only_polygon:
            n=unpack(endian+'I')[0]
            if n>budget.max_coordinates:raise LimitReached('component_count_limit')
            result=[]
            for _ in range(n):result.extend(geometry(True))
            return result
        raise ValueError('unsupported_type_or_dimension')
    result=geometry()
    if offset!=len(blob):raise ValueError('trailing_WKB_bytes')
    return tuple(result)

def ring_relation(c,ring,budget):
    inside=False
    for a,b in segments(ring):
        budget.segment();dx=b[0]-a[0];dy=b[1]-a[1];vx=c[0]-a[0];vy=c[1]-a[1]
        if dx*vy-dy*vx==0 and min(a[0],b[0])<=c[0]<=max(a[0],b[0]) and min(a[1],b[1])<=c[1]<=max(a[1],b[1]):
            return 'boundary'
        if (a[1]>c[1])!=(b[1]>c[1]):
            crossing=a[0]+(c[1]-a[1])*dx/dy
            if crossing>c[0]:inside=not inside
    return 'inside' if inside else 'outside'

def strict_inside(c,polygons,budget=None):
    budget=budget or Budget();included=False;relations=[]
    for poly in polygons:
        values=[ring_relation(c,r,budget) for r in poly];relations.append(values)
        if 'boundary' in values:return False,relations
        included |= values[0]=='inside' and all(v=='outside' for v in values[1:])
    return included,relations

def segment_distance_squared(c,a,b):
    dx=b[0]-a[0];dy=b[1]-a[1];vx=c[0]-a[0];vy=c[1]-a[1];length=dx*dx+dy*dy;dot=vx*dx+vy*dy
    if length==0 or dot<=0:return vx*vx+vy*vy
    if dot>=length:return (c[0]-b[0])**2+(c[1]-b[1])**2
    return (dx*vy-dy*vx)**2/length

def minimum_distance(c,p,q,budget):
    best=None;owner=None
    for role,polys in [('p',p),('q',q)]:
        for pi,poly in enumerate(polys):
            for ri,ring in enumerate(poly):
                for si,(a,b) in enumerate(segments(ring)):
                    budget.segment();d=segment_distance_squared(c,a,b)
                    if best is None or d<best:best=d;owner={'operand':role,'polygon':pi,'ring':ri,'segment':si,'a':point_json(a),'b':point_json(b)}
    return best,owner

def candidates(p,q):
    for role,polys in [('p',p),('q',q)]:
        for pi,poly in enumerate(polys):
            v=poly[0][:-1];n=len(v)
            yield (sum(x for x,y in v)/n,sum(y for x,y in v)/n),{'operand':role,'polygon':pi,'kind':'exterior_mean'}
            for i in range(min(16,n)):
                tri=[v[(i+j)%n] for j in range(3)]
                yield (sum(x for x,y in tri)/3,sum(y for x,y in tri)/3),{'operand':role,'polygon':pi,'kind':'consecutive_triangle_mean','first_vertex':i}

def dyadic_square(c,delta):
    if delta is None or delta<=0:return None
    for k in range(257):
        h=F(1,2**k)
        if 2*h*h<delta:
            return {'k':k,'h':rational(h),'lower_area_m2':rational(4*h*h),
                'center':point_json(c),'minimum_boundary_distance_squared':rational(delta),
                'strict_inequality_verified':True,'corners':[point_json((c[0]+sx*h,c[1]+sy*h)) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]}
    return None

def find_witness(p,q,budget=None):
    budget=budget or Budget();attempts=[];truncated=False
    for index,(c,source) in enumerate(candidates(p,q)):
        if index>=128:truncated=True;break
        a,ar=strict_inside(c,p,budget);b,br=strict_inside(c,q,budget)
        item={'index':index,'source':source,'center':point_json(c),'strict_inside_p':a,'strict_inside_q':b}
        attempts.append(item)
        if not(a and b):continue
        d,nearest=minimum_distance(c,p,q,budget);square=dyadic_square(c,d)
        if square is None:item['rejection']='dyadic_depth_limit';continue
        return {'status':'certified_witness','candidate_index':index,'attempts':attempts,'square':square,'nearest_boundary':nearest,'inside_relations_p':ar,'inside_relations_q':br,'search_truncated':False}
    return {'status':'no_witness_in_fixed_search','attempts':attempts,'search_truncated':truncated,'does_not_prove_no_overlap':True}

def compare_area(value,lower):
    if value is None or not math.isfinite(value):return {'status':'not_comparable'}
    a=F.from_float(float(value));margin=lower-a
    return {'reported_area_float':value,'reported_area_exact':rational(a),'status':'refuted_below_exact_lower_bound' if a<lower else 'not_refuted_NOT_validated','bound_minus_reported_exact':rational(margin)}

def cap_check():
    c=json.loads(CAP.read_text())
    if datetime.now(timezone.utc)>=datetime.fromisoformat(c['end_utc_A']):raise LimitReached('absolute_UTC_cap')

def write(path,value):
    b=(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    size=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file()) if OUT.exists() else 0
    if size+len(b)>MAX_BYTES:raise LimitReached('output_byte_limit')
    Path(path).write_bytes(b)

def freeze():
    cap_check()
    if OUT.exists():raise FileExistsError('evidence already exists')
    manifest=json.loads((SOURCE/'manifest.json').read_text());OUT.mkdir(parents=True)
    inputs=[]
    for name in PAIRS:
        for role in ['pixel','other_union']:
            file=name+'-'+role+'.wkb.gz'
            if digest(SOURCE/file)!=manifest['files'][file]['sha256']:raise ValueError('source WKB hash mismatch')
            shutil.copyfile(SOURCE/file,OUT/file);inputs.append(file)
    for p,name in [(Path(__file__),'code.snapshot.py.txt'),(ROOT/'tests/test_exact_geometry_witness.py','tests.snapshot.py.txt'),(PROTOCOL,'protocol.snapshot.md.txt'),(DESIGN,'design.snapshot.md.txt'),(CAP,'cap.snapshot.json')]:shutil.copyfile(p,OUT/name)
    write(OUT/'freeze.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),'protocol_commit':'97dbd33',
        'code_sha256':digest(__file__),'tests_sha256':digest(ROOT/'tests/test_exact_geometry_witness.py'),
        'protocol_sha256':digest(PROTOCOL),'design_sha256':digest(DESIGN),'cap_sha256':digest(CAP),
        'source29_manifest_sha256':digest(SOURCE/'manifest.json'),'results29_sha256':digest(SOURCE/'results.json'),
        'inputs':inputs,'files_sha256':{p.name:digest(p) for p in OUT.iterdir() if p.is_file()},
        'tests_passed_before_real':True,'search_started':False,'GEOS_oracle':False})
    print('FREEZE',digest(OUT/'freeze.json'),flush=True)

def run():
    cap_check();freeze_data=json.loads((OUT/'freeze.json').read_text())
    if (OUT/'search.json').exists() or (OUT/'results.json').exists():raise FileExistsError('results exist')
    for path,key in [(Path(__file__),'code_sha256'),(PROTOCOL,'protocol_sha256'),(DESIGN,'design_sha256'),(CAP,'cap_sha256')]:
        if digest(path)!=freeze_data[key]:raise ValueError('frozen code/protocol/cap changed')
    for n,h in freeze_data['files_sha256'].items():
        if digest(OUT/n)!=h:raise ValueError('frozen input changed: '+n)
    budget=Budget(check=cap_check);rows=[];exhausted=False
    for name in PAIRS:
        if exhausted:rows.append({'id':name,'status':'not_evaluated_resource_limit'});continue
        try:
            parsed=[]
            for role in ['pixel','other_union']:
                path=OUT/(name+'-'+role+'.wkb.gz')
                with gzip.open(path,'rb') as f:blob=f.read(MAX_BYTES+1)
                if len(blob)>MAX_BYTES:raise LimitReached('uncompressed_WKB_byte_limit')
                parsed.append(parse_wkb(blob,budget))
            result=find_witness(*parsed,budget);rows.append({'id':name,**result})
        except LimitReached as exc:
            rows.append({'id':name,'status':'resource_limit','reason':str(exc)});exhausted=True
        except (ValueError,OverflowError,struct.error) as exc:rows.append({'id':name,'status':'not_applicable_parser','reason':str(exc)})
    # Persist search before interpreting any stored overlay area.
    write(OUT/'search.json',{'completed_utc':datetime.now(timezone.utc).isoformat(),'rows':rows,'segment_evaluations':budget.segments,'coordinate_tuples':budget.coordinates,'area29_read':False,'GEOS_oracle':False})
    if digest(SOURCE/'results.json')!=freeze_data['results29_sha256']:raise ValueError('results29 changed')
    previous=json.loads((SOURCE/'results.json').read_text())
    for row in rows:
        if row['status']!='certified_witness':row['area_comparisons']={'status':'not_comparable_no_witness'};continue
        z=row['square']['lower_area_m2'];lower=F(z['numerator'],z['denominator']);comparisons={}
        for stage,key in [('original','original'),('centered','centered')]:
            old=next(x for x in previous[key] if x['id']==row['id'])
            for order in ['pq','qp']:comparisons[stage+'_'+order]=compare_area(old['intersection_'+order]['area_m2'],lower)
        row['area_comparisons']=comparisons
    write(OUT/'results.json',{'completed_utc':datetime.now(timezone.utc).isoformat(),'freeze_sha256':digest(OUT/'freeze.json'),'search_sha256':digest(OUT/'search.json'),
        'rows':rows,'segment_evaluations':budget.segments,'coordinate_tuples':budget.coordinates,'GEOS_oracle':False,'full_area_oracle':False,'gate1_passed':False,'physical_truth':False,'all_five_preserved':len(rows)==5})
    write(OUT/'manifest.json',{'files':{p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in OUT.iterdir() if p.is_file() and p.name!='manifest.json'},'no_previous_files_modified':True})
    print('DONE',[(r['id'],r['status']) for r in rows],flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['freeze','run']);args=parser.parse_args();{'freeze':freeze,'run':run}[args.stage]()
