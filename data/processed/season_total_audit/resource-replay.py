"""One permitted resource replay; immutable scientific helper, output override only."""
import hashlib,json,pathlib,resource,subprocess,sys,datetime,platform

ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=ROOT/'data/processed/season_total_audit'
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def main():
    amendment=ROOT/'docs/reviews/evidence/issue48-assessment/resource-amendment.json'
    freeze={'wrapper_sha256':sha(__file__),'amendment_sha256':sha(amendment),
        'helper_sha256':sha(ROOT/'pipeline/season_total_audit.py'),
        'code_freeze_sha256':sha(OUT/'code-freeze.json'),
        'attempt01_manifest_sha256':sha(OUT/'manifest.json'),
        'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'output_override':'data/processed/season_total_audit/attempt-02',
        'resource_api':'resource.getrusage(RUSAGE_CHILDREN).ru_maxrss; Darwin bytes'}
    need(freeze['helper_sha256']=='9cf6d85d7ff73b872c7143aae2ac1708d2f9aae3cde46a318d08580b9bfd52f6','Source helper changed')
    need(freeze['attempt01_manifest_sha256']=='40f2bed44132991636d0483d8dbafb9eb8045a4a8be81f026d69a07d51cf1e8b','Original manifest changed')
    if '--freeze-only' in sys.argv:
        need(not (OUT/'resource-replay-freeze.json').exists(),'Replay already frozen')
        (OUT/'resource-replay-freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
        print(json.dumps(freeze));return
    prior=json.loads((OUT/'resource-replay-freeze.json').read_text())
    for k in freeze:
        if k!='created_utc':need(freeze[k]==prior[k],'Replay freeze changed: '+k)
    need(platform.system()=='Darwin','RSS units only validated for Darwin')
    need(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss==0,'Parent already has child RSS history')
    attempt=OUT/'attempt-02';need(not attempt.exists(),'No third attempt/overwrite')
    attempt.mkdir();(attempt/'code-freeze.json').write_bytes((OUT/'code-freeze.json').read_bytes())
    child="""import importlib.util,pathlib,sys
root=pathlib.Path(sys.argv[1]);spec=importlib.util.spec_from_file_location('audit42',root/'pipeline/season_total_audit.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.OUT=root/'data/processed/season_total_audit/attempt-02'
sys.argv=['season_total_audit.py','--protocol',str(root/'docs/reviews/2026-11-15-season-total-protocol.md'),'--protocol-sha256','41734018c7a516444053c7042d08b4d813c87e01cb1f24d3cb6e998ad91d0646'];m.main()
"""
    proc=subprocess.run([sys.executable,'-c',child,str(ROOT)],capture_output=True,text=True)
    rss=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    envelope={'status':'PENDING','completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'Darwin_peak_RSS_bytes':rss,'RSS_cap_bytes':1073741824,'child_returncode':proc.returncode,'wrapper_freeze_sha256':sha(OUT/'resource-replay-freeze.json'),'attempt01_RSS_still_unknown':True,'fits':0,'downloads':0}
    (OUT/'resource-attempt-02.json').write_text(json.dumps(envelope,indent=2)+'\n')
    need(proc.returncode==0,'Frozen helper failed: '+proc.stderr[-1000:])
    need(rss>0 and rss<=1073741824,'RSS unknown or above cap')
    need(sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<5*1024*1024,'All-attempt output cap exceeded')
    for name in ['season-totals.csv','monthly-controls.csv','per-cut.csv']:
        need((OUT/name).read_bytes()==(attempt/name).read_bytes(),'Numeric CSV byte mismatch: '+name)
    a=json.loads((OUT/'summary.json').read_text());b=json.loads((attempt/'summary.json').read_text())
    a.pop('completed_utc');b.pop('completed_utc');need(a==b,'Summary numeric/value mismatch')
    envelope.update(status='PASS',numeric_CSV_byte_identity=True,summary_identity_except_completion_time=True,all_attempt_output_bytes=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file()),attempt02_manifest_sha256=sha(attempt/'manifest.json'))
    (OUT/'resource-attempt-02.json').write_text(json.dumps(envelope,indent=2)+'\n')
    print(json.dumps(envelope))
if __name__=='__main__':main()
