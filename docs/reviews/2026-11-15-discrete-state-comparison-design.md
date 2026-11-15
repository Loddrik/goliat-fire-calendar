# Diseño33 condicional — comparación de etiquetas registradas en puntos nominales fijos

**Sólo diseño: no se abrieron datos de etiquetas nativas, no se ejecutaron joins, QA, estados conjuntos o nuevas métricas.** Requiere32AGEO con todos sus gates, revisión independiente aceptada y un protocolo33 propio congelado por raíz antes de implementar/reproducir estados. Un pase32AGEO no autoriza automáticamente este replay. Si32A queda parcial o bloqueado, este diseño no cambia ese resultado ni habilita seleccionar sólo cohortes favorables.

Estado al cerrar diseño: raíz comunica32AGEO aprobado y revisado a06:34Z, con198804consultas,16grupos y79204comprobaciones anidadas. Esa evidencia no contiene etiquetas y no sustituye la autorización/protocolo33 pendiente. No se leyó labeldata para este documento.

## Objetivo, unidad y población primaria

Pregunta: ¿qué etiquetas registradas por los dos algoritmos nativos quedan asociadas a los mismos puntos de consulta nominales, dadas unas propiedades geométricas y temporales ya fijadas? Unidad textual obligatoria: **“etiqueta nativa del quad nominal asignado al punto de consulta”**. No es clase física del fuego en ese punto, observación independiente, área quemada, oportunidad física comparable ni reparación del operador continuo.

Usar exactamente las cohortes32A: dos casos2019-01-03/2023-02-10; AOI y universoCORE originales; fases(0,0) y(125,125)m; pasos250m y500m anidados por fase; prioridades conjuntasearly/late. Puntos/IDs/propietarios/candidatos/causas/referencias temporales se heredan de32A, nunca se reconstruyen usando etiquetas. Primaria caso por caso: fase0/paso250/early; las otras siete combinaciones por caso son sensibilidades prefijadas, todas publicadas y ninguna elegida por concordancia. No nuevos desplazamientosVIIRS, fases, grids, umbrales, casos o nearest-neighbor.

Cada escenario conserva **todos sus puntos de consulta**, incluso sin propietario nominal o etiqueta interpretable. No filtrar a ambos sensores presentes, QA nominal, cielo despejado, positivos o píxeles con datos antes de construir la tabla primaria. No agrupar ambos casos como muchas réplicas; vecinos/grillas/políticas comparten datos nativos.

## Condiciones de entrada y congelamiento previo

El protocolo33 deberá fijar start/end reales y recursos antes del código/datos. Primera entrega propuesta≤60min incluida revisión. Entradas cerradas: manifests/certificados/salidasGEO32A aprobados, índices de fuentes originales y **sólo columnas nativas ya exportadas por24B** necesarias para máscara/QA/identidad/superficie y catálogo individual de positivos. No abrir HDF/FIRE originales ni nuevos productos para rellenar campos. No usar áreas, intersecciones, propiedades o retenciones continuas incorrectas24B/30B. Los campos de área heredados no sirven para ninguna métrica ni ponderación33; conservar su provenance histórica únicamente donde corresponda al catálogo, con aviso de invalidez.

Antes de leer etiquetas: congelar código/parser/decoder, protocolo, hashes de fuentes nativas, tablasGEO32A, rosters de puntos y nativeIDs, AOI/CRS, esquema, semántica de valores nulos y catálogo completo. Cualquier hash o procedencia incompatible bloquea la comparación, sin buscar otra fuente o versión que favorezca el resultado. Verificar que las claves nativas sean caso/producto/versión/archivo/fila/columna yscan coherente; no unir por coordenada redondeada o cercanía.

Separar dos situaciones:

- **Identidad/correspondencia inválida:** duplicatekey, nativeID fuera de dominio, versiones incompatibles, relaciones múltiples contradictorias o mask/QA diferente para el mismo nativeID entre las exportacionesearly/late → gatefalse; detener estados del alcance afectado y registrar. No escoger la fila conveniente.
- **Etiqueta legítimamente ausente/null o registro nativo faltante en un propietario identificable:** conservar el punto y propietario, etiquetaU con causa explícita `native_label_missing`/`native_record_missing`; nunca0. Cuantificar cobertura del replay y casos no comprobables, sin transformar esa falta en observación física ausente. El protocolo no puede llamar identidad completa al campo faltante.

