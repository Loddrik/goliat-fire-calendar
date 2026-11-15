# Revisión 18 — mejor asignación local conservando el presupuesto de B

El [protocolo 18](2026-11-14-science-protocol-18.md) compara tres decisiones predefinidas sobre la misma distribución E11 de la etapa 17, con κ=10 fijo y sin nuevas grillas. **E_coherent reduce el MAE comuna-mes de 1,903194 a 1,797939: una mejora del 5,530 % frente a B.** Conserva los totales mensuales de B en las 54 comunas por construcción. Es una mejora retrospectiva de la asignación territorial a un presupuesto heredado, no una nueva capacidad para estimar el total regional ni una validación independiente.

## Comparación completa de decisiones

Resultados nested 2012–2019 sobre las mismas 5.184 filas:

| Método | MAE | MSE | Sesgo medio | Suma estimada | MAE regional mensual |
|---|---:|---:|---:|---:|---:|
| M1 | 2,047245 | 31,414738 | +0,014950 | 21.566,503 | 47,254789 |
| B | 1,903194 | 23,287463 | −0,087189 | 21.037,010 | 31,546960 |
| E11, mediana sin reconciliar | 1,808210 | 22,404691 | −0,731078 | 17.699,089 | 49,535897 |
| E_mean, media exacta | 2,046114 | 26,689756 | +0,272902 | 22.903,725 | 42,728613 |
| **E_coherent, asignación L1** | **1,797939** | **19,032810** | **−0,087189** | **21.037,010** | **31,546960** |
| E_proportional, reescalamiento | 1,859192 | 20,557817 | −0,087189 | 21.037,010 | 31,546960 |

La media integra exactamente cada átomo positivo tras convertirlo a la escala destino y aplicar el mínimo de una celda-día. Empeora el MAE un 7,510 % y también el MSE frente a B. Aunque la media es óptima para pérdida cuadrática bajo su propia distribución, esa propiedad no garantiza menor error observado si la distribución predictiva está mal especificada.

El control proporcional mejora el MAE un 2,312 %. E_coherent alcanza 1,797939 frente a 1,859192 de ese control: el avance observado no se explica enteramente por reescalar las medianas. Son decisiones alternativas, no ganancias independientes que puedan sumarse a las de la etapa 17. Tampoco E_coherent domina todas las decisiones en cada población o transporte.

## Conservación y dependencia del presupuesto

E_coherent minimiza la suma de pérdidas absolutas esperadas bajo las CDF ajustadas, sujeto a asignaciones no negativas cuya suma mensual coincide con B. Entre óptimos empatados elige el más cercano a B en distancia euclídea. El total observado nested es 21.489; el total heredado, 21.037,010, conserva también el déficit de B. La igualdad del MAE regional y del sesgo global es una consecuencia algebraica de esa restricción.

La conservación corresponde al **universo fijo de 54 comunas**, reconciliado antes de filtrar un área. No se exige conservación separada para las 14 publicadas, las 40 restantes ni los estratos definidos por la referencia. Una consulta sobre un subconjunto debe conservar las asignaciones ya calculadas para el universo completo; reconciliar de nuevo el subconjunto produciría otra decisión.

| Población nested | Filas | MAE B | MAE E_mean | MAE E_coherent | MAE proporcional |
|---|---:|---:|---:|---:|---:|
| 14 publicadas | 1.344 | 2,999471 | 3,035181 | **2,816152** | 2,941017 |
| 40 restantes | 3.840 | 1,519497 | 1,699941 | **1,441565** | 1,480553 |

E_coherent mejora el MAE un 6,112 % en las 14 y un 5,129 % en las 40. Sin embargo, **el sesgo de las 14 empeora de −0,421417 a −0,630788**; su suma baja de 9.845,616 a 9.564,221. Su MAE agregado mensual mejora de 18,748498 a 16,564526. En las 40, el sesgo aumenta de +0,029790 a +0,103070 y el MAE agregado pasa de 20,479695 a 21,748618. La compensación entre ambos grupos preserva únicamente el presupuesto conjunto. El modelo sigue dependiendo de los errores y de la política de selección de B.

## Estratos: la mejora no elimina todos los costes

| Estrato, 54 comunas | Filas | MAE B | MAE mediana E11 | MAE media | MAE coherente | MAE proporcional |
|---|---:|---:|---:|---:|---:|---:|
| Referencia positiva | 2.563 | 3,565127 | 3,511262 | 3,469093 | **3,302380** | 3,546450 |
| Referencia cero | 2.621 | 0,278038 | 0,142844 | 0,654625 | **0,326790** | 0,209271 |
| Ambos sensores registran cero | 2.491 | 0,159746 | 0,041349 | 0,548604 | **0,201006** | 0,059871 |
| Aqua cero y S-NPP positivo | 1.152 | 1,803305 | 1,953125 | 1,385959 | **1,655785** | 1,933467 |
| Referencia ≥50 celdas-día | 74 | 19,708540 | 22,961981 | 25,722694 | **18,917949** | 19,254231 |

