# Revisión independiente 39 — CRPS de las CDF21 congeladas

**Dictamen: verificación completa PASS; primaria favorable a F21 frente a δB, con costes territoriales y extremos que impiden afirmar dominancia.** La revisión terminó el 15 de noviembre de 2026 a las 08:57:35.997463 UTC, dentro del cap absoluto 08:43–10:13 UTC. No quedan bloqueantes de correspondencia entre protocolo, implementación y resultados revisados.

El contraste primario prefijado, media con igual peso de cuatro diferencias held `CRPS(F21)−MAE(B)`, es **−0.6181638838629885**. La integral independiente produce −0.6181638838629886; la diferencia corresponde al redondeo numérico entre algoritmos. Menor CRPS es mejor y los cuatro regímenes favorecen a F21 en su promedio held. El promedio ponderado por filas, secundario, es −0.5713792772177094.

| Régimen | N held | CRPS medio F21 | CRPS medio δB = MAE(B) | Diferencia |
|---|---:|---:|---:|---:|
|08_backward|1008|1.6749993501|2.1533948542|−0.4783955041|
|08_forward|1008|1.8464397058|3.0254334293|−1.1789937234|
|16_backward|1584|1.4750271801|1.8294557416|−0.3544285615|
|16_forward|1584|1.6907906943|2.1516284407|−0.4608377464|

Estos valores permiten retener la rama de investigación de forecasts marginales F21 bajo esta comparación retrospectiva concreta. No identifican un beneficio aislado de la dispersión: F21 y δB difieren también en localización. No demuestran calibración, valor adicional de Aqua, coherencia conjunta entre 54 CUT, exactitud física ni generalización a un holdout fresco. G sigue siendo una decisión puntual, sin distribución reconciliada inventada. Los negativos 23/35/37 no cambian.

## Guardrails que acompañan el promedio

Los reportes completos se conservaron y verificaron. Algunos costes prefijados son adversos, aunque la primaria sea favorable:

| Régimen y población held | N | Diferencia media F21−δB |
|---|---:|---:|
|16_forward, publicados 14, todos los meses|288|+0.2762319394|
|16_backward, referencia Y=0|761|+0.1029928347|
|16_backward, extremos Y≥50|11|+10.0760698298|
|16_forward, extremos Y≥50|14|+15.6025483818|

Son estratos fijados antes de resultados, no nuevas reglas para seleccionar el método. No se ocultan con el promedio ni se convierten retrospectivamente en otra primaria. El resultado es favorable para el contraste agregado y condicionado por estos costes; no respalda una mejora uniforme.

## Oráculos y reconstrucción

Antes de cualquier score real, un oráculo independiente construyó 14 fixtures analíticos con `Fraction`: integral exacta de la discrepancia cuadrática de CDF entre knots, verificada además contra la doble suma exacta. Incluyen δ, observación dentro/fuera del soporte, masas racionales, empates, pesos 0, reordenamiento, división de masas, átomos no enteros y floor 1. El helper congelado del productor coincidió en todos los casos dentro de la tolerancia prefijada. Esta evidencia se guardó antes de abrir la evaluación real y el productor conservó su comparación separada.

El verificador completo se congeló con código e inputs por SHA. Restauró **10368 CDF y 444826 elementos de soporte** desde los modelos 21 y sus consultas, sin fit ni reconciliación. Una implementación propia reconstruyó desde JSON las probabilidades parent/local y los soportes RAWZ; no usó `_components` para ese oráculo. Los arrays exportados de átomos y pesos originales coincidieron exactamente con la restauración congelada 21. La reconstrucción alternativa de pesos desde JSON difirió como máximo 5.551115123125783e−17. Se verificaron B, mediana original, media, roles, 54 CUT por mes, soporte no negativo, pesos válidos, sumas y **normalización única mediante fsum**. Se conservaron empates y pesos 0. Las 5184 consultas held tienen identidad exacta de CDF completa con el parent: esto es un control estructural, no un brazo comparativo nuevo.

