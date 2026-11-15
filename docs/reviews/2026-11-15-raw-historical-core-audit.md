# Núcleo histórico desde crudos exactos: máscara y conteos reproducidos con límites

**Resultado mixto:** la detección exacta de 13 columnas conserva un fallo de una fila por lado; la máscara histórica y los conteos mensuales de entrenamiento coinciden exactamente en el alcance declarado. No se modifica ni rescata el resultado de la auditoría inicial 38.

Esta ampliación fue autorizada prospectivamente durante la ventana de recuperación. Antes de leer filas, se comprobaron 205 fuentes contra tamaño/SHA256 del inventario y se congelaron protocolo/código/inputs: 40 archivos país MODIS/S-NPP y 165 API NOAA-20 históricos. Se comprobó que ninguna entrada inventariada con filas potenciales anteriores a 2020-07-01 quedaba sin fuente exacta. Los archivos país posteriores incluidos en ese conjunto no aportan a los filtros históricos. La completitud sigue siendo relativa al inventario, no una certificación de oportunidades físicas de observar.

Freeze SHA256 `2c7032da 0bfaf6f8617af401c47bba8ac365955105368e14d652f6001f9ecb31`. La ejecución terminó a 13:19:52.354892 UTC del 15 de noviembre de 2026, antes del límite propio 13:23 y sin ampliar el plazo global.

## Qué se reprodujo

Se ejecutó SQL equivalente de ingestión en DuckDB `:memory:` con las fuentes exactas, filtros originales, ranking por prioridad antes de confianza y sin nuevo desempate. No se importaron scripts con efectos ni se abrió `goliat.duckdb`. La comparación primaria incluyó todas las detecciones con `acq_date < 2020-07-01`, antes de selección comunal:

| Comparación | Resultado |
|---|---:|
|Detecciones reconstruidas anteriores al corte|125740|
|Detecciones canónicas del mismo corte|125740|
|EXCEPT ALL reconstruidas−canónicas, 13 columnas|1|
|EXCEPT ALL canónicas−reconstruidas, 13 columnas|1|

La igualdad del número de filas no convierte esa primaria en un pase. La fase 38 ya documentó un empate no idéntico por coordenadas redondeadas y prioridad sin desempate. Aquí no se guardaron ejemplos individuales de las diferencias históricas, por lo que no se atribuye automáticamente este nuevo par de diferencias al mismo registro.

Para la máscara se extrajeron por AST **sólo los tres literales SQL originales** `cell_stats`, `static_core` y `static_mask` de `build_mask.py`; se ejecutaron contra la ingestión privada. Se conservaron corte 2020-07-01, plataformas disponibles, conteos de días/temporadas, tipos, umbrales y buffers originales. No se importó el módulo ni se reescribieron sus reglas.

La máscara resultante tiene **223 filas y 223 celdas únicas**. `EXCEPT ALL` de `(cell_x,cell_y,rule)` da 0 en ambos sentidos frente a `static_mask.parquet`; también coincide la proyección de celdas únicas. Esto reproduce la máscara en este núcleo histórico sin exigir que todas las coordenadas/FRP de detecciones sean idénticas.

## Conteos de entrenamiento, condicionados al mapa existente

Se reutilizó **`cells_comuna.parquet` congelado**: no se reconstruyó la cartografía, STRtree, pertenencia de centroides o decisiones fronterizas. Con esa condición se deduplicaron celdas-día, se aplicó la máscara reconstruida y se agregaron Aqua/S-NPP por comuna/mes/temporada 2012–2019.

Los conteos coinciden exactamente, con `EXCEPT ALL` 0/0, frente a las correspondientes filas de `celldays_comuna_month_masked.parquet`. Los totales son Aqua 9123 y S-NPP 21466. Su razón aritmética es **2.352954072125397**, exactamente el factor conservado en `params.json`. No se ejecutó un ajuste, selección, LOSO o publicador: esta identidad verifica conteos y una división ya definida, no una nueva evaluación del modelo.

## Qué no queda acreditado

El resultado no reproduce toda la adquisición 2026, NOAA-21, la asignación geográfica ni todos los productos públicos desde originales. Tampoco acredita observabilidad, fuego verdadero, equivalencia física o un holdout nuevo. La detección de 13 columnas sigue fallando; las coincidencias de máscara y conteos no autorizan cambiar esa primaria ni corregir silenciosamente el canónico.

Todos los hashes protegidos de entradas/canónicos permanecieron iguales al terminar. No hubo descargas, fits, ejecución LOSO, modificaciones de parámetros/gates o escritura de producción. Las salidas 38 se preservaron sin cambios. Esta evidencia permite una afirmación acotada: **con 205 fuentes exactas y el mapa comunal ya existente se reproducen la máscara histórica y los conteos de entrenamiento, pese a una discrepancia de representación en detecciones**.

[Protocolo](evidence/raw-historical-core-audit/protocol.json), [freeze de fuentes](evidence/raw-historical-core-audit/freeze.json), [código congelado](evidence/raw-historical-core-audit/code.py.txt), [resumen](evidence/raw-historical-core-audit/summary.json) y [manifiesto](evidence/raw-historical-core-audit/manifest.json) conservan el alcance y ambos desenlaces. La restauración general de archivos y su inventario final se auditan por separado.
