# Diseño de identificación parcial sobre clasificaciones registradas

Estado: propuesta de API pura; pendiente de protocolo del responsable. No autoriza implementación, cómputos con datos reales, nuevas descargas, alertas ni cambios de G1. Sólo se usan universos hipotéticos fijados y ejemplos sintéticos. Fecha nominal del estudio: 15 de noviembre de 2026.

## Estimando y condiciones de entrada

Para cada unidad común hipotética `j`, A y V son indicadores binarios de **clasificación positiva registrada**, no de fuego físico, detección verdadera, energía ni equivalencia de respuesta instrumental. La regla que convierte clases registradas en positivo debe estar fijada y versionada antes de calcular. Las unidades son átomos disjuntos de un universo común finito: cada unidad cuenta una vez y tiene el mismo peso. Este diseño no calcula áreas ni mezcla conteos de centros nativos. Un identificador de universo no acredita su validez física.

Se distinguen dos incertidumbres:

- **Clasificación desconocida en una unidad admitida:** puede representarse mediante los valores posibles `{0,1}` y restricciones explícitas entre A y V.
- **Soporte común no identificado o no acotado:** no permite admitir unidades, rellenar ausencias con cero ni construir el universo mediante una unión de centros. La API devuelve `not_identified` sin cotas numéricas. No fabrica un intervalo `[0,1]`.

Los límites que siguen son exactos sólo para el universo hipotético y la clase de escenarios declarada. No resuelven footprints, exposición, integridad ni elegibilidad global pendientes. Si se usan en el futuro soportes acotados alternativos, cada universo deberá evaluarse por separado y las restricciones entre universos deberán declararse en otro protocolo.

## Contrato de API propuesto (sin implementación)

Función pura: `bound_registered_classifications(request) -> BoundsResult`. Sin archivos, reloj, red, estado global, aleatoriedad o ajustes de modelo. La misma entrada produce la misma salida canónica.

`request` contiene:

| Campo | Contrato |
| --- | --- |
| `schema_version` | Versión explícita del contrato. |
| `target` | Literal `registered_positive`; cualquier otro estimando se rechaza. |
| `positive_rule_id` | Regla externa fijada de clasificación positiva. No se infiere de QA o FRP. |
| `scope` | Unión discriminada: `fixed_hypothetical` con `universe_id`, declaración de unidades disjuntas y peso uno; o `unidentified` con razón y evidencia pendiente. Un soporte no acotado usa la segunda variante. |
| `units` | Lista de `UnitScenario`, sólo para `fixed_hypothetical`; IDs únicos. Una lista vacía representa explícitamente un universo vacío conocido. `unidentified` no admite una lista de unidades supuestamente comunes. |
| `coupling` | Literal `cartesian_across_units`. Restricciones globales o dependencia entre unidades no representables aquí causan error; no se sustituyen por independencia silenciosamente. |

Cada `UnitScenario` contiene `unit_id`, `A`, `V` y `allowed_pairs`. Cada observación A/V contiene `recorded_values`, conjunto no vacío de `{0,1}`, y metadatos separados `qa_flags`, `policy_inclusion` y `frp_status`.

- `allowed_pairs` es un subconjunto no vacío y explícito de `{00,01,10,11}`; el primer bit siempre es A. Debe estar contenido en `A.recorded_values × V.recorded_values` y sus proyecciones deben coincidir con dichos conjuntos. Así las dos representaciones no pueden contradecirse. No se supone producto dentro de una unidad: `{00,11}` expresa una restricción válida distinta de los cuatro pares.
- Una observación final conocida positiva tiene `recorded_values={1}`, aun con QA M13 u otro flag. Los flags nunca cambian ese conjunto automáticamente.
- `policy_inclusion` registra `include`, `exclude` o `undecided` y el identificador de política cuando corresponda. Es metadato: no excluye unidades ni transforma un positivo en cero en este estimando. Otra población seleccionada por política requeriría otro estimando y protocolo explícitos.
- `frp_status` distingue `not_assessed`, `reported` y `unavailable`. `reported` puede conservar un valor registrado cero y flags, pero no contiene ni induce límites de energía física. Ninguna variante cambia `allowed_pairs`. La API no devuelve cotas de FRP.

