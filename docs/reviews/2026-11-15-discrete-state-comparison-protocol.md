# Protocolo33 — etiquetas nativas sobre cohortes discretas fijas

Congelado antes de leer etiquetas, ejecutar joins o calcular estados conjuntos. Adopta diseño33 y revisiones de identificación/medición/coste con precisiones aquí explícitas. Autorización acotada: inicio2026-11-15T06:48:00Z; fin2026-11-15T07:48:00Z, **incluida revisión independiente**, sin reiniciar por errores/correcciones. No nuevas descargas, HDF/FIRE, geometría continua, modelos, productos publicados o producción.

## Estimando, alcance y cohortes

Unidad: **etiqueta nativa del quad nominal asignado al punto de consulta**, nunca actividad física en el punto, área, incendio u oportunidad física equivalente.32AGEO pasó revisión;30B continuo permanece fallido. G1físico/PSF/exposiciónpíxel/MODISSuspect científico no quedan resueltos.

Heredar sin reconstruir propietarios ni índices32A: dos casos2019-01-03/2023-02-10, AOI/CORE/origen previos; fases(0,0) y(125,125)m; pasos250m/500m anidados por fase; prioridadesearly/late. **16escenarios totales**, no16por caso. Primaria por caso fase0/paso250/early, demás sensibilidades todas visibles. Metadatos32A deben confirmar198804consultas únicas antes de expansión por política y397608filas finales por punto/escenario; si no coinciden, bloquear por dominio, no ajustar la cifra mirando etiquetas. No shiftsVIIRS u otras grillas/fases/casos.

## Preflight, entradas cerradas y freeze antes de datos

Sólo manifests/certificados/salidas32A aprobados y tablas de etiquetas nativas universales ya exportadas24B, identificadas por ruta ySHA en sus manifests. Primero inspección de **metadatos/esquemas**, sin leer valores de etiquetas; registrar rutas, hashes, versiones/productos y mapping de nombres a esquema canónico antes del run. Si los exports no suministran estos contratos, entregar bloqueo, no abrir HDF o catálogo positivo para completarlos.

Allowlist estricta de columnas de etiqueta: `case,product,row,col,mask_class,algorithm_QA,geographic_flag,surface,screen_sensitivity_state,screen_exclusion_reasons,screen_unresolved_reasons,M13_non_nominal`. Identidad de archivo, versión, plataforma y decoder proviene de manifests, no de nuevas columnas de contenido. No cargar columnas de áreas, geometrías, retenciones continuas o cualquier variable fuera de allowlist. Los aliases indispensables de nombres se fijan explícitamente por esquema/metadata antes de valores; no inferir roles de datos por resultados.

Congelar protocolo/código/tests/decoder, fuente24B nativa y manifests, catálogos individuales permitidos sólo para retención, todas las cohortes/rosters/candidatos exactos32A y sus manifests, cap y mappingQA abajo. SHA originales protegidos antes/después. No reconstruir geometría o usar áreas incorrectas24B/30B. Archivo copiado no se presume íntegro por nombre: su hash/shape/procedencia deben verificarse.

Catálogo positivo es **sólo auditoría de retención nativa**; jamás fuente para rellenar máscaras/QA de la tabla universal. La fuente de labels debe cubrir todos los IDs32A que el manifest24B declara exportados. Un ownerID oincludedID esperado en tabla universal que falta es **fallo de procedencia/join**: gatefalse, detener alcance afectado; nunca ocultarlo comoUlegítimo o completarlo con catálogo. Ausencia fuera del universo documentado se reporta separadamente; no habilita seleccionar una cohorte favorable. Campo nulo documentado en un registro válido→U con causa para ese campo; no detección0inventada. Ausencia genuina documentada en metadatos de un campo se mantiene como incompletitud visible, sin llamarla identidad completa.

## Replay e identidades no compensables

Claves nativas únicas porcaso/producto/fila/columna, más identidad/versiones de manifiesto. Verificar scan coherente con32A. Duplicatekey, índice fuera de dominio, join uno-a-muchos, versiones incompatibles o máscaras/QA diferentes para el mismoID entre exportacionesearly/late bloquean. Verificar valores nativos iguales independientemente de política; prioridad cambia elownerID, nunca su máscara/QA. Null documentado y valor presente contradictorios entre duplicados no se resuelven escogiendo el conveniente.

Una fila porpointID/caso/fase/paso/política, **todos los puntos**32A. Añadir etiquetas porjoin muchos-a-uno validado, sin quitar puntos sin propietario. Hash de la proyecciónGEO antes/después exactamente idéntico. QA/fuego no pueden cambiar candidatos,interiores,ownerID,causas,referencias o población. Las propiedades sin dueño único conservanUgeometry y todas sus causas32A (frontera,tiempo desconocido,ambigüedad mismo scan,sinsoporte), no una etiqueta de un candidato favorable.

