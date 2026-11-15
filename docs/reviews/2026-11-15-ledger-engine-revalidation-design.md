# Diseño 28: revalidación ampliada del ledger con motor aislado

**Condición de entrada no cumplida.** Raíz informó que el estudio27 con GEOS3.15 no restauró cuatro de los cinco ejemplos; no se autoriza ejecutar este diseño de upgrade. Se conserva como alternativa condicional descartada por ese antecedente, sin instalación, transformación o revalidación28 ejecutada por este agente. Los controles ampliados descritos siguen siendo requisitos útiles para cualquier diagnóstico futuro con protocolo nuevo; no se transfieren como evidencia de pase.

**Sólo diseño, no autorización de instalación o ejecución.** Depende del experimento 27: la comparación con los mismos cinco pares WKB debe restaurar las identidades/predicados definidos en su protocolo. Si 27 falla, este diseño queda condicional y no se intenta rescatar con precisión, reparación, orden de operandos u otro algoritmo. Pasar cinco ejemplos tampoco acredita el operador completo: 28 es precisamente su prueba ampliada.

## Alcance y pregunta

¿La misma implementación geométrica 24B, sobre los mismos datos y políticas, satisface sus identidades en **ambos casos y ambas prioridades** al ejecutarse con un motor aislado diferente? No pregunta por verdad física, PSF, detección de incendios o equivalencia de oportunidad de observación. No identifica por sí solo el PR o cambio interno responsable. El código 24B original y sus resultados fallidos permanecen intactos y visibles.

La comparación se limita a 2019-01-03 y 2023-02-10, AOI UTM18S 50×50 km, halo15 km, referencias de escaneo, CORE, flags geométricos y regla de transición VIIRS ya fijados. Nada de nuevas fechas, datos, cambios de grilla, `grid_size`, snap, `set_precision`, `buffer(0)`, simplify, reparación o selección por etiquetas. No cambia el modelo mensual, producción o G1.

## Condición de entrada y nuevo presupuesto

Antes de comenzar, raíz debe congelar un protocolo 28 con el resultado revisado de 27, SHA de este diseño/adaptador, rutas, entorno e instante real de inicio. Propuesta: **90 minutos totales desde ese instante, incluida revisión independiente**, con `deadline_UTC=start_UTC+90min` escrito antes del run. No se inicia este reloj durante el diseño. Si hay límite global de sesión más cercano, prevalece el menor y se declara antes de comenzar.

Presupuesto propuesto: cero datos satelitales nuevos; máximo100 MiB de descargas adicionales de dependencias y1 GiB de espacio de build/entorno, como presupuestos separados; máximo200 MiB de artefactos de salida. Preparación/build máximo30 minutos dentro de los90; geometría/verificación40; replay y revisión20. Si un paso excede su límite, entregar `resource_limit` o alcance parcial, sin reiniciar reloj ni elegir subconjuntos favorables. Usar primero fuentes/build de27 y cachés existentes. Una sola combinación nueva: Shapely2.2.0 contra GEOS3.15.0, no un barrido de versiones.

## Entorno aislado y atribución limitada

Crear, sólo si se autoriza, `.runtime/ledger28-env` y un prefijo propio o reutilizar de manera de sólo lectura el prefijo GEOS3.15 de27. Compilar **la misma versión Shapely2.2.0** contra esa biblioteca. No tocar `.venv`, `.runtime/obs-env`, paquetes globales, `uv.lock`, dependencias de aplicación o publicación. Conservar versión/intérprete y NumPy de la ejecución geométrica original siempre que sean compatibles; cualquier desviación se registra antes del run y no se oculta como aislamiento de una única variable.

Fijar hashes de tarballs/wheels y los de GEOS C/C++ y C API realmente cargados, compiladores, flags y logs de build. Una wheel Shapely que cargue su GEOS incluido no cumple la comparación. Registrar `shapely.__version__`, `geos_version_string`, versión C API, rutas de módulos y dependencias dinámicas (`otool -L` en macOS), junto con comprobación en proceso de la versión realmente usada. Congelar lista de paquetes y binarios antes de geometría. No instalar un paquete distinto para hacer pasar un caso.

Aunque cambien los resultados, la conclusión permitida es dependencia de este resultado del motor/entorno, en estos inputs. No atribuir causalmente a PR1499 ni afirmar que se aisló un único cambio interno sólo por comparar releases.

## Adaptador: reutilizar código congelado sin reescribirlo

Proponer un adaptador nuevo, por ejemplo `pipeline/observation_ownership_revalidation.py`, con tests sintéticos propios. Cargar por ruta y verificar byteidéntico el helper original:

`pipeline/observation_ownership_ledger.py` SHA256 `058a60986c28efe3b96fb10dbb2fb872e87b2f460e477c65077f784b515ff2d5`.

