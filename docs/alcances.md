# Alcances y reparto de trabajo — GOLIAT

*14-11-2026, 15:00. Para que Daniel (ciencia) y Rubén (producto) avancen en paralelo sin pisarse. Si algo no está aquí, se pregunta antes de tocar.*

## 1. Quién es dueño de qué

| Área | Dueño | Archivos | Se coordina por |
|---|---|---|---|
| **Ciencia y algoritmo** | Daniel | `pipeline/build_mask.py`, `pipeline/experiment.py`, `docs/method.md` §2–4 y §6, `data/processed/gates.csv`, `eval_*.csv`, `params.json` | Issues `ciencia` (#1–#10) |
| **Datos base** (descarga, inventario, detecciones, celdas-día) | Compartido, **congelado**: no se toca salvo bug. Un cambio aquí invalida todo lo de abajo. | `pipeline/download_firms.py`, `inventory.py`, `comunas.py`, `build_detections.py`, `build_monthly.py`, `data/raw/dpa/` | Issue + aviso explícito a los dos |
| **Publicación** (del pipeline a la web) | Compartido por contrato (§2) | `pipeline/publish.py`, `web/public/data/` | Daniel cambia *qué números*; Rubén cambia *qué campos y formato*. Si un cambio toca ambos, issue y PR revisado por el otro |
| **Producto y app** | Rubén | `web/`, `server.mjs`, `README.md`, página de Space Apps, demo, `docs/reviews/*product*`, `docs/alcances.md` | Issues `producto` (#11–#17) |
| **Despliegue** | Rubén | `railway.json`, `railpack.json`, `.dockerignore`, Railway | — |
| **Textos que explican el método en la app** | Rubén escribe, **Daniel aprueba** | `web/src/i18n.ts` → `methodBody`, `estimated`, `reconNotWhy`, `seasonHelp` | Comentario en el PR o en el issue #10 |

Regla simple: **los números los produce `pipeline/` y los muestra `web/`.** Nadie corrige un número en la web, en un texto ni con IA.

## 2. El contrato entre ciencia y producto

`pipeline/publish.py` escribe `web/public/data/index.json` y `web/public/data/comunas/<cut>.json`. La web solo lee eso. Lo que la web espera de cada comuna (ver `web/src/types.ts`):

- `series[]`: una fila por mes con `season, y, m, value, state ∈ {observed, estimated, not_enabled}`, y opcionales `sat, provisional, partial, band, aqua`.
- `season_compare`: `season, months, cutoff_day, current, observed_seasons{}, n, median, p25, p75, p90`.
- `recurrence[]`: `x, y, n, d, f, l` por celda.
- `gates{}`: los números que muestra el panel de método (`aqua_train, snpp_train, min_aqua, loso_mae_raw/const/clim, wins_vs_clim, wins_vs_raw, of, min_wins, gate_*, band_mae, band_coverage_1/2`).
- `reconstruction_enabled`, `r_const`, `cutoff`.

**Cambios compatibles** (los puede hacer cualquiera de los dos sin avisar): agregar campos nuevos.
**Cambios incompatibles** (requieren issue y PR revisado por el otro): renombrar o quitar campos, cambiar el significado de `state`, cambiar la unidad.

**Extensión FireChronos (14-11):** la vista de historia por plataforma consume un contrato separado generado por `pipeline/publish_observed.py` en `observed/dist/data/publication/`, servido bajo `/observed/data/publication/`. Unidad `cell_days_per_platform`, `harmonization: none`, DPA 2023 y Type=0. No modifica la unidad ni los estados del contrato armonizado. No trasladar coeficientes, máscaras o compuertas entre publicaciones; ver `docs/integracion-firechronos.md`. Los números de ambas vistas salen de publicadores deterministas; React solo los muestra. El build sincroniza `observed/dist/` a los activos web.

Si Daniel cambia el método (p. ej. issue #1: método por comuna), agrega `method: "M1" | "A"` a `gates` y actualiza `docs/method.md`; Rubén decide cómo mostrarlo. Los textos de la app que citan números del método (2,35; 14 de 54; 70 %/88 %) **se actualizan en el mismo PR** que cambia los números, o se marcan como pendientes en el issue.

## 3. Cómo trabajamos en git

- `main` despliega solo a Railway; **solo se toca para desplegar**. Los cambios se acumulan en `dev` (desde el 14-11 a las 15:30) y, cuando se quiere desplegar, se mergea `dev` → `main`. **Nada se mergea a `main` ni a `dev` si el CI falla** (`.github/workflows/ci.yml`: lint, tipos, build, JSON de `web/public/data` válido con 54 comunas, y el servidor levanta; corre en cada PR y en cada push a `main` y `dev`).
- Daniel trabaja en ramas `ciencia/<issue>-<tema>` y abre PR **contra `dev`**; Rubén revisa que el contrato (§2) y los textos sigan coherentes y mergea. Rubén trabaja en `dev` directo para la app (es una persona, va rápido) o en `producto/<tema>` con PR a `dev` si el cambio es grande.
- Un PR de ciencia que cambie números publicados **corre `publish.py` y versiona los JSON** en el mismo PR, para que la app y el método cambien juntos.
- Commits en español, con el porqué. `Co-Authored-By` cuando lo escribe Claude.
- Datos: `data/raw/` no se versiona (cada uno baja lo suyo con su `FIRMS_MAP_KEY`, o pide los parquet). `data/processed/*.parquet`, `gates.csv`, `params.json` y los JSON **sí** se versionan: son el resultado reproducible. `goliat.duckdb` no: `experiment.py` y `publish.py` corren desde los parquet si no existe.

## 4. Cortes del plan (manifiesto v2)

| Cuándo | Qué cierra | Qué significa para cada uno |
|---|---|---|
| **Sábado 19:00** | Investigación | Daniel: el método que esté en `main` a esa hora es el que se publica. Lo que no alcance queda como "siguiente paso" en `method.md`. Después solo bugs y documentación. |
| **Domingo 11:00** | Funcionalidades | Rubén: después solo correcciones, textos, reproducción, página, demo. Daniel: después solo revisión (#10) y textos del método. |
| **Domingo 20:00** | Entrega preparada | Ambos: lectura final de página, README y demo. |
| **Domingo 23:59** | Envío | Sin prórroga. Objetivo: enviado a las 22:00. |

Si Daniel cierra #1 después de las 19:00 del sábado con resultados sólidos, se decide entre los dos si entra (riesgo: cambia números, textos y demo a la vez). Por defecto, **no entra** y se documenta como siguiente paso.

## 5. Cuando algo cruza la línea

1. Se abre un issue con las dos etiquetas (`ciencia` + `producto`) y se describe qué cambia de cada lado.
2. El dueño del lado afectado responde en el issue antes de que se escriba código.
3. Un solo PR con los dos cambios, revisado por el otro.

Ejemplos que ya se ven venir: #1 (método por comuna → campo `method` + texto), #3 (banda relativa → `band` cambia de significado + leyenda), #17 (columnas del CSV de detecciones → `publish.py`, formato, lo hace Rubén y Daniel solo confirma que `used_in_series` reproduce su filtro).

## 6. Lo que ninguno hace

- Prometer alerta, pronóstico, incendios o hectáreas (manifiesto §3, criterio P4).
- Mostrar un número que no salga del pipeline.
- Cambiar particiones, filtros o la máscara "para que den mejor".
- Trabajar sobre `data/raw/` descargado por el otro sin inventariarlo.
- Tocar la demo o la página de Space Apps sin pasar por el `jurado` simulado (lo corre Rubén; Daniel lee el veredicto).

## 7. Comunicación

- Todo lo que cambie números o alcance queda escrito en un issue o PR, no solo en el chat.
- Cada uno anota en el issue qué verificó y con qué comando.
- Si uno se traba más de 30 minutos con algo del otro lado, pregunta en vez de resolverlo por su cuenta.
