# Protocolo 24B: propiedad geométrica y ledger de retención nominal

Se fija antes de calcular nuevas particiones, retenciones o asociaciones QA de este estudio. Implementa el plan conjunto 24, sin matriz de concordancia ni tabla cruzada de clases MODIS–VIIRS. Inicio del cap: 2026-11-15 04:29:28 UTC; primera entrega, incluyendo revisión, antes de 05:29:28 UTC. Un resultado parcial o soporte no identificado es admisible; no se amplía el cap para rescatarlo.

## Entradas congeladas y dominio

Dos casos existentes: 2019-01-03 y 2023-02-10. Usar los NPZ GEO de la fase B y su índice con SHA verificado contra su manifiesto; helpers CORE y transiciones sin cambios. Usar los ocho originales FIRE/GEO ya adquiridos exclusivamente para referencias de escaneo, etiquetas nativas y QA individual, comprobando sus hashes, shapes e InputPointer. Cero descargas, API o credenciales. No abrir datos de entrenamiento/modelo ni modificar publicación o estudios anteriores.

AOI idéntica: cuadrado de 50×50 km EPSG:32718 centrado en (-72.5,-37). Reconstruir CORE con halo de 15 km, escaneos completos, dos columnas vecinas y mapping nativo exacto, conservando el manejo de saltos VIIRS >1.25/<0.8 preregistrado. No extrapolar bordes, reparar polígonos o reemplazar centros excluidos por vecinos. La validez geométrica conserva su política de flags geográficos; no incorpora máscaras de fuego o calidad atmosférica.

El ledger geométrico contiene todos los polígonos CORE que intersectan la AOI, incluyendo centros exteriores cuya geometría nominal contribuye dentro. Se conservará también la tabla de estados de geometría pendiente. El catálogo de **positivos originales 7–9** retiene cada índice nativo del granule, con pertenencia centro-AOI/halo/exterior/no asignable si su geolocalización lo permite. Las conclusiones de retención se restringen a AOI y halo fijados; los positivos fuera del dominio no se eliminan ni se anuncian como ausentes.

## Separación operacional antes de leer actividad

1. Exportar desde GEO solamente las referencias `EV center time`/`EV start time` MODIS y `ev_mid_time`/`scan_start_time`/`scan_end_time` VIIRS, con atributos/validez por escaneo. No convertirlas en tiempo físico por píxel.
2. Construir y guardar geometría, prioridades y áreas de propiedad por instrumento/caso, junto con hashes de código/inputs/protocolo. Esta etapa no lee máscaras FIRE o QA de fuego.
3. Solo después, exportar etiquetas/QA nativas y positivos originales de cada instrumento. Incorporarlos al ledger usando índices nativos, sin cambiar prioridades ni áreas por esos valores. No combinar clases de ambos sensores en una misma fila ni generar concordancias.

## Propiedad exclusivamente geométrica

Primaria: prioridad del escaneo con referencia temporal válida más temprana; sensibilidad: más tardía. Resolver referencias exactamente empatadas por menor índice nativo de escaneo, sin consultar QA o actividad. Si una referencia no es válida o falta, mantener soporte de ese escaneo como propiedad temporal no identificada, separado; no sustituir tiempo desconocido por cero o una prioridad favorable.

La unión de polígonos de escaneos con referencia desconocida se marca explícitamente como soporte de propiedad no identificada. Se resta esa unión de la propiedad identificable de **todos** los escaneos, incluidos los de tiempo conocido: no puede certificarse un propietario conocido sobre una zona que también cubre un escaneo de orden temporal desconocido. Su área se reporta como incertidumbre de asignación y sus propiedades no identificadas quedan null, no cero.

Cada escaneo aporta su unión de polígonos CORE recortados a la AOI. Para un escaneo en orden de prioridad, restar la unión reclamada por escaneos previos. Cada polígono hereda la parte de su geometría que permanece en esa propiedad de escaneo. Verificar que los polígonos del mismo escaneo no tengan solapamiento de área material: la malla nominal comparte vértices; si falla esta condición, marcar la asignación como no identificada en lugar de elegir etiquetas favorables. La prioridad no se cambia para preservar positivos.

