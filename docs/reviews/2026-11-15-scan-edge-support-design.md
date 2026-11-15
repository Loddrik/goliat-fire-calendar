# Diseño 26: soporte nominal en bordes de detector dentro del escaneo

Estado: **diseño para congelar antes de implementar o leer clases**. Esta tarea no implementa métodos, no abre raw ni arrays FIRE/GEO, no ejecuta casos y no modifica 24/25. La pregunta es de ingeniería geométrica: ¿puede extenderse la representación nominal a la primera y última fila de detector de cada escaneo, con una regla unilateral explícita y controles que no dependan de actividad? No se busca mejorar MAE, retener un número determinado de detecciones ni aumentar acuerdo entre instrumentos.

**Decisión propuesta:** conservar CORE como referencia inmutable y autorizar, mediante protocolo posterior, una evaluación geométrica de la alternativa A. No incorporar bordes automáticamente. Si los controles fallan o el dominio relevante no queda justificado, adoptar B: conservar bordes como soporte no identificado. Un método puede pasar comprobaciones nominales sin acreditar bordes ópticos, PSF, exposición ni G1.

## Prerrequisito bloqueante: validar el operador base

La dirección informa un fallo de aditividad del área común en GEOS para 2023 en 24B; las áreas propias totales y el catálogo permanecen preservados, mientras se diagnostica GEO de forma aislada. **Resolver y validar el operador base y sus identidades precede a cualquier extensión real de bordes o uso por 25.** No usar áreas nuevas para compensar, ocultar o reinterpretar ese fallo. El resultado de una extensión no puede certificar retrospectivamente un baseline cuya partición no reconcilia.

Este documento y pruebas sintéticas futuras pueden diseñarse sin resolver ese bloqueo; G26.2/G26.3 y cualquier comparación con casos reales quedan bloqueados hasta que exista una versión base corregida, revisada, con identidades/topología validadas y hashes congelados. La corrección del operador base pertenece a su estudio, no se realiza dentro de 26 ni se mezcla con extrapolación. Si cambia su implementación, registrar nueva versión y conservar los artefactos anteriores; comparar extensiones sólo contra esa misma versión validada.

## Dominio y separación respecto de estudios anteriores

CORE excluye la primera y última fila de detector de bloques de diez filas MODIS y 32 VIIRS porque sus vértices no tienen todos los vecinos internos necesarios. Es una decisión de construcción de malla, no una prueba de que esas filas carezcan de observación ni una frontera de respuesta física.

Se mantienen los mismos dos casos, AOI, EPSG:32718, índices nativos, flags geográficos y reglas existentes de transición de agregación. Baseline CORE y resultados 24/25 permanecen intactos. El universo de comparación se divide en `CORE_original`, `edge_candidate`, `edge_rejected` y `other_geometry_unresolved`, con causas; no se llama cero al área que no puede construirse. La geometría nueva no puede desplazar vértices CORE, reparar su topología ni sustituir sus registros por vecinos.

La extensión se prueba en **todos los bordes geométricamente elegibles del dominio fijado**, incluidos centros exteriores cuyos polígonos podrían tocar la AOI. No seleccionar escaneos, detectores, columnas o tolerancias por clases, confianza, FRP o concordancia. La motivación ya conoce exclusiones de positivos: es una investigación adaptativa de ingeniería, no un holdout independiente ni una confirmación preseleccionada de precisión física. Recuperar posteriormente registros positivos mediría retención bajo otra representación, no accuracy.

## Dos alternativas

### A. Ghost centers unilaterales del mismo escaneo

Trabajar con centros proyectados válidos `c[r,j]=(x,y)`, preservando escaneo, detector, fila y columna. Para un bloque de R=10/32 filas, proponer sólo:

- borde inicial: `g[-1,j]=2*c[0,j]−c[1,j]`;
- borde final: `g[R,j]=2*c[R−1,j]−c[R−2,j]`.

