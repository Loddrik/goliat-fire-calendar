# Estudio29: dependencia del origen de coordenadas en ejemplos geométricos

Diagnóstico ejecutado bajo protocolo `9f324a4`, con cap propio 2026-11-15T05:04:54.272007Z–05:34:54.272007Z, incluida revisión. No se amplió el cap24B, cambió reloj, instaló software o reejecutó su ledger. Se preservan24B fallido y27 negativo. Este estudio no ejecuta25/26/28 ni habilita comparaciones de estados.

## Resultado acotado

Sobre los cinco pares WKB previamente fijados y cuatro controles, el baseline original reprodujo exactamente las nueve filas de27. Con **el mismo Shapely2.2.0/GEOS3.14.1**, trasladar ambos operandos al único origen AOI prefijado produjo resultados que pasan todos los controles locales fijados. La equivalencia de coordenadas se certificó completamente antes de los overlays traducidos:5271 tuplas,10542 restas escalares comprobadas mediante `Fraction.from_float`,19 geometrías incluyendo todos los operandos/anillos/cierres y la AOI. No se descartó ninguna coordenada o ejemplo.

El baseline tenía cuatro regresores fallidos y uno que ya pasaba esos controles. Por tanto, el resultado correcto es **1/5→5/5 pases locales**, no cinco errores demostrados reparados. Los cuatro controles sintéticos pasan en ambas representaciones.

| WKB previamente fijado | Gate local original | Gate local centrado | Intersección original m² | Intersección centrada m² |
|---|---|---|---:|---:|
| Aqua temprano818/1166 | falla | pasa | 0 | 2656776.365251 |
| Aqua tardío833/1149 | pasa | pasa | 0.0000000296 | 2495637.940578 |
| Aqua tardío844/1161 | falla | pasa | 0 | 2610235.181689 |
| VIIRS temprano2051/3869 | falla | pasa | 0 | 177775.386520 |
| VIIRS temprano2076/3864 | falla | pasa | 0 | 179084.116595 |

**La segunda fila es una limitación sustantiva del gate:** pasaba las identidades/predicados locales27 pese a devolver una intersección casi nula, y también pasa tras un cambio de área de≈2.496 km². No se considera validación de su área por el mero pase. La futura revalidación completa debe exigir cierre entre sumas de áreas comunes y la intersección de uniones, disjunción y representación de propietarios para ambos casos/prioridades. Estos cinco ejemplos no sustituyen ese control.

El máximo residuo absoluto de las identidades centradas fue `2.0070001482963562e-7 m²`, frente a tolerancia fija1 m². Las áreas calculadas de **todos los operandos** se conservaron exactamente como valores float64 (diferencia reportada0 m²). Los resultados fueron válidos y finitos; bounds de intersección dentro de bounds de entrada e intersecciones no mayores que cada operando. Los cuatro fallos originales tenían intersecciones lineales de área0; centrados producen polígonos o multipolígonos. Tipo y validez se reportan, sin tratar fragmentos como réplicas científicas.

Esto demuestra dependencia de los resultados computacionales del origen en esta colección seleccionada de ejemplos. No identifica una única causa interna, prueba el PR1499, acredita un motor correcto en general ni mide un error geográfico físico. Tampoco certifica todavía toda la geometría24B.

## Exactitud previa e invariantes

Origen único leído del índice público GEO previamente hashed:

- EPSG:32718, `center_xy=[722459.8026976171,5902205.764776958]`.
- Representaciones exactas float: `0x1.60c379afb2e9cp+19`, `0x1.683df70f21b0ep+22`.
- SHA índice: `6cbcf6b06506c22330045119378639eca3f392b8125a72d36fb350dab4421cfb`.

Cada resta `x−cx`/`y−cy` se verificó contra su resultado racional exacto; cada inversión devolvió todos los bits originales. Se conservaron dimensión2D, tipo, número/orden de componentes, anillos y coordenadas de cierre. También se comprobaron los controles sintéticos al trasladarlos por ese mismo origen, sin ajustar su localización para favorecer exactitud. No se usaron snap, grilla de precisión, escalamiento, nuevos vértices, simplificación, reparación o selección de origen.

