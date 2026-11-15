# Recuperación local de los CSV originales: búsqueda acotada

Corte de esta búsqueda: **2026-11-15T13:04:49.617951+00:00**. Es una búsqueda de originales idénticos al inventario, no una reconstrucción de observaciones ni una evaluación del modelo.

La búsqueda volvió a verificar los **38 originales locales ya conocidos** en `firechronos/data/raw/history`. **No encontró originales locales adicionales** entre los archivos y respaldos examinados. Respecto de esas copias preexistentes, quedan **1.033 de los 1.071 registros** del inventario sin localizar en el ámbito revisado. Esto no demuestra que los archivos no existan en otros discos, carpetas o servicios.

El inventario de referencia es [inventory.csv](../../data/processed/inventory.csv): **1071 registros**, **101,477,474 bytes**, SHA256 `97428b84e89ae70c9d87529a0239a5b4872a453f42b6f853cb51a7377b1090ad`. La aceptación exige tamaño y SHA256 exactos. No se aceptan CSV regenerados, normalizados o solamente equivalentes en significado.

## Dónde se buscó y cómo se verificó

Se enumeraron archivos con `rg --files -uuu` en `/Users/dquinteros/nasa` y en nombres de rutas relacionados con NASA, MODIS, VIIRS, FIRMS, fire, Goliat, SNPP, Suomi, NOAA o hotspot dentro de Downloads. Se excluyeron expresamente `.runtime/secrets`, entornos y dependencias. La enumeración no encontró paquetes de Downloads con esos nombres relacionados; los nombres de archivos ajenos al proyecto se suprimieron y no se abrió su contenido.

En el proyecto se enumeraron **945 CSV**. Se comparó primero su tamaño con el inventario y se calculó SHA256 para los **83 candidatos de tamaño compatible**. Se inspeccionaron los índices de **7 archivos tar/zip**, que contenían **324 miembros CSV**, y se compararon por hash los miembros de tamaño compatible sin extracción masiva. Ningún miembro aportó un original adicional. Los dos paquetes `firechronos-site.tar.gz` y `firechronos-stage2-site.tar.gz` contienen exportaciones del sitio, que no coincidieron con los originales solicitados. Los respaldos de observación y cobertura terrestre no contenían miembros CSV.

También se revisaron los encabezados de **24 bundles Git**. Todas sus referencias están cubiertas por las historias actualmente alcanzables de Goliat o FireChronos, por lo que no hizo falta importar bundles ni modificar referencias. En esas historias se enumeraron **573 objetos CSV** y se verificaron los **4 objetos de tamaño compatible**: ninguno coincide con el inventario. La historia Goliat examinada no incluía objetos CSV bajo `data/raw/`. Este resultado cubre las historias referenciadas por los bundles, no objetos colgantes o nunca referenciados.

## Separación de la recuperación de red concurrente

Durante la enumeración aparecieron **4 originales exactos** bajo `.runtime/raw-recovery/network/exact/`: MODIS país 2000 y 2001 y dos archivos de API, uno MODIS_SP y otro VIIRS_NOAA20_SP. Son resultados del trabajo de red paralelo, **no hallazgos locales de esta búsqueda**. Se preservan sus rutas, tamaños y hashes en la evidencia para evitar doble contabilización. El estado de ese trabajo puede haber avanzado después de este corte.

Los 38 originales preexistentes corresponden a MODIS país 2002–2025 y VIIRS Suomi NPP país 2012–2025. Las copias ya preparadas bajo `restored-exact` tampoco se cuentan nuevamente como originales recuperados.

## Distribución de lo que faltaba al comenzar la búsqueda local

Los siguientes conteos se refieren a los **1.033 registros distintos de los 38 originales preexistentes**. No descuentan los resultados concurrentes de red ni representan el saldo final de toda la operación.

| Grupo del inventario | Registros |
| --- | ---: |
| `firms_api/MODIS_NRT` | 16 |
| `firms_api/MODIS_SP` | 49 |
| `firms_api/VIIRS_NOAA20_NRT` | 22 |
| `firms_api/VIIRS_NOAA20_SP` | 609 |
| `firms_api/VIIRS_NOAA21_NRT` | 22 |
| `firms_api/VIIRS_NOAA21_SP` | 250 |
| `firms_api/VIIRS_SNPP_NRT` | 20 |
| `firms_api/VIIRS_SNPP_SP` | 43 |
| `firms_country/modis` | 2 |

La prioridad solicitada para MODIS país 2000/2001 y las API NOAA-20/21 se mantuvo visible. Los dos CSV de país ya aparecieron por recuperación de red; los paquetes locales revisados no aportaron API NOAA-20/21 adicionales.

## Evidencia y límites

El [resumen verificable](evidence/raw-local-recovery/summary.json) separa coincidencias preexistentes, copias de trabajo y resultados de red. El [manifiesto de evidencia](evidence/raw-local-recovery/manifest.json) contiene los SHA256 de los inventarios de búsqueda, índices de archivos y cobertura de bundles. El detalle de cada coincidencia incluye ruta de origen, bytes, SHA256 y ruta esperada en el inventario.

No se descargaron archivos, no se copiaron originales a `data/raw`, no se extrajeron miembros, no se ejecutó contenido de paquetes y no se modificaron entradas canónicas ni referencias Git. Tampoco se leyeron secretos. La búsqueda no se extendió a todo el directorio personal, servicios remotos o archivos de Downloads sin relación identificable por su ruta. No existe una pista local que justifique ampliar esta tarea a releases o artifacts de GitHub.

Una comprobación adicional de extensiones sin distinción de mayúsculas no encontró candidatos locales nuevos en los formatos originales. La enumeración de `.csv.gz` identificó únicamente derivados de las auditorías de observación; no se abrió ni descomprimió su contenido nativo. Las rutas de recuperación de red aparecidas después del corte tampoco se reclasificaron como hallazgos locales.
