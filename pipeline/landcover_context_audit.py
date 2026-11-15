"""Protocol22: pinned landcover acquisition/schema/area descriptors; no SNP models."""
import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/processed'
OUT=DATA/'landcover_context_audit'
RUNTIME=ROOT/'.runtime/landcover-context'
PREFLIGHT=ROOT/'docs/reviews/evidence/landcover-context-preflight'
PROTOCOL=ROOT/'docs/reviews/2026-11-15-science-protocol-22.md'
CAP=150*1024**2
RADIUS=6371007.181
PIXEL=463.312716525
RETAINED_QC={0,2,4,5,6,7,8,9}
UNKNOWN_QC={1,3,10,255}
GEO={
 'legacy':(ROOT/'data/processed/comunas_biobio_nuble.geojson','6bfe6baebd6e56dad166851f4280a80115812d424ce253c3487350fcb5de8375'),
 'DPA2023':(ROOT/'observed/data/processed/communes-full.geojson','134981d8b085157d7e88ab5fa465d89935554640746b66129d63843a16e70602')}


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024**2),b''):h.update(block)
    return h.hexdigest()


def dump(path,obj):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n')


def protected_snapshot():
    paths=[p for p in DATA.rglob('*') if p.is_file() and OUT not in p.parents]
    paths += list((ROOT/'web/public/data').rglob('*.json'))
    paths += [p for p in (ROOT/'observed/dist/data/publication').glob('*.json')]
    paths += [value[0] for value in GEO.values()]
    paths += list(PREFLIGHT.glob('*.json'))
    return {str(p.relative_to(ROOT)):sha(p) for p in paths}


def transport_headers(host,token=None):
    headers={'User-Agent':'GOLIAT-protocol22/1.0'}
    if token is not None and host=='data.lpdaac.earthdatacloud.nasa.gov':headers['Authorization']='Bearer '+token
    return headers


