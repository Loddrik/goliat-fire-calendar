# Revisión científica 21 — transporte sin calibración local S-NPP

La mediana parental mejora el MAE en **uno de los cuatro regímenes** de transporte espacial y temporal. La media predefinida con igual peso para los cuatro es favorable, pero depende de una mejora grande al aprender en Biobío 2012–2015 y evaluar Ñuble 2016–2019; los otros tres contrastes empeoran. No hay evidencia de transporte uniforme ni fundamento para promover un nuevo modelo.

Este experimento responde cuánto transporta una calibración compartida a comunas sin calibración local S-NPP al cambiar también el período. **No prueba el valor de contextos ecológicos de la hipótesis 4**, no mide oportunidad de observación y no constituye un holdout nuevo: se reutiliza retrospectivamente el desarrollo 2012–2019 en un dominio de ajuste distinto.

## Diseño fijado y soporte distinto

Se ejecutó el protocolo congelado en `3cf20cb`. Los cuatro regímenes cruzan región SOURCE (Biobío 33 o Ñuble 21 comunas) con origen 2012–2015/destino 2016–2019 y el reverso. Son temporadas julio–junio. Ninguna etiqueta S-NPP de comunas held, en ningún año, participa en ajuste ni selección. Tampoco se usan etiquetas del destino temporal de las comunas SOURCE.

La máscara candidata se construyó con las reglas A/B/C y radios heredados, usando **solo Terra/Aqua y fecha UTC anterior a 2012-01-01**. No se utilizó `season<2012`, que admitiría enero–junio 2012. La procedencia registra 5331 detecciones Terra entre 2000-11-01 y 2011-12-31, y 16718 Aqua entre 2002-07-04 y 2011-12-31. La máscara resultante contiene **6 celdas**, se guarda aparte y no reemplaza la máscara publicada de 223.

El mapa y la unidad de `celldays` son heredados. El mapa legado revela soporte espacial derivado del corpus completo, y la máscara puede utilizar historia MODIS previa en las comunas held. Por ello, “sin calibración local S-NPP” no significa ausencia absoluta de información de esos territorios ni zero-shot absoluto. El soporte cambió respecto de 18: **no se comparan directamente los MAE 21 con los de 18**.

En cada régimen, todas las razones, normalizaciones, regresiones y distribuciones se ajustaron exclusivamente en SOURCE×origen. B eligió entre las cuatro λ existentes (.01,.1,1,10) mediante leave-one-origin-season-out dentro de SOURCE, con la regla original de mejora mayor al 1% sobre M1 y desempate por λ mayor. κ=10 permaneció fijo. No hubo nuevas búsquedas, selección por destinos ni ajuste con 2020+.

## Resultado primario: mediana parental frente a M1 en held

ΔMAE se define como E00−M1 antes de reconciliar; negativo favorece la distribución parental. La tabla conserva los cuatro regímenes.

| Régimen SOURCE → held | Filas held | MAE M1 | MAE E00 | ΔMAE |
|---|---:|---:|---:|---:|
|Biobío 2012–2015 → Ñuble 2016–2019|1008|3.025433|2.392566|-0.632868|
|Biobío 2016–2019 → Ñuble 2012–2015|1008|2.153395|2.161018|0.007623|
|Ñuble 2012–2015 → Biobío 2016–2019|1584|2.151628|2.184947|0.033319|
|Ñuble 2016–2019 → Biobío 2012–2015|1584|1.829456|1.979108|0.149652|

La media con igual peso por régimen es **-0.110569**. La media ponderada por fila es **-0.065668** sobre 5184 filas held; difiere porque los destinos tienen 21 o 33 comunas. Los cuatro regímenes comparten datos y estructuras de ajuste, y no se presentan como cuatro réplicas independientes. No se calcularon intervalos IID por celda ni se eligió el régimen favorable como resultado representativo.

