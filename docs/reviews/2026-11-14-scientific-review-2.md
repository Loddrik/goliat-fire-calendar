# Evaluación científica — iteración 2

**Decisión: conservar M1 como método publicado y someter a revisión la validación y la descripción de su incertidumbre. La selección local anidada no justifica todavía reemplazarlo.**

Auditoría de desarrollo sobre `0f0eb95`, con protocolo fijado en el commit `dede0ee` antes de ejecutar los nuevos experimentos. Relacionada con #1, #3, #5 y #10. No es una nueva prueba externa, no cierra esos issues y no modifica parámetros, compuertas ni JSON de producción. Las comprobaciones de hashes confirmaron que esos archivos permanecieron iguales.

## 1. Qué se ejecutó

Se reprodujeron las reglas de máscara y las cifras publicadas desde los Parquet versionados, sin importar ni ejecutar `experiment.py`. Se compararon cuatro tratamientos de máscara; después se ejecutó una selección M1/A por comuna con dos bucles de validación por temporadas completas. Cada partición interna volvió a aprender su propia máscara. Las bandas M1 se fijaron con residuos internos y se midieron sobre la temporada externa, que no intervino en su calibración.

Solo se usaron temporadas julio–junio 2012–2019 para el experimento. La máscara puede usar las detecciones anteriores a 2012 y las temporadas de entrenamiento permitidas. Enero–junio de 2020 pertenece a la temporada 2019. Las temporadas 2020–2021 y 2022 en adelante no entraron en selección ni evaluación de esta iteración.

La separación mecánica de datos mejora la evaluación, pero las reglas de máscara y la familia de métodos ya se habían diseñado con estos mismos datos. Además, las compuertas que seleccionan comunas usan los resultados externos de desarrollo: el desempeño del subconjunto seleccionado no queda validado de forma independiente por ese mismo procedimiento. No se presentan como 14 o 12 comunas «científicamente certificadas».

## 2. La máscara sí usa información de las temporadas retiradas, pero el efecto medido es pequeño

**[Hecho]** La máscara publicada, aprendida antes de julio de 2020, se reproduce exactamente: 223 celdas únicas. Al excluir cada temporada externa, la misma regla aprende entre 174 y 198 celdas. Desaparecen entre 25 y 49 celdas de la máscara; esto demuestra acceso a información de la temporada retirada en la validación anterior.

| Máscara | ΣMAE de M0 | ΣMAE de M1 | ΣMAE de climatología | Comunas que pasan compuertas diagnósticas |
| --- | ---: | ---: | ---: | ---: |
| Sin máscara | 1.118,25 | 953,33 | 1.356,25 | 12 |
| Publicada, fija | 1.080,58 | 881,17 | 1.335,17 | 14 |
| Aprendida dentro de cada partición | 1.081,67 | 884,41 | 1.335,75 | 14 |
| Aprendida antes del solape, hasta junio de 2012 | 1.095,58 | 918,34 | 1.345,67 | 13 |

ΣMAE es la suma de errores absolutos medios mensuales sobre 54 comunas × 8 temporadas; no es un conteo de detecciones ni el total de errores mensuales. Menor es mejor dentro de una definición de objetivo dada.

**[Hecho]** La comparación fija → por partición aumenta el ΣMAE de M1 un **0,37 %** y mantiene exactamente las mismas 14 comunas. Retiene 23 celdas-día S-NPP y 70 Aqua adicionales en el conjunto de temporadas externas. No hay evidencia aquí de un colapso de las conclusiones por esa fuga concreta.

**Límite de interpretación:** la máscara cambia tanto la señal predictora como el objetivo S-NPP. Una diferencia de MAE entre máscaras no es, por sí sola, una mejora de detección de fuego real. Tampoco hemos verificado con evidencia externa que cada celda excluida sea industrial, urbana o volcánica. La recomendación es incorporar el ajuste de máscara dentro de las particiones de validación y mantener estas limitaciones visibles.

## 3. Selección de método por comuna: mejora pequeña y no estable

