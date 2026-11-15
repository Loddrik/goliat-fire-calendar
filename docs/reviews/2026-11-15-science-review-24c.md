# Revisión científica24C — sensibilidad contractual de decisiones congeladas

**Resultado:** la ventaja MAE global coherente frente a B conserva signo y no cruza la materialidad práctica prefijada al sustituir C→O. Esto no resuelve sus costes territoriales: en las14 comunas publicadas la ventaja casi desaparece y el coste en extremos persiste. No se promueve ningún modelo ni contrato.23 primario continúa negativo.

Protocolo congelado commit1c92bc8; plan conjunto24. Cap04:29:28Z–05:29:28Z incluye revisión y no se reinicia. Código/510 fuentes protegidas congelados antes de nuevas métricas a 2026-11-15T04:33:27.286387+00:00. Freeze SHA256 `5a7c732ac84dc519c34a097513f634d6a824ab9d24fb9ec58a7fe8d7acedf868`. Siete pruebas sintéticas pasaron antes del freeze. Sin fits, descargas, credenciales o cambios de producción.

## Identidades antes de pérdidas

- 3456 filas=54 comunas×64 meses, Jul2020–Dic2025 excluyendo Ago/Sep2020. Las324 filas Jan–Jun2026 excluidas por20A no se rellenan con cero. No selección por actividad.
- 108CSV:54 Aqua/MODIS/confianza30–100 y54 N20/VIIRS/n–h; todos día/type0. Hash/tamaño/filas/plataforma/instrumento/CUT/nombre/cuadrícula/año/fuente/versión verificados. Hashes de geometría, manifest, índice y publicaciones, series de detecciones/celdas-día reproducidos.
- NOAA20 O reproduce20A O0; C reproduce20A/19 Cmaskedall. Aqua C y las seis funciones reproducen18/19 en las mismas filas. Modelo y helpers coinciden con los manifests históricos.
- Predicciones invariantes al eliminar/cambiar etiquetas destino. Modelo no mutado. Ambos inputs reconciliados en54 comunas por mes antes de subgrupos.
- 128 reconciliaciones: error absoluto máximo de presupuesto9.094947e−13, residual KKT2.220446e−16, riesgo L1 esperado bajo CDF no excede B. Presupuesto y MAE regional iguales a B en54 son identidad construida, no habilidad adicional.

## Comparación primaria

Primera letra=input Aqua, segunda=target NOAA20. CC/OO son extremos; CO/OC son mezclas diagnósticas. Target de error es observación NOAA20 bajo cada contrato, nunca fuego físico ni precisión SNP.

| Contrato | MAE B | MAE coherente | Δ coherente−B | Sesgo B/coherente |
|---|---:|---:|---:|---:|
| CC | 2.044547741 | 1.947497693 | -0.097050047 | -0.019013/-0.019013 |
| CO | 2.054564980 | 1.957641849 | -0.096923131 | -0.037531/-0.037531 |
| OC | 1.988030624 | 1.898168338 | -0.089862287 | -0.137870/-0.137870 |
| OO | 1.997093600 | 1.907817350 | -0.089276251 | -0.156388/-0.156388 |

τ=.01 MAE(B_CC)=0.020445477. ΔOO−ΔCC=+0.007773797; |cambio|<τ, sin inversión de signo. Esta regla práctica no es significación, intervalo de confianza ni evidencia de equivalencia física.

## Guardrails territoriales y extremos

No se sustituye la primaria por un subgrupo favorable. Los valores siguientes son descriptivos; no se crea un umbral de promoción territorial.

| Grupo/población fija | N | ΔCC | ΔOO | Sesgo coherente CC→OO |
|---|---:|---:|---:|---:|
| all54/all_months | 3456 | -0.097050047 | -0.089276251 | -0.019013→-0.156388 |
| all54/YC_50_plus_FIXED | 53 | -2.999389344 | -2.995570026 | +3.889030→+2.916454 |
| all54/YC_zero | 1789 | +0.025100419 | +0.027699327 | +0.411711→+0.323033 |
| all54/both_C_zero | 1690 | +0.022031040 | +0.018709747 | +0.242034→+0.222666 |
| published14/all_months | 896 | -0.072307311 | -0.009143048 | -0.317074→-0.486835 |
| published14/YC_50_plus_FIXED | 21 | +0.691615288 | +1.111559429 | +4.852549→+3.679541 |
| published14/YC_zero | 310 | -0.017255913 | +0.009549530 | +0.665254→+0.547773 |
| published14/both_C_zero | 289 | +0.001985490 | -0.001196755 | +0.450068→+0.436506 |
| remaining40/all_months | 2560 | -0.105710005 | -0.117322872 | +0.085309→-0.040732 |
| remaining40/YC_50_plus_FIXED | 32 | -5.421611134 | -5.690873731 | +3.256721→+2.415679 |
| remaining40/YC_zero | 1479 | +0.033978352 | +0.031503544 | +0.358568→+0.275927 |
| remaining40/both_C_zero | 1401 | +0.026166061 | +0.022816085 | +0.199120→+0.178555 |

