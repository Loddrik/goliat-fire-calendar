# Protocolo 20 — brecha entre contratos, sin otro modelo

Fijado antes de medir nuevas cantidades de esta auditoría. Complementa19: allí se cambió plataforma dentro del contrato científico; aquí se audita la definición del conteo. Ningún ajuste, selección, descarga, MAE de modelos ni cambio de publicación.

Dominio fijo: NOAA-20,54comunas,las mismas3780filas/70meses solicitados completos de19. FuenteO:54CSV NOAA20de `observed/dist` ymanifest/seriespublicadas;fuenteC: detections/celldays/cells_comuna/mask223deinvestigación. Both representan deteccionesinstrumentales,noverdadfísica ni oportunidadobservada. Se preservan fechasUTC, day/confidence,type0delcontratoO yventanascomunes; ninguna ausenciadearchivo se rellena.

Antes de comparar, comprobar hashes/tamaños/filas/identidaddecomuna/filtersdeCSVcontra manifest,geometríaDPAhash,yreproducir EXACTAMENTE seriesmensualesO0(todaslasfechasdelos54CSV ocomo mínimopanelcomún). ConfirmarqueOyaasignaporcentrodeceldas, NOporpuntodetección. ReproducirCmaskedexactoconreferenteNN20de19antesdeotrascantidades.

TransformacionesO, registradas antesdelscore:

- O0: conteos cell-day publicados por su cuadrícula y comuna.
- Ogrid: recalcularcuadrícula con regla científica literal floor(lon/.01),floor(lat/.01),manteniendo comunaO. Registrar desacuerdos con gridOoffset18000/9000,especialmentebordes; nodarporhechaidentidaddebidoaredondeos.
- Omask: excluir223celdas deOgrid.
- Omap: reasignar Omask usandocells_comunacientífico congelado. Celdas sinmapping seexcluyendeesta varianteysecuantifican explícitamente; noatribuirsuefecto soloageografía, puesmappingrepresentasoportedeobservacionescientíficasprevias. ReportarmovimientosCUT yexclusiones.

ContrastesdentroC: Cmaskedall de19 y Cmaskedtype0 reconstruidodesdedetections con type==0ANTESdededuplicarcelda-día, mismamáscara/mapa. Medirdíasmezclados0/otro/unknown paraevitarcontardosveces; cambiosporfiltrotiposeránsoloefectomecánicodentroC. Filas typeunknownno se reinterpretancomo0. VerificarreconstrucciónC_all desdedetections sicabenombrecolumns yprovenance; si no encaja abortarcomparacionesantesdecuantificar, noajustarrecetasporresultado.

Cerrar porcomuna-mes exactamente: Cmaskedall−O0=(Ogrid−O0)+(Omask−Ogrid)+(Omap−Omask)+(Cmaskedtype0−Omap)+(Cmaskedall−Cmaskedtype0). Reportartodascolumnasydeltas. ElresidualCtype0−Omap sigue mezclandocohortes/archivos/version/geometría/selecciónprevia; losCSVOprefiltradosno recuperandeteccionesdescartadas. Noesefectoaisladotipo ni geografía, yningún cierre algebraico demuestra causalidad.

Reportar sumas,diferenciasabsolutasporcomuna-mes,mesesidénticos,desglose54/14/40,períodos19; sinrankingmodelosni escoger otroreferente favorable. Completitudsolicitada≠observación,counts0≠ausenciafísica. Protegerhashesbase/publicación/resultadosanteriores, escribirsolo `data/processed/contract_gap_audit/`, pipeline/test/review20nuevos. Pruebassintéticas degridborder,tipoantesdedup, mappingfaltante/movimiento, cierrealgebraico,rechazodeCSV/seriesnocoincidentes. Si seencuentraincompatibilidadirreducible registrar gatefallido ydetener, noforzaridentidad.
