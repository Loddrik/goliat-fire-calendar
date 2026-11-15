# Totales de temporada M1: respuesta científica al issue 48

Este diagnóstico responde al [issue 48](https://github.com/Loddrik/goliat-fire-calendar/issues/48) con las predicciones mensuales LOSO ya existentes, sumadas por temporada julio–junio. No ajusta otro modelo ni modifica los factores, gates o JSON publicados. Las temporadas se nombran por el año de inicio: 2012 incluye julio de 2012 a junio de 2013, y 2019 incluye enero–junio de 2020.

## Contrato y procedencia

Se usa exclusivamente `scientific_audit/outer_predictions.csv`, `policy=published_fixed`, para 54 comunas × 8 temporadas × 12 meses. M1 utiliza las predicciones congeladas de cada temporada reservada; M0 y M2 son controles descriptivos. La población primaria son las 14 comunas habilitadas por los gates anteriores; all54 y remaining40 se mantienen separados. Antes de sumar se exige reproducir MAE, bias, n y Aqua mensuales de M1 contra `eval_loso.csv` con κ0 y su invariancia exacta sobre los siete κ. El código de ajuste anterior se registra por hash y no se importa ni ejecuta.

Para cada comuna/temporada, `Y=ΣSNPP`, `P=ΣM1`, error firmado `P−Y` y absoluto `|P−Y|`. MARE promedia `|P−Y|/Y`; mediana APE calcula su mediana; bias relativo promedia `(P−Y)/Y`. `WAPE=Σ|P−Y|/ΣY` y `bias agregado=Σ(P−Y)/ΣY`, de modo que ponderan de otra forma. Con Y=0 los relativos son NULL; se distinguen P=0 y P>0. La unidad son celdas-día registradas, no incendios distintos ni superficie quemada.

La selección de las 14 y la máscara publicada usaron el mismo desarrollo. Por tanto, el resultado es un **diagnóstico aparente postselección**, no un nuevo holdout ni validación del período 2002–2011. Los valores aproximados del issue eran conocidos antes de este protocolo; no se eligieron fórmulas para reproducirlos.

## Resultados

Los 432 controles mensuales M1 pasaron antes de agregar y M1 fue exactamente invariante a los siete κ. Se exportaron 1.296 filas de temporada (54×8×3 métodos), 162 resúmenes por comuna/método y los 432 controles. La población primaria M1 contiene **112 comuna-temporadas, todas con Y>0**:

| Métrica primaria M1, 14 publicadas | Resultado |
| --- | ---: |
| Mediana APE | 20,34 % |
| MARE | 22,81 % |
| Media del error relativo firmado | −11,46 % |
| WAPE | 20,42 % |
| Bias agregado, Σerror/ΣY | −10,60 % |
| MAE de la suma por temporada | 18,96 celdas-día |
| Error firmado medio de la suma | −9,84 celdas-día |
| Temporadas subestimadas | 76/112 |

Los valores aproximados del issue (~20 % y ~−12 %) son compatibles con estas fórmulas y esta población; la cifra exacta auditada es 20,3355 % y −11,4588 %. No son el mismo estimando que MARE o el ratio de sumas.

| CUT / comuna | Mediana APE | MARE | Bias relativo medio | Temporadas por debajo |
| --- | ---: | ---: | ---: | ---: |
| 08111 · Tomé | 9.1% | 18.8% | -14.4% | 7/8 |
| 08202 · Arauco | 22.4% | 23.3% | -17.1% | 6/8 |
| 08203 · Cañete | 22.8% | 26.2% | -23.9% | 6/8 |
| 08207 · Tirúa | 18.4% | 26.1% | -26.1% | 8/8 |
| 08301 · Los Ángeles | 18.0% | 17.6% | -17.6% | 8/8 |
| 08308 · Quilaco | 11.4% | 18.9% | -0.5% | 3/8 |
| 16102 · Bulnes | 17.4% | 19.1% | -8.5% | 5/8 |
| 16104 · El Carmen | 9.5% | 13.8% | 10.1% | 2/8 |
| 16108 · San Ignacio | 19.9% | 24.0% | -6.8% | 5/8 |
| 16201 · Quirihue | 24.7% | 23.5% | -3.2% | 4/8 |
| 16203 · Coelemu | 36.1% | 37.2% | -12.2% | 5/8 |
| 16301 · San Carlos | 29.9% | 27.1% | -27.1% | 8/8 |
| 16302 · Coihueco | 17.1% | 15.6% | -1.6% | 4/8 |
| 16303 · Ñiquén | 26.9% | 28.0% | -11.6% | 5/8 |

Cada fila contiene ocho temporadas con referencia positiva. Tirúa (08207), San Carlos (16301) y Los Ángeles (08301), señaladas antes del análisis por el issue, quedan por debajo en 8/8 temporadas. Los rangos firmados son respectivamente −56,83 % a −7,21 %, −35,60 % a −2,43 % y −28,11 % a −5,09 %. El extremo aproximado −34 % citado para Los Ángeles no se reproduce con esta fuente fija; no se fuerza su concordancia ni se cambia el contrato.

Las tres comunas centrales de la pregunta del issue y los dos contrastes que ya citaba muestran:

| CUT / comuna | Bias relativo medio | Rango del error relativo firmado | Temporadas por debajo |
| --- | ---: | ---: | ---: |
| 08207 · Tirúa | −26,10 % | −56,83 % a −7,21 % | 8/8 |
| 16303 · Ñiquén | −11,62 % | −50,87 % a +45,45 % | 5/8 |
| 08203 · Cañete | −23,94 % | −67,44 % a +8,26 % | 6/8 |
| 16301 · San Carlos | −27,08 % | −35,60 % a −2,43 % | 8/8 |
| 08301 · Los Ángeles | −17,62 % | −28,11 % a −5,09 % | 8/8 |

Esto confirma subestimación media dentro del solapamiento para las tres primeras, con persistencia distinta. No convierte esos porcentajes en una corrección estimada para la década anterior ni adjudica el salto entre períodos.

Los controles se conservan separados: M0 tiene mediana APE 62,86 % y bias relativo medio −62,41 %; M2, 30,32 % y −18,10 %, ambos en las mismas 112 observaciones. Son comparaciones descriptivas, no una selección nueva de modelo. Para M1/all54, la mediana APE es 29,63 %, media relativa −8,03 % y bias agregado +0,23 %; para remaining40, 35,56 %, −6,77 % y +10,41 %. Un balance regional próximo a cero puede coexistir con sesgo en las 14 y no reemplaza su evaluación. All54 tiene 432 filas, 416 con Y>0 y 16 con Y=0 (11 con P=0 y cinco con P>0 para M1); remaining40 contiene esas 16. No se eliminan del MAE/WAPE, y sus ratios individuales quedan NULL.

Los resultados de otro período, como 2020–2025, y otra población no contradicen por sí solos este diagnóstico ni validan el salto entre décadas.

### Recursos e integridad

El código/entradas/entorno se congeló antes de leer valores (helper `9cf6d85d…`, freeze `c5fb02bf…`, protocolo `41734018…`). El intento 01 terminó la agregación, pero `/usr/bin/time -l` no emitió RSS por una restricción de `sysctl`; su RSS queda **desconocido de forma permanente** y sus archivos se preservan. No se interpretaron las métricas antes de resolver el control de recursos.

La enmienda prospectiva `resource-amendment.json` autorizó una sola repetición instrumental con el mismo helper y sólo otro directorio de salida. Se congeló el wrapper `66e46bcf…` antes del child. El intento 02 finalizó a las **10:34:28 UTC**: el RSS máximo del único child, medido por `resource.RUSAGE_CHILDREN` en bytes Darwin, fue **114.757.632 bytes**, por debajo de 1 GiB. Sus tres CSV son idénticos byte a byte al intento 01 y el resumen es idéntico salvo la hora. La carpeta de ambos intentos y controles ocupó aproximadamente 376 kB, por debajo de 5 MiB. Esta medida certifica sólo el intento 02, no retrospectivamente el 01. No hubo cambios de fórmulas, entradas, modelos ni plazo. Cero fits, solvers y descargas; producción intacta.

El intento de referencia revisable es `data/processed/season_total_audit/attempt-02/`; el envelope de recursos está en su directorio padre. La incorporación de nombres usa exclusivamente el índice público, conserva CUT como clave y no selecciona filas según errores. Su SHA-256 es `fdad4cdb99f9fb394a9fd704f51088defba1d2c21265f485025dccd1ef774174`.

La revisión independiente pasó: reconstruyó las 1.296 filas con los controles originales `eval_loso` (`bias×n`) y denominadores SNPP del Parquet mensual canónico con máscara, sin usar las predicciones mensuales primarias como referencia. Verificó las 432 filas M1, las 112 primarias, nueve resúmenes población/método, 162 resúmenes comuna/método y los 432 controles mensuales. El dictamen separado se conserva en `docs/reviews/2026-11-15-season-total-independent-review.md`.


## Qué permite decidir

Un MAE mensual no valida automáticamente la suma anual: los errores mensuales pueden cancelarse o acumularse. Tampoco permite construir una banda de error para la suma sin comprobar su dependencia temporal. Una cifra de error de temporada durante 2012–2019 caracteriza esa escala en ese período; no demuestra transporte a 2002–2011.

La razón entre promedios de dos décadas mezcla cambios reales y cambios del operador de observación, además del método de reconstrucción. Un sesgo de M1 dentro del solapamiento demuestra una limitación descriptiva donde existe referencia; no identifica qué fracción del salto de Tirúa, Ñiquén o Cañete es artificial. Sin observaciones comparables anteriores a 2012 no se puede resolver esa atribución con esta tabla.

No se inventa un umbral anual para retirar comunas después de mirar estos resultados. Los gates originales evaluaban la reconstrucción mensual, no certificaban la continuidad del total anual entre décadas. Se recomienda conservar por ahora la landing limitada a temporadas observadas y presentar la reconstrucción histórica con una divulgación explícita. Una política de habilitación anual requeriría criterios propios fijados antes de una evaluación posterior; aquí no se cambian habilitaciones.

## Entrega y divulgación propuesta

Las salidas separan la tabla de temporadas, las métricas por comuna, los controles mensuales y los resúmenes de poblaciones. Si se incorporan metadatos al producto, conviene usar nombres inequívocos como `season_mare`, `season_median_ape`, `season_bias_rel`, `season_wape`, junto con período, N, unidad y condición postselección; `season_mae_rel` por sí solo no identifica la fórmula.

Texto propuesto para `docs/method.md` §6, sujeto a integrar las cifras revisadas: «Los totales julio–junio de M1 se auditaron sumando sus predicciones LOSO de 2012–2019, con máscara publicada fija. Es un diagnóstico aparente de las comunas seleccionadas con ese mismo desarrollo; no valida la reconstrucción de 2002–2011, una banda anual ni la causa del salto entre sensores». Esta tarea no modifica ese archivo ni publica automáticamente el tramo histórico en la landing.
