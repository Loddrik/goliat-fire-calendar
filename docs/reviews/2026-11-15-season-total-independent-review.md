# Revisión independiente 42 — sumas de temporada y preguntas del issue 48

**Dictamen: PASS de los resultados del intento 02 y del alcance del reporte final.** La reconstrucción independiente terminó a las 10:34:57.989180 UTC del 15 de noviembre de 2026, dentro del cap 10:27–10:43, sin ampliar el plazo ni iniciar otro ajuste. El protocolo `41734018…` y el helper congelado se leyeron y aceptaron antes de la agregación. Se identificó entonces que faltaba medir el cap RSS; su reparación instrumental se documenta abajo y no se oculta como pase del primer intento.

Se reprodujeron las **1296 filas comuna/temporada/método**, incluidas las 432 de M1 y las 112 primarias de las 14 publicadas. También coinciden 162 resúmenes por comuna/método, nueve resúmenes población/método, los 432 controles mensuales y la invariancia exacta de M1 sobre siete κ. El reporte final revisado tiene SHA256 `347c1b1a5b3d1d6af86da713fa6b403b94c879b9a7a2171d64895d3a03006cd9`.

## Una referencia distinta de las predicciones del productor

El oráculo no leyó `outer_predictions.csv` como referencia ni llamó al helper productor. Para cada comuna/temporada/método obtuvo **Δtotal=bias×n** del `eval_loso.csv` original, usando κ0; calculó Y sumando los conteos SNPP de `celldays_comuna_month_masked.parquet`. Luego reconstruyóP=Y+Δtotal, errores, relativos y resúmenes. También contrastó los totales Aqua con los controles originales. Los grupos canónicos sin registros aportan cero sólo bajo el contrato de conteos/grilla completa ya existente; eso no se interpreta como ausencia física de actividad u oportunidad útil.

Los hashes de entradas y código se congelaron antes de estos cálculos y permanecieron iguales al cerrar. El manifiesto del intento 02 quedó intacto: SHA256 `3870823331e085a76bc5289dd8b33d9560ef981c48cdb485c52dc2e9ae41d455`. No se importó `experiment.py`, que tendría efectos al importar; no se ajustaron factores, climatologías, modelos o umbrales.

## Resultado y denominadores

En las 112 comuna-temporadas primarias todas las referencias son positivas:

| Métrica M1, 14 publicadas | Resultado independiente |
|---|---:|
|Mediana del error relativo absoluto|20,3355%|
|Media del error relativo absoluto, MARE|22,8060%|
|Media del error relativo firmado|−11,4588%|
|WAPE,Σerror absoluto/ΣY|20,4151%|
|Bias agregado,Σerror firmado/ΣY|−10,5974%|
|MAE de la suma de temporada|18,9569 celdas-día|
|Error firmado medio de la suma|−9,8405 celdas-día|
|Comuna-temporadas subestimadas|76/112|

Son pérdidas sobre **sumas julio–junio**, no suma de MAE mensuales ni error de un único total regional. Las métricas relativas tienen denominadores y ponderaciones distintos; el reporte los distingue correctamente. Los casos Y=0 del universo 54/remaining40 conservan relativos NULL y categorías P=0/P>0; permanecen en métricas que sí están definidas. No hay epsilon ni exclusión silenciosa para mejorar el resumen.

La tabla completa y las comunas mencionadas en el issue se conservaron. La subestimación 8/8 de Tirúa, San Carlos y Los Ángeles es descriptiva de estas temporadas; no identifica la causa de diferencias entre décadas. El extremo aproximado −34% atribuido a Los Ángeles no reproduce aquí: el reporte mantiene el rango de su fuente fija en lugar de cambiar la fórmula. El control M0/M2 y all54/remaining40 no reemplazan la población primaria 14 ni justifican una selección nueva.

## Reparación instrumental, sin aprobación retroactiva

El intento 01 conserva sus archivos y su RSS **desconocido permanentemente**: `/usr/bin/time -l` no lo informó en el sandbox. Antes de interpretar métricas, raíz congeló una enmienda y un launcher que autorizaban exactamente una repetición idéntica, con otro directorio de salida y el mismo helper/inputs/freeze/cap. No se autorizaron nuevas fórmulas, parámetros o adquisiciones.

El intento 02 terminó 10:34:28UTC. El envelope registra 114757632 bytes de RSS máximo del único child, bajo 1 GiB; los artefactos de ambos intentos suman 375736 bytes, bajo 5 MiB. El revisor comprobó por hashes propios que **los tres CSV numéricos son byte idénticos** entre 01 y 02 y que ambos code-freeze coinciden. El envelope apunta al manifiesto correcto. Esta evidencia acredita el intento 02; no reconstruye ni certifica el RSS del 01.

El revisor no volvió a ejecutar el agregador ni el launcher. Su cálculo independiente usó las referencias anteriores y no seleccionó un modelo. No hubo fits, solvers, descargas o modificaciones de producción. La observación de recursos y sus hashes quedan en [resource-checks.json](evidence/season-total-independent-review/resource-checks.json), separados del manifiesto científico del productor.

## Alcance de las respuestas

El reporte responde las tres preguntas sin sobreafirmar: valida la aritmética del diagnóstico anual declarado, explica que errores mensuales pueden cancelarse o acumularse y conserva la ausencia de evidencia para atribuir el salto entre décadas. Una banda mensual no proporciona automáticamente una banda de la suma; la dependencia temporal importaría.

La máscara publicada y las 14 comunas seleccionadas usan el mismo desarrollo 2012–2019. Es un diagnóstico aparente postselección; los números aproximados del issue eran conocidos antes del protocolo. No se presenta como ciego, holdout fresco, validación 2002–2011, equivalencia física de sensores o evidencia causal de un salto 2012. La unidad sigue siendo celdas-día SNP registradas, no incendios o superficie quemada.

No existe un umbral anual nuevo que habilite o deshabilite comunas retrospectivamente. Las propuestas de nombres inequívocos para metadatos y divulgación en el método son recomendaciones, no cambios de gates, factores, JSON públicos o landing ejecutados por este estudio.

Evidencia separada: [freeze del revisor](evidence/season-total-independent-review/freeze.json), [oráculo congelado](evidence/season-total-independent-review/reviewer-code.py.txt), [tabla reconstruida](evidence/season-total-independent-review/independent-season-totals.csv), [resumen](evidence/season-total-independent-review/summary.json) y [manifiesto](evidence/season-total-independent-review/manifest.json). El resumen tiene SHA256 `e2545a45c63b4512c0d129f8c9e084e656310f84ffd77361fab4cbfa28a28fb5`. Cualquier futura política anual exige una decisión y evaluación propias; este pase no amplía la publicación ni modifica los resultados previos.

## Divulgación integrada al método

Se revisó también el nuevo punto de `docs/method.md` §6 sobre totales de temporada. La mediana APE20,34% y la media relativa firmada−11,46% se identifican como diagnóstico interno de112 comuna-temporadas seleccionadas con el mismo desarrollo, sin validar2002–2011, una banda anual o la causa de la transición2012. La habilitación mensual no se declara certificación anual. PASS de ese texto añadido, con SHA256 del método `b944e2bec9f06a5d83edc8fa76e728f834c96caf001aa14fef5415555e0542de`; no se revisitan como nuevas todas sus afirmaciones históricas. La [constancia separada](evidence/season-total-independent-review/method-disclosure-check.json) registra esta revisión posterior al cálculo independiente, sin alterar el manifiesto del productor.
