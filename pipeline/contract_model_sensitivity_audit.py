"""Study24C: frozen-model representation sensitivity, never refit or publish."""
import csv
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from scientific_audit import ROOT, DATA, sha
from frozen_temporal_audit import KEYS, publication_metadata
from contract_gap_audit import BASE, verify_series, observed_grid
from coherent_experiment import METHODS, extend
from hurdle_experiment import estimate_frozen, load_model, model_signature

OUT=DATA/'contract_model_sensitivity_audit'
PROTOCOL=ROOT/'docs/reviews/2026-11-15-science-protocol-24c.md'
CAP_END=datetime.fromisoformat('2026-11-15T05:29:28+00:00')
SOURCE=DATA/'platform_target_audit/paired_predictions.parquet'
COUNTS=DATA/'contract_gap_common_archive_audit/contract_counts.parquet'
MODEL=DATA/'hurdle_audit/frozen_model.json'


def cap():
    if datetime.now(timezone.utc)>=CAP_END:raise TimeoutError('Study24C absolute cap reached; no restart')


def validate_platform_csv(payload,segment,commune,source):
    if hashlib.sha256(payload).hexdigest()!=segment['sha256'] or len(payload)!=segment['bytes']:
        raise ValueError('Observed CSV hash/size mismatch')
    rows=list(csv.DictReader(payload.decode().splitlines()))
    if len(rows)!=segment['rows']:raise ValueError('Observed CSV row count mismatch')
    expected={'aqua-history':('MODIS','Aqua'),'noaa20-history':('VIIRS','N20')}
    if source['id'] not in expected:raise ValueError('Unregistered platform')
    instrument,satellite=expected[source['id']]
    if source['instrument']!=instrument:raise ValueError('Manifest instrument mismatch')
    files={f['filename']:f for f in source['files']}
    for r in rows:
        acquired=date.fromisoformat(r['acq_date'])
        confidence=(30<=float(r['confidence'])<=100) if instrument=='MODIS' else r['confidence'].lower() in ('n','h')
        if (r['cut_com']!=commune['cut'] or r['comuna']!=commune['name'] or r['instrument']!=instrument or
            r['satellite']!=satellite or r['daynight']!='D' or r['type']!='0' or not confidence or
            r['source_file'] not in files or acquired.year not in source['available_years']):
            raise ValueError('Observed platform/filter provenance mismatch')
        if acquired.year!=files[r['source_file']]['year']:raise ValueError('Source-file year mismatch')
        if r['version'] not in source['versions']:raise ValueError('Version outside source manifest')
        if observed_grid(float(r['longitude']),float(r['latitude']))!=(int(r['grid_x']),int(r['grid_y'])):
            raise ValueError('Observed grid mismatch')
    return rows


def require_equal(actual,expected,columns,tolerance=1e-10):
    a=actual.sort_values(KEYS).reset_index(drop=True);b=expected.sort_values(KEYS).reset_index(drop=True)
    if a.duplicated(KEYS).any() or b.duplicated(KEYS).any() or not a[KEYS].equals(b[KEYS]):
        raise ValueError('Identity keys mismatch')
    for c in columns:
        if not np.allclose(a[c],b[c],atol=tolerance,rtol=0,equal_nan=False):raise ValueError('Identity values mismatch: '+c)