Para **cada una de las 10368 respuestas**, el revisor calculó la integral directamente sobre los intervalos de `sorted(unique(atoms∪{Y}))`. La CDF en cada extremo izquierdo se obtuvo sumando las masas de átomos menores o iguales, sin llamar al CRPS del productor ni usar su fórmula de prefijos de esperanza/semidiferencia. La máxima discrepancia frente al score crudo del productor fue **2.1316282072803006e−14**, dentro de τ para todos los casos. Todos los scores de δB coincidieron con `abs(B−Y)`. No hubo filas con clamping negativo. Se comprobaron también Eabs, EabsX, término semipar, tolerancia, score crudo y flags.

La unión de targets por claves fue exacta y sus dos copias por clave global coincidieron sin promediar. Se verificaron los **216 reportes de población/estrato y 432 conjuntos por forecast**, las tablas de todos los CUT, los cuatro contrastes y el agregado secundario. El peor CUT held por régimen se reconstruyó usando exclusivamente el MAE del B original y desempate por CUT, como diagnóstico prefijado. La primaria se recalculó también directamente desde las integrales independientes, además de comprobar la aritmética de las cifras serializadas.

## Procedencia, recursos y alcance

El checkpoint/CDF freeze terminó a las 08:54:37.636703 UTC, antes del límite 09:03 y antes del primer join real de respuestas. Los dos freezes del productor, sus versiones de entorno, sus modelos 21 y los hashes protegidos se verificaron antes y después. Se preservaron todos los originales; la evidencia del revisor es separada.

Productor y revisor realizaron **0 fits, 0 solvers y 0 adquisiciones científicas**. Restaurar una CDF de parámetros congelados no se contabilizó como ajustar otro modelo. El productor emitió aproximadamente 2.26 MB antes del manifiesto, muy por debajo de 100 MiB; el RSS observado del revisor fue 281804800 bytes, por debajo de 2 GiB. Las fórmulas puntúan la distribución finita emitida; no aplican corrección fair-ensemble ni redondean átomos a conteos enteros.

La referencia continúa siendo actividad SNP registrada en celdas-día mensuales, no incendios ni oportunidad observacional. Los cuatro regímenes se solapan y los destinos ya se han consultado durante el desarrollo: no son réplicas IID ni evidencia fresca. G1 físico sigue false; 30B permanece fallido y ninguna cifra autoriza producción, cambios de M1, gates, κ o máscaras.

Evidencia: [fixtures exactos anteriores a scores reales](evidence/crps-independent-review/synthetic-preflight/fixtures.json), [comparación sintética independiente](evidence/crps-independent-review/synthetic-producer-comparison/summary.json), [código completo congelado](evidence/crps-independent-review/full-review/reviewer-code.py.txt), [freeze del revisor](evidence/crps-independent-review/full-review/freeze.json), [todas las integrales](evidence/crps-independent-review/full-review/all-query-independent-integrals.csv), [resumen verificable](evidence/crps-independent-review/full-review/summary.json) y [manifiesto independiente](evidence/crps-independent-review/full-review/manifest.json).

- Protocolo 39: SHA256 `ef2be85264a1e91b334e4aabcc6e28feceeaf2556f002946a43f52737cc2bd38`.
- Freeze completo del revisor: SHA256 `dec2c6125bf60472a9a275b8723d36ab1bd1077813f327a53febe36ae3305606`.
- Manifiesto productor antes/después: SHA256 `aec1533e33b1d354c6102daf51d51d295d449f2afc15cf5ae50d2fe9719779ea`.
- Resumen independiente: SHA256 `a96042e91f2e724d5a47e76da232076dfb2c60e7985a90aaa1ba04f006fe6aae`.
- Manifiesto independiente: SHA256 `25a17776cb335b346c4264a00322d3e74be38b82efa8de2ae6c15cb8c3bed112`.
