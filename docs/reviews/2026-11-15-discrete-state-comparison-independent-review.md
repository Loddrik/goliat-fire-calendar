# Revisión independiente 33 — etiquetas en puntos nominales fijos

**Pasa sin bloqueantes para el alcance descriptivo declarado.** Se verificaron todas las 898704 filas de datos, sin importar el helper del autor ni usar GEOS, HDF, nuevos datos o ajustes de modelos. La revisión terminó dentro del cap original 07:48 UTC del 15 de noviembre de 2026.

| Tipo de fila verificada | Cantidad |
|---|---:|
| Puntos de los 16 escenarios |397608|
| Etiquetas nativas universales |85451|
| Rosters nativos |404152|
| Retención de positivos |10216|
| Catálogos positivos |1277|
| Total |898704|

El verificador propio comparó las fuentes nativas originales con sus proyecciones allowlist y comprobó igualdad exacta de los IDs esperados, sin completar etiquetas desde el catálogo positivo. Reconstruyó cada join propietario→etiqueta, campos GEO, máscaras, estados básicos y sus causas, superficies exportadas y referencias temporales de los scans propietarios. Los hashes GEO antes/después coinciden exactamente.

La política QA se rederivó mediante una implementación propia de los bits crudos y del screen congelado, sin importar el decoder del productor. Se verificaron los nueve estados conjuntos, cinco agregados, denominadores, Jaccard condicionado a etiquetas conocidas, tiers QA y estratos de superficie en todos los escenarios. Los positivos 7–9 permanecen positivos, incluidos M13 no nominal. Los puntos anidados conservan todos los campos esperados.

La retención se reconstruyó con incidencias estrictamente interiores, separadas de candidatos bbox y fronteras. Los cinco estados de retención y sus scopes coinciden para todo el catálogo; un quad ausente conserva campos null. No se interpretó la frecuencia de puntos como número de incendios, área o réplicas independientes.

Se verificaron los hashes completos de fuentes y salidas y pasaron los nueve tests del código final. La [evidencia independiente](evidence/discrete-state-comparison-independent-review/summary.json) conserva todos los hashes del productor y los resultados reproducidos. El [snapshot del verificador ejecutado](evidence/discrete-state-comparison-independent-review/verifier-executed.py.txt) tiene SHA256 `92f7fba309703e801221f835f63d010041f3646819184b5b5f2b88e05159b694`. Tiene una ruta ROOT local explícita y compara también los CSV nativos originales ignorados; se conserva como registro de la auditoría ejecutada, sin prometer portabilidad o un replay irrestricto.

La evidencia y el manifiesto del revisor están separados de los del productor. Ningún archivo ni manifiesto del intento 33 fue modificado o ampliado por esta revisión.

El pase acredita correspondencia y cálculo sobre **etiquetas nativas del quad nominal asignado al punto**. No acredita actividad física en esa coordenada, precisión instrumental, exposición comparable o causalidad. Los tiers QA incluyen el screen previo y exclusiones de máscara; no son calidad instrumental pura. La procedencia de superficie es la heredada del export 24B, sin reinspeccionar GEO. 30B continuo sigue fallido y G1 físico permanece falso.
