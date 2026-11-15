# Protocolo30B — revalidación geométrica completa en offsets locales exactos

**Protocolo congelado antes de nuevas operaciones reales de30B.** 24B original permanece fallido;29 sólo mostró restauración de controles locales en cinco ejemplos seleccionados. El presente estudio amplía los controles a toda la representación de ambos casos y añade una expresión computacional por pares. El cap empieza en el instante explícito fijado al congelarlo.

## Pregunta, estimando y cap que se fijará antes de comenzar

¿La misma representación CORE mundial de24B, expresada mediante una traslación exacta al origen AOI fijo antes de operaciones de conjuntos, satisface sus identidades globales y controles por propietarios individuales? El objeto es un **operador geométrico nominal** sobre dos casos, no un footprint físico, superficie despejada, incendio o estimación causal.

Casos únicos2019-01-03 y2023-02-10; misma AOI50×50km, halo15km, scans/crops/columnas vecinas, flags geométricos, transicionesVIIRS, referencias temporales y prioridades conjuntas temprano/temprano y tardío/tardío. No desplazamientos, ampliación de muestra, nueva grilla, cambio de origen, ajuste de precisión o alternativa favorable si un método falla.

Cap real fijado: inicio `2026-11-15T05:24:38.114629+00:00`, final `2026-11-15T06:54:38.114629+00:00`, **incluida revisión independiente**. Se guarda en `.runtime/study30-cap.json` y su snapshot público antes de ejecutar; no modifica los caps históricos. Prevalece cualquier límite global más cercano declarado antes de comenzar. Propuesta de distribución:20min implementación/tests/freeze;45min geometría/control de todas las expresiones;10min replay opcional;15min revisión. No reiniciar el reloj por errores, comparaciones parciales o instalación. No se instalan dependencias: misma Shapely2.2.0/GEOS3.14.1 comprobada en29.

Límites duros:250000 componentes-atómo de área positiva por caso/prioridad;2M átomos totales;5M pares candidatos geométricos totales y200MiB de salida física total. Contar candidatos de controles intra-instrumento y cross-instrumento; un par nativo se procesa una vez por control/escenario, sin duplicarlo por orden. Contactos de área0 tienen contador aparte, no se transforman en átomos positivos. Exceso→`resource_limit`, sin simplificar geometrías, muestrear candidatos, descartar fragmentos minúsculos o ampliar el cap para rescatarlo.

## Fuentes, congelamiento y conservación del intento previo

Implementación nueva propuesta: `pipeline/centered_observation_ledger.py`, con tests propios. No editar el helper24B SHA `058a60986c28efe3b96fb10dbb2fb872e87b2f460e477c65077f784b515ff2d5`, sus snapshots,24B/27/29 o sus manifiestos. El nuevo método y su diferencia de frame deben figurar explícitamente en código/procedencia; no presentarlo como ejecución byteidéntica24B ni usar su deadline vencido.

Entradas efectivas: NPZ GEO/índice previos, referencias GEO ya exportadas y helpers congelados de construcción CORE/transiciones/propiedad. Comprobar todos sus hashes contra los manifiestos anteriores; preservar el mapping nativo completo. Fuente del origen: `docs/reviews/evidence/observation-mesh-validation/export-index.json`, SHA `6cbcf6b06506c22330045119378639eca3f392b8125a72d36fb350dab4421cfb`, `center_xy=[722459.8026976171,5902205.764776958]` EPSG:32718. Registrar valoresfloathex/bytes, hash del origen/AOI, código/helper, binarios GEOS/Shapely y cap antes de nuevas operaciones reales.

OUT nuevo propuesto `docs/reviews/evidence/centered-observation-ledger/attempt-01/`; TEMP nuevo `.runtime/centered-observation-ledger/attempt-01/`. Rechazar rutas existentes. Ninguna sobrescritura de24B; no alterar el reloj ni sus constantes para fingir una ejecución original. Fuente24B y cadena de datos raw se citan como procedencia previa; el estudio nuevo no vuelve a abrir FIRE/GEO raw, ni afirma una validación nueva de esos bytes si sólo utiliza sus exportaciones verificadas.

## Orden obligatorio: mundo CORE → certificado → operaciones locales

