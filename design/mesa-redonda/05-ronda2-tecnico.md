# Ronda 2 · Posición del auditor técnico

## 1. Acuerdos
Con 01-usuarios: el orden "comuna → frase de temporada → calendario → leyenda con palabras → no es alerta" en los primeros 10 s; el glosario ("no habilitado" nunca como "sin datos", provisional como "cifras preliminares"); A4 en blanco y negro con corte y fuente al pie; ficha que quepa en una captura de celular. Con 02-problema: calendario primero, temporada segundo, mapa tercero con advertencia fija, método plegable; los tres riesgos de diseño (mapa de culpables, número sin estado, afordancia de alerta) son exactamente lo que veo frágil en el CSS actual.

## 2. Qué no es factible hoy y la alternativa

| Propuesta | Problema | Factible hoy | Pedir a Daniel (`ciencia`) |
|---|---|---|---|
| Fila "Mediana 2012–2026" bajo el calendario / resaltar 3 meses más altos / leer celda como anomalía (02 §4, revisión ajuste 1) | No existe mediana por mes en `series` ni en `season_compare`; calcularla en la web viola la regla | Mostrar la fila "Σ temporada" que ya existe y confiar en la rampa para que el ojo vea los meses altos | Campo `month_climatology[]` por mes: `median, p25, p75` (observado 2012→), y opcional `rank` por celda |
| "hasta el [corte], X detecciones, vs. Y habitual a esta fecha" (01 §5) | Ninguno | Sí: `season_compare.current`, `.median`, `.cutoff_day`, `.months`, `doc.cutoff`, `.n` | — |
| Guardia de temporada temprana (≤ noviembre o mediana < 10) | El umbral es una regla de presentación, no un número nuevo; la decisión de si "noviembre es temprano" la tomo yo en la web | Aceptable como regla de texto (no produce cifra), pero que Daniel la apruebe como texto del método | Idealmente `season_compare.verdict_ok: boolean` para que el criterio viva en el pipeline |
| Veredicto "sobre el p75/p90" | Hoy se calcula en la web (SeasonCompare.tsx:11-13); es una comparación, no un número nuevo, pero el p90 débil se cuela como etiqueta | Mostrar current y mediana juntos sin etiqueta de percentil; p25–p75 como franja gris en las barras | — |
| "Comunas vecinas" (01 §5) | No hay adyacencia en el JSON | El mapa ya permite clic en la comuna vecina (RecurrenceMap.tsx:27); basta un texto que lo diga | `neighbors[]` en index.json si se quiere lista |
| Cobertura observacional / "nublado" | No existe | Solo el texto fijo "un mes con 0 puede ser nublado" | Fuera de alcance al domingo |
| Plataforma en tooltip (P12) | Ninguno | `series[].sat` ya viene | — |
| Mapa que atenúe n = 1 | Ninguno | Cambiar la rampa en el cliente (presentación) | — |
| Texto de usuario, acknowledgement FIRMS, títulos bilingües | Ninguno | Solo i18n | — |

## 3. Layout

**Escritorio 1280–1440.** Dos columnas: izquierda 280 px fija (buscador + lista de 54 con nombre, "2012→ / 2002→" y mini-cifra `current`/`median` del index); derecha 1 columna de 920–1040 px. Orden: (1) encabezado de comuna 72 px: nombre, región/CUT, chip de serie, "Datos hasta 13-11-2026"; (2) frase de temporada 110 px: una línea grande "Hasta el 13-nov: 12 detecciones · lo habitual a esta fecha: 43 (14 temporadas)" + barras 60 px con franja p25–p75; (3) calendario ≈ 25 × 28 px + cabecera + leyenda = 820 px, con un separador horizontal entre 2012-13 y 2011-12 (frontera observado/estimado) y la leyenda pegada; (4) mapa 420 px + texto fijo; (5) método plegado (una línea con 3 cifras clave visibles: "Aqua ≥ 50 ✓ · gana a climatología 8/8 ✓ · gana a Aqua crudo 7/8 ✓"); (6) pie: disclaimer, fuentes, botones CSV/imprimir/ES-EN también aquí. Nada "above the fold" depende del mapa.

