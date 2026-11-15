# Protocolo 23 — compartir distribuciones mediante contexto externo retrospectivo

Congeladoantesdeajustes/score23. Adoptardiseño `2026-11-15-context-cdf-design.md` ycaracterísticas22(conrevisiónindependiente). Pregunta:¿ponderarSOURCEporsimilituddecomposiciónterritorialmejoralaCDFfrenteamismafamiliauniformeencold-regions21? No prueba mecanismoecológico,validación física,forecastas-of2012ninuevoholdout. MapasMCD12Q1nominalesreprocesados2022/HMMpuedenusarposterior;soncontextoretrospectivoexterno, noSNPheldenajuste.

## Datos, variantes y objetivo fijos

Cuatroregímenes21(SOURCE08/16×origenprimera/últimamitad2012–2019),54destinosantesfiltrar,6maskMODISUTCpre2012 ymapahereditadosSINcambiar. TresINPUTSCENARIOSsolamente:PRIMARYalltypes+2010legacyQCretained;SECONDARYalltypes+2001legacyQCretained;SECONDARYtype0+2010legacyQCretained. No2001×type0,noDPA/QC0scores,noseelegiráaño/unidadfavorable. Paraalltypes controlesfrozen21,paratipo0filtrarenAMBOScountsAqua/SNPtype==0desde detectionsANTESdedup sat/celda/día,mismamáscara6 ycalendario;typenulo noes0niconfirmaciónvegetación. Tipo0requierebaseSOURCE-onlypropia(rconst/r_g/Z/B/CDF),noequivalenciaobligadacon21alltype.

Primaria23:ΔMAEheldC11−C00antescoherenciaenPRIMARY,4contrastesypromedioIGUAL4;reportarpoolingporfilaademás. Gananciarelativaprincipal=(promedio4L00−promedio4L11)/promedio4L00,no sumarporcentajesni promediarporcentajesimplícitamente. >1%reglademargen detrabajo,noNASA/significancia. NoatribuirmejoracontextoaC11−E00cuandoSOURCEtienelocales: C00=E11κ10de21en54,heldC00=E00porfallback. ComparartambiénM1/B ycoherentesoriginales,source/held×14/40,activos/ceros/Aqua0SNPpositivo/≥50,sesgo,MSE,Brierprobabilidadproducto,métricasregionales;4regímenesdependientes,noCIIIDniselecciónporwinner.

## Contexto y kernel fijados

Vector18:17fraccionesIGBP+unknown sobreáreatotalpolígono,22retained;no3featuresrenormalizadas. Admitirsoloredondeonuméricodecierre:siabs(sum−1)≤1e−8yclasesen[−1e−12,1+1e−12],recortarroundoffal[0,1]ynormalizarTODOvectorporΣ;si fuera,invalid_input. NoestimarscalercombinandoSOURCE/held. Usarcontext_available95%de22;desconocidosseconservannorecodificadosavector0.

H²(p,q)=.5Σ(√p_i−√q_i)²,K=exp(−H²/(2h²)); h=.25,α=.5,κlocal=10FIJOS. Kernelpositivo≥exp(−8)paraSIMPLEXnosignificasoporteestadístico/ecológico. No thresholdOODni selecciónh/α. ReportarminH,ESSCUT/observaciones,máximopeso,fallbacksCOMODIAGNÓSTICO,nointervaloposteriorBayes. αpreservamitadglobal.

ParaquerycontextoconocidoypoolSOURCEg,stateconN=nP=Σ_c n_c:K_c0siSOURCEcontextunknown;Z_K=ΣK_cn_c. SiZ_K>0,w_c=(1−α)+α*K_c*N/Z_K;Σw_cn_c=N. QueryunknownoZ_K0→w_c=1 ENESEPOOL,conrazón(noconcluirOOD). MediauniformeporCUTNOequivaleuniformeporobservacióncuandonnAqua0/>0difiere;normalizarsobreNdelpoolnoNsCUT. Pparent=(Σw_cm_c+.5)/(N+1);masa/countsse usan como suavizadoempírico,no inferenciaBayesconNindependientes.

Fparent+usaátomosZ=Y/(1+r_g A)guardadosporCUT/g/stateconpesow_cporátomo;norecalcularr_gporcontexto. Si poolsinobservaciones,usarGLOBALsourceconreglaNglobal. Si poolobservadopero m0,pgrupoquedasuavizadoenpoolyF+fallbackGLOBALconpesosRECALCULADOSconn_cGLOBAL ANTESposiblesm;no normalizarpornúmerodepositivosnireusarwgrupo. Queryconocidopuede pgrupo fallbackuniforme yFglobalcontextual;queryunknown→uniformetodospools. Si fuenteGLOBALsinpositivos→distribucióndegenerada0como21.

LocalesSOURCE(n,m,Z+)conκ10mismos21,paracandidatocontextual pL=(mL+κpParent)/(nL+κ);si nL0→padreexacto;F+localusaátomoslocalespeso1+priorκpParentFparent. ParentincluyelocalSOURCE,comopoolingempírico21,no datosindependientes. Heldno localnolecturadey. rconst/r_g/escalaZ yBcongeladosporunidad,source×originsolo;λB4existentesselecciónOOFsource(siunitalltypesreusar21,sitipo0repetirpolítica),ningunagrillanueva.

## Factorial y decisiones

Calcular(p0,F0)uniforme y(p1,F1)contextualCOMPLETOS antesfactores;F1incluyeκpParentcontextual. C00=(p0,F0),C10=(p1,F0),C01=(p0,F1),C11=(p1,F1). NoreconstruirF1cambiandopsegúnfactor;atribuciónFespaquetedistribuciónpositiva,noefectocausalindependiente. ReportarL11−L10−L01+L00enmismafila/población,sin sumarrelativesgains. CDFoutputmass1−pen0,positivosmax(1,(1+r_gA)*Z),medianaslowerquantile;noglobalindex0–100.

Secundarias:coherenciaL1C11ysucontrolC00,ambosconΣBmensual54+tieEuclideanaB;C11proporcionalcontrol(ΣC11med0→B). IgualdadregionalconBconstruida,no nuevahabilidadtotal;subgruposno conservados. Todosescenarios/métodosseexportan,aunpeores;ningunapromoción porganancianetaoculta14/cero/extremos.

## Pruebas e integridad

PRIMARYalltypesC00CDF/pred/B/coherenciareproduce21tolerancia1e−10;2001alltypesC00tambiénigual(noctxencontrol). Tipo0C00reproduceuniformebaseSOURCE-onlypropia. KernelconstanteyTODOSsourceconmasaAVAILABLEeidénticos(queryincluido)→C11=C00;conSOURCEunknownnosigueesaidentidad,probarseparado. α0/queryunknown→uniforme;componentesCDFnormalizados,ties,fallbackporpool,missing/no-globalpositive. Invariancia parámetros/54pred almodificar/reemplazarNaNSNPheld/destinos;featuremetadataexternopermitido,noseaprendenormalizaciónusandodistribuciónheld. Controlreconcile54ypropiedadesCDFrisk≤B,no garantíaerrorobservado.

Outputsnuevos `data/processed/context_cdf_audit/`,code/tests/review23,modelos/params/choices/contextdiagnostics/manifiestosconinputs22/21/base/protocolosyhelperssha. NoleerHDFrawparaSNPfitsninuevadescarga,protegerbase/publicación/estudiospreviosincl22. Resultadonegativoesinformación;si<1%omejoraunrégimen,consejocomparaotraunidad/covariable/observaciónantesdegrillasadicionales. Deadline11:30UTCdel15nov2026.
