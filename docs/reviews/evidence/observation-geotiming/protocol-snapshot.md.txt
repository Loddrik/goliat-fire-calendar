# Protocolo técnico: centros geográficos y referencias de escaneo

Fijado antes de ejecutar este análisis. Extiende G0 técnico sin certificar G1 científico. Abrir SOLO MYD03 y VNP03IMG ya adquiridos; ningún producto de fuego, máscara de actividad, concordancia, nuevas descargas ni credenciales. Heredar cuarentena por MYD14Suspect; no reemplazarlo por otro caso.

AOI: cuadrado exacto50×50km enEPSG32718, centroproyectado de(-72.5,-37),±25000m. Seeds Aqua dentro; candidatosVIIRS en cuadrado ampliado500m para evitar sesgo de borde. Coordenadas finitas/rango válido; QAgeográfica conservadora0enambos (políticadeclarada, no equivalencia física). Registrar exclusiones/motivos sin inferir fuegoausente ni cobertura.

Asociar cada centroAqua con un único centroVIIRS más cercano en distanciaeuclídeaUTM≤500m. Empate exacto: menor fila y luego columnaVIIRS. Permitir reutilizaciónVIIRS y reportarla; no tratar asociaciones como muestras independientes. Registrar si centroVIIRS cae fuera delcuadradoprimario. El umbral no se ajusta por cantidades, calidad de concordancia ni desfases.

Validarshape/escaneos: fila//10Aqua, fila//32VIIRS; dimensionesdivisibles ylongitudescompatibles. LeerEVstart/EVcenterAqua yscan_start/scan_end/ev_midVIIRSconatributosyrellenos; conservarTAI93nativo, sinconvertiraUTC. CompararEVcenter−ev_mid yEVstart−scan_start SOLOcomo referenciasdeescaneo; no llamarlotiempoexactodepíxel, intervaloconservadordeexposiciónniempate≤10mincientífico. Tiemposno finitos/relleno/ordeninválidoquedanunknown, no ceros.

Reportar conteos técnicos,distancias ycuantiles[0,.25,.5,.75,1],offsets firmadosyabsolutos, centrosreutilizados,bordes,hashesdeentradas/código/protocolo/entorno. Un resultado0associations es válido; no ampliar umbral después. No porcentajes desuperficie/coberturani normalizaciónporcalidad.

Entornolectura aisladoobs-env; instalarpyproj3.6.1allí si necesario,sinmodificarlocks/global. Código nuevo `pipeline/observation_geotiming.py`, pruebas sintéticaspropias, revisiónyevidencianuevas `docs/reviews/evidence/observation-geotiming/`. Pruebasdesempate,borde,reutilización,geoflags,shapesyrellenos. Salidas explícitasG1false, scientificeligibilityfalse,commonfootprints/timepixpending.
