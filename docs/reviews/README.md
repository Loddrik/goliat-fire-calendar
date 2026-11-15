# Evidencia de investigación científica

Este índice distingue el modelo publicado de los experimentos de desarrollo. El producto conserva **M1**, el factor regional aproximado 2,35 y sus gates de publicación en 14 de 54 comunas. Ningún resultado posterior de esta rama promueve automáticamente otro modelo o amplía esa cobertura.

En las revisiones, **B** identifica políticas afines de investigación, **G/E_coherent** la asignación que conserva ΣB sobre 54 comunas y **held** el dominio reservado dentro de cada experimento. Esas etiquetas no son nuevas versiones desplegadas. La unidad mensual es celda-día registrada por plataforma, agregada por comuna; no incendios, área quemada o verdad física. Cada protocolo define su máscara, calendario y contrato: no comparar MAE absolutos entre paneles diferentes ni sumar porcentajes de mejoras alternativas.

Para una explicación visual del proceso, los consejos y los límites: [informe HTML hasta35, con seis diagramas](../artifacts/science-observation-plan-2026-11-15.html). El [informe anterior](../artifacts/science-session-2026-11-14.html) conserva el snapshot 16–20A y los dos casos L2.

| Pregunta/etapa | Resultado y alcance | Evidencia principal |
|---|---|---|
|17–18: separar ceros/cantidades y reconciliarCDF|18 reduce MAE 1,903194→1,797939 frente a B sobre su mismo panel; totales iguales aB por construcción, con costes por grupo. No promoción.|[Revisión18](2026-11-14-science-review-18.md)|
|21: transporte entre región y período|Las direcciones no se comportan uniformemente. Máscara pre2012 de 6 celdas, distinta de 223 del ajuste completo.|[Revisión21](2026-11-14-science-review-21.md)|
|23: contexto de cobertura de suelo|Primaria desfavorable: +0,1453% MAE, mejora 1/4 regímenes. Sensibilidades no sustituyen primaria.|[Revisión23](2026-11-15-science-review-23.md)|
|24C: contrato de datos|La ventaja global conserva signo sobre 3456 filas comunes; fragilidad de las 14 y los extremos permanece. Replay offline auditado.|[Replay y límites](2026-11-15-contract-model-sensitivity-replay.md)|
|24B–30B: soporte nominal continuo|Fallos geométricos preservados; cambios de motor/origen y gates locales no validaron el operador completo.|[Dictamen30B](2026-11-15-centered-ledger-revalidation-review.md)|
|32A/B: puntos exactos y conflicto local|Propiedad nominal puntual verificada; último par tiene microárea positiva exacta, sin cota del error global. Nuevo estimando, no reparación del continuo.|[Revisión32A](2026-11-15-point-ownership-audit-review.md) · [32B](2026-11-15-exact-local-overlay-review.md)|
|33: etiquetas sobre consultas prefijadas|898704 filas verificadas independientemente. Jaccard conocido 2023=15%; 2019 null. Muestreo 500 m pierde representación de positivos nativos. No superioridad de sensores.|[Reporte33](2026-11-15-discrete-state-comparison-report.md) · [Revisión independiente](2026-11-15-discrete-state-comparison-independent-review.md)|
|35A: presupuestos separados|Primaria negativa:ΔMAE held R−G=+0,041975, mejora 1/4. Complemento separado completa diagnósticos B/C omitidos, sin editar original.|[Reporte35A](2026-11-15-group-budget-report.md) · [Revisión independiente](2026-11-15-group-budget-independent-review.md)|
|36: adyacencia diaria y placebo|Cubo íntegro: 5184 claves, 10368 controles Aqua exactos; D real=1 en105meses y placebo en59,110discordantes. Integridad verificada, sin utilidad predictiva demostrada.|[Reporte36](2026-11-15-daily-adjacency-report.md) · [Revisión independiente](2026-11-15-daily-adjacency-independent-review.md)|
|37: contexto diario como predictor|No cumple el doble criterio: real−placebo −0,004927; real−G21 +0,010794. Sin sustitución de G21 ni cambio de semilla o κ.|[Reporte37](2026-11-15-daily-context-model-report.md) · [Revisión independiente](2026-11-15-daily-context-independent-review.md)|

## Cómo se decide y revisa

Los consejos conservan los criterios 30% validez, 25% información discriminante, 20% factibilidad/reproducción/coste, 15% transporte/selección y 10% interpretación, con límites no compensables. Sus rangos son juicios subjetivos solapados, no probabilidades o intervalos de confianza. Los [planes 24](2026-11-15-joint-plan-24.md), [31](2026-11-15-joint-plan-31.md) y [35](2026-11-15-joint-plan-35.md) preservan críticas adversarias, ratificaciones y disensos. No se presenta todo el consejo como ciego: 35 ingeniería había leído el voto estadístico.

Cada estudio conserva protocolo previo, freeze de código/entradas/predicciones según su etapa, resultados y manifiestos, junto a una revisión de alcance declarado. Un pase de ingeniería o identidades acredita ese cálculo; no demuestra observabilidad física, calibración prospectiva o aptitud operacional. Las fechas 2020+ y estos dominios ya consultados se describen como desarrollo retrospectivo, sin anunciarlos como holdout fresco.

G1 físico, tiempos de exposición por píxel, PSF y semántica específica MYD14 Suspect siguen pendientes. Los [hallazgos documentales](2026-11-15-modis-quality-followup.md) no eliminan esas limitaciones. Desconocido no es 0; detección no es incendio individual.

## Revisión incremental y reproducción

Los PRs se dirigen a dev y se encadenan: [#55](https://github.com/Loddrik/goliat-fire-calendar/pull/55), [#56](https://github.com/Loddrik/goliat-fire-calendar/pull/56) y [#57](https://github.com/Loddrik/goliat-fire-calendar/pull/57). Cada descripción incluye comparación propia para revisar el incremento sin confundirlo con toda la cadena. Los enlaces no certifican merges futuros ni despliegues.

Las pruebas puras se ejecutan con `.venv/bin/python -m unittest discover -s tests -q` tras instalar las dependencias bloqueadas. Los drivers de investigación tienen caps absolutos y fuentes congeladas: no se elude el reloj para repetirlos. Su replay necesita las entradas y condiciones declaradas, o un protocolo nuevo explícito. Algunos verificadores preservados contienen rutas locales; se guardan como evidencia de lo ejecutado, no como promesa de portabilidad. Los originales raw no están completos en este checkout: disponibilidad de derivados y reproducibilidad íntegra de adquisición son afirmaciones distintas. Credenciales y datos privados no forman parte de este índice.
