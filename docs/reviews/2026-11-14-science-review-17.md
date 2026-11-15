# Revisión 17 — la distribución de dos partes mejora el MAE local y pierde volumen

El [protocolo 17](2026-11-14-science-protocol-17.md) se fijó antes de medir. La evaluación sigue siendo retrospectiva y adaptativa: no es un nuevo holdout ni una validación del fuego físico. La referencia es la actividad diurna registrada por S-NPP, agregada por comuna y mes. La oportunidad física de observar continúa sin medirse.

## Resultado principal y coste agregado

El factorial primario con κ=10 fijo logra MAE **1,808210**, frente a **1,903194** de B: una reducción del **4,991 %** sobre 5.184 filas de las 54 comunas. Es un avance en la métrica primaria preregistrada. Sin embargo, su MAE de totales regionales mensuales aumenta de **31,546960 a 49,535897**, un **57,023 %**. La suma de medianas locales no estima la media de la suma.

| Método | MAE comuna-mes | Sesgo medio | Suma estimada | MAE regional mensual |
|---|---:|---:|---:|---:|
| M1 | 2,047245 | +0,014950 | 21.566,503 | 47,254789 |
| B | 1,903194 | −0,087189 | 21.037,010 | 31,546960 |
| B/P guardado | 1,883928 | −0,167567 | 20.620,334 | 31,716607 |
| E11, κ=10 fijo | **1,808210** | **−0,731078** | **17.699,089** | **49,535897** |
| B_E, selección interna | 1,841148 | −0,451696 | 19.147,406 | 38,133135 |

La suma observada es 21.489: E11 queda un 17,637 % por debajo. B_E selecciona entre los tres κ dentro del origen y conserva B salvo mejora interna mayor al 1 %. Mejora el MAE global un 3,260 % frente a B, pero tampoco elimina el coste agregado. Su resultado pertenece al paquete de selección; no reemplaza el factorial fijo para atribuir componentes.

La mejora tampoco es uniforme por población. En las **14 comunas publicadas**, E11 empeora de 2,999471 a **3,048382** y su MAE regional aumenta de 18,748498 a 26,842575. B_E obtiene 2,993291, apenas por debajo de B, con MAE regional 20,952497. No hay fundamento para sustituir la publicación actual.

## Ganancias marginales e interacción

Todos los términos siguientes usan κ=10, la misma población y las mismas máscaras. P indica probabilidad local con pooling y F la distribución positiva local con pooling; 00 emplea ambos componentes parentales.

| Componente | MAE | Diferencia frente a 00 |
|---|---:|---:|
| E00: P padre, F padre | 1,901226 | — |
| E10: P local, F padre | 1,876303 | −0,024922 |
| E01: P padre, F local | 1,838845 | −0,062381 |
| E11: P local, F local | 1,808210 | −0,093016 |

La interacción en pérdida es `I = L11 − L10 − L01 + L00 = −0,005713`. El bootstrap exploratorio por ocho temporadas, con 5.000 réplicas y semilla 20261114, entrega **IC percentil 95 % [−0,020833; +0,004270]**: incluye cero. No demuestra una sinergia estable entre ambos componentes. El valor medio está muy influido por 2017; tres temporadas tienen interacción positiva. Los intervalos de los efectos marginales son [−0,036578; −0,010063] para P y [−0,086179; −0,039478] para F. No deben sumarse porcentajes de mejoras frente a B ni atribuir causalidad física a este factorial.

El contraste E11−B tiene diferencia media −0,094984 e intervalo exploratorio [−0,153448; −0,028827]; mejora en seis de ocho temporadas, con retrocesos en 2014 y 2016. B_E−B tiene −0,062046 e intervalo [−0,104019; −0,017296], mejorando en siete temporadas. Ocho bloques y una historia adaptativa de investigación limitan la fuerza inferencial de estos intervalos.

## Qué mejora y qué empeora

