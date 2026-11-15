# Estudio33: etiquetas registradas sobre puntos nominales fijos

**Pase estructural confirmado por revisión independiente.** Se enriquecieron397608 filas de las16 cohortes/políticas prefijadas, conservando propietarios y población32A. El resultado describe la **etiqueta nativa del quad nominal asignado al punto de consulta**. No mide actividad física en la coordenada, área, número de incendios, superioridad de sensores o oportunidad física comparable.30B continuo sigue fallido; G1 sigue falso y el modelo mensual no cambió.

Protocolo `c6b5285`, precisión previa a datos `755b68e` (SHA `e51c135d30fc655718cae2d9e0127f9e8f7d700c74670ce72c54e0c5fe9c5c16`). Cap absoluto06:48–07:48UTC del15 de noviembre2026, incluida revisión. Código SHA `63111ebf3f927310bb4299157767dbed09b2a356441857bf41bfa8c8be540553`; freeze SHA `31c7f8017050f022e5f2b1306057dd3625d9723259403678cb01d24bc5800cc3`, emitido antes de leer etiquetas. Ejecución terminada aproximadamente07:03UTC; revisión independiente completa recibida antes de07:10UTC. Sin nuevos datos, HDF, geometrías continuas, refit, dependencias o publicación.

## Qué se comparó y qué permaneció fijo

Dos casos,2019-01-03 y2023-02-10; fases0/125m diagonales, pasos250/500m y prioridadesearly/late. Son ocho escenarios por caso, **16 en total**. Primaria por caso: fase0,250m,early. Se conservan todos los puntos, incluidos propietarios ausentes o máscaras desconocidas; ninguna cohorte se restringió a positivos, QA nominal o ambos sensores presentes.

Los85000+ registros de etiquetas son universales **para el universoCORE incluido documentado**, no todos los píxeles de los granules. Exactamente85451 IDs nativos debían estar presentes: todos estuvieron, sin duplicados, y su proyección nativa coincidió con ambas exportaciones históricasearly/late. Un ID esperado faltante habría bloqueado, sin convertirlo enU ni completarlo con el catálogo positivo. Las etiquetas se unieron porcaso/producto/fila/columna con versión/archivo/shape en los manifests, no por cercanía.

La máscara base conserva7/8/9 como1,3/5 como0 registrado y el resto comoU con causa. QA y superficie son ejes separados. Hash de la proyecciónGEO antes/después idéntico en cada escenario; puntos compartidos500/250 conservan propietarios, causas, máscara, QA, superficie y referencias. Los scopes/propietarios no se reconstruyeron mirando etiquetas.

Un quad grande puede asociar su etiqueta a muchos puntos y otro a pocos. En2023, cuatro positivos nativos Aqua representados producen162 puntos positivos, mientras16 nativosVIIRS producen45. **162 frente45 no clasifica capacidad de detección o sensibilidad**, ni representa162/45 incendios: cuenta asociaciones de etiquetas a esta grilla nominal. Tampoco16 frente4 identifica incendios independientes.

## Resultados primarios, con todos los desconocidos

Primer símboloMODIS, segundoVIIRS.00/10/01/11 describen etiquetas conocidas;0U/1U/U0/U1/UU conservan al menos un desconocido. UU no se llama acuerdo. Cada fila siguiente cierra exactamente con39601 puntos.

| Caso |00|10|01|11|0U|1U|U0|U1|UU|Total|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|2019, primaria|32179|0|0|0|1081|0|6026|0|315|39601|
|2023, primaria|39396|135|18|27|25|0|0|0|0|39601|

2019 no tiene unión positiva conocida en estos puntos: Jaccard secundario **null**, no0/1 ni prueba de sensibilidad. Sus cuatro positivos nativosVIIRS con centro en el halo siguen íntegros en el catálogo, sin incidencias interiores en las cohortes de puntos. “No positivo representado” no los borra ni demuestra ausencia física.

