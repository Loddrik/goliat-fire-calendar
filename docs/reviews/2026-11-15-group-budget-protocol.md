# Protocolo35A — presupuestos de grupo conCDF congeladas y control de mezcla fija

**Protocolo previo a implementación y datos. Este documento no ejecuta predicciones, nuevas pérdidas, asignaciones ni refits.** Cap absoluto: inicio2026-11-15T07:19:05Z, fin2026-11-15T08:04:05Z,45min incluidos protocolo, implementación y revisión independiente, sin reinicio. Checkpoint de identidades antes de2026-11-15T07:34:05Z; si no es auditable a esa hora, STOP con entrega parcial, sin rescate con otra familia/partición/contrato.

## Consejo, pregunta y límites

Conservar criterios24/31/35: validez30%, información25%, factibilidad20%, transporte15%, interpretación10% y no compensables. El acuerdo operativoA+Cprimero no borra el disenso: observación/medición preferíanB por información nueva. D tiene checkpoint de consolidación realizado por raíz; Bpersistencia/cubo queda fuera de este experimento y no se ejecuta en paralelo.

Pregunta: ¿cómo cambia la discrepancia MAE frente a las deteccionesSNP registradas en las comunas held de21 al restringir la reconciliaciónCDF de54comunas a presupuestos por región, comparado con la misma decisión globalG? Es un cambio de decisión/acoplamiento conCDF/Bcongelados, no prueba de ecología, física del fuego, causalidad u oportunidades observacionales. G1físicofalse;33nominal no aporta groundtruth ni parámetros. No nuevas familias, descargas, targetretargeting, grids de semillas/λ/proporciones o cambios de producción. Fechas, regiones y respuestas21 ya exploradas: noholdoutfresco.

## Único dominio y entradas cerradas

Usar **sólo21**: cuatro regímenes `08_forward,08_backward,16_forward,16_backward`, tabla54CUT×4temporadas×12meses por régimen, mismas clavesCUT/season/m y gtemporal, source/held,14publicadas/40restantes fijadas. Cada régimen tiene54predicciones antes de filtros. Orígenes/destinos temporales y33Biobío/21Ñuble son exactamente21; no seleccionar años/comunas por resultados. Máscara fija6celdas de21 construida conMODISTerra/AquaUTC<2012-01-01; no reemplazar por223 ni usarSNPheld para máscara.

Entradas permitidas: manifests/protocolo/código congelado21, `data/processed/cold_region_audit/models.json`, `predictions.parquet`, `candidate_mask.csv`, fuentes canónicas/procedencia sólo si son indispensables para identidades; no18/24Cni otros paneles. Registrar rutas/SHA256 y esquema antes de valores. No leer modelos para refitear: sólo restaurar los mismos coeficientes, elecciones yCDF por régimen. Verificar hashes contra21 y proteger todos los originales antes/después.

Primero separar una tabla de **features únicamente** `[cut,season,m,g,aqua]`, nativekey/regime y asignacionesSOURCE/held derivadas del modelo/territorio; no introducir snpp ni otra columna target en predictor/solver. Congelar/restaurar modelo y features y registrar su hash. ReproducirB yGconfeatures; congelar predicciones B/G/R/P/C y sus controles antes de unir etiquetasheld para calcular pérdidas. Las etiquetas históricas que estén físicamente en21predictions no pueden entrar a funciones de predicción, reparto, partición o selección; la lectura de target para pérdidas ocurre sólo después de pasar gates yfreeze de predicción.

## Cinco decisiones fijadas antes de resultados

- **B:** baseline de21, SOURCE con su política afín congelada; held fallbackM1 idéntico21.
- **G:** `E11_coherent` original21, mismaCDFE11κ10, reconciliación global54 y presupuestoΣ54B.
- **R:** mismaCDFporcomuna, solver/riesgo/tie-break congelados; reconciliar separadamente grupos reales CUTprefijo08 y16, cada presupuesto igual aΣBdeesegrupo. En cada régimen los grupos reales coinciden conSOURCE/held, cambiando sus roles entre regímenes.
- **P:** mismaCDF/solver, partición artificial única: para cadaCUTstring canónico calcularSHA256UTF8de`goliat-council35-partition-v1|`+CUT. Orden ascendente por bytesdigest; empate porCUT. Primeros33grupoP33, restantes21grupoP21. Lista completa/hashes se congelan antes de pérdidas. No estratificar por etiquetas, intensidad, ubicación o resultados, ni probar otrassemillas.
- **C:** `C=(B+G)/2` porfila; proporción1/2 fija, sin ajuste, selección, pretensión de medianaCDF o óptimo de reconciliación.

