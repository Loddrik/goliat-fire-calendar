# GOLIAT: una historia del fuego que el municipio puede revisar

**Estado al cierre, 15-11-2026 12:15 Santiago (15:15 UTC):** #64, #65 y #66 están fusionados en `dev` y publicados en `main` con #67. #31 se cerró sin fusionar: lo reemplazó #66, que estabiliza el mismo orden de la recurrencia. Las menciones a PR abiertos y la guía de merge quedan como registro histórico; no quedan merges pendientes de esta entrega.

**Actualización de originales, 14:11 UTC:** la copia del otro desarrollador completó **1.071/1.071 CSV exactos**. El guard devuelve **COMPLETE, salida 0** en esta máquina. Los 956 recuperados y 115 faltantes citados en informes previos corresponden al corte anterior. No se repitieron ingestión, cartografía ni modelos; el fallo estricto histórico de una fila por lado sigue sin resolverse. [Recibo de la copia](evidence/peer-raw-recovery.json).

**Actualización de integración:** `dev` avanzó a `2fa31b4` durante la preparación. La [consulta de cierre](evidence/repository-at-close.json) registra ahora **23 de los 24 PR científicos seleccionados fusionados y uno abierto (#64)**. El inventario de las 13:41 UTC se conserva como antecedente fechado. Se incorporan localmente la marca nueva y el método en inglés del otro desarrollador; esto no acredita despliegue ni promoción de los modelos de investigación.

**Resumen para presentar · 15 de noviembre de 2026.** GOLIAT organiza actividad térmica registrada por satélites en un calendario territorial para las 54 comunas de Biobío y Ñuble. Su propuesta es ayudar a preparar la temporada con información histórica comprensible y trazable. El producto conservado utiliza M1; los candidatos de investigación permanecen separados. Este documento no acredita un nuevo despliegue.

## El problema y la decisión del usuario

Un equipo municipal necesita reconocer cuándo suele concentrarse la actividad, comparar temporadas con el mismo corte y revisar lugares con recurrencia. Una serie larga ayuda, pero combina instrumentos distintos: VIIRS registra actividad pequeña que MODIS puede omitir. Un salto en las detecciones puede mezclar cambios del fuego y cambios de observación.

GOLIAT permite seleccionar una comuna, consultar mapa y calendario, distinguir observaciones de estimaciones y exportar una tabla para revisión. Puede apoyar una conversación sobre cuándo reforzar preparación y qué sectores estudiar. No calcula dotaciones óptimas, rutas de evacuación o alertas, y no demuestra que usarlo reduzca pérdidas. El municipio sigue necesitando información local y procedimientos oficiales.

## Cómo funciona, sin prometer más de lo medido

La unidad es una **celda-día**: una celda de aproximadamente un kilómetro con al menos una detección diurna en un día. Varias detecciones pueden pertenecer al mismo episodio; la cifra no cuenta incendios individuales ni hectáreas quemadas.

M1 aplica un factor regional de **2,35**[^factor] a los conteos mensuales de MODIS Aqua para aproximar la referencia VIIRS S-NPP. El factor procede del solapamiento de las temporadas 2012–2019. No es una regla universal del sensor. Una temporada comprende julio–junio y se nombra por su año de inicio.

La estimación histórica de julio de 2002 a junio de 2012 se habilita en **14 de 54 comunas**. Deben tener al menos 50 celdas-día Aqua en el desarrollo, superar la climatología en seis de ocho temporadas evaluadas y superar Aqua sin corregir en seis de ocho; son dos conteos separados. Son reglas propias del proyecto. En las otras 40 comunas se conserva la historia observada desde 2012, sin habilitar esa reconstrucción.

El producto distingue el tramo estimado, las observaciones S-NPP y las observaciones NOAA-20 recientes. El explorador FireChronos conserva además el historial por plataforma, con otros filtros y límites territoriales: sirve para inspeccionar fuentes, pero sus números no deben empalmarse automáticamente con la serie armonizada.

## Qué entregamos y qué significa su evidencia

**Valor observable hoy:** una aplicación con selección comunal, mapa, calendario, tabla exportable, procedencia y método consultable. El ranking de temporadas de la landing se limita a temporadas observadas. La utilidad para usuarios, el ahorro de trabajo y el impacto en prevención siguen pendientes de evaluación con un municipio; no hay clientes, contratos, ROI o reducción de incendios acreditados en esta entrega.

| Evidencia | Lectura que podemos defender |
| --- | --- |
| Investigación puntual: en un mismo panel retrospectivo de **5.184 comuna-meses**, la referencia M1 reajustada por origen tuvo un error absoluto medio mensual (**MAE**, en celdas-día) de **2,047245** y E_coherent **1,797939**: reducción compuesta **12,18 %**. | Es una mejora media de investigación bajo ese contrato, con costes territoriales. No sustituye M1 publicado ni equivale a incendios evitados. No se suman porcentajes de etapas. |
| Totales julio–junio M1: **112 casos**, correspondientes a las 14 seleccionadas × 8 temporadas. Mediana del error porcentual absoluto **20,34 %**; media del error relativo firmado **−11,46 %**; **76/112** totales subestimados. | Diagnóstico aparente después de seleccionar comunas con ese desarrollo. La mediana no es la media: MARE **22,81 %**, WAPE **20,42 %** y sesgo agregado **−10,60 %** responden otras preguntas. No valida 2002–2011. |
| Recuperación actual: **1.071/1.071 CSV** idénticos al inventario; los 115 faltantes se completaron con la copia del otro desarrollador. En la auditoría previa con **205 fuentes históricas**, se reprodujeron las **223 celdas** de máscara y los conteos Aqua **9.123** / S-NPP **21.466**, usando el mapa comunal congelado. | El cociente reproduce el factor M1 exacto. La comparación estricta de detecciones todavía difiere en **una fila por cada lado**; la adquisición y cartografía completas no están reproducidas. |

Los consejos multifocales acordaron criterios antes de priorizar; consejos adversarios buscaron errores de interpretación, dependencia y selección. Protocolos previos, resultados negativos conservados y revisiones independientes limitaron qué podía afirmarse. Varios candidatos no superaron sus controles y no se promovieron. Los **358 tests confirmados en el CI del corte**, para el commit `6410fcb`, están identificados en el [recibo técnico](evidence/verification-snapshot.json). Acreditan controles de software, no verdad física del fuego ni el despliegue de otra versión.

## Ruta de demo sugerida y guion de tres minutos

Usar el enlace del sitio indicado en el [README](../../../README.md), comprobando previamente la versión accesible. Para la versión local preparada, iniciar la aplicación según la guía técnica del handoff. Las rutas siguientes están implementadas en el repositorio. El [acta local](acta-ensayo.md) registra un recorrido automatizado de estas rutas y la descarga CSV del candidato. El guion completo de tres minutos todavía debe ensayarlo el presentador; la disponibilidad y versión del sitio público no se verificaron en esa comprobación. El mapa depende de recursos externos: una ejecución local no garantiza operación offline. Si falla, usar calendario/tabla o capturas atribuidas a una versión.

1. **0:00–0:40 · La pregunta municipal.** Abrir `/explorar?cut=08111&lang=es` — Tomé, habilitada. «Queremos saber en qué meses se concentra la actividad registrada. Esta cifra cuenta celdas con detecciones; para tomar decisiones operativas la contrastamos con información local». Mostrar calendario y temporadas comparadas hasta el mismo corte.
2. **0:40–1:25 · La corrección visible.** Abrir `/explorar?cut=08111&lang=es&vista=tabla`. «Los satélites no ven igual. En esta comuna habilitamos una estimación histórica con una corrección sencilla y publicamos cómo se evaluó». Identificar tramo estimado y observado; descargar CSV. No presentar el error mensual como garantía del total anual.
3. **1:25–2:10 · El límite es parte del producto.** Abrir `/explorar?cut=08101&lang=es` — Concepción, no habilitada. «Aquí conservamos las observaciones; no extendemos una estimación que no pasó nuestras reglas». Cambiar a `/explorar?cut=08111&lang=es&view=observed` para inspeccionar plataformas, manteniendo explícita la diferencia de contratos.
4. **2:10–3:00 · La entrega y la siguiente prueba.** «Entregamos un calendario revisable, con exportaciones y decisiones documentadas. La investigación encontró mejoras medias y también fallos; por eso no reemplazamos automáticamente el modelo. El próximo paso útil es probar una decisión concreta con un municipio y conseguir evidencia independiente sobre cuándo ambos satélites pudieron observar». Cerrar con la preparación territorial, sin prometer pronóstico o impacto demostrado.

## Preguntas difíciles: respuestas que deben ser consistentes

**¿El salto en 2012 demuestra que aumentaron los incendios?** No. Cambia el instrumento y pueden cambiar otros factores. La corrección reduce parte de la discrepancia en un desarrollo conocido; no identifica qué fracción del salto entre décadas es instrumental o real.

**¿Por qué sólo 14 comunas?** Porque aplicamos compuertas de publicación. Las otras 40 conservan observaciones. Pasar una compuerta mensual no certifica exactitud anual, equivalencia física ni validez de la década anterior.

**¿Un cero significa que no hubo fuego?** Significa que no se registró actividad bajo el contrato usado. Nubes, humo o falta de una observación útil pueden producir omisiones. Los puntos FIRMS por sí solos no resuelven esa diferencia.

**¿La banda da confianza sobre 2002 o sobre la suma anual?** No. El error típico mensual no es un intervalo de confianza ni una banda anual validada. El estudio del issue 48 no valida 2002–2011. Los metadatos estacionales propuestos para API/JSON **aún no están implementados**.

**¿F21 ya pronostica futuros incendios?** No. Es una distribución experimental de S-NPP del **mismo mes histórico**, condicionada al Aqua mensual ya conocido. Su comparación favorable de CRPS mezcla localización y dispersión; no demuestra calibración, oportunidad física ni bandas consistentes alrededor del punto reconciliado E_coherent.

**¿Todo está integrado y desplegado?** Hay que distinguir cada estado. En el corte histórico, el [inventario de entrega](evidence/pr-inventory.json), consultado a las **13:41 UTC**, registraba **24 ramas científicas: 3 fusionadas y 21 abiertas**. En ese corte, la integración PR22 estaba fusionada y el fix PR31 seguía abierto contra `main`; entre las 26 entradas revisadas, sólo PR22–25 estaban fusionados. La consulta de cierre actualiza la selección científica a 23 fusionados y uno abierto (#64). Ningún estado de PR acredita despliegue; revisado, fusionado y desplegado son estados distintos.

## Sostenibilidad: hipótesis que debe probar un piloto

La base abierta puede sostenerse mediante colaboración con municipios o universidades y, si existe demanda, servicios de instalación, capacitación y mantenimiento de datos. Son hipótesis, no ventas demostradas. Un piloto acotado debería pedir a un equipo que compare dos temporadas hasta el mismo corte, identifique observaciones y estimaciones e interprete las ausencias antes de exportar una tabla. Se observaría su comprensión y finalización de esa tarea, sin presumir ahorro o impacto. Recién después corresponde estimar costes de operación, soporte y disposición a financiarlo. El compromiso actual es preservar una herramienta comprensible y una cadena de evidencia revisable.

**Fuentes de apoyo:** [método publicado](../../method.md), [decisión científica](../../reviews/2026-11-15-final-scientific-decision.md), [totales estacionales e issue 48](../../reviews/2026-11-15-season-total-report.md), [recuperación y límites](../../reviews/2026-11-15-raw-recovery-report.md), [auditoría histórica](../../reviews/2026-11-15-raw-historical-core-audit.md) y [explicación HTML con diagramas](../../artifacts/science-observation-plan-2026-11-15.html). El mapa de fuentes de esta entrega conserva sus hashes y distingue evidencia del repositorio de información comunicada durante la coordinación.

[^factor]: Valor conservado en el método y parámetros: **2,352954072125397**. La cifra redondeada facilita la presentación; no se recalculó ni cambió el modelo.
