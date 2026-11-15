# Revisión científica 8 — la mejora no se transporta igual hacia el pasado

**Conclusión:** conservar M1 publicado. La ventaja media de los candidatos en LOSO no se mantiene al entrenar en temporadas tardías y reconstruir las tempranas. Es una limitación directamente relevante para extender el calendario hacia años anteriores a VIIRS; no se debe promover M1/B/P únicamente por su mejora retrospectiva de 7,98 %.

Se ejecutó el [protocolo 8](2026-11-14-science-protocol-8.md), congelado antes de puntuar estas particiones. Selección por comuna y todas las estadísticas se aprenden solo en el origen, mediante cuatro folds LOSO con tres temporadas de ajuste cada uno. El ajuste final usa cuatro temporadas y evalúa otras cuatro sin actualizar parámetros. Grilla y cartografía publicadas; máscara recalculada por origen y dentro de cada fold. Las dos direcciones comparten familias y reglas, pero tienen períodos y máscaras distintos: sus MAE absolutos no son comparables como si fueran el mismo objetivo.

## Resultado por dirección

MAE mensual promedio sobre las 54 comunas, incluidos meses con cero detecciones. Temporadas julio–junio, nombradas por su año inicial. Cambios porcentuales respecto a M1 **dentro de cada dirección**; una reducción negativa indica empeoramiento.

| Política | Origen 2012–2015 → destino 2016–2019: MAE | Reducción frente a M1 | Origen 2016–2019 → destino 2012–2015: MAE | Reducción frente a M1 |
| --- | ---: | ---: | ---: | ---: |
| M0 Aqua sin escalar | 2,62809 | −10,59 % | 2,40625 | −30,39 % |
| M1 factor regional | 2,37638 | referencia | 1,84547 | referencia |
| M1/B | 2,23913 | 5,78 % | 1,86119 | −0,85 % |
| M1/H | 2,19136 | 7,79 % | 1,88575 | −2,18 % |
| M1/P | 2,21605 | 6,75 % | 1,86551 | −1,09 % |
| M1/B/P | 2,20286 | 7,30 % | 1,89018 | −2,42 % |
| M2 climatología | 3,42901 | −44,30 % | 3,05324 | −65,44 % |

Todos los candidatos mejoran frente a M1 en las cuatro temporadas de destino hacia adelante. H tiene el menor MAE en esa partición. Hacia atrás, todos presentan mayor MAE agregado que M1. No seleccionar la dirección favorable como resultado principal ni reinterpretar este estrés como un holdout independiente: las ocho temporadas ya se consultaron en desarrollo.

Contrastes de error absoluto emparejados, bootstrap por temporada, 5.000 réplicas, semilla 20261114:

| Dirección | Contraste | Δ MAE | Intervalo percentil 95 % |
| --- | --- | ---: | --- |
| Adelante | M1/B − M1 | −0,13725 | [−0,18929;−0,09869] |
| Adelante | M1/H − M1 | −0,18502 | [−0,21076;−0,14654] |
| Adelante | M1/B/P − M1/B | −0,03627 | [−0,05174;−0,00749] |
| Atrás | M1/B − M1 | +0,01572 | [−0,02406;+0,06776] |
| Atrás | M1/H − M1 | +0,04028 | [−0,00509;+0,08566] |
| Atrás | M1/B/P − M1 | +0,04471 | [+0,00467;+0,08466] |
| Atrás | M1/B/P − M1/B | +0,02899 | [+0,00718;+0,06210] |

Solo cuatro bloques por dirección: estos intervalos son exploratorios, frágiles y sujetos al desarrollo adaptativo previo. El contraste M1/B/P − M1/B es desfavorable en las cuatro temporadas de reconstrucción temprana. No establece causalidad, ni demuestra el comportamiento de 2002–2011.

## Subgrupos y contrato temporal

En la dirección hacia atrás:

- Los 32 meses con VIIRS ≥50 muestran MAE 18,2088 con M1, 17,7787 con M1/B, 19,5540 con H y 19,0178 con M1/B/P. La ganancia en extremos no se conserva para todas las familias.
- En 1.236 meses donde ambos sensores registran cero, M1/B agrega 92,47 celdas-día estimadas; H 133,89; M1/B/P 51,44. P y M1 quedan en cero por construcción.
- En 589 meses Aqua=0/VIIRS>0, M1/B reduce MAE de 2,2224 a 2,0545; H a 1,9523. Ese beneficio no compensa todas las pérdidas del bloque.

Las máscaras de origen contienen 73 celdas para el ajuste temprano y 106 para el tardío, frente a 223 en el entrenamiento completo de ocho temporadas. Esto no es un error de reproducción: las reglas fijas de persistencia tienen menos observaciones y temporadas disponibles. El experimento mezcla menor tamaño de entrenamiento, cambio temporal y distinta máscara aprendida; **no atribuir la degradación únicamente a deriva del sensor o sobreajuste**. Un diagnóstico posterior puede separar esos factores con un nuevo protocolo, sin modificar las familias según el destino.

## Decisión y siguiente evidencia

1. Mantener la publicación M1 y sus compuertas existentes. Esta etapa no habilita comunas nuevas ni actualiza bandas.
2. M1/B sigue como candidato de desarrollo más simple que la selección ampliada; tampoco se demuestra aquí una mejora hacia atrás sobre M1.
3. Antes de una sustitución, exigir evidencia de transporte hacia temporadas previas, estabilidad territorial y una banda evaluada para el contrato elegido. Los resultados de protocolos 6–8 impiden afirmar que una sola familia domina todos esos criterios.
4. El contraste externo CONAF se planteará por rangos de temporadas y con unidades distintas declaradas. No ajustar factores ni elegir hiperparámetros para maximizar correlación con registros de incendios.

## Verificación y reproducción

`data/processed/temporal_transport_audit/` contiene 5.184 pares mensuales sin duplicados, selección por origen, coeficientes, máscaras, puntuaciones por comuna/temporada, resumen y manifiesto de hashes. Los nueve candidatos Huber del ajuste final convergen en ambas direcciones: máximo KKT 9,99×10⁻⁷ hacia adelante y 9,65×10⁻⁷ hacia atrás. Los ajustes internos usan el mismo control de convergencia obligatorio.

Tres tests nuevos comprueban disyunción temporal y demuestran que alterar arbitrariamente todos los objetivos del destino no cambia parámetros, selección ni estimaciones. También se verifica que cada ajuste y máscara recibe solo las temporadas de origen permitidas. Producción y auditorías anteriores permanecen intactas.

```sh
uv run python -m unittest discover -s tests -p 'test_temporal_transport.py' -v
uv run python pipeline/temporal_transport_audit.py
```

No se utilizaron CONAF, datos 2020+ ni puentes NOAA para elegir candidatos en esta etapa. Los números son celdas-día comparadas con detecciones VIIRS, no incendios individuales ni hectáreas.
