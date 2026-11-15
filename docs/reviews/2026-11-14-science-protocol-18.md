# Protocolo 18 — decisión aditiva y asignación coherente

Fijado antes de calcular scores nuevos. Motivación: etapa17 mejora MAE comunal con medianas pero empeora totales regionales. Se evalúan funcionales de la misma CDF E11, κ=10 fijo, sin nuevo aprendizaje ni grillas de mezclas. Investigación retrospectiva adaptativa, no nuevo holdout.

## Métodos predefinidos

1. `E_mean`: media exacta de la CDF de17. Para cada fila, μ=p Σw max(1,s z)/Σw. El truncamiento ocurre por átomo, antes de la esperanza. No asumir que corrige sesgo observado; reportar MAE, MSE, sesgo y error regional sin cambiar retrospectivamente la métrica ganadora.
2. `E_coherent`: para cada temporada-mes con las54comunas, minimizar Σ E_Fi |Yi−ai| sujeto ai≥0 y Σai=T, donde T=ΣBi. Los Fi son los de17κ10 y B es la política base del mismo origen. Resolver convexidad por segmentos de coste marginal2F−1. En la cara de soluciones empatadas, elegir la más cercana a B en distancia euclídea cuadrada. Sin etiquetas destino.
3. `E_proportional`: control simple, redistribuir T proporcionalmente a medianas E11_10; si suma de medianas es cero, usar B. Permite distinguir optimización de pérdida de mero reescalamiento. No seleccionar entre estos métodos después de medir para reportar solo el ganador.

El total de los dos reconciliados será exactamente B por construcción, por lo que igualdad del error regional no es nueva habilidad predictiva regional. Ambos heredan errores del presupuesto B. La distribución discreta es predictiva de detecciones registradas S-NPP, no probabilidad física de fuego ni oportunidad de observación.

## Evaluación y controles

Primaria de reconciliación: MAE comunal frente a B sobre las mismas5184filas nested. Ganancia útil de trabajo >1 %, junto a conservación regional y sesgo agregado de B (tolerancia relativa1e-10). Describir todos los transportes4/6 adelante/atrás, 2020–2021 y2022–2025 como destinos ya consultados, estratos activos, ambos0, Aqua0/SNPpositivo, SNP≥50,14publicadas y40restantes. No exigir éxito futuro desconocido ni interpretar multiplicidad exploratoria como confirmación independiente.

Usar ochoCDF externas guardadas por17; para transporte reconstruir solo los cuatro ajustes de origen y comprobar que reproducen E11_10 guardado a1e-10 antes de extenderlos. Modelo completo ya congelado por17. Comparar controles de origen y hashes de entradas; no modificar predicciones de17. Reportar cambios emparejados por temporada y bootstrap5000semilla20261114 exploratorio.

Pruebas del solver: oracle exhaustivo en dos filas, presupuesto cero, distribuciones degeneradas, permutación de filas, entradas inválidas, suma conservada y riesgo esperado≤riesgo de B. Esa última garantía solo vale bajo la CDF ajustada, no garantiza menor error observado. Verificar que quitar/cambiar etiquetas de destino no cambie ninguna predicción.

No cambiar producción, M1/14, indicadores publicados ni datos base. Salidas nuevas en `data/processed/coherent_audit/`. Si reconciliar no mejora, mantenerlo como resultado negativo y evitar más grillas esta noche. La etapa observacional G0/G1 es independiente; acceso a archivos no implica elegibilidad científica de píxeles.
