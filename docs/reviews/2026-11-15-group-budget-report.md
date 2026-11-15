# Informe35A — separar presupuestos empeora la primaria held

La primaria predeclarada es negativa para la propuesta: la media igual de los cuatro contrastes MAE(R)−MAE(G) es **+0.041975**. Sólo uno de cuatro regímenes mejora. El agregado por fila es +0.037285; no reemplaza a la primaria. No se cambia partición, CDF, contrato, proporción de mezcla o período para rescatarla.

R separa presupuestos por las regiones08/16 de21. En estos regímenes esas regiones coinciden exactamente con SOURCE/held: el cambio bloquea transferencia de presupuesto entre roles de calibración. No identifica ecología ni causalidad geográfica. La conservación de totales de grupo es una construcción del estimador, no habilidad regional nueva.

## Congelamiento, gate y recursos

- Protocolo previo: SHA256 `a1107de9e9c1256f8e6a502d868e9d536fca5a624d50257d514750e7a73f778c`, commit raíz `5f8960a`. Cap absoluto07:19:05–08:04:05UTC, checkpoint07:34:05, sin reinicio.
- Código/tests/entradas congelados antes de predicciones y targets. Cinco tests sintéticos pasaron;19 llamadas a reconcile incluidas y contadas en el mismo módulo del driver mediante alias explícito.
- Checkpoint guardado `2026-11-15T07:26:39.626161+00:00`; verificado por raíz07:27:12UTC. B yG reproducen exactamente21 en los cuatro regímenes: máximo error absoluto0.0 para ambos,2592filas por régimen. No hubo refits ni descargas.
- Parquet leído por proyección explícita de features `[regime,cut,season,m,g,aqua]`, controlesB/G leídos por otra proyección sin respuesta. Las cinco decisiones y sus hashes quedaron persistidos antes de unir snpp para evaluar.
- SHA del Parquet de predicciones congeladas: `26b0ca7663284d2ca3cd15030d41cc182bdc409bdfc5ca3427ac87fb71a94509`; certificado `prediction-freeze.json` SHA `62b75586ff24354cefa9025c97ebb4b5a587d0296d1b0f43dc91ddad9da2b0c4`;979 llamadas originales en total (19fixtures+960reales),960checks de grupos. RSS máximo original159571968bytes; salidas originales904424bytes antes del manifest. Contabilidad de repeticiones de revisión/CI se registra aparte por raíz; no se oculta en las960 reales.
- Las llamadas reales son G192+R384+P384. KKT se verifica por grupo; riesgoCDF global≤riesgoR/P≤riesgoB. Las identidades de grupos únicos/singletons, renombrado, permutación, factibilidad deG y localidadheld se prueban con fixtures previos.
- La lectura de etiquetas para pérdidas se autorizó sólo después de verificar el checkpoint. La evaluación terminó sin cambiar el código, modelos, partición o predicciones congelados. Todos los archivos protegidos conservan sus hashes.

## Los cuatro contrastes primarios

|Régimen|N held|MAE G|MAE R|ΔR−G|
|---|---:|---:|---:|---:|
|08_backward|1008|2.116247|2.136683|0.020437|
|08_forward|1008|2.864694|2.970416|0.105722|
|16_backward|1584|1.850047|1.838480|-0.011566|
|16_forward|1584|2.113125|2.166432|0.053307|

Los regímenes reutilizan escenas, comunas y desarrollo históricos; no son replicaciones independientes y no se calculan IC/p-values IID por fila.

## Controles secundarios completos, sin elegir ganador

B es baseline congelado;G reconciliación global54;R regiones;P una única partición hash33/21;C=(B+G)/2 fijo. La tabla muestra el mismo held en cada régimen.

|Régimen|B|G|R|P|C|
|---|---:|---:|---:|---:|---:|
|08_backward|2.153395|2.116247|2.136683|2.144270|2.120636|
|08_forward|3.025433|2.864694|2.970416|2.872916|2.926208|
|16_backward|1.829456|1.850047|1.838480|1.839010|1.828492|
|16_forward|2.151628|2.113125|2.166432|2.111611|2.097850|

