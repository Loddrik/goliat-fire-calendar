"""Protocol 5: monotone, continuous, zero-anchored two-slope calibration."""
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from scientific_audit import ROOT,DATA,TRAIN,AuditData,fit_models,predict,score,summarize,diagnostic_gates,sha,band_metrics
from affine_experiment import LAMBDAS,fit_affine,predict_affine,choose_policies,candidate_values,paired_bootstrap
from robust_affine_experiment import check_deadline

OUT=DATA/"piecewise_audit"
PROTOCOL=ROOT/"docs/reviews/2026-11-14-science-protocol-5.md"
POLICIES=("M1_P","M1_B_P")
METHODS=("M0","M1","M2","M1_B",*POLICIES)


def name(lam):return f"P_{lam:g}"


def fit_piecewise(training,affine):
    threshold=training[training.aqua>0].groupby("g").aqua.median()
    params=affine[["scale","prior_beta","n"]].copy()
    groups=params.index.get_level_values("g")
    params["threshold"]=threshold.reindex(groups).fillna(1).to_numpy()
    t=training.merge(params[["scale","threshold"]],on=["cut","g"],validate="many_to_one")
    t["z1"]=np.minimum(t.aqua,t.threshold)/t.scale
    t["z2"]=np.maximum(t.aqua-t.threshold,0)/t.scale
    t["z11"],t["z12"],t["z22"]=t.z1*t.z1,t.z1*t.z2,t.z2*t.z2
    t["zy1"],t["zy2"]=t.z1*t.snpp,t.z2*t.snpp
    moments=t.groupby(["cut","g"])[["z11","z12","z22","zy1","zy2"]].mean().reindex(params.index)
    for lam in LAMBDAS:
        h0,h1,h2=(moments.z11+lam).to_numpy(),moments.z12.to_numpy(),(moments.z22+lam).to_numpy()
        q0=(moments.zy1+lam*params.prior_beta).to_numpy();q1=(moments.zy2+lam*params.prior_beta).to_numpy()
        determinant=h0*h2-h1*h1
        if (determinant<=0).any():raise ValueError("Piecewise normal equations not positive definite")
        u0,u1=(q0*h2-q1*h1)/determinant,(q1*h0-q0*h1)/determinant
        # Interior plus both exact boundary optima and the origin.
        candidates=np.stack([np.column_stack([u0,u1]),
            np.column_stack([np.maximum(0,q0/h0),np.zeros(len(params))]),
            np.column_stack([np.zeros(len(params)),np.maximum(0,q1/h2)]),np.zeros((len(params),2))])
        v0,v1=candidates[:,:,0],candidates[:,:,1]
        objectives=h0*v0*v0+2*h1*v0*v1+h2*v1*v1-2*q0*v0-2*q1*v1
        objectives[0,(u0<0)|(u1<0)]=np.inf
        selected=candidates[np.argmin(objectives,axis=0),np.arange(len(params))]
        g0=h0*selected[:,0]+h1*selected[:,1]-q0;g1=h1*selected[:,0]+h2*selected[:,1]-q1
        kkt=np.maximum(np.where(selected[:,0]>1e-10,np.abs(g0),np.maximum(0,-g0)),np.where(selected[:,1]>1e-10,np.abs(g1),np.maximum(0,-g1)))
        if not np.isfinite(selected).all() or kkt.max()>1e-6:raise ValueError("Piecewise solution fails finite/KKT checks")
        params[name(lam)+"_b1"]=selected[:,0]/params.scale.to_numpy()
        params[name(lam)+"_b2"]=selected[:,1]/params.scale.to_numpy()
        params[name(lam)+"_kkt"]=kkt
    return params


def predict_piecewise(frame,params):
    x=frame.merge(params,on=["cut","g"],how="left",validate="many_to_one")
    if x.threshold.isna().any():raise ValueError("Missing piecewise training group")
    for lam in LAMBDAS:
        x[name(lam)]=x[name(lam)+"_b1"]*np.minimum(x.aqua,x.threshold)+x[name(lam)+"_b2"]*np.maximum(0,x.aqua-x.threshold)
    return x.drop(columns=params.columns)


