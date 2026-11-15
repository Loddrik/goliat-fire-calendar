# Fase A: biblioteca pura de malla nominal dentro de escaneos

Se implementó `pipeline/observation_mesh.py` conforme al [protocolo congelado](2026-11-15-observation-mesh-protocol.md), commit `bd09bf3`. La entrega contiene software y pruebas sintéticas; **no se leyeron geolocalizadores reales, clasificaciones de fuego, QA ni geometrías de los casos adquiridos**. No se midieron áreas, intersecciones o coberturas reales y no cambia G1.

La biblioteca permite ensayar un soporte nominal aproximado, como propone el [diseño documental](2026-11-14-observation-footprint-design.md), sin atribuir límites ópticos exactos a puntos medios entre centros.

## API y contrato

```python
result = build_scan_mesh(x, y, valid, rows_per_scan)
```

`x` e `y` son matrices de coordenadas métricas proyectadas; `valid` es una matriz booleana explícita de validez geométrica, de igual forma. Solo se aceptan escaneos de diez o 32 filas, con filas divisibles por ese tamaño y al menos tres columnas. La biblioteca no valida un CRS, convierte grados, infiere flags de calidad ni selecciona observaciones.

El resultado contiene:

- `polygons`: registros con fila, columna, escaneo, detector, polígono Shapely y orientación del anillo.
- `states`: un estado y sus razones por cada posición de entrada, incluidos centros sin polígono.
- `counts`: partición exhaustiva de estados, con ceros explícitos para categorías ausentes.
- `metadata`: requisitos de coordenadas e índices, alcance nominal, ausencia de extrapolación o reparación y precondiciones para la fase B.

Los índices corresponden exactamente a la matriz proporcionada: no hay remuestreo, desplazamiento o reordenamiento. Si la fase B pasa ventanas recortadas, deberá mantener explícitamente la correspondencia con índices nativos y conservar las fronteras reales de escaneo. El contrato actual no permite declarar una ventana arbitraria de filas como si comenzara en un escaneo nuevo.

## Construcción y estados

Cada escaneo se procesa por separado. Un vértice interior es el promedio de cuatro centros vecinos del mismo escaneo. Los polígonos interiores usan cuatro vértices de esa malla compartida; los vecinos conservan exactamente el mismo borde. No se promedian coordenadas a través de la última fila de un escaneo y la primera del siguiente.

La primera y última fila de detectores de cada escaneo, y la primera y última columna de entrada, quedan `geometry_edge_unresolved`. No se extrapolan. Un centro inválido, coordenada no finita o centro vecino necesario ausente produce `geometry_input_unresolved`. No se completan huecos ni se desplazan centros para obtener una geometría válida.

Un cuadrilátero se rechaza si su topología es inválida, su área no es finita/positiva o no contiene su centro nativo. Queda `geometry_topology_unresolved` con la razón correspondiente. No se usa `buffer(0)`, snapping, triangulación reparadora ni otra corrección silenciosa. Una orientación horaria de la matriz puede ser legítima: se registra sin cambiar vértices, manteniendo área geométrica positiva.

El estado `nominal_core_polygon` significa exclusivamente que pudo construirse y verificarse esa geometría sintética o nominal según el contrato. No es una observación válida de fuego, una garantía IFOV/DFOV o una demostración de cobertura. Los bordes pendientes tampoco significan que el satélite no haya observado esas posiciones.

Con entradas completas y afines, el número de polígonos CORE por escaneo es `(filas_por_escaneo − 2) × (columnas − 2)`. Ese recorte estructural debe quedar visible en una aplicación futura; no se aceptará como denominador completo por omisión.

## Validación sintética

```sh
.venv/bin/python -m unittest discover -s tests -p test_observation_mesh.py -v
```

Resultado: **nueve pruebas aprobadas** en Python 3.14, NumPy 2.5.4 y Shapely 2.2.0.

- Mallas regulares, rotadas, cizalladas y reflejadas: vértices analíticos y áreas verificadas con tolerancia `1e-10` en la escala sintética.
- Vértices y bordes exactamente compartidos entre polígonos vecinos del mismo escaneo.
- Dos escaneos espacialmente superpuestos: se conservan las fronteras, índices y solapamientos; no se reduce artificialmente el ancho de los píxeles al mezclar filas de distintos escaneos.
- NaN y validez explícita falsa: invalidación de centro y vértices dependientes, sin reconstrucción silenciosa.
- Deformación cuadrática suave conocida: el error es distinto de cero y se reduce por un factor cuatro al dividir la separación por dos. Es una comprobación de error controlado, no una declaración de exactitud en terrenos reales.
- Cuadriláteros cruzados, degenerados y con centro exterior rechazados.
- Invariancia al permutar la lista de polígonos, unión idempotente, intersección no mayor que sus uniones y área de unión menor que suma de áreas cuando hay solapamiento.
- Escaneos de 32 filas e inputs incompatibles rechazados, incluidos máscara no booleana y formas diferentes.
- Un polígono sintético con centro fuera de una AOI puede intersectarla: se comprueba la necesidad del halo sin afirmar que la biblioteca lo haya validado.

## Precondiciones para la fase B

La metadata conserva `nominal_approximation=true`, pero `physical_footprints_verified=false`, `real_nominal_support_validated=false`, `halo_verified=false`, `scientific_eligibility_certified=false` y `gate1_passed=false`.

La fase B requiere otro protocolo fijado antes de medir geometrías reales: comparación de halos de 10/15 km; conservación de índices y fronteras; fórmulas MODIS nominales verificadas por columna; tolerancias dimensionales y geométricas predefinidas; comprobación geodésica; tratamiento explícito de bordes y cambios de agregación VIIRS. El margen anterior de 500 m para asociación de centros no se transforma en un halo universal.

Si el control dimensional externo VIIRS sigue sin resolverse, debe continuar pendiente: la separación entre centros no se canoniza como DFOV ni se inventan rectángulos constantes de 375 m. La futura evaluación geométrica puede aceptar una aproximación con error medido a la escala necesaria, sin exigir una PSF físicamente exacta.

Este módulo no suma polígonos como cobertura ni calcula un denominador de observación. La fase A tampoco resuelve la exposición temporal o calidad global de los casos. No se instalaron dependencias, modificaron archivos anteriores, modelos, datos base o publicación. Sin modificaciones del estado Git, commits ni push por este agente.
