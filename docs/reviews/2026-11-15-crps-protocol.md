# Protocolo39 — auditoríaCRPS deCDF21congeladas

**Nueva decisión explícita de raíz: A+Dúnicamente, sin rescatar37. Protocolo previo a implementación/inferencia/scores reales.** Criterios30/25/20/15/10 yno-compensables24/31/35/38 conservados. Los rangos de consejo se solapan, no ganador robusto. Se preserva apoyo condicional de estadística/observación aCdocumental, pero no se ejecuta enparalelo; una sustitución deAdetenido exigiría decisión/protocolo propios,cap45minrevisado ysin tocarD. Babstención no ejecutable sin contrato deacción/coste.

A: cap absoluto **2026-11-15T08:43:00Z–10:13:00Z**,90min TOTALincluidos protocolo,código,tests,fixtures,inferencia yrevisión independiente. Checkpoint **09:03:00Z** antes de nuevos scores: reconstrucciónCDF21/roster eidentidadesB/mediana/media ydosoráculos sintéticos auditables;fallo→STOP/parcial,sin sustituirCDF/refit/scoring37. Sinreinicio. D:60min protegidos **10:13–11:13UTC**;11:13–11:30 sólo contingencia/auditoría/entrega, no nuevosrecursos. Un cierre tempranoA no obliga agotarcap;Dconserva almenos30min finales deconsolidación efectiva.

## Pregunta, estimando y población

¿LaCDFmarginalF21 original aporta menorCRPS que unforecast degenerado en elbaselineB sobre deteccionesSNP registradas de21? Primaria=**media igualpeso de los cuatro contrastesheld `CRPS(F21)−|B−Y|`**, mismasfilas/target/contrato/máscara6 de21. Menor esmejor. NoMAE nueva familia ni mejora deG;G es decisiónpuntual, noCDFreconciliada. NoδG, distribuciónresidual alrededorB/G, CDF37 o E11vsparentheld como brazoidéntico.

Únicosdosforecasts: **F21 originalE11κ10** y **δB**. EnheldE11 yE00parent son idénticos: verificarlo como identidad diagnóstica, no comparación informativa. Nofit, recalibración, solver,reconciliación,nuevasfuentes/máscaras/κ/targets oacquisiciones científicas. No reabrir presupuestosL2.35/37primarios negativos intactos;33nominal no suministra verdad física o coeficientes.

Cuatro modelosSOURCE-only congelados21:08_forward,08_backward,16_forward,16_backward; mismosCUT54/mes,mismasfuentes/regiones/temporadasorigen/destino,10368filas expandidas21. `g` es calendario, no región. Panel/máscara6pre2012/roles/published14/remaining40 fijos. Ya son fechas/desarrolloadaptativo consultados, noholdoutfresco; sinICIID,bootstrap,p-value oclaims de significación. No seleccionar regiones/años/subgrupos que rescaten primariaadversa.

## Entradas y reconstrucción sin targets

Antes de inferencia real congelar porSHA código/tests/protocolo/cap/modelos21 ymanifests/features/controles; registrar **entorno/versiones en elfreeze delPRODUCTOR**, conPython,plataforma,NumPy/Pandas/PyArrow ydependencias realmenteusadas. No repetir omisión37 ni presentar metadatos tardíos como snapshot contemporáneo.

Leer delParquet21 únicamente keys/regime/roles/features `[cut,season,m,g,aqua]` ycontrolesB,E11,E11_mean paraidentidades, **sinY**. Modelos se restauran sinfit; features yB deben coincidir porhash/claves/valores con21. ReconstruirB de coeficientes/políticaoriginal ymediana/media deF21. No ejecutarfit21 odriver que vuelva areconciliarG. Verificar10368keys,54CUTpormes/regime yrolterritorialcongelado.

ReconstruirF21 usando `atom_distribution`original21 orepresentación equivalente verificada: `_components`RAWZ,p/pesos originales yescalaquery`1+r_g*Aqua`; aplicar **sólo a átomos positivos** `max(1,scale*Z)`, preservando masa0. No redondear los átomos no enteros ni trasladarZflooreado a otroquery. No cambiar los ratios, priors,fallbacks,zero-mass oconvenciones de mediana. Exportar átomos/pesos originales ynormalizados,metadata/owners dequery,firma/modelo,mediana/media eidentidadesB/21 para auditoría.

