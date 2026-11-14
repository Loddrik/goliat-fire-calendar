# Brief de diseño · GOLIAT (síntesis de la mesa redonda, 14-11-2026)

Para el diseñador (Pencil) y el monitor. Todo sale de los informes 01–09 y de `datos-ejemplo.md`. Las diferencias residuales se resolvieron hacia la posición más conservadora respecto al manifiesto; se marcan **[res.]**.

## 1. Acuerdos de la mesa

1. **Orden:** cabecera (para quién + no es alerta) → selector → encabezado de comuna → **calendario** → **línea de hechos** → **comparación de temporada** → **mapa** → método plegado → pie. Usuarios cedió "frase primero"; analista cedió que la frase exista; técnico cedió que no viva en el encabezado de comuna.
2. **Dónde va la línea de hechos:** primera línea del bloque "¿Cómo va esta temporada?", justo debajo de la leyenda del calendario. El encabezado de comuna lleva solo nombre, región, CUT, chip de serie y "Datos hasta". **[res.]** pregunta 1 antes que pregunta 2 (manifiesto §2).
3. **Redacción:** A (analista): "Temporada 2026-27, hasta el 13 de noviembre: 12 celdas-día con detección. A esta misma fecha, la mediana de 14 temporadas anteriores es 43." B (usuarios): "…En las 14 temporadas observadas (2012–2025), al mismo día, la mediana fue 4. Van 5 de los 12 meses de la temporada." **Se elige B**: dice "observadas (2012–2025)" como exige el glosario y la guardia de temporada temprana queda como hecho, sin umbral en la web. "Van k de 12 meses" (k = largo de `season_compare.months`) necesita el visto bueno de Daniel como texto del método; si no llega, se usa A.
4. **Sin veredicto, sin KPI p90, sin adjetivo, "vs.", flecha ni color comparativo.** El p90 solo se nombra en el método: "con 14 temporadas es una referencia débil" (CLAUDE.md regla 5).
5. **"No es alerta ni pronóstico; CONAF (Botón Rojo) y SENAPRED" va en la cabecera**, antes de cualquier número, en pantalla e impresión.
6. **n = 1 se conserva en el mapa**, en el tono más claro, nombrado en la leyenda, con el aviso fijo pegado.
7. **Sin columna Σ** hasta que `publish.py` entregue `season_totals`; se dibuja el hueco oculto.
8. **Sin fila de mediana por mes ni resaltado de "meses altos"**: no están en el JSON. Hueco oculto bajo el calendario.
9. **Lista de comunas sin cifras**: nombre · región · chip "2012→" o "2002→". Nunca "∅" solo.
10. **Nada que no venga de `web/public/data/`**; "no habilitado" nunca como "sin datos"; ningún rojo/naranjo para estados. Vecinas: solo "toca una comuna vecina en el mapa".

## 2. Textos definitivos (ES)

- **Título:** GOLIAT · Actividad de fuego detectada por satélite
- **Subtítulo:** Biobío y Ñuble, 54 comunas, 2002–2026. Datos NASA FIRMS (MODIS y VIIRS), puestos en una sola escala.
- **Para quién + no es alerta:** Para quien prepara su comuna antes de la temporada: planes comunales, juntas de vecinos, prensa e investigación. No es una alerta ni un pronóstico; una detección satelital no es un incendio. En una emergencia: CONAF (Botón Rojo) y SENAPRED.
- **Buscador:** "Buscar comuna o CUT…"
- **Encabezado (habilitada):** "Coihueco · Ñuble · CUT 16302" / "Datos hasta el 13-11-2026" / chip "Serie 2002–2026: observada desde 2012, estimada antes".
- **Encabezado (no habilitada):** "Penco · Biobío · CUT 08107" / "Datos hasta el 13-11-2026" / chip "Serie observada 2012–2026: antes de 2012 no habilitada".
- **Chip de serie en la lista:** "2002→" / "2012→".
- **Línea de hechos:** "{comuna}, temporada {temporada}, hasta el {corte}: {current} celdas-día con detección. En las {n} temporadas observadas (2012–2025), al mismo día, la mediana fue {median}. Van {k} de los 12 meses de la temporada." Coihueco: 7 / 14 / 173 / 5. Penco: 3 / 14 / 4 / 5. {corte} = "13 de noviembre de 2026".
- **Bloque 1:** "¿En qué meses se concentra?" — "Celdas-día con detección por mes y temporada (julio a junio)."
- **Bloque 2:** "¿Cómo va esta temporada?" — "Acumulado al 13-11, comparado con las 14 temporadas observadas al mismo día. Pocas temporadas: compara con cuidado."
- **Bloque 3:** "¿Dónde se ha repetido?" — "Temporadas con detección por sector, 2012–2026."
- **Bloque 4 (plegado):** "Cómo se hizo y qué no muestra" — "Factor regional, prueba por comuna, error típico y límites."
- **Leyenda (siempre junto al calendario):**
  - Observado — lo vio el satélite VIIRS (desde julio de 2012).
  - Estimado ±e — calculado desde el satélite Aqua (2002–2012) con un factor regional; el ± es el error típico (7 de cada 10 meses caen dentro).
  - ∅ No habilitado — sin estimación antes de 2012: en esta comuna la corrección no pasó la prueba. No significa cero detecciones.
  - • Provisional — últimos meses, cifras preliminares que FIRMS corrige en unos 5 meses (datos NRT).
  - Rampa: "0 … máx de la comuna · celdas-día". Mes incompleto: "…".
