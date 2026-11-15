# Informe39 — CRPS de la distribución marginal21 frente aδB

El productor obtiene una diferencia primaria igual4held **CRPS(F21)−CRPS(δB)=-0.618164**, menor en los cuatro regímenes. δB tiene toda su masa enB, por lo que suCRPS coincide punto a punto conMAE(B). La revisión independiente completa pasó dentro del cap; su alcance es la comparación retrospectiva condicionada aquí descrita.

El resultado está limitado a la calidad de forecast marginal bajo esta pérdida, referencia y desarrollo retrospectivo. CRPS combina localización y dispersión: no aísla el valor de incertidumbre, deAqua o de dispersión manteniendo igual localización. No demuestra calibración, verdad física, generalización fresca, distribución conjunta de54comunas ni unaCDFalrededor deG. Los costes en subgrupos impiden afirmar dominancia. No cambia ni rehabilita los resultados negativos23/35/37.

## Pregunta y comparación congeladas

- ÚnicamenteF21 originalE11κ10 yδB, sobre el panel21/máscara6 de cuatro regímenes y10368filas. G es una decisión, no una distribución reconciliada; no se fabricaδG ni unaCDFresidual para otro control.
- No hubo fits, solvers/reconcile, selección de parámetros ni adquisiciones científicas. Se restauraron ratios, políticas, priors y átomos de los modelos21 previamente congelados.
- Los átomos conservan la escalaSNP de cada consulta yfloor positivo original. Se mantienen los ceros, empates y soportes no enteros. Los pesos se validan finitos/no negativos yabs(fsum−1)≤1e−12; se normalizan una sola vez y se guardan originales y normalizados.
- PérdidaCRPS=Σw|x−Y|−0.5ΣΣww|x−x′|, menor es mejor. Es laCDFfinita emitida, sin correcciónfair-ensemble. El productor usa prefijos compensadosNeumaier/fsum y el revisor una integralCDF independiente porknots.
- Enheld,E11 yparentE00 son exactamente la mismaCDF; se verifica como identidad, sin presentarlos como brazos distintos.

## Cronología, entorno y freezes

Protocolo raíz `0558831`, SHA256 `ef2be85264a1e91b334e4aabcc6e28feceeaf2556f002946a43f52737cc2bd38`. Cap absoluto08:43–10:13UTC, checkpoint09:03, conrevisión dentro del mismo cap. D conserva el espacio de cierre protegido posterior; no se iniciaCdocumental enparalelo.
Freeze productor `2026-11-15T08:53:06.468292+00:00` antes de fixtures/inferencia/scores: `aabdd82794dfe60d3bf21666553c4126771633e94f3bd23bc2e3eadc55468e5f`. IncluyePython3.14.7, plataforma y versionesNumPy/Pandas/PyArrow/DuckDB/Shapely, además deSHAuv.lock contemporáneo. No se incorporó el entorno retroactivamente al freeze.
Cinco tests propios pasaron. Además,14fixtures racionales independientes del revisor coinciden con el productor antes de scores reales; fuenteSHA `e76ad48ce135b0666305b038b9407e3ef4fb45baa7e08d6d446e98daebd66ba5`. Comparación separada enindependent-fixture-comparison.json, sin editar el código congelado.
Checkpoint/fullCDFfreeze `2026-11-15T08:54:37.636703+00:00`, SHA `f16b3c38c6c6226cc726758b3b73d3aa358a1b7752bd99442323ce3985dc7e19`. Se reconstruyeron10368forecasts y444826elementos atómicos;B ymediana21 tienen máximoerror0.0;media normalizada difiere como máximo2.85e−14. Las5184consultasheld tienen átomos/pesosE11 exactamente iguales alparent. La mediana conserva la semántica original21 de masa0 ycuantil inferior positivo.
SnapshotCDF SHA `561ba3df6fa5ec53a0a4976d355a511601f63f6e91f2e56fa1c9e997ff191e7e` yrosterSHA `25529ba8360e8be25dc1c1414a70951ff5fb08459c5d1caf83796baf83146115` guardados ANTES deljoin de respuestas. Raíz verificócheckpoint08:55:53UTC. Primerjoin realY: `2026-11-15T08:56:25.882657+00:00`. La proyección previa sólo lee features/roles/B/E11/E11_mean, sin snpp.

Después del freeze, las respuestas se unen porregime/CUT/season/m, exigiendo que las dos copias históricas de cada clave entre regímenes coincidan exactamente. No se promedian discrepancias ni se expulsan distribuciones conpesos fallidos. δB se verifica contraabs(B−Y) fila a fila. El clamp sólo admite CRPSnegativo dentroτ=1e−10max(1,|Y|,E|X|), conserva raw/tolerancia yflag; en este run hubo0clamps.

## Cuatro contrastes primarios

