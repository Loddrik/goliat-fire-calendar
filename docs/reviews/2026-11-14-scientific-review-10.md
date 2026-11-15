# Revisión científica 10 — más entrenamiento recupera parte de la mejora, sin resolver la estabilidad

**Conclusión:** la degradación hacia atrás del protocolo 8 no demuestra que toda calibración flexible sea inútil para reconstruir el pasado. Con seis temporadas de origen aparecen mejoras; con cuatro, su composición y la máscara influyen considerablemente. No hay evidencia suficiente para sustituir M1 publicado ni escoger retrospectivamente la combinación más favorable.

El [protocolo 10](2026-11-14-science-protocol-10.md) se fijó antes de ejecutar los 64 casos. Se usaron dos destinos fijos de dos temporadas: 2012–2013, con origen disponible 2014–2019; y 2018–2019, con origen disponible 2012–2017. En cada dirección se evaluó el origen completo de seis temporadas y **las quince combinaciones de cuatro**, sin selección según el destino. Cada caso mantuvo la selección LOSO dentro de su origen. Las familias, hiperparámetros y reglas permanecieron congelados.

M1 es aquí la familia de factor regional **reajustada solo sobre el origen de cada caso**, igual que en el protocolo 8. No es aplicar el factor publicado 2,353 sin volver a estimarlo. Las familias están congeladas; sus coeficientes y elecciones comunales se aprenden en cada partición. Ninguna de estas evaluaciones cambia el factor de producción.

## Control primario: objetivo idéntico con máscara fija

La máscara se aprende exclusivamente con **temporadas de índice <2012**, es decir, observaciones anteriores a julio de 2012, y contiene **7 celdas**. Es un control de disponibilidad temporal; no equivale a la máscara publicada de 223 celdas ni demuestra que haya retirado todas las fuentes persistentes conocidas después. Tampoco es una máscara necesariamente anterior al inicio de VIIRS: puede usar enero–junio de 2012, correspondientes a temporada 2011.

Dentro de cada dirección se exigió igualdad exacta de comuna, temporada, mes, Aqua y S-NPP entre los dieciséis destinos. Así, la diferencia de error entre orígenes se calcula sobre el mismo objetivo. No comparar MAE absoluto entre direcciones o contra el contrato de máscara aprendida, pues esos objetivos difieren.

Reducción porcentual de MAE respecto al M1 del **mismo caso**; valores negativos significan empeoramiento. Todos los meses de las 54 comunas, incluidos ceros de conteo.

| Dirección | Política | Seis temporadas | Mediana de las 15 combinaciones de cuatro | Rango de las 15 | Combinaciones que mejoran a M1 |
| --- | --- | ---: | ---: | --- | ---: |
| Atrás | M1/B | **4,03 %** | 0,75 % | [−4,19 %;5,83 %] | 11/15 |
| Atrás | M1/H | **4,15 %** | 0,30 % | [−3,37 %;5,48 %] | 9/15 |
| Atrás | M1/P | **3,87 %** | 0,61 % | [−8,08 %;5,74 %] | 9/15 |
| Atrás | M1/B/P | **3,70 %** | 0,48 % | [−9,18 %;5,42 %] | 9/15 |
| Adelante | M1/B | **11,49 %** | 6,90 % | [−0,36 %;9,91 %] | 14/15 |
| Adelante | M1/H | **13,26 %** | 6,53 % | [0,70 %;12,52 %] | 15/15 |
| Adelante | M1/P | **11,51 %** | 7,65 % | [1,95 %;14,16 %] | 15/15 |
| Adelante | M1/B/P | **10,89 %** | 6,57 % | [0,61 %;10,15 %] | 15/15 |

Los quince subconjuntos se superponen; las fracciones de mejora no son probabilidades independientes de éxito. Se conserva la distribución completa, no solo el máximo. Más temporadas cambian también normalización y estabilidad de selección; este diseño no identifica una única causa de la recuperación.

El resultado agregado hacia atrás también puede ocultar diferencias entre sus dos temporadas. Con seis temporadas y máscara fija, M1/B empeora **0,51 %** en 2012 y mejora **7,81 %** en 2013; M1/B/P empeora **1,39 %** y mejora **7,94 %**, respectivamente. H mejora 1,12 % y 6,67 %. Con dos bloques no se construyeron intervalos bootstrap ni se trataron las comunas como réplicas independientes.

## Contrato secundario: máscara aprendida dentro del origen

