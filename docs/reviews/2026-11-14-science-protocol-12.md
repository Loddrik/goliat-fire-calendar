# Protocolo 12 — radios dependientes de actividad y pérdida de intervalo

Fijado antes de comparar las nuevas bandas. Base 2d3455e. La etapa 11 mostró cobertura variable por período e intensidad. Se evaluará una única forma intermedia nueva —raíz cuadrada— frente a dos controles existentes: radio absoluto y relativo. **Las estimaciones puntuales no cambian.** No se elegirá una banda por cobertura observada en 2020+.

## Tres reglas declaradas

Para una estimación no negativa p y potencia a∈{0;0,5;1}, definir escala s(p)=(1+p)^a. Aprender q como percentil 80 de |y−p|/s(p) exclusivamente en meses activos S-NPP del conjunto permitido de calibración. El radio al consultar un destino es q·s(p); no depende de su etiqueta S-NPP ni de conocer si será activo.

- a=0: radio absoluto, control de las etapas 3–5 y 11.
- a=0,5: raíz cuadrada, regla heurística nueva sin estimar otra potencia.
- a=1: radio relativo con desplazamiento 1, control de la etapa 3.

El 1 es una referencia de una celda-día que evita escala cero; no demuestra una distribución Poisson ni independencia física de celdas/días. Mantener las cinco políticas puntuales M1, M1/B, M1/H, M1/P y M1/B/P. No añadir modelos, modificar λ/δ, cambiar confianza/cartografía ni seleccionar comunas según el resultado.

## Evaluación histórica anidada: recalcular, no reciclar OOF global

Para cada temporada externa 2012–2019:

1. Excluirla de todo ajuste, máscara, selección y calibración. Recalcular los siete folds internos sobre las otras temporadas, con los mismos helpers y máscaras aprendidas solo con temporadas permitidas y anteriores al solape.
2. Elegir candidatos por comuna/política con las mismas funciones y regla >1 %. Para calibrar cada radio, usar las predicciones candidatas internas de ese candidato elegido, normalizadas por su propia estimación interna y solo con etiquetas activas internas.
3. Ajustar la política puntual con las siete temporadas y evaluar la temporada externa sin modificar q. La selección y calibración comparten datos internos, por lo que esto **no es split conformal ni tiene garantía distribucional**; el destino externo permite medir empíricamente ese procedimiento.
4. Exigir reproducción de claves y conteos objetivo, estimaciones puntuales y radios absolutos frente a los artefactos 4–5. Para M1 y M1/B, exigir también reproducción del radio relativo guardado en el protocolo 3, tolerancia numérica 1e-10.

No calibrar un fold externo con los registros OOF de otros folds de la tabla global: esos ajustes pueden haber usado la temporada externa y provocar fuga indirecta. Aunque se preserve la separación computacional, las ocho temporadas ya fueron consultadas en desarrollo: la comparación de estas bandas es retrospectiva y adaptativa, no validación independiente nueva.

## Métrica común y desgloses

Usar intervalos l=max(0,p−r), u=p+r. Para α=0,2, la pérdida de intervalo es:

`IS = (u−l) + (2/α)·max(l−y,0) + (2/α)·max(y−u,0)`.

Menor es mejor. Es la forma de pérdida de la ecuación 43 de [Gneiting y Raftery (2007)](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf). La regla estándar evalúa extremos cuantílicos centrales; nuestras bandas simétricas y discretas no son necesariamente cuantiles centrales. Aplicarla como pérdida comparativa no certifica calibración ni cobertura del 80 %.

Reportar conjuntamente cobertura, anchura media, IS medio y fracciones por debajo/encima. Poblaciones: todos los meses, meses activos y estratos S-NPP 0, 1–9, 10–49 y ≥50, heredados de análisis anteriores. Los estratos usan la etiqueta solo para evaluar; no determinan el radio de consulta. Mantener todas las 54 comunas y el subgrupo preexistente de 14, sin nuevas compuertas.

Conservar los resultados de las 15 combinaciones política×potencia, por temporada externa y agregado, sin seleccionar solo las favorables. Para cada política, comparar raíz y relativo contra absoluto mediante diferencias emparejadas de IS por temporada, publicar las ocho diferencias y su media. No presentar múltiples comparaciones como confirmación independiente ni tratar meses/comunas como réplicas independientes. No elegir una potencia para producción en esta etapa.

## Diagnóstico posterior con punto congelado

Aprender tres radios por política/comuna con las estimaciones de política OOF anidadas completas 2012–2019, igual que etapa 11 para a=0. Guardarlos antes de evaluar destinos; exigir reproducción exacta del radio absoluto y de la firma del modelo puntual congelado de etapa 11. Evaluar solo sobre sus 3.780 pares posteriores ya versionados, con bloques y transición enero–junio 2022 idénticos. El objetivo posterior no participa en radios; reportar los resultados como diagnóstico reutilizado, no un holdout nuevo. No sustituir los radios del artefacto anterior.

## Artefactos y pruebas

Nuevo `data/processed/scaled_band_audit/`: radios por fold y finales, predicciones/intervalos en Parquet, métricas por temporada/población, contrastes, resumen y manifiesto de entradas/helpers/protocolo/archivos protegidos. Mantener fuentes, producción y auditorías previas intactas. Tests de fórmula IS, clipping, ausencia de calibración sin imputar cero, independencia de etiqueta futura, escala en p=0, exclusión del destino y controles de reproducción. Si se incluyen figuras, exportarlas con herramientas científicas estándar y conservar sus datos; no usarlas para escoger un resultado favorable. Control de deadline hasta 21:00 de Santiago; commits Daniel Quinteros sin firma; PR a dev.