2023 tieneNconocido39576 yNtotal39601;25 puntos conservanU. Jaccard conocido es27/(27+135+18)=**0.15**, secundario y condicional a las etiquetas conocidas de este operador. No es precisión/recall físico, truth, armonización lograda o porcentaje causal de desacuerdo eliminado. La predominancia00 tampoco constituye éxito de detección.

## Sensibilidades prefijadas y selección nativa

Todos los escenarios están en `summary.json` y sus tablas completas. En estos dos casos early/late producen iguales vectores de estados; eso no significa que todos losownerIDs sean iguales ni acredita estabilidad fuera de estas escenas. Las fases tienen poblaciones diferentes y no son un experimento causal.

|2023, ambas prioridades|Ntotal|10|01|11|U agregado|Jaccard conocido|VIIRS nativosAOI conowner /16|
|---|---:|---:|---:|---:|---:|---:|---:|
|fase0,250m|39601|135|18|27|25|0.150000|16|
|fase0,500m|9801|37|6|6|6|0.122449|12|
|fase125,250m|40000|145|19|23|24|0.122995|16|
|fase125,500m|10000|32|5|5|5|0.119048|10|

No se selecciona0.15 por ser mayor. La pérdida de representación nativa a500m está explícita: cuatro o seis de los16 positivosVIIRS centroAOI no contienen una consulta estrictamente interior de esa grilla. No pasan a no detección, y una mayor densidad de puntos no es una validación física.

Aqua conserva cuatro positivos centroAOI conowner en todos los escenarios y **dos positivos de borde sinquad con geometríaNULL**, de seis originales. Permanecen en el catálogo y la partición de retención, con counts geométricos no identificados comoNULL, nunca0. No se fabricaron footprints ni tomaron vecinos para rescatarlos.

Los catálogos completos conservan60/132 positivos nativosAqua/VIIRS en2019 y177/908 en2023, separados por centroAOI/halo/exterior/no asignable. Prepropiedad usa **STRICT_INTERIOR**, no bboxcandidates; frontera se cuenta aparte. El roster y retención distinguen: sinquad,quad fuera de universo,quad incluido sin punto interior,interiores sinownership yowner representado. Muchos registros exteriores no pueden resumirse como un porcentaje de fuego perdido enAOI.

## QA y superficie: diagnósticos, sin borrar positivos

El tierQA deriva del screen previo verificado contra los campos crudos y decoder congelado. Sus exclusiones incluyen máscaras de nube/glint/no procesado además de flags de calidad: **no es una partición pura de defectos instrumentales**. MODISM13 es `not_applicable`. Una exclusión verificable oM13 verdadero esnon_nominal; incompletitud/no verificación/unresolved sin no nominalidad conocida permaneceunknown. La máscara primaria no cambia.

Sobre la misma primaria2023:

| Tier delscreen/campos inspeccionados |Ntotal|00|10|01|11|0U|Jaccard conocido secundario|
|---|---:|---:|---:|---:|---:|---:|---:|
|both_nominal_in_inspected_fields|39541|39389|129|12|11|0|0.072368|
|some_non_nominal|38|7|6|6|16|3|0.571429|
|QA_unknown|22|0|0|0|0|22|null|

Los otros estadosU de esta tabla son0 y permanecen en el esquema. La diferencia entre tiers no demuestra que un screen mejore o empeore una medición: cambia la composición de etiquetas observadas. No se escogió el tier que maximizaJaccard. Los162/45 positivos de puntos permanecen en la primaria sin filtroQA.

Un conteo descriptivo delCSV primario confirma que ocho de los16 IDs nativosVIIRS representados tienenM13 no nominal y sus22 puntos siguen siendo1; los otros ochoIDs aportan23 puntos positivos. No se descartó clase7. `Suspect` globalMODIS se conserva por separado, sin inventarPassed o trasladar reglasL1B.

La superficie nativa exportada se conserva literalmente, sin inferir tierra por positividad ni copiar el otro instrumento. La fuente24B usaba `VNP03IMG/geolocation_data/land_water_mask` si estaba disponible y un fallback nativo enotrocaso. Las etiquetasplainland/water/coast se interpretan conforme esa rama del código congelado; el nuevo replay **no reabrióGEO** y el valorland_water crudo no estaba exportado. Su provenance histórica es condicional y explícita, no una nueva inspección del auxiliar. En la primaria2023, los45 puntos positivosVIIRS tienen superficie exportadaland; no se afirmó que todos fueran desconocidos. La primaria conserva también cualquier superficieunknown.

