# Diagnóstico de concentración de la mejora

Fijado antes de calcular este desglose. No ajusta modelos, selecciona políticas ni cambia compuertas. Reutiliza las 5.184 predicciones anidadas existentes para M1, M1/B, M1/H y M1/B/P, verificando claves, etiquetas y controles compartidos.

Por comuna y candidato calcular MAE M1, MAE candidato y beneficio absoluto (M1−candidato). Contar comunas con beneficio positivo, deterioro o igualdad usando tolerancia fija 1e-10. Resumir mediana e intervalo intercuartil de beneficio absoluto, ganancia bruta positiva, deterioro bruto, beneficio neto y proporción de ganancia bruta positiva concentrada en las cinco comunas de mayor beneficio. Reconciliar la media de los 54 MAE con los resúmenes originales a tolerancia 1e-10.

Repetir el resumen en las 14 comunas publicadas y las otras 40; esa pertenencia usa la publicación ya fijada. Es un desglose condicionado por selección, no un experimento independiente. Publicar las 54 filas por candidato, con nombres de la tabla CUT oficial. No ordenar candidatos para promover el mejor de este diagnóstico ni crear una nueva lista de habilitaciones. Todos los cálculos son retrospectivos sobre el desarrollo ya consultado.
