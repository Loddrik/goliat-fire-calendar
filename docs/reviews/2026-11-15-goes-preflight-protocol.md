# Protocolo40 — preflight documental de contexto temporal GOES16

Nueva decisión explícita de raíz, ratificada por los seis miembros38 tras verificar A39 terminado y revisado a08:57:35.997463UTC. Amplía la condición anterior de sustitución sólo tras parada temprana a **finalización completa temprana**: el motivo es tiempo/capacidad realmente liberados, independiente del signoCRPS. No modifica protocolo, métricas o resultados39 ni rescata35/37.

Cap absoluto **2026-11-15T09:15:00Z–10:00:00Z**,45minTOTAL incluidos protocolo, fuentes y revisión. Productor observación y revisor medición dedicados, distintos y sin doble asignaciónA. Raíz consolida en paralelo. D mantiene **10:13–11:13UTC**,60min con últimos30 de cierre real;11:13–11:30 sólo contingencia/entrega. Si falta prueba documental o revisión alcap, declarar desconocido/inconcluso sin extensión.

## Pregunta y casos cerrados

¿La documentación y los metadatos de **GOES16 ABI-L2-FDCF** permiten definir un futuro operador grueso repetido que aporte contexto temporal a los dos casos polares ya fijados? Es factibilidad de otra fuente, no validación de conteos mensuales, selección de modelo o adjudicación física de píxeles375m.

Casos fijos2019-01-03 y2023-02-10. AOI50×50km,EPSG32718, centro(longitud−72.5,latitud−37). Ventanas de archivos polares aproximadas:2019UTC18:36–18:45;2023UTC18:30–18:36. No son instantes de exposición porpíxel. No cambiarfecha/AOI porque un producto muestre una señal favorable; no se consultarán señales científicas aquí.

## Fuentes y prohibiciones

Únicamente documentación primaria oficial NOAA/GOES-R,filespec/ATBD/PUG y metadatos de colección/catálogo o listados públicos de objetos. Un S3LIST puede acreditar nombres/intervalos declarados y existencia de catálogo, no lectura efectiva de variable/descarga científica. RegistrarURL, título, versión/fecha, accesoUTC, aplicabilidad actual/histórica y qué punto apoya o no. Hasta12documentos primarios y8URLs de catálogo/listado explícitamente seleccionados; no rastreo indiscriminado.

**Cero bytes de datos científicos adquiridos.** No abrir/descargar .nc, HDF, radiancias, máscaras, productos de fuego, headers/ranges científicos, tiles o productos de imagen; no autenticar, usar claves/tokens, aceptar acuerdos, registrarse, contactar personas o enviar solicitudes. Figuras ilustrativas dentro de documentación técnica se tratan como documentación, sin extraer mediciones ni usarlas como evidencia del caso. No reabrir el presupuestoL2 cerrado ni habilitar futuras adquisiciones. No nuevasfeatures/modelos/fits/solvers/scores.

## Contrato que debe poder definirse

1. Modo y cadencia **históricos** aplicables a2019/2023 y aFDCFfullDisk; no transferir automáticamente modos actuales ni usar CONUS/meso fuera delAOI. Distinguirstart/end/nombre de archivo y referencia temporal de exposición física exacta enROI.
2. Proyección/coordenadas/nav y resolución nominal, efectos de posición/visión pertinentes alAOI. Documentación de grilla no certifica PSF/footprint óptico o geolocalización real delgranule. Atributos científicos no inspeccionados quedan sin verificar.
3. Semántica Mask/DQF/fill/confianza/nubes/no procesado y su versión; sólo códigos definidos en fuente primaria aplicable. No inferir que valor0 significa ausencia física o buena observación, ni que clase positiva equivale a incendio único. Incompatibilidad/no prueba de aplicabilidad histórica→unknown.
4. Acceso y formato por catálogo/listado para las dos fechas fijas, si verificable sin datos. Registrar límites del acceso probado; ausencia en un listado o falloHTTP no prueban inexistencia global. No seguir un enlace científico para completar metadata.
5. Qué contraste temporal **grueso** podría apoyar esa fuente y qué no. Repeticiones positivas no prueban continuidad del mismo incendio; ausencia gruesa no refuta un foco375m; compartir respuesta térmica o algoritmos no garantiza independencia de errores/verdad física. Cadencia documental no identifica oportunidades físicas comparables entre MODIS/VIIRS.

## Artefactos y desenlaces

Productor conserva scope/cap, fuentes/URLs/versiones y matriz conocido/desconocido por requisito/caso, registro de consultas permitidas y contador0deacquisición/fits/solvers. Puede guardar extractos breves o referencias y metadatos no científicos porhash; no una biblioteca externa de datos. Revisión independiente verifica fuentes primarias y límites, con evidencia separada; originales del repositorio/modelos21/cubo36/resultados37/39 intactos.

- **Viabilidad documental condicionada:** existe un operador potencial bien delimitado; cualquier ciencia futura necesita nueva decisión, presupuesto, versión/granules/geometría y validación explícitos. No esGOpara adquirir automáticamente.
- **Negativo:** resolución/tiempo/estados no distinguen la pregunta; cerrar esa ruta paraese fin sin elegir otrafecha.
- **Inconcluso:** documentación/versionado/acceso insuficientes; declarar qué falta, sin inventar equivalencia o llamar no-detección aunknown.

La decisión posterior puede recomendar sólo contexto de señales grandes, o ninguna adquisición. Ningún resultado acreditaG1,PSF,tiempospíxel,verdadfísica o factor de armonización. No altera las primarias23/35/37/39, los14gates, M1 ni producción.