def choose(inner):
    previous,_=choose_policies(inner)
    cols=sorted(set([name(l) for l in LAMBDAS]+["M1"]+list(previous["M1_B"].values())))
    losses=pd.DataFrame({c:(inner[c]-inner.snpp).abs() for c in cols});losses["cut"]=inner.cut.to_numpy()
    losses=losses.groupby("cut").mean()
    choices={"M1_B":previous["M1_B"],"M1_P":{},"M1_B_P":{}}
    for cut,row in losses.iterrows():
        lam=min(LAMBDAS,key=lambda l:(row[name(l)],-l));candidate=name(lam);old=previous["M1_B"][cut]
        choices["M1_P"][cut]=candidate if row[candidate]<.99*row.M1 else "M1"
        choices["M1_B_P"][cut]=candidate if row[candidate]<.99*row[old] else old
    return choices,losses


def add_intervals(external,inner,choices):
    x=external.copy()
    for policy in ("M1","M1_B",*POLICIES):
        mapping={c:"M1" for c in inner.cut.unique()} if policy=="M1" else choices[policy]
        errors=inner[["cut","snpp"]].copy();errors["err"]=np.abs(candidate_values(inner,mapping)-errors.snpp)
        q=errors[errors.snpp>0].groupby("cut").err.quantile(.8)
        x[policy+"_abs80_radius"]=x.cut.map(q)
    return x


def population_metrics(frame,populations):
    return {label:{"n":len(x),"methods":{m:{"mae":float((x[m]-x.snpp).abs().mean()) if len(x) else None,
        "bias":float((x[m]-x.snpp).mean()) if len(x) else None,"prediction_sum":float(x[m].sum())} for m in METHODS}} for label,x in populations.items()}


