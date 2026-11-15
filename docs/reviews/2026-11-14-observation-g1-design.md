# Diseño G1: soporte observado común antes de comparar actividad

Fecha: 14 de noviembre de 2026. Investigación documental y propuesta de protocolo; **no ejecuta G1**, no calcula concordancia de fuego y no incorpora variables observacionales al modelo mensual. Los resultados autenticados anteriores permanecen intactos.

La adquisición ya probó acceso, lectura de máscaras completas, dimensiones y correspondencia exacta de `InputPointer`. Eso permite desarrollar un decodificador. No demuestra todavía una superficie común observada con calidad aceptable. G1 permanece pendiente.

## Fuentes primarias y alcance de versión

1. [Equipo MODIS: guía C6 y C6.1, v1.0, mayo de 2021](https://modis-fire.umd.edu/files/MODIS_C6_C6.1_Fire_User_Guide_1.0.pdf), §§2.1, 5.1 y tabla 4, pp.22–23. El [índice del equipo](https://modis-fire.umd.edu/guides.html) enlaza esta versión. La guía declara que C6.1 no cambió el algoritmo ni el formato del producto de fuego respecto de C6; sí cambió la calibración de entrada.
2. [NASA: guía VIIRS 375 m Collection 2, v1.0, mayo de 2024](https://www.earthdata.nasa.gov/s3fs-public/2024-07/VIIRS_C2_AF-375m_User_Guide_1.0.pdf), §3.1, tablas 1–2, pp.3–5. Se recuperó el PDF público mediante `curl` con validación TLS; el lector web recibió 403. No sustituirla por la guía VIIRS 750 m.
3. [LAADS: especificación MOD03/MYD03 en ruta Collection 61](https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/61/MOD03), §§3.1 y 3.3. El documento servido se identifica internamente como formato versión 6.0.3, junio de 2012, e incluye ejemplos Collection 006. Se usa para interpretar campos coincidentes, dejando explícita esa antigüedad. La página genérica actual de MYD03 describe Collection 7 y no debe reemplazarla.
4. [LAADS: VNP03IMG Collection 2](https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP03IMG), DOI `10.5067/VIIRS/VNP03IMG.002`, ArchiveSet 5200. La [especificación antigua Collection 1](https://ladsweb.modaps.eosdis.nasa.gov/filespec/VIIRS/1/VNP03IMG.fs) sirve como referencia de nombres, no como prueba de continuidad de todos los bits C2. Para los cuatro indicadores de calidad geográfica se dispone además de atributos explícitos del archivo C2 realmente adquirido, guardados en la inspección autenticada.
5. [NASA: guía L1 VIIRS, julio de 2017, §4.3](https://oceandata.sci.gsfc.nasa.gov/files/resources/docs/technical/VIIRS_Level-1_DataProductUsersGuide.pdf): define tiempos por escaneo TAI93. Es una referencia histórica, no una certificación integral del esquema C2. El enlace de LAADS a la guía L1B de agosto de 2021 devolvió una transferencia parcial o inválida que `pdftotext` no pudo leer; se registra como evidencia fallida y no se atribuyen definiciones a ese documento.
6. [NASA: aclaración del equipo de geolocalización MODIS sobre EV Start Time](https://atmosphere-imager.gsfc.nasa.gov/issues/cloud): tiempo TAI con origen en 1993 y ajuste por segundos intercalares; el nombre del archivo es UTC aproximado. [NASA SDP Toolkit, herramientas de tiempo](https://wiki.earthdata.nasa.gov/spaces/DAS/pages/172919502/SDP%2BToolkit%2BPrimer%2Bfor%2Bthe%2BECS%2BProject) proporciona la referencia de conversión, no una autorización para tratar TAI93 como Unix.

Los PDF se leyeron temporalmente fuera del repositorio. `evidence/observation-g1-design/sources.json` conserva URL, tamaño y hash; no se guardaron PDF ni credenciales. Las definiciones siguientes son paráfrasis técnicas.

## Máscara de clasificación y QA son campos distintos

### MYD14 C6.1

La máscara `fire mask` distingue: 0 entrada ausente; 1–2 categorías obsoletas/no procesadas según la leyenda nativa; 3 agua sin fuego detectado; 4 nube; 5 tierra sin fuego detectado; 6 resultado desconocido; 7–9 detección con confianza baja, nominal y alta. Cualquier clase no reconocida se conserva como desconocida y se excluye de elegibilidad.

En `algorithm QA` (uint32), numerando desde el bit menos significativo:

| Bits | Significado confirmado por guía C6/C6.1, tabla 4 |
| --- | --- |
| 0–1 | Superficie: 0 agua, 1 costa, 2 tierra, 3 sin uso |
| 2 | Selección banda 21/22 |
| 3 | Corrección atmosférica aplicada |
| 4 | Algoritmo nocturno/diurno |
| 5 | Candidato potencial a fuego |
| 6, 17–19, 29–31 | Reservados |
| 7–10 | Parámetro de tamaño de ventana de fondo |
| 11–16 | Resultados de pruebas de detección |
| 20 | Nube adyacente |
| 21 | Agua adyacente |
| 22–23 | Nivel de reflejo solar |
| 24–28 | Indicadores de pruebas de rechazo |

**Corrección decisiva:** los bits 0–1 de este producto no son los antiguos bits MODLAND de confianza. Una búsqueda puede devolver especificaciones C4/C5 con otro significado. Tampoco puede usarse `QA == 0` como regla de buena calidad: cero representa agua en esos dos bits y otras pruebas tienen significados distintos. No se reconstruyen aquí los umbrales de cada prueba 11–16 o 24–28; requieren la especificación L2 correcta o el ATBD antes de utilizarlos como filtros.

### VNP14IMG C2

`fire mask`: 0 sin procesar; 1 eliminado por bowtie; 2 reflejo solar; 3 agua; 4 nube; 5 tierra; 6 sin clasificación; 7–9 detecciones de confianza creciente. Aquí **clase 1 de la máscara** significa bowtie eliminado y no debe confundirse con **bit 1 del QA**, que informa calidad de I2.

| Bits QA | Significado confirmado en guía C2, tabla 2 |
| --- | --- |
| 0, 1, 2 | Calidad I1, I2, I3; cero nominal o nocturno |
| 3, 4 | Calidad I4, I5; cero nominal |
| 5 | Calidad de geolocalización de entrada; cero nominal |
| 6 | Calidad M13; cero nominal |
| 7 | Detección inequívoca nocturna |
| 8 | Candidato para fondo |
| 9 | Rechazo por brillo |
| 10 | Candidato a fuego |
| 11 | Fondo de escena |
| 12–15 | Pruebas contextuales 1–4 |
| 16 | Saturación |
| 17 | Condición de reflejo solar |
| 18 | Posible anomalía magnética del Atlántico Sur |
| 19 | Detección sobre agua |
| 20–21 | Pruebas de persistencia |
| 22 | Bowtie residual |
| 23–31 | Reservados |

La tabla permite interpretar qué describe cada bit; no todos son fallos de calidad. Por ejemplo, saturación puede acompañar una detección de alta confianza. La guía advierte que el bowtie residual puede duplicar FRP. Propuesta conservadora del piloto: excluir bit 22 del soporte analítico y cuantificar esa exclusión por separado, sin afirmar que NASA exige excluirlo para cualquier aplicación. Mantener los bits 18–21 visibles para revisar actividad sobre agua y anomalías; no convertirlos automáticamente en ausencia de fuego.

## Geolocalización y tiempo: confirmado y pendiente

| Producto | Confirmado | Pendiente antes de G1 |
| --- | --- | --- |
| MYD03 061 | Coordenadas de centros; diez filas de 1 km por escaneo; `EV start time` TAI por escaneo, relleno −2e9. `gflags`: bit7 entrada inválida, 6 sin intersección elipsoidal, 5 terreno inválido, 4 DEM ausente/de calidad inferior, 3 rango inválido, 2 limbo >85°. | Confirmar continuidad de los detalles de formato 6.0.3 con el granule 061 y significado de bits bajos no descritos. No interpretar `EV center time` como tiempo de cada píxel. |
| VNP03IMG 002 | Archivo leído: `quality_flag` masks 1/2/4/8 = entrada inválida, apuntado malo, terreno malo, ángulo solar malo. `scan_start_time`, `scan_end_time`, `ev_mid_time` con `long_name` TAI93. Guía C2 de fuego: 32 filas de I-band por escaneo. | Verificar semántica de inicio/fin exacta, flags a nivel de escaneo C2 y límites de exposición por muestra. Los atributos del archivo no certifican que todo escaneo esté sano. |

Reglas propuestas de geolocalización, separadas de la máscara: coordenadas finitas y dentro de rango, rellenos excluidos; MYD03 `gflags == 0` como restricción conservadora explícita del piloto mientras los bits restantes no se documenten; VNP03IMG `(quality_flag & 15) == 0`, además de rechazar rellenos y cualquier bit desconocido activo. Estas reglas son decisiones de diseño, no una equivalencia entre los QA de los dos sensores.

Los intervalos de catálogo 18:40–18:45 y 18:36–18:42 UTC solo permiten una diferencia potencial de 0–9 minutos; no constituyen tiempos de la zona piloto. Primero asignar fila a escaneo mediante `row // 10` y `row // 32`, validando divisibilidad y dimensiones. Luego convertir TAI93 con una implementación que trate su época y los segundos intercalares; contrastar varios escaneos con límites UTC del granule. **No restar mecánicamente 37 segundos ni interpretar los valores como segundos Unix.**

Después se necesita un intervalo temporal conservador para cada muestra: inicio/fin de la porción Earth-view y desplazamiento dentro del escaneo. Los campos de escaneo disponibles no demuestran por sí solos tiempo exacto por píxel. No se extrapola el último escaneo ni se interpola cruzando escaneos sin documentación. Conservar incertidumbre residual de exposición y geolocalización; si no puede acotarse, el emparejamiento queda `time_unknown`.

## Estados propuestos: observado sin detección no significa ausencia física

La unidad futura debe ser una porción espacial común y una pareja de oportunidades temporales, no un par elegido por coincidencia positiva.

1. **Observación no utilizable:** clase 0/4/6 en MODIS; clase 0/1/2/4/6 en VIIRS, fallo de geolocalización o de entradas, ausencia de producto, tiempo desconocido o cobertura espacial no demostrada. Preservar la causa. No rellenar con cero.
2. **Observación utilizable sin detección registrada:** MODIS clase 5 sobre tierra o clase 3 sobre agua; VIIRS clase 5 sobre tierra o clase 3 sobre agua, superando reglas QA/geográficas/temporales predefinidas. Solo es una condición instrumental de la observación; persisten límites por tamaño, humo y sensibilidad. No equivale a incendio ausente.
3. **Observación utilizable con detección:** clases 7–9 que superen las mismas reglas de calidad de entrada y soporte. Confianza es una dimensión adicional. Las detecciones de baja confianza siguen siendo detecciones en la clasificación principal; no se convertirán en ceros para mejorar concordancia. Una sensibilidad nominal/alta deberá marcar las bajas como ambiguas/excluidas.

Para VIIRS, el filtro conservador propuesto de entradas es `(algorithm_QA & 127) == 0` y bowtie residual ausente; no implica que cada bit de pruebas contextuales deba ser cero. Para MODIS se usan las clases finales y geolocalización; los bits de superficie, día/noche y reflejo solar se decodifican, pero no se inventa una bandera binaria de calidad de entrada que su QA no contiene. El valor de reflejo solar no se convierte en umbral sin documentación adicional. El denominador resultante debe llamarse **soporte compatible con la política QA declarada**, no oportunidad completa de detectar cualquier fuego.

Mantener tierra, agua y costa como estratos separados. Para una comparación terrestre primaria, proponer tierra en ambos productos: MODIS bits 0–1 = 2 y VNP03IMG `land_water_mask = 1`, con coherencia de clases y máscaras comprobada. Costa, desacuerdo de superficies y agua se reportan como exclusiones o análisis separado; no se reetiquetan como tierra. La elección del soporte no depende de si uno o ambos detectaron fuego.

## Protocolo G1 que falta congelar

**Pregunta:** en la geometría y ventanas temporales predeclaradas, ¿qué superficie tiene observación comparable de ambos instrumentos y qué fracción de su desacuerdo se asocia descriptivamente a las exclusiones por observabilidad? Un único par sirve para validar ingeniería y estudiar un caso, no para estimar una corrección universal o atribuir causalidad.

- Mantener región y fechas del preflight. El rectángulo geográfico consultado es una envolvente conservadora; si la unidad se describe como 50×50 km, definir el cuadrado métrico exacto, por ejemplo en UTM 18S centrado en 37°S, 72.5°W, antes de ejecutar. No confundirlo con la envolvente ni seleccionar la región por detecciones.
- Congelar geometría y construcción del soporte antes de abrir resultados de fuego. Las coordenadas son centros: ni su caja envolvente ni la unión de círculos de radio nominal demuestran footprints. La relación 1 km/375 m no es un factor de equivalencia física. Una cuadrícula común facilita indexar, pero no prueba cobertura común.
- Rama científica preferida: footprints derivados con método geodésico documentado, correcciones de borde/escaneo y control de solapamientos. Usar intersección de soportes QA válidos y una operación de unión para evitar doble conteo. Aproximar esquinas con vecinos, especialmente al borde de escaneo o bowtie, exige validación y análisis de sensibilidad; no llamarlo exacto.
- Rama técnica posible: correspondencias entre centros con distancia umbral fijada y resolución original conservada. Reportarlas únicamente como asociaciones entre centros; no publicar porcentajes de superficie observada ni resultados de armonización con ese denominador. No declarar G1 científico superado con esta rama.
- Para el emparejamiento temporal, proponer ventana primaria ≤10 minutos basada en extremos conservadores de exposición del soporte común. Tratar como inciertos los casos cuyo máximo exceda el umbral aunque el mínimo no lo exceda. Ventanas 5/15 minutos serían sensibilidades predeclaradas, no una búsqueda de la mejor concordancia. Esa ventana no garantiza estabilidad del incendio.
- Construir inventario de exclusiones QA/geolocalización/tiempo/agua/costa sin usar la clase positiva para aceptar casos. La máscara clasifica posteriormente el soporte aprobado. No exigir que ambos sensores estén en clase no fuego para crear el denominador.
- Congelar reglas sobre deduplicación, ponderación por superficie, confianza y días antes de calcular concordancia. Incluir todos los estados, incluidos ambos sin detección; conservar por separado no-observación. No dividir cantidades por la fracción despejada como corrección automática.
- Comparación posterior, solo tras protocolo aprobado: diferencias emparejadas sobre idéntico soporte, con desglose de exclusiones. La versión sin filtros y la versión con calidad no deben compararse como si tuvieran el mismo denominador. No atribuir toda reducción de desacuerdo a corregir sensores: cambió la población observable.

## Flag global Suspect y bloqueo mínimo

El MYD14 adquirido declara `AUTOMATICQUALITYFLAG = Suspect` y explicación `not being investigated`. Se conserva literalmente en evidencia; ni las guías recuperadas ni esa explicación resuelven la causa. No significa automáticamente que cada píxel sea inválido, pero tampoco habilita omitir el flag. Para una prueba técnica puede usarse en cuarentena claramente etiquetada. Para acreditar G1 científico con este único caso, exigir interpretación específica del flag por documentación del producto/procesado; si sigue sin resolverse, declarar elegibilidad global pendiente. No buscar otro granule después de observar su actividad para eludirlo.

**Bloqueo mínimo concreto:** falta un soporte espacial común defendible, tiempos de exposición comparables con incertidumbre acotada y política QA validada por versión, incluida la elegibilidad del flag global. Ninguna mejora del MAE mensual ni la existencia de cuatro archivos resuelve estos tres requisitos.

Siguiente entrega factible antes de UTC03: un **decodificador puro**, sin datos reales ni puntuación de fuego, con tablas versionadas y pruebas sintéticas: extracción de campos de superficie MODIS; contraste con el mapeo antiguo erróneo; máscaras VIIRS 0–6 frente a pruebas 7–22; distinción máscara1/QA bit1; rellenos; rechazo de versiones desconocidas; separaciones agua/tierra/costa; estados desconocidos; propagación de fallos geográficos y de tiempo. Su éxito acreditaría software de decodificación, no G1. Esta entrega se propone aquí y no se ejecuta bajo este documento.