def load_observed(panel):
    manifest=json.loads((BASE/'data/history-manifest.json').read_text())
    index=json.loads((BASE/'data/publication/index.json').read_text())
    if index['source_manifest_sha256']!=sha(BASE/'data/history-manifest.json'):raise ValueError('Publication manifest hash mismatch')
    if sha(ROOT/'observed/data/processed/communes-full.geojson')!=manifest['geography']['geometry_sha256']:
        raise ValueError('Observed geometry hash mismatch')
    if manifest['grid']['assignment']!='cell-centre':raise ValueError('Observed assignment changed')
    if set(c['cut'] for c in manifest['communes'])!=set(panel.cut):raise ValueError('Commune domain mismatch')
    monthly=json.loads((BASE/'data/observed-monthly.json').read_text());out=panel[KEYS+['month']].copy()
    ledger=[]
    for source_id,column in [('aqua-history','aqua_O'),('noaa20-history','Y_O')]:
        source=next(s for s in manifest['sources'] if s['id']==source_id);values=[]
        for commune in manifest['communes']:
            cap();cut=commune['cut'];segment=next(s for s in source['communes'] if s['cut']==cut)
            path=BASE/segment['url'];rows=validate_platform_csv(path.read_bytes(),segment,commune,source)
            publication=BASE/'data/publication'/f'{cut}.json';expected=next(c for c in index['communes'] if c['cut']==cut)
            if sha(publication)!=expected['sha256']:raise ValueError('Publication commune hash mismatch')
            series=[r for r in monthly if r['source_id']==source_id and r['cut']==cut]
            pub=next(s for s in json.loads(publication.read_text())['sources'] if s['id']==source_id)['series']
            verify_series(rows,series);verify_series(rows,pub)
            a=sorted(series,key=lambda r:r['month']);b=sorted(pub,key=lambda r:r['month'])
            if [(r['month'],r['cell_days'],r['detections']) for r in a]!=[(r['month'],r['cell_days'],r['detections']) for r in b]:
                raise ValueError('Source/publication series identity mismatch')
            for r in series:values.append({'cut':cut,'month':r['month'],column:r['cell_days']})
            ledger.append({'source':source_id,'cut':cut,'csv':str(path.relative_to(ROOT)),'sha256':sha(path),'rows':len(rows)})
        support=pd.DataFrame(values)
        if support.duplicated(['cut','month']).any():raise ValueError('Duplicate support keys')
        out=out.merge(support,on=['cut','month'],how='left',validate='one_to_one')
        if out[column].isna().any():raise ValueError('Unavailable observed month; no zero fill')
        out[column]=out[column].astype('int64')
    return out,pd.DataFrame(ledger)


def predict_input(features,model):
    # Whitelist features ensures targets cannot enter predictions or solver.
    f=features[[*KEYS,'g','aqua']].copy()
    if not np.isfinite(f.aqua.to_numpy()).all() or (f.aqua<0).any():raise ValueError('Invalid Aqua input')
    estimated=estimate_frozen(f,model)
    return extend(estimated,model['hurdle'])


def scores(frame,target):
    result={'n':len(frame),'target_sum':float(frame[target].sum()),'methods':{}}
    for method in METHODS:
        error=frame[method]-frame[target]
        monthly=frame.groupby(['season','m'])[[method,target]].sum()
        result['methods'][method]={'mae':float(error.abs().mean()) if len(frame) else None,
            'bias':float(error.mean()) if len(frame) else None,'prediction_sum':float(frame[method].sum()),
            'regional_monthly_mae':float((monthly[method]-monthly[target]).abs().mean()) if len(frame) else None}
    result['delta_coherent_minus_B']=(result['methods']['E_coherent']['mae']-result['methods']['M1_B']['mae']) if len(frame) else None
    result['ranking_secondary']=sorted(METHODS,key=lambda c:(result['methods'][c]['mae'],c)) if len(frame) else []
    return result


def materiality(cc,oo,b_mae):
    tau=.01*b_mae
    return {'tau':float(tau),'delta_CC':float(cc),'delta_OO':float(oo),'change':float(oo-cc),
            'material_change':bool(abs(oo-cc)>=tau),'sign_inversion':bool(cc*oo<0),
            'material_sign_inversion':bool(cc*oo<0 and abs(cc)>tau and abs(oo)>tau)}


def fixed_populations(frame):
    return {'all_months':np.ones(len(frame),dtype=bool),'YC_zero':frame.Y_C.eq(0).to_numpy(),
        'YC_positive':frame.Y_C.gt(0).to_numpy(),'YC_50_plus_FIXED':frame.Y_C.ge(50).to_numpy(),
        'AquaC_zero_YC_positive':(frame.aqua_C.eq(0)&frame.Y_C.gt(0)).to_numpy(),
        'both_C_zero':(frame.aqua_C.eq(0)&frame.Y_C.eq(0)).to_numpy(),
        'YO_50_plus_DIAGNOSTIC':frame.Y_O.ge(50).to_numpy()}