La asignación coherente mejora actividad positiva, casos omitidos por Aqua y meses intensos frente a B, pero añade más cantidad donde S-NPP registra cero. En las 14, el MAE de ambos ceros pasa de 0,211781 a 0,334779; en los 40 meses intensos de ese grupo el sesgo pasa de −2,577705 a −5,653178, aunque su MAE mejora de 19,376366 a 18,205585. En los 34 meses intensos de las 40 restantes, el sesgo pasa de −2,020598 a +6,842187. La mejora global no demuestra ausencia de redistribuciones indeseables. Los estratos se solapan y sus resultados no se suman como experimentos independientes.

## Transporte, temporadas e incertidumbre exploratoria

| Bloque | B | Mediana E11 | Media exacta | Coherente | Proporcional |
|---|---:|---:|---:|---:|---:|
| 4 temporadas hacia adelante | 2,239129 | 1,919541 | 2,299163 | 2,115970 | 2,180145 |
| 4 temporadas hacia atrás | 1,861186 | 1,828707 | 2,002892 | 1,779354 | 1,822013 |
| 6 temporadas hacia adelante | 1,931063 | 1,708109 | 2,165360 | 1,791467 | 1,843317 |
| 6 temporadas hacia atrás | 1,716298 | 1,681774 | 1,924421 | 1,676779 | 1,707204 |
| 2020–2021, descriptivo | 1,960280 | 1,847724 | 2,090787 | 1,913429 | 1,946040 |
| 2022–2025, descriptivo | 2,374788 | 2,217186 | 2,358355 | 2,202605 | 2,268191 |

E_coherent mejora frente a B en los cuatro transportes y en las dos consultas posteriores. La mediana sin reconciliar mantiene menor MAE local en varios destinos, a cambio de su deterioro regional documentado en la etapa 17. Los dos reconciliados conservan exactamente el MAE regional de B en cada bloque; no debe presentarse esa igualdad como validación adicional. Los destinos posteriores ya se habían consultado y siguen siendo descriptivos.

E_coherent mejora frente a B en las **ocho temporadas nested**. La diferencia media de MAE es −0,105255, con intervalo percentil exploratorio 95 % **[−0,160217; −0,059814]**. Para la media, la diferencia es +0,142920, intervalo [+0,075728; +0,210070]; para el proporcional, −0,044002, intervalo [−0,106061; +0,003455], que incluye cero. Se emplean ocho bloques, 5.000 réplicas y semilla 20261114. Estos intervalos no corrigen la historia adaptativa ni convierten los datos ya explorados en un holdout independiente.

## Auditoría numérica y transparencia

Se reutilizaron los ocho modelos externos de la etapa 17 y su modelo completo congelado; los cuatro ajustes de transporte se reconstruyeron únicamente con sus orígenes y reprodujeron las medianas guardadas a tolerancia 1e-10. El runner separa las etiquetas de las variables de decisión; la prueba real de invariancia a etiquetas ausentes se ejecuta en nested, y las pruebas sintéticas incluyen etiquetas cambiadas. El mismo camino de inferencia se usa para los demás destinos.

`allocation_checks.csv` contiene **310 grupos mensuales completos**: 96 nested, 144 de los cuatro transportes y 70 posteriores. El máximo error absoluto de presupuesto es **9,095×10⁻¹³** y el máximo residuo KKT **2,220×10⁻¹⁶**. Hubo **cero asignaciones por encima del soporte máximo individual** en todos los bloques. El solver permite ese caso como extensión lineal válida de la pérdida, pero no fue necesario aquí. En todos los grupos el riesgo esperado ajustado es menor al de B; esa garantía pertenece a la CDF aprendida y no garantiza menor error real. Las tolerancias numéricas del solver permanecen fijas.

El primer intento se detuvo antes de puntuar por una comparación de identidad exacta: la suma mediante BLAS difería **8,9×10⁻¹⁶** entre evaluaciones equivalentes. Se sustituyó por acumulación determinista `math.fsum` antes del scoring, sin cambiar candidatos, particiones ni parámetros. El manifiesto identifica la ejecución corregida con el commit `cb6d4cdfb10edbdba0dcd29f74c807e7921d907e` y conserva hashes de entradas, código, protocolo y salidas. La interrupción y corrección numérica deben acompañar el resultado, no ocultarse como una selección posterior de modelos.

## Decisión

Conservar E_coherent como candidato de investigación para una asignación local coherente con B: supera el umbral de trabajo del 1 %, mejora las ocho temporadas y los cuatro transportes, y reduce el coste regional observado en la etapa 17 mediante una restricción explícita. **No promover a producción ni cambiar las 14 comunas publicadas.** Persisten mayor cantidad en ceros registrados, sesgos de subgrupos, dependencia del presupuesto B y ausencia de información sobre oportunidad de observación. Las decisiones puntuales tampoco reconcilian intervalos ni constituyen un modelo probabilístico conjunto regional.

Fuente reproducible: `data/processed/coherent_audit/summary.json`, `allocation_checks.csv`, `manifest.json`, modelos de transporte y predicciones nested, de transporte y posteriores del mismo directorio. No se modificaron resultados, código ni artefactos publicados al redactar esta revisión.
