# Reconstrucción de la base: valores reproducidos, orden JSON variable

**Los agregados y parámetros se reproducen. La comparación estricta de la publicación falla por el orden de `recurrence`.** Se conserva ese resultado, sin convertir un diagnóstico posterior en aprobación del criterio original.

Se ejecutó el [protocolo fijado](2026-11-14-baseline-reconstruction-protocol.md) en un checkout temporal `b1e277c`, con una DuckDB nueva poblada únicamente desde las detecciones y asignaciones celda/comuna versionadas. Se ejecutaron sin cambiar reglas `build_monthly.py`, `build_mask.py`, `experiment.py` y `publish.py`, con el entorno reconstruido desde `uv.lock`.

| Comprobación | Resultado |
| --- | --- |
| `celldays.parquet`, mensual sin máscara, máscara y mensual enmascarado | Cero filas distintas por `EXCEPT ALL` en ambas direcciones |
| `eval_loso.csv`, `eval_final.csv`, `gates.csv` | Igualdad byte por byte |
| `params.json` | Igualdad byte por byte, incluidos diagnósticos históricos |
| 54 documentos comunales | Cambia únicamente el orden de la lista `recurrence` |
| Índice público | Cambia únicamente el timestamp `generated`, previsto en el protocolo |

Los registros de recurrencia conservan exactamente coordenadas, días, temporadas y extremos temporales. Al ordenarlos por coordenada ambos conjuntos son iguales, pero esa normalización es un **diagnóstico posterior**, no la comparación estricta predefinida. Ningún otro valor comunal cambió.

La consulta de recurrencia agrupa las celdas sin `ORDER BY`. DuckDB puede devolver los grupos en distinto orden según el orden físico de los insumos o la ejecución. Eso explica que el JSON serializado difiera aun cuando los datos coinciden. La corrección propuesta es ordenar por CUT y coordenadas al final de esa consulta. Se prepara en una rama y PR separados para revisión compartida de publicación; no se regeneran los JSON públicos actuales ni se cambian datos o compuertas.

El inventario histórico enumera 1.071 CSV, 101.477.474 bytes. Los 1.071 faltan en el checkout actual. Por tanto, esta prueba empieza en detecciones procesadas y no valida desde los crudos el filtro diurno, la confianza, la prioridad entre fuentes o la deduplicación. No se intentó reemplazar archivos históricos por descargas actuales potencialmente distintas.

[Evidencia de reconstrucción](evidence/2026-11-14/baseline-reconstruction.json) y [disponibilidad de crudos](evidence/2026-11-14/raw-availability.json). Los archivos originales se conservaron; los resultados nuevos quedaron en el checkout temporal.
