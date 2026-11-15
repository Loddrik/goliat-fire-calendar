# Preflight35 — tres hipótesis de siguiente iteración

**Sólo disponibilidad/coste, pendiente del consejo35 tras revisión33.** No se leyeron valores de targets, etiquetasQA33 ni arrays de predicciones para calcular resultados. Se inspeccionaron esquemas/metadataParquet, código y manifests, y se verificaron hashes existentes. No se calcularon pérdidas, scores, features, mezclas, presupuestos nuevos o refits. No se selecciona propuesta. Criterios del consejo conservados: validez/identificabilidad30%, información discriminante25%, factibilidad/reproducción/coste20%, transporte/selección15%, utilidad interpretativa10%.

## Tres propuestas del agente loco

- **A — presupuesto de reconciliación por grupos.** LimitarEcoherent con presupuestos derivados deB por región real; contrastar con una partición artificial de tamaños33/21 fijada porhash antes de resultados. Sin nuevosfits. Pregunta condicional sobre acoplamiento territorial de la decisión, no prueba de ecología.
- **B — persistencia diaria de deteccionesAqua.** Indicador de actividad registrada en días consecutivos, contrastado con placebo de permutación de días y una semilla única prefijada. Operador/unidad exactos pendientes: “la misma celda en días consecutivos” y “alguna celda de la comuna cada día consecutivo” son variables distintas. Incorporarlo al modelo necesita protocoloSOURCE-only propio y controles.
- **C — mezcla fija.** `H=(B+Ecoherent)/2`, proporción1/2 fijada antes de calcular cualquier pérdida. Postprocesamiento de estimaciones congeladas, sin refit ni búsqueda de proporciones.

Ninguna es mejora demostrada. No rescatar23 primario negativo con secundarios;24C estable globalmente conserva fragilidad14. Nuevas funciones en fechas ya exploradas no sonholdoutfresco. Ninguna ruta acredita observabilidad física,PSF,G1 o cambia producción.

## Historia canónica y originales faltantes

Archivos derivados locales existentes, metadataParquet inspeccionada sin valores de target:

| Ruta bajo `data/processed/` | Filas declaradas por metadata | Tamaño bytes | Campos pertinentes |
|---|---:|---:|---|
| `celldays.parquet` |116413|766995|sat,cut,cell_x,cell_y,acq_date,y,m,season,n_det,any_nrt|
| `detections.parquet` |274926|6099252|lat,lon,acq_date,acq_time,sat,instrument,confidence,frp,type,version,source_kind,cell_x,cell_y|
| `cells_comuna.parquet` |21730|66905|cell_x,cell_y,cut|
| `static_mask.parquet` |223|1892|cell_x,cell_y,rule|

Dtypes inspeccionados: en `celldays`, sat/cut son string, cell_x/cell_y int32, acq_date `date32[day]`, season/m int64 y any_nrt bool. En `detections`, fecha es `date32[day]`, hora string, type int32 y frp double. En predicciones21, CUT/g/regime son `large_string`, season/m int64 y B/E11_coherent double. Las fechas diarias no conservan la hora dentro de celldays; acq_time permanece en detections.

El código `pipeline/build_detections.py` documenta filtrado diurno/confianza y deduplicación canónica; `pipeline/build_monthly.py` preserva celda/satélite/día y asignaciónCUT. `pipeline/scientific_audit.py:AuditData` consume directamente estosParquet, no losCSVcrudos.

**B es materialmente construible desde estos derivados sin los1071CSV originales faltantes reportados en la sesión.** No se recontaron aquí los crudos faltantes y no se afirma que se pueda reconstruir el historial completo desde ellos. Integridad de un derivado congelado y reproducibilidad íntegra de adquisición son afirmaciones distintas.

Los cuatroParquet canónicos anteriores coinciden porSHA256 con `protected_sha256` de los manifests de18 (`coherent_audit/manifest.json`),21 (`cold_region_audit/manifest.json`) y24C (`contract_model_sensitivity_audit/manifest.json`). Sus rutas y hashes completos permanecen en esos manifiestos; no se sustituyeron ni reescribieron archivos. Las prediccionesParquet de cada uno también coinciden con `output_sha256` correspondiente.

La máscara223 disponible es la publicada de ese contrato, no una máscara universal intercambiable:21usa su máscara fija pre2012 documentada en `cold_region_audit/candidate_mask.csv`. No asumir que223 puede usarse en entrenamientoSOURCE-only o sustituir otras máscaras. Elegir el contrato/estudio antes de extraer persistencia y reproducir su máscara exacta porfold/régimen.

## Predicciones y modelos disponibles paraA/C

