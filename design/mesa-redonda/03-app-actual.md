# Mesa redonda · Informe 3 — Auditoría de la app actual (agente auditor, 14-11-2026)

Nota: la URL en vivo es un SPA; WebFetch solo devuelve el `<title>` ("GOLIAT · Fire activity calendar · Biobío y Ñuble", `web/index.html:7`, mezclado ES/EN). Lo demás se describe desde el código.

## 1. Inventario de pantallas y bloques (orden real en `web/src/App.tsx`)

Layout de 2 columnas: aside fijo 260 px + main ≤1100 px (`App.css:16,25`). Una sola página, sin rutas; la comuna va en `?cut=` (App.tsx:13,22); por defecto 08107 (Penco).

1. **Header** (App.tsx:34-45): h1 "GOLIAT", subtítulo "Calendario de actividad de fuego detectada · Biobío y Ñuble · MODIS + VIIRS armonizados (NASA FIRMS)" (i18n.ts:5). Botones a la derecha: toggle "EN/ES", "CSV serie", "CSV detecciones", "Imprimir / guardar PDF" (i18n.ts:28-30). No dice para quién es ni muestra el disclaimer arriba.
2. **Selector de comuna** (aside, App.tsx:48-61): input "Buscar comuna…" (sin tildes, también por CUT) + lista de 54 comunas ordenadas región→nombre; cada ítem muestra nombre y `region · ∅` si no está habilitada (App.tsx:56). Seleccionada: fondo celeste + bold (App.css:23). Solo oculto en impresión.
3. **Titlebar de comuna** (App.tsx:66-73): h2 "{comuna} · {region} · CUT {cut}", chip verde "Reconstrucción 2002–2012 habilitada" o naranjo "Reconstrucción 2002–2012 no habilitada" (i18n.ts:9-10; App.css:30-31), "Datos hasta {cutoff}" alineado a la derecha. Bajo el chip, en 40/54 comunas, párrafo naranjo técnico `reconNotWhy` (i18n.ts:11).
4. **Temporada en curso** (`SeasonCompare.tsx`, primera tarjeta): h2 "Temporada en curso 2026-27"; help `seasonHelp` ("Acumulado desde el 1 de julio hasta el día de corte, contra las 14 temporadas observadas desde 2012 truncadas al mismo día (13 de noviembre)… Con 14 temporadas, el percentil 90 es una referencia débil", i18n.ts:19). 4 KPIs: "Esta temporada" (grande, color acento, con veredicto en cursiva gris calculado en la web: "sobre el percentil 90 / 75", "en torno a la mediana", "bajo la mediana", SeasonCompare.tsx:11-13), "Mediana histórica", "Percentil 75", "Percentil 90". Debajo, barras de 90 px de alto por temporada (etiqueta de 2 dígitos "12…25", barra actual en acento), sin eje ni valores visibles salvo tooltip (SeasonCompare.tsx:24-35).
5. **Calendario** (`Calendar.tsx`): h2 "Calendario de actividad de fuego"; help i18n.ts:13. Tabla temporadas (filas, más reciente arriba, 2026-27 → 2002-03 = 25 filas) × meses Jul→Jun + columna "Σ". Celda 48×26 px, fuente 12 px (App.css:49-52). Color: rampa viridis 6 pasos sobre √(valor/máx) (Calendar.tsx:5-11); texto blanco sobre oscuros. **Tres estados hoy**: observado = color plano; estimado = mismo color + rayado diagonal blanco + cursiva + tooltip "valor ± banda" (App.css:53; Calendar.tsx:41); no habilitado = gris #f3f3f3 con "∅" (App.css:54). Provisional (NRT) = outline punteado naranjo (App.css:55); mes incompleto = "valor…" (Calendar.tsx:46). Leyenda con swatches "Observado (VIIRS)", "Estimado (MODIS Aqua × 2,35) ± error típico", "∅ No habilitado", "Provisional (datos NRT, se reprocesan en ~5 meses)" y rampa "0 … máx" (Calendar.tsx:56-62). La distinción sin color depende del rayado fino, la cursiva y el ∅; **no hay fila de mediana ni resaltado de meses altos**.
6. **Mapa de recurrencia** (`RecurrenceMap.tsx`): h2 "Dónde se repite"; help i18n.ts:25. MapLibre 440 px, estilo OpenFreeMap *positron* (línea 9), polígonos comunales (clic = cambia comuna, línea 27), celdas 0,01° coloreadas por nº de temporadas con rampa roja 5 pasos (1, 2, 3–4, 5–7, 8+; línea 10). Popup solo en español "{n} temporadas · {d} días · {f}–{l}" (línea 31); leyenda "temporadas / seasons" mezclada (línea 48). fitBounds a las celdas de la comuna (línea 66).
7. **Método y límites** (App.tsx:89-99): acordeón cerrado por defecto (▸), abierto siempre en impresión (`print-only`). Lista `gates` con MAE crudo/const/clim, victorias n/8 con ✓/✗, Aqua/S-NPP de entrenamiento, error típico y coberturas; luego 7 párrafos `methodBody` (i18n.ts:35-43).
8. **Footer** (App.tsx:102-105): disclaimer en bold gris: "GOLIAT entrega antecedentes históricos para la planificación. No es una alerta ni un pronóstico: para la emergencia, CONAF y SENAPRED. Una detección satelital no es un incendio." (i18n.ts:34) y fuentes (i18n.ts:44; sin acknowledgement FIRMS).
9. **Descargas**: "CSV serie" se genera en la web desde el JSON (csv.ts:3-13, columnas `cut, comuna, season, year, month, celldays_viirs_scale, state, platform, provisional, band_mae, aqua_celldays, cutoff, r_const` + 4 líneas de metadatos); "CSV detecciones" es un enlace estático a `/data/detections/<cut>.csv`.
10. **Impresión** (App.css:79-89): oculta aside y botones, una columna, mapa 320 px, celdas 40×20, método desplegado. Mismo DOM.
11. **ES/EN**: idioma inicial por `navigator.language` (App.tsx:11); dict completo en i18n.ts, pero varios strings están inline con ternarios (App.tsx:93-95; SeasonCompare.tsx:8,11-13; Calendar.tsx:23,45) y el mapa es monolingüe.

