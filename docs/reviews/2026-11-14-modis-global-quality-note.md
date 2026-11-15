# Nota documental — alcance de `Suspect` en la calidad global de MYD14

Consulta de fuentes primarias: 14 de noviembre de 2026. Alcance: interpretación documental del par `AUTOMATICQUALITYFLAG=Suspect` y `AUTOMATICQUALITYFLAGEXPLANATION=not being investigated`. No se abrieron gránulos, cambiaron políticas G1, recalcularon resultados ni contactaron cuentas o personas.

## Conclusión

**No se encontró evidencia primaria suficiente para resolver si ese par concreto es una constante de producción de MYD14 colección 6.1 o el resultado de una evaluación específica del gránulo.** Tampoco es correcto deducir únicamente del texto que hubo un fallo científico comprobado. La interpretación permanece pendiente; esta nota no libera el gránulo ni lo declara defectuoso.

Existe documentación NASA que describe exactamente ese par como constante por falta de un algoritmo automático de QA, pero corresponde a **MODIS L1B, MOD_PR02**, no a MYD14 L2. Transferir esa explicación al producto de incendios sería una inferencia sin demostrar. Es una hipótesis documental plausible, no una resolución para MYD14.

## Evidencia directa y alcance de cada fuente

**MYD14 L2, colección 6.1.** La especificación alojada en LAADS para Aqua, revisión 6.2.3 del 4 de septiembre de 2014, enumera `AutomaticQualityFlag`, su explicación, `ScienceQualityFlag` y `OperationalQualityFlag` dentro de `CoreMetadata.0`. También distingue estadísticas globales y los SDS `fire mask` y `algorithm QA`. No proporciona allí una tabla de umbrales ni una regla que permita interpretar el par consultado como constante o fallo específico. La revisión del algoritmo indicada en el documento y el identificador de colección no son el mismo concepto. [Especificación MYD14 C61, secciones 1 y 4](https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/61/MYD14_c61.fs).

**MODIS L1B, evidencia de un mecanismo diferente.** El diccionario MCST, revisión D de julio de 2012, documenta en §2.1.1.3, página impresa 10, que los campos `.2` se refieren a bandas térmicas emisivas de los productos L1B de 1 km y OBC. Para esos campos, tanto `Suspect` como `not being investigated` son constantes del código: no existe allí un algoritmo automático de QA para esas bandas. El documento especifica su aplicación al código MOD_PR02 para Terra y Aqua; no identifica a MOD_PR14/MYD14 como destinatario de esa regla. Por tanto, prueba que la combinación puede existir sin diagnóstico individual de fallo en un producto MODIS, pero no que esa sea su causa en nuestro MYD14. [MCST, MODIS Level 1B Products Data Dictionary, §2.1.1.3](https://mcst.gsfc.nasa.gov/sites/default/files/file_attachments/M1055_PDD_D_072712final.pdf#page=14).

**ScienceQualityFlag es otro campo.** LDOPE explica que el estado científico se inicializa con `Not Investigated` y puede actualizarse para un producto completo, una versión, dominios temporales o geográficos, o gránulos individuales. Ese valor inicial no debe confundirse con el campo automático `Suspect`, aunque los textos parezcan relacionados. [LDOPE, Science Quality Metadata](https://landweb.modaps.eosdis.nasa.gov/help/sciqaflag).

**Los problemas específicos tienen documentación adicional.** El registro oficial Aqua C61 incluye incidentes delimitados por fecha y hora. Por ejemplo, la entrada de falsas detecciones de agosto de 2024 describe radiancias anómalas que no fueron marcadas por el QA interno, con índices de incertidumbre nominales. Esto muestra que ni una etiqueta global aislada ni QA local nominal bastan para resolver toda la calidad científica. La aplicabilidad de un incidente debe comprobarse contra el producto y la adquisición concretos; esta nota no vincula ese ejemplo con los archivos del piloto. [LDOPE, problemas conocidos Aqua C61](https://landweb.modaps.eosdis.nasa.gov/knownissue?as=61&sat=Aqua&sensor=MODIS).

## Guías consultadas y límite de acceso

Se localizaron las guías oficiales del equipo MODIS para [C6/C6.1, versión 1.0](https://www.modis-fire.umd.edu/files/MODIS_C6_C6.1_Fire_User_Guide_1.0.pdf) y [C6, revisión C](https://www.modis-fire.umd.edu/files/MODIS_C6_Fire_User_Guide_C.pdf). Sus referencias indexadas separan máscara, bits QA y metadatos. La recuperación íntegra de esos PDF falló durante esta consulta; **no se afirma haber verificado que carezcan de una explicación adicional**. La especificación C61 y el diccionario L1B sí se pudieron consultar directamente. No se usaron foros ni ejemplos de terceros para resolver la semántica del campo.

## Implicación para el piloto

Registrar literalmente ambos campos y su producto, colección y versión de proceso, con estado **semántica global no resuelta**. La cuarentena conservadora actual es una decisión del piloto, no una prohibición NASA demostrada por estas fuentes. Tampoco se encontró una exigencia documental específica de MYD14 que obligue a esperar que el metadato llegue a `Passed` para cualquier uso científico.

El inventario de máscaras y QA nativos puede seguir documentándose separado de esa cuarentena, manteniendo `scientific_eligibility_certified=false` y G1 pendiente. Resolver el campo global requiere una regla específica de la implementación MYD14 correspondiente o una aclaración publicada de LAADS/equipo MODIS. Aun si se confirma que es plantilla, seguirán pendientes los controles independientes de geometría, tiempo, QA de entrada y soporte común. Esta nota no modifica ninguno de esos requisitos.