## Estados primarios congelados

Por instrumento/punto: máscara original7/8/9→`1`detección registrada;3/5→`0`no detección registrada; resto→`U`con causa (sinowner,documentednull,nube,glint,bowtie/noprocesado,desconocido,fill/layoutnointerpretable). Mask3/5 no certifica cielo útil ni ausencia física.7–9siempre1 aunqueM13 no nominal,screen excluido,QA desconocida oSuspect global; clase7 no se elimina por confianza baja. QA es otro eje y jamás cambia la máscara primaria interpretable.

Tabla exhaustiva3×3 por escenario: `00,10,01,11,0U,1U,U0,U1,UU`, primer símboloMODIS. Cinco agregados00/10/01/11/U dondeU suma los5estados con al menos un desconocido. Sumas exactas=Ntotal de puntos, conUgeometry ymask/fieldunknown separados por causas.1U/U1 visibles;UU no se llama acuerdo.

Primaria descriptiva: conteos y fracciones sobreNtotal por caso, escenario primario. Todas las sensibilidades tienen mismo esquema condenominador propio, sin selección del mejor. Jaccard conocido secundario=n11/(n11+n10+n01); denominador0→null con causa, nunca1/0ni éxito. AdjuntarNconocido/Ntotal/n1U/nU1/causasU. No precision/recall físico, porcentajes de desacuerdo causal eliminado, frecuencia de incendios, área oICIID.2019 no se presume sin positivos por inventario antiguo: verificar nuevo dominio sin exigir un resultado prefijado.

## QA secundaria: mapping fijado antes de conteos

No se redefine el screen nativo24B ni se llamaNASA a una política propia. Se usan únicamente sus campos previos y los campos crudos requeridos:mask_class,algorithm_QA,geographic_flag y estado/causas de screen; enVIIRSademásM13_non_nominal. ParaMODISM13 es `not_applicable`, nofalse ni desconocido. Los nulos o causas se preservan; no decodificar unlayout no identificado como nominal.

EstadoQA por instrumento, con todas lascausas guardadas:

1. `non_nominal`: exclusión conocida y verificable del screen previo, oM13_non_nominal explícitamente verdadero enVIIRS. No altera unpositivo1. Guardar también incompletitudes adicionales, sin convertir una no nominalidad conocida en nominal.
2. `unknown`: sin no nominalidad conocida del punto anterior y screenunresolved/null/layoutdesconocido, ausencia de cualquier campo crudo requerido o ausencia de sus causas necesarias. Una etiqueta de screen no puede acreditar nominalidad si falta el soporte crudo requerido. Unscreenexcluded sin soporte de procedencia/campos para verificar su causa se mantieneunknown, con el valor previo visible.
3. `nominal_in_inspected_fields`: screen `local_candidate`, campos crudos requeridos completos/interpretables, sin exclusión/unresolved y sinM13 no nominal aplicable. No certifica oportunidad física o toda calidad del producto.

Tier pareado exhaustivo: si algún instrumento `non_nominal`→`some_non_nominal`; si ninguno es non_nominal yalgunounknown→`QA_unknown`; si ambosnominales→`both_nominal_in_inspected_fields`. Mostrar también cadaestado/causeporproducto; un tier non_nominal puede coexistir con incompletitud del otro y se conserva su causa. Sinowner único/QA correspondiente→unknown, no tiernominal por datos de candidatos.

Tablas tiers secundarias sobrela misma cohorte conNtotal/retención visibles y etiquetas primarias intactas. Si se muestra el screen previo como subconjunto adicional, publicarNantes/después y puntos/nativeIDs positivos excluidos, incluidosM13; no llamarlo “agreementimproved”, optimizarlo porJaccard o seleccionar un tier favorable. `AUTOMATICQUALITYFLAG=Suspect`MODIS queda como eje global pendiente, separado de tiers locales; no inventarPassedni reglasL1Btransferidas.

## Superficie y catálogo nativo

Conservar `surface` real exportada24B y su provenance. SiVIIRS ya tiene una máscara geográfica land/water genuina documentada, usar ese valor y fuente; **no afirmar que todos sus positivos tienen superficie desconocida**. Si no está disponible/interpretada, conservarunknown, nunca inferir tierra por positividad ni copiarMODIS. La primaria siempre sin estratificar: ningúnpositivo se elimina por superficieunknown.