- **Separador:** "↑ observado (VIIRS) · ↓ estimado (Aqua)"; en Penco "↓ no habilitado".
- **Texto fijo bajo el calendario:** Una detección no es un incendio: puede ser incendio, quema agrícola o falso positivo. Una celda-día no es una hectárea. Un mes en cero puede haber estado nublado.
- **Barras:** rótulos "mediana" y "mitad central (p25–p75)"; barra actual "2026-27, al 13-11".
- **Texto fijo del mapa (encima, pegado):** Cada cuadro es una detección satelital de 375 m, no un predio, una empresa ni un incendio. Indica en cuántas temporadas hubo detección ahí. Toca una comuna vecina para verla.
- **Leyenda del mapa:** "1 temporada · 2 · 3–4 · 5–7 · 8 o más". Popup: "{n} temporadas · {d} días con detección · {f} a {l}".
- **Método, línea de compuertas:** "Prueba de la comuna: Aqua de entrenamiento 568 (mín. 50) ✓ · gana a climatología 8/8 ✓ · gana a Aqua crudo 8/8 ✓ (mín. 6) · error típico ±5,5 celdas-día." Penco: "21 (mín. 50) ✗ · 4/8 ✗ · 1/8 ✗ · sin estimación". Debajo, `methodBody` de Daniel, que incluye "no mostramos el percentil 90: con 14 temporadas es una referencia débil".
- **Pie:** "Datos: NASA FIRMS (MODIS/VIIRS), usados tal cual · Límites comunales: geoBoundaries/BCN · Mapa base: OpenFreeMap · Código abierto, Apache 2.0 · Corte: 13-11-2026 · Uso de IA declarado en el README." Luego, tal cual: "We acknowledge the use of data and/or imagery from NASA's Fire Information for Resource Management System (FIRMS) (https://earthdata.nasa.gov/firms), part of NASA's Earth Science Data and Information System (ESDIS)." y el disclaimer LANCE copiado del README.
- **Botones:** "Imprimir / guardar PDF", "CSV de la serie", "CSV de detecciones", "EN" (alterna "ES"), "Ver tabla", "Ver dónde se ha repetido" (celular), "Cómo se hizo y qué no muestra ▸". Bloque de botones: "Llevar".

## 3. Pantallas a diseñar

**Escritorio 1440 — Coihueco y Penco.** Aside 280 px (buscador + lista de 54, ítems 36 px) y main 1000 px. Alturas aproximadas: cabecera 96 px (título, subtítulo, para quién; botones EN · CSV serie · CSV detecciones · Imprimir a la derecha); encabezado de comuna 72 px; calendario ≈ 850 px (25 filas × 28 px, cabecera de meses 28, separador 24, leyenda 56, texto fijo 40; etiqueta de fila 88 px "2026-27", 12 celdas de 64 px, hueco Σ 64 px oculto); línea de hechos 72 px (20 px, peso 500) + subtítulo; barras 120 px con valor sobre cada barra, línea de mediana y franja p25–p75; mapa 420 px con aviso encima y leyenda dentro; método plegado 48 px; pie 72 px. Nada arriba del pliegue depende del mapa. Penco: filas 2011-12 → 2002-03 todas ∅, chip distinto.

