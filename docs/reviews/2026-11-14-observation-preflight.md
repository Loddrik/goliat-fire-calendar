# Preflight de observación: catálogo disponible, G0 aún no superado

Se consultó CMR público para el alcance fijado por los consejos: envolvente geográfica `-72.782,-37.226,-72.218,-36.774`, nominalmente alrededor de 50×50 km con centro 37° S / 72,5° O, del 1 al 15 de enero de 2019. La envolvente de catálogo no acredita cobertura de píxeles de la AOI. No se consultaron focos para seleccionar las parejas.

**Hallazgo:** existe un universo de metadatos y geolocalización de las versiones previstas, pero solo una pareja de granules diurnos tiene un máximo desfase temporal posible ≤10 min. Los cuatro probes anónimos del conjunto técnico devuelven HTTP302 hacia autorización Earthdata. No se siguieron redirecciones ni se descargaron productos completos; no se leyeron QA o coordenadas de píxeles. **G0 y G1 siguen sin pasar.**

## Inventario obtenido

| Producto | Colección CMR fijada | Granules recuperados | DAY metadata | NIGHT metadata |
|---|---|---:|---:|---:|
| MYD14 | `C2278858993-LPCLOUD`, versión`061` | 35 | 18 | 17 |
| MYD03 | `C1379841358-LAADS`, versión`6.1` | 35 | 18 | 17 |
| VNP14IMG | `C2734202914-LPCLOUD`, versión`002` | 46 | 22 | 24 |
| VNP03IMG | `C2105092163-LAADS`, versión`2` | 46 | 22 | 24 |

La consulta comprueba paginación y ausencia de IDs duplicados. Los 35 MYD14 tienen un único MYD03 del inventario con el mismo identificador de adquisición (fecha juliana yHHMM); sucede lo mismo con los 46 pares VIIRS. Esto no verifica todavía `InputPointer`, dimensiones ni compatibilidad de píxeles. Una búsqueda literal por versión `061` para MYD03 no devuelve esta colección: su representación CMR es `6.1`. No se sustituyó por Collection 7.

## Desfase temporal, sin etiquetas de fuego

Se enumeraron asociaciones muchos-a-muchos entre granules con metadata DAY y mínimo desfase posible ≤60 min: 18 candidatos. Son asociaciones de archivos que intersectan la envolvente de catálogo, no 18 pasadas independientes ni 18 oportunidades de observación válidas.

Para intervalos de adquisición A=[a0,a1] y V=[v0,v1], el mínimo desfase es la distancia entre intervalos (0 si se solapan); el máximo es el mayor desfase entre extremos. Un candidato está definitivamente dentro si su máximo ≤ ventana; fuera si su mínimo > ventana; en otro caso es incierto.

| Ventana, minutos | Definitivamente dentro | Temporalmente inciertos | Fechas Aqua de los definitivamente dentro |
|---|---:|---:|---|
|5|0|4|Ninguna|
|10, primaria propuesta|1|3|2019-01-03|
|15|3|3|2019-01-03,06,11|
|30|7|4|2019-01-01,03,06,08,09,11,14|
|60, diagnóstico separado|15|3|14 fechas del período|

La pareja técnica elegida por una regla determinista, sin resultados de detección, es:

- Aqua MYD14: 2019-01-03,18:40–18:45 UTC.
- S-NPP VNP14IMG: 2019-01-03,18:36–18:42 UTC.
- Desfase posible 0–9 min; la hora nominal de inicio difiere 4 min, pero no se la trata como tiempo exacto de cada píxel.

No se propone ampliar la primaria a 30 min para obtener más muestra. Todavía debe comprobarse que ambas observaciones comparten soporte real dentro de la AOI; la ficha DAY es del granule, no una lectura de QA local. El período sigue siendo desarrollo previamente consultado, no un holdout nuevo.

## Acceso real y resultado de la puerta

En este preflight anónimo inicial se comprobó únicamente presencia de credenciales, como booleanos: no había variables Earthdata/LAADS configuradas ni entradas para sus hosts en `.netrc`. La verificación autenticada autorizada posteriormente se documenta por separado; este snapshot conserva el resultado original. No se expusieron valores ni se inició autenticación nueva.

El preflight realizó probes HTTP anónimos acotados a 1 KiB por archivo y sin seguir redirecciones, sobre los cuatro archivos de la pareja técnica y sus auxiliares. Todos respondieron 302 al endpoint OAuth Earthdata; se leyeron0 bytes de producto. Los parámetros de las URL de redirección no se guardan. Esto demuestra el obstáculo del acceso anónimo en estos enlaces, sin afirmar que el conjunto sea inaccesible con una configuración autorizada.

Una pareja técnica accesible no superaría por sí sola G1: el inventario completo del período debe traducirse a soporte y calidad realmente interpretables. Tampoco basta una firma binaria de archivo para declarar decodificadas máscaras y geolocalización.

## Artefactos y reproducción

[Resumen completo](evidence/observation-preflight/summary.json), [asociaciones temporales](evidence/observation-preflight/candidate_pairs.json) y [manifiesto](evidence/observation-preflight/manifest.json). Se guardan los metadatos normalizados de las cuatro colecciones y sus granules, con enlaces sin parámetros sensibles. `pipeline/observation_preflight.py` no usa credenciales, no sigueOAuth y no descarga productos completos.

```sh
.venv/bin/python pipeline/observation_preflight.py --probe
.venv/bin/python -m unittest discover -s tests -p test_observation_preflight.py -v
```

Cinco tests pasan: límites temporales conservadores, solapamiento sin simultaneidad inventada, asociaciones muchos-a-muchos invariantes al orden y sin usar detecciones, eliminación de credenciales de URLs y rechazo de inventarios incompletos/duplicados.

## Consecuencia para la iteración

Esta evidencia favorece mantener 1+2 como línea condicionada y continuar en paralelo los experimentos con los datos disponibles. No permite agregar todavía una variable de oportunidad real al modelo. Evita inventar negativos y muestra que la propuesta de quince días con primaria 10 min puede ofrecer muy poca información temporal independiente incluso si se resuelve el acceso. El dato nuevo aquí es de disponibilidad y diseño, no una mejora predictiva ni una medida del desacuerdo de fuego.
