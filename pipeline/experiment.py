"""Experimento de armonización Aqua → VIIRS (S-NPP diurno), por comuna y mes. Manifiesto v2 §5.

Particiones congeladas (14-11-2026 14:20), temporadas jul–jun nombradas por el año de inicio:
  entrenamiento + selección interna (LOSO): 2012–2019 (8 temporadas)
  prueba final (se miró una vez con A(κ); después se eligió M1 por parsimonia → sus cifras 2020–2021 son DESCRIPTIVAS)
  2022→ : deriva orbital de Aqua; solo diagnóstico.
  Excluidos en ambos sensores: 2020-08 y 2020-09 (falla de Aqua 16-08 a 02-09-2020).
Métodos: M0 Aqua sin corregir · M1 factor regional constante · M2 climatología VIIRS por comuna y mes (MEDIANA, sin Aqua)
         A(κ) factor por grupo de meses con encogimiento regional: r = (V + κ r_R)/(A + κ)
Compuertas por comuna (SOLO con LOSO, revisión científica 14-11 16:30):
  M1 gana a M2 en ≥ 6 de 8 temporadas, M1 gana a M0 en ≥ 6 de 8 temporadas, y Aqua 2012–2019 ≥ 50 celdas-día.
Salida: data/processed/eval_loso.csv, eval_final.csv, gates.csv, params.json
"""
import json, pathlib, duckdb, pandas as pd, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[1]; OUT = ROOT / "data/processed"
TRAIN = list(range(2012, 2020)); TEST = [2020, 2021]; KAPPAS = [0, 10, 30, 50, 100, 300, 1e9]
MIN_AQUA, MIN_WINS = 50, 6
def connect():
    """Usa goliat.duckdb si existe; si no (clon fresco), reconstruye las tablas necesarias desde los parquet versionados."""
    db = OUT / "goliat.duckdb"
    if db.exists():
        return duckdb.connect(str(db), read_only=True)
    c = duckdb.connect()
    for t, f in [("monthly_masked", "celldays_comuna_month_masked.parquet"), ("monthly", "celldays_comuna_month.parquet"), ("cells_comuna", "cells_comuna.parquet"),
                 ("celldays", "celldays.parquet"), ("static_mask", "static_mask.parquet"), ("det", "detections.parquet")]:
        if (OUT / f).exists(): c.execute(f"create view {t} as select * from read_parquet('{OUT / f}')")
    return c
con = connect()
cuts = [r[0] for r in con.execute("select distinct cut from cells_comuna order by 1").fetchall()]
m = con.execute("""select cut, season, m, sum(case when sat='Aqua' then celldays end) aqua, sum(case when sat='SNPP' then celldays end) snpp
                   from monthly_masked where season between 2012 and 2025 group by all""").df()
grid = pd.MultiIndex.from_product([cuts, range(2012, 2026), range(1, 13)], names=["cut", "season", "m"]).to_frame(index=False)
d = grid.merge(m, how="left").fillna({"aqua": 0, "snpp": 0})
d = d[~((d.season == 2020) & d.m.isin([8, 9]))]  # falla de Aqua
d["g"] = d.m.map(lambda x: "JJA" if x in (6, 7, 8) else str(x))

def fit(tr):
    r_const = tr.snpp.sum() / tr.aqua.sum()
    clim = tr.groupby(["cut", "m"]).snpp.median().rename("clim")
    reg = tr.groupby("g").agg(A=("aqua", "sum"), V=("snpp", "sum")); reg["rR"] = reg.V / reg.A
    loc = tr.groupby(["cut", "g"]).agg(A=("aqua", "sum"), V=("snpp", "sum"))
    return dict(r_const=r_const, clim=clim, reg=reg, loc=loc)

def predict(te, p, kappa):
    x = te.merge(p["clim"], on=["cut", "m"], how="left").merge(p["reg"][["rR"]], on="g", how="left") \
          .merge(p["loc"], on=["cut", "g"], how="left").fillna({"A": 0, "V": 0, "clim": 0})
    x["M0"] = x.aqua; x["M1"] = x.aqua * p["r_const"]; x["M2"] = x.clim
    r = (x.V + kappa * x.rR) / (x.A + kappa) if kappa < 1e8 else x.rR
    x["A_k"] = x.aqua * r
    return x

def score(x, cols):
    rows = []
    for cut, grp in x.groupby("cut"):
        for c in cols:
            e = grp[c] - grp.snpp
            rows.append(dict(cut=cut, method=c, mae=e.abs().mean(), bias=e.mean(), n=len(grp), aqua_sum=grp.aqua.sum()))
    return pd.DataFrame(rows)

# 1) LOSO en entrenamiento
loso, preds = [], []
for s in TRAIN:
    tr, te = d[d.season.isin([t for t in TRAIN if t != s])], d[d.season == s]
    p = fit(tr)
    for k in KAPPAS:
        x = predict(te, p, k); sc = score(x, ["M0", "M1", "M2", "A_k"]); sc["kappa"] = k; sc["held_out"] = s; loso.append(sc)
        if k == KAPPAS[0]: preds.append(x[["cut", "season", "m", "aqua", "snpp", "M0", "M1", "M2"]])
