# Diseño30A — testigo racional de intersección nominal

**Propuesta previa a código/resultados; requiere protocolo30 congelado por raíz. No se implementó ni ejecutó este diseño.** Viable como diagnóstico acotado≤15min, incluidos revisión y serialización, con presupuesto explícito de operaciones. No es viable como oráculo completo de todas las áreas ni como prueba de ausencia de intersección.

## Motivo y afirmación posible

29 preservó entradas mediante traslación exacta y restauró ciertos controles, pero un caso que pasaba los gates antiguos puede cambiar enormemente su área de intersección. Que identidades y predicados sean mutuamente consistentes no prueba que el overlay represente la intersección correcta.

30A buscará **un cuadrado explícito de área positiva contenido en la intersección de los conjuntos poligonales de entrada**, mediante aritmética racional exacta independiente de GEOS. Es una cota inferior geométrica, no área verdadera completa. Contrastar después esta cota con áreas original/centrada ya registradas29 permite refutar un área informada demasiado pequeña; no permite validar un área mayor, certificar otros gates, localizar fuego o cuantificar sensibilidad instrumental. No encontrar testigo es inconcluso, nunca “sin intersección”. Conservar los cinco pares, incluido el que pasaba antes.

## Dominio, entradas y parser independiente

Sólo los cinco paresWKB originales congelados27/29, sin recalcular overlays ni leer FIRE/QA. Congelar SHA256 de archivos comprimidos y WKB descomprimidos, tabla de correspondencia de casos y resultados29 originales/centrados usados únicamente después de buscar testigos. No usar el valor de área o su cambio para elegir candidato, tamaño, orden o presupuesto.

Parser propio con `struct`, `gzip` y `Fraction`; prohibido importar GEOS/Shapely para decidir interior, frontera, distancias, candidatos o validez del testigo. WKB sólo como representación de entrada. Admitir exclusivamente Polygon y MultiPolygon2D finitos, con byte-order leído por objeto, consumiendo exactamente todos los bytes. Rechazar dimensionesZ/M, SRID/layout inesperado, tipos no definidos, longitud inválida, coordenadas no finitas, anillos abiertos, anillos con menos de4coordenadas almacenadas, contadores que excedan recursos o trailingbytes. No reparar ni reordenar anillos. El punto de cierre repetido se conserva para estructuras/hashes pero no se duplica como vértice candidato.

Cada float64 de entrada se convierte en su racional binario exacto `Fraction.from_float`; no decimal redondeado ni tolerancia espacial. Segmentos de longitud0 se conservan con distancia al punto, sin dividir por0. Aritmética de enteros sin overflow silencioso.

El conjunto definido es unión de componentesPolygon; cada Polygon es región del exterior menos la unión de interiores de sus holes. La pertenencia de anillo se define por paridad exacta, sin depender de orientación. Especificar esta semántica es necesario: el testigo no certifica por sí mismo la validez topológica global de unWKB. Su inclusión local se acredita por pertenencia estricta y separación positiva de **todas** las fronteras almacenadas; no requiere confiar en un predicadoGEOS. Si la estructura no permite esta semántica, bloquear ese par sin interpretarlo como área0.

## Candidatos determinísticos antes de mirar áreas

Generar para ambos operandos, en orden WKB almacenado (primerop, luegoq), para cada componentePolygon hasta un máximo global prefijado de candidatos por par:

1. Promedio racional de los vértices exteriores sin el cierre repetido.
2. Baricentros racionales `(v_i+v_(i+1)+v_(i+2))/3` de los primeros16tríos consecutivos del exterior; índices cíclicos sobre el anillo sin cierre.

Un baricentro de tres vértices no se presume interior: pasa exactamente el mismo test. No usar holes como nuevas semillas ni ampliar a más vértices porque fallen los anteriores. Una media exterior puede caer fuera de un polígono cóncavo o dentro de un hole: se conserva el fallo.

**Límite recomendado:**128candidatos por par, orden anterior; si la enumeración prefijada excede ese límite, registrar cuáles no fueron examinados y marcar búsqueda limitada, no seleccionar por mayor área ni por el resultadoGEOS. Todos los componentes siguen entrando en pertenencia y distancias, aunque no generen semillas dentro del límite. No priorizar componentes por tamaño, positivo, cercanía a un overlay discrepante o éxito anterior.

Examinar candidatos en orden y aceptar el **primer** testigo certificado por par. No maximizar el cuadrado ni elegir el que mejor refute/beneficie un motor. Si ninguno certifica, estado `no_witness_in_fixed_search`, con causas y denominador de candidatos examinados.

## Pertenencia exacta por raycasting

Para cada anillo y punto racionalc:

- Primero comprobar frontera: producto cruzado exactamente0 y proyección dentro del segmento cerrado. Un centro en cualquier frontera se rechaza como testigo estricto.
- Raycasting horizontal hacia+x con convención semiabierta: el segmento cruza si `(y1>cy)!=(y2>cy)`; calcular su x de intersección racional y alternar paridad sólo si `x_intersección>cx`. Segmentos horizontales no alternan. Esta regla evita doble conteo de vértices.
- Polygon contiene estrictamente si está en el exterior y en ningún hole. MultiPolygon contiene si al menos un componente lo contiene. Conservar pertenencia por componente y holes relevantes en el certificado.

Rechazar un candidato en cualquier frontera de cualquiera de los dos operandos es conservador, incluso si la frontera pertenece a otro componente solapado cuyo interior ya lo contiene. No produce testigos falsos; puede dejar búsquedas inconclusas. La paridad exacta y el sentido de los símbolos deben probarse con casos sobre vértices/horizontales y holes antes de datos reales.

