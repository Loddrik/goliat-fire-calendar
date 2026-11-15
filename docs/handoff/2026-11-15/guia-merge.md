# Guía para integrar los PR pendientes

**Consulta del 15 de noviembre de 2026.** Orden recomendado: **#64 → #65 → #31 hacia `dev`**, seguido, si el responsable decide publicar, de un **PR separado `dev` → `main`**. Esta guía no ejecuta merges, cambios de base ni despliegues. El [recibo de estado](evidence/merge-guide-snapshot.json) conserva los heads y checks consultados; repetir la consulta antes de actuar.

## Qué queda abierto y por qué ese orden

| PR | Base actual / estado | Qué incorpora | Acción recomendada |
| --- | --- | --- | --- |
| [#64](https://github.com/Loddrik/goliat-fire-calendar/pull/64) | `dev`, borrador; head `6410fcb` | Verificador del inventario, guard antes de DuckDB, pruebas y evidencia de recuperación. | Actualizar con `dev`, revisar, ejecutar CI del head actualizado y fusionar primero. |
| [#65](https://github.com/Loddrik/goliat-fire-calendar/pull/65) | `dev`, borrador; head anterior a esta guía `85092ea` | Handoff, informes, evidencia de la copia completa y renderer documental. Contiene #64 como antecesor. | Tras #64, actualizar con `dev`, revisar el diff restante y fusionar. |
| [#31](https://github.com/Loddrik/goliat-fire-calendar/pull/31) | `main`, abierto; head `76c7d3e` | Orden determinista de recurrencia en `publish.py` y una prueba de republicación. | Cambiar su base a `dev`, sincronizar y validar antes de fusionar. No usar su base `main` actual para saltarse integración. |

Los PR científicos #32–#63 ya están integrados en `dev`. La comparación local confirma que #64 añade un único commit sobre `5382411`, ya antecesor de `dev`. Algunas vistas de GitHub todavía mostraban la base antigua de #64: usar el parentesco y el diff actualizado, no el tamaño de una vista antigua como prueba de duplicación.

La comprobación por archivos confirma que **#31 todavía no está incorporado**: añade `order by 1,2,3` a la consulta de recurrencia y una prueba que reordena las celdas-día en un directorio temporal. Ese orden de JSON **no resuelve el empate de deduplicación FIRMS** ni la discrepancia estricta de una fila por lado. Puede prepararse en paralelo; se ubica tercero para mantener un solo candidato de integración por vez.

## Antes de cada merge: identificar base, head y aceptación

Trabajar con el checkout limpio y conservar un respaldo Git. El raw completo se respalda por separado: no está incluido en Git ni en un bundle. La [guía de entrega](README.md) identifica el tar de 1.071 originales y su SHA.

```sh
git status --short
git fetch origin dev main
gh pr list --repo Loddrik/goliat-fire-calendar --state open
git config user.name 'Daniel Quinteros'
git config user.email 'daniel.quinterosc@gmail.com'
git config commit.gpgsign false
```

Usar **Create a merge commit** para conservar la ascendencia entre #64 y #65; el repositorio permite ese método. Squash o rebase cambian los identificadores y obligan a reconciliar otra vez la rama apilada. Conservar las ramas hasta terminar el traspaso y registrar el SHA que finalmente se integró.

La configuración de identidad y firma anterior controla commits **locales**. GitHub puede crear sus propios commits y firmas de plataforma al fusionar: no asumir que `commit.gpgsign=false` controla el servidor. Si también se exige ausencia de firma en el commit de integración, el mantenedor debe comprobar ese requisito y utilizar un método local permitido por las reglas de rama; no saltarse esas reglas con un push directo.

## Paso 1: #64, recuperación y guard

El mantenedor revisa su diff contra `dev`: el guard debe ejecutarse antes de abrir DuckDB; no cambia los SQL de detección, parámetros, gates o JSON publicados. El recibo antiguo de 956 archivos sigue siendo evidencia de un corte anterior; el recibo de la copia peer acredita ahora 1.071 exactos.

Para preparar su rama, después de confirmar que el checkout está limpio:

```sh
gh pr checkout 64 --repo Loddrik/goliat-fire-calendar
git fetch origin dev
git -c commit.gpgsign=false merge origin/dev
git push
gh pr checks 64 --repo Loddrik/goliat-fire-calendar --watch --fail-fast
```

Si hay conflictos, resolver cada archivo conservando el método actual en inglés y los cambios vigentes de marca/CI. Revisar el resultado antes de crear el commit de resolución. Un check verde del head antiguo no sustituye los checks del head actualizado.

**Aceptación:** CI web y científico pasan; el lector CRPS reproduce evidencia congelada; el guard da COMPLETE/salida 0 con el respaldo completo y rechaza inventarios incompletos. La ausencia de raw en GitHub Actions o un clon limpio es esperable y no justifica regenerar el inventario. Revisar y quitar el estado borrador sólo cuando se cumpla esa aceptación. Fusionar #64 mediante el procedimiento de revisión del equipo y registrar el commit de merge.

## Paso 2: #65, entrega y guía de integración

Después de confirmar que #64 está fusionado:

```sh
git fetch origin dev
gh pr checkout 65 --repo Loddrik/goliat-fire-calendar
git -c commit.gpgsign=false merge origin/dev
git push
gh pr diff 65 --repo Loddrik/goliat-fire-calendar --name-only
gh pr checks 65 --repo Loddrik/goliat-fire-calendar --watch --fail-fast
```

**Aceptación:** el diff restante contiene la entrega y sus herramientas documentales; no debe volver a introducir una versión antigua de método, marca o datos. Los HTML coinciden con sus Markdown; enlaces y fuentes resuelven; el estado actual indica 1.071 originales exactos y diferencia integración de despliegue. Los snapshots históricos y los seis votos conservan sus fechas y hashes. Verificar que ambos checks corresponden al head que se revisó, no al head `85092ea` anterior a esta guía. Quitar borrador y fusionar tras revisión.

Si el equipo ya incorporó #64 a través de un merge directo de #65, consultar primero el head actual de #64 con `gh pr view 64 --json headRefOid`, obtenerlo con `git fetch` y verificar `git merge-base --is-ancestor SHA_ACTUAL_DE_64 origin/dev`. Si la ascendencia confirma que ya está incorporado, no volver a aplicarlo ni hacer cherry-pick; comprobar el estado de #64 y documentar su incorporación. El orden normal anterior evita esta ambigüedad.

## Paso 3: #31, publicación determinista hacia dev

El responsable cambia expresamente la base; esta guía no la modifica:

```sh
gh pr edit 31 --repo Loddrik/goliat-fire-calendar --base dev
git fetch origin dev
gh pr checkout 31 --repo Loddrik/goliat-fire-calendar
git -c commit.gpgsign=false merge origin/dev
git push
uv run --frozen python -m unittest discover -s tests -p 'test_publication.py' -v
gh pr checks 31 --repo Loddrik/goliat-fire-calendar --watch --fail-fast
```

**Aceptación:** el cambio neto conserva su alcance de dos archivos, `pipeline/publish.py` y `tests/test_publication.py`; la prueba obtiene el mismo contenido y orden de las 54 comunas con dos permutaciones de entrada. La republicación de esa prueba ocurre en un directorio temporal. No ejecutar el publisher real para preparar el merge ni regenerar los JSON versionados por este motivo. El CI completo debe pasar, incluida la nueva prueba; el número histórico de 358 tests no es un techo para futuros cambios.

Cambiar la base puede alterar el diff y los checks. Revisar de nuevo antes de fusionar. Si aparece un cambio de parámetros, máscara, filtro científico o valores publicados, detener esa integración y separar la modificación que amplió el alcance.

## Comprobaciones comunes y decisión de release

Los workflows [web](../../../.github/workflows/ci.yml) y [científico](../../../.github/workflows/science.yml) son la referencia. Usan Node 22 y el entorno Python bloqueado. El mínimo de lectura incluye:

```sh
uv sync --frozen
uv run --frozen python -m unittest discover -s tests -p 'test_*.py' -v
uv run --frozen python -O pipeline/verify_crps_evidence.py
uv run --frozen python pipeline/verify_raw_inventory.py
npm ci
npm --prefix web ci
npm --prefix web run lint
npm --prefix web run build
```

El guard tiene salida 0 con los 1.071 raw verificados y salida 1 si no están completos. Es disponibilidad de entradas, no validación física. Las comprobaciones del renderer se instalan en un entorno documental separado siguiendo el [README de entrega](README.md); CI también las ejecuta. No lanzar drivers científicos con deadlines vencidos, reingestar ni ajustar modelos para resolver un merge.

Al terminar la integración, comprobar Tomé habilitada, Concepción sin reconstrucción, CSV con estados observado/estimado y vista por plataforma. Registrar commit y resultado; las capturas del handoff pertenecen al candidato que indica su acta, no automáticamente al último release.

**`main` es una decisión de publicación separada.** Según [alcances](../../alcances.md), `main` despliega automáticamente a Railway. El responsable de despliegue debe confirmar el candidato y abrir/revisar un PR `dev` → `main`, ejecutar CI y el ensayo de presentación antes de fusionarlo. El merge a `dev` no prueba despliegue. Después de publicar, consultar `/health`, confirmar la versión servida cuando esté disponible y repetir el recorrido; no inferir producción a partir de un check o de la versión local.

## Cómo recuperar una integración fallida

Antes de integrar, registrar el SHA de `dev`; después, el **commit de merge del PR creado al integrarlo**. Si falla una comprobación, mantener el candidato anterior y corregir mediante un PR pequeño. Para revertir, crear una rama desde el `dev` actual y un PR de reversión hacia `dev`; no reescribir la historia compartida.

Con merges que preservan ascendencia, revertir las dependencias en orden inverso: **#65 antes de #64** si se retiran ambos. #31 puede revertirse por separado. Para un merge commit, el comando de reversión es `git revert -m 1 SHA_DEL_MERGE_DEL_PR`, sustituyendo el identificador por el registrado. No usar el SHA interno `85092ea` de sincronización ni `6410fcb` como si fueran el merge futuro del PR. Revisar el diff de reversión y su CI antes de integrarlo. Si se usó squash, la reversión es la de un commit normal y no lleva `-m 1`.

Si el fallo ya llegó a producción, el responsable de despliegue coordina la recuperación del release; revertir `dev` por sí solo no cambia `main` ni Railway.