Son centros auxiliares sintéticos, no observaciones ni posiciones acreditadas de detectores adicionales. Usar esos ghosts exclusivamente para los vértices que faltan en la frontera exterior. Por ejemplo, el vértice superior entre columnas j y j+1 sería el promedio de `g[-1,j]`, `g[-1,j+1]`, `c[0,j]` y `c[0,j+1]`. El vértice inferior de esa celda sigue siendo el original derivado de filas 0 y 1. La extensión es exacta para una malla afín, no necesariamente para una geometría real curvada.

No extrapolar columnas laterales en este estudio: los extremos de columna sin vecinos laterales suficientes permanecen pendientes. No mezclar escaneos, envolver índices ni usar el escaneo anterior/siguiente aunque sus centros estén cerca por bowtie. No atravesar rellenos, coordenadas inválidas, flags geográficos inadmisibles o saltos/transiciones que el helper previo excluye. El stencil completo debe pertenecer al mismo bloque y región admisible; un fallo se conserva como causa. No introducir ajustes cuadráticos, suavizado o reparación `buffer(0)` si la fórmula congelada falla.

La salida separaría polígono original, nuevo polígono de borde, stencil/ghosts y estado `edge_extrapolated_nominal`. Incluso si pasa los controles siguientes, su error en el borde real permanece no acreditado: la conclusión sería consistencia nominal condicionada al supuesto de regularidad local.

### B. No extender: CORE más borde no identificado

Mantener CORE y el catálogo completo de índices pendientes. Es una salida científica/ingenieril válida cuando A no pase, exceda cap o necesite supuestos adicionales no resueltos. No dar un área nominal cero a los bordes ni estimarla a partir de positivos próximos.

Para MODIS, los rectángulos orientados con ΔS/ΔT de la guía pueden actuar como **control dimensional auxiliar** de A, también en bordes; no se sustituye unilateralmente la malla por esos rectángulos para recuperar registros. Para VIIRS no hay en este diseño una parametrización DFOV/IFOV de todos los píxeles acreditada: no copiar fórmulas MODIS ni usar cuadrados de 375 m. Una eventual alternativa basada en ray tracing o esquinas oficiales necesitaría otro método/protocolo y no se añade como rescate dentro del cap.

## Alternativa oficial de corners: qué está ya documentado