## Distancia exacta y cuadrado certificado

Sólo si c está estrictamente dentro de ambos conjuntos, calcular distancia al cuadrado a **todos** los segmentos de todas las fronteras de ambos operandos (exteriores y holes, incluidos componentes no propietarios de c). Para segmentoa→b:

- `d=b−a`, `v=c−a`, `L=d·d`.
- SiL=0: distancia²=`v·v`.
- Si `v·d≤0`: distancia² a a; si `v·d≥L`: distancia² a b.
- En otro caso: distancia²=`v·v−(v·d)²/L`, racional exacta equivalente al cuadrado del producto cruzado dividido porL.

Guardar la mínima exacta `δ²>0` y el segmento que la alcanza. No convertir a float para elegir tamaño. La frontera más cercana de los dos operandos basta para cota conservadora; usar todas evita omitir un hole o componente.

Elegir `h=2^(−k)` metros con el **menor** enterok≥0 tal que `2h²<δ²`; por tanto h≤1m. El cuadrado cerrado `Q=[cx−h,cx+h]×[cy−h,cy+h]` queda dentro de la bola abierta de radioδ alrededor de c, pues su esquina está a distancia²2h². Al no atravesar ninguna frontera, todoQ conserva la pertenencia del centro en ambos conjuntos. Cota inferior exacta `L=4h²`m².

**Defensas:** límite k≤256prefijado; si no se alcanza desigualdad estricta, registrar `dyadic_depth_limit`, no cambiar δ/tolerancia. Guardarc,h,δ² yL como pares numerador/denominador enteros, desigualdad exacta, IDs de anillos/segmentos y cuatro esquinas racionales. Centro no tiene por qué serfloat representable: no devolver el cuadrado aGEOS ni redondearlo para la prueba. Probar explícitamente el caso de igualdad `2h²=δ²`: debe reducir h.

Esta prueba usa continuidad local de la pertenencia fuera de fronteras; no afirma PSF, área quemada, origen físico de la detección ni representatividad de ese cuadrado para un fuego subpíxel.

## Comparar con resultados existentes sin un overlay nuevo

Una vez terminada la búsqueda con reglas fijadas, leer sólo las áreas de intersección ya almacenadas29 de ambos órdenes, original y centrada. Guardar cada float informado como racional exacto y compararlo conL.

- `area_reportada<L`: incompatibilidad con la cota geométrica exacta, indicando el margen racional y su aproximación decimal para lectura. No esconder la contradicción tras tolerancia1m²: L≤4m² puede ser pequeño. Esta es una prueba nueva exacta, no un cambio retroactivo del gate29.
- `area_reportada≥L`: **no refutada por este testigo**, nunca área validada. L no es estimación puntual ni error máximo.
- Ausencia de testigo o área no finita/faltante: estado inconcluso/no comparable, no0.

Reportar todos los cinco pares y cuatro columnas de áreas (`original_pq`, `original_qp`, `centrada_pq`, `centrada_qp`), sin elegir orden favorable. No usar las cotas para corregir overlays, recalibrar el modelo, declarar reparación completa o presentar una clasificación de motores.27/29 conservan sus resultados y alcance; si un testigo refuta un área que antes pasaba gates, se documenta la insuficiencia del conjunto anterior de gates.

## Recursos, primer artefacto y stop

Cap absoluto recomendado≤15min desde inicio implementador, incluida revisión; congelar hora exacta en protocolo y no reiniciar tras bugs. Hasta5pares,128candidatos/par,2Mtuplas de coordenadas con multiplicidad como límite de lectura,50MiBsalidas. Añadir presupuesto máximo **2millones de evaluaciones exactas candidato×segmento**, contando pertenencia y distancia por separado; si se agota, cerrar parcialmente con casos restantes `resource_limit`, sin aproximaciones ni nuevas semillas. Este límite contiene el coste deFraction con denominadores grandes; su cumplimiento no garantiza terminar todos los pares. No ampliar porque el caso de interés no encuentre testigo.

Primer artefacto: freeze de protocolo/código/WKB, parser+pruebas sintéticas y certificado de búsqueda con estados de los cinco pares; resultados comparados sólo después. Si la implementación no puede cumplir prueba exacta y revisión en cap, entregar diseño/limitación sin datos. Es preferible inconcluso honesto a un “oráculo” que reutilice GEOS para la inclusión.

Pruebas mínimas: cuadrado contenido; rectángulos disjuntos; concavidad con promedio exterior; hole que contiene candidato; candidato en borde/vértice/horizontal; segmento degenerado; MultiPolygon y componentes solapados; raycasting con orientación invertida; igualdad del límiteh; candidato racional nofloat; parser endian/truncado/trailing/Z/M/no finitos/anillo abierto; presupuesto agotado; no_witness≠no_intersection; área existente inferior aL correctamente refutada y área superior sólo no refutada. Las expectativas proceden de geometrías analíticas, noGEOS.

## Relación con30B y siguiente decisión

30B puede revalidar geometríaGEO global en paralelo bajo protocolo independiente, sin clases. Ningún testigo30A sustituye cierres/disjunción/propiedad/global30B. Si30A refuta un resultado antes aceptado, sus gates deben ampliarse antes de habilitar estados25/26, incluso aunque30B cierre áreas. Si no refuta, persiste la insuficiencia de un testigo local para validar el global.

La prioridad es obtener evidencia discriminante sobre un artefacto numérico, no conseguir un pase. Todos los desenlaces pueden ser útiles: testigo refutador, testigo no refutador o búsqueda inconclusa. La pregunta física de oportunidad comparable y el límite causal original siguen abiertos; G1 permanece false.
