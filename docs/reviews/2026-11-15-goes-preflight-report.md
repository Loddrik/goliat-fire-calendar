# Estudio40: factibilidad documental de contexto temporal GOES16

**Conclusión revisada independientemente: factibilidad documental condicionada de contexto temporal grueso; sin soporte establecido para adjudicar discrepancias375m o de minutos entre los sensores polares.** El catálogo existe para las dos fechas, pero no se verificaron ninguna señal, variable, geolocalización o versión de software de los productos. La máquina de estados histórica ejecutable permanece **inconclusa**. No se recomienda ni autoriza adquirir ciencia automáticamente.

Protocolo `64b79f6`, SHA `8f5df8704d9adc17e35b8e8c5e86309d8cf1cfedc626362e7e014ea6cd187fe2`; cap09:15–10:00UTC del15 de noviembre2026, incluida revisión independiente. La ampliación de recursos se ratificó tras terminarA39 temprano y liberarse capacidad, no por el signo de su resultado. D conserva su horario protegido10:13–11:13 y contingencia11:13–11:30. No cambia ningún resultado previo.

## Pregunta, alcance y adquisición0

Se consultó exclusivamente documentación primaria NOAA/GOES-R y dos listadosS3 públicos de **ABI-L2-FDCF**, FullDisk, para2019-01-03 y2023-02-10. AOI fijada:50×50km EPSG32718, centro(longitud−72.5,latitud−37). Las ventanas polares aproximadas de archivos —2019,18:36–18:45UTC;2023,18:30–18:36UTC— no son tiempos de exposición de píxeles.

Se seleccionaron nueve documentos, incluyendo una URLlegacy que no devolvió elPUG, y dos URLs lógicas de catálogo compartidas con el revisor. Las variantes deURL/redirects y fallos se registran; no se amplió la búsqueda a señales favorables. **Cero bytes científicos adquiridos:** ningúnGET/HEAD/Range deNetCDF/HDF, máscara, radiancia, producto oimagen científica; sin tiles, credenciales, cuentas, acuerdos o contacto con personas. Figuras técnicas no se analizaron como mediciones. El presupuestoL2 anterior sigue cerrado; no existe presupuesto nuevo de adquisición.

LosPDF técnicos se conservaron en caché local ignorada con tamaño/hash registrados, sin duplicarlos en el repositorio. Los bytes de documentos recibidos por la herramientaweb no son reportados por esa herramienta: permanecen desconocidos como transferencia documental, **no** se contabilizan como datos científicos0. LogsHTTP, referencias,XML y metadatos permiten revisar qué se consultó.

## Cadencia histórica y presencia de catálogo

