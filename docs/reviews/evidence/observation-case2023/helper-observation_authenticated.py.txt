"""Bounded authenticated acquisition of one fixed G0 candidate and auxiliaries.

Read tokens only from ignored local files. Never persist bearer values, redirect
queries or response bodies for errors. Authentication headers are recomputed at
EVERY hop; non-NASA data/CDN redirects receive no Authorization header.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
import re
from pathlib import Path
import time
from urllib.error import HTTPError,URLError
from urllib.parse import urljoin,urlsplit,urlunsplit
from urllib.request import Request,build_opener,HTTPRedirectHandler

ROOT=Path(__file__).resolve().parents[1]
NASA_AUTH_HOSTS=frozenset({'data.lpdaac.earthdatacloud.nasa.gov','data.laadsdaac.earthdatacloud.nasa.gov','urs.earthdata.nasa.gov'})
CDN_HOSTS=frozenset({'d1nklfio7vscoe.cloudfront.net','d13j1jds5ybppo.cloudfront.net'})
BUDGET=400*1024*1024


def safe_url(url):
 p=urlsplit(url);host=p.hostname or ''
 if p.port:host+=':'+str(p.port)
 return urlunsplit((p.scheme,host,p.path,'',''))


def permitted(url):
 p=urlsplit(url);host=p.hostname or ''
 return p.scheme=='https' and p.username is None and p.password is None and p.port in (None,443) and (
  host in NASA_AUTH_HOSTS or host in CDN_HOSTS or host.endswith('.s3.amazonaws.com') or ('.s3.' in host and host.endswith('.amazonaws.com')))


def auth_headers(url,token):
 if not permitted(url):raise ValueError('Unapproved data redirect host')
 headers={'User-Agent':'GOLIAT-observation-G0/1.0'}
 if urlsplit(url).hostname in NASA_AUTH_HOSTS:headers['Authorization']='Bearer '+token
 return headers


class NoRedirect(HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None


def file_magic(path):
 with Path(path).open('rb') as stream:return stream.read(8)


def file_sha(path):
 digest=hashlib.sha256()
 with path.open('rb') as stream:
  for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
 return digest.hexdigest()


def download(url,destination,token,remaining_bytes,deadline):
 if remaining_bytes<=0:raise ValueError('Download budget exhausted')
 destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
 if destination.exists():
  if not (file_magic(destination).startswith(b'\x0e\x03\x13\x01') or file_magic(destination).startswith(b'\x89HDF\r\n\x1a\n')):
   return {'status':'invalid_existing_file','bytes':0},0
  return {'status':'existing_file','bytes':destination.stat().st_size,'sha256':file_sha(destination),'file':str(destination.relative_to(ROOT)),
          'hdf_magic':file_magic(destination).hex(),'downloaded_now':False},0
 opener=build_opener(NoRedirect());current=url;hops=[];started=time.monotonic()
 for _ in range(8):
  if time.time()>=deadline:raise TimeoutError('G0 deadline')
  headers=auth_headers(current,token)
  try:response=opener.open(Request(current,headers=headers),timeout=min(60,max(1,deadline-time.time())))
  except HTTPError as error:
   error.close()
   if error.code in (301,302,303,307,308) and error.headers.get('Location'):
    target=urljoin(current,error.headers['Location'])
    hops.append({'http_status':error.code,'from':safe_url(current),'to':safe_url(target),'authorization_on_request':'Authorization' in headers})
    if not permitted(target):return {'status':'redirect_not_allowed','http_status':error.code,'hops':hops,'bytes':0},0
    current=target;continue
   return {'status':'http_error','http_status':error.code,'url':safe_url(current),'hops':hops,'bytes':0},0
  except (URLError,OSError,TimeoutError) as error:
   return {'status':'transport_error','error_class':type(error).__name__,'url':safe_url(current),'hops':hops,'bytes':0},0
  with response:
   content_type=response.headers.get('Content-Type','');length=response.headers.get('Content-Length')
   if 'html' in content_type.lower() or 'json' in content_type.lower():
    return {'status':'non_science_response','http_status':response.status,'content_type':content_type,'url':safe_url(current),'hops':hops,'bytes':0},0
   if length and int(length)>remaining_bytes:
    return {'status':'budget_exceeded_before_download','declared_bytes':int(length),'url':safe_url(current),'hops':hops,'bytes':0},0
   part=destination.with_suffix(destination.suffix+'.part');written=0;digest=hashlib.sha256();magic=b''
   try:
    with part.open('wb') as stream:
     while True:
      if time.time()>=deadline:raise TimeoutError('G0 deadline')
      if written==remaining_bytes:
       if length and written==int(length):break
       raise ValueError('Budget reached before end could be verified')
      chunk=response.read(min(1024*1024,remaining_bytes-written))
      if not chunk:break
      written+=len(chunk)
      if written>remaining_bytes:raise ValueError('Download budget exceeded')
      if not magic:magic=chunk[:8]
      stream.write(chunk);digest.update(chunk)
    if length and written!=int(length):raise ValueError('Incomplete data response')
    if not (magic.startswith(b'\x0e\x03\x13\x01') or magic.startswith(b'\x89HDF\r\n\x1a\n')):
     raise ValueError('Unexpected file magic')
    part.replace(destination)
   except Exception as error:
    return {'status':'download_failed','error_class':type(error).__name__,'bytes':written,'url':safe_url(current),'hops':hops},written
   return {'status':'downloaded','bytes':written,'sha256':digest.hexdigest(),'file':str(destination.relative_to(ROOT)),'hdf_magic':magic.hex(),
    'http_status':response.status,'content_type':content_type,'url':safe_url(current),'hops':hops,'seconds':round(time.monotonic()-started,3),
    'final_request_had_authorization':'Authorization' in headers,'downloaded_now':True},written
 return {'status':'redirect_limit','hops':hops,'bytes':0},0


def run(token_file,raw_dir,evidence_dir,deadline,budget=BUDGET):
 token=Path(token_file).read_text().strip()
 if not token:raise ValueError('Missing configured credential')
 raw_dir=Path(raw_dir);evidence_dir=Path(evidence_dir);evidence_dir.mkdir(parents=True,exist_ok=True)
 source=ROOT/'docs/reviews/evidence/observation-preflight/summary.json';anon=json.loads(source.read_text())
 record={'scope':'One fixed metadata candidate; authenticated files, not a fire accuracy experiment','started_utc':datetime.now(timezone.utc).isoformat(),
  'token_configured':True,'token_persisted_in_evidence':False,'budget_bytes':budget,'downloaded_bytes':0,'files':{},'gate0_passed':False,
  'geolocation_qa_read':False,'input_pointer_verified':False,'common_pixel_support_verified':False,
  'source_anonymous_summary_sha256':file_sha(source),'candidate':anon['chosen_probe_pair']}
 def save():
  (evidence_dir/'acquisition.json').write_text(json.dumps(record,indent=2,allow_nan=False)+'\n')
 for name,item in anon['anonymous_probes'].items():
  url=item['url'];filename=Path(urlsplit(url).path).name
  result,spent=download(url,raw_dir/filename,token,budget-record['downloaded_bytes'],deadline)
  record['files'][name]=result;record['downloaded_bytes']+=spent;save()
  print(name,result['status'],'bytes',result.get('bytes',0),flush=True)
 record['completed_utc']=datetime.now(timezone.utc).isoformat();record['all_four_files_acquired']=all(x.get('status') in {'downloaded','existing_file'} for x in record['files'].values()) and len(record['files'])==4
 record['code_sha256']=file_sha(Path(__file__));save();return record


def inspect_files(raw_dir,evidence_dir):
 import numpy as np
 import h5py
 from pyhdf.SD import SD,SDC
 def plain(value):
  if isinstance(value,bytes):return value.decode('utf-8','replace')
  if isinstance(value,(str,int,float,bool)) or value is None:return value
  if isinstance(value,(list,tuple)):return [plain(v) for v in value]
  if hasattr(value,'tolist'):return plain(value.tolist())
  return str(value)
 def chosen_attrs(attrs):
  keys=['legend','units','valid_range','_FillValue','flag_masks','flag_meanings','scale_factor','add_offset','long_name']
  return {k:plain(attrs[k]) for k in keys if k in attrs}
 def odl(core,key):
  match=re.search(r'OBJECT\s*=\s*'+re.escape(key)+r'\s.*?VALUE\s*=\s*"([^"\n]+)"',core,re.S)
  return match.group(1) if match else None
 def raster_evidence(mask,qa):
  shape=tuple(mask.shape) if hasattr(mask,'shape') else tuple(mask.info()[2]);hist=np.zeros(256,dtype=np.int64);qsha=hashlib.sha256();msha=hashlib.sha256();read=0
  for row in range(0,shape[0],256):
   end=min(row+256,shape[0]);m=np.asarray(mask[row:end,:]);q=np.asarray(qa[row:end,:])
   if m.shape!=q.shape:raise ValueError('Mask/QA block mismatch')
   hist+=np.bincount(m.ravel(),minlength=256);msha.update(m.tobytes(order='C'));qsha.update(q.tobytes(order='C'));read+=m.size
  return {'shape':list(shape),'pixels_read':int(read),'mask_class_counts_entire_granule':{str(i):int(v) for i,v in enumerate(hist) if v},
          'mask_raw_array_sha256':msha.hexdigest(),'qa_raw_array_sha256':qsha.hexdigest(),'qa_bits_not_yet_interpreted':True}
 def coordinate_evidence(lat,lon):
  shape=tuple(lat.shape) if hasattr(lat,'shape') else tuple(lat.info()[2]);n=0;extent=None
  for row in range(0,shape[0],256):
   end=min(row+256,shape[0]);y=np.asarray(lat[row:end,:]);x=np.asarray(lon[row:end,:])
   selected=np.isfinite(x)&np.isfinite(y)&(x>=-72.782)&(x<=-72.218)&(y>=-37.226)&(y<=-36.774)
   if selected.any():
    values=[float(x[selected].min()),float(y[selected].min()),float(x[selected].max()),float(y[selected].max())]
    extent=values if extent is None else [min(extent[0],values[0]),min(extent[1],values[1]),max(extent[2],values[2]),max(extent[3],values[3])]
    n+=int(selected.sum())
  return {'shape':list(shape),'centers_inside_catalog_aoi_envelope':n,'inside_center_extent_lonlat':extent,
          'not_exact_footprint_or_valid_quality_area':True}
 raw_dir=Path(raw_dir);evidence_dir=Path(evidence_dir);acq=json.loads((evidence_dir/'acquisition.json').read_text());paths={k:ROOT/v['file'] for k,v in acq['files'].items()}
 if len(paths)!=4 or any(file_sha(p)!=acq['files'][k]['sha256'] for k,p in paths.items()):raise ValueError('Acquired file hash mismatch')
 result={'scope':'Technical read of one fixed candidate; no paired detection comparison, no G1 eligibility decision',
         'started_utc':datetime.now(timezone.utc).isoformat(),'downloaded_bytes':acq['downloaded_bytes'],'files_sha256':{k:file_sha(p) for k,p in paths.items()},'platforms':{}}
 mf=SD(str(paths['MYD14']),SDC.READ);mg=SD(str(paths['MYD03']),SDC.READ)
 try:
  attrs=mf.attributes();core=attrs.get('CoreMetadata.0','');pointer=str(attrs.get('MOD03 input file',''))
  m_mask=mf.select('fire mask');m_qa=mf.select('algorithm QA');lat=mg.select('Latitude');lon=mg.select('Longitude')
  shape=list(m_mask.info()[2]);geo_shape=list(lat.info()[2]);qa_shape=list(m_qa.info()[2]);geo_file=paths['MYD03'].name
  if shape!=geo_shape or shape!=qa_shape:raise ValueError('MODIS raster/geolocation shape mismatch')
  info={'fire_file':paths['MYD14'].name,'geo_file':geo_file,'input_pointer_geolocation_basename':Path(pointer).name,
        'input_pointer_exact_match':Path(pointer).name==geo_file,'same_shape':True,'shape':shape,
        'beginning_utc':str(odl(core,'RANGEBEGINNINGDATE'))+'T'+str(odl(core,'RANGEBEGINNINGTIME'))+'Z',
        'ending_utc':str(odl(core,'RANGEENDINGDATE'))+'T'+str(odl(core,'RANGEENDINGTIME'))+'Z',
        'automatic_quality_flag':odl(core,'AUTOMATICQUALITYFLAG'),'quality_flag_explanation':odl(core,'AUTOMATICQUALITYFLAGEXPLANATION'),
        'mask_attributes':chosen_attrs(m_mask.attributes()),'qa_attributes':chosen_attrs(m_qa.attributes()),
        'raster_read':raster_evidence(m_mask,m_qa),'coordinates':coordinate_evidence(lat,lon),'geometry_fields':{}}
  for name in ['SensorZenith','SensorAzimuth','SolarZenith','SolarAzimuth','gflags']:
   d=mg.select(name);info['geometry_fields'][name]={'shape':list(d.info()[2]),'attributes':chosen_attrs(d.attributes())};d.endaccess()
  for name in ['EV start time','EV center time']:
   d=mg.select(name);values=np.asarray(d[:]);info[name]={'values':len(values),'raw_min':float(values.min()),'raw_max':float(values.max()),'attributes':chosen_attrs(d.attributes()),'epoch_not_assumed_from_seconds_alone':True};d.endaccess()
  result['platforms']['Aqua']=info
 finally:mf.end();mg.end()
 with h5py.File(paths['VNP14IMG'],'r') as vf,h5py.File(paths['VNP03IMG'],'r') as vg:
  m=vf['fire mask'];q=vf['algorithm QA'];lat=vg['geolocation_data/latitude'];lon=vg['geolocation_data/longitude'];geo_file=paths['VNP03IMG'].name
  pointer=plain(vf.attrs.get('InputPointer',''));pointers=re.findall(r'VNP03IMG\.[A-Za-z0-9_.-]+\.nc',pointer)
  if m.shape!=q.shape or m.shape!=lat.shape or m.shape!=lon.shape:raise ValueError('VIIRS raster/geolocation shape mismatch')
  info={'fire_file':paths['VNP14IMG'].name,'geo_file':geo_file,'input_pointer_geolocation_basenames':pointers,
        'input_pointer_exact_match':geo_file in pointers,'same_shape':True,'shape':list(m.shape),
        'beginning_utc':plain(vg.attrs['time_coverage_start']),'ending_utc':plain(vg.attrs['time_coverage_end']),
        'mask_attributes':chosen_attrs(m.attrs),'qa_attributes':chosen_attrs(q.attrs),
        'raster_read':raster_evidence(m,q),'coordinates':coordinate_evidence(lat,lon),'geometry_fields':{}}
  for name in ['sensor_zenith','sensor_azimuth','solar_zenith','solar_azimuth','quality_flag']:
   d=vg['geolocation_data/'+name];info['geometry_fields'][name]={'shape':list(d.shape),'attributes':chosen_attrs(d.attrs)}
  for name in ['scan_start_time','scan_end_time','ev_mid_time']:
   d=vg['scan_line_attributes/'+name];values=d[:];info[name]={'values':len(values),'raw_min':float(values.min()),'raw_max':float(values.max()),'attributes':chosen_attrs(d.attrs)}
  result['platforms']['SNPP']=info
 a=result['platforms']['Aqua']['coordinates']['inside_center_extent_lonlat'];v=result['platforms']['SNPP']['coordinates']['inside_center_extent_lonlat']
 if a is not None and v is not None:
  intersection=[max(a[0],v[0]),max(a[1],v[1]),min(a[2],v[2]),min(a[3],v[3])]
  overlap=intersection[0]<intersection[2] and intersection[1]<intersection[3]
 else:intersection=None;overlap=False
 result.update(input_pointer_verified=all(x['input_pointer_exact_match'] for x in result['platforms'].values()),
   native_masks_qa_and_geolocation_read=True,geolocation_center_extent_overlap=overlap,overlapping_center_extents_lonlat=intersection,
   common_pixel_support_verified=False,full_algorithm_qa_bit_semantics_verified=False,gate1_passed=False,
   gate0_access_schema_passed=overlap and all(x['input_pointer_exact_match'] for x in result['platforms'].values()),gate0_full_scientific_eligibility_passed=False,
   limitations=['Overlap refers to extents of native geolocated centers in the fixed AOI, not equal footprints or quality-eligible area',
    'File-wide class counts are decoder checks, not AOI fire quantities or cross-sensor concordance',
    'Algorithm QA bit semantics require version-specific interpretation before G1',
    'MODIS automatic quality metadata is preserved; no favorable-quality decision is inferred from it'],
   code_sha256=file_sha(Path(__file__)))
 result['completed_utc']=datetime.now(timezone.utc).isoformat()
 (evidence_dir/'inspection.json').write_text(json.dumps(result,indent=2,allow_nan=False)+os.linesep);return result


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--token-file',type=Path,default=ROOT/'.runtime/secrets/earthdata-token')
 parser.add_argument('--raw-dir',type=Path,default=ROOT/'.runtime/observation-pilot/raw')
 parser.add_argument('--evidence-dir',type=Path,default=ROOT/'docs/reviews/evidence/observation-authenticated')
 parser.add_argument('--deadline-utc')
 parser.add_argument('--inspect-only',action='store_true')
 args=parser.parse_args()
 try:
  if args.inspect_only:
   result=inspect_files(args.raw_dir,args.evidence_dir)
   print(json.dumps({'gate0_access_schema_passed':result['gate0_access_schema_passed'],'gate1_passed':False,'downloaded_bytes':result['downloaded_bytes']}))
  else:
   if not args.deadline_utc:raise ValueError('Explicit download deadline required')
   limit=datetime.fromisoformat(args.deadline_utc.replace('Z','+00:00')).timestamp()
   result=run(args.token_file,args.raw_dir,args.evidence_dir,limit)
   print(json.dumps({'all_four_files_acquired':result['all_four_files_acquired'],'downloaded_bytes':result['downloaded_bytes'],'gate0_passed':False}))
 except Exception as error:
  # Deliberately omit exception strings, which may contain signed URLs.
  print(json.dumps({'status':'failed','error_class':type(error).__name__}))
  raise SystemExit(1)
