"""Experimento de armonización Aqua → VIIRS (S-NPP diurno), por comuna y mes. Manifiesto v2 §5.

Particiones congeladas (14-11-2026 14:20), temporadas jul–jun nombradas por el año de inicio:
  entrenamiento + selección interna (LOSO): 2012–2019 (8 temporadas)
  prueba final (se mira una sola vez): 2020–2021
  2022→ : deriva orbital de Aqua; solo diagnóstico, no se usa.
  Excluidos en ambos sensores: 2020-08 y 2020-09 (falla de Aqua 16-08 a 02-09-2020).
Métodos: M0 Aqua sin corregir · M1 factor regional constante · M2 climatología VIIRS (sin Aqua)
         A(κ) factor por grupo de meses con encogimiento regional: r = (V + κ r_R)/(A + κ)
Grupos de meses: sep..may individuales, jun–ago juntos.
Salida: data/processed/eval_loso.csv, eval_final.csv, gates.csv, params.json
"""
import json, pathlib, itertools, duckdb, pandas as pd, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[1]; OUT = ROOT / "data/processed"
TRAIN = list(range(2012, 2020)); TEST = [2020, 2021]; KAPPAS = [0, 10, 30, 50, 100, 300, 1e9]
con = duckdb.connect(str(OUT / "goliat.duckdb"), read_only=True)
cuts = [r[0] for r in con.execute("select distinct cut from cells_comuna order by 1").fetchall()]
m = con.execute("""select cut, season, m, sum(case when sat='Aqua' then celldays end) aqua, sum(case when sat='SNPP' then celldays end) snpp
                   from monthly_masked where season between 2012 and 2021 group by all""").df()
grid = pd.MultiIndex.from_product([cuts, TRAIN + TEST, range(1, 13)], names=["cut", "season", "m"]).to_frame(index=False)
d = grid.merge(m, how="left").fillna({"aqua": 0, "snpp": 0})
d = d[~((d.season == 2020) & d.m.isin([8, 9]))]           # falla de Aqua
d = d[~((d.season == 2012) & d.m.isin([7, 8, 9, 10, 11, 12]))]  # S-NPP parte 2012-01-20 pero la temporada 2012 empieza en jul-2012: completa. (se deja)
d["g"] = d.m.map(lambda x: "JJA" if x in (6, 7, 8) else str(x))

def fit(tr):
    """Devuelve los parámetros aprendidos con las filas de entrenamiento tr."""
    r_const = tr.snpp.sum() / tr.aqua.sum()
    clim = tr.groupby(["cut", "m"]).snpp.mean().rename("clim")
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
            rows.append(dict(cut=cut, method=c, mae=e.abs().mean(), bias=e.mean(), n=len(grp), snpp_mean=grp.snpp.mean(), aqua_sum=grp.aqua.sum()))
    return pd.DataFrame(rows)

# 1) LOSO en entrenamiento para elegir κ
loso = []
for s in TRAIN:
    tr, te = d[d.season.isin([t for t in TRAIN if t != s])], d[d.season == s]
    p = fit(tr)
    for k in KAPPAS:
        x = predict(te, p, k); sc = score(x, ["M0", "M1", "M2", "A_k"]); sc["kappa"] = k; sc["held_out"] = s; loso.append(sc)
loso = pd.concat(loso)
tot = loso[loso.method == "A_k"].groupby("kappa").mae.sum()
ctrl = loso[(loso.kappa == KAPPAS[0])].groupby("method").mae.sum()
print("MAE total LOSO (suma sobre comunas y temporadas):")
print("  controles:", {k: round(v, 1) for k, v in ctrl.items() if k != "A_k"})
print("  A(κ):", {k: round(v, 1) for k, v in tot.items()})
kappa_sel = float(tot.idxmin()); print("κ elegido:", kappa_sel)
loso.to_csv(OUT / "eval_loso.csv", index=False)