La [nota de soporte nominal](2026-11-14-observation-footprint-design.md) ya revisó los esquemas oficiales [MOD03/MYD03](https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/61/MOD03) y [VNP03IMG](https://ladsweb.modaps.eosdis.nasa.gov/filespec/VIIRS/1/VNP03IMG.fs): documentan centros y navegación; no estableció una matriz de cuatro esquinas por píxel de fuego en los geolocalizadores disponibles. Los offsets MODIS de mayor resolución no son corners de píxeles de fuego de 1 km; GRing/bounds de granule tampoco lo son. El documento VIIRS histórico no acredita por sí mismo todos los detalles C2.

Por tanto **no hay un dataset oficial de corners ya establecido en la evidencia revisada que pueda sustituir ahora A**. No es una afirmación de inexistencia global. No se buscarán nuevos granules, credenciales, LUT o descargas para ampliar esta entrega. Si aparece una referencia documental existente que sí establezca corners, exigir producto/versión, unidad, bandas, índices, georreferencia y significado de los vértices antes de proponer un reemplazo; su carácter oficial no demuestra respuesta óptica equivalente.

## Validación previa a cualquier clase

### 1. Pruebas sintéticas obligatorias

Mallas afines regulares/rotadas/cizalladas: recuperar esquinas conocidas y no mover CORE. Malla suavemente curvada con parámetros fijados: reportar desviación frente a esquinas sintéticas conocidas, incluidos bordes donde la curvatura crece. Ejemplo adversario con curvatura sólo en la frontera: mostrar que los pseudo-bordes interiores pueden pasar aunque el borde real falle; esto delimita el alcance de la extrapolación.

Escaneos superpuestos, orden invertido, IDs discontinuos, separación extrema entre escaneos, relleno en cada posición del stencil y transiciones I-band: verificar que nunca aparece conexión entre bloques o interpolación de datos inválidos. Comprobar detector 0/R−1, R=10/32, columnas sin vecinos, centro exterior con intersección AOI, proyección inválida, polígono invertido o auto-intersectado. La permutación del orden de entrada debe preservar geometría por índice.

### 2. Pseudo-bordes internos con vecinos ocultos

En cada escaneo con geometría interna admisible, tratar sucesivamente cada detector interior `r=1..R−2` como frontera sintética. Para un pseudo-borde inicial ocultar la fila `r−1` y extrapolar desde r/r+1; para uno final ocultar r+1 y extrapolar desde r/r−1. El vecino oculto se usa **únicamente como referencia de evaluación**: el constructor no puede acceder a él. Comparar vértices, lados, orientación y área con la malla interior original de stencil completo.

Usar todas las posiciones admisibles fijadas por geometría, sin adaptar una muestra a errores pequeños; registrar las no evaluables. Separar resultados por instrumento, caso, escaneo, detector, sentido, zona de agregación I-band y posición a lo largo del escaneo. No llamar a estas posiciones réplicas independientes ni extrapolar automáticamente su error a un extremo físico que no tiene vecino de referencia.

Tolerancias de trabajo propuestas para congelamiento: por estrato, P95 del desplazamiento de vértice dividido por el menor lado local ≤0,05 y máximo ≤0,10; P95 del error relativo de área ≤0,05 y máximo ≤0,10. Son criterios de consistencia de ingeniería, **no tolerancias NASA ni IC**. Reportar además todos los errores sin umbral. Si un estrato no tiene referencias admisibles suficientes —mínimo propuesto 20 polígonos de al menos dos escaneos— queda no evaluable, sin combinarlo con otro favorable. Estos números pueden discutirse antes del protocolo; no cambiarse tras medir ni usarse para reabrir gates anteriores.

### 3. Dimensiones nominales y controles de escala

Contrastar MODIS con ΔS(sample), ΔT(sample) y su producto de la [guía C6/C6.1 §8.4.6](https://modis-fire.umd.edu/files/MODIS_C6_C6.1_Fire_User_Guide_1.0.pdf), conservando la convención de índices y el control dimensional ya congelado en el estudio geométrico previo. No recalibrar multiplicadores usando A ni cambiar sus umbrales para los bordes. Separar eje/dirección, área y ángulo; no confundir espaciamiento entre centros con DFOV/IFOV.

En VIIRS, conservar la [tabla I-band y sus límites desde cero](2026-11-15-viirs-nominal-geometry-preflight.md) como diagnóstico nominal de agregación. La consistencia selectiva de dimensiones en unas referencias no certifica todos los bordes. Si sólo está sustentado el muestreo, reportar eso y mantener desconocida la extensión de respuesta del detector; no convertir la validación por pseudo-bordes en validación DFOV.

### 4. Topología, bowtie, halo y proyección

Polígonos simples, área positiva, centro dentro o sobre borde dentro de tolerancia numérica y vértices compartidos donde corresponda. Sin reparaciones silenciosas. Superposición entre escaneos es admisible y se mide mediante suma frente a unión; no forzar teselación global ni reducirla usando vecinos de otro bloque. Un solapamiento material dentro del mismo escaneo invalida la partición afectada, sin prioridad basada en actividad.

Mantener halo baseline de 15 km y evaluar una sensibilidad geométrica predeclarada de 30 km usando sólo GEO ya disponible, sin descargas. Si la caché existente no permite comprobar el halo mayor o no hay cota defendible de la máxima extensión nominal, marcar borde AOI no resuelto. La estabilidad observada de dos halos no demuestra por sí sola una cota global de soporte. Comparar el recorte AOI, no sólo el conjunto de centros interiores. Conservar el umbral numérico de reconciliación de 1 m² del ledger: no convertirlo en error geográfico.

Comparar áreas UTM y áreas geodésicas sobre los mismos vértices, separando distorsión de proyección de discrepancia instrumental. Tolerancia propuesta antes de datos: diferencia relativa de área ≤0,01; si falla, detener interpretación métrica y revisar el cálculo sin cambiar de proyección según concordancia. No promediar longitudes/latitudes en grados para construir ghosts.

## Gates, artefacto y caps de un eventual estudio 26

**G26.0 — contrato:** operador base e identidades de partición/topología revisados y validados antes de cualquier geometría real; hashes de protocolo, código, cachés GEO autorizadas y helpers; separación verificable de clases; dominios, umbrales y caps congelados. El constructor no importa FIRE, FRP, confianza ni tablas de positivos. Sin esto no se ejecutan geometrías reales.

**G26.1 — sintético:** pasan invariantes, bloqueos de cross-scan/fill y pruebas adversarias; el ejemplo de fallo de extrapolación se conserva como limitación, no se elimina para declarar éxito.

**G26.2 — consistencia nominal local:** pasan pseudo-bordes, topología y control dimensional en el dominio declarado. Cualquier estrato no evaluable o fallido permanece identificado en el ledger y no se omite del denominador de evaluación. Una pasada global no se obtiene promediando estratos fallidos. Si no se sostiene al menos un dominio de bordes explícito para ambos casos, el resultado primario es B; pueden conservarse diagnósticos por estrato sin declarar extensión general.

**G26.3 — alcance espacial:** halo y proyección son suficientes para la conclusión AOI declarada o se conserva esa parte como no identificada. Aceptación condicional no acredita PSF ni exposición física.

Primer artefacto futuro ≤60 minutos, **incluida revisión**: módulo geométrico puro, pruebas sintéticas y manifiesto de stencils/contrato; si no cabe, detener. Un segundo cap independiente ≤60 minutos sólo después de resolver el bloqueo del operador base, y con autorización y protocolo para GEO existente: tablas de pseudo-bordes y dimensiones, comparación CORE/CORE+borde por áreas/uniones/causas y ejemplos geométricos fijados por índice, sin clases. Máximo propuesto 200.000 polígonos candidatos por caso/instrumento y dos halos fijados; al exceder memoria/tiempo/cantidad, preservar un resultado parcial explícito, sin seleccionar filas convenientes ni ampliar caps para lograr aceptación. Cero descargas, credenciales, fits y modificaciones productivas.

No calcular matrices de concordancia ni decidir propiedad nueva usando etiquetas en estos caps. Cualquier unión/propiedad posterior conserva las prioridades ya congeladas de escaneo temprano/tardío y hace una comparación equivalente sobre CORE original; no transfiere los tiempos de antiguos pares de centros a nuevos soportes. Que un borde gane geometría puede cambiar exclusiones por propiedad: esa reasignación exige ledger antes de interpretar retención.

## Bifurcación final y límites

Si A pasa, reportar **representación nominal extrapolada con controles de consistencia y dominio explícito**, junto a CORE, áreas añadidas/excluidas y sensibilidad; no reemplazar el baseline ni certificar todos los píxeles. Si falla, resulta no evaluable o el halo/nominal no se justifica, mantener B. El resultado puede ser «no se justifica extender». No alternar métodos o tolerancias para recuperar positivos concretos.

PSF/IFOV/DFOV, posición geográfica y exposición temporal siguen siendo incertidumbres distintas. Los ghosts no crean mediciones ni tiempos; 10/32 filas identifican estructura de detector, no una exposición simultánea. No se declara que una fracción de área nominal retenida contenga la misma fracción de fuego subpíxel. Los indicadores físicos y G1 permanecen falsos, aun si todos los gates de ingeniería son favorables.
