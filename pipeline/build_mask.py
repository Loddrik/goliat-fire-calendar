"""Máscara de fuentes estáticas (industrias, volcanes), propia y fija para toda la serie.

Regla congelada (v1, 14-11-2026 14:10), calculada sobre detecciones diurnas 2002-07 → 2020-06 (período de entrenamiento;
no usa las temporadas reservadas) de todas las plataformas:
  A. Persistencia industrial: celda con ≥ 30 días distintos de detección y ≥ 8 temporadas distintas.
  B. Volcán: celda con ≥ 10 días y ≥ 50 % de sus detecciones tipificadas (MODIS/VIIRS SP) con type = 1.
  C. Estática declarada por FIRMS: celda con ≥ 15 días y ≥ 60 % de sus detecciones tipificadas con type = 2.
  Buffer: las 8 celdas vecinas de cualquier celda A o B con ≥ 100 días (el desfase geométrico entre sensores es de 1–3 celdas).
`type` solo sirve como evidencia para construir la máscara; la máscara se aplica igual a SP y NRT (que no trae `type`).
Salida: data/processed/static_mask.parquet, tabla monthly_masked, y el efecto por plataforma."""
import pathlib, duckdb
ROOT = pathlib.Path(__file__).resolve().parents[1]; OUT = ROOT / "data/processed"
con = duckdb.connect(str(OUT / "goliat.duckdb"))
con.execute("""
create or replace table cell_stats as
select cell_x, cell_y, count(distinct acq_date) n_days,
  count(distinct case when month(acq_date)>=7 then year(acq_date) else year(acq_date)-1 end) n_seasons,
  avg(case when type is not null then (type=1)::int end) share_type1,
  avg(case when type is not null then (type=2)::int end) share_type2
from det where acq_date < date '2020-07-01' group by 1,2
""")
con.execute("""
create or replace table static_core as
select cell_x, cell_y, n_days,
  case when n_days>=30 and n_seasons>=8 then 'A_persistente'
       when n_days>=10 and share_type1>=0.5 then 'B_volcan'
       when n_days>=15 and share_type2>=0.6 then 'C_type2' end rule
from cell_stats where rule is not null
""")
con.execute("""
create or replace table static_mask as
select cell_x, cell_y, rule from static_core
union
select s.cell_x+dx, s.cell_y+dy, 'buffer' from static_core s, (values (-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)) v(dx,dy)
where s.n_days>=100 and s.rule in ('A_persistente','B_volcan')
  and not exists (select 1 from static_core c where c.cell_x=s.cell_x+dx and c.cell_y=s.cell_y+dy)
""")
print("celdas enmascaradas por regla:", con.execute("select rule, count(*) from static_mask group by 1 order by 1").fetchall())
con.execute("""
create or replace table monthly_masked as
select sat, cut, season, y, m, count(*) celldays, sum(n_det) detections, max(any_nrt) has_nrt
from celldays c where not exists (select 1 from static_mask s where s.cell_x=c.cell_x and s.cell_y=c.cell_y)
group by all
""")
print("efecto de la máscara por plataforma (celdas-día quitadas, 2013–2020):")
print(con.execute("""
select a.sat, a.t total, a.t - coalesce(b.t,0) quitadas, round(100.0*(a.t - coalesce(b.t,0))/a.t,1) pct
from (select sat, sum(celldays) t from monthly where season between 2013 and 2019 group by 1) a
left join (select sat, sum(celldays) t from monthly_masked where season between 2013 and 2019 group by 1) b using(sat) order by 1""").fetchall())
print("comunas donde la máscara quita más del 20 % (S-NPP 2013–2019):")
print(con.execute("""
select a.cut, a.t, round(100.0*(a.t-coalesce(b.t,0))/a.t,1) pct from
(select cut, sum(celldays) t from monthly where sat='SNPP' and season between 2013 and 2019 group by 1) a
left join (select cut, sum(celldays) t from monthly_masked where sat='SNPP' and season between 2013 and 2019 group by 1) b using(cut)
where 100.0*(a.t-coalesce(b.t,0))/a.t > 20 order by 3 desc""").fetchall())
con.execute(f"copy static_mask to '{OUT}/static_mask.parquet' (format parquet)")
con.execute(f"copy monthly_masked to '{OUT}/celldays_comuna_month_masked.parquet' (format parquet)")
