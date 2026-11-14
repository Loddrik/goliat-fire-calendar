# Mesa redonda · Informe 14 — Propuesta: el mapa como puerta de entrada

Diseñador de experiencia de mapas. Base: CLAUDE.md (regla 4), informe 12 (Patricio y Rosa), brief 10 (§2, §9, §11 se conservan), `publish_web.py`, `derived/region.json` (15.550 celdas de 0,01°, 1,3 MB / 103 KB gz), `RecurrenceMap.tsx`.

Cifras de los datos que mandan el diseño: 54 % de las celdas tienen detección en una sola temporada (8.442 de 15.550); máximo 13 temporadas. Por temporada, una celda tiene como máximo 19 días con detección y casi siempre 1–2. Entre 1.400 y 3.800 celdas tienen detección en una temporada dada; 2026-27 lleva 233. `region.json` trae días por temporada por celda, pero **no** el eje de mes (ese está solo en `derived/<cut>.json`, sumado sobre todas las temporadas) y **no existe mes × temporada**.

## 1. Las tres decisiones

**(a) Al abrir: mapa regional con todas las celdas, "todas las temporadas", comuna sin elegir.** Patricio y Rosa reconocen su territorio antes que un nombre en una lista; Rosa además necesita ver las comunas vecinas ("nunca pensamos que el de Nacimiento iba a venir para acá"), cosa que una vista "comuna primero" esconde. Encima del mapa va un buscador grande; al tocar una comuna (polígono) o buscarla, el mapa se acerca y abre la ficha. El enlace compartido `?cut=08112` abre directo en la comuna con la ficha desplegada: es lo que viaja por WhatsApp. En celular con `navigator.connection.saveData` o `effectiveType` 2g, se abre con buscador y ficha, y el mapa queda en un botón "Ver el mapa" (la ficha no depende del mapa).

**(b) Control de tiempo: solo temporada, en chips; sin mes, sin animación.** Chips en una fila (desplazable en celular): `Todas 2012→` · `12-13` · `13-14` … `25-26` · `26-27•`. "Todas" es el valor inicial y pinta **temporadas con detección** (n); una temporada pinta **días con detección en esa temporada** (sᵢ). Mes no entra al mapa: no hay mes × temporada en los datos y la pregunta "¿en qué meses?" ya la responde la ficha (perfil de 12 meses). Animación no: el salto chip a chip ya cuenta la historia y no hay tiempo para que se vea bien. Rótulo bajo los chips, siempre visible:
- Todas: "Temporadas con detección por sector, 2012-13 a 2026-27 (hasta el 13-11-2026). Solo observado por VIIRS."
- Una temporada: "Días con detección por sector, temporada 2022-23 (julio 2022 a junio 2023)."
- 2026-27: "…temporada 2026-27, hasta el 13-11-2026 · provisional (FIRMS corrige en unos 5 meses)."

**(c) La tabla queda como herramienta, a un toque.** La ficha de comuna muestra, en este orden: encabezado del brief (nombre · región · CUT · "Datos hasta" · chip de serie); **línea de hechos** (texto B del brief, sin cambios); **perfil de 12 meses**: 12 barras jul→jun con la mediana observada por mes (`month_climatology`, 2012→2025) y el valor de 2026-27 marcado con •; botones "Ver tabla completa" (la matriz actual de 25 filas con sus 3 estados y leyenda, en una vista aparte con el mismo `?cut=&vista=tabla`), "Imprimir / guardar PDF", "CSV de la serie", "CSV de detecciones", "Compartir" (Web Share con la URL). Se pliega: método, caja "Para el plan comunal", pie. Impresión y CSV no cambian: siguen leyendo `comunas/<cut>.json`; el A4 sigue sin mapa. La mediana por mes es un número nuevo en pantalla: pasa por `revisor-cientifico` antes de mostrarse; si no alcanza, las barras muestran 2025-26 y 2026-27, sin mediana.

## 2. Guion de uso

**Patricio (notebook, Coihueco).**
- P1-T1 (meta ≤ 60 s, ≤ 3 clics). Ve el mapa de las dos regiones con puntos azules y la frase "No es una alerta…". Escribe "Coi" en el buscador (clic 1), elige Coihueco (clic 2): el mapa se acerca, la comuna queda con borde negro y las vecinas atenuadas; a la izquierda aparece la ficha. Lee el perfil de 12 meses: las barras altas son ene–feb–mar. Responde a los 25 s, sin método.
- P1-T2 (≤ 90 s). Lee la línea de hechos: "Coihueco, temporada 2026-27, hasta el 13 de noviembre de 2026: 7 celdas-día con detección. En las 14 temporadas observadas…". Toca "Copiar" junto a la frase (se copia con la fuente y la URL). 40 s.
- P1-T3 (≤ 2 min). Clic en "Ver tabla completa": la matriz con observado liso, estimado con trama y ±e, ∅ con borde punteado, leyenda con prefijos "Seguro · Aproximado · No lo mostramos". Clic en "Imprimir". Explica los tres estados desde la leyenda; "∅ no significa cero". 90 s.

