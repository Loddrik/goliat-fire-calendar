# Diseño propuesto25 — estados de operadores nominales sobre soporte explícito

**Diseño para revisión y autorización posterior; no se ejecutaron emparejamientos, tablas cruzadas ni nuevas métricas.** Depende del ledger24B y no presupone que sus identidades o su soporte resulten suficientes. No modifica24C, E ni resultados anteriores. G1 físico permanece false; esto puede ser un experimento descriptivo condicional de operadores nominales, no una certificación de oportunidad física.

## Pregunta, estimando y primera decisión

Pregunta acotada: ¿cómo se distribuyen los estados registrados MODIS/VIIRS sobre la intersección de sus operadores geométricos nominales, y cuánto cambia esa descripción bajo decisiones geométricas prefijadas? No responde todavía qué fracción del desacuerdo original se debe a oportunidades físicas diferentes de observación.

Unidad descriptiva: **área de un átomo de intersección con dos propietarios nativos identificados**, en m² EPSG:32718. No es incendio, píxel independiente, área quemada, footprint óptico/PSF ni ubicación de fuego dentro de un píxel positivo. Dos fechas son dos casos, nunca miles de réplicas independientes por contar átomos vecinos. Se informa cada caso por separado, sin promedio que haga dominar el caso mayor o sin positivos.

Primaria recomendada: vector exhaustivo de áreas `(A00,A10,A01,A11,AU)` sobre soporte nominal común identificado, más su desagregación9estados y denominadores geométricos. Publicar áreas absolutas y fracciones con denominador visible, no optimizar una puntuación de acuerdo. Diferencia nominal10/01 no se llama error, falso positivo o sensibilidad. Las referencias13VIIRS del mismo scan2023 son comprobación dimensional selectiva, no tamaño muestral de validación.

Primera entrega posterior a autorización: artefacto reproducible con gates, ledger de soporte, tabla de estados y sensibilidades completas o resultado bloqueado. Fijar cap temporal y límites numéricos de complejidad de overlay/filas/salida antes del run; si se exceden, resource_limit sin aproximación escogida por resultado; no iniciar la parte de estados mientras24B siga pendiente. No downloads, nuevos casos, hiperparámetros o cambios de producción.

## Entradas, dominio y gates antes de clases conjuntas

Heredar exactamente24B: casos2019-01-03 y2023-02-10; AOI50×50km centrada en(-72.5,-37), EPSG:32718; halo15km, ocho originales FIRE/GEO ya adquiridos e índices SHA; mallaCORE, reglas de transiciones y flags geométricos sin cambios. La población incluye polígonos CORE que intersectan AOI aunque su centro esté fuera. No añadir vecinos para reemplazar geometría ausente.

Antes de nuevas tablas de estados:

1. Congelar protocolo, código, hashes de entradas, decoder versionado y resultados24B. Validar InputPointer/shapes/índices nativos y referencias temporales conforme24B.
2. Exigir balances de unión/propiedad, ausencia de solapamiento material dentro de scan y cierre por área con tolerancia de ingeniería24B de1m². Conservar residuo real, sin `buffer(0)`, reparación o reparto favorable de etiquetas. Si una identidad falla, bloquear la comparación afectada; no ampliar tolerancia.
3. Construir soporte y propietarios usando sólo geometría y referencias de scan, sin clases o QA de fuego. Tiempo desconocido y zona cubierta por scan de orden desconocido conservan la política24B: propiedad no identificada, sin asignar un propietario favorable.
4. Congelar/exportar las tablas geométricas de escenarios, soporte común y controles fijos antes de unir estados. Si sólo un caso o subconjunto es identificable, conservar exactamente ese alcance y el resto como pendiente; no reemplazar el caso.

La elegibilidad global científica MODISSuspect sigue sin resolver. Su descripción se conserva literalmente según evidencia existente; no imponer `Passed` como supuesto requisitoNASA. La cuarentena local es política propia. Este estudio no cambia `scientific_eligibility_certified`, `physical_footprints_verified`, `pixel_exposure_times_verified` ni `gate1_passed`: permanecen false.

## Construcción de átomos y denominadores

Puente con24B: el campo propia_común de24B usa la unión geométrica del otro instrumento y puede incluir soporte con propiedad temporal no identificada. El soporte25 exige dos propietarios identificados: reconstruir UM_identificada∩UV_identificada y cerrar la diferencia respecto de24B con las zonas temporales no identificadas. Nunca reutilizar sin esta reconciliación el denominador24B. Distinguir área de estadoU dentro del soporte25 de área de geometría/tiempo no identificados fuera de ese soporte.

