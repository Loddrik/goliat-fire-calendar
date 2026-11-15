# Protocolo29 — origen fijo y equivalencia numérica certificada

Cap propio de diagnóstico, incluido código/revisión: 2026-11-15T05:04:54.272007+00:00 a 2026-11-15T05:34:54.272007+00:00, sin reinicio.24B ya se conserva fallido; no se extiende su cap ni se reejecuta.27 negó que actualizar GEOS bastara.25/26/28 siguen pendientes/bloqueados.

## Consejo técnico y selección previa

Se conservan criterios24: validez30/información25/factibilidad20/transporte15/interpretación10. Tres miembros prefierenA como siguiente diagnóstico único: ingeniería observacional recomiendaA antesB; estadísticaA81–85,B77–81,C59–71; agente locoA79–83,B73–77,C64–74. Son juicios de diseño en deliberación abierta, no votos cegados ni evidencia empírica. A=traslaciónexacta alorigenAOIfijo;B=operacioneslocalesSTRtree;C=detener/cambiarfuente. No se ejecutanB/otrosorígenes en este estudio. Los dos primeros votos distinguieron independencia de origen y de expresión computacional; el loco advirtió que exactitud de entradas no garantiza redondeo interno estable.

## Hipótesis, entradas y equivalencia antes de overlays

¿Dependen las inconsistencias de la representación con coordenadas absolutas grandes? Misma biblioteca Shapely2.2.0/GEOS3.14.1 delbaseline; no cambiar motor/dependencias. Los mismos5paresWKB y4controles de27, conservando todos incluso el que pasa. Cero FIRE/QA/raw/descargas/modelos.

Único origen permitido: center_xy del índiceGEO previo, igual alcentroAOI de50×50km ya fijado. Leerlo del export-index público previamentehashed, congelar origen exacto/byteshash yAOI; no buscarcentros, escalas,grids,tolerancias o umbrales favorables. Operación única x'=x−cx,y'=y−cy, float64, sin snap/set_precision/buffer/make_valid/simplify/nuevosvértices.

ANTES de overlays traducidos, certificar TODAS coordenadas de ambos operandos, anillos/cierres yAOI (también controles trasladados): Fraction.from_float(x)−Fraction.from_float(cx)==Fraction.from_float(float(x−cx)), análogoY. Verificar que inversión float64 devuelve exactamente los bits de origen y preserva estructura/tipo/dimensión/orden/anillos. Dimensiones no contempladas, NaN/no finitos o cualquier falla de exactitud bloqueanA completo, no excluirfilas. Este certificado comprueba datos reales, sin depender sólo de invocar un teorema. WKB/coordshashesoriginales inmutables ytraducidosnuevos aparte. No convertir coordenadas descartadas en0.

Sólo si todo pasa, comparar operaciones originales ycentradas bajo el mismo motor ylasmismasexpresiones de27:validez/tipo/área,within/covered_by,intersección,diferencias/uniónambosórdenes,identidades yconsistenciapredicado-overlay. Baselineoriginal debe reproducir27 antes de resumircentering. Cuatrocontrolescontraáreasanalíticas; resultados inválidos son fallo aunque áreas cierren. Tolerancia existente1m² sin ampliación;reportar también diferencias/invariancia de áreasdeentrada ytodosresiduos. No cambiar estado semántico de matriz/granule.

## Artefactos, límites y decisiones

Own helperpipeline/coordinate_origin_diagnostic.py,tests proporcionados si necesita validarcertificador, docs/reviews/evidence/coordinate-origin-diagnostic/ yreview29. Congelar código/protocolo/origen/inputs antes de overlays; certificado previo comoartefactoseparado. Hasta5paresreales,4controles,2Mcoordenadas totaltomadasconmultiplicidad y50MiBsalidacomprimida;si excede resource_limit sin aproximación. Ningún ajuste deprecisión implícito; todos los fallosguardados.

Si no equivalencia exacta→cerrarAinconcluso/noaplicable. Si equivalencia pasa pero inconsistencia persiste→cerrarAnegativo, sin buscarorigenalternativo. Si restaura criterios en5ejemplos→evidencia de dependencia numérica del origen enestosregresores, no reparación general ni causaúnica. Revalidación íntegra delledger exigiría protocolonuevo, mismoCORE/worldvertices transformados después deconstrucción antesoverlays, cierres/disjunción/identidades yrevisiónindependiente antesQA/clasesconjuntas. Ningún resultado29habilita25por sísolo ni validaPSF/oportunidadfísica/G1. No se elegirá escenario poragreement.
