# Consistencia nominal VIIRS frente a tamaños FIRMS selectivos

Los trece registros S-NPP de 2023 que cumplen el protocolo tienen una asociación única con centros nativos y polígonos CORE. Sus tamaños nominales FIRMS y los del proxy pasan los tres gates de ingeniería. El caso de 2019 no ofrece referencias dentro de la ventana y AOI fijadas y queda **no evaluable**, sin sustitución.

**El resultado cierra una comparación nominal local sobre referencias selectivas de 2023. No valida dimensiones de todos los píxeles, otras zonas de agregación, observaciones sin detección, verdad física de fuego o G1.**

## Protocolo, fuente y selección

Se aplicó el [protocolo congelado](2026-11-15-viirs-dimension-consistency-protocol.md), commit `1c065c4`, usando la fuente local `snpp-history` publicada en `observed/dist`. Se verificaron los 54 CSV contra SHA-256, bytes y número de registros del manifiesto, junto con plataforma S-NPP, instrumento VIIRS, versión, procedencia, coordenadas, hora y cohorte heredada: día, tipo 0, confianza n/h. NOAA-20 no es una plataforma admitida por esta comprobación.

La cohorte ya estaba filtrada; no recupera bajas confianzas, otros tipos o mediciones sin detección. No se filtró por acuerdo de tamaños, FRP o conveniencia geométrica. No se consultó FIRMS API ni se utilizó su clave. No se abrieron máscaras FIRE, arrays QA de fuego o FRP. No hubo asociaciones MODIS–VIIRS ni recalibración de geometría.

Los intervalos UTC, cerrados por la izquierda y abiertos por la derecha, fueron los del granule S-NPP fijado previamente:

| Caso | Ventana UTC | Referencias dentro de la AOI y ventana |
| --- | --- | ---: |
| 2019-01-03 | 18:36:00–18:42:00 | 0 |
| 2023-02-10 | 18:30:00–18:36:00 | 13 |

La AOI conserva el cuadrado de 50×50 km en UTM 18S. El instante CSV se interpreta a resolución de minuto para seleccionar esa ventana; no se transforma en tiempo exacto de exposición del píxel. La correspondencia de centro y metadatos tampoco se presenta como un `InputPointer` FIRMS→L2 certificado.

## Asociación única, sin rescates

La tolerancia primaria fue de **25 m**; 75 m se fijó únicamente como sensibilidad. Para cada identidad CSV se contaron todos los centros geolocalizables dentro de la tolerancia. Cero candidatos implica no asociado y más de uno implica ambigüedad; no se escogió el más cercano para resolverla. Distintas identidades que llegaran al mismo centro se rechazarían para no inflar N. Los duplicados con dimensiones conflictivas no pueden elegir el valor que ajuste mejor.

En 2023 las trece identidades resultaron únicas, sin duplicados o conflictos de fuente. Las distancias de asociación fueron **0,194–0,565 m**, dentro de 25 m. Ninguna asociación necesitó ampliar el umbral, elegir un vecino interior o resolver ambigüedad por dimensiones. Las trece llegaron a polígonos CORE válidos y completos; no se recortaron a la AOI para medir su tamaño.

La prueba secundaria de 75 m conserva las mismas trece asociaciones y métricas. Se exportó por separado y no reemplaza el resultado primario. En 2019 ambas tolerancias conservan cero referencias y estado `not_evaluable`: no es un fallo observacional ni evidencia de ausencia física de fuego.

## Errores nominales y gates fijados

Las longitudes de la malla son medias de los pares de lados opuestos en las direcciones nativas scan/track. La referencia es `scan` y `track` del proveedor, en km; su producto se convierte a m² para comparar área. Es una comparación entre representaciones nominales, no medición de una PSF exacta. Se usaron polígonos completos, sin escalar, ajustar o rellenar geometría para mejorar los errores.

| Error relativo absoluto, 2023, primario 25 m | Mediana | p95 | Máximo |
| --- | ---: | ---: | ---: |
| Along-scan | 2,678 % | 3,442 % | 3,493 % |
| Along-track | 3,875 % | 3,956 % | 3,965 % |
| Área | 6,656 % | 7,437 % | 7,500 % |

