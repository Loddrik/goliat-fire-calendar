# Informe37 — la adyacencia diaria no supera el doble contraste fijado

La media igual de los cuatro contrastes held **Qreal−Qplacebo=-0.004927**, pero el contraste obligatorio **Qreal−G21=0.010794** empeora. El criterio exige ambos negativos y no se cumple. No se afirma una mejora útil de cronología ni se rescata el resultado cambiando agregación, placebo,κ,rasgo o familia.

La ventaja media frente al placebo está concentrada en08_backward:Qreal mejora frente aQplacebo sólo en ese régimen y empeora en los otros tres. Frente aG21 también mejora sólo uno de cuatro. En las comunas held publicadas, Qreal empeora frente al placebo en los cuatro regímenes. Se conservan todos los costes y fuentes.

## Dominio y matemática congelados

- Únicamente panel21:54CUT, cuatro regímenes, máscara6 pre2012, mismosAqua/B/r_g/CDF21. Cubo36 real y placebo auditado, sin nueva permutación ni nueva información externa.35A se mantiene cerrado y negativo.
- El rasgo es existencia de pareja de deteccionesAqua en la misma celda y días consecutivos dentro del mesUTC. D0 no indica ausencia de fuego ni observación útil. Es armonización retrospectiva de meses completos, no forecast.
- Nuevas mezclasCDF completas en RAWZ: empiricalSOURCE-D+10priorparent21; paraSOURCE localD empiricalCUT-D+10parentcontextual. Ceros conservan átomo0. Sólo la consulta transforma positivos amax(1,(1+r_g*Aqua)Z). No se obtieneZ de predicciones flooreadas.
- PoolSOURCE(g,Aqua>0)sin variaciónD, incluido vacío, devuelveCDF21 completa de cadaCUT:incluye localesSOURCE y queryD no observado. No se resuaviza el priorJeffreys ni se sustituye por unparent distinto.
- Reconciliación global54 conΣB ysolver/tie-break originales. No presupuestos regionales35R. Riesgo yKKT se comprueban bajo laCDF propia de cada modelo; no se comparan riesgos de objetivos distintos como una sola métrica.

## Cronología, SOURCE por régimen y controles

Protocolo raíz `fe1eaa4`, SHA256 `368134a10997832cc6f5a846aa5c27dc90771168b0f02528c1e71e2cd37a08cf`. Cap absoluto08:07:07–09:07:07UTC, incluido protocolo, implementación, fits, tests y revisión; checkpoint08:32:07 sin reinicio. El límite64candidatefits se fijó antes de ejecutar para incluir reconstrucción independiente y fixtures; no añadió variantes.
Código/inputs congelados `2026-11-15T08:15:10.587592+00:00`, antes incluso de los fixtures candidatos. FreezeSHA `ee9c5db21c8337248858f6707ce6d75e04118d7134a99cc05b4f570ff1eb7da6`. Cuatro tests sintéticos y cinco candidatefits,0solvers, pasaron después de ese freeze.
Checkpoint `2026-11-15T08:16:15.611503+00:00`: B/G reproducidos exactamente21 en los cuatro regímenes, máximo error0.0;20736comparacionesCDF completas para todosCUT yD0/D1, además de54allocations constantes iguales exactamente aG. SelectoresSOURCE previos al load están registrados. Raíz verificó el checkpoint antes de candidatos reales.
Modelos y10368predicciones congelados `2026-11-15T08:18:45.259768+00:00`, antes del join de evaluación. PredictionfreezeSHA `5dad677218bfebc933e188fa42a9379cf9eeaacc04333815824f632298bf2f57` yprediccionesSHA `f04f6bbd129ddb361d1775417aec8564e6732ed36d16c3562fb46b21d63093a7`. Primer join de respuestas para evaluación `2026-11-15T08:20:03.767965+00:00`, posterior alack de raíz.

Cada régimen escaneaParquet con filtrosCUT∈SOURCE yseason∈origin y columnascut/season/m/snpp ANTES de materializar valores. No se filtra porregime antiguo, porque sus filas representan destinos: la extracción correcta encuentra dos copias por clave de las otras combinaciones, exige igualdad exacta yunique una sola. No promedia discrepancias. LosSOURCEsets de los cuatro modelos colectivamente pueden cubrir todo el historial: la garantía es PORRÉGIMEN; no se afirma que nunca se leyeron labels held de otro régimen.

El metamorfo por régimen usa labels reales exclusivamenteSOURCE y añade sólo respuestasSINTÉTICASNaN/999999 para features prohibidas. Modelo/políticas/suficientes no cambian. No se materializan respuestas reales prohibidas para realizar ese test antes del freeze.

Contabilidad original: 21candidatefits=5fixtures+4constantcontrol+8real/placebo+4poison;768solvers=384controlesG/constantG+384candidatos. La revisión independiente y repeticiones de fixtures se contabilizan separadas por raíz dentro del cap64/3000. RSS del proceso de evaluación160755712bytes (el máximo registrado entre fases es203411456bytes en prediction-freeze) ysalidas4551368bytes antes delmanifest. Todos los archivos/modelos/cubo originales conservaron hashes.

