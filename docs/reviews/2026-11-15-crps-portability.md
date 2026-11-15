# Verificación portátil de los snapshots CRPS del estudio 39

El lector `pipeline/verify_crps_evidence.py` verifica los resultados congelados del estudio 39 usando exclusivamente archivos versionados. No necesita `.runtime`, datos originales privados, credenciales, acceso a red ni el reloj del experimento. No ajusta modelos, reconstruye pronósticos ni ejecuta el driver cuyo plazo ya venció.

Desde la raíz de un clon con las dependencias del proyecto instaladas:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python pipeline/verify_crps_evidence.py
```

Necesita NumPy, pandas y el lector Parquet del entorno del proyecto. Imprime un único JSON con `status: PASS`; una discrepancia produce `ValueError` y salida distinta de cero. Los controles usan condiciones explícitas, no `assert`, y se mantienen con `python -O`. `--evidence-dir` y `--gates-file` permiten señalar copias de los mismos archivos anclados; no permiten sustituir los hashes esperados. No escribe los archivos de evidencia.

## Anclas y alcance comprobado

- Manifest 39: `aec1533e33b1d354c6102daf51d51d295d449f2afc15cf5ae50d2fe9719779ea`, más todos sus hashes de salida, comprobados antes y después del replay.
- `data/processed/gates.csv`: `218627f14acfc4834ac3d92360df4ee15d64354c8f49ef07428901e58d23ae42`, también exigido en `code-freeze.json`. Sus valores públicos `enabled` determinan las 14 comunas publicadas; no se infieren a partir de pérdidas.
- Las 10.368 claves CDF, los 444.826 átomos, identidad con el roster, dominio completo de CUT/temporadas/meses, roles SOURCE/held y respuestas repetidas congeladas.
- Pesos finitos y no negativos; suma original dentro de la tolerancia congelada y pesos almacenados exactamente iguales a una sola división por esa suma. El integrador no vuelve a normalizar.
- CRPS de cada CDF mediante integración por intervalos y CRPS de la distribución degenerada en B igual a `abs(B-Y)`. Se verifica también la tolerancia y política de redondeo originales.
- Los cuatro contrastes primarios, su promedio equiponderado y el secundario ponderado por filas; 216 tablas de población/estrato, equivalentes a 432 conjuntos por método; 216 filas por CUT y el peor CUT preseleccionado por el MAE original de B.

La integración reutiliza la semántica del verificador independiente archivado del estudio 39. Comparte esa procedencia: este lector no constituye un tercer oráculo independiente. Las tablas agregadas se contrastan con las pérdidas congeladas, después de verificar individualmente todas ellas contra la integral; se comprueba además directamente el primario agregado con las integrales reproducidas.

## Validación realizada

La ejecución sobre el repositorio pasó todos esos controles. El residuo máximo entre la integral y el CRPS crudo almacenado fue `2.1316282072803006e-14`. El contraste primario reproducido fue el valor ya publicado, `-0.6181638838629885`; no es un resultado científico adicional.

Se probaron fallos aislados con Python optimizado (`-O`): una copia temporal de los snapshots con un byte añadido a `fixtures.json` fue rechazada por hash; un registro en memoria con CUT alterado fue rechazado por identidad; unos pesos normalizados alterados fueron rechazados. Los hashes de todos los snapshots originales permanecieron iguales. La primera invocación del arnés de prueba resolvió el enlace del intérprete fuera del entorno virtual y no alcanzó el control esperado; se corrigió el arnés conservando la ruta del intérprete virtual y las tres pruebas pasaron. Esto no requirió cambios en las evidencias ni en las reglas del lector.

Este replay confirma la consistencia de los artefactos de la misma pérdida congelada. No reproduce el ajuste de origen, no valida físicamente el fuego ni demuestra calibración probabilística por sí solo. No cambia el resultado negativo del estudio 37, el estado de G1 ni las limitaciones del operador de observación. Contadores de esta tarea: cero ajustes, solvers, descargas científicas, nuevas CDF y nuevas definiciones de pérdida.