Se recalcula la máscara en cada origen y cada fold interno, conservando únicamente las temporadas permitidas y las anteriores a 2012. Sus tamaños, considerando todos los ajustes, varían de **40 a 187 celdas**. Aquí cambiar el origen también cambia el conjunto objetivo: los MAE absolutos entre casos no miden por sí solos una mejora del modelo. Los porcentajes siguientes comparan cada candidato con el M1 de su propio caso.

| Dirección | Política | Seis temporadas | Mediana de las 15 combinaciones de cuatro | Rango de las 15 | Combinaciones que mejoran a M1 |
| --- | --- | ---: | ---: | --- | ---: |
| Atrás | M1/B | **5,14 %** | −0,27 % | [−5,25 %;5,46 %] | 6/15 |
| Atrás | M1/H | **4,37 %** | −0,58 % | [−3,67 %;5,08 %] | 6/15 |
| Atrás | M1/P | **0,56 %** | −0,81 % | [−8,38 %;5,01 %] | 5/15 |
| Atrás | M1/B/P | **2,17 %** | −0,35 % | [−5,54 %;5,42 %] | 6/15 |
| Adelante | M1/B | **6,06 %** | 3,27 % | [−4,40 %;6,90 %] | 13/15 |
| Adelante | M1/H | **8,51 %** | 3,01 % | [−4,12 %;7,85 %] | 12/15 |
| Adelante | M1/P | **6,21 %** | 3,84 % | [−1,29 %;10,25 %] | 14/15 |
| Adelante | M1/B/P | **6,50 %** | 2,68 % | [−3,28 %;7,01 %] | 14/15 |

Con seis temporadas, M1/B mejora hacia atrás en ambas temporadas del contrato secundario: **6,90 % en 2012** y **3,62 % en 2013**. Aun así, ampliar la política a M1/B/P reduce la mejora agregada de 5,14 % a 2,17 %. La selección ampliada tampoco supera a B en el agregado primario hacia atrás. Esto favorece estudiar una alternativa más simple antes que publicar automáticamente la familia con mejor LOSO global.

## Qué cambia en la evaluación

1. La advertencia del protocolo 8 sigue siendo válida: cuatro temporadas y una dirección favorable no bastan para demostrar reconstrucción histórica robusta. Este diagnóstico añade que el resultado depende del conjunto de entrenamiento y del contrato de máscara.
2. La ventaja de M1/B/P en LOSO no se convierte en una dominancia sobre B al transportar hacia atrás. Más complejidad no resuelve automáticamente el problema relevante para años anteriores a VIIRS.
3. No se escoge la máscara de siete celdas por sus mejoras mayores: deja una definición distinta de actividad y puede retener fuentes persistentes que la máscara publicada elimina.
4. No se crean habilitaciones ni se cambia producción. Todos estos destinos ya forman parte del desarrollo retrospectivo; el estudio no valida 2002–2011 de manera independiente.
5. El siguiente diagnóstico debe congelar ajustes completos sobre 2012–2019 y revisar discrepancia temporal e incertidumbre en 2020–2021 **descriptivamente**, separando 2022+ por deriva de Aqua. No volver a presentar períodos ya consultados como prueba nueva.

## Evidencia y reproducción

`data/processed/training_size_audit/` conserva los **82.944 pares mensuales** de los 64 casos, errores por comuna/temporada, agregados por caso y temporada destino, todas las selecciones y tamaños/hashes de máscara. Los Parquet comprimen las predicciones y errores para evitar CSV duplicados extensos. El manifiesto identifica código, helpers, entorno, protocolo y archivos protegidos.

El máximo KKT Huber de los ajustes finales es **9,9997×10⁻⁷**, dentro de la tolerancia preestablecida; todos los ajustes internos también exigen convergencia antes de continuar. Los controles verifican exclusión del destino del ajuste/máscara y objetivo primario idéntico. Se preservaron todos los hashes de fuentes, producción y auditorías anteriores. **51 tests Python pasan**, incluidos cuatro nuevos de diseño completo, contratos de máscara y detección de cambios del objetivo.

```sh
uv run python -m unittest discover -s tests -p 'test_training_size.py' -v
uv run python pipeline/training_size_audit.py
```

Los resultados son discrepancias entre conteos de celdas-día, no precisión sobre incendios individuales, superficies quemadas o ausencia física de fuego. No se utilizaron CONAF, NOAA-20/21 ni datos 2020+ para seleccionar candidatos en esta etapa.
