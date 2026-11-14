"""Tabla canónica de detecciones diurnas del piloto (Biobío + Ñuble).

Entrada: data/raw/firms_country/** y data/raw/firms_api/** (inventariados en inventory.csv).
Reglas congeladas (manifiesto v2 §4–5):
  - Solo daynight = 'D'. acq_date tal como viene (UTC); la pasada diurna ~18 UTC cae en el mismo día local.
  - MODIS: confidence >= 30. VIIRS: confidence != 'l'.
  - Fuente por período: archivo país (SP) hasta 2025-12-31 para MODIS y S-NPP; API SP para NOAA-20/21 y 2026;
    NRT solo donde no hay SP (provisional). Se deduplica por (satélite, lat, lon, fecha, hora).
  - Grilla 0,01°: cell_x = floor(lon/0.01), cell_y = floor(lat/0.01). Centroide de celda → comuna (asignación única).
Salida: data/processed/detections.parquet y cells_comuna.parquet.
"""
import json, pathlib, duckdb
from shapely.geometry import shape, Point
from shapely.strtree import STRtree

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data/raw", ROOT / "data/processed"
BBOX = (-74.0, -38.6, -70.9, -35.9)  # oeste, sur, este, norte (con margen sobre las comunas)

con = duckdb.connect(str(OUT / "goliat.duckdb"))
con.execute("install spatial; load spatial;") if False else None

def read(glob, source_kind):
    return f"""
    select latitude::double lat, longitude::double lon, acq_date::date acq_date, lpad(acq_time::varchar, 4, '0') acq_time,
           satellite, instrument, confidence::varchar confidence, frp::double frp, daynight,
           try_cast(type as integer) type, version::varchar version, '{source_kind}' source_kind, filename
    from read_csv('{glob}', header=true, union_by_name=true, filename=true, all_varchar=true)
    where daynight = 'D' and longitude::double between {BBOX[0]} and {BBOX[2]} and latitude::double between {BBOX[1]} and {BBOX[3]}
    """

parts = [
    read(RAW / "firms_country/modis/*.csv", "country_sp"),
    read(RAW / "firms_country/viirs-snpp/*.csv", "country_sp"),
    read(RAW / "firms_api/MODIS_SP/*.csv", "api_sp"),
    read(RAW / "firms_api/VIIRS_SNPP_SP/*.csv", "api_sp"),
    read(RAW / "firms_api/VIIRS_NOAA20_SP/*.csv", "api_sp"),
    read(RAW / "firms_api/VIIRS_NOAA21_SP/*.csv", "api_sp"),
    read(RAW / "firms_api/MODIS_NRT/*.csv", "nrt"),
    read(RAW / "firms_api/VIIRS_SNPP_NRT/*.csv", "nrt"),
    read(RAW / "firms_api/VIIRS_NOAA20_NRT/*.csv", "nrt"),
    read(RAW / "firms_api/VIIRS_NOAA21_NRT/*.csv", "nrt"),
]
con.execute("create or replace table raw_all as " + " union all ".join(parts))
print("filas crudas en bbox:", con.execute("select count(*) from raw_all").fetchone()[0])

# Satélite normalizado y filtros de confianza
con.execute("""
create or replace table det as
with x as (
  select *,
    case satellite when 'Terra' then 'Terra' when 'Aqua' then 'Aqua' when 'N' then 'SNPP' when 'N20' then 'NOAA20' when 'N21' then 'NOAA21' else satellite end sat,
    case when instrument = 'MODIS' then try_cast(confidence as integer) >= 30 else confidence <> 'l' end conf_ok,
    -- prioridad de fuente: SP de archivo país > SP de API > NRT
    case source_kind when 'country_sp' then 1 when 'api_sp' then 2 else 3 end prio
  from raw_all
),
ranked as (
  select *, row_number() over (partition by sat, round(lat, 4), round(lon, 4), acq_date, acq_time order by prio) rn from x
)
select lat, lon, acq_date, acq_time, sat, instrument, confidence, frp, type, version, source_kind,
       floor(lon / 0.01)::integer cell_x, floor(lat / 0.01)::integer cell_y
from ranked where rn = 1 and conf_ok
""")
print("detecciones diurnas, confiables, deduplicadas:", con.execute("select count(*) from det").fetchone()[0])
print(con.execute("select sat, source_kind, min(acq_date), max(acq_date), count(*) from det group by 1,2 order by 1,2").fetchall())

# Celda → comuna por centroide (asignación única)
fc = json.load(open(OUT / "comunas_biobio_nuble.geojson"))
geoms = [shape(f["geometry"]) for f in fc["features"]]
cuts = [f["properties"]["cut"] for f in fc["features"]]
tree = STRtree(geoms)
cells = con.execute("select distinct cell_x, cell_y from det").fetchall()
rows = []
for cx, cy in cells:
    p = Point((cx + 0.5) * 0.01, (cy + 0.5) * 0.01)
    for i in tree.query(p, predicate="within"):
        rows.append((cx, cy, cuts[i])); break
con.execute("create or replace table cells_comuna (cell_x integer, cell_y integer, cut varchar)")
con.executemany("insert into cells_comuna values (?, ?, ?)", rows)
print("celdas con detección:", len(cells), "→ dentro de una comuna:", len(rows))

con.execute(f"copy det to '{OUT}/detections.parquet' (format parquet)")
con.execute(f"copy cells_comuna to '{OUT}/cells_comuna.parquet' (format parquet)")
print("listo")
