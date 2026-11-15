# Protocolo 13 — separar forma de banda y conjunto de calibración

Fijado antes de comparar estas variantes. Base a8b27a4, con dev f49a9af integrado. La etapa 12 mostró mejoras de pérdida con raíz y colas desiguales; también dejó abierta la interpretación de calibrar solo con meses activos cuando ese estado futuro es desconocido. Se hará un diseño factorial, sin cambiar estimaciones puntuales ni escoger un ámbito favorable después de ver resultados.

## Ocho combinaciones declaradas

Mantener únicamente las políticas puntuales preexistentes **M1 y M1/B**, como referencia publicada y candidato afín más simple. Fijar escala raíz `s(p)=sqrt(1+p)` sin volver a optimizar la potencia. Cruzar dos decisiones, aplicando las cuatro recetas a cada política:

1. **Conjunto de calibración:** todos los meses del origen o solo sus meses S-NPP>0.
2. **Forma:** simétrica o asimétrica.

Simétrica: q80 de `abs(y−p)/s(p)`; intervalo `[max(0,p−q80*s(p)), p+q80*s(p)]`.

Asimétrica: q10 y q90 del residuo firmado `(y−p)/s(p)`; intervalo `[max(0,p+q10*s(p)), max(0,p+q90*s(p))]`. Usar cuantiles empíricos con interpolación lineal. No forzar que contenga el punto ni equilibrar después sus colas con el destino; cuantiles de una distribución discreta tampoco garantizan fracciones de exceso exactamente 10 %/10 %. Registrar cuándo el punto queda fuera del intervalo.

Estas son bandas empíricas de discrepancia con S-NPP, no intervalos certificados de incendios físicos. Calibrar con meses activos es una condición sobre etiquetas pasadas, **no una regla para escoger receta al consultar el futuro**. Las ocho combinaciones se aplican siempre; no decidir cuál usar mirando si el destino tuvo actividad.

## Separación temporal y controles

Repetir el LOSO externo 2012–2019 y sus siete folds internos mediante el ajuste/selección verificado de etapa 12. Se puede capturar las predicciones internas al ejecutar ese helper, sin modificarlo ni usar tablas OOF globales que hayan entrenado con la temporada externa. Reconstruir la elección por comuna de cada política y calibrar cada receta solo con sus predicciones internas, excluyendo el destino de ajuste, máscara y calibración.

Exigir que la receta **simétrica/activa/raíz** reproduzca las estimaciones y radios de etapa 12 en M1 y M1/B (tolerancia 1e-10). Para la calibración completa de 2012–2019, exigir reproducción de sus radios finales y de la firma puntual congelada d199e3f7857de17cc8d3b70d392c6c7e60ea1694bb58163de27bf7135dcc5868. Conservar cantidad de meses total/activos de cada calibración. Si una receta activa no tiene etiquetas suficientes para calcular el cuantil, conservar banda desconocida, no rellenar cero ni copiar el destino.

Todas las temporadas ya se consultaron en desarrollo. No hay garantía conformal ni nueva validación independiente: la selección y calibración comparten el origen, y el punto y las familias fueron desarrollados adaptativamente.

## Criterios definidos antes de puntuar

- **Primario:** pérdida de intervalo IS con α=0,2 sobre todos los meses, incluidos ceros de detección; menor es mejor. Misma fórmula y referencia que protocolo 12, sin modificar pesos.
- **Secundarios obligatorios:** IS y cobertura en meses activos, anchura, fracciones por debajo/encima, banda sin calibración, fracción de anchura cero, límite inferior positivo y punto fuera del intervalo. No declarar una mejora general si oculta deterioro de actividad baja o de meses con señal no detectada por Aqua.
- Estratos ya conocidos: S-NPP=0, 1–9, 10–49 y ≥50, más Aqua=0/S-NPP>0 y ambos sensores cero. Son análisis de resultado, nunca variables para determinar la banda del destino.
- Publicar las ocho combinaciones sobre las 54 comunas y las 14 habilitadas, por temporada y agregado. Comparar simétrica con asimétrica manteniendo fijo el conjunto de calibración, y activos con todos manteniendo fija la forma. No atribuir a la forma un cambio que también modifica el conjunto de calibración.
- Registrar diferencias emparejadas de IS por las ocho temporadas, sin tratar meses/comunas como réplicas independientes ni presentar múltiples comparaciones como confirmación. Sin nuevos umbrales, habilitaciones o selección automática para producción.

## Diagnóstico posterior y artefactos

Calibrar las ocho recetas con las estimaciones de política OOF anidadas completas 2012–2019; guardar parámetros antes de leer los mismos 3.780 pares posteriores de etapa 11. Mantener sus bloques y transición enero–junio 2022. Son diagnósticos reutilizados, no un holdout nuevo. El punto queda idéntico; la receta no requiere etiqueta futura, incluso si falta o es desconocida.

Nuevo directorio `data/processed/asymmetric_band_audit/`: parámetros por fold y finales, intervalos en Parquet con Aqua/S-NPP de diagnóstico, métricas y contrastes, resumen y manifiesto de código/helpers/protocolo/entradas protegidas. Tests de cuantiles firmados, clipping de ambos extremos, ausencia de datos activos sin imputación, independencia de etiquetas, exclusión externa y reproducción del control simétrico/activo. Si se incluyen figuras, mostrar las ocho recetas y sus costes, sin elegir un ejemplo por su resultado.

No modificar publicación, `publish_web.py`, máscaras, datos base ni artefactos anteriores. Los metadatos derivados de producto f49a9af son la referencia actual; los manifiestos antiguos conservan sus instantáneas históricas. Commits Daniel Quinteros sin firma, PR a dev y control de deadline hasta 21:00 de Santiago.
