"""Development audit: refit masks inside folds, nest method choice and band calibration.

Never imports experiment.py or writes its production outputs. Uses only seasons
2012–2019 for evaluation and earlier detections for fitting the static mask.
See docs/reviews/2026-11-14-science-protocol-2.md, frozen before this run.
"""
import hashlib
import json
import platform
import subprocess
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed"
OUT = DATA / "scientific_audit"
TRAIN = tuple(range(2012, 2020))
KAPPAS = (0, 10, 30, 50, 100, 300, 1000000000)
CANDIDATES = ("M1",) + tuple(f"A_{k}" for k in KAPPAS)
POLICIES = ("none", "published_fixed", "fold_fitted", "pre_overlap")
PROTOCOL = ROOT / "docs/reviews/2026-11-14-science-protocol-2.md"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fit_models(training):
    denominator = training.aqua.sum()
    if denominator <= 0:
        raise ValueError("No Aqua training signal; cannot fit a regional ratio")
    ratio = float(training.snpp.sum() / denominator)
    regional = training.groupby("g").agg(A=("aqua", "sum"), V=("snpp", "sum"))
    regional["rR"] = np.divide(regional.V, regional.A, out=np.full(len(regional), ratio), where=regional.A.to_numpy() > 0)
    local = training.groupby(["cut", "g"]).agg(A=("aqua", "sum"), V=("snpp", "sum"))
    climatology = training.groupby(["cut", "m"]).snpp.median().rename("clim")
    return {"ratio": ratio, "regional": regional, "local": local, "climatology": climatology}


def predict(frame, model):
    x = frame.merge(model["climatology"], on=["cut", "m"], how="left", validate="many_to_one")
    x = x.merge(model["regional"][["rR"]], on="g", how="left", validate="many_to_one")
    x = x.merge(model["local"], on=["cut", "g"], how="left", validate="many_to_one")
    if x[["clim", "rR", "A", "V"]].isna().any().any():
        raise ValueError("Training did not cover the expected commune/month groups")
    x["M0"], x["M1"], x["M2"] = x.aqua, x.aqua * model["ratio"], x.clim
    for k in KAPPAS:
        denominator = (x.A + k).to_numpy(dtype=float)
        numerator = (x.V + k * x.rR).to_numpy(dtype=float)
        # At k=0 with A=0 the local ratio is unidentified, not infinite.
        factor = np.divide(numerator, denominator, out=x.rR.to_numpy(copy=True), where=denominator > 0)
        x[f"A_{k}"] = x.aqua * factor
    if not np.isfinite(x[["M0", "M2", *CANDIDATES]].to_numpy()).all():
        raise ValueError("Non-finite predictions")
    return x.drop(columns=["clim", "rR", "A", "V"])


def choose_methods(inner):
    losses = pd.DataFrame({c: (inner[c] - inner.snpp).abs() for c in CANDIDATES})
    losses["cut"] = inner.cut.to_numpy()
    mean = losses.groupby("cut").mean()
    choices = {}
    for cut, row in mean.iterrows():
        best = min(KAPPAS, key=lambda k: (row[f"A_{k}"], -k))
        choices[cut] = f"A_{best}" if row[f"A_{best}"] < .99 * row.M1 else "M1"
    return choices, mean


def calibration(inner):
    active = inner[inner.snpp > 0].copy()
    active["absolute"] = (active.M1 - active.snpp).abs()
    active["scaled"] = active.absolute / (1 + active.M1)
    return active.groupby("cut").agg(mae=("absolute", "mean"), q80=("scaled", lambda s: s.quantile(.8)), n=("absolute", "size"))


def add_bands(external, inner):
    x = external.merge(calibration(inner), on="cut", how="left", validate="many_to_one")
    x["band_mae_radius"] = x.mae
    x["band_scaled_radius"] = x.q80 * (1 + x.M1)
    x["calibration_n"] = x.n.fillna(0).astype(int)
    return x.drop(columns=["mae", "q80", "n"])


def score(frame, methods):
    records = []
    for (cut, season), group in frame.groupby(["cut", "season"]):
        for method in methods:
            error = group[method] - group.snpp
            records.append({"cut": cut, "season": int(season), "method": method,
                            "mae": float(error.abs().mean()), "bias": float(error.mean()), "n": len(group),
                            "aqua": float(group.aqua.sum()), "target": float(group.snpp.sum())})
    return pd.DataFrame(records)


