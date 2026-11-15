# Revisión independiente40 — preflight documental GOES16

**Sin bloqueantes para el alcance documental condicionado.** La revisión corroboró las fuentes y los dos listados mediante accesos propios, contrastó la matriz conocido/desconocido y el esquema documental del productor y revisó sus conclusiones. No acredita lectura de productos científicos, ejecución de un decoder histórico o elegibilidad física del piloto. Los hashes finales de los artefactos revisados se fijan en el manifiesto independiente.

El protocolo corresponde al commit `64b79f6`, SHA256 `8f5df8704d9adc17e35b8e8c5e86309d8cf1cfedc626362e7e014ea6cd187fe2`. Se conserva el cap09:15–10:00UTC y la ampliación ratificada por capacidad efectivamente liberada, independiente del resultado39. No se modifica el cierreD.

## Comprobaciones independientes

Se recuperaron directamente documentos oficiales NOAA y los dos S3LIST compartidos; no se siguió ningún enlace de objeto científico. Los PDF completos permanecen en caché ignorada. Las recuperaciones propias de PUGv3.0, ATBDv2.7 y ReadMev2 coinciden por tamaño/SHA con las del productor. PUGv2.4 fue recuperado por este revisor y el productor utilizó esa misma caché: no se presenta como dos adquisiciones independientes. El acceso fallido al PUGlegacy y aNCEI no demuestra inexistencia de datos.

Los dos XML independientes coinciden con los del productor. Un verificador propio reconstruyó los diez registros por nombre, modo, inicio/fin declarados, tamaño yLastModified. Ambos listados son completos para esos prefijos (`IsTruncated=false`): cuatro clavesM3 en2019/003/18 con inicios separados900s y seisM6 en2023/041/18 separados600s. Se cotejaron sus fechas como metadatos de nombres, sin convertirlas en observaciones delAOI. El snapshot del verificador y los XML están en la [evidencia separada](evidence/goes-preflight-independent-review/catalog-verification.json).

El [avisoNOAA de marzo2019](https://www.ospo.noaa.gov/data/messages/2019/03/MSG_20190327_1424.html) y la [página de modosABI](https://www.nesdis.noaa.gov/our-satellites/currently-flying/goes-east-west/abi-scan-mode-information-and-channel-summary) respaldan el contexto del cambioM3→M6. Los nombres de ambos casos respaldan el modo declarado de sus archivos. Esto no verifica su contenido ni continuidad de observación útil.

## Semántica y límites corroborados

El [PUGv2.4,11julio2022](https://www.ospo.noaa.gov/resources/documents/PUG/GS%20Series%20416-R-PUG-L2%20Plus-0349%20Vol%205%20v2.4.pdf),§5.19, especifica grilla fija, ángulosx/y y resolución nominal2km al nadir. Describe`t` como referencia central del scan y sus extremos; no como exposición porpíxel. Se cotejaron los códigos documentados: Mask0 sin procesar,100 sin detección algorítmica,fill−99; DQF0 corresponde a fuego,1 a terreno procesado sin fuego,2–5 a causas de invalidez yfill255. El informe conserva esos valores como esquema esperado, no como atributos verificados de2019/2023. No se calculó geometría o resolución efectiva delAOI.

La discrepancia temporal está correctamente conservada. El [ReadMe actualizado20diciembre2019](https://www.ospo.noaa.gov/operations/goes/product-quality-overview/ps-pvr/goes-16/ABI/Fires%20and%20Hot%20Spots%20Characterization/Provisional/GOES-16_ABI_L2_FHS_Provisional_ReadMe_v2.pdf) describe antecedentes en el mismo píxel durante12h y declara una diferencia frente al vecindario delATBD. También informa problemas de procesamiento, especialmente enSudamérica, con correcciones entonces previstas para2020. No prueba el estado del caso enero2019 ni su corrección en2023. El [ATBDv2.7,octubre2020](https://www.ospo.noaa.gov/resources/documents/ATBD/ATBD_GOES-R_FIRE_v2.7_Oct2020.pdf) conserva un vecindario de líneas/elementos; no adjudicamos qué versión se desplegó. Repetición de clases filtradas no es confirmación independiente de continuidad del mismo incendio.

La detección subpíxel contemplada por el [ATBDv2.6](https://www.star.nesdis.noaa.gov/goesr/documents/ATBDs/Baseline/ATBD_GOES-R_FIRE_v2.6_Oct2013.pdf) impide afirmar que un sensor grueso sólo detecte incendios grandes. Tampoco convierte su ausencia en refutación375m o su positivo en verdad de terreno. El informe expresa una falta de evidencia para adjudicar discrepancias finas, no una imposibilidad física general.

## Dictamen y adquisición

El resultado defendible es **factibilidad documental condicionada para contexto temporal grueso**; la semántica histórica ejecutable y el contenido real permanecen inconclusos. LIST público no pruebaGetObject, variables válidas o condiciones de los objetos. Un campo genérico de licencia delPUG tampoco determina por sí solo sus condiciones reales ni exige cuentas o acuerdos.

Los registros inspeccionados contienen únicamente documentación y LIST; no hay solicitudes científicasGET/HEAD/Range, autenticación o cuentas. Esta revisión solicitó **cero objetos y cero bytes científicos**. Los bytes de documentación son una categoría separada, con cantidades registradas donde el transporte las informó. No se reabre el presupuestoL2 ni se autoriza adquisición futura.

No quedan correcciones científicas pendientes en el alcance revisado. Un trabajo futuro necesitará otra decisión/protocolo, versiones y geometría aplicables y validación de contenido. Este pase no acreditaG1,PSF, exposición física, oportunidades comparables, calibración o un factor de armonización; no rescata35/37 ni altera39 o30B.