**Celular 390 — Coihueco.** Una columna, márgenes 16 px. Buscador como combobox plegado. Cabecera + no es alerta. Encabezado de comuna. Calendario completo (25 filas): etiqueta 48 px ("26-27"), 12 celdas de 26 × 26 px sin número; la celda muestra solo trama/∅/borde; al tocar aparece bajo la grilla "Oct 2016 · 41 ±14 celdas-día · estimado". Botón "Ver tabla". Leyenda vertical. Línea de hechos a 18 px. Barras a ancho completo con valores (**[res.]** el recorrido obligatorio pasa por la temporada; no se pliegan). Mapa plegado, 300 px al abrir. Método y pie plegados. "Llevar" al final en dos filas; sin barra fija.

**Impresión A4 — Coihueco, una página, vertical, márgenes 15 mm, blanco y negro.** Cabecera: GOLIAT, comuna · región · CUT, "Datos hasta", para quién + no es alerta. Calendario completo, celdas 36 × 18 px, números siempre, tramas y glifos en vez de color, separador rotulado, leyenda textual. Línea de hechos. Tabla de 14 temporadas en texto (temporada / acumulado al 13-11 / mediana). Compuertas en 1 línea. Pie con fuentes, acknowledgement y URL `?cut=16302`. Sin aside, botones ni mapa (**[res.]** depende de teselas y no cabe; una eventual página 2 lleva el aviso fijo pegado).

## 4. Sistema visual

