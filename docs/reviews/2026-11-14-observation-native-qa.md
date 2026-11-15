# Inventario nativo de clasificación y QA: caso fijado del 3 de enero de 2019

El inventario de la AOI predefinida contiene exclusivamente clases sin detección registrada y tres centros VIIRS afectados por reflejo solar. Este caso permite comprobar lectura, clasificación, reconciliaciones y separación entre candidatos locales y elegibilidad global. **No valida sensibilidad frente a fuego ni explica desacuerdos de detecciones positivas. G1 permanece falso.**

Se siguió el [protocolo fijado antes de los conteos](2026-11-14-observation-native-qa-protocol.md), commit `514c530`: los mismos cuatro archivos ya adquiridos, cuadrado de 50×50 km en EPSG:32718 centrado en 37°S, 72.5°W, sin selección por actividad. No se cambiaron productos, caso, geometría o umbrales después de observar los resultados.

## Conteos separados por producto

Son **centros de píxeles nativos**, no áreas, incendios individuales, oportunidades comparables o observaciones independientes. No se sumaron entre instrumentos ni se calcularon ratios de resolución o concordancia.

| Partición geográfica del granule | MYD14 061 | VNP14IMG 002 |
| --- | ---: | ---: |
| Total nativo | 2.748.620 | 41.369.600 |
| Centros dentro de la AOI | 2.280 | 16.978 |
| Centros fuera de la AOI | 2.746.340 | 41.352.622 |
| No asignables: coordenadas inválidas | 0 | 0 |
| No asignables: proyección inválida | 0 | 0 |

Las dos particiones suman exactamente sus respectivos totales nativos. Las dimensiones FIRE/GEO/QA coinciden sin reescalamiento: MYD14/MYD03 2.030×1.354; VNP14IMG/VNP03IMG 6.464×6.400. Los SHA-256 coinciden con el inventario autenticado y `InputPointer` referencia exactamente cada geolocalizador utilizado.

| Clase de máscara dentro de la AOI | MYD14 061 | VNP14IMG 002 |
| --- | ---: | ---: |
| 0: entrada ausente / no procesado, según producto | 0 | 0 |
| 1: categoría obsoleta MODIS / bowtie eliminado VIIRS | 0 | 0 |
| 2: categoría obsoleta MODIS / reflejo solar VIIRS | 0 | 3 |
| 3: agua sin detección registrada | 11 | 28 |
| 4: nube | 0 | 0 |
| 5: tierra sin detección registrada | 2.269 | 16.947 |
| 6: desconocido / sin clasificar | 0 | 0 |
| 7: detección de confianza baja | 0 | 0 |
| 8: detección de confianza nominal | 0 | 0 |
| 9: detección de confianza alta | 0 | 0 |
| Rellenos explícitos de máscara | 0 | 0 |
| Valores de clase no reconocidos | 0 | 0 |

Cada columna reconcilia con sus centros dentro de la AOI. La implementación mantiene los valores de relleno definidos por cada campo; si el atributo no existe, no inventa un relleno para la máscara o QA del algoritmo. Clase 0 sigue siendo una categoría explícita, separada de un atributo de relleno. Una clase 7 continúa siendo detección incluso cuando se considera de baja confianza.

## QA del algoritmo, geolocalización y política local

En las dos AOI todos los valores del QA del algoritmo pertenecen al layout versionado soportado; no aparecen rellenos ni bits reservados activos. Todos los flags geográficos son cero. Estos resultados no incluyen integridad completa de escaneo ni calidad atmosférica adicional.

En MODIS, los bits 0–1 del QA registran **2.269 tierra, cinco agua y seis costa**. La máscara clasifica once centros como agua sin detección, pero el QA distingue agua y costa; no se reemplazó esa distinción por un estado terrestre común. Todos usan algoritmo diurno y nivel de reflejo solar cero. El QA del algoritmo es distinto de cero por motivos normales del layout: no se aplicó una regla universal `QA==0`.

