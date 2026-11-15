# Revisión 23 — el contexto probado no supera el control uniforme primario

La política contextual fijada **no mejora la primaria**. Con el descriptor 2010, la media con igual peso de los cuatro regímenes pasa de MAE C00=2.179410 a C11=2.182576: Δ=0.003166, equivalente a un aumento del error de 0.1453%. Solo mejora uno de cuatro regímenes. Se conserva el resultado negativo; no se promueve ni se cambia de configuración buscando la sensibilidad favorable.

La sensibilidad 2001 mejora 0.3913%, por debajo del margen de trabajo 1%. La sensibilidad type0 simétrica mejora 1.5374% dentro de su propia unidad, pero no reemplaza a la primaria fallida: no es válido escoger el contrato por ese resultado. Ninguna cifra valida mecanismo ecológico, fuego físico, forecast as-of2012 o un holdout nuevo.

## Protocolo, código e integridad antes de métricas

El protocolo se congeló en `4653bd3`. Se implementaron helper, runner y 13 pruebas sintéticas. Antes de cualquier métrica nueva de 23, se generó `code-freeze.json` en 2026-11-15T03:53:47.174921+00:00, SHA256 `f2c74a6ac4c79edc0c81d50367e88f4ffdbc14e2ed73bc9c2d340d09ca51a104`. Código y entradas se verificaron al iniciar y terminar; no se modificaron después de ese congelamiento.

La ejecución completó las 12 combinaciones predefinidas, sus controles e invariancias **antes de calcular las métricas de destino 23**. Los controles de source-only OOF para seleccionar B type0 pertenecen exclusivamente al origen, no a destinos. No se descargaron datos ni se leyó HDF en esta etapa; se utilizaron características 22 y suficientes congelados 21.

La ruta alltypes C00 reprodujo la CDF completa, mediana, media, B, M1 y asignaciones uniformes 21 en 54 CUT, con tolerancia 1e−10. En held, C00=E00 de 21; en SOURCE, C00=E11 κ10 de 21. No se sustituyó el control por un promedio uniforme de CDF por CUT que cambiara la representación. Se verificó además, por lectura de suficientes, la reconstrucción exacta de probabilidades y soportes positivos de los 80 padres almacenados en los cuatro modelos 21.

La máscara 6, calendario, mapa legado, orígenes y destinos 21 permanecieron fijos. Las dos variantes alltypes reutilizaron exactamente las bases 21. Type0 filtró AMBOS sensores Aqua/SNP antes de deduplicar satélite/celda/día desde detecciones canónicas, con la misma máscara. Sus razones, normalizaciones, Z, B y CDF se ajustaron solo en SOURCE×origen usando la política4λ OOF y κ10 existentes. No se obliga a que esa unidad distinta reproduzca el modelo alltypes; sí reprodujo su propio control uniforme.

## Estimador aplicado

El contexto utiliza 18 componentes IGBP+unknown de 2010/legacy/retained, o el año 2001 en la sensibilidad declarada. Solo se corrigió el pequeño error numérico de cierre conforme al protocolo; no se normalizaron únicamente tres clases ni se aprendió una escala con los destinos.

Hellinger h=0.25, α=0.5 y κ=10 fueron constantes. Para cada pool g/estado Aqua, los pesos preservan Σw_cn_c=nP. Se usaron conteos por observación, no media por CUT que alterase el control al variar frecuencias Aqua0/>0. Las fuentes con contexto desconocido conservan la mitad global; consultas desconocidas o pool sin masa contextual vuelven a pesos 1 en ese pool.

El padre positivo sin soporte local de grupo utiliza suficientes globales y pesos recalculados con nGLOBAL antes de seleccionar positivos; su p conserva el grupo. Un grupo sin observaciones usa el pool global para ambos componentes. Si GLOBAL no tiene positivos, la distribución es degenerada 0. Son reglas empíricas, no una posterior binomial independiente.

Los pares completos (p0,F0), (p1,F1) se calcularon antes de construir C00,C10,C01,C11. F1 local incluye la masa prior κpParent contextual y no se reconstruye al intercambiar p en el factorial. En held no hay componente local propio: se transporta el padre contextual. La variable respuesta sigue siendo detección registrada por el producto S-NPP, no observabilidad física ni ocurrencia verdadera.