El adaptador sólo cambia explícitamente constantes de **runtime** del módulo importado: `OUT`, `TEMP` y `DEADLINE`. Mantener `ROOT`, `GEO`, `PROTOCOL`, fórmulas, funciones, escenarios y código original. `DEADLINE` es el cap nuevo aprobado y real; no se modifica el reloj ni se pretende haber reproducido el run antiguo dentro de su cap vencido. Registrar valores anteriores/nuevos y hash del adaptador en el manifiesto 28.

Rutas nuevas propuestas:

- `OUT=docs/reviews/evidence/observation-ownership-revalidation/attempt-01/`.
- `TEMP=.runtime/observation-ownership-revalidation/attempt-01/`.
- Logs/build en `.runtime/ledger28-build/`; metadatos y hashes pequeños exportados aOUT.

No sobrescribir ninguna salida24B. Rechazar rutas existentes antes de ejecutar. Copiar las referencias GEO previas **byteidénticas**, conservando sus hashes, aTEMP. No invocar `reference_export()` ni `raw_stage()` para evitar abrir otra vez datos originales. Invocar el `geometry_stage()` congelado. Sus hashes internos siguen identificando el helper/protocolo24B; un manifiesto externo28 debe añadir claramente el adaptador, protocolo28, entorno y cap nuevos, sin sustituir esa procedencia por una afirmación falsa de código idéntico de extremo a extremo.

Para verificar geometrías que el helper no exporta, el adaptador puede envolver temporalmente `assign_ownership`: delegar sin alterar argumentos ni retorno y capturar objetos geométricos/índices en memoria. Verificar la secuencia esperada de ocho llamadas (dos casos×dos prioridades×dos instrumentos) y sus hashes de índices. No inyectar otra fórmula, filtrar polígonos o modificar resultados capturados. Congelar y probar este adaptador antes de datos. Los controles ampliados operan sobre esas geometrías capturadas; ningún estado FIRE/QA participa en ellos.

## Entradas y comparación de representación antes de áreas comunes

Fijar hash del manifiesto original24B, su `geometry-stage.json`, índice/NPZ GEO, referencias, helper CORE, reglas de transición y fuentes originales; preservar también el diagnóstico fallido. Comprobar cada NPZ contra su índice y el índice contra su manifiesto previo, como24B. El replay no declara haber revalidado bytes RAW si no los vuelve a abrir: utiliza su cadena de procedencia previa y valida los bytes de las entradas efectivas nuevas (NPZ, referencias y exportaciones de etiquetas).

Antes de comparar áreas comunes:

1. Exactitud de conjunto de índices nativos CORE y estados de geometría por caso/instrumento frente24B. Conservar offsets/crop, filas completas, columnas vecinas e índices de scan/detector. Ningún índice duplicado.
2. Mismos casos, referencias por escaneo y orden temprano/tardío; soporte temporal desconocido retira su unión de toda propiedad identificada. Null no se convierte en0.
3. Comparar `area_full_nominal_m2` y `area_AOI_m2` por mismo índice, y sus sumas/uniones, contra la representación anterior con tolerancia de ingeniería ya fijada de1 m². Publicar diferencias reales; no relajar para conseguir igualdad. Si el cambio de motor altera CORE o representación de forma material, reportar variante del operador y bloquear el replay, sin asumir reparación equivalente.
4. No solapamiento material dentro de scan y de propietarios identificados: suma de áreas frente área de unión dentro de1 m²; partición de propiedad por píxel y unión global, incluyendo soporte de tiempo desconocido, conforme24B. Conservar fallos y geometrías mínimas; no repararlas.

Estos controles de equivalencia usan geometría/índices, nunca si un píxel era positivo. Los tamaños de24B eran4672/40707 filas Aqua/VIIRS para2019 y2674/37398 para2023, por prioridad, incluidos ceros conocidos de halo: el universo completo está acotado y no requiere muestreo de polígonos para este estudio.

## Gate ampliado de áreas comunes, antes de QA

Aplicar a ambos casos, ambos instrumentos y ambas prioridades, sin seleccionar sólo los cinco WKB. Para cada propietario geométrico `P` y unión identificada ajena `Q`, inspeccionar todos los polígonos no vacíos y contabilizar aparte los vacíos conocidos. Publicar recuentos de controles realizados/excluidos/desconocidos; no anunciar validación completa si sólo termina un subconjunto.

