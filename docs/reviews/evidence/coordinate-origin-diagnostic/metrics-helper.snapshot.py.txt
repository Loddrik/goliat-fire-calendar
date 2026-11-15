"""Frozen WKB-only regression diagnostic; no science data or geometry repair.

C declarations follow official GEOS3.15.0 capi/geos_c.h.in. Each engine runs in
its own process, preventing dynamic-loader symbol sharing across GEOS versions.
"""
from __future__ import annotations
import argparse
import ctypes as C
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/reviews/evidence/observation-ownership-ledger/diagnostic'
OUT = ROOT / 'docs/reviews/evidence/geometry-engine-diagnostic'
RUNTIME = ROOT / '.runtime/geometry-engine-diagnostic'
PROTOCOL = ROOT / 'docs/reviews/2026-11-15-geometry-engine-diagnostic-protocol.md'
PAIRS = ('MYD14_early-818-1166', 'MYD14_late-833-1149', 'MYD14_late-844-1161',
         'VNP14IMG_early-2051-3869', 'VNP14IMG_early-2076-3864')
TOLERANCE = 1.0
DEADLINE = datetime(2026, 11, 15, 5, 25, tzinfo=timezone.utc)
TYPE_NAMES = ('Point', 'LineString', 'LinearRing', 'Polygon', 'MultiPoint',
              'MultiLineString', 'MultiPolygon', 'GeometryCollection')


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + '\n')


def rectangle(x0, y0, x1, y1):
    points = ((x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0))
    return struct.pack('<BIII', 1, 3, 1, 5) + b''.join(struct.pack('<dd', *p) for p in points)


def controls():
    p = rectangle(0,0,10,10)
    return [
        ('control_disjoint', p, rectangle(20,0,30,10), [100,100,0,100,100,200]),
        ('control_contained', rectangle(2,2,4,4), p, [4,100,4,0,96,100]),
        ('control_partial', p, rectangle(5,0,15,10), [100,100,50,50,50,150]),
        ('control_touch', p, rectangle(10,0,20,10), [100,100,0,100,100,200]),
    ]


def freeze():
    if OUT.exists():
        raise FileExistsError('existing diagnostic evidence must not be overwritten')
    manifest = json.loads((SOURCE / 'manifest.json').read_text())
    for prefix in PAIRS:
        for role in ('pixel','other_union'):
            name = prefix + '-' + role + '.wkb.gz'
            if digest(SOURCE/name) != manifest['files'][name]['sha256']:
                raise ValueError('original WKB hash mismatch: '+name)
    OUT.mkdir(parents=True)
    fixtures=[]
    for prefix in PAIRS:
        item={'id':prefix,'kind':'selected_GEO_regression_counterexample'}
        for role in ('pixel','other_union'):
            name=prefix+'-'+role+'.wkb.gz'
            shutil.copyfile(SOURCE/name,OUT/name)
            item[role]=name
        fixtures.append(item)
    for name,p,q,expected in controls():
        item={'id':name,'kind':'synthetic_control','expected_areas_p_q_i_dp_dq_u':expected}
        for role,data in [('pixel',p),('other_union',q)]:
            filename=name+'-'+role+'.wkb'
            (OUT/filename).write_bytes(data)
            item[role]=filename
        fixtures.append(item)
    write(OUT/'fixtures.json',fixtures)
    shutil.copyfile(__file__,OUT/'code-snapshot.py.txt')
    shutil.copyfile(PROTOCOL,OUT/'protocol-snapshot.md.txt')
    shutil.copyfile(RUNTIME/'tag.json',OUT/'official-tag.json')
    source_dir=RUNTIME/'geos-3.15.0'
    shutil.copyfile(source_dir/'capi/geos_c.h.in',OUT/'official-geos_c.h.in.txt')
    write(OUT/'freeze.json',{
        'frozen_utc':now(),'deadline_utc':DEADLINE.isoformat(),
        'code_sha256':digest(__file__),'protocol_sha256':digest(PROTOCOL),
        'files_sha256':{p.name:digest(p) for p in sorted(OUT.iterdir()) if p.is_file()},
        'source':{'url':'https://github.com/libgeos/geos/archive/refs/tags/3.15.0.tar.gz',
                  'tls':'HTTPS certificate verification enabled; curl --proto=https --tlsv1.2',
                  'bytes':(RUNTIME/'geos-3.15.0.tar.gz').stat().st_size,
                  'sha256_local':digest(RUNTIME/'geos-3.15.0.tar.gz'),
                  'remote_checksum_verified':False,'tag':'3.15.0',
                  'commit':json.loads((RUNTIME/'tag.json').read_text())['object']['sha']},
        'selection':'five previously fixed geometry-only algebraic counterexamples; not a random sample',
        'repair_or_precision_changes':False,'fire_data_read':False,
        'gate1_passed':False})
    print(json.dumps({'freeze_sha256':digest(OUT/'freeze.json'),
                      'code_sha256':digest(__file__),'fixtures_sha256':digest(OUT/'fixtures.json')}))