| Estrato de referencia | Filas | MAE B | MAE E11, κ=10 |
|---|---:|---:|---:|
| Actividad S-NPP positiva | 2.563 | 3,565127 | 3,511262 |
| S-NPP registra cero | 2.621 | 0,278038 | 0,142844 |
| Ambos sensores registran cero | 2.491 | 0,159746 | 0,041349 |
| Aqua cero y S-NPP positivo | 1.152 | 1,803305 | **1,953125** |
| Aqua positivo | 1.541 | 4,796121 | 4,555976 |
| Referencia de 50 o más celdas-día | 74 | 19,708540 | **22,961981** |

El modelo reduce estimaciones positivas cuando S-NPP registra cero y mejora donde Aqua sí registra actividad. A cambio, recupera menos actividad con Aqua=0 y subestima más los meses intensos. Estos estratos se solapan; sus ganancias no se suman como experimentos independientes. “Cero registrado” sigue sin equivaler a observación útil o ausencia física de fuego.

La probabilidad local reduce Brier de 0,170188 a **0,153589**. Los cinco bins predefinidos muestran, entre otros, probabilidad media 0,478396 frente a frecuencia positiva 0,543818 en [0,4; 0,6). La mejora de Brier no acredita calibración perfecta ni una probabilidad de incendio físico; describe detección registrada por S-NPP.

## Transporte temporal y consultas posteriores

| Bloque | MAE B | MAE E11 | MAE B_E | Regional B | Regional E11 |
|---|---:|---:|---:|---:|---:|
| 4 temporadas hacia adelante | 2,239129 | 1,919541 | 2,066443 | 47,922723 | 50,537004 |
| 4 temporadas hacia atrás | 1,861186 | 1,828707 | 1,801438 | 35,852461 | 56,238649 |
| 6 temporadas hacia adelante | 1,931063 | 1,708109 | 1,786839 | 31,984951 | 39,588446 |
| 6 temporadas hacia atrás | 1,716298 | 1,681774 | 1,681220 | 30,982880 | 48,208565 |
| 2020–2021, descriptivo | 1,960280 | 1,847724 | 1,904265 | 39,419882 | 59,849430 |
| 2022–2025, descriptivo | 2,374788 | 2,217186 | 2,261450 | 55,197785 | 72,667457 |

E11 mejora el MAE comuna-mes en los cuatro transportes y empeora el MAE regional en los cuatro. B_E mejora el MAE local en los cuatro, pero el regional empeora en tres. El patrón posterior repite el compromiso; 2020+ ya había sido consultado y no constituye validación independiente. Se conservaron los cortes de calendario y las exclusiones heredadas; los diagnósticos de enero–junio de 2022 y del calendario anterior figuran por separado en el JSON.

## Integridad y decisión

El resumen registra reproducción de controles previos a tolerancia 1e-10, **64 ajustes nested, 24 de transporte y uno completo**, con 5.184 filas nested y 3.780 posteriores. Los ajustes y la selección usan únicamente el origen. El modelo completo se persistió antes de leer las etiquetas posteriores, y su restauración reproduce exactamente sus predicciones. Las pruebas sintéticas del helper y runner comprueban medianas, identidad con la CDF equivalente, fallbacks y ausencia de dependencia de etiquetas futuras; el manifiesto conserva firmas y parámetros.

**No promover.** Conservar el avance primario y el coste agregado como un resultado conjunto, manteniendo M1, las 14 comunas publicadas y los datos base protegidos. La evidencia sugiere estudiar decisiones distintas sobre la misma distribución: media para estimar cantidad esperada y mediana para minimizar MAE local. No demuestra que una distribución más compleja ni el simple producto de probabilidad por cantidad solucionen ambos objetivos.

Una eventual reconciliación con el total de B debe preregistrarse y evaluarse como candidato separado. Si impone por mes `Σ predicción = Σ B`, preservará el MAE regional y el sesgo global de B **por construcción**; la evidencia nueva será su error local bajo ese presupuesto. El dominio completo de 54 comunas debe fijarse antes de filtrar áreas de interés, y no debe presentarse como mejora independiente del total ni como reconciliación de intervalos probabilísticos.

Fuente reproducible: `data/processed/hurdle_audit/summary.json`, junto con `manifest.json`, selecciones, pérdidas internas, temporadas de ajuste, predicciones y `frozen_model.json` de ese mismo directorio.