## 2. Datos disponibles para diseñar (`web/public/data/`)

**index.json** (`types.ts:44-45`): `generated`, `cutoff` ("2026-11-13"), `current_season` (2026), `r_const` (2,353), `params{}` (validación: `loso_total_mae` M0/M1/M2, `r_by_season_train/after`, coberturas de banda, `excluded`, `train/test`; hoy no se muestra) y `comunas[54]` con `cut, comuna, region, enabled (14 true), observed_2012_2025 (total celdas-día observadas), current (acumulado temporada), median`. Permite un ranking/mini-resumen por comuna en la lista.

**comunas/<cut>.json** (`types.ts:31-42`):
- `cut, comuna, region, cutoff, r_const, reconstruction_enabled`.
- `gates{}`: `aqua_train, snpp_train, min_aqua, loso_mae_raw/const/clim, wins_vs_clim, wins_vs_raw, of (8), min_wins (6), gate_aqua/gate_vs_clim/gate_vs_raw, band_mae, band_coverage_1/2` (las coberturas son globales, iguales en todas).
- `series[293]`: un mes desde 2002-07 hasta 2026-11: `season, y, m, value|null, state ∈ observed|estimated|not_enabled`, opcionales `sat (SNPP|NOAA20), provisional, partial, band (± error típico, solo estimado), aqua (celdas-día Aqua crudas; también viene en las filas not_enabled)`. Ej. Tomé: 120 estimados, estimado `{value:0.0, band:3.1, aqua:0}`.
- `season_compare`: `season, months[] (7..11), cutoff_day (13), current, observed_seasons{2012..2025}, n (14), median, p25, p75, p90`. Todo truncado al mismo día, solo observado.
- `recurrence[]`: celdas `x, y` (×0,01° = lon/lat), `n` temporadas, `d` días, `f`/`l` primera/última temporada. Entre 3 y 1032 celdas por comuna.
- `comunas.geojson` (308 KB, `promoteId: cut`). `status.json` = `{"status":"empty"}`, sin uso.

**No existe** en los datos: mediana por mes del calendario, anomalía mes vs mediana, cobertura observacional, noche, FRP, hectáreas, nombre de predios, nada por día. Todo lo que no está aquí requiere issue `ciencia`/`publish.py` (alcances.md §2).

## 3. Pendientes de la revisión de producto (docs/reviews/2026-11-14-product-review.md)

