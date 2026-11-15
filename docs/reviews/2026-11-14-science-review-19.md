# Revisión científica 19 — sensibilidad al referente NOAA-20

La ganancia local de la asignación coherente frente a B persiste al sustituir S-NPP por NOAA-20 en las mismas filas posteriores. Su magnitud disminuye y algunas conclusiones por período cambian. Esta es evidencia descriptiva de sensibilidad a plataforma: no valida incendios reales, no constituye un nuevo holdout y no autoriza modificar la publicación.

## Diseño y verificaciones

Se ejecutó el protocolo 19 congelado en `6f281a1`, sin ajustar modelos, descargar datos, buscar hiperparámetros ni seleccionar un ganador con NOAA-20. Se reutilizaron exactamente las seis columnas predictivas de `coherent_audit/later_predictions.parquet`. Sus 3780 filas corresponden a 54 comunas y 70 meses de temporadas 2020–2025, con agosto/septiembre calendario 2020 excluidos de origen. Las temporadas son julio–junio: enero–junio 2022 pertenece a temporada 2021, por lo que los cortes de temporada y de calendario se muestran por separado.

Antes de calcular métricas:

- Se comprobó el hash de las predicciones frente al manifiesto 18 y los hashes de `celldays.parquet`, `inventory.csv` y `static_mask.parquet` frente a los manifiestos 18 y 7.
- Se verificó que las 223 coordenadas de la máscara publicada coinciden exactamente con la reproducción determinista de la máscara completa TRAIN 2012–2019 usada para 18. No se escogió una máscara distinta. SHA256 de coordenadas canónicas: `cee163687b5c88c4506bd0259f5563d2f024f1afb520a1836c6c033f1c51fbfa`.
- Se extrajeron conteos de celda-día diurna 0.01° por plataforma desde el mismo `celldays.parquet`, excluyendo esas coordenadas. El referente S-NPP se reprodujo **exactamente**, fila por fila, frente al guardado en 18. Un desacuerdo habría detenido la ejecución antes de puntuar.
- El inventario documenta solicitudes SP completas de ambas plataformas para los 70 meses: no hubo exclusiones adicionales. Se permite rellenar un conteo ausente con cero solo después de este control. Una solicitud completa no prueba que el sensor observó, que hubo cielo despejado ni ausencia de fuego.
- No aparece `any_nrt` en los positivos de ninguna plataforma en estas filas. Se produjeron grupos con/sin positivos NRT; el grupo con NRT está vacío y no ofrece un contraste SP/NRT. Las banderas proceden de detecciones, no identifican oportunidad de observación en filas con cero.
- Se conservaron 54, 14 publicadas y 40 restantes; las filas de ambos referentes son idénticas. Las predicciones no reciben etiquetas NOAA-20. Se comprobó su identidad exacta tras las uniones.

El NOAA-20 reconstruido aquí tampoco reproduce el contrato `observed` exacto de la web. `publish_observed.py` aplica un filtro `type=0` y su propia asignación geográfica; la ruta `build_detections`/`celldays` empleada en este estudio no aplica ese filtro y asigna por centroide de celda. Por tanto, se contrasta la **plataforma** utilizada por el producto con la unidad y máscara de investigación fijadas, sin afirmar equivalencia con sus valores publicados. No se cambió el referente después de observar resultados.

Totales de referente: S-NPP 17764 y NOAA-20 17476 celdas-día. Son productos instrumentales distintos; la diferencia no se interpreta como error físico de uno respecto del otro.

## Resultados sobre todas las filas posteriores

MAE local, en unidades de celdas-día por comuna-mes:

| Método congelado | S-NPP (54) | NOAA-20 (54) | S-NPP (14) | NOAA-20 (14) |
|---|---:|---:|---:|---:|
| M1 |2.334435|2.434186|3.195446|3.234522|
| B |2.244514|2.237767|3.126108|3.000359|
| E11_10, mediana |2.101069|2.135312|3.131594|3.123917|
| E_mean |2.274262|2.306894|3.193035|3.094925|
| E_coherent |2.111721|2.142587|3.062757|2.957323|
| E_proportional |2.166944|2.225595|3.203168|3.159914|

Frente a B, E_coherent reduce la discrepancia local agregada 5.92% frente a S-NPP y 4.25% frente a NOAA-20. En las 14 publicadas las reducciones son 2.03% y 1.43%, respectivamente. En las 40 restantes el MAE frente a NOAA-20 pasa de 1.970860 a 1.857429.

El ranking agregado 54 mantiene mediana, coherente, proporcional, B, media y M1 con ambos referentes. En 14 la asignación coherente queda primera en ambos, pero media y mediana intercambian posiciones. El ranking describe estas filas ya exploradas: no selecciona un nuevo modelo.

