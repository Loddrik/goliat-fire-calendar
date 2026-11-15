# Recuperación de crudos: auditoría aislada de ingestión de 38 archivos exactos

**Resultado: integridad de fuentes y controles de parser verificados; la comparación exacta de detecciones falla en una fila por lado por un empate no resuelto de deduplicación.** No se declara reproducción completa del pipeline. El resultado original de 13 columnas permanece fallido aunque una proyección posterior a celdas-día coincida.

Se auditó exclusivamente el conjunto de 38 copias locales previamente identificadas por tamaño y SHA256 contra `inventory.csv`: MODIS 2002–2025 y VIIRS S-NPP 2012–2025, con 48448231 bytes. No se descargó nada ni se reconstruyeron archivos a partir de derivados. El protocolo, código, fuentes, entorno e inputs protegidos se congelaron **antes de cargar filas**; la ejecución terminó a 13:06:42.975482 UTC del 15 de noviembre de 2026. Deadline propio 13:23, dentro de la autorización global 12:59:41–13:29:41.

## Completitud decidida antes de comparar

El inventario muestra que las fuentes API de MODIS y S-NPP empiezan en 2026. Por eso las 38 fuentes seleccionadas cubren todas las entradas inventariadas que pueden aportar a Terra/Aqua 2002–2025 yS-NPP 2012–2025. La declaración es **completitud relativa al inventario**, no prueba de que NASA observó todos los días o de que cada archivo contenga todo el fuego.

La referencia no se filtró por `source_kind=country_sp` para hacerla coincidir: incluyó todas las detecciones de esas plataformas/fechas. Se comparó el bbox completo original, no sólo registros asignados a las 54 comunas. Tampoco se agregaron fuentes después de conocer el resultado. Recuperaciones adicionales pertenecen al manifiesto general de raíz y no amplían retroactivamente esta auditoría.

## Método y controles

No se importó `build_detections.py`, pues abriría y modificaría `goliat.duckdb`. Se implementó su SQL equivalente en DuckDB **`:memory:`**, con salida de trabajo sólo en `.runtime/raw-recovery/ingestion-audit/`. Los hashes de canónicos, base, parámetros, gates y JSON públicos permanecieron iguales.

Se conservaron estrictamente lectura CSV como strings, uniones por nombre, fecha UTC, padding de hora, bbox y filtro diurno; normalización de satélite; prioridad de fuente; deduplicación por satélite, coordenadas redondeadas a cuatro decimales, fecha y hora; y confianza **después** de elegir el ganador. La comparación primaria fue multiset `EXCEPT ALL` en ambos sentidos sobre:

`lat, lon, acq_date, acq_time, sat, instrument, confidence, frp, type, version, source_kind, cell_x, cell_y`.

No se añadió redondeo, tolerancia o nuevo desempate para obtener igualdad. Los conteos, fechas mínima/máxima y hashes de los 38 CSV coincidieron con su inventario. Resultado de las etapas:

| Etapa | Filas |
|---|---:|
|Crudos completos de los 38 archivos|604800|
|Diurnos dentro del bbox|188588|
|Con confianza aceptada antes de deduplicar|171823|
|Ganadores de deduplicación antes del filtro de confianza|188587|
|Detecciones finales reconstruidas|171822|
|Referencia canónica del mismo alcance|171822|
|Reconstruidas menos canónicas, EXCEPT ALL|1|
|Canónicas menos reconstruidas, EXCEPT ALL|1|

La misma cantidad no prueba igualdad de contenido. Las filas distintas son:

|Campo|Ganador reconstruido|Ganador canónico|
|---|---:|---:|
|Plataforma/fecha/hora|SNPP 2017-01-26 19:33|SNPP 2017-01-26 19:33|
|Latitud|−36.91106|−36.91114|
|Longitud|−72.57348|−72.57353|
|FRP|70.66|67.6|
|Celda|−7258,−3692|−7258,−3692|

Ambos registros están en el mismo CSV 2017 con SHA256 `3241722a7abd3e230ec6745eda70476e5707d488e621d2da9d39b6274b86a5bc`. Tienen confianza `n`, tipo 0, versión 2 y prioridad `country_sp`. Sus coordenadas completas son distintas, pero al redondearlas a cuatro decimales caen en la misma clave. Es el único grupo repetido observado, con dos contenidos distintos.

