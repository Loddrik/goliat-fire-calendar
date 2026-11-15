# Iteración 7 — continuidad VIIRS por territorio y período

**Conclusión:** el factor 1 entre NOAA-20 y S-NPP es una aproximación razonable del total regional de estas temporadas, pero no demuestra equivalencia mensual local ni coincidencia de detecciones individuales. Mantener la plataforma de cada estimación y declarar esa diferencia en la interpretación de la serie.

Auditoría descriptiva según [protocolo 7](2026-11-14-science-protocol-7.md). No se ajustó ningún factor ni candidato Aqua, ni se modificó producción. Se mantuvieron grilla, cartografía y máscara fija publicadas para medir exactamente el contrato actual. El inventario documenta ventanas solicitadas completas para los períodos comparados; no prueba que cada celda/día pudiera observarse. Las ventanas usadas no contienen celdas-día NRT.

## Totales casi iguales, diferencias locales mayores

| Comparación | Temporadas completas | Celdas-día referencia | Comparador | Razón de sumas | WAPE mensual por comuna |
| --- | --- | ---: | ---: | ---: | ---: |
| NOAA-20 / S-NPP | 2018–2025 | 23.283 | 23.260 | 0,9990 | 28,84 % |
| NOAA-21 / NOAA-20 | 2023–2025 | 7.704 | 7.599 | 0,9864 | 30,36 % |

Temporadas julio–junio: 2025 incluye enero–junio de 2026. WAPE = suma de diferencias mensuales absolutas emparejadas / suma de referencia, sobre todas las comunas; no es error frente a verdad de terreno ni mide cobertura. Un cociente regional cercano a uno puede ocultar compensaciones entre lugares y meses.

Bootstrap por temporadas completas, 5.000 réplicas y semilla 20261114:

- NOAA-20/S-NPP: intervalo percentil **[0,9679;1,0342]**, ocho bloques.
- NOAA-21/NOAA-20: **[0,9281;1,0202]**, solo tres bloques. Especialmente débil para afirmar equivalencia.

Las razones anuales NOAA-20/S-NPP varían entre **0,9349 y 1,0625**, reproduciendo aproximadamente el rango anual declarado. Los conteos emparejados corresponden a ventanas SP solicitadas; no se infiere observabilidad a partir de que haya o no alguna detección.

## Mes calendario y comuna

En el mismo conjunto de temporadas completas, la razón NOAA-20/S-NPP agregada por mes calendario va de **0,8309 en enero** a **1,1701 en julio**. El rango mensual 0,96–1,20 mencionado anteriormente en `method.md` **no se reproduce bajo esta ventana/máscara** y se reemplaza por este diagnóstico explícito. La comparación NOAA-21/NOAA-20 va de **0,8610 en febrero** a **1,3896 en enero**, con tres temporadas; no convertir esos extremos en factores estacionales sin validación.

De 47 comunas con al menos 100 celdas-día S-NPP acumuladas, tres quedan fuera del intervalo de cribado [0,8;1,25]:

| CUT | Comuna | S-NPP | NOAA-20 | Razón |
| --- | --- | ---: | ---: | ---: |
| 08101 | Concepción | 181 | 122 | 0,6740 |
| 08304 | Laja | 122 | 90 | 0,7377 |
| 16103 | Chillán Viejo | 152 | 117 | 0,7697 |

El mínimo 100 y el intervalo de cribado son diagnósticos del proyecto, no estándares NASA ni nuevas compuertas. Estas razones no prueban causalidad instrumental o un sesgo estable; faltan oportunidad de observación e incertidumbre local. Todas las comunas, incluidas las de señal menor, quedan en el CSV sin descartar resultados desfavorables.

En NOAA-21/NOAA-20 ninguna de las 26 comunas que supera ese mínimo queda fuera del intervalo. Tres temporadas y una selección por señal acumulada no permiten afirmar que el problema de continuidad esté resuelto.

## Coincidencia de celdas-día positivas

| Pareja | Intersección | Unión | Jaccard |
| --- | ---: | ---: | ---: |
| S-NPP y NOAA-20 | 9.848 | 36.695 | 26,84 % |
| NOAA-20 y NOAA-21 | 3.109 | 12.194 | 25,50 % |

El Jaccard usa la misma comuna, celda y día, y conjuntos de detecciones positivas. **No** es precisión, recall ni identificación de incendios independientes. Las pasadas, oportunidades de observación y geolocalización pueden diferir; no se adjudica a una plataforma la condición de verdad de terreno. La igualdad de totales regionales no significa que ambas observaran exactamente las mismas celdas-día.

## Consecuencias para el modelo

1. Conservar explícita la plataforma por temporada y el factor 1 como aproximación regional declarada; no presentarlo como equivalencia local demostrada.
2. La reconstrucción Aqua se calibra contra S-NPP. Una serie reciente NOAA-20 tiene una discrepancia adicional de continuidad que no está representada automáticamente por la banda de calibración Aqua/S-NPP.
3. No aprender factores locales a partir de estas mismas cifras y declarar después que el puente quedó validado. Un puente alternativo necesitaría entrenamiento/validación separados, máscaras y calendario coherentes, además de controles contra identidad y climatología.
4. La siguiente evaluación temporal mantendrá las políticas de Aqua congeladas y estos resultados como diagnóstico separado. No se usaron aquí para ampliar candidatos ni modificar regularizaciones.

## Identidad territorial y verificación

Al cotejar nombres contra la DPA se corrigió un error de etiqueta en los informes 2–3: **16106 es Pinto; Chillán Viejo es 16103**. Los cálculos y compuertas estaban indexados por los CUT correctos, por lo que sus resultados numéricos no cambian. Los 54 nombres del índice actual coinciden con la DPA tras normalizar tildes y espacios.

Artefactos en `data/processed/platform_bridge_audit/`: 7.128 pares mensuales, razones por temporada/mes/comuna, solape, resumen y hashes. Los 5.184 pares de NOAA-20/S-NPP y 1.944 de NOAA-21/NOAA-20 reproducen sus respectivos conjuntos de celdas-día. Se probaron calendarios julio–junio y años bisiestos, ventanas SP, exclusión por faltantes documentados, denominadores cero, bootstrap emparejado y conjuntos vacíos.

```sh
uv run python -m unittest discover -s tests -p 'test_platform_bridge.py' -v
uv run python pipeline/platform_bridge_audit.py
```

Los archivos fuente/producción y las iteraciones anteriores permanecen intactos. Los originales de CONAF descargados para una próxima comprobación externa no se utilizaron en este análisis.
