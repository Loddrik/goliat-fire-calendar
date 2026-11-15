# Estudio32A: pertenencia y propiedad exactas en puntos prefijados

**Resultado técnico: pase de los gates GEO, confirmado por revisión independiente.** No se leyeron FIRE, QA o el catálogo positivo. El resultado cambia la pregunta a propietarios nominales en puntos fijos; no repara áreas continuas30B, no habilita estados conjuntos y no acredita G1.

Protocolo congelado `eaec7ca`, plan31 ratificado `793ade7`. Cap real06:16:47.752408–07:01:47.752408UTC del15 de noviembre2026, incluida revisión, sin reinicio. Ejecución terminada aproximadamente06:27UTC. Código `pipeline/point_ownership_audit.py` SHA `b03a9c9e17dee5fef270b09d1f0c6f5996c37c6ac2741207a9b6925df315f607`; freeze SHA `1f2e2fc462935444c1a8b0347d99d04b6e46081ca3af30052e900207cff4c19a`.

## Alcance y población

Mismos dos casos2019-01-03/2023-02-10, AOI50×50km y universo CORE/halo/índices del protocolo. Se reutilizaron únicamente los NPZ **anteriores a overlays** de30B, verificando hash contra su manifiesto y certificado. No se utilizaron sus propietarios/intersecciones fallidos.

Los101038 quads construidos y la AOI pasan simplicidad, cierre y área exacta no nula. El universo indexado conserva85451 quads según los flags previos, sin nuevo filtro de actividad o calidad. Los quads vecinos/no incluidos también se validaron; no se omitió una geometría difícil para conseguir el pase. Los IDs nativos son únicos y conservan scan/detector.

Se comprobaron505195 tuplas contra la representación mundial fuente: hash de vértices reconstruidos, retorno bitidéntico y resta racional exacta de su origen. El origen permanece `[722459.8026976171,5902205.764776958]` EPSG:32718. Internamente se expresan todos los valores dyadic como enteros Python en una escala común `2^33`, sin pérdida de bits: es una representación exacta de los mismos racionales, **no** una nueva grilla de redondeo o una precisión geográfica supuesta.

La pertenencia usa orientaciones, frontera y paridad exactas sobre esos enteros arbitrarios. No se importó ni usó Shapely/GEOS para candidatos, simplicidad, pertenencia o propiedad. Los puntos mundiales se definen como el origen racional exacto más offsets enteros; no se redondean a otra coordenada float antes del predicado.

## Índice exhaustivo y escenarios independientes

Para cada quad del universo indexado, bbox racional→rangos enteros cerrados incluye sus fronteras, recortando sólo al dominio abiertoAOI. Cada rango calculado con división entera se verificó independientemente mediante `Fraction` y ceil/floor. Se conservan TODOS los postings punto/quad, incluso los que el predicado clasifica fuera del polígono. El conteo esperado de cada rango cierra con el realmente enumerado; no hay nearest, selección de positivos o descarte de candidatos.

Se generaron por separado las cuatro grillas de cada caso: pasos250/500m y fases0/125m diagonal. Por fase, los puntos500m se comprobaron contra los250m, comparando candidatos, relaciones exactas, todas las causas y ambos propietarios. No se copió la solución fina para fingir una validación gruesa. Ocho verificaciones anidadas por instrumento/caso/fase terminaron correctamente.

Dominio abierto `−25000<x,y<25000m`. La fase0 tiene39601 puntos a250m y9801 a500m; fase125 tiene40000 y10000. Son poblaciones distintas entre fases: sus diferencias de conteos no identifican un efecto causal ni representan toda incertidumbre de fase. Todos los escenarios quedan publicados; no se escoge el de mayor soporte.

La precedencia es frontera→tiempo desconocido→múltiples interiores mismo scan→sin soporte nominal→propietario identificado. Se guardan también todas las causas superpuestas. Early/late sólo ordenan candidatos de scans conocidos; empate por menor scan. Inputs duplicados o quads no simples habrían bloqueado el estudio. `−1` representa propietario no identificado, nunca un propietario ficticio0.

## Resultados GEO por escenario

La tabla muestra puntos con propietario nominal identificado y puntos sin soporte del universoCORE. No es área, disponibilidad de observación útil o ausencia de fuego.

| Caso/producto | Fase m |250m: propietario / sin soporte |500m: propietario / sin soporte |
|---|---:|---:|---:|
|2019 Aqua|0|33260 /6341|8239 /1562|
|2019 Aqua|125|33570 /6430|8393 /1607|
|2019 VIIRS|0|38212 /1389|9459 /342|
|2019 VIIRS|125|38607 /1393|9655 /345|
|2023 Aqua|0|39601 /0|9801 /0|
|2023 Aqua|125|40000 /0|10000 /0|
|2023 VIIRS|0|39579 /22|9795 /6|
|2023 VIIRS|125|39978 /22|9995 /5|

