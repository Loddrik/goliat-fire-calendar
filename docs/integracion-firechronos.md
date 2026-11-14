# Integración GOLIAT + FireChronos

14 de noviembre de 2026. Base GOLIAT: `6d0db39`; base FireChronos: `d61ccf826ed3dbfd6461ad19324b0d65f9ffd4ac`.

## Resultado

Una aplicación React, un selector comunal y dos publicaciones explícitas. El calendario de GOLIAT conserva el método y las 14 comunas habilitadas de la revisión científica recibida. El historial por plataforma incorpora el archivo observado de FireChronos: Aqua, S-NPP y NOAA-20, DPA 2023 oficial, hashes, exportaciones y cobertura desconocida. El explorador original, incluida la carga local de CSV, permanece en `/observed/index.html`.

Se preservan los dos pipelines. No se sustituyen los polígonos ni filtros del experimento armonizado por los de FireChronos, pues eso exigiría recalibrar y validar de nuevo. Los archivos crudos y entornos locales quedan fuera de Git. La configuración de acceso del sitio privado FireChronos no se incorpora al repositorio público ni se cambia.

## Contratos

| Vista | Publicación | Unidad y alcance |
| --- | --- | --- |
| Calendario armonizado | `pipeline/publish.py` → `/data/index.json`, `/data/comunas/<cut>.json` | Celdas-día en escala VIIRS. S-NPP/NOAA-20 por temporada; Aqua estimado donde pasan las compuertas. Cartografía geoBoundaries/BCN y máscara de GOLIAT. |
| Historia por plataforma | `pipeline/publish_observed.py` → `/observed/data/publication/` | `cell_days_per_platform`, `harmonization: none`. DPA 2023, día, confianza, Type=0; sin máscara persistente adicional. Archivo anual hasta diciembre de 2025. |

El segundo publicador verifica los 162 CSV por SHA-256 y reproduce sus 29.322 filas mensuales a partir de 119.232 detecciones seleccionadas. Verifica además el hash de la geometría normalizada. React verifica el hash y el contrato de cada documento antes de mostrarlo y utiliza los valores publicados, sin ajustar ni volver a contar la actividad.

La consulta exporta meses seleccionados y metadatos de comuna, plataforma, unidad, filtros, grilla, cartografía y procedencia. El enlace al CSV original está rotulado como archivo completo de esa plataforma/comuna, independiente del rango de consulta. Las descargas de la otra vista desaparecen al cambiar de vista. Las consultas inválidas y las respuestas corruptas ocultan resultados y bloquean exportaciones.

## Correcciones comprobadas durante la integración

1. **JSON inválido.** El índice recibido contenía `Infinity` en dos diagnósticos de `params`. `JSON.parse` lo rechaza, dejando vacío el selector. La publicación convierte exclusivamente diagnósticos no finitos a `null`, registra las rutas en `unavailable_metrics` y serializa con `allow_nan=False`. No cambia el factor, las compuertas ni el archivo original de parámetros.
2. **Ventana estacional.** Para cortes julio–diciembre, el predicado recibido incluía también enero–junio en los acumulados históricos. Se corrigió para exigir mes ≥ 7 y fecha mes/día ≤ corte. Para enero–junio incluye julio–diciembre previos y enero–corte. Se regeneraron los 54 documentos; los acumulados se comprobaron contra los registros diarios con un cálculo independiente. Ejemplo Penco al 13 de noviembre: el valor actual sigue en 3; la mediana histórica pasa de 4 a 0 porque se excluyen meses futuros respecto del corte.
3. **Reproducción desde un clon.** Faltaba `data/raw/dpa/comunas_cut.csv`, pese al soporte Parquet del publicador. Ahora usa las propiedades CUT/nombre/región del GeoJSON versionado cuando no existe ese CSV y exige 54 CUT únicos.
4. **Estado de consulta.** Se abortan solicitudes anteriores, se valida la comuna recibida y se revalidan los JSON HTTP. Se evita conservar exportaciones de otra comuna mientras carga una nueva y reutilizar un índice inválido desde la caché.

La corrección de enero–junio de 2013, la actualización de CUT y las nuevas compuertas ya venían en `6d0db39`; se conservaron. Los tests incluyen la regresión temporal de 2013 para todas las comunas.

## Comprobaciones

- `python3 pipeline/publish_observed.py`: hashes y reproducción completa de 162 CSV y 29.322 agregados.
- `npm test`: pruebas originales de CSV, grilla, filtros y faltantes, más contratos, hashes, incompatibilidad de unidades y regresión de 2013.
- `python -m unittest discover -s tests -p 'test_*.py' -v`: fechas julio/noviembre/diciembre/enero/marzo/junio, JSON estricto y contraste independiente de todos los acumulados publicados con los Parquet diarios.
- Tests geográficos y de procesamiento de FireChronos y `observed/tests/verify_history.py`: originales locales, geometría, asignación y 29.701 comprobaciones de agregación.
- Compilación TypeScript/Vite y revisión de navegador de ambas vistas, selección comunal, plataformas, rango de meses, descargas, idiomas, errores y adaptación móvil. Resultado del navegador en `docs/reviews/2026-11-14-integration-browser.json`.

## Límites vigentes

La integración no aporta una nueva validación independiente del modelo. Se mantienen las divulgaciones de `docs/method.md`, incluido el carácter descriptivo del bloque 2020–2021. La máscara aprendida antes de julio de 2020 y su uso dentro de los folds requieren revisión científica; aquí no se refitó la máscara ni se modificaron sus métricas. La equivalencia de versiones Aqua y el historial anual 2026 de FireChronos siguen pendientes. No se concatenan las dos publicaciones ni se trasladan sus coeficientes.
