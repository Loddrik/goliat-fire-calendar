"""Protocol 4: nested Huber affine development, never production publication."""
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from scientific_audit import ROOT, DATA, TRAIN, AuditData, fit_models, predict, score, diagnostic_gates, summarize, sha, band_metrics
from affine_experiment import fit_affine, predict_affine, choose_policies, candidate_values, paired_bootstrap

DELTAS = (1., 3., 10.)
LAMBDAS = (.01, .1, 1.)
POLICIES = ("M1_H", "M1_B_H")
METHODS = ("M0", "M1", "M2", "M1_B", *POLICIES)
OUT = DATA / "robust_affine_audit"
PROTOCOL = ROOT / "docs/reviews/2026-11-14-science-protocol-4.md"
DEADLINE = datetime.fromisoformat(os.environ["GOLIAT_RESEARCH_DEADLINE_UTC"]) if os.environ.get("GOLIAT_RESEARCH_DEADLINE_UTC") else None


def check_deadline():
    if DEADLINE is not None and datetime.now(timezone.utc) >= DEADLINE:
        raise TimeoutError("Authorized Santiago 21:00 research deadline reached")


def name(delta, lam):
    return f"H_d{delta:g}_l{lam:g}"


def gradient(a, beta, z, y, codes, counts, prior, delta, lam):
    psi = np.clip(a[codes] + beta[codes] * z - y, -delta, delta)
    ga = np.bincount(codes, weights=psi, minlength=len(a)) / counts + lam * a
    gb = np.bincount(codes, weights=psi * z, minlength=len(a)) / counts + lam * (beta - prior)
    slope_error = np.where(beta > 1e-10, np.abs(gb), np.maximum(0, -gb))
    kkt = np.maximum(np.abs(ga), slope_error)
    return ga, gb, kkt


def fit_huber(training, affine_params, tolerance=1e-6, max_iter=1000):
    params = affine_params[["scale", "prior_beta", "n"]].copy()
    indices = pd.MultiIndex.from_frame(training[["cut", "g"]])
    codes = params.index.get_indexer(indices)
    if (codes < 0).any():
        raise ValueError("Training groups missing from affine normalization")
    counts = np.bincount(codes, minlength=len(params)).astype(float)
    if not np.array_equal(counts, params.n.to_numpy()):
        raise ValueError("Incorrect within-group averaging")
    z = training.aqua.to_numpy(dtype=float) / params.scale.to_numpy()[codes]
    y = training.snpp.to_numpy(dtype=float)
    prior = params.prior_beta.to_numpy()
    diagnostics = []
    for delta in DELTAS:
        for lam in LAMBDAS:
            a = affine_params[f"B_{lam:g}_a"].to_numpy(copy=True)
            beta = affine_params[f"B_{lam:g}_b"].to_numpy(copy=True) * params.scale.to_numpy()
            for iteration in range(max_iter + 1):
                if iteration % 100 == 0:
                    check_deadline()
                ga, gb, kkt = gradient(a, beta, z, y, codes, counts, prior, delta, lam)
                if kkt.max() <= tolerance:
                    break
                if iteration == max_iter:
                    raise RuntimeError(f"Huber {name(delta, lam)} failed convergence: KKT={kkt.max():g}")
                residual = a[codes] + beta[codes] * z - y
                mean = lambda values: np.bincount(codes, weights=values, minlength=len(params)) / counts
                if iteration < 10:
                    weights = np.minimum(1, delta / np.maximum(np.abs(residual), 1e-300))
                    h00, h01, h11 = mean(weights) + lam, mean(weights * z), mean(weights * z * z) + lam
                    q0, q1 = mean(weights * y), mean(weights * z * y) + lam * prior
                    determinant = h00 * h11 - h01 * h01
                    a = (q0 * h11 - q1 * h01) / determinant
                    beta = (q1 * h00 - q0 * h01) / determinant
                    a = np.where(beta >= 0, a, q0 / h00)
                    beta = np.maximum(0, beta)
                else:
                    # Same convex objective; accelerate slow IRLS at breakpoints.
                    active = (np.abs(residual) < delta).astype(float)
                    h00, h01, h11 = mean(active)+lam, mean(active*z), mean(active*z*z)+lam
                    determinant = h00*h11-h01*h01
                    da = (-ga*h11+gb*h01)/determinant
                    db = (-gb*h00+ga*h01)/determinant
                    boundary = beta+db < 0
                    db = np.where(boundary,-beta,db)
                    da = np.where(boundary,(-ga-h01*db)/h00,da)
                    da = np.where(kkt<=tolerance,0,da);db=np.where(kkt<=tolerance,0,db)
                    direction = ga*da+gb*db
                    def objective(aa,bb):
                        err=aa[codes]+bb[codes]*z-y;absolute=np.abs(err)
                        loss=np.where(absolute<=delta,.5*err*err,delta*(absolute-.5*delta))
                        return mean(loss)+.5*lam*(aa*aa+(bb-prior)**2)
                    old=objective(a,beta);step=np.ones(len(a))
                    for backtrack in range(60):
                        new=objective(a+step*da,beta+step*db)
                        reject=new>old+1e-4*step*direction+1e-13*(1+np.abs(old))
                        if not reject.any():break
                        step[reject]*=.5
                    else:raise RuntimeError("Huber Newton line search failed")
                    a=a+step*da;beta=np.maximum(0,beta+step*db)
            if not np.isfinite(a).all() or not np.isfinite(beta).all():
                raise ValueError("Huber produced non-finite coefficients")
            candidate = name(delta, lam)
            params[candidate + "_a"] = a
            params[candidate + "_b"] = beta / params.scale.to_numpy()
            diagnostics.append({"candidate": candidate, "iterations": iteration, "max_kkt": float(kkt.max()),
                                "boundary_slopes": int((beta == 0).sum()), "groups": len(params)})
    return params, diagnostics


