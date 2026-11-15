# Protocolo27 — diagnóstico aislado del motor de intersección

Fijado después del fallo24B y antes de comparar otra versión del motor. No es una nueva validación física ni rescate de concordancia:25/26 permanecen diseños pendientes.24B se conserva como entrega parcial fallida en additividad común2023.

## Hipótesis y entradas

La implementación produce polígonos válidos con within/covered_by verdaderos pero intersección de área0 y diferencia de área completa. Contrastar la hipótesis de fallo del motorGEOS frente a error en coordenadas/llamadas. Referencia primaria motivadora: [PRGEOS1499](https://github.com/libgeos/geos/pull/1499), incluido en [release3.15.0](https://github.com/libgeos/geos/releases/tag/3.15.0). No se presume que nuestro fallo sea exactamente1499: la conmutatividad observada del resultado incorrecto no reproduce ese síntoma particular.

Inputs: hasta5pares representativos de WKB originales del diagnósticoGEO24B, sin máscaras/QA/labelsFIRE. Selección documentada por contradicción algebraica ya observada, no por actividad o acuerdo. Guardar hashes/IDs nativos/selección yconservar catálogo diagnóstico originalprivado si produjo más pares antes de fijar este límite. Estas entradas son ejemplos de regresión seleccionados, no muestra probabilística ni holdout. Congelarlas antes de ejecutar3.15.

## Comparación y presupuesto

Baseline actual Shapely2.2.0/GEOS3.14.1. ComparadorúnicoGEOS3.15.0oficial, sin probar versiones para escoger favorable. Instalar/compilar únicamente en.runtime/geometry-engine-diagnostic/, sin tocar.venv,uv.lock,bibliotecasglobales,producciónuoutputs24B. Fuente oficialrelease/tag conTLS, metadata/bytes/hashlocalyversiónregistrados; si no hay checksumremoto no afirmar verificaciónNASA/GitHubdechecksum. Hasta20MiB de fuente, presupuestodeingeniería separado deL2cerrado;hasta2procesoscompilación.

Capdiagnóstico:04:50:00Z–05:25:00Z del15nov2026,incluidarevisión. No prolongaB05:29:28Z ni elhorizontegeneral11:30Z. Si acceso/build/ABI no permite completar, entregar estadoinconcluso. No nuevas descargas científicas, APIscredencialesoreadFIRE.

## Contrastes congelados

Sobre mismos WKB/orden/coordenadas, sin snap,grid_size,set_precision,buffer,repair,simplificationoextrapolación, medir en ambos motores:validez/tipo/área deinputs;within/covered_by;área/tipodeintersecciónen ambosórdenes;diferenciaenambosórdenes;unión;identidades |p|=|p∩q|+|p\q| y |p∪q|=|p|+|q|−|p∩q|. Registrar residuo,tolerancia deingeniería1m²yaexistente,sinretocarla. Controles mínimos sintéticos:disjuntos,contenido,solapeparcial,contactoceroárea;comparador debe declarar versión real ymismaWKB.

Unresultado3.15que restauraidentidades enlos5ejemplos sólo respalda una reparación de motor enesoscontraejemplos. No demuestra que1499fueexactamentecausa ni que todo24B quedevalidado. Cualquierreproceso ledger requerirá protocolo/código/inputscongelados, additividadglobalydisjunción/unioncomunes yrevisiónindependiente nuevas, preservando24Boriginal. Si ambos motoresfallan, investigarrepresentación oalgoritmo sinatribuirerroressatélite. Si3.14fallaperocomparadorinaccesible,conservar bugdemostrado yreparaciónpendiente.

## Salidas y decisión

Guardar reporte yWKB acotados en docs/reviews/evidence/geometry-engine-diagnostic/, helperpipeline/geometry_engine_diagnostic.py ytestsproporcionados sólo si hacenfalta para validaradaptador. Primerfreeze registra fuentes/WKB/códigoantes deejecutarcomparador. Rawlibs/buildquedanignorados. Nunca convertir éxito de biblioteca enG1,precisióncientífica,áreaquemada o concordancia de fuego.
