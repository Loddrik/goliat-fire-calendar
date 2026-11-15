# Estudio36: cubo de adyacencia diaria registrada Aqua

**Resultado: integridad del cubo confirmada por revisión independiente.** Se construyó un predictor y un placebo prefijados; no se leyeron respuestasSNP, calcularon pérdidas, ejecutaron solvers o ajustaron modelos. El resultado no autoriza automáticamente la etapa37.

Protocolo `f6e45cc`, SHA `f12fe4cbebf08e3f9897a50ddd2682ca778524e6be3b62999c9baa69195d55fe`; diseño aplicable SHA `56c902ab443d391047838b87de6795c206788b8ce5bbdf9c0fa28c0c04cbebdf`. Cap absoluto07:48:23–08:33:23UTC del15 de noviembre2026, incluida revisión. Código SHA `12b4fd53f57a9aeb149b5d959d755d1de6616b336b9b5fcb4e2b082ab6ef3993`; freeze SHA `8f778677797ef94bab6a2552fc63f6fe63fa7aa64f1e02846c4523627822f8f7`, emitido antes de calcularD o permutar fechas.

## Checkpoint antes de features

El checkpoint terminó **07:57:21.258922UTC**, antes del límite08:03:23. SHA `c915c5dc2b8fd7f93cb2c6e91fafb3fa0a08ff0c142ad625821d39ee742f9fa3`. Raíz lo comprobó antes de continuar el cubo. Certificó:

- Las5184 claves exactas54CUT×8temporadas×12meses y sus10368 filas duplicadas de control21.
- Recuento Aqua reconstruido idéntico a **cada fila**21, tolerancia0; duplicados de clave con valores contradictorios habrían bloqueado, sin promedio o selección.
- Máscara21 de seis celdas, porSHA y unicidad; no se sustituyó por la máscara223 publicada.
- Incidencias canónicasAqua únicas, fechas/temporada/mes coherentes y asignación celda→CUT única, sin remapear.
-9902 registrosAqua sin máscara dentro del dominio de estudio, exportados como soporte suficiente para auditar.

En ese checkpoint no se habían calculadoD o permutaciones. Las fuentes se congelaron y comprobaron antes/después; no se reconstruyeron adquisiciones originales faltantes ni se cambiaron los datos para obtener igualdad.

## Unidad, calendario y placebo

Una incidencia es una celda canónica0,01° con al menos una detección diurnaAqua registrada en un díaUTC, según el contrato existente. `n_det` se ignora: varias detecciones en el mismo día/celda no forman dos días.

`D_real=1` si una misma celda tiene registros en dos fechasUTC consecutivas, ambas dentro del **mismo mes calendario**. `D_placebo` aplica la misma regla tras la permutación. D0 significa que no existe ese par en el historial registrado disponible, no ausencia física, pasadas útiles u oportunidad observacional0. D1 tampoco identifica persistencia de un mismo incendio: pueden ser fuentes/episodios distintos dentro de la celda.

Se preserva la temporada julio–junio2012–2019, es decirUTC2012-07-01–2020-06-30. Enero–junio usan `year=season+1`; se incluyen29febrero2016/2020. No se aplica timezoneSantiago oDST. No se cuentan pares que crucen mes, año otemporada; la regla vale idénticamente para real/placebo. `Aqua<=1⇒D_real=D_placebo=0` es identidad estructural comprobada.

CadaCUT/YYYYMM tiene su calendario completo de28/29/30/31 columnas, incluidas las de cero registros. Se ordenan días porSHA256UTF8 de `goliat-daily-adjacency-v1|CUT|YYYYMM|DD`, digestbytes ascendente y desempate por día. Para díaORIGENd, el destino es literalmente `rankedDays[d−1]`; no se usa el mapping inverso.

La misma columna diaria completa se mueve para todas las celdas. Se conservaron exactamente conteos mensuales porcelda, multiset de **conjuntos de celdas** por día —incluidos conjuntos vacíos—, distribución de conteos diarios y coocurrencia intradía. Preservar sólo el multiset de cantidades diarias habría sido insuficiente. No se permutan celdas porseparado o sólo días activos. Un único prefijo y una única permutación porCUT/mes, compartidos por los regímenes duplicados; ninguna repetición para forzar diferencia.

## Resultado descriptivo, sin inferencia predictiva

El cubo terminó **07:58:25.296226UTC**. Todos los5184 bloques pasan las identidades. La tabla siguiente sólo describe features construidas sin respuestas:

|D_real|D_placebo|CUT-meses|
|---:|---:|---:|
|0|0|5047|
|1|0|78|
|0|1|32|
|1|1|27|
|Total||5184|

Hay105 mesesD_real=1 y59D_placebo=1; difieren en110. Los192 pares registrados reales y85placebo son un **diagnóstico prefijado**, no otra feature habilitada tras ver los datos. Ni105 frente59 ni192 frente85 prueban ganancia de predicción, causalidad o duración física. La permutación puede conservar o crear adyacencias; no se exige que las destruya y no se cambió la semilla.

