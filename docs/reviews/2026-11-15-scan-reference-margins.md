# Márgenes de referencia de escaneo: requisitos condicionales de exposición

Para el umbral primario de 600 segundos, los resúmenes existentes permitirían una garantía temporal uniforme **si** se acreditaran márgenes iguales por instrumento de hasta aproximadamente **136,35 segundos en 2019** y **295,50 segundos en 2023**, usando las referencias de inicio. Las referencias centrales dan 136,38 y 295,52 segundos, respectivamente. Son requisitos condicionales que falta justificar: los márgenes físicos siguen desconocidos, sus métricas son nulas y **G1 permanece falso**.

Se ejecutó el [protocolo congelado](2026-11-15-scan-reference-margin-protocol.md), commit `accb2f3`, con `pipeline/scan_reference_margins.py`. Sólo se abrieron dos JSON existentes: el [resumen geotemporal de 2019](evidence/observation-geotiming/summary.json) y el [resultado de 2023](evidence/observation-case2023/result.json). No se abrieron productos raw, se descargaron archivos, se reconstruyeron asociaciones ni se consultaron clases de fuego. Las asociaciones de centros previamente construidas se conservan como contexto técnico; no se convierten en unidades físicas comunes.

## Qué está condicionado y qué permanece desconocido

Para cada asociación existente, sea δ la diferencia absoluta entre referencias de escaneo en la misma escala nativa TAI93. Si la adquisición A estuviera dentro de ±m_A de su referencia y V dentro de ±m_V de la suya, la diferencia de adquisición estaría dentro de `[max(0, δ−m_A−m_V), δ+m_A+m_V]`. Esta premisa no está acreditada aquí. Los márgenes no son errores calibrados, intervalos de confianza ni estimaciones de tiempo exacto por columna; incluyen toda incertidumbre que hubiera que justificar respecto de cada referencia elegida.

Con los mínimos y máximos ya resumidos, el sobre global condicional es `lower=max(0,minδ−m_A−m_V)` y `upper=maxδ+m_A+m_V`. `forall_within` requiere `upper≤W`; `forall_outside` requiere `lower>W`; cualquier otro caso se etiqueta `no_uniform_resolution`. Esta última etiqueta no identifica una fracción de asociaciones compatibles, no afirma que existan resultados mixtos reales y no prueba incompatibilidad de todas las asociaciones. Tampoco se infiere estabilidad del fuego entre pasadas.

Las tablas usan W=300/600/900 segundos y m_A=m_V=m para m=0/1/2/5/10/30/60/120/180/300 segundos: **la incertidumbre total asumida siempre es 2m**. Incluso m=0 es un escenario hipotético, no una imputación física a un margen desconocido. Cuando un margen es desconocido o no acotado, `conditional_relation` devuelve `not_identified` y `metrics=null`; ese resultado está separado de las tablas de supuestos.

## Requisitos cuantitativos

Las cifras siguientes se muestran redondeadas para lectura. Los CSV/JSON conservan los números de entrada y los resultados completos; la frontera estricta/abierta no debe decidirse usando el redondeo de esta tabla.

| Caso y referencia | minδ, s | maxδ, s | m máximo para todos dentro de 300 s | m máximo para todos dentro de 600 s | m máximo para todos dentro de 900 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2019 central | 323,989362 | 327,245756 | No existe m≥0 | 136,377122 | 286,377122 |
| 2019 inicio | 324,040752 | 327,297146 | No existe m≥0 | 136,351427 | 286,351427 |
| 2023 central | 5,092731 | 8,953425 | 145,523288 | 295,523288 | 445,523288 |
| 2023 inicio | 5,144125 | 9,004815 | 145,497593 | 295,497593 | 445,497593 |

Estos máximos iguales tienen frontera **cerrada**: `m≤(W−maxδ)/2`, sólo cuando el numerador es no negativo. Sin imponer igualdad de márgenes, el requisito correspondiente es `m_A+m_V≤W−maxδ`. Para W=600 e inicio, eso significa justificar un presupuesto total de hasta 272,702854 segundos en 2019 y 590,995185 segundos en 2023. No exige conocer el tiempo exacto de cada columna: exige demostrar que todas las adquisiciones pertinentes quedan dentro de los márgenes declarados respecto de la referencia utilizada. Este cálculo no demuestra por sí mismo que exista tal cota ni la transfiere a futuros pareados de footprints.

En 2019 con W=300, todos quedarían fuera condicionalmente sólo si `m<11,994681` segundos con referencia central o `m<12,020376` con referencia de inicio. La frontera es **abierta**: `m<(minδ−W)/2`; en la igualdad el mínimo sería W y la conclusión uniforme de estar fuera ya no vale. En los demás casos no existe aquí una región de margen no negativo que garantice todos fuera.

En la grilla de supuestos para W=600, ambas referencias de 2019 dan `forall_within` hasta m=120 y dejan de resolverse uniformemente en m=180 y 300. Ambas referencias de 2023 dan `forall_within` hasta m=180 y dejan de resolverse uniformemente en m=300. Son contrastes aritméticos sobre supuestos, sin selección de modelos ni acreditación de exposición física.

## Reproducción, artefactos y verificación

Se generaron [120 filas de márgenes](evidence/scan-reference-margins/conditional-margins.csv), [12 requisitos de frontera](evidence/scan-reference-margins/tipping-requirements.csv) y un [JSON conjunto](evidence/scan-reference-margins/result.json). El [manifiesto](evidence/scan-reference-margins/manifest.json) registra hashes de los dos JSON fuente, protocolo, código y helper reutilizado, además de hashes de CSV/JSON y snapshots. Se incluyen snapshots del código, del helper `observation_qa.py` y del protocolo; ningún artefacto previo fue modificado.

```sh
python3 pipeline/scan_reference_margins.py
```

El comando reproduce los artefactos únicamente cuando la carpeta nueva de evidencia todavía no existe; rechaza sobrescribir evidencia existente. Para verificar un resultado ya presente, puede importarse `build_report` sobre los dos JSON y comparar su salida con `result.json`, sin escribir archivos.

La ejecución comprobó: números finitos/no negativos, extremos ordenados, forma de cuantiles, conteos compatibles con las asociaciones ya existentes, referencias conocidas y definición en TAI93. Los ejemplos sintéticos reutilizan `temporal_relation` en igualdad, exterior estricto e incertidumbre; confirman el límite cerrado de dentro y abierto de fuera. Se verificó que un margen desconocido no se sustituye por cero y que el aumento de márgenes sólo expande el sobre temporal y no recupera una resolución uniforme ya perdida. Se rechazan valores negativos, infinitos, NaN, booleanos y extremos invertidos. Los hashes de fuentes y artefactos y la reproducción en memoria del JSON completo se verificaron después de generar la evidencia.

La evidencia añade una meta cuantitativa para una futura justificación temporal. No asigna probabilidades, costes o valor económico de información, no establece un ranking obligatorio de investigaciones y no evalúa calibración, scores, detección, FRP, concordancia física o alertas. `physical_exposure_verified=false` y `gate1_passed=false` permanecen explícitos en las salidas.
