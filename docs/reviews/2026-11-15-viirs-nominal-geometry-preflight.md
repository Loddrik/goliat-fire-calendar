# Preflight de referencia geométrica nominal VIIRS

15 de noviembre de 2026. Revisión de cabeceras locales, esquema L2 y documentación primaria. No se leyeron registros CSV, arrays de fuego, valores de clasificación o asociaciones positivas. No se calcularon nuevas geometrías, errores o gates. No se llamó a la API FIRMS ni se accedió a su clave.

**Hay una vía viable para contrastar dimensiones nominales VIIRS sin exigir una PSF exacta:** los CSV existentes tienen columnas `scan` y `track`. Una consulta futura, fijada por protocolo, podría contrastarlas selectivamente con la geometría del mismo instrumento/caso. Además, el ATBD NASA contiene una tabla explícita de agregación para I-band: ya no es necesario inventar límites copiando columnas M-band. Esto no convierte los tamaños FIRMS de detecciones en un denominador de observación de toda la escena.

## 1. Qué confirman las cabeceras locales

Se abrió únicamente la primera línea de cada archivo `observed/dist/data/history/snpp-history/*.csv`. Las cabeceras inspeccionadas comparten este esquema; ejemplo: `08101.csv`.

```text
latitude,longitude,acq_date,acq_time,satellite,instrument,confidence,version,
brightness,bright_ti4,bright_t31,bright_ti5,scan,track,frp,daynight,type,
cut_com,comuna,grid_x,grid_y,source_file
```

SHA-256 de la línea de cabecera original del ejemplo:

```text
0e2c29e68a01197f8f4c3f375b164a68b08f6ca2a393e956da00e4473ecfd90f
```

Existen campos para dimensiones, coordenadas, fecha/hora, satélite, instrumento, versión y procedencia. **No se comprobó que las columnas tengan valores**, que los registros cubran el caso de 2023, que su fuente sea el procesamiento estándar compatible ni que `source_file` identifique un granule L2 concreto. Los nombres de carpeta y columna no certifican esas propiedades.

No hay columnas `FP_line`/`FP_sample` en esta cabecera. Una comparación posterior necesitaría correspondencia inequívoca de fecha, satélite, producto y centro geográfico, con tolerancia de redondeo predeclarada; la hora FIRMS no se convertirá en tiempo físico exacto por píxel. No se deberá inventar el índice nativo si la asociación resulta ambigua.

## 2. Agregación I-band documentada, sin trasladar índices M-band