En VIIRS, los bits 0–6 de calidad de entrada están nominales y no aparece bowtie residual dentro de la AOI. Existen bits de pruebas de detección/rechazo activos; no se consideran fallos simplemente por valer uno. La clase final 2 identifica tres centros de reflejo solar y los excluye de la política local, aunque los bits de calidad radiométrica sean nominales. No se inspeccionó `land_water_mask` independiente; se conservan los estados de superficie derivados de clases 3/5 y no se infiere superficie de una detección a partir de bits de calidad.

| Resultado de la política local, condicionado a los campos inspeccionados | MYD14 061 | VNP14IMG 002 |
| --- | ---: | ---: |
| Candidatos locales | 2.280 | 16.975 |
| Excluidos locales | 0 | 3 |
| Política local sin resolver | 0 | 0 |

Las dos últimas particiones reconcilian con la AOI. Los once candidatos MODIS de clase 3 conservan cinco estados agua y seis costa; los demás son tierra. Los candidatos VIIRS son 28 de clase 3 y 16.947 de clase 5. Estas categorías describen los resultados registrados por cada algoritmo, no ausencia física de fuego, humo o actividad pequeña no detectable.

**La cuarentena global se aplica por separado:** MYD14 declara `AUTOMATICQUALITYFLAG=Suspect`, con la explicación conservada en evidencia. Ningún candidato local recibe por ello aprobación científica. El código no pasa un falso `Passed` para obtener los conteos locales: la función local carece de argumento de calidad global y la decisión global se almacena aparte. VIIRS tampoco recibe certificación global a partir de este inventario. Una cuarentena no se representa como una serie de ceros o como ausencia de observación física.

## Qué acredita y qué no

La entrega acredita software capaz de conservar estados nativos exhaustivos, leer layouts de QA por versión y separar geolocalización no asignable, flags geográficos, clasificación final, superficie y decisión global. En este par concreto no se encontraron centros con coordenadas inválidas ni flags geográficos no nominales; las pruebas sintéticas cubren esos casos y comprueban que un centro geolocalizable con flag malo se cuenta en la AOI y se excluye únicamente del screen local.

No se emparejaron clases de fuego entre sensores, no se generó matriz de positivos ni se calculó concordancia. Tampoco se estimó qué proporción del desacuerdo desaparece al filtrar observabilidad. No se derivaron cobertura física, porcentajes de superficie, probabilidades de ausencia de fuego o factores para el modelo mensual.

La exposición física acotada por muestra/escaneo, footprints comunes, integridad completa de escaneo y resolución del flag global siguen pendientes. El informe conserva explícitamente `gate1_passed=false`, `scientific_eligibility_certified=false`, `common_footprints_verified=false` y `pixel_exposure_times_verified=false`.

## Reproducción y verificación

```sh
.runtime/obs-env/bin/python -m unittest discover -s tests -p test_observation_native_qa.py -v
DYLD_LIBRARY_PATH="$PWD/.runtime/obs-native/lib" \
  .runtime/obs-env/bin/python pipeline/observation_native_qa.py
```

La primera ejecución encontró un atributo NetCDF con bytes anidados al serializar el informe. Se corrigió únicamente la serialización y se añadió una prueba antes de repetir; no cambiaron reglas, caso o conteos para obtener un resultado favorable. La ejecución que generó los artefactos tiene código y protocolo identificados por hash. El programa rechaza sobrescribir evidencia no vacía; la reproducción debe usar `--output-dir` con un directorio nuevo.

**Siete pruebas sintéticas aprobadas:** reconciliación de clases/rellenos/desconocidos/QA reservado; geoflag dentro de AOI frente a coordenada no asignable; shapes, filas por escaneo y tipos nativos; agua/tierra/confianza baja; máscara frente a bits VIIRS; política local sin aprobación global y glint pendiente; serialización de atributos nativos anidados.

Los [artefactos de evidencia](evidence/observation-native-qa/counts.json) incluyen conteos, atributos seleccionados, entorno, hashes de cuatro entradas, código, decodificador y protocolo, snapshots reproducibles y manifiesto. El entorno aislado existente fue suficiente; no se instalaron nuevas dependencias ni se hicieron descargas. Sin cambios a modelos, datos base, producción o indicadores publicados. Sin commit ni push por este agente.