## Tiempo y límites de identificación

Cada fila usa sus propios scans propietarios y las referencias originales MODIS EVstart/EVcenter yVIIRS scan_start/scan_end/ev_mid. `summary.json` conserva atributos/unidades originales, fuenteREF yvalidación. La escala documentada esTAI93; delta esev_midVIIRS−EVcenterMODIS ensegundos, conNULL/causa si falta propietario/referencia. No se reutilizaronnearest-centertimes ni se seleccionó una ventana para mejorar acuerdo.

Son referencias de scan, **no instantes o intervalos de exposición por píxel**. El cambio real entrepasadas y la respuesta instrumental siguen mezclados. No hay evidencia aquí para atribuir135/18 discordancias a un sensor equivocado, nubes, omisiones o evolución del fuego.

## Auditoría y reproducibilidad

La revisión independiente pasó sobre las898704 filas:397608 puntos,85451 proyecciones nativas,404152 roster,10216 retención y1277 proyecciones de catálogo. Su implementación propia comprobó16 escenarios, nueveestados, QA desde bits, superficie, tiempos, hashesGEO, rosterestricto, catálogos y nested, sin usar el helper del autor,GEOS oHDF. Ver dictamen separado `2026-11-15-discrete-state-comparison-independent-review.md` y su evidencia propia.

Los nueve tests puros cubren positivos7–9/M13,null/U,expectedIDfaltante como fallo, superficie real/unknown,QA incompleta/exclusión no verificable,Jaccardnull, retención estricta/noquad/outside yGEO invariante frente a cambiar etiquetas. Helpers/tests no leen runtime oclock. Los campos fuera deallowlist sólo se tokenizan transitoriamente al leerCSV y se descartan: no se retienen ni interpretan semántica/numéricamente, conforme la precisión predata755b68e. No se usó ningún campo de área continuo.

El presupuesto cerró con1,381,763 búsquedas nativas, picoRSS213385216 bytes enmacOS y aproximadamente8.23MB de salida, bajo los caps2Mjoins/2GiB/200MiB. Las898704 filas incluyen todos los productos auxiliares y quedan bajo1M. SHA de inputs, tests, código ydecoder protegidos antes/después. Sin corrección o rerun tras resultados.

Proyeccionesallowlist universales ycatálogos están publicados en la evidencia para permitir verificación independiente desde unclone sin losCSV privados completos. El driver original **todavía requiere sus fuentes locales congeladas y su cap absoluto**: no se afirma un replayoffline completo e ilimitado que no fue implementado/probado. La proyección conserva elSHA original y su propioSHA/provenance en freeze/manifest; no incluye áreas,coords nativas innecesarias o secretos.

Comandos del intento:

```sh
.venv/bin/python -m unittest discover -s tests -p test_discrete_state_comparison.py
.venv/bin/python pipeline/discrete_state_comparison.py freeze
.venv/bin/python pipeline/discrete_state_comparison.py run
```

El programa rechaza sobrescribir el intento. Una reproducción posterior necesita protocolo/cap nuevo documentado; no modificar el reloj para eludir el fin original. Se priorizaron tablas revisables; no se añadió un mapa nuevo ni se publicaron productos operativos.

## Decisión

33 acredita integridad y una descripción reproducible de etiquetas bajo un operador nominal discreto prefijado. Expone el coste de bordes y muestreo, y conserva calidad/tiempo/superficie como ejes interpretativos. **No demuestra comparabilidad física, no armoniza cantidadesMODIS–VIIRS ni mejora el modelo mensual.** Dos casos y sensibilidades de sus mismos registros no sonholdouts nuevos o muestrasIID. G1físico y la pregunta causal original permanecen abiertos; el operador continuo30B conserva su resultado negativo.