**Segundo freeze obligatorio:** todaslasCDF porquery,rosters,features,controlesB,predicciones/medianas/medias ysus hashes antes delprimerjoin deY paraevaluación. Registrar hora/hash. Luego unirSNP21 conkeys yscopeexactos; duplicados de respuesta deunmismoKEY en diferentesregímenes deben coincidir exactamente, sinpromedio; identidad falsa bloqueascores. NingúnY entra areconstrucción,validación deweights,selecciónCDF oforecast. LosYusados enfixtures son analíticos sintéticos, no respuestasreales.

## Pesos, atoms y tolerancias fijadas

Validar porforecast: arraysigualshape,soporte no vacío,atoms/pesosfinito,weights≥0 estrictamente (ningúnpeso negativo seclampa), suma positiva y `abs(fsum(weights)−1)≤1e−12`. Si falla,gatefalse; no repararunadistribución distinta. Sólo traspasar, normalizar **una vez** cadaweightdividiendo por `math.fsum(weights)` como correcciónnumérica, conservarrawsum/rawweights. No cambiaratoms,redondear aenteros,eliminarceros/duplicadoso hacer ensemblecorrection. Ordenarestable poratom para elalgoritmo; duplicados ypesos0 permanecen representados.

EabsX=`fsum(w_i*abs(x_i))` conpesosnormalizados. Toleranciadeoráculos/δyroundoff `τ=1e−10*max(1,abs(y),EabsX)`. ResultadoCRPSnegativo en[−τ,0) seclampa0, registrar valor crudo,τyflag; menorque−τ→gatefail. No clampingpositivo ni silencioso. Conservar resultadoscrudos para revisión. Comparacionesdelta/oráculos usan absdifference≤τ; identidadesCDF/controls usan toleranciasoriginales21dondecorresponde, sin ampliar según caso.

## PérdidaCRPS y dos algoritmos independientes

Convención: **pérdida no negativa, menor es mejor**. ParaCDFfinita emitida:

`CRPS(F,y)=Σ_i w_i|x_i−y| − 0.5Σ_iΣ_j w_iw_j|x_i−x_j|`.

No correcciónfair-ensemble: estosátomos/pesos son la distribución emitida, no una muestraIID de unaCDFlatente. No cambiarfactor por número deátomos;masas0/empatesnofactoresadicionales.

Productor: ordenarstableatoms,incluidosties,computar primer término con `fsum`; segundo término semidiferencia medianteprefijosponderados:

`Wprev_i=Σ_(j<i)w_j`, `Sprev_i=Σ_(j<i)w_j*x_j`, `half_pair_term=Σ_i w_i*(x_i*Wprev_i−Sprev_i)`.

Usar sumaestable `fsum` para agregaciones yconstrucción de prefijos (acumulacióncompensada/expansión verificable o`fsum`de términos previos), sin materializar una matrizN×N para cadaforecast. Al finalrestar losdostérminos con sumaestable; guardarEabs yhalf_pair para controles. Duplicados contribuyen distancia0,de forma natural. No cálculo enespacioRAWZsinvolver a escalaquery.

Revisor independiente: integrar directamente `[F(z)−1{y≤z}]²` porintervalos entre `sorted(unique(atoms∪{y}))`;en cada intervalo utilizar laCDFconstante yelindicadorcorrespondiente. Fuera de esosknots la contribuciónes0; knots deanchura0noaportan. Algoritmo/oráculo no puede llamarCRPSdelproductor,prefijos oreescalar resultados;pesos/atoms iguales yotrocamino de cálculo. Sobrefixtures además puede comprobarse la doble-suma exacta rational oanalítica, sin convertirlo enotroforecast.

## Fixtures ycheckpoint antes de pérdida real

Antes de scoresdelpanel, ambosalgoritmos deben concordar con expectativasanalíticas:

- δ_b paravariosb/y,incluidos0,y=b,yfuera soporte:CRPS=`abs(b−y)`.
- Dosátomos depesosracionales,ytantoenátomos comoentremedios/fuera:expectativaanalíticaexhaustiva,rawvsnormalizado dentro1e−12.
- Empates,masas0,todosátomosiguales,mezclamasa0/positivos,soportenoentero yfloor1; invariancia aorden ypartirunamasa enátomosidénticos.
- Rechazarweightsnegativos/no finitos/suma fuera1e−12,empty/supportshapeincorrecta;probar clampingnegativo sóloentolerancia yfail fuera.
- CDF21restaurada: probmasa0,mediana inferior,mediaE11_mean yBde21idénticosdentro toleranciasoriginales. HeldE11=parent verificadodirectamentesobreCDF, sin nuevobrazo.
- Eliminar/cambiar targets no cambiaCDFlists/weights/rosters/B; no columnasYenAPIforecast. FixturedeCRPS sóloYsyntético.

