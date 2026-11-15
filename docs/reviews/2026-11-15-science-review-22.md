# Revisión 22 — descriptor retrospectivo de cobertura terrestre

Se construyó el descriptor de cobertura terrestre para las 54 comunas completas, sin ajustar modelos ni calcular errores de predicción S-NPP. La configuración primaria 2010/geografía legada/QC retenido entrega 54 filas con fracción clasificable ≥95%. Esto acredita la disponibilidad del descriptor bajo las reglas declaradas, **no exactitud ecológica, disponibilidad antes de 2012, calidad de observación de incendios ni elegibilidad G1**.

El protocolo 22 se congeló en `0e36507` antes de adquirir HDF y extraer características. Se preservaron año 2010 primario, 2001 para sensibilidad, geografía legada primaria, DPA 2023 secundaria y dos políticas de QC. No se escogió ninguna alternativa usando resultados de modelos.

## Adquisición y procedencia

Se adquirieron exactamente los dos HDF `MCD12Q1.061`, tesela `h12v12`, identificados en el preflight:

| Año nominal | Gránulo CMR | Producción UTC | Bytes HDF |
|---|---|---|---:|
|2010|G2484150734-LPCLOUD|2022-06-09T09:16:28Z|13764955|
|2001|G2484181538-LPCLOUD|2022-05-26T05:11:51Z|16769989|

Total real: 30534944 bytes = 29.120392 MiB, igual al contador de transferencia incluidos intentos fallidos, dentro del cap separado de 150 MiB. El intento anónimo se detuvo en el control de redirección antes de leer cuerpos HDF y dejó 0 bytes registrados. El intento autorizado leyó el bearer del archivo privado ignorado y lo adjuntó exclusivamente al host NASA original; no lo transfirió a CDN o URS ni abrió flujos de cuenta. No se imprimieron/persistieron valores de credenciales ni URLs firmadas. El cap y los datos L2 de observación permanecieron separados.

Los HDF y NPZ derivados permanecen bajo `.runtime/landcover-context/`, ignorado por Git. Se preservaron tamaño, SHA256 local y procedencia CMR; los metadatos CMR inspeccionados no proporcionan un checksum de objeto NASA que se pueda afirmar verificado. La repetición usa la caché con tamaño/SHA comprobados, sin nuevas descargas.

## Esquema real y rejilla nativa

En ambos archivos se verificaron `LC_Type1`, `QC` y `LW`: uint8, dimensiones 2400×2400, fill 255 y rangos/códigos documentados. `CoreMetadata` reproduce nombre de producto, colección 61, identidad completa del gránulo y fechas enero–diciembre del año fijado. No se dedujo el año únicamente del nombre local ni se trasladó QA de incendios a este producto.

Los extremos reales de `StructMetadata.0` son:

- Superior izquierdo: (-6671703.118,-3335851.559) m.
- Inferior derecho: (-5559752.598333,-4447802.078667) m.
- Paso X: 463.3127165279165m; paso Y: 463.3127165279167m.
- Proyección `GCTP_SNSOID`, esfera 6371007.181 m, parámetros restantes cero.

Las rejillas de ambos años son exactamente idénticas. La etiqueta nominal 500 m no se usó como área de píxel 500×500 m. Se utilizó cada rectángulo nativo definido por esos extremos y pasos reales.

La conversión geométrica registra explícitamente el pipeline PROJ: grados→radianes→sinusoidal con R=6371007.181. La descripción de PROJ incluye un offset geográfico “ballpark” entre WGS84 y la esfera sin datum equivalente definido; se conserva esa metadata. Aquí se adopta la convención cartográfica nativa del producto, **sin afirmar una transformación geodésica de alta precisión entre elipsoide y esfera**.

El lector HDF4 aislado usó Python 3.10.0, NumPy 2.2.6, pyhdf 0.11.7 y HDF 4.2.15. Se preservó el hash de cada array leído y se verificó su identidad contra el NPZ consumido en el entorno principal. El overlay utilizó Python 3.14.7, NumPy 2.5.4, Pandas 3.1.1, Shapely 2.2.0/GEOS 3.14.1 y pyproj 3.8.0/PROJ 9.8.1. No se cambiaron locks ni paquetes globales.

