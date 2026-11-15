# Addendum del cierre: contexto GOES y alcance de las revisiones

La [decisión científica principal](2026-11-15-final-scientific-decision.md) conserva su versión aprobada por revisión independiente: SHA256 `d996f6ad6d19db63abff8fb22e9eaf99f7dab168adaf5dfe6db0102d5c759934`. Esa revisión resolvió las precisiones sobre el mismo mes histórico, las máscaras por origen y los conteos LOSO separados. Este addendum incorpora el cierre posterior de C40; no atribuye esos contenidos a una aprobación anterior.

**GOES ofrece una posibilidad condicionada de contexto temporal grueso.** El [reporte40](2026-11-15-goes-preflight-report.md) y su [revisión dedicada](2026-11-15-goes-preflight-independent-review.md), terminados a las 09:40:54 y 09:41:54 UTC, consultaron documentación primaria y dos listados de catálogo. Sus diez objetos declaran M3 e inicios cada 15 minutos en enero de 2019, y M6 e inicios cada 10 minutos en febrero de 2023. Son metadatos, no observaciones útiles verificadas del área de interés. Se adquirieron cero objetos y cero bytes científicos.

La documentación conserva una discrepancia relevante: el ReadMe de diciembre de 2019 describe filtrado temporal en el mismo píxel hasta doce horas, mientras los ATBD describen un vecindario. No se verificaron las versiones desplegadas, los atributos reales, los estados de calidad ni la exposición por píxel en los casos. La repetición de etiquetas filtradas tampoco acredita observaciones independientes de continuidad de un incendio. La resolución nominal al nadir no es la resolución efectiva calculada para el área chilena.

Por tanto, C40 **no resuelve la adjudicación MODIS–VIIRS a 375 m o a escala de minutos**, no certifica G1 y no determina cuánto desacuerdo desaparecería con oportunidades comparables. La conclusión expresa falta de evidencia suficiente en este contrato; no afirma una imposibilidad física general ni que GOES sólo detecte incendios grandes. El presupuesto L2 continúa cerrado. Una adquisición futura requiere un protocolo y presupuesto propios.

El siguiente estudio útil necesita decidir primero cuál de estas dos preguntas pretende responder:

| Pregunta | Evidencia necesaria antes de adquirir | Límite de interpretación |
|---|---|---|
| ¿Hay contexto térmico regional repetido alrededor de las ventanas fijadas? | Versión histórica y semántica de Mask/DQF/fill/filtrado verificables; selección temporal y geográfica prefijada; acceso y coste estimados. | Podría describir contexto grueso; no identificar el mismo incendio ni refutar ausencias a 375 m. |
| ¿Ambos sensores polares tuvieron oportunidades físicas comparables? | Estados útiles y sin detección, geometría y tiempos de exposición compatibles, QA aplicable y referencia documental o independiente. | Un catálogo y los puntos FIRMS solos no proporcionan ese denominador. |

Para elegir o publicar otro modelo, además se necesita un destino reservado antes de formular la alternativa y una evaluación que conserve los costes territoriales y extremos. Los resultados ya vistos no pasan a ser un nuevo holdout al cambiar la fórmula. La menor pérdida media de una distribución histórica no prueba pronóstico futuro ni autoriza bandas alrededor de una asignación reconciliada.

C40 quedó publicado para revisión en [PR61](https://github.com/Loddrik/goliat-fire-calendar/pull/61), base `dev`, head `3faed09`; la existencia del PR no certifica merge o despliegue. El informe HTML y las verificaciones de portabilidad se revisan por su propio alcance durante la consolidación, sin alterar los manifiestos de los experimentos.
