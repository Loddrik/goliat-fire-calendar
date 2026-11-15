# Protocolo científico — iteración 3, candidato afín

Fijado antes de ejecutar los resultados de esta iteración. Base: `de968249789c48d5d36f997da0f3c89fc0bdf7de`, continuación del PR #23 y del issue #2. Es desarrollo retrospectivo: las temporadas y resultados anteriores ya son conocidos. No se cambia producción ni se crea una prueba externa nueva.

## Modelo B

Por comuna × grupo mensual, predecir `max(0, a + b·Aqua)`, con `b ≥ 0`. El intercepto puede ser negativo; el resultado se trunca en cero. Se mantienen los grupos anteriores: junio–agosto juntos, los otros meses por separado.

En cada entrenamiento, calcular `s = max(1, RMS(Aqua))` regional por grupo y `z = Aqua/s`. Ajustar `a` y `β = b·s` minimizando:

`media[(VIIRS − a − β·z)²] + λ·[a² + (β − r_regional·s)²]`, sujeto a `β ≥ 0`.

La regularización acerca el intercepto a cero y la pendiente a la razón VIIRS/Aqua regional del grupo, calculada solo en entrenamiento. Si ese grupo no tiene Aqua, se usa la razón global del entrenamiento. λ ∈ {0,01; 0,1; 1; 10}. Normalización, máscara, razones y coeficientes se vuelven a aprender en cada partición. No se añaden candidatos después de mirar los resultados externos de esta iteración.

El problema es cuadrático y de dos parámetros; se resuelve por sus ecuaciones normales. Si la solución libre da pendiente negativa, fijarla en cero y resolver el intercepto en esa frontera. No se redondean predicciones ni se convierten infinitos/NaN en cero. No se afirma que un intercepto positivo sea una detección histórica recuperada: es una estimación de actividad no observada por Aqua.

## Validación y selección

- Mismos Parquet y geografía, grilla, filtros y temporadas 2012–2019 que en la iteración 2. Máscara aprendida dentro de cada partición, con los mismos umbrales. Temporadas 2020 en adelante fuera del análisis.
- Ocho particiones externas LOSO. Dentro de cada una, siete particiones internas LOSO con sus propias máscaras. Ninguna fila ni detección de la temporada externa participa en selección, normalización, ajuste o calibración.
- Controles M0, M1 y M2; reproducir además las predicciones externas de la selección M1/A de la iteración 2.
- Evaluar tres políticas anidadas, sin elegir retrospectivamente la más favorable: **M1/A** (misma regla anterior), **M1/B** y **M1/A/B**. Para M1/B, B debe mejorar el MAE interno de M1 en más de 1 %; para M1/A/B, debe mejorar en más de 1 % al candidato M1/A seleccionado internamente. Si no, mantener el método anterior. Empates λ → mayor regularización.
- Las compuertas siguen siendo diagnósticas: señal Aqua ≥ 50 celdas-día y victoria frente a Aqua crudo y climatología en ≥ 6/8 temporadas. No bajarlas para habilitar Mulchén. El subconjunto que pasa no tiene una nueva validación independiente.

## Métricas fijadas

1. MAE y sesgo, por comuna/temporada y agregados; pérdidas por temporada, no solo el promedio global.
2. Bootstrap pareado por temporadas completas: 5.000 réplicas, semilla 20261114, intervalo percentil 2,5–97,5 % para las diferencias M1/B−M1, M1/A/B−M1/A y M1/A/B−M1. Ocho bloques, tres contrastes exploratorios; no es una prueba confirmatoria ni corrección por selección del diseño.
3. Desglosar meses con Aqua=0 y VIIRS>0, Aqua=0 y VIIRS=0, y Aqua>0. Reportar error, sesgo y actividad añadida en ceros observados, para no ocultar que un intercepto puede mejorar omisiones a costa de inventar actividad donde ambas plataformas registran cero.
4. Mostrar compuertas y cambios de comunas, Mulchén y la variación del método elegido entre particiones. Más comunas habilitadas no es el objetivo de selección.
5. Comparar bandas de cuantil **absoluto 80** y **escalado 80** a igual nivel nominal interno, para M1 y las tres políticas. Los residuos se obtienen de las predicciones internas del candidato seleccionado por comuna. Se calibran en meses activos internos (VIIRS>0), como la comparación anterior; evaluar cobertura y ancho en todos los meses y en activos externos. El cuantil absoluto y el escalado comparten exactamente la misma población de calibración. La elección interna del candidato también usa esos residuos: se mide el procedimiento completo en el bucle externo y no se promete garantía de cobertura. No escoger una banda según el resultado externo.

## Artefactos y condiciones para terminar

Guardar protocolo, código, hashes de entradas y de la evaluación anterior, coeficientes externos, elecciones internas, predicciones externas, métricas, compuertas diagnósticas, bandas y resumen JSON estricto en un directorio nuevo. Exigir reproducción numérica de M1/M1-A y comprobar que los archivos de producción y los resultados de la iteración 2 no cambian. Añadir tests de pendiente no negativa, casos Aqua=0, normalización solo en entrenamiento, regla de parsimonia y calibración independiente de la verdad externa.

El resultado puede recomendar conservar M1 o continuar el desarrollo; no obliga a publicar B. Ningún cambio de modelo o texto de la app entra en `main` como parte de este experimento. Una eventual adopción necesita revisar simultáneamente contrato, reconstrucción, incertidumbre y textos con producto.