## Intersección fraccional y cierre

Se verificaron los hashes congelados de las 54 geometrías completas de cada fuente. Todos los polígonos eran válidos antes y después de proyectar; no se aplicó reparación, buffer0, simplificación ni recorte a celdas que hubiesen registrado incendios.

Para cada polígono, las celdas enteramente contenidas aportan su área nativa completa y las celdas de borde aportan el área exacta de intersección vectorial. No se asignó por centro ni se interpolaron categorías. El área fuera de la tesela se conserva como desconocida explícita; en las geometrías reales de este estudio no hubo área fuera de tesela.

La ejecución produjo **108 operaciones geométricas** (54 por 2 geografías), **432 filas descriptivas** (2 años×2 geografías×2 QC×54) y 7776 componentes de clase (17 clases+unknown). Las mismas intersecciones geométricas se reutilizaron para ambos años y políticas, evitando variaciones de soporte entre comparaciones.

| Comprobación | Máximo real | Límite fijado |
|---|---:|---:|
|Cierre relativo intersecciones+fuera frente a área de polígono|9.016e-14|1e−8|
|Cierre relativo clases 17+unknown|9.016e-14|1e−8|
|Desviación de suma de las 18 fracciones respecto de 1|9.015e-14|derivado del cierre anterior|

No se renormalizaron arbitrariamente áreas para aparentar identidad; se conserva el pequeño residual numérico y el denominador completo del polígono.

## Política de categorías y disponibilidad

La primaria retiene `LC_Type1` válido 1–17 con `QC∈{0,2,4,5,6,7,8,9}`. QC 1/3/10/255 y LC fill se registran como desconocidos con motivo; QC 1 etiquetado barren no se convierte en área válida clase 16. QC 8/9 permanecen identificados como backfill/modificación del clasificador, no garantía de verdad. `LW` es diagnóstico y no añade otro filtro. El QC 0 exclusivo es una sensibilidad declarada con población distinta; no se presenta como regla NASA.

Las variables primarias son área etiquetada bosque 1–5, cultivo 12, urbano 13 y mosaico 14 separado, divididas por área total. Se exportaron todas las 17 clases, agua 17, unknown y cruces LC/QC/LW. Las salidas secundarias usan tierra clasificada válida 1–16 y conservan la fracción que representa ese denominador; cero denominador devuelve NA, no 0. Bosque/cultivo/urbano no se fuerzan a sumar 1.

| Configuración | Filas | Contexto disponible ≥95% | Menor fracción retenida | Mayor fracción desconocida |
|---|---:|---:|---:|---:|
|2001/DPA2023/QC 0|54|45|67.747090%|32.252910%|
|2001/DPA2023/retained|54|54|100.000000%|0.000000%|
|2001/legacy/QC 0|54|45|68.316385%|31.683615%|
|2001/legacy/retained|54|54|100.000000%|0.000000%|
|2010/DPA2023/QC 0|54|45|68.220744%|31.779256%|
|2010/DPA2023/retained|54|54|100.000000%|0.000000%|
|2010/legacy/QC 0|54|45|68.857859%|31.142141%|
|2010/legacy/retained|54|54|100.000000%|0.000000%|

Bajo QC retenido no aparece área desconocida en las 54 comunas de ninguno de los cuatro pares año/geografía. Bajo QC 0, nueve comunas quedan por debajo de 95% en cada combinación: 08101, 08102, 08103, 08105, 08107, 08108, 08110, 08112 y 08310. Se conservan sus filas, valores y desconocidos; no se eliminan territorios para un futuro modelo. El umbral 95% es de ingeniería, no un criterio de calidad NASA ni una prueba de soporte contextual común entre SOURCE y held.

Rangos del descriptor primario2010/legado/retenido entre 54 comunas:

| Variable sobre área total | Mínimo | Máximo |
|---|---:|---:|
|Bosque 1–5|5.203204%|92.293587%|
|Cultivo 12|0.000000%|17.772280%|
|Urbano 13|0.000000%|47.867668%|
|Mosaico 14|0.000000%|16.339017%|

