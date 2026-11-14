# Iteración 5 — calibración por tramos con cero exacto

**Resultado de desarrollo:** añadir P a la selección M1/B reduce otro **1,01 %** el MAE y disminuye las estimaciones en ceros de ambos sensores. El beneficio tiene costes: aumenta el error donde Aqua=0 y VIIRS>0 y hace más negativo el sesgo agregado. La propuesta requiere revisar esas compensaciones, no publicar automáticamente un nuevo ganador.

El [protocolo 5](2026-11-14-science-protocol-5.md) se fijó antes de ejecutar. P utiliza dos pendientes no negativas, un umbral regional aprendido solo de Aqua de entrenamiento y valor exactamente cero en Aqua=0. Se mantuvieron el ajuste cuadrático y la grilla de regularización de B. Ocho particiones externas 2012–2019 y siete internas, con máscara y parámetros aprendidos de nuevo. Se reprodujeron exactamente M1 y M1/B de la iteración 3.

## Comparación

| Política | ΣMAE | MAE medio mensual | Mejora frente a M1 | Sesgo medio | Compuertas diagnósticas |
| --- | ---: | ---: | ---: | ---: | ---: |
| M1 | 884,41 | 2,0472 | — | +0,0150 | 14 |
| M1/B | 822,18 | 1,9032 | 7,04 % | −0,0872 | 15 |
| M1/P | 825,93 | 1,9119 | 6,61 % | −0,3133 | 15 |
| M1/B/P | 813,86 | 1,8839 | 7,98 % | −0,1676 | 14 |

Las compuertas son diagnósticas y se aplican sobre resultados de desarrollo; no validan de forma independiente el subconjunto elegido. Más comunas no es el criterio de elección.

M1/P frente a M1: diferencia de MAE medio **−0,1354**, intervalo percentil por temporadas **[−0,2334; −0,0507]**. M1/B/P frente a M1/B: **−0,01927**, intervalo **[−0,02790; −0,00958]**. Ambos mejoran en 7 de 8 temporadas. Bootstrap pareado de 5.000 réplicas, ocho bloques, semilla 20261114. Son resultados exploratorios sobre datos conocidos, no inferencia confirmatoria ni validación externa.

## Qué mejora y qué empeora

| Subgrupo | Meses | MAE M1/B | MAE M1/P | MAE M1/B/P |
| --- | ---: | ---: | ---: | ---: |
| Aqua=0, VIIRS>0 | 1.152 | 1,8033 | 2,1502 | 1,8779 |
| Aqua=0, VIIRS=0 | 2.491 | 0,1597 | 0 | 0,1029 |
| Aqua>0 | 1.541 | 4,7961 | 4,8243 | 4,7674 |

El candidato P cumple P(0)=0 en las 5.184 predicciones externas, al igual que la selección M1/P. La selección M1/B/P **no** está anclada globalmente: algunas comunas siguen usando B. Aun así, reduce de **397,93 a 256,35** las celdas-día estimadas donde ambos sensores registran cero. Son estimaciones, no detecciones recuperadas; tampoco esos ceros confirman ausencia de actividad real.

La restricción sacrifica parte de la mejora en meses Aqua=0/VIIRS>0. El error medio allí sube de 1,8033 a 1,8779 al ampliar M1/B con P. Por eso no se debe mostrar solo el ahorro en ceros ni afirmar que la forma por tramos domina al afín en todas las situaciones.

## Meses intensos y Mulchén

En los 74 meses con VIIRS≥50, M1/B tiene MAE **19,7085** y la selección M1/B/P **19,7826**: la mejora global no supone mejor desempeño en este subgrupo. El sesgo cambia de −2,3217 a −2,4362.

Mulchén pasa las compuertas con ambas políticas: M1/P gana a Aqua crudo y climatología en 6/8; M1/B/P gana en 7/8 y 6/8. Su MAE es **6,0951** con M1/P y **5,7915** con M1/B/P, frente a **5,7413** con M1/B. No justificar una política global por favorecer una comuna particular.

## Incertidumbre y verificación

El cuantil absoluto nominal 80 de la selección M1/B/P tiene cobertura activa externa **78,03 %**, ancho medio **7,17**, sobre 2.563 meses activos. M1/B: **78,23 %** y ancho **7,24**. El cambio de ancho no demuestra una mejora de cobertura.

Los 64 entrenamientos vectorizados y sus cuatro regularizaciones cumplieron KKT≤10⁻⁶; el máximo fue **4,55×10⁻¹³**. Se probaron continuidad, monotonía, cero exacto, optimalidad mediante perturbaciones factibles, umbral solo de entrenamiento y parsimonia de selección. Artefactos en `data/processed/piecewise_audit/`, con hashes y protección de producción/iteraciones previas. No se cambió la app.

```sh
uv run python -m unittest discover -s tests -p 'test_piecewise.py' -v
uv run python pipeline/piecewise_experiment.py
```

## Próxima comprobación

Antes de seguir aumentando la familia, revisar sensibilidad a la asignación de grilla y límites comunales. Las mejoras cercanas al 1 % deben contrastarse con decisiones del preprocesamiento. Después, congelar políticas para una revisión temporal descriptiva, sin reutilizarla para ajustar retrospectivamente la grilla de candidatos.
