# Revisión científica 14 — Terra no aporta una mejora estable sobre el afín Aqua ensayado

**Conclusión:** no promover C (Aqua+Terra) ni ampliar compuertas. La clase monotónica regularizada ensayada mejora frente al factor M1, pero **no supera al comparador M1/B** en la evaluación anidada principal. Sus ventajas pequeñas en destinos posteriores no revierten ese resultado ni constituyen una validación independiente. Terra sigue siendo una fuente de información potencial, no una plataforma que deba sumarse a Aqua.

Se ejecutó el [protocolo 14](2026-11-14-science-protocol-14.md), fijado antes de comparar candidatos. El cambio fue una columna de celdas-día Terra separada, con los mismos filtros, grilla/cartografía y máscaras aprendidas por partición. No se modificaron datos base ni se interpretaron las dos plataformas como conteos de eventos independientes.

## Modelo y controles

C ajusta una respuesta lineal con intercepto y pendientes Aqua/Terra no negativas, prior regional Aqua igual al de B y prior Terra cero. Se normalizan los dos predictores con RMS regionales de entrenamiento; λ mantiene los cuatro valores anteriores. El recorte a cero se aplica al estimar, no dentro del objetivo cuadrático de ajuste.

D reemplaza Terra por su mediana comunal de mes calendario aprendida solo en el origen. Usa los mismos priors y normalizaciones de Terra real: añade estacionalidad sin leer el Terra del destino. La comparación C/D diagnostica el aporte temporal bajo estas clases, sin identificar causalidad.

El solver enumera las cuatro caras de las restricciones de pendiente. Se realizaron **89 ajustes** entre evaluación anidada, cuatro pruebas temporales y ajuste completo. El máximo KKT registrado es **4,55×10⁻¹³**, dentro de 1e-6. Con Terra de entrenamiento idénticamente cero, el test reproduce B para cada λ. Se verificaron los componentes Aqua/Terra/intercepto antes del recorte en todas las predicciones guardadas; no se interpretan como atribución causal.

Los controles Aqua/S-NPP, M0, M1, M2 y M1/B reproducen las etapas anteriores en desarrollo, los cuatro casos temporales y los 3.780 pares posteriores. Se conservan el factor completo y la selección B congelada; fuente de referencia `d199e3f7857de17cc8d3b70d392c6c7e60ea1694bb58163de27bf7135dcc5868`.

## Evaluación anidada principal

54 comunas y 5.184 pares mensuales, temporadas 2012–2019. Selección dentro de los siete folds internos, recalculando máscaras, RMS y climatología D sin consultar la temporada externa. La mejora interna >1 % y desempates por mayor regularización son los anteriores.

| Política | MAE mensual | Mejora frente a M1 | MAE en las 14 publicadas |
| --- | ---: | ---: | ---: |
| M1 | 2,04724 | referencia | 3,10654 |
| M1/B | **1,90319** | **7,04 %** | **2,99947** |
| M1/C | 1,93045 | 5,70 % | 3,06625 |
| M1/B/C | 1,92613 | 5,92 % | 3,06713 |
| M1/B/D | 1,90224 | 7,08 % | 2,99577 |

Añadir C a la selección de B **aumenta MAE 1,21 %** frente a B. La diferencia media por temporada es **+0,02294**, desfavorable en 7/8 temporadas; el intervalo exploratorio por bootstrap de temporadas es [+0,00856;+0,03804], 5.000 réplicas y semilla 20261114. Solo ocho bloques y desarrollo adaptativo: no tratarlo como confirmación externa. Frente a la ablación D, B/C también es peor (+0,02390).

La pequeña diferencia favorable de B/D frente a B no constituye un nuevo método recomendado. En el ajuste final completo, D no se selecciona en ninguna comuna; el mapa de elecciones B/D coincide con B. C se selecciona en diez comunas en B/C, pero eso **no habilita ninguna** ni transforma las reglas de evidencia basadas en Aqua en compuertas válidas para dos predictores.

## Señal perdida por Aqua y coste en otros estados

De los **1.152 meses Aqua=0/S-NPP>0**, Terra registra actividad en **196** y también registra cero en 956. Esto limita la información adicional disponible en esa situación. Los conteos no miden oportunidad de observación ni prueban ausencia física de fuego.

