# Protocolo 9 — contraste externo de patrones estacionales con CONAF

Fijado antes de calcular correlaciones o consultar los conteos numéricos de resultado. Base 0823eb1. El esquema y la completitud ya fueron inspeccionados: las 54 comunas se emparejan por nombre sin alias ni duplicados; tres celdas de conteo están vacías (Alto Biobío en 2012–2013 y 2016–2017; Hualqui en 2023–2024). Los blancos se mantienen desconocidos, nunca cero.

## Pregunta y límites

¿Las temporadas con más actividad detectada S-NPP tienden a coincidir con temporadas con más incendios registrados por CONAF? Es una comprobación externa de **orden estacional**, no validación del número de incendios ni de detecciones individuales, ni del error de armonización Aqua. No se ajusta modelo, factor, máscara, banda ni compuerta; no se elige un candidato por correlación con CONAF.

Fuente: [resumen oficial por comuna 1985–2024](https://www.conaf.cl/centro-documental/resumen-de-ocurrencia-y-dano-por-comuna-1985-2023/), XLSX descargado con SHA256 1d92971eab0b8c73bae139f2d5228589370b72641917c630dde8eb0c9b16aad0. CONAF describe temporadas [de julio a junio](https://www.conafprevencionincendios.cl/situacion-nacional-de-incendios-forestales/). El archivo contiene conteos y superficies; **en esta etapa se usa solo el campo de número de incendios**, sin cambiar a superficie según el resultado.

## Unidad y extracción

- Temporadas completas 2012–2023 (julio 2012 a junio 2024), 12 bloques. La inspección del inventario confirma ventanas SP solicitadas completas para S-NPP; no demuestra cobertura de cada celda/día.
- Extraer exclusivamente las 12 hojas con encabezado de temporada concordante y columnas REGION, PROVINCIA, COMUNA, NUMERO INCENDIOS. Registrar hoja, fila Excel, nombre original, estado del valor y CUT emparejado.
- Nombres de las 54 comunas de `observed/dist/data/communes.json`, DPA oficial normalizada; ignorar tildes, caja, espacios y puntuación. Exigir correspondencia única, sin fuzzy matching. No filtrar Ñuble por región histórica: sus comunas estuvieron en Biobío antes de 2018. Si un nombre no coincide o se duplica, detener/reportar, no inventar un CUT.
- Conteos numéricos finitos, enteros y no negativos; vacío significa desconocido. Rechazar texto, booleanos, errores o fórmulas no resueltas en registros esperados. Abrir con openpyxl read_only/data_only, sin modificar el archivo. Una fórmula sin valor almacenado conserva estado desconocido y debe señalarse si se detecta en la columna de conteos.
- Serie satelital: sumar celdas-día diurnas S-NPP de los Parquet publicados, grilla/cartografía y máscara fija de 223 celdas publicadas. Sin Type=0 nuevo ni combinación NOAA. Los ceros son conteos de detecciones y no observaciones de ausencia física. Esta máscara usa datos hasta 2020: no simular evaluación prospectiva ni independencia del desarrollo satelital.

## Análisis declarado

1. **Primario regional:** panel territorial constante de comunas con conteos CONAF numéricos en las 12 temporadas (52 según inspección de esquema); sumar ambas series sobre exactamente esas comunas. Spearman de 12 pares anuales, rangos medios en empates. No usar una selección por señal o por correlación.
2. Bootstrap emparejado de temporadas, 5.000 réplicas y semilla 20261114, intervalo percentil 95 % de Spearman. Reportar réplicas degeneradas como indefinidas y su número, no rellenarlas. Solo 12 bloques; intervalo exploratorio y sin corrección de dependencia temporal.
3. **Sensibilidad regional:** las 54 comunas, únicamente temporadas completas sin ningún conteo desconocido (9 según inspección). Mantener territorio constante; no sumar un total regional parcial como si fuera completo.
4. **Descriptivo local:** Spearman entre temporadas dentro de cada comuna con al menos 8 pares conocidos y ambas series variables; reportar n y valores desconocidos/constantes. Publicar las 54 filas, mediana e intervalo intercuartil de correlaciones definidas y cantidad positivas/no positivas. Sin p-valores ni selección de comunas por significación. No usar una correlación agrupada comuna×temporada que confunda diferencias de tamaño territorial con co-variación temporal.
5. Sensibilidad de influencia regional: retirar una temporada por vez en el panel primario y reportar todos los coeficientes, sin descartar extremos del resultado principal.

Las definiciones administrativas/operacionales de CONAF y la cartografía fija del satélite no son idénticas. No se dispone aquí de eventos individuales emparejados ni del punto de inicio que permita armonizar sus límites. Una correlación alta no demuestra equivalencia de unidades; una baja no identifica por sí sola qué fuente falla. No se evalúa 2002–2011 ni se emplean conteos CONAF para optimizar reconstrucciones en este protocolo.

## Artefactos y verificación

Directorio nuevo `data/processed/conaf_external_audit/`: extracción con procedencia, panel anual emparejado, panel primario y sensibilidad, correlaciones locales, influencia, resumen y manifiesto. Hash antes/después del XLSX y de producción/auditorías anteriores; metadata con fuente y versiones. Tests de nombres, ambigüedad, blancos vs cero, temporada/encabezados, conteos inválidos, empates, series constantes, panel territorial constante y bootstrap reproducible. El XLSX crudo queda fuera de Git; añadir el parser requerido a dependencias. Todos los PR a dev, Daniel Quinteros sin firma; investigación hasta 21:00 de Santiago.
