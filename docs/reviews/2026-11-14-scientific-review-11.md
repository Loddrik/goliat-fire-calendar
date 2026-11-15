# Revisión científica 11 — ajuste congelado y límites temporales de error y bandas

**Conclusión:** mantener M1 y los radios publicados. Los candidatos mejoran la discrepancia agregada del bloque descriptivo 2020–2021, pero su ventaja no es estable por territorio o temporada y todos empeoran en la temporada 2025. Las bandas alternativas q80 no garantizan cobertura futura del 80 %. El estudio conserva los resultados favorables y desfavorables, sin elegir un candidato o ampliar una banda tras observarlos.

Se ejecutó el [protocolo 11](2026-11-14-science-protocol-11.md), fijado antes de evaluar 2020+ de estas políticas. Se congelaron coeficientes, selección comunal y calibración con 2012–2019. **2020–2021 ya había sido consultado y no es un holdout nuevo**; 2022–2025 es diagnóstico separado. Ninguno modifica el ajuste ni las compuertas de publicación.

## Ajuste reproducible antes de consultar destinos

- Las 223 celdas de la máscara y el factor completo **2,352954072125397** reproducen exactamente la publicación actual.
- Se unieron 5.184 registros OOF de H y P con claves y conteos Aqua/S-NPP idénticos. La elección final usa solo esos registros, reglas y regularizaciones existentes. La calibración de radios usa las **estimaciones de política anidadas**, cuya elección se hizo dentro de cada fold externo; no las estimaciones elegidas sobre las mismas etiquetas de calibración.
- La selección M1/B elige algún B en 36 comunas; M1/H en 35; M1/P algún P en 38. Son elecciones internas de investigación, **no nuevas habilitaciones**. Las 14 comunas publicadas se mantienen como subgrupo fijo.
- Los coeficientes y referencias se guardan y restauran verificando hashes y una firma del modelo. Todas las estimaciones y métricas se mantuvieron idénticas tras usar los coeficientes restaurados, sin volver a entrenar.

Firma del ajuste y radios congelados: `d199e3f7857de17cc8d3b70d392c6c7e60ea1694bb58163de27bf7135dcc5868`. El esquema de artefacto es versión 1; se rechazan modificaciones de sus archivos. No es una firma criptográfica de autoría, sino una huella reproducible del estado científico.

## Panel posterior y transición orbital

Se comparan **Aqua y S-NPP**, no la serie reciente de publicación basada en NOAA-20. Son 3.780 pares comuna/mes: 1.188 en temporadas 2020–2021 (22 meses por comuna, excluidos agosto y septiembre de 2020) y 2.592 en temporadas 2022–2025 (48 meses). Todas las ventanas SP solicitadas están completas en el inventario y no hay celdas-día NRT; **la oportunidad de observación sigue siendo desconocida**.