## Primaria: conservar los cuatro regímenes

ΔMAE=C11−C00 antes de reconciliar; negativo favorece la política contextual.

| Régimen SOURCE/tiempo | Filas held | C00 | C11 | ΔMAE |
|---|---:|---:|---:|---:|
|08_forward|1008|2.392566|2.527614|0.135048|
|08_backward|1008|2.161018|2.175611|0.014594|
|16_forward|1584|2.184947|2.002759|-0.182188|
|16_backward|1584|1.979108|2.024319|0.045211|

La media igual 4 es +0.003166. La agregación ponderada por fila da −0.012757 y **cambia el signo**, porque las regiones destino tienen 21 y 33 comunas. No se sustituye el estimando primario por ese pooling favorable. Los cuatro regímenes dependen entre sí y reutilizan el desarrollo 2012–2019; no se calcularon intervalos IID por celda.

La ganancia relativa se calculó como `(media4L00−media4L11)/media4L00`, no promedio de porcentajes por régimen y no suma de ganancias de 17/18/21.

## Sensibilidades predeclaradas, no configuraciones candidatas a elegir

| Escenario | MAE medio C00 | MAE medio C11 | ΔMAE igual 4 | Ganancia relativa | Regímenes que mejoran |
|---|---:|---:|---:|---:|---:|
|PRIMARY_2010_alltypes|2.179410|2.182576|0.003166|-0.1453%|1/4|
|SECONDARY_2001_alltypes|2.179410|2.170883|-0.008527|0.3913%|1/4|
|SECONDARY_2010_type0|2.149026|2.115987|-0.033039|1.5374%|2/4|

El margen 1% es una regla de trabajo, no significación ni criterio NASA. El escenario type0 tiene un control y una respuesta distintos: su reducción interna no demuestra que filtrar tipo0 sea “más preciso” respecto de fuego real ni autoriza promoverlo. No se ejecutó 2001×type0 ni se puntuaron modelos DPA/QC0.

## Factorial: efectos en pérdida, sin atribución física

| Régimen | ΔP=L10−L00 | ΔF=L01−L00 | Interacción | Cambio conjunto |
|---|---:|---:|---:|---:|
|08_forward|-0.000475|0.126534|0.008989|0.135048|
|08_backward|0.002338|-0.009953|0.022208|0.014594|
|16_forward|-0.017916|-0.088140|-0.076132|-0.182188|
|16_backward|0.013128|0.033646|-0.001564|0.045211|

Promedios con igual peso 4: ΔP=-0.000731, ΔF=0.015522, interacción=-0.011625; suman el conjunto +0.003166. En la primaria, el pequeño avance medio de P no compensa el paquete F con su interacción. La diferencia se expresa en unidades de MAE sobre las mismas filas, no en porcentajes acumulables.

El factor F se refiere al componente positivo completado. En SOURCE incluye cambios de prior κpParent además de ponderaciones; no es un experimento causal de “cantidad verdadera”. La interacción tampoco demuestra sinergia ecológica o independencia de los componentes aprendidos.

Brier de la probabilidad de registro positivo S-NPP, held:

| Régimen | p0 uniforme | p1 contextual |
|---|---:|---:|
|08_forward|0.171073|0.169107|
|08_backward|0.166670|0.160294|
|16_forward|0.191289|0.191554|
|16_backward|0.196336|0.200903|

Mejora en dos de cuatro regímenes, mientras la mediana primaria solo mejora en uno; una mejor pérdida de probabilidad no acredita mejor pérdida de cantidad ni calibración física del fuego.

## Coherencia secundaria y coste territorial

MAE held:

| Régimen | M1=B held | C00 | C11 | Coherente C00 | Coherente C11 | Proporcional C11 |
|---|---:|---:|---:|---:|---:|---:|
|08_forward|3.025433|2.392566|2.527614|2.864694|2.909657|2.889426|
|08_backward|2.153395|2.161018|2.175611|2.116247|2.076944|2.132701|
|16_forward|2.151628|2.184947|2.002759|2.113125|2.074498|2.122988|
|16_backward|1.829456|1.979108|2.024319|1.850047|1.817793|1.946440|

