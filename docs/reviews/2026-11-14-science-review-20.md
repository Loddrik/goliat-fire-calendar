# Revisión científica 20 — dominio incompatible entre contratos

La auditoría estricta se detuvo en el control de disponibilidad, antes de cuantificar diferencias entre contratos. El panel de investigación de la etapa 19 incluye enero–junio de 2026; los archivos y series `observed` NOAA-20 terminan en diciembre de 2025. Esas ausencias no son ceros y no se redujo el dominio silenciosamente.

## Controles ejecutados

Se aplicó el protocolo congelado en `4366588`, sin ajustar modelos, descargar datos ni calcular MAE de modelos. Los resultados son:

| Control | Resultado |
|---|---|
| Dominio fuente 19, hash y claves únicas | 3780 filas, 54 comunas, conservadas |
| Detections, celldays, mapa y máscara frente al manifiesto 19 | Hashes idénticos |
| Geometría DPA frente al manifiesto `observed` | Hash idéntico |
| 54 CSV NOAA-20: hash, tamaño, filas, comuna, fuente y filtros | Reproducidos |
| Cuadrícula `observed` y series mensuales de CSV/manifiesto/publicación | Reproducidas exactamente |
| Cmaskedall desde detections + mapa + máscara | Reproduce exactamente el referente NOAA-20 de las 3780 filas de 19 |
| `observed` disponible en todas las 3780 filas | **Falla** |

El control final identifica 324 filas sin soporte `observed`: 54 comunas por los seis meses de enero–junio de 2026. Las temporadas de investigación son julio–junio y la temporada 2025 alcanza junio de 2026. La fuente publicada declara `end=2025-12`. El estado queda como `blocked-contract-domain-incompatibility`.

## Qué no se deduce

No se midieron todavía Ogrid, Omask, Omap, Cmaskedtype0 ni los componentes del cierre. No se atribuyó ninguna diferencia a tipo, geometría, archivos o versiones; no se eligió un referente favorable ni un nuevo modelo. El cero publicado en un mes con archivo disponible sigue describiendo ausencia de detecciones bajo su contrato, no ausencia física de fuego ni oportunidad útil de observación.

Ambas rutas asignan por **centro de celda**. El contraste pendiente no es detección puntual contra centro de celda: `observed` usa DPA 2023 y la investigación conserva otra geometría y otro soporte de mapa. La cuadrícula literal científica puede además discrepar en bordes con la regla redondeada de `observed`. Las funciones para examinar esas transformaciones quedaron preparadas y probadas, sin ejecutarlas sobre datos reales bajo un dominio modificado.

## Siguiente paso propuesto

Un protocolo adicional puede fijar la intersección por disponibilidad documental, julio de 2020–diciembre de 2025, preservando las exclusiones heredadas de agosto/septiembre de 2020. Esa restricción se justificaría por soporte de archivos y calendario, antes de observar contrastes; no constituye selección por resultados. Requiere congelar esa nueva especificación antes de medir cantidades. La etapa 20 estricta queda cerrada como control fallido y no se sobrescribe para aparentar éxito.

## Reproducibilidad

`data/processed/contract_gap_audit/summary.json` registra los controles y el motivo de detención; `observed_domain.csv` conserva las 3780 claves y marca explícitamente las 324 ausencias como desconocidas; `manifest.json` registra protocolo, código, entorno y hashes. Los artefactos anteriores y las publicaciones permanecieron idénticos.

Pasaron siete pruebas sintéticas: borde de cuadrícula; tipo antes de deduplicar y desconocido distinto de cero; mapa ausente y movimiento de comuna; cierre algebraico; ausencia de mes no rellenada; rechazo de series discrepantes y rechazo de CSV corrupto. No se modificaron datos anteriores ni Git.