loso = pd.concat(loso); preds = pd.concat(preds)
tot = loso[loso.method == "A_k"].groupby("kappa").mae.sum()
ctrl = loso[loso.kappa == KAPPAS[0]].groupby("method").mae.sum()
print("MAE total LOSO:", {k: round(v, 1) for k, v in ctrl.items() if k != "A_k"}, "| A(κ):", {k: round(v, 1) for k, v in tot.items()})
kappa_best = float(tot.idxmin())
loso.to_csv(OUT / "eval_loso.csv", index=False)

# 2) Compuertas por comuna, solo LOSO
piv = loso[loso.kappa == KAPPAS[0]].pivot_table(index=["cut", "held_out"], columns="method", values="mae")
wins = pd.DataFrame({"wins_vs_M2": (piv.M1 < piv.M2).groupby("cut").sum(), "wins_vs_M0": (piv.M1 < piv.M0).groupby("cut").sum()})
g = pd.DataFrame(index=cuts)
tr_all = d[d.season.isin(TRAIN)]
g["aqua_train"] = tr_all.groupby("cut").aqua.sum(); g["snpp_train"] = tr_all.groupby("cut").snpp.sum()
lm = loso[loso.kappa == KAPPAS[0]].groupby(["cut", "method"]).mae.mean().unstack()
g["loso_mae_M0"], g["loso_mae_M1"], g["loso_mae_M2"] = lm.M0, lm.M1, lm.M2
g = g.join(wins)
g["gate_aqua"] = g.aqua_train >= MIN_AQUA
g["gate_vs_clim"] = g.wins_vs_M2 >= MIN_WINS
g["gate_vs_raw"] = g.wins_vs_M0 >= MIN_WINS
g["enabled"] = g.gate_aqua & g.gate_vs_clim & g.gate_vs_raw

# error típico y cobertura empírica de la banda (LOSO, M1), por comuna, en meses activos (snpp > 0)
act = preds[preds.snpp > 0].copy(); act["err"] = (act.M1 - act.snpp).abs()
mae_act = act.groupby("cut").err.mean().rename("band_mae")
act = act.merge(mae_act, on="cut")
cov1 = (act.err <= act.band_mae).mean(); cov2 = (act.err <= 2 * act.band_mae).mean()
g = g.join(mae_act); g["band_mae"] = g.band_mae.fillna(0)
rel = (act.err / act.snpp)[act.snpp >= 10].median()
print(f"cobertura de ±MAE en meses activos: {cov1:.0%}; ±2·MAE: {cov2:.0%}; error relativo mediano (≥10 celdas-día): {rel:.0%}")

# 3) Prueba final: DESCRIPTIVA para M1 (ver docstring)
p = fit(tr_all)
x = predict(d[d.season.isin(TEST)], p, kappa_best)
final = score(x, ["M0", "M1", "M2", "A_k"]); final.to_csv(OUT / "eval_final.csv", index=False)
reg = x.groupby(["season", "m"])[["snpp", "M0", "M1", "M2", "A_k"]].sum()
print("prueba 2020–2021 (descriptiva), MAE regional mensual:", {c: round((reg[c] - reg.snpp).abs().mean(), 1) for c in ["M0", "M1", "M2", "A_k"]})
g.round(3).to_csv(OUT / "gates.csv")

# diagnósticos para el método
r_season = d[d.season.isin(TRAIN)].groupby("season").agg(a=("aqua", "sum"), v=("snpp", "sum")); r_season = (r_season.v / r_season.a)
r_drift = d[d.season >= 2020].groupby("season").agg(a=("aqua", "sum"), v=("snpp", "sum")); r_drift = (r_drift.v / r_drift.a)
print("r por temporada 2012–2019:", r_season.round(2).to_dict(), f"CV {r_season.std()/r_season.mean():.1%}")
print("r 2020→ (diagnóstico):", r_drift.round(2).to_dict())
print("\nComunas habilitadas:", int(g.enabled.sum()), "de", len(g), "→", sorted(g.index[g.enabled]))
print(g.sort_values("snpp_train", ascending=False).round(2).to_string())
json.dump(dict(r_const=p["r_const"], kappa_best_A=kappa_best, train=TRAIN, test=TEST, min_aqua=MIN_AQUA, min_wins=MIN_WINS,
               loso_total_mae={k: float(v) for k, v in ctrl.items()}, loso_total_mae_A={str(k): float(v) for k, v in tot.items()},
               band_coverage_1mae=float(cov1), band_coverage_2mae=float(cov2), rel_err_median_active=float(rel),
               r_by_season_train={int(k): float(v) for k, v in r_season.items()}, r_by_season_after={int(k): float(v) for k, v in r_drift.items()},
               excluded=["2020-08", "2020-09"], frozen_at="2026-11-14T14:20-03:00", gates_revised_at="2026-11-14T16:40-03:00"),
          open(OUT / "params.json", "w"), indent=1)