- **Tokens (nombres de App.css):** `--bg #FCFBF7`, `--fg #1A1A1A`, `--muted #5F5F5F`, `--card #FFFFFF`, `--line #E2E2DC`, `--accent #1F6F8B`. `--warn` deja de usarse para estados; ningún rojo/naranjo de advertencia.
- **Rampa calendario (viridis 6 pasos, 0 → máx de la comuna):** `#440154 #414487 #2A788E #22A884 #7AD151 #FDE725`; texto blanco en los tres primeros, negro en los tres últimos. Cero = `--card` con borde `--line`.
- **Rampa mapa (ColorBrewer Purples, entre #cbc9e2 y #3f007d del técnico, n = 1 más tenue):** 1 `#DADAEB` · 2 `#BCBDDC` · 3–4 `#9E9AC8` · 5–7 `#756BB1` · 8+ `#3F007D`. Basemap positron.
- **Tipografía:** IBM Plex Sans 400/500/600; cifras con `tabular-nums`. Cuerpo 15 px, celdas 12 px escritorio / 11 px impresión, línea de hechos 20 px.
- **Cuatro estados sin color:** observado = celda lisa, número romano · estimado = número + "±e" en cuerpo menor ("41 ±14") y trama diagonal 45° blanca 4/8 px; la cursiva nunca es la única señal · no habilitado = fondo blanco, borde punteado 1 px `--muted`, "∅" gris centrado · provisional = "•" tras el número ("4•") y borde continuo 2 px `--accent` · separador rotulado entre 2011-12 y 2012-13: regla 2 px `--fg`.

## 5. Componentes en Pencil

`Cabecera` · `BarraAcciones` (escritorio; en celular, bloque "Llevar") · `Boton` (primario / secundario / enlace) · `Buscador` (lista / combobox) · `ItemComuna` (normal / seleccionada; chip 2012→ / 2002→) · `Chip` (serie-2012, serie-2002, provisional) · `EncabezadoComuna` (habilitada / no habilitada) · `CeldaCalendario` (observado / estimado / no-habilitado / provisional / incompleto / futuro × 28, 26, 18 px × con/sin número) · `FilaTemporada` (etiqueta + 12 celdas + hueco Σ oculto) · `SeparadorSerie` · `Leyenda` (horizontal / vertical / textual-impresión) · `TextoFijo` (calendario / mapa / no-es-alerta) · `LineaHechos` (20 / 18 px / impresión) · `Barras14` (mediana + franja p25–p75; variante tabla-impresión) · `LeyendaMapa` (5 clases) · `PanelPlegable` (abierto en impresión) · `Pie`.

## 6. Lista de verificación del monitor

1. ¿Ningún texto dice incendios, hectáreas, alerta (salvo en sus negaciones fijas), riesgo, pronóstico, predicción, tiempo real?
2. ¿Observado, estimado, ∅ y provisional se distinguen con la pantalla en gris (número/trama/borde/glifo)?
3. ¿Cada celda estimada muestra su "±e"?
4. ¿La leyenda de ∅ dice que no significa cero detecciones?
5. ¿"No es alerta; CONAF/SENAPRED" está en la cabecera, antes de cualquier número, en las tres pantallas?
6. ¿La comparación no tiene adjetivo ni veredicto, y dice n = 14, "observadas (2012–2025)" y "al mismo día"?
7. ¿El mapa lleva el aviso "375 m, no un predio, una empresa ni un incendio" pegado y ningún nombre de predio o empresa?
8. ¿La fecha de corte aparece en encabezado de comuna, línea de hechos, impresión y pie?
9. ¿Todo número existe en `index.json` o `comunas/<cut>.json`? (sin Σ, mediana por mes, p90 ni mini-cifras en la lista)
10. ¿Acknowledgement FIRMS, geoBoundaries/BCN, OpenFreeMap y licencia visibles o a un clic?
11. ¿Las tres pantallas están completas, sin contenido recortado ni texto desbordado (Penco con 10 filas ∅; A4 en una página)?
12. ¿Todos los textos están en ES, copiados de la sección 2 sin variaciones?
13. ¿Todos los números salen de `datos-ejemplo.md` (Coihueco 7 / 173 / ±5,5 / 568 / 8/8 / 8/8; Penco 3 / 4 / 21 / 4/8 / 1/8; 14 temporadas; corte 13-11-2026)?

## 7. Issue `ciencia` pendiente y huecos

Texto del técnico (cambio compatible, alcances §2):
1. En `comunas/<cut>.json` agregar `season_totals[]`: `{season, value, state, n_months, complete}` (suma de `series` por temporada, estado estimado si algún mes lo es, `complete=false` para 2026-27).
2. Agregar `month_climatology[]`: `{m, median, p25, p75}` sobre meses observados 2012→.
3. Opcional: `season_compare.verdict_ok: boolean` (temporada suficientemente avanzada para comparar).
4. Mismo PR corre `publish.py` y versiona los JSON; la web los muestra solo si llegan antes del domingo 11:00.

Huecos del diseño: columna "Σ temporada" a la derecha del calendario (64 px, oculta; mostrará `season_totals` con su estado y "…" si `complete=false`); fila "Mediana 2012–2026" bajo la grilla (oculta; `month_climatology`); "Van k de 12 meses" se mantiene aunque llegue `verdict_ok` (no se agrega veredicto). Si nada llega, los huecos quedan cerrados y nada cambia de lugar.

## 8. Adenda de la sesión principal (14-11, tras verificar los datos)

- **Issue #20 (bug en `publish.py`):** `season_compare.observed_seasons/median/p25/p75` publicados hoy NO están truncados al día de corte; son casi totales de temporada. Por eso la maqueta **no usa 173 (Coihueco) ni 4 (Penco)** como mediana. Usa los valores de maqueta de `datos-ejemplo.md` (sección final): Coihueco current 7 · mediana ≈ 21 · p25 ≈ 17 · p75 ≈ 30 · n 14; Penco current 3 · mediana ≈ 0 · p25 ≈ 0 · p75 ≈ 1 · n 14. Las barras de las 14 temporadas usan los acumulados jul–nov de esa misma sección. El diseño lleva una nota de canvas (fuera de la pantalla) "valores de maqueta, pendiente #20".
- **Issue #21** ya abierto con el texto de la sección 7.
- El punto 13 del monitor se corrige en consecuencia: la línea de hechos de Coihueco dice "7 … la mediana fue 21"; la de Penco "3 … la mediana fue 0".

## 9. Cambios tras el monitor (ciclo 1)

- **Rampa del calendario en pantalla:** viridis se reemplaza por ColorBrewer Blues de 6 pasos, clara→oscura: `#DEEBF7 #C6DBEF #9ECAE1 #6BAED6 #3182BD #08519C` (variables `azul-1..6`); texto `--fg` en los 4 primeros, blanco en los 2 últimos; cero = `--card` con borde `--line`. Motivo: con viridis los valores bajos quedaban en el morado más oscuro y los máximos en amarillo claro, invirtiendo "más oscuro = más actividad".
- **Impresión A4:** gris-1 = `#EBEBEB` (el cero sigue blanco con borde) para que 1–18 no se confunda con cero.
- **Barras de temporada:** histórico `#BDBDB5`, barra actual `--accent`.
- **Aviso del mapa (corrección de validez):** "Cada cuadro es un sector de ~1 km donde el satélite (píxeles de 375 m) detectó calor en una o más temporadas. No es un predio, una empresa ni un incendio, y no dice quién lo provocó. Toca una comuna vecina para verla." Las celdas del mapa son de 0,01°, no de 375 m.
- **Capa de traducción para el encargado municipal (pedido de la sesión principal, 14-11):** línea bajo el encabezado de comuna explicando la unidad ("Cada celda-día es un cuadrado de ~1 km donde el satélite vio calor un día…"); caja "Para el plan comunal" (qué copiar, cómo citar, total por temporada pendiente de #21); prefijos de usuario en la leyenda ("Seguro ·", "Aproximado ·", "No lo mostramos ·", "Puede cambiar ·").
- **Pendiente de producto:** la mención "(aviso LANCE)" en el pie requiere agregar el disclaimer oficial al README o quitarla (revisión de producto P5).

## 10. Actualización 14-11 (tarde): PR #22 de Daniel

El PR #22 (mergeado directo a `main` y desplegado) corrigió el truncado de `season_compare` (#20 cerrado). Los "valores de maqueta" de la sección 8 pasaron a ser los valores publicados: Coihueco current 7 · mediana 21 · p25 17 · p75 29; Penco 3 · 0 · 0 · 1. El mismo PR reordenó la app (calendario antes que temporada), agregó una línea de audiencia bajo el subtítulo, chips 2002→/2012→ en la lista y un `<title>` bilingüe, y sumó una segunda vista "Historial por plataforma · FireChronos" (sin armonizar, DPA 2023) con un conmutador de vistas arriba. El rediseño debe partir del `App.tsx` de `main`, no del de `dev`.

## 11. Cierre de colores y texto (decisión de Rubén, 14-11 tarde)

- **Una sola rampa en toda la página, 5 pasos Blues:** `#C6DBEF #9ECAE1 #6BAED6 #3182BD #08519C`. Calendario y mapa usan la misma.
- **Tramos fijos para las 54 comunas** (ya no "0 … máx de la comuna"), elegidos con la distribución real de 9.342 meses observados (51 % son cero; de los >0, 68 % están en 1–5, 22 % en 6–20, 6 % en 21–50, 2 % en 51–100, 1 % sobre 100): 0 = blanco con borde · 1–5 · 6–20 · 21–50 · 51–100 · más de 100 celdas-día. La leyenda rotula cada muestra con su número. Impresión: 5 grises `#EBEBEB → #333333`.
- **Mapa:** 1 · 2 · 3–4 · 5–7 · 8 o más temporadas, mismos azules.
- **Cabecera:** se elimina el párrafo de audiencias. Línea bajo el título: "Cuándo y dónde ha habido fuego en tu comuna, según los satélites de la NASA, desde 2002." Aviso aparte: "No es una alerta. En una emergencia, llama a CONAF o SENAPRED."
- **Pendiente de conversar:** la matriz completa pasa a segundo plano (perfil de 12 meses + comparación de temporadas por defecto; depende de #21) y el mapa como puerta de entrada con control de temporada (requiere celdas por temporada del pipeline).

## 12. Mapa primero (decisiones de Rubén, 14-11 noche)

- **Al abrir: mapa regional** con las 15.550 celdas (propuesta en `14-propuesta-mapa.md`, condiciones del manifiesto en `15-ronda4-analista-mapa.md`).
- **Control de tiempo por temporada** (jul–jun): "Todas 2012→" + un botón por temporada 12-13 … 26-27. Sin mes, sin animación.
- **Frase de temporada con categoría** (pedido de Patricio y Rosa, `13-usuario-final-eval-actual.md`): "por debajo / parecido / por encima de lo habitual para esta fecha", **solo en diseño hasta que el issue #4 (estabilidad de categorías, ciencia) lo apruebe**. Resguardo: sin categoría cuando p75 < 10 (34 de 54 comunas al 13-11). Siempre con "No anticipa cómo seguirá la temporada" y los meses donde suele llegar la actividad.
- **Perfil de 12 meses**: barra = mediana observada; marca = máximo; rótulo "en X de 14 temporadas" (`month_climatology.seasons_with`, agregado a `publish_web.py`). La mediana sola aplana comunas como Hualqui.
