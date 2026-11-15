# Control de invariancia al orden físico de insumos

Fijado antes de barajar los archivos. No se propone una familia de modelos ni una nueva población de validación. La pregunta es de software: ¿los resultados científicos dependen del orden físico de filas de datos idénticos?

En un checkout temporal se barajarán únicamente las filas de `detections.parquet`, `cells_comuna.parquet`, `celldays.parquet` y `static_mask.parquet`, con semillas 20261114–20261117, respectivamente. Esas copias son perturbaciones deliberadas: no se las describirá como checkout limpio. Se guardarán hashes antes/después, esquemas y conteos; `EXCEPT ALL` en ambas direcciones debe demostrar que cada multiconjunto permanece idéntico. No se modifican los insumos originales ni sus parámetros o publicación.

Se repetirán las etapas 2–15 con el entorno reconstruido desde uv.lock y se compararán los 118 resultados anteriores. Igualdad de bytes es el control inicial, más fuerte que una igualdad numérica con tolerancia. Ante diferencias se conservarán los artefactos y se distinguirá orden físico, redondeo u otros cambios; no se reescribirán los originales ni se declarará retrospectivamente aprobado el criterio estricto. Los manifiestos deberán reflejar el nuevo commit y los hashes de los insumos deliberadamente barajados.

No se calculan nuevos scores para seleccionar políticas, no se promocionan compuertas y no se modifica la publicación. Se respetará el límite UTC 2026-11-15T00:00:00Z, reservando tiempo para guardar evidencia y verificar ramas/PR.

## Control de preparación antes de concluir

La primera preparación mediante Pandas conserva los multiconjuntos, pero cambia tipos físicos (por ejemplo `string`→`large_string` y un entero nullable→double). No cumple la perturbación de **solo orden**; se conserva aparte como diagnóstico combinado de orden y representación. Sus resultados no se usarán para declarar aprobado el protocolo estricto.

La ejecución estricta usa `pyarrow.Table.take` con permutaciones NumPy y verifica igualdad del esquema Arrow completo, incluidos metadatos y nulabilidad, además de `EXCEPT ALL`. Mantiene las semillas fijadas. Solo esta segunda preparación puede responder al criterio de invariancia al orden sin cambio de tipos. No se relaja la igualdad inicial de 118 resultados.
