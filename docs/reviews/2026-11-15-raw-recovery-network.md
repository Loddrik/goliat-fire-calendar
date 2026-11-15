# Recuperación de originales FIRMS mediante red

Objetivo: localizar los **mismos bytes originales** inventariados, sin sustituirlos por consultas parecidas ni reconstruir CSV a partir de los Parquet. La autorización tiene un plazo 12:59:41–13:29:41 UTC. El corte inicial de red era 13:24; se amplió expresamente hasta 13:27, manteniendo el cierre de revisión a las 13:29:41. Esta tarea no reabre la adquisición L2 de los estudios anteriores.

## Fuente y controles

Se partió de `data/processed/inventory.csv` y de la auditoría local que ya verificó 38 copias exactas. La red busca exclusivamente las 1.033 rutas restantes. Cada respuesta se acepta sólo si **SHA-256 y número de bytes coinciden** con el inventario. No se ordenan filas, redondean valores ni eliminan registros para intentar producir una coincidencia.

La [documentación oficial de área FIRMS](https://firms.modaps.eosdis.nasa.gov/api/area/) especifica consultas por fuente, caja, fecha y rango de 1–5 días. [MAP_KEY](https://firms.modaps.eosdis.nasa.gov/api/map_key/) documenta 5.000 transacciones por intervalo de diez minutos y advierte que consultas mayores pueden contar como varias. Se conservó la caja del descargador original: `-76,-56,-66,-17`; fuente, fecha y duración se derivan de cada nombre inventariado. No se solicita aumento de cuota ni otra clave.

El índice [API oficial](https://firms.modaps.eosdis.nasa.gov/api/) marca actualmente la API de país como no disponible. Esto se distingue del archivo anual estático `data/country/modis/<año>/<archivo>`, que sí respondió para los dos originales faltantes de 2000 y 2001. Ambos coincidieron exactamente con sus hashes. El preflight terminó a las 13:02:45 UTC, dentro de los primeros cinco minutos: esos dos CSV y dos ventanas API inventariadas devolvieron cuatro coincidencias exactas, con 214.338 bytes de respuesta.

La primera prueba bajo sandbox falló en transporte sin descargar cuerpos. Se preservan esos cuatro fallos y el reintento autorizado con red escalada, sin atribuir los fallos de acceso a inexistencia de datos. Las llamadas posteriores tienen timeout de 18 segundos y no usan reintentos automáticos por ventana. El límite de cuerpos de respuesta es 150 MiB y existe un corte absoluto antes de las 13:27. Los contadores de transferencia describen bytes de respuesta leídos por el cliente, no una medición de paquetes TLS/cabeceras.

### Corrección de la tasa y pausa por cuota

La versión inicial usó tres workers e inicios cada 0,75 segundos. Esa planificación subestimó el coste: el JavaScript de la página oficial aplica un factor 2 a VIIRS y multiplica por días y teselas de 60 grados; para nuestra caja una ventana VIIRS de cinco días cuesta **10 transacciones**, no cinco. Se observaron HTTP400 sostenidos; se detuvo el proceso a las 13:11:45 y una lectura diagnóstica confirmó el mensaje «Exceeding allowed transaction limit.». No se trataron esos errores como archivos inexistentes.

La consulta de estado enlazada por la propia página oficial informó después 4.628 transacciones usadas de 5.000. La reanudación v2 comprobó 3.340 y usó dos workers con separación de dos segundos. La v3, expresamente autorizada, comprobó 2.780 y usa separación de **1,5 segundos**, como máximo unas 4.000 transacciones VIIRS de cinco días por diez minutos. Comprueba saldo antes de iniciar y se detiene automáticamente ante cuota. Sólo vuelve a intentar ventanas sin original recuperado; los CSV con SHA diferente no se reintentan. Las versiones anteriores, los errores y el checkpoint de las 13:16 se preservan; no se oculta el error de planificación inicial.

## Resultado

La red terminó a las **13:26:36 UTC**, antes del corte ampliado. La revalidación posterior volvió a comprobar SHA-256 y bytes de cada archivo aceptado.

| Estado | Archivos |
| --- | ---: |
| Inventario completo | 1.071 |
| Copias locales exactas verificadas previamente | 38 |
| Nuevos originales exactos recuperados por red | **918** |
| Total de originales exactos localizados | **956** |
| Respuestas CSV con SHA distinto, en quarantine | 4 |
| Ventanas no consultadas por límite de tiempo | 111 |
| Originales todavía pendientes | **115** |

Los nuevos originales exactos suman **45.897.343 bytes**. Se contabilizaron **45.935.947 bytes** de cuerpos de respuesta; añadiendo una cota conservadora para las cinco lecturas que podían estar en vuelo al detener las versiones anteriores, el límite superior de esos cuerpos es **76.479.867 bytes**, inferior a 150 MiB. No se presenta esto como medición de tráfico TLS ni retransmisiones. La consulta diagnóstica y el HTML de documentación fueron pequeños y se registran aparte.

Hubo 1.048 intentos registrados: 918 coincidencias exactas, cuatro mismatches, cuatro fallos iniciales de transporte y 122 errores HTTP históricos (121 de cuota y uno de servidor). Estos últimos se recuperaron posteriormente con la tasa corregida; no quedan como archivos inexistentes. Los cuatro CSV no coincidentes son:

- `MODIS_NRT_2026-11-05_3d.csv`.
- `MODIS_NRT_2026-11-13_2d.csv`.
- `VIIRS_NOAA20_NRT_2026-11-13_2d.csv`.
- `VIIRS_NOAA21_NRT_2026-11-13_2d.csv`.

No se transformaron ni aceptaron como originales. Los 111 restantes no se probaron antes del cierre; no se concluye que NASA no los tenga. La lista exhaustiva está en `evidence/raw-recovery-network/unresolved.csv`; los 918 aceptados, con hash y ubicación, en `exact-files.csv`. Los checkpoints de 13:16, 13:20 y 13:24 permanecen inmutables y sus manifests están enlazados desde el manifest final. El resultado es **recuperación parcial exacta**, no recuperación completa.

## Integridad y límites

Las coincidencias se guardan en `.runtime/raw-recovery/network/exact/<ruta-del-inventario>`. Los CSV con hash distinto quedan en `quarantine/`; una respuesta HTTP 200 por sí sola no acredita recuperación del original. Las respuestas ajenas al formato de detecciones no se guardan como CSV recuperado. Las excepciones se reducen a tipos/códigos, nunca a URLs privadas. La clave se lee exclusivamente del archivo de secretos autorizado, se mantiene en memoria y no se copia a los logs o a la evidencia.

Esta tarea **no escribe `data/raw`**, no modifica el inventario, no regenera Parquet ni recalcula indicadores o modelos. Por ello, «recuperado» significa copia exacta verificada en staging; la instalación posterior en las rutas canónicas corresponde a una acción separada y revisable. Un archivo no coincidente sigue faltando aunque exista una descarga más reciente con datos de aspecto similar. No se presume la causa de las diferencias.

La evidencia pública contendrá fuentes, helper, resultados sanitizados, lista de coincidencias, faltantes y hashes. Los CSV originales permanecen en el staging local autorizado; no se incluyen claves ni URLs de API con claves.