1. Construir los **mismos vértices CORE en coordenadas mundiales**, utilizando los NPZ originales y helpers sin modificaciones. Conservar fórmula/orden de sumas, detección de transiciones y estados. La construcción/validación de un cuadrilátero y su prueba de cobertura del centro del helper son parte de esa representación previa; todavía no realizar `intersection`, `difference`, `union`, clipAOI u otro overlay mundial.
2. Guardar hashes por índices/vertices, estados y área del polígono nominal completo mundial. Aplicar los mismos límites de crop/halo por coordenadas/índices, sin nuevo recorte geométrico ni omitir centros exteriores cuyos polígonos contribuyan aAOI.
3. Certificar **todos los vértices mundiales construidos**, incluidos componentes/anillos/cierres, AOI y cualquier punto adicional que se traduzca, antes de cualquier operación de conjuntos. Incluir también geometrías construidas de columnas vecinas/halo aunque luego no contribuyan; no certificar solamente los seleccionados porAOI. Límite2M tuplas con multiplicidad de las entradas realmente construidas; reutilizar el certificado del mismo input en las dos prioridades no cambia sus bits ni agrega input nuevo. Un estado sin CORE no recibe vértices inventados para completar el certificado.
4. Traslación única float64 `x_local=x_world−cx`, `y_local=y_world−cy`. Comprobar cada resta mediante `Fraction.from_float`, inversión bitidéntica y preservación de tipo/dimensión2D/componentes/anillos/orden/cierres. No finitos, dimensiones adicionales, resta no exacta, cambio de estructura o exceso→bloqueo completo, no exclusión favorable de filas. No confiar únicamente en el teorema deSterbenz.
5. Persistir certificado, geometrías locales y hashes; avisar de ese freeze intermedio antes de overlays. Sólo entonces ejecutar TODOS clips/uniones/diferencias/intersecciones/propiedad en coordenadas locales. No construir la malla a partir de centros ya trasladados: eso cambiaría el redondeo de la fórmula de vértices. No hacer overlay de resultados devueltos a coordenadas mundiales.

Geometrías canónicas del resultado: **offsets locales en metros**, con `coordinate_frame=local_offsets`, `parent_crs=EPSG:32718`, `origin_xy`/floathex/hash explícitos. Un WKB local no se etiqueta engañosamente como coordenadas EPSG:32718 absolutas. Cualquier reconstrucción mundial para inspección visual sería exportación aparte, sin operaciones métricas ni uso para los gates de este run.

## GateA: misma representación y propiedad identificada

Antes de cualquier etiquetaQA/FIRE, exigir ambos casos y ambas prioridades completos:

- Conjuntos y unicidad de IDs nativos CORE/estados de geometría exactos frente24B; preservar filas/columnas/scan/detector, dimensiones de inputs/crop y causas de ausencia. Sin sustitución por vecino o extrapolación.
- Hash de vértices mundiales reconstruidos fijado antes de transformar; coordenadas de la representación original preservadas por el certificado. Comparar áreas nominales completas mundiales por índice contra24B, y áreas locales antes de clip: diferencias reales publicadas, tolerancia de ingeniería1m² por identidad, sin ajuste. Si cambia CORE o área material, detener como representación no equivalente.
- Orden exclusivamente geométrico por referencia nativa de scan válida: temprano primario/tardío sensibilidad, empate por menor scan. Tiempo desconocido conserva su unión como propiedad no identificada y la retira de TODOS los propietarios conocidos. Campos no identificados null, nunca0.
- Validez, finitud y no negatividad de todos los resultados de operaciones, también intermedios. Vacío conocido se distingue de geometría no identificada; bounds vacíos null con causa. No `buffer(0)`, `make_valid`, snap, `grid_size`, cambio de precisión, reparación o reparto de residuos.
- No solapamiento material dentro de scan y entre propietarios del mismo instrumento: suma de áreas/área de unión y verificación de pares candidatos porSTRtree; interiores compartidos totales≤1m². Separar contactos lineales/puntuales de área0. Conservar índices de todos los pares inspeccionados.
- Cierre de propiedad por píxel y por unión, incluidas partes desconocidas, excluidas, propias y exterioresAOI. Uniones dentro deAOI; suma de áreas propias coincide con su unión dentro de1m². La suma nativa antes de propiedad se reporta aparte para mostrar bowtie.

Controles por operación usados efectivamente: geometrías válidas y finitas, tipos/dimensiones/bounds registrados; intersección contenida en bounds de ambos operandos y de área≤cadaoperando; diferencias dentro del operando izquierdo; uniones dentro del bbox conjunto. Coherencia de predicados de contención/disjunción frente al overlay. Identidades de complemento, ambas órdenes de intersección/unión y diferencias correspondientes con tolerancia1m² donde se comparan áreas/conjuntos. Los bounds usan las coordenadas calculadas, sin corregirlas para pasar. Reportar contradicciones y residuos, no sólo booleanos.

## GateB: común por uniones Y control por todos los pares propietarios

Definir `UM`/`UV` como uniones de **propiedad identificada** local, no suma de píxeles ni unión geométrica con orden desconocido. El soporte común es `C=UM∩UV`. Esta definición no hereda sin reconciliación el campo común24B. Separar explícitamente diferencia con su denominador previo y soporte de propiedad temporal desconocida.

Expresión1, por unión ajena: para cada propietario `PM(i)` obtener `IM(i)=PM(i)∩UV` y el análogo `IV(j)=PV(j)∩UM`. Comprobar exhaustivamente validez/tipo/bounds/predicados y complementos. Exigir:

`Σarea(IM)=area(C)=Σarea(IV)` dentro de1m² en cada identidad; las uniones de fragmentos comunes deben reproducirC por diferencia simétrica≤1m² y sin doble área. Comprobar también `C` en ambos órdenes. El resultado29 que ya pasaba con intersección casi nula muestra por qué controles locales sin este cierre global no bastan.