# estabilidad: en cuántas temporadas LOSO A gana a M1 y a M2, por comuna
a = loso[(loso.kappa == kappa_sel) & (loso.method == "A_k")].set_index(["cut", "held_out"]).mae
m1 = loso[(loso.kappa == KAPPAS[0]) & (loso.method == "M1")].set_index(["cut", "held_out"]).mae
m2 = loso[(loso.kappa == KAPPAS[0]) & (loso.method == "M2")].set_index(["cut", "held_out"]).mae
stab = pd.DataFrame({"wins_vs_M1": (a < m1).groupby("cut").sum(), "wins_vs_M2": (a < m2).groupby("cut").sum()})

# 2) Prueba final: una sola configuración, se mira una vez
p = fit(d[d.season.isin(TRAIN)])
x = predict(d[d.season.isin(TEST)], p, kappa_sel)
final = score(x, ["M0", "M1", "M2", "A_k"]); final.to_csv(OUT / "eval_final.csv", index=False)
f = final.pivot(index="cut", columns="method", values=["mae", "bias"])
g = pd.DataFrame(index=cuts)
g["aqua_train"] = d[d.season.isin(TRAIN)].groupby("cut").aqua.sum()
g["snpp_train"] = d[d.season.isin(TRAIN)].groupby("cut").snpp.sum()
g["mae_M1"], g["mae_M2"], g["mae_A"] = f["mae"]["M1"], f["mae"]["M2"], f["mae"]["A_k"]
g["bias_M1"], g["bias_A"] = f["bias"]["M1"], f["bias"]["A_k"]
g = g.join(stab)
g["gate_vs_const"] = (g.mae_A < g.mae_M1) & (g.bias_A.abs() <= g.bias_M1.abs() * 1.1 + 0.05)
g["gate_vs_clim"] = g.mae_A < g.mae_M2
g["gate_stable"] = (g.wins_vs_M1 >= 5) & (g.wins_vs_M2 >= 5)
g["enabled"] = g.gate_vs_const & g.gate_vs_clim & g.gate_stable
g.round(3).to_csv(OUT / "gates.csv")
reg = x.groupby(["season", "m"])[["snpp", "M0", "M1", "M2", "A_k"]].sum()
print("\nPrueba final 2020–2021, suma regional por método: MAE mensual")
print({c: round((reg[c] - reg.snpp).abs().mean(), 1) for c in ["M0", "M1", "M2", "A_k"]})
print("\nComunas habilitadas:", int(g.enabled.sum()), "de", len(g))
print(g.sort_values("snpp_train", ascending=False).head(15).round(2).to_string())
json.dump(dict(kappa=kappa_sel, train=TRAIN, test=TEST, r_const=p["r_const"], rR=p["reg"].rR.to_dict(),
               excluded=["2020-08", "2020-09"], frozen_at="2026-11-14T14:20-03:00"), open(OUT / "params.json", "w"), indent=1)

# 3) Lectura de parsimonia: en LOSO, A(κ*) y M1 empatan (diferencia < 0,2 %). Se evalúa M1 (factor constante) como
#    método publicable, con las mismas compuertas contra la climatología y la misma regla de estabilidad.
#    DIVULGACIÓN: esta evaluación se decidió DESPUÉS de mirar el bloque final con A(κ*). Las métricas de M1 en 2020–2021
#    ya no son una prueba independiente estricta; la elección de M1 se apoya en el LOSO (solo entrenamiento).
m1w = pd.DataFrame({"wins_vs_M2_M1": (m1 < m2).groupby("cut").sum()})
g = g.join(m1w)
g["M1_gate_vs_clim"] = g.mae_M1 < g.mae_M2
g["M1_gate_stable"] = g.wins_vs_M2_M1 >= 6
g["M1_enabled"] = g.M1_gate_vs_clim & g.M1_gate_stable
g.round(3).to_csv(OUT / "gates.csv")
print("\nM1 (factor constante r =", round(p["r_const"], 3), ") habilitado en", int(g.M1_enabled.sum()), "de", len(g), "comunas")
print("  habilitadas:", sorted(g.index[g.M1_enabled].tolist()))
print("  no habilitadas:", sorted(g.index[~g.M1_enabled].tolist()))
print("  LOSO M1 vs M2 por temporada (suma comunas):", {s: (round(v1, 1), round(v2, 1)) for s, v1, v2 in
      zip(TRAIN, m1.groupby("held_out").sum().values, m2.groupby("held_out").sum().values)})
