"""Read-only portable replay of the existing study39 loss snapshots.

The piecewise CDF integral follows the archived39 peer's algorithm, with shared
provenance; this is not a third independent oracle. No CDF reconstruction, fits,
solvers, downloads, private runtime files, wall-clock gates or output writes.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
MANIFEST_SHA256='aec1533e33b1d354c6102daf51d51d295d449f2afc15cf5ae50d2fe9719779ea'
GATES_SHA256='218627f14acfc4834ac3d92360df4ee15d64354c8f49ef07428901e58d23ae42'
FROZEN_GATES=ROOT/'docs/reviews/evidence/crps-portable-inputs/gates39.csv'
REGIMES={'08_forward','08_backward','16_forward','16_backward'}
KEYS=['regime','cut','season','m']
IDENTITY=['row_id',*KEYS,'g','aqua','role','B','F21_median','F21_mean','original_E11_mean','model_sha256','original_weight_sum']

def require(condition,message):
    if not bool(condition):raise ValueError(message)
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def near(a,b,label):
    if a is None or b is None:require(a is None and b is None,label+': null mismatch')
    else:require(math.isfinite(float(a)) and math.isfinite(float(b)) and math.isclose(float(a),float(b),rel_tol=1e-11,abs_tol=1e-9),label+': numeric mismatch')
def verify_identity(record,roster):
    for name in IDENTITY:require(record[name]==roster[name],'CDF/roster identity mismatch: '+name)
def check_distribution(record):
    x=np.asarray(record['atoms'],dtype=float);w=np.asarray(record['original_weights'],dtype=float);wn=np.asarray(record['normalized_weights'],dtype=float)
    require(x.ndim==1 and len(x)>0 and w.shape==x.shape and wn.shape==x.shape,'CDF shape/empty support')
    require(np.isfinite(x).all() and np.isfinite(w).all() and np.isfinite(wn).all(),'Nonfinite CDF atom/weight')
    require((x>=0).all() and (w>=0).all() and (wn>=0).all(),'Negative CDF atom/weight')
    total=math.fsum(map(float,w));require(total>0 and abs(total-1)<=1e-12,'Original weights not normalized within1e-12')
    expected=np.asarray([float(a)/total for a in w]);require(np.array_equal(expected,wn),'Weights differ from exactly one original-fsum division')
    require(abs(math.fsum(map(float,wn))-1)<=1e-12,'Stored normalized weights invalid')
    near(total,record['original_weight_sum'],'original weight sum')
    near(math.fsum(float(a)*float(b) for a,b in zip(x,wn)),record['F21_mean'],'Frozen mean')
    return x,wn

def integral_crps(atoms,normalized_weights,y,cache):
    """Same direct interval-integral semantics as39peer; no normalization."""
    token=hashlib.sha256(atoms.tobytes()+normalized_weights.tobytes()).digest()
    if token not in cache:
        knots=np.unique(atoms)
        cdf=np.asarray([math.fsum(map(float,normalized_weights[atoms<=k])) for k in knots])
        cache[token]=(knots,cdf)
    knots,cdf=cache[token];cuts=np.unique(np.r_[knots,float(y)]);parts=[]
    for left,right in zip(cuts,cuts[1:]):
        index=int(np.searchsorted(knots,left,side='right'))-1;prob=float(cdf[index]) if index>=0 else 0.
        parts.append(float(right-left)*(prob-int(y<=left))**2)
    return math.fsum(parts)

def metric(frame,f21='CRPS_F21'):
    delta=frame[f21]-frame.CRPS_delta_B
    return {'n':len(frame),'forecasts':{name:{'sum_CRPS':math.fsum(map(float,frame[col])),'mean_CRPS':float(frame[col].mean()) if len(frame) else None} for name,col in [('F21',f21),('delta_B','CRPS_delta_B')]},'mean_difference_F21_minus_delta_B':float(delta.mean()) if len(frame) else None}
def compare_metric(actual,recorded,label):
    require(actual['n']==recorded['n'],label+': population size')
    near(actual['mean_difference_F21_minus_delta_B'],recorded['mean_difference_F21_minus_delta_B'],label+' difference')
    for name in ['F21','delta_B']:
        for field in ['sum_CRPS','mean_CRPS']:near(actual['forecasts'][name][field],recorded['forecasts'][name][field],label+' '+name+' '+field)

def published_cuts(gates,code_freeze,cuts):
    expected=code_freeze['protected_sha256'].get('data/processed/gates.csv')
    require(expected==GATES_SHA256,'Public gates not anchored in39 snapshot')
    require(sha(gates)==expected,'Public gates hash mismatch')
    enabled=set();seen=set()
    with Path(gates).open(newline='') as f:
        reader=csv.reader(f);header=next(reader);position=header.index('enabled')
        for row in reader:
            cut=row[0];require(cut not in seen and cut in cuts,'Duplicate/unknown public gate CUT');seen.add(cut)
            require(row[position] in {'True','False'},'Invalid enabled gate value')
            if row[position]=='True':enabled.add(cut)
    require(seen==cuts and len(enabled)==14,'Published14/remaining40 domain mismatch')
    return enabled

def verify(evidence_dir,gates_file):
    p=Path(evidence_dir)
    require(sha(p/'manifest.json')==MANIFEST_SHA256,'Study39 manifest anchor hash mismatch')
    manifest=json.loads((p/'manifest.json').read_text())
    for name,h in manifest['output_sha256'].items():
        require(Path(name).name==name,'Unsafe snapshot filename')
        require(sha(p/name)==h,'Snapshot hash mismatch: '+name)
    require(manifest['exported_query_rows']==10368 and manifest['atom_elements']==444826,'Manifest scope mismatch')
    for field in ['fits','solvers','science_downloads']:require(manifest[field]==0,'Original forbidden action counter nonzero')
    summary=json.loads((p/'summary.json').read_text());checkpoint=json.loads((p/'checkpoint.json').read_text());code_freeze=json.loads((p/'code-freeze.json').read_text())
    require(checkpoint['CDF_snapshot_sha256']==sha(p/'forecast-CDFs.jsonl.gz') and checkpoint['roster_sha256']==sha(p/'forecast-roster.parquet'),'Pre-response snapshot linkage mismatch')
    roster=pd.read_parquet(p/'forecast-roster.parquet');scored=pd.read_parquet(p/'scored-queries.parquet')
    require(len(roster)==10368 and len(scored)==10368,'Roster/scored row count mismatch')
    for name,frame in [('roster',roster),('scored',scored)]:
        require(not frame.duplicated(KEYS).any(),name+': duplicate row keys')
        require(np.array_equal(frame.row_id,np.arange(10368)),name+': row_id order/domain mismatch')
        require(set(frame.regime)==REGIMES,name+': regime domain mismatch')
    require(roster.equals(scored[list(roster.columns)]),'Scored GEO/forecast identity differs from frozen roster')
    cuts=set(roster.cut);require(len(cuts)==54 and sum(c.startswith('08') for c in cuts)==33 and sum(c.startswith('16') for c in cuts)==21,'CUT54 domain mismatch')
    for regime,frame in roster.groupby('regime'):
        source,direction=regime.split('_');seasons=range(2016,2020) if direction=='forward' else range(2012,2016)
        expected={(c,s,m) for c in cuts for s in seasons for m in range(1,13)}
        require(set(frame[['cut','season','m']].itertuples(index=False,name=None))==expected,'Incomplete CUT/month/regime roster')
        for row in frame.itertuples(index=False):
            require(row.role==('SOURCE' if row.cut.startswith(source) else 'held'),'Frozen SOURCE/held role mismatch')
            require(row.g==('JJA' if row.m in [6,7,8] else str(row.m)),'Calendar group mismatch')
    require(np.isfinite(scored.snpp).all() and (scored.snpp>=0).all(),'Invalid frozen recorded response')
    require((scored.groupby(['cut','season','m']).snpp.nunique()==1).all() and (scored.groupby(['cut','season','m']).size()==2).all(),'Frozen repeated response inconsistent')
    cache={};count=0;atom_count=0;max_error=0.;clamps=0;integrals=[]
    roster_records=roster.to_dict('records');scored_records=scored.to_dict('records')
    with gzip.open(p/'forecast-CDFs.jsonl.gz','rt') as stream:
        for line in stream:
            record=json.loads(line);require(count<10368,'Too many frozen CDF rows');verify_identity(record,roster_records[count]);x,w=check_distribution(record)
            row=scored_records[count];y=float(row['snpp']);value=integral_crps(x,w,y,cache);eabsx=math.fsum(float(a)*abs(float(b)) for a,b in zip(w,x));tau=1e-10*max(1.,abs(y),eabsx)
            raw=float(row['F21_raw_score']);error=abs(value-raw);max_error=max(max_error,error);require(error<=tau,'Integral differs from recorded raw CRPS beyond frozen tolerance')
            baseline=abs(float(record['B'])-y)
            require(float(row['CRPS_delta_B'])==baseline and float(row['delta_B_MAE'])==baseline,'DeltaB != abs(B-Y)')
            require(abs(integral_crps(np.asarray([record['B']],float),np.asarray([1.]),y,cache)-baseline)<=tau,'Degenerate CDF integral != MAE')
            near(tau,row['F21_tolerance'],'Frozen roundoff tolerance');near(eabsx,row['F21_EabsX'],'Frozen EabsX')
            eabs=math.fsum(float(a)*abs(float(b)-y) for a,b in zip(w,x));near(eabs,row['F21_Eabs'],'Frozen Eabs')
            near(math.fsum([float(row['F21_Eabs']),-float(row['F21_half_pair_term'])]),raw,'Recorded CRPS decomposition')
            require(raw>=-tau,'Negative CRPS beyond frozen tolerance');clamped=raw<0
            require(bool(row['F21_negative_roundoff_clamped'])==clamped and float(row['CRPS_F21'])==(0. if clamped else raw),'Recorded clamping differs from policy')
            clamps+=int(clamped);integrals.append(value);atom_count+=len(x);count+=1
    require(count==10368 and atom_count==444826,'Frozen CDF/atom count mismatch')
    require(clamps==summary['negative_roundoff_clamped_rows'],'Clamp count mismatch')
    scored['replayed_integral_F21']=integrals
    enabled=published_cuts(gates_file,code_freeze,cuts);populations=0;primary=[];integral_primary=[];percut=pd.read_csv(p/'per-CUT.csv',dtype={'cut':str});primarycsv=pd.read_csv(p/'primary-contrasts.csv')
    require(len(percut)==216 and not percut.duplicated(['regime','cut']).any(),'Per-CUT table keys mismatch')
    require(len(primarycsv)==4 and set(primarycsv.regime)==REGIMES,'Primary table regime keys mismatch')
    for regime,frame in scored.groupby('regime',sort=True):
        groups={'all54':frame,'SOURCE':frame[frame.role=='SOURCE'],'held':frame[frame.role=='held'],'published14':frame[frame.cut.isin(enabled)],'remaining40':frame[~frame.cut.isin(enabled)]}
        for role in ['SOURCE','held']:
            for name,mask in [('published14',frame.cut.isin(enabled)),('remaining40',~frame.cut.isin(enabled))]:groups[role+'_'+name]=frame[(frame.role==role)&mask]
        for name,group in groups.items():
            strata={'all_months':group,'zero_reference':group[group.snpp==0],'positive_reference':group[group.snpp>0],'aqua_zero_reference_positive':group[(group.aqua==0)&(group.snpp>0)],'both_zero':group[(group.aqua==0)&(group.snpp==0)],'reference_50_plus':group[group.snpp>=50]}
            for label,sub in strata.items():compare_metric(metric(sub),summary['reports'][regime][name][label],regime+'/'+name+'/'+label);populations+=1
        held=groups['held'];m=metric(held);claim=next(q for q in summary['primary']['regimes'] if q['regime']==regime);recorded=primarycsv[primarycsv.regime==regime].iloc[0]
        values={'n':len(held),'mean_CRPS_F21':m['forecasts']['F21']['mean_CRPS'],'mean_CRPS_delta_B':m['forecasts']['delta_B']['mean_CRPS'],'difference_F21_minus_delta_B':m['mean_difference_F21_minus_delta_B']}
        for field,value in values.items():near(value,claim[field],'Primary summary '+field);near(value,recorded[field],'Primary CSV '+field)
        delta=float((held.replayed_integral_F21-held.CRPS_delta_B).mean());near(delta,values['difference_F21_minus_delta_B'],'Integral primary');primary.append({'regime':regime,**values});integral_primary.append(delta)
        for cut,sub in frame.groupby('cut'):
            row=percut[(percut.regime==regime)&(percut.cut==cut)].iloc[0];m=metric(sub);require(row.n==len(sub),'Per-CUT n mismatch')
            for forecast in ['F21','delta_B']:near(m['forecasts'][forecast]['mean_CRPS'],row['mean_CRPS_'+forecast],'Per-CUT '+forecast)
            near(m['mean_difference_F21_minus_delta_B'],row.difference,'Per-CUT difference')
        original_mae={cut:float(sub.CRPS_delta_B.mean()) for cut,sub in held.groupby('cut')};worst=min(original_mae,key=lambda c:(-original_mae[c],c));claim=next(q for q in summary['worst_CUT_fixed_from_original_B_MAE'] if q['regime']==regime)
        require(worst==claim['cut'],'Worst originalB heldCUT identity mismatch');compare_metric(metric(frame[frame.cut==worst]),claim['metrics'],'Worst frozenCUT')
    equal=float(np.mean([r['difference_F21_minus_delta_B'] for r in primary]));weighted=sum(r['difference_F21_minus_delta_B']*r['n'] for r in primary)/sum(r['n'] for r in primary)
    near(equal,summary['primary']['equal_four_difference'],'Equal-four primary');near(weighted,summary['primary']['row_weighted_difference'],'Weighted secondary');near(float(np.mean(integral_primary)),equal,'Integral equal-four primary')
    require(populations==216,'Population report scope mismatch')
    # Re-check immutable sources after replay. No write path exists in this tool.
    require(sha(p/'manifest.json')==MANIFEST_SHA256 and sha(gates_file)==GATES_SHA256,'Anchored input changed during verification')
    for name,h in manifest['output_sha256'].items():require(sha(p/name)==h,'Snapshot changed during verification: '+name)
    return {'status':'PASS','scope':'Replay frozen39 CDF loss snapshots plus historical anchored gate membership; no original fit reconstruction','manifest_sha256':MANIFEST_SHA256,'CDF_rows':count,'atom_elements':atom_count,'weights_single_normalization_verified':True,'CRPS_integral_rows':count,'deltaB_equals_MAE_rows':count,'population_reports_verified':populations,'method_report_sets_verified':populations*2,'per_CUT_rows_verified':len(percut),'primary_regimes':4,'primary_equal_four_difference':equal,'max_abs_integral_vs_recorded_raw_CRPS':max_error,'shared_oracle_provenance':'Archived39peer direct CDF-integral semantics; not a third independent oracle','fits':0,'solvers':0,'downloads':0,'new_CDFs_or_predictions':0,'new_loss_definitions':0,'same_frozen_loss_replay_only':True,'original_files_written':0,'private_runtime_or_absolute_clock_dependency':False,'physical_G1_claim':False}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--evidence-dir',type=Path,default=ROOT/'data/processed/crps_audit');parser.add_argument('--gates-file',type=Path,default=FROZEN_GATES);args=parser.parse_args()
    try:result=verify(args.evidence_dir,args.gates_file)
    except (OSError,KeyError,TypeError,IndexError,StopIteration) as exc:raise ValueError('Incomplete or invalid frozen evidence: '+str(exc)) from exc
    print(json.dumps(result,sort_keys=True,allow_nan=False))
if __name__=='__main__':main()
