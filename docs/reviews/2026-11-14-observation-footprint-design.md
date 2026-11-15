# Soporte espacial nominal: aproximación geométrica comprobable

14 de noviembre de 2026. Estudio documental y propuesta de método. No se abrieron archivos satelitales ni se calcularon polígonos, áreas, intersecciones, clasificaciones cruzadas o nuevas métricas. G1 permanece falso.

**Sí es viable construir un soporte espacial aproximado y validable con los geolocalizadores disponibles.** No hace falta resolver exactamente la respuesta óptica de cada detector. Hace falta declarar qué representa el polígono nominal, respetar la geometría de escaneo, comprobar sus dimensiones y cuantificar cuánto cambian las intersecciones bajo alternativas razonables. La precisión aceptable debe corresponder a la escala de la pregunta, no a una exigencia imposible de bordes físicos perfectamente definidos.

## Qué aportan las fuentes primarias

La [descripción NASA de MOD03/MYD03](https://modis.gsfc.nasa.gov/data/dataprod/mod03.php) identifica posiciones de centros de IFOV de diez detectores de una banda ideal de 1 km. La cabecera permite aproximar centros de otras bandas; no promete esquinas físicas por píxel. La diferencia entre la banda ideal y las bandas utilizadas por fuego debe entrar en la incertidumbre geométrica.

La [especificación MOD03/MYD03 servida en la ruta 61](https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/61/MOD03), §§2–3, enumera centros, ángulos, rango, modelo de detectores/bandas y offsets de mayor resolución. Sus `Scan offsets`, `Track offsets` y `Height offsets` corresponden a geolocalización subpíxel de 500 m; **no son cuatro esquinas de cada píxel de fuego de 1 km**. El documento interno sigue siendo versión 6.0.3 de 2012, por lo que hay que verificar correspondencia de campos con el archivo 061. No se encontró una matriz de cuatro corners por píxel en ese esquema.

La [guía MODIS C6/C6.1 v1.0](https://modis-fire.umd.edu/files/MODIS_C6_C6.1_Fire_User_Guide_1.0.pdf), §8.4.6, p.53, proporciona dimensiones aproximadas along-scan y along-track en función de la columna nativa: `A_nominal ≈ ΔS(sample) × ΔT(sample)`. Advierte que esas aproximaciones tienen menos error que el supuesto de bordes perfectamente nítidos. Es un respaldo directo para una representación nominal, con límites explícitos, sin exigir una PSF exacta. Las fórmulas son MODIS y no se deben trasladar a VIIRS ni confundir ángulo de escaneo instrumental con ángulo cenital de observación.

La [página NASA LAADS de VNP03IMG Collection 2](https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP03IMG) describe coordenadas geodésicas, ángulos, altura, rango, máscara de superficie y calidad por muestra. La [especificación histórica del producto](https://ladsweb.modaps.eosdis.nasa.gov/filespec/VIIRS/1/VNP03IMG.fs) añade navegación y parámetros por escaneo; no se encontró un array de esquinas por píxel. Esa especificación es Collection 1 y no acredita por sí sola la continuidad de cada parámetro de C2.

El [ATBD NASA revisado de geolocalización VIIRS, julio de 2014](https://ladsweb.modaps.eosdis.nasa.gov/api/v2/content/archives/Document%20Archive/Science%20Data%20Product%20Documentation/Product%20Generation%20Algorithms/NASARevisedVIIRSGeolocationATBD2014.pdf), §§2.2.1–2.2.2 y 3.3.2.1, distingue respuesta espacial, centro del píxel agregado, integración y separación entre muestras. Documenta agregación, crecimiento fuera de nadir y solapamiento bowtie. Esto respalda separar el espaciamiento entre centros de la extensión nominal del detector. No convierte un punto medio entre vecinos en un límite óptico verdadero. Es un ATBD de arquitectura y algoritmo, no una garantía de calibración exacta de cada adquisición de C2.

## Método recomendado: dos aproximaciones geométricas que se contrastan

Se propone una etapa nueva, exclusivamente geométrica y anterior a usar resultados de actividad. Los métodos siguientes son decisiones de implementación propuestas; no se presentan como un algoritmo de corners certificado por NASA.

**A. Malla nominal derivada de centros dentro del escaneo.** Usar latitud/longitud nativas válidas y convertir a un sistema métrico local, conservando fila, columna, escaneo y detector. Dividir en bloques de diez filas MODIS o 32 filas VIIRS. Construir vértices interiores en las posiciones de media fila/media columna mediante promedio de los cuatro centros vecinos del mismo bloque. Cada píxel interior toma sus cuatro vértices de esa malla compartida; así se evitan bordes inconsistentes entre polígonos vecinos de un mismo bloque.

La regla produce exactamente la celda esperada en una malla afín regular y aproxima una malla suave deformada. No basta con promediar longitudes/latitudes en grados o con crear cuadrados de 1.000/375 m. En el ámbito chileno se puede usar la proyección UTM 18S ya fijada, verificando posteriormente dimensiones y áreas con geodesia elipsoidal.

**Fronteras de escaneo:** nunca usar la última fila de un escaneo y la primera del siguiente como vecinos de una malla continua. La proximidad debida a bowtie haría que esa regla redujera artificialmente el ancho along-track. En el primer ensayo, conservar el núcleo con vértices sustentados por vecinos internos y marcar bordes como `geometry_edge_unresolved`. Una extensión posterior puede usar extrapolación unilateral con los dos o tres centros internos más próximos, guardando `edge_extrapolated=true` y evaluándola por separado. Excluir el borde inicial no debe convertirse en una política permanente sin medir su efecto geométrico.

**Transiciones y huecos:** no construir vértices atravesando coordenadas faltantes, cambios de agregación no tratados o saltos geométricos. Los cambios de agregación VIIRS deben identificarse mediante índices/modelo documentado de la colección o diagnósticos geométricos preregistrados. No adoptar sin comprobar un conjunto de columnas de otra resolución. No interpolar filas eliminadas por bowtie como si contuvieran observaciones: geometría y disponibilidad de medición son decisiones distintas.

**B. Polígonos orientados de dimensión nominal como control.** Derivar orientación local along-scan/along-track con vecinos internos al mismo escaneo. Para MODIS, usar las dimensiones analíticas de la guía en cada columna, con convenciones de índice verificadas. Construir un rectángulo tangente orientado, explicitando la aproximación de ortogonalidad; compararlo con los cuadriláteros A. Para VIIRS, usar dimensiones respaldadas por su modelo de agregación/ángulo o por un producto de geometría apropiado; si falta esa parametrización, dejar B pendiente para VIIRS y no sustituirlo por un cuadrado constante.

Una implementación de ray tracing completo usando actitud, órbita, LUT de geolocalización, geometría óptica y DEM puede ser una referencia futura más exigente. No es requisito para este piloto si A y su incertidumbre quedan validados a la escala requerida. Los campos de navegación disponibles por sí solos no garantizan que todas esas entradas y LUT estén disponibles o actualizadas.

## Un detalle que cambia el denominador: el halo exterior

Los conteos actuales de la AOI seleccionan **centros dentro del cuadrado**. Ese conjunto no es suficiente para calcular una unión de footprints dentro de la AOI: un centro exterior puede tener parte de su polígono nominal dentro. La geometría nueva debe construir polígonos en un halo suficientemente amplio y recortar después al cuadrado exacto.

El margen de 500 m utilizado para asociar centros VIIRS tampoco es automáticamente un halo válido para MODIS fuera de nadir. La amplitud necesaria debe derivarse de una cota de media diagonal nominal, extrapolación e incertidumbre de posición, y verificarse ampliando el halo antes de usar actividad. Si no se logra justificar una cota, debe informarse borde espacial pendiente. No reutilizar los conteos de centros como si ya fueran cobertura.

## Off-nadir, bowtie y unión espacial

Las dimensiones crecen fuera de nadir y pueden diferir en las dos direcciones. Una celda de muestreo y un IFOV/DFOV no son sinónimos. En VIIRS la agregación modifica tamaños y posiciones efectivas; en ambos instrumentos hay estructura de escaneo que una cuadrícula geográfica uniforme no conserva.

Para combinar polígonos se conserva inicialmente cada escaneo como colección propia, incluyendo posibles solapamientos con otros escaneos. Cuando corresponda representar soporte de una oportunidad, se calcula la **unión**, no la suma de áreas de todos los píxeles. No forzar una teselación global sin solapamientos a través de fronteras de escaneo. Tampoco unir observaciones de tiempos diferentes para fingir una única exposición simultánea.

En una etapa posterior, una vez congeladas geometría, QA y regla temporal, el soporte común aproximado sería la intersección de las uniones admisibles de ambos sensores, recortada a la AOI. Eso requiere soporte válido para observaciones sin detección y con detección; no se construirá únicamente alrededor de positivos. Esta nota no aplica esa operación a los casos adquiridos.

## Validación geométrica propuesta

1. **Pruebas sintéticas:** malla regular, rotada y afín con esquinas conocidas; deformación suave conocida; escaneos superpuestos; detector en borde; transiciones de agregación; huecos, coordenadas inválidas y cambio de orden. Deben comprobar orientación, centro contenido, polígonos simples, área positiva, vértices compartidos dentro de bloques y ausencia de conexiones entre escaneos.
2. **Dimensiones y área nominales:** contrastar MODIS en todas las columnas de una selección geométrica predeclarada con `ΔS`, `ΔT` y su producto; estratificar por detector, posición en escaneo, relieve y borde. Para VIIRS, contrastar tamaños por zona de agregación y geometría documentada. No validar todo el granule comprobando solo cercanía a nadir.
3. **Comparación de aproximaciones:** reportar diferencias de vértices, longitudes de lados, área y orientación entre A y B; localizar errores sistemáticos en extremos o cambios de agregación. Si solo funciona el núcleo, declarar explícitamente el dominio donde es utilizable.
4. **Topología y recorte:** verificar invariancia al orden de entrada, unión idempotente, área de intersección no mayor que cada unión, conservación al particionar la AOI y estabilidad al ampliar el halo. Separar área sumada y área de unión como diagnóstico de solapamiento.
5. **Proyección:** comparar longitudes/áreas UTM con cálculos geodésicos sobre los mismos vértices; no atribuir al sensor un sesgo del cálculo métrico.

Los umbrales de aceptación deben fijarse antes de medir geometrías reales: error dimensional tolerable para el tamaño de unidad analítica elegido, fracción máxima de bordes no resueltos y sensibilidad máxima tolerable del soporte común. Esta nota no inventa una tolerancia NASA universal ni elige un porcentaje después de ver qué método funciona.

## Qué pueden aportar FIRMS, PixArea y los bounds L1

Las descripciones oficiales de [FIRMS MODIS](https://firms.modaps.eosdis.nasa.gov/descriptions/FIRMS_MODIS_Firehotspots.html) y [FIRMS VIIRS](https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html) documentan `scan` y `track` como dimensiones del píxel. Sirven como contraste de escala para el mismo sensor/producto/colección y muestra, no como coordenadas de cuatro esquinas ni orientación fija norte-sur/este-oeste. Un símbolo dibujado en un visor no es referencia suficiente de footprint.

La [guía VIIRS 375 m C2](https://www.earthdata.nasa.gov/s3fs-public/2024-07/VIIRS_C2_AF-375m_User_Guide_1.0.pdf), tabla del producto mensual, documenta `PixArea` en km². Es un control de área nominal de los registros disponibles; no debe suponerse que existe el mismo campo para todos los píxeles L2. Los puntos FIRMS y esos registros son selectivos por detección y pueden compartir el mismo modelo geométrico de origen. Su acuerdo sería una comprobación de consistencia, no validación independiente de esquinas ni prueba del denominador de observaciones sin detección. No usarlos para escoger el soporte según actividad.

Los bounds o GRing de un granule sirven para detectar coordenadas imposibles, orientación equivocada o recorte absurdo, y para limitar búsquedas amplias. No describen el borde de cada píxel, huecos de adquisición o detalle bowtie. No usar un bounding box de centros como sustituto de la unión espacial.

## Incertidumbre explícita y decisión siguiente

Separar tres componentes: posición de centros, forma/dimensión nominal y extrapolación de bordes. La página C2 de VNP03IMG informa precisión geográfica nominal del orden de 75 m a una sigma equivalente al nadir; **no es una cota dura ni un radio universal de todos los polígonos**. Para MODIS revisar los metadatos de error de geolocalización y su interpretación, sin convertir un valor desconocido en cero.

Proponer sensibilidades de traslación coherente por sensor/escaneo, variación A/B y núcleo frente a extensión de bordes. Para un radio `ε` explícitamente supuesto, dilatar/erosionar polígonos puede mostrar cuánto cambia la intersección; esos resultados se llamarán envolventes de sensibilidad, no intervalos de confianza físicos sin un modelo de error validado. Las perturbaciones no deben ajustarse para aumentar concordancia de fuego.

**Siguiente entrega viable:** módulo puro de construcción de malla por escaneo con pruebas sintéticas y estados de borde; después, con protocolo congelado, ensayo geométrico usando únicamente los geolocalizadores existentes y validación dimensional. Si funciona, se puede acreditar un soporte **nominal aproximado con error evaluado**, sin exigir exactitud óptica imposible. Un resultado geométrico favorable no elimina las tareas independientes de QA global, exposición temporal y definición del análisis. No autoriza por sí solo G1 ni comparaciones de actividad.
