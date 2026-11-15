# Revisión independiente 37 — contexto diario y CDF completas

**Dictamen: implementación y resultados reproducidos; resultado comparativo negativo según la regla prefijada.** La revisión completa terminó el 15 de noviembre de 2026 a 08:21:28.108102UTC, dentro del cap absoluto 08:07:07–09:07:07UTC. No quedan bloqueantes de correspondencia matemática o de los reportes revisados. Esto no acredita validez física ni recomienda sustituir G21.

La media con igual peso de los cuatro regímenes held fue **MAE(Qreal)−MAE(Qplacebo)=−0.004926788323947051**, pero **MAE(Qreal)−MAE(G21)=+0.010794137734920661**. El protocolo exige ambos contrastes negativos: la condición conjunta no se cumple. El primer promedio favorable frente al placebo no permite atribuir una mejora útil al orden cronológico ni compensar el deterioro frente a G21. No se cambian agregación, κ, semilla, rasgo, grilla o panel para rescatarlo.

| Régimen | Filas held | Qreal−Qplacebo, MAE | Qreal−G21, MAE |
|---|---:|---:|---:|
|08_backward|1008|−0.03688613479973357|+0.006596946217436894|
|08_forward|1008|+0.0013414056506775296|+0.028438029017589184|
|16_backward|1584|+0.013144883428317877|+0.010847490445559327|
|16_forward|1584|+0.0026926924249499606|−0.0027059147409027595|

Tres de cuatro regímenes empeoran frente a G21. La comparación es retrospectiva sobre destinos ya conocidos; los regímenes se solapan y no constituyen cuatro réplicas independientes. No se infiere significación ni generalización a un holdout fresco.

## Qué se verificó independientemente

El verificador propio se congeló antes de sus cálculos, con hashes de todos sus inputs y copia exacta del código. No invocó los fit/driver históricos 21 ni el solver de reconciliación. Se reconstruyeron **ocho modelos completos** desde las respuestas SOURCE seleccionadas mediante filtros Parquet de CUT y temporadas de origen, antes de cargar valores. Las dos copias de cada respuesta debían coincidir exactamente y se redujeron a una observación; no se filtró por el régimen antiguo, cuya etiqueta corresponde al destino. Los ocho modelos reconstruidos coincidieron exactamente con los JSON del productor, incluidos todos los pools, soporte positivo RAWZ, locales D, rosters y procedencia del modelo base.

La CDF original se reconstruyó directamente desde sus estadísticas JSON, sin reutilizar `_components` para el oráculo independiente. Sobre esa representación se construyeron las mezclas parent/local completas con κ=10, masa 0 explícita y floor sólo después del escalado de positivos. Se comprobaron **20 736 CDF candidatas**, sus probabilidades de actividad, medianas inferiores y campos de soporte/fallback. También se comprobaron **20 736 consultas del control constante**, D0 y D1 para todos los CUT, con identidad exacta de los arrays de átomos y pesos respecto del control 21. B/G y las claves/roles de las 10 368 predicciones permanecieron exactos.

Se recalcularon directamente los riesgos L1 esperados y las condiciones de subgradiente KKT, sin volver a resolver: **768 controles de asignación** de G, Gconstante, Qreal y Qplacebo. Cada método conserva su presupuesto global de 54 CUT, ΣB y su riesgo bajo su propia CDF no excede el de B. Máximo residual KKT independiente: 2.220446049250313e−16; máximo residual absoluto de presupuesto: 2.2737367544323206e−13. Estos controles no comparan riesgos esperados entre CDF distintas como si compartieran objetivo.

La unión exacta de predicciones congeladas con targets se reconstruyó tras esos controles. Se verificaron **216 poblaciones/estratos y 864 conjuntos de métricas por método**, todos los CUT, los peores CUT held fijados por MAE de G21, los cuatro contrastes primarios y sus agregados secundarios. Ninguna cifra de resultado quedó sustentada sólo en la tabla resumen del autor.

## Freezes, recursos y omisión documental

El checkpoint auditable terminó 08:16:15.611503UTC, antes del límite 08:32:07. El freeze de modelos/predicciones fue 08:18:45.259768UTC y precedió al primer join de evaluación. El verificador confirmó los hashes iniciales y finales del productor y sus fuentes; no modificó código, datos ni manifiestos originales.

El productor contabilizó 21 construcciones de modelo y 768 llamadas reconcile. La revisión agregó 8 reconstrucciones completas, **0 reconcile y 0 repeticiones de fixtures**: subtotal productor+revisor=29fits de un máximo 64. Las pruebas posteriores de raíz, si se realizan, deben añadirse explícitamente; este subtotal no pretende ser el contador final de toda la ventana. El cambio 32→64 fue documentado y congelado antes de datos/modelos 37, sin autorizar nuevas variantes. Salidas del productor ≈4.55 MB; el RSS observado del revisor fue 169492480 bytes, dentro del cap 2 GiB.

El protocolo pedía versiones/entorno, pero el productor no guardó ese campo. Con autorización explícita de raíz, el freeze del revisor aporta un **complemento de metadatos observado por el revisor**: ejecutable del mismo venv, Python, plataforma, NumPy, Pandas y PyArrow. No se presenta como snapshot contemporáneo de la ejecución del productor. Los originales permanecen intactos y la omisión queda declarada.

## Límites y evidencia

La garantía de exclusión de targets es **por régimen**. Una respuesta que es held para un régimen puede pertenecer legítimamente al SOURCE de otro; no se afirma que jamás se hayan leído labels held globalmente. Las mezclas reutilizan observaciones SOURCE también contenidas en el parent original: son un ajuste empírico regularizado, no un posterior Bayes ni incertidumbre calibrada.

La referencia es actividad SNP registrada en celdas-día mensuales. No mide incendios físicos, cobertura u oportunidad de observación. El placebo conserva su única permutación congelada y puede mantener alguna adyacencia;D también puede representar cantidad o distribución de registros. G1 físico sigue false, 30B fallido y 35 negativo permanecen intactos. Los resultados 33 no se convierten en verdad, pesos o labels del modelo 37.

Evidencia reproducible: [verificador congelado](evidence/daily-context-independent-review/reviewer-code.py.txt), [freeze y entorno observado](evidence/daily-context-independent-review/freeze.json), [resumen de verificación](evidence/daily-context-independent-review/summary.json) y [manifiesto independiente](evidence/daily-context-independent-review/manifest.json).

- Protocolo 37: SHA256`368134a10997832cc6f5a846aa5c27dc90771168b0f02528c1e71e2cd37a08cf`.
- Freeze independiente: SHA256`c76cf22910468efbc3955bf3c378f2a09d1969b3b8d4e939c72640b5ca65d011`.
- Manifiesto productor antes/después: SHA256`21b16ec5d559a3546004fa868125357e4a7a0e9d0b3fb84e8ea4256542900286`.
