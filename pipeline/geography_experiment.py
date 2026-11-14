"""Protocol 6: factorial numerical-grid/geography sensitivity in memory only."""
import json
import math
import subprocess
from collections import Counter
from decimal import Decimal, ROUND_FLOOR
from pathlib import Path

import numpy as np
import pandas as pd
from shapely import Point,STRtree
from shapely.geometry import shape

from scientific_audit import ROOT,DATA,TRAIN,AuditData,fit_models,predict,score,summarize,diagnostic_gates,sha
from affine_experiment import fit_affine,predict_affine,candidate_values
from piecewise_experiment import fit_piecewise,predict_piecewise,choose,METHODS
from robust_affine_experiment import check_deadline

OUT=DATA/"geography_audit"
PROTOCOL=ROOT/"docs/reviews/2026-11-14-science-protocol-6.md"
LEGACY=DATA/"comunas_biobio_nuble.geojson"
OFFICIAL=ROOT/"observed/data/processed/communes-full.geojson"
SCENARIOS=("published","decimal_grid","dpa_legacy_grid","dpa_decimal_grid")


def decimal_cell(value):
    if not math.isfinite(float(value)):raise ValueError("Non-finite coordinate")
    return int((Decimal(str(value))*100).to_integral_value(rounding=ROUND_FLOOR))


class GeometryAssignment:
    def __init__(self,features,canonical):
        if canonical:features=sorted(features,key=lambda f:f['properties']['cut'])
        self.cuts=[f['properties']['cut'] for f in features]
        self.geoms=[shape(f['geometry']) for f in features]
        if any(not g.is_valid for g in self.geoms):raise ValueError("Invalid input commune geometry; no implicit repair")
        self.tree=STRtree(self.geoms);self.canonical=canonical

    def assign(self,cell):
        p=Point((int(cell[0])+.5)*.01,(int(cell[1])+.5)*.01)
        if not self.canonical:
            candidates=self.tree.query(p,predicate='within')
            return (self.cuts[int(candidates[0])],"inside") if len(candidates) else (None,"outside")
        candidates=[int(i) for i in self.tree.query(p) if self.geoms[int(i)].covers(p)]
        if not candidates:return None,"outside"
        if len(candidates)==1:return self.cuts[candidates[0]],"single-cover"
        interior=[i for i in candidates if self.geoms[i].contains(p)]
        if len(interior)>1:return None,"ambiguous-interior-overlap"
        if len(interior)==1:return self.cuts[interior[0]],"inside"
        return min(self.cuts[i] for i in candidates),"shared-edge-min-cut"


def prepare_data(raw,scenario,published_assignments,legacy_assigner,dpa_assigner):
    frame=raw.copy()
    if scenario in ("decimal_grid","dpa_decimal_grid"):
        for source,target in [("lon","cell_x"),("lat","cell_y")]:
            mapping={v:decimal_cell(v) for v in frame[source].unique()}
            frame[target]=frame[source].map(mapping).astype('int64')
    cell_keys=sorted(set(zip(frame.cell_x.astype(int),frame.cell_y.astype(int))))
    assignments=[]
    for cell in cell_keys:
        if scenario=="published":cut,status=published_assignments.get(cell),"published"
        else:cut,status=(dpa_assigner if scenario.startswith('dpa_') else legacy_assigner).assign(cell)
        assignments.append({"cell_x":cell[0],"cell_y":cell[1],"cut":cut,"status":status})
    assignment=pd.DataFrame(assignments)
    within=assignment[assignment.cut.notna()].copy()
    if within.duplicated(['cell_x','cell_y']).any():raise ValueError("A cell cannot belong to two communes")
    data=AuditData()
    data.con.register('scenario_detections',frame)
    data.con.register('scenario_assignment',within)
    data.con.execute('create or replace view det as select * from scenario_detections')
    data.con.execute("""create or replace view days as
      select d.sat,c.cut,d.cell_x,d.cell_y,d.acq_date,year(d.acq_date) y,month(d.acq_date) m,d.season,
      count(*) n_det,max(d.source_kind='nrt') any_nrt
      from det d join scenario_assignment c using(cell_x,cell_y) group by all""")
    # Map every retained input row for a like-for-like assignment comparison.
    lookup=dict(zip(zip(within.cell_x,within.cell_y),within.cut))
    mapped=pd.Series([lookup.get((int(x),int(y))) for x,y in zip(frame.cell_x,frame.cell_y)],index=frame.index,dtype='object')
    return data,frame,assignment,mapped