El certificado independiente es `exactness-certificate.json`, SHA `98052130f5138530b6dae95cc45967e183ece384089d4810a0aee96c944d5615`; indica explícitamente que aún no habían comenzado overlays traducidos. Antes del run un guard de orquestación comprobó su vínculo al código/freeze, exactamente las19 entradas esperadas, los hashes de todos los WKB centrados y el presupuesto de salida; queda registrado en `execution-link.json`, SHA `8103d6e616d71a06e6fb4fdc310b85ba6e8c0cbb27ffb6b6182dd6ce9eff7ee4`. El revisor independiente confirmó esos checks antes del run.

## Método y trazabilidad

Código congelado antes de overlays: `pipeline/coordinate_origin_diagnostic.py`, SHA `52575983c1d5bc106bb5030c0f4a417c3f895a75ee43f0a7c1726d51d0139aca`; freeze SHA `fb52da253740d6cf36269009b923ee27de1b6c04f3c731daf5c1d2f166d43695`. `origin.json` SHA `66cc481d70ce04e269fad79c30b127df790b52a3eb7ffaa7291e9dc443634793`. Incluye hashes de binarios GEOS/Shapely del entorno original y del helper27.

Se reutilizó únicamente `finish_metrics` puro de27, conservando sus expresiones de áreas, identidades, predicados y umbral1 m². No se invocó su worker, C API3.15, driver o deadline. El cap29 procede de `.runtime/coordinate-origin-cap.json` y se conserva en un snapshot público. Cada fila baseline se compara exactamente con la fila27 antes de emitir su comparación centrada. No se seleccionó orden de operandos por resultados: ambos órdenes de intersección, diferencia y unión se ejecutan para todos los pares.

Siete tests sintéticos previos comprobaron todos los anillos/componentes/cierres, rechazo completo ante resta no exacta, preservación de bits incluyendo cero firmado, rechazo3D, rechazo de una coordenada no finita, controles analíticos y controles enteros trasladados. El warning del test NaN es intencional para verificar rechazo, no un input real omitido. El código no se modificó después de freeze.

El límite era2M tuplas y50MiB de salida; se consumieron5271 tuplas y aproximadamente0.30MiB. Los WKB centrados se guardan sin compresión por su pequeño tamaño, conservando hashes; no se necesitaron instalaciones, credenciales, descargas, datos RAW o máscaras FIRE/QA. El presupuesto de salida se comprueba durante la ejecución y el guard registró229680 bytes antes de overlays. El manifiesto final conserva hashes de artefactos y los snapshots; la revisión humana vive fuera del directorio para no invalidarlo.

Comandos ejecutados desde el repositorio:

```sh
.venv/bin/python -m unittest discover -s tests -p test_coordinate_origin_diagnostic.py
.venv/bin/python pipeline/coordinate_origin_diagnostic.py freeze
.venv/bin/python pipeline/coordinate_origin_diagnostic.py certify
# Guard externo code/freeze/19entradas/hashes/cap, registrado en execution-link.json.
.venv/bin/python pipeline/coordinate_origin_diagnostic.py run
```

Los stages rechazan sobrescribir freeze/certificado/resultados. Una reproducción posterior debe conservar este intento, declarar cap nuevo y documentar cualquier cambio de orquestación; no modificar el reloj para hacer pasar el cap viejo. No usar este comando de nuevo sobre los mismos outputs.

## Decisión conservada

El diagnóstico positivo sólo permite diseñar una revalidación ampliada con protocolo nuevo: misma construcción CORE en coordenadas originales, certificación de traslación exacta **después** de construir vértices y **antes** de operaciones de conjuntos, mismos inputs/políticas y todos los cierres globales antes de reutilizar etiquetas individuales. No cambiar CORE para rescatar los dos de seis positivos Aqua2023 sin polígono; siguen siendo registros preservados con área desconocida.

Revisión independiente de `hurdle_design`: sin bloqueantes. Recalculó racionales y bitinverse de las5271 tuplas desde los WKB existentes sin nuevos overlays, verificó hashes, las nueve filas baseline y controles/residuos/tipos, y repitió los siete tests. Confirmó el alcance condicional y que no acredita ledger/G1 o causa única.

24B original sigue fallido;25/26/28 no se ejecutaron aquí. `gate1_passed=false`, `full_ledger_validated=false`, `physical_exposure_verified=false`. No se valida PSF, exposición, tiempo por píxel, causalidad de incendios o eficacia de un modelo. Los13 contrastes dimensionalesVIIRS anteriores siguen selectivos. El siguiente paso requiere revisión independiente de29 y autorización explícita de su propio protocolo, no una promoción automática desde estos cinco pares.
