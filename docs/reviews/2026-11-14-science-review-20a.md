# Revisión científica 20A — comparación de contratos en archivo común

La investigación y el producto `observed` producen conteos cercanos en su archivo común, pero sus contratos no son idénticos. En 3456 comuna-meses, el total científico es 14649 celdas-día frente a 14713 del producto observado; la diferencia neta −64 oculta 220 unidades de diferencia absoluta repartidas en 164 filas. Esta auditoría describe definiciones y procedencia; no valida fuego real ni evalúa modelos.

## Dominio fijado antes de comparar

La etapa 20 estricta permanece detenida: 324 filas de enero–junio de 2026 carecen de archivo `observed`. El protocolo 20A se congeló en `db3391e` después de identificar ese límite documental y antes de medir diferencias. Restringe las filas de 19 por `start`, `end` y `available_years` del manifiesto NOAA-20 observado, sin usar cantidades de actividad ni errores para elegir fechas.

La intersección contiene 64 meses y 54 comunas, julio de 2020–diciembre de 2025, conservando la exclusión previa de agosto/septiembre de 2020: 3456 filas. Las 324 exclusiones se exportan explícitamente y no se rellenan con cero. No se descargó información ni se ajustaron modelos; no se calcularon MAE de predicciones ni rankings.

Se reprodujeron exactamente O0 desde los CSV contra las series publicadas y Cmaskedall desde detecciones contra NOAA-20 de 19. Se verificaron de nuevo hashes, tamaños, filas, filtros, geometría DPA y procedencia de publicación. La misma máscara de 223 celdas y el mapa científico permanecieron congelados. La disponibilidad de archivos/solicitudes no mide oportunidad útil de observación.

## Transformaciones y cierre

Ambas rutas asignan por **centro de celda**. `Observed` utiliza DPA 2023 y una cuadrícula que redondea antes de aplicar el piso; la investigación utiliza su mapa geográfico previo y la expresión literal `floor(lon/.01), floor(lat/.01)`. El siguiente recorrido mantiene un orden fijo: los componentes son contrastes mecánicos condicionados por ese orden, no efectos causales independientes.

| Variante | Definición | Total 54 | Total 14 publicadas | Total 40 restantes |
|---|---|---:|---:|---:|
| O0 | Conteo publicado, cuadrícula y comuna O |14713|5993|8720|
| Ogrid | Cuadrícula literal C, conservando comuna O |14714|5993|8721|
| Omask | Ogrid sin las 223 celdas estáticas |14617|5965|8652|
| Omap | Omask reasignado por mapa C; excluye mapa ausente |14613|5968|8645|
| Cmaskedtype0 | Detecciones C tipo0 antes de deduplicar celda-día, mapa y máscara C |14632|5975|8657|
| Cmaskedall | Todas las categorías C, mapa y máscara C |14649|5987|8662|

El cierre se verificó exactamente en cada comuna-mes:

`Cmaskedall − O0 = (Ogrid − O0) + (Omask − Ogrid) + (Omap − Omask) + (Cmaskedtype0 − Omap) + (Cmaskedall − Cmaskedtype0)`

| Componente, 54 comunas | Suma firmada | Suma de diferencias absolutas | Filas idénticas de 3456 |
|---|---:|---:|---:|
| Cuadrícula |+1|1|3455|
| Máscara dentro de Ogrid |−97|97|3388|
| Mapa y soporte disponible |−4|92|3379|
| Residual entre cohortes tipo0 |+19|19|3443|
| Categorías de tipo dentro de C |+17|17|3444|
| Brecha final Cmaskedall−O0 |−64|220|3292|

El máximo de diferencia absoluta final es cuatro celdas-día en un comuna-mes. No se suman los valores absolutos de los componentes para atribuir porcentajes del total: pueden compensarse dentro de una fila y entre territorios.

## Bordes, soporte geográfico y tipo

Entre las 23875 detecciones O seleccionadas en el dominio común, 50 están cerca de un borde literal de cuadrícula y una recibe una celda distinta al aplicar la regla científica. Esa diferencia aumenta en una unidad el conteo mensual después de deduplicar. La tabla de diagnósticos conserva coordenadas, celdas de ambas reglas, fecha, fuente y versión; la igualdad de reglas no se asumió por compartir resolución nominal de 0.01°.

