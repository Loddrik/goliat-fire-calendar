# Reproducción aislada de la investigación

El runner `pipeline/reproduce_research.py` ejecuta las etapas 2–15 y los tests desde un checkout separado del mismo commit. Se niega a operar sobre el checkout original, directorios anidados, una copia sucia o un commit distinto. Conserva registros por etapa, hashes de resultados y el estado de los archivos públicos y científicos originales. Exige una hora límite con zona horaria y detiene nuevos procesos antes de agotarla.

## Alcance

La reproducción parte de las tablas satelitales **procesadas y versionadas** del repositorio. No vuelve a descargar y procesar el archivo FIRMS original. Comprueba que los algoritmos vuelven a producir los resultados guardados; no demuestra validez física, independencia del conjunto de desarrollo ni calibración futura.

El único insumo adicional es `data/raw/external/conaf-1985-2024.xlsx`, cuya procedencia figura en `data/processed/external_sources/conaf-download.json`. El runner verifica el SHA-256 `1d92971eab0b8c73bae139f2d5228589370b72641917c630dde8eb0c9b16aad0` y copia únicamente ese insumo crudo al checkout temporal. No copia resultados calculados desde el árbol de trabajo original.

Los resultados existentes en Git se vuelven a calcular secuencialmente. Sus manifiestos cambian porque registran el nuevo `source_head` y hashes de manifiestos previos. Deben revisarse esas diferencias explícitamente. Los resultados numéricos, parámetros, CSV, Parquet, resúmenes y figuras se comparan byte por byte; no se omite un resultado solo porque sea JSON.

## Ejecución

Desde una rama limpia y con sus cambios confirmados:

```sh
git worktree add --detach /private/tmp/goliat-reproduction HEAD
UV_PROJECT_ENVIRONMENT=/private/tmp/goliat-reproduction-env uv sync \
  --project /private/tmp/goliat-reproduction --frozen
python pipeline/reproduce_research.py \
  --checkout /private/tmp/goliat-reproduction \
  --python /private/tmp/goliat-reproduction-env/bin/python \
  --report-dir .runtime/reproduction-evidence \
  --deadline-utc 2026-11-15T00:00:00Z
```

Cambiar la fecha límite por una futura al repetir el procedimiento. El Python que lanza el runner usa solamente la biblioteca estándar; cada cálculo utiliza el intérprete indicado por `--python`. Un entorno nuevo instalado con `uv sync --frozen` permite comprobar la instalación sin depender del entorno de trabajo previo. Sigue siendo la misma máquina, arquitectura y conjunto de datos; no es una réplica externa independiente.

`summary.json` registra cada archivo coincidente o distinto, códigos de salida, duración, tests y hashes originales. Un fallo de comparación debe investigarse; los manifiestos no se reescriben en el checkout original para hacerlos coincidir. Los logs y checkout temporales se conservan para inspección.