Si `scope=unidentified`, la salida es `status=not_identified`, `reason`, `metrics=null`, `decision={status:unknown, reason:unidentified_scope}`. La validación estructural de la variante sigue siendo obligatoria. Los errores de contrato son `invalid_input`, nunca un resultado científico ni una cota vacía.

Para `fixed_hypothetical`, la salida es `status=identified_set` e incluye regla, universo, número de unidades, restricciones, estados alcanzables ordenados y resultados siguientes. Cada mínimo/máximo debe incluir un testigo sintético como asignación `unit_id → pair`; se permite un desempate lexicográfico determinista.

## Métricas y límites exactos

Para un escenario completo, sean `I` el número de pares 11, `U` el número de pares distintos de 00 y `P_A` el número de positivos A. Entonces:

- `P_V = U + I − P_A`.
- `A_only = P_A − I` cuenta pares 10; `V_only = U − P_A` cuenta pares 01.
- `disagreement_count = U − I`.
- `jaccard = I/U`, definida sólo si `U>0`.
- `A_only_fraction_of_A = (P_A−I)/P_A`, definida sólo si `P_A>0`.
- `V_only_fraction_of_V = (U−P_A)/(U+I−P_A)`, definida sólo si `P_V>0`.

Los dos últimos nombres fijan la dirección y el denominador. No se llaman sensibilidad, error, precisión ni tasa de fallos. Las cotas de conteos son sus mínimos/máximos alcanzables. Cada razón devuelve `lower`, `upper`, `defined_possible` y `undefined_possible`; extremos nulos si no hay ningún escenario definido. Si hay escenarios definidos e indefinidos, los extremos describen exclusivamente el subconjunto definido y `undefined_possible=true` permanece visible. En Jaccard, ese flag equivale exactamente a que sea alcanzable `U=0`. No se adopta `J(∅,∅)=1` ni cero.

Las razones se guardan como pares enteros numerador/denominador reducidos y se comparan exactamente por productos cruzados. Un decimal opcional es presentación, no el valor usado por el oráculo. Las cotas marginales no forman una caja de combinaciones simultáneamente posibles: los testigos de distintos extremos pueden ser diferentes.

## DP finita y exactitud

Se empieza con el único estado `(I,U,P_A)=(0,0,0)`. Por cada unidad, cada par permitido añade:

| Par A,V | Incremento `(I,U,P_A)` |
| --- | --- |
| 00 | `(0,0,0)` |
| 01 | `(0,1,0)` |
| 10 | `(0,1,1)` |
| 11 | `(1,1,1)` |

Se conservan todos los estados distintos y un predecesor por estado para recuperar testigos. No se podan estados por un objetivo particular. Al terminar, se evalúan las métricas sobre los estados alcanzables. La inducción sobre unidades da correspondencia exacta entre escenarios permitidos y estados alcanzables; cada extremo devuelto es alcanzado por su testigo. Ésta es la garantía de cotas sharp, condicionada a `cartesian_across_units`.

La proyección `(I,U)` basta para Jaccard y desacuerdo total, pero **pierde la orientación 10 frente a 01**. Por eso el estado completo conserva `P_A`. Por ejemplo, los escenarios unitarios 10 y 01 tienen ambos `(I,U)=(0,1)` y diferentes conteos direccionales. No se puede prometer cotas direccionales usando sólo esa proyección. Un límite de recursos explícito devuelve `resource_limit` sin resultados aproximados; no cambia el problema por un ajuste heurístico.

## Decisión abstracta y estados de conocimiento

Regla única: `any_registered_positive → review_human`, aplicada al universo fijado; en cada escenario es `review_human` si `U>0`, y `no_review_from_this_rule` si `U=0`. Esta última etiqueta sólo describe la regla abstracta; no certifica ausencia de fuego ni prescribe no actuar en un sistema real.

La salida enumera `possible_actions` y devuelve `invariant` si contiene una sola acción o `varies` si contiene ambas. `unknown` se reserva para soporte no identificado o resultado no calculable; no es sinónimo de `varies`, cuyo conjunto de escenarios sí está especificado. No hay conexión con producción ni alertas. Se puede etiquetar qué incertidumbre separa dos testigos con decisiones distintas, pero no atribuir causalidad ni valor económico a esa diferencia.

## Dos extremos sintéticos obligatorios

