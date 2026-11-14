# Revisión de producto #1 — 2026-11-14 ~14:10 (agente `revisor-producto`, solo lectura)

**Veredicto: SIRVE CON AJUSTES.** Usuario y decisión están en el README pero **no en la app** (P3, bloqueante, 10 min). Todo lo demás son textos, orden de secciones y una fila de tabla: nada nuevo antes del cierre del domingo 11:00.

## Bloqueantes

1. **P3 — la app no dice para quién es.** Agregar bajo el subtítulo (y en la impresión):
   - ES: *"Para el encargado municipal de emergencias o SECPLAN que debe caracterizar la amenaza de incendios en su plan comunal, y para vecinos y dirigentes que preparan su sector antes de la temporada. Son antecedentes históricos: no es una alerta ni un pronóstico."*
   - EN: *"For municipal emergency and planning officers who must characterize wildfire hazard in their communal plan, and for residents and community leaders preparing their area before the season. Historical background only: not an alert, not a forecast."*
2. **Integridad.** README decía 36/54 y r = 2,34; app y método dicen 14/54 y 2,35. → Corregido el 14-11 14:40.
3. **P4 en riesgo por diseño.** La tarjeta "Temporada en curso" va primero, con veredicto en cursiva, y el "no es alerta" queda al pie. Ver ajuste 3.

## Ajustes, en orden de impacto por hora

1. **Fila "Mediana 2012–2026" bajo el calendario + resaltar los 3 meses más altos** (~1 h). Es la respuesta directa a la pregunta 1 del manifiesto y lo que va al cuadro de ocurrencia del plan comunal (Coihueco). Permite leer cada celda como anomalía contra la mediana (P1, P13).
2. **Reencuadrar "no habilitada" y reordenar la página** (~45 min): calendario → temporada → mapa.
   - Chip gris, no naranjo. `reconNot` → *"Serie observada 2012–2026 · 14 temporadas"*; `reconEnabled` → *"Serie 2002–2026 · observada + estimada"*.
   - `reconNotWhy` → ES: *"Para esta comuna publicamos solo lo observado por VIIRS desde julio de 2012 (14 temporadas). La estimación 2002–2012 a partir de MODIS no pasó nuestras pruebas aquí, así que no la mostramos. Detalle en «Método y límites»."* EN: *"For this commune we publish only what VIIRS observed since July 2012 (14 seasons). The 2002–2012 estimate from MODIS did not pass our tests here, so it is not shown. Details under 'Method and limits'."* La explicación técnica se va al panel de método.
   - Barra lateral: `" · ∅"` → `" · 2012→"` / `" · 2002→"`.
3. **Guardia de temporada temprana en la tarjeta** (~45 min). Si el último mes acumulado es ≤ noviembre **o** la mediana < 10, no mostrar veredicto; mostrar: *"Temporada recién empezando: hasta el 13 de noviembre lo habitual en {comuna} son pocas detecciones (mediana {N} en 14 temporadas). La comparación es más informativa desde diciembre. Este dato no anticipa cómo seguirá la temporada."* KPI → *"Esta temporada, al 13-nov"*. Agregar a `seasonHelp`: *"No anticipa cómo seguirá la temporada."* Quitar el KPI p90 (débil con n = 14; las barras ya muestran los extremos).
4. **Mapa: evitar la lectura de culpa** (~30 min).
   - Título: *"Sectores donde el fuego se ha repetido (2012–2026)"* / *"Where fire has recurred (2012–2026)"*.
   - Texto fijo bajo el mapa, también en impresión: *"Cada celda es ~1 km donde el satélite detectó calor diurno en una o más temporadas. No identifica predios, propietarios, causas ni responsables: una celda puede abarcar varios terrenos, y una quema agrícola autorizada cuenta igual que un incendio. Sirve para saber que el fuego ya pasó por este sector, no para decir quién lo provocó ni dónde habrá fuego."*
   - Popup bilingüe: *"{n} temporadas con detecciones · {d} días · {f}–{l}"* / *"{n} seasons with detections · {d} days · {f}–{l}"*.
   - Quitar (o casi transparentar) la categoría n = 1: una temporada es un evento, no recurrencia.
5. **P5/P6/P17 textos** (~20 min). `sources` de la app: agregar *"Reconocemos el uso de datos de NASA FIRMS (EOSDIS). Datos entregados «tal cual», no aptos para decisiones tácticas (aviso LANCE)."* `calendarHelp`: agregar *"Una detección es calor visto desde el satélite: puede ser un incendio, una quema agrícola autorizada o un falso positivo; no se distinguen."* "Una detección no es un incendio" junto al calendario, no solo al pie.
6. **P10** `<title>` y leyenda del mapa bilingües de verdad (ES o EN según idioma, no mezclados).
7. **P11 CSV de detecciones** (~30 min, `publish.py`): agregar columnas `daynight` (hoy todas D, pero debe constar) y `used_in_series` (día + confianza + no enmascarada + plataforma de la temporada) para que el filtro sea reproducible. CSV de serie: agregar mediana y percentiles por mes si cabe.
8. **P12** mostrar la plataforma (S-NPP / NOAA-20) en el tooltip del calendario.

## Checklist

| # | Estado | Nota |
|---|---|---|
| P1 | ⚠️ | Sin vista de anomalía mes vs mediana (ajuste 1) |
| P2 | ✅ | Temporada truncada al mismo día, misma plataforma |
| P3 | ❌ | Usuario y decisión solo en README |
| P4 | ✅/⚠️ | Tarjeta con veredicto arriba |
| P5 | ⚠️ | Acknowledgement FIRMS falta en la app |
| P6 | ⚠️ | "Detección ≠ incendio" solo al pie |
| P7–P9 | ✅ | |
| P10 | ⚠️ | Popup y título mezclados |
| P11 | ⚠️ | CSV detecciones sin `daynight` / `used_in_series` |
| P12 | ⚠️ | Plataforma solo en CSV |
| P13 | ⚠️ | Calendario tercero; sin fila de mediana |
| P14, P15 | ✅ | |
| P16 | N/A | Sin IA |
| P17 | ❌ | La app no menciona quemas agrícolas |

## Recortar
KPI p90; párrafo técnico naranjo en la cabecera de comuna; cualquier función nueva antes de las 11:00 del domingo.
