"""32B: bounded convex rational clipping; no GEOS, QA, repair or global claim."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import struct
from exact_geometry_witness import parse_wkb,Budget as ParseBudget

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'docs/reviews/evidence/centered-observation-ledger/attempt-01'
OUT=ROOT/'docs/reviews/evidence/exact-local-overlay-audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-15-exact-local-overlay-protocol.md'
CAP=ROOT/'.runtime/study32-cap.json'
INPUTS=('last-operation-p.wkb.gz','last-operation-q.wkb.gz','last-operation-context.json')
MAX_OUTPUT=50*1024*1024

class ResourceLimit(RuntimeError):pass
class DomainUnknown(ValueError):pass

class Budget:
    def __init__(self,max_operations=2_000_000,max_bits=4096,max_vertices=1024,check=None):
        self.operations=0;self.max_operations=max_operations;self.max_bits=max_bits;self.max_vertices=max_vertices;self.check=check
    def guard(self,x):
        x=F(x)
        if max(abs(x.numerator).bit_length(),x.denominator.bit_length())>self.max_bits:raise ResourceLimit('rational_bit_limit')
        return x
    def tick(self):
        if self.operations>=self.max_operations:raise ResourceLimit('exact_operation_limit')
        self.operations+=1
        if self.check and self.operations%256==0:self.check()
    def add(self,a,b):self.tick();return self.guard(a+b)
    def sub(self,a,b):self.tick();return self.guard(a-b)
    def mul(self,a,b):self.tick();return self.guard(a*b)
    def div(self,a,b):
        self.tick()
        if b==0:raise DomainUnknown('zero_denominator_in_clipping')
        return self.guard(a/b)
    def vertices(self,v):
        if len(v)>self.max_vertices:raise ResourceLimit('intermediate_vertex_limit')

def rational(x):return {'numerator':x.numerator,'denominator':x.denominator}
def vertices_json(v):return [[rational(x),rational(y)] for x,y in v]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cross(a,b,c,budget):
    dx=budget.sub(b[0],a[0]);dy=budget.sub(b[1],a[1]);vx=budget.sub(c[0],a[0]);vy=budget.sub(c[1],a[1])
    return budget.sub(budget.mul(dx,vy),budget.mul(dy,vx))
def signed_area2(v,budget):
    total=F(0)
    for a,b in zip(v,v[1:]+v[:1]):total=budget.add(total,budget.sub(budget.mul(a[0],b[1]),budget.mul(a[1],b[0])))
    return total

def on_segment(p,a,b,budget):
    return cross(a,b,p,budget)==0 and min(a[0],b[0])<=p[0]<=max(a[0],b[0]) and min(a[1],b[1])<=p[1]<=max(a[1],b[1])
def intersect_segments(a,b,c,d,budget):
    o1=cross(a,b,c,budget);o2=cross(a,b,d,budget);o3=cross(c,d,a,budget);o4=cross(c,d,b,budget)
    if o1==0 and min(a[0],b[0])<=c[0]<=max(a[0],b[0]) and min(a[1],b[1])<=c[1]<=max(a[1],b[1]):return True
    if o2==0 and min(a[0],b[0])<=d[0]<=max(a[0],b[0]) and min(a[1],b[1])<=d[1]<=max(a[1],b[1]):return True
    if o3==0 and min(c[0],d[0])<=a[0]<=max(c[0],d[0]) and min(c[1],d[1])<=a[1]<=max(c[1],d[1]):return True
    if o4==0 and min(c[0],d[0])<=b[0]<=max(c[0],d[0]) and min(c[1],d[1])<=b[1]<=max(c[1],d[1]):return True
    return (o1>0)!=(o2>0) and (o3>0)!=(o4>0) and o1!=0 and o2!=0 and o3!=0 and o4!=0

def certify_polygon(vertices,budget=None):
    budget=budget or Budget();v=tuple(tuple(budget.guard(x) for x in p) for p in vertices);n=len(v)
    if n<3 or n>256:raise DomainUnknown('vertex_count_outside_3_to_256')
    if len(set(v))!=n:raise DomainUnknown('duplicate_vertex')
    area2=signed_area2(v,budget)
    if area2==0:raise DomainUnknown('zero_exact_area')
    for i in range(n):
        a,b,c=v[i-1],v[i],v[(i+1)%n]
        turn=cross(a,b,c,budget)
        if turn==0:
            dot=budget.add(budget.mul(budget.sub(b[0],a[0]),budget.sub(c[0],b[0])),budget.mul(budget.sub(b[1],a[1]),budget.sub(c[1],b[1])))
            if dot<=0:raise DomainUnknown('adjacent_collinear_backtracking')
    pairs=0
    for i in range(n):
        for j in range(i+1,n):
            if j==i+1 or (i==0 and j==n-1):continue
            pairs+=1
            if intersect_segments(v[i],v[(i+1)%n],v[j],v[(j+1)%n],budget):raise DomainUnknown('nonadjacent_segments_intersect')
    orientation=1 if area2>0 else -1
    for i in range(n):
        turn=cross(v[i-1],v[i],v[(i+1)%n],budget)
        if (orientation>0 and turn<0) or (orientation<0 and turn>0):raise DomainUnknown('nonconvex')
    normalized=v if orientation==1 else tuple(reversed(v))
    return normalized,{'vertices':n,'nonadjacent_pairs_checked':pairs,'simple':True,'convex':True,'area_exact':rational(budget.div(abs(area2),2)),'source_signed_area2':rational(area2),'reversed_to_CCW':orientation<0,'source_vertices':vertices_json(v)}

def parse_operand(blob,budget):
    if len(blob)>10*1024*1024:raise ResourceLimit('input_byte_limit')
    if len(blob)<13:raise DomainUnknown('truncated_WKB')
    flag=blob[0]
    if flag not in (0,1):raise DomainUnknown('invalid_byte_order')
    e='<' if flag else '>';kind,rings,n=struct.unpack_from(e+'III',blob,1)
    if kind!=3:raise DomainUnknown('not_2D_Polygon')
    if rings!=1:raise DomainUnknown('holes_or_empty_polygon_outside_domain')
    if n<4 or n>257:raise DomainUnknown('stored_vertex_count_outside_domain')
    parsed=parse_wkb(blob,ParseBudget(max_coordinates=257))
    if len(parsed)!=1 or len(parsed[0])!=1:raise DomainUnknown('not_single_polygon_ring')
    return certify_polygon(parsed[0][0][:-1],budget)

def dedup_consecutive(v):
    result=[]
    for p in v:
        if not result or p!=result[-1]:result.append(p)
    if len(result)>1 and result[0]==result[-1]:result.pop()
    return tuple(result)

def clip(subject,clipper,budget=None):
    """CCW convex inputs; exact boundary-inclusive Sutherland–Hodgman."""
    budget=budget or Budget();output=tuple(subject);steps=[]
    for ai,a in enumerate(clipper):
        b=clipper[(ai+1)%len(clipper)];incoming=output;result=[]
        if not incoming:steps.append({'clip_edge':ai,'vertices':0});continue
        s=incoming[-1];ds=cross(a,b,s,budget)
        for point in incoming:
            de=cross(a,b,point,budget);sin=ds>=0;ein=de>=0
            if sin!=ein:
                t=budget.div(ds,budget.sub(ds,de))
                at=(budget.add(s[0],budget.mul(t,budget.sub(point[0],s[0]))),budget.add(s[1],budget.mul(t,budget.sub(point[1],s[1]))))
                result.append(at);budget.vertices(result)
            if ein:result.append(point);budget.vertices(result)
            s=point;ds=de
        output=dedup_consecutive(result);budget.vertices(output);steps.append({'clip_edge':ai,'vertices':len(output)})
    area=budget.div(abs(signed_area2(output,budget)),2) if output else F(0)
    return output,area,steps

def adjudicate(p,q,budget=None):
    budget=budget or Budget();a,ac=certify_polygon(p,budget);b,bc=certify_polygon(q,budget)
    v,area,steps=clip(a,b,budget);w,other,reverse=clip(b,a,budget)
    if area!=other:raise ArithmeticError('exact_area_order_identity_failed')
    if area>min(F(ac['area_exact']['numerator'],ac['area_exact']['denominator']),F(bc['area_exact']['numerator'],bc['area_exact']['denominator'])):raise ArithmeticError('intersection_area_exceeds_input')
    return {'area_exact_m2':rational(area),'pq_vertices':vertices_json(v),'qp_vertices':vertices_json(w),'pq_clip_steps':steps,'qp_clip_steps':reverse,'both_orders_exactly_equal':True,
        'classification':'positive_exact_intersection_refutes_zero_overlay' if area>0 else 'zero_exact_area_refutes_2D_relation',
        'does_not_adjudicate_global_ledger_or_physical_fire':True}

def cap_check():
    cap=json.loads(CAP.read_text())
    if datetime.now(timezone.utc)>=datetime.fromisoformat(cap['end_utc_B']):raise ResourceLimit('absolute_UTC_cap')
def write(p,value):
    b=(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode();size=sum(x.stat().st_size for x in OUT.iterdir() if x.is_file()) if OUT.exists() else 0
    if size+len(b)>MAX_OUTPUT:raise ResourceLimit('output_byte_limit')
    Path(p).write_bytes(b)

def freeze():
    cap_check()
    if OUT.exists():raise FileExistsError('evidence exists')
    m=json.loads((SOURCE/'manifest.json').read_text());OUT.mkdir(parents=True);total=0
    for n in INPUTS:
        if sha(SOURCE/n)!=m['files'][n]['sha256']:raise ValueError('source hash mismatch: '+n)
        total+=(SOURCE/n).stat().st_size
        if total>10*1024*1024:raise ResourceLimit('input_byte_limit')
        shutil.copyfile(SOURCE/n,OUT/n)
    paths=[(Path(__file__),'code.snapshot.py.txt'),(ROOT/'tests/test_exact_local_overlay_audit.py','tests.snapshot.py.txt'),(ROOT/'pipeline/exact_geometry_witness.py','parser.snapshot.py.txt'),(PROTOCOL,'protocol.snapshot.md.txt'),(CAP,'cap.snapshot.json')]
    for p,n in paths:shutil.copyfile(p,OUT/n)
    write(OUT/'freeze.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),'protocol_commit':'eaec7ca','code_sha256':sha(__file__),'parser30A_sha256':sha(ROOT/'pipeline/exact_geometry_witness.py'),'protocol_sha256':sha(PROTOCOL),'cap_sha256':sha(CAP),'source_manifest_sha256':sha(SOURCE/'manifest.json'),
        'files_sha256':{p.name:sha(p) for p in OUT.iterdir() if p.is_file()},'tests_before_real':True,'real_inputs_parsed':False,'GEOS_oracle':False})
    print('FREEZE',sha(OUT/'freeze.json'),flush=True)

def run():
    cap_check();f=json.loads((OUT/'freeze.json').read_text())
    if (OUT/'results.json').exists():raise FileExistsError('results exist')
    for p,key in [(Path(__file__),'code_sha256'),(ROOT/'pipeline/exact_geometry_witness.py','parser30A_sha256'),(PROTOCOL,'protocol_sha256'),(CAP,'cap_sha256')]:
        if sha(p)!=f[key]:raise ValueError('freeze changed')
    for n,d in f['files_sha256'].items():
        if sha(OUT/n)!=d:raise ValueError('frozen input changed: '+n)
    budget=Budget(check=cap_check);domains={};result={'status':'pending','gate1_passed':False,'GEOS_oracle':False,'full_ledger_validated':False,'last_operation_not_necessarily_failure_cause':True}
    try:
        parsed=[];total=0
        for role in ['p','q']:
            with gzip.open(OUT/f'last-operation-{role}.wkb.gz','rb') as stream:blob=stream.read(10*1024*1024+1)
            total+=len(blob)
            if total>10*1024*1024:raise ResourceLimit('uncompressed_total_input_byte_limit')
            poly,certificate=parse_operand(blob,budget);parsed.append(poly);domains[role]=certificate
        # Domain already certified above; repeat exact checks as part of pure adjudicator, fixed algorithm.
        result.update(adjudicate(*parsed,budget),status='exact_local_adjudication_complete')
    except (DomainUnknown,ValueError) as exc:result.update(status='unknown_outside_registered_domain',reason=str(exc))
    except ResourceLimit as exc:result.update(status='resource_limit_inconclusive',reason=str(exc))
    except ArithmeticError as exc:result.update(status='blocked_exact_identity',reason=str(exc))
    result.update(domain_certificates=domains,exact_operations=budget.operations,completed_utc=datetime.now(timezone.utc).isoformat(),freeze_sha256=sha(OUT/'freeze.json'),context=json.loads((OUT/'last-operation-context.json').read_text()))
    write(OUT/'results.json',result)
    write(OUT/'manifest.json',{'files':{p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in OUT.iterdir() if p.is_file() and p.name!='manifest.json'},'previous_studies_unchanged':True})
    print('DONE',result['status'],result.get('area_exact_m2',result.get('reason')),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['freeze','run']);args=parser.parse_args();{'freeze':freeze,'run':run}[args.stage]()