Después de aplicar la máscara, 47 celdas-día observadas cambian de CUT al usar el mapa científico. Otras cuatro celdas-día, provenientes de cinco detecciones, no tienen entrada en ese mapa y se excluyen de Omap. El contraste neto −4 y la diferencia absoluta de 92 incluyen movimientos, posibles fusiones por deduplicación y soporte ausente. No equivalen a un efecto aislado de límites administrativos: `cells_comuna` contiene soporte derivado de las observaciones científicas originales.

Dentro de C, el filtro `type==0` se aplicó **antes** de deduplicar. Se registran 14627 celdas-día con solo tipo0, cinco con tipo0 y otro tipo, y 17 sin tipo0 pero con otro tipo. No aparece tipo desconocido en este dominio; no existe aquí evidencia para evaluar ese caso real, aunque la prueba sintética confirma que desconocido no se transforma en cero. Los cinco días mixtos permanecen en Cmaskedtype0 y se cuentan una sola vez: sumar por categorías sin considerar solapamientos produciría duplicación.

Las detecciones C del dominio y máscara son `api_sp`, versión2: 23774 filas tipo0 y 28 de otros tipos. Esas 28 filas ocupan 22 celdas-día, de las cuales cinco ya contienen tipo0 y 17 explican el incremento mecánico Cmaskedall−Cmaskedtype0. Las sumas de celda-día de cohortes pueden solaparse; el archivo de patrones registra la unión correcta.

El residual Cmaskedtype0−Omap suma +19 en 13 filas. Sigue mezclando archivos, cohortes, versiones, selección y asignación geográfica previa. Los CSV O ya fueron filtrados y no permiten recuperar detecciones excluidas antes de exportar. Ni el cierre exacto ni la pequeña magnitud residual identifican una causa o prueban equivalencia científica entre contratos.

## Territorios y períodos

| Grupo | Filas | Brecha neta C−O | Diferencia absoluta total | Filas idénticas |
|---|---:|---:|---:|---:|
| 54 comunas |3456|−64|220|3292|
| 14 publicadas |896|−6|70|843|
| 40 restantes |2560|−58|150|2449|

Las 14 comunas muestran casi igualdad de totales, pero difieren en 53 meses-comuna. Una diferencia neta pequeña no demuestra que las series locales sean intercambiables.

| Corte, 54 comunas | Filas | Brecha neta C−O | Diferencia absoluta total |
|---|---:|---:|---:|
| Temporadas 2020–2021 |1188|−33|93|
| Temporadas 2022–2025, archivo común |2268|−31|127|
| Antes de calendario2022 |864|−29|69|
| Desde calendario2022 |2592|−35|151|

Los cortes por temporada y por año calendario no son equivalentes: enero–junio de 2022 pertenece a temporada2021. La temporada2025 queda limitada a julio–diciembre en este archivo común; no se describe como temporada completa. Los desgloses completos 54/14/40 para ambos tipos de período quedan exportados.

## Implicación y artefactos

La etapa19 se interpreta como sensibilidad a plataforma dentro del contrato C; no como reproducción de `observed`. La etapa20A cuantifica ahora esa brecha de contrato sin cambiar el referente ni recalcular errores de los candidatos. No se promueve ningún modelo. Para mejorar la ciencia siguen pendientes datos sobre oportunidad real de observación y comparación de adquisiciones equivalentes.

`data/processed/contract_gap_common_archive_audit/` contiene conteos y deltas por fila, exclusiones documentales, contrastes por grupo/período, diagnósticos de cuadrícula/mapa, cohortes de ambas rutas y patrones de tipo por celda-día. El manifiesto identifica ambos protocolos, código, entorno, hashes y la protección de resultados anteriores/publicación. El error máximo de cierre es cero y todos los archivos protegidos permanecieron idénticos, incluida la evidencia fallida de 20.

Pasaron nueve pruebas sintéticas combinadas de 20/20A, incluidas selección de archivo independiente de actividad, exclusión explícita de 2026, reglas de borde, tipos antes de deduplicar, mapa ausente/movimientos, unión de claves, cierre y rechazo de CSV/series incompatibles. La ejecución real confirmó ambas reproducciones exactas antes de exportar contrastes.