|Régimen|Nheld|CRPS F21|CRPS δB (=MAEB)|DiferenciaF21−δB|
|---|---:|---:|---:|---:|
|08_backward|1008|1.674999|2.153395|-0.478396|
|08_forward|1008|1.846440|3.025433|-1.178994|
|16_backward|1584|1.475027|1.829456|-0.354429|
|16_forward|1584|1.690791|2.151628|-0.460838|

Media igual4=-0.618164. Agregado porfila, secundario=-0.571379; no sustituye el estimando primario. Los regímenes son dependientes y sus fechas ya fueron exploradas; no hay p-values,ICIID o nuevoholdout.

## Subgrupos que limitan el alcance

|Régimen|Nheld/publicadas|CRPS F21|CRPS δB|Diferencia|
|---|---:|---:|---:|---:|
|08_backward|384|2.286527|2.831316|-0.544789|
|08_forward|384|2.613279|4.110527|-1.497248|
|16_backward|288|3.010381|3.085447|-0.075066|
|16_forward|288|3.261212|2.984981|0.276232|

Las comunasheld/publicadas de16_forward empeoran, aunque el promedioheld completo mejora. Las otras tres interseccionesheld/publicadas tienen menorCRPS; se preservan todas.

|Régimen|Nambosregistros0|ΔCRPSambos0|NY≥50|ΔCRPSY≥50|
|---|---:|---:|---:|---:|
|08_backward|465|0.126628|21|-1.887820|
|08_forward|396|0.159747|29|-13.334948|
|16_backward|705|0.248139|11|10.076070|
|16_forward|759|0.232562|14|15.602548|

Ambosregistros0 empeora en los cuatro regímenes. Los extremosSNP≥50 empeoran en los dos regímenesSOURCE16 y mejoran en los otros dos; susN pequeños se muestran explícitos, sin tratarlos como replicaciones físicas independientes. Estos ceros y extremos son estados del producto registrado, no ausencia real/incendios confirmados.

## PeorCUT fijado porB histórico

|Régimen|CUTheld peor segúnMAEB|CRPS F21|CRPS δB|Diferencia|
|---|---|---:|---:|---:|
|08_backward|16301|3.409994|4.892273|-1.482279|
|08_forward|16104|4.212624|6.991496|-2.778872|
|16_backward|08305|3.799109|5.619985|-1.820877|
|16_forward|08305|5.346594|10.973167|-5.626573|

ElCUTse selecciona exclusivamente por elcontrolB originalheld, condesempateCUT, en fase de evaluación ysin afectar ningunaCDF. Es un diagnóstico adaptativo previamente fijado, no evidencia independiente de superioridad. per-CUT.csv conserva216filas ysummary.json todosSOURCE/held,54/14/40 e intersecciones; ceros/positivos/Aqua0SNPpositivo/ambos0/Y≥50. Cada reporte contieneN,sumas/mediaCRPS y diferencia sobre la misma población para ambosforecasts.

## Recursos, reproducción y cierre

Productor:0fits,0solvers,0descargas;RSS máximo174153728bytes ysalida física2255662bytes antes delmanifest. Exportar unaCDFporquery enJSONLcomprimido conserva sus arrays yroster, no cambia átomos. Sus444826elementos se contabilizan aparte; incluso contando cada elemento, las exportaciones quedan bajo1Mfilas. Todos los originales/modelos/versiones/cubo ypublicación conservaron hashes.

La [revisión independiente](2026-11-15-crps-independent-review.md) pasó a08:57:35UTC: reconstruyó10368CDF/444826átomos y5184identidadesheld,parent; verificó todaslasintegralesCDF con máximoerror2.13e−14 frentealrawscore delproductor,δB=MAEexacto,0clamps ylos216reportespor2forecasts,todaslasfilasCUT yla primaria. Código/freeze/evidencia están separados en`evidence/crps-independent-review/full-review/`; no se modificó el snapshot delproductor. El dictamen exige conservar los guardrails y limitar elclaim aestecomparador/panel, sincalibración o dominancia.

La conclusión eventual se limita a menorCRPS deF21 frente aδB en el desarrollo fijado, con los costes anteriores. No es reducción deMAE del calendario ni “menos incendios erróneos”; no se suman mejorasCRPS yMAE. La incertidumbre de observabilidad,PSF,exposición ySuspect permanece;G1físico falso y30Bsin reparar. Los1071CSVraw previos faltantes impiden afirmar reconstrucción completa de adquisición.

Ningún resultado promueve un modelo, cambiaM1/14gates/producto o rehabilita35/37. Finalizar revisión dentrodelcap y entregar evidencia auditada es el siguiente paso; no se abre otro forecast, semilla ofamilia por este score.

En el estrato held con Aqua=Y=0, B=0 por construcción del baseline: δB acierta exactamente esa respuesta ya conocida y su CRPS es0. Una distribución con masa positiva conserva un coste allí. Esa comparación condicionada al resultado no prueba por sí sola mala calibración; se publica junto a los extremos y al promedio completo, sin reinterpretarla como una alerta física.