El SQL original usa `row_number() ... order by prio` sin un desempate dentro de la misma prioridad. **Ambos ganadores son compatibles con esa regla incompleta.** Esto localiza una falta de determinismo/reproducibilidad; no demuestra corrupción de los crudos ni cuál registro representa mejor la realidad. Tampoco decide si los dos registros deben ser el mismo evento: eso exigiría otra regla y evidencia, no elegir después el que hace pasar la comparación.

## Diagnóstico posterior, sin rescatar la primaria

Un diagnóstico separado, con código e inputs propios congelados, verificó ambos candidatos en el crudo y dos proyecciones del mismo conjunto:

- Al omitir solamente latitud, longitud y FRP, `EXCEPT ALL` da 0 en ambos sentidos.
- La proyección distinta `(sat,cell_x,cell_y,acq_date)` también da 0 en ambos sentidos.

Esto acota la discrepancia: en este subconjunto el ganador alternativo conserva la celda-día registrada y otros atributos comparados. **No sustituye la primaria de 13 columnas ni demuestra que se hayan rehecho máscaras, calibraciones o resultados desde todos los crudos.** No se modificó el canónico ni se aplicó un tie-break nuevo.

## Riesgos que permanecen

1. La deduplicación implementada redondea coordenadas; la descripción abreviada “lat/lon/fecha/hora” no muestra esa pérdida de información. Una regla futura debe declarar colisiones y desempates antes de ejecutar, sin elegirlos para favorecer un archivo canónico existente.
2. La prioridad opera por clave de detección, y el filtro de confianza se aplica después del ranking. Esta auditoría sólo contiene `country_sp`: no prueba el comportamiento comparativo de API-SP/NRT ni la conveniencia científica de ese orden.
3. Los canónicos no son invertibles: eliminan registros nocturnos, externos, filtrados o no ganadores y no conservan todos los campos de los CSV. No se pueden fabricar originales ausentes con su mismo SHA a partir del Parquet ni confundir una descarga actual con el archivo histórico requerido.
4. No se ensayó asignación espacial a comunas, máscara, agregados mensuales, ajuste o publicación. El conjunto 38 no incluye Terra 2000/2001 ni NOAA-20/21. Para la máscara heredada importa el corte `acq_date < 2020-07-01`, aplicado a todas las plataformas disponibles: faltan los registros Terra anteriores y NOAA-20 de ese intervalo. El inventario sitúa NOAA-21 desde 2023, por lo que no aporta a esa máscara anterior a 2020, aunque sí a la ingestión completa posterior. Un inventario de recuperación posterior puede cambiar qué archivos están disponibles, pero no lo que se utilizó aquí.
5. Una igualdad de proyecciones es ingeniería del registro, no validación del fuego, superficie quemada, oportunidad observacional o equivalencia física de sensores.

Los próximos pasos útiles son preservar las fuentes exactas y este fallo; completar el inventario faltante y, por separado, acordar una política determinista de deduplicación. No se autoriza un cambio de datos/modelos ni se presenta el hallazgo como una mejora de precisión.

## Evidencia

El [protocolo](evidence/raw-ingestion-recovery/protocol.json), [freeze público](evidence/raw-ingestion-recovery/freeze-public.json), [código congelado](evidence/raw-ingestion-recovery/audit-code.py.txt), [resumen primario](evidence/raw-ingestion-recovery/summary.json) y [manifiesto](evidence/raw-ingestion-recovery/manifest.json) conservan el resultado. El [diagnóstico del empate](evidence/raw-ingestion-recovery/tie-diagnostic.json) y su [manifiesto separado](evidence/raw-ingestion-recovery/diagnostic-manifest.json) quedan explícitamente posteriores a la primaria.

Freeze principal SHA256 `81c4cbb1d96f4fa259cc38b5ccac1f42aefa995c9b699f1dd132559dcef42ad3`. Se utilizaron DuckDB y el intérprete del venv del proyecto; el RSS observado fue 483999744 bytes. No hubo fits, descargas, importación del pipeline con efectos, apertura de la base original ni escrituras de producción. Los ajustes de sintaxis del código ocurrieron en el preflight antes del freeze/lectura de filas, sin modificar reglas ni reiniciar el plazo.
