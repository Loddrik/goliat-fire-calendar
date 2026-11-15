# Fase B: consistencia de una malla CORE nominal sobre dos casos

La malla MODIS supera los controles dimensionales, de proyección y estabilidad espacial preregistrados en las regiones ensayadas de 2019 y 2023. Los controles geométricos disponibles para VIIRS también pasan, pero su comparación con dimensiones externas I-band/DFOV sigue pendiente. **Esto acredita consistencia de un proxy nominal dentro del dominio CORE ensayado; no acredita footprints físicos ni cobertura observada y no cambia G1.**

Se aplicaron el [protocolo original](2026-11-15-observation-mesh-validation-protocol.md), commit `69a35d3`, y su [aclaración](2026-11-15-observation-mesh-validation-clarification.md), commit `0fc9af4`, ambos congelados antes de nuevas geometrías reales. La aclaración fijó diferencia **simétrica** de halos y mantuvo el gate de área, además de longitudes, en 20 %/30 %. No se reajustó ningún umbral ni se modificó el constructor CORE de fase A después de medir.

## Entradas y población del ensayo

Se abrieron únicamente MYD03 y VNP03IMG de cada uno de los casos ya adquiridos: 3 de enero de 2019 y 10 de febrero de 2023. No se abrieron productos FIRE, sus máscaras, QA atmosférica o resultados de actividad. Los cuatro GEO conservaron hashes originales, verificados antes y después; los registros previos de adquisición también mantienen sus hashes.

El lector aislado exportó ventanas NPZ ignoradas por Git: diez escaneos MODIS y nueve VIIRS en cada caso. Se conservaron todas las filas de detector, al menos dos columnas vecinas de margen y mapping explícito a fila, columna y escaneo nativos. Los flags geográficos se retuvieron; coordenadas inválidas o flags geográficos distintos de cero son entradas geométricas pendientes, no observaciones sin fuego.

La AOI es el cuadrado de 50×50 km en EPSG:32718 ya fijado. Se construyeron independientemente halos de 10 y 15 km y se recortaron sus uniones a la AOI. La población de métricas son polígonos CORE aceptados cuyos centros caen dentro de cada halo; no se extienden los resultados a todas las columnas del granule. Los estratos fijos de escaneo, detector y franjas de 100 columnas nativas se conservan como diagnósticos, sin seleccionar los más favorables.

## Gates de ingeniería preregistrados

Los errores dimensionales MODIS comparan lados along-scan/along-track medios y área UTM con el modelo nominal de la guía C6/C6.1, usando la **columna nativa desde cero** y centro instrumental 676,5. La conversión explícita fue km→m y km²→m²; no se recalibró el modelo a los datos. Estas tolerancias de ingeniería no son estándares NASA ni una prueba de IFOV verdadero.

| Caso, halo 15 km | Scan: mediana / p95 | Track: mediana / p95 | Área: mediana / p95 |
| --- | ---: | ---: | ---: |
| MODIS 2019 | 1,914 % / 2,520 % | 1,791 % / 1,813 % | 3,744 % / 4,332 % |
| MODIS 2023 | 1,886 % / 3,250 % | 1,478 % / 1,509 % | 3,383 % / 4,695 % |
| Umbral fijado para cada métrica | ≤20 % / ≤30 % | ≤20 % / ≤30 % | ≤20 % / ≤30 % |

Los tres gates pasan también con halo de 10 km, cuyos percentiles completos están en evidencia. El máximo error de área MODIS no se ocultó: aproximadamente 6,73 % en 2019 y 11,15 % en 2023 con halo de 15 km. Pasar medianas y p95 no certifica una cota por píxel ni elimina diferencias locales entre celda de muestreo y respuesta del detector.

| Estabilidad de uniones CORE recortadas: 10 frente a 15 km | Diferencia simétrica |
| --- | ---: |
| MODIS 2019 | 0 m² |
| VIIRS 2019 | 0 m² |
| MODIS 2023 | aproximadamente 0,000000249 m² |
| VIIRS 2023 | 0 m² |

Los cuatro pasan el umbral `1e-6 × área AOI`, equivalente a 2.500 m². El residuo diminuto de 2023 es numérico. Se utilizó la diferencia simétrica espacial, no una resta de áreas que pudiera compensar cambios de forma.

Los errores de área UTM frente a geodesia WGS84 sobre los mismos vértices no exceden aproximadamente **0,0898 %**, por debajo del 1 % fijado; los lados también pasan. Estos controles evalúan la métrica/proyección, no exactitud óptica ni superficie real de terreno inclinado.

## CORE, bordes y bowtie

| Ventanas con halo de 15 km | Polígonos CORE medidos, centros dentro de halo | Posiciones de borde pendientes en ventanas completas |
| --- | ---: | ---: |
| MODIS 2019 | 4.672 | 1.564 |
| VIIRS 2019 | 40.707 | 3.776 |
| MODIS 2023 | 2.674 | 1.018 |
| VIIRS 2023 | 37.398 | 3.530 |

Las dos columnas tienen dominios distintos: la segunda filtra por centro dentro del halo y la tercera conserva las ventanas completas con sus vecinos de construcción. Las particiones y fracciones de geometría pendiente de cada dominio están identificadas en el informe; no deben combinarse como denominador observacional.

No se encontraron polígonos CORE rechazados por topología o centros inválidos en estas ventanas. Los bordes de escaneo y de ventana permanecen pendientes, sin extrapolación o reparación. Todos los índices pendientes se conservaron. La regla VIIRS de razones de espaciamiento fuera de `[0,8;1,25]` no encontró saltos en estos subconjuntos; **no significa que esté verificado el modelo físico de agregación C2**. `VIIRS_detector_dimensions_verified=false` y su consistencia nominal global permanece pendiente.