def verify_freeze():
    frozen=json.loads((OUT/'freeze.json').read_text())
    if digest(__file__) != frozen['code_sha256'] or digest(PROTOCOL) != frozen['protocol_sha256']:
        raise ValueError('code/protocol changed after freeze')
    for name, expected in frozen['files_sha256'].items():
        if digest(OUT/name)!=expected:
            raise ValueError('frozen fixture/source changed: '+name)


def wkb(name):
    data=(OUT/name).read_bytes()
    return gzip.decompress(data) if name.endswith('.gz') else data


class Engine:
    def __init__(self,path,expected):
        self.lib=C.CDLL(str(Path(path).resolve()),mode=C.RTLD_LOCAL)
        def bind(name,args,ret):
            fn=getattr(self.lib,name);fn.argtypes=args;fn.restype=ret;return fn
        V=C.c_void_p
        self.version=bind('GEOSversion',[],C.c_char_p)().decode()
        if not self.version.startswith(expected+'-CAPI-'):
            raise ValueError('unexpected actual GEOS version: '+self.version)
        self.init=bind('GEOS_init_r',[],V)
        self.finish=bind('GEOS_finish_r',[V],None)
        self.ctx=self.init()
        if not self.ctx:raise RuntimeError('GEOS context allocation failed')
        self.errors=[]
        handler=C.CFUNCTYPE(None,C.c_char_p,V)
        self.callback=handler(lambda message,user:self.errors.append(message.decode(errors='replace')))
        bind('GEOSContext_setErrorMessageHandler_r',[V,handler,V],V)(self.ctx,self.callback,None)
        self.reader=bind('GEOSWKBReader_create_r',[V],V)(self.ctx)
        if not self.reader:raise RuntimeError('GEOS WKB reader allocation failed')
        self.read_fn=bind('GEOSWKBReader_read_r',[V,V,C.POINTER(C.c_ubyte),C.c_size_t],V)
        self.destroy_reader=bind('GEOSWKBReader_destroy_r',[V,V],None)
        self.destroy=bind('GEOSGeom_destroy_r',[V,V],None)
        self.area_fn=bind('GEOSArea_r',[V,V,C.POINTER(C.c_double)],C.c_int)
        self.type_fn=bind('GEOSGeomTypeId_r',[V,V],C.c_int)
        self.valid_fn=bind('GEOSisValid_r',[V,V],C.c_byte)
        self.within_fn=bind('GEOSWithin_r',[V,V,V],C.c_byte)
        self.covered_fn=bind('GEOSCoveredBy_r',[V,V,V],C.c_byte)
        self.ops={name:bind('GEOS'+name+'_r',[V,V,V],V)
                  for name in ('Intersection','Difference','Union')}

    def read(self,data):
        array=(C.c_ubyte*len(data)).from_buffer_copy(data)
        result=self.read_fn(self.ctx,self.reader,array,len(data))
        if not result:raise RuntimeError('WKB read failed: '+str(self.errors))
        return result

    def predicate(self,fn,*args):
        result=fn(self.ctx,*args)
        if result not in (0,1):raise RuntimeError('GEOS predicate exception: '+str(self.errors))
        return bool(result)

    def info(self,g):
        area=C.c_double()
        if self.area_fn(self.ctx,g,C.byref(area))!=1 or not math.isfinite(area.value):
            raise RuntimeError('GEOS area failure')
        kind=self.type_fn(self.ctx,g)
        if not 0<=kind<len(TYPE_NAMES):raise RuntimeError('GEOS geometry type failure')
        return {'area_m2':area.value,'type':TYPE_NAMES[kind],
                'valid':self.predicate(self.valid_fn,g)}

    def close(self):
        self.destroy_reader(self.ctx,self.reader)
        self.finish(self.ctx)


