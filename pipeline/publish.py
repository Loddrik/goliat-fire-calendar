"""Genera los datos que consume la web: web/public/data/index.json, comunas/<cut>.json y CSV de detecciones por comuna.

Serie publicada por comuna (celdas-día diurnas, escala VIIRS):
  - observed: S-NPP temporadas 2012–2017; NOAA-20 temporadas 2018→ (puente 0,93–1,06 anual, factor 1,0 declarado).
  - estimated: Aqua × r_const (params.json) para 2002-07 → 2012-06, solo si gates.csv enabled; con error típico ± MAE LOSO
    de la comuna en meses activos (cobertura empírica ~50 %; ±2·MAE ~85 %). No es una banda de confianza.
  - not_enabled: null con estado explícito.
  - provisional: meses con datos NRT.
Comparación de temporada: acumulado de la temporada en curso hasta el día de corte, contra cada temporada observada
truncada AL MISMO DÍA DEL MES (misma plataforma que la serie).
Recurrencia: celdas 0,01° con detección diurna por temporada, misma regla de plataforma que la serie (S-NPP ≤ 2017, NOAA-20 ≥ 2018).
"""
import json, os, glob, shutil, pathlib, duckdb, pandas as pd
from publication_contract import finite_json, season_window_predicate
ROOT = pathlib.Path(__file__).resolve().parents[1]; OUT = ROOT / "data/processed"; WEB = ROOT / "web/public/data"
(WEB / "comunas").mkdir(parents=True, exist_ok=True)
params = json.load(open(OUT / "params.json")); r = params["r_const"]
gates = pd.read_csv(OUT / "gates.csv", index_col=0, dtype={0: str}); gates.index = gates.index.astype(str).str.zfill(5)
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
communes_csv = ROOT / "data/raw/dpa/comunas_cut.csv"
if communes_csv.exists():
    comunas = pd.read_csv(communes_csv, dtype={"cut": str})
else:
    # A fresh clone has versioned geometries/CUT, but no ignored raw downloads.
    fc = json.load(open(OUT / "comunas_biobio_nuble.geojson"))
    comunas = pd.DataFrame([f["properties"] for f in fc["features"]])[["cut", "comuna", "region"]]
if len(comunas) != 54 or comunas.cut.nunique() != 54 or not comunas.cut.str.fullmatch(r"\d{5}").all():
    raise ValueError("Expected 54 unique official commune CUT codes")
cutoff = con.execute("select max(acq_date) from det").fetchone()[0]
cur_season = cutoff.year if cutoff.month >= 7 else cutoff.year - 1
PLATFORM_RULE = "case when season <= 2017 then 'SNPP' else 'NOAA20' end"
mm = con.execute("select sat, cut, season, y, m, celldays, has_nrt from monthly_masked").df()

def series(cut):
    x = mm[mm.cut == cut]; rows = []
    for season in range(2002, cur_season + 1):
        for m in list(range(7, 13)) + list(range(1, 7)):
            y = season if m >= 7 else season + 1
            if (y, m) > (cutoff.year, cutoff.month): break
            if season <= 2011:
                a = int(x[(x.sat == "Aqua") & (x.y == y) & (x.m == m)].celldays.sum())
                if gates.loc[cut, "enabled"]:
                    rows.append(dict(season=season, y=y, m=m, value=round(a * r, 1), state="estimated", band=round(float(gates.loc[cut, "band_mae"]), 1), aqua=a))
                else:
                    rows.append(dict(season=season, y=y, m=m, value=None, state="not_enabled", aqua=a))
            else:
                sat = "SNPP" if season <= 2017 else "NOAA20"
                o = x[(x.sat == sat) & (x.y == y) & (x.m == m)]
                rows.append(dict(season=season, y=y, m=m, value=int(o.celldays.sum()), state="observed", sat=sat,
                                 provisional=bool(o.has_nrt.any()) if len(o) else False, partial=(y, m) == (cutoff.year, cutoff.month)))
    return rows

# acumulado por temporada hasta el mismo día del mes de corte (día del año relativo al 1 de julio)
sc_all = con.execute(f"""
with c as (select cell_x, cell_y, acq_date, season, sat, cut from celldays
           where sat = {PLATFORM_RULE} and season >= 2012
             and not exists (select 1 from static_mask s where s.cell_x=celldays.cell_x and s.cell_y=celldays.cell_y))
select cut, season, count(*) acc from c
where {season_window_predicate(cutoff.month, cutoff.day)}
group by 1, 2""").df()