R/P reutilizan distribuciones y valoresB originales; no se aprende nada de fuentes/regiones held. `g` del modelo es calendario, no región geográfica. No confundir grupos de presupuesto con el pooling estadístico que ya forma laCDF.

Para cada régimen/mes construir54distribuciones y54B antes de dividir en grupos. R/Pson subproblemas del mismo objetivoΣE_F|Y−a|,a≥0,Σgrupo a=ΣgrupoB, mismo desempate euclídeo haciaB. No aplicar restricciones a un subgrupo después de haber filtrado filas. C preservaΣ54B porqueG/Blo comparten; no se presume que preserve cada presupuestoR/P.

## Gates de reproducción, matemática y no fuga

Freeze de código/tests/protocolo/inputs antes del run; pruebas sintéticas previas, helperspuros sin.runtime/clock, driver aplica cap y recursos. Sin gates completos no pérdidas nuevas o rankings.

1. Reproducir exactamente las claves y54CUT por régimen/mes, B yG21 con tolerancias numéricas originales. RestaurarCDF por régimen y fuenteSOURCE-only, comprobar hash de parámetros/políticas inmutables. No reinterpretar destinos21como nuevosholdout.
2. ReconciliaciónR/P no negativa/finita; porgrupoΣa=ΣB con tolerancia `1e-10*max(1,ΣBgrupo)`. Gmantiene identidad54original. Todos los controles con mismasclaves/target/filas; sin completar actores faltantes con0.
3. Sobre **las mismas54CDF** ypresupuestosglobales idénticos, verificar riesgo esperadoCDF `risk(G)≤risk(R)≤risk(B)` y`risk(G)≤risk(P)≤risk(B)`, usando tolerancia original `1e-8*max(1,risk(B))`. Son identidades de optimización, noMAE física. RiesgoR/P≥Gporque añaden restricciones; una eventual mejora externa no sería mejora del óptimoCDF global.
4. KKT se verifica por **cadaGRUPO**R/P, umbral1e-8, no unKKTglobal que exigiera igualmultiplicador entre grupos. Cnoesóptimo y no se le exigeKKT; comprobar punto a puntoL1convexidad `|C−Y|≤(|B−Y|+|G−Y|)/2` después deljoin de evaluación y suΣ54. Esta cota no garantiza superar al mejor o proteger cada subgrupo.
5. Testsdegenerados: unúnicogrupo54→G; singletonsporCUT→B; renombrar grupos sin cambiar miembros conserva salida; permutar orden de filas y restaurarlo conserva valores. SiGyaesfactible para presupuestosR, entoncesR=G con el mismo desempate euclídeo haciaB; testear explícitamente y con tolerancias originales, sin afirmar igualdad si sólo se aproxima lafactibilidad.
6. SOURCE/held se usan sólo para aplicar controles/fuentes ya congelados yreportar. Test sintético conCDF yBheldfijos: perturbar SOURCE no cambiaRheld al reconciliar elgrupoheldseparado; no usar esa invariancia para afirmar independencia de entrenamiento de lasCDF. El predictor/solver de todas variantes debe ser invariante al eliminar/cambiar targetsheld; funciones aceptan exclusivamentefeatures/modelo/particiónBpermitidos.
7. Construcción de transferencia `T=ΣheldG−ΣheldB` por régimen/mes y su análogoSOURCE, con suma compensada entre roles; bajoR`T_R=0` porpresupuesto. Se reporta como contabilidad construida, **no nueva habilidad sobreheld** ovalidación de región. P/CyGpueden trasladar presupuesto entreSOURCE/held.

Checkpoint15min07:34:05Z: B/Gexactos, claves/panel/máscara/modelohashes, particiónP prefijada y tests/controles de grupos deben ser auditables. Si no, congelar un estado parcial/bloqueado sin abrir pérdidasnuevas ni cambiar el panel. No reiniciar el cap por correcciones.

