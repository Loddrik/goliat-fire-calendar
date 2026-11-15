# Seguimiento 34: cómo adjudicar el flag global de MYD14 L2

Consulta documental: **15 de noviembre de 2026**, iniciada 06:51:59 UTC, con cap de 30 minutos. **La búsqueda no resolvió la semántica específica de `Suspect` / `not being investigated` en MYD14 colección 6.1.** Añade una ruta concreta de procedencia y un límite de acceso, no evidencia para liberar ni declarar defectuoso el producto. La [nota anterior](2026-11-14-modis-global-quality-note.md), la cuarentena y los indicadores científicos permanecen intactos. No se leyeron datos, clases, HDF ni modelos; no hubo contactos, credenciales, aceptación de acuerdos o descargas satelitales.

## Evidencia nueva y límite de la búsqueda

El [portal oficial MODAPS de distribución PGE](https://modaps.modaps.eosdis.nasa.gov/services/pge/) —actualización declarada 27-01-2020, consultado hoy— identifica código fuente de producción MODIS/VIIRS, pero exige Earthdata Login y firma de Software Usage Agreement antes de habilitar visualización/descarga. Se consultó únicamente la página pública. **No se inspeccionó ese código** ni se intentó superar el acceso. Es una vía de adjudicación potencial, no una prueba sobre el valor del flag.

La [guía NASA DRL de MOD14 SPA 6.2.1](https://directreadout.sci.gsfc.nasa.gov/users_guides_documents/MOD14_6.2.1_SPA_1.1.pdf), enero de 2017, documenta un wrapper 1.1 con algoritmo portado desde la producción MOD14 6.2.1 para Direct Readout/IPOPP, con entradas Terra/Aqua. Su publicación establece una familia de implementación identificable, pero **no demuestra identidad del escritor de metadatos, wrapper o configuración con el MYD14 C6.1 operacional del piloto**. También exige acuerdo antes de descargar software; no se descargó ni ejecutó.

A diferencia del acceso fallido registrado el día anterior, ahora se recuperó el texto completo de la [guía C6/C6.1 v1.0, mayo de 2021](https://lpdaac.usgs.gov/documents/1005/MOD14_User_Guide_V61.pdf). Las búsquedas textuales dirigidas de `Suspect` y `AutomaticQualityFlag` no devolvieron coincidencias. Esto cierra aquel límite de acceso, **no prueba ausencia de toda explicación implícita o de documentos complementarios**. La [filespec MYD14 C61](https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/61/MYD14_c61.fs), revisión interna 6.2.3 del 04-09-2014, sigue identificando los campos, sin aportar en las secciones consultadas la regla decisoria buscada.

La búsqueda adicional cubrió combinaciones de MOD_PR14/MYD14/MOD14, los dos literales del flag, MCF y metadata en documentación indexada NASA/MODAPS y del equipo científico. No se localizó una asignación pública verificable del escritor MYD14 que resolviera la cuestión. No se usaron ejemplos HDF de terceros, productos L1B o la repetición del mismo texto como evidencia de que sea constante. Este resultado negativo no implica inexistencia de código o aclaración publicada fuera de ese alcance.

## Estrategia específica de adjudicación, sin ejecutar ciencia

La unidad de evidencia necesaria es **la procedencia del campo**, no más píxeles de fuego. Un seguimiento sólo documental debería exigir esta cadena:

1. Identificar por metadatos de procedencia ya autorizados el producto/colección, versión de algoritmo y PGE, rama de producción estándar/NRT y versión/configuración del escritor. No inferir el número PGE del «14» en MOD14 ni confundir revisión de filespec con versión de código.
2. Localizar la definición MCF del campo y la rutina que lo escribe, junto a wrapper/configuración y todas las asignaciones posteriores. Un literal `Suspect` en una plantilla sólo acredita un valor inicial: **no demuestra constancia si luego puede sobrescribirse**.
3. Adjudicar dos hipótesis distinguibles: asignación incondicional/placeholder de ese escritor, o evaluación dependiente de entradas/estadísticas del granule. Si es dinámica, documentar condición, umbral y sentido; si es plantilla, demostrar que no existe un overwrite alcanzable en la ruta pertinente. Registrar versión, archivo, líneas y hash del artefacto realmente inspeccionado.
4. Si sólo se consigue una implementación Direct Readout, otra colección o un fragmento sin configuración/wrapper, conservar «correspondencia operacional no demostrada». No transferir una explicación L1B MOD_PR02 al escritor L2. Una aclaración publicada explícita del equipo sobre MYD14 y versiones aplicables podría satisfacer la misma necesidad sin reconstruir el call graph.

No se propone obtener más granules para contar cuántos repiten el flag: una constante de plantilla y un estado persistente de evaluación podrían generar la misma observación. Tampoco se propone ejecutar MOD_PR14 o reproducir radiancias para interpretar un campo cuya regla de producción aún no está identificada.

## Decisión

**Cerrar este seguimiento como negativo para la resolución semántica, con una dependencia de acceso/versionado ahora explícita.** No afirmar que `Suspect` significa fallo individual ni que es inocuo; no exigir un futuro `Passed` como regla NASA que no se ha demostrado. La política conservadora del piloto no se modifica.

Esta cuestión es distinta de la PSF o de las esquinas ópticas exactas: perfeccionar un footprint no revela quién asignó el metadato. Un estimando descriptivo de clasificaciones registradas puede tener requisitos propios declarados y conservar este flag pendiente, sin reclamar verdad física; su autorización concreta depende del protocolo correspondiente. Esta nota no habilita nuevos análisis, no amplía G1 ni convierte una aproximación nominal en certificación científica.
