"""Celdas-día por comuna, satélite y mes. Unidad congelada: celda 0,01° con ≥1 detección diurna en un día.
Temporada: jul–jun, nombrada por el año en que empieza (2022 = jul-2022..jun-2023).
Salida: data/processed/celldays_comuna_month.parquet (sin máscara de estáticas todavía: se aplica en el paso siguiente)."""
import pathlib, duckdb
ROOT = pathlib.Path(__file__).resolve().parents[1]; OUT = ROOT / "data/processed"
con = duckdb.connect(str(OUT / "goliat.duckdb"))
con.execute(f"""
create or replace table celldays as
select d.sat, c.cut, d.cell_x, d.cell_y, d.acq_date,
       year(d.acq_date) y, month(d.acq_date) m,
       case when month(d.acq_date) >= 7 then year(d.acq_date) else year(d.acq_date) - 1 end season,
       count(*) n_det, max(d.source_kind = 'nrt') any_nrt
from det d join cells_comuna c using (cell_x, cell_y)
group by all
""")
con.execute("""
create or replace table monthly as
select sat, cut, season, y, m, count(*) celldays, sum(n_det) detections, max(any_nrt) has_nrt
from celldays group by all order by cut, sat, y, m
""")
con.execute(f"copy celldays to '{OUT}/celldays.parquet' (format parquet)")
con.execute(f"copy monthly to '{OUT}/celldays_comuna_month.parquet' (format parquet)")
print(con.execute("select sat, count(*) celldays from celldays group by 1 order by 1").fetchall())
print("top comunas por celdas-día VIIRS S-NPP 2013–2024:")
print(con.execute("""select cut, sum(celldays) from monthly where sat='SNPP' and season between 2013 and 2024 group by 1 order by 2 desc limit 8""").fetchall())
print("Aqua vs SNPP por temporada (todo el piloto):")
print(con.execute("""select season, sum(celldays) filter (sat='Aqua') aqua, sum(celldays) filter (sat='SNPP') snpp, sum(celldays) filter (sat='NOAA20') n20
from monthly where season between 2012 and 2025 group by 1 order by 1""").fetchall())