def run():
    check_deadline()
    protected=[DATA/f for f in ["params.json","gates.csv","static_mask.parquet","eval_loso.csv","eval_final.csv"]]
    protected+=sorted((ROOT/"web/public/data").rglob("*.json"))
    for directory in ["scientific_audit","affine_audit","robust_affine_audit"]:protected+=sorted((DATA/directory).glob("*"))
    before={str(p.relative_to(ROOT)):sha(p) for p in protected}
    data=AuditData();external,selection,coefficients,numerics=[],[],[],[]
    def fold(allowed,held,outer,layer):
        check_deadline();frame=data.monthly("fold_fitted",allowed);tr,te=frame[frame.season.isin(allowed)],frame[frame.season==held]
        reference=fit_models(tr);affine=fit_affine(tr,reference);params=fit_piecewise(tr,affine)
        numerics.append({"outer":outer,"held":held,"layer":layer,"max_kkt":float(params[[c for c in params if c.endswith('_kkt')]].max().max()),"training_seasons":";".join(map(str,allowed))})
        return predict_piecewise(predict_affine(predict(te,reference),affine),params),params
    for held in TRAIN:
        allowed=tuple(s for s in TRAIN if s!=held)
        inner=pd.concat([fold(tuple(s for s in allowed if s!=ih),ih,held,"inner")[0] for ih in allowed],ignore_index=True)
        choices,loss=choose(inner);test,params=fold(allowed,held,held,"outer")
        for policy,mapping in choices.items():
            test[policy]=candidate_values(test,mapping);test[policy+"_chosen"]=test.cut.map(mapping)
            for cut,method in mapping.items():selection.append({"outer_held":held,"cut":cut,"policy":policy,"candidate":method,"internal_mae":float(loss.loc[cut,method]),"training_seasons":";".join(map(str,allowed))})
        external.append(add_intervals(test,inner,choices));coefficients.append(params.reset_index().assign(outer_held=held))
        print("Piecewise outer fold complete:",held,flush=True)
    x=pd.concat(external,ignore_index=True)
    prior=pd.read_csv(DATA/"affine_audit/outer_predictions.csv",dtype={"cut":str})
    both=x.merge(prior[["cut","season","m","M1","M1_B","snpp"]],on=["cut","season","m"],suffixes=("","_old"),validate="one_to_one")
    if len(both)!=5184 or any(not np.allclose(both[c],both[c+"_old"],atol=1e-10,rtol=0) for c in ["M1","M1_B","snpp"]):raise ValueError("Previous control reproduction failed")
    scores=score(x,METHODS);full=data.monthly("fold_fitted",TRAIN);gates=[]
    for method in ("M1","M1_B",*POLICIES):gates.append(diagnostic_gates(scores,full,method).reset_index().assign(method=method))
    gates=pd.concat(gates,ignore_index=True);choices_frame=pd.DataFrame(selection);num=pd.DataFrame(numerics)
    old14=json.loads((DATA/"scientific_audit/summary.json").read_text())["mask_policies"]["published_fixed"]["enabled_diagnostic"]
    subgroup=population_metrics(x,{"aqua_zero_viirs_positive":x[(x.aqua==0)&(x.snpp>0)],"both_observed_zero":x[(x.aqua==0)&(x.snpp==0)],"aqua_positive":x[x.aqua>0]})
    intensity=population_metrics(x,{"zero":x[x.snpp==0],"positive_lt10":x[(x.snpp>0)&(x.snpp<10)],"10_to_lt50":x[(x.snpp>=10)&(x.snpp<50)],"50_plus":x[x.snpp>=50]})
    report={"status":"development-experiment","controls_reproduced":True,"external_validation":False,"scores":summarize(scores),
        "enabled_diagnostic":{m:sorted(g.loc[g.enabled_diagnostic,"cut"].tolist()) for m,g in gates.groupby("method")},
        "contrasts":[paired_bootstrap(x,a,b) for a,b in [("M1_P","M1"),("M1_B_P","M1_B")]],"subgroups":subgroup,"intensity":intensity,
        "bands":{m:{p:band_metrics(x.assign(M1=x[m]),m+"_abs80_radius",cuts) for p,cuts in [("all54",None),("previous14",old14)]} for m in ("M1","M1_B",*POLICIES)},
        "choice_counts":{p:g.candidate.value_counts().astype(int).to_dict() for p,g in choices_frame.groupby("policy")},
        "numerical":{"max_kkt":float(num.max_kkt.max()),"fits":len(num),"all_converged":bool((num.max_kkt<=1e-6).all()),"max_candidate_prediction_at_aqua_zero":float(x.loc[x.aqua==0,[name(l) for l in LAMBDAS]].abs().max().max())},
        "mulchen":{"scores":summarize(scores[scores.cut=="08305"]),"gates":gates[gates.cut=="08305"].to_dict("records")}}
    if before!={str(p.relative_to(ROOT)):sha(p) for p in protected}:raise ValueError("Protected files changed")
    OUT.mkdir(parents=True,exist_ok=True)
    for filename,frame in [("outer_predictions.csv",x),("nested_selection.csv",choices_frame),("outer_coefficients.csv",pd.concat(coefficients,ignore_index=True)),("scores.csv",scores),("diagnostic_gates.csv",gates),("numerics.csv",num)]:frame.to_csv(OUT/filename,index=False)
    (OUT/"summary.json").write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
    manifest={"source_head":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"protocol_sha256":sha(PROTOCOL),"code_sha256":sha(Path(__file__)),
        "helpers_sha256":{f:sha(ROOT/"pipeline"/f) for f in ["scientific_audit.py","affine_experiment.py","robust_affine_experiment.py"]},"protected_sha256":before,"production_and_previous_unchanged":True,
        "input_sha256":{f:sha(DATA/f) for f in ["detections.parquet","celldays.parquet","static_mask.parquet"]},"output_sha256":{p.name:sha(p) for p in sorted(OUT.glob("*")) if p.name!="manifest.json"}}
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,allow_nan=False)+"\n");print("Piecewise experiment complete:",OUT,flush=True)
    return report


if __name__=="__main__":run()
