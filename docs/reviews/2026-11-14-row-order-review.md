# Orden físico: métricas estables, ejemplos seleccionados variables

**La igualdad estricta de 118 resultados no pasa: 117 coinciden y el resumen geográfico cambia sus ejemplos.** Las predicciones, parámetros, métricas, compuertas diagnósticas, intervalos y figuras permanecen idénticos. Los demás campos del resumen geográfico también coinciden. Pasan los 90 tests.

El [protocolo](2026-11-14-row-order-protocol.md) baraja filas de cuatro Parquet en un checkout temporal, con semillas fijadas. La preparación estricta usa `pyarrow.Table.take` y verifica igualdad de esquemas completos, metadatos y nulabilidad; `EXCEPT ALL` en ambas direcciones confirma los mismos multiconjuntos. Los archivos originales permanecen intactos. La copia tiene modificaciones deliberadas y no se presenta como un checkout limpio.

Se recalcularon las 14 etapas 2–15. El único resultado no manifiesto diferente es `geography_audit/summary.json`: los escenarios con grilla decimal incluyen diez ejemplos de detecciones que cambian de celda. El código usa `head(10)` sin ordenar previamente, por lo que selecciona otros registros válidos al barajar la entrada. Al comparar por separado todos los demás campos, coinciden exactamente como valores JSON. Eso explica el fallo, pero **no convierte la prueba estricta fallida en aprobada**.

Se conservan los tres resúmenes geográficos (original y dos perturbaciones), los resultados comparados, las diferencias de manifiestos y los logs. El orden de ejemplos es una limitación del informe auxiliar histórico, distinta del orden de `recurrence` en la publicación, cuyo arreglo está en el PR #31. No se sobrescribe el informe geográfico original para forzar coincidencia.

Una preparación inicial con Pandas también conservó valores, pero modificó tipos físicos y nulabilidad. Se separa como diagnóstico combinado de orden/representación; no responde al protocolo de solo orden. También obtuvo 117 coincidencias y 90 tests, con la misma variación de ejemplos. La segunda preparación estricta mantiene el esquema y permite aislar la pregunta original.

[Evidencia estricta](evidence/2026-11-14/row-order-strict-reproduction.json), [insumos y esquemas](evidence/2026-11-14/row-order-strict-inputs.json), [diferencias de manifiestos](evidence/2026-11-14/row-order-strict-manifest-differences.json) y [diagnóstico combinado](evidence/2026-11-14/row-and-representation-reproduction.json). Los snapshots de los drivers ejecutados se conservan junto a la evidencia; contienen rutas locales que deben adaptarse para repetirlos.

No se produjeron nuevos scores de validación predictiva, ajustes candidatos o habilitaciones. La invariancia de resultados frente al orden es un control técnico y no valida equivalencia física entre sensores.