| Estado observado | n | MAE B | MAE B/C |
| --- | ---: | ---: | ---: |
| Aqua=0, S-NPP>0, Terra>0 | 196 | 2,20744 | 2,17423 |
| Aqua=0, S-NPP>0, Terra=0 | 956 | 1,72045 | 1,70644 |
| Aqua=0, S-NPP=0, Terra>0 | 195 | 0,24898 | 0,31946 |
| Aqua=0, S-NPP=0, Terra=0 | 2.296 | 0,15217 | 0,16651 |
| S-NPP≥50 | 74 | 19,70854 | 19,98107 |

Hay beneficios parciales en meses donde Aqua no detectó señal, pero aumentan las estimaciones frente a ceros de los otros sensores y empeoran los meses de mayor actividad. Una detección Terra sin S-NPP puede corresponder a otro horario u oportunidad de observación; no se la declara falsa ni se interpreta esta tabla como precisión sobre incendios individuales.

## Transporte temporal: conservar direcciones favorables y desfavorables

Máscara fold_fitted y selección solo en el origen. Se reprodujeron los controles de cuatro temporadas de etapa 8 y los de seis de etapa 10.

| Origen → destino | MAE M1/B | MAE M1/C | MAE M1/B/C | MAE M1/B/D |
| --- | ---: | ---: | ---: | ---: |
| 2012–2015 → 2016–2019 | 2,23913 | 2,27596 | 2,24260 | 2,24424 |
| 2016–2019 → 2012–2015 | 1,86119 | 1,83211 | 1,85656 | 1,85923 |
| 2012–2017 → 2018–2019 | 1,93106 | 1,97891 | 1,95327 | 1,93106 |
| 2014–2019 → 2012–2013 | 1,71630 | 1,76920 | 1,75848 | 1,71630 |

B/C mejora levemente el caso hacia atrás de cuatro temporadas, pero empeora los otros tres frente a B. M1/C mejora M1 en ese caso particular, sin dominar el conjunto de pruebas. No elegir una dirección o tamaño de origen por su resultado ni construir inferencia con dos temporadas de destino.

## Ajuste completo y destinos posteriores ya consultados

Se congelaron coeficientes, climatología y elecciones usando solo 2012–2019 antes de agregar Terra a los pares posteriores existentes. Se conservan la exclusión agosto/septiembre 2020 y la transición enero–junio 2022; no se evalúa aquí la capacidad de suplir una interrupción Aqua. No hay NRT Terra inesperado en los períodos usados.

| Bloque | MAE M1/B | MAE M1/C | MAE M1/B/C |
| --- | ---: | ---: | ---: |
| 2020–2021 descriptivo | 1,96028 | 1,95811 | 1,95334 |
| 2022–2025 diagnóstico | 2,37479 | 2,35488 | 2,36582 |

Las mejoras posteriores de B/C son pequeñas y, en las 14 publicadas, sus estimaciones finales coinciden con B. Esos destinos ya fueron consultados durante el desarrollo y no rescatan el resultado anidado principal. No se cambia selección después de observarlos.

## Decisión y reproducción

Mantener M1 publicado y B como comparador experimental más simple. El resultado rechaza promover **esta clase C y este selector**, no toda utilización futura de Terra. Tampoco prueba que añadir predictores sea perjudicial en general; aquí se exigió pendiente Terra no negativa y un prior concreto. Las bandas y la observabilidad siguen siendo problemas separados de información y comparación de plataformas.

`data/processed/terra_feature_audit/` conserva 5.184 pares anidados, 7.776 bloqueados y 3.780 posteriores, coeficientes por fold y finales, climatología, elecciones, componentes, diagnósticos KKT y manifiesto. Datos base, publicación y artefactos anteriores permanecen idénticos.

```sh
uv run python -m unittest discover -s tests -p 'test_terra_feature.py' -v
uv run python pipeline/terra_feature_audit.py
```

Siete tests nuevos comprueban C(T=0)=B, caras y KKT, objetivo bajo perturbaciones factibles, señal Terra sintética, mediana y normalizaciones de origen, ablación independiente de Terra futuro y exclusión del destino. **79 tests Python pasan**. Todos los controles reales y las sumas de componentes antes de recorte se verificaron. No se generaron nuevas habilitaciones ni números públicos.