def evaluate(data,scenario):
    frames,selections=[],[]
    def fold(allowed,held):
        check_deadline();f=data.monthly('fold_fitted',allowed);tr,te=f[f.season.isin(allowed)],f[f.season==held]
        reference=fit_models(tr);affine=fit_affine(tr,reference);piecewise=fit_piecewise(tr,affine)
        return predict_piecewise(predict_affine(predict(te,reference),affine),piecewise)
    for held in TRAIN:
        allowed=tuple(s for s in TRAIN if s!=held)
        inner=pd.concat([fold(tuple(s for s in allowed if s!=ih),ih) for ih in allowed],ignore_index=True)
        choices,_=choose(inner);test=fold(allowed,held)
        for policy,mapping in choices.items():
            test[policy]=candidate_values(test,mapping)
            for cut,candidate in mapping.items():selections.append({'scenario':scenario,'held_out':held,'cut':cut,'policy':policy,'candidate':candidate})
        frames.append(test)
        print('Geography outer fold:',scenario,held,flush=True)
    pred=pd.concat(frames,ignore_index=True);scores=score(pred,METHODS);full=data.monthly('fold_fitted',TRAIN);gates=[]
    for method in ['M1','M1_B','M1_P','M1_B_P']:gates.append(diagnostic_gates(scores,full,method).reset_index().assign(method=method))
    gate=pd.concat(gates,ignore_index=True)
    return pred,scores,gate,pd.DataFrame(selections)


