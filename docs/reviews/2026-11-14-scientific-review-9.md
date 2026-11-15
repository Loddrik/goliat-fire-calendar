# Revisión científica 9 — el calendario detectado no ordena las temporadas como el número de incendios CONAF

**Conclusión:** no se observa una asociación regional clara entre el orden de las temporadas por celdas-día S-NPP y por número de incendios registrados por CONAF. No traducir el calendario a conteos de incendios ni usar este contraste como validación de la armonización Aqua. La asociación local es heterogénea y no justifica seleccionar solo comunas favorables.

Se ejecutó el [protocolo 9](2026-11-14-science-protocol-9.md). Es un contraste externo descriptivo; ningún factor, candidato, máscara, banda o compuerta fue ajustado con CONAF. El resultado no cambia la decisión de mantener M1 publicado, cuya validación de reconstrucción requiere otro tipo de evidencia.

## Fuente y correspondencia

[CONAF publica el resumen de ocurrencia y daño por comuna 1985–2024](https://www.conaf.cl/centro-documental/resumen-de-ocurrencia-y-dano-por-comuna-1985-2023/), actualizado en noviembre de 2024. Se conservó el XLSX de 2.587.710 bytes con SHA256 `1d92971eab0b8c73bae139f2d5228589370b72641917c630dde8eb0c9b16aad0`. Las temporadas se interpretan de julio a junio, según la [descripción de CONAF](https://www.conafprevencionincendios.cl/situacion-nacional-de-incendios-forestales/).

Se usan las doce temporadas completas 2012–2023: julio de 2012 a junio de 2024. Los nombres de las 54 comunas se emparejan sin alias con la DPA normalizada, conservando CUT, hoja, fila y nombre original. Las comunas actuales de Ñuble se buscan también cuando formaban parte de Biobío. Se verificaron encabezados, temporadas y unicidad; no se imputaron valores.

| CUT | Nombre en DPA | Temporada inicial | Fila Excel | Estado CONAF |
| --- | --- | ---: | ---: | --- |
| 08103 | Chiguayante | 2023 | 208 | vacío, desconocido |
| 08314 | Alto Biobío | 2012 | 165 | vacío, desconocido |
| 08314 | Alto Biobío | 2016 | 188 | vacío, desconocido |

El protocolo original llamó Hualqui a 08103; se corrigió mediante fe de erratas explícita. Hualqui es 08105. El parser ya usaba los nombres y CUT correctos; el panel y todos los resultados se reprodujeron idénticos byte a byte tras corregir la etiqueta del protocolo. No cambió ninguna regla de análisis.

S-NPP se agrega desde las celdas-día publicadas, grilla y cartografía actuales, con la máscara fija de 223 celdas. Los períodos cuentan con ventanas SP solicitadas completas en el inventario y no incluyen celdas-día NRT; esto **no demuestra cobertura de observación**. La máscara usa información hasta 2020, por lo que tampoco se presenta el contraste como evaluación prospectiva.

## Resultado regional primario y sensibilidad

El panel primario conserva exactamente las mismas 52 comunas en las doce temporadas, excluyendo las dos con algún conteo desconocido. La sensibilidad conserva las 54 comunas y solo las nueve temporadas en que todos sus conteos son conocidos. No se suman totales territoriales parciales como si fueran completos.

| Panel | Comunas constantes | Temporadas | Spearman | Intervalo bootstrap percentil 95 % |
| --- | ---: | ---: | ---: | --- |
| Primario | 52 | 12 | **0,0979** | **[−0,6131;0,7434]** |
| Sensibilidad | 54 | 9 | **−0,1833** | **[−0,8104;0,7368]** |

Bootstrap de 5.000 réplicas de temporadas emparejadas, semilla 20261114; las 5.000 fueron definidas en ambos paneles. Son intervalos exploratorios con pocos bloques y sin corrección de dependencia temporal; no prueban ausencia de toda asociación. La sensibilidad cambia también las temporadas, de modo que su signo no se atribuye únicamente a las dos comunas adicionales.

Al retirar una temporada por vez del panel principal, Spearman varía entre **−0,1727 y +0,3000**. Se conservan las doce exclusiones en `season_influence.csv`; no se retira ninguna temporada del resultado principal según su influencia.

Ejemplos del panel constante de 52 comunas ilustran por qué no intercambiar las unidades:

| Temporada inicial | Celdas-día S-NPP | Incendios registrados CONAF |
| --- | ---: | ---: |
| 2014 | 3.362 | 3.606 |
| 2016 | 3.575 | 1.937 |
| 2022 | 5.046 | 2.535 |

Son conteos de objetos distintos. Un episodio puede producir muchas celdas-día; el contraste agregado no empareja episodios, puntos de origen, duración ni oportunidad de observación. No se atribuye la discrepancia a un error de una fuente particular ni se afirma que cada detección tenga una clasificación operacional equivalente a CONAF.

## Resultado local

Las 54 comunas tienen al menos ocho pares conocidos y series variables: 52 tienen doce pares, Chiguayante once y Alto Biobío diez. Se publica la tabla completa, sin filtrar por magnitud o signo:

- Mediana de Spearman: **0,2054**; cuartiles **−0,1458 y 0,4155**.
- **33 correlaciones positivas y 21 no positivas**. No equivalen a 33 comunas validadas; no se hicieron pruebas de significación ni se corrigió multiplicidad.
- La dispersión local impide presentar la asociación como uniforme. Las diferencias de tamaño territorial no se usan para inflar la relación mediante una correlación agrupada de todos los pares comuna×temporada.

No se cambió a superficie quemada ni a otro resultado CONAF tras observar la asociación débil. Un contraste posterior con otro resultado requeriría declarar su pregunta y protocolo por separado; tampoco convertiría celdas-día en hectáreas.

## Consecuencia para producto y modelo

1. El producto responde sobre **actividad de fuego detectada**, con trazabilidad de plataforma y límites de observación. Este contraste no permite afirmar que el calendario mide o predice el número de incendios.
2. CONAF aporta contexto externo, pero no es verdad de terreno emparejada para calibrar aquí MODIS/VIIRS. Se necesita validación específica de sensores, dirección temporal e incertidumbre.
3. No modificar factores para maximizar estas correlaciones, ni habilitar comunas usando su signo. La comparación queda separada de los datos y compuertas publicados.
4. La siguiente iteración investigará por qué la mejora de candidatos no se conserva hacia atrás, separando cantidad de entrenamiento y máscara, con las familias congeladas.

## Reproducción y controles

`data/processed/conaf_external_audit/` incluye 648 registros con procedencia, panel emparejado, dos agregados regionales, 54 correlaciones comunales, influencia por temporada, resumen y manifiesto de hashes. El XLSX crudo no se versiona; su URL de descarga y hash están en `data/processed/external_sources/conaf-download.json`. Si la fuente cambia, el auditor se detiene en lugar de sustituir el benchmark silenciosamente.

```sh
uv sync --locked
# Descargar el XLSX oficial en data/raw/external/conaf-1985-2024.xlsx y comprobar el SHA indicado.
uv run python -m unittest discover -s tests -p 'test_conaf_external.py' -v
uv run python pipeline/conaf_external_audit.py
```

Se añadió openpyxl al proyecto y al lockfile. Lectura read_only/data_only y comprobación de fórmulas sin valor almacenado; fuente intacta antes y después. Siete tests nuevos cubren identidad, ambigüedad, blancos y ceros, conteos inválidos, encabezados y temporadas, procedencia, empates, constantes, panel territorial fijo y bootstrap reproducible. **47 tests Python pasan**; las entradas de aplicación no cambiaron. Se verifican hashes de producción y todas las auditorías anteriores. Este estudio no evalúa 2002–2011 ni autoriza un reemplazo automático del modelo.