def diagnostic_gates(scores, full_training, method):
    pivot = scores.pivot(index=["cut", "season"], columns="method", values="mae")
    signals = full_training.groupby("cut").aqua.sum()
    gates = pd.DataFrame({"aqua_train": signals,
        "wins_vs_raw": (pivot[method] < pivot.M0).groupby("cut").sum(),
        "wins_vs_clim": (pivot[method] < pivot.M2).groupby("cut").sum()})
    gates["enabled_diagnostic"] = (gates.aqua_train >= 50) & (gates.wins_vs_raw >= 6) & (gates.wins_vs_clim >= 6)
    return gates


def band_metrics(frame, radius_col, cuts=None):
    if cuts is not None:
        frame = frame[frame.cut.isin(cuts)]
    report = {}
    for label, population in [("all_months", frame), ("active_months", frame[frame.snpp > 0])]:
        x = population[population[radius_col].notna()]
        lo = np.maximum(0, x.M1 - x[radius_col])
        hi = x.M1 + x[radius_col]
        report[label] = {"n": len(x), "missing_calibration": len(population) - len(x),
                         "coverage": float(((x.snpp >= lo) & (x.snpp <= hi)).mean()) if len(x) else None,
                         "mean_width": float((hi - lo).mean()) if len(x) else None}
    return report


class AuditData:
    def __init__(self):
        self.con = duckdb.connect()
        self.con.execute(f"create view det as select *, case when month(acq_date)>=7 then year(acq_date) else year(acq_date)-1 end season from read_parquet('{DATA}/detections.parquet')")
        self.con.execute(f"create view days as select * from read_parquet('{DATA}/celldays.parquet')")
        self.cuts = [r[0] for r in self.con.execute("select distinct cut from days order by 1").fetchall()]
        if len(self.cuts) != 54:
            raise ValueError("Expected 54 communes")
        self.published_mask = set(self.con.execute(f"select distinct cell_x,cell_y from read_parquet('{DATA}/static_mask.parquet')").fetchall())
        self.mask_cache, self.monthly_cache = {}, {}

    def fit_mask(self, allowed):
        allowed = tuple(sorted(allowed))
        if not set(allowed).issubset(TRAIN):
            raise ValueError("Mask must never see a season outside the training pool")
        if allowed in self.mask_cache:
            return self.mask_cache[allowed]
        inclusion = "season < 2012"
        if allowed:
            inclusion += " or season in (" + ",".join(map(str, allowed)) + ")"
        stats = self.con.execute(f"""
          select cell_x,cell_y,count(distinct acq_date) n_days,count(distinct season) n_seasons,
          avg(case when type is not null then (type=1)::int end) p1,
          avg(case when type is not null then (type=2)::int end) p2
          from det where acq_date < date '2020-07-01' and ({inclusion}) group by 1,2
        """).fetchall()
        core = {}
        for x, y, days, seasons, p1, p2 in stats:
            if days >= 30 and seasons >= 8:
                core[x, y] = ("A", days)
            elif days >= 10 and p1 is not None and p1 >= .5:
                core[x, y] = ("B", days)
            elif days >= 15 and p2 is not None and p2 >= .6:
                core[x, y] = ("C", days)
        mask = set(core)
        for (x, y), (rule, days) in core.items():
            radius = 2 if rule == "B" else 1 if rule == "A" and days >= 100 else 0
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    mask.add((x + dx, y + dy))
        self.mask_cache[allowed] = mask
        return mask

    def mask(self, policy, allowed):
        if policy == "none":
            return set()
        if policy == "published_fixed":
            return self.published_mask
        return self.fit_mask(allowed if policy == "fold_fitted" else ())

    def monthly(self, policy, allowed):
        mask = self.mask(policy, allowed)
        key = tuple(sorted(mask))
        if key in self.monthly_cache:
            return self.monthly_cache[key].copy()
        self.con.register("audit_mask", pd.DataFrame(list(mask), columns=["cell_x", "cell_y"]).astype("int64"))
        monthly = self.con.execute("""
          select cut,season,m,
          count(*) filter (sat='Aqua') aqua, count(*) filter (sat='SNPP') snpp
          from days d where season between 2012 and 2019 and sat in ('Aqua','SNPP')
          and not exists (select 1 from audit_mask s where s.cell_x=d.cell_x and s.cell_y=d.cell_y)
          group by all
        """).df()
        grid = pd.MultiIndex.from_product([self.cuts, TRAIN, range(1, 13)], names=["cut", "season", "m"]).to_frame(index=False)
        frame = grid.merge(monthly, how="left", validate="one_to_one").fillna({"aqua": 0, "snpp": 0})
        frame["g"] = frame.m.map(lambda m: "JJA" if m in (6, 7, 8) else str(m))
        self.monthly_cache[key] = frame
        return frame.copy()


def summarize(scores):
    return {method: {"sum_commune_season_mae": float(g.mae.sum()), "mean_monthly_mae": float(g.mae.mean()),
                     "mean_bias": float(g.bias.mean())} for method, g in scores.groupby("method")}


