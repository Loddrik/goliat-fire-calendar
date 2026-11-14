"""Genera los datos que consume la web: web/public/data/index.json y comunas/<cut>.json.

Serie publicada por comuna (celdas-día diurnas, escala VIIRS):
  - observado: S-NPP temporadas 2012–2017; NOAA-20 temporadas 2018→ (puente evaluado, factor 1,0 declarado).
  - estimado: Aqua × r_const (params.json) para 2002-07 → 2012-06, solo si gates.csv M1_enabled; con banda ± MAE LOSO de la comuna.
  - no habilitado: null con estado explícito.
  - provisional: meses con datos NRT.
Recurrencia: celdas 0,01° de la comuna con el número de temporadas (2012→) con detección diurna VIIRS (S-NPP o NOAA-20), tras la máscara.
"""
import json, pathlib, duckdb, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]; OUT = ROOT / "data/processed"; WEB = ROOT / "web/public/data"
(WEB / "comunas").mkdir(parents=True, exist_ok=True)
params = json.load(open(OUT / "params.json")); r = params["r_const"]
gates = pd.read_csv(OUT / "gates.csv", index_col=0, dtype={0: str}); gates.index = gates.index.astype(str).str.zfill(5)
loso = pd.read_csv(OUT / "eval_loso.csv", dtype={"cut": str}); loso["cut"] = loso.cut.str.zfill(5)
mae_m1 = loso[(loso.method == "M1")].groupby("cut").mae.mean()
con = duckdb.connect(str(OUT / "goliat.duckdb"), read_only=True)
comunas = pd.read_csv(ROOT / "data/raw/dpa/comunas_cut.csv", dtype={"cut": str})
cutoff = con.execute("select max(acq_date) from det").fetchone()[0]
cur_season = cutoff.year if cutoff.month >= 7 else cutoff.year - 1
mm = con.execute("select sat, cut, season, y, m, celldays, has_nrt from monthly_masked").df()

def series(cut):
    x = mm[mm.cut == cut]
    rows = []
    for season in range(2002, cur_season + 1):
        for m in list(range(7, 13)) + list(range(1, 7)):
            y = season if m >= 7 else season + 1
            if (y, m) > (cutoff.year, cutoff.month): break
            if season <= 2011 or (season == 2012 and m < 7):  # era MODIS (hasta jun-2012)
                a = x[(x.sat == "Aqua") & (x.y == y) & (x.m == m)]
                if gates.loc[cut, "M1_enabled"]:
                    v = float(a.celldays.sum()) * r
                    rows.append(dict(season=season, y=y, m=m, value=round(v, 1), state="estimated", band=round(float(mae_m1.get(cut, 0)), 1), aqua=int(a.celldays.sum())))
                else:
                    rows.append(dict(season=season, y=y, m=m, value=None, state="not_enabled", aqua=int(a.celldays.sum())))
            else:
                sat = "SNPP" if season <= 2017 else "NOAA20"
                o = x[(x.sat == sat) & (x.y == y) & (x.m == m)]
                rows.append(dict(season=season, y=y, m=m, value=int(o.celldays.sum()), state="observed", sat=sat,
                                 provisional=bool(o.has_nrt.any()) if len(o) else False))
    return rows

def season_compare(rows):
    """Acumulado de la temporada en curso hasta el mes de corte, contra las temporadas observadas en los mismos meses."""
    months_done = [(x["m"]) for x in rows if x["season"] == cur_season]
    def acc(s, states): return sum((x["value"] or 0) for x in rows if x["season"] == s and x["m"] in months_done and x["state"] in states)
    cur = acc(cur_season, {"observed"})
    obs = {s: acc(s, {"observed"}) for s in range(2012, cur_season)}
    vals = sorted(obs.values())
    q = lambda p: vals[min(len(vals) - 1, int(p * len(vals)))] if vals else None
    return dict(season=cur_season, months=months_done, current=cur, observed_seasons=obs, median=q(0.5), p25=q(0.25), p75=q(0.75), p90=q(0.9))

rec = con.execute("""
select c.cut, c.cell_x, c.cell_y, count(distinct season) n_seasons, count(*) n_days, min(season) first_season, max(season) last_season
from celldays c where sat in ('SNPP','NOAA20') and season >= 2012
  and not exists (select 1 from static_mask s where s.cell_x=c.cell_x and s.cell_y=c.cell_y)
group by 1,2,3""").df()

index = []
for _, cm in comunas.iterrows():
    cut = cm.cut; rows = series(cut); g = gates.loc[cut]
    rc = rec[rec.cut == cut]
    doc = dict(cut=cut, comuna=cm.comuna, region=cm.region, cutoff=str(cutoff), r_const=round(r, 3),
               reconstruction_enabled=bool(g.M1_enabled),
               gates=dict(mae_const=round(float(g.mae_M1), 2), mae_clim=round(float(g.mae_M2), 2), wins_vs_clim=int(g.wins_vs_M2_M1), of=8,
                          aqua_train=int(g.aqua_train), snpp_train=int(g.snpp_train)),
               series=rows, season_compare=season_compare(rows),
               recurrence=[dict(x=int(a.cell_x), y=int(a.cell_y), n=int(a.n_seasons), d=int(a.n_days), f=int(a.first_season), l=int(a.last_season)) for a in rc.itertuples()])
    json.dump(doc, open(WEB / "comunas" / f"{cut}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    obs_total = sum((x["value"] or 0) for x in rows if x["state"] == "observed" and 2012 <= x["season"] <= 2025)
    index.append(dict(cut=cut, comuna=cm.comuna, region=cm.region, enabled=bool(g.M1_enabled), observed_2012_2025=obs_total,
                      current=doc["season_compare"]["current"], median=doc["season_compare"]["median"]))
json.dump(dict(generated=pd.Timestamp.now(tz="America/Santiago").isoformat(), cutoff=str(cutoff), current_season=cur_season,
               r_const=round(r, 3), params=params, comunas=index), open(WEB / "index.json", "w"), ensure_ascii=False, indent=0)
print("corte:", cutoff, "temporada en curso:", cur_season, "| comunas:", len(index), "| habilitadas:", sum(i["enabled"] for i in index))
print("ejemplo Penco:", {k: v for k, v in json.load(open(WEB / "comunas/08107.json"))["season_compare"].items() if k != "observed_seasons"})
import os; print("tamaño total KB:", round(sum(os.path.getsize(p) for p in (WEB / "comunas").glob("*.json")) / 1e3))

# Detecciones filtradas usadas (por comuna), para la exportación cruda
DET = OUT / "detections_csv"; DET.mkdir(exist_ok=True)
con.execute(f"""
copy (
  select c.cut, d.acq_date, d.acq_time, d.lat, d.lon, d.sat, d.instrument, d.confidence, d.frp, d.source_kind,
         d.cell_x, d.cell_y,
         exists(select 1 from static_mask s where s.cell_x=d.cell_x and s.cell_y=d.cell_y) masked_static
  from det d join cells_comuna c using (cell_x, cell_y) order by c.cut, d.acq_date, d.acq_time
) to '{DET}' (format csv, partition_by (cut), overwrite_or_ignore, header)
""")
import glob, shutil
for p in glob.glob(str(DET / "cut=*/*.csv")):
    cut = p.split("cut=")[1].split("/")[0]; shutil.move(p, DET / f"{cut}.csv"); shutil.rmtree(DET / f"cut={cut}", ignore_errors=True)
print("CSV de detecciones por comuna:", len(list(DET.glob("*.csv"))), "archivos,", round(sum(os.path.getsize(p) for p in DET.glob("*.csv")) / 1e6, 1), "MB")