La asignación contextual coherente mejora en tres de cuatro regímenes held frente al control coherente uniforme. No reemplaza a la primaria previa a coherencia ni demuestra una distribución regional nueva. Ambos conservan el presupuesto ΣB de 54 comunas; su sesgo global y error regional coinciden con B **por construcción**.

En cambio, **la asignación contextual coherente empeora en las comunas held/publicadas en los cuatro regímenes primarios**:

| Régimen | Filas held/publicadas | M1 | C00 | C11 | Coherente C00 | Coherente C11 |
|---|---:|---:|---:|---:|---:|---:|
|08_forward|384|4.110527|3.481444|3.532230|3.854485|3.871087|
|08_backward|384|2.831316|2.960741|2.946407|2.755179|2.773930|
|16_forward|288|2.984981|4.268163|4.081162|3.174599|3.239656|
|16_backward|288|3.085447|4.054577|4.355906|3.211311|3.251231|

El número de comunas publicadas held es 8 para SOURCE Biobío y 6 para SOURCE Ñuble. Es un subgrupo heredado de evaluaciones anteriores con S-NPP, no una cohorte nueva independiente. La mejora global posterior a asignación puede coexistir con transferencia de presupuesto perjudicial para ese subgrupo. Se exportan SOURCE, held, 54/14/40 y sus intersecciones, sin seleccionar un ganador agregado.

## Ceros y extremos que no deben ocultarse

| Régimen | Grupo | Estrato | Filas | C00 | C11 | Coherente C00 | Coherente C11 |
|---|---|---|---:|---:|---:|---:|---:|
|08_forward|held|both_observed_zero|396|0.020202|0.055556|0.258515|0.333011|
|08_forward|held|aqua_zero_snpp_positive|213|2.037559|1.971831|1.823704|1.724819|
|08_forward|held|50_plus|29|20.469722|24.476124|28.583030|28.824462|
|08_forward|held/publicadas|both_observed_zero|97|0.030928|0.072165|0.266431|0.409627|
|08_forward|held/publicadas|aqua_zero_snpp_positive|89|2.359551|2.292135|2.176335|1.976722|
|08_forward|held/publicadas|50_plus|19|19.782320|22.101980|24.779642|25.860743|
|08_backward|held|both_observed_zero|465|0.000000|0.111828|0.101461|0.192129|
|08_backward|held|aqua_zero_snpp_positive|210|2.471429|2.290476|2.278674|2.104304|
|08_backward|held|50_plus|21|24.587823|25.465247|20.770540|20.855425|
|08_backward|held/publicadas|both_observed_zero|127|0.000000|0.055118|0.072428|0.110973|
|08_backward|held/publicadas|aqua_zero_snpp_positive|92|3.086957|2.913043|2.922213|2.731421|
|08_backward|held/publicadas|50_plus|12|22.431299|22.576355|19.369526|20.223741|
|16_forward|held|both_observed_zero|759|0.102767|0.077734|0.537759|0.450170|
|16_forward|held|aqua_zero_snpp_positive|321|1.956386|1.953271|1.585933|1.590302|
|16_forward|held|50_plus|14|57.224177|43.000529|29.327027|29.551777|
|16_forward|held/publicadas|both_observed_zero|79|0.050633|0.025316|0.480981|0.443038|
|16_forward|held/publicadas|aqua_zero_snpp_positive|56|2.303571|2.339286|1.902848|1.982958|
|16_forward|held/publicadas|50_plus|5|60.717703|53.061066|26.857949|32.862343|
|16_backward|held|both_observed_zero|705|0.214184|0.215603|0.375025|0.291755|
|16_backward|held|aqua_zero_snpp_positive|376|2.074468|2.077128|1.864826|1.878424|
|16_backward|held|50_plus|11|30.162839|36.620779|15.502960|16.356624|
|16_backward|held/publicadas|both_observed_zero|71|0.154930|0.154930|0.308358|0.197183|
|16_backward|held/publicadas|aqua_zero_snpp_positive|70|1.942857|1.942857|1.752243|1.840030|
|16_backward|held/publicadas|50_plus|4|52.984148|68.838023|20.123218|20.649332|

