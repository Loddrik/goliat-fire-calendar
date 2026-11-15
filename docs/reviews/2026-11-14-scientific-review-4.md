# Iteración 4 — afín con pérdida robusta

**Conclusión de desarrollo:** Huber mejora frente al factor regional M1, pero no aporta todavía una mejora consistente sobre el afín cuadrático B que justifique una política más compleja. Ninguno de estos resultados cambia el método publicado.

El [protocolo 4](2026-11-14-science-protocol-4.md) fija candidatos y métricas antes de la evaluación externa. Se usaron las temporadas 2012–2019 y validación anidada con la máscara, escala y ajuste aprendidos dentro de cada partición. Se reprodujeron exactamente las predicciones M1 y M1/B de la iteración 3. El diseño sigue siendo retrospectivo y adaptado a datos conocidos; no es una prueba independiente.

## Resultado agregado

| Política | ΣMAE | MAE medio mensual | Mejora frente a M1 | Sesgo medio | Compuertas diagnósticas |
| --- | ---: | ---: | ---: | ---: | ---: |
| M1 | 884,41 | 2,0472 | — | +0,0150 | 14 |
| M1/B | 822,18 | 1,9032 | 7,04 % | −0,0872 | 15 |
| M1/H | 816,74 | 1,8906 | 7,65 % | −0,1321 | 16 |
| M1/B/H | 817,95 | 1,8934 | 7,51 % | −0,1250 | 17 |

H es un afín monótono regularizado como B, sustituyendo el error cuadrático local por Huber. No cambia los priors ni la normalización regional, por lo que no se presenta como un procedimiento totalmente robusto frente a extremos. Las compuertas usan los resultados de desarrollo: más comunas no equivale a mejor validación independiente.

M1/H supera M1 en las ocho temporadas. La diferencia media de MAE tiene intervalo percentil por temporadas **[−0,2866; −0,0539]**. Pero la política ampliada M1/B/H frente a M1/B solo reduce el MAE medio **0,00979**, con intervalo **[−0,0327; +0,0104]**, que incluye cero. Bootstrap pareado, 5.000 réplicas, semilla 20261114, ocho bloques. Son contrastes exploratorios, sin garantía confirmatoria ni corrección por el diseño adaptativo.

## Intensidad y coste en ceros

| VIIRS objetivo | Meses | MAE M1 | MAE M1/B | MAE M1/H |
| --- | ---: | ---: | ---: | ---: |
| 0 | 2.621 | 0,1441 | 0,2780 | 0,2783 |
| Mayor que 0 y menor que 10 | 2.047 | 2,2882 | 2,1244 | 2,1105 |
| 10 a menos de 50 | 442 | 8,4401 | 7,5347 | 7,5992 |
| 50 o más | 74 | 24,6054 | 19,7085 | 18,8158 |

La mejora no se consigue degradando el MAE de los 74 meses más intensos: H mejora ese error frente a B. Sin embargo, su sesgo allí es más negativo (**−3,63**, frente a **−2,32** de B). La reducción de error absoluto y la subestimación media deben leerse juntas.

El problema de los ceros no desaparece. Donde Aqua y VIIRS registran cero, H añade **412,76** celdas-día estimadas, frente a **397,93** de M1/B. No son detecciones recuperadas ni se demuestra actividad física: son estimaciones del modelo donde no hubo detecciones seleccionadas. No se identifican esos ceros como ausencia confirmada de fuego.

Para Mulchén, M1/H pasa las reglas diagnósticas con 6/8 victorias frente a Aqua crudo y 6/8 frente a climatología. Su MAE es **5,9559**, peor que **5,7413** de M1/B, aunque mejor que **7,1968** de M1. La decisión no debe basarse en exhibir una comuna favorita.

## Banda absoluta nominal 80

Calibrada en meses activos internos; evaluación en los mismos 2.563 meses activos externos de las 54 comunas:

| Política | Cobertura | Ancho medio |
| --- | ---: | ---: |
| M1 | 79,09 % | 7,94 |
| M1/B | 78,23 % | 7,24 |
| M1/H | 77,25 % | 7,12 |
| M1/B/H | 77,37 % | 7,12 |

El menor ancho viene acompañado de menor cobertura. No se declara una mejora de incertidumbre ni una cobertura garantizada del 80 %. Quedan por revisar los picos y la transferencia temporal antes de publicar una banda.

## Corrección numérica y comprobaciones

IRLS puro no convergió en un ajuste interno: después de 1.000 iteraciones, KKT=0,000335797, por encima de la tolerancia 10⁻⁶. La ejecución se detuvo antes de obtener puntuaciones externas. Se documentó la corrección en el protocolo y se mantuvieron pérdida, candidatos, tolerancia y límite: diez pasos IRLS seguidos de Newton semisuave amortiguado para la misma función convexa.

Los **576 ajustes vectorizados** (64 entrenamientos × 9 candidatos, cada uno sobre 540 grupos comunales/mensuales) convergieron con KKT≤10⁻⁶; máximo 16 iteraciones. Se extrajo el grupo real que ocasionó el fallo y se agregó como fixture de regresión, además de tests de gradiente, restricciones, parsimonia e independencia de la verdad externa. No se descartó un candidato por su error de validación ni se sustituyeron fallos por ceros.

Artefactos: `data/processed/robust_affine_audit/` contiene predicciones, elecciones, coeficientes, métricas, compuertas, diagnóstico numérico y hashes. Producción y las iteraciones anteriores quedaron intactas. Pasaron 20 tests Python, 13 JS, lint y build tras incorporar `origin/dev`. Lint presenta advertencias no bloqueantes ya existentes; no se modificó la interfaz en esta iteración.

```sh
uv run python -m unittest discover -s tests -p 'test_*.py' -v
uv run python pipeline/robust_affine_experiment.py
```

Durante el objetivo con plazo se ejecuta con `GOLIAT_RESEARCH_DEADLINE_UTC=2026-11-15T00:00:00Z`. La variable es opcional para permitir reproducción posterior autorizada; hay un test que comprueba su enforcement.

## Siguiente pregunta fijada por la evidencia

La mayor parte de la mejora sigue ocurriendo donde Aqua es positivo, mientras que el intercepto añade actividad en ceros. Conviene comparar una calibración monótona no lineal **anclada en cero**, con complejidad similar al afín, antes de aumentar la familia de políticas. Esto no cambia la población de detecciones ni busca más comunas habilitadas. La revisión temporal se hará después de congelar los candidatos, manteniendo el bloque 2020–2021 como descriptivo.
