# Nota documental: envolventes temporales por escaneo

14 de noviembre de 2026. Solo revisión documental: no se abrieron archivos satelitales, no se calcularon nuevos desfases ni se modificaron código, resultados o estado G1.

**Conclusión:** una envolvente conservadora por escaneo puede resolver el requisito temporal sin reconstruir el tiempo exacto de cada columna. Las fuentes recuperadas respaldan ese enfoque y la compatibilidad TAI93, pero no acreditan todavía que los extremos propuestos encierren toda la integración física de las bandas relevantes para el producto de fuego. La carencia es concreta: vincular las marcas temporales almacenadas con el principio y final de la adquisición física, sus offsets por banda y cualquier incertidumbre del reloj. No es necesario exigir precisión por píxel para solucionar esa carencia.

## Lo que está documentado

**MYD03:** la [especificación alojada en la ruta Collection 61](https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/61/MOD03), §3.1, identifica `EV start time` como “Earth view start time (TAI)”. La misma especificación separa información por escaneo, coordenadas por muestra y parámetros geométricos. Su versión interna es 6.0.3 de 2012; no debe confundirse la ruta web con una actualización documental integral de C6.1.

La [aclaración del equipo MODIS sobre MYD03](https://atmosphere-imager.gsfc.nasa.gov/issues/cloud) confirma que EV Start Time utiliza TAI con referencia al inicio de 1993 y que el nombre de archivo corresponde a UTC. Esto permite trabajar con diferencias nativas de tiempo una vez comprobada la misma época en ambos productos. No hace falta convertir esas diferencias a UTC ni restarles una constante de segundos intercalares. La aproximación de ~1,5 segundos discutida allí corresponde al nombre del granule; no es un margen documentado de exactitud del SDS ni debe transferirse automáticamente al intervalo de exposición.

**Arquitectura MODIS:** el [ATBD Earth Location versión 3.0, NASA, agosto de 1997](https://oceancolor.gsfc.nasa.gov/files/resources/docs/technical/atbd_mod28_v3.pdf), §3.1.1, pp.3-1 y 3-22–3-24, distingue ciclo de escaneo (~1,477 s), porción Earth-view (~0,451 s), comienzo del sector, tiempo del primer frame y tiempos de muestreo por banda. También distingue latch del detector y centro de integración. Los tiempos individuales dependen de posición de banda y retardos de lectura. Esta distinción impide asumir, solo por el nombre, que el SDS EV start sea exactamente el borde inicial de toda integración de todas las bandas. Los valores nominales describen el instrumento; no son por sí solos cotas operacionales certificadas para cada granule.

El [manual instrumental MODIS alojado por NASA](https://directreadout.sci.gsfc.nasa.gov/aqua_documents/MODIS_UG.pdf), §5.1, explica que en cada ciclo se observan sucesivamente sectores de calibración, espacio y Tierra. El inicio del ciclo se define por el sector solar diffuser, no por el sector Earth-view. Por tanto, no son intercambiables “comienzo de ciclo” y “EV start”. Esta fuente respalda una envolvente de ciclo como estrategia más amplia, pero no identifica por sí sola qué instante del procesamiento C6.1 representa cada SDS.

**VNP03IMG:** la [guía NASA VIIRS L1 de julio de 2017](https://oceandata.sci.gsfc.nasa.gov/files/resources/docs/technical/VIIRS_Level-1_DataProductUsersGuide.pdf), §4.3, define `scan_start_time` y `scan_end_time` como principio y final de escaneo, en segundos desde 1/1/1993. Su §4.5 distingue `ev_mid_time` y calidad de escaneo en el producto geográfico. Proporciona una base para usar el intervalo de escaneo nominal como envolvente; no especifica en ese párrafo si los extremos delimitan todo el ciclo o solamente el sector Earth-view, ni el margen de integración de todas las bandas.

La [guía NASA VIIRS L1B de agosto de 2021, versión archivada](https://ladsweb.modaps.eosdis.nasa.gov/api/v2/content/archives/Document%20Archive/Science%20Data%20Product%20Documentation/Processing%20and%20Algorithm%20Version%20History/NASA_VIIRS_L1B_UG_August_2021.pdf), §4.3, tabla 7, incluye para los productos geográficos VNP/VJ103IMG los tres campos de tiempo etiquetados TAI93, en segundos, con relleno −999,9. La tabla confirma etiquetas y unidades; no resuelve por sí sola la distinción ciclo/sector o la integración física. El contenido relevante se recuperó del índice de búsqueda de NASA; la descarga íntegra volvió a agotar el tiempo de espera. No se considera que el PDF entero haya sido validado.

Como contraste, la [especificación LAADS del producto radiométrico VNP02IMG](https://ladsweb.modaps.eosdis.nasa.gov/filespec/VIIRS/1/VNP02IMG.fs), §3, sí describe los extremos como comienzo y final del sector EV. Sin embargo, es **otro producto**, contiene una advertencia de cambio TAI93→TAI58 desde versión de software 3.0.0 y conserva algunas etiquetas antiguas. No se trasladará automáticamente esa definición al archivo geográfico Collection 2. Esta diferencia refuerza la necesidad de comprobar producto, colección, versión de procesamiento y época; los nombres parecidos no bastan.

## Qué permiten los dos intervalos propuestos

Para MODIS, `A[k] = [EVstart[k], EVstart[k+1]]`, excluyendo el último escaneo, es una **envolvente nominal entre referencias Earth-view consecutivas**. Bajo la condición de que toda adquisición asignada al escaneo k quede entre esas referencias, encierra sus muestras sin calcular tiempos por columna. La arquitectura secuencial del instrumento respalda esa condición a escala de sector; falta verificar la correspondencia exacta del SDS con los bordes de integración y los retardos del procesamiento. Excluir el último escaneo evita inventar un siguiente inicio, pero no demuestra por sí mismo aquella condición.

Para VIIRS, `V[j] = [scan_start[j], scan_end[j]]` es un **intervalo nominal de escaneo documentado**. Tanto un ciclo completo como su sector EV podrían servir como envolvente suficiente si se confirma que contienen las adquisiciones relevantes. El requisito científico es esa inclusión, no preferir necesariamente el intervalo más estrecho. Sigue pendiente documentar inclusión de todos los canales utilizados, integración y precisión de los extremos para el geolocalizador de la colección fijada.

Si se documentan límites máximos de offsets o error de reloj, se pueden ampliar los extremos con márgenes explícitos. No introducir aquí un margen arbitrario de 1,5 segundos, un período nominal o una multiplicación de duración para declarar conservadurismo. Un margen puede ser amplio y útil, pero su capacidad de cubrir la adquisición debe estar justificada.

## Prueba temporal que puede preregistrarse después

Sean dos envolventes acreditadas `A=[a0,a1]` y `V=[v0,v1]`. El máximo desfase posible entre adquisiciones incluidas es:

`d_max = max(|a0 − v1|, |a1 − v0|)`.

El mínimo es `d_min = max(0, a0 − v1, v0 − a1)`. Con ventana predeclarada W: compatible si `d_max ≤ W`; fuera si `d_min > W`; incierto en el resto. Esta es una propiedad de intervalos, no una medición nueva del caso. Una vez acreditada la inclusión física, basta para comprobar una ventana temporal sin conocer la columna exacta.

Antes de usarla: rechazar rellenos/no finitos, orden inválido, escaneos de integridad o modo no aceptado, épocas incompatibles y márgenes desconocidos. Excluir el último MODIS si no existe siguiente referencia; no extrapolar. Las interrupciones o escaneos ausentes deben conservar su trazabilidad; no sustituir tiempos desconocidos por cero.

**Decisión recomendada ahora:** conservar los intervalos como candidatos de diseño y, si se estudian, etiquetarlos como envolventes nominales pendientes de acreditación de exposición. La siguiente búsqueda debe concentrarse en la definición de generación de los SDS y límites de retardos/incertidumbre del reloj, no en exigir una tabla temporal de cada píxel. Esta nota no habilita ejecutar un análisis nuevo ni cambiar G1. Footprints comunes y elegibilidad QA/global siguen siendo requisitos independientes.
