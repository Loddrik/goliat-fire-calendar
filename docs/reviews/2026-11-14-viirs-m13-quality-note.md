# Nota documental — M13 no nominal y detecciones VIIRS de alta confianza

Consulta de fuentes primarias: 14 de noviembre de 2026. Producto del piloto: **VNP14IMG, colección 002, VIIRS S-NPP 375 m**. Esta nota no abre nuevos archivos nativos, cambia reglas, recalcula conteos ni modifica G1.

## Conclusión

**El bit 6 no permite declarar falsa una detección.** Resume calidad de entrada M13 no nominal; no identifica por sí solo el mecanismo que la produjo. La documentación contempla incendios detectados cuyo M13 impide recuperar FRP. Exigir que todos los bits de entrada sean nominales es una política conservadora del piloto, no una condición universal de validez de detección demostrada por NASA.

Un filtro duro podría seleccionar contra parte de los incendios intensos. Es un mecanismo plausible para investigar, **no una atribución causal ni una demostración de datos faltantes MNAR** en este caso. No corresponde retirar el filtro ni declarar válidos los excluidos solo porque pertenecen a clases positivas.

## Qué dice la documentación de la versión correcta

La referencia principal es la **guía de producto activo de 375 m, Collection 2, versión documental 1.0, mayo de 2024**, no la guía separada del producto de 750 m. Su tabla 2 define el bit 6 como calidad M13 nominal/no nominal. El bit 16 describe una condición de saturación basada en I4/I5; el bit 22 identifica bowtie residual. Son campos diferentes. [Guía NASA C2 v1.0, §3.1.2 y tabla 2](https://ladsweb.modaps.eosdis.nasa.gov/archive/Document%20Archive/Science%20Data%20Product%20Documentation/VIIRS_C2_AF-375m_User_Guide_1.0.pdf#page=6).

La misma guía asocia la clase 9 de alta confianza con saturación o plegamiento del número digital en la detección. En §3.1.3 indica que M13 también puede saturarse, raramente, sobre incendios grandes e intensos: puede conservarse una detección de 375 m mientras su FRP se devuelve como cero. Confianza alta, calidad nominal de todas las entradas y posibilidad de estimar FRP son, por tanto, dimensiones distintas. [Guía NASA C2 v1.0, §§3.1.2–3.1.3](https://ladsweb.modaps.eosdis.nasa.gov/archive/Document%20Archive/Science%20Data%20Product%20Documentation/VIIRS_C2_AF-375m_User_Guide_1.0.pdf#page=8).

El **ATBD de 375 m, versión 1.0 de diciembre de 2016**, aporta el mecanismo: las bandas I son las entradas principales de detección; M13 participa en FRP y en discriminación de ciertas falsas alarmas. Su §2.3.10 explica que la saturación M13 puede activar QA en la entrada e incluso acompañarse de radiancia no utilizable, sin impedir necesariamente detectar con la información restante. Es documentación algorítmica anterior a C2, consistente con el comportamiento descrito expresamente en la guía C2; no sustituye la implementación exacta de colección 002. [NASA VIIRS, ATBD 375 m, §§2.2 y 2.3.10](https://viirsland.gsfc.nasa.gov/PDF/VIIRS_activefire_375m_ATBD.pdf#page=13).

## Lo que no permite inferir el bit 6

El nivel de entrada distingue más estados que el resumen binario del producto de fuego. La guía NASA Level-1 de **julio de 2017**, tabla 8 y apéndice A, enumera saturación, fuera de rango, temperatura no nominal, calibración sustituida o fallida, datos faltantes y estados de ganancia. `Low_Gain` y `Mixed_Gain` describen estados de agregación en bandas de doble ganancia; no son sinónimos automáticos de radiancia inválida. Sus números de bit pertenecen a **Level-1**, no al `algorithm QA` de Level-2. [NASA VIIRS Level-1 Data Product User’s Guide](https://oceandata.sci.gsfc.nasa.gov/files/resources/docs/technical/VIIRS_Level-1_DataProductUsersGuide.pdf).

No se encontró una regla primaria inequívoca que traduzca **cada combinación de QA M13 Level-1 de C2 al bit 6 del archivo concreto VNP14IMG 002**. En consecuencia, no podemos decidir si esas activaciones proceden de saturación, baja ganancia, calibración, dato ausente u otra condición. La documentación Level-1 histórica orienta las distinciones que se deben comprobar; no autoriza a trasladarlas automáticamente al procesamiento C2.

Tampoco `FRP=0` resolvería por sí solo la causa: la guía contempla otras dificultades de recuperación, como fondo insuficiente. No debe convertirse ese cero en una medición física de potencia nula ni confundirse con ausencia de detección.

## Evidencia local y límite de un solo caso

El [caso adicional predefinido de 2023](2026-11-14-observation-case2023.md) registra doce centros VIIRS excluidos por el screen conservador debido al bit 6 M13. Las clases positivas originales 7/8/9 contienen 3/11/2 centros; después del screen contienen 2/6/0. Por diferencia, se excluyen ocho centros de clases positivas, incluidos los dos de clase 9. **Doce exclusiones totales no son doce detecciones de fuego.**

Esto demuestra una selección efectiva por la política, no la falsedad de esas detecciones ni la causa del QA M13. Son centros nativos de una adquisición y AOI, con dependencia espacial y entradas M13 compartidas; no ocho ensayos independientes. La alta confianza tampoco proporciona una medida independiente de intensidad real con la que probar MNAR. El caso de 2019 sigue formando parte de la evidencia, aunque carezca de clases positivas dentro de su AOI.

## Sensibilidades que conviene fijar antes de otra evaluación

Mantener los resultados existentes. Un siguiente protocolo puede comparar **dos políticas declaradas**, sin escoger después la que produzca más detecciones:

1. **Screen conservador actual:** conservar exactamente la prueba `(algorithm_QA & 127) == 0` y las restantes reglas. Su denominación debe explicitar que es una decisión del piloto.
2. **Sensibilidad que cambia únicamente M13:** mantener los otros seis bits de entrada, controles geográficos y reglas restantes; no excluir automáticamente por bit 6. Conservarlo como estrato explícito `M13_non_nominal`, sin convertirlo en aprobación científica ni imputar una causa.

Reportar ambas sobre todos los casos fijados, con clases 3/5/7/8/9 y causas de exclusión separadas, sin modificar el conjunto de adquisiciones por sus resultados. La intersección y diferencia de políticas deben reconciliarse exactamente. Las clases bajas permanecen separadas de nominales y altas; ninguna confianza se convierte en verdad física. Este ejercicio mide sensibilidad al screen, no mejora de precisión.

Separar además los **usos del dato**: conservar una clasificación de detección para inspección no implica aceptar su FRP para emisiones o intensidad. Un futuro examen de radiancias/QA Level-1 y trazabilidad del procesamiento podría explicar el bit; requeriría un protocolo y datos adicionales, no una inferencia retrospectiva a partir de la máscara.

No se estima todavía una corrección de observabilidad, un factor entre sensores ni una fracción de área comparable. G1, elegibilidad científica, soporte común y exposición física verificada permanecen pendientes. El inventario sirve para revelar cómo una política de calidad puede cambiar qué actividad llega a un modelo, sin demostrar aún cuál política representa mejor el fenómeno físico.