- Validez, tipo/dimensión, área finita no negativa y bounds de `P`, `Q`, `I=P∩Q`, `D=P\Q`. Bounds deI no pueden salir del bbox deP/Q; usar la precisión de coordenadas del motor, registrar cualquier discrepancia y resolverla explícitamente, sin añadir un snap.
- `0≤area(I)≤area(P)` y `area(P)=area(I)+area(D)` dentro de1 m². Verificar además identidad de conjuntos `P △ (I∪D)` dentro de1 m² y que los interiores deI/D no se solapen materialmente.
- Coherencia de predicados: si `P.covered_by(Q)`/`Q.covers(P)`, entoncesI debe recuperarP yD ser vacío en área dentro de1 m²; si son disjuntos,I debe tener área0 dentro de tolerancia. Si la relación declara intersección bidimensional de interiores, el resultado no puede ser sólo lineal/vacío. Preservar por separado los casos minúsculos y el residuo real, sin reinterpretar un fallo macroscópico como tolerancia.
- Conmutatividad: comparar ambas órdenes de intersección por diferencia simétrica/área, dentro de1 m²; no escoger el orden favorable por píxel. Los ejemplos fallidos actuales son conmutativos pero incorrectos: este control por sí solo no basta.
- Para cada caso/prioridad, `Σ_i area(P_M(i)∩U_V)=area(U_M∩U_V)=Σ_j area(P_V(j)∩U_M)` dentro de1 m² en cada identidad. Verificar también las uniones de fragmentos comunes por diferencia simétrica contra la intersección de uniones, y su no doble conteo. Registrar residuos firmados de todas las identidades, no sóloun booleano.
- Verificar que áreas comunes no superen las respectivas uniones; uniones/comunes deben permanecer dentro deAOI. No sumar los dos lados como si fueran nueva superficie.

Este gate remedia la omisión de control24B; no cambia el estimando ni la tolerancia. Si falla cualquier identidad obligatoria, dejar la comparación afectada bloqueada. Para la entrega ampliada completa exigir todos los ocho grupos; no presentar un pase parcial como reparación global. Guardar manifiesto de geometría y revisión **antes** de cualquier replay QA. Sin gate completo no se invoca el join ni se emiten nuevas tablas comunes con etiquetas.

## Replay de etiquetas nativas: sólo después del gate

Usar exportaciones24B `.runtime/observation-ownership-ledger/{caso}-{producto}-labels.csv.gz` y `all-positive-originals.csv.gz`, comprobando sus SHA contra el `raw-stage.json` original conservado. No volver a abrir FIRE, consultar sparse FP arrays o cambiar decodificador/screen. Exigir igualdad exacta y unicidad de claves nativas esperadas; si falta una etiqueta, bloquear sin rellenar ni tomar vecino.

Copiar esas exportaciones sin cambios aTEMP28. Crear un **nuevo manifiesto de replay** que enlace explícitamente el raw-stage24B y sus hashes, la geometría nueva y el hecho `raw_read_executed=false`. Si el `join_stage()` congelado requiere un `raw-stage.json` con el hash geométrico nuevo, construir un adaptador de metadatos con ambos enlaces y `replay_only=true`: no modificar el archivo original ni presentarlo como nueva extracción RAW. Mantener las fuentes/shape/InputPointer ya auditadas y su fecha/procedencia original.

El join sigue siendo por instrumento individual e índice nativo, sin pares de clases, concordancia o suma de sensores. Todos los positivos originales permanecen: catálogos granule2019 Aqua60/VIIRS132 y2023 Aqua177/VIIRS908; seis Aqua con centroAOI2023, **cuatro CORE y dos bordes con área null**. No extrapolar esos dos para completar el denominador. M13 no nominal no borra clases7–9; agua/tierra/costa/desconocido, screen y flags son ejes separados. La superficie nominal de un registro positivo no localiza fuego subpíxel.

Verificar retención exacta del catálogo original y sus campos nativos; sólo las áreas geométricas revalidadas pueden variar. Mostrar temprano/tardío sin escoger el más favorable. La auditoría dimensionalVIIRS previa de13 referencias de un mismo scan continúa selectiva; no se transforma en validación de todos los píxeles.

## Artefactos y desenlaces

Entregables28: protocolo/freeze con cap real; manifiestos de código/entorno/binarios/entradas; controles ampliados por caso/instrumento/prioridad; nuevos ledger geométricos o fallo; replay independiente autorizado o razón de no ejecución; catálogo de positivos y estados de borde preservado; revisión independiente. Mantener referencias al manifiesto24B fallido, sin reetiquetarlo como pasado porque una versión nueva funcione.

Desenlaces posibles:27 no restaura los ejemplos→no ejecutar28; preparación excedida→resource_limit; cambia CORE/representación material→no equivalencia demostrada; fallan controles ampliados→ledger sigue bloqueado; pasan todos→operador nominal revalidado para estos dos casos/entorno, con QA replay opcional y revisado. Un pase habilitaría revisar el protocolo25, nunca ejecutarlo implícitamente.

En todos los desenlaces: `gate1_passed=false`, `physical_footprints_verified=false`, `pixel_exposure_times_verified=false`, `scientific_eligibility_certified=false`. SuspectMODIS sigue pendiente y los tiempos son referencias de scan. No conclusión física, causal de incendios o del PR1499; no promoción de modelo o modificación de producción.