| Archivo bajo `data/processed/` | Filas metadata | Campos disponibles pertinentes |
|---|---:|---|
| `coherent_audit/nested_predictions.parquet` |5184|cut,season,m,g,aqua,M1_B,E11_10,E_mean,E_coherent,E_proportional|
| `coherent_audit/blocked_predictions.parquet` |7776|mismos campos, case de transporte|
| `coherent_audit/later_predictions.parquet` |3780|mismos campos,block,orbit_epoch|
| `cold_region_audit/predictions.parquet` |10368|cut,season,m,g,aqua,B,E00,E11,E11_mean,E11_coherent,E00_coherent,E11_proportional,regime,source_region,role|
| `contract_model_sensitivity_audit/paired_predictions.parquet` |3456|cut,season,m,month,g,block,orbit_epoch,aqua_C,aqua_O,M1_B_C/E_coherent_C,M1_B_O/E_coherent_O yotroscontroles|

Las tablas contienen además respuestas históricas para los estudios respectivos; **no se accedió a sus valores en este preflight**. Los nombres no hacen intercambiables targets,máscaras ocohortes. No sumar porcentajes ni combinar21/18/24C como replicaciones independientes.

Se verificó existencia de modelos congelados: `hurdle_audit/frozen_model.json`, `hurdle_audit/outer_hurdle_models.json`, `coherent_audit/transport_hurdle_models.json` y `cold_region_audit/models.json`. No se abrieron sus valoresCDF para esta comprobación. El código `coherent_experiment.py:distributions/extend` y `cold_region_audit.py:atom_distribution/predict_all` reconstruye distribuciones desde modelos y featuresCUT/g/Aqua sin refit; las predicciones tabulares por sí solas no contienen laCDF completa requerida para otra reconciliación óptima.

**`g` es grupo de calendario temporal, no región geográfica.** La región real se obtiene de la correspondencia territorialCUT ya definida en21; no reutilizar `g` para dividirBiobío/Ñuble. Fijar cuálCDF/método(E11 ocontrolparent) y cuálmodelo corresponde a cadafold/régimen antes de reconstruir; no escoger el que mejore el score.

## Riesgo, coste y faltantes por propuesta

| Propuesta | Disponible | Falta prefijar / comprobar | Coste estimado de primer artefacto con revisión |
|---|---|---|---|
|A|B porfila, claves54CUT/mes yCDF/modelos congelados|Regiones reales, partición artificial33/21 porhash+semilla/ordenfijo, mismo control ycohorte, reconstrucciónCDF/riesgo/presupuestos|30–45min, sinrefit; estimación de trabajo, no tiempo medido|
|B|RegistroAqua diario/celda y mappingCUT/procedencia en derivados|Operador deconsecutividad, UTC/bordesmes/temporada, máscara/contrato, tratamiento de datos desconocidos, unidad/bloquepermutación ysemilla, protocolo de eventualmodeloSOURCE-only|30–45min para cubo auditado; ajuste/evaluación posteriores requieren otro protocolo, no prometidos dentro de ese plazo|
|C|B/E de18/21/24C ya calculados|Panel/target/contrato yguardrails fijos, mezcla1/2 yninguna selección posterior de proporción|15–25min para postprocesamiento yrevisión; sin refit|

### A — límites del presupuesto construido

Preservar porgrupoΣB hace que los totales por esegrupo coincidan conB porconstrucción: no acredita habilidad regional adicional. Una única partición artificial es control descriptivo, no prueba de aleatorización o evidenciaecológica. Mantener grupos detamaño33/21 no iguala automáticamente intensidad/estacionalidad/geografía. Si sepreregistraA, conservar controlglobal54 y gruposambos, sinselección favorable dehashes/particiones ysinrefit. No se calculó aquí ningún presupuesto.

### B — detección diaria no observabilidad

Una secuencia sin detecciónAqua no prueba ausenciafísica ni oportunidad útil. El indicador debe llamarse persistencia de **detecciones registradas**. No imputarFOV/QA/observación diaria a partir de puntosFIRMS. La agrupación puede distinguir celda frente acomuna y usar fechaUTC; fijar antes de resultados cómo intervienen días aambos lados de límites demes ytemporada.

El placebo debe especificar si permuta el calendario conjuntodeceldas deuna comuna o permuta cada celda porseparado; destruyen relaciones distintas. Bloques temporales y SOURCE/destino deben conservarse conforme al protocolo, sin usar target o futuras etiquetas para escoger permutación. Una semilla única es un escenario diagnóstico, no distribucióninferencial niIC. Incorporar esta información requiere una función nueva o modeloSOURCE-only explícito; no fingir que lasCDF actuales ya usan persistencia.

### C — mezcla no óptimo demostrado

H conserva el presupuesto global compartido deB/E cuando ambos tienen el mismoΣ54, pero no es necesariamente mediana deCDF ni minimizadorL1. No afirmar que sea la esperanza de una mezcla deCDF. Regiones/subgrupos pueden conservar costes aunqueel promedio mejore. Fijarλ=1/2 sin probarproporciones posteriores; conservarB,E,extremos,ceros,sesgo y14/40. No se calculóH en este preflight.

## Cierre provisional

Disponibilidad material confirmada para las tres rutas; no se compararon resultados ni se eligió opción. Esperar33review y consejo35 conlos mismos criterios30/25/20/15/10. Mantenerlímites deproveniencia,distinciónpredicción/observabilidad yningúncambio deproducción. Sin descargas, etiquetasQA33, nuevos documentos o commits por esta tarea.