En cada partición externa, los siete años restantes se dividieron de nuevo para elegir M1 o A(κ) por comuna. Se fijó previamente que A debía reducir el MAE interno de M1 en más de 1 %; de lo contrario se prefería M1. Los empates entre κ se resolvieron a favor del mayor. La temporada externa no seleccionó el método ni su κ.

| Procedimiento, misma máscara externa | ΣMAE | MAE medio por comuna/mes | Sesgo medio |
| --- | ---: | ---: | ---: |
| M1 | 884,41 | 2,0472 | +0,0150 |
| Selección anidada M1/A | 878,87 | 2,0344 | −0,0715 |

**[Hecho]** La mejora puntual es **0,63 %**. Un bootstrap pareado de 5.000 réplicas por temporadas completas, semilla 20261114, da un intervalo percentil de **−0,0695 a +0,0384** para la diferencia de MAE medio «selección − M1». Incluye cero. Con solo ocho bloques, no respalda una mejora consistente ni es una prueba externa. M1 fue elegido en 237 de las 432 decisiones comuna/temporada; el resto se distribuyó entre siete κ de A.

Las compuertas diagnósticas pasan de 14 a 12: entra Chillán Viejo (16106) y salen Bulnes (16102), El Carmen (16104) y San Ignacio (16108). Cambiar de método para aumentar el número de comunas no está justificado por este resultado.

**Mulchén (08305):** el ΣMAE mejora de 57,57 con M1 a 49,88 con selección anidada en la comparación con máscara por partición. Sin embargo, sigue ganando a Aqua crudo en solo 5/8 temporadas y a la climatología en 6/8. No pasa la regla predefinida de 6/8 en ambos controles. No habilitar su reconstrucción para facilitar una demo.

## 4. Bandas: cobertura fuera de calibración y coste en ancho

El 70,26 % anterior se reproduce en los meses activos de **las 54 comunas**, usando los mismos residuos para definir la banda ±MAE y medir su cobertura. Dentro de las 14 comunas publicadas, esa cobertura aparente es 68,70 %. Conviene especificar la población, además de mantener el nombre «error típico».

La siguiente tabla usa exclusivamente bandas fijadas con residuos internos M1 y evaluadas en la temporada externa, con máscara por partición:

| Población de evaluación | Banda | Meses activos evaluados | Cobertura en meses activos | Ancho medio en meses activos |
| --- | --- | ---: | ---: | ---: |
| 54 comunas | ±MAE interno | 2.563 | 69,61 % | 5,99 |
| 54 comunas | Cuantil 80 de residuo escalado por 1+predicción | 2.563 | 82,36 % | 24,96 |
| 14 comunas actualmente habilitadas | ±MAE interno | 920 | 68,37 % | 6,84 |
| 14 comunas actualmente habilitadas | Cuantil 80 de residuo escalado por 1+predicción | 920 | 81,30 % | 31,89 |

Anchos en celdas-día, después de truncar el límite inferior en cero. No faltó calibración en estas evaluaciones. El número de meses activos cambia respecto del cálculo aparente porque la máscara cambia algunos objetivos; la diferencia no puede atribuirse exclusivamente a reutilizar residuos.

**[Hecho]** La banda escalada alcanza aproximadamente el 80 % de cobertura activa, pero su ancho es 4,66 veces el de ±MAE en las 14 comunas. No se comparan bandas a una cobertura idéntica. Antes de elegirla habría que contrastarla con un cuantil absoluto al mismo nivel nominal y desglosar períodos de actividad alta/baja, usando únicamente calibración interna. Esta iteración no escoge una banda a partir de su resultado externo ni demuestra cobertura garantizada para 2002–2012.

## 5. Dos diagnósticos descriptivos para la próxima iteración

Estos recuentos se añadieron después de revisar la primera ejecución para orientar el siguiente trabajo; no intervinieron en la elección de métodos, máscaras, umbrales o bandas.

**Límite de los multiplicadores.** En los datos externos con máscara por partición hay 1.152 meses comuna/temporada con Aqua=0 y S-NPP>0. Acumulan 2.477 de las 21.489 celdas-día objetivo evaluadas (11,53 %). Todos los candidatos multiplicativos predicen cero en esos casos. Esto motiva evaluar el candidato afín del issue #2; no demuestra que ese candidato vaya a recuperar actividad real ni que deba publicarse.

