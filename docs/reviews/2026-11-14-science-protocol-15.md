# Protocolo 15 — extremos ajustados por pérdida en unidades originales

Fijado antes de calcular los nuevos extremos. Base 4ccdbe4. Etapa 13 comparó cuantiles de residuos normalizados, que no se ajustaron minimizando IS en las unidades originales. Pregunta: manteniendo punto, escala y dos extremos libres, ¿un ajuste directo de esa pérdida mejora su transporte?

## Clase y criterio fijos

Solo puntos M1 y M1/B; escala raíz s=sqrt(1+p), α=0,2, misma grilla/cartografía y máscaras existentes. Comparar dos reglas para una banda asimétrica, cruzadas con calibración activa/todos los meses:

- **Control empírico:** q10/q90 de `(y−p)/s`, exactamente la receta asimétrica de etapa 13.
- **Ajuste IS:** elegir qL≤qU para minimizar el promedio de la misma pérdida de intervalo sobre el conjunto permitido de calibración, en unidades de celdas-día y con clipping incorporado: L=max(0,p+s*qL), U=max(0,p+s*qU).

Ambas tienen dos parámetros por comuna y usan idénticos puntos y etiquetas de origen. No optimizar potencia, α, cohorte o política con el destino. Aplicar las ocho combinaciones siempre; no seleccionar receta sabiendo si el destino fue activo. Añadir únicamente como referencia las bandas simétricas/activas/raíz M1 y M1/B de etapa 12, sin reajustarlas.

## Optimización verificable, sin grilla arbitraria

Para cada calibración, los cambios de pendiente de la pérdida respecto a cada q están en `(y−p)/s` y `−p/s` (cruce del clipping en cero). Usar su unión ordenada, más 0, como candidatos; no fijar límites según el destino. La pérdida es lineal por tramos. Separar su parte inferior `−L+10*max(L−y,0)` y superior `U+10*max(y−U,0)` y combinar mínimos de prefijos para imponer qL≤qU. Así se comprueban todos los puntos de quiebre y las caras diagonales relevantes, sin enumerar una malla elegida por resultado.

Verificar la solución contra búsqueda exhaustiva de pares en pequeños ejemplos y perturbaciones factibles. Comparación de pérdidas con tolerancia numérica 1e-12 y desempate lexicográfico por menor qL, luego menor qU; fijado antes de evaluar. Recalcular la pérdida elegida con la fórmula IS completa. Una calibración activa vacía conserva extremos desconocidos; no la convierte en intervalo cero. Esta optimización empírica no garantiza riesgo o cobertura futura y puede sobreajustar.

## Separación, controles y métricas

Repetir ocho folds externos 2012–2019 y sus siete folds internos, capturando las predicciones del helper ya verificado sin modificarlo. Selección puntual, máscaras y datos de calibración no pueden ver la temporada externa. Reproducir los controles asimétricos empíricos de etapa 13 y los simétricos/activos de etapa 12, tolerancia 1e-10. El punto y los radios anteriores permanecen intactos.

Criterio primario: IS en todos los meses. Secundarios: IS/cobertura activos, anchura, colas inferior/superior, anchura cero, límite inferior positivo, punto fuera del intervalo y ausencia de calibración. Mantener los mismos estratos de etapa 13, incluyendo Aqua=0/S-NPP>0 y ambos sensores cero, las 54 comunas y las 14 publicadas. Publicar las diez combinaciones, no solo el mínimo.

Comparar ajuste IS con control empírico manteniendo fija la cohorte, con diferencias emparejadas por las ocho temporadas; sin tratar meses/comunas como réplicas independientes. Distinguir la mejora de entrenamiento (esperable por construcción) de la mejora externa, que puede faltar. No llamar validación independiente a temporadas consultadas en desarrollo.

Congelar parámetros completos con las estimaciones de política OOF anidadas 2012–2019 antes de leer los 3.780 pares posteriores ya disponibles. Mantener bloques y transición calendario de etapa 11. Reproducir su punto congelado y las bandas de control correspondientes. Los resultados posteriores son descriptivos reutilizados, sin adaptación del criterio.

## Artefactos y cierre de investigación

Nuevo `data/processed/interval_loss_fit_audit/`: extremos por fold y finales, pérdidas de calibración y diagnóstico del optimizador, intervalos Parquet, métricas, contrastes, resumen y manifiesto. Tests de óptimo exhaustivo, clipping, orden, desempates, ausencia de calibración e independencia de etiquetas/exclusión temporal. No cambiar publicación, datos base ni artefactos anteriores.

Esta es la última ampliación de familias prevista antes de dedicar el tramo restante a reproducción desde checkout limpio, comprobación de integridad y consolidación de evidencia. Commits Daniel Quinteros sin firma, PR a dev, límite de nuevos cálculos de investigación 21:00 de Santiago.