**Rosa (Android, Hualqui, enlace recibido por WhatsApp).**
- P2-T1 (≤ 60 s). Abre `?cut=08112`: cabecera de dos líneas, aviso, mapa a 55 % de alto ya centrado en Hualqui, y abajo la ficha asomada con "Hualqui · Biobío" y la línea de hechos. Sube la ficha: perfil de 12 meses con barras en ene–feb. Responde "sí, enero y febrero". 35 s.
- P2-T2 (≤ 90 s). Baja la ficha. Sobre el mapa lee el aviso pegado ("…sector de ~1 km donde el satélite detectó calor… no es un predio, una empresa…"). Los cuadros oscuros se agrupan hacia un cerro; toca uno: "Sector de ~1 km · 6 temporadas con detección · 9 días". Toca el chip "22-23": quedan menos cuadros, claros. Vuelve a "Todas". Explica: "donde el satélite vio calor varios veranos, no de quién es". 70 s.
- P2-T3 (≤ 60 s). La pantalla a altura de comuna cabe en una captura: nombre, chip de temporada, rótulo con fecha, mapa, leyenda. Toca "Compartir" y manda el enlace con la frase de hechos (comuna, número, "hasta el 13-11-2026"). Al municipio le mostraría la tabla impresa. 30 s.

## 3. Pantalla

**Escritorio (1440).** Cabecera 64 px: "GOLIAT · Actividad de fuego detectada por satélite" + línea "Cuándo y dónde ha habido fuego en tu comuna…" a la izquierda; "EN" a la derecha; debajo una franja 32 px `--bg` con borde inferior: "No es una alerta. En una emergencia, llama a CONAF o SENAPRED." El resto (≈ 880 px) es mapa a todo el ancho; el mapa es dominante. Sobre el mapa, pegado a su borde superior, una franja 40 px con fondo `--card` al 95 % con el **aviso fijo del mapa** (texto §9 del brief); no se cierra ni se desplaza. Columna flotante izquierda 360 px, margen 16 px, con sombra: arriba el buscador ("Buscar comuna o CUT…", combobox con nombre · región · chip 2002→/2012→); debajo la ficha (vacía al inicio: "Toca una comuna o búscala"). Abajo centrado, sobre el mapa: los chips de temporada en una píldora `--card` y bajo ellos el rótulo (13 px, `--muted`). Abajo a la derecha, dentro del mapa: leyenda de 5 muestras azules §11 (`#C6DBEF … #08519C`) rotuladas "1 · 2 · 3–4 · 5–7 · 8 o más" y un título que cambia con el chip: "temporadas con detección" / "días con detección en 2022-23". Misma rampa, mismos cortes para ambas variables: la distribución lo permite (días por temporada: máximo 19, casi todo 1–2) y la persona no tiene que aprender dos escalas. Los cortes del calendario (1–5 … más de 100) no se usan en el mapa porque el máximo por celda es 30 días en toda la serie. Zoom +/− arriba a la derecha; sin brújula.

**Celular (390).** Cabecera 2 líneas + aviso "No es una alerta". Buscador a ancho completo. Mapa 55 vh con el aviso fijo (dos líneas, 12 px) pegado arriba, leyenda compacta (5 muestras + título) abajo a la izquierda, chips desplazables en la parte baja del mapa y rótulo de una línea. Ficha como hoja inferior: asomada 96 px (nombre + línea de hechos truncada a 2 líneas), al arrastrar sube a 85 vh con perfil, botones y "Ver tabla completa" (abre la matriz a pantalla completa, celdas 26 px, como el brief). El popup de celda es una tarjeta bajo el mapa, no un globo (fácil de leer y de cerrar).

## 4. Salvaguardas de la regla 4

- Celda mínima 0,01° (~1 km) siempre; nunca el píxel de 375 m ni el punto de detección.
- `maxZoom` 12: la celda mide ≈ 30 px, suficiente para tocarla, y positron a ese nivel muestra caminos y localidades, no parcelas; se ocultan las capas de POI del estilo. `minZoom` 6.
- Aviso fijo pegado al mapa en las dos pantallas y en cualquier captura; no se puede cerrar.
- Rampa azul §11, un solo tono por tramo; sin rojo, naranjo ni iconos de llama; las celdas se dibujan al 75 % para que se vea el terreno debajo.
- n = 1 se mantiene en el tono más claro (es el 54 % de las celdas; sacarlo haría parecer que "ahí nunca pasó"), rotulado en la leyenda; en el popup, "1 temporada" sin más.
- Popup sin nombres, sin coordenadas, sin dirección, sin "primera/última fecha" en vista regional: "Sector de ~1 km · {n} temporadas con detección · {d} días". Con comuna cargada se añade "{f} a {l}" (temporadas, no fechas).
- Ningún borde ni etiqueta de predio; los únicos polígonos son las comunas (geoBoundaries/BCN).
- "Compartir" envía la URL y la frase de hechos de la comuna, nunca una celda.

