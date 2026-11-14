# Evaluación científica — iteración 3, modelo afín

**Resultado: el candidato afín B aporta una mejora de desarrollo que merece avanzar a una propuesta de modelo; todavía no sustituye a M1 en producción.** La selección anidada M1/B reduce el MAE un 7,04 % frente a M1 y mejora en 7 de 8 temporadas. Su principal beneficio aparece donde Aqua sí detecta actividad, no en una recuperación neta demostrada de los ceros de Aqua.

Base `de96824`, continuación de la evaluación #2 y del issue #2. El [protocolo](2026-11-14-science-protocol-3.md) se fijó en `88d2cf9` antes de ejecutar los resultados. Todos son resultados retrospectivos de desarrollo. Las reglas y las temporadas ya eran conocidas; ninguna cifra de este informe constituye una nueva validación externa ni valida la extrapolación a 2002–2012.

## 1. Modelo y validación

B estima `max(0, a + b·Aqua)` por comuna y grupo mensual, con pendiente `b ≥ 0`. Ajusta un intercepto y una pendiente regularizados hacia cero y la razón regional, respectivamente. La normalización regional se calcula solo con el entrenamiento. λ ∈ {0,01; 0,1; 1; 10}, elegido por comuna, compartido entre sus grupos mensuales. La función de ajuste es un error cuadrático regularizado; la selección y evaluación usan MAE. Se conserva la distinción entre esas dos funciones.

Se mantuvieron los mismos datos, filtros, grilla y geografía. Ocho particiones externas de temporadas completas 2012–2019; dentro de cada una, siete particiones internas para elegir el candidato. La máscara, la normalización, las razones y los coeficientes se aprenden de nuevo en cada partición. No entran las temporadas 2020 en adelante. Un candidato B debe mejorar más de 1 % el MAE interno de la alternativa anterior para sustituirla.

Se evaluaron las tres políticas previstas: M1/A, M1/B y M1/A/B. Las predicciones M1 y M1/A reprodujeron las de la iteración #2, con tolerancia absoluta 10⁻¹⁰. Las observaciones objetivo fueron idénticas: no se obtuvo la mejora cambiando la máscara o el conjunto evaluado.

## 2. Error y estabilidad por temporada

| Método o política anidada | ΣMAE comuna/temporada | MAE medio por comuna/mes | Sesgo medio | Comunas que pasan compuertas diagnósticas |
| --- | ---: | ---: | ---: | ---: |
| M0, Aqua sin corregir | 1.081,67 | 2,5039 | −2,3719 | — |
| M1, factor regional | 884,41 | 2,0472 | +0,0150 | 14 |
| M2, climatología | 1.335,75 | 3,0920 | −1,3764 | — |
| Selección M1/A | 878,87 | 2,0344 | −0,0715 | 12 |
| Selección M1/B | 822,18 | 1,9032 | −0,0872 | 15 |
| Selección M1/A/B | 825,42 | 1,9107 | −0,0877 | 14 |

ΣMAE es la suma de MAE mensuales de 54 comunas × 8 temporadas, no el total de errores ni de detecciones. El sesgo medio con B es ligeramente más negativo; no todo indicador mejora al mismo tiempo.

**[Hecho]** M1/B reduce el MAE un **7,04 %** respecto de M1; M1/A/B lo reduce un **6,67 %**. Son políticas elegidas internamente, no el mejor candidato escogido a posteriori para cada temporada externa. No se declara un ganador final entre las políticas a partir de esta misma evaluación.

| Contraste pareado | Diferencia de MAE medio | Intervalo percentil del bootstrap por temporadas |
| --- | ---: | --- |
| M1/B − M1 | −0,1441 | [−0,2646; −0,0444] |
| M1/A/B − M1/A | −0,1237 | [−0,2029; −0,0607] |
| M1/A/B − M1 | −0,1365 | [−0,2555; −0,0380] |

5.000 réplicas, semilla 20261114, ocho bloques anuales. Los tres intervalos de desarrollo quedan bajo cero. No son pruebas confirmatorias: no corrigen la adaptación del diseño a los datos ni la comparación de familias y no son una garantía frente a deriva temporal. Los 54 municipios de una temporada se remuestrean juntos, no como observaciones independientes.

M1/B mejora en 2012, 2013, 2014, 2016, 2017, 2018 y 2019; empeora en 2015. La mayor diferencia aparece en 2017. Las pérdidas y diferencias de cada temporada están conservadas, para que el promedio no oculte esa concentración.

## 3. El balance de los ceros cambia la interpretación

| Subgrupo externo | Meses | MAE M1 | MAE M1/B | Balance de error absoluto total |
| --- | ---: | ---: | ---: | --- |
| Aqua=0, VIIRS>0 | 1.152 | 2,1502 | 1,8033 | Reduce 399,59 |
| Aqua=0, VIIRS=0 | 2.491 | 0 | 0,1597 | Añade 397,93 |
| Aqua>0 | 1.541 | 5,2796 | 4,7961 | Reduce 745,09 |

**[Hecho]** En meses con Aqua=0 y VIIRS>0, B permite estimaciones positivas y reduce el error. Pero introduce 397,93 celdas-día estimadas en 882 meses donde ambas plataformas registran cero. El beneficio neto de error absoluto en **todos** los meses Aqua=0 es apenas **1,66**, frente a **745,09** en los meses Aqua>0.

Por tanto, no corresponde presentar este resultado como «recuperamos los focos que MODIS no vio». Lo defendible es que la calibración afín mejora el error agregado en este experimento; casi todo ese beneficio neto procede de meses con señal Aqua positiva. Donde ambas plataformas registran cero, la actividad añadida es una estimación del modelo, no una observación. Cero detecciones tampoco demuestra ausencia de actividad real ni cobertura suficiente.

