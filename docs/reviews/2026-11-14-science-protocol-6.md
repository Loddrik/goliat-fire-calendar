# Protocolo 6 — sensibilidad a grilla y cartografía

Fijado antes de calcular diferencias o comparar modelos en nuevos agregados. Base `5faa396`. Pregunta: ¿cuánto dependen las mejoras observadas de la asignación numérica de celdas y de los límites comunales?

## Cuatro escenarios, sin alterar producción

1. **Publicado:** celdas y asignación comunal de los Parquet versionados. Reconstruir las celdas-día desde las detecciones y exigir coincidencia exacta con la base publicada antes de comparar.
2. **Grilla decimal + geoBoundaries:** interpretar `str(float(coordenada))` como coordenada decimal canónica y calcular `floor(Decimal(valor)·100)`, con origen 0°. No es acceso al CSV crudo: se evalúa la representación decimal de las coordenadas conservadas en Parquet. Mantener los polígonos y la regla de asignación originales de geoBoundaries (primer interior encontrado).
3. **Grilla publicada + DPA 2023:** conservar los identificadores de celda y asignar sus centros a la DPA oficial normalizada de FireChronos. Interior único; bordes compartidos al CUT menor; solapamientos interiores ambiguos excluidos, nunca duplicados.
4. **Grilla decimal + DPA 2023:** combinar las dos alternativas anteriores.

Usar únicamente las detecciones canónicas anteriores a julio de 2020: las mismas observaciones, filtros y prioridades de fuente, sin añadir Type=0 ni nuevos datos. La grilla decimal es una alternativa numérica explícita, no una declaración de que el algoritmo anterior identificaba incendios equivocados. La DPA 2023 se aplica fija retrospectivamente, no reconstruye límites de cada año.

## Medición y validación

- Verificar hashes de ambas geometrías. Comprobar la reproducción de la asignación geoBoundaries existente en los mismos identificadores de celda. Detenerse si no coincide.
- Registrar detecciones que cambian de celda, ejemplos de frontera numérica, asignación de celdas, entradas/salidas/cambios de CUT y estados de borde/solapamiento. No exponer predios ni propietarios.
- Cada escenario reconstruye sus celdas-día, aprende su máscara dentro de las particiones y mantiene las 54 comunas, incluidos ceros de conteo. No cambia la interpretación de cobertura desconocida.
- Evaluar M0, M1, M2, selección M1/B, M1/P y M1/B/P con el protocolo 5, mismas temporadas 2012–2019 y anidamiento. Reproducir numéricamente los controles y políticas del escenario publicado frente a la iteración 5.
- Reportar MAE, sesgo, compuertas diagnósticas, señales retenidas y mejora relativa dentro de cada escenario. Cambiar cartografía o grilla cambia la variable objetivo; **no comparar MAE absoluto entre escenarios como si midiera precisión física contra la misma verdad**.
- No elegir una geografía o regla numérica por dar más comunas habilitadas. Las diferencias deben orientar la decisión de contrato de datos, no optimizar retrospectivamente métricas.

## Artefactos y plazo

Directorio nuevo `data/processed/geography_audit/`, con hashes, diagnósticos, asignaciones, predicciones y selecciones por escenario. Las tablas DuckDB se reconstruyen solo en memoria. Proteger los archivos publicados y todas las iteraciones previas. Tests de piso decimal, asignación única, agujeros, bordes compartidos y exclusión de solapamientos interiores. Se mantiene el plazo de investigación 21:00 de Santiago y todos los PR contra `dev`.