En held, **B=M1 y E11=E00 exactamente**, por construcción del fallback. Se comprobó la identidad de la distribución completa, no solo de la mediana: probabilidad, átomos y pesos positivos coinciden. No existe una hipótesis identificable de mejora E11 frente a su padre en CUT sin parámetros locales.

## Decisiones secundarias y acoplamiento

Los dos métodos coherentes usan el mismo presupuesto ΣB de las 54 comunas por temporada-mes. E00_coherent utiliza distribuciones parentales para todos los CUT; E11_coherent permite distribuciones locales en SOURCE. Las distribuciones held son iguales antes de asignar, pero compiten con diferentes distribuciones SOURCE por el presupuesto. Cualquier diferencia held entre ambas asignaciones representa ese acoplamiento, **no aprendizaje contextual local en held**.

MAE held:

| Régimen | M1=B | E00=E11 | Media E11 | Coherente E00 | Coherente E11 | Proporcional E11 |
|---|---:|---:|---:|---:|---:|---:|
|08_forward|3.025433|2.392566|2.785979|2.908116|2.864694|2.841611|
|08_backward|2.153395|2.161018|2.380674|2.174626|2.116247|2.115056|
|16_forward|2.151628|2.184947|2.620271|2.120270|2.113125|2.122315|
|16_backward|1.829456|1.979108|2.180761|1.861598|1.850047|1.880030|

E11_coherent mejora frente a M1 en los primeros tres regímenes de esta tabla y empeora en 16_backward. Ese patrón secundario no reemplaza la primaria preregistrada, que solo mejora en 08_forward. En los cuatro regímenes, E11_coherent tiene menor MAE held que E00_coherent; esto no demuestra transferir un contexto territorial nuevo, puesto que la única diferencia informativa está en las distribuciones SOURCE y su competencia por el mismo total.

MAE SOURCE, también en períodos destino:

| Régimen | M1 | B | E00 | E11 | Coherente E11 |
|---|---:|---:|---:|---:|---:|
|08_forward|2.261929|2.005605|1.869955|1.746737|1.967353|
|08_backward|1.824532|1.789075|1.937144|1.851542|1.653873|
|16_forward|2.889467|2.682696|2.428715|2.306693|2.680695|
|16_backward|2.160848|2.125409|2.124218|2.043371|2.079251|

Los totales, sesgo global y MAE regional de ambos coherentes y del control proporcional igualan B únicamente en las 54 comunas por construcción. No se impone esa igualdad en SOURCE, held, 14 publicadas o 40 restantes, ni en sus intersecciones. Todos estos grupos, sus MSE, sesgos y volúmenes se exportan sin seleccionar un nuevo ganador. Las 14 comunas publicadas son un subgrupo heredado de evaluaciones anteriores con S-NPP; su selección no constituye una cohorte independiente de esa historia de desarrollo.

## Costes que la media puede ocultar

En Ñuble→Biobío hacia adelante, los held entre las 14 publicadas son 6 comunas (288 filas): E00 pasa de MAE M1=2.984981 a 4.268163, con sesgo −3.583341 frente a −1.025461. En esa misma intersección, coherente E11 logra 3.174599 y sigue por encima de M1; la mejora held/global no representa una mejora uniforme de los territorios publicados. En el reverso Ñuble→Biobío, E00 pasa de 3.085447 a 4.054577 en held/publicadas y coherente E11 a 3.211311, también peor que M1.

