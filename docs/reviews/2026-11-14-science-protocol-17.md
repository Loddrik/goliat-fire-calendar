# Protocolo 17 — distribución de dos partes y factorial de ganancias marginales

Fijado antes de scoring, sin esperar ni adaptar su clase al resultado16. Usa detecciónS-NPP registrada, no oportunidad física ni fuego verdadero. Datos/particiones/controles y ventana UTC03 son los del protocolo16; M1/14publicados permanecen congelados.

## Distribución y pooling predefinidos

PadreP=(g,estadoAqua0/>0), localL=(cut,g,estado). Escala s(A)=1+r_g*A, conr_g aprendido en origen. Positivosz=Y/s(A). RegionalpP=(mP+0.5)/(nP+1); pL=(mL+κpP)/(nL+κ). F+P esCDF empírica positiva; F+L mezcla sus positivos locales con masaκpP del padre: [ΣlocalPosI(z_i≤z)+κpP F+P]/(mL+κpP). Padre incluye local como shrinkage empírico: no se anuncia posterior independiente ni probabilidad calibrada.

κ∈{3,10,30}. Si un padre no tiene observaciones, usar todoelentrenamiento como padre y registrar fallback. Si no tiene positivos, usarCDFpositiva global de origen. Si no hay ningún positivo global, distribución degenerada0conprobabilidadpositiva0. Un local vacío usa su padre. Ninguna rama mira etiquetas futuras. Todo residual conserva su escala de origen.

Predicción MAE:0si p≤.5; sip>.5, max(1,s*Q+((p−.5)/p)). Cuantil ponderado inferior, sin interpolación. La cantidad positiva tiene mínimo1celda-día; no se confunde p×mediapositiva con mediana. Este hurdle factoriza unaCDFconjunta: la factorización no añade información ni cambia cuantiles; se comprobará identidad con laCDFdirecta equivalente.

## Factorial primario, κ10 fijo

Cuatro métodos00=(pP,F+P),10=(pL,F+P),01=(pP,F+L),11=(pL,F+L). Mantenerκ10 y mismo marco de predicciones/máscaras para atribuir diferencias descriptivas a estos componentes. Registrar L00,L10,L01,L11 en misma población; ΔP=L10−L00,ΔF=L01−L00,I=L11−L10−L01+L00. Inegativo indica sinergia en pérdida de esa evaluación, no causalidad física. No sumar porcentajes ni comparar distintosκ para atribuir interacción.

Secundaria de selección: candidatos11κ3/10/30, mayorκenempate; comparar mejor conB interno seleccionado y usar solo si mejora>1%, conservandoBsi no. Su resultado describe el paquete de selección; no sustituye factorial fijo ni se usa para atribuir componentes. No añadirZencima como si fuera ganancia independiente.

## Evaluación y límites

Mismos ochofolds anidados64fits, controlesM1/B exactos1e-10, estratos y cuatrocasos temporales delprotocolo16. ComparadoresM1,B yB/P guardado. MAE primaria; sesgo,suma/errorregional y extremos obligatorios. Una suma de medianas no estima la media de la suma: mejoraMAE no autoriza cambiar el calendario agregado.

Brier de I(Yref>0) y calibración en5bins fijos[0,.2,.4,.6,.8,1] para probabilidades regional/local deκ10; diagnósticos, no probabilidad física ni selección alternativa. Bootstrap por temporadas exploratorio. Congelar modelo completoantesdereutilizar2020+; informaciónobservacional faltante sigue faltando. No llamar nuevo holdout a datos ya consultados.

Pruebas: mediana de mezcla vs enumeración del riesgo absoluto, punto p=.5, todosceros/positivos, gruposvacíos/fallbacks, cuantil con masas repetidas, identidadCDFdirecta, exclusión temporal, invariancia a etiquetas futuras ausentes/NaN/cambiadas y orden de filas. Proteger artefactos previos; salidas nuevas solo `data/processed/hurdle_audit/`. Resultados y tradeoffs pueden abrirPRincremental a dev; sinpromoción automática.
