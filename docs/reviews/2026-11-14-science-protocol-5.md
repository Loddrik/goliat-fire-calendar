# Protocolo 5 — calibración monótona por tramos anclada en cero

Fijado antes de ejecutar esta iteración, sobre `f5fec06`, a continuación de las evaluaciones afín y Huber. Objetivo: comprobar si se puede mejorar la calibración donde Aqua es positivo sin el coste de un intercepto en ceros. El anclaje en cero es una restricción de este candidato, no una afirmación de que cero detecciones signifique ausencia de actividad.

## Candidato P

Por comuna y grupo mensual:

`pred = b₁·min(Aqua,τ) + b₂·max(Aqua−τ,0)`, con `b₁,b₂ ≥ 0`.

τ es la mediana de Aqua positivo en el entrenamiento regional del grupo; si el grupo no tiene valores positivos, τ=1. Se aprende dentro de cada partición, sin consultar la temporada retirada. Se conserva la escala RMS regional `s` y razón regional `r` del afín B. Ajustar `β₁=b₁·s`, `β₂=b₂·s`, con `z₁=min(Aqua,τ)/s`, `z₂=max(Aqua−τ,0)/s`, minimizando:

`media[(VIIRS−β₁z₁−β₂z₂)²] + λ·[(β₁−r·s)²+(β₂−r·s)²]`.

λ ∈ {0,01;0,1;1;10}, misma grilla de B. No hay intercepto; P(0)=0, es continuo en τ y no decreciente. Las dos pendientes tienen la misma cantidad de parámetros locales que el afín; el umbral es regional y solo depende del predictor de entrenamiento. No se optimiza τ con resultados externos. Resolver el problema cuadrático con las dos restricciones, comprobando solución interior y fronteras; exigir coeficientes finitos y KKT≤10⁻⁶.

## Evaluación

- Mismas temporadas 2012–2019, máscara por partición y dos bucles LOSO. Temporadas 2020 en adelante fuera. Reproducir M1 y M1/B de la iteración 3.
- Políticas fijadas: **M1/P** (P sustituye a M1 solo con mejora interna >1 %) y **M1/B/P** (P sustituye a la elección interna M1/B solo con mejora >1 %). Empates λ → mayor regularización. No se añade H a esta comparación: se aísla la forma funcional con el mismo ajuste cuadrático que B.
- Comparar MAE, sesgo, pérdidas por temporada, subgrupos Aqua/VIIRS, intensidad VIIRS 0, (0,10), [10,50), ≥50 y compuertas diagnósticas sin cambiar umbrales. Mostrar Mulchén. Que P no prediga actividad en cero no se contabiliza como detección recuperada.
- Bootstrap pareado por temporadas, 5.000 réplicas, semilla 20261114: M1/P−M1 y M1/B/P−M1/B. Intervalos de desarrollo, ocho bloques, sin evidencia confirmatoria externa.
- Cuantil absoluto 80 calibrado en residuos activos internos, misma regla que la iteración 4; reportar cobertura/ancho externos, sin seleccionar banda por esos resultados.

## Integridad y avance

Nuevo directorio `data/processed/piecewise_audit/`. Registrar entradas, código, protocolo, umbrales, coeficientes, elecciones, predicciones y métricas, preservando por hash producción y las iteraciones anteriores. Añadir pruebas de continuidad, cero exacto, monotonía, KKT, normalización y umbral solo de entrenamiento, selección interna y ausencia de cambios ante la verdad externa.

No cambiar producción ni elegir retrospectivamente una familia por la cantidad de comunas. Los PR se dirigen a `dev`. Se respeta el plazo explícito de investigación de las 21:00 de Santiago; el runner aceptará la misma variable de deadline que la iteración 4.