Para cada caso/escenario, sea `P_M(i)` la geometría propia MODIS y `P_V(j)` la propiaVIIRS, tras prioridad exclusivamente geométrica y recorteAOI. El átomo es cada componente no vacía de `P_M(i)∩P_V(j)`, identificado por caso, escenario, ambos índices nativos y componente. No reducir al centro más cercano, replicar el mismo píxel como observación independiente ni interpolar clases. Hereda las dos etiquetas originales: no se asigna fuego sólo a la parte solapada de un píxel.

Exigir que los interiores de átomos sean disjuntos y que su área total reproduzca la intersección de ambas uniones de propiedad identificable. Contactos de área0 se registran como tales y no cuentan como observaciones positivas. Un área desconocida es null, nunca0. Separar área nominal total, áreaAOI, propia, excluida por prioridad, propia común y propia sin soporte del otro.

La AOI se descompone geométricamente en soporte común identificado, soporte identificado sóloMODIS, sóloVIIRS, ninguno y zona de propiedad temporal no identificada. Esta última tiene prioridad en la partición para evitar doble conteo. Fuera del soporte común no existe estado conjunto inventado: se informa como soporte no comparable, con estados individuales disponibles aparte. El vector5estados sólo es exhaustivo **dentro** del soporte común declarado; también se presentan sus áreas divididas por áreaAOI para revelar denominadores que se contraen.

La suma de áreas nativas con solapamiento no sustituye el área de la unión. Las métricas por átomo son ponderadas por área; no por número de fragmentos, que depende del overlay.

## Estados registrados: semántica exhaustiva, sin borrar positivos

Decodificar cada producto/version con helpers existentes, conservando máscara original y causas. Estado básico por instrumento:

| Estado | Regla fijada | Lo que no implica |
|---|---|---|
| `1` | Clases originales7,8,9 | Fuego verdadero, localización subpíxel o oportunidad física equivalente |
| `0` | Clases originales3 o5 | Ausencia física, cielo completamente útil o certeza sobre fuegos pequeños |
| `U` | Nube4, glintVIIRS2, bowtie/no procesado, entradas ausentes, desconocidos6, fill, clase no reconocida o layout de máscara no interpretable | Cero o no detección útil |

Los positivos7–9 permanecen `1` aunque M13 sea no nominal, exista cautela de canal, screen local excluido o flag global pendiente. Los ejes QA se conservan aparte; no sobreescriben el hecho de detección registrada. Las clases3/5 siguen siendo `0` **registrado**, incluso si QA aconseja cautela: dicha cautela figura en el ejeQA y no se convierte en prueba de ausencia. Si la máscara misma no es interpretable, correspondeU con causa. Nunca usar una regla genérica `QA==0`.

La tabla elemental es3×3: `00,10,01,11,0U,1U,U0,U1,UU`, primer dígitoMODIS. Los nueve estados son mutuamente excluyentes y exhaustivos sobre cada átomo; `AU=A0U+A1U+AU0+AU1+AUU`. Publicar además los desconocidos con una detección registrada (`1U/U1`) para evitar que desaparezcan de una tabla sólo de estados conocidos. Cerrar sumas por caso/escenario/estrato hasta soporte declarado.

No comparar clases7/8/9 como niveles de confianza equivalentes entre productos. Se pueden conservar desgloses por clase nativa individuales, nunca seleccionar el que aumente acuerdo.

## Tierra, agua y QA como ejes separados

Usar exclusivamente los campos de superficie ya leídos/decodificados y su procedencia. MODISQA puede distinguir tierra/agua/costa; VIIRS3/5 sólo permite superficie agua/tierra en esas clases y positivos pueden conservar superficie desconocida si falta una máscara independiente. **No inferir tierra para una detecciónVIIRS por ser positiva ni asignar la superficie del otro instrumento.** No descargar una capa nueva dentro de este estudio.

Publicar tabla completa sin estratificar y estratos conjuntos de superficie mutuamente exhaustivos: tierra/tierra, agua/agua, costa presente, conflicto tierra/agua y superficie desconocida. La clasificación exacta debe dar prioridad a desconocido si cualquiera lo es; después costa; después tierra/tierra, agua/agua o conflicto. Conservar además cada par de etiquetas nativas. Los positivos sin superficie identificada permanecen en total y en desconocidos, no fuera de la población. No sumar estratos solapados como si fueran partición.

Separar ejes de estado registrado, QA geográfica, QA algoritmo/layout, canalesVIIRS/M13, bowtie/glint y screen local. Tabla mínima: áreas y positivos afectados/no afectados/QA desconocido por producto, más descripciones conjuntas sólo sobre los átomos ya fijados. M13 no nominal es sensibilidad de interpretación; el positivo permanece visible en todas las tablas primarias. Si se presenta un screen conservador adicional, debe decir qué área/positivos dejaría sin interpretación y retener el catálogo original; no anunciar su acuerdo condicionado como mejora de detección.

## Tiempo: referencias concretas de cada par propietario