Las diferencias de punto flotante se registran con tolerancia de reconciliación de ingeniería de **1 m²**, por identidad y por AOI; no es una tolerancia NASA o incertidumbre geográfica. Un residuo se conserva como diagnóstico y no se corrigen silenciosamente las geometrías. La suma de áreas y la unión se reportan separadas para no recontar bowtie.

## Identidades del ledger nominal

Por píxel CORE/intersección AOI, registrar índice de caso/producto/fila/columna/escaneo/detector y:

- área del polígono nominal completo, área recortada AOI y parte exterior;
- área propia, parte excluida por prioridad y referencia temporal concreta;
- área propia intersectada con la unión geométrica del otro instrumento, y parte propia sin ese soporte común;
- identidad para tiempo conocido `área_AOI = propiedad_temporal_no_identificada + excluida_por_propiedad_identificada + propia_no_común + propia_común`; para tiempo desconocido, registrar la parte no identificada y dejar las propiedades no identificadas como null.

La unión del otro instrumento no contiene etiquetas para esta operación: solo geometría. No equivale a emparejar estados. Verificar que la intersección nominal no exceda cada unión y que el área total de propiedad reconcilie con su unión geométrica. Conservar cifras para ambas prioridades y sus diferencias; no elegir la sensibilidad porque retenga más detecciones.

Un positivo original sin polígono CORE, fuera del halo o con geometría no asignable conserva su registro y causa. Sus áreas no identificadas son **null**, nunca cero. Un polígono conocido cuya propiedad o intersección común sea vacía sí puede tener área cero, con esa causa explícita. No localizar fuego subpíxel usando la fracción de área retenida.

## Etiquetas y calidad individuales, sin borrar positivos

Conservar máscara original y su semántica por producto. 7–9 son detecciones registradas y permanecen positivas aunque el screen QA conservador las hubiera excluido. 3/5 son no detección registrada sobre agua/tierra bajo ese operador; no son pruebas de ausencia física. Nube, glint, no procesado, desconocido, relleno o clase no reconocida quedan desconocidos con causa, no cero.

Separar ejes: superficie tierra/costa/agua/desconocida; flags geográficos; layout/fill/reservados del algoritmo; calidad de canales VIIRS, incluido M13; bowtie; glint; resultado descriptivo del screen local previamente definido. El screen es una **sensibilidad de calidad**, no un filtro de propiedad ni una operación que borre positivos originales. Informar áreas y positivos afectados por M13 no nominal aparte, sin llamar falsas esas detecciones.

Conservar `Suspect` y explicación global MODIS por separado. No imponer `Passed` como regla NASA inventada; la elegibilidad global del piloto sigue pendiente. Las dimensiones VIIRS contrastadas selectivamente no certifican todos los detectores o regiones de agregación.

## Productos, controles y límites

Exportar ledger por instrumento/caso/prioridad, catálogo completo de positivos originales y sus estados/áreas, geometría pendiente indexada, resúmenes de balances/retención y diferencias temprano/tardío. Tablas de QA o positivos son individuales por instrumento, no crosstabs con el otro. Las áreas comunes nominales se pueden registrar sin clases conjuntas. Las sensibilidades espaciales 75/150 m de B siguen siendo escenarios supuestos; esta primera entrega no recalcula concordancia bajo ellas.

Pruebas sintéticas previas: prioridad independiente de etiquetas; solapamientos y conservación; caso sin solapamiento; recorte AOI y centro exterior; igualdad de unión al invertir prioridad con reasignación de propietarios; positivos de borde sin área ≠ positivos con propiedad vacía; desconocido ≠ no detección; M13 no borra 7–9; mapping de índices; referencias temporales desconocidas y mismo-escaneo con solapamiento material sin reparación.

Antes de ejecutar datos reales, avisar a raíz con protocolo y hashes de código/inputs para congelamiento. No matriz de concordancia, rankings, nuevos parámetros, porcentajes de desacuerdo eliminado o causalidad. Área nominal no es superficie despejada, quemada o una oportunidad física acreditada. `gate1_passed`, `physical_footprints_verified`, `pixel_exposure_times_verified` y `scientific_eligibility_certified` permanecen falsos. Ante incompatibilidad, preservar fallo y alcance parcial, sin cambiar prioridad, caso, halo o semántica.
