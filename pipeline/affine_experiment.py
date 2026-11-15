"""Nested development experiment for a monotone, regularized affine candidate.

Read-only production inputs; outputs only to affine_audit/. See frozen protocol 3.
Imports the mask and controls from scientific_audit without executing that audit.
"""
import json
import platform
import subprocess
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from scientific_audit import (ROOT, DATA, TRAIN, AuditData, band_metrics,
    choose_methods, diagnostic_gates, fit_models, predict, score, sha, summarize)

OUT = DATA / "affine_audit"
PROTOCOL = ROOT / "docs/reviews/2026-11-14-science-protocol-3.md"
LAMBDAS = (.01, .1, 1., 10.)
POLICIES = ("M1_A", "M1_B", "M1_A_B")
METHODS = ("M0", "M1", "M2", *POLICIES)


def b_name(lam):
    return f"B_{lam:g}"


def fit_affine(training, reference):
    if len(training) == 0 or not np.isfinite(training[["aqua", "snpp"]]).all().all():
        raise ValueError("Invalid affine training observations")
    t = training.copy()
    scale = t.assign(x2=t.aqua ** 2).groupby("g").x2.mean().pow(.5).clip(lower=1)
    t["z"] = t.aqua / t.g.map(scale)
    t["z2"], t["zy"] = t.z ** 2, t.z * t.snpp
    moments = t.groupby(["cut", "g"]).agg(z=("z", "mean"), z2=("z2", "mean"),
        y=("snpp", "mean"), zy=("zy", "mean"), n=("snpp", "size"))
    groups = moments.index.get_level_values("g")
    moments["scale"] = scale.reindex(groups).to_numpy()
    moments["prior_beta"] = reference["regional"].rR.reindex(groups).to_numpy() * moments.scale
    if moments[["scale", "prior_beta"]].isna().any().any():
        raise ValueError("Missing training-only normalization or regional prior")
    params = moments[["scale", "prior_beta", "n"]].copy()
    for lam in LAMBDAS:
        # Normal equations for mean squared error plus a ridge penalty toward
        # [intercept=0, scaled slope=regional_ratio * scale].
        h00, h01, h11 = 1 + lam, moments.z, moments.z2 + lam
        q0, q1 = moments.y, moments.zy + lam * moments.prior_beta
        determinant = h00 * h11 - h01 ** 2
        if (determinant <= 0).any():
            raise ValueError("Affine normal equations are not positive definite")
        a = (q0 * h11 - q1 * h01) / determinant
        beta = (q1 * h00 - q0 * h01) / determinant
        # The single inequality beta>=0 has an exact boundary solution.
        a = a.where(beta >= 0, q0 / h00)
        beta = beta.clip(lower=0)
        params[b_name(lam) + "_a"] = a
        params[b_name(lam) + "_b"] = beta / moments.scale
    if not np.isfinite(params.to_numpy()).all():
        raise ValueError("Non-finite affine coefficients")
    return params


def predict_affine(frame, params):
    x = frame.merge(params, on=["cut", "g"], how="left", validate="many_to_one")
    if x.scale.isna().any():
        raise ValueError("Affine training has no parameters for a test group")
    for lam in LAMBDAS:
        name = b_name(lam)
        x[name] = np.maximum(0, x[name + "_a"] + x[name + "_b"] * x.aqua)
    names = [b_name(lam) for lam in LAMBDAS]
    if not np.isfinite(x[names]).all().all():
        raise ValueError("Non-finite affine predictions")
    return x.drop(columns=params.columns)


def choose_policies(inner):
    ma, _ = choose_methods(inner)
    bcols = [b_name(lam) for lam in LAMBDAS]
    # Compute each candidate's loss only from predictions on inner holdouts.
    from scientific_audit import CANDIDATES
    losses = pd.DataFrame({c: (inner[c] - inner.snpp).abs() for c in [*CANDIDATES, *bcols]})
    losses["cut"] = inner.cut.to_numpy()
    losses = losses.groupby("cut").mean()
    choices = {p: {} for p in POLICIES}
    for cut, row in losses.iterrows():
        lam = min(LAMBDAS, key=lambda lam: (row[b_name(lam)], -lam))
        best = b_name(lam)
        choices["M1_A"][cut] = ma[cut]
        choices["M1_B"][cut] = best if row[best] < .99 * row.M1 else "M1"
        choices["M1_A_B"][cut] = best if row[best] < .99 * row[ma[cut]] else ma[cut]
    return choices, losses


