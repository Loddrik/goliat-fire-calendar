# Protocolo de evaluación científica, iteración 2

Fijado antes de ejecutar esta iteración, sobre `0f0eb952c737516379d4d3bc62932cd63a4c8de7`. Da continuidad a los issues #1, #3, #5 y #10. Es una auditoría de desarrollo, no una nueva prueba externa: ya se conocen resultados anteriores de estas temporadas. No cambia datos publicados, parámetros ni compuertas.

## Preguntas y reglas

1. **Máscara y validación.** Reproducir M0/M1/M2 y las compuertas actuales sobre 2012–2019; comparar sin máscara, máscara publicada, máscara aprendida dentro de cada partición y máscara anterior al solape. En la variante por partición se mantienen literalmente las reglas A/B/C y buffers publicados; se usan las temporadas anteriores a 2012 y las temporadas de entrenamiento permitidas, sin la temporada retirada ni fechas posteriores a junio de 2020. No se cambian umbrales para obtener más comunas habilitadas.
2. **Selección por comuna.** Bucle externo LOSO de ocho temporadas (2012–2019). En cada entrenamiento externo, otro LOSO de siete temporadas elige M1 o A(κ), con κ ∈ {0,10,30,50,100,300,10⁹}, mediante MAE mensual medio de cada comuna. La máscara se vuelve a aprender también dentro de cada partición interna. Se elige A solo si reduce el MAE interno de M1 en más de 1 %; de lo contrario se conserva M1 por parsimonia. En empates entre κ se prefiere el mayor. El margen del 1 % es una decisión de desarrollo explícita, no un estándar NASA. Cuando el denominador local es cero se usa la razón regional del grupo, o la global si falta señal regional; nunca se crean infinitos ni se convierten en cero los errores inválidos.
3. **Bandas.** En cada partición externa, fijar el ancho exclusivamente con residuos M1 de validación interna fuera de muestra. Comparar (a) ±MAE de meses activos internos, como en la definición publicada, y (b) el percentil 80 empírico de |error|/(1+predicción) en meses activos internos, aplicado como ±q·(1+predicción). Truncar el límite inferior en cero y medir cobertura y ancho en la temporada externa, en todos los meses y en meses activos. Si no hay residuos activos de calibración, no se inventa un ancho. No elegir entre bandas según resultados externos ni prometer cobertura probabilística garantizada.

## Métricas y comparabilidad

- MAE y sesgo por comuna/temporada; suma de MAE por comuna/temporada para reproducir el informe anterior, y MAE medio por observación.
- Las mismas compuertas diagnósticas: Aqua ≥ 50 celdas-día, victoria frente a M0 y M2 en ≥ 6 de 8 temporadas. El recuento de comunas que pasan usa resultados de desarrollo; no valida de manera independiente el subconjunto seleccionado.
- Mostrar comunas que entran/salen, tamaño y diferencias de máscara, observaciones retenidas y coeficientes. Cambiar la máscara cambia la variable objetivo: una reducción de MAE entre máscaras no demuestra por sí sola mejor detección de fuego real.
- Para la política seleccionada anidada, comparar sus predicciones externas con M1 sobre la misma máscara externa. Presentar Mulchén explícitamente, sin fijar su habilitación de antemano.
- Reproducir aparte la cobertura aparente publicada y contrastarla con cobertura externa de bandas fijadas sin la temporada externa. Reportar población completa y, de forma descriptiva, el subconjunto de las 14 comunas ya habilitadas.
- Bootstrap pareado por temporadas completas para la diferencia de MAE entre política anidada y M1: 5.000 réplicas, semilla 20261114, intervalo percentil 2,5–97,5 %. Solo ocho bloques; incertidumbre de desarrollo, no evidencia externa ni garantía frente a deriva temporal.

## Trazabilidad y límites

Guardar hashes de Parquet, parámetros, protocolo y código; particiones, máscaras, predicciones externas, selección interna, compuertas diagnósticas y resumen JSON estricto. Verificar que los archivos de producción no cambian. No se ejecuta `experiment.py`, porque sobrescribe resultados publicados. No se utiliza 2020–2021 para escoger candidatos, umbrales o máscaras; tampoco 2022 en adelante. No se evalúan aún el candidato afín, CONAF, nuevas geografías o nuevas reglas de cobertura.

La máscara por partición evita el acceso mecánico a la temporada retirada. Sus reglas y las familias de candidatos ya fueron diseñadas mirando estos datos, por lo que subsiste adaptación del diseño al conjunto conocido. Hace falta un conjunto externo o una validación prospectiva para una afirmación independiente. Tampoco se demuestra que todas las celdas enmascaradas sean fuentes estáticas: eso exige evidencia externa.

## Fuentes metodológicas

- [scikit-learn: fuga de información y preprocesamiento dentro de la validación](https://scikit-learn.org/stable/common_pitfalls.html).
- [scikit-learn: validación anidada para selección y evaluación](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html).
- [NASA MODIS Active Fire Product User Guide](https://landweb.modaps.eosdis.nasa.gov/data/userguide/MODIS_C6_Fire_User_Guide_C.pdf): detecciones y limitaciones de observación; no usar el conteo de focos como cobertura.