Los valores nativos de un mismo ID deben ser idénticos al reutilizarlos paraearly/late; la prioridad puede cambiar **qué** ID posee un punto, pero nunca cambia la máscara/QA del ID. Un diccionario nativo único, verificado contra todas las versionesearly/late disponibles, evita que el estado dependa accidentalmente de la fila del ledger usada.

## Replay: sólo enriquecimiento por ID, propiedad inmutable

Crear una fila porcaso/fase/paso/política/pointID, con propietarios y razones32A de ambos instrumentos. Añadir las columnas nativas porjoin muchos-a-uno validado. Hash de la proyecciónGEO antes/después debe ser idéntico; etiquetas/QA no pueden alterar candidatos, interiores, tiempos, prioridad, ownerID ni la población. No usar iteraciones de geometría para recuperar un positivo sin punto.

Mantener todas las causas32A:boundary_unidentified,time_unidentified,same_scan_ambiguous,no_nominal_support y otras explícitamente declaradas. Si no hay propietario único, estado básicoUgeometry con razón; no asignar0 ni escoger una etiqueta de los candidatos ambiguos. Se pueden conservar IDs candidatos sin sus valores conjuntos, paraauditoría; no resolver ambigüedad eligiendo confianza o fuego.

## Estados básicos: registrados, exhaustivos y sin borrar positivos

Para cada instrumento/punto:

| Estado | Regla primaria | Separación necesaria |
|---|---|---|
| `1` | Máscara original7,8,9 del ownerID válido | Detección registrada; no fuego físico en la coordenada del punto |
| `0` | Máscara original3 o5 | No detección registrada; no certifica oportunidad física ni ausencia de fuego |
| `U` | Sin owner único, etiqueta ausente, nube4, glintVIIRS2, no procesado/bowtie/entrada ausente, desconocido6, fill, clase/layout no interpretable | Conservar causa y máscara cruda cuando exista; nunca rellenar0 |

7–9 **siempre** permanecen1 en la primaria, incluidosM13no nominal, otras cautelas, screen local excluido yMODISSuspectglobal. Clase7 es positivo registrado, aunque tenga confianza baja. No equiparar numéricamente categorías de confianza MODIS/VIIRS. LaQA es otro eje, no cambia la máscara base. Si la máscara misma no es interpretable correspondeU; bits reservados deQA no borran una máscara positiva interpretable.

Tabla elemental3×3: `00,10,01,11,0U,1U,U0,U1,UU`, primer dígitoMODIS. Agregado5estados:00/10/01/11/U, dondeU es suma de los cinco estados con al menos un desconocido. Son mutuamente excluyentes y exhaustivos sobre **todos los puntos de consulta**, incluso ambos sin soporte. Publicar1U yU1 de forma visible, con causas/desglose de qué instrumento registrópositivo.

No existe una categoría “acuerdoU”. UU sólo dice que ambos estados son desconocidos, posiblemente por causas diferentes. UnUgeometry no equivale a nube ni a píxel que no observó.

## Resúmenes y denominadores congelados

Primaria descriptiva por caso y escenario primario: conteos enteros de nueveestados, totalN y fracciones sobre **Ntotal**. Publicar además tabla5estados, causasU por producto yownerIDs únicos representados. No convertir densidad de puntos a área ni a número de incendios. Los escenarios secundarios conservan mismo esquema y denominador propio visible.

Jaccard secundario de etiquetas conocidas: `n11/(n11+n10+n01)`; denominador0→null con causa `no_known_positive_union`, nunca1 o éxito. AdjuntarNconocido, Ntotal, n1U/nU1 y fracciónU: el denominador delJaccard no incluye todos los posibles positivos registrados. No usar `(n00+n11)/Nconocido` como conclusión de éxito dominada por00. No precision/recall, tasa de acierto físico, causalidad oICbasados en puntosIID.

No asumir que2019 sigue sin positivos porque su antiguo inventario de centrosAOI no los tenía: el nuevo dominio incluye quads que pueden aportar a puntos aunque su centro esté fuera. Si el replay efectivamente tiene unión positiva conocida0, presentarJaccardnull y valor de ingeniería, sin extrapolar sensibilidad. No elegir2023 como primaria por ser más activo.