def season_compare(cut):
    x = sc_all[sc_all.cut == cut].set_index("season").acc
    cur = int(x.get(cur_season, 0))
    obs = {int(s): int(x.get(s, 0)) for s in range(2012, cur_season)}
    vals = sorted(obs.values()); q = lambda p: vals[min(len(vals) - 1, int(p * len(vals)))] if vals else None
    months = list(range(7, cutoff.month + 1)) if cutoff.month >= 7 else list(range(7, 13)) + list(range(1, cutoff.month + 1))
    return dict(season=cur_season, months=months, cutoff_day=cutoff.day, current=cur, observed_seasons=obs, n=len(vals),
                median=q(0.5), p25=q(0.25), p75=q(0.75), p90=q(0.9))

rec = con.execute(f"""
select c.cut, c.cell_x, c.cell_y, count(distinct season) n_seasons, count(*) n_days, min(season) first_season, max(season) last_season
from celldays c where sat = {PLATFORM_RULE} and season >= 2012
  and not exists (select 1 from static_mask s where s.cell_x=c.cell_x and s.cell_y=c.cell_y)
group by 1,2,3 order by 1,2,3""").df()

index = []
for _, cm in comunas.iterrows():
    cut = cm.cut; rows = series(cut); g = gates.loc[cut]; rc = rec[rec.cut == cut]; sc = season_compare(cut)
    doc = dict(cut=cut, comuna=cm.comuna, region=cm.region, cutoff=str(cutoff), r_const=round(r, 3),
               reconstruction_enabled=bool(g.enabled),
               gates=dict(aqua_train=int(g.aqua_train), snpp_train=int(g.snpp_train), min_aqua=params["min_aqua"],
                          loso_mae_raw=round(float(g.loso_mae_M0), 2), loso_mae_const=round(float(g.loso_mae_M1), 2), loso_mae_clim=round(float(g.loso_mae_M2), 2),
                          wins_vs_clim=int(g.wins_vs_M2), wins_vs_raw=int(g.wins_vs_M0), of=8, min_wins=params["min_wins"],
                          gate_aqua=bool(g.gate_aqua), gate_vs_clim=bool(g.gate_vs_clim), gate_vs_raw=bool(g.gate_vs_raw),
                          band_mae=round(float(g.band_mae), 1), band_coverage_1=params["band_coverage_1mae"], band_coverage_2=params["band_coverage_2mae"]),
               series=rows, season_compare=sc,
               recurrence=[dict(x=int(a.cell_x), y=int(a.cell_y), n=int(a.n_seasons), d=int(a.n_days), f=int(a.first_season), l=int(a.last_season)) for a in rc.itertuples()])
    json.dump(doc, open(WEB / "comunas" / f"{cut}.json", "w"), ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    index.append(dict(cut=cut, comuna=cm.comuna, region=cm.region, enabled=bool(g.enabled),
                      observed_2012_2025=sum((x["value"] or 0) for x in rows if x["state"] == "observed" and 2012 <= x["season"] <= 2025),
                      current=sc["current"], median=sc["median"]))
unavailable_metrics = []
params_for_web = finite_json(params, "params", unavailable_metrics)
json.dump(dict(generated=pd.Timestamp.now(tz="America/Santiago").isoformat(), cutoff=str(cutoff), current_season=cur_season,
               r_const=round(r, 3), params=params_for_web, unavailable_metrics=unavailable_metrics, comunas=index),
          open(WEB / "index.json", "w"), ensure_ascii=False, indent=0, allow_nan=False)
print("corte:", cutoff, "temporada:", cur_season, "| habilitadas:", sum(i["enabled"] for i in index), "de", len(index))
print("Penco:", {k: v for k, v in season_compare("08107").items() if k != "observed_seasons"})

# Detecciones filtradas usadas (por comuna)
DET = OUT / "detections_csv"; shutil.rmtree(DET, ignore_errors=True); DET.mkdir()
con.execute(f"""
copy (select c.cut, d.acq_date, d.acq_time, d.lat, d.lon, d.sat, d.instrument, d.confidence, d.frp, d.source_kind, d.cell_x, d.cell_y,
             exists(select 1 from static_mask s where s.cell_x=d.cell_x and s.cell_y=d.cell_y) masked_static
      from det d join cells_comuna c using (cell_x, cell_y) order by c.cut, d.acq_date, d.acq_time)
to '{DET}' (format csv, partition_by (cut), overwrite_or_ignore, header)""")
for p in glob.glob(str(DET / "cut=*/*.csv")):
    cut = p.split("cut=")[1].split("/")[0]; shutil.move(p, DET / f"{cut}.csv"); shutil.rmtree(DET / f"cut={cut}", ignore_errors=True)
print("CSV de detecciones:", len(list(DET.glob("*.csv"))), "archivos,", round(sum(os.path.getsize(p) for p in DET.glob("*.csv")) / 1e6, 1), "MB")
