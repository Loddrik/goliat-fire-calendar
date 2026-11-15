# Protocolo36 — integridad de adyacencia diaria registrada y placebo

Autorización explícita de raíz después del cierre independiente negativo35A. No es un rescate de sus resultados. Este intento construye y audita un predictor; **no autoriza ajuste, nuevas pérdidas o modelo posterior**. Diseño consolidado aplicable: `2026-11-15-daily-adjacency-design.md`, SHA256 `56c902ab443d391047838b87de6795c206788b8ce5bbdf9c0fa28c0c04cbebdf`. Sus definiciones y límites forman parte de este protocolo.

Cap absoluto inicio `2026-11-15T07:48:23+00:00`, cierre `2026-11-15T08:33:23+00:00`, incluidos protocolo, implementación, pruebas y revisión independiente. Checkpoint `2026-11-15T08:03:23+00:00`: contrato, máscara6,5184claves y reconciliación mensual Aqua deben estar auditables; fallo→STOP parcial, sin nueva máscara/operador/semilla o reinicio. Hasta1Mfilas exportadas,50MiB de salidas y1GiB peakRSS; reportar unidades/cifras. Sin nuevas descargas, raw/HDF, geometría, solvers, refits, respuestasSNP o producción.

## Universo y entrada cerrada

Sólo derivado canónico `data/processed/celldays.parquet` para registrosAqua; máscara congelada `data/processed/cold_region_audit/candidate_mask.csv` (6celdas) y su manifest; proyección **sin snpp** de `cold_region_audit/predictions.parquet`, columnasregime/cut/season/m/aqua para control. Código previo/protocolo21/manifests/versiones se documentan; freezehash de todos los insumos y código/tests antes de calcularD o permutar fechas. Hash incorrecto/duplicados/incompatibilidadbloquean; no corregir operadores para hacer coincidir.

Temporadas2012–2019 julio–junio, fechasUTC julio2012–junio2020. Derivar año calendario correctamente, incluyendo29feb2016/2020. CUT/índicescelda0,01° existentes sin rebin/remap. Validar identidad única sat/cut/cell_x/cell_y/acq_date y consistencia fecha/season/m. Aplicar máscara6 antes del operador. Las5184claves54CUT×8temporadas×12meses incluyen todos los vacíos registrados. En las10368filas de21, cada clave repetida debe tener exactamente igualAqua, y el recuento canónico reconstruido debe coincidir con **cada fila, tolerancia0**. No promediar duplicados contradictorios.

## Operador y placebo únicos

`D=1` si existe una misma celdaAqua canónica con registros en dos fechasUTC consecutivas, ambas en el mismo mes calendario. Conteo diagnóstico prefijado: número de pares celda-día consecutivos; no se seleccionará después como otrafeature. Una celda-día cuenta una vez aunque n_det>1. No pares entre meses, años otemporadas. `Aqua<=1⇒D=0`; D0 no significa ausencia física, observación útil ni adquisición completa.

Fullcalendar deL días reales porCUT/YYYYMM, incluidas columnas sin registros. Para cada díaDD2 calcular SHA256UTF8 del literal `goliat-daily-adjacency-v1|`+CUT+`|`+YYYYMM+`|`+DD2. Ordenar días por digestbytes ascendente y desempatar por día. Para ORIGINdayd, DESTday=`rankedDays[d-1]`. Aplicar la misma permutación a todas las celdas delCUT/mes y todas las repeticiones de régimen. Representación sparse permitida sólo si equivale al calendario completo; nunca permutar sólo fechas activas ni una permutación distinta por celda.

Conservar exactamente conteo mensual de registros por celda, multiset de conjuntos de celdas activas por día (incluidos conjuntos vacíos), distribución de conteos diarios y coocurrencia intradía. La permutación puede preservar adyacencias/D; **no se exige destruirlas y no se repite la semilla**. Sin interpretación de causalidad o test aleatorio/IC. Fechas ausentes del derivado congelado se denominan cero registros del contrato, no oportunidadfísica0; originales locales faltantes no se completan ni se presume reproducción íntegra de adquisición.

## Entrega y controles

Helperspuros con tests de misma celda vs otra celda, año bisiesto, límites mes/temporada, D0cuandoA<=1, calendarios vacíos y placebo fullcalendar estable. Driver confreeze antes de features, no overwrite, contadores de filas/bytes/RSS/UTC y conservación de hashes previos. Publicar todas las5184filas conAqua,Dreal,Dplacebo,paresreal/paresplacebo,claves; permutaciones y soporte/registros suficientes para auditoría independiente sin respuestasSNP. Describir prevalencia ydiscordanciaD porg/A>0 y porregímenesSOURCE/held, sin seleccionar población/semilla/modelo a partir de ellas. Integridad no exige variación o señal; constante/idéntico alplacebo es resultado válido e informativamente limitado.

Revisor independiente verifica contrato/reconciliación de todas las filas, D medianteotroalgoritmo, permutación porhash e invariantes completas, dominios/superficies nativas no aplicables y que no se leyeron respuestas/estimaron pérdidas. Evidencia del revisor separada; no modificar manifiesto/productor para ocultar fallos. Revisión incompleta alcap→parcial sin interpretación predictiva.

## Propósito posterior, sin autorización de modelo

Pregunta futura congelada: si adyacencia registrada aporta diferencia predictiva frente al placebo y mejora frente aG21, sobre los mismos cuatroheld con igualpeso. Primariafutura MAE(realD)−MAE(placeboD), contraste obligatorio MAE(realD)−MAE(G21); ambosnegativos sólo apoyarían evidencia predictiva condicional, nunca verdad/observabilidad o holdoutfresco. Modelo necesita otroprotocolo explícito con60minTOTALinclrevisión, parent/localκ10 fijos, B/r_g/G congelados y SOURCE-only. SOURCEpool(g,A>0)sinvariaciónD(inclvacío)debe devolverCDF21 COMPLETA exacta paraTODOqueryCUTincllocal, sinresuavizarJeffreys. Con soporte variable, SOURCElocal condicionadaD yparentcontextual coherentes; ese detalle se revisa antes de autorizar ajuste. Nada del cubo autoriza automáticamente esa etapa.

35Anegativo sigue cerrado;33no aporta etiquetas/QA como covariables históricas. M1,14gates,publicación,G1y30B no cambian. Reservar al menos30min reales finales de consolidación hasta11:30UTC del objetivo vigente.