En estas grillas no aparecieron consultas con frontera, tiempo desconocido o varios interiores del mismo scan. Sus estados no se eliminaron del método: tienen tests y columnas explícitas, y conservan conteo0 observado. El número de puntos identificados es el mismo para ambas prioridades porque la ambigüedad se decide antes del orden; **los IDs de propietario sí se calculan y conservan separadamente** para temprano/tardío.

El roster por quad contiene candidatos bbox, incidencias interiores/frontera y asignaciones por ambas prioridades, junto con el flag de pertenencia al universo indexado. Los quads sin punto interior incluyen quads de halo y geometrías pequeñas respecto del muestreo; no se atribuye ese conteo únicamente a aliasing ni a falta de actividad. El roster representa quads construidos, no inventa footprints de píxeles de borde sinCORE.

Los dos positivos Aqua2023 sinCORE permanecen en el catálogo original intocado; este estudio **no lo abrió ni cruzó**. No se puede afirmar todavía cuánta actividad registrada retienen los puntos. El control de esa selección exigiría otro protocolo, conservando esos dos registros con geometría/área desconocida. Sin punto de consulta no significa sin detección.

## Presupuestos y trazabilidad

Contadores finales:198804 consultas (caso×fase×paso, sin multiplicar sensores/prioridades);482769 candidatos punto/quad evaluados una vez antes de políticas;3143544 evaluaciones exactas de segmento, incluyendo validación e inclusión; picoRSS145870848 bytes en macOS. Todos quedan bajo los límites prefijados. La salida física es aproximadamente5.45MB, bajo200MiB. Los16 grupos instrumentales, las cuatro cohortes de cada caso y ambas prioridades están conservados en NPZ sin pickle y JSON con leyendas/índices/hashes.

Nueve tests sintéticos precedieron la geometría real: simplicidad/no degeneración, cierre y rechazo de floats truncables, quads no convexos, orientación inversa, frontera, bbox dyadic, enteros superiores a64bits, precedencia con causas simultáneas, tiempos/scan/no soporte, desempate y nested generado independientemente. Un cambio intencional de propietario en el test anidado produce fallo. Helpers/tests puros no leen `.runtime` ni clocks; sólo el driver aplica los presupuestos.

El primer intento de **prefreeze** abortó porque el plan ratificado había cambiado de nombre (`joint-plan-31-draft.md`→`joint-plan-31.md`). Se preservaron error y snapshot previo en `preflight-01/`; únicamente se corrigió esa ruta antes del freeze real. No había ejecución de quads/puntos o resultados que pudieran seleccionarse por su valor. El cap no cambió. Código y datos del intento principal permanecen congelados después de esa corrección.

Freeze incluye fuentes efectivas nombradas, certificado/manifiesto anterior, referencia de scan, origen, cap/protocolo/plan y hashes del intérprete/NumPy. No protege archivos concurrentes ajenos indiscriminadamente ni usa outputs32B como entrada. El manifiesto del intento principal identifica todos sus archivos; `preflight-01` conserva el fallo de orquestación por separado. No se modificó ningún estudio previo, paquete, lock o producción.

Comandos del intento principal:

```sh
.venv/bin/python -m unittest discover -s tests -p test_point_ownership_audit.py
.venv/bin/python pipeline/point_ownership_audit.py freeze
.venv/bin/python pipeline/point_ownership_audit.py run
```

Los stages rechazan sobrescribir el intento. Una reproducción posterior exige ruta/cap de orquestación nuevos y documentados; no cambiar el reloj o fingir que se ejecuta dentro de un cap vencido.

## Decisión permitida y límites

La revisión independiente de `independent_review_23` pasó sin bloqueantes. Recalculó todos los101038 quads,482769 postings y16 grupos con una implementación propia: candidatos mediante `bisect` sobre las grillas, diferente deceil/floor; pertenencia mediante windingnumber entero exacto, diferente deparidad. Reprodujo propietarios, causas, rosters y79204 comprobaciones de puntos compartidos anidados, además de los hashes/inputs/binarios y los nueve tests. No modificó el código o las salidas del autor ni usó GEOS o nuevas etiquetas.

El paseGEO, tras revisión independiente, sólo permitiría diseñar un protocolo de estados registrados sobre puntos, con población/QA/retención/tiempos/sensibilidades explícitos. No autoriza replay automático. No multiplicar conteos por tamaño de celda para presentar una reparación de áreas30B. Dos escenas siguen siendo dos casos; puntos vecinos comparten píxeles/scans, sin intervalosIID o validación física por multiplicar muestras.

`gate1_passed=false`, `QA_FIRE_positive_catalogue_read=false`, `continuous_area30B_repaired=false`. SuspectMODIS, oportunidad física, PSF y exposición por píxel siguen pendientes. No hay matriz de clases conjunta, comparación de detecciones o mejora demostrada del modelo mensual. Este operador exacto responde una pregunta nominal discreta distinta.