## Los cortes muestran fragilidad relevante

| Bloque | Grupo | B contra SNP | Coherente contra SNP | B contra NOAA-20 | Coherente contra NOAA-20 |
|---|---|---:|---:|---:|---:|
| Temporadas 2020–2021 |54|1.960280|1.913429|1.989367|1.916415|
| Temporadas 2020–2021 |14|2.956713|2.979495|2.810467|2.726279|
| Temporadas 2022–2025 |54|2.374788|2.202605|2.351617|2.246249|
| Temporadas 2022–2025 |14|3.203747|3.100919|3.087392|3.063218|
| Antes de calendario 2022 |54|1.590897|1.567726|1.619629|1.546994|
| Desde calendario 2022 |54|2.438178|2.272905|2.420919|2.319059|

En 14/temporadas 2020–2021 la dirección cambia: coherente empeora frente a S-NPP y mejora frente a NOAA-20. No se puede afirmar dominancia uniforme ni estabilidad del ranking entre referentes. En 54/temporadas 2022–2025 coherente supera a la mediana contra S-NPP, mientras la mediana supera a coherente contra NOAA-20; ambas siguen superando a B en MAE local.

Las restricciones regionales siguen siendo construidas: en 54 el sesgo y el MAE de totales regionales de coherente y proporcional son iguales a B frente a **cualquier** referente porque conservan su presupuesto por mes. Contra NOAA-20, B y coherente tienen sesgo −0.141869 y MAE regional 52.254644. Esta igualdad no agrega evidencia de capacidad regional predictiva ni establece una distribución conjunta condicionada.

La igualdad no se impone en 14 o 40 por separado. En 14 contra NOAA-20, el sesgo empeora de −0.370531 a −0.614921 y el MAE de subtotales mensuales empeora de 24.540934 a 24.664720, aunque baja el MAE local. La asignación transfiere parte del presupuesto entre territorios; la conservación 54 puede ocultar compensaciones entre subgrupos.

## Estratos definidos por cada referente

Los estratos de S-NPP y NOAA-20 se definieron por separado; no son las mismas filas salvo coincidencia del dato observado. No se comparan sus tamaños como si fueran cobertura.

Contra NOAA-20 en 54, coherente mejora los positivos (4.169320→3.947959) y los meses Aqua=0/referente positivo (1.907995→1.859506), pero empeora los ceros (0.382353→0.408381) y ambos conteos=0 (0.213402→0.233372). El resultado no resuelve la tensión entre recuperar positivos y añadir estimación en ceros observados.

En 14 contra NOAA-20, los 26 meses con referente ≥50 empeoran en MAE 20.230034→21.229276 y sesgo −1.540749→−2.391758. La mejora agregada de los extremos 54 (28.822598→25.993616) depende del avance de las 40 restantes; no justifica prometer una mejora de meses intensos en el territorio publicado. La misma advertencia existe con S-NPP: los 23 extremos de las 14 comunas empeoran 23.096126→25.007587.

## Decisión y trabajo pendiente

Se conserva E_coherent como candidato de investigación: la ganancia local frente a B no desaparece al referente usado en producto, pero no se promueve ni se recalibra con NOAA-20. La mediana simple continúa con menor MAE 54 agregado y peor consistencia de totales; el objetivo de decisión necesita explicitar ese intercambio.

La prioridad siguiente permanece medir oportunidad de observación y comparar pares espaciotemporales equivalentes en un piloto. Estos conteos no identifican nubes, humo, píxeles realmente observados, geometría ni contrafactual de detección. La sensibilidad a NOAA-20 no reemplaza esos datos. Las etiquetas de ambos satélites y estos destinos ya aportaron feedback al proyecto; no se presentan como validación independiente ni se reutilizan aquí para elegir otra configuración.

## Artefactos y validación

`data/processed/platform_target_audit/` contiene `paired_predictions.parquet` (predicciones y ambos referentes), `requested_months.csv` (70 controles mensuales), `metrics.csv` (ambos referentes, períodos, 54/14/40 y estratos), `summary.json` y `manifest.json` (código, protocolo, entorno, hashes de entradas y outputs). Todos los artefactos anteriores y la publicación permanecieron idénticos por hash.

Pasaron 6 pruebas sintéticas: calendario y mes con un día faltante; exclusión previa al relleno y claves idénticas; desacuerdo SNP aborta; procedencia faltante y duplicados abortan; cambiar etiquetas NOAA-20 no cambia ninguna predicción; igualdad construida de sesgo/total contra ambos referentes. La ejecución real reprodujo SNP exactamente y no ajustó modelos. No se calculó bootstrap ni significación con miles de celdas como supuestas réplicas independientes.
