# Ronda 3 · Posición final del auditor técnico

**(a) Orden.** Concedo al analista: calendario antes que la comparación. Pero la cabecera de comuna lleva una línea de **hechos sin juicio**, que sale íntegra del JSON: "Temporada 2026-27, hasta el 13-11: 12 celdas-día con detección · mediana de 14 temporadas al mismo día: 43" (`season_compare.current/median/n/cutoff_day`, `doc.cutoff`). Es la captura de WhatsApp que pide usuarios y no es veredicto. El veredicto y el KPI p90 se eliminan.

**(b) Lista de comunas.** Sin cifras. Cada ítem: nombre · región · chip de serie ("2012→" u "2002→", desde `index.comunas[].enabled`). Nada más; `observed_2012_2025`, `current` y `median` del índice no se muestran en la lista.

**(c) Fila Σ.** No existe en el JSON. `season_compare.observed_seasons{}` es el acumulado **truncado al día de corte**, no el total de la temporada; `index.observed_2012_2025` es un gran total. Concedo: la columna Σ se quita hasta que la publique el pipeline; el diseño deja el hueco dibujado como opcional.

Issue `ciencia` (cambio compatible, alcances §2):
1. En `comunas/<cut>.json` agregar `season_totals[]`: `{season, value, state, n_months, complete}` (suma de `series` por temporada, estado estimado si algún mes lo es, `complete=false` para 2026-27).
2. Agregar `month_climatology[]`: `{m, median, p25, p75}` sobre meses observados 2012→.
3. Opcional: `season_compare.verdict_ok: boolean` (temporada suficientemente avanzada para comparar).
4. Mismo PR corre `publish.py` y versiona los JSON; la web los muestra solo si llegan antes del domingo 11:00.

**No concedo:** la cabecera sin los dos números con fecha (sin ellos el alcalde y el periodista no tienen qué citar); n = 1 se conserva en el mapa, más tenue, con el aviso fijo pegado.
