# GOLIAT — repo de entrega · NASA Space Apps 2026 (Concepción)

Calendario de actividad de fuego detectada, MODIS + VIIRS armonizados (NASA FIRMS), para las 54 comunas de Biobío y Ñuble. **Entrega: domingo 15-11-2026 a las 23:59 (hora de Chile), sin prórroga.** App en vivo: https://goliat-fire-calendar-production.up.railway.app (cada push a `main` despliega solo).

## Lee primero

- **Manifiesto v2** (problema, usuario, producto mínimo, alcance, compuertas, plan hora a hora): `/Users/loddrik/projects/personal/nasa-space-challenge/docs/manifiesto.md`. Si una tarea no sirve a lo que dice, no se hace.
- **`docs/alcances.md`: reparto Daniel/Rubén, contrato pipeline↔web, flujo git y cortes. Leerlo antes de tocar algo del otro lado.**
- `docs/method.md`: el método congelado, con números y divulgaciones. `docs/reviews/`: revisiones y qué se cambió.
- Investigación de usuarios con fuentes: `/Users/loddrik/projects/personal/nasa-space-challenge/docs/investigacion/usuarios/*.md`.
- Decisiones y su porqué: `/Users/loddrik/projects/personal/nasa-space-challenge/docs/decisiones.md` (las del 14-11).

## Reparto de trabajo (desde el 14-11 a las 14:30)

- **Ciencia y algoritmo = Daniel.** Todo lo que toque `pipeline/experiment.py`, `build_mask.py`, compuertas, factor, bandas, particiones o `docs/method.md` §2–4 se le levanta como **issue de GitHub** (etiqueta `ciencia`) y **no se cambia desde esta sesión**. Si la app necesita un dato nuevo del pipeline, se abre un issue y mientras tanto se trabaja con lo que hay.
- **Producto y app = esta sesión** (Rubén + Claude): `web/`, `server.mjs`, textos, CSV, impresión, página del proyecto, demo, README.
- Los números que muestra la app salen **solo** de `web/public/data/` (generado por `pipeline/publish.py`). Nunca se calcula ni se corrige un número en la web ni con IA.

## Reglas que no se negocian (vienen del manifiesto y de los revisores)

1. **Lenguaje:** "actividad de fuego detectada", "celdas-día", "detecciones". Nunca "incendios", "hectáreas", "alerta", "riesgo", "pronóstico", "predicción". Una detección no es un incendio (FAQ de FIRMS).
2. **Tres estados siempre visibles y distinguibles sin color:** observado (VIIRS 2012→), estimado (Aqua × 2,35, con "error típico", solo en las 14 comunas habilitadas), no habilitado (∅). Lo provisional (NRT) se marca.
3. **No es alerta ni pronóstico.** Para la emergencia: CONAF (Botón Rojo) y SENAPRED. Herramienta para ayudarse en la planificación, no plan listo.
4. **El mapa de recurrencia** son detecciones de 375 m, no predios ni culpables. Nunca se nombra un predio, empresa o persona.
5. **Comparación de temporada:** mismo territorio, mismos días (truncada al día de corte), solo observado. Con 14 temporadas, el p90 es débil y se dice.
6. Pantalla, impresión y CSV muestran los mismos números (leen el mismo JSON).
7. Cada fuente se cita: FIRMS (acknowledgement oficial en README), geoBoundaries/BCN, OpenFreeMap. Licencia Apache 2.0. Uso de IA declarado en README.

## Estructura y comandos

```
pipeline/   Python + DuckDB (uv). Orden: download_firms → inventory → comunas → build_detections → build_monthly → build_mask → experiment → publish
            experiment.py y publish.py corren también desde los parquet versionados en data/processed/ (sin goliat.duckdb).
web/        React 19 + Vite + TypeScript + MapLibre (basemap OpenFreeMap). Lee /data/index.json y /data/comunas/<cut>.json.
server.mjs  Express: sirve web/dist, /data (web/public/data) y /data/detections/<cut>.csv (data/processed/detections_csv).
```

- `npm install && npm run build && npm start` (puerto `PORT`, por defecto 3000). Dev: `npm run dev`. Local de prueba usado hoy: `PORT=3017 node server.mjs`.
- `uv sync && uv run python pipeline/publish.py` regenera los JSON de la web (solo si cambió el pipeline; eso es de Daniel).
- Railway: proveedor Node forzado en `railpack.json`; `railway.json` tiene el start command y `/health`. Logs: `railway logs --build`, `railway logs`.
- No usar pnpm (corepack roto en esta máquina); npm en todo.

## Estado al 14-11 14:30

Hecho: pipeline completo con revisión científica #1 aplicada (14/54 comunas con reconstrucción); web con selector, temporada en curso, calendario con 3 estados, mapa de recurrencia, panel de método, CSV serie + detecciones, impresión, ES/EN; desplegada.
En curso: revisión de producto (agente `revisor-producto`, resultados llegan a la sesión principal; se copian a `docs/reviews/`).
Pendiente (producto): aplicar la revisión de producto; vista imprimible revisada; página del proyecto en inglés (Space Apps); demo ≤ 30 s con subtítulos en inglés o ≤ 7 slides (medir antes de subir); jurado simulado (`jurado`) sábado noche y domingo; README final; declaración de IA.
Cortes del plan: **sábado 19:00 cierra la investigación; domingo 11:00 cierran funcionalidades**; después solo correcciones, reproducción y entrega.

## Agentes revisores

`.claude/agents/` (copiados del repo de preparación): `revisor-cientifico`, `revisor-producto`, `jurado` (y los de ideación, que ya no se usan). Son de solo lectura y leen los criterios desde la ruta absoluta del repo de preparación. Antes de mostrar un número nuevo en la app o el pitch → `revisor-cientifico`; al cambiar pantallas o textos → `revisor-producto`; con página, demo o README → `jurado`.

## Cómo trabajamos

Español chileno neutro, sin tecnicismos innecesarios. Commits en español, con `Co-Authored-By`. Antes de cambiar un texto que explica el método, releer `docs/method.md`: el texto de la app no puede prometer más que el método.
