# De calibrar cantidades a estudiar la observación: dictamen de dos consejos

**Propuesta conjunta ratificada con condiciones por seis agentes:** investigar 1+2, con evidencia 5 transversal, pero empezar por **5a + comprobación de acceso G0**, no por comprometer una implementación completa. Después deben pasar **G1: inventario y diseño del universo**, y recién entonces un piloto 1+2 con auditoría 5b. Los giros 3 y 4 quedan como experimentos posteriores, sujetos a lo aprendido.

Esto respalda una dirección de investigación, no demuestra una mejora del modelo. Sigue siendo una hipótesis que la información sobre observación sea el principal límite actual. Un resultado de desacuerdo persistente o de datos insuficientes debe poder cambiar nuestra decisión.

La evaluación es analítica: no se ejecutó el piloto, no se probó acceso autenticado a productos L2 ni se calcularon nuevas mejoras predictivas. El contexto técnico se leyó del repositorio en `22acc26` y de su [decisión científica acumulada](2026-11-14-research-decision.md).

## 1. Cómo se realizó el consejo

El consejo multifocal tuvo tres miembros: física y observación satelital; inferencia y evaluación estadística; ingeniería, acceso a datos y utilidad. Cada uno propuso criterios antes de puntuar. Los tres ratificaron la misma matriz y emitieron juicios independientes.

Un segundo consejo, con tres agentes nuevos y contexto separado, atacó esa propuesta desde identificación/selección, física de medición y viabilidad/coste de oportunidad. El resultado se devolvió a los tres miembros originales. Ellos negociaron cambios; los tres adversarios revisaron la versión conjunta y la ratificaron condicionalmente. No se interpretó la ratificación de agentes como autorización del usuario para implementar o publicar.

## 2. Criterios acordados antes de evaluar

| Criterio | Peso | Qué debe responder |
| --- | ---: | --- |
| Validez e identificabilidad | 30 % | ¿La comparación responde una pregunta definida sin inventar verdad o causalidad? |
| Información discriminante | 25 % | ¿Puede distinguir explicaciones del error y cambiar la siguiente decisión? |
| Acceso y factibilidad reproducible | 20 % | ¿Hay insumos obtenibles, trazabilidad y una inversión acotada hasta evidencia útil? |
| Transporte y selección | 15 % | ¿Qué población queda fuera y qué generalización sería defendible? |
| Utilidad interpretativa | 10 % | ¿Un analista puede entender qué se observó y qué sigue desconocido? |

Son criterios del consejo, no estándares oficiales NASA. Hay condiciones no compensables por puntuación: desconocido no equivale a cero; se necesitan no-detecciones observadas, no solo positivos; hay que declarar tiempo y soporte; comprobar acceso a QA/geolocalización; y separar concordancia entre productos de verdad sobre fuego.

El adversario señaló solapamiento entre criterios y un coste de oportunidad insuficientemente explícito. La respuesta conjunta lo incorpora dentro de factibilidad y mediante una puerta de inversión, sin cambiar retrospectivamente los pesos para fabricar unanimidad.

## 3. Valoración de los cinco giros

Puntuaciones ponderadas sobre cinco, derivadas de escalas ordinales. Son juicios de planificación, no probabilidades de éxito, intervalos estadísticos ni mejoras medidas. Los rangos son los expresados por el miembro de observación.

| Giro | Observación | Inferencia | Ingeniería | Acuerdo operativo |
| --- | ---: | ---: | ---: | --- |
| 1. Oportunidades de observación | 4,45 | 4,25 | 3,85 | Mayor prioridad científica; medir aproximaciones a elegibilidad, no prometer visibilidad perfecta |
| 2. Comparar observaciones próximas | 4,15–4,35 | 3,70 | 3,65 | Complemento de 1, condicionado al acceso y al diseño |
| 5. Evidencia documentada | 3,35–4,15 | 3,80 | 3,68 | Empezar ahora en alcance posible y continuar dentro del piloto |
| 3. Presencia y cantidad | 3,30 | 3,50 | 3,38 | Siguiente experimento si existe objetivo predictivo y evidencia que lo justifique |
| 4. Información por contexto territorial | 3,10 | 3,00 | 3,33 | Posterior a estabilizar observación/respuesta y reservar territorios |

Los [componentes por criterio y cálculos de cada voto](evidence/observation-councils/votes.json) se conservan para inspección. No hubo acuerdo de orden estricto entre 2 y 5: inferencia puso 5 por encima de 2. Se conserva esa discrepancia. Tampoco se suman puntuaciones de 1 y 2: comparten insumos y no son proyectos independientes.

