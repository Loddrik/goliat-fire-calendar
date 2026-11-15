"""Aggregate existing fixed-mask LOSO monthly predictions; no fitting."""
from __future__ import annotations
import argparse, hashlib, json, math, platform
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/processed'
OUT = DATA / 'season_total_audit'

def require(condition, message):
    if not bool(condition):
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def totals(months, methods):
    rows = []
    for (cut, season), frame in months.groupby(['cut', 'season'], sort=True):
        require(len(frame) == 12 and set(frame.m) == set(range(1, 13)), 'Incomplete monthly season')
        y = math.fsum(map(float, frame.snpp))
        for method in methods:
            prediction = math.fsum(map(float, frame[method]))
            error = prediction - y
            rows.append(dict(cut=cut, season=int(season), method=method, n_months=12,
                observed_total=y, predicted_total=prediction, signed_error=error,
                absolute_error=abs(error), signed_relative_error=error/y if y>0 else None,
                absolute_relative_error=abs(error)/y if y>0 else None,
                relative_error_defined=y>0))
    return pd.DataFrame(rows)

def summarize(frame):
    positive = frame[frame.observed_total > 0]
    target = math.fsum(map(float, frame.observed_total))
    return dict(n_cut_seasons=len(frame), n_positive_target=len(positive), n_zero_target=int((frame.observed_total==0).sum()),
        n_zero_target_zero_prediction=int(((frame.observed_total==0)&(frame.predicted_total==0)).sum()),
        n_zero_target_positive_prediction=int(((frame.observed_total==0)&(frame.predicted_total>0)).sum()),
        season_mae=float(frame.absolute_error.mean()), mean_signed_error=float(frame.signed_error.mean()),
        season_mare=float(positive.absolute_relative_error.mean()) if len(positive) else None,
        season_median_ape=float(positive.absolute_relative_error.median()) if len(positive) else None,
        season_bias_rel=float(positive.signed_relative_error.mean()) if len(positive) else None,
        season_wape=math.fsum(map(float, frame.absolute_error))/target if target>0 else None,
        aggregate_relative_bias=math.fsum(map(float, frame.signed_error))/target if target>0 else None,
        observed_total=target, predicted_total=math.fsum(map(float, frame.predicted_total)),
        seasons_underpredicted=int((frame.signed_error<0).sum()),
        min_signed_relative_error=float(positive.signed_relative_error.min()) if len(positive) else None,
        max_signed_relative_error=float(positive.signed_relative_error.max()) if len(positive) else None)

def stamp():
    return datetime.now(timezone.utc).isoformat()