def download_pinned(use_token=False):
    """Anonymous, manually controlled NASA/CDN transport; no account flows."""
    class StopRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):return None
    opener=urllib.request.build_opener(StopRedirect)
    RUNTIME.mkdir(parents=True,exist_ok=True)
    ledger_path=RUNTIME/'transfer-ledger.json'
    ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else {'cap_bytes':CAP,'received_body_bytes':0,'attempts':[]}
    if ledger['cap_bytes']!=CAP or ledger['received_body_bytes']>CAP:raise ValueError('Transfer ledger/cap mismatch')
    for prior in ledger['attempts']:
        if prior['status']=='started' and prior['bytes']==0:prior['status']='failed_before_payload_redirect_guard'
    token=None
    if use_token:
        secret=ROOT/'.runtime/secrets/earthdata-token'
        if secret.stat().st_mode & 0o077:raise ValueError('Secret file permissions are not private')
        token=secret.read_text().strip()
        if not token or any(c.isspace() for c in token):raise ValueError('Invalid private bearer file format')
    pins=json.loads((PREFLIGHT/'summary.json').read_text())['granules']
    acquired=[]
    for pin in pins:
        year=pin['nominal_year'];expected=pin['head_exact_content_length_bytes'];filename=pin['producer_granule_id']+'.hdf'
        dest=RUNTIME/'raw'/filename;dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():
            if dest.stat().st_size!=expected:raise ValueError('Cached HDF size differs from pin')
            existing=next((a for a in reversed(ledger['attempts']) if a.get('filename')==filename and a.get('status')=='complete'),None)
            if existing is None or existing['sha256']!=sha(dest):raise ValueError('Cached HDF lacks matching transfer hash')
            acquired.append({'year':year,'path':str(dest.relative_to(ROOT)),'bytes':expected,'sha256':sha(dest),'cache_reused':True,'NASA_checksum_available':False})
            continue
        original=json.loads((PREFLIGHT/f'head-{year}.json').read_text())['url']
        attempt={'filename':filename,'year':year,'started_utc':datetime.now(timezone.utc).isoformat(),'bytes':0,'status':'started','authorization_used':False,'redirect_hosts':[]}
        ledger['attempts'].append(attempt);dump(ledger_path,ledger)
        current=original;response=None
        for redirect in range(5):
            parsed=urllib.parse.urlparse(current);host=parsed.hostname or ''
            if parsed.scheme!='https' or not (host=='data.lpdaac.earthdatacloud.nasa.gov' or host.endswith('.cloudfront.net')):
                attempt.update(status='blocked_redirect_host',blocked_host=host);dump(ledger_path,ledger)
                raise ValueError('Blocked unapproved transport host/account flow')
            try:
                headers=transport_headers(host,token)
                if 'Authorization' in headers:attempt['authorization_used']=True
                response=opener.open(urllib.request.Request(current,headers=headers),timeout=40)
                if response.status!=200:raise ValueError('Unexpected transport status')
                break
            except urllib.error.HTTPError as error:
                if error.code not in (301,302,303,307,308):
                    attempt['status']='HTTP_'+str(error.code);dump(ledger_path,ledger);error.close()
                    raise ValueError('Anonymous acquisition failed; no credential/account fallback attempted') from None
                location=error.headers.get('Location');error.close()
                if not location:raise ValueError('Missing redirect location')
                current=urllib.parse.urljoin(current,location)
                attempt['redirect_hosts'].append(urllib.parse.urlparse(current).hostname)
        if response is None:raise ValueError('Too many controlled redirects')
        partial=dest.with_suffix('.hdf.part');digest=hashlib.sha256()
        try:
            with partial.open('wb') as stream:
                while True:
                    remaining=CAP-ledger['received_body_bytes']
                    if remaining<=0:raise ValueError('Dataset transfer cap exhausted')
                    block=response.read(min(1024**2,remaining))
                    if not block:break
                    stream.write(block);digest.update(block)
                    attempt['bytes']+=len(block);ledger['received_body_bytes']+=len(block)
                    dump(ledger_path,ledger)
                    if attempt['bytes']>expected:raise ValueError('Object exceeds pinned HEAD size')
        except Exception:
            attempt['status']='failed_partial';dump(ledger_path,ledger);raise
        finally:response.close()
        if attempt['bytes']!=expected:
            attempt['status']='failed_size';dump(ledger_path,ledger);raise ValueError('Object size differs from pin')
        partial.replace(dest);attempt.update(status='complete',sha256=digest.hexdigest(),completed_utc=datetime.now(timezone.utc).isoformat());dump(ledger_path,ledger)
        acquired.append({'year':year,'path':str(dest.relative_to(ROOT)),'bytes':expected,'sha256':digest.hexdigest(),'cache_reused':False,'NASA_checksum_available':False})
        print('Pinned landcover acquired:',year,expected,'bytes',flush=True)
    return acquired,ledger


def native_read(path,npz_path,metadata_path):
    """Runs only inside the existing isolated HDF4 environment."""
    import numpy as np
    from pyhdf.SD import SD,SDC
    from pyhdf.HDF import getlibversion
    from importlib.metadata import version
    hdf=SD(str(path),SDC.READ);global_attrs=hdf.attributes()
    structure=global_attrs.get('StructMetadata.0')
    if not isinstance(structure,str):raise ValueError('Missing actual StructMetadata.0')
    arrays={};attrs={}
    for name in ('LC_Type1','QC','LW'):
        sds=hdf.select(name);array=sds.get();attributes=sds.attributes()
        arrays[name]=np.asarray(array);attrs[name]=to_json(attributes)
        sds.endaccess()
    meta={'file':Path(path).name,'file_sha256':sha(path),'global_attributes':to_json(global_attrs),
          'SDS_attributes':attrs,'SDS_schema':{n:{'shape':list(a.shape),'dtype':str(a.dtype)} for n,a in arrays.items()},
          'reader_environment':{'python':sys.version.split()[0],'numpy':np.__version__,'pyhdf':version('pyhdf'),'HDF4_library':to_json(getlibversion())},'reader_code_sha256':sha(Path(__file__)),'expected_SDS_names':list(arrays),
          'SDS_array_sha256':{n:hashlib.sha256(a.tobytes(order='C')).hexdigest() for n,a in arrays.items()}}
    hdf.end();validate_schema(arrays,meta)
    Path(npz_path).parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(npz_path,**arrays)
    dump(metadata_path,meta)