[NASA sitúa la deriva libre de Aqua desde enero de 2022](https://science.nasa.gov/mission/a-train/). Enero–junio de 2022 pertenece a temporada 2021. Por eso el bloque heredado se divide además en 864 pares anteriores al año calendario 2022 y 324 de transición. No se atribuye causalmente a la deriva una diferencia que también mezcla estacionalidad, intensidad de actividad, procesamiento y otros cambios.

## Error puntual

MAE por comuna/mes, sobre las 54 comunas e incluidos ceros de detección. Las reducciones se calculan contra el M1 del mismo bloque. M1 usa el factor completo congelado; los candidatos mantienen las elecciones fijadas antes de consultar el destino.

| Método | 2020–2021: MAE | Reducción frente a M1 | 2022–2025: MAE | Reducción frente a M1 |
| --- | ---: | ---: | ---: | ---: |
| M0 Aqua sin escalar | 2,5741 | −21,21 % | 3,0239 | −24,39 % |
| M1 | 2,1237 | referencia | 2,4310 | referencia |
| M2 climatología | 2,7677 | −30,32 % | 3,9730 | −63,43 % |
| M1/B | 1,9603 | **7,69 %** | 2,3748 | **2,31 %** |
| M1/H | 1,9590 | **7,75 %** | 2,4049 | **1,07 %** |
| M1/P | 2,0670 | **2,67 %** | 2,3668 | **2,64 %** |
| M1/B/P | 1,9635 | **7,54 %** | 2,3509 | **3,30 %** |

La mejora de las 54 comunas no describe necesariamente a las 14 que hoy tienen reconstrucción. En ese subgrupo, las reducciones de 2020–2021 son **0,69 % con B, 2,06 % con H, −1,21 % con P y 1,30 % con B/P**. En los meses anteriores a enero de 2022, los cuatro candidatos presentan MAE mayor que M1 en las 14: entre 2,49 % y 5,07 % de deterioro. No seleccionar el ámbito territorial favorable como resultado principal.

Reducción de MAE por temporada sobre las 54 comunas:

| Temporada inicial | M1/B | M1/H | M1/P | M1/B/P |
| --- | ---: | ---: | ---: | ---: |
| 2020 | 6,05 % | 6,34 % | 1,56 % | 5,29 % |
| 2021 | 8,83 % | 8,73 % | 3,44 % | 9,10 % |
| 2022 | 7,11 % | 4,81 % | 8,96 % | 9,47 % |
| 2023 | 10,29 % | 10,39 % | 14,18 % | 10,46 % |
| 2024 | 0,23 % | −1,54 % | 0,34 % | 1,64 % |
| 2025 | **−8,31 %** | **−8,43 %** | **−12,43 %** | **−9,17 %** |

La temporada 2025 abarca julio de 2025 a junio de 2026. Estos resultados no son mediciones de incendios individuales ni evidencia de su causa; son discrepancias entre celdas-día detectadas por plataformas distintas. Tampoco validan 2002–2011 ni justifican corregir retrospectivamente el factor para mejorar el último año.

## Cobertura y anchura: el nivel nominal no es una garantía

Radios q80: percentil 80 del error absoluto en meses S-NPP activos de la política anidada OOF, aprendido solo con 2012–2019. Cada comuna tiene entre **4 y 92 meses activos de calibración**, mediana 49: varios cuantiles locales descansan en muestras pequeñas. La máscara de calibración se aprende por fold y el destino usa la máscara final; esa diferencia forma parte del transporte evaluado.

Intervalos descriptivos `[max(0, estimación−radio), estimación+radio]`. El estado activo solo determina el análisis de cobertura, no selecciona el radio al estimar un mes futuro. El error típico publicado se evalúa con el mismo redondeo a una décima de punto y radio que usa `publish.py`.

Cobertura en **meses activos S-NPP de las 14 comunas habilitadas**, con anchura media en celdas-día:

| Banda | 2020–2021: cobertura (n=195) | Anchura | 2022–2025: cobertura (n=447) | Anchura |
| --- | ---: | ---: | ---: | ---: |
| M1 error típico publicado | **64,10 %** | 6,85 | **69,13 %** | 6,60 |
| M1 q80 OOF | 78,46 % | 9,59 | 77,85 % | 9,22 |
| M1/B q80 OOF | 77,95 % | 9,72 | 77,63 % | 9,47 |
| M1/H q80 OOF | 78,97 % | 9,63 | 78,08 % | 9,35 |
| M1/P q80 OOF | 79,49 % | 9,47 | 78,52 % | 9,21 |
| M1/B/P q80 OOF | 77,44 % | 9,70 | 78,97 % | 9,41 |

No comparar el error típico con q80 como si tuvieran el mismo nivel nominal. Los q80 son más anchos y tampoco aseguran 80 % futuro. Sobre **todas las 54 comunas**, q80 de B cubre 78,96 % de los 599 meses activos heredados y 74,70 % de los 1.257 diagnósticos; B/P cubre 77,63 % y 74,30 %. El subgrupo publicado tiene otro perfil de señal.

La mezcla temporal oculta además una caída descriptiva: q80 de B en las 54 comunas cubre **83,57 %** de meses activos antes de enero de 2022 y **68,16 %** en enero–junio de 2022. En las 14, el error típico publicado pasa de **70,29 %** a **49,12 %**. Son períodos de distinta composición estacional y actividad; no un experimento causal de órbita. No recalibrar los radios con estos resultados y afirmar después que quedaron validados.

Los datos completos incluyen cobertura en todos los meses, que suele ser mayor porque abundan los ceros. Se informa separadamente, junto al denominador y a los casos sin calibración; no sustituye la cobertura de meses activos. No se construyen intervalos inferenciales con solo dos temporadas ni se trata cada mes/comuna como observación independiente.

## Corrección documental de controles heredados

El auditor reproduce todos los controles por comuna en `eval_final.csv`, incluidos M0, M1, M2 y el A(κ=100) preexistente. El MAE de la **suma regional mensual** es:

| Control | MAE regional mensual reproducido |
| --- | ---: |
| M0 | 132,7273 |
| M1 | 45,7120 |
| M2 | 82,6818 |
| A(κ=100) heredado | 45,6301 |

El documento de método citaba 133/44/86/45. Se actualiza a **132,7/45,7/82,7/45,6**, porque las cifras anteriores no se reproducen todas con los datos congelados actuales. A se usa aquí únicamente para auditar un control heredado, no como nueva política elegida sobre 2020+. Estos errores regionales pueden compensar discrepancias entre comunas; no son la misma métrica que el MAE local de las tablas principales.

## Decisión y reproducción

Mantener los parámetros, radios y 14 compuertas existentes. La siguiente investigación puede evaluar la dependencia del error con el nivel de actividad y comparar reglas de anchura fijadas de antemano, con evaluación anidada; no aumentar el radio hasta alcanzar una cobertura deseada en este mismo destino. Una mejora de punto no resuelve automáticamente cobertura, continuidad NOAA o validez histórica.

Artefactos en `data/processed/frozen_temporal_audit/`: modelo congelado restaurable, referencias, coeficientes, elecciones, 270 radios, 3.780 pares mensuales, errores y cobertura, resumen y hashes. Los archivos publicados, datos base y auditorías anteriores permanecen intactos.

```sh
uv run python -m unittest discover -s tests -p 'test_frozen_temporal.py' -v
uv run python pipeline/frozen_temporal_audit.py
```

Restauración sin entrenamiento:

```python
import sys
sys.path.insert(0, "pipeline")
from frozen_temporal_audit import load_frozen, estimate
model = load_frozen()
# estimate(frame, model): frame agregado con cut, season, m, g, aqua y snpp de diagnóstico.
# snpp se conserva para evaluar; no participa en la fórmula de estimación.
```

Nueve tests nuevos comprueban objetivos futuros sin efecto en estimaciones/radios, exclusión temporal, unión OOF estricta, radio calibrado solo en meses activos pasados, frontera calendario, ventanas solicitadas, cobertura, controles heredados y restauración con rechazo de manipulación. **60 tests Python pasan**. El modelo restaurado reproduce exactamente las estimaciones y no cambia de firma al evaluar los destinos. No se usó CONAF ni un puente NOAA para ajustar estas políticas.
