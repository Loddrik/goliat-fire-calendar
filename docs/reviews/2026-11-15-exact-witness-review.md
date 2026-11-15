# Revisión30A — testigos exactos de intersección geométrica

**Resultado:** los cinco pares contienen un cuadrado racional certificado de4m² en su intersección nominal. Esto refuta las áreas de intersección originales29 en ambos órdenes, incluido el caso833 que pasaba los gates anteriores. Las áreas centradas29 superan esa cota y por ello no quedan refutadas; **no quedan validadas**.

No se ejecutaron nuevos overlays, no se importóGEOS/Shapely/Numpy para el oráculo, no se leyeron clasesFIRE/QA y no se modificaron29/24B ni producción. G1false y25/26pendientes se conservan.

## Congelamiento y recursos

- Protocolo30A97dbd33 y diseño previos. Cap05:24:38.114629Z–05:39:38.114629Z, incluida revisión, sin reinicio.
-12pruebas analíticas pasaron antes de datos. Código, tests, diezWKB, protocolo, diseño y cap congelados: SHA256 `053f73027f46b8773d21325bd0710f5c308ce74398fb959e6baf6352e73e7e1d`, UTC2026-11-15T05:27:26.669986+00:00. Raíz fue notificada antes de run.
- Búsqueda completada y persistida antes de interpretar áreas29; comparación terminada2026-11-15T05:27:36.708473+00:00.
-5226tuplas de coordenadas leídas,9090evaluaciones exactas de segmentos, ambos contadores globales. Ningún límite de128candidatos/2Mtuplas/2Msegmentos/50MiB/k256 se alcanzó.

## Qué certifica cada testigo

El parser stdlib lee exactamente Polygon/MultiPolygon2D finitos y convierte cadafloat64 enFraction binaria exacta. Semántica: unión de componentes, cada exterior menos sus holes; orientación irrelevante. Sin reparación de anillos, coordenadas nuevas inferidas o predicadosGEOS.

En los cinco pares, el primer candidato fijado —promedio racional del exterior del primer componente del operando p— está estrictamente dentro de ambos conjuntos por raycasting exacto. Fronteras se excluyen conservadoramente, incluidos holes y componentes secundarios. Se calcula la distancia cuadrada mínima δ² a todos los segmentos originales de ambos operandos.

El primer hdyádico permitido cumple h=1m y2h²<δ² en todos. El cuadrado racional de centroc y semiladoh queda dentro de la bola sin fronteras; conserva pertenencia y está contenido en ambos conjuntos. Por tanto área de intersección≥4h²=4m². La prueba es local y no calcula el área total. Numeradores/denominadores de c,h,δ²,L, esquinas y segmento más próximo están en results.json/search.json.

## Contraste con las áreas ya existentes29

| Par | Área original pq | Área original qp | Cota exacta | Área centrada pq | Área centrada qp |
|---|---:|---:|---:|---:|---:|
| MYD14_early-818-1166 | 0 | 0 | 4 | 2656776.36525126 | 2656776.36525127 |
| MYD14_late-833-1149 | 2.96371638341952e-08 | 2.96371638341952e-08 | 4 | 2495637.94057758 | 2495637.94057758 |
| MYD14_late-844-1161 | 0 | 0 | 4 | 2610235.18168863 | 2610235.18168863 |
| VNP14IMG_early-2051-3869 | 0 | 0 | 4 | 177775.386519807 | 177775.386519807 |
| VNP14IMG_early-2076-3864 | 0 | 0 | 4 | 179084.116594871 | 179084.116594871 |

Cada comparación usa el racional exacto delfloat de área existente frente aL, sin tolerancia que pueda esconder un cuadrado pequeño. Esta nueva prueba no cambia retrospectivamente el umbral1m² de29: demuestra que los gates antiguos eran insuficientes para acreditar las áreas. En particular833 podía cerrar identidades/predicados consistentes y aun devolver una intersección incompatible con una cota exacta.

No hay selección del mejor centro, del mayor cuadrado o del orden favorable. Los cinco se conservaron; todas las columnas se informan. El límite h≤1m explica queL sea una cota deliberadamente pequeña, no estimación de la gran discrepancia ni de la extensión de una detección.

## Alcance y decisión

La evidencia discrimina un artefacto geométrico numérico del software: hay una región común exacta que las áreas originales no pueden representar correctamente. No acredita que toda área centrada sea correcta, que el origen sea la única causa, que toda la malla/propiedad cierre, ni que haya oportunidades físicas equivalentes. La revalidación global30B necesita sus propios gates y revisión;30A por sí sola no la sustituye ni habilita25.

No localiza fuego, no mide PSF, área quemada, sensibilidad instrumental o verdad física. No resuelve MODISSuspect, timing de píxel, humo/nube, clases desconocidas ni la pregunta causal de cuánto desacuerdo procede de observabilidad. No se modifica el modelo mensual o contrato de publicación.

No encontrar testigo habría significado búsqueda inconclusa, nunca ausencia de intersección. No se produjo ese desenlace en estos cinco regresores seleccionados; no son una muestra aleatoria ni cinco replicaciones físicas independientes.

## Pruebas, reproducibilidad y límites de implementación

12tests sintéticos: parser endian/MultiPolygon y rechazos; holes/fronteras/vértices/horizontales/orientación; componentes solapados; distancias y segmento degenerado; desigualdad estricta y centro racional; búsqueda sin testigo; promedio cóncavo; presupuesto global; clasificación de área; truncamiento128candidatos. Helpers puros no dependen de.runtime ni del reloj: sólo el driver aplica capUTC/presupuesto.

Limitación de auditabilidad para un eventual recurso agotado: siBudget interrumpe un par dentro de find_witness, el driver conserva estado/resource_limit y contadores globales, pero no los intentos parciales de ese par. No se alcanzó recurso ni se perdió intento en este run; no se retocó código congelado para añadirlo después.

Fuentes: `pipeline/exact_geometry_witness.py`, `tests/test_exact_geometry_witness.py`, `docs/reviews/evidence/exact-geometry-witness/{freeze,search,results,manifest}.json`; entradas copian únicamenteWKB29 y hashes. results29 se lee después de persistirsearch; no hay comparación nueva de estados. Revisión matemática independiente completada antes del cap, sin bloqueantes: parserWKB propio, raycasting por signo sin división y distancia por proyección/clamp racional confirman los5testigos, δ², menork, esquinas y cotas. Los10valores originales quedan refutados y los10centrados sólo no refutados. Freeze/manifests verificados por revisor separado.
