# Diseño36 — adyacencia diaria registrada en la misma celdaAqua

**Diseño consolidado de estadística y observación, no protocolo de ejecución ni cap autorizado.** No se ejecutaron cubos/features/permutaciones, targets, pérdidas, fits o nuevas predicciones para este documento.35A se conserva cerrado y negativo;36 no es un rescate automático ni abre otra grilla de modelos. Raíz decidirá protocolo/branch después dePR57.

## Pregunta y unidad

¿La adyacencia de deteccionesAqua en una misma celda0.01° aporta información predictiva sobre las deteccionesSNP registradas más allá de la misma distribución de actividad con días permutados y delG21congelado? Es persistencia de **detecciones registradas**, no continuidad de un incendio físico, oportunidad útil de observación ni ausencia de fuego cuandoD=0.33 sólo aporta límites de representación/aliasing; no groundtruth, labels históricos físicos o coeficientes.

Dominio único21:54CUT, ocho temporadas2012–2019 de julio a junio, es decirUTC2012-07-01–2020-06-30, incluidos29feb2016 y29feb2020; mismos cuatro regímenesSOURCE/held. Máscara6 pre2012 de21 y su contrato canónico. No máscara223, otra geografía,18/24C, casos nuevos o fechas favorables. PanelAqua fijo5184CUT-meses; expansión por los cuatro regímenes produce10368filas de predicción21. Ninguno esholdoutfresco.

## Fase propuesta1: cubo auditable, sin modelo automático

Cap propuesto45min **incluida revisión independiente**, con checkpoint de identidades a15min; horas reales y recursos deberán congelarse en protocolo propio antes de código/datos. Si a15min no son auditables claves/máscara/reconciliaciónAqua, entregar bloqueado/parcial, sin abrir fits. Finalizar cubo no autoriza modelo: se necesita decisión explícita de raíz después de su auditoría.

Entradas derivadas canónicas existentes y protegidas porhash:celldays/detections,mappingCUT y máscara6/certificados21. Su disponibilidad permite estudiar el historial canónico sin recuperar1071CSV crudos faltantes, pero no restaura reproducibilidad de adquisición completa. Ceros de registros canónicos no prueban archivo raw íntegro, pasadas útiles o cobertura física. Sin nuevas descargas/HDF/QA ni imágenes.

Una incidencia canónicaAqua/celda/fechaUTC, asignada al mismoCUT y filtrada por máscara6. Validar uniqueness y procedencia antes de contar: duplicado exactamente idéntico se reconoce/documenta según contrato canónico; **duplicados conflictivos de clave o asignación fallan**, no escoger registro/fuente para obtener una feature. No cambiar la deduplicación21 ni mezclar tipos/contratos. El cubo deberá reproducirAqua21 exacto porlas5184claves, no sólo totales globales. Faltantes de identidad/procedencia no se rellenan como0.

Para cadaCUT-año-mes crear matriz binaria `X[cell,day]` de detección registrada: columnas para **todos** los días calendario, incluidos días sin registro. Se puede almacenar dispersa con calendario explícito, sin materializar celdas del planeta no presentes en el universo canónico; omitir una celda de ceros no cambiaD ni justifica oportunidad observacional. Celdas sin registros mensuales no generan parejas positivas. No interpretar la matriz como denominador de FOV u observación.

Feature primaria única:

`D=1` si existe celda y día d tal queX[cell,d]=X[cell,d+1]=1, con ambas fechas dentro del **mismo mes calendarioUTC**; enotrocasoD=0 para ese historial registrado. Enero31/febrero1 no cuentan como pareja dentro de ninguno de los dos meses. No agrupar por temporada para formar parejas que atraviesen mes. Gate estructuralD=1⇒Aqua mensual≥2celdas-día. A=0 o1 implicaD=0. No usarSNP para construirD o elegir celda.

Diagnóstico opcional prefijado: cantidad de pares celda-día consecutivos dentro del mes, cada pareja una vez. Sólo diagnóstico, nunca feature adicional escogida tras ver resultados; no ajustar longitud de racha/ventana.

## Placebo único de columnas diarias conjuntas

Mantener el multiconjunto de columnas diarias delCUT-mes y permutarlas conjuntamente para todas las celdas. Incluir columnas cero y29febcuando corresponda. Preserva exactamente conteos porcelda, multiconjunto de conteos diarios, coocurrencia intradía yAqua mensual. No permutar cada celda porseparado, ni sólo días positivos, ni mover entre meses/CUT/SOURCE/destino.

Regla determinista propuesta, a congelar antes de valores: para cada díaDD deYYYYMM calcularSHA256UTF8de`goliat-daily-adjacency-v1|CUT|YYYYMM|DD` (CUT canónico,YYYYMMseisdígitos,DDdosdígitos). Ordenar días por bytesdigest, empate porDD. Definir `rankedDays` por ese orden ascendente; para cada día ORIGEN d=1..L, mover su columna al día DESTINO `rankedDays[d-1]`. Esa dirección origen→destino es literal y fija, no su inversa. Misma permutación para todas las celdas y duplicados de régimen del mismoCUT-mes; registrar mapping/hash de cada bloque. Un único prefijo global; no semilla adaptada por resultados ni algoritmo de shuffle dependiente de librería.