Se conservaron los solapamientos entre escaneos. Por ejemplo, en 2023 la suma de polígonos MODIS recortados excede su unión en aproximadamente 232,02 km²; para VIIRS, en aproximadamente 15,05 km². No se sumaron como si fueran superficie nueva. El exceso VIIRS de 2019 es numéricamente −0,00000143 m², compatible con cero a la precisión de la operación; se retuvo el residuo firmado, sin convertirlo en solapamiento físico negativo o reparar geometrías.

## Intersecciones nominales y perturbaciones supuestas

| Caso | Unión MODIS CORE recortada | Unión VIIRS CORE recortada | Intersección de ambas |
| --- | ---: | ---: | ---: |
| 2019 | 2.098,249 km² | 2.412,819 km² | 2.030,812 km² |
| 2023 | 2.500,000 km² | 2.498,580 km² | 2.498,580 km² |

Son áreas del **modelo geométrico CORE**, incluidas sus exclusiones estructurales. Las zonas fuera del CORE no son evidencia de falta de observación. Las áreas no describen superficie despejada, quemada o con calidad suficiente para detectar fuego. Ambas intersecciones son menores o iguales que sus respectivas uniones y las uniones pasan idempotencia.

Las ocho perturbaciones predefinidas por caso trasladaron la unión VIIRS **antes del recorte**, ±75 m y ±150 m en las cuatro direcciones cardinales, manteniendo Aqua fijo. Esto evita introducir pérdidas artificiales al desplazar una geometría ya cortada por la AOI. En 2019 el cambio de intersección va aproximadamente de −0,3771 a +0,1756 km²; en 2023, de −0,0252 a +0,0249 km². Se conservaron todos los desplazamientos: no se escogió el que maximiza intersección. Son escenarios supuestos, no errores físicos calibrados ni intervalos de confianza.

## Estado y limitaciones

`nominal_geometry_consistency_passed=true` para MODIS en los dos casos, restringido al proxy y población ensayados. Para VIIRS, `available_engineering_checks_passed=true` pero `nominal_geometry_consistency_passed=false`, dado el control dimensional externo pendiente. Ningún píxel o producto recibe aprobación científica por esos indicadores.

Las cuatro decisiones globales continúan falsas: G1, footprints físicos verificados, exposición física temporal verificada y elegibilidad científica. Resolver los restantes requisitos no exige una PSF exacta; sí exige una definición defendible de soporte nominal, su incertidumbre y las políticas independientes de tiempo y QA/global. Esta fase no calculó concordancia de fuego ni entrenó modelos.

## Reproducción y evidencia

```sh
.venv/bin/python -m unittest discover -s tests -p test_observation_mesh_validation.py -v
DYLD_LIBRARY_PATH="$PWD/.runtime/obs-native/lib" \
  .runtime/obs-env/bin/python pipeline/observation_mesh_validation.py --export-geolocation
.venv/bin/python pipeline/observation_mesh_validation.py
```

Las siete pruebas pasaron **antes de abrir los GEO**: fórmula, simetría, unidades y positividad; índice nativo tras recorte; gates mediana/p95; vecinos y filas completas; transiciones de espaciamiento; diferencia simétrica de igual área y traslación anterior al recorte. El módulo no sobrescribe exportaciones o evidencia existentes. No se instalaron paquetes ni modificaron locks o entornos globales.

La lectura aislada produjo NPZ con hashes en `.runtime/observation-mesh-validation/`; el benchmark corrió en el entorno principal con NumPy/Shapely/pyproj. Los dos entornos se registran. La ejecución del benchmark duró aproximadamente 31 segundos.

El [resumen compacto](evidence/observation-mesh-validation/summary.json) contiene gates, conteos, cuantiles esenciales y sensibilidades. El [informe completo comprimido](evidence/observation-mesh-validation/report.json.gz) conserva percentiles 0–100, todos los estratos fijos e índices pendientes. El manifiesto identifica protocolo, aclaración, código, helper CORE, entradas GEO y NPZ de intercambio; se incluyen snapshots y protección por hash de entradas/registros previos. No se modificaron producción, datos base, resultados anteriores o el helper de fase A. Sin modificaciones Git, commits ni push por este agente.

### Empaque posterior, separado de la ejecución

El pipeline original generó `report.json`, de **13.572.302 bytes**. Después de finalizar y verificar el análisis se empaquetaron esos mismos bytes como gzip determinístico, nivel 9, `mtime=0` y sin nombre en cabecera: **2.041.896 bytes**. No se reruneó el análisis ni se alteraron métricas, resumen, código o snapshots ejecutados. El JSON plano original se movió a `.runtime/observation-mesh-validation/report.json`, ignorado por Git. El pipeline conserva su comportamiento original de generar JSON; el `.gz` es exclusivamente un empaque posterior de almacenamiento.

Se verificaron identidad exacta de bytes al descomprimir y determinismo de dos empaques independientes. El [manifiesto](evidence/observation-mesh-validation/manifest.json) distingue el archivo físico `.gz` y su SHA-256 del nombre lógico, tamaño y hash descomprimido. Para consultar y verificar el contenido:

```sh
gzip -dc docs/reviews/evidence/observation-mesh-validation/report.json.gz > /tmp/goliat-mesh-report.json
shasum -a 256 /tmp/goliat-mesh-report.json
```

SHA-256 esperado del JSON descomprimido:

```text
79b062851322078852a301db039683cf5b11a49c8f6fa30d418d66b4ae97fa07
```