def candidate_values(frame, choices):
    selected = frame.cut.map(choices)
    if selected.isna().any():
        raise ValueError("No candidate selected for a test commune")
    return np.array([row[method] for row, method in zip(frame.to_dict("records"), selected)], dtype=float)


def calibrate_bands(external, inner, choices):
    out = external.copy()
    # For each outer fold, calibrate both bands on identical inner active rows.
    for policy in ("M1", *POLICIES):
        mapping = {cut: "M1" for cut in inner.cut.unique()} if policy == "M1" else choices[policy]
        train = inner[["cut", "snpp"]].copy()
        train["pred"] = candidate_values(inner, mapping)
        train = train[train.snpp > 0]
        train["err"] = (train.pred - train.snpp).abs()
        train["scaled"] = train.err / (1 + train.pred)
        cal = train.groupby("cut").agg(abs80=("err", lambda s: s.quantile(.8)),
            scaled80=("scaled", lambda s: s.quantile(.8)), n=("err", "size"))
        out[policy + "_abs80_radius"] = out.cut.map(cal.abs80)
        out[policy + "_scaled80_radius"] = out.cut.map(cal.scaled80) * (1 + out[policy])
        out[policy + "_calibration_n"] = out.cut.map(cal.n).fillna(0).astype(int)
    return out


def paired_bootstrap(frame, candidate, reference):
    delta = ((frame[candidate] - frame.snpp).abs() - (frame[reference] - frame.snpp).abs())
    blocks = frame.assign(delta=delta).groupby("season").delta.mean()
    draws = np.random.default_rng(20261114).choice(blocks.to_numpy(), size=(5000, len(blocks)), replace=True).mean(axis=1)
    return {"candidate": candidate, "reference": reference, "mean_delta_mae": float(blocks.mean()),
        "interval_95_percentile": [float(v) for v in np.quantile(draws, [.025, .975])],
        "per_season_delta": {str(k): float(v) for k, v in blocks.items()}, "blocks": len(blocks), "replicates": 5000, "seed": 20261114}


def subgroup_metrics(frame):
    populations = {"aqua_zero_viirs_positive": frame[(frame.aqua == 0) & (frame.snpp > 0)],
                   "both_observed_zero": frame[(frame.aqua == 0) & (frame.snpp == 0)],
                   "aqua_positive": frame[frame.aqua > 0]}
    output = {}
    for name, group in populations.items():
        output[name] = {"n": len(group), "target_sum": float(group.snpp.sum()), "methods": {}}
        for method in METHODS:
            error = group[method] - group.snpp
            output[name]["methods"][method] = {"mae": float(error.abs().mean()) if len(group) else None,
                "bias": float(error.mean()) if len(group) else None, "prediction_sum": float(group[method].sum()),
                "months_positive_estimate": int((group[method] > 1e-12).sum())}
    return output