El [ATBD NASA revisado de geolocalización VIIRS de 2014](https://ladsweb.modaps.eosdis.nasa.gov/api/v2/content/archives/Document%20Archive/Science%20Data%20Product%20Documentation/Product%20Generation%20Algorithms/NASARevisedVIIRSGeolocationATBD2014.pdf), §§3.3.2.1.2–3.3.2.1.3, pp.50–56, da explícitamente 12.608 muestras originales y 6.400 muestras I-band agregadas. Su tabla de frames I-band usa índices desde uno:

| Agregación nominal | Frame I-band en la tabla NASA | Columna equivalente desde cero |
| --- | --- | --- |
| 1:1 | 1–1.280 | 0–1.279 |
| 2:1 | 1.281–2.016 | 1.280–2.015 |
| 3:1 | 2.017–4.384 | 2.016–4.383 |
| 2:1 | 4.385–5.120 | 4.384–5.119 |
| 1:1 | 5.121–6.400 | 5.120–6.399 |

La conversión de la última columna es aritmética, restando uno a cada límite. La tabla I-band establece pasos entre centros agregados de `1`, `2` o `3` períodos de muestra, con pasos de `1,5` o `2,5` en transiciones. El período nominal especificado es 44,1295 μs. Es una referencia nominal de arquitectura, no una lectura de LUT de calibración del granule C2.

El [ATBD de Imagery VIIRS de NOAA, revisión E](https://www.star.nesdis.noaa.gov/jpss/documents/ATBD/D0001-M01-S01-008_JPSS_ATBD_VIIRS-Imagery_E.pdf), §3.2.4, explica específicamente la agregación I-band de tres, dos y una muestras y los cambios nominales cercanos a 31,59° y 44,68°. Son ángulos instrumentales de escaneo: no equivalen a los ángulos cenitales de superficie del GEO.

La [guía NASA VIIRS L1 de 2017](https://oceandata.sci.gsfc.nasa.gov/files/resources/docs/technical/VIIRS_Level-1_DataProductUsersGuide.pdf), tabla 4 y §4.2, confirma 32 detectores I-band y 6.400 muestras agregadas, frente a 16 y 3.200 para M-band. No se deben usar directamente los índices M-band, ni una relación lineal `ángulo ∝ columna agregada` sobre todo el scan: el cambio de agregación altera ese espaciamiento.

Esto permite implementar y probar una función pura `aggregation_I(sample)` y una referencia de separación angular nominal por regiones, antes de nuevos datos. Una dimensión terrestre en metros necesita además una geometría de proyección del detector y parámetros nominales respaldados; la tabla de agregación por sí sola no proporciona ambos tamaños del píxel. Se debe registrar la diferencia entre parámetros nominales y calibración C2, sin exigir recuperar toda la PSF para una comparación de ingeniería.

## 3. GSD/HSI y dimensión nominal del detector

El [trabajo primario de caracterización geométrica de NASA/GSFC](https://ntrs.nasa.gov/api/citations/20120009053/downloads/20120009053.pdf) distingue respuesta espacial, DFOV a lo largo del escaneo e IFOV en dirección de track. La distancia entre centros o HSI describe el muestreo; una celda obtenida por puntos medios no es automáticamente la extensión de la respuesta del detector.

El benchmark CORE anterior sí puede contrastarse con dimensiones nominales proporcionadas por otro producto, identificando esa diferencia de definición. Un acuerdo mostraría consistencia entre representaciones en esas posiciones; no prueba bordes ópticos exactos. Un desacuerdo tampoco demostraría por sí mismo que alguna detección de fuego sea falsa.

La ausencia de saltos de espaciamiento en las ventanas ya estudiadas no certifica que toda la geometría de agregación esté verificada. La tabla I-band permite un diagnóstico explícito de regiones nativas en una etapa posterior; no autoriza retocar la regla de saltos ya aplicada o volver a evaluar gates antiguos con nuevos umbrales.

## 4. Esquema real de los dos L2 ya adquiridos

Se abrieron los archivos VNP14IMG existentes de 2019 y 2023 **solo como metadatos HDF5**: nombres de datasets y atributos descriptivos de `FP_line`/`FP_sample`. No se leyeron sus arrays, longitudes de detecciones ni atributos globales de conteos.

En ambos están presentes `FP_line` y `FP_sample`, descritos como línea y muestra del granule. No se encontraron datasets de nivel superior cuyo nombre contenga `area`: en particular, no aparece allí `FP_area` o `PixArea`. No se infiere un área a partir de `FP_power` u otros valores radiométricos.

La [guía VIIRS 375 m C2 v1.0 de 2024](https://www.earthdata.nasa.gov/s3fs-public/2024-07/VIIRS_C2_AF-375m_User_Guide_1.0.pdf), tabla 3, documenta `FP_line` desde 0 hasta `32*N−1` y `FP_sample` desde 0 hasta 6.399, de modo que ambos son índices desde cero. Esa tabla L2 no enumera un campo `FP_area`. La tabla del producto mensual `VNP14IMGML` sí incluye `PixArea`, en km²: **es otro formato de producto**, no un campo disponible automáticamente para todos los centros del L2. Tampoco prueba área independiente de detecciones sin fuego.

## 5. Uso correcto de scan/track FIRMS para el caso de 2023

La [descripción oficial FIRMS VIIRS](https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html) define `scan` y `track` como tamaños along-scan y along-track del píxel, que varían respecto del nominal de 375 m. La [explicación de NASA sobre esos campos](https://forum.earthdata.nasa.gov/viewtopic.php?t=5157) confirma que reflejan dimensiones espaciales. La orientación debe venir de la geometría nativa, no suponerse alineada con norte/este en el mapa.

**Sí pueden servir para un chequeo selectivo de consistencia en 2023**, sujeto a un protocolo nuevo. Sería una asociación dentro de S-NPP entre el registro FIRMS y el centro/malla nominal correspondientes, no una comparación de positivos MODIS–VIIRS ni una medición de sensibilidad de fuego.

El protocolo debería fijar antes de leer filas:

1. Caso y fecha/instante previstos, límites espaciales y producto S-NPP I-band; procedencia y versiones admisibles. No seleccionar registros por confianza, FRP o qué asociación produce menor error geométrico.
2. Tratamiento de valores vacíos, unidades, formatos de hora y precisión de coordenadas. La presencia de columnas no reemplaza estas comprobaciones.
3. Regla de asociación geográfica/temporal única y tolerancia justificada por precisión/convención del archivo. Coincidencias múltiples, ambiguas o fuera del CORE quedan pendientes, nunca se sustituyen por un punto más favorable.
4. Contraste scan/track/área nominales y denominador de registros efectivamente comprobables, conservando todos los fallos o casos no asociables. Los umbrales deben fijarse para esta comprobación, sin reinterpretar retrospectivamente los gates ya publicados.
5. Alcance: `selective_firms_size_consistency`, no certificación de dimensiones para todos los píxeles, IFOV exacto o verdad física de fuego. La geometría FIRMS puede compartir modelos instrumentales de origen; no sería validación independiente.

No existe una razón para exigir PSF perfecta antes de ese chequeo. Sí existe una razón para limitar su conclusión al dominio muestreado: FIRMS contiene detecciones, no todos los centros observables y no observables. Los registros no comprobables deben conservarse y no rellenarse con dimensiones inferidas de los positivos vecinos.

## 6. API: alternativa todavía no necesaria

Como el esquema local contiene los campos geométricos, no se llamó a la API ni se consultó la clave privada. Si un protocolo posterior encuentra que los campos están vacíos o no cubren el caso, la [documentación oficial de FIRMS API](https://firms.modaps.eosdis.nasa.gov/api/area/) permite definir una consulta por fuente, área, fecha y duración. El esquema VIIRS documentado incluye coordenadas, `scan`, `track`, fecha/hora, satélite y versión.

Cualquier consulta futura debe verificar primero disponibilidad del día y procesamiento históricos requeridos, y fijar fuente, rango temporal y presupuesto antes de ejecutarse. Esta revisión no presupone que el endpoint de área sirva el caso de 2023 con la misma versión que el L2 adquirido. La clave de `.runtime/secrets/firms-map-key` permanecería privada; el endpoint incorpora la clave en la ruta, por lo que **no basta con eliminar el query string** para redactar URLs FIRMS. El descargador Earthdata existente no debe reutilizarse ciegamente para persistir esos endpoints. Haría falta un adaptador que redacte el segmento de clave, omita excepciones/URLs sensibles y guarde solo parámetros públicos y hashes. Nada de eso se ejecutó en este preflight.

**Siguiente paso recomendado:** protocolo de comprobación selectiva usando primero CSV locales, con asociación inequívoca y sin nuevos downloads. En paralelo puede desarrollarse la función I-band nominal a partir de la tabla primaria, explicitando qué parte es muestreo y qué parte aún necesita una referencia dimensional. Esto acota el pendiente VIIRS sin modificar métricas anteriores ni declarar G1 verdadero.
