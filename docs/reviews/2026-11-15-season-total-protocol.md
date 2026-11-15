# Protocolo42: preguntas del issue48 sobre totales de temporada

Petición explícita del usuario recibida durante D: incorporar las preguntas del [issue48](https://github.com/Loddrik/goliat-fire-calendar/issues/48). Nuevo diagnóstico de escala, no otra familia de modelos o rescate de primarias. Cap absoluto **10:27–10:43 UTC del15 noviembre2026**, incluidos código, controles e independiente. Si no se completa, conservar parcial/inconcluso. Últimos30min D10:43–11:13 y contingencia11:13–11:30 permanecen sin recursos científicos nuevos. No descargas, fits, búsqueda, cambios de factores/gates o JSON de producción.

El issue ya aporta resultados de su revisor (~20% mediana de error relativo absoluto, ~−12% media de error relativo y razones entre décadas). Esos claims se conocen antes del protocolo; no se llama ciego, nuevo holdout o validación histórica a este análisis. No se eligen fórmulas para reproducirlos. Los targets y máscaras se han consultado durante el desarrollo.

## Preguntas y contratos fijados

1. Cuantificar el error de la SUMA julio–junio para M1 en las14 publicadas bajo el LOSO original2012–2019, no sumar MAE mensuales.
2. Explicar por qué la validación mensual no valida automáticamente el total anual, su banda o el período2002–2011.
3. Determinar qué permiten concluir estos datos sobre el salto2012 y las habilitaciones. Concordancia o sesgo no identifican causa: épocas distintas mezclan actividad y observación. No inventar umbral anual ni deshabilitar comunas retrospectivamente.

Fuente primaria: `data/processed/scientific_audit/outer_predictions.csv`, exclusivamente `policy=published_fixed`. Predicciones M1 ya existentes con factor ajustado fuera de cada temporada; no importarejecutar `experiment.py`, que tiene efectos al importar. Se usan todas las54×8×12 filas; población primaria14habilitadas por `data/processed/gates.csv`, y all54/remaining40 como contexto separado. M0 yM2 congelados son controles descriptivos, sin selección de ganador. Contrato de máscara publicada fija, no fold_fitted ni máscara6 del21. Fuente de control: `eval_loso.csv`, M1 yκ0, con invariancia exacta de controlesM1 sobre los7κ. Revisor independiente usa `bias*n` para Δtotal y SNPP de `celldays_comuna_month_masked.parquet` para denominadores.

Antes de agregar: freeze de protocolo/código/entradas/entorno productor; comprobar claves únicas y12meses por CUT/temporada,54CUT×8temporadas,14habilitadas. Reproducir por CUT/temporada los MAE/bias/n/aqua_sum mensuales deM1 contra eval_losoκ0, tolerancia absoluta1e−9 yrelativa1e−11. Fallo→STOP sin resultados interpretados. Sólo lectura de tablas versionadas; no rehacer ajustes o rellenar adquisición desconocida.

Para cada CUT/temporada: `Y=sum(snpp)`, `P=sum(M1)`, `error=P−Y`, `abs_error=abs(P−Y)`. Relativo firmado `error/Y` y absoluto `abs_error/Y` sólo siY>0; siY=0 ambosnull, con estados separados P=0 yP>0. Sin epsilon. Escala celdas-día registradas agregadas; no incendios ni superficie.

Resumen por CUT y por población: Ntemporadas, NconY>0, número Y0/P0 yY0/P>0, MAEabs=media deabs_error, biasabs=media deerror, MARE=media deabs_relative, medianaAPE, media_signed_relative, WAPE=sumabs_error/sumY y weighted_bias=sumerror/sumY (null siΣY=0). No llamar a todas «MAE relativo». Primaria descriptiva14: medianaAPE y media_signed_relative sobre sus CUT-temporadasY>0, conN explícito. No test de significación ni causalidad; los14 se seleccionaron con ese mismo LOSO y la máscara usa todo el desarrollo: diagnóstico aparente postselección, sin garantía para2002–2011. All54/40 yM0/M2 se muestran separados; no sustituyen14.

Preservar tabla completa54×8 por método(1296filas si3métodos), resumen por CUT y grupo, checks/manifest/protocolo/env. Máximo5MiB salidas,1GiB RSS,0fits/solvers/descargas. Informe responde las3preguntas sin promover M1 como validado anualmente ni cambiar su habilitación mensual. Producción espera revisión aparte: aquí se propone metadata inequívoca y divulgación docs/method§6, no se devuelve automáticamente el tramo2002 a la landing.

Independiente separado reconstruye todos los erroresM1 anuales y resúmenes14 con controles originales/Parquet, revisa sumas, ceros, denominadores, procedencia y claims; no toca salidas originales. Si necesita otros métodos, usa las columnas ya congeladas para controles, sin nuevos fits. No pérdida nueva para elegir modelo: es el mismo error de M1 en una unidad de decisión explícitamente solicitada.
