# Protocolo 8 — transporte temporal con familias congeladas

Fijado antes de obtener métricas de estas particiones. Base 24f9aa3. Pregunta: ¿se mantienen las mejoras al cambiar la dirección temporal de calibración, especialmente al reconstruir temporadas anteriores?

## Dos particiones y ninguna selección sobre destino

- **Hacia adelante:** entrenamiento 2012–2015, destino 2016–2019.
- **Hacia atrás:** entrenamiento 2016–2019, destino 2012–2015.

Temporadas julio–junio. Se usan grilla, cartografía, fuentes y reglas publicadas; cada máscara se aprende solo con temporadas permitidas y observaciones anteriores a 2012, exactamente como en las iteraciones previas. Cada destino usa la máscara aprendida en su correspondiente origen. La selección de candidato por comuna usa únicamente LOSO de las cuatro temporadas de origen, con máscaras recalculadas en cada subconjunto de tres. Después se ajusta con las cuatro temporadas de origen y se evalúa el bloque destino completo.

Familias congeladas: M0 Aqua sin escalar, M1 factor regional, M2 climatología, selección M1/B, M1/H, M1/P y M1/B/P. Mismos candidatos λ, δ, priors, umbral de P, tolerancia numérica y regla de mejora interna >1 % que protocolos 3–5. No añadir parámetros, ni seleccionar familias, umbrales de intensidad o comunas usando el destino. Los datos completos 2012–2019 ya fueron consultados en desarrollo: estas pruebas son **estrés retrospectivo**, no un holdout nuevo ni validación independiente de 2002–2011.

## Medidas declaradas

Reportar MAE, sesgo, suma de error absoluto por comuna/temporada y agregado de las 54 comunas; todos los meses incluidos. Contrastes emparejados por temporada contra M1 y M1/B, bootstrap 5.000 réplicas semilla 20261114. Solo cuatro bloques por dirección: intervalos exploratorios y muy frágiles. Desglosar ceros observados, Aqua cero/VIIRS positivo y meses VIIRS ≥50; no convertir ceros de conteo en ausencia física de fuego ni cobertura.

Registrar selección por comuna, coeficientes de origen y composición de máscaras. No aplicar ni ampliar compuertas de ocho temporadas con solo cuatro resultados: no producir nuevas habilitaciones. No comparar MAE absoluto entre direcciones como evidencia de superioridad: período y máscara objetivo difieren. Dentro de cada dirección todas las políticas comparten exactamente el mismo objetivo.

## Reproducción y límites

Directorio nuevo `data/processed/temporal_transport_audit/`, manifiesto de hashes de código, helpers, protocolo, entradas y archivos protegidos; fuentes y producción intactas. Tests de disyunción temporal, máscaras/selección por origen y asignación de las políticas. No se usan datos 2020+, CONAF ni NOAA-20/21 para ajustar o elegir candidatos en esta etapa. Todos los PR a `dev`, commits Daniel Quinteros sin firma. Respetar el plazo 21:00 de Santiago mediante el control de deadline existente.