Los tres cumplen mediana ≤20 % y p95 ≤30 %, con **N=13 ≥5**. Son umbrales de ingeniería predeclarados, no tolerancias de NASA. El informe completo conserva percentiles 0–100; no se eligió una métrica después de observar cuál pasaba.

En 2019, N=0 no cumple el mínimo ni permite estimar esos percentiles: su gate sigue falso y las métricas quedan ausentes, no se rellenan con ceros. No se ampliaron fechas, AOI o confianza para conseguir referencias.

## Dominio I-band realmente contrastado

Se utilizó el mapa nominal I-band de la tabla NASA ATBD 2014, con índices desde cero: 0–1279 factor 1; 1280–2015 factor 2; 2016–4383 factor 3; 4384–5119 factor 2; 5120–6399 factor 1. No se trasladaron índices M-band ni se afirmó calibración óptica exacta C2.

Las referencias de 2023 ocupan columnas nativas **3796–3820**, filas **2117–2124** y detectores **5, 7, 9, 10, 11 y 12**, todos en el **escaneo nativo 66** y región nominal **3:1**. Es un dominio estrecho, no un muestreo de otros escaneos, regiones o transiciones.

Los GEO exportados para las ventanas geométricas previas cubren columnas 3327–3567 en 2019 y 3704–3922 en 2023, también dentro de la región 3:1. Este inventario delimita el alcance; no permite inferir desempeño dimensional de regiones 1:1/2:1 por ausencia de saltos en estas ventanas.

El HSI o separación entre centros y el IFOV/DFOV no se igualan por definición. El acuerdo con tamaños FIRMS es un control de consistencia del proxy en estos puntos registrados; FIRMS puede compartir geometría instrumental de origen y no es ground truth independiente. Los trece registros tampoco se anuncian como trece pruebas físicamente independientes.

## Estado final

- `primary_selective_size_consistency_passed=true` solo para 2023; 2019 permanece `not_evaluable` y falso.
- `physical_detector_dimensions_verified=false` y `all_pixel_dimensions_verified=false`.
- `gate1_passed=false` y `scientific_eligibility_certified=false`.

No se modifican los gates ni reportes de la fase B anterior. La nueva evidencia permite acotar el pendiente VIIRS a un chequeo nominal selectivo exitoso, sin certificar el denominador de observación completo o eliminar las tareas de soporte, tiempo y QA global.

## Reproducción y trazabilidad

```sh
.venv/bin/python -m unittest discover -s tests -p test_viirs_dimension_consistency.py -v
.venv/bin/python pipeline/viirs_dimension_consistency.py
```

Ocho pruebas sintéticas verifican el mapa I-band, deduplicación/conflictos, unicidad 25/75 m sin nearest rescue, colisiones de identidades, reloj/intervalo semiabierto, mínimo N/gates, medición del polígono completo e integridad de fuente/cohorte. Antes de datos se corrigió una expectativa de percentil interpolado de un fixture; los gates no cambiaron. El primer arranque se cerró antes de leer CSV por buscar el hash del índice en el resumen compacto B; se corrigió la referencia al manifiesto B que sí fija ese hash. No se cambió una regla científica para obtener el resultado.

Los NPZ reutilizados permanecen ignorados y verificados contra el índice de la fase B y su manifiesto. Los helpers CORE/transiciones conservan sus hashes; el script rehúsa sobrescribir evidencia existente. El análisis terminó en unos doce segundos.

La [evidencia nueva](evidence/viirs-dimension-consistency/summary.json) incluye los dos casos y tolerancias, todas las identidades y razones, errores, dominio de índices, manifiesto de los 54 CSV y hashes de código/helpers/protocolo. Las versiones planas CSV son exportaciones posteriores de los mismos registros JSON, sin FRP, temperaturas o arrays de clases de fuego; no recalculan métricas. Se registran entorno y contrato selectivo de fuente. Se verificó que los hashes de los CSV publicados permanecen iguales tras el chequeo. Sin nuevas dependencias, red, cambios en datos anteriores, producción, modelo, Git, commits o push.