Las14 comunas publicadas retienen una mejora global pequeña en OO; sus21 extremos empeoran frente a B en ambos contratos. Los40 restantes concentran la mejora de extremos. En los ceros de54 se conserva un coste. No esconder estas diferencias detrás del promedio ni atribuirlas causalmente a una transformación.

Extremos primarios siempre YC≥50:53 filas. YO≥50 suplementario también53; intersección53, entradas0/salidas0. Esta coincidencia observada no altera la regla de población congelada. No son episodios independientes: son meses/comunas repetidos.

## Cotas verificadas y separación de ejes

Para cada input fijo, cambio de Δ al cambiar target acotado por2media|YC−YO|. Global440/3456=.127314815, reproducido exactamente a tolerancia1e−12. Esta cota es potencialmente holgada y no certifica equivalencia. Para cada target fijo, cambio de Δ acotado por media|EcohC−EcohO|+media|BC−BO|, con presupuestos propios.

| Población todos los meses | Cota target propia | Cota input propia | Cambio target con inputC | Cambio input con targetC |
|---|---:|---:|---:|---:|
| all54 | 0.127314815 | 0.316046284 | 0.000126916 | 0.007187761 |
| published14 | 0.156250000 | 0.379764919 | 0.009629415 | 0.055434903 |
| remaining40 | 0.117187500 | 0.293744762 | 0.003198958 | 0.009698739 |

Todas las cotas también se verifican para los estratos fijos y YO≥50 suplementario; consultar summary.json. La cota440/3456 no se reutiliza en14/40 ni extremos. La descomposición es algebraica, dependiente del camino, no atribución causal instrumental.

## Decisión y límites

Cerrar C como sensibilidad definicional acotada: la primaria global no sugiere inversión contractual en este panel, pero los costes y la fragilidad de14 impiden una conclusión homogénea. Continuar B, el ledger observacional nominal, sin descartar cobertura/calidad. No cambiar contrato según ranking ni iniciar otra grilla. E documental puede cerrar una ruta de observabilidad compuesta.

C/O difieren en filtros, cuadrícula, máscara, geografía y cohortes; ambos asignan centros de celda. Reaplicar el modelo SNP congelado a Aqua O es sensibilidad de entrada, no recalibración válida ni producto nuevo. No se prueba bridge SNP→NOAA20, ausencia de actividad, PSF, causalidad o oportunidad física. Disponibilidad del archivo/request no es cobertura útil; G1 físico permanece false. Fechas previamente exploradas no se convierten en holdout fresco al cambiar variables. Ninguna mejora porcentual se suma a estudios16–23.

## Artefactos reproducibles

- `data/processed/contract_model_sensitivity_audit/code-freeze.json`: hashes previos de código, protocolo y510 fuentes.
- `source_csv_ledger.csv`:108 CSV de origen validadas.
- `paired_predictions.parquet`:3456 filas, ambos inputs/targets y seis funciones por input.
- `metrics.csv`, `summary.json`: factorial completo, seis métodos secundarios,14/40, sesgo, extremos y cotas.
- `allocation_checks.csv`:128 presupuestos/riesgos/KKT.
- `manifest.json`: hashes de salida y constatación de entradas previas sin cambios.
- `tests/test_contract_model_sensitivity_audit.py`: siete pruebas sintéticas; invariancia de etiquetas destino adicional realizada en el run real.

Revisión independiente completada sin bloqueantes dentro del cap: siete tests, hashes de510fuentes,128conciliaciones, métricas completas3grupos×7poblaciones×4contratos×6métodos y todas las cotas propias reconstruidas desde predicciones. El cap y las pruebas no se reinterpretan como validación física.
