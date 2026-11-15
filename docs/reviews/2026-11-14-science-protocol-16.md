# Protocolo 16 — ganancia marginal de anclar Aqua=0 sin cambiar cantidad positiva

Fijado antes de medir nuevos scores. Base22acc26, ventana autorizada hasta2026-11-15T03:00Z (domingo00:00Santiago). Objetivo es discrepancia frente a detección registrada S-NPP; Aqua=0 no significa ausencia física ni oportunidad observacional conocida. No cambiar publicaciónM1/14 ni datosbase.

## Comparación primaria aislada

Reproducir selección M1/B y sus cuatroλ(.01,.1,1,10), con máscaras y priors dentro del origen. `Z_locked` conserva esa elección y su λ: predice B paraAqua>0 y0paraAqua=0. Es la ablación primaria y debe coincidir exactamente conB en todas las filasAqua>0. Si la políticaB eligióM1, la ablación no cambia nada.

Añadir `B_Z_locked`: porcomuna, aplicar la ablación solo si su MAE interno mejora>1% la políticaB interna ya elegida; en empate conservarB. No volver a elegirλ paraesta variante. Secundarias separadas: `M1_Z` elige entrelos4Zλ vsM1, `B_Z_reselected` elige mejorZλ vsB si mejora>1%; se reconoce que mezclan gate y retuning, no efecto puro del cero.

## Separación y criterios

Ocho folds externos2012–2019, siete internos dentro de cada origen. Máscaras, factorregional, normalizaciónB y elección solo con origen. Reproducir M0/M1/M2/B previos a tolerancia1e-10 sobre las5.184filas, usando64fits B-only, no Huber. Comparar también con referenciaB/P ya guardada, sin reescogerla.

Primaria: MAE mensual sobre54comunas. Secundarias: sesgo,suma predicha,MAE regional por temporada-mes, activos,SNP≥50,Aqua0/SNPpositivo,ambos0,14publicadas y distribución comunal. Contrastes por8temporadas, bootstrap5000semilla20261114exploratorio; no píxeles/comunasIID. Mantener fallos y compensaciones, no solo neto.

Evaluar transporte4temporadas adelante/atrás y6temporadas adelante/atrás con selección solo origen. Congelar ajuste completo2012–2019 antes de leer destinos2020–2025 ya consultados, siempre descriptivos. Probar independencia de etiquetas de destino y reproducción exacta de positivos deZ_locked.

Diagnóstico adicional predefinido: oráculo restringido a acciones{0,B} solo enAqua0. UsarY únicamente para mínimo retrospectivo de pérdida de esa clase, sin elegirλ conYdestino. Es techo optimista de ganancia paraese gate, NOmodelo ni validación ni rankingcompetitivo. No restringe ganancias de modelos que cambien cantidad.

## Agregación de ganancias y estancamiento

Reportar mejora neta emparejada en la misma población; no sumar porcentajes de variantes alternativas. GatesZ y hurdle compiten por ceros y no se acumulan automáticamente. Candidatos con<1% de mejora sobreB o cuya ventaja desaparece en transporte se conservan como evidencia marginal, pero dos familias consecutivas así activan revisión de dirección mediante consejo≤6miembros que incluye un agente de ideas heterodoxas. El1% es regla de trabajo interna, no NASA ni prueba de significación. La calidad científica también puede hacer interesante un resultado negativo paraPRincremental a dev.

Artefactos nuevos solo `data/processed/zero_anchor_audit/`, código/test aislados y revisión. Manifiesto de entradas/código/protocolo/entorno y protección de datos, publicación y etapas anteriores.