| Régimen | Estrato held | Filas | MAE M1 | MAE E00 | MAE coherente E11 |
|---|---|---:|---:|---:|---:|
|08_forward|zero|440|0.357491|0.206536|0.526822|
|08_forward|both_observed_zero|396|0.000000|0.020202|0.258515|
|08_forward|50_plus|29|30.978582|20.469722|28.583030|
|08_backward|zero|492|0.216625|0.100812|0.257990|
|08_backward|both_observed_zero|465|0.000000|0.000000|0.101461|
|08_backward|50_plus|21|20.494811|24.587823|20.770540|
|16_forward|zero|834|0.384708|0.260596|0.790726|
|16_forward|both_observed_zero|759|0.000000|0.102767|0.537759|
|16_forward|50_plus|14|27.870581|57.224177|29.327027|
|16_backward|zero|761|0.216034|0.338371|0.524760|
|16_backward|both_observed_zero|705|0.000000|0.214184|0.375025|
|16_backward|50_plus|11|12.971770|30.162839|15.502960|

Los estratos se solapan. Los meses intensos held (≥50 registros S-NPP) empeoran con la mediana parental en tres de cuatro regímenes; en 16_forward pasan de 27.870581 a 57.224177. La distribución parental puede reducir estimaciones en ceros y aumentar subestimación de positivos intensos. Al reconciliar, la obligación presupuestaria vuelve a introducir estimaciones en ambos ceros: M1 da 0 en ese estrato y coherente E11 es positivo en los cuatro regímenes. No se interpretan esos ceros como ausencia física de actividad.

## Pruebas de aislamiento, invariancia y conservación

Pasaron siete pruebas sintéticas: cuatro regímenes con años disjuntos; reglas de máscara y radios; exclusión de S-NPP y enero 2012; recorte SOURCE y fallback de CDF completo; refits tras borrar/cambiar etiquetas prohibidas; serialización/permutación; y rechazo de grupos SOURCE incompletos, etiquetas en inferencia o dominios de 53 CUT.

La ejecución real repitió cada ajuste completo dos veces: sustituyó todas las etiquetas fuera de SOURCE×origen por NaN y por 1234567. Ambos casos preservaron exactamente los parámetros, selecciones y las ocho columnas predictivas de las 54 comunas, incluidas ambas reconciliaciones. La función de inferencia acepta solo CUT, temporada, mes, g y Aqua; se añadieron etiquetas para puntuar después.

El ajuste principal comprende 20 llamadas a regresión affine (5 por régimen: 4 internas y 1 completa) y 4 CDF completas; las dos pruebas de invariancia agregan 40 llamadas affine y 8 CDF. Las cuatro λ se estiman con el helper existente en cada llamada, sin ampliar su grilla.

Se verificaron 384 asignaciones (4 regímenes×48 meses×2 CDF). El error máximo de presupuesto es 1.14e−13 y el residual KKT máximo 2.22e−16; el riesgo absoluto esperado bajo cada CDF no supera el de la asignación B factible. Esto no garantiza menor error frente a etiquetas reales. Se exige el conjunto exacto de 54 CUT antes de reconciliar; recién después se filtran grupos evaluados.

## Decisión

Conservar el resultado negativo de tres regímenes primarios y la asimetría regional/temporal. El beneficio medio no demuestra que una distribución parental viaje de forma estable a territorios sin calibración. La evidencia apoya mantener observación y contexto como incertidumbres prioritarias antes de otro ajuste, sin afirmar que ya se identificó cuál explica el error.

Para probar contextos ecológicos harían falta covariables o grupos territoriales fijados antes de resultados, capaces de asignar un CUT held a contexto aprendido SOURCE; los fallbacks actuales no lo hacen. El trabajo G0/G1 continúa por separado: este estudio no incorpora nubes, exposición temporal, footprints ni oportunidad de observación. No se promueve un método ni se modifica publicación.

## Artefactos

`data/processed/cold_region_audit/` conserva modelos JSON por régimen y firmas semánticas, selecciones/predicciones internas SOURCE, predicciones de destino 54, contrastes primarios, comprobaciones de asignación, estadísticas/procedencia/coordenadas de la máscara candidata, resumen y manifiesto. Los hashes verifican que base, publicación y todos los resultados anteriores permanecieron idénticos. No se descargaron datos, editaron helpers anteriores ni realizaron operaciones Git por este agente.
