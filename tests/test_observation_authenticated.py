import io
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from observation_authenticated import auth_headers,permitted,safe_url,download,ROOT

NASA='https://data.lpdaac.earthdatacloud.nasa.gov/file.hdf'
CDN='https://d1nklfio7vscoe.cloudfront.net/file.hdf?Signature=UNIT_TEST_SIGNATURE'
TOKEN='UNIT_TEST_FAKE_CREDENTIAL'

class Response(io.BytesIO):
 def __init__(self,data,length=True):
  super().__init__(data);self.status=200;self.headers={'Content-Type':'application/octet-stream'}
  if length:self.headers['Content-Length']=str(len(data))

class AuthenticatedObservationTests(unittest.TestCase):
 def test_authentication_is_only_attached_to_exact_nasa_hosts(self):
  self.assertIn('Authorization',auth_headers(NASA,TOKEN))
  self.assertNotIn('Authorization',auth_headers(CDN,TOKEN))
  self.assertNotIn('Authorization',auth_headers('https://bucket.s3.us-west-2.amazonaws.com/file',TOKEN))
  for url in ['http://data.lpdaac.earthdatacloud.nasa.gov/file','https://data.lpdaac.earthdatacloud.nasa.gov.evil.test/file','https://user:password@data.lpdaac.earthdatacloud.nasa.gov/file']:
   self.assertFalse(permitted(url))
   with self.assertRaises(ValueError):auth_headers(url,TOKEN)

 def test_redirect_does_not_forward_bearer_or_persist_signed_query(self):
  seen=[];payload=b'\x89HDF\r\n\x1a\n'+b'data'*10
  class Opener:
   def open(self,request,timeout):
    seen.append(request)
    if len(seen)==1:raise HTTPError(NASA,303,'redirect',{'Location':CDN},None)
    return Response(payload)
  (ROOT/'.runtime').mkdir(exist_ok=True)
  with tempfile.TemporaryDirectory(dir=ROOT/'.runtime') as directory:
   with patch('observation_authenticated.build_opener',return_value=Opener()):
    result,spent=download(NASA,Path(directory)/'file.nc',TOKEN,1000,time.time()+60)
  self.assertEqual(result['status'],'downloaded');self.assertEqual(spent,len(payload))
  self.assertIsNotNone(seen[0].get_header('Authorization'));self.assertIsNone(seen[1].get_header('Authorization'))
  persisted=json.dumps(result);self.assertNotIn(TOKEN,persisted);self.assertNotIn('UNIT_TEST_SIGNATURE',persisted)
  self.assertEqual(safe_url(CDN),'https://d1nklfio7vscoe.cloudfront.net/file.hdf')

 def test_unannounced_body_never_reads_beyond_budget(self):
  response=Response(b'\x89HDF\r\n\x1a\n'+b'x'*200,length=False)
  class Opener:
   def open(self,*args,**kwargs):return response
  (ROOT/'.runtime').mkdir(exist_ok=True)
  with tempfile.TemporaryDirectory(dir=ROOT/'.runtime') as directory:
   with patch('observation_authenticated.build_opener',return_value=Opener()):
    result,spent=download(NASA,Path(directory)/'file.nc',TOKEN,32,time.time()+60)
  self.assertEqual(result['status'],'download_failed');self.assertEqual(spent,32)

 def test_cached_html_is_not_accepted_as_science_file(self):
  (ROOT/'.runtime').mkdir(exist_ok=True)
  with tempfile.TemporaryDirectory(dir=ROOT/'.runtime') as directory:
   path=Path(directory)/'file.hdf';path.write_text('<html>login</html>')
   result,spent=download(NASA,path,TOKEN,1000,time.time()+60)
  self.assertEqual(result['status'],'invalid_existing_file');self.assertEqual(spent,0)

if __name__=='__main__':unittest.main()