def predict_huber(frame, params):
    x = frame.merge(params, on=["cut", "g"], how="left", validate="many_to_one")
    for delta in DELTAS:
        for lam in LAMBDAS:
            candidate = name(delta, lam)
            x[candidate] = np.maximum(0, x[candidate + "_a"] + x[candidate + "_b"] * x.aqua)
    if x.isna().any().any():
        raise ValueError("Missing Huber prediction inputs/coefficients")
    return x.drop(columns=params.columns)


def choose(inner):
    previous, _ = choose_policies(inner)
    hcols = [name(d, l) for d in DELTAS for l in LAMBDAS]
    allcols = sorted(set(hcols + list(previous["M1_B"].values()) + ["M1"]))
    loss = pd.DataFrame({c: (inner[c] - inner.snpp).abs() for c in allcols})
    loss["cut"] = inner.cut.to_numpy(); loss = loss.groupby("cut").mean()
    choices = {"M1_B": previous["M1_B"], "M1_H": {}, "M1_B_H": {}}
    for cut, row in loss.iterrows():
        d, l = min(((d,l) for d in DELTAS for l in LAMBDAS), key=lambda pair: (row[name(*pair)], -pair[1], -pair[0]))
        best, previous_best = name(d,l), previous["M1_B"][cut]
        choices["M1_H"][cut] = best if row[best] < .99 * row.M1 else "M1"
        choices["M1_B_H"][cut] = best if row[best] < .99 * row[previous_best] else previous_best
    return choices, loss


def add_intervals(test, inner, choices):
    result = test.copy()
    for policy in ("M1", "M1_B", *POLICIES):
        mapping = {cut: "M1" for cut in inner.cut.unique()} if policy == "M1" else choices[policy]
        residuals = inner[["cut", "snpp"]].copy()
        residuals["err"] = np.abs(candidate_values(inner, mapping) - residuals.snpp)
        active = residuals[residuals.snpp > 0]
        q = active.groupby("cut").err.quantile(.8)
        result[policy + "_abs80_radius"] = result.cut.map(q)
    return result


def intensity_metrics(frame):
    populations = {"zero":frame[frame.snpp == 0], "positive_lt10":frame[(frame.snpp > 0)&(frame.snpp <10)],
                   "10_to_lt50":frame[(frame.snpp >=10)&(frame.snpp <50)], "50_plus":frame[frame.snpp >=50]}
    return {label:{"n":len(x), "methods":{m:{"mae":float((x[m]-x.snpp).abs().mean()) if len(x) else None,
                    "bias":float((x[m]-x.snpp).mean()) if len(x) else None} for m in METHODS}} for label,x in populations.items()}


