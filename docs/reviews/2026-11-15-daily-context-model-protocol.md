# Protocolo37 — contexto de adyacencia diaria conCDF congeladas de referencia

**Decisión explícita de raíz posterior a36 auditado, no ejecución automática del cubo.** Se fija antes de código/datos/modelos nuevos. Inicio absoluto2026-11-15T08:07:07Z; fin2026-11-15T09:07:07Z,60min **TOTAL**, incluidos protocolo, implementación, tests, fits y revisión independiente. Sin reinicio ni ampliación por errores. Checkpoint de identidades a2026-11-15T08:32:07Z: si no es auditable,STOP parcial sin nuevas pérdidas. Diseño36 es antecedente; este protocolo fija la matemática y controles autorizados.

## Pregunta, dominio y decisiones

¿Condicionar lasCDF de21 por adyacencia diariaAqua real aporta menor discrepancia conSNPregistrado que la misma familia con placebo de días y queG21? Unidad de respuesta=celda-díaSNPmensual del contrato21, no fuego físico ni oportunidad observacional. No cambiar máscaras/geografía/períodos/targets/semilla/rasgos/κ.35A negativo permanece cerrado y35Rno se usa.33nominal no es truth ni fuente decoeficientes. Fechas ya exploradas no sonholdoutfresco; sin significación/ICIID/p-value o promoción automática.

Único panel21: cuatro regímenes08_forward/08_backward/16_forward/16_backward, mismosSOURCEcuts/originseasons/destinos,54CUT por mes, máscara6 fija pre2012,8temporadas2012–2019 yexpansión10368filas21. Cubo36 independienteFULLPASS:5184claves únicas,10368expandidas; reglasUTCJul2012–Jun2020,dentroMES,mismacelda ypermutaciónSHA de columnas diarias congeladas. No nuevasfeatures ni modificación del cubo. Verificar hashes/dominio/Aquaexacto; no reconstruirD ni permutar otra vez porque no convenga.

Métodos: B yG21congelados como controles; Qreal yQplacebo nuevos, mismafamilia matemática y sóloDdistinto. B,pesos afines, ratios/r_g yCDFold por régimen quedan fijos. Reconciliación **GLOBAL54** con presupuestoΣB,mismosolver/tie-break y tolerancias21; ninguna restricciónregional35R. No nueva búsqueda de regularización, forecast, targets, cuantiles o variantes por resultado.

## Fuentes, selección per régimen y dos freezes

Antes de candidatefit congelar protocolo/código/tests/decoder/modelos21/cubo36/inputs/controlfeatures ycap porSHA; registrar versiones/entorno,protegidos antes/después. Inputstarget sólo21, lectura por columnaKEYS+snpp y**filtroSOURCE antes de cargar valores**. Para cada régimen, SOURCE=`cut∈model.source_cuts AND season∈model.origin_seasons`; keys cut/season/m. ElParquet21tiene dos copias de cadakey entre regímenes: dentro de la extracciónSOURCE exigir que todas las copias tengan exactamente el mismoYfinito/no negativo, entoncesunique; discrepancia→gatefail, nunca promedio/primera fila conveniente. Usar filtro de escaneoParquet/SQL registrado, no cargar todosYyfiltrar después enmemoria.

Los cuatroSOURCEsets colectivamente pueden cubrir todosloslabels: **no afirmar globalmente “no se leyeronheldlabels”**. La garantía es PORREGIMEN: ningún destino temporal ni CUTheld deese régimen entra a su fit/fallback/selección. Capturar selectores/keys/hashes en cada modelo; nunca reutilizar labels deotro régimen por caché global sin filtro validado.

Features/evaluación10368 deben coincidir con21 y36. Cargar controlesB/G yfeatures sin columnasY para reproducir baseline. Ajustar nuevasCDF únicamenteSOURCE ypredecir con `[cut,season,m,g,aqua,D]`; elsolver sólo recibe átomos/pesos/B. Congelar modelos candidatos ypredicciones54, soporte/fallbacks ycontroles **antes de unir targetsheld para pérdidas**. Registrar hora/hash de ambosfreezes ydelprimer acceso de evaluaciónheld. No target para elegirfamily/semilla/κ/pool/fallback/grupo.

## Átomos originales y escala: sin alterar el floor

Por régimenyconsulta, original `atom_distribution`21 es el control exacto. Extraer de `_components` probabilidades yátomos normalizados **RAWZ antes delmax(1,·)**. LaCDFparent original para(g,s),s=1[Aqua>0], tiene masa0ypositivos con esosZ ypesos. Cada observaciónSOURCE positiva generaZ=`Y/(1+r_g*Aqua)` con r_g **congelado21** deese régimen. Ceros permanecen átomo0; no se normalizan a unpositivo artificial. No extraerZ de predicciones ya flooreadas ni “desfloorear” valores1.

Componer toda nueva mezcla en espacioRAWZ: representar masa0yátomos positivos explícitamente. Sólo al predecir convertir cada positivo a `max(1,(1+r_g*Aqua_query)*Z)`, como21. No aplicarfloor a0, no aplicar dosveces, no cambiar escala yno usar p×media como mediana. Mediana inferior de laCDFmixta con su masa0ysemántica21. Se puede conservar probabilidadactividad para diagnósticos, sin nuevoscalibradores.

