# Decodificador de QA observacional: entrega técnica separada de G1

Se implementó `pipeline/observation_qa.py` como módulo puro de biblioteca estándar. No lee archivos, usa credenciales, descarga productos, convierte TAI93 ni calcula comparaciones de fuego. Las pruebas son sintéticas. La lectura de granules reales y los resultados previos permanecen intactos.

## Comportamiento

- Colecciones canónicas explícitas del nombre del archivo: MYD14/MYD03 `061`; VNP14IMG/VNP03IMG `002`. Otros productos, versiones y alias se rechazan: la traducción de versiones CMR corresponde al futuro adaptador de entrada.
- La máscara y el QA se decodifican por separado. En MODIS, bits 0–1 representan agua/costa/tierra/sin uso, nunca la confianza MODLAND de otras colecciones. Las pruebas de detección y rechazo cuyo detalle no está confirmado conservan sus números de bit, sin inventar condiciones físicas.
- En VIIRS, clase 1 de máscara representa bowtie eliminado, mientras bit 1 de QA representa calidad I2. Bits 0–6 son calidad de entradas; las pruebas restantes, incluida saturación, no se consideran fallos de calidad simplemente por ser distintas de cero.
- Rellenos explícitos, valores de clase desconocidos, bits reservados y ausencia de QA conservan estados separados. Un relleno no se interpreta como detección ni como observación sin detección. Las detecciones de baja confianza permanecen detecciones.
- Los indicadores geográficos documentados se decodifican con su producto. La política conservadora exige cero para **esos indicadores geográficos**, incluida ausencia de bits no documentados; no existe una regla universal `algorithm_QA == 0`.
- `temporal_relation` acepta únicamente intervalos de exposición ya justificados en una misma escala. Usa extremos conservadores, permite incertidumbre y no estima el momento de adquisición a partir del nombre del granule.
- `inspect_observation` entrega exclusiones, pendientes y cautelas con `policy_declared`. Conserva agua/costa/tierra, fallos de calidad, tiempo o soporte desconocidos, y cuarentena por flag global `Suspect`.

Las reglas conservadoras son decisiones declaradas del piloto, no recomendaciones universales de NASA. Un estado `policy_candidate_observed_no_detection` significa únicamente que los campos proporcionados cumplen esas reglas; no certifica cobertura, ausencia física de fuego, geolocalización válida completa o comparabilidad de sensores. Incluso un candidato devuelve `gate1_passed=False` y `scientific_eligibility_certified=False`.

Para VIIRS con detección, la superficie queda pendiente porque debe leerse `land_water_mask` independiente de VNP03IMG. En MODIS, un nivel de reflejo solar distinto de cero mantiene la elegibilidad pendiente hasta fijar una política documentada. Los campos adyacentes y pruebas SAA/persistencia generan cautelas y no se reetiquetan como ceros.

## Fuentes y límites

Las tablas se fijaron a partir de las guías primarias y atributos documentados en [el diseño G1](2026-11-14-observation-g1-design.md), con [metadatos de fuentes](evidence/observation-g1-design/sources.json). Para MYD03 se mantiene la advertencia sobre la antigüedad interna de la especificación servida en la ruta 61. El significado de los cuatro bits geográficos VIIRS está además corroborado por atributos del archivo C2 en la inspección autenticada previa. No se reinterpretó el PDF L1B2021 que llegó ilegible.

El módulo no verifica coordenadas, calidad de escaneo, footprints ni época temporal. Sus argumentos de compatibilidad deben venir de evidencia independiente; pasar `True` no constituye esa evidencia. G1 científico sigue bloqueado por soporte común defendible, exposición temporal acotada y elegibilidad QA/global validada.

## Validación

Comando reproducible:

```sh
.venv/bin/python -m unittest discover -s tests -p test_observation_qa.py -v
```

Resultado: **16 pruebas sintéticas aprobadas**. Cubren el contraste con MODLAND antiguo, offsets de campos, máscara frente a QA VIIRS, calidad de entradas frente a pruebas de detección, clases desconocidas/rellenos, preservación de baja confianza, superficies distintas, fallos geográficos, bits reservados, tiempo y soporte desconocidos, `Suspect`, extremos temporales e inputs inválidos. Este resultado valida el contrato del decodificador; no valida observaciones reales ni armonización.

Sin cambios a producción, modelos, indicadores publicados, datos base o locks de dependencias. Sin commit ni push por este agente.