El acuerdo final separa dos decisiones: **prioridad científica 1+2; siguiente inversión ejecutable 5a + G0**. La auditoría inmediata no reemplaza el estudio de oportunidades, pero permite aprender mientras se verifica si ese estudio es viable.

## 4. Qué cambió el consejo adversario

| Objeción | Cambio incorporado |
| --- | --- |
| El desacuerdo puede bajar porque cambia la población | Universo previsto fijo, flujo de exclusiones y resultados condicionados; no atribución causal |
| QA y humo pueden depender del propio fuego | Declarar esa dependencia; no tratar QA como exposición externa ni dividir automáticamente cantidades por cobertura |
| Usar “no fuego” para certificar oportunidad es circular | Separar calidad/cobertura de entrada y salida del detector; aplicar reglas equivalentes a positivos y negativos |
| Ambos negativos pueden dominar el acuerdo | Mostrar las cuatro combinaciones, marginales, discordancias direccionales, retención e inciertos |
| Una pareja legible no prueba viabilidad del período | Separar acceso G0 de inventario y diseño G1 |
| Tiempo, malla y asociación pueden elegirse para mejorar resultados | Congelar reglas antes de concordancia y conservar incertidumbre temporal |
| El piloto cambia de unidad respecto de M1 | No aplicar el factor comuna-mes a píxel/pasada ni promover el calendario desde ese contraste |
| La ruta sofisticada puede desplazar evidencia útil inmediata | Auditoría 5a ahora; inversión G0 acotada y piloto condicionado |

La pregunta conjunta es:

> **En un universo fijado de observaciones Aqua–S-NPP, ¿cómo varían las discordancias direccionales y las tasas marginales al aplicar reglas documentadas de cobertura, tiempo y QA, y qué observaciones quedan fuera?**

No estima qué porcentaje del desacuerdo fue causado por oportunidades desiguales. Si las observaciones excluidas no tienen etiquetas válidas, su desacuerdo no es observable: no existe un resultado global previo que pueda compararse directamente con el posterior. Fijar el universo no vuelve evaluable todo su contenido.

## 5. Plan conjunto

### A. Auditoría 5a con los datos actuales

Examinar de forma reproducible detecciones retenidas, ausencias registradas, tiempos UTC, localización, confianza y cambios de agregación/plataforma. Incluir concordancias y ambos sentidos del desacuerdo; evitar elegir únicamente ejemplos espectaculares.

Los Parquet ya filtraron baja confianza y no contienen máscaras completas. Esta fase no puede recuperar detecciones descartadas, nubes conocidas o negativos elegibles que no estén en sus insumos. Un cero se llama **ausencia de detección registrada**, con oportunidad desconocida. Esta auditoría puede encontrar errores de alineación o agregación, pero no responde por sí sola a la pregunta de oportunidades comparables. Preparar casos con los registros actuales tampoco equivale a disponer ya de evidencia externa nueva: imágenes o registros independientes y temporalmente alineados tienen que obtenerse y documentarse según su disponibilidad.

### B. G0: demostrar acceso y lectura

Obtener y leer una pareja técnica real Aqua/S-NPP y sus auxiliares, verificando procedencia, dimensiones, máscara y QA completos, geolocalización, tiempos y soporte también donde no hay detecciones. Archivar versiones, asociaciones entre archivos y hashes; medir bytes y tiempo reales.

Productos candidatos, sujetos a verificar compatibilidad concreta:

| Función | Aqua | S-NPP |
| --- | --- | --- |
| Fuego/máscara y QA | [MYD14, Collection 6.1](https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/MYD14/) | [VNP14IMG, Collection 2, 375 m](https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP14IMG/) |
| Geolocalización y geometría | MYD03 compatible con el producto obtenido | [VNP03IMG compatible](https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP03IMG/) |

