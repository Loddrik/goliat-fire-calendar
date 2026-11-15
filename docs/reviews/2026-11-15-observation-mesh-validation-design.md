# Diseño previo de validación geométrica: fórmula MODIS y criterios de ingeniería

Esta nota fija recomendaciones antes de nuevas lecturas o mediciones geométricas reales. Solo se revisó el PDF primario ya descargado y se inspeccionó visualmente su página 53; no se abrieron geolocalizadores ni se ejecutó la fase B. No cambia G1.

## Fórmula MODIS verificada en la fuente primaria

Fuente: [MODIS Collection 6 and Collection 6.1 Active Fire Product User’s Guide, v1.0, mayo de 2021](https://modis-fire.umd.edu/files/MODIS_C6_C6.1_Fire_User_Guide_1.0.pdf), §8.4.6, página 53, ecuaciones 11–13. Se contrastó el texto extraído con la imagen de la página del PDF local original de 1.459.584 bytes, cuya procedencia está registrada en [el inventario documental](evidence/observation-g1-design/sources.json).

La transcripción exacta de las expresiones es:

```text
Re = 6378.137 km
h  = 705 km
r  = Re + h
s  = 0.0014184397 rad

theta = s * (sample - 676.5)
D     = sqrt((Re/r)^2 - sin(theta)^2)

DeltaS_km = Re * s * (cos(theta)/D - 1)
DeltaT_km = r  * s * (cos(theta) - D)
A_km2     = DeltaS_km * DeltaT_km
```

`DeltaS` corresponde a along-scan; `DeltaT`, a along-track. Convertir longitudes a metros multiplicando por 1.000 y área a m² multiplicando por 1.000.000. La altura `h` es la altitud nominal del satélite del modelo, no la elevación del terreno de un campo GEO. No sustituir `theta` por `SensorZenith`: uno es ángulo de escaneo instrumental y el otro ángulo cenital de observación.

La misma guía, §8.4.4, página 52, declara que `FP line` y `FP sample` usan índices **desde cero**. Para una evaluación usando exclusivamente GEO, `sample` debe ser la columna nativa correspondiente, `0…1353`. La mitad del escaneo se encuentra entre 676 y 677; no hay una muestra entera exactamente en 676,5. No añadir uno por una convención Fortran y no reiniciar la columna cuando se recorta una ventana.

Las fórmulas describen dimensiones nominales aproximadas. La guía reconoce la limitación de asumir bordes nítidos. Un acuerdo dimensional no transforma una celda reconstruida de centros en una respuesta óptica exactamente conocida.

### Controles analíticos que deben pasar antes de leer GEO

- Para `theta=0`, ambas longitudes se reducen algebraicamente a `s*h`, aproximadamente 1 km. Este control no requiere una columna nativa que tenga exactamente ese ángulo.
- Las dimensiones son simétricas para columnas `j` y `1353-j`.
- El radicando, las dimensiones y las áreas deben ser finitos y positivos en todas las columnas nativas válidas. No recortar un radicando negativo a cero para ocultar una implementación errónea.
- La conversión km→m y km²→m² debe comprobarse separadamente.
- Un recorte cuya primera columna nativa sea `j0` debe producir el mismo resultado analítico en su posición local `c` que la columna `j0+c` del granule completo.

## Alcance recomendado para la fase B

Usar los cuatro geolocalizadores ya adquiridos de los casos de 2019 y 2023, con hashes verificados: **dos GEO por caso**, sin abrir FIRE, máscaras, QA de fuego o datos de actividad. No descargar nada ni seleccionar muestras por detecciones. La validez de entrada geométrica debe depender de coordenadas utilizables y del contrato declarado; no equivale a una decisión de QA científica.

Conservar la AOI exacta de 50×50 km en EPSG:32718 y ensayar, por separado y con la misma construcción CORE, halos de 10 y 15 km. El propósito es verificar estabilidad del recorte del proxy nominal, no medir cobertura observacional.

Para cada halo, identificar escaneos relevantes y conservar sus diez o 32 filas completas. En cada escaneo, utilizar un intervalo contiguo de columnas que abarque las seleccionadas más al menos un vecino a cada lado cuando exista. La función pura conserva índices de la matriz que recibe; el adaptador deberá mantener y probar la traducción externa a fila, columna y escaneo nativos. Nunca concatenar trozos de distintos escaneos o columnas discontinuas y tratarlos como una malla regular.

Los bordes de detector y de ventana siguen pendientes, sin extrapolación. Si una ventana carece de vecinos suficientes, registrar ese estado; no expandirla según resultados de actividad ni interpretar ausencia de polígono como ausencia de observación. Conservar por separado el dominio CORE efectivamente ensayado.

## Qué longitudes y áreas comparar

En cada cuadrilátero MODIS válido, identificar los dos pares de lados según la construcción nativa: bordes que avanzan en columna son along-scan; bordes que avanzan en detector son along-track. Usar la media de las dos longitudes opuestas para cada dirección, manteniendo también su diferencia como diagnóstico de deformación. No asignar direcciones por ejes este/norte de UTM.

Definir, sin reajuste del modelo:

```text
e_scan  = abs(L_scan  / (1000*DeltaS_km) - 1)
e_track = abs(L_track / (1000*DeltaT_km) - 1)
e_area  = abs(A_polygon_m2 / (1e6*A_km2) - 1)
```

La fórmula usa la columna nativa del centro del píxel. No calibrar tamaños o multiplicar áreas para hacer pasar la prueba. El espaciamiento entre centros, la malla que construye el proxy y el IFOV/DFOV nominal son objetos distintos; la comparación es un diagnóstico de consistencia entre aproximaciones.

Para VIIRS, validar geometría interna, medidas elipsoidales, topología, halos y separación de escaneos. Si falta un modelo dimensional externo verificado de I-band y sus zonas de agregación, **no inventar el control analítico VIIRS ni exigir que todas las áreas sean 375² m²**. El resultado dimensional externo queda pendiente.

## Criterios recomendados antes de medir

Todos los umbrales siguientes son decisiones de ingeniería propuestas para este piloto; ninguno constituye una tolerancia de NASA o una garantía de exactitud física.

| Comprobación | Criterio previo propuesto | Interpretación |
| --- | --- | --- |
| Pruebas afines de fase A | Mantener exactitud sintética `1e-10` a escala unitaria | Contrato del algoritmo |
| Shapes, índices, hashes, fronteras de escaneo | Coincidencia exacta | Cualquier error bloquea la ejecución |
| Cuadriláteros inválidos o sin centro contenido | Marcar pendientes, sin reparación | Nunca convertirlos en área cero observada |
| Halo 10 frente a 15 km | Área de diferencia simétrica de uniones recortadas / área AOI ≤ `1e-6`, para cada caso y sensor | Estabilidad del dominio nominal CORE ensayado |
| Métrica UTM frente a geodesia | Error relativo ≤1 % en lados y áreas de cada polígono válido, reportando máximo y cuantiles | Control numérico y de proyección |
| MODIS longitudes: scan y track por separado | Mediana de error relativo absoluto ≤20 % y p95 ≤30 %, en cada caso | Alarma de inconsistencia del proxy, no certificación IFOV |
| MODIS área nominal | Reportar mediana/p95 y señalar si exceden los mismos 20 %/30 % | Control adicional que no se oculta aunque las longitudes pasen |

**Mi voto:** 20 %/30 % es razonable como filtro inicial amplio de consistencia para un proxy de centros; no es evidencia suficiente para declarar su exactitud física. Aplicarlo por dirección y caso evita que una dirección compense la otra. Un área muy discordante debe mantener pendiente la utilización cuantitativa del soporte, aunque las dos longitudes hayan pasado. No endurecer ni aflojar umbrales una vez vistos los resultados.

Reportar además resultados por detector, núcleo frente a borde no resuelto y franjas de columna nativa predefinidas. Recomiendo franjas de muestras de ancho 100, con la última incompleta, como descripción sistemática del scan; no seleccionar los estratos más favorables. Los umbrales globales por caso no deben ocultar un fallo sistemático en un estrato: el informe debe restringir el dominio de uso o dejar la validación pendiente.

### Dos precisiones sobre halos y geodesia

La diferencia simétrica es preferible a comparar solo áreas totales: dos geometrías diferentes pueden tener igual área. Para la AOI UTM de 2.500.000.000 m², el umbral normalizado `1e-6` corresponde a 2.500 m². Registrar también `|area(U15)-area(U10)|`, pero no usarlo como sustituto. Comparar cada sensor por separado; no se necesita intersección MODIS–VIIRS ni ninguna clasificación de fuego.

La medida geodésica debe calcularse sobre los mismos vértices, transformados de vuelta a longitud/latitud y usando el elipsoide WGS84. Comparar áreas absolutas y longitudes correspondientes; una orientación horaria válida no es área física negativa. Este control evalúa la representación métrica, no corrige diferencias entre superficie horizontal elipsoidal y terreno inclinado.

## Salidas y decisión que sí puede producir esta etapa

Conservar número de polígonos CORE y estados pendientes, área nominal de unión recortada por halo, diferencias simétricas, longitudes/áreas y diagnósticos MODIS, controles geodésicos, errores estratificados y hashes de entradas/código/protocolo/entorno. La suma de áreas de píxeles y el área de unión deben distinguirse, especialmente ante bowtie.

Las pérdidas de dominio por bordes se informan como limitación geométrica. La estabilidad de halos tampoco demuestra que todos los polígonos físicos posibles estén contenidos: es una prueba del modelo nominal con su construcción y dominio declarados.

Un resultado favorable permitiría afirmar **“proxy CORE geométricamente consistente en el dominio ensayado, con diferencias cuantificadas respecto de la referencia nominal MODIS”**. Un fallo sería evidencia útil sobre índices, definición de tamaño, deformación o aproximación; no autoriza ajustar a posteriori el modelo para borrarlo. Ninguno de esos resultados certifica disponibilidad de observación, calidad global o exposición temporal. G1 y la elegibilidad científica permanecen falsos bajo este diseño.
