"""Public-metadata preflight for the fixed Aqua/S-NPP observation pilot.

This does not decode fire masks, certify clear-sky opportunity, or pass G0/G1.
CMR intervals define conservative time bounds, not per-pixel acquisition times.
No credentials are used; optional data probes stop at redirects and read <=1KiB.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import netrc
import os
from pathlib import Path
import re
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen

ROOT = Path(__file__).resolve().parents[1]
CMR = 'https://cmr.earthdata.nasa.gov/search/'
PRODUCTS = {
 'MYD14': {'concept_id':'C2278858993-LPCLOUD','version':'061'},
 'MYD03': {'concept_id':'C1379841358-LAADS','version':'6.1'},
 'VNP14IMG': {'concept_id':'C2734202914-LPCLOUD','version':'002'},
 'VNP03IMG': {'concept_id':'C2105092163-LAADS','version':'2'},
}
TEMPORAL = '2019-01-01T00:00:00Z,2019-01-15T23:59:59Z'
# Conservative catalog envelope of the proposed 50km AOI, not pixel coverage.
BBOX = '-72.782,-37.226,-72.218,-36.774'
WINDOWS = (5,10,15,30,60)
MAX_PROBE_BYTES = 1024


def sha(data): return hashlib.sha256(data).hexdigest()


def public_url(value):
    """Never persist URL userinfo, query credentials or redirect OAuth state."""
    p=urlsplit(value)
    host=p.hostname or ''
    if p.port: host += ':'+str(p.port)
    return urlunsplit((p.scheme,host,p.path,'',''))


def scrub_links(value):
    if isinstance(value,list):return [scrub_links(v) for v in value]
    if isinstance(value,dict):return {k:(public_url(v) if k in {'href','url'} and isinstance(v,str) else scrub_links(v)) for k,v in value.items()}
    return value


def utc(value):
    result=datetime.fromisoformat(value.replace('Z','+00:00'))
    if result.tzinfo is None:raise ValueError('Acquisition time needs timezone')
    return result


def interval_bounds(a,b):
    a0,a1=utc(a['time_start']),utc(a['time_end'])
    b0,b1=utc(b['time_start']),utc(b['time_end'])
    if a1<a0 or b1<b0:raise ValueError('Reversed acquisition interval')
    minimum=max(0.,(a0-b1).total_seconds(),(b0-a1).total_seconds())/60
    maximum=max(abs((a0-b1).total_seconds()),abs((a1-b0).total_seconds()))/60
    return minimum,maximum


def time_state(minimum,maximum,window):
    if maximum<=window:return 'definitely_within'
    if minimum>window:return 'definitely_outside'
    return 'uncertain'


def acquisition_key(entry):
    match=re.match(r'^[^.]+\.A(\d{7})\.(\d{4})\.',entry['producer_granule_id'])
    if not match:raise ValueError('Unexpected producer identifier')
    return match.groups()


def candidate_pairs(aqua,viirs):
    pairs=[]
    for a in sorted(aqua,key=lambda e:e['producer_granule_id']):
        for v in sorted(viirs,key=lambda e:e['producer_granule_id']):
            minimum,maximum=interval_bounds(a,v)
            if minimum>60:continue
            pairs.append({'aqua_id':a['producer_granule_id'],'viirs_id':v['producer_granule_id'],
                'aqua_concept_id':a['id'],'viirs_concept_id':v['id'],
                'aqua_start':a['time_start'],'aqua_end':a['time_end'],
                'viirs_start':v['time_start'],'viirs_end':v['time_end'],
                'minimum_possible_gap_minutes':minimum,'maximum_possible_gap_minutes':maximum,
                'time_states':{str(w):time_state(minimum,maximum,w) for w in WINDOWS}})
    return pairs


def query(endpoint,parameters):
    url=CMR+endpoint+'?'+urlencode(parameters)
    request=Request(url,headers={'Accept':'application/json','User-Agent':'GOLIAT-observation-preflight/1.0'})
    with urlopen(request,timeout=30) as response:
        raw=response.read();hits=response.headers.get('CMR-Hits')
    return json.loads(raw),int(hits) if hits is not None else None,url


def fetch_granules(concept,fetch=query):
    entries=[];requests=[];expected=None
    for page in range(1,11):
        payload,hits,url=fetch('granules.json',{'collection_concept_id':concept,'temporal':TEMPORAL,
            'bounding_box':BBOX,'page_size':2000,'page_num':page,'sort_key':'start_date'})
        batch=payload['feed']['entry'];entries.extend(batch);requests.append(url)
        if expected is None:expected=hits
        elif hits is not None and hits!=expected:raise ValueError('CMR hits changed while paginating')
        if len({e['id'] for e in entries})!=len(entries):raise ValueError('Duplicate CMR granule IDs')
        if len(batch)<2000:
            if expected is not None and len(entries)!=expected:raise ValueError('Incomplete CMR pagination')
            return entries,requests,expected
    raise ValueError('CMR page limit reached; refusing incomplete inventory')


def credential_presence():
    env_keys=('EARTHDATA_USERNAME','EARTHDATA_PASSWORD','EARTHDATA_TOKEN','EDL_TOKEN','LAADS_TOKEN')
    result={'environment':{k:bool(os.environ.get(k)) for k in env_keys},'earthdata_netrc_entry':False,'laads_netrc_entry':False}
    try:
        parsed=netrc.netrc()
        result['earthdata_netrc_entry']=bool(parsed.authenticators('urs.earthdata.nasa.gov'))
        result['laads_netrc_entry']=bool(parsed.authenticators('ladsweb.modaps.eosdis.nasa.gov'))
    except (OSError,netrc.NetrcParseError):pass
    return result


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):return None


def probe(entry):
    links=[x for x in entry.get('links',[]) if x.get('rel','').endswith('/data#') and x.get('href','').startswith('https://')]
    native=[x for x in links if (urlsplit(x['href']).hostname or '').startswith('data.')]
    if not native:return {'status':'no_native_https_link','bytes_read':0}
    url=public_url(native[0]['href']);started=time.monotonic()
    result={'url':url,'anonymous_only':True,'redirects_followed':False,'bytes_read':0,'full_product_read':False}
    opener=build_opener(NoRedirect())
    try:
        request=Request(url,headers={'Range':'bytes=0-1023','User-Agent':'GOLIAT-observation-preflight/1.0'})
        with opener.open(request,timeout=30) as response:
            body=response.read(MAX_PROBE_BYTES)
            result.update(http_status=response.status,content_type=response.headers.get('Content-Type'),bytes_read=len(body),
                hdf_signature=body.startswith(b'\x0e\x03\x13\x01') or body.startswith(b'\x89HDF\r\n\x1a\n'),
                content_range=response.headers.get('Content-Range'))
    except HTTPError as error:
        result.update(http_status=error.code,status='http_error_or_redirect')
        if error.headers.get('Location'):result['redirect_location']=public_url(error.headers['Location'])
    except (URLError,TimeoutError,OSError) as error:
        result.update(status='transport_error',error_class=type(error).__name__)
    result['seconds']=round(time.monotonic()-started,3)
    return result


def run(output,perform_probe=False):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);all_entries={};source_requests={};collections={}
    for name,spec in PRODUCTS.items():
        collection,_,url=query('collections.json',{'concept_id':spec['concept_id'],'page_size':10})
        selected=collection['feed']['entry']
        if len(selected)!=1 or selected[0]['short_name']!=name or selected[0]['version_id']!=spec['version']:
            raise ValueError('Pinned collection identity changed: '+name)
        collections[name]=scrub_links(collection)
        all_entries[name],urls,hits=fetch_granules(spec['concept_id'])
        source_requests[name]=[url,*urls]
        (output/(name+'-collections.json')).write_text(json.dumps(collections[name],indent=2)+'\n')
        (output/(name+'-granules.json')).write_text(json.dumps(scrub_links(all_entries[name]),indent=2)+'\n')
        print(name,'metadata granules',len(all_entries[name]),'CMR hits',hits,flush=True)
    day={name:[e for e in entries if e.get('day_night_flag')=='DAY'] for name,entries in all_entries.items()}
    pairs=candidate_pairs(day['MYD14'],day['VNP14IMG']);stats={}
    for w in WINDOWS:
        counted=Counter(p['time_states'][str(w)] for p in pairs)
        stats[str(w)]={k:counted.get(k,0) for k in ['definitely_within','uncertain','definitely_outside']}
        stats[str(w)]['distinct_aqua_dates_definitely_within']=sorted({p['aqua_start'][:10] for p in pairs if p['time_states'][str(w)]=='definitely_within'})
    association={}
    for fire,geo in [('MYD14','MYD03'),('VNP14IMG','VNP03IMG')]:
        geokeys=Counter(acquisition_key(e) for e in all_entries[geo])
        association[fire]={'fire_granules':len(all_entries[fire]),'same_acquisition_id_geolocation_matches':sum(geokeys[acquisition_key(e)]==1 for e in all_entries[fire]),
            'note':'Identifier/date-time association only; InputPointer, dimensions and actual pixel compatibility not read.'}
    selected=next((p for p in pairs if p['time_states']['10']=='definitely_within'),None);probes={}
    if perform_probe and selected:
        identifiers={'MYD14':selected['aqua_id'],'VNP14IMG':selected['viirs_id']}
        for fire,geo in [('MYD14','MYD03'),('VNP14IMG','VNP03IMG')]:
            f=next(e for e in all_entries[fire] if e['producer_granule_id']==identifiers[fire])
            g=next((e for e in all_entries[geo] if acquisition_key(e)==acquisition_key(f)),None)
            for name,e in [(fire,f),(geo,g)]:
                if e:probes[name]=probe(e)
    summary={'scope':'Catalog and anonymous access preflight; no fire outcomes inspected','started_or_completed_utc':datetime.now(timezone.utc).isoformat(),
        'aoi':{'proposal':'50x50km centered37S72.5W','catalog_bbox':BBOX,'bbox_is_envelope_not_pixel_coverage':True},'temporal':TEMPORAL,
        'pinned_collections':PRODUCTS,'credentials_used':False,'credential_presence':credential_presence(),
        'inventory':{name:{'granules':len(entries),'metadata_day_flags':dict(Counter(e.get('day_night_flag','UNKNOWN') for e in entries)),
            'sum_cmr_granule_size_metadata':sum(float(e.get('granule_size',0)) for e in entries),
            'size_note':'CMR granule_size field convention; catalog size, not measured download bytes.'} for name,entries in all_entries.items()},
        'geolocation_identifier_associations':association,'daytime_metadata_candidates_minimum_gap_le60':len(pairs),'window_counts':stats,
        'candidate_counts_are_not_independent_passes_or_valid_observations':True,'chosen_probe_pair':selected,'anonymous_probes':probes,
        'gate0_passed':False,'gate1_passed':False,'full_qa_geolocation_read':False,
        'limitations':['No authenticated data access verified','No full masks/geolocation decoded; no observation-quality denominator',
            'Granule footprints only intersect catalog AOI envelope; actual common pixel support unknown',
            'Many-to-many granule candidates are not analytical pairs or independent days/episodes',
            'Acquisition intervals are metadata bounds, not pixel acquisition instants',
            'DAY is a granule metadata flag, not verified local pixel day/night QA','2019 is development, not new predictive holdout'],
        'source_requests':source_requests}
    (output/'candidate_pairs.json').write_text(json.dumps(pairs,indent=2)+'\n')
    (output/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    manifest={'producer':'observation_preflight','source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'code_sha256':sha(Path(__file__).read_bytes()),'products_and_metadata_only':True,
        'output_sha256':{p.name:sha(p.read_bytes()) for p in sorted(output.glob('*.json')) if p.name!='manifest.json'}}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'docs/reviews/evidence/observation-preflight')
    parser.add_argument('--probe',action='store_true',help='Anonymous1KiB probes of one candidate and auxiliaries; no redirects/auth')
    args=parser.parse_args();result=run(args.output_dir,args.probe)
    print(json.dumps({'gate0_passed':result['gate0_passed'],'counts':result['window_counts'],'probes':result['anonymous_probes']},indent=2))
