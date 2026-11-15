# Centros cercanos y desfase local de referencias de escaneo

El inventario técnico del caso del 3 de enero de 2019 encuentra referencias de escaneo separadas aproximadamente **5 minutos y 26 segundos** para centros espacialmente próximos. Esto reduce la ambigüedad de usar únicamente los intervalos generales de los granules, que admitían una separación potencial de 0–9 minutos. **No estima tiempos exactos por píxel ni verifica una oportunidad comparable de detectar fuego. G1 permanece falso.**

Se ejecutó el [protocolo fijado antes del análisis](2026-11-14-observation-geotiming-protocol.md), commit `0e30172`. Se abrieron exclusivamente MYD03 y VNP03IMG ya adquiridos. No se abrieron productos de fuego, máscaras de actividad ni su QA; no se usaron credenciales ni nuevas descargas satelitales. El flag global `Suspect` se heredó de la inspección previa, conservando cuarentena.

## Asociación geográfica predefinida

El área primaria es un cuadrado de 50×50 km en EPSG:32718, centrado en la proyección de 37°S, 72.5°W. Los centros Aqua dentro de ese cuadrado se asociaron con el centro VIIRS más próximo a ≤500 m, buscando candidatos en el cuadrado ampliado 500 m. Coordenadas finitas, dentro de rango y QA geográfica exactamente cero fueron requisitos declarados; no se afirma equivalencia de los algoritmos de calidad.

El desempate usa menor fila y luego columna nativa VIIRS. La reutilización se permite por diseño y se cuenta. No se eligieron asociaciones por actividad, tiempos más favorables o resultado de concordancia.

| Resultado técnico | Valor |
| --- | ---: |
| Centros Aqua elegibles dentro del cuadrado | 2.280 |
| Centros VIIRS candidatos, incluido margen | 17.660 |
| Asociaciones dentro de 500 m | 2.280 |
| Centros Aqua sin asociación | 0 |
| Centros VIIRS distintos utilizados | 2.280 |
| Centros VIIRS reutilizados | 0 |
| Asociaciones con centro VIIRS fuera del cuadrado primario | 8 |

| Distancia UTM entre centros | Metros |
| --- | ---: |
| Mínimo | 4,32 |
| Cuartil 25 % | 107,53 |
| Mediana | 153,99 |
| Cuartil 75 % | 188,75 |
| Máximo | 273,80 |

Son distancias euclídeas en UTM, aproximaciones locales a distancias geodésicas. Las asociaciones no prueban intersección de footprints ni forman observaciones independientes. Las ocho asociaciones de borde muestran por qué se conservó el margen espacial predefinido; no se cambió el área primaria.

## Referencias temporales almacenadas

Se validaron dimensiones nativas de 2.030×1.354 y 6.464×6.400, asignando fila a escaneo con divisores 10 y 32. Hay 203 y 202 referencias de escaneo válidas, respectivamente; ninguna de las 2.280 asociaciones tiene referencia temporal desconocida bajo las comprobaciones de finitud, relleno y orden definidas. Se conservaron los valores nativos TAI93 y no se convirtió a UTC.

| Cuantil | EV center Aqua − ev_mid VIIRS, segundos | EV start Aqua − scan_start VIIRS, segundos |
| --- | ---: | ---: |
| Mínimo | 323,9894 | 324,0408 |
| 25 % | 325,1643 | 325,2157 |
| Mediana | 325,7686 | 325,8200 |
| 75 % | 326,0708 | 326,1222 |
| Máximo | 327,2458 | 327,2971 |

Todos los desfases son positivos: la referencia Aqua ocurre después de la referencia S-NPP. Sus valores absolutos coinciden con los firmados. La estrechez del rango describe este conjunto de referencias locales; no demuestra estabilidad del fuego entre pasadas, precisión temporal de cada centro ni un intervalo conservador de exposición. Tampoco se interpreta como cumplimiento científico de una ventana de diez minutos.

Los campos geográficos leídos no contienen coordenadas fuera de rango, rellenos ni flags distintos de cero en este par de granules completo. Esto únicamente describe los indicadores geográficos inspeccionados: no informa nubes, humo, calidad radiométrica, clasificación de fuego o integridad de todos los flags de escaneo.

## Qué cambia y qué sigue pendiente

La novedad es técnica: podemos pasar de una coincidencia aproximada de granules a asociaciones reproducibles entre centros y referencias de escaneo locales. Los datos disponibles permiten construir esa etapa sin seleccionar únicamente detecciones positivas.

Siguen pendientes los footprints, la exposición por muestra, los indicadores de escaneo completos, la calidad de observación del producto de fuego y la interpretación específica del flag global `Suspect`. El resultado no produce denominador observado, porcentaje de cobertura, factor de armonización, concordancia de fuego ni nuevas variables para el modelo mensual. No justifica normalizar cantidades por fracción despejada.

## Reproducción y evidencia

```sh
.runtime/obs-env/bin/python -m unittest discover -s tests -p test_observation_geotiming.py -v
DYLD_LIBRARY_PATH="$PWD/.runtime/obs-native/lib" \
  .runtime/obs-env/bin/python pipeline/observation_geotiming.py
```

**Siete pruebas sintéticas aprobadas:** desempates/permutaciones, reutilización, umbral inclusivo y candidatos ausentes, área primaria frente a margen, divisibilidad de filas/escaneos, rellenos/NaN/orden temporal, exclusiones geográficas y cuantiles vacíos. La ejecución se niega a sobrescribir un directorio de evidencia no vacío; para reproducir fuera de los artefactos fijados se requiere `--output-dir` con un directorio nuevo.

Entorno aislado: Python 3.10.0, NumPy 2.2.6, h5py 3.16.0, pyhdf 0.11.7, pyproj 3.6.1 y PROJ 9.3.0. Se instaló pyproj y su dependencia certifi únicamente en `.runtime/obs-env`; no se modificaron locks ni paquetes globales. La ejecución técnica duró aproximadamente diez segundos.

La carpeta [de evidencia](evidence/observation-geotiming/summary.json) contiene resumen, las 2.280 asociaciones con índices nativos, entorno, snapshots de código y protocolo, y manifiesto con tamaños y SHA-256. Los hashes de ambos archivos geográficos coinciden con el inventario autenticado anterior. La evidencia conserva explícitamente `gate1_passed=false`, `scientific_eligibility_certified=false`, `common_footprints_verified=false` y `pixel_exposure_times_verified=false`.

Sin cambios a modelos, producción, indicadores publicados o datos base. Sin commit ni push por este agente.