def bounded_contrasts(frame):
    if not len(frame):return {'n':0}
    target_bound=2*float((frame.Y_C-frame.Y_O).abs().mean())
    input_bound=float((frame.E_coherent_C-frame.E_coherent_O).abs().mean()+(frame.M1_B_C-frame.M1_B_O).abs().mean())
    delta={}
    for inp in 'CO':
        for target in 'CO':
            delta[inp+target]=float(((frame['E_coherent_'+inp]-frame['Y_'+target]).abs()-(frame['M1_B_'+inp]-frame['Y_'+target]).abs()).mean())
    changes={'target_inputC':abs(delta['CO']-delta['CC']),'target_inputO':abs(delta['OO']-delta['OC']),
             'input_targetC':abs(delta['OC']-delta['CC']),'input_targetO':abs(delta['OO']-delta['CO'])}
    if any(v>target_bound+1e-10 for k,v in changes.items() if k.startswith('target')):raise ValueError('Target Lipschitz bound failed')
    if any(v>input_bound+1e-10 for k,v in changes.items() if k.startswith('input')):raise ValueError('Input Lipschitz bound failed')
    return {'n':len(frame),'target_bound':target_bound,'input_bound':input_bound,'deltas':delta,'absolute_changes':changes}


def reports(wide,enabled):
    report={};flat=[]
    groups={'all54':np.ones(len(wide),bool),'published14':wide.cut.isin(enabled).to_numpy(),'remaining40':~wide.cut.isin(enabled).to_numpy()}
    for group,groupmask in groups.items():
        report[group]={}
        for name,popmask in fixed_populations(wide).items():
            x=wide.loc[groupmask&popmask].copy();r={}
            for inp in 'CO':
                f=x[[*KEYS,'Y_C','Y_O']].copy()
                for m in METHODS:f[m]=x[m+'_'+inp].to_numpy()
                for target in 'CO':
                    key=inp+target;r[key]=scores(f,'Y_'+target)
                    for m,v in r[key]['methods'].items():flat.append(dict(group=group,population=name,contract=key,method=m,n=len(f),**v))
            r['bounds']=bounded_contrasts(x);report[group][name]=r
    return report,pd.DataFrame(flat)