Los estratos se solapan. En Ñuble held (Biobío SOURCE), la política aumenta estimaciones en ambos ceros y empeora extremos. En Biobío held hacia adelante, reduce el MAE de extremos de 57.224177 a 43.000529, pero el coherente contextual empeora ligeramente esos extremos y el coste es mayor en los cinco extremos de sus comunas publicadas (26.857949→32.862343). En Biobío held hacia atrás, C11 empeora extremos (30.162839→36.620779); en sus cuatro extremos publicados pasa 52.984148→68.838023. Esos tamaños pequeños limitan generalización; no se eliminan del informe ni se suman sus pérdidas como poblaciones disjuntas.

Los ceros registrados siguen con oportunidad de observación desconocida; no se convierten en ausencia física de actividad. Type0 desconocido tampoco se interpreta como vegetación o confirmación de incendio. La deduplicación canónica previa por detección/fuente no se revierte al filtrar tipo0 antes de celda-día.

## Concentración y controles de inferencia

En consultas held primarias con pool aplicable, ESS_CUT mínimo=3.422161, ESS_observaciones mínimo=5.887368 y peso máximo por registro=10.798212. La mínima distancia H a SOURCE por consulta/pool va aproximadamente de 0.073020 a0.623327. Son diagnósticos de ponderación y no se presentan como muestras independientes, intervalos bayesianos o soporte ecológico demostrado. La positividad del kernel impide interpretar masa K>0 como prueba de solapamiento.

Los 13 tests cubren simplex/cierre y roundoff; nP con tamaños de estado desiguales; α0, consulta desconocida y contextos conocidos idénticos; SOURCE desconocido con mitad global; fallback positivo con nGLOBAL antes de positivos; fallback por pool sin masa aunque el global pueda seguir contextual; swaps completos y mediana inferior; fuente sin positivos; rechazo de stats/categorías/etiquetas; reproducción del control e invariancia 54; tipo0 simétrico antes de deduplicar; loader 18/54; congelamiento de código y fórmula relativa correcta.

Las12 combinaciones reales pasaron las identidades uniformes y dos pruebas de eliminación/modificación de etiquetas prohibidas. Alltypes usó bases congeladas; type0 repitió los ajustes SOURCE-only con todas las etiquetas fuera de SOURCE×origen sustituidas por NaN y por 1234567. Parámetros, selecciones y las 54 predicciones permanecieron exactamente iguales, incluidas asignaciones contextuales. La API de inferencia rechaza columnas objetivo.

Se verificaron 1728 asignaciones principales (12 casos×48 meses×3 CDF:uniforme,contextual,padreoriginal). Error máximo de presupuesto=2.274e-13; KKT máximo=2.220e-16; el riesgo esperado bajo la CDF no supera al de la asignación B factible. Esto es una propiedad del problema optimizado, no garantía de error observado.

## Decisión y artefactos

**No promover la política contextual probada.** El resultado principal no supera al control ni al margen de trabajo; elegir 2001 o type0 por sus sensibilidades sería cambiar la pregunta después del resultado. La evidencia no refuta toda utilidad de contexto territorial: delimita esta representación, este kernel y esta política de sharing. Antes de otra grilla, el consejo debe revisar unidad/respuesta, otro descriptor con justificación independiente o evidencia de observación G0/G1, manteniendo el resultado negativo.

Los mapas nominales 2010/2001 fueron reprocesados 2022 con HMM y las geografías son retrospectivas. No se acredita as-of2012, contexto ecológico verdadero ni independencia de todo el desarrollo. Ninguna característica de este estudio mide nubes, exposición temporal o footprints; el trabajo observacional no queda sustituido.

`data/processed/context_cdf_audit/` conserva freeze de código/inputs, predicciones de los tres escenarios, modelos usados y firmas, composiciones, diagnósticos de pesos/fallback/ESS, predicciones internas SOURCE type0, contrastes primarios, comprobaciones de asignación, resumen y manifiesto. Los hashes verifican base, publicación, 21 y 22 intactos. No hubo nuevas descargas ni edits de helpers previos, commits o push por este agente.