1. **Bloqueante — la app no dice para quién es** (P3, líneas 7-9): texto de usuario bajo el subtítulo y en impresión.
2. **P4 — orden y tono**: temporada con veredicto arriba, "no es alerta" al pie (línea 11). Propuesta: calendario → temporada → mapa; guardia de temporada temprana (≤ noviembre o mediana < 10: sin veredicto, texto explicativo); quitar KPI p90; KPI "Esta temporada, al 13-nov" (líneas 16, 20).
3. **P1/P13 — fila "Mediana 2012–2026" y resaltar 3 meses más altos** bajo el calendario (línea 15). Ojo: la mediana por mes **no viene en el JSON**; pedirla a `publish.py`.
4. **Reencuadrar "no habilitada"**: chip gris, "Serie observada 2012–2026 · 14 temporadas" vs "Serie 2002–2026 · observada + estimada"; `reconNotWhy` breve; aside `· 2012→`/`· 2002→` en vez de ∅ (líneas 17-19).
5. **Mapa sin lectura de culpa**: título "Sectores donde el fuego se ha repetido (2012–2026)", texto fijo bajo el mapa, popup bilingüe, atenuar/quitar n = 1 (líneas 21-25).
6. **P5/P6/P17 textos**: acknowledgement FIRMS + "tal cual"; "una detección puede ser incendio, quema agrícola autorizada o falso positivo" junto al calendario (línea 26).
7. **P10** `<title>` y leyenda del mapa bilingües (línea 27). **P12** plataforma S-NPP/NOAA-20 en tooltip (línea 29). P11 es de pipeline.

## 4. Problemas de UI vistos en código/CSS

- **Jerarquía**: tres niveles de h2 (comuna, tarjetas, botón acordeón) con tamaños 22/17 px (App.css:27,35); el dato principal (calendario) es la 3.ª tarjeta y la cursiva del veredicto compite con el KPI de 34 px (App.css:41-42).
- **Densidad/legibilidad del calendario**: 25 filas × 14 columnas con celdas 48×26 y texto 12 px; el rayado del estimado (3/7 px) sobre amarillo viridis casi no se ve; umbral de texto blanco a 0,45 de la raíz (Calendar.tsx:42) deja números negros sobre verde medio. Total "Σ" sin unidad. Sin fila de mediana ni separador visual entre bloque estimado (2002–2011) y observado (2012→).
- **Estados sin color**: cursiva + rayado fino es débil; en impresión en blanco y negro la rampa viridis pierde orden. Provisional = outline naranjo que también es el color de "no habilitada" (--warn), confundiendo "advertencia" con "dato nuevo".
- **Barras de temporada**: 90 px, sin eje, sin valores, sin línea de mediana; etiquetas de 10 px (App.css:43-47).
- **Móvil** (App.css:72-77): lista de comunas a 180 px de alto encima del contenido; calendario con scroll horizontal (14 columnas); mapa de 440 px; botones del header en una sola fila sin wrap (App.css:11); KPIs 2×2.
- **Impresión**: no hay cabecera de reporte (comuna, fecha de corte, usuario, disclaimer arriba); mapa depende de que los tiles carguen; leyenda del mapa mezclada; acordeón de método completo (7 párrafos + gates) ocupa más que el dato.
- **Textos inline no traducidos** (ver §1.11) y popup del mapa solo ES.
- **Mapa**: 1 temporada ocupa el color más claro pero sigue siendo "recurrencia"; popup usa `f–l` como años sin etiqueta de temporada.
- Estado de carga "…" (App.tsx:101); no hay estado vacío cuando `recurrence` tiene 3 celdas.

## 5. Restricciones técnicas que el diseño debe respetar

- React 19 + Vite + TypeScript, un solo `App.css` con variables (`--bg, --fg, --muted, --card, --line, --accent #2a788e, --warn #b4560a`, App.css:2); sin librería de componentes.
- Mapa MapLibre GL con basemap OpenFreeMap *positron* (RecurrenceMap.tsx:9), worker configurado (líneas 4-6); capas: comunas (geojson) + celdas de recurrencia como polígonos 0,01°. Atribución compacta obligatoria.
- **Nada se calcula en la web** (CLAUDE.md; alcances.md §1 línea 16): hoy la web sí deriva el veredicto, el máximo de la rampa, el total Σ y el rango de temporadas; el rediseño no debe agregar más cálculos (mediana por mes, anomalías → pipeline).
- Pantalla, impresión y CSV leen el mismo JSON (`series`); el CSV serie se arma en csv.ts desde `doc.series`. Si el diseño muestra un campo nuevo, debe estar en el JSON y en el CSV.
- ES/EN completo vía `dict` (i18n.ts); `methodBody`, `estimated`, `reconNotWhy`, `seasonHelp` los aprueba Daniel (alcances.md §1).
- Tres estados + provisional siempre distinguibles sin color; lenguaje: "actividad de fuego detectada", "celdas-día", "detecciones"; nunca incendios/hectáreas/alerta/riesgo/pronóstico.
- Impresión por `window.print()` con `.no-print`/`.print-only`; la URL `?cut=` es el único estado compartible.
- Corte: domingo 11:00 cierran funcionalidades; lo demás son textos y CSS.