## 4. Compuertas y Mulchén

Las reglas no cambiaron: Aqua ≥ 50 celdas-día en entrenamiento, mejora frente a M0 y M2 en ≥ 6/8 temporadas. Las compuertas siguen siendo diagnósticas: utilizar los mismos resultados de desarrollo para elegir el subconjunto no proporciona una validación independiente de ese subconjunto.

Para M1/B pasan 15 comunas. Frente a las 14 actuales, entran Mulchén (08305), Chillán (16101), Pinto (16106) y Cobquecura (16202); salen El Carmen (16104), San Ignacio (16108) y Quirihue (16201). No consiste en añadir Mulchén y conservar automáticamente todas las habilitaciones anteriores.

**Mulchén:** M1/B gana a Aqua crudo en **7/8** temporadas y a la climatología en **6/8**. Su MAE medio baja de **7,1968 a 5,7413**, y el sesgo medio de **+2,8171 a +0,0971**. Pasa las compuertas diagnósticas sin alterar umbrales. Esto justifica revisar su reconstrucción candidata; no habilita por sí solo una serie histórica publicada.

En las 432 decisiones comuna/temporada, M1/B usa M1 en 176 y una variante B en 256. Las elecciones de λ varían: 108 con 0,1; 90 con 0,01; 31 con 10 y 27 con 1. No se trata de un único factor regional que pueda copiarse al contrato actual de la app.

## 5. Bandas al mismo nivel nominal

Se compararon cuantiles 80 **absolutos** y **escalados por 1+predicción**, calibrados sobre exactamente los mismos meses activos internos. La política se eligió con esos datos internos; por eso se mide el procedimiento completo en la temporada externa, sin prometer cobertura garantizada. Ambas bandas se truncan en cero por abajo.

| Predicción | Banda nominal 80 | Cobertura activa externa, 54 comunas | Ancho medio activo |
| --- | --- | ---: | ---: |
| M1 | Cuantil absoluto | 79,09 % | 7,94 |
| M1 | Cuantil escalado | 82,36 % | 24,96 |
| M1/B | Cuantil absoluto | 78,23 % | 7,24 |
| M1/B | Cuantil escalado | 80,53 % | 18,23 |

Mismos 2.563 meses activos externos. No faltó calibración. La cobertura empírica conseguida no es idéntica, aunque el nivel nominal interno sí lo sea; no se presenta la diferencia de ancho como una comparación a cobertura externa exactamente igual.

Dentro del subconjunto **preexistente** de 14 comunas (920 meses activos), M1/B alcanza 78,26 % con ancho 9,22 para el cuantil absoluto y 80,11 % con ancho 24,09 para el escalado. No son las 15 comunas que pasan ahora ni una validación de ese nuevo subconjunto.

El control absoluto al mismo nivel nominal resuelve una carencia de la iteración anterior: se puede obtener una cobertura cercana al 80 % sin asumir que la banda escalada, mucho más ancha, es automáticamente preferible. Antes de publicar una banda hay que revisar cobertura por intensidad y temporada; estos promedios no aseguran buen comportamiento durante picos excepcionales ni en la era estimada.

## 6. Qué avanzar y qué mantener separado

1. **Avanzar B como candidato serio de desarrollo.** La mejora es mayor y más estable que la de M1/A en la iteración #2. El siguiente paso es fijar la política candidata y su configuración de entrenamiento completo, manteniendo explícito que su selección se apoya en desarrollo retrospectivo.
2. **Mantener M1 publicado mientras se revisa esa propuesta.** B requiere un contrato de coeficientes por comuna/grupo, identidad del método, incertidumbre y exportaciones coherentes. No puede servirse bajo el texto «Aqua × 2,35».
3. **No vender recuperación de detecciones faltantes.** El balance Aqua=0 revela que la mejora allí se compensa casi por completo con actividad estimada en ceros de ambos sensores. Registrar ese coste es parte del resultado, no una objeción que deba esconderse.
4. **Revisar extremos, extrapolación y fuentes estáticas.** No se ha validado 2002–2012 ni la verdad física de cada celda enmascarada. Una evaluación futura sobre 2020–2021 solo puede ser descriptiva porque ese bloque ya se consultó anteriormente. Hace falta evidencia externa o prospectiva para una afirmación independiente.
5. **Revisar bandas absolutas y escaladas sin elegirlas por el resultado externo.** La menor anchura absoluta motiva una comprobación condicional más detallada; no constituye una garantía del 80 %.

## Reproducción y verificación

```sh
uv sync
uv run python -m unittest discover -s tests -p 'test_affine_experiment.py' -v
uv run python pipeline/affine_experiment.py
uv run python -m unittest discover -s tests -p 'test_*.py' -v
npm test
```

Artefactos en `data/processed/affine_audit/`: predicciones externas, 1.296 elecciones internas de política, 4.320 grupos de coeficientes externos (cada uno contiene las cuatro regularizaciones), métricas, compuertas, resumen y manifiesto. Se verificaron hashes de entradas, protocolo, código, helper de máscara y cada salida. Se reprodujeron las 5.184 predicciones M1/M1-A anteriores y cada candidato seleccionado. Los archivos de producción y los de la iteración #2 permanecieron intactos.

Pasaron **13 tests Python y 13 JS**, incluidos seis nuevos para ecuaciones normales, pendiente restringida, interceptos con Aqua=0, independencia de normalización/calibración respecto de la verdad externa y parsimonia de selección. No hay cambios de interfaz que requieran una nueva prueba de navegador o despliegue.