CalcularDplacebo con idéntica regla de pareja dentro del mes sobre esa matriz. **La permutación no garantiza eliminar adyacencias**, cambiarD o destruir toda estructura temporal; puede coincidir con calendario original o conservar parejas por azar. No rereseed, cambiar prefijo o añadir permutaciones porque el contraste tenga poco poder. Una permutación única es control condicional, no distribución de aleatorización, p-value oIC.

Identidades previas: mismos5184keys/calendarios/máscara/Aceldas-día; suma porcelda idéntica; conteos diarios conservados como multiconjunto; columnas/eventos intradía sólo reordenados; mapping de días bijectivo;D/Dplacebo⇒A≥2. Reportar concordanciaDreal/Dplacebo y soporte por grupos sin usar targets; si ambos casi siempre coinciden, limitar poder discriminante, sin inventar después un porcentaje de gate o nueva semilla.

## Fase propuesta2: decisión separada y60min totales

Sólo tras cubo auditado y autorización explícita posterior de raíz. Cap futuro60min **TOTALincluidosfit,tests,implementación yrevisión**, no60minmás30de revisión. Protocolo propio debe fijar horas, recursos, fórmulas, identidades y pérdida antes de targets/modelos. Si no cabe con revisión, cerrar cubo como entrega válida y diferir el modelo. No fit automático al pasar un gate técnico.

Comparar sóloG21 original, modeloDreal y modeloDplacebo. BaselineB,ratios globales/r_g,CDF21 y políticas afines quedan congelados por régimen; ninguna selecciónλ,normalización nueva, cambio de máscara, target o nueva fuerza de regularización. Reconciliación **global54** comoG21;35R/presupuestos regionales permanece cerrado. Los nuevos ajustes usan únicamenteCUTSOURCE×temporadasorigen de cada uno de los cuatro regímenes21;heldSNP ytemporadasdestino nunca entran a fit/fallback/selección.

Featuresheld pueden construirse de suAqua mensual porque se trata de armonización retrospectiva de meses completos, no forecast antes del fin del mes. Permutar un mes completo no habilita afirmar uso operacional sin futuro. Congelarfeatures/modelos/predicciones antes de unir targetsheld para evaluación.

## Distribuciones completas y controles de identidad

Porparent original `(g,s)` cons=1[Aqua>0], usar suCDF21congelada completa `H_P`, probabilidadp_P yCDFpositivaF_P+, con los mismosZnormalizados y r_g originales. `g` es calendario, no región. D=1 es estructuralmente imposible cuandos=0; no extrapolar ese estado como evidencia nueva.

**Fallback indispensable:** el conjunto elegible es exactamente `cut∈model.source_cuts AND season∈model.origin_seasons`. Si `len(uniqueD)` en ese SOURCEparent(g,s) es≤1, incluido vacío, desactivarD para **toda consulta** de ese pool, incluso una combinaciónD no vista. Devolver exactamente `atom_distribution` original21 completa correspondiente a CADAconsultaCUT/g/Aqua, incluidos componentes locales deSOURCE, no sólo laCDFparent ni sólo losheld. No volver a suavizar los mismos registros: pJeffreysoriginal=(m+.5)/(n+1), y(m+10p_P)/(n+10) no coincide necesariamente. Este fallback evita un cambio de pseudo-conteos disfrazado de información temporal. También permite un negativo-control donde feature constante reproduceG21 en54predicciones/allocations exactamente a toleranciaoriginal.

CuandoD sí varía, definir para cada claseD los suficientesSOURCE n_D,m_D yátomos positivosZ; no cambiar la normalización deY ni r_g. Shrinkage fijo **κparent=10** sobre la distribución completa:

`H_D=(n_D*H_emp,D+10*H_P)/(n_D+10)`.

Equivalentemente:

`p_D=(m_D+10*p_P)/(n_D+10)`;

`F_D+=(Σ_positive,D δ_Z +10*p_P*F_P+)/(m_D+10*p_P)`.

Son componentes de la misma mezcla, no una probabilidad yCDFpositiva ajustadas conpesos incompatibles. n_D=0→parent21exacto; masa positiva0→degenerada0; si hacefaltaF+enmasa0mantener fallback original sin asignarle probabilidadpositiva inventada. Parent sinregistros/positivos conserva los fallbacks globales21, con sus reglas y procedencia, no nuevos umbrales. Sharedpool incluye sus propias observacionesSOURCE como21: shrinkage empírico, no posteriorBayesiano ni intervalos de incertidumbre calibrados. No se exige marginalpreserving de toda la mezcla; se declara esta limitación y se verifica especialmente el control de no variación.

