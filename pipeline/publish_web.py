"""Capa de publicación de la web (lado producto).

Lee SOLO lo que ya produce el pipeline científico y está versionado:
  - data/processed/celldays.parquet   (celda × día × satélite × comuna, ya filtrado a diurno/confianza)
  - data/processed/static_mask.parquet (celdas descartadas)
  - web/public/data/comunas/<cut>.json y index.json (series publicadas por publish.py)
y las reordena en los archivos que la web necesita y que publish.py no entrega.
No calcula ningún número nuevo del método: solo rebana, cuenta días y resume la serie publicada.

Escribe web/public/data/derived/<cut>.json y web/public/data/derived/region.json.
Antes de escribir, comprueba que las celdas y sus conteos coinciden con `recurrence` de publish.py.

Uso: uv run python pipeline/publish_web.py
"""
import json, pathlib, statistics, sys
import duckdb

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROC = ROOT / "data/processed"; WEB = ROOT / "web/public/data"; OUT = WEB / "derived"
OUT.mkdir(parents=True, exist_ok=True)

# Misma regla de plataforma y mismos filtros que publish.py (una plataforma por temporada, desde 2012, sin estáticas).
PLATFORM_RULE = "case when season <= 2017 then 'SNPP' else 'NOAA20' end"
index = json.load(open(WEB / "index.json"))
cutoff = index["cutoff"]; cur_season = index["current_season"]
SEASONS = list(range(2012, cur_season + 1))
MONTHS = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]

con = duckdb.connect()
cells = con.execute(f"""
with c as (
  select cut, cell_x, cell_y, season, m, acq_date from read_parquet('{PROC / "celldays.parquet"}') c
  where sat = {PLATFORM_RULE} and season >= 2012
    and not exists (select 1 from read_parquet('{PROC / "static_mask.parquet"}') s where s.cell_x = c.cell_x and s.cell_y = c.cell_y))
select cut, cell_x, cell_y, season, m, count(*) as n_days from c group by all order by cut, cell_x, cell_y, season, m""").df()

def quantile(vals, p):
    v = sorted(vals); return v[min(len(v) - 1, int(p * len(v)))] if v else None

region = []; problems = 0
for cm in index["comunas"]:
    cut = cm["cut"]
    doc = json.load(open(WEB / "comunas" / f"{cut}.json"))
    # --- celdas por temporada y por mes (para el mapa con control de tiempo)
    g = cells[cells.cut == cut]
    out_cells = {}
    for r in g.itertuples():
        k = (int(r.cell_x), int(r.cell_y))
        e = out_cells.setdefault(k, {"x": k[0], "y": k[1], "s": [0] * len(SEASONS), "m": [0] * 12})
        e["s"][SEASONS.index(int(r.season))] += int(r.n_days); e["m"][int(r.m) - 1] += int(r.n_days)
    for e in out_cells.values():
        e["n"] = sum(1 for v in e["s"] if v); e["d"] = sum(e["s"])
    # comprobación contra la recurrencia que publica publish.py (mismo contrato, mismos números)
    ref = {(c["x"], c["y"]): (c["n"], c["d"]) for c in doc["recurrence"]}
    mine = {k: (e["n"], e["d"]) for k, e in out_cells.items()}
    if ref != mine:
        problems += 1
        diff = [(k, ref.get(k), mine.get(k)) for k in set(ref) | set(mine) if ref.get(k) != mine.get(k)]
        print(f"[{cut} {cm['comuna']}] recurrencia no coincide con publish.py en {len(diff)} celdas, p. ej. {diff[:3]}", file=sys.stderr)
    # --- totales por temporada y climatología mensual, desde la serie publicada (números de publish.py)
    by_season = {}
    for s in doc["series"]:
        by_season.setdefault(s["season"], []).append(s)
    season_totals = []
    for season, rows in sorted(by_season.items()):
        vals = [r["value"] for r in rows if r["value"] is not None]
        states = {r["state"] for r in rows}
        state = "not_enabled" if states == {"not_enabled"} else ("estimated" if "estimated" in states else "observed")
        season_totals.append(dict(season=season, value=(round(sum(vals), 1) if state != "not_enabled" else None), state=state,
                                  n_months=len(vals), complete=(len(vals) == 12 and not any(r.get("partial") for r in rows)),
                                  provisional=any(r.get("provisional") for r in rows)))
    clim = []
    for m in MONTHS:
        vals = [r["value"] for r in doc["series"] if r["m"] == m and r["state"] == "observed" and r["value"] is not None
                and 2012 <= r["season"] < cur_season and not r.get("partial")]
        clim.append(dict(m=m, n=len(vals), median=quantile(vals, 0.5), p25=quantile(vals, 0.25), p75=quantile(vals, 0.75),
                         max=(max(vals) if vals else None)))
    out = dict(cut=cut, comuna=cm["comuna"], region=cm["region"], cutoff=cutoff, current_season=cur_season,
               generated_from=["data/processed/celldays.parquet", "data/processed/static_mask.parquet", f"web/public/data/comunas/{cut}.json"],
               platform_rule="S-NPP hasta 2017, NOAA-20 desde 2018; diurno; sin celdas estáticas (igual que publish.py)",
               seasons=SEASONS, season_totals=season_totals, month_climatology=clim,
               cells_note="s = días con detección por temporada (índices = seasons); m = días por mes del año (índice 0 = enero); n = temporadas con detección; d = días",
               cells=sorted(out_cells.values(), key=lambda e: (e["x"], e["y"])))
    json.dump(out, open(OUT / f"{cut}.json", "w"), ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    region.extend(dict(cut=cut, x=e["x"], y=e["y"], n=e["n"], d=e["d"], s=e["s"]) for e in out_cells.values())

json.dump(dict(cutoff=cutoff, current_season=cur_season, seasons=SEASONS, cell_size_deg=0.01,
               note="Todas las celdas de las 54 comunas con días de detección por temporada (observado VIIRS, misma regla que publish.py). Para el mapa regional.",
               cells=region), open(OUT / "region.json", "w"), ensure_ascii=False, separators=(",", ":"), allow_nan=False)
print(f"derived/: {len(index['comunas'])} comunas, {len(region)} celdas en region.json, corte {cutoff}; comunas con diferencias vs publish.py: {problems}")
if problems: sys.exit(1)
