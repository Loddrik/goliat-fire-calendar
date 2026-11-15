# Revisión32B — intersección racional del último par registrado30B

**Resultado:** ambos operandos cumplen el dominio prefijado, y su intersección tiene área racional estrictamente positiva, idéntica en ambos órdenes. Es incompatible con asignar área exacta0 a este par. No demuestra que el par sea la causa del fallo30B: el contexto original declara explícitamente `not_necessarily_cause=true`.

## Congelamiento y alcance

Protocolo32B eaec7ca y plan31 anteriores al código/datos. Cap06:16:47.752408Z–06:46:47.752408Z, incluida revisión, sin reinicio. Doce pruebas analíticas pasaron antes de leer geometría real. Freeze SHA256 `d8763b48f6671f7c907d8df2f83e5b1a415d47f4c40f683ae0deb4cf829c5cdd`, UTC2026-11-15T06:20:38.324791+00:00; raíz avisada antes del run. Hashes de dosWKB+contexto se verificaron contra el manifest30Battempt-01; parser30A se reutiliza como helper puro, fijado por hash. Código, tests, protocolo, cap y copias de entradas quedaron congelados.

Ningún GEOS/Shapely/Numpy en el oráculo, ni nuevos overlays de motores flotantes, clasesFIRE/QA, descargas, credenciales, modelos o producción. No se modificaron30B/29/30A. El par es el último registrado por el driver anterior; no se seleccionó por área, positividad o conveniencia.

## Dominio exacto y algoritmo

El parser sólo aceptaPolygon2D finito de un anillo cerrado, sinholes,3–256vértices únicos sin contar cierre. Fuera del dominio→unknown, sin reparar ni triangular. Se comprobaron productos cruzados exactos, área no nula, ausencia de intersecciones entre segmentos no adyacentes y de backtracking collineal adyacente. Convexidad se verifica por signos exactos. Ambos eran clockwise; se invirtió matemáticamente el orden aCCW, preservando las coordenadas y su conjunto geométrico. No snap, epsilon, grid, simplificación o vértices fuente alterados.

| Operando | Vértices | Pares de segmentos no adyacentes examinados | Simple/convexo | Normalización |
|---|---:|---:|---|---|
| p | 4 | 2 | Sí/Sí | Orden invertido aCCW |
| q | 5 | 5 | Sí/Sí | Orden invertido aCCW |

Sutherland–Hodgman conFraction usa semiplanos cerrados, intersecciones racionales exactas y deduplicación exclusivamente consecutiva de puntos iguales. No elimina puntos por cercanía ni trata collinearidad con tolerancia. La salida es un triángulo en ambos órdenes; áreas shoelace coinciden como racional, no aproximadamente. Se conservan todos los vértices numerador/denominador, pasos por arista y certificados de dominio.

## Resultado

Área exacta:

`75245373460380228544614245301434420217 / 413035307066988553173563968428541782654799839232 m²`

Aproximación únicamente para lectura: **1.8217661341037967×10⁻¹⁰m²**. El signo positivo es exacto; la aproximación no se usa en decisiones. Resultado positivo refuta área0 para estos conjuntos poligonales y es compatible con interior bidimensional; no calcula el error de ningún otro par. No se recalculó el overlayGEOS ni se fabricó un valor de fallo ausente del contexto.

Que sea pequeña en metros cuadrados **no demuestra que sea globalmente despreciable**: no hay aquí cota agregada de todos los pares, relación con una pérdida de decisión, prueba de disjunción global ni permiso para relajar30B. Tampoco se identifica esta discrepancia como única causa. El diagnóstico deja30B fallido y no autoriza otro rerun o cadena de reparaciones.

## Recursos y pruebas

Run completado2026-11-15T06:20:46.440903+00:00. Se usaron1104operaciones aritméticas exactas, muy por debajo de2M. Driver aplica capUTC, límites10MiB de entradas,1024vértices intermedios,4096bits para numeradores/denominadores y50MiB de salidas. Cada operación aritmética controlada comprueba su resultado; los helpers y tests no dependen de.runtime o relojes históricos. Ningún límite se alcanzó.

Doce pruebas analíticas: disjunto/contenido/parcial/identidad/tangencias de línea y punto, orientación y collinearidad hacia adelante, triángulo racional, concavidad/degeneración/duplicados rechazados, cruces no adyacentes, backtracking, segmentos collineales, parser/layouts y rechazos, límites de vértices/bits/operaciones e intermedios, salidas vacía/lineal. No se usaGEOS como expectativa de pruebas.

Artefactos: `pipeline/exact_local_overlay_audit.py`, `tests/test_exact_local_overlay_audit.py`, `docs/reviews/evidence/exact-local-overlay-audit/{freeze,results,manifest}.json` y snapshots/copias de entradas. Hashes finales de código/parser/entradas/salidas verificados; revisión matemática independiente completada antes del cap sin bloqueantes: un algoritmo diferente —intersecciones exactas de pares de aristas, vértices contenidos y convexhull monótono exacto, sinSutherland–Hodgman— produjo los mismos3vértices y la misma área racional. Freeze/manifests y12tests verificados por revisor separado.

## Decisión y límites físicos

Cerrar32B como adjudicación exacta local positiva y conservar32A como rama separada de nuevo estimando discreto. No concede pase al ledger continuo, puntos, comparación de estados25/26 oQA. No acreditaPSF, oportunidad física, tiempo por píxel, ausencia/presencia de fuego ni resolución deMODISSuspect. G1false y la pregunta causal original siguen abiertos.
