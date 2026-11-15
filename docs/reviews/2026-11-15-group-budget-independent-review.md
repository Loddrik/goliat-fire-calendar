# Revisión independiente 35A — presupuestos de grupos

**Pasa la verificación independiente con resultado primario desfavorable.** La media con igual peso de los cuatro contrastes held, MAE(R)−MAE(G), es **+0,0419746461**: separar los presupuestos por región empeora el error medio frente al control global. El agregado ponderado por filas, secundario, también empeora: +0,0372847545. No se sustituye la primaria por una sensibilidad favorable.

| Régimen | ΔMAE held R−G |
|---|---:|
|08_forward|+0,1057215506|
|08_backward|+0,0204367661|
|16_forward|+0,0533065848|
|16_backward|−0,0115663170|

Se reconstruyeron las CDF y B mediante la función pura de inferencia sobre los modelos congelados y features únicamente. Las llamadas históricas fit_source y predict_all se bloquearon expresamente en el verificador. B y G coinciden exactamente con 21 en los cuatro regímenes de 2592 filas. Se verificaron 960 grupos de asignación: presupuestos, riesgo esperado y KKT por grupo. El mayor residual KKT independiente fue 4,44×10⁻¹⁶ y el mayor residuo global de presupuesto 2,27×10⁻¹³. No se volvió a ejecutar el solver sobre datos reales.

La evaluación independiente comprobó el join de targets, las 216 poblaciones y sus 1080 reportes por método, todos los CUT y el peor CUT seleccionado por el control histórico G. Se mantuvieron los mismos estratos y targets. La mezcla fija C cumple la convexidad L1 punto a punto; no se presenta como mediana de una CDF ni como nuevo óptimo.

## Complemento obligatorio y transparente

El productor omitió B/C en su archivo de diagnósticos de riesgo/transferencia, aunque estaban requeridos por el protocolo. Sin editar ese código, sus predicciones o su manifiesto, el revisor congeló un verificador propio antes de calcular el complemento. El [sidecar de los cinco métodos](evidence/group-budget-independent-review/all-method-decision-diagnostics.csv) contiene 960 filas con riesgoCDF, exceso frente a G, distancia a B y transferencias SOURCE/held. Es un complemento posterior explícito de campos preregistrados omitidos, no otra primaria, nuevo método o búsqueda por resultados.

La implementación independiente usa sumas directas de pérdida absoluta ponderada y subgradientes desde los mismos átomos congelados. Se verifican G≤R/P≤B y G≤C≤[riesgo(B)+riesgo(G)]/2. Estos son controles matemáticos de decisión, no evidencia de precisión física. Los diagnósticos originales G/R/P también coinciden dentro de las tolerancias congeladas.

## Recursos y procedencia

El [resumen independiente](evidence/group-budget-independent-review/summary.json), [freeze previo](evidence/group-budget-independent-review/freeze.json) y [snapshot del código ejecutado](evidence/group-budget-independent-review/reviewer-code.py.txt) registran inputs/hashes y alcance. La verificación terminó a las 07:34:30 UTC, dentro del cap original 08:04:05 UTC. El checkpoint del productor se emitió a las 07:26:40 UTC, antes de las 07:34:05 fijadas; se verificó su hash y que precede al join de evaluación.

El [registro completo de llamadas](evidence/group-budget-independent-review/resource-accounting.json) contabiliza **1017**: productor 979 (19 sintéticas+960 reales), revisión 19 sintéticas y regresión raíz 19 de los nuevos fixtures35. El verificador no repitió las 960 reconciliaciones. Pasaron sus cinco tests; la regresión raíz pasó 330 tests. El campo subtotal998 del resumen ejecutado corresponde sólo al productor más esta revisión; el companion incorpora explícitamente las 19 llamadas de raíz. No se ocultan ni recalculan métricas para cambiar ese registro.

Los hashes del productor permanecen idénticos antes y después. La evidencia del revisor y su manifiesto están separados: el manifiesto original no se amplió. El verificador conserva una ruta ROOT local explícita; su snapshot registra lo ejecutado, sin prometer portabilidad o repetir un driver fuera de su cap.

En 21, las regiones reales coinciden con SOURCE/held. El contraste informa sensibilidad al acoplamiento de asignación, no identifica ecología ni causalidad territorial. La igualdad de totales regionales con B es construida. No hay nuevo holdout, ajuste de modelos, validación de observabilidad física o promoción de producto. G1 permanece falso y 30B continuo sigue fallido.
