# Recuperación de originales y auditoría de ingestión

Ventana solicitada:30min,12:59:41–13:29:41UTC. Se restauraron en `data/raw` **956 de1071 CSV exactamente iguales al inventario**,94345574 de101477474bytes.38 se recuperaron de copias locales y918 deNASA. Todos se verificaron por tamaño ySHA256; el inventario congelado permanece intacto.

Quedan115: cuatro respuestas NRT recientes difieren del original y se conservaron en quarantine, y111 ventanas no llegaron a consultarse antes del corte. No se presentan redescargas diferentes como originales ni se modifican filas para forzar el hash. La consulta a la copia del desarrollador sigue siendo útil, especialmente para los cuatro snapshots NRT.

Se recuperaron las205 fuentes necesarias para la parte histórica anterior a julio2020. La [auditoría histórica](2026-11-15-raw-historical-core-audit.md) reproduce las223 celdas de la máscara y, usando el mapa comunal congelado, los conteos de entrenamiento Aqua/SNPP y el ratio M1 exacto2.352954072125397. Esto no reproduce la adquisición cartográfica ni valida toda la serie reciente.

La comparación estricta de13 columnas aún falla una fila por lado. La [auditoría de38 archivos](2026-11-15-raw-ingestion-recovery-review.md) identificó un empate de deduplicación sin desempate explícito, con distinta localización/FRP pero igual celda y día. Es un fallo conservado; la coincidencia de máscara/conteos no lo convierte en reproducción idéntica de todas las detecciones.

Se añade `pipeline/verify_raw_inventory.py`, sin escrituras: COMPLETE exige1071 rutas exactas y ningúnCSV adicional. La entrada de ingestión verifica esto **antes de abrir DuckDB**; una recuperación parcial queda bloqueada. No ejecutar `inventory.py` para reemplazar el inventario histórico. El verificador dispone de10 pruebas de integridad y una prueba aislada confirmó que la entrada incompleta no crea DuckDB.

La regresión completa descubrió dos tests sintéticos que caducaban con la fecha del experimento23. Se aisló su comprobación temporal únicamente dentro de los tests; el deadline del driver real no cambió y no se reejecutó el estudio histórico.

Los archivos restaurados quedan ignorados porGit, con copia tar local cuyos956 miembros se verificaron porSHA. [Recibo](evidence/raw-recovery-final/restoration-manifest.json), [estado de inventario](evidence/raw-recovery-final/inventory-verification.json), [respaldo](evidence/raw-recovery-final/backup-verification.json), [recuperación de red](2026-11-15-raw-recovery-network.md) y [búsqueda local](2026-11-15-raw-local-recovery.md) documentan el alcance. Modelos, Parquets y JSON publicados permanecen intactos. La recuperación completa sigue pendiente de115originales.