**Campo `version` de Aqua.** En las detecciones diurnas canónicas asignadas a las 54 comunas, antes de la máscara, se observa:

| Año | Campo version | Detecciones | type=2 | Proporción type=2 |
| --- | --- | ---: | ---: | ---: |
| 2016 | 6.2 | 921 | 37 | 4,02 % |
| 2017 | 6.2 | 1.809 | 70 | 3,87 % |
| 2018 | 6.03 | 1.469 | 190 | 12,93 % |
| 2019 | 6.03 | 1.474 | 169 | 11,47 % |

**[Hecho]** Coinciden un cambio literal del campo y un salto de proporción en esa población. **[No demostrado]** Su causa, la equivalencia entre versiones y si corresponde a un cambio de colección. No interpretar `6.2` como una colección oficial identificada solo por esa cadena ni atribuir automáticamente el salto a un cambio ambiental. NASA documenta el papel de colecciones y calibración, pero este archivo requiere comprobar su procedencia concreta.

## 6. Recomendación y siguiente experimento

1. Conservar M1 y las 14 comunas actuales. La selección M1/A por comuna sigue como candidato de desarrollo, sin habilitar Mulchén.
2. Adoptar en una revisión del experimento el aprendizaje de máscara por partición, con sus pruebas de independencia. La máscara de despliegue final puede aprenderse con todo el entrenamiento; son operaciones distintas.
3. Describir el 70 % como cobertura aparente interna del piloto completo; conservar «error típico». Cualquier cambio de texto o banda publicada debe coordinarse con producto en un PR compatible.
4. Próxima iteración: comparar cuantil absoluto y escalado con igual nivel nominal interno; después evaluar el candidato afín y su comportamiento donde Aqua=0. No cambiar a la vez cartografía, máscara, filtros y modelo.
5. Mantener pendientes la comprobación externa de fuentes estáticas, la oportunidad de observación, el puente por comuna NOAA-20/S-NPP y una validación realmente externa o prospectiva. Con los datos conocidos no se puede crear retrospectivamente una prueba final que nunca se haya consultado.

## Reproducción y archivos

```sh
uv sync
uv run python -m unittest discover -s tests -p 'test_scientific_audit.py' -v
uv run python pipeline/scientific_audit.py
uv run python -m unittest discover -s tests -p 'test_*.py' -v
npm test
```

Resultados versionados en `data/processed/scientific_audit/`: `summary.json`, `manifest.json`, `scores.csv`, `mask_folds.csv`, `nested_selection.csv`, `diagnostic_gates.csv` y `outer_predictions.csv`. El manifiesto registra hashes de entradas, protocolo, código, versiones del entorno y archivos de producción antes de ejecutar; exige que estos últimos no cambien. Los CSV contienen predicciones de desarrollo, no una nueva publicación web.

Se aprobaron 7 tests Python (4 nuevos de independencia y casos degenerados) y 13 tests JS. Se reprodujo el MAE M1 publicado y las 14 compuertas. No se requiere una nueva prueba de navegador porque esta rama no cambia la app ni los JSON que consume.

## Referencias

- [Protocolo fijado para esta iteración](2026-11-14-science-protocol-2.md).
- [scikit-learn: errores de preprocesamiento y fuga de información](https://scikit-learn.org/stable/common_pitfalls.html).
- [scikit-learn: separar selección de hiperparámetros y evaluación mediante validación anidada](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html).
- [NASA MODIS Active Fire Product User Guide](https://landweb.modaps.eosdis.nasa.gov/data/userguide/MODIS_C6_Fire_User_Guide_C.pdf): limitaciones de detección y de oportunidad de observación.
- [NASA Earthdata: colecciones de MODIS y VIIRS](https://forum.earthdata.nasa.gov/viewtopic.php?t=5183): contexto de colecciones/calibración; no identifica por sí solo el significado de los valores presentes en este archivo.