La página genérica actual [MYD03](https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/MYD03/) anuncia Collection 7. No se elige “latest” automáticamente para acompañar MYD14 C6.1. Los campos de píxeles de fuego `FP_*` no sustituyen la información de todos los píxeles. VNP14IMG de 375 m tampoco es el mismo producto que VNP14 de 750 m; la [especificación del producto](https://ladsweb.modaps.eosdis.nasa.gov/filespec/VIIRS/1/VNP14IMG) debe leerse en su versión correspondiente.

El límite de inversión propuesto para G0 es **una jornada de trabajo**, no una estimación medida ni garantía de éxito. Si no se acredita acceso y decodificación compatibles, entregar obstáculos e inventario y detener el piloto. No sustituir los datos faltantes por confianza de positivos o ceros. Una pareja técnica no necesita contener todas las clases para poder verificar el decodificador, pero tampoco acredita que el universo posterior sea informativo.

No se presupone acceso autenticado. Una clave FIRMS no demuestra acceso a otros archivos. Una AOI pequeña tampoco garantiza descargas pequeñas: hay que medir el volumen real de granules y auxiliares antes de comprometer el trabajo.

### C. G1: inventariar y cerrar el diseño antes de ver concordancias

Alcance propuesto de ingeniería: **50 × 50 km, centro 37° S / 72,5° O; 1–15 de enero de 2019; Aqua y S-NPP**. Se propone por contener un dominio del piloto actual y acotar trabajo, no porque se hayan buscado focos favorables. Tamaño y ventana no constituyen suficiencia estadística.

Ese período ya pertenece al desarrollo 2012–2019. Nuevas variables pueden aportar evidencia nueva sobre observación, pero no lo convierten en un test predictivo independiente. Si se adopta esta opción, fijarla antes de inspeccionar detecciones; no ampliar la muestra después buscando actividad favorable.

Inventariar todo el período previsto: oportunidades geométricas, productos disponibles, pasadas emparejables, cobertura y faltantes. **Inventario completo no significa exigir cobertura perfecta** ni eliminar días incompletos. Los faltantes permanecen visibles.

Antes de calcular concordancia deben quedar registrados:

- Proyección, soporte/malla y tamaño; tratamiento de bordes y solapes; sensibilidades espaciales y estratos angulares.
- Qué significa cobertura/elegibilidad según los campos de la versión exacta; tratamiento de baja confianza y estados indeterminados.
- Asociaciones analíticas deterministas por tiempo/geometría, antes de QA y detecciones. Granules pueden relacionarse muchos-a-muchos para cubrir una pasada; se evita duplicar la misma observación.
- Ponderación primaria por unidad/pasada o área; métricas secundarias y dependencia temporal/episódica.
- Muestra de casos a auditar y reglas que harían informativo, insuficiente o exploratorio el resultado.

Estos parámetros espaciales y decodificaciones **no están todavía validados con archivos**. La ratificación del plan no declara aprobado G1.

### D. Piloto 1+2 con auditoría 5b

**Tiempo:** ventana primaria propuesta ≤10 minutos; sensibilidades 5/15/30 minutos; 60 minutos solo diagnóstico separado. Ingeniería retiró su propuesta inicial de 30 minutos como primaria tras la crítica: conseguir más parejas no justifica mezclar más evolución real del fuego. Diez minutos es una convención conservadora, no un estándar NASA ni un óptimo demostrado.

Usar tiempos de adquisición efectivos cuando existan. Con intervalos: definitivamente dentro si el máximo desfase posible está dentro de la ventana; definitivamente fuera si el mínimo la excede; en otro caso, tiempo incierto. No usar inicios nominales de archivos para inventar simultaneidad. Reutilizar IDs de parejas en sensibilidades; si se reasocia, informar una política distinta y no llamarla necesariamente cohorte anidada. Si faltan pares de diez minutos, declarar insuficiencia sin ampliar la primaria post hoc.

**Espacio:** soporte común de análisis por pasada con geometría y fracciones de cobertura declaradas. Geolocalizar centros no reconstruye footprints exactos ni iguala sensibilidades. No sumar nueve VIIRS como si correspondieran físicamente a un MODIS.

**Estados:** separar detección aceptada, baja confianza/resultado incierto, no-detección elegible y desconocido con motivo. La calidad de entrada y geolocalización se evalúan de forma equivalente en positivos y negativos. QA puede depender del algoritmo y del propio fuego: no representa una medición independiente de oportunidad física perfecta.

**Resultados:** filas=Aqua y columnas=S-NPP. En los R pares con ambas etiquetas binarias válidas, publicar n00/n01/n10/n11, las tasas n01/R y n10/R, marginales y concordancia positiva Jaccard cuando su denominador sea distinto de cero. No llamar esas métricas precisión o sensibilidad sobre fuego real.

Acompañar siempre con área/unidades retenidas, disponibilidad, incertidumbre y exclusiones por motivo; retención de positivos **reportados y conocidos**, con su denominador y confianza. No se sabe cuántos verdaderos positivos hay entre los desconocidos. No ocultar inciertos dentro de cero ni calcular una concordancia fuera de etiquetas válidas.

Informar días, pasadas y episodios efectivos. Los píxeles del mismo episodio no son réplicas independientes. Con poca información independiente, presentar diagnóstico descriptivo o inconcluso. No se fija aquí un número mágico de píxeles que valide el experimento.

La auditoría 5b incorpora las categorías realmente identificables con L2: ambas discordancias, concordantes positivos, no-detecciones elegibles, inciertos y excluidos. Muestreo reproducible y probabilidades/estratos registrados si se busca inferencia poblacional; evidencia alineada en tiempo y escala, con independencia de fuentes declarada. Cuando sea viable, ocultar a anotadores el resultado comparativo. Conservar indeterminado y desacuerdo entre revisores: una cicatriz posterior, imágenes del mismo detector o CONAF no acreditan automáticamente fuego durante esa pasada o su ausencia.

### E. Decisiones después del piloto

| Resultado | Decisión defendible |
| --- | --- |
| No hay acceso compatible o faltan auxiliares interpretables | Detener piloto y conservar obstáculos/auditoría |
| Pocos pares o episodios; alta incertidumbre | Resultado local descriptivo o inconcluso |
| Menos discordancia, pero también pérdida selectiva de área o detecciones reportadas | No generalizar la supuesta mejora; describir la selección |
| Dependencia fuerte de malla, ventana o reglas QA | Reabrir diseño como exploratorio, sin elegir la versión más favorable |
| Patrón consistente dentro del soporte definido | Diseñar la siguiente prueba sobre condiciones y sensibilidad; no promover automáticamente un modelo |

“Pérdida fuerte” o “patrón robusto” no tienen aquí umbrales confirmatorios universales. Deben operacionalizarse antes de usarlos para una decisión confirmatoria. El piloto no tiene como criterio de éxito conseguir que baje el desacuerdo: tiene que producir una comparación interpretable, incluidas sus limitaciones.

## 6. Qué pasa con los giros 3 y 4

El giro 3 sigue siendo plausible. Su objetivo sería probabilidad de **detección en la referencia bajo oportunidades definidas**, junto con cantidad condicionada, no probabilidad física de incendio. Conviene evaluar una distribución de dos partes antes de imponer un encendido/apagado por umbral arbitrario. Un baseline exploratorio con datos actuales es posible, pero no responde la pregunta de observabilidad ni resuelve la validación reutilizada.

El giro 4 exige covariables territoriales históricamente apropiadas, sin incorporar información del resultado futuro, y reservar territorios/bloques completos, evitando que el mismo episodio se filtre entre entrenamiento y evaluación. Una sola AOI no demuestra transferencia regional.

Para volver al calendario mensual hará falta una evaluación específica a esa unidad. M1 fue calibrado por comuna-mes; no se transplanta a píxel/pasada. Además, el objetivo de calibración es S-NPP y la publicación reciente usa NOAA-20: el puente local requiere su propia evidencia.

## 7. Fuentes y alcance de las afirmaciones

Las [notas oficiales FIRMS](https://firms.modaps.eosdis.nasa.gov/alerts/notes.php) documentan omisiones por nubes, humo, dosel, intervalos entre pasadas y sensibilidad. Motivan buscar información de observación; no prueban que ésta explique la mayor parte de nuestro error.

El DOI aportado corresponde a Li et al. (2018), *Comparison of Fire Radiative Power Estimates From VIIRS and MODIS Observations*. El [registro y resumen primario NOAA](https://repository.library.noaa.gov/view/noaa/49896) relaciona FRP, geometría y escala. No valida directamente celdas-día de 375 m ni un factor de conversión local. Se pudo contrastar el resumen, no recuperar el artículo completo. Las guías PDF específicas también presentaron restricciones de recuperación; no se da por comprobada su decodificación de bits sin obtener la versión aplicable.

## 8. Acta de ratificación conjunta

| Miembro | Ratificación y condición decisiva |
| --- | --- |
| Multifocal: observación | Sí, con tiempos inciertos, asociación analítica sin exigir 1:1 de granules, QA separada y soporte aproximado |
| Multifocal: inferencia | Sí, con universo distinto de denominador evaluable, parejas fijas, ponderación explícita y retención solo de positivos reportados |
| Multifocal: ingeniería | Sí; retira 30 min como primaria y 2–4 jornadas como compromiso; distingue 5a y 5b |
| Adversario: identificación | Sí condicionado; G1 previo y ninguna atribución causal ni concordancia inventada entre excluidos |
| Adversario: medición | Sí condicionado; no queda veto adicional al plan, sin acreditar acceso, cobertura o equivalencia |
| Adversario: viabilidad | Sí condicionado; retira veto ejecutivo por separar inversión y valor científico; G0 no prueba suficiencia del piloto |

Se conserva el disenso de ranking 2 frente a 5. El consenso logrado es una **política de inversión y aprendizaje condicionada**, no unanimidad cuantitativa ni evidencia empírica de que el modelo vaya a mejorar.