**Desconocido no equivale a cero.** Una unidad admitida, A conocido cero, V desconocido: `allowed_pairs={00,01}`. Estados finales `(0,0,0)` y `(0,1,0)`. `A_only=[0,0]`, `V_only=[0,1]`, Jaccard definida sólo para 01 y entonces igual a cero; `undefined_possible=true`. La fracción A es siempre indefinida; la fracción V es uno cuando está definida y también puede estar indefinida. La decisión `varies`. Sustituir V desconocido por cero borraría un escenario válido. Si en cambio se desconoce el soporte común, la salida es `not_identified`, sin admitir esta unidad y sin números.

**Detección positiva con M13 y FRP registrada cero.** Una unidad admitida con A conocido cero y V final conocido positivo: `allowed_pairs={01}`; V lleva flag M13, `policy_inclusion=exclude` bajo una política conservadora declarada y `frp_status=reported` con valor registrado cero. Resultado: `A_only=0`, `V_only=1`, Jaccard cero definida, decisión invariante `review_human`. La exclusión de política no borra V=1. No se devuelve energía cero, intervalo de FRP ni inferencia sobre la causa del flag. Si A fuera también positivo, `{11}` daría Jaccard uno sin cambiar estas limitaciones físicas.

## Pruebas y oráculo exhaustivo propuestos

El oráculo independiente enumera todos los escenarios mediante producto cartesiano de los conjuntos de pares y calcula las métricas directamente por conteo de pares, sin usar la transición DP ni sus fórmulas de estado. Para cada caso con `n≤7`, debe comparar conjuntos de estados, extremos racionales, flags de indefinición, acciones y validez de testigos. Son como máximo `4^7=16.384` asignaciones por entrada; no se afirma cubrir las `15^7` entradas posibles de conjuntos locales.

Suite determinista propuesta:

- Para `n=0,1,2,3`, todas las entradas posibles con los 15 subconjuntos no vacíos de pares por unidad. Para `n=4..7`, los 15 casos homogéneos, ciclos de cada par de subconjuntos distintos y 200 entradas por tamaño mediante generador con semilla fijada, documentando que esta última cobertura no es exhaustiva sobre entradas.
- Casos explícitos: universo vacío; sólo 00; sólo 11; sólo 10 frente a sólo 01; cuatro pares libres; `{00,11}`; `{01,10}`; denominadores siempre cero; denominadores unas veces cero; ambos extremos sintéticos anteriores; soporte no identificado.
- Metamorfismos: permutar unidades conserva resultados; intercambiar A/V conserva Jaccard y permuta las direcciones; expandir pares permitidos no estrecha rangos de conteos ni elimina acciones y nunca pierde estados alcanzables. Para razones, la comparación de intervalos sólo se aplica cuando ambos conjuntos definidos son no vacíos; los flags se comparan por inclusión de posibilidades.
- Invariancia de separación: modificar únicamente QA, inclusión de política o FRP no altera estados, cotas o acciones. En particular, positivo final más flag sigue positivo. Cambiar el conjunto de pares exige una justificación de clasificación, independiente del filtro de señal.
- Rechazos: pares vacíos o fuera de dominio, proyecciones contradictorias, IDs duplicados, pesos distintos, unidades no disjuntas declaradas, objetivo diferente, acoplamiento global y unidades suministradas bajo soporte no identificado. Límite de recursos produce error explícito sin intervalo parcial.

## Criterios de aceptación para autorizar una implementación posterior

1. Protocolo del responsable fija estimando, regla positiva, universo y restricciones; ninguna entrada real se deriva automáticamente de los centros cercanos existentes.
2. La implementación futura sólo usa datos sintéticos durante esta etapa; no lee raw ni produce conteos reales de concordancia o nuevos scores de modelo.
3. El oráculo coincide exactamente con la DP en toda la suite indicada y verifica cada testigo extremo; `undefined_possible` y `not_identified` permanecen distinguibles en salida y presentación.
4. QA, selección por política, detección final y FRP permanecen separados. Ningún flag ni FRP cero modifica por sí solo una clasificación registrada.
5. La salida expresa que sus cotas son condicionales a un universo hipotético. No afirma validación física, equivalencia entre sensores, sensibilidad o energía, y conserva G1 falso.
6. Toda ampliación a área ponderada, universos inciertos, restricciones globales o FRP requiere ampliar el contrato y el protocolo antes de calcular.
