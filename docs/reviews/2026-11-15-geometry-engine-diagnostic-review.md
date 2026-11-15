# Diagnóstico 27: GEOS 3.15.0 no resuelve los contraejemplos fijados

**La actualización aislada de GEOS 3.14.1 a 3.15.0 no restaura los criterios de consistencia en cuatro de los cinco pares WKB seleccionados.** El quinto pasa en ambas versiones. Los fallos son distintos: dos pares contradicen relaciones de contención, uno viola identidades de área y otro produce resultados inválidos aunque sus identidades numéricas cierren. No son cuatro fallos de todas las identidades. La hipótesis operativa «basta actualizar a 3.15.0» queda descartada en estos ejemplos.

Los cuatro controles sintéticos pasan en ambos motores. El adaptador CAPI sobre 3.14.1 reproduce exactamente todas las filas obtenidas con Shapely 2.2.0/GEOS 3.14.1; se verifican WKB y propiedades de entrada idénticos entre versiones. Esto reduce la explicación por el wrapper Python o mezcla de bibliotecas, pero no identifica la causa interna, ni resuelve representación/robustez numérica. **No se atribuye el fallo al issue 1499, al satélite, a fuego físico ni a sensibilidad instrumental.**

## Protocolo, congelamiento y aislamiento

Se siguió el [protocolo 27](2026-11-15-geometry-engine-diagnostic-protocol.md), congelado en `c69e6b2`. Cap fijo: 2026-11-15 04:50:00–05:25:00 UTC, incluida revisión, sin reinicio. Código e inputs quedaron congelados a las **04:54:27,815436 UTC**; el comparador terminó a las **04:57:31,363750 UTC**, dejando tiempo de revisión dentro del cap.

El [freeze](evidence/geometry-engine-diagnostic/freeze.json) identifica:

- Código `pipeline/geometry_engine_diagnostic.py`: SHA-256 `9ce8197e93947b5111fa84b7203ede64f9883a344dd64d5034a1f421780f6d1b`.
- `fixtures.json`: SHA-256 `daa89a9c67fec0fdc035da4c9d969facbb6c1f6f9497f75c7110e1bbaef4fbfa`.
- Freeze: SHA-256 `70678f6550c63743a5c42ae76aa06328e954df5ee20c8437ec296a25db7b7cf0`.

Se conservaron exactamente los cinco pares previamente fijados del [diagnóstico GEO original](evidence/observation-ownership-ledger/diagnostic/manifest.json), con sus diez archivos WKB comprimidos verificados contra ese manifiesto. No se eligieron por actividad, no se incorporaron nuevos pares reales y no se eliminó el que pasa. Son ejemplos seleccionados de regresión, no una muestra probabilística ni holdout. Se añadieron cuatro controles sintéticos WKB binarios de rectángulos: disjuntos, contenido, solape parcial y contacto de área cero.

