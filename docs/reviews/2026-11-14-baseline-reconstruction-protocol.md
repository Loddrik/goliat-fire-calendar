# Protocolo de reconstrucción de la base publicada

Fijado antes de recalcular la agregación y publicación. La reproducción de las etapas 2–15 verifica los experimentos desde los Parquet fijados; falta comprobar que el tramo que genera esos agregados y la publicación original sigue siendo consistente.

## Alcance y límites

El inventario registra 1.071 CSV y 101.477.474 bytes. Ninguno de esos CSV está disponible en este checkout. No se intentará fabricar una descarga equivalente ni afirmar reproducción desde FIRMS crudo. Se conserva el inventario como evidencia histórica. Las detecciones canónicas y la asignación celda/comuna versionadas son el punto inicial de esta comprobación.

En un tercer checkout temporal del mismo commit, usando el entorno nuevo instalado con uv.lock:

1. Crear una base DuckDB local solo con `detections.parquet` y `cells_comuna.parquet` versionados como tablas `det` y `cells_comuna`. No leer una base persistente del checkout original.
2. Ejecutar el código existente `build_monthly.py`, `build_mask.py`, `experiment.py` y `publish.py`, sin modificar reglas ni publicar al remoto.
3. Comparar celdas-día, agregados mensuales y máscara con los versionados mediante multiconjuntos de filas (`EXCEPT ALL` en ambas direcciones), porque el orden físico de Parquet no es una diferencia científica. Conservar igualmente ambos hashes físicos.
4. Comparar `eval_loso.csv`, `eval_final.csv`, `gates.csv` y `params.json` completos. Primero probar igualdad de bytes; ante diferencias de serialización, informar valores/columnas y tolerancia absoluta máxima 1e-10 para números, con claves y estados exactos. Conservar `Infinity` solo donde ya forma parte del diagnóstico histórico; no introducirlo en JSON de navegador.
5. Comparar los 54 JSON comunales completos y el índice público. Solo la propiedad `generated` del índice es un timestamp esperado variable; ningún otro campo se excluye de la comparación. No ejecutar el publicador derivado de producto ni sobrescribir sus JSON.
6. Verificar que los archivos científicos y públicos originales permanecen iguales a sus hashes de partida.

La prueba no valida la clasificación diurna ni deduplicación desde los CSV ausentes, no prueba cobertura de observación, y no hace independiente el desarrollo histórico. Un fallo de reconstrucción se informa y analiza sin cambiar los artefactos publicados para forzar coincidencia. No se ajustan modelos candidatos nuevos ni compuertas.