Cada átomo hereda **sus propios** IDs nativos de scan y sus referencias: MODIS `EV center time`/`EV start time`; VIIRS `ev_mid_time`/`scan_start_time`/`scan_end_time`, unidades/época/flags originales. Calcular, si identificables, diferencias de referencias de ese ownerpair. No reutilizar la distribución temporal de antiguos pares de centros para certificar nuevos átomos. No interpretar esos tiempos como instante o intervalo conservador de exposición por píxel.

Reportar área por ownerpair y diferencias temporales, preservando referencia nula y causa. No filtrar por10min ni ajustar ventana para aumentar coincidencia. Una diferencia de estados puede mezclar instrumento y evolución real entre pasadas; este diseño no los identifica por separado.

## Escenarios prefijados, sin elegir el favorable

Conjunto completo fijado por caso: dos políticas conjuntas de prioridad24B (temprano/temprano primaria; tardío/tardío sensibilidad), cruzadas con nueve traslacionesVIIRS: `(0,0)`, `(±75,0)`, `(0,±75)`, `(±150,0)`, `(0,±150)` metros en ejeseste/norteEPSG:32718. Total18escenarios por caso. No es el factorial independiente MODIS×VIIRS de prioridades, que tendría36; no se incorporan las dos políticas mixtas. Mover toda la geometríaVIIRS de forma rígida, con sus índices/clases/referencias, no MODIS ni etiquetas aisladas; reintersectar AOI y volver a resolver propiedad conforme misma regla. Mantener halos/malla sin extrapolar. Si faltan polígonos suficientes para un escenario, reportar soporte desconocido y detener su resumen, no reconstruir vecinos favorables.

Estas traslaciones y prioridades son escenarios condicionales supuestos, no error geográfico medido, distribución probabilística, intervalo de confianza o optimización. No seleccionar el máximoJaccard, mínimo desacuerdo o mayor retención. Publicar las18filas, incluidas fallidas.

Controles geométricos de cohorte fija, definidos **antes de estados**:

- `S*`: intersección de soportes comunes identificados de los18escenarios; recortar cada partición al mismo S* para comparar vectores integrados sobre la misma ubicación del mapa, permitiendo que cambien propietarios. No exigir refinamiento simultáneo de todos los límites de18escenarios; si se desean transiciones espaciales, usar refinamiento por contraste contra la base. Nunca definirS* por estar despejado, conocido o sin positivos.
- `S_priority*`: intersección temprano/tardío sin desplazamiento, para aislar el cambio de prioridad de cambios de soporte.
- Además de estos controles, reportar la población nativa común de cada escenario y su área retenida. SiS* es vacío o insignificante para la pregunta, informarlo y no forzar comparación estable.

Las áreas de desconocidos siguen formando parte deS*; no restringir después a “conocido en todos los escenarios”. Tal restricción condicionaría por calidad y podría eliminar los casos difíciles. Puede tabularse con denominador explícito como diagnóstico secundario, nunca como control primario.

## Cómo detectar acuerdo aparente por pérdidas

No llamar mejora a menorA10+A01 si cambió el soporte. Para cada contraste con escenario base separar geométricamente soporte retenido, perdido y entrante; sobre estas tres regiones mostrar tabla de estados de cada escenario donde exista. El cambio de área de cada estado se cierra como: cambio dentro de soporte fijo + contribución de área entrante − contribución de área perdida. Este cierre es contabilidad, no causalidad del sensor.

Conservar el catálogo completo24B de positivos originales por instrumento/caso: dentroAOI, halo, exterior, no asignable; geometría conocida/null; parte excluida por propiedad, propia sin soporte común y propia común. Marcar cada positivo que pierda todo soporte común aunque el resumen de acuerdo mejore. No sumar conteos nativos entre sensores; no sumar áreas de positivos de scans solapados como si fueran unión única. Una fracción de polígono positivo retenida no es fracción de fuego retenido.

La estabilidad enS* acompañada de pérdidas de positivos fuera deS* sólo acredita estabilidad condicionada al soporte superviviente. Siempre mostrar cuánto y qué se perdió. Una caída de desconocidos por exclusión geométrica no equivale a adquirir observaciones útiles.

## Resúmenes secundarios e inconclusos

- Jaccard nominal de estados registrados `A11/(A11+A10+A01)` sólo sobre pares conocidos, con áreas1U/U1/UU y área total adyacentes. Denominador0→null, no1. No usarlo como objetivo de selección.
- Area discordante registrada `A10+A01` y sus dos direcciones, siempre con denominadores común/AOI y controles de soporte fijo. No presentar `(A00+A11)/área_conocida` como éxito: puede estar dominado por00.
-2019 sin positivos en el inventario anterior no autoriza asumir de antemano ningún valor en soporte ampliado de polígonos. Si el nuevo dominio tampoco tiene positivos conjuntos, Jaccardnull: caso de ingeniería/ceros registrados, no evidencia de sensibilidad ni concordancia positiva.
- Sin intervalos de confianza basados en miles de átomos: comparten píxeles/scans/escena. Las amplitudes entre escenarios son rangos descriptivos condicionales, noIC.