Checkpoint09:03UTC exige controlB/mediana/media,rosters/CDF21 yfixtures/oráculos auditables; no basta testsdeproducto sinoráculo independiente. Si no estálisto,entregabloqueadoconfuentes/alcance, sinempezarpérdidasnuevas,refit o alternativa. Gates posteriores depoblación/weights también bloquean antes de concluir.

## Reportes fijados después deljoin de evaluación

Primariaigual4heldcontrastF21−δB,conlos4valores. Agregadofilaponderado secundario,nunca sustituye primaria. δBscore debe reproducirabs(B−Y) puntoapunto conτ; mediaδBcoincide conMAEBdelmismocontrato. No sumar mejorasMAE/CRPS de estudios distintos.

Reportarúnicamentedosforecasts para todaspoblaciones21:54,SOURCE,held,14/40 e intersecciones,cerosY=0,positivosY>0,Aqua0/Y>0,ambos0,extremosfijosY≥50. N,suma/mediaCRPS,diferencias ytodosCUT por régimen;pesos/source soportes/fallbacks tambiénvisibles. PeorCUTheldfijo porcontrolB original(absB−Y),desempateCUT,definido en fasedeevaluación sinafectarCDF/predicciones; no cambiar al peorsegúnresultado nuevo. TablaCUTcompletaimpideocultarcostes. Denominadores/filtros se fijanantes de resultados, noexpulsarforecasts conpesosfallidos para mejorar.

Unpromediofavorable **sólo** indica menorCRPSdeF21frenteδBenestedesarrollo retrospectivo. CRPS combina localización ydispersión: no aisla “valor de incertidumbre” nirelevancia adicionaldeAqua. Tampoco certificacalibración,probabilidadfísica deincendio,coherenciaconjunta54/generalizaciónfresca ni distribuciónalrededorG. Mezcladedirecciones/guardrails permiteconclusióncondicional, no dominancia. Resultadoadverso no invalida matemáticamenteCDFni todauncertidumbre; indica queestareferencia no fue superada aquí. Norescata37/35/23ni cambiaM1/gates/producción/G1/30B.

## Recursos, fuentes y cierre

**0fits,0reconcile/solvers,0nuevasadquisicionescientíficas.**≤1Mfilasexportadas,≤100MiBsalidafísica,peakRSS≤2GiBconunidadesplataforma; contador0explícito yentornoalfreeze. Unproductor yotrorevisor;freeze delrevisorseparado, todosoriginales/modelos21protegidos yhashesfinalesiguales. Runsno sobrescriben evidenciaexistente. A10:13 cierra conreviewcompletaoentregaparcial,sinconclusióncomparativa si no auditable.

Fuente deimplementación primaria **consultada por raíz**: `https://github.com/properscoring/properscoring/blob/master/properscoring/_crps.py`. Las fórmulas anteriores se especifican analíticamente aquí; no se ejecuta ni importa esa librería como oráculo. Referencia conceptual2007DOI`10.1198/016214506000001437`: elfetch de texto falló por timeoutPDF/403publisher; **no se afirma haber leído esepaper** ni derivar de él citas textuales. La revisión usa identidadmatemática integral↔esperanzasyfixtures, no prestigio bibliográfico como sustituto de controles.

Salidas: protocolo/cap,freeze productor conentorno/code/tests/inputs;CDFs/rosters/controles/preYfreeze;fixtures/oraclechecks/weights/roundoff;reportescompletosytablaCUT;recursos/hashpreviousunchanged;reviewindependiente conoráculopropio. Dconsolida18gananciaasignación,21transportelímites,23/35/37negativos,24Csensibilidady33nominalsin verdadfísica,además39condicional. Losúltimos30minDse reservanaconsolidaciónreal, nootrafamilia. Cqueda diferida adecisiónseparada,no paralelismo ni nuevosbytes automáticos.