def run():
    check_deadline()
    protected=[DATA/f for f in ['params.json','gates.csv','eval_loso.csv','eval_final.csv','static_mask.parquet','detections.parquet','celldays.parquet','cells_comuna.parquet']]
    protected+=sorted((ROOT/'web/public/data').rglob('*.json'))
    for name in ['scientific_audit','affine_audit','robust_affine_audit','piecewise_audit']:protected+=sorted((DATA/name).glob('*'))
    before={str(p.relative_to(ROOT)):sha(p) for p in protected}
    meta=json.loads((ROOT/'observed/dist/data/history-manifest.json').read_text())
    if sha(OFFICIAL)!=meta['geography']['geometry_sha256']:raise ValueError('DPA geometry provenance mismatch')
    legacy=GeometryAssignment(json.loads(LEGACY.read_text())['features'],False)
    dpa=GeometryAssignment(json.loads(OFFICIAL.read_text())['features'],True)
    original=AuditData();raw=original.con.execute("select * from det where acq_date < date '2020-07-01'").df()
    published=dict(((int(x),int(y)),cut) for x,y,cut in original.con.execute(f"select cell_x,cell_y,cut from read_parquet('{DATA}/cells_comuna.parquet')").fetchall())
    old_keys=sorted(set(zip(raw.cell_x.astype(int),raw.cell_y.astype(int))))
    mismatches=[cell for cell in old_keys if legacy.assign(cell)[0]!=published.get(cell)]
    if mismatches:raise ValueError(f'Cannot reproduce existing geometry assignment: {len(mismatches)} cells')
    report={'status':'development-sensitivity','external_validation':False,'input_detections_before_july2020':len(raw),'existing_assignment_reproduced':True,'scenarios':{}}
    predictions,scores_out,gates_out,selections_out,assignments_out=[],[],[],[],[]
    baseline_mapped=None
    for scenario in SCENARIOS:
        data,det,assignment,mapped=prepare_data(raw,scenario,published,legacy,dpa)
        if scenario=='published':
            baseline_mapped=mapped
            # Independent SQL difference proves the canonical cellday rebuild.
            columns='sat,cut,cell_x,cell_y,acq_date,y,m,season,n_det,any_nrt'
            old=f"select {columns} from read_parquet('{DATA}/celldays.parquet') where acq_date < date '2020-07-01'"
            count=data.con.execute(f"select count(*) from ((select {columns} from days except all {old}) union all ({old} except all select {columns} from days))").fetchone()[0]
            if count:raise ValueError('Rebuilt published celldays differ from versioned source')
        pred,scores,gates,selection=evaluate(data,scenario)
        if scenario=='published':
            previous=pd.read_csv(DATA/'piecewise_audit/outer_predictions.csv',dtype={'cut':str})
            joined=pred.merge(previous[['cut','season','m','M1','M1_B','M1_P','M1_B_P','snpp']],on=['cut','season','m'],suffixes=('','_old'),validate='one_to_one')
            if len(joined)!=5184 or any(not np.allclose(joined[c],joined[c+'_old'],atol=1e-10,rtol=0) for c in ['M1','M1_B','M1_P','M1_B_P','snpp']):raise ValueError('Published scenario model controls do not reproduce')
        changed_cells=(det.cell_x.to_numpy()!=raw.cell_x.to_numpy())|(det.cell_y.to_numpy()!=raw.cell_y.to_numpy())
        old_cut=baseline_mapped.fillna('outside');new_cut=mapped.fillna('outside')
        details={'scores':summarize(scores),'enabled_diagnostic':{m:sorted(g.loc[g.enabled_diagnostic,'cut'].tolist()) for m,g in gates.groupby('method')},
            'detections_changing_cell':int(changed_cells.sum()),'unique_input_cells':len(assignment),'assigned_cells':int(assignment.cut.notna().sum()),
            'assignment_status':dict(Counter(assignment.status)),'detections_changing_cut_or_membership':int((old_cut!=new_cut).sum()),
            'detections_entering_territory':int(((old_cut=='outside')&(new_cut!='outside')).sum()),'detections_leaving_territory':int(((old_cut!='outside')&(new_cut=='outside')).sum()),
            'evaluated_target_cell_days':int(pred.snpp.sum()),'evaluated_aqua_cell_days':int(pred.aqua.sum()),'full_training_mask_cells':len(data.fit_mask(TRAIN)),
            'relative_mae_improvement_vs_M1':{m:float(1-(pred[m]-pred.snpp).abs().mean()/(pred.M1-pred.snpp).abs().mean()) for m in ['M1_B','M1_P','M1_B_P']}}
        examples=det.loc[changed_cells,['lat','lon','cell_x','cell_y']].head(10).copy()
        if len(examples):
            examples['old_cell_x']=raw.loc[examples.index,'cell_x'];examples['old_cell_y']=raw.loc[examples.index,'cell_y']
        details['numerical_examples']=examples.to_dict('records')
        report['scenarios'][scenario]=details
        predictions.append(pred.assign(scenario=scenario));scores_out.append(scores.assign(scenario=scenario));gates_out.append(gates.assign(scenario=scenario));selections_out.append(selection);assignments_out.append(assignment.assign(scenario=scenario))
        print('Geography scenario complete:',scenario,flush=True)
    if before!={str(p.relative_to(ROOT)):sha(p) for p in protected}:raise ValueError('Protected input/production files changed')
    OUT.mkdir(parents=True,exist_ok=True)
    for filename,frames in [('outer_predictions.csv',predictions),('scores.csv',scores_out),('diagnostic_gates.csv',gates_out),('nested_selection.csv',selections_out),('cell_assignments.csv',assignments_out)]:pd.concat(frames,ignore_index=True).to_csv(OUT/filename,index=False)
    (OUT/'summary.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    manifest={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'protocol_sha256':sha(PROTOCOL),'code_sha256':sha(Path(__file__)),
        'geometry_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [LEGACY,OFFICIAL]},'protected_sha256':before,'production_and_previous_unchanged':True,
        'output_sha256':{p.name:sha(p) for p in sorted(OUT.glob('*')) if p.name!='manifest.json'}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n');print('Geography sensitivity complete:',OUT,flush=True)
    return report


if __name__=='__main__':run()
