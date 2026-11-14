# Protocolo 14 — Terra como información adicional, sin sumar plataformas

Fijado antes de comparar los nuevos modelos. Base 4b8bfed. Los Parquet existentes contienen Terra diurno desde temporada 2000 y Aqua desde 2002. Solo se verificó disponibilidad y esquema; no se ajustó ni puntuó el nuevo candidato. Pregunta: ¿Terra añade señal a Aqua frente a S-NPP, especialmente donde Aqua=0, o basta con estacionalidad adicional?

## Datos y controles

Usar las 54 comunas, grilla/cartografía publicadas, mismos filtros y celdas-día UTC ya versionados. No descargar ni cambiar datos base, máscara, confianza o fuentes; no añadir noche. Agregar Terra como **columna separada**, con la misma máscara aprendida dentro de cada partición. No sumar Terra+Aqua ni tratarlas como observaciones equivalentes; sus horarios y fuentes de discrepancia son distintos.

Mantener M0 Aqua, M1 factor regional, M2 climatología y selección M1/B como controles. Exigir que Aqua, S-NPP, referencias y M1/B reproduzcan sus predicciones anidadas previas. Los ceros siguen siendo conteos de detección, no ausencia física de fuego ni prueba de cobertura.

## Nuevo modelo C y ablación D

Por comuna y grupo mensual g de las etapas previas (junio/julio/agosto agrupados), estimar:

`p = max(0, a + bA*Aqua + bT*Terra)`, con bA,bT≥0.

Usar normalización de entrenamiento sA=max(1,RMS regional Aqua en g) y sT=max(1,RMS regional Terra en g). Definir βA=bA*sA, βT=bT*sT. Minimizar error cuadrático medio más

`λ * [a² + (βA − r_g*sA)² + βT²]`,

con r_g la referencia regional Aqua/S-NPP de entrenamiento. Mismos λ de B: {0,01;0,1;1;10}, sin ampliar la grilla. El prior de Terra es cero: debe aportar evidencia para separarse del modelo sin esa señal. Intercepto libre, pronóstico recortado a cero; no interpretar pendientes como conversión física ni causalidad.

Resolver exactamente las ecuaciones normales de tres variables y enumerar las cuatro caras posibles de las dos restricciones de pendiente. Seleccionar la solución factible con menor objetivo, exigir finitud y KKT≤1e-6. Con Terra idénticamente cero, C debe reducirse numéricamente a B para cada λ.

**Ablación D:** reemplazar Terra por su mediana comunal de mes calendario aprendida exclusivamente en el entrenamiento, tanto al ajustar como al evaluar. Mantener las normalizaciones calculadas con Terra real del entrenamiento, mismos priors y λ. D añade patrón estacional sin información Terra del mes destino; no debe acceder a su valor real. Comparar C y D como diagnóstico de aportación temporal, sin afirmar identificación causal de ese aporte.

## Selección y evaluación predefinidas

- Primario: LOSO externo 2012–2019 con siete folds internos; máscara, escalas, climatología Terra y parámetros recalculados dentro del origen correspondiente. Excluir la temporada externa de todo aprendizaje.
- Elegir λ por MAE interno, desempate hacia mayor regularización. Políticas: **M1/C** (C debe mejorar M1 >1 %), **M1/B/C** (C debe mejorar el M1/B elegido >1 %) y **M1/B/D** (misma regla para la ablación). Mantener el comparador M1/B; no seleccionar entre C y D con el destino.
- Reportar MAE, sesgo, error absoluto total, errores por comuna/temporada y MAE de suma regional mensual. Comparaciones y diferencias por ocho temporadas, sin tratar meses/comunas como réplicas independientes. Las temporadas ya se consultaron: desarrollo retrospectivo, no holdout nuevo.
- Subgrupos obligatorios: todas las 54 y las 14 publicadas; S-NPP=0, 1–9, 10–49 y ≥50; Aqua=0/S-NPP>0 separado por Terra=0 o >0; Aqua=0/S-NPP=0 también separado por Terra; Aqua>0. No describir ceros de detección como incendios ausentes, ni la mejoría de un subgrupo como resultado global.
- Guardar elecciones, pendientes Terra y contribuciones estimadas por las dos fuentes. Que se elija C no habilita una comuna; las compuertas publicadas basadas en Aqua no se reinterpretan automáticamente como reglas de evidencia para dos predictores.

## Transporte temporal y destinos posteriores

Repetir cuatro casos ya definidos, con selección LOSO solo en cada origen y máscara fold_fitted:

1. Origen 2012–2015 → destino 2016–2019.
2. Origen 2016–2019 → destino 2012–2015.
3. Origen 2012–2017 → destino 2018–2019.
4. Origen 2014–2019 → destino 2012–2013.

Reproducir los controles M1/B de los casos de etapas 8 y 10. No escoger solo dirección o tamaño favorables ni construir intervalos inferenciales con dos destinos.

Congelar elección final con predicciones candidatas OOF de 2012–2019 y ajuste completo con esas ocho temporadas. Guardar coeficientes/climatología/elecciones antes de evaluar los 3.780 pares posteriores de etapa 11, agregando únicamente Terra con la máscara final de 223 celdas. Exigir reproducción del factor y M1/B congelados previos. Mantener excluidos agosto/septiembre 2020; no atribuir a Terra la capacidad de suplir una interrupción Aqua que no se evalúa. Mantener bloques 2020–2021 descriptivo y 2022–2025 diagnóstico con transición calendario enero–junio 2022; no son validación independiente nueva. Registrar provisionalidad Terra y detenerse si se mezclan NRT inesperados con ventanas SP.

## Artefactos, tests y plazo

Nuevo `data/processed/terra_feature_audit/`: agregados/diagnósticos de predictores, parámetros y selecciones, predicciones anidadas/bloqueadas/posteriores, métricas, resumen y manifiesto. Todos los datos y artefactos previos intactos. Tests de equivalencia C(T=0)=B, objetivo/condiciones KKT en sus caras, señal Terra sintética, normalización/climatología solo de origen, ablación sin acceso a Terra futuro, exclusión temporal y reproducción de controles reales. No cambiar `publish.py`, `publish_web.py`, JSON públicos o compuertas. PR a dev, commits Daniel Quinteros sin firma, control de deadline hasta 21:00 de Santiago.
