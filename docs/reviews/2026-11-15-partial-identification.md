# Identificación parcial sintética: implementación y verificación

La API pura implementa el [protocolo congelado](2026-11-15-partial-identification-protocol.md), adoptando el [diseño](2026-11-15-partial-identification-design.md). Produce cotas exactas sobre clasificaciones registradas en un universo hipotético disjunto y de peso unidad. No se leyó raw, no se compararon sensores reales y no se calcularon scores de modelos. G1 permanece falso. Las cotas son **sharp únicamente dentro del modelo cartesiano hipotético declarado**, sin interpretación de intervalo de confianza físico.

## Resultado y contrato

`pipeline/partial_identification.py` expone `bound_registered_classifications(request, *, limits=None)`. La entrada y la salida son estructuras compatibles con JSON; no hay acceso a archivos, red, reloj, aleatoriedad ni estado global mutable durante una llamada. Versión de esquema: entero 1. La regla positiva externa se identifica mediante un ID explícito. El universo fijo requiere `scope.status=fixed_hypothetical`, `universe_id`, `disjoint=true`, `unit_weight=1`; las unidades tienen IDs únicos, observaciones A/V y conjuntos no vacíos de pares 00/01/10/11 cuyas proyecciones coinciden exactamente con los conjuntos de clasificaciones registradas. `cartesian_across_units` es una restricción del conjunto de escenarios, no una afirmación probabilística de independencia.

El soporte no identificado usa `scope.status=unidentified` y una razón, sin unidades admitidas. Devuelve `not_identified`, `metrics=null` y decisión `unknown`, sin extremos numéricos inventados. Una entrada inválida devuelve `invalid_input`, tampoco resultados científicos. No se admite automáticamente una unidad a partir de un centro nativo o un vecino próximo.

La DP conserva estados `(intersección, unión, positivos_A)`. A partir de ellos calcula conteos exclusivos A/V, desacuerdo total, Jaccard y fracciones exclusivas con sus denominadores explícitos. Las razones se comparan como `Fraction` y se serializan en numerador/denominador reducidos; no se usan decimales para elegir extremos. Los denominadores cero se mantienen mediante `defined_possible` y `undefined_possible`; si ninguna completación define la razón, ambos extremos y testigos son nulos. Las cotas de métricas diferentes no implican que sus extremos sean simultáneamente alcanzables.

Cada extremo lleva un testigo completo en el universo hipotético. Se canonicaliza el orden por ID de unidad y por par; entre testigos que alcanzan un mismo extremo se conserva el primero lexicográfico. Se almacenan predecesores por capa y se reconstruyen sólo los testigos de extremos, evitando materializar un camino completo para cada estado final. Los estados alcanzables se devuelven ordenados. La conservación de todos los estados sin poda y la enumeración cartesiana de pares dan la garantía de exactitud condicional; no se asume esa garantía para otros tipos de soporte o acoplamiento.

Los límites predeterminados son 200 unidades, 100.000 estados por capa, 200.000 predecesores almacenados y 2.000.000 transiciones intentadas. Pueden reducirse explícitamente para probar rechazos; aumentarlos por encima del protocolo se rechaza. Excederlos devuelve `resource_limit`, métricas nulas y decisión desconocida, sin estados parciales ni intervalos aproximados. El estado inicial vacío cuenta como un estado; los predecesores cuentan sólo las capas posteriores. Alcanzar exactamente un límite es válido; excederlo no lo es.

QA, inclusión de política y FRP son metadatos validados y no cambian los pares permitidos ni los resultados. Una detección final conocida positiva con M13 conserva el valor registrado 1 aunque una política indique exclusión. Una FRP registrada cero se conserva como reporte, sin inferir energía cero, causa del flag o intervalo físico de FRP. Esta API no calcula ninguna cota de FRP.

La decisión abstracta devuelve `review_human` cuando alguna clasificación registrada es positiva en el escenario y `no_review_from_this_rule` en otro caso. El conjunto de acciones puede ser invariante o variar; soporte no identificado y errores computacionales dan estado desconocido. Esta regla no está conectada a alertas ni producción y no certifica ausencia de fuego.

## Evidencia sintética

Los [artefactos JSON](evidence/partial-identification/manifest.json) contienen cinco entradas y salidas reproducibles: desconocido distinto de cero, positivo M13 con FRP reportada cero, soporte no identificado, universo vacío conocido y siete unidades con restricciones mixtas. Todos declaran `synthetic_only=true`, `physical_validation=false` y `G1=false`. El manifiesto identifica hashes SHA-256 del protocolo, diseño, implementación y pruebas.

En el ejemplo desconocido-distinto-de-cero, A es cero y V admite cero o uno: la acción varía; Jaccard es cero cuando está definida y también puede estar indefinida. Reemplazar V por cero perdería una completación admisible. En el ejemplo M13, A=0 y V=1 con exclusión de política y FRP reportada cero: el positivo registrado se conserva, la acción abstracta es invariante y no aparece una estimación de energía. Cuando el soporte es no identificado, no se admite la unidad ni se produce un intervalo.

## Verificación

Comando ejecutado:

```sh
python3 -m unittest discover -s tests -p test_partial_identification.py -v
```

**Siete pruebas pasan en 5,853 segundos** en el entorno local. El oráculo es independiente: enumera todas las completaciones de cada entrada, cuenta directamente los pares 10/01/11 y positivos de cada etiqueta y calcula razones y testigos sin usar constantes de transición ni funciones de la DP.

La cobertura fijada contiene 5.316 entradas principales y 333.425 completaciones enumeradas, además de metamorfismos y casos de contrato/recursos. Para n=0..3 se cubren todas las entradas de los 15 subconjuntos no vacíos de pares por unidad: 3.616 entradas. Para cada n=4..7 se cubren 15 entradas homogéneas, los 210 ciclos alternantes de pares de subconjuntos ordenados distintos —incluidas ambas fases— y 200 entradas generadas con semilla 20261115: 1.700 entradas en total. La exhaustividad para n=4..7 corresponde a las completaciones de cada entrada cubierta, no a las 15^n entradas posibles.

Se comparan conjuntos completos de estados alcanzables, extremos racionales exactos, flags de indefinición, acciones y testigos lexicográficos de todos los extremos. Los metamorfismos comprueban invariancia ante orden de unidades/pares, intercambio A/V con permuta de direcciones y expansión de conjuntos permitidos. Las pruebas de metadatos confirman igualdad de toda la salida ante cambios exclusivos de QA/política/FRP. Los rechazos cubren esquemas, estimandos, acoplamiento global, pesos, disjunción, IDs duplicados, pares vacíos/inválidos, proyecciones contradictorias y soporte desconocido con unidades admitidas; los límites computacionales producen no-resultados explícitos.

La suite tarda menos de dos minutos sin reducir la cobertura fijada. No se incorporaron dependencias nuevas ni cambios de CI/modelos. No se modificaron documentos previos ni se hicieron commits o push desde esta tarea. Aplicar la API a observaciones reales requerirá otro protocolo que justifique unidades comunes, soporte, exposición y restricciones.