Desenlaces fijados antes de autorizar métricas:

1. **Identidad/propiedad no reproducible:** bloquear tabla conjunta afectada; entregar ledger de fallo, sin cambiar caso, prioridad o tolerancias.
2. **Términos de cambio con soporte/estados:** publicar cada término firmado de cambio retenido+entrada−pérdida por componente, sin dividir por una variación neta pequeña ni llamarlo porcentaje atribuible. Sin regla adicional previa no concluir que un término explica principalmente el resultado; conservar el alcance abierto y resolver representación/retención antes de interpretar concordancia.
3. **Estados y discordancia persisten sobre controles geométricos fijos y todas las sensibilidades:** evidencia descriptiva de persistencia bajo este operador nominal; el siguiente estudio deberá discriminar tiempo, respuesta instrumental o contexto con evidencia adicional, no convertir persistencia en error físico.
4. **Sin positivos, soporte común insuficiente, superficie/timing no identificables o gran masaU:** resultado inconcluso para comparación positiva/causal; conservar valor técnico sin buscar otro caso favorable.

No fijar después del resultado un umbral de “suficiente” para promover hipótesis. Publicar tamaños/áreas/estados para que la revisión decida el alcance, no un gate físico inventado.

## Pruebas previas y artefactos requeridos

Pruebas sintéticas antes de datos conjuntos: overlay/áreas/disjunción; prioridad independiente de etiquetas;9estados exhaustivos;1U/U1 preservados;7–9+M13 no nominal permanecen positivos;fill/glint/nube desconocidos;3/5 no detección registrada; superficie positivaVIIRS desconocida; tiempos de ownerpair distintos de nearest-center antiguo; desplazamientos y bordeAOI; unión≠sumas; pérdida/entrada y cierre;S* sin condicionamientoQA;Jaccard0den null; todos18escenarios conservados. Invariancia de propiedad al permutar clases/QA; cambiar etiquetas no debe modificar soporte o prioridades.

Artefactos nuevos: protocolo autorizado; freeze/manifiesto hashes; geometrías/índices de átomos y controles fijos; ledger original24B preservado y referencias; tabla9estados/5agregados con denominadores; superficie y QA separados;18escenarios por caso con fallos; contabilidad de pérdidas/entradas; revisión de conclusiones condicionales. Sólo después de revisión puede decidirse una nueva investigación, nunca una corrección del modelo mensual basada en este pequeño estudio.

## Fuentes y deuda científica conservada

Base local: `2026-11-15-observation-ownership-ledger-protocol.md`, `2026-11-15-joint-plan-24.md`, `2026-11-14-observation-native-qa.md`, `2026-11-14-observation-geotiming-protocol.md`, decoder `pipeline/observation_qa.py` y `local_screen` en `pipeline/observation_native_qa.py` como eje separado, no sustituto de la máscara original.

Referencias primarias ya documentadas: [guía NASA VIIRS375mC2](https://www.earthdata.nasa.gov/s3fs-public/2024-07/VIIRS_C2_AF-375m_User_Guide_1.0.pdf), [ATBD geolocalizaciónNASA](https://ladsweb.modaps.eosdis.nasa.gov/api/v2/content/archives/Document%20Archive/Science%20Data%20Product%20Documentation/Product%20Generation%20Algorithms/NASARevisedVIIRSGeolocationATBD2014.pdf), [caracterización geométricaNASA/GSFC](https://ntrs.nasa.gov/api/citations/20120009053/downloads/20120009053.pdf). No se consultaron nuevos productos ni se ejecutaron arrays de comparación para este diseño.

La pregunta original “¿cuánto del desacuerdo desaparece cuando ambos tuvieron oportunidad comparable?” sigue abierta: los operadores nominales y referencias de scan no identifican por sí solos oportunidades físicas, detección de subpíxel, PSF, omisiones por humo/nube o evolución entre pasadas. Este protocolo acota un paso observable sin sustituir esa deuda por acuerdo aparente.

## Revisión adversaria previa al protocolo

El miembro adversarial_council_measurement24 considera admisible el experimento condicional tras validar24B. Sus cuatro ajustes se incorporaron: puente de denominadores,18políticasconjuntas frente36independientes, soporteS* sin overlayglobalinnecesario y cierre firmado sin atribuciónprincipal retrospectiva. Los límites numéricos y cap concretos quedan por fijar en protocolo25 antes de cualquier clase conjunta. Este diseño todavía no es autorización de ejecución.