## 5. Factibilidad para el domingo (MapLibre + derived/)

- **Carga.** `region.json` entero al abrir (103 KB gz), una sola fuente GeoJSON con 15.550 polígonos y propiedades planas `n, d, s0…s14` (se aplana al convertir, 1 ms). `comunas.geojson` (273 KB, ya se carga). `comunas/<cut>.json` solo al elegir comuna (ya se hace). `derived/<cut>.json` no hace falta para esta versión.
- **Dibujo por zoom.** z 6–8,9: una capa `circle` sobre centroides (radio 2–3 px) para las 15.550 celdas, porque un polígono de 1 km mide menos de 1 px y se vuelve ruido; z ≥ 9: capa `fill` con los polígonos. MapLibre tesela el GeoJSON en el worker y pinta solo el viewport: a altura de comuna son 300–1.100 polígonos (Santa Bárbara, la mayor, 1.032).
- **Filtro sin recalcular.** Chip "Todas": color `step(get n)`. Chip i: `setFilter([">", ["get","s"+i], 0])` y color `step(get s_i)`. Solo se muestra u oculta lo publicado; ningún número se deriva en el cliente. Si la ficha dice "N sectores con detección en 2022-23", es un conteo de celdas publicadas y pasa por `revisor-cientifico`.
- **Celular.** Peso inicial ≈ 1 MB (MapLibre ~230 KB gz, teselas z6 300–600 KB, datos 180 KB): en 3G rural, 15–25 s. Mitigación: la ficha y el buscador no esperan al mapa; `?cut=` carga primero la ficha; `saveData` → mapa diferido. Probar en un Android real con limitación "Slow 3G".
- **Horas (Rubén + Claude).** Fuente regional y capas circle/fill: 1,5 h · chips, filtro, rótulo y leyenda dinámica: 1,5 h · ficha con piezas existentes (encabezado, línea de hechos, barras) y vista "tabla": 2 h · hoja inferior y columna flotante: 1,5 h · deep link, Compartir, popup táctil: 1 h · prueba en Android y revisión de producto: 1,5 h. **≈ 9 h; versión mínima sin hoja inferior (ficha bajo el mapa) ≈ 6 h.** Corte: funcionalidad cerrada domingo 11:00.
- **No hacer:** teselas vectoriales propias o PMTiles, API o servidor para filtrar, animación con interpolación, modo mes en el mapa, coropleta por comuna (sería un ranking, y la lista va sin cifras), clustering.

## 6. Qué cambia y qué se conserva

**Cambia:** el orden de la página (mapa primero; calendario, barras, método y pie pasan a la ficha y a la vista "tabla"); el aside con lista de 54 se vuelve buscador flotante (mismos ítems y chips); la leyenda del mapa tiene título variable (temporadas / días); aparece el control de temporada y el rótulo con fecha; la rampa roja de `RecurrenceMap.tsx` se reemplaza por los azules §11; el botón "Ver dónde se ha repetido" desaparece y "Ver tabla" pasa a ser primario; se agrega "Compartir"; en Pencil, nuevos componentes `ChipsTemporada`, `RotuloTiempo`, `FichaComuna`, `HojaInferior`, `PopupCelda`.

**Se conserva tal cual:** todos los textos de §2 y §9 (aviso del mapa, línea de hechos B, leyendas, prefijos de usuario, pie y acknowledgement); los 4 estados sin color en la tabla; el A4 sin mapa y los CSV; la rampa Blues de 5 pasos y los tramos de §11 para el calendario; "No es una alerta" antes de cualquier número; n = 1 en el mapa; nada que no venga de `web/public/data/`; mapa solo observado 2012→ (dicho en el rótulo).

## Adenda de la sesión principal (verificación contra los datos)

- El guion usa cifras ilustrativas que no calzan con los datos. Coihueco no concentra en ene–feb–mar: su perfil real (`derived/16302.json`) tiene la mediana más alta en **abril (70) y mayo (43)**. El CUT de Hualqui es **08105**, no 08112 (ese es Hualpén).
- **Hallazgo para el perfil de 12 meses:** en Hualqui la mediana de cada mes es 0 a 2, pero el máximo de enero es 141 y el de febrero 80. La mediana sola dibuja una comuna "sin actividad" donde hubo temporadas muy grandes. El perfil debe mostrar algo más que la mediana (por ejemplo, el máximo o cuántas temporadas tuvieron detección ese mes) o Rosa leerá "aquí no pasa nada".
