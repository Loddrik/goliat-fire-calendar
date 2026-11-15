# Iteración 6 — sensibilidad de grilla y límites comunales

**Conclusión:** la mejora relativa de las políticas calibradas se conserva con las cuatro definiciones de grilla/cartografía, pero las habilitaciones comunales no son totalmente estables. No escoger límites ni una regla de grilla por maximizar el número de comunas que pasan.

El [protocolo 6](2026-11-14-science-protocol-6.md) precede los nuevos resultados. Se usaron las mismas 125.740 detecciones canónicas anteriores a julio de 2020, sin cambiar confianza, horario, Type ni prioridad de fuente. Todas las transformaciones ocurrieron en tablas DuckDB en memoria. No se alteró producción ni las auditorías anteriores.

## Reproducción y definiciones

Se reprodujo la asignación geoBoundaries de cada identificador de celda existente y se reconstruyeron exactamente las celdas-día históricas del Parquet. Las predicciones M1, M1/B, M1/P y M1/B/P del escenario publicado coincidieron con la iteración 5, con tolerancia absoluta 10⁻¹⁰.

La alternativa decimal calcula el piso de `Decimal(str(coordenada))·100`, en lugar del cociente binario por 0,01. Interpreta la representación decimal canónica de los valores del Parquet: no recupera una precisión desconocida del archivo crudo. Ambas reglas se documentan como alternativas numéricas. Ejemplo: longitud −73,43 queda en la celda −7344 con la regla publicada y en −7343 con la decimal.

La DPA 2023 es la geometría oficial normalizada conservada por FireChronos, con su hash verificado; se aplica fija a todos los años. Se mantuvieron fuera los filtros Type=0 y las otras diferencias de FireChronos para aislar la cartografía. Se usaron asignación única, CUT menor en borde compartido y exclusión de solapamientos interiores. En los centros reales consultados no hubo casos de borde compartido o solapamiento interior: las diferencias medidas no proceden de resolver esos casos artificialmente.

## Cuánto cambia la asignación

| Escenario | Detecciones que cambian de celda | Cambian de CUT o de pertenencia al territorio | Entran / salen del territorio | Máscara entrenada con todas las temporadas |
| --- | ---: | ---: | ---: | ---: |
| Publicado | 0 | 0 | 0 / 0 | 223 |
| Decimal + geoBoundaries | 104 | 3 | 0 / 0 | 216 |
| Grilla publicada + DPA | 0 | 286 | 35 / 20 | 223 |
| Decimal + DPA | 104 | 289 | 35 / 21 | 216 |

104 detecciones representan **0,083 %** de la entrada histórica. Aunque el cambio numérico es pequeño, también cambia la máscara aprendida: algunas reglas y buffers son discretos. No corresponde concluir que 104 incendios estuvieran mal localizados; se trata de registros de detección y una definición de celdas agregadas.

## Resultado del modelo dentro de cada escenario

| Escenario | MAE medio M1 | Mejora M1/B | Mejora M1/P | Mejora M1/B/P |
| --- | ---: | ---: | ---: | ---: |
| Publicado | 2,0472 | 7,04 % | 6,61 % | 7,98 % |
| Decimal + geoBoundaries | 2,0477 | 7,17 % | 6,54 % | 8,15 % |
| Grilla publicada + DPA | 2,0519 | 6,50 % | 7,17 % | 7,28 % |
| Decimal + DPA | 2,0520 | 6,45 % | 7,04 % | 7,32 % |

Los porcentajes comparan métodos contra M1 **dentro de cada escenario**, usando el mismo objetivo y máscara por partición. Cambiar grilla/cartografía cambia el objetivo: no interpretar el MAE absoluto de una fila frente a otra como una mejora o pérdida de exactitud física contra una misma verdad. El objetivo externo suma 21.489–21.492 celdas-día S-NPP según escenario; su distribución entre comunas también cambia.

La ventaja de M1/B/P no desaparece, pero la posición relativa de B y P cambia con la cartografía. No congelar una familia usando solamente la ordenación de una tabla del escenario original.

## Habilitación sensible a decisiones de datos

| Política | Publicado | Decimal + geoBoundaries | Grilla publicada + DPA | Decimal + DPA | Intersección de las cuatro |
| --- | ---: | ---: | ---: | ---: | ---: |
| M1 | 14 | 13 | 13 | 12 | 12 |
| M1/B | 15 | 14 | 15 | 13 | 13 |
| M1/P | 15 | 15 | 17 | 16 | 15 |
| M1/B/P | 14 | 13 | 15 | 14 | 13 |

La intersección es un diagnóstico posterior derivado de las compuertas conservadas, **no una nueva regla de publicación** ni una validación externa. La muestra es pequeña y el umbral de 6/8 temporadas hace que cambios cercanos al límite cambien la etiqueta.

Para M1/B/P, las 13 comunas que pasan en los cuatro escenarios son CUT 08111, 08202, 08203, 08207, 08301, 08305, 08308, 16106, 16202, 16203, 16301, 16302 y 16303. Mulchén pasa en los cuatro escenarios con B, P y B/P; no pasa con M1 en ninguno. Esto respalda una revisión de su candidato, sin convertir el diagnóstico en autorización de una serie histórica nueva.

## Comprobaciones y siguiente paso

Se aprobaron tests de piso decimal, finitos, borde compartido, agujeros, exclusión de solapamientos interiores y rechazo de geometrías inválidas. La reconstrucción SQL y las predicciones originales se contrastaron antes de los escenarios alternativos. Artefactos completos en `data/processed/geography_audit/`: asignaciones por celda, predicciones, elecciones internas, métricas, compuertas, resumen y manifiesto con hashes. Las geometrías originales permanecen intactas.

```sh
uv run python -m unittest discover -s tests -p 'test_geography_sensitivity.py' -v
uv run python pipeline/geography_experiment.py
```

La decisión de cartografía debe basarse en procedencia y uso territorial, con un contrato explícito. Para continuar la comparación con la publicación vigente se conserva su grilla/cartografía como referencia, sin escoger una alternativa por su puntuación. La próxima evaluación examinará la continuidad S-NPP/NOAA-20 por comuna: un cociente regional cercano a uno no prueba equivalencia local ni igualdad de oportunidad de observación.