Se descargó únicamente la fuente oficial del [tag GEOS 3.15.0](https://github.com/libgeos/geos/releases/tag/3.15.0) mediante HTTPS con verificación de certificado; el [ref oficial](https://api.github.com/repos/libgeos/geos/git/ref/tags/3.15.0) identifica el commit `d0228513abb0c29c185443cf2bfb06c9281024b5`. Archivo de fuente: **7.717.015 bytes**, bajo 20 MiB; SHA-256 local `134aaf78026f4311737e20ff1465cd31a48c4ca8858fb68e99d13ccd3d52753a`. **No se verificó un checksum remoto ni se afirma firma criptográfica del release.** El release y NEWS incluyen GH-1499; eso sólo motivó el contraste, no demuestra causalidad en nuestros WKB.

La compilación Release usó `/usr/bin/cc`/AppleClang 17 y `cmake --build ... --parallel 2 --target geos_c`. Fuente, objetos y bibliotecas permanecen bajo `.runtime/geometry-engine-diagnostic/`, ignorado. No se ejecutó instalación global ni se modificaron `.venv`, locks o paquetes del entorno principal. El [registro de compilación y controles](evidence/geometry-engine-diagnostic/build-and-control-review.json) conserva comandos, versiones y hash de CMakeCache; el log completo está guardado como evidencia.

Cada motor se ejecutó en su propio proceso. El comparador CAPI/ctypes utiliza sólo biblioteca estándar, contexto `GEOS_init_r` y operaciones `_r`; no importa Shapely/GeoPandas ni carga dos versiones juntas. Las firmas siguen el header oficial `capi/geos_c.h.in`, guardado antes del contraste. Un proceso separado ejecuta el baseline Shapely para comprobar el adaptador.

La [inspección anterior a operaciones](evidence/geometry-engine-diagnostic/execution-linkage-freeze.json) verificó versión real `3.15.0-CAPI-1.21.0`, `otool -L` e imágenes dyld: sólo estaban cargados los dos GEOS nuevos bajo el directorio aislado. Hash CAPI `9906c58e7de5c80454139cea93d9cc03c32e6064201e680cf510990f52ecfa5c`; núcleo C++ `899116fcb65ba7d0c32809d4c157f348c7eabf12953b10e0a1367487473cd81c`. El baseline declara `3.14.1-CAPI-1.20.5`.

## Resultados de los cinco pares

Se compararon, sin cambiar coordenadas ni orden: tipo/validez/área de entradas; within/covered_by en ambas direcciones; intersección, diferencia y unión en ambos órdenes; identidades de partición y unión; coherencia de contención frente a overlay. La tolerancia de identidad es la existente de **1 m²**, sin reajuste. También se conserva la validez de resultados como diagnóstico explícito. No se aplicaron snap, grid_size, set_precision, buffer, reparación, simplificación o extrapolación.

| Par fijado | Hallazgo en 3.14.1 | Hallazgo en 3.15.0 | Alcance |
| --- | --- | --- | --- |
| MYD14 temprano 818/1166 | I=0; residuo de partición q y unión ≈2.656.776,365251 m² | Misma contradicción de área | No restaurado |
| MYD14 tardío 833/1149 | I≈2,96×10⁻⁸ m²; identidades dentro de tolerancia; resultados válidos | Igual conclusión; cambia una cantidad ínfima | Pasa ambos; no es reparación |
| MYD14 tardío 844/1161 | Identidades cierran, pero q\\p y ambas uniones producen MultiPolygon inválido | Mismo patrón | Fallo de validez de salida, no de esas identidades de área |
| VNP14IMG temprano 2051/3869 | within y covered_by verdaderos; I=0 y p\\q≈177.775,386520 m², igual al área p | Misma contradicción; identidades de área cierran | No restaurado; las identidades solas no detectan el fallo |
| VNP14IMG temprano 2076/3864 | Contención verdadera con I=0 y p\\q≈179.084,116595 m²; residuo de partición q/unión ≈179.084,116582 m² | Misma contradicción y residuo | No restaurado |

Todas las entradas son Polygon válidos en ambos motores; no se registran errores CAPI. En los cuatro contraejemplos fallidos la intersección de área cero es LineString en ambos órdenes, no una demostración de ausencia de soporte físico. La igualdad del resultado incorrecto al invertir operandos no reproduce por sí sola el síntoma particular descrito en GH-1499. Hay diferencias numéricas diminutas entre algunas áreas de versiones; **no se afirma identidad bit a bit entre motores**, sino ausencia de restauración de estos checks.

Los [resultados CAPI baseline](evidence/geometry-engine-diagnostic/baseline-capi.json), [baseline Shapely](evidence/geometry-engine-diagnostic/baseline-shapely.json), [comparador](evidence/geometry-engine-diagnostic/comparator-capi.json) y [tabla conjunta](evidence/geometry-engine-diagnostic/comparison.json) conservan todas las magnitudes y tipos, incluidos resultados desfavorables. Los controles se verificaron además contra áreas analíticas, predicados esperados y tipo de intersección —LineString en contacto— en las tres ejecuciones, doce combinaciones motor/control en total.

## Reproducción y revisión

Órdenes históricas ejecutadas, dentro del cap:

```sh
.venv/bin/python pipeline/geometry_engine_diagnostic.py --freeze
.venv/bin/python pipeline/geometry_engine_diagnostic.py --run \
  --library .runtime/geometry-engine-diagnostic/build/lib/libgeos_c.1.21.0.dylib
```

El helper rechaza sobrescribir evidencia, comprueba hashes de código/protocolo/fixtures antes de cada proceso y conserva el deadline. Las órdenes no autorizan un nuevo experimento fuera del cap; un reproceso posterior requeriría otro protocolo. La revisión puede comprobar fuentes, hashes, WKB y resultados guardados sin modificar estudios anteriores. El [manifiesto](evidence/geometry-engine-diagnostic/manifest.json) registra hashes de todos los artefactos; las bibliotecas y el tar de fuente no se incorporan al repositorio.

La revisión independiente informó ausencia de bloqueantes para este diagnóstico: reprodujo directamente los nueve pares en Shapely con las mismas operaciones/áreas/flags y comprobó freeze, manifiesto y linkage CAPI/núcleo. Esa revisión no valida el ledger 24B completo ni certifica geometría física. No se intentó una segunda versión de GEOS ni un workaround favorable.

## Decisión y límites

Conservar **24B como entrega parcial con fallo de operador pendiente**. Este diagnóstico no reejecuta ni reemplaza sus outputs. Mantener 25 y la extensión real de bordes 26 bloqueados hasta resolver la representación/algoritmo y validar nuevamente particiones, disjunción y uniones comunes bajo un protocolo distinto, con revisión independiente. Haber encontrado el mismo fallo fuera de Shapely no convierte la geometría nominal en verdad física.

No se abrieron FIRE, QA o clases, no se descargaron datos científicos, no se calcularon estados conjuntos o concordancias y no se modificó producción. G1, exposición física verificada y validación global del ledger permanecen falsos. No hubo commit o push desde esta tarea.