def run():
    cap();OUT.mkdir(parents=True,exist_ok=True)
    freeze=json.loads((OUT/'code-freeze.json').read_text())
    for path,digest in {**freeze['code_sha256'],**freeze['protected_sha256']}.items():
        if sha(ROOT/path)!=digest:raise ValueError('Frozen source changed: '+path)
    gates={};summary={'status':'pending','fits':0,'new_downloads':0,'independent_validation':False,'G1_physical':False,
        'cap_start':'2026-11-15T04:29:28Z','cap_end':'2026-11-15T05:29:28Z','regional_equality_is_constructed':True,'gates':gates}
    try:
        for folder,name in [('coherent_audit','later_predictions.parquet'),('platform_target_audit',SOURCE.name),('contract_gap_common_archive_audit',COUNTS.name)]:
            provenance=json.loads((DATA/folder/'manifest.json').read_text())
            if sha(DATA/folder/name)!=provenance['output_sha256'][name]:raise ValueError('Historical artifact manifest mismatch: '+folder)
        provenance18=json.loads((DATA/'coherent_audit/manifest.json').read_text())
        model=load_model(MODEL)
        if model_signature(model)!=provenance18['frozen_model_signature']:raise ValueError('Frozen model differs from18')
        for helper,digest in provenance18['code_sha256'].items():
            if sha(ROOT/'pipeline'/helper)!=digest:raise ValueError('Historical decision helper changed: '+helper)
        for folder in ['platform_target_audit','contract_gap_common_archive_audit']:
            provenance=json.loads((DATA/folder/'manifest.json').read_text())
            for key in ['data/processed/detections.parquet','data/processed/celldays.parquet','data/processed/static_mask.parquet','data/processed/cells_comuna.parquet']:
                if key in provenance['protected_sha256'] and sha(ROOT/key)!=provenance['protected_sha256'][key]:raise ValueError('Research source provenance mismatch: '+key)
        gates['historical_manifest_chain_and_model_exact']=True
        panel=pd.read_parquet(SOURCE);counts=pd.read_parquet(COUNTS)
        panel=counts[KEYS+['month']].merge(panel,on=KEYS,validate='one_to_one')
        if len(panel)!=3456 or panel.month.nunique()!=64 or panel.duplicated(KEYS).any():raise ValueError('Fixed common domain mismatch')
        if set(panel.cut)!=set(counts.cut):raise ValueError('CUT domain mismatch')
        require_equal(panel.rename(columns={'noaa20':'Cmaskedall'}),counts,['Cmaskedall'],0)
        observed,ledger=load_observed(panel);gates['108_csv_filters_hash_grid_and_series_exact']=True
        joined=panel.merge(observed.drop(columns='month'),on=KEYS,validate='one_to_one').merge(counts[KEYS+['O0']],on=KEYS,validate='one_to_one')
        if not np.array_equal(joined.Y_O,joined.O0):raise ValueError('NOAA20 O differs from20A')
        prior=pd.read_parquet(DATA/'coherent_audit/later_predictions.parquet').merge(counts[KEYS],on=KEYS,validate='one_to_one')
        require_equal(joined,prior,['aqua',*METHODS]);gates['source18_19_common_identity']=True
        model=load_model(MODEL);signature=model_signature(model)
        c,checksC=predict_input(joined,model)
        require_equal(c,joined,list(METHODS));gates['CC_six_frozen_functions_reproduce18_19']=True
        poisoned=joined.copy();poisoned['snpp']=-999;poisoned['noaa20']=123456;poisoned['Y_O']=987654
        again,_=predict_input(poisoned,model);require_equal(c,again,list(METHODS),0)
        gates['destination_labels_invariant_C']=True
        o_input=joined.copy();o_input['aqua']=o_input.aqua_O
        o,checksO=predict_input(o_input,model)
        againO,_=predict_input(o_input[[*KEYS,'g','aqua']],model);require_equal(o,againO,list(METHODS),0)
        gates['destination_labels_invariant_O']=True
        if model_signature(model)!=signature:raise ValueError('Frozen model mutated')
        gates['all_reproduction_gates_passed']=True
        wide=joined[[*KEYS,'month','g','block','orbit_epoch','aqua','aqua_O','noaa20','Y_O']].rename(columns={'aqua':'aqua_C','noaa20':'Y_C'})
        for inp,f in [('C',c),('O',o)]:
            f=wide[KEYS].merge(f[KEYS+list(METHODS)],on=KEYS,validate='one_to_one')
            for m in METHODS:wide[m+'_'+inp]=f[m].to_numpy()
        # First losses occur here, after every identity and destination-invariance gate.
        cap();enabled,_=publication_metadata(sorted(wide.cut.unique()));report,flat=reports(wide,enabled)
        primary=report['all54']['all_months'];cc=primary['CC']['delta_coherent_minus_B'];oo=primary['OO']['delta_coherent_minus_B']
        mat=materiality(cc,oo,primary['CC']['methods']['M1_B']['mae'])
        tc=primary['bounds']['target_bound']
        if not np.isclose(tc,440/3456,atol=1e-12,rtol=0):raise ValueError('Target bound does not reproduce20A440/3456')
        a=wide.Y_C.ge(50);b=wide.Y_O.ge(50)
        summary.update(status='frozen-contract-sensitivity-complete',domain_rows=len(wide),calendar_months=64,
            primary=mat,reports=report,extreme_population_movement={'YC_n':int(a.sum()),'YO_n':int(b.sum()),
            'intersection':int((a&b).sum()),'YO_entries':int((~a&b).sum()),'YO_exits':int((a&~b).sum())},
            observation_opportunity='unknown; requested/archive availability is not useful coverage',
            interpretation='Definition sensitivity only; no physical validation, no promotion, no fresh holdout')
        wide.to_parquet(OUT/'paired_predictions.parquet',index=False);flat.to_csv(OUT/'metrics.csv',index=False)
        ledger.to_csv(OUT/'source_csv_ledger.csv',index=False)
        pd.DataFrame([dict(x,input_contract=i) for i,checks in [('C',checksC),('O',checksO)] for x in checks]).to_csv(OUT/'allocation_checks.csv',index=False)
    except (ValueError,KeyError,StopIteration,FileNotFoundError,TimeoutError) as exc:
        summary.update(status='blocked-reproduction-or-cap',reason=str(exc),reports=None)
        gates['all_reproduction_gates_passed']=False
    for path,digest in freeze['protected_sha256'].items():
        if sha(ROOT/path)!=digest:raise ValueError('Protected source changed: '+path)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    (OUT/'manifest.json').write_text(json.dumps({'protocol_sha256':sha(PROTOCOL),'freeze_sha256':sha(OUT/'code-freeze.json'),
        'all_previous_artifacts_unchanged':True,'protected_sha256':freeze['protected_sha256'],
        'code_sha256':freeze['code_sha256'],'output_sha256':{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='manifest.json'}},indent=2)+'\n')
    print(summary['status'],summary.get('reason',''),flush=True);return summary


if __name__=='__main__':run()