## Superficie: primaria sin estratificar y desconocidos retenidos

La tabla principal no depende de que se conozca la superficie. Usar sólo valores ya exportados y su provenance:MODISQA tierra/agua/costa; VIIRS3/5 puede indicaragua/tierra, pero positivoVIIRS puede conservar superficie desconocida sin capa independiente. **No inferir tierra por positividad, asignarle la superficieMODIS o eliminar ese positivo.**

Secundarios: superficie nativa de cada instrumento y pares conjuntos en partición exhaustiva con orden explícito: si alguno desconocido→surface_unknown; enotrocaso costa presente→coast; después tierra/tierra, agua/agua, conflicto tierra/agua. Todas las filas permanecen en la primaria y en su estrato. No comparar tasas de tierra con una cohorte que perdió selectivamente positivosVIIRSde superficie desconocida.

## QA pareada como diagnóstico, nunca mejora elegida

Mantener máscara registrada y ejes separados: calidad/layout/fill del algoritmo, QA geográfica, canalesVIIRS/M13, bowtie/glint, screen local previo yflag globalMODIS. No inventar `QA==0` ni `Passed` como requisitoNASA. SemánticaSuspectL2 sigue pendiente; no transferir reglasL1B.

Tabla secundaria mínima sobre **la misma cohorte primaria**: tiers disjuntos por parQA (`ambos_nominales_en_campos_inspeccionados`, `alguno_no_nominal`, `QA_desconocida`), manteniendo las etiquetas básicas intactas. Fijar el mapping de bits/layouts exacto del decoder previamente versionado antes de cualquier conteo. Si se muestra aparte el screen local previo como subconjunto, publicarNantes/después, puntos/nativeIDs positivos retenidos/perdidos y estados completos excluidos, incluidosM13. No llamarlo “agreementimproved”, validar el screen por elevarJaccard ni escoger sólo el tierfavorable.

La ausencia de un campo inspeccionado permaneceQAunknown. “Ambosnominales” sólo se refiere a esos campos; no certifica cobertura física comparable. No ajustar umbrales de confianza/calidad tras resultados.

## Retención nativa y bordes: no confundir puntos con detecciones

Conservar íntegro el catálogo individual de positivos7–9 ya exportado24B, incluidos todos los casos de confianza, M13no nominal, los dosbordesAqua con geometríaNULL y positivos sin puntos. No convertirNULL en área0 ni generar un quad faltante por vecinos. Las cantidades antiguas se verifican contra hashes/esquema, no se usan para forzar el nuevo resultado.

Porcaso/instrumento/fase/paso/política eIDnativo, anexar al roster32A: número de incidencias de puntos antes de propiedad, número de puntos poseídos y si tiene≥1punto representado. SepararNativeIDs de counts depuntos; un positivo que posee muchos puntos no son muchos fuegos. Conservar categorías no excluyentes ycausas claras: sinquad/geometríadesconocida, quad sinpunto aestegrid, candidatos conpuntos pero sinpropiedad, ownercon≥1punto; jamásno_point⇒no_detection. Para particiones agregadas usar una precedencia fijada y mostrar lascausas adicionales.

Scopes del catálogo explícitos: centroAOI, centrohalo fueraAOI, exteriorhalo yno asignable. Un centrohalo puede aportar aAOI; no excluirlo del replay si32Aya lo incluye. Positivos externos sinsoporte no se anuncian ausentes; el alcance de retención nominal esAOI/halo fijados. Ninguna fracción nativa retenida significa fracción de fuego o área retenida. No optimizar paso/fase/política para salvar lospositivos que pierde una configuración.

## Tiempo por ownerpair, sin certificación de exposición

Cada fila conserva scanIDs de **sus propietarios** y referencias concretasMODISEVcenter/EVstart,VIIRSev_mid/scan_start/end enunidades/época/validación nativas. Añadir diferencias de referencias sólo si ambas existen; null ycausas explícitas enotrocaso. No reutilizarnearest-centertime ni certificaciones de antiguos pares de centros. Los puntos de un mismoquad comparten referencia; no son exposiciones independientes. Sinventanatemporal nueva seleccionada poracuerdo, ni llamar10min/exposiciónpíxel a referencias descaneo. La evolución real entrepasadas sigue mezclada con diferenciasinstrumentales.

