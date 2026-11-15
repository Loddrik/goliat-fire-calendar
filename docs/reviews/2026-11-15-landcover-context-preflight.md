# Preflight de contexto territorial — MCD12Q1.061, años nominales 2010 y 2001

**El catálogo y el coste permiten un piloto acotado de contexto retrospectivo. No permiten llamarlo información disponible antes de 2012.** La colección anual 2010 existe, requiere una sola tesela para las 54 comunas y ocupa 13.13 MiB según HEAD. Sin embargo, fue producida en 2022 y utiliza estabilización interanual: el año nominal anterior a los destinos no garantiza ausencia de información posterior. No se descargó ni abrió ningún raster, calcularon proporciones o ajustaron modelos.

## Identidad y disponibilidad comprobadas

La búsqueda pública CMR devolvió **`C2484079608-LPCLOUD`**, `MCD12Q1`, versión `061`, DOI [10.5067/MODIS/MCD12Q1.061](https://doi.org/10.5067/MODIS/MCD12Q1.061). No se eligió “latest” ni se confundió con MCD12C1 o la colección 006. La metadata indica producto anual desde 2001 y formato nativo HDF-EOS2/HDF4. Se conservaron el UMM completo de colección y los dos gránulos. [CMR colección](https://cmr.earthdata.nasa.gov/search/concepts/C2484079608-LPCLOUD.umm_json)

| Año nominal | Concept ID del gránulo | Tesela | Producción UTC | Bytes HEAD exactos | MiB |
|---|---|---|---|---:|---:|
|2010|`G2484150734-LPCLOUD`|`h12v12`|2022-06-09T09:16:28Z|13764955|13.1273|
|2001|`G2484181538-LPCLOUD`|`h12v12`|2022-05-26T05:11:51Z|16769989|15.9931|

Nombres exactos: `MCD12Q1.A2010001.h12v12.061.2022160091628.hdf` y `MCD12Q1.A2001001.h12v12.061.2022146051151.hdf`. Cada gránulo cubre enero–diciembre de su año nominal, no una medición instantánea del 1 de enero. Las fechas de producción pertenecen al reprocesamiento, no al período de observación. [CMR 2010](https://cmr.earthdata.nasa.gov/search/concepts/G2484150734-LPCLOUD.umm_json), [CMR 2001](https://cmr.earthdata.nasa.gov/search/concepts/G2484181538-LPCLOUD.umm_json)

Las dos consultas espaciales CMR devolvieron exactamente un gránulo por año. Se verificó además que el rectángulo completo de ambas geografías cae en `h12v12` mediante sus extremos proyectados; no se eligieron teselas por detecciones de fuego. La prueba de cuadrícula queda en `aoi-tile-proof.json`.

| Geografía completa 54 | Oeste | Sur | Este | Norte |
|---|---:|---:|---:|---:|
|DPA 2023|−73.973590|−38.492447|−70.982980|−36.005384|
|Legada de 21|−73.961443|−38.492463|−70.983273|−36.005560|

La guía C61 confirma compatibilidad de formato con C6. La cuadrícula sinusoidal usa esfera 6371007.181 m, píxel 463.312716525 m y 2400×2400 píxeles por tesela; 500 m es la denominación nominal. [Guía C61](https://lpdaac.usgs.gov/documents/1409/MCD12_User_Guide_V61.pdf)

## Coste y acceso: HEAD no equivale a adquisición

Se realizaron HEAD anónimos controlados: el enlace NASA original respondió 303 y el CDN devolvió 200 con los tamaños de la tabla. No se enviaron credenciales, siguieron flujos de cuenta, leyeron cuerpos HDF ni conservaron URLs firmadas. Los JSON guardan únicamente host CDN, estados, Content-Length y procedencia pública. El token Earthdata no se leyó.

Un año 2010 supone 13.13 MiB; sumar 2001 da **30534944 bytes = 29.12 MiB**. Cabe holgadamente en el presupuesto propuesto de **150 MiB exclusivo de cobertura terrestre**, separado del cap 400 MiB del piloto L2. Estos son bytes transferibles de los objetos HDF, no memoria de procesamiento; documentación y archivos de evidencia son independientes. El acceso final por GET, checksum del objeto y lectura de SDS todavía no se han probado. No se autoriza ni inicia una descarga con este preflight.

La lectura futura puede reutilizar el entorno HDF4 aislado ya existente, sin cambiar paquetes globales. La memoria y tiempo del overlay no se midieron; deben acotarse por ventanas de tesela y medir el coste real al ejecutar. No se propone descargar mosaicos globales ni incorporar años adicionales después de mirar errores.

## Esquema que debe validarse al leer

| Campo esperado | Uso propuesto | Rango documentado/fill |
|---|---|---|
|`LC_Type1`|Clasificación IGBP anual|uint8; 1–17; 255|
|`QC`|Estado de clasificación/correcciones|uint8; 0–10; 255|
|`LW`|Máscara tierra/agua|uint8; 1 agua, 2 tierra; 255|

Son campos documentados, no atributos observados en estos dos HDF todavía. QC es una leyenda categórica específica; no se aplica un decodificador de bits de otra colección. El estado 1 puede tener etiqueta barren pese a carecer de clasificación; 8 refleja backfill y 9 modificación de tipo forestal. Fill y estados desconocidos se mantienen separados. [Guía C61, tablas 1 y 11](https://lpdaac.usgs.gov/documents/1409/MCD12_User_Guide_V61.pdf)

La metadata también enumera esquemas alternativos y evaluaciones LCCS: una evaluación de `LC_Prop*` no se utilizaría como confianza universal de `LC_Type1`. Los nombres, dimensiones, proyección, rango, fill y leyenda deben comprobarse contra el archivo concreto antes de calcular características. [CMR colección](https://cmr.earthdata.nasa.gov/search/concepts/C2484079608-LPCLOUD.umm_json)

## Metodología de proporciones propuesta, antes de conocerlas

Para mantener el contrato de 21, propongo como geografía primaria **los 54 polígonos completos legados**, no las celdas que tuvieron detecciones ni las celdas con mapa científico disponible. Su fuente local es geoBoundaries/BCN 2020, según `pipeline/comunas.py`; se congela por hash. DPA 2023 sería una sensibilidad geográfica separada, definida antes de extracción y sin escoger la que produzca mejores errores. Usar DPA como primaria también sería posible, pero cambiaría la relación exacta con el mapa de 21 y requiere declararlo previamente.

Ambas son geografías retrospectivas posteriores a 2010; no se presentan como límites administrativos vigentes en ese año. Los hashes son:

- Legada: `6bfe6baebd6e56dad166851f4280a80115812d424ce253c3487350fcb5de8375`.
- DPA completa, verificada contra el manifiesto: `134981d8b085157d7e88ab5fa465d89935554640746b66129d63843a16e70602`.

Receta candidata fija:

1. Intersectar cada celda raster nativa con el polígono completo en la convención de área sinusoidal del producto; ponderar la fracción de intersección, especialmente en bordes y costa. No asignar por centro ni usar interpolación bilineal de categorías.
2. Conservar las 17 clases, QC, agua y área desconocida para cierre. Definir las tres variables solicitadas como área de píxeles clasificados bosque (códigos 1–5), cultivo (12) y urbano (13), dividida por el área total del polígono. Mosaico (14), agua (17) y otras clases quedan separados; 14 no se convierte íntegramente en agricultura. [Leyenda IGBP, guía C61](https://lpdaac.usgs.gov/documents/1409/MCD12_User_Guide_V61.pdf)
3. Exportar cobertura clasificable, agua/fill/desconocido y fracciones por QC. Un QC distinto de 0 no significa universalmente fallo. La política propuesta conservaría etiquetas entregadas con correcciones identificadas y separaría estados sin clasificación; un análisis conservador QC 0 sería sensibilidad declarada, no una regla NASA ni una alternativa elegida por desempeño.
4. Como salida secundaria, calcular fracciones sobre tierra clasificada válida, siempre junto a la fracción de territorio que retuvo ese denominador. Si no existe denominador válido, devolver NA explícito; nunca sustituirlo por 0. No renormalizar únicamente bosque/cultivo/urbano para que sumen 1.
5. Congelar mapeo de categorías, tratamiento exacto de QC y política de faltantes antes de extraer. El protocolo de ejecución debe enumerar qué valores acepta cada salida y exigir cierre de áreas, rechazo de códigos inesperados y pruebas sintéticas de costa/borde/fill/mosaico.

Estas proporciones describirían **área de categorías de un clasificador**, no porcentajes exactos de dosel, cultivo efectivo o impermeabilidad. No distinguen por sí solas plantación forestal de bosque nativo, prácticas de quema, combustible o causalidad del fuego. La agregación por comuna tampoco describe necesariamente el contexto específico de cada detección. El QC de cobertura terrestre no sustituye QA de incendios ni acredita nubes, tiempos o elegibilidad G1.

## Límite temporal y científico decisivo

La guía C61 describe estabilización multianual con HMM y desaconseja inferir cambios de cobertura mediante diferencias directas entre mapas anuales. Por ello, el mapa nominal 2010 reprocesado no certifica disponibilidad 2012 ni una ventana de entradas estrictamente anterior; 2001 reprocesado no resuelve esa garantía. [Guía C61, §1](https://lpdaac.usgs.gov/documents/1409/MCD12_User_Guide_V61.pdf)

La inferencia correcta es **contexto territorial retrospectivo externo al ajuste S-NPP local**. No usar etiquetas S-NPP held evita una vía concreta de contaminación; no prueba ausencia de información posterior en la covariable ni independencia física. Tampoco permite llamar a sus categorías “verdad ecológica”. La nota oficial sobre deterioro de la base de entrenamiento después de 2021 refuerza la decisión de no incorporar 2021 como contexto futuro de destinos 2012–2019, pero no certifica exactitud 2010. [NASA LDOPE, issue 781](https://landweb.modaps.eosdis.nasa.gov/displayissue?id=781)

2010 podría ser el mapa primario y 2001 una sensibilidad histórica definida ahora; **no se escogería año, geografía, QA o agrupación según cuál reduzca más el error**. Comparar sus proporciones sería sensibilidad del descriptor, no medición validada de cambio territorial.

## ¿Permite una prueba por contexto sobre cold-region 21?

Sí, con un protocolo nuevo y alcance retrospectivo. Una variable común conocida en SOURCE y held permite condicionar una distribución incluso cuando no hay parámetros locales del CUT. Los modelos seguirían aprendiendo exclusivamente de SOURCE×origen, conservando las cuatro direcciones, máscara de 21, todos los destinos y sus ceros/desconocidos.

Un contraste pequeño y explícito podría reutilizar las mismas distribuciones SOURCE y comparar **mezcla con pesos uniformes frente a mezcla con pesos definidos solo por semejanza de las tres proporciones**. E00 y M1 permanecerían controles adicionales. Comparar únicamente esa mezcla contextual con E00 confundiría la nueva ponderación con el cambio de representación de la mezcla; el control uniforme es necesario. La primaria sería held antes de reconciliar; la asignación 54 vendría después como análisis de acoplamiento.

Distancia, escala, regularización, tratamiento de faltantes y fallback fuera de soporte requieren fijarse antes de etiquetas destino. Cualquier escala o ajuste dependiente de datos se estimaría solo en SOURCE; las covariables held pueden utilizarse para inferencia y diagnóstico de soporte, no para escoger el resultado favorable. Sin soporte o con contexto desconocido, conservar fallback y banderas, evitando eliminar silenciosamente los territorios difíciles.

Esto probaría **utilidad predictiva del descriptor y de una política concreta de compartir información**, no causalidad, mecanismo ecológico verdadero, desempeño operacional ni independencia de todo el desarrollo. La factibilidad G0 de características aún requiere adquisición/lectura/overlay auditables; su variación y soporte común entre regiones no se han cuantificado en este preflight.

## Alternativa temporal si se exige producto publicado antes de 2012

**ESA GlobCover 2009 V2.3** tiene una procedencia temporal más clara: ESA documenta observaciones MERIS 2009 y publicación el 21 de diciembre de 2010, con resolución nominal 300 m. Es una alternativa independiente del clasificador MODIS para examinar antes de comprometer una afirmación as-of. [ESA, publicación 2010](https://www.esa.int/Applications/Observing_the_Earth/Envisat/ESA_unveils_latest_map_of_world_s_land_cover), [catálogo GlobCover](https://due.esrin.esa.int/page_globcover.php)

No se verificaron ahora tamaño, acceso del archivo global, subset reproducible, QA detallado ni correspondencia de leyendas para Chile. No se declara que quepa en 150 MiB ni se inicia una descarga. Las ecorregiones WWF 2001/RESOLVE 2017 serían otro tipo de descriptor biogeográfico, distinto de uso/cobertura observados; no se adquirió ni verificó un archivo exacto y no se propone como reemplazo automático.

## Evidencia y estado final

`docs/reviews/evidence/landcover-context-preflight/` conserva CMR UMM, consultas espaciales, HEAD iniciales/finales sin URLs firmadas, prueba de tesela para ambas geografías, fuentes, resumen y manifiesto con hashes. La respuesta redundante de búsqueda de colección se redujo a identidad y hash de su snapshot original; el UMM completo queda intacto. La evidencia JSON ocupa aproximadamente 56 KiB.

Estado: **catálogo/tamaño/acceso HEAD verificados; adquisición HDF, SDS reales, características, soporte contextual, ajuste y resultados aún no realizados.** No se usaron credenciales, descargaron productos, contaron clases o proporciones, modificaron modelos/publicación/resultados anteriores ni ejecutaron operaciones Git.