def run():
    check_deadline()
    protected = [DATA/f for f in ("params.json","gates.csv","static_mask.parquet","eval_loso.csv","eval_final.csv")]
    protected += sorted((ROOT/"web/public/data").rglob("*.json"))
    protected += sorted((DATA/"scientific_audit").glob("*")) + sorted((DATA/"affine_audit").glob("*"))
    before = {str(p.relative_to(ROOT)):sha(p) for p in protected}
    data = AuditData(); frames, selections, numerical, coefficients = [], [], [], []

    def fold(allowed, held, outer, layer):
        check_deadline()
        frame=data.monthly("fold_fitted",allowed)
        tr,te=frame[frame.season.isin(allowed)],frame[frame.season==held]
        reference=fit_models(tr); affine=fit_affine(tr,reference); robust,diag=fit_huber(tr,affine)
        for item in diag:
            numerical.append({**item,"outer_held":outer,"held_out":held,"layer":layer,"training_seasons":";".join(map(str,allowed))})
        return predict_huber(predict_affine(predict(te,reference),affine),robust), robust

    for held in TRAIN:
        allowed=tuple(s for s in TRAIN if s!=held)
        inner=pd.concat([fold(tuple(s for s in allowed if s!=ih),ih,held,"inner")[0] for ih in allowed],ignore_index=True)
        choices,loss=choose(inner); test,params=fold(allowed,held,held,"outer")
        for policy,mapping in choices.items():
            test[policy]=candidate_values(test,mapping);test[policy+"_chosen"]=test.cut.map(mapping)
            for cut,method in mapping.items():
                selections.append({"outer_held":held,"cut":cut,"policy":policy,"candidate":method,
                    "internal_mae":float(loss.loc[cut,method]),"training_seasons":";".join(map(str,allowed))})
        frames.append(add_intervals(test,inner,choices))
        coefficients.append(params.reset_index().assign(outer_held=held))
        print("Huber outer fold complete:",held,flush=True)
    x=pd.concat(frames,ignore_index=True)
    prior=pd.read_csv(DATA/"affine_audit/outer_predictions.csv",dtype={"cut":str})
    joint=x.merge(prior[["cut","season","m","M1","M1_B","snpp"]],on=["cut","season","m"],suffixes=("","_old"),validate="one_to_one")
    if len(joint)!=5184 or any(not np.allclose(joint[c],joint[c+"_old"],atol=1e-10,rtol=0) for c in ["M1","M1_B","snpp"]):
        raise ValueError("Failed reproduction of previous controls")
    scores=score(x,METHODS);full=data.monthly("fold_fitted",TRAIN);gates=[]
    for method in ("M1","M1_B",*POLICIES):
        g=diagnostic_gates(scores,full,method).reset_index().assign(method=method);gates.append(g)
    all_gates=pd.concat(gates,ignore_index=True)
    old14=json.loads((DATA/"scientific_audit/summary.json").read_text())["mask_policies"]["published_fixed"]["enabled_diagnostic"]
    choices_frame=pd.DataFrame(selections);num=pd.DataFrame(numerical)
    # subgroup_metrics uses the earlier global METHODS; reproduce its structure
    # with explicit robust method names rather than changing an imported global.
    subgroup={}
    for label,group in {"aqua_zero_viirs_positive":x[(x.aqua==0)&(x.snpp>0)],"both_observed_zero":x[(x.aqua==0)&(x.snpp==0)],"aqua_positive":x[x.aqua>0]}.items():
        subgroup[label]={"n":len(group),"methods":{m:{"mae":float((group[m]-group.snpp).abs().mean()),
            "bias":float((group[m]-group.snpp).mean()),"prediction_sum":float(group[m].sum())} for m in METHODS}}
    report={"status":"development-experiment","external_validation":False,"controls_reproduced":True,
        "scores":summarize(scores),"enabled_diagnostic":{m:sorted(g.loc[g.enabled_diagnostic,"cut"].tolist()) for m,g in all_gates.groupby("method")},
        "contrasts":[paired_bootstrap(x,a,b) for a,b in [("M1_H","M1"),("M1_B_H","M1_B")]],
        "subgroups":subgroup,"intensity":intensity_metrics(x),
        "bands":{m:{p:band_metrics(x.assign(M1=x[m]),m+"_abs80_radius",cuts) for p,cuts in [("all54",None),("previous14",old14)]} for m in ("M1","M1_B",*POLICIES)},
        "choice_counts":{p:g.candidate.value_counts().astype(int).to_dict() for p,g in choices_frame.groupby("policy")},
        "numerical":{"fits":len(num),"max_iterations":int(num.iterations.max()),"max_kkt":float(num.max_kkt.max()),"all_converged":bool((num.max_kkt<=1e-6).all())},
        "mulchen":{"scores":summarize(scores[scores.cut=="08305"]),"gates":all_gates[all_gates.cut=="08305"].to_dict("records")}}
    if before!={str(p.relative_to(ROOT)):sha(p) for p in protected}:raise ValueError("Protected production/previous results changed")
    OUT.mkdir(parents=True,exist_ok=True)
    for filename,frame in [("outer_predictions.csv",x),("nested_selection.csv",choices_frame),("numerics.csv",num),("outer_coefficients.csv",pd.concat(coefficients,ignore_index=True)),("scores.csv",scores),("diagnostic_gates.csv",all_gates)]:frame.to_csv(OUT/filename,index=False)
    (OUT/"summary.json").write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
    manifest={"protocol_sha256":sha(PROTOCOL),"code_sha256":sha(Path(__file__)),"helpers_sha256":{f:sha(ROOT/"pipeline"/f) for f in ["scientific_audit.py","affine_experiment.py"]},
        "source_head":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"protected_sha256":before,"production_and_previous_unchanged":True,
        "input_sha256":{f:sha(DATA/f) for f in ["detections.parquet","celldays.parquet","static_mask.parquet"]},
        "output_sha256":{p.name:sha(p) for p in sorted(OUT.glob("*")) if p.name!="manifest.json"}}
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,allow_nan=False)+"\n")
    print("Huber experiment complete:",OUT,flush=True)
    return report


if __name__=="__main__":run()
