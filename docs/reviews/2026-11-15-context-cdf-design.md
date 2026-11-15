# Diseño 23 — contexto externo para una CDF empírica transportable

**El diseño es matemáticamente coherente si conserva la medida por observación, los suficientes de 21 y los componentes completos antes del factorial.** Permite probar una política concreta de compartir información por cobertura terrestre retrospectiva; no identifica mecanismos ecológicos ni produce una probabilidad física de incendio. Este documento no ejecuta modelos, ajuste, extracción adicional ni scores.

## Contrato y control que deben quedar inequívocos

Primaria propuesta: las cuatro combinaciones SOURCE/región×origen/destino de 21, todas las filas destino y la misma máscara 6. Se conservan coeficientes, selección B, r_const, r_g yZ de los modelos all-type congelados de 21. No se recalculan normalizaciones según la consulta, el contexto o el destino.

El contexto primario es 2010/legacy/retained de 22, con sus 18 componentes (clases 17+unknown), disponibilidad ≥95% y geometría completa. Las proporciones deben ser finitas, no negativas y sumar 1 dentro del error numérico declarado de 22. Solo entonces se divide por su suma para corregir cierre; no se recortan masas negativas ni se normalizan únicamente bosque/cultivo/urbano. La disponibilidad utiliza el indicador congelado, no se inventa después de normalizar. Datos corruptos o filas esperadas ausentes no se convierten silenciosamente en “contexto desconocido”.

**C00 debe reproducir E11 κ10 de 21 en los 54 CUT**, incluidas sus distribuciones locales SOURCE. En held, E11 de 21 coincide con E00 por fallback; por eso también reproduce el padre allí. No debe definirse C00 como un promedio de CDF condicionales por CUT: eso cambiaría la representación y la ponderación originales.

La reproducción debe abarcar suficientes, p, CDF completa canónica, medianas, medias y controles de asignación, con las tolerancias previas declaradas. La ruta uniforme puede delegar al helper 21 original para evitar diferencias de orden/suma. Si no reproduce, se detiene antes de nuevos scores; no se fuerza identidad modificando datos.

## 1. Medida parental y pesos

Para un grupoP=(g,estado Aqua), cada CUT fuente aporta n_c observaciones, m_c positivas y sus átomosZ positivos. n_P=Σn_c; el estado Aqua cambia los tamaños n_c entre comunas. El predictor conserva el reescalamiento 21, Y=max(1,(1+r_gA)Z) en la parte positiva.

Con q,p_c como composiciones de consulta y CUT fuente, respectivamente:

`H²(q,p_c) = 0.5 Σ_j (sqrt(q_j)−sqrt(p_cj))²`

`K_c = exp(−H²/(2×0.25²))`

`D_P = Σ_c K_c n_c`

Si consulta disponible y D_P>0:

`w_c = (1−0.5) + 0.5 × K_c n_P / D_P`

Un SOURCE desconocido tiene K_c=0 y mantiene w_c=0.5: participa en la mitad global, sin recibir masa de semejanza. Consulta desconocida o D_P=0 activa w_c=1 para todo el pool, con motivo explícito.

Esto preserva Σw_c n_c=n_P. **Normalizar por la media no ponderada de K entre CUT sería incorrecto para reproducir21**: con n_c distintos cambia el tamaño ponderado, el centrado y la fuerza del pseudoconteo. Una medida igual por comuna sería otra hipótesis y requeriría otro control, no sustituir este denominador.

La probabilidad regularizada queda:

`p_P(contexto) = (Σ_c w_c m_c + 0.5)/(n_P+1)`

La CDF positiva asigna peso w_c a cada átomo positivo de ese CUT y normaliza por Σw_c m_c. No se usa w_c/m_c ni una media no ponderada de CDF por comuna. Así se mantiene la medida de registros positivos condicionada al pool ponderado.

El ancho Hellinger0.25 y α=0.5 son constantes de una política de shrinkage empírico, no parámetros estimados ni hiperparámetros seleccionados con destinos. El denominador Jeffreys n_P+1 se conserva como regularización empírica del control. Con pesos de semejanza no corresponde automáticamente a una posterior Beta-binomial de muestras independientes. No se derivan intervalos bayesianos de n_P.