def run():
    protected = [DATA / f for f in ("params.json", "gates.csv", "eval_loso.csv", "eval_final.csv", "static_mask.parquet")]
    protected += sorted((ROOT / "web/public/data").rglob("*.json"))
    protected += sorted((DATA / "scientific_audit").glob("*"))
    before = {str(p.relative_to(ROOT)): sha(p) for p in protected}
    data = AuditData()
    if data.fit_mask(TRAIN) != data.published_mask:
        raise ValueError("Cannot reproduce the frozen static mask")
    outer, selections, coefficients = [], [], []

    def predict_fold(training_seasons, held):
        frame = data.monthly("fold_fitted", training_seasons)
        training, test = frame[frame.season.isin(training_seasons)], frame[frame.season == held]
        model = fit_models(training)
        params = fit_affine(training, model)
        return predict_affine(predict(test, model), params), params

    for held in TRAIN:
        training_seasons = tuple(s for s in TRAIN if s != held)
        inner = []
        for inner_held in training_seasons:
            allowed = tuple(s for s in training_seasons if s != inner_held)
            prediction, _ = predict_fold(allowed, inner_held)
            inner.append(prediction)
        inner = pd.concat(inner, ignore_index=True)
        choices, losses = choose_policies(inner)
        test, params = predict_fold(training_seasons, held)
        for policy in POLICIES:
            test[policy] = candidate_values(test, choices[policy])
            test[policy + "_chosen"] = test.cut.map(choices[policy])
            for cut, candidate in choices[policy].items():
                selections.append({"held_out": held, "cut": cut, "policy": policy, "candidate": candidate,
                    "internal_mae_M1": float(losses.loc[cut, "M1"]), "internal_mae_selected": float(losses.loc[cut, candidate]),
                    "training_seasons": ";".join(map(str, training_seasons))})
        outer.append(calibrate_bands(test, inner, choices))
        params = params.reset_index().assign(held_out=held, training_seasons=";".join(map(str, training_seasons)))
        coefficients.append(params)
        print("affine outer fold complete:", held, flush=True)
    external = pd.concat(outer, ignore_index=True)
    previous = pd.read_csv(DATA / "scientific_audit/outer_predictions.csv", dtype={"cut": str})
    previous = previous[previous.policy == "nested_fold_fitted"]
    compare = external.merge(previous[["cut", "season", "m", "M1", "selected", "snpp"]], on=["cut", "season", "m"], suffixes=("", "_old"), validate="one_to_one")
    if len(compare) != 5184 or not np.allclose(compare.M1, compare.M1_old, rtol=0, atol=1e-10) or not np.allclose(compare.M1_A, compare.selected, rtol=0, atol=1e-10) or not np.array_equal(compare.snpp, compare.snpp_old):
        raise ValueError("Iteration 2 control predictions do not reproduce")
    scores = score(external, METHODS)
    full = data.monthly("fold_fitted", TRAIN)
    gates, gate_summary = [], {}
    for method in ("M1", *POLICIES):
        gate = diagnostic_gates(scores, full, method).reset_index()
        gate["method"] = method; gates.append(gate)
        gate_summary[method] = sorted(gate.loc[gate.enabled_diagnostic, "cut"].tolist())
    previous_summary = json.loads((DATA / "scientific_audit/summary.json").read_text())
    published14 = previous_summary["mask_policies"]["published_fixed"]["enabled_diagnostic"]
    bands = {}
    for policy in ("M1", *POLICIES):
        # band_metrics expects an M1 column: supply the actual policy prediction.
        evaluation = external.assign(M1=external[policy])
        bands[policy] = {population: {kind: band_metrics(evaluation, policy + "_" + kind + "_radius", cuts)
            for kind in ("abs80", "scaled80")} for population, cuts in [("all54", None), ("previously_enabled14", published14)]}
    choice_frame = pd.DataFrame(selections)
    all_gates = pd.concat(gates, ignore_index=True)
    report = {"status": "development-experiment", "external_validation": False, "production_changed": False,
        "training_seasons": list(TRAIN), "excluded": "seasons 2020 onward", "control_predictions_reproduced": True,
        "scores": summarize(scores), "enabled_diagnostic": gate_summary,
        "choice_counts": {p: choice_frame[choice_frame.policy == p].candidate.value_counts().astype(int).to_dict() for p in POLICIES},
        "contrasts": [paired_bootstrap(external, a, b) for a, b in [("M1_B", "M1"), ("M1_A_B", "M1_A"), ("M1_A_B", "M1")]],
        "subgroups": subgroup_metrics(external), "bands": bands,
        "mulchen": {"gates": all_gates[all_gates.cut == "08305"].to_dict("records"),
                    "scores": summarize(scores[scores.cut == "08305"]),
                    "choices": choice_frame[choice_frame.cut == "08305"].to_dict("records")}}
    after = {str(p.relative_to(ROOT)): sha(p) for p in protected}
    if after != before:
        raise ValueError("Production or previous audit changed during experiment")
    inputs = [DATA / f for f in ("detections.parquet", "celldays.parquet", "static_mask.parquet", "gates.csv", "params.json")]
    manifest = {"input_sha256": {str(p.relative_to(ROOT)): sha(p) for p in inputs}, "protocol_sha256": sha(PROTOCOL),
        "code_sha256": sha(Path(__file__)), "audit_helper_sha256": sha(ROOT / "pipeline/scientific_audit.py"),
        "source_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "runtime": {"python": platform.python_version(), "duckdb": duckdb.__version__, "pandas": pd.__version__, "numpy": np.__version__},
        "protected_sha256": before, "production_and_iteration2_unchanged": True}
    OUT.mkdir(parents=True, exist_ok=True)
    external.to_csv(OUT / "outer_predictions.csv", index=False)
    choice_frame.to_csv(OUT / "nested_selection.csv", index=False)
    pd.concat(coefficients, ignore_index=True).to_csv(OUT / "outer_coefficients.csv", index=False)
    scores.to_csv(OUT / "scores.csv", index=False)
    all_gates.to_csv(OUT / "diagnostic_gates.csv", index=False)
    (OUT / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    manifest["output_sha256"] = {p.name: sha(p) for p in sorted(OUT.glob("*")) if p.name != "manifest.json"}
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print("affine experiment complete:", OUT, flush=True)
    return report


if __name__ == "__main__":
    run()