El avisoNOAA de marzo2019 anunció la transiciónM3→M6 para2abril2019; elReadMeGOES16 actualizado en diciembre2019 describe esa transición como realizada. No se transfirió un modo actual automáticamente a2019. Los propios nombres listados corroboranM3 enenero2019 yM6 enfebrero2023. Véanse [avisoNOAA](https://www.ospo.noaa.gov/data/messages/2019/03/MSG_20190327_1424.html) y [información de modosABI](https://www.nesdis.noaa.gov/our-satellites/currently-flying/goes-east-west/abi-scan-mode-information-and-channel-summary).

|Caso y listado horario18UTC|Objetos listados|Modo en nombre|Separación de inicios|Ejemplo de intervalo declarado en nombre|
|---|---:|---|---|---|
|2019-01-03, prefijo2019/003/18|4|M3|15min|18:30:36.2–18:41:12.9UTC|
|2023-02-10, prefijo2023/041/18|6|M6|10min|18:30:20.5–18:39:51.3UTC|

AmbosS3LIST respondieronHTTP200 sin credenciales y `IsTruncated=false`. Se preservaron **todos** sus diez nombres, Size yLastModified; no se siguió ningún enlace de objeto. URLs exactas: [listado2019](https://noaa-goes16.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-FDCF/2019/003/18/&max-keys=1000) y [listado2023](https://noaa-goes16.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-FDCF/2023/041/18/&max-keys=1000).

Loscamposs/e/c se interpretan exclusivamente como fechas declaradas por la convención de nombres delPUG; tampocoLastModified acredita versión algorítmica o reprocessing. El tiempo`t` esperado por elPUG es el punto medio del scan y `time_bounds` sus extremos, con épocaJ2000; **ni éstos ni el nombre identifican exposición delAOI/píxel**. No se leyó ninguno de esos atributos reales. La cadencia del catálogo no garantiza una observación independiente dentro de la ventana polar de6/9min, ni cobertura útil entrepasadas.

## Geometría y resolución: contrato esperado, no validación delAOI

El [PUGv2.4,11julio2022](https://www.ospo.noaa.gov/resources/documents/PUG/GS%20Series%20416-R-PUG-L2%20Plus-0349%20Vol%205%20v2.4.pdf),§5.19, documenta grilla geostacionaria fija, coordenadasangularesx/y en radianes, parámetros deproyección y resolución nominal2km **alnadir**. No se calculó la proyección, ángulo local, footprint,PSF, resolución efectiva o píxeles válidos delAOI. No confundir2km nominal con resolución validada en37°S. FullDisk es la colección pertinente para el contexto sudamericano; la cadenciaCONUS oMESO no se atribuye alAOI.

La capacidad de detectar anomalías subpíxel suficientemente intensas está contemplada por el [ATBDv2.6](https://www.star.nesdis.noaa.gov/goesr/documents/ATBDs/Baseline/ATBD_GOES-R_FIRE_v2.6_Oct2013.pdf). Por eso no se concluye queGOES sólo pueda detectar fuegos grandes o que sea físicamente imposible detectar un foco pequeño. El límite de esta etapa es que **no acredita una adjudicación375m**, y una no detección gruesa no refuta un foco fino. Una detección tampoco esgroundtruth o un incendio único.

## Mask/DQF y versión histórica pendiente

Se separan documentos y productos: ATBDv2.6(2013),ATBDv2.7(2020),PUGv2.4(2022),PUGv3.0(2025) yReadMev2 actualizado20diciembre2019 no prueban por su fecha cuál software/configuración produjo los objetos2019/2023. ElPUGlegacy redirigió a unlanding general y **no** se usó comoPUG. La descarga documental directa recuperó versiones reales, con hashes; la versión actual no se retroaplicó a los casos.

ElPUGv2.4 describe candidatos de esquema, no un decoder autorizado para esos archivos:

- Mask0: no procesado;100: clase algorítmica procesada sin fuego;−99: fill documentado(short), distinto de0. No equivale a ausencia física.
- Mask10–15: categorías de fuego/probabilidad;30–35: equivalentes filtrados temporalmente. No son confianza equivalente aMODIS/VIIRS ni eventos independientes.
- Otros códigos distinguen offEarth, bloqueos geométricos/glint, entradas ausentes/inválidas, superficie, problemas algorítmicos y nubes. Valores no definidos/reservados permanecen desconocidos.
- DQF0 identifica la categoría de calidad de fuego;1 la de terreno procesado sin fuego;2–5 distintas invalideces;255 esfill documentado(unsignedbyte). **`DQF==0` no es un filtro universal de “buenas observaciones sin fuego”.**

El detalle de códigos y fill está en `documented-schema-not-case-decoder.json`, vinculado a tablas5.19.6.1-1/2 y§5.19.6 delPUG. **Losflag_values,FillValue,versión y estados de los granules reales siguen sin verificar.** No se aplicó el esquema a píxeles ni se asumieron ceros.

Hay una discrepancia documental sustantiva: el [ReadMeGOES16 actualizado20diciembre2019](https://www.ospo.noaa.gov/operations/goes/product-quality-overview/ps-pvr/goes-16/ABI/Fires%20and%20Hot%20Spots%20Characterization/Provisional/GOES-16_ABI_L2_FHS_Provisional_ReadMe_v2.pdf) describe filtrado con fuego previo en **el mismo píxel**, hasta12h, y declara que difiere del vecindario±1píxel delATBD. El [ATBDv2.7,octubre2020](https://www.ospo.noaa.gov/resources/documents/ATBD/ATBD_GOES-R_FIRE_v2.7_Oct2020.pdf) mantiene el criterio vecino. No se resuelve escogiendo el documento conveniente: la regla desplegada en cada fecha quedaunknown. Repetir clases filtradas no constituye confirmación independiente de continuidad del mismo incendio.

EseReadMe también documenta bloques faltantes, frecuentes enSudamérica, y correcciones **previstas** para2020. No se comprobó que el defecto afectara elAOI ni que estuviera corregido en2023. Tener un objeto archivado no acredita cielo despejado, procesamiento completo u oportunidad de observar. Instrumento diferente no significa errores independientes: geometría, nubes, respuesta térmica y procesamiento siguen importando.

## Acceso probado y no probado

Lo verificado es permiso efectivo de **listado de metadatos** sin autenticación y acceso a documentos técnicos. No se probóGetObject de ciencia, integridad del contenido, disponibilidad de variables o condiciones concretas de acceso de esos objetos. ElPUG incluye un campo genérico de licencia restrictivo; no demuestra ni autorización ni restricción real de estos objetosS3. No exige iniciar cuentas o acuerdos para este preflight. La consultaNCEIC01520 no terminó a tiempo y no fundamenta un claim de disponibilidad/inexistencia global.

Las diferenciasweb403/directHTTP200, redirectlegacy, timeout yDNS inicial del entorno se conservan en los logs. No son evidencia de ausencia científica. LosSize listados son **metadatos de objetos no descargados**, no bytes científicos adquiridos o un presupuesto futuro habilitado.

## Decisión y falsadores

**Contexto grueso potencial:** una futura pregunta podría estudiar etiquetas térmicas suficientemente detectables alrededor de los tiempos fijados, repetidas en los ciclos documentados, conservando nubes/fill/bloqueos y dependencia del filtrado temporal. Esto requeriría nueva decisión y presupuesto, versión histórica resuelta, geometría y selección temporal prefijadas, más validación del contenido. Este informe no la autoriza.

**Sin soporte para la adjudicación fina:** con lo consultado no se establece qué satélite tiene razón ante una diferencia375m/minutal, continuidad de un incendio, exposición física porpíxel o denominador comparableMODIS–VIIRS. Es una limitación de evidencia y contrato, no una imposibilidad física general. Cadencias15/10min y estados/granuleversion no verificados impiden usar esta etapa como validación deG1.

**Stop concreto:** si no se establece una semántica histórica verificable deMask/DQF/fill/filtrado, o la pregunta futura necesita una oportunidad física entrepasadas que no suministran estos tiempos, no se adquiere para adjudicar esa pregunta. UnG0 documental negativo/inconcluso no se rescata cambiando fechas, buscando un positivo o reabriendo el presupuestoL2.39,37,35A,33,30B,modelo yproducción permanecen intactos.

La matriz por requisito/caso,catálogo,fuentes,querylog ycontador explícito0 quedan en `docs/reviews/evidence/goes-preflight/`. El revisor de medición comprobó independientemente documentos primarios, los diez nombres listados y las limitaciones de versión/tiempo/acceso, sin bloqueantes para este alcance documental condicionado. Conserva dictamen y evidencia separados; este pase de revisión no es un pase de decoder histórico, oportunidad física o accesoGetObject. El cierre se realizó antes de10:00, sin extensión ysin tocarD.