## 2. Fallbacks antes de construir componentes

Aplicar una jerarquía fija usando exclusivamente los suficientes SOURCE:

1. **Pool g/estado sin observaciones:** sustituirlo por el pool global de observaciones SOURCE. Recalcular n_c,m_c y pesos de ese pool global para p yF+.
2. **Pool g/estado con observaciones pero sin positivos:** mantener su p regularizada; para F+ usar los positivos globales SOURCE. Los pesos contextuales se construyen con los n_c del pool global completo, antes de seleccionar positivos; no se reutilizan pesos del grupo vacío de positivos ni se normaliza por m_c.
3. **Ningún positivo en el entrenamiento SOURCE global:** distribución degenerada en 0 y p=0, reproduciendo el control21. No dejar el pseudoconteo 0.5 crear actividad sin soporte positivo global.
4. **Consulta desconocida:** pesos uniformes en todos los pools. **Consulta conocida pero sin SOURCE conocido con n_c>0 en un pool:** pesos uniformes para ese pool. Conservar filas y banderas, sin excluir territorios difíciles. Si el grupo sin positivos carece de masaK pero el pool global sí dispone de ella, p conserva la ruta uniforme del grupo y F+ global puede seguir contextual; no se fuerza retrospectivamente todo el par a uniforme.

Los suficientes locales por CUT/g/estado permiten reconstruir el pool global concatenandoZ con su procedencia CUT. El array global ordenado de positivos por sí solo pierde esa procedencia: no basta para asignar pesos contextuales. La unión de los locales debe reproducir n_global, m_global y la CDF global almacenada antes de usarla.

No hay soporte estadístico “verificado” porque D_P>0. H² está entre 0 y 1 y este kernel es positivo incluso a distancia máxima (K≥e⁻⁸). El fallback por D_P=0 detecta ausencia de contexto utilizable, no extrapolación fuera del soporte de SOURCE. La mitad global limita concentración, pero no certifica transportabilidad.

## 3. Dos pares completos y factorial de decisiones

Primero construir el par uniforme parental y el contextual, cada uno con su p yF+. Para CUT con datos locales, aplicar la misma regla κ10 de 21:

`p_L = (m_L + 10 p_P)/(n_L+10)`

`F_L+ ∝ átomos locales con peso 1 + prior F_P+ con masa 10 p_P`

Sin datos locales, usar exactamente el padre. Sin positivos locales, la CDF condicional queda igual al padre, evitando cancelaciones numéricas. El propio CUT SOURCE puede formar parte de su padre como en 21: esto es pooling empírico, no una posterior con prior independiente ni una nueva evidencia independiente sobre SOURCE.

Después de completar ambas rutas se congelan los pares (p0,F0+) y (p1,F1+). El factorial es:

| Decisión | Probabilidad final | CDF condicional positiva final |
|---|---|---|
|C00|p0|F0+|
|C10|p1|F0+|
|C01|p0|F1+|
|C11|p1|F1+|

No se reconstruye F1 al cambiar la probabilidad final en C01/C11. De otro modo, la celda01 y la11 no compartirían el mismo componente y el factorial perdería su definición.

La interpretación debe conservar un matiz: F1 local incorpora tanto los nuevos pesos positivos como el cambio de masa del prior 10p_P contextual. Por tanto, el “factor F” representa ese componente completo; no aísla únicamente la forma de la CDF parental ni una causa física de intensidad. El “factor P” cambia la masa binaria final manteniendo el otro componente completado.

Para pérdida L sobre idénticas filas, los contrastes son ΔP=L10−L00, ΔF=L01−L00 e I=L11−L10−L01+L00. Se suman en unidades de pérdida como Δjoint=ΔP+ΔF+I; no se suman porcentajes frente a diferentes baselines ni mejoras de experimentos anteriores. Una interacción de pérdida no demuestra sinergia causal.

## 4. Identidades y diagnósticos de concentración

Exigir antes de puntuar:

- Pesos 1 reproducen21 completo; α=0 reproduce también el control.
- Contextos idénticos de **consulta y todos los SOURCE con masa, disponibles** dan C11=C00. Si hay SOURCE desconocidos, K=0 reduce su peso a0.5 y la igualdad no se sigue aunque los conocidos sean idénticos entre sí.
- Consulta desconocida activa identidad uniforme, sin pérdida de filas.
- Los pesos, probabilidades y átomos no cambian al borrar/modificar todas las etiquetas fuera de SOURCE×origen. Las covariables held se usan en inferencia, no en ajuste o selección.
- Fuente propia incluida conserva la semántica empírica; su beneficio no se presenta como transferencia a un CUT sin datos locales.

Diagnósticos predefinidos por consulta/pool: n_P, número de CUT con masa y contexto, H² mínimo, K medio ponderado por n_c, masa por CUT, peso máximo y motivos de fallback. No se añaden umbrales de exclusión después de ver resultados.

Dos ESS descriptivos distintos ayudan a no confundir registros con territorios:

`ESS_observaciones = (Σ w_c n_c)² / Σ n_c w_c²`

`ESS_CUT = (Σ w_c n_c)² / Σ (w_c n_c)²`

El primero supone registros como unidades de ponderación; el segundo refleja concentración entre CUT. Ninguno acredita independencia mensual/espacial, tamaño muestral inferencial o intervalo bayesiano. Deben rotularse como diagnósticos de pesos.

## 5. Evaluación y sensibilidades sin selección posterior

Primaria: ΔMAE held C11−C00 antes de reconciliar, con los cuatro regímenes y promedio con peso igual 4. Reportar también ponderación por fila, sin elegir direcciones ni intervalos IID por comuna-mes. El corpus y los destinos siguen siendo retrospectivos y adaptativos; nuevos pesos no crean un holdout fresco.

Secundarias fijadas: M1/B21, SOURCE/held y sus intersecciones 14/40, Brier de detección S-NPP registrada, ceros/ambos ceros/Aqua=0/SNP positivo/extremos. La mezcla mediana debe calcularse desde su masa en 0+CDF+, no multiplicando p por una mediana positiva. Media exacta y asignaciones coherentes conservan sus objetivos distintos.

CTXcoherent y proporcional usarán ΣB21 de los 54 CUT antes de filtrar grupos. Su igualdad regional global con B es construida. Para interpretar una ventaja contextual tras asignación conviene conservar también la asignación coherente de C00 con el mismo presupuesto: de otro modo se confunden contexto y nueva decisión presupuestaria. No se deriva una distribución conjunta ni independencia entre CUT.

Sensibilidades:

- **2001/legacy/retained:** misma calibración all-type21 y mismos suficientes; cambia solo el descriptor fijo. Mantenerlo separado del primario y no escoger el año con menor error. Los dos productos son reprocesados 2022 con HMM, sin garantía as-of2012.
- **Type0:** filtrar `type==0` en AMBOS conteos Aqua/SNP desde detections ANTES de deduplicar por satélite/celda/día, conservando exactamente la máscara 6. Cambian respuesta y A; se construye una nueva base SOURCE-only con la misma política OOF de cuatro λ y κ10. Su C00 debe reproducir su propia base uniforme type0, no la 21 all-type. Desconocido no equivale a vegetación. Los Parquet canónicos ya hicieron una deduplicación previa por detección/fuente: esta sensibilidad no recupera registros descartados allí.
- **DPA y QC0:** exclusivamente diagnósticos de descriptor de 22; no nuevas puntuaciones de modelos.

Los únicos escenarios con scores serían: PRIMARY2010/legacy/retained/alltypes; SECONDARY2001/legacy/retained/alltypes; SECONDARY2010/legacy/retained/type0. No se cruza 2001×type0 ni se puntúan modelos DPA/QC0. Ningún escenario se selecciona o promueve por MAE.

Antes de ejecutar se deben congelar fingerprints de modelos 21, features 22 y política type0, además de las reglas anteriores. Si falla C00 o cambia alguna población sin motivo registrado, detener y reportar; no reparar el método después para fabricar una mejora. La disponibilidad del descriptor no resuelve G1 de observación ni demuestra soporte ecológico común entre regiones.
