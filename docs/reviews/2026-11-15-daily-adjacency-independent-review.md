# Revisión independiente 36 — cubo de adyacencia Aqua

**Pasa sin bloqueantes la integridad del predictor y su placebo.** Se verificaron todas las 5184 claves, las 10368 filas Aqua de control, los 9902 registros canónicos seleccionados y los 157788 mappings diarios del calendario completo. La revisión terminó a las **08:02:23 UTC**, antes del cap original 08:33:23; el checkpoint del productor fue auditable a las 07:57:21, antes de su límite 08:03:23.

El verificador propio se congeló antes de recalcular features, con SHA del freeze `726a7349fad8c8f5f0384691c9e4fddbbc65dde755e67e6c232b5a8886197a9c`. Usó los registros Aqua canónicos y la máscara de seis celdas, sin importar el helper del productor para decidir D. La implementación independiente representa los días de cada celda mediante un entero binario y cuenta pares con `(bits & (bits >> 1)).bit_count()`, en lugar de intersectar conjuntos de celdas de días adyacentes. Ambas implementaciones coinciden en cada fila CSV y Parquet.

Se verificaron fechas UTC, temporadas julio–junio, bisiestos 2016/2020 y exclusión de pares entre meses. Todos los registros de una celda conservan su CUT y no se usó multiplicidad intradía como días adicionales. Aqua reconstruido coincide con cada fila del control 21, sin promediar duplicados contradictorios ni leer respuestas SNP.

Para cada CUT/mes se reconstruyó el orden hash de **todos** los días. El mapping ORIGEN→DESTINO coincide con el literal congelado, incluida su dirección. Se comprobaron las 5184 bijecciones, conteos por celda, multiconjuntos de conjuntos de celdas activos por día —incluidos días vacíos— y distribuciones de conteos diarios. Las incidencias SOURCE×ORIGIN se mantuvieron separadas de SOURCE/held×DESTINO en todos los diagnósticos.

Se reprodujeron 105 meses con D_real=1, 59 con D_placebo=1 y 110 discordantes. Los 192 y 85 pares respectivos siguen siendo diagnósticos prefijados, no nuevas features. Estos números no prueban utilidad predictiva ni causalidad. La permutación puede conservar D; ninguna identidad exige variación ni otra semilla.

Los nueve tests puros pasan. Fuentes, código y salidas coinciden por hash; el manifiesto del productor permanece `9169cc2320591a000d72097b76d2207e652bc3141b2f10cc183a3f993272c626`, sin modificación o ampliación. La [evidencia independiente](evidence/daily-adjacency-independent-review/summary.json), [freeze](evidence/daily-adjacency-independent-review/freeze.json) y [snapshot del verificador](evidence/daily-adjacency-independent-review/verifier-code.py.txt) quedan separados del productor. El snapshot registra la ruta ROOT local y el cap con que se ejecutó; no promete un replay irrestricto después del vencimiento.

En el resumen independiente, `all_source_event_rows=9902` se refiere al subconjunto **Aqua, temporadas 2012–2019, tras excluir la máscara6**; no al historial completo ni a adquisición raw restaurada. Cero registros o D=0 no identifica ausencia de fuego, FOV útil o cobertura. D=1 tampoco identifica un mismo incendio físico.

No se abrieron modelos, respuestas SNP o HDF, ni se ejecutaron fits, pérdidas, solvers o nuevas adquisiciones. El pase no autoriza automáticamente la etapa 37. Un modelo requiere otro protocolo y revisión; 35A continúa negativo, 30B fallido y G1 físico falso.
