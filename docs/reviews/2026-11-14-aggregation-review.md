# Concentración comunal de las mejoras retrospectivas

**El beneficio medio no describe una mejora uniforme.** M1/B reduce error en 22 comunas, lo aumenta en 17 y empata en 15. La mediana del beneficio absoluto entre comunas es cero. No se promueven modelos ni nuevas compuertas.

Se ejecutó el [protocolo](2026-11-14-aggregation-protocol.md) sobre las 5.184 predicciones anidadas existentes. No hay ajustes nuevos, consulta de destinos nuevos ni selección adicional. Las medias de los 54 MAE comunales reconcilian los resúmenes originales a tolerancia 1e-10.

| Política | Mejoran | Empeoran | Iguales | Mediana del beneficio absoluto | Cinco mayores / ganancia bruta | Mejora MAE en las 14 publicadas |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| M1_B | 22 | 17 | 15 | 0.00000 | 49.14 % | 3.45 % |
| M1_H | 24 | 19 | 11 | 0.00000 | 46.98 % | 6.75 % |
| M1_B_P | 30 | 12 | 12 | 0.02647 | 45.26 % | 3.76 % |

Beneficio absoluto = MAE M1 − MAE candidato, en celdas-día mensuales; positivo significa menor error. Igualdad usa tolerancia 1e-10. La concentración divide la suma de las cinco mayores mejoras positivas por la suma de todas las mejoras positivas, sin ocultar deterioros compensándolos en el denominador. No es participación sobre beneficio neto.

B/P mejora más comunas que B, pero esa distribución no revierte su deterioro en el transporte hacia atrás. H mejora más el subconjunto publicado en este desarrollo, sin establecer una recomendación nueva. Las 14 comunas se seleccionaron con evidencia relacionada; el desglose está condicionado por selección. No interpretar los conteos de comunas como ensayos binomiales independientes: comparten temporadas, condiciones regionales y partes del ajuste.

`data/processed/aggregation_audit/commune_errors.csv` conserva las 162 filas (54 comunas × 3 políticas), nombres de la tabla CUT oficial, MAE, beneficio y pertenencia publicada. El resumen incluye también ganancias/deterioros brutos, beneficio neto, mediana y cuartiles en los tres grupos. El manifiesto protege insumos, publicación, resultados previos, nombres, código y entorno. No se modifica ninguna estimación ni compuerta.
