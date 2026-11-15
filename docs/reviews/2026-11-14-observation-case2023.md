# Caso adicional de 2023: lectura real de clases positivas y QA

El caso seleccionado exclusivamente por metadatos contiene clases de detección positivas y flags de entrada no nominales. Permite extender las pruebas del lector y la política de QA a estados que no aparecieron en la AOI de 2019. **No mide sensibilidad física, no valida detecciones y no establece concordancia entre sensores. G1 permanece falso.**

## Selección fijada antes de observar actividad

Se siguió el [protocolo](2026-11-14-observation-case2023-protocol.md), commit `f213aff`, sin cambiar las colecciones 061/002, el cuadrado de 50×50 km en EPSG:32718 centrado en 37°S, 72.5°W o la regla temporal. El contexto [regional documentado por NASA](https://science.nasa.gov/earth/earth-observatory/fires-blaze-through-south-central-chile-150945/) motivó consultar el período; no certifica fuego en esta AOI o instante y no funciona como ground truth.

La consulta pública cubrió del 3 al 10 de febrero de 2023, con límite superior exclusivo el 11 a las 00:00 UTC. CMR devolvió 19 granules MYD14, 19 MYD03, 23 VNP14IMG y 23 VNP03IMG. El filtro DAY y máximo desfase entre extremos de granule ≤600 segundos produjo **un único par**:

- Aqua: `MYD14.A2023041.1830.061.2023042110133`.
- S-NPP: `VNP14IMG.A2023041.1830.002.2024078170147`.

Ambos comienzan a las 18:30 UTC del 10 de febrero de 2023. Su cota por intervalos completos de granule es de seis minutos. Se fijó y guardó la elección antes de descargar o abrir productos de fuego. No se buscaron coincidencias positivas ni se sustituyó este par por otro.

Los geolocalizadores tienen identificador de adquisición único y `InputPointer` exacto. Las dimensiones nativas son 2.040×1.354 para MODIS y 6.464×6.400 para VIIRS: la implementación conserva el número real de escaneos, sin imponer las 2.030 filas del caso anterior. Máscaras, QA y geolocalización coinciden sin remuestreo, y los hashes de los cuatro archivos se verificaron antes de la inspección.

## Presupuesto y trazabilidad

| Archivo | Bytes descargados |
| --- | ---: |
| MYD14 | 444.680 |
| MYD03 | 34.766.537 |
| VNP14IMG | 2.762.282 |
| VNP03IMG | 157.375.995 |
| Total adicional | **195.349.494** |

El total adicional equivale aproximadamente a 186,3 MiB y está bajo el límite de 200 MiB. Sumado a los 193.748.806 bytes anteriores, alcanza **389.098.300 bytes**, bajo los 400 MiB acumulados. No hubo transferencias fallidas. La selección, descarga e inspección terminaron en aproximadamente 59 segundos, antes del deadline fijado de las 02:14 UTC.

Se reutilizó el descargador seguro existente: credencial solo desde archivo local ignorado, autorización limitada a hosts NASA permitidos y redirects a CDN sin autorización. Las URLs guardadas carecen de queries y credenciales; no hubo cambios de cuenta, EULA o nuevas dependencias. Los originales permanecen en `.runtime/observation-case2023/raw/`, ignorado por Git.

## Inventarios independientes de clasificación

Las columnas siguientes conservan **centros nativos por producto**. No son incendios, área observada, observaciones independientes ni cantidades comparables directamente. No se sumaron entre instrumentos ni se calcularon ratios o aciertos conjuntos.

| Clase en la AOI | MYD14 061 | VNP14IMG 002 |
| --- | ---: | ---: |
| 2: obsoleta MODIS / reflejo solar VIIRS | 0 | 1 |
| 3: agua sin detección registrada | 8 | 24 |
| 5: tierra sin detección registrada | 1.293 | 15.504 |
| 7: detección de confianza baja | 0 | 3 |
| 8: detección de confianza nominal | 3 | 11 |
| 9: detección de confianza alta | 3 | 2 |
| Total de centros dentro de la AOI | **1.307** | **15.545** |

Las clases 0, 1, 4 y 6, los rellenos explícitos y valores de clase desconocidos son cero dentro de cada AOI. Los inventarios conservan también centros fuera del cuadrado y no asignables. Todas las particiones geográficas, de máscara, QA, superficie y screen local reconcilian exactamente.

## Clasificación positiva y calidad de entrada son dimensiones diferentes

Todos los flags geográficos dentro de la AOI son cero. No aparecen QA de algoritmo con relleno o bits reservados activos. Esto no demuestra ausencia de nubes o humo no reconocidos, integridad de todo escaneo o sensibilidad completa de los sensores.

El screen local MODIS conserva sus 1.307 centros: 1.299 estados tierra, cinco costa y tres agua según bits 0–1 del QA. La clase 3 de máscara no se confunde con una única categoría geográfica de agua pura. Sus tres detecciones nominales y tres altas siguen siendo clasificaciones positivas, sin reinterpretarlas como incendios confirmados.

En VIIRS el screen local excluye un centro de clase 2 por reflejo solar y doce por calidad de entrada no nominal, concretamente el bit 6 asociado a M13. Quedan 15.532 candidatos locales: 15.500 de clase 5, 24 de clase 3, dos de clase 7 y seis de clase 8. No quedan candidatos locales de clase 9 bajo esta política. La exclusión no demuestra que las detecciones originales sean falsas; muestra que confianza de detección y calidad de entradas no son equivalentes. La superficie de las detecciones VIIRS sigue marcada como desconocida porque no se inspeccionó su `land_water_mask` independiente.

**Elegibilidad global separada:** MYD14 vuelve a declarar `Suspect`, con explicación `not being investigated`. Se conserva como elegibilidad global pendiente bajo la política conservadora del piloto; no se interpreta como prueba NASA de fallo físico. Ningún candidato local recibe una aprobación global artificial. VIIRS tampoco queda certificado por este inventario.

## Centros próximos y referencias de escaneo

Con la misma política predefinida de geolocalización, margen VIIRS de 500 m, asociación más próxima a ≤500 m y desempate por fila/columna, se obtuvieron 1.307 asociaciones de centros Aqua. Ninguna quedó sin vecino; no hubo reutilización de centros VIIRS y ocho asociaciones usan el margen exterior del cuadrado primario.

| Medida técnica | Mínimo | 25 % | Mediana | 75 % | Máximo |
| --- | ---: | ---: | ---: | ---: | ---: |
| Distancia UTM entre centros, m | 4,81 | 111,91 | 162,97 | 201,11 | 286,95 |
| EV center Aqua − ev_mid VIIRS, s | 5,0927 | 6,5698 | 7,1741 | 7,7448 | 8,9534 |
| EV start Aqua − scan_start VIIRS, s | 5,1441 | 6,6212 | 7,2255 | 7,7962 | 9,0048 |

No hay referencias desconocidas bajo los controles de relleno, finitud y orden utilizados. Los desfases se calcularon en la escala nativa TAI93 y son positivos: la referencia Aqua ocurre después. **Son diferencias entre referencias almacenadas de escaneo, no tiempos exactos de píxel ni cotas conservadoras acreditadas de exposición.** La proximidad temporal local resulta informativa para la siguiente etapa técnica, pero no permite declarar G1 o comparar las clases de fuego de esas asociaciones.

## Alcance de la evidencia nueva

El caso de 2019 sin clases positivas permanece íntegro y visible. Este segundo caso amplía el inventario real a clases 7–9 y a un flag de calidad radiométrica relevante. La elección se hizo sin observar esos resultados, pero dos casos no representan una validación estadística independiente ni un conjunto de verdad física.

No se generaron emparejamientos de clases entre sensores, tablas cruzadas de detecciones o concordancias. Tampoco se estimó cuánto desacuerdo desaparece al filtrar por calidad, ni se entrenó o seleccionó un modelo. Footprints comunes, exposición acotada, integridad completa de escaneo y elegibilidad QA/global permanecen pendientes. Los cuatro indicadores científicos siguen falsos: G1, elegibilidad científica, footprints comunes y exposición física verificada.

## Reproducción y verificación

```sh
.runtime/obs-env/bin/python -m unittest discover -s tests -p test_observation_case2023.py -v
DYLD_LIBRARY_PATH="$PWD/.runtime/obs-native/lib" \
  .runtime/obs-env/bin/python pipeline/observation_case2023.py \
  --deadline-utc 2026-11-15T02:14:00Z
```

La segunda orden documenta la ejecución original, no autoriza repetir descargas: el módulo rechaza evidencia o carpeta raw preexistentes. El deadline histórico además impide una ejecución posterior. Las seis pruebas sintéticas cubren selección determinista independiente de actividad, DAY y fecha límite, extremos temporales, geolocalizador único, presupuestos que incluyen fallos y redacción de URLs/hosts.

La [evidencia](evidence/observation-case2023/result.json) contiene catálogos CMR, selección previa, adquisiciones, inventarios, referencias de escaneo, SHA-256 de archivos/código/helpers/protocolo, entorno, snapshots y manifiesto. No se modificaron scripts, resultados o snapshots anteriores, dependencias globales, locks, modelos, datos base o publicación. Sin commit ni push por este agente.