def finish_metrics(row):
    a,b=row['p']['area_m2'],row['q']['area_m2']
    ip,iq=row['intersection_pq']['area_m2'],row['intersection_qp']['area_m2']
    dp,dq=row['difference_pq']['area_m2'],row['difference_qp']['area_m2']
    up,uq=row['union_pq']['area_m2'],row['union_qp']['area_m2']
    residuals={'partition_p':a-ip-dp,'partition_q':b-iq-dq,
               'union_pq':up-a-b+ip,'union_qp':uq-a-b+iq,
               'intersection_order':ip-iq,'union_order':up-uq}
    row['identity_residuals_m2']=residuals
    row['identities_within_1m2']=all(abs(v)<=TOLERANCE for v in residuals.values())
    contradictions=[]
    for suffix,area,inter,diff in [('pq',a,ip,dp),('qp',b,iq,dq)]:
        if row['within_'+suffix] or row['covered_by_'+suffix]:
            if abs(area-inter)>TOLERANCE or abs(diff)>TOLERANCE:
                contradictions.append('containment_vs_overlay_'+suffix)
    row['predicate_overlay_contradictions']=contradictions
    row['regression_checks_pass']=row['identities_within_1m2'] and not contradictions and all(
        row[key]['valid'] for key in ('p','q','intersection_pq','intersection_qp',
                                     'difference_pq','difference_qp','union_pq','union_qp'))
    if 'expected_areas_p_q_i_dp_dq_u' in row:
        actual=[a,b,ip,dp,dq,up]
        row['control_expected_areas_pass']=all(abs(x-y)<=1e-9 for x,y in zip(
            actual,row['expected_areas_p_q_i_dp_dq_u']))
    return row


def worker(library,expected,output,shapely_mode=False):
    verify_freeze()
    if datetime.now(timezone.utc)>=DEADLINE:raise TimeoutError('frozen deadline reached')
    fixtures=json.loads((OUT/'fixtures.json').read_text())
    engine=None
    if shapely_mode:
        import shapely
        version=shapely.geos_version_string
        if version!=expected:raise ValueError('unexpected Shapely baseline engine')
        version+=' (Shapely '+shapely.__version__+')'
    else:
        engine=Engine(library,expected);version=engine.version
    rows=[]
    try:
        for item in fixtures:
            if datetime.now(timezone.utc)>=DEADLINE:raise TimeoutError('frozen deadline reached')
            row={**item,'wkb_sha256':{role:hashlib.sha256(wkb(item[role])).hexdigest()
                                      for role in ('pixel','other_union')}}
            objects=[]
            try:
                if shapely_mode:
                    p,q=[shapely.from_wkb(wkb(item[role])) for role in ('pixel','other_union')]
                    row.update(p={'area_m2':p.area,'type':p.geom_type,'valid':p.is_valid},
                               q={'area_m2':q.area,'type':q.geom_type,'valid':q.is_valid})
                    for suffix,left,right in [('pq',p,q),('qp',q,p)]:
                        row['within_'+suffix]=left.within(right)
                        row['covered_by_'+suffix]=left.covered_by(right)
                        for name in ('intersection','difference','union'):
                            result=getattr(left,name)(right)
                            row[name+'_'+suffix]={'area_m2':result.area,'type':result.geom_type,'valid':result.is_valid}
                else:
                    p=engine.read(wkb(item['pixel']));objects.append(p)
                    q=engine.read(wkb(item['other_union']));objects.append(q)
                    row.update(p=engine.info(p),q=engine.info(q))
                    for suffix,left,right in [('pq',p,q),('qp',q,p)]:
                        row['within_'+suffix]=engine.predicate(engine.within_fn,left,right)
                        row['covered_by_'+suffix]=engine.predicate(engine.covered_fn,left,right)
                        for name,fn in engine.ops.items():
                            result=fn(engine.ctx,left,right)
                            if not result:raise RuntimeError('GEOS overlay failure: '+str(engine.errors))
                            objects.append(result)
                            row[name.lower()+'_'+suffix]=engine.info(result)
                rows.append(finish_metrics(row))
            finally:
                if engine:
                    for obj in reversed(objects):engine.destroy(engine.ctx,obj)
        result={'version_actual':version,'started_or_completed_utc':now(),'rows':rows,
                'fire_data_read':False,'precision_or_repair_changed':False,
                'gate1_passed':False,'physical_exposure_verified':False}
        if not shapely_mode:
            result.update(library_path=str(Path(library).resolve()),library_sha256=digest(library),
                          engine_error_messages=engine.errors)
        write(output,result)
    finally:
        if engine:engine.close()