Secundarios de superficie: desconocido si alguno loes; luego costa presente; luego tierra/tierra,agua/agua,conflicto. Conservar par de valores nativos/procedencia. Partición exhaustiva sin dobleconteo; mostrar positivosunknown en total.

Catálogo individual completo7–9sólo pararetención: conservar todos losnativeIDs, causas, scopescentroAOI/halo/exterior/noasignable, M13 ydosbordesAqua con geometríaNULL. No backfill de labels ni fabricar quads. No usar áreas continuas heredadas ni llamarNULLárea0.

**Prepropiedad=incidencias STRICT_INTERIOR32A**, nunca bboxpostings/candidatos que pueden estar fuera. Frontera se cuenta aparte; includedquad con0consultas interiores es distinto dequad fuera de universoCORE. Propiedad=incidencias cuyoownerID elegido coincide. Mostrar por caso/instrumento/fase/paso/política:nativeIDs con≥1strictinterior,con≥1ownership ycantidad de puntos de cadaID. Roster y catálogocompletos incluso sinpuntos.

Partición de retención con precedencia fija: (a)geometría/quadno disponible,NULL;(b)quadfuera universo32A;(c)includedquad sinstrictinterior;(d)strictinteriorpresente pero sinownership;(e)conownership. Boundaryincidencias yotrascausas adicionales siempreseparadas, no se usan como representación. ScopesAOI/halo/exterior no se mezclan ni se interpretan comoausencia física. Unpositivo sinpuntos continúa positivo nativo; unquad con muchos puntos no son muchosfuegos. No elegirgrid/política para maximizarretención.

## Tiempo, nested e invariancia

Cada fila hereda sus propiosownerpairscanIDs yreferenciasMODISEVcenter/EVstart yVIIRSev_mid/scan_start/end de32A, conunidades/época/validación. Diferencias sólo si ambasrefs existen; deotro modo null/causa. No transferirnearestcentertime, inferir exposiciónpíxel o introducirventana temporal para mejorar acuerdo. Evolución real entrepasadas sigue mezclada coninstrumentos.

Gates de tolerancia0: claves/filas exactamente32A, proyecciónGEOigual; nine/fivestatescierran; valoresnativeID únicos eearlylateidénticos; QA/M13noborra7–9; nullnunca0; catálogoroosterscierran sinomitirpositivos; every500point compartido con250 de mismafase/política conservaowner/causas/mask/QA/surface/refs exactamente. Nestedvalidación utiliza consultasindependientes32A, no copiarresultado como prueba. Fasesdiferentes son cohortesdiferentes, noidentidad exigida. Testspermutar/eliminarlabels/QA mantieneGEO; faltanteexpectedID falla; nullfielddocumentadoU;VIIRSsurfacereal/unknown;M13positivo;Jaccard0dennull; fronteraystrictinteriorretención;sinquad/outsideuniverse/0queriesdistintos.

## Recursos, artefactos y stop

Límites fijos:≤1Mfilasfinales,≤2Mjoins nativos,peakRSS≤2GiB(conunidadesplataformaregistradas),salidasfísicas≤200MiB; cap absoluto07:48Zinclreview. Sin aumento para rescatar un escenario. Helperspuros/tests sin dependencia.runtime/clock; driver aplicaUTC/operaciones/recursos, snapshots yhashes. Establecerenpreflight contador de joins como búsquedas de etiqueta porinstrumento/fila; cada consulta debecontarse aunque reutilicecaché. Retenciónnative rostersecuenta/apartepara noocultarcostes. Guardarnegativos/parciales yscope.

Primeraentrega: freeze/manifiesto,tabla completa porpointID/escenario,9/5estados/QA/surface/refs,rosters estrictos/retención,CSV/JSON/export yreporte. MapaHTMLoffline de puntos opcional sólo sicabeconrevisión, sin áreasinferidas niCDN; omitirlo nodebeocultar unfallo. Todos16escenarios sepreservan.

Siidentidad/provenance/nestedfallan→detener conclusióncomparativa delalcanceafectado, publicarfallo sinrerunfavorable. Siestadosdiscordantespersisten→descripcióncondicional, no identificaquéinstrumentotienerazón. Sisensibilidadescambian→documentaraliasing/retención sin escogermejor. Sinuniónpositiva/masaU/incompletitud/cap→inconcluso físico; norescatarconotrocaso/tier. NingúnthresholdJaccard/mejorapromuevearmonización,G1o cambia30Bfallido. Nuevasvariables sobreestasfechas no sonholdoutfresco. Revisiónindependiente requerida antesde conclusión; ningunaetapa modifica producción.