Los rangos describen categorías cartográficas agregadas, no proporciones físicas exactas de dosel, superficie cultivada o impermeabilidad. No distinguen automáticamente plantaciones de bosque nativo ni caracterizan prácticas de quema. Su relación predictiva con detecciones sigue sin evaluarse.

## Sensibilidades declaradas, sin selección de configuración

Las siguientes son diferencias del descriptor, expresadas en puntos porcentuales; no son errores de modelo ni mediciones validadas de cambio territorial. El promedio absoluto anual da el mismo peso a cada comuna.

| Variable | Mín Δ2010−2001, legado | Máx Δ2010−2001 | Media absoluta Δanual | Mín ΔDPA−legado,2010 | Máx ΔDPA−legado |
|---|---:|---:|---:|---:|---:|
|Bosque|-15.385083|42.020803|7.820941|-0.951925|2.858739|
|Cultivo|-1.430407|3.081446|0.380357|-0.017564|0.024242|
|Urbano|0.000000|1.220780|0.040911|-0.469382|0.742248|
|Mosaico|-9.013556|0.000000|0.780572|-0.000241|0.086346|

La fracción forestal presenta diferencias anuales importantes, hasta +42.02 puntos en un CUT, y sensibilidad geográfica hasta +2.86 puntos. No se atribuyen a deforestación, expansión o error del clasificador de forma automática. La guía desaconseja inferir cambios reales mediante diferencias de mapas anuales y describe estabilización interanual HMM.[Guía oficial C61](https://lpdaac.usgs.gov/documents/1409/MCD12_User_Guide_V61.pdf)

Los mapas nominales 2001/2010 fueron producidos en 2022; ni el nombre del año ni escoger 2001 garantizan información disponible antes de 2012. Las dos geografías también son retrospectivas. El descriptor es externo al ajuste local S-NPP, pero no se acredita independencia de información posterior ni causalidad ecológica.

## Integridad, pruebas y siguiente puerta

Pasaron **9 pruebas sintéticas**: intersecciones de borde distintas de asignación por centro; polígonos con huecos y fuera de tesela; costa fraccional con denominadores tierra/agua; rechazo de geometría inválida sin reparar; QC 1/barren, QC 3/QC 10, fill y correcciones retenidas; QC 0 y NA por tierra válida cero; umbral 95% y ausencia de renormalización entre tres clases; esquema/CRS/fill/rangos/códigos; identidad/año nativo; y Bearer limitado al host NASA exacto, excluyendo CDN, URS y hosts imitadores.

La corrida completa tomó aproximadamente 11.8 segundos de overlay/validación en el entorno actual, sin contar la adquisición y los lectores HDF anteriores. Se verificaron hashes de toda la base, publicaciones y resultados anteriores; permanecieron idénticos. Ninguna función de características lee etiquetas S-NPP: los archivos anteriores se recorren únicamente para hashes de protección.

Se entregan en `data/processed/landcover_context_audit/`:

- `features.csv`: 432 filas con denominadores, indicadores de disponibilidad y las cuatro variables solicitadas.
- `class_areas.csv`, `unknown_reasons.csv`, `QC_areas.csv`, `LW_areas.csv`, `LC_QC_LW_areas.csv`: categorías, razones y cierres auditables.
- `geometry_checks.csv`, `year_stability.csv`, `geography_sensitivity.csv`: soporte y diferencias descriptivas sin elegir una alternativa ganadora.
- `native_metadata_2001.json`, `native_metadata_2010.json`, `acquisition.json`, `summary.json` y `manifest.json`: procedencia, esquema real, entornos, transferencias y hashes.

Una prueba 23 necesitaría otro protocolo antes de ajustar o puntuar. Debería conservar los cuatro regímenes de 21 y comparar una política contextual con un control de mezcla uniforme de las mismas distribuciones SOURCE, además de M1/E00, para separar ponderación contextual de representación. La disponibilidad 54/54 no demuestra que los contextos held estén representados por SOURCE; ese diagnóstico y los fallbacks deben fijarse sin escoger territorios por error. G0/G1 de observación sigue activo y no queda resuelto por estas características.

No se ajustaron modelos, calcularon nuevos scores, modificaron publicación/resultados previos ni realizaron commits/push por este agente.