## No variaciónSOURCE: identidad completa prioritaria

Para cada variante ySOURCEparent(g,s), computarlen(uniqueD) únicamente en SOURCEcuts×originaños. Si≤1, **incluido poolvacío**, desactivarD y devolver `atom_distribution` ORIGINAL21 COMPLETA por cada consultaCUT/g/Aqua, incluido SOURCEconlocalCDF y queryD0o1no visto. No sólo parent, no sóloheld yno resuavizarJeffreys. El originalp=(m+.5)/(n+1) no es en general(m+10p)/(n+10); ese cambio no puede presentarse como ganancia temporal.

Testnegativo-control forzarSOURCE D=0 enTODOSlospools yconsultarD0yD1paraTODOCUT: CDFcompleta original y54allocationsG deben reproducirse. Si sólounpoolesconstante, suCDFindividualdebeseroriginal, **pero no exigir suallocación individualGigual**: elsolverglobal puede redistribuir al cambiar otrasCDF. No confundir identidad de componente con invariancia frente a acoplamiento global.

## Pools variables: mezcla completa yκ fijos

CuandoDvaríaSOURCEenparent(g,s), n_D esnúmero deobservacionesSOURCE deesa clase,m_D positivos yH_emp,D distribución empírica completa enRAWZ (incluye ceros). H_P esCDFparentoriginal21, p_PyF_P+ provenientes coherentemente de `_components`.

κparent=10 fijo:

`H_D=(n_D*H_emp,D+10*H_P)/(n_D+10)`;

`p_D=(m_D+10*p_P)/(n_D+10)`;

`F_D+=(Σ_positive,D δ_Z+10*p_P*F_P+)/(m_D+10*p_P)`.

No agregarJeffreysnuevo. n_D=0→H_Pexacto. Masapositiva0→degenerada0; no asignar probabilidadpositiva para hacer utilizable unF+vacío. Parentoriginal sinobservaciones/positivos conserva fallbacks21documentados sin retocarlos. Esta es mezclaempírica conobservacionesSOURCE potencialmente contenidas también enH_P, no posteriorBayes ni incertidumbrecalibrada; no exige marginalpreservation global yno seinterpreta como evidenciaindependiente.

ParaCUTSOURCE yparentvariable, usar datos locales **condicionadosD**, no conteoslocales incondicionales: n_cD,m_cD,Z_cD. κlocal=10 fijo:

`H_cD=(n_cD*H_emp,cD+10*H_D)/(n_cD+10)`;

`p_cD=(m_cD+10*p_D)/(n_cD+10)`;

`F_cD+=(Σ_positive,cD δ_Z+10*p_D*F_D+)/(m_cD+10*p_D)`.

n_cD=0→parentcontextual. CUTheldsiempre nlocal=0,parentcontextual; no aprendeCDFoafinidad porCUT held. La identidad de no variaciónparent anterior tiene prioridad yretornaCDFoldCUTcompleta envez de estasfórmulas. D1imposiblecuandoA=0segúncubo, pero no usar unqueryimposible para fabricarfallback favorable. Real/placebo tienen idénticaformulación y fuentes, sólo cambiaD; soporte/fallbacksporvariante,g,s,D yCUT quedanexportados.

## Controles previos a nueva pérdida y checkpoint

Pruebas sintéticas/helperspuros sin.runtime/reloj; sólo driver aplica cap/recursos. Freeze código+inputs antes de candidatosfit; counters explícitos de pruebas y reales.

- BaselineB/G, ratios/r_g,panel/máscara/modelosCDF21 reproducidos conhash/keys;54por régimen/mes ymisma lógica de normalización/floor. Cantidad10368 yclaves idénticas acontrol.
- No variación: todaCDFOLDparaTODOSCUTD0/D1 con fuerzaSOURCEconstante, incluidos locales; allocationsGidénticas con todoslospoolsforzadosconstantes. Poolvacío yqueryDno visto cubiertos. Unpoolconstante aislado verificaCDF, sin falsoassert deallocaciónindividual.
- Mixtura prob/F+igualCDFdirecta, ceros/positivos/floor, mediana inferior ymasa0correctos; n_D0,n_cD0,cerosglobales yfuentespositivasraras.
- SelectoresSOURCE aplicados antes deloadtarget; duplicadosYconflictivos fallan yduplicadosidénticosunique; featureD/sourceeligibility/fallback no inspeccionan Yheld. Metamórficos usan labels verdaderos sólo del SOURCE permitido y filas de features prohibidas con respuestas SINTÉTICAS NaN/999999; nunca leen los Yheld reales para esa prueba antes del freeze. Eliminar/alterar esas filas fueraSOURCE no cambia modelo, parámetros ni54predicciones; guardar calls/selectores.
- LocalD exclusivamente filasDmatching; heldnlocal=0. Hashmodelos/ref21 yAquadailycubo36 inmutables.
- PorcadaCDFPROPIA: prediccionesfinitas/no negativas,Σ54=ΣB tolerancia `1e-10*max(1,ΣB)`; riesgoL1esperadobajoCDFpropia≤riesgodeB con `1e-8*max(1,riskBpropio)`;KKT1e-8. **No comparar riesgos esperados entreCDFdiferentes como si fueran la misma métrica**; Gpuede tenerotroobjetivo aQ.