P yC no tienen intensidad de regularización emparejada conR. Una sola partición artificial no produce una distribución de aleatorización ni valida la geografía por diferencia de scores. C no es mediana de una CDF ni óptimoL1; se verificó su cota convexa punto a punto después del join. No se probaron otras proporciones.

## Costes de las comunas publicadas y el control histórico peor

|Régimen|N held/publicadas|G|R|P|C|
|---|---:|---:|---:|---:|---:|
|08_backward|384|2.755179|2.790885|2.794408|2.778564|
|08_forward|384|3.854485|3.917572|3.821979|3.947836|
|16_backward|288|3.211311|3.196454|3.214603|3.138546|
|16_forward|288|3.174599|3.125822|3.120406|2.988725|

|Régimen|CUTheld peor según G histórico|G|R|P|C|
|---|---|---:|---:|---:|---:|
|08_backward|16301|4.564588|4.776777|4.786929|4.710103|
|08_forward|16104|6.925755|6.926689|7.002162|6.908651|
|16_backward|08207|5.388111|5.237271|5.386177|4.887466|
|16_forward|08305|8.651653|8.770246|8.826624|9.812410|

El CUTheld se fija por MAEG original21, desempate lexicográfico, después del freeze de predicción; es un diagnóstico histórico seleccionado, no nuevoholdout ni selector del modelo. La tabla completa de216CUT/régimen permanece en per_CUT.csv.

No se reemplaza la primaria held por all54: por ejemplo en08_forward R mejora all54 pero empeora held. Se exportan SOURCE/held,14/40 e intersecciones; ceros registrados, positivos, Aqua0/SNPpositivo, ambos0 y extremosSNP≥50, conN,MAE,sesgo,sumas yMAE agregado mensual para cada población. Las poblaciones condicionadas a la respuesta son diagnósticos, no evidencia de observabilidad física.

## Contabilidad y límites de alcance

decision_diagnostics.csv registra paraG/R/P distanciaL1 aB, transferencias entre SOURCE/held y exceso de riesgoCDF. BajoR la transferenciaheld es0 porconstrucción y la compensación conSOURCE cierra. Estos controles describen la decisión condicionada aCDF congeladas, no observación nueva.

Omisión detectada después de ejecutar: ese archivo no emitió las filasB/C del diagnóstico de riesgoCDF; no afecta predicciones, primaria ni las tablas de pérdidas. ParaB el riesgo de baseline está en allocation_checks; paraC transferencia y distancia aB se deducen algebraicamente deG, pero su riesgoCDF no se infiere como la mitad. Se notificó a raíz y al revisor. No se modificó el código/output congelado para ocultar la omisión; el [complemento independiente](evidence/group-budget-independent-review/all-method-decision-diagnostics.csv) completa las cinco decisiones con 960 filas y freeze propio. Se distingue como pos-ejecución, sin solver/refit ni nuevo resultado primario.

La [revisión independiente](2026-11-15-group-budget-independent-review.md) confirmó los cálculos y completó el diagnóstico omitido. Su manifiesto y evidencia están separados; el manifiesto y las salidas originales permanecen intactos. El ledger registra 1017 llamadas: 979 originales, 19 fixtures del revisor y 19 de la regresión de raíz.

33 acreditó un operador puntual nominal bajo condiciones declaradas; sus dos casos/Jaccard/QA no entraron como variables, objetivos o pesos en35A. G1 físico sigue falso;30B no se repara; el producto publicado M1/14gates permanece igual. Una detecciónSNP registrada no equivale a incendio individual ni verdad física. Ninguna mejora secundaria justifica promoción.

## Decisión

Conservar la primaria negativa y cerrar este contraste sin otra partición/semilla/proporción/CDF. Las mejoras o costes secundarios permanecen visibles. Este estudio no decide automáticamente abrir persistenciaB: requiere otra pregunta, operador y protocolo SOURCE-only con tiempo explícito de revisión.