`summary.json` conserva todos los grupos de calendario original21 (`g`, incluidoJJA), estratificados porAqua>0, y todos los scopes de régimen. Los grupos son temporales, no regiones ecológicas. No se seleccionó un grupo favorable; integridad no depende de variación, discordancia o prevalencia mínima.

Para evitar confundir soporte futuro de entrenamiento y población de predicción, se publican por separadoSOURCE×ORIGIN ySOURCE/held×DEST. Primer scope —sóloAqua/features, sin ajustes—:

|Régimen|N SOURCE×ORIGIN|D_real=1|D_placebo=1|D distintos|
|---|---:|---:|---:|---:|
|08_forward|1584|26|14|26|
|08_backward|1584|34|25|37|
|16_forward|1008|16|5|19|
|16_backward|1008|29|15|28|

Las tablasDEST completasSOURCE/held están en elJSON, con sus denominadores y desglosesg/Aqua>0. No se usan para decidir variación del futuroSOURCEparent o elegir hiperparámetros. El mismoCUT-mes conserva idénticoD al aparecer en dos regímenes; los regímenes no son réplicas independientes niholdouts nuevos.

## Auditoría y artefactos

Fuentes efectivas únicas: `celldays.parquet` filtrado lógicamenteAqua y columnas de identificación/fecha; máscara6; proyecciónParquet21 **sólo** `regime,cut,season,m,aqua`; código/manifests/protocolo previos. No se solicitaron columnasSNP o sus valores. La lectura del archivo completo paraSHA es verificación de bytes, no lectura semántica de respuestas.

REGIMES se deriva del fragmentoAST literal del código21 congelado, sin importar/ejecutar el módulo de entrenamiento y sin abrir modelosJSON. RolesSOURCE/held siguen su regla de prefijoCUT08/16. No se ejecutan ninguna funciónCDF, solver,fit o loss.

Nueve tests puros cubren misma celda frente a celdas distintas, bisiestos/temporadaUTC, límites de mes/año, cero/una incidencia, duplicados como fallo, direcciónORIGIN→DEST conjunta/calendario vacío, multiset de conjuntos intradía y la posibilidad de que la permutación conserveD. Los helpers/tests no leen `.runtime` oclock; sólo el driver aplica límites.

Se exportaron203984 filas, contando también formatos duplicados y la máscara: soporteAqua,10368features21 sin respuestas,10368identidades mensuales, seis celdas, cubeCSV/Parquet,157788 mappings día completos y5184 controles de bloques. Tamaño físico≈1.05MB, bajo50MiB; picoRSS163139584bytes enmacOS, bajo1GiB. El manifiesto SHA `9169cc2320591a000d72097b76d2207e652bc3141b2f10cc183a3f993272c626` identifica archivos y snapshots. El costo permanece bajo1Mfilas y dentro del cap, sin reinicio.

PyArrow emitió avisos de `sysctlbyname` de cachéCPU denegado por el entorno durante su import. No son datos científicos olecturas de respuestas; los tests y controles de tablas terminaron. No se instalaron dependencias para resolverlos.

Los derivados canónicos están íntegros porhash, pero esto no restaura reproducibilidad completa de adquisición desde losCSV originales faltantes. Columnas vacías describen cero registros **del contrato congelado**, no un denominador de observaciones útiles. No se rellenó información faltante de satélite,QA o cobertura.

Comandos:

```sh
.venv/bin/python -m unittest discover -s tests -p test_daily_adjacency_cube.py
.venv/bin/python pipeline/daily_adjacency_cube.py freeze
.venv/bin/python pipeline/daily_adjacency_cube.py checkpoint
.venv/bin/python pipeline/daily_adjacency_cube.py run
```

El intento no sobrescribe outputs existentes; una reproducción posterior necesita ruta/cap propios documentados, sin eludir el reloj. La evidencia del revisor debe quedar separada del manifiesto del productor.

## Decisión conservada

La revisión de `independent_review_23` pasó sin bloqueantes. Su implementación propia usa bitsets porcelda y conteo de bits de `mask & (mask>>1)`, distinto de la intersección de conjuntos diarios del autor. Reprodujo todas las5184 filas,10368 controlesAqua,9902 registros soporte,157788 mappings de calendario e invariantes de5184 bloques, incluidos conjuntos vacíos, conteos porcelda y scopesSOURCE_ORIGIN/DEST. Repitió los nueve tests y comprobó fuentes/contratos, sin importar el helper del autor o leer respuestas/modelos. Ver dictamen separado `2026-11-15-daily-adjacency-independent-review.md` y su evidencia propia; no modificó los outputs del productor.

Un pase independiente sólo acredita que el predictor y su placebo están construidos como se fijó y que Aqua reproduce21. No demuestra utilidad incremental. Un modelo posterior exige autorización/protocolo separado,60min totales con revisión, SOURCE-only y fallbacksCDF completos ya diseñados. No se ejecutó esa etapa aquí.

`model_fitted=false`, `loss_computed=false`, `response_columns_read=[]`, `stage37_authorized=false` yG1físicofalse.35A negativo y30B fallido no cambian;33 no aportó etiquetasQA históricas. No publicación o producción modificada.