## Gates y guards antes de conclusiones

Los gates son identidades estructurales de tolerancia **cero**, no umbrales de mejora deconcordancia:

1.32Aallgates yreviewaceptados, hashes/IDs/esquemas adecuados. Duplicatekey/conflicto de etiqueta nativa entreearly/late oalteraciónGEO bloquean; faltantelegítimo se conservaU concausa.
2.Nfilas yclaves exactamenteiguales a cada cohortefija32A; una fila porpointID/escenario. Suma9estados=Ntotal; suma5estados=Ntotal ycadaUagregado coincide exactamente con sus9estados. Estado básico, máscara nativa, surface yQA no se mezclan por coerción de nulos.
3.Puntos compartidos250/500 de cadafase/política deben tenerownerIDs/causas/etiquetas/QA/superficie/refs temporales idénticos; comparar consultas independientes ya certificadas32A, no copiarfilas y llamarlo validación. Cualquier diferencia deestado en un punto compartido esgatefalse. Fasesdistintas son poblacionesdistintas, no identidad exigida.
4.Permutando/eliminando valores deQA/fuego, ownership/candidatos/proyecciónGEO permanecen iguales. M13no nominal nunca transforma7–9 en0/Uprimario. Las ausencias nativas nunca pasan0.
5.Reconciliar rosters nativos con incidencias/owners ycatálogo completo, conservandoNULL/positivos sinpuntos. No gates de “retenerciertoporcentaje” ni veto de secundario adverso: todo coste se publica.

No hay umbral numérico deJaccard/mejora que permita promoverarmonización, resolverG1 o elegir escenario. Sensibilidades repetidas no sonICni nuevosholdouts.

## Primera entrega≤60min y decisiones

Propuesta para protocolo33: cap absoluto60min incluida implementación/revisión, helperspuros importables sin.runtime/clock; drivercapUTC, máximo1Mfilaspoint×escenario×caso y2Mjoins nativos antes de lecturas, peakRSS≤2GiB ysalidas≤200MiB (confirmarpreflightmetadataantesautorizar, nunca ampliar porresultados). Sin nuevosdatos/descargas, geometríascontinuas o entrenamiento.

Artefacto revisable: freeze+manifiesto, proyecciónGEOhashinmutable, tabla porpointID deestados/causas/owners/QA/superficie/refs, tablas9/5estados condenominadores, rosters/retención nativa,16escenarios completos(2casos×2fases×2pasos×2políticas), CSV/JSON exportables y mapaHTMLoffline opcional de puntos **sinpolígonosdeárea inferida**, reporteconlimitaciones. Si elmapa compromete revisión/cap, omitirlo ydeclararlo; tablas reproducibles sonprimeraentrega esencial. No CDN/servicios depublicación enestaetapa.

Desenlaces prefijados:

- **Gatesdeidentidad fallan:** detener tabulación interpretativa delalcanceafectado, entregarfallo/cohortes yunknownsinrepararlo con otrogrid/dato.
- **Estadosdiferen auncuandopropiedad esidentificada ysonestablesenpuntoscompartidos/sensibilidades:** evidencia descriptiva condicionada aloperador nominal discreto; no demuestra cuál algoritmo tiene razón ni quéparte corresponde a tiempo/instrumento/observabilidad.
- **Grandes diferencias porfase/política/QA osinrepresentación de positivos:** documentar aliasing/selección/retención ycerrarlímite, sin escogermejor escenario. “Grandes” debe describirse con valores, no convertirse después enunthresholddepase.
- **MasaU, uniónpositiva0, etiquetasincompletas ocap:** inconcluso para comparación positiva/física;Jaccardnullcuandocorresponde, no0/1inventado. No rescatar elresultado con tierQA ocaso favorable.

32A acredita sóloGEOdiscreto condicional;30Bcontinuo permanecefallido. Este estudio noarmoniza cantidadesMODIS–VIIRS, no pruebaoportunidadesobservacionalesniPSF/tiempopíxel/Suspectresuelto. G1físicofalse ylapreguntacausaloriginalquedanabiertos.