def run():
    production = [DATA / f for f in ("params.json", "gates.csv", "eval_loso.csv", "eval_final.csv", "static_mask.parquet")]
    production += sorted((ROOT / "web/public/data").rglob("*.json"))
    before = {str(p.relative_to(ROOT)): sha(p) for p in production}
    data = AuditData()
    if data.fit_mask(TRAIN) != data.published_mask:
        raise ValueError("Cannot reproduce published mask; stop audit before comparing methods")
    report = {"status": "development-audit", "production_changed": False, "external_validation": False,
              "seasons": list(TRAIN), "excluded_from_analysis": "seasons 2020 onward (Jan-Jun 2020 belongs to season 2019)", "mask_cells_published": len(data.published_mask),
              "mask_policies": {}, "nested": {}, "bands": {}}
    predictions, selections, mask_rows, all_scores, all_gates = [], [], [], [], []
    fixed_predictions = None
    for policy in POLICIES:
        frames = []
        for held in TRAIN:
            allowed = tuple(s for s in TRAIN if s != held)
            frame = data.monthly(policy, allowed)
            tr, te = frame[frame.season.isin(allowed)], frame[frame.season == held]
            model = fit_models(tr)
            pred = predict(te, model)
            frames.append(pred)
            mask = data.mask(policy, allowed)
            mask_rows.append({"policy": policy, "held_out": held, "cells": len(mask),
                              "added_vs_published": len(mask - data.published_mask),
                              "removed_vs_published": len(data.published_mask - mask),
                              "fit_seasons": ";".join(map(str, allowed)) if policy == "fold_fitted" else "fixed",
                              "ratio": model["ratio"]})
        combined = pd.concat(frames, ignore_index=True)
        combined["policy"] = policy
        scores = score(combined, ["M0", "M1", "M2"])
        full = data.monthly(policy, TRAIN)
        gates = diagnostic_gates(scores, full, "M1")
        scores["policy"] = policy; gates["policy"] = policy
        all_scores.append(scores); all_gates.append(gates.reset_index())
        report["mask_policies"][policy] = {"scores": summarize(scores),
            "enabled_diagnostic": sorted(gates.index[gates.enabled_diagnostic].tolist()),
            "target_cell_days_evaluated": int(combined.snpp.sum()), "aqua_cell_days_evaluated": int(combined.aqua.sum())}
        predictions.append(combined)
        if policy == "published_fixed":
            fixed_predictions = combined
            published = json.loads((DATA / "params.json").read_text())
            if not np.isclose(scores[scores.method == "M1"].mae.sum(), published["loso_total_mae"]["M1"], atol=1e-7):
                raise ValueError("Published M1 error cannot be reproduced")
            previous = pd.read_csv(DATA / "gates.csv", index_col=0, dtype={0: str})
            expected = set(previous.index[previous.enabled].astype(str).str.zfill(5))
            if set(gates.index[gates.enabled_diagnostic]) != expected:
                raise ValueError("Published commune gates cannot be reproduced")
        print("mask policy complete:", policy, "diagnostic enabled:", int(gates.enabled_diagnostic.sum()), flush=True)

    # Every inner fold has its own mask and model. Neither outer observations
    # nor their source detections enter selection or residual calibration.
    nested_frames = []
    for held in TRAIN:
        outer_train = tuple(s for s in TRAIN if s != held)
        inner_frames = []
        for inner_held in outer_train:
            inner_train = tuple(s for s in outer_train if s != inner_held)
            frame = data.monthly("fold_fitted", inner_train)
            inner_frames.append(predict(frame[frame.season == inner_held], fit_models(frame[frame.season.isin(inner_train)])))
        inner = pd.concat(inner_frames, ignore_index=True)
        choices, losses = choose_methods(inner)
        frame = data.monthly("fold_fitted", outer_train)
        external = predict(frame[frame.season == held], fit_models(frame[frame.season.isin(outer_train)]))
        external["chosen_method"] = external.cut.map(choices)
        external["selected"] = [row[method] for row, method in zip(external.to_dict("records"), external.chosen_method)]
        external = add_bands(external, inner)
        nested_frames.append(external)
        for cut, method in choices.items():
            selections.append({"held_out": held, "cut": cut, "chosen_method": method,
                               "internal_mae_M1": float(losses.loc[cut, "M1"]),
                               "internal_mae_selected": float(losses.loc[cut, method]),
                               "inner_seasons": ";".join(map(str, outer_train))})
        print("nested outer fold complete:", held, flush=True)
    nested = pd.concat(nested_frames, ignore_index=True)
    nested["policy"] = "nested_fold_fitted"
    nested_scores = score(nested, ["M0", "M1", "M2", "selected"])
    nested_gates = diagnostic_gates(nested_scores, data.monthly("fold_fitted", TRAIN), "selected")
    report["nested"]["scores"] = summarize(nested_scores)
    report["nested"]["enabled_diagnostic"] = sorted(nested_gates.index[nested_gates.enabled_diagnostic].tolist())
    report["nested"]["choice_counts"] = pd.Series([r["chosen_method"] for r in selections]).value_counts().astype(int).to_dict()
    deltas = nested.assign(loss_delta=(nested.selected - nested.snpp).abs() - (nested.M1 - nested.snpp).abs()).groupby("season").loss_delta.mean().to_numpy()
    rng = np.random.default_rng(20261114)
    bootstrap = rng.choice(deltas, size=(5000, len(TRAIN)), replace=True).mean(axis=1)
    report["nested"]["paired_delta_mae_selected_minus_M1"] = {"mean": float(deltas.mean()),
        "percentile_interval": [float(v) for v in np.quantile(bootstrap, [.025, .975])], "blocks": 8, "replicates": 5000, "seed": 20261114}
    nested_scores["policy"] = "nested_fold_fitted"; nested_gates["policy"] = "nested_fold_fitted"
    all_scores.append(nested_scores); all_gates.append(nested_gates.reset_index()); predictions.append(nested)
    # Apparent coverage reuses the same residuals for fitting and measurement,
    # reproducing the old descriptive calculation for an explicit comparison.
    apparent = add_bands(fixed_predictions, fixed_predictions)
    published_enabled = report["mask_policies"]["published_fixed"]["enabled_diagnostic"]
    for label, cuts in [("all_communes", None), ("previously_enabled_14", published_enabled)]:
        report["bands"][label] = {
            "apparent_fixed_mask": band_metrics(apparent, "band_mae_radius", cuts),
            "external_fold_fitted_mae": band_metrics(nested, "band_mae_radius", cuts),
            "external_fold_fitted_scaled80": band_metrics(nested, "band_scaled_radius", cuts)}
    zeros = nested[(nested.aqua == 0) & (nested.snpp > 0)]
    report["zero_aqua_positive_viirs"] = {"months": len(zeros), "evaluated_months": len(nested),
        "target_cell_days": int(zeros.snpp.sum()), "target_cell_days_total": int(nested.snpp.sum()),
        "note": "Structural diagnostic: every multiplicative candidate predicts zero here; not an affine-model evaluation."}
    # Track known version discontinuities without assigning a cause.
    report["aqua_version_diagnostic_scope"] = "Aqua canonical daytime detections assigned to the 54 communes, before static mask; seasons before 2020"
    report["aqua_version_diagnostic"] = [dict(zip(("year", "version", "n", "type2"), row)) for row in data.con.execute(f"""
      select year(acq_date) y,version,count(*) n,count(*) filter(type=2) type2
      from det d where sat='Aqua' and season < 2020 and exists (
        select 1 from read_parquet('{DATA}/cells_comuna.parquet') c where c.cell_x=d.cell_x and c.cell_y=d.cell_y)
      group by 1,2 order by 1,2
    """).fetchall()]
    report["mulchen"] = {policy: gate[gate.cut == "08305"].to_dict("records") for policy, gate in zip([*POLICIES, "nested_fold_fitted"], all_gates)}
    after = {str(p.relative_to(ROOT)): sha(p) for p in production}
    if after != before:
        raise ValueError("Production files changed during audit")
    inputs = [DATA / f for f in ("detections.parquet", "celldays.parquet", "static_mask.parquet", "gates.csv", "params.json")]
    manifest = {"input_sha256": {str(p.relative_to(ROOT)): sha(p) for p in inputs}, "protocol_sha256": sha(PROTOCOL),
                "code_sha256": sha(Path(__file__)), "source_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "runtime": {"python": platform.python_version(), "duckdb": duckdb.__version__, "pandas": pd.__version__, "numpy": np.__version__},
                "production_before_sha256": before, "production_unchanged": True}
    OUT.mkdir(parents=True, exist_ok=True)
    pd.concat(all_scores, ignore_index=True).to_csv(OUT / "scores.csv", index=False)
    pd.concat(all_gates, ignore_index=True).to_csv(OUT / "diagnostic_gates.csv", index=False)
    pd.DataFrame(mask_rows).to_csv(OUT / "mask_folds.csv", index=False)
    pd.DataFrame(selections).to_csv(OUT / "nested_selection.csv", index=False)
    pd.concat(predictions, ignore_index=True).to_csv(OUT / "outer_predictions.csv", index=False)
    (OUT / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print("audit complete:", OUT, flush=True)
    return report


if __name__ == "__main__":
    run()