ParaCUTSOURCE sólo, construir suficientes **condicionados también porD**, n_cD,m_cD yZ_cD, no reutilizar conteoslocales incondicionales como si fueranD-específicos. **κlocal=10**:

`p_cD=(m_cD+10*p_D)/(n_cD+10)`;

`F_cD+=(Σ_positive,cD δ_Z +10*p_D*F_D+)/(m_cD+10*p_D)`.

n_cD=0→parentcontextual; heldsinlocal→parentcontextual, sin nuevo coeficiente porcomunaheld. Si parentD está desactivado por no variación, se usaCDF21completa original envez de pasar por estas fórmulas. No ajustarκporsoporte/score; reportar n/m y masas prestadas como diagnósticos, no tamaño de muestra independiente o intervalosBayes.

Los dos modelosDreal/Dplacebo siguen exactamente la misma familia/fallbacks; sólo cambiaD construido sin target. Al predecir, transformarátomos positivos con la escala original ysu mínimo positivo original; mediana inferior de mezcla con masa0según21, media sólo si sepredeclara diagnóstico, sin sustituirlas porp×media como mediana. Solver global54,desempate haciaB y tolerancias21iguales.

## Pruebas requeridas antes de pérdidas

- Feature constante porparent→CDF21completa/medianas/54prediccionesG21, incluidoslocalSOURCE yconsultaDno observada; no sólo proximidad de medias.
- Reproducción exacta B/r_g/modelos/máscara/Aqua/panel21; fórmulasmixtas prob/CDF equivalentes, filas vacías/masa0 yfallbacks originales.
- No localheld; SOURCE yorigenaños únicamente en suficientes/modelos; eliminar/cambiar targetsheld yfueraaño de entrenamiento no cambia parámetros o54predicciones.
- n_D=0 y n_cD=0; localD usa sólo filasDcorrespondientes; no variaciónSOURCE no se decide mirandoheldD/Y.
- Hash/modelo/conteos de features reales/placebo independientes deSNP; escenarios de febrero, finmes/cambioaño yceros canónicos como registros, no observabilidad.
- PresupuestoglobalΣB,no negatividad/finitud, KKT/riesgo bajo laCDF **propia** de cada modelo y tolerancias21. Riesgo deCDFdistintas no se compara como si fuera idéntico objetivo.

## Pregunta discriminante y reportes futuros prefijados

Primaria recomendada: media igualpeso de los cuatro contrastesheld `MAE(modeloDreal)−MAE(modeloDplacebo)`. **Obligatorio al lado** `MAE(modeloDreal)−MAE(G21)`, además de todaslasMAE deG/real/placebo/B. No cambiar a agregadofilaponderado o año que mejore. Reportar cuatro regímenes dependientes, sinclaim de significación, noICIID ni nuevoholdout. ConservarSOURCE/held,54/14/40 e intersecciones, cerosY=0,Aqua0/Y>0,ambos0,positivosY>0,extremos fijosY≥50,sesgo,presupuestos ytabla completaCUT/peorCUTfijo sobrecontrolGoriginal.

Interpretación prefijada:

1.Ambos contrastes igualpeso —real−placebo yreal−G— son negativos: evidencia predictiva condicional compatible con información de adyacencia, sin causalidad física ni promoción automática; todos los costes territoriales siguen visibles.
2.Si cualquiera de los dos contrastes no es negativo, no afirmar mejora útil de cronología. Real supera placebo pero empeoraG: sólo contraste relativo entre modelosnuevos; no rescatarlo ocultandoG, cambiando agregación, semilla o grilla.
3.Placebo igual o mejor, oambosmejoran similarmenteG: no adjudicar novedad a orden temporal. D puede ser proxy de cantidad/distribución de detecciones, soporte o cambio de representación, incluso conservando conteos; cerrar esa explicación limitada, no otra semilla.
4.SoporteD insuficiente, casi sin diferenciaDreal/placebo, gates/cap fallidos otradeoffs contradictorios: inconcluso; no añadirdiagnóstico-rasgo,racha,lags o regularización después.

No se promete queDexplique desacuerdo físico, que permutar elimine toda señal temporal ni que el test sea independiente de intensidad. A≥2,Ddependiente de conteos y masas raras quedan explícitos. Un resultado positivo no convierte registro mensual en oportunidad comparable ni resuelve la pregunta original sobre cómo observa cada satélite.

## Cierre de alcance

El cubo y el modelo son decisiones/protocolos separados, cada uno con revisión dentro de su cap. No ejecución, datos, nuevasfeatures o scores autorizados por este diseño. No cambios aproducción, publicación,35Anegativo,30Bfallido oG1físicofalse. Conservar también resultado nulo/negativo y el motivo de detener; no agotar la ventana11:30UTC en rescates iterativos del mismo destino.
