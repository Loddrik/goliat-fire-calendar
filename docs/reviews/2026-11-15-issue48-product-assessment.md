# Issue 48: diagnóstico estacional y contrato de producto

**Recomendación:** responder la solicitud con un diagnóstico explícito de totales julio–junio, una vez verificado el estudio 42, sin convertirlo en una compuerta anual ni habilitar por esa vía barras reconstruidas desde2002. M1, las 14 comunas habilitadas, las bandas y todos los JSON/frontend actuales permanecen intactos en esta evaluación. No se calcularon valores, pérdidas, ajustes o estimaciones nuevos.

Se leyó mediante el conectorGitHub el [issue 48 original](https://github.com/Loddrik/goliat-fire-calendar/issues/48), abierto: “Reconstrucción: el total por temporada no está validado y en algunas comunas se ve un salto en2012-13”. Sus razones entre décadas y cifras aproximadas de error son afirmaciones del autor del issue, no resultados verificados o recalculados aquí. El estudio 42, con productor y revisor separados, debe establecer qué puede reproducirse y con qué contrato antes de que se publiquen cifras nuevas.

## Qué solicita el issue y qué permite responder

La solicitud tiene tres partes: error/sesgo LOSO de los totales por temporada, una divulgación en el método y una lectura sobre el salto en algunas comunas y su habilitación. La motivación de volver a mostrar2002→en la landing no constituye un criterio científico de éxito. Publicar una cifra de error retrospectivo no concede automáticamente permiso para esa visualización.

Las compuertas actuales comparan **errores mensuales** con Aqua sin corregir y climatología en temporadas LOSO. El error de una suma anual depende además de la dirección y compensación de errores mensuales: doce meses con el mismo sesgo lo acumulan; otros pueden compensarlo. Superar una regla mensual no prueba precisión suficiente del total anual ni conserva el ranking de temporadas. Tampoco la banda mensual de error típico es una distribución conjunta de los12 meses: no se obtiene un intervalo anual sumándola, multiplicando su amplitud por12 o por√12 sin un modelo y validación adicionales.

El código de producto confirma esa distinción. [`pipeline/publish.py`](../../pipeline/publish.py) publica `reconstruction_enabled`, `gates`mensuales y `band_mae`; [`pipeline/publish_web.py`](../../pipeline/publish_web.py) deriva `season_totals` por suma, sin que sumar constituya una validación nueva. Los tipos en [`web/src/types.ts`](../../web/src/types.ts) separan `complete`, `state` y `provisional`. La pregunta de landing “¿Qué año tuvo más?” en [`CommuneSample.tsx`](../../web/src/landing/CommuneSample.tsx) filtra temporadas completas **observadas**. Se recomienda conservar ese comportamiento; este documento no modifica ese código.

## Definiciones para42 y para la API futura

Para una comuna c y temporada LOSO s completa de julio a junio:

- `Y_cs=Σ_m Y_csm`: total de celdas-día SNP registradas de los12 meses.
- `P_cs=Σ_m P_csm`: suma de las12 estimaciones M1 obtenidas con el coeficiente del mismofold externo.
- `E_cs=P_cs−Y_cs`: error firmado; negativo significa subestimación frente al producto SNP, no incendios omitidos demostrados.

Exigir12 claves mensuales únicas y completas, sin meses parciales ni nulos rellenados con0. Los ceros registrados válidos siguen siendo0; desconocidos y faltantes son otra condición. Si se usa `bias*n` de `eval_loso.csv` como identidad, sólo equivale aE_cs tras comprobar que bias es la media firmada del mismofold/12 meses. Los controles M1 repetidos por κ no son temporadas adicionales:42 debe seleccionar o deduplicar las copias mediante una identidad explícita, sin promediar discrepancias. Este texto no ejecuta esa comprobación.

El diagnóstico debe conservar la máscara/territorio/publicación de su fuente; no sustituirlo por21máscara6, otro modeloB/G, o el período2020+ porque dé sesgo más cercano a0. El LOSO publicado puede excluir la temporada del **coeficiente** y a la vez usar la máscara aprendida con el desarrollo completo: no se llama validación externa de todo elpipeline. Las14 se seleccionaron con resultados del mismo desarrollo; su diagnóstico es condicionado a esa selección, no una cohorte independiente ni prueba del tramo2002–2011. Véanse [método](../method.md), [auditoría2](2026-11-14-scientific-review-2.md) y [decisión científica consolidada](2026-11-15-final-scientific-decision.md).

Las métricas siguientes no son intercambiables:

| Nombre propuesto | Fórmula sobre temporadas válidas | Unidad y tratamiento de ceros |
|---|---|---|
| `season_total_mae_cell_days` | media de\|E_cs\| | Celdas-día por temporada; incluyeY=0válidos. |
| `season_total_mean_error_cell_days` | media deE_cs | Celdas-día; signoP−Y, no valor absoluto. |
| `season_total_mare_positive_reference` | media de\|E_cs\|/Y_cs, sóloY_cs>0 | Fracción, no porcentaje; cada temporada positiva pesa igual. InformarN. |
| `season_total_mean_relative_error_positive_reference` | media deE_cs/Y_cs, sóloY_cs>0 | Fracción firmada por temporada; distinta del sesgo relativo agregado. |
| `season_total_wape` | Σ\|E_cs\| /ΣY_cs | Fracción; incluye en numerador errores de temporadasY=0. Denominador0→null. |
| `season_total_aggregate_relative_bias` | ΣE_cs /ΣY_cs | Fracción firmada,ponderada por volumen; denominador 0→null. |

EnMARE, temporadas Y=0no tienen error relativo definido: no asignar 0, ∞ o un porcentaje truncado. Informar por separado `n_complete_seasons`, `n_positive_reference_seasons`, `n_zero_reference_seasons`, temporadas faltantes y razones. Los errores absolutos en temporadas de referencia0no desaparecen deMAE/WAPE. No llamar `season_mae_rel` a una mezcla deMARE/WAPE, ni `season_bias_rel` a dos agregaciones diferentes. Mostrar porcentajes en UI sólo multiplicando por100un campo cuyaAPI declare`fraction`.

El resumen de 14debe declarar si esmacro —media o mediana de métricas comunales—, poolCUT-temporada oprimero suma territorial por temporada. Pueden discrepar por pesos, ceros y compensaciones espaciales. No presentar una mediana de porcentajes como error del total regional ni usar el promedio regional para absolver una comuna.

## Propuesta de esquema, separada de las compuertas

Tras42 verificado y revisión de publicación, se recomienda un objeto **nuevo y opcional**, fuera de `gates`, por ejemplo `diagnostics.season_total_loso`. No sobrecargar `reconstruction_enabled`, `band_mae` o `season_compare`. Añadir metadatos de período/esquema y agregado en `index.params` sólo con idénticas definiciones; las métricas comunales pertenecen a `comunas/<cut>.json`.

Esquema ilustrativo **sin cifras calculadas y no escrito a ningúnJSON público**:

```json
{
  "diagnostics": {
    "season_total_loso": {
      "schema_version": 1,
      "status": "pending_verified_publication",
      "method": "M1_origin_fold",
      "target_platform": "SNPP",
      "unit": "registered_daytime_0.01deg_cell_days_per_Jul_Jun_season",
      "season_start_years": [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019],
      "selection_scope": "published14_selected_on_same_development",
      "validation_scope": "retrospective_LOSO_overlap_diagnostic",
      "relative_error_unit": "fraction",
      "signed_error_convention": "prediction_minus_reference",
      "n_complete_seasons": null,
      "n_positive_reference_seasons": null,
      "n_zero_reference_seasons": null,
      "season_total_mae_cell_days": null,
      "season_total_mean_error_cell_days": null,
      "season_total_mare_positive_reference": null,
      "season_total_mean_relative_error_positive_reference": null,
      "season_total_wape": null,
      "season_total_aggregate_relative_bias": null,
      "undefined_reasons": [],
      "mask_contract_id": "must_match_verified_study42",
      "source_manifest_sha256": null,
      "historical_pre2012_validation": false,
      "annual_reconstruction_eligibility_assessed": false,
      "coverage_probability_claim": false
    }
  }
}
```

Los null anteriores son placeholders del diseño, no datos ni una publicación lista. En integración, estado`available`requiere hashes/método y métricas auditadas; un dato indefinido conserva null con causa y denominador. Falta de objeto o estado`unavailable`debe mostrar “diagnóstico no disponible”, no 0 ni “total validado”. LaAPI debe mantener precisión suficiente y redondear únicamente la presentación. La fuente JSON, CSV descargable, UI ytexto del método deben compartir esquema y contrato; los tests posteriores deben comprobar denominador 0,nulos,signo,12 meses,duplicados y no confundir estado observado conestimado.

No se propone un campo `annual_enabled=true`, ni un umbral MARE<20% u otro número elegido por las cifras. Una política de disponibilidad anual necesitaría definir para qué decisión sirve el total, qué pérdida o distorsión de ranking es admisible y validarla antes de convertirla en una compuerta. El diagnóstico 42 describe; no elige esa política por sí mismo.

## Qué podría publicarse después de la revisión

Si42reproduce fuentes, temporada/folds y definiciones, pueden prepararse sus métricas descriptivas y denominadores con provenance, unCSVde temporadas y una divulgación compatible en `docs/method.md`. El texto debería decir que son **errores retrospectivos de totales SNP en el solape LOSO**, condicionados al contrato y selección, sin garantía para2002–2011. “Validado por separado” sin esas precisiones sería excesivo.

Nada deesto autoriza reutilizar la banda mensual como error anual ni mostrar una barra 2002–2011 con una confianza aparente tomada del LOSO2012–2019. La habilitación mensual actual no implica la anual. Mientras no haya decisión de producto y evidencia apropiadas, la landing mantiene sólo temporadas observadas para ranking. En Explorar puede mantenerse el contrato actual estimado y su advertencia, sin elevar la semántica a total anual independiente validado. Cualquier cambio de contenido/serialización exige un PR separado y revisión; no se regenera ahora ningún número oJSONpúblico.

## Respuesta a la pregunta3 del issue

**No es identificable con la comparación entre décadas si el salto de Tirúa,Ñiquén oCañete se debe a sesgo M1 o cambio real.** Antes ydespués cambian los años, plataforma y condiciones; también pueden cambiar actividad, tipos de fuente y procesamiento. Una razón entre promedio observado 2012–2019 ypromedio estimado2002–2011 no es un experimento con el mismo territorio/tiempo observado por ambos sensores.

Si42confirma subestimación consistente durante el solape, eso documentará una limitación de M1 **frente a SNP registrado en esos años** y hará plausible que el método contribuya al salto de presentación. No atribuye causalmente todo el salto, no estima su fracción instrumental, no descarta cambio real yno identifica fuego físico. Las cifras del issue aún requieren la verificación42; no se adoptan aquí como hecho calculado.

¿Deben seguir habilitadas? Elissue no modifica automáticamente las reglas mensuales vigentes: pasan un criterio específico que no evalúa por sí solo uso anual. Se conservan esos indicadores yse explicita la limitación; no se retiran o añaden comunas mediante un umbral nuevo elegido después, pero tampoco se interpreta `reconstruction_enabled` como permiso para ranking anual2002→. Si los resultados fuerzan una decisión sobre el servicio mensual, debe definirse yrevisarse como cambio de política independiente, no ocultarlo detrás de un campo anual.

**Pregunta3 de la interfaz** —“¿Qué año tuvo más?”— puede responder sobre temporadas completas observadas con fecha/plataforma/unidad explícitas, como hace ahora. No debe ordenar conjuntamente años estimados y observados ni adjudicar su diferencia a la actividad real sin el soporte requerido. Un ranking histórico de registros no responde quién encendió el fuego, cuánto ardió o qué causó un cambio.

## Alcance de esta evaluación

Fuentes consultadas: issue 48 por conector GitHub de sólo lectura; código de `publish.py`, `experiment.py`, `publish_web.py` referenciado por elcontrato, tipos yselección observada del componente de landing; método yrevisiones ya existentes. De `eval_loso.csv` sólo se leyó su cabecera para identificar esquema, no valores ni nuevosresultados. No se ejecutófrontend, publicador, agregación estacional, ajuste o consulta NASA/GOES, ni se envió respuesta alissue. No se modificaron código, gates, parámetros, JSON o documentos previamente revisados.42 y su revisión son requisitos previos, no evidencia anticipada en este diseño de producto.