**Celular 390.** Una columna. Buscador arriba (combobox, no lista); encabezado; frase de temporada (barras ocultas tras "ver temporadas"); calendario con 12 columnas de 26 px (390 − 32 − etiqueta 48 = 310/12), celdas sin número bajo 600 px, número en tooltip/tap y fila Σ siempre visible; las 25 filas se muestran completas (650 px) porque es el dato; mapa 300 px plegado por defecto ("ver mapa"); método y pie plegados. Botones en barra inferior fija de 48 px: CSV · Imprimir · EN.

**A4 impresión.** Portrait, márgenes 15 mm. Cabecera: GOLIAT, comuna, "Datos hasta", para quién es. Bloque 1: frase de temporada + tabla de 14 temporadas en texto (no barras). Bloque 2: calendario completo con celdas 36 × 18 px, números siempre, tramas en vez de color, leyenda textual. Página 2: mapa 110 mm con leyenda y texto fijo, compuertas de la comuna en 3 líneas, método resumido, fuentes, acknowledgement, URL con `?cut=`. Sin aside ni botones.

## 4. Sistema visual
Fondo #FCFBF7, texto #1A1A1A, gris #5F5F5F, acento azul-verde #1F6F8B (conserva el actual), nunca rojo como semáforo. Rampa del calendario: viridis 6 pasos (ya es segura para daltónicos y monótona en luminancia, por eso sobrevive en gris). Mapa: una rampa secuencial morado-negra (`#cbc9e2 → #3f007d`) en vez de rojos para alejar la lectura "peligro". Tipografía: **IBM Plex Sans** (texto) + **IBM Plex Mono** o `font-variant-numeric: tabular-nums` de Plex Sans para cifras; alternativa **Inter** con `tnum`. Plex tiene cursiva real distinta de la romana, útil para el estimado.

Glifos/tramas (visibles sin color y en B/N): observado = celda lisa, número romano; estimado = trama diagonal 45° gruesa (4/8 px) + número en cursiva + "±" al lado en pantalla ancha ("8 ±3"); no habilitado = celda blanca con borde punteado y "∅" gris; provisional = borde continuo grueso del acento + punto "•" tras el número ("4•"), nunca naranjo (hoy comparte --warn con "no habilitada"). Mes incompleto = "4…" (ya existe).

## 5. Componentes en Pencil
`Chip` (serie 2012→ gris / 2002→ azul / provisional); `CeldaCalendario` en 4 variantes × 2 tamaños (escritorio 28 px, celular 26 px, impresión 18 px) con número opcional; `FilaTemporada` (etiqueta + 12 celdas + Σ); `Leyenda` (horizontal y vertical, con texto); `KPIFrase` (cifra grande + comparación + fecha, variante compacta para celular); `Barras14` con franja p25–p75; `EncabezadoComuna`; `Boton` (primario/secundario/enlace) y `BarraAcciones` (escritorio y fija inferior); `CajaAdvertencia` (disclaimer, texto fijo del mapa); `PanelPlegable` (método); `ItemComuna` de la lista. Todo con tokens CSS nombrados igual que App.css (`--bg --fg --muted --accent --line`) para traducir 1:1.

## 6. Veto y conservación
**Veto:** cualquier fila o resaltado de "meses más altos / mediana por mes" calculado en la web antes de que exista el campo en el JSON; se diseña el hueco y se activa cuando Daniel lo publique. **Conservo sí o sí:** la celda de calendario con los tres estados + provisional distinguibles por trama y glifo, la frase de temporada con fecha de corte y n = 14, y el "no es alerta" arriba, no al pie.