## Evaluación prefijada tras gates yfreeze de predicción

Primaria: **media de cuatro contrastesheld por régimen `MAE(R)−MAE(G)`**, igualpeso de regímenes, todoslosheld ymeses21fijos. Reportar los cuatrovalores y el promedio; signo negativo indica menor discrepancia conSNPregistrado. El agregado ponderadoporfilas es secundario y no reemplaza la primaria si cambia el signo. No tratar regímenes dependientes ocomunas/meses como réplicasIID ni producirp-values/ICporfila.

ReportarB/G/R/P/C sin elección del ganador: todos54, SOURCE, held,14publicadas,40restantes, SOURCE×14/40 yheld×14/40; cerosY=0, Aqua0/Y>0, ambos0, positivosY>0 yextremos fijosY≥50. Mismos estratos para los cinco métodos. MostrarN,MAE,sesgo, sumas/MAEregional ypresupuestos. Añadir distancia L1 de cada decisión aB, transferenciaSOURCE/held y exceso de riesgoCDF respecto aG sobre las mismas distribuciones; estos diagnósticos no requieren targets y no son mejoras observacionales. TotalesregionalRigualB son construidos, no logro adicional. No seleccionar casos/años/gruposcontratos que rescaten una primaria negativa.

WorstCUTfijo sinselección por el resultado nuevo: dentro de cada régimen definir el CUTheld con mayorMAE **G21original**, desempate lexicográficoCUT, guardarlo despuésdelgatedeidentidad yantes de nuevaspérdidas, y conservarlo para todoslosmétodos. Este diagnóstico está seleccionado con uncontrol histórico ya explorado, noholdout yno nueva primaria. Para transparencia entregar tabla completa porCUT. Si determinar el fijo exige lectura de etiquetas antes delfreeze de predicción, posponer su cómputo a la fase de evaluación sobreGya congelado; nunca afecta predictions/selección.

Pcontrolhash yCmezcla **no tienen intensidad de regularización emparejada** conR; diferencias no identifican un efectoecológico/geográfico causal. Una única particiónPno es distribución de aleatorización; no repetir para buscar otra. Cno arbitra “verdad” entreB/G.33sólo advierte sobre representación/aliasing y desconocidos: no convertirJaccard/tierQA/retención de doscasos en pesos otargets deeste modelo.

No umbral de promoción física/producto. Resultado favorable primario con daños en14/extremos/worstCUT se publica completo; no lo declara apto. SiR yP actúan similar, se limita explicación territorial; si difieren, sólo evidencia de sensibilidad a agrupación. Si primaria negativa, se conserva y cierra contraste; ningún ajuste dehash/mezcla/CDF. Si cap/gate falla, inconcluso parcial, no se amplía infraestructura.

## Recursos y salida revisable

Hasta2000llamadas individuales a `reconcile` en total, incluidas pruebas sintéticas, controles y comprobaciones reales. Llamada significa una invocación del solver sobre un grupo de filas; cada repetición cuenta aunque el grupo coincida con otra. Ejecución real mínima prevista:G192+R384+P384=960llamadas; registrar aparte controles/sintéticos y suma global. Las pruebas previas no se usan para ocultar ejecuciones reales.≤1Mfilas,peakRSS≤2GiB(conunidadesplataformaregistradas),salidasfísicas≤100MiB, cap08:04:05Zinclreview. No raw/HDF/nuevosdatos. Runoutputs en un directorio nuevo exclusivo, protegido de sobrescritura; no modificar21ni otrosestudios.

Artefactos: protocolo/cap/freeze de código/inputs ypredicción,partición completa hash/regiones, identidadesB/G, parámetros/modelos sólo referenciados porhash, predictionsfijasfeatures-only antesjoin, controles de presupuestos/riesgo/KKT/invariancia, evaluación/reportes completos, rostersworstCUTfijos, límites/consumo, hashes de resultados/previousunchanged yreviewindependiente. Primeraentrega45min; un partialauditable es válido si gate/cap impiden terminar. Ningún artefacto científico queda promovido por ausencia de tiempo.