Checkpoint08:32:07Z requiere baselineB/Gexactos,SOURCEselectors yno-variationFULLCDF/allocGauditables. Si no están,STOP/parcial,sin abrir nuevaspérdidas ni ignorarunpool/fallback; lafamilia queda inconclusa yno se extiende elcap. Gatesrestantes yfreeze de predicciones deben pasar antes deevaluación.

## Evaluación prefijada y límites de interpretación

Primaria: media igualpeso de cuatro `MAEheld(Qreal)−MAEheld(Qplacebo)`. Obligatorio al lado: media igualpeso de cuatro `MAEheld(Qreal)−MAEheld(G21)`. Informar ambos, los4regímenes yB/G/Qreal/Qplacebo completos. **Sólo amboscontrastespromediosnegativos permiten afirmar evidencia predictiva condicional compatible con información de adyacencia**, siempre conguardrails visibles ysinpromociónautomática. Si cualquiera no esnegativo, no afirmar cronologíamásútil, no rescatar cambiando agregación/semilla/κ/rasgo/grid; si placeboigualomejor,no adjudicar novedadtemporal. Los agregadosfilaponderados son secundarios,no reemplazan primaria.

Conservar reportes21:54,SOURCE,held,14/40 e intersecciones, Y≥50fijo, Y=0,Aqua0/Y>0,ambos0,Y>0,sesgo, sumas/presupuestos,MAEregional ytablaCUTcompleta. PeorCUTfijo por régimen segúnMAEG21heldcongelado,desempateCUT; seleccionar sólo en fase de evaluaciónsin afectarpredicciones ypresentarlo como diagnóstico adaptativoexplorado, no primariofresh. Soporte n/m,masasprestadas,frecuenciaD/fallbacks porvariante yparent incluidos aunque seanadversos. No tratar meses/comunas/regímenes solapados comoIID ni inferir significación.

Compararcontrolplacebo no garantiza que se haya eliminado todaadyacencia: se conserva lacolumnapermutada única36 yno hayrereseed. Dpuedeproxycantidad/distribuciónderegistros;A≥2esnecesario,no causalidad. Si ambosmodelosmejoranGsimilarmente,no atribuirganancia al ordencronológico. Masacerosregistrosnoobservabilidad,1071CSVrawfaltantesno reparados,G1físicofalse. No convertir33Jaccard/QA/retención en labelsverdaderos o pesosCDF. Nominalidad local no acredita equivalencia física;Suspect,PSF ytiempoexposición siguen pendientes.

## Recursos, contadores y entrega

Máximo64candidatefits **TOTAL**, incluidosQreal/Qplacebo,constantcontrol,metamórficos/sintéticos. Una llamada que construye un modelo condicional por régimen+variante cuenta1, aunque no hayaoptimizador; registrar por separado losfits/helperssintéticos yreales concontrato de conteo explícito antes de testspara no ocultar réplicas. Máximo3000llamadasindividualesreconcileTOTALincluidoscontroles/sintéticos/repeticiones,≤1Mfilasexportadas,≤100MiBsalidafísica,peakRSS≤2GiBconunidadesplataformaregistradas. No ampliar después de resultados; reusar cálculo sólo si conserva identidades yno se presenta copiarresultado como pruebaindependiente.

Salidas exclusivas nuevas,sin sobrescribiroriginales: protocol/cap,code/tests/inputsfreeze,SOURCEselectorlogs/modelos ysoporte/CDFs/featurehash,predictionfreeze antesheldloss,contadores/tests/checkpoint,allocations/riesgo/KKTpropios,reportescompletos/guardrails yreview. Al cerrarverificar todoshashes deoriginales yparámetros21sinmodificar. Revisiónindependiente dentro09:07:07Z obligatoria; si incompleta,entregaparcialsinconclusióncomparativa. Ningúndesenlace autoriza producción,nuevasfamilias ogrillasautomáticas. El resultado negativo/nulo/inconcluso sepublica talcualy35negativopermanececerrado.

## Aclaración de recursos previa a ejecución

Antes del commit, freeze o cualquier nuevo fit, raíz corrigió el presupuesto estimado32→64 modelos completos por régimen/variante para incluir pruebas, controles constantes/poison, reconstrucción independiente y regresión de raíz (estimación48 llamadas). Los mismos Qreal/Qplacebo y controles permanecen fijos; no se autorizan nuevas variantes, semillas o búsquedas. Cada invocación que produce el modelo completo cuenta una vez, no cada grupo padre/local interno; la reconstrucción independiente se registra aunque no llame al helper del autor. Los demás límites y horas no cambian. Esta previsión de coste anterior a datos no depende de resultados37.