def budget():
    require(datetime.now(timezone.utc)<datetime(2026,11,15,10,43,tzinfo=timezone.utc), 'Study42 absolute cap exceeded')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--protocol-sha256', required=True)
    parser.add_argument('--freeze-only', action='store_true')
    args=parser.parse_args()
    require(sha(args.protocol)==args.protocol_sha256, 'Protocol hash mismatch')
    budget()
    inputs=[DATA/'scientific_audit/outer_predictions.csv', DATA/'eval_loso.csv', DATA/'gates.csv',
        ROOT/'pipeline/scientific_audit.py', ROOT/'pipeline/experiment.py']
    frozen=dict(protocol_sha256=args.protocol_sha256, code_sha256=sha(__file__),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in inputs},
        python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__)
    OUT.mkdir(parents=True, exist_ok=True)
    freeze_file=OUT/'code-freeze.json'
    if args.freeze_only:
        require(not freeze_file.exists(), 'Freeze already exists')
        frozen['frozen_utc']=stamp()
        freeze_file.write_text(json.dumps(frozen, indent=2)+'\n')
        print(json.dumps({'status':'FROZEN', 'freeze_sha256':sha(freeze_file), **frozen}))
        return
    previous=json.loads(freeze_file.read_text())
    for name,value in frozen.items():
        require(previous[name]==value, 'Frozen source/environment changed: '+name)
    before={str(p.relative_to(ROOT)):sha(p) for p in [DATA/'params.json', DATA/'gates.csv', *sorted((ROOT/'web/public/data').rglob('*.json'))]}
    x=pd.read_csv(inputs[0], dtype={'cut':str}, usecols=['cut','season','m','aqua','snpp','M0','M1','M2','policy'])
    x=x[x.policy=='published_fixed'].copy()
    require(len(x)==5184 and not x.duplicated(['cut','season','m']).any(), 'Fixed-mask prediction keys/count')
    require(set(x.season)==set(range(2012,2020)) and set(x.m)==set(range(1,13)), 'Season/month domain')
    cuts=set(x.cut);require(len(cuts)==54, 'CUT count')
    require(set(x[['cut','season','m']].itertuples(index=False,name=None))=={(c,s,m) for c in cuts for s in range(2012,2020) for m in range(1,13)}, 'Full monthly Cartesian domain')
    require(np.isfinite(x[['aqua','snpp','M0','M1','M2']]).all().all() and (x[['aqua','snpp','M0','M1','M2']]>=0).all().all(), 'Nonfinite/negative inputs')
    g=pd.read_csv(inputs[2], index_col=0, dtype={0:str});g.index=g.index.str.zfill(5)
    require(set(g.index)==cuts and g.index.is_unique and g.enabled.dtype==bool, 'Gate key/boolean domain')
    enabled=set(g.index[g.enabled]);require(len(enabled)==14, 'Published14 count')
    controls=pd.read_csv(inputs[1], dtype={'cut':str});controls=controls[controls.method=='M1'].copy()
    require(len(controls)==54*8*7 and len(set(controls.kappa))==7 and not controls.duplicated(['cut','held_out','kappa']).any(), 'M1 controls domain')
    fields=['mae','bias','n','aqua_sum']
    require((controls.groupby(['cut','held_out'])[fields].nunique(dropna=False)==1).all().all(), 'M1 not exactly invariant over seven kappa')
    reference=controls[controls.kappa==0].set_index(['cut','held_out'])
    require(len(reference)==432 and set(reference.index)=={(c,s) for c in cuts for s in range(2012,2020)}, 'Kappa0 controls incomplete')
    checks=[]
    for key, frame in x.groupby(['cut','season'], sort=True):
        error=frame.M1-frame.snpp
        actual=dict(mae=float(error.abs().mean()), bias=float(error.mean()), n=len(frame), aqua_sum=float(frame.aqua.sum()))
        ref=reference.loc[key]
        for field in fields:
            require(math.isclose(actual[field],float(ref[field]),abs_tol=1e-9,rel_tol=1e-11), 'Monthly M1 control failed: '+str(key)+'/'+field)
        checks.append({'cut':key[0], 'season':int(key[1]), **actual, 'monthly_control_pass':True})
    budget()
    # All monthly controls must pass before any seasonal totals are computed.
    result=totals(x,['M0','M1','M2']);result['published_enabled']=result.cut.isin(enabled)
    require(len(result)==1296 and len(result[(result.method=='M1')&result.published_enabled])==112, 'Season-total output scope')
    report=dict(status='PASS', completed_utc=stamp(), methods=['M0','M1','M2'], season_start_years=list(range(2012,2020)),
        monthly_controls=432, kappa_invariance_exact=True, kappa_count=7, monthly_rows=5184,
        selected_published_cuts=sorted(enabled), primary='M1/published14',
        unit='registered cell-days aggregated July-June; not distinct fires or burned area',
        apparent_postselection=True, fresh_holdout=False, validates_2002_2011=False,
        fits=0, solvers=0, downloads=0, production_changed=False, populations={})
    cut_rows=[]
    for method, frame in result.groupby('method',sort=True):
        report['populations'][method]={}
        for name, sub in [('published14',frame[frame.published_enabled]),('all54',frame),('remaining40',frame[~frame.published_enabled])]:
            report['populations'][method][name]=summarize(sub)
        for cut, sub in frame.groupby('cut',sort=True):
            cut_rows.append(dict(cut=cut, method=method, published_enabled=cut in enabled, **summarize(sub)))
    result.to_csv(OUT/'season-totals.csv',index=False)
    pd.DataFrame(cut_rows).to_csv(OUT/'per-cut.csv',index=False)
    pd.DataFrame(checks).to_csv(OUT/'monthly-controls.csv',index=False)
    (OUT/'summary.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    require(before=={p:sha(ROOT/p) for p in before}, 'Production changed')
    require(all(sha(ROOT/p)==h for p,h in previous['input_sha256'].items()), 'Frozen input changed')
    budget()
    files=[p for p in OUT.iterdir() if p.is_file()]
    require(sum(p.stat().st_size for p in files)<5*1024*1024, 'Output cap exceeded')
    manifest=dict(status='PASS', completed_utc=stamp(), code_freeze_sha256=sha(freeze_file),
        protocol_sha256=args.protocol_sha256, output_sha256={p.name:sha(p) for p in files},
        production_unchanged=True, input_unchanged=True, fits=0, solvers=0, downloads=0,
        output_bytes_before_manifest=sum(p.stat().st_size for p in files))
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':'PASS','manifest_sha256':sha(OUT/'manifest.json'), 'primary':report['populations']['M1']['published14']}))

if __name__ == '__main__':
    main()
