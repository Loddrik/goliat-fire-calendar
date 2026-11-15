# Protocolo 11 — ajuste completo congelado, discrepancia temporal y bandas

Fijado antes de calcular resultados 2020+ de estas políticas. Base 15b9d0c. Objetivo: comprobar el transporte descriptivo de los candidatos actuales y la cobertura empírica de bandas aprendidas sin consultar esos períodos. No convertir períodos ya consultados en un nuevo test independiente ni actualizar producción.

## Congelación con 2012–2019

- Entrenamiento completo: ocho temporadas 2012–2019, grilla/cartografía publicadas y máscara aprendida con esas temporadas más las anteriores; debe coincidir exactamente con las 223 celdas publicadas.
- Ajustar las mismas familias y regularizaciones B, H y P, con referencias M0, M1 y M2. M1 se ajusta con el origen completo y debe reproducir el factor publicado 2,352954072125397. Mantener las políticas M1/B, M1/H, M1/P y M1/B/P, sin añadir candidatos.
- Elegir el candidato final de cada política/comuna usando únicamente las predicciones fuera de fold 2012–2019 ya versionadas en los protocolos 4–5. Cada predicción candidata se ajustó excluyendo su temporada y recalculando la máscara. Reusar las funciones de selección y regla >1 %, con sus desempates existentes; no elegir por error 2020+.
- Comprobar coincidencia exacta de claves, Aqua y S-NPP al unir los artefactos de H y P. Guardar elección, pérdida OOF, coeficientes completos y firma del ajuste congelado en un directorio de investigación separado. Las familias/selección ya fueron desarrolladas sobre esas ocho temporadas; no reclamar independencia del desarrollo adaptativo.

## Destinos y oportunidad de observación

1. Bloque heredado 2020–2021, **descriptivo**. Excluir meses calendario agosto y septiembre de 2020 de ambos sensores por la interrupción de Aqua, igual que el protocolo original.
2. Bloque diagnóstico 2022–2025, **descriptivo y separado**. No ajustar ni elegir políticas con él.
3. La [documentación NASA](https://science.nasa.gov/mission/a-train/) sitúa el inicio de deriva libre de Aqua en enero de 2022. Como una temporada julio–junio no es un año calendario, **enero–junio de 2022 pertenece a temporada 2021**. Además de los bloques heredados, marcar cada mes por año calendario y reportar el bloque 2020–2021 separado en meses anteriores a enero de 2022 y meses de transición enero–junio de 2022. No llamar a todo el bloque heredado «anterior a deriva» ni atribuir cambios de error solo al sensor.

Construir panel completo 54 comunas×72 meses y retirar las dos interrupciones conocidas: 3.780 pares en total, 1.188 heredados y 2.592 diagnósticos. Objetivo S-NPP observado, predictor Aqua; **no concatenar NOAA-20/21**, cuyo puente local presenta discrepancias adicionales. Verificar fuentes SP solicitadas y registrar NRT; detenerse si los períodos supuestamente SP contienen celdas-día provisionales. Ventanas solicitadas completas no demuestran observabilidad; un cero de detecciones no demuestra ausencia de actividad física.

## Métricas y bandas fijadas

- Errores por comuna/temporada y agregados: MAE mensual de las 54 comunas, sesgo, suma de error absoluto; también MAE de la suma regional mensual, para mostrar la diferencia entre discrepancia local y compensaciones regionales. Reportar cada temporada, ambos bloques y transición calendario.
- Comparar todas las políticas con M1 y climatología sin seleccionar una ganadora con el destino. Las 14 comunas publicadas constituyen un subgrupo preexistente; publicar resultados para ese conjunto fijo y para todas las comunas, sin nuevas compuertas.
- Radios alternativos por comuna/política: percentil 80 del error absoluto en meses S-NPP>0, calculado **solo con las estimaciones de política del LOSO anidado de 2012–2019** (cada política eligió su candidato dentro del entrenamiento de su fold externo). No calcular radios con los candidatos finales seleccionados sobre las mismas etiquetas OOF. Registrar número de meses activos de calibración; estos objetivos usan máscaras aprendidas por fold y el destino usa máscara final, una limitación de transporte explícita.
- Intervalo descriptivo `[max(0, estimación−radio), estimación+radio]`. Reportar cobertura y anchura tanto en todos los meses como en meses S-NPP>0; el estado activo solo define el análisis, nunca selecciona el radio al consultar el destino. Un cuantil empírico no garantiza cobertura futura ni constituye una banda de confianza de incendio real.
- Referencia de publicación: M1 con valor y radio de error típico redondeados a una décima como `publish.py`, tomando el radio de cada JSON comunal. Evaluar su cobertura sobre las 14 habilitadas, y separadamente las alternativas q80 sin redondear. No comparar radios de distinta calibración como si fueran el mismo nivel nominal.
- Desglosar Aqua=0/S-NPP>0, ambos sensores cero y meses S-NPP≥50, umbral heredado. No usar bootstrap inferencial con dos temporadas ni tratar meses/comunas como réplicas independientes. No calibrar nuevos radios tras ver cobertura desfavorable.

## Artefactos y verificación

Nuevo directorio `data/processed/frozen_temporal_audit/`: coeficientes, elecciones, calibración de radios, predicciones, errores, cobertura por comuna/bloque y resumen; manifiesto con hash de entradas, código, helpers, entorno, protocolo, modelo congelado y archivos protegidos. Tests de exclusión temporal, unión OOF estricta, independencia de objetivos futuros, bandas y transición calendario. Reproducir M1 publicado y controles del panel antes de interpretar resultados. No tocar `publish.py`, `publish_web.py`, parámetros ni JSON publicados. Los PR siguen a dev; commits Daniel Quinteros sin firma; control de deadline a las 21:00 de Santiago.