def to_json(value):
    if isinstance(value,dict):return {str(k):to_json(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [to_json(v) for v in value]
    if hasattr(value,'tolist'):return to_json(value.tolist())
    if hasattr(value,'item'):return to_json(value.item())
    if isinstance(value,bytes):return value.decode('utf-8','replace')
    return value


def validate_pinned_metadata(meta,pin):
    text=meta['global_attributes'].get('CoreMetadata.0','')
    def core(name):
        block=re.search(r'OBJECT\s*=\s*'+name+r'\b(.*?)END_OBJECT\s*=\s*'+name,text,re.S)
        value=re.search(r'VALUE\s*=\s*([^\n]+)',block[1]) if block else None
        if value is None:raise ValueError('Missing actual CoreMetadata field: '+name)
        return value[1].strip().strip('"')
    expected_file=pin['producer_granule_id']+'.hdf';year=pin['nominal_year']
    if meta.get('file')!=expected_file or core('LOCALGRANULEID')!=expected_file:raise ValueError('Actual native granule identity differs from pin')
    if core('SHORTNAME')!='MCD12Q1' or core('VERSIONID') not in ('61','061'):raise ValueError('Actual native shortname/collection differs from pin')
    if core('RANGEBEGINNINGDATE')!=f'{year}-01-01' or core('RANGEENDINGDATE')!=f'{year}-12-31':raise ValueError('Actual native dates differ from nominal-year pin')
    return {'file':expected_file,'year':year,'short_name':'MCD12Q1','collection':'061','native_dates_verified':True}


def grid_from_metadata(meta):
    text=meta['global_attributes']['StructMetadata.0']
    def pair(name):
        match=re.search(r'\b'+name+r'\s*=\s*\(\s*([-+0-9.eE]+)\s*,\s*([-+0-9.eE]+)\s*\)',text)
        if not match:raise ValueError('Missing actual grid coordinate: '+name)
        return tuple(map(float,match.groups()))
    ul=pair('UpperLeftPointMtrs');lr=pair('LowerRightMtrs')
    xdim=re.search(r'\bXDim\s*=\s*(\d+)',text);ydim=re.search(r'\bYDim\s*=\s*(\d+)',text)
    projection=re.search(r'\bProjection\s*=\s*"?([A-Z0-9_]+)',text)
    params=re.search(r'\bProjParams\s*=\s*\(([^)]+)\)',text)
    if not xdim or not ydim or not projection or not params:raise ValueError('Incomplete projection metadata')
    projection_params=[float(v.strip()) for v in params[1].split(',')]
    if len(projection_params)!=13 or any(abs(v)>1e-12 for v in projection_params[1:]):raise ValueError('Unsupported native projection parameters')
    nx,ny=int(xdim[1]),int(ydim[1]);radius=projection_params[0]
    dx=(lr[0]-ul[0])/nx;dy=(ul[1]-lr[1])/ny
    expected_ul=(-20015109.354+12*2400*PIXEL,10007554.677-12*2400*PIXEL)
    if projection[1]!='GCTP_SNSOID' or abs(radius-RADIUS)>1e-6 or (nx,ny)!=(2400,2400):raise ValueError('Unexpected native CRS/dimensions')
    if not all(math.isfinite(v) for v in (*ul,*lr,dx,dy)) or max(abs(dx-PIXEL),abs(dy-PIXEL))>1e-5:raise ValueError('Unexpected actual grid spacing')
    if max(abs(ul[i]-expected_ul[i]) for i in (0,1))>.01:raise ValueError('Actual tile grid differs from h12v12 pin')
    return {'ulx':ul[0],'uly':ul[1],'lrx':lr[0],'lry':lr[1],'dx':dx,'dy':dy,'nx':nx,'ny':ny,'radius':radius,'projection':projection[1]}


def validate_schema(arrays,meta):
    import numpy as np
    if set(arrays)!={'LC_Type1','QC','LW'}:raise ValueError('Unexpected SDS set')
    expected={'LC_Type1':set(range(1,18))|{255},'QC':set(range(11))|{255},'LW':{1,2,255}}
    ranges={'LC_Type1':[1,17],'QC':[0,10],'LW':[1,2]}
    if meta['global_attributes'].get('identifier_product_doi')!='10.5067/MODIS/MCD12Q1.061':raise ValueError('Unexpected actual product DOI/version')
    for name,array in arrays.items():
        if array.shape!=(2400,2400) or array.dtype!=np.dtype('uint8'):raise ValueError('Unexpected actual SDS shape/type: '+name)
        if set(map(int,np.unique(array)))-expected[name]:raise ValueError('Unexpected actual categorical code: '+name)
        fill=meta['SDS_attributes'][name].get('_FillValue')
        if isinstance(fill,list):fill=fill[0] if len(fill)==1 else None
        if fill!=255:raise ValueError('Unexpected actual SDS fill: '+name)
        if meta['SDS_attributes'][name].get('valid_range')!=ranges[name]:raise ValueError('Unexpected actual valid_range: '+name)
    return grid_from_metadata(meta)


def acquire_and_read(use_token=False):
    acquired,ledger=download_pinned(use_token=use_token)
    for obj in acquired:
        year=obj['year'];npz=RUNTIME/'arrays'/f'{year}.npz';meta=RUNTIME/'arrays'/f'{year}-metadata.json'
        if not npz.exists() or not meta.exists() or json.loads(meta.read_text()).get('file_sha256')!=obj['sha256'] or 'SDS_array_sha256' not in json.loads(meta.read_text()) or json.loads(meta.read_text()).get('reader_code_sha256')!=sha(Path(__file__)):
            environment=os.environ.copy();environment['DYLD_LIBRARY_PATH']=str(ROOT/'.runtime/obs-native/lib')
            subprocess.run([str(ROOT/'.runtime/obs-env/bin/python'),str(Path(__file__).resolve()),'native-read',str(ROOT/obj['path']),str(npz),str(meta)],env=environment,check=True,cwd=ROOT)
        obj.update(npz=str(npz.relative_to(ROOT)),metadata=str(meta.relative_to(ROOT)))
    return acquired,ledger


def polygon_weights(polygon,grid,chunk_rows=64):
    """Exact polygon/native-cell intersection areas; no label or center selection."""
    import numpy as np
    import shapely
    if polygon.is_empty or not polygon.is_valid or not math.isfinite(polygon.area) or polygon.area<=0:raise ValueError('Invalid/empty polygon; no repair permitted')
    required={'ulx','uly','lrx','lry','dx','dy','nx','ny'}
    if not required<=set(grid) or grid['dx']<=0 or grid['dy']<=0:raise ValueError('Invalid native grid')
    tile=shapely.box(grid['ulx'],grid['lry'],grid['lrx'],grid['uly'])
    outside=float(shapely.area(shapely.difference(polygon,tile)))
    left,bottom,right,top=polygon.bounds
    c0=max(0,math.floor((left-grid['ulx'])/grid['dx']));c1=min(grid['nx'],math.ceil((right-grid['ulx'])/grid['dx']))
    r0=max(0,math.floor((grid['uly']-top)/grid['dy']));r1=min(grid['ny'],math.ceil((grid['uly']-bottom)/grid['dy']))
    rows=[];cols=[];weights=[];boundary_count=0;full_count=0
    shapely.prepare(polygon)
    for start in range(r0,r1,chunk_rows):
        rr,cc=np.meshgrid(np.arange(start,min(r1,start+chunk_rows)),np.arange(c0,c1),indexing='ij')
        rr=rr.ravel();cc=cc.ravel()
        if not len(rr):continue
        x0=grid['ulx']+cc*grid['dx'];y1=grid['uly']-rr*grid['dy']
        cells=shapely.box(x0,y1-grid['dy'],x0+grid['dx'],y1)
        full=shapely.contains(polygon,cells)
        touch=(~full)&shapely.intersects(polygon,cells)
        area=np.zeros(len(cells),dtype=float);area[full]=grid['dx']*grid['dy']
        if touch.any():area[touch]=shapely.area(shapely.intersection(polygon,cells[touch]))
        if not np.isfinite(area).all() or (area<0).any() or (area>grid['dx']*grid['dy']*(1+1e-8)).any():raise ValueError('Invalid fractional intersection area')
        keep=area>0
        rows.append(rr[keep].astype('int32'));cols.append(cc[keep].astype('int32'));weights.append(area[keep])
        boundary_count+=int((touch&keep).sum());full_count+=int(full.sum())
    rr=np.concatenate(rows) if rows else np.array([],dtype='int32')
    cc=np.concatenate(cols) if cols else np.array([],dtype='int32')
    aa=np.concatenate(weights) if weights else np.array([],dtype=float)
    error=math.fsum(float(a) for a in aa)+outside-polygon.area
    if abs(error)>1e-8*max(1.,polygon.area):raise ValueError('Polygon/native-cell intersection does not close')
    return rr,cc,aa,{'polygon_area_m2':float(polygon.area),'outside_tile_area_m2':outside,'covered_area_m2':float(aa.sum()),
      'intersection_closure_error_m2':float(error),'positive_intersection_cells':len(aa),'full_native_cells':full_count,'partial_native_cells':boundary_count}


def descriptor(lc,qc,lw,areas,total_area,outside_area,policy):
    """Full polygon denominator; valid categorical labels, explicit unknown mass."""
    import numpy as np
    lc=np.asarray(lc);qc=np.asarray(qc);lw=np.asarray(lw);areas=np.asarray(areas,dtype=float)
    if any(a.ndim!=1 or a.shape!=areas.shape for a in (lc,qc,lw)) or not np.isfinite(areas).all() or (areas<=0).any():raise ValueError('Invalid weighted cell inputs')
    if not math.isfinite(total_area) or total_area<=0 or not math.isfinite(outside_area) or outside_area<0:raise ValueError('Invalid polygon denominator')
    if set(map(int,np.unique(lc)))-set(range(1,18))-{255} or set(map(int,np.unique(qc)))-set(range(11))-{255} or set(map(int,np.unique(lw)))-{1,2,255}:raise ValueError('Unexpected category in descriptor')
    if abs(math.fsum(map(float,areas))+outside_area-total_area)>1e-8*max(1.,total_area):raise ValueError('Weighted polygon inputs do not close')
    if policy not in ('retained','QC0'):raise ValueError('Unknown QA policy')
    classified=(lc>=1)&(lc<=17)
    keep=classified&np.isin(qc,list(RETAINED_QC) if policy=='retained' else [0])
    class_area={int(k):math.fsum(map(float,areas[keep&(lc==k)])) for k in range(1,18)}
    unknown=math.fsum(map(float,areas[~keep]))+outside_area
    retained=math.fsum(class_area.values());land=math.fsum(class_area[k] for k in range(1,17))
    error=retained+unknown-total_area
    if abs(error)>1e-8*max(1.,total_area):raise ValueError('Class/unknown area closure failed')
    fractions={k:v/total_area for k,v in class_area.items()}
    record={'total_area_m2':total_area,'outside_tile_area_m2':outside_area,'retained_classified_area_m2':retained,
      'classified_land_area_m2':land,'classified_land_denominator_fraction':land/total_area,
      'unknown_area_m2':unknown,'unknown_fraction':unknown/total_area,'retained_fraction':retained/total_area,
      'layout_valid':True,'context_available':bool(retained/total_area>=.95),'class_unknown_closure_error_m2':error,
      'fraction_closure_error':math.fsum(fractions.values())+unknown/total_area-1}
    for name,classes in [('forest',(1,2,3,4,5)),('crop',(12,)),('urban',(13,)),('mosaic',(14,))]:
        area=math.fsum(class_area[k] for k in classes)
        record[name+'_area_m2']=area;record[name+'_fraction_total']=area/total_area
        record[name+'_fraction_classified_land']=area/land if land>0 else None
    reasons={'outside_tile':outside_area,'LC_fill':math.fsum(map(float,areas[lc==255]))}
    for code in sorted(set(map(int,qc[~keep&classified]))):
        reasons['QC_'+str(code)]=math.fsum(map(float,areas[(~keep)&classified&(qc==code)]))
    if abs(math.fsum(reasons.values())-unknown)>1e-8*max(1.,total_area):raise ValueError('Unknown reasons do not close')
    classes=[{'class_code':k,'area_m2':class_area[k],'fraction_total':fractions[k]} for k in range(1,18)]
    classes.append({'class_code':'unknown','area_m2':unknown,'fraction_total':unknown/total_area})
    return record,classes,reasons


def read_geographies():
    import shapely
    import pyproj
    transformer=pyproj.Transformer.from_crs('EPSG:4326',f'+proj=sinu +R={RADIUS} +units=m +no_defs',always_xy=True)
    result={};expected_cuts=None
    for name,(path,expected) in GEO.items():
        if sha(path)!=expected:raise ValueError('Frozen geometry hash changed: '+name)
        doc=json.loads(path.read_text());items=[]
        for f in doc['features']:
            properties=f['properties'];cut=str(properties['cut']);g=shapely.geometry.shape(f['geometry'])
            if not g.is_valid or g.is_empty:raise ValueError('Invalid source geometry; no repair allowed: '+name+'/'+cut)
            projected=shapely.transform(g,lambda xy:__import__('numpy').column_stack(transformer.transform(xy[:,0],xy[:,1])))
            if not projected.is_valid or projected.is_empty or projected.area<=0:raise ValueError('Invalid projected geometry; no repair allowed: '+name+'/'+cut)
            items.append((cut,str(properties.get('comuna',properties.get('name',''))),projected))
        cuts={cut for cut,_,_ in items}
        if len(items)!=54 or len(cuts)!=54 or sum(c.startswith('08') for c in cuts)!=33 or sum(c.startswith('16') for c in cuts)!=21:raise ValueError('Unexpected whole-polygon54 CUT domain')
        if expected_cuts is not None and cuts!=expected_cuts:raise ValueError('Geographies differ in CUT domain')
        expected_cuts=cuts;result[name]=sorted(items,key=lambda item:item[0])
    return result,{'description':transformer.description,'definition':transformer.definition,'native_crs_proj4':f'+proj=sinu +R={RADIUS} +units=m +no_defs','interpretation':'Map geographic longitude/latitude to the MODIS product sphere by the explicit pipeline; not a claimed high-accuracy ellipsoidal datum transformation.'}


def categorical_area_tables(lc,qc,lw,areas,total_area,outside_area):
    import numpy as np
    tables={}
    for name,values in [('QC',qc),('LW',lw)]:
        records=[{'code':int(code),'area_m2':math.fsum(map(float,areas[values==code])),'fraction_total':math.fsum(map(float,areas[values==code]))/total_area} for code in sorted(np.unique(values))]
        if outside_area:records.append({'code':'outside_tile','area_m2':outside_area,'fraction_total':outside_area/total_area})
        tables[name]=records
    combo=np.stack([lc,qc,lw],axis=1)
    unique,inverse=np.unique(combo,axis=0,return_inverse=True)
    sums=np.bincount(inverse,weights=areas)
    cross=[{'LC_Type1':int(a),'QC':int(b),'LW':int(c),'area_m2':float(w),'fraction_total':float(w/total_area)} for (a,b,c),w in zip(unique,sums)]
    if outside_area:cross.append({'LC_Type1':'outside_tile','QC':'outside_tile','LW':'outside_tile','area_m2':outside_area,'fraction_total':outside_area/total_area})
    tables['cross']=cross
    return tables


def stability_tables(features):
    import pandas as pd
    fields=['forest_fraction_total','crop_fraction_total','urban_fraction_total','mosaic_fraction_total','unknown_fraction','retained_fraction']
    annual=[];geo=[]
    for (geography,policy,cut),g in features.groupby(['geography','policy','cut']):
        a=g.set_index('year')
        if set(a.index)!={2001,2010}:raise ValueError('Incomplete fixed-year stability comparison')
        for field in fields:annual.append({'geography':geography,'policy':policy,'cut':cut,'field':field,'value2001':float(a.loc[2001,field]),'value2010':float(a.loc[2010,field]),'delta2010_minus2001':float(a.loc[2010,field]-a.loc[2001,field])})
    for (year,policy,cut),g in features.groupby(['year','policy','cut']):
        a=g.set_index('geography')
        if set(a.index)!={'legacy','DPA2023'}:raise ValueError('Incomplete fixed-geography sensitivity')
        for field in fields:geo.append({'year':int(year),'policy':policy,'cut':cut,'field':field,'legacy':float(a.loc['legacy',field]),'DPA2023':float(a.loc['DPA2023',field]),'delta_DPA_minus_legacy':float(a.loc['DPA2023',field]-a.loc['legacy',field])})
    return pd.DataFrame(annual),pd.DataFrame(geo)


def run():
    import numpy as np
    import pandas as pd
    import shapely
    import pyproj
    started=time.monotonic();before=protected_snapshot()
    acquisition=json.loads((RUNTIME/'acquisition.json').read_text())
    if acquisition['protocol_sha256']!=sha(PROTOCOL):raise ValueError('Acquisition protocol differs from frozen22')
    pins=json.loads((PREFLIGHT/'summary.json').read_text())['granules']
    arrays={};metadata={};grid=None
    for obj in acquisition['files']:
        year=obj['year'];pin=next(p for p in pins if p['nominal_year']==year)
        raw=ROOT/obj['path']
        if raw.stat().st_size!=pin['head_exact_content_length_bytes'] or sha(raw)!=obj['sha256']:raise ValueError('Pinned acquired HDF changed')
        meta=json.loads((ROOT/obj['metadata']).read_text())
        if meta['file_sha256']!=obj['sha256']:raise ValueError('Native metadata/HDF provenance mismatch')
        with np.load(ROOT/obj['npz'],allow_pickle=False) as cache:current={k:cache[k] for k in cache.files}
        actual=validate_schema(current,meta)
        validate_pinned_metadata(meta,pin)
        for name,a in current.items():
            if hashlib.sha256(a.tobytes(order='C')).hexdigest()!=meta['SDS_array_sha256'][name]:raise ValueError('Derived NPZ does not reproduce native-reader arrays')
        if grid is not None and actual!=grid:raise ValueError('The pinned years do not share an identical actual grid')
        grid=actual;arrays[year]=current;metadata[year]=meta
    if set(arrays)!={2001,2010}:raise ValueError('Expected exactly two pinned years')
    geographies,transform_description=read_geographies()
    feature_rows=[];class_rows=[];reason_rows=[];qc_rows=[];lw_rows=[];cross_rows=[];geometry_rows=[]
    for geography,items in geographies.items():
        for cut,name,polygon in items:
            rr,cc,weights,geo=polygon_weights(polygon,grid)
            geometry_rows.append(dict(geography=geography,cut=cut,**geo))
            for year in (2010,2001):
                source=arrays[year];lc=source['LC_Type1'][rr,cc];qc=source['QC'][rr,cc];lw=source['LW'][rr,cc]
                keys={'geography':geography,'cut':cut,'year':year}
                categories=categorical_area_tables(lc,qc,lw,weights,geo['polygon_area_m2'],geo['outside_tile_area_m2'])
                qc_rows += [dict(**keys,**v) for v in categories['QC']]
                lw_rows += [dict(**keys,**v) for v in categories['LW']]
                cross_rows += [dict(**keys,**v) for v in categories['cross']]
                for policy in ('retained','QC0'):
                    record,classes,reasons=descriptor(lc,qc,lw,weights,geo['polygon_area_m2'],geo['outside_tile_area_m2'],policy)
                    key=dict(**keys,policy=policy)
                    feature_rows.append(dict(**key,commune=name,**record))
                    class_rows += [dict(**key,**v) for v in classes]
                    reason_rows += [dict(**key,reason=k,area_m2=v,fraction_total=v/geo['polygon_area_m2']) for k,v in reasons.items()]
            print('Whole-polygon fractional overlay complete:',geography,cut,flush=True)
    features=pd.DataFrame(feature_rows);geometry=pd.DataFrame(geometry_rows)
    if len(features)!=432 or len(class_rows)!=432*18:raise ValueError('Incomplete fixed feature grid')
    year_stability,geo_sensitivity=stability_tables(features)
    configurations={}
    for key,g in features.groupby(['year','geography','policy']):
        configurations['/'.join(map(str,key))]={'n':len(g),'context_available':int(g.context_available.sum()),'context_unavailable_cuts':g.loc[~g.context_available,'cut'].tolist(),
          'min_retained_fraction':float(g.retained_fraction.min()),'max_unknown_fraction':float(g.unknown_fraction.max()),
          'feature_ranges':{f:{'min':float(g[f+'_fraction_total'].min()),'max':float(g[f+'_fraction_total'].max())} for f in ('forest','crop','urban','mosaic')}}
    summary={'status':'retrospective-landcover-area-descriptor','protocol':'22','model_fits':0,'new_prediction_scores':0,'uses_SNPP_labels':False,
      'asof2012_claim':False,'nominal2010_reprocessed2022_HMM':True,'classification_is_ecological_truth':False,
      'primary_year':2010,'stability_year':2001,'primary_geography':'legacy','secondary_geography':'DPA2023','primary_QC_retained':sorted(RETAINED_QC),'unknown_QC':sorted(UNKNOWN_QC),'sensitivity':'QC0 only; declared policy, not NASA requirement',
      'context_available_threshold':.95,'threshold_is_engineering_policy_not_NASA':True,'primary_denominator':'complete native-SINU polygon area','secondary_denominator':'retained classified land classes1-16; null if zero',
      'feature_rows':len(features),'whole_polygons_per_geography':54,'geometry_operations':len(geometry),'grid':grid,
      'max_intersection_relative_closure_error':float((geometry.intersection_closure_error_m2.abs()/geometry.polygon_area_m2.clip(lower=1)).max()),
      'max_class_relative_closure_error':float((features.class_unknown_closure_error_m2.abs()/features.total_area_m2.clip(lower=1)).max()),
      'max_fraction_closure_error':float(features.fraction_closure_error.abs().max()),'configurations':configurations,
      'acquired_HDF_bytes':sum(obj['bytes'] for obj in acquisition['files']),'transfer_body_bytes_including_failures':acquisition['transfer_ledger']['received_body_bytes'],'dataset_cap_bytes':CAP,'L2_budget_separate_unchanged':True,
      'NASA_object_checksum_available':False,'local_SHA256_preserved':True,'geometry_repair_performed':False,'class_interpolation_performed':False,'footprint_area_convention':'native spherical sinusoidal projected geometry; no center assignment',
      'transform':transform_description,'elapsed_seconds':time.monotonic()-started,
      'environment':{'python':sys.version.split()[0],'numpy':np.__version__,'pandas':pd.__version__,'shapely':shapely.__version__,'GEOS':shapely.geos_version_string,'pyproj':pyproj.__version__,'PROJ':pyproj.proj_version_str}}
    if before!=protected_snapshot():raise ValueError('Protected base/publication/prior results changed')
    OUT.mkdir(parents=True,exist_ok=True)
    for filename,frame in [('features.csv',features),('class_areas.csv',pd.DataFrame(class_rows)),('unknown_reasons.csv',pd.DataFrame(reason_rows)),('QC_areas.csv',pd.DataFrame(qc_rows)),('LW_areas.csv',pd.DataFrame(lw_rows)),('LC_QC_LW_areas.csv',pd.DataFrame(cross_rows)),('geometry_checks.csv',geometry),('year_stability.csv',year_stability),('geography_sensitivity.csv',geo_sensitivity)]:frame.to_csv(OUT/filename,index=False)
    dump(OUT/'summary.json',summary);dump(OUT/'acquisition.json',acquisition)
    for year,meta in metadata.items():dump(OUT/f'native_metadata_{year}.json',meta)
    manifest={'protocol_sha256':sha(PROTOCOL),'code_sha256':sha(Path(__file__)),'input_geography_sha256':{name:sha(value[0]) for name,value in GEO.items()},
      'input_HDF_sha256':{str(obj['year']):obj['sha256'] for obj in acquisition['files']},'native_NPZ_sha256':{str(obj['year']):sha(ROOT/obj['npz']) for obj in acquisition['files']},
      'protected_sha256':before,'all_previous_artifacts_unchanged':True,'output_sha256':{p.name:sha(p) for p in OUT.glob('*') if p.name!='manifest.json'}}
    dump(OUT/'manifest.json',manifest);print('Landcover descriptor audit complete; no model fitting/scoring:',OUT,flush=True)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['acquire','acquire-authenticated','native-read','run']);parser.add_argument('paths',nargs='*');args=parser.parse_args()
    if args.mode=='native-read':native_read(*args.paths)
    elif args.mode in ('acquire','acquire-authenticated'):
        before=protected_snapshot();dump(RUNTIME/'protected-before-acquisition.json',before)
        acquired,ledger=acquire_and_read(use_token=args.mode=='acquire-authenticated')
        if before!=protected_snapshot():raise ValueError('Protected data changed during acquisition')
        dump(RUNTIME/'acquisition.json',{'files':acquired,'transfer_ledger':ledger,'protocol_sha256':sha(PROTOCOL)})
        print('Acquisition/schema complete; no area features yet',flush=True)
    else:run()
