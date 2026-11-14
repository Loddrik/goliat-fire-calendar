# Protocolo 4 — pérdida robusta del afín y estabilidad

Fijado antes de ejecutar la iteración 4. Base `0b972a4`; objetivo autorizado: iterar hasta el 14-11-2026 a las 21:00 America/Santiago (15-11-2026 00:00 UTC). La extensión horaria autoriza continuar la investigación más allá del corte anterior de las 19:00; no modifica por sí sola la publicación en producción.

## Pregunta

El afín B se ajusta con pérdida cuadrática y se selecciona con MAE. ¿Sustituir la pérdida local por Huber mejora el error fuera de ajuste y reduce la actividad añadida en meses sin detecciones, sin deteriorar los períodos intensos?

## Candidato H

Misma forma `max(0,a+b·Aqua)`, grupos mensuales, normalización RMS, pendiente no negativa y prior regional del candidato B. Cambiar solo la función de pérdida local:

`media[Huber_δ(VIIRS−a−β·z)] + λ/2 · [a²+(β−β_prior)²]`.

Huber vale `r²/2` si |r|≤δ, y `δ·(|r|−δ/2)` en otro caso. δ ∈ {1,3,10} celdas-día; λ ∈ {0,01;0,1;1}. No ampliar la grilla al ver resultados externos. El prior y la escala regionales se conservan para aislar el cambio de pérdida: no se afirma que todo el procedimiento sea robusto a valores extremos.

Resolver por mínimos cuadrados iterativamente reponderados con restricciones de pendiente. Exigir gradiente/KKT máximo ≤10⁻⁶ por grupo, con máximo 1.000 iteraciones; registrar iteraciones y residuo de optimalidad. Si algún candidato no converge, detener la evaluación, diagnosticar la implementación y documentar cualquier corrección; no reemplazar sus predicciones por ceros ni excluirlo silenciosamente según su resultado. Validar con casos sintéticos y un contraste de objetivo/gradiente.

## Comparación fijada

- Reutilizar exclusivamente temporadas 2012–2019, máscaras dentro de cada partición y validación anidada de las iteraciones 2–3. Temporadas 2020 en adelante siguen fuera.
- Reproducir exactamente M1 y política M1/B antes de comparar.
- Evaluar **M1/H** (H sustituye a M1 solo con mejora interna >1 %) y **M1/B/H** (H sustituye a la elección M1/B solo con mejora interna >1 %). En empate de H, preferir mayor λ y luego mayor δ. No cambiar compuertas: Aqua ≥50 y victoria frente a M0/M2 en ≥6 de 8 temporadas.
- Reportar MAE/sesgo, bloques por temporada, las mismas tres poblaciones Aqua/VIIRS de la iteración 3 y Mulchén. Añadir un desglose predefinido de intensidad objetivo VIIRS: 0, (0,10), [10,50), ≥50 celdas-día. Son diagnósticos con etiquetas observadas, no una condición disponible al predecir.
- Bootstrap pareado de temporadas completas, 5.000 réplicas, semilla 20261114: M1/H−M1 y M1/B/H−M1/B. Los intervalos son exploratorios de desarrollo, con solo ocho bloques y un diseño adaptado a datos conocidos.
- Mostrar cobertura/ancho de cuantil absoluto 80 calibrado en residuos activos internos para cada política. No escoger política ni banda por maximizar resultados externos ni publicar garantías de cobertura.

## Integridad y límite temporal

Directorio de salida nuevo `data/processed/robust_affine_audit/`; conservar predicciones, selección, diagnósticos numéricos, resumen y hashes. No modificar iteraciones anteriores ni producción. Registrar protocolo y código antes de dar por válidos los resultados. No iniciar experimentos que no puedan detenerse al plazo autorizado; la última fase antes de las 21:00 consolidará resultados y propuestas revisables.