def run(new_library):
    verify_freeze()
    baseline=ROOT/'.venv/lib/python3.14/site-packages/shapely/.dylibs/libgeos_c.1.20.5.dylib'
    for name,path,expected,mode in [
        ('baseline-capi',baseline,'3.14.1',False),
        ('baseline-shapely',baseline,'3.14.1',True),
        ('comparator-capi',Path(new_library),'3.15.0',False)]:
        output=OUT/(name+'.json')
        if output.exists():raise FileExistsError('refusing to overwrite '+str(output))
        remaining=(DEADLINE-datetime.now(timezone.utc)).total_seconds()
        if remaining<180:raise TimeoutError('insufficient cap remaining for comparison and review')
        command=[sys.executable,str(Path(__file__).resolve()),'--worker',
                 '--library',str(path),'--expected-version',expected,'--output',str(output)]
        if mode:command.append('--shapely-mode')
        subprocess.run(command,check=True,timeout=min(90,remaining-120))
        if name=='baseline-shapely':
            capi=json.loads((OUT/'baseline-capi.json').read_text())
            shape=json.loads(output.read_text())
            if capi['rows']!=shape['rows']:raise ValueError('ctypes baseline disagrees with Shapely')
        data=json.loads(output.read_text())
        if not all(r['control_expected_areas_pass'] and r['regression_checks_pass']
                   for r in data['rows'] if r['kind']=='synthetic_control'):
            raise ValueError('synthetic adapter controls failed: '+name)
    old=json.loads((OUT/'baseline-capi.json').read_text())
    new=json.loads((OUT/'comparator-capi.json').read_text())
    comparisons=[]
    for a,b in zip(old['rows'],new['rows']):
        if a['id']!=b['id'] or a['wkb_sha256']!=b['wkb_sha256']:
            raise ValueError('engine inputs differ')
        comparisons.append({'id':a['id'],'kind':a['kind'],
                            'baseline_checks_pass':a['regression_checks_pass'],
                            'comparator_checks_pass':b['regression_checks_pass'],
                            'same_input_properties':a['p']==b['p'] and a['q']==b['q'],
                            'baseline_predicate_overlay_contradictions':a['predicate_overlay_contradictions'],
                            'comparator_predicate_overlay_contradictions':b['predicate_overlay_contradictions']})
    write(OUT/'comparison.json',{'completed_utc':now(),'comparisons':comparisons,
          'baseline_adapter_matches_shapely':True,'same_WKB_verified':True,
          'tolerance_m2':TOLERANCE,'issue1499_cause_proved':False,
          'full_24B_ledger_validated':False,'gate1_passed':False,
          'physical_exposure_verified':False})
    write(OUT/'manifest.json',{'completed_utc':now(),
          'files':{p.name:{'bytes':p.stat().st_size,'sha256':digest(p)}
                   for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='manifest.json'},
          'source_archive_local_sha256':digest(RUNTIME/'geos-3.15.0.tar.gz'),
          'build_parallelism':2,'main_environment_modified':False,
          'raw_or_FIRE_read':False,'gate1_passed':False})
    print(json.dumps(comparisons))


def main():
    parser=argparse.ArgumentParser()
    action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--freeze',action='store_true')
    action.add_argument('--run',action='store_true')
    action.add_argument('--worker',action='store_true')
    parser.add_argument('--library')
    parser.add_argument('--expected-version')
    parser.add_argument('--output')
    parser.add_argument('--shapely-mode',action='store_true')
    args=parser.parse_args()
    if args.freeze:freeze()
    elif args.worker:worker(args.library,args.expected_version,args.output,args.shapely_mode)
    else:run(args.library)


if __name__=='__main__':main()