Expresión2, por propietarios individuales: construirSTRtree de TODOS los propietarios nativos identificados de un instrumento y consultar TODOS los candidatos bbox del otro. No filtrar por centros, cercanía, máscara oQA, ni rescatar un par ausente por vecindad. Intersectar cada par candidato y conservar todas sus componentes de área positiva como átomos con ambos IDs; conservar contactos0 aparte. Este es control independiente de la **expresión computacional megaunión**, no una segunda biblioteca ni verdad externa.

Exigir que suma de áreas de átomos, área de su unión yarea(C) reconcilien dentro de1m²; su unión reproduceC por diferencia simétrica≤1m². Verificar disjunción de interiores de átomos con todos los candidatos geométricos relevantes; suma de áreas solapadas≤1m², con residuos registrados. Las sumas por ID izquierdo/derecho deben reproducir las respectivas áreasIM/IV deExpresión1 dentro de1m². Casos/prioridades y candidatos fallidos se preservan; no elegir la expresión que arroje más soporte o retenga más positivos.

Ambas expresiones son obligatorias. Si falla una, si no termina toda la población, si una operación es inválida/no finita o se excede un límite, el operador afectado queda bloqueado y el pase completo30B no se acredita. No promediar residuos ni compensar fallos de un caso con otro. Gates en ocho grupos (dos casos×dos instrumentos×dos prioridades) y cuatro overlay cross-instrumento (dos casos×dos prioridades), con sus identidades explícitas. Congelar resultados geométricos y solicitar revisión independiente **antes** del replay.

## Papel de30A y pruebas sintéticas

30A desarrolla testigos exactos/cotas de solapamiento para los cinco WKB, independientes deGEOS. Su evidencia no sustituye30B: pocos ejemplos no validan todos los propietarios; del mismo modo, identidadesGEOS consistentes no sustituyen un testigo independiente. Documentar30A y cualquier contradicción antes de interpretar30B; no descartar el testigo que resulte incómodo. Raíz coordina orden/freeze sin ejecución implícita por este documento.

Antes de reales: tests de mundoCORE→local frente a construirlocal(no intercambiables); igualdad de vértices/índices; Fraction/cero firmado/anillos; desconocido temporal que bloquea propietarios conocidos; mismo-scan y cross-scan; clipAOI con centros exteriores; sumas≠uniones; bidireccionalidad/complementos/bounds;STRtree exhaustivo con candidatos de sólo contacto, partición, agujeros, multipolígonos y fragmentos pequeños; cierres por ID/átomo/unión; fallo obligatorio si cualquiera de las dos expresiones falla. Incluir los WKB29 como regresión técnica, sin optimizar por sus resultados.

## Replay individual opcional, exclusivamente después de TODOS los gates

Sin pase geométrico completo, **no leer exportaciones de máscara/QA nativa ni ejecutar joins**. No se abren FIRE raw en ningún momento de30B. Tras pase y revisión, se puede autorizar replay de columnas nativas24B verificadas por SHA e índice exacto, sin modificar campos nativos, decodificador, screen o catálogos originales. Nueva procedencia debe decir `raw_read_executed=false`, `replay_only=true`, enlazar raw-stage24B y geometría30B; no alterar el original para fingir una nueva extracción.

Los positivos originales se preservan incluso sin propiedad o con área desconocida. Aqua2023 tiene seis registros centroAOI: cuatro CORE y **dos bordes sinCORE con áreas null**; no reconstruirlos para rescatar retención. M13 no nominal no borra7–9; agua/tierra/costa/desconocido yQA son ejes separados. Los13 contrastes dimensionalesVIIRS anteriores siguen selectivos, no validación de todos los píxeles. No sumar sensores ni producir una tabla conjunta de clases, concordancia, falsas detecciones o resultado del modelo.

## Artefactos, fallos y alcance final

Entregar código/tests/protocolo/cap y freeze; origen/frame y entorno/binaryhash; hashes de vértices mundiales y certificado exacto; geometrías locales identificadas; ledger de soporte/propiedad; controles exhaustivos y átomos geométricos sin etiquetas; candidatos/recursos/reconciliaciones; replay opcional separado y revisión. Empaquetado determinístico si procede, preservando bytes/hash lógico y sin modificar geometría para reducir tamaño. Guardar negativos, límites e intentos parciales, con código ejecutado identificado.

Un pase sólo acreditaría consistencia del operador nominal sobre esos inputs/entorno y ambas expresiones. No reescribe24B como pasado ni elimina su fallo, no prueba PSF/oportunidad física o causalidad interna deGEOS, y no autoriza25 automáticamente. `gate1_passed=false`, `physical_footprints_verified=false`, `pixel_exposure_times_verified=false`, `scientific_eligibility_certified=false`. GlobalSuspectMODIS y tiempos de exposición siguen pendientes. Sin modelos, nuevas descargas o cambios de producción.

30A se congela por separado bajo el mismo inicio y cap propio15min; su prueba exacta no sustituye30B. Helpers matemáticos puros/tests no deben depender de archivos.runtime o reloj del run; los drivers aplican presupuesto real yrechazan sobreescribir evidencia.