## Cuatro contrastes primarios

|Régimen|Nheld|MAEG21|MAEQreal|MAEQplacebo|Real−placebo|Real−G|
|---|---:|---:|---:|---:|---:|---:|
|08_backward|1008|2.116247|2.122844|2.159730|-0.036886|0.006597|
|08_forward|1008|2.864694|2.893132|2.891791|0.001341|0.028438|
|16_backward|1584|1.850047|1.860894|1.847749|0.013145|0.010847|
|16_forward|1584|2.113125|2.110419|2.107727|0.002693|-0.002706|

Promedios ponderados porfila, secundarios: real−placebo=-0.002072;real−G=0.009300. Tampoco cumplen ambos negativos. No sustituyen la primariaigual4. Los regímenes se solapan y no son replicaciones independientes; no se producen p-values/ICIID.

## Costes en held/publicadas y peorCUT histórico

|Régimen|Nheld/publicadas|B|G|Qreal|Qplacebo|
|---|---:|---:|---:|---:|---:|
|08_backward|384|2.831316|2.755179|2.803629|2.774097|
|08_forward|384|4.110527|3.854485|3.973578|3.943492|
|16_backward|288|3.085447|3.211311|3.236761|3.212069|
|16_forward|288|2.984981|3.174599|3.145634|3.136088|

|Régimen|PeorCUTheld segúnG21histórico|G|Qreal|Qplacebo|
|---|---|---:|---:|---:|
|08_backward|16301|4.564588|4.502513|4.638696|
|08_forward|16104|6.925755|7.132338|6.591879|
|16_backward|08207|5.388111|5.438402|5.375231|
|16_forward|08305|8.651653|7.990763|8.504989|

El peorCUT se fija porG21histórico después del freeze, sin afectar predicciones y con desempatelexicográfico. Es un diagnóstico adaptativo sobre datos explorados, no holdout fresco. per_CUT.csv conserva216filas. Reports completos incluyen54,SOURCE,held,14/40 e intersecciones; Y=0,Y>0,Aqua0/Y>0,ambos0,Y≥50, conN,MAE,sesgo,sumas yMAE mensual agregado de cada población.

## Soporte y fallback — sin escoger variante favorable

|Régimen|Variante|Pools SOURCE variables(g,state)|Consultas fallback original|Consultas parentcontextual|Consultas localcontextual|
|---|---|---:|---:|---:|---:|
|08_forward|real|9/20|1767|450|375|
|08_forward|placebo|7/20|1966|332|294|
|08_backward|real|9/20|1800|414|378|
|08_backward|placebo|9/20|1800|401|391|
|16_forward|real|5/20|2068|302|222|
|16_forward|placebo|5/20|2102|296|194|
|16_backward|real|6/20|2073|333|186|
|16_backward|placebo|5/20|2185|270|137|

Las variantes activan distintos números de pools bajo la misma regla congelada de soporte: real/placebo9/7 en08_forward y6/5 en16_backward, por ejemplo. Su capacidad efectiva y fallback no están emparejados; la comparación incluye esas diferencias de soporte, no sólo orden temporal. No se cambia la regla después de resultados para igualarlas.

candidate-models.json conserva n/m/átomosSOURCE porclase ylocalCUT-D;query-support.csv conserva D,g,soporte ymasas prestadas porconsulta. La mezcla empírica puede compartir observaciones con el prior viejo: no es una posteriorBayes independiente ni produce intervalos calibrados. La semilla/permutación única no define una distribución de aleatorización y no garantiza destruir adyacencia.

## Revisión y límites

Informe de autor pendiente de enlazar al dictamen independiente. El productor omitió un bloque explícito de versiones del entorno en su freeze; el revisor registrará el entorno observado por separado, sin alterar el snapshot original. Integridad de hashes/modelos y controles numéricos no acredita reconstrucción íntegra de adquisición:1071CSVraw previos siguen faltantes.

33 conserva su alcance de operador nominal en dos casos, sin convertirse aquí en etiquetas físicas, pesos o covariables históricas. G1físico continúa falso;PSF,tiempo de exposición,Suspect y observabilidad no se resuelven. Cero registros no demuestra ausencia de fuego. No cambia M1/14gates/publicación ni se repara30B.

## Decisión

El doble contraste predeclarado falla: conservar este resultado y cerrar esta formulación congelada sin otra semilla,κ,normalización,lag,rasgo oagregación para rescatarlo. El resultado se limita al indicador binario, la mezclaCDFκ10 y el panel21 aquí evaluados; no adjudica el valor de toda información temporal posible. La pequeña ventaja media frente al placebo no autoriza afirmar utilidad temporal cuando empeoraG y los costes territoriales son adversos. Una siguiente dirección requiere otra pregunta/protocolo y revisión reservados; nada se promueve automáticamente.

La [revisión independiente final](2026-11-15-daily-context-independent-review.md) reprodujo los ocho modelos y reportes y confirmó que falla el criterio conjunto. El [ledger completo de raíz](evidence/daily-context-resource-accounting/summary.json) registra34fits observados (21productor+8revisor+5fixtures de raíz),768solvers y343tests aprobados; los manifiestos originales permanecen intactos.
