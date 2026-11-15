# Protocolo 10 — tamaño de entrenamiento y máscara en transporte temporal

Fijado antes de calcular los resultados de estos casos. Base 7af20eb. El protocolo 8 mostró degradación de candidatos hacia atrás y máscaras distintas con cuatro temporadas. Este diagnóstico mantiene las familias congeladas y no busca una combinación favorable para publicación.

## Destinos fijos y todos los subconjuntos de origen

- **Reconstrucción hacia atrás:** destino 2012–2013; conjunto de origen completo 2014–2019.
- **Transporte hacia adelante:** destino 2018–2019; conjunto de origen completo 2012–2017.

En cada dirección, ajustar con las seis temporadas de origen y, por separado, con **las 15 combinaciones posibles de cuatro de esas seis**. Así no se elige solo un bloque de cuatro particularmente cercano o lejano al destino. Los subconjuntos se fijan combinatoriamente, no por su resultado. Se usa el mismo destino de dos temporadas para todos los casos de una dirección. No se incluyen datos 2020+ ni CONAF.

Cada caso selecciona por comuna mediante LOSO únicamente del origen (cuatro o seis folds internos); ajuste final sobre su origen completo. Familias M0, M1, M2, M1/B, M1/H, M1/P y M1/B/P; mismas regularizaciones, umbral regional de P, priors, tolerancia Huber y regla interna >1 % de protocolos 3–5. No modificar candidatos en función de resultados del destino.

## Dos contratos de máscara

1. **Primario, máscara anterior al solape:** aprender una única máscara exclusivamente con detecciones de temporadas anteriores a 2012 (`AuditData.fit_mask(())`), usando las reglas existentes. Mantenerla constante para todos los ajustes internos, orígenes y destinos. El conjunto objetivo de cada dirección será exactamente idéntico entre los 16 casos. Esto permite comparar errores sobre el mismo objetivo. La máscara no es la publicada ni tiene por qué excluir todas las fuentes persistentes identificables con años posteriores.
2. **Secundario, máscara aprendida por origen:** mismo contrato fold_fitted de los protocolos previos; cada máscara interna/final usa solo sus temporadas permitidas y datos anteriores a 2012. Aquí el objetivo cambia entre casos cuando cambia la máscara. Reportar sus tamaños y solo comparar cada candidato con M1 dentro del caso; no atribuir diferencias de MAE entre casos a un cambio exclusivo de calidad del modelo.

Los dos contratos usan la misma grilla y cartografía publicadas. No elegir máscara por error menor ni por número de comunas habilitadas. No cambiar los Parquet ni la publicación existente.

## Medidas y límites

- Por caso: MAE, sesgo, error absoluto total y errores por comuna/temporada para todos los métodos; diferencia y reducción porcentual contra el M1 del mismo caso. Registrar selección, origen y composición de máscara final e interna (número y hash).
- Para el contrato primario, exigir igualdad exacta de `cut, season, mes, Aqua, S-NPP` de los 16 destinos de cada dirección. Comparar el resultado de seis temporadas con la distribución completa de los 15 subconjuntos de cuatro: mediana, mínimo, máximo y número de subconjuntos donde cada candidato mejora a M1. No reemplazar esa distribución por su mejor subconjunto.
- Reportar los dos resultados por temporada destino además del agregado. **No construir intervalos bootstrap con solo dos temporadas**, ni tratar comunas o los 15 subconjuntos superpuestos como réplicas independientes.
- La comparación de seis con todos los subconjuntos de cuatro cambia el volumen de ajuste y la estabilidad de selección/normalización, con superposición y composición temporal dependientes. Es un diagnóstico retrospectivo; no identifica una causa única ni valida por sí mismo 2002–2011.
- No producir compuertas nuevas ni seleccionar una política ganadora para producción. Toda modificación posterior requeriría su evidencia y revisión explícitas.

## Artefactos y comprobación

Nuevo directorio `data/processed/training_size_audit/`: predicciones y errores por caso (Parquet para evitar duplicar CSV extensos), selecciones, tamaños/hashes de máscara, agregados, resumen y manifiesto de código/helpers/protocolo/entradas/archivos protegidos. Tests de enumeración completa y disjunta, política de máscara constante, exclusión del destino e igualdad del objetivo primario. Reusar el ajuste/selección verificado del protocolo 8; no recalibrar mirando el destino. Respetar el control de deadline 21:00 de Santiago, commits Daniel Quinteros sin firma, todos los PR a dev.
