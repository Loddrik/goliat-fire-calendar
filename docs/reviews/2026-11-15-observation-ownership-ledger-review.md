# Estudio 24B: propiedad geométrica y retención de registros originales

**BLOQUEADO por revisión independiente:** el 15 de noviembre antes de cerrar el cap se identificó que, para 2023, la suma de `area_common_m2` de los píxeles no reproduce la intersección de uniones registrada en `geometry-stage.json`. Residuales: Aqua temprano −2,656,776.365 m²; Aqua tardío −7,666,341.290 m²; VIIRS temprano −4,469,738.445 m²; VIIRS tardío −7,175,317.794 m². Superan 1 m². Los controles de suma propia/unión, partición por píxel y common≤owned que siguen descritos **no eran suficientes**. Los outputs originales y sus hashes se preservan sin cambios como intento fallido; ninguna tabla común de 2023 queda validada ni habilita el estudio 25. La conservación del catálogo de positivos y sus índices/estados de borde sigue siendo una auditoría independiente de esa área común. El diagnóstico inicialmente acotado a código/CSV localizó polígonos completos con intersección común cero o casi cero; la causa aún no está confirmada. No se amplía tolerancia, modifica prioridad o supone una reparación geométrica.

Entrega técnica del plan conjunto 24. Protocolo congelado en `4248093`, antes de resultados; cap fijo 04:29:28–05:29:28 UTC del 15 de noviembre de 2026. Se usaron únicamente los dos casos y ocho archivos ya adquiridos. No hubo consultas externas, descargas ni credenciales. No se ejecutó comparación conjunta de clases de fuego.

## Hallazgo y decisión que permite

Es posible eliminar el doble conteo de área nominal entre escaneos mediante una propiedad geométrica reproducible, sin ordenar por actividad o calidad. **Eso no garantiza retener todos los registros positivos en un soporte de comparación.** En la AOI de 2023, Aqua tiene seis positivos originales: cuatro tienen CORE nominal y dos están en bordes de escaneo sin CORE. Los seis permanecen en el catálogo; los dos últimos conservan áreas desconocidas, representadas como campos vacíos/null, nunca cero. No se extrapolaron sus polígonos, sustituyeron por vecinos o localizaron fuegos subpíxel.

El siguiente protocolo tendría que tratar explícitamente este límite de retención antes de comparar estados. Una gran intersección geométrica no convierte en representables los positivos de borde. La ausencia de área identificada de esos registros no equivale a ausencia de actividad ni se resuelve atribuyéndoles la propiedad de otro escaneo.

## Propiedad nominal, por instrumento

Áreas en km² sobre el mismo cuadrado UTM de 50×50 km. La suma de polígonos puede contar dos veces el solapamiento entre escaneos; la unión y la propiedad no lo hacen. Son áreas geométricas nominales, no áreas despejadas, quemadas o físicamente observadas.

| Caso | Instrumento | Suma de áreas AOI | Unión/propiedad identificada | Intersección nominal común |
|---|---|---:|---:|---:|
| 2019-01-03 | Aqua/MODIS | 2098.249421 | 2098.249421 | 2030.811870 |
| 2019-01-03 | SNPP/VIIRS | 2412.819222 | 2412.819222 | 2030.811870 |
| 2023-02-10 | Aqua/MODIS | 2732.019761 | 2500.000000 | 2498.580100 |
| 2023-02-10 | SNPP/VIIRS | 2513.630558 | 2498.580100 | 2498.580100 |

La prioridad primaria usa el escaneo de referencia temporal más temprana; la sensibilidad usa el más tardío, con desempate por índice nativo. Ambas conservan las uniones anteriores. En estos archivos todas las referencias usadas fueron identificadas: la unión con referencia desconocida es cero por datos, sin asumir que los desconocidos valen cero en general. El test sintético de escaneo desconocido exige retirar su soporte de todos los propietarios conocidos. El residuo máximo de partición por píxel fue `2.3283064365386963e-10 m²`, dentro de la tolerancia preregistrada de 1 m². Todas las áreas comunes quedaron dentro de las áreas propias con esa tolerancia.

La tabla geométrica conserva también polígonos de centros en el halo, incluso cuando su intersección AOI es vacía: esos ceros conocidos son diferentes de un área sin polígono. `area_full_nominal_m2 - area_AOI_m2` identifica la parte exterior. `area_time_unidentified_m2`, `area_excluded_by_priority_m2`, `area_owned_not_common_m2` y `area_common_m2` permiten auditar la identidad preregistrada. No se almacenaron pares de clases MODIS–VIIRS.

## Positivos originales y ejes de calidad

Los catálogos contienen todos los registros 7–9 del granule, sin selección positiva para construir la geometría:

| Caso | Instrumento | Positivos originales del granule | Centro dentro AOI | Centro en halo exterior AOI |
|---|---|---:|---:|---:|
| 2019 | Aqua | 60 | 0 | 0 |
| 2019 | SNPP | 132 | 0 | 4 |
| 2023 | Aqua | 177 | 6 | 3 |
| 2023 | SNPP | 908 | 16 | 7 |

Los restantes registros están fuera del halo y permanecen identificados en los catálogos. Los estados de geometría pendiente también se conservan por índice nativo. Fuera del dominio exportado, o sin CORE aceptado en el dominio, las áreas son null. Un estado `nominal_core_polygon` del catálogo de estados, acompañado de área null y alcance exterior, solo indica que la malla pudo construirse en columnas vecinas exportadas: no extiende el dominio analítico al exterior del halo.

En 2023, los cuatro positivos Aqua con CORE y los 16 SNPP con CORE conservan área propia y común no vacía bajo ambas prioridades. Los otros dos Aqua son `geometry_edge_unresolved`. Esto describe retención geométrica de registros; no es superficie física de fuego. No se halló un cambio temprano/tardío en esas áreas positivas identificadas; no demuestra insensibilidad general a la prioridad.

Ocho de los 16 positivos SNPP con centro en AOI tienen M13 no nominal y permanecen como positivos registrados. El screen conservador anterior se exporta únicamente como eje de sensibilidad: no cambia propiedad ni borra clases 7–9. El número no debe confundirse con todos los motivos posibles de exclusión QA. Las clases 3 y 5 mantienen semánticas distintas de no detección registrada sobre agua y tierra; nube, glint, relleno y otras clases desconocidas no se convierten en no detección.

`surface`, `geographic_flag`, `algorithm_QA`, `screen_sensitivity_state`, sus causas y `M13_non_nominal` permiten inspección independiente. `native-axis-summary.json` agrega por separado esos ejes de cada instrumento desde las tablas congeladas; no cruza estados entre instrumentos. Sus sumas son áreas nominales asociadas a etiquetas de píxel, no localización subpíxel. Las etiquetas raw y los flags enteros siguen disponibles para auditar el decodificador, sin inventar una regla universal `QA==0`.

Los dos MYD14 conservan `AutomaticQualityFlag=Suspect` y su explicación en `raw-stage.json`/`summary.json`. La ausencia de atributo global análogo en VIIRS se representa como null, no `Passed`. La elegibilidad científica global sigue pendiente. Las referencias TAI93 solo ordenan escaneos; no acreditan tiempos de exposición por píxel. El contraste dimensional VIIRS previo era selectivo y no se amplía aquí a todos los píxeles.

## Ejecución, reparación y trazabilidad

Nueve tests sintéticos pasaron antes de datos reales: prioridades y conservación, área propia cero frente a desconocida, soporte temporal desconocido, rechazo de solapamiento material dentro del mismo escaneo, vecinos/recorte vacío, independencia de etiquetas, clases desconocidas/agua/tierra, M13 y CSV determinístico. La reconstrucción CORE/mapping de índices reutiliza los helpers previamente probados; no se modificaron sus fórmulas, halo, umbrales o estados.

Freeze inicial de código: `5bcce6dc3277df5372b2c7764eca9e382aac91c7c17504aba222eac836b88ffe`. El primer intento, limitado a referencias GEO, abortó porque el atributo HDF5 `DIMENSION_LIST` contiene objetos `Reference` no serializables. Ocurrió antes de propiedad, outputs de referencias o lectura FIRE. Se restringió el export de atributos de tiempo a `units`, `long_name`, `_FillValue`, `valid_range`. No cambiaron valores de referencia, validez, orden, selección, índices o política. El snapshot inicial se reconstruyó y verificó byteidéntico contra su SHA.

Código reparado congelado **antes** de propiedad/QA: `058a60986c28efe3b96fb10dbb2fb872e87b2f460e477c65077f784b515ff2d5`. Hash del protocolo: `139bf266f38d91df6c263c5513e75079e2ad85f85ee64fbfb69747062a80f116`. `initial-freeze.json` contiene hashes de helpers, índice GEO, fuentes y los ocho raw comprobados; `serialization-fix-freeze.json` enlaza esa cadena. No se descartó un resultado por su valor; fue una reparación de serialización previa a la medición de propiedad.

Los cuatro stages se ejecutaron en orden: referencias GEO, propiedad persistida, raw individual y join por índice nativo. `geometry-stage.json` guarda hashes de todas sus tablas antes de abrir FIRE; el raw-stage valida esos hashes y el join vuelve a comprobarlos. Los archivos NPZ y originales se validan contra sus hashes previos, shapes compatibles e InputPointer; la malla mantiene offsets nativos y las reglas CORE/transición ya congeladas.

Comandos desde el repositorio (requieren archivos ignorados locales):

```sh
.venv/bin/python -m unittest discover -s tests -p test_observation_ownership_ledger.py
DYLD_LIBRARY_PATH="$PWD/.runtime/obs-native/lib" .runtime/obs-env/bin/python pipeline/observation_ownership_ledger.py references
.venv/bin/python pipeline/observation_ownership_ledger.py geometry
DYLD_LIBRARY_PATH="$PWD/.runtime/obs-native/lib" .runtime/obs-env/bin/python pipeline/observation_ownership_ledger.py raw
.venv/bin/python pipeline/observation_ownership_ledger.py join
```

Los stages rechazan sobrescribir referencias/propiedad/raw ya existentes: para una reproducción se deben preservar primero los outputs y usar un checkout/directorio limpio con los mismos inputs. El cap fijo del programa evita ejecutarlo después de 05:29:28 UTC; cualquier reproducción posterior exige documentar expresamente un nuevo cap, sin presentar esa modificación como el código ejecutado originalmente. No se debe cambiar el reloj para eludirlo.

Entornos: geometría/join en `.venv` (Python 3.14, NumPy/Shapely); lectura HDF4/HDF5 en `.runtime/obs-env` (Python 3.10, pyhdf/h5py/pyproj) y la misma biblioteca HDF4 aislada previa. No se instalaron dependencias nuevas. Los CSV se empaquetan gzip determinístico `mtime=0`; campos numéricos vacíos significan null. `manifest.json` incluye hashes físicos y snapshots de código/protocolo/tests. Los resúmenes de ejes son un postprocesamiento transparente de las tablas individuales, sin tocar geometría ni selección.

## Límites de esta entrega

El diagnóstico posterior autorizado reconstruyó únicamente GEO 2023, sin QA o máscaras FIRE, con los mismos helpers/grilla. En Shapely 2.2.0 / GEOS 3.14.1 reprodujo una contradicción entre predicados y overlay: para el propietario VIIRS `(2076,3864)` temprano, ambas geometrías son válidas y `within/covered_by` son verdaderos, pero ambas órdenes de intersección devuelven área cero y la diferencia devuelve prácticamente toda el área del píxel (179084.116595 m²). No se reprodujo no conmutatividad; ambos órdenes fallan igual. Esto localiza un fallo de operación geométrica para ese par, sin identificar todavía la versión/fix que lo resolvería. Cinco pares WKB GEO sin etiquetas y un mini-script se preservan en `diagnostic/`; el JSON de auditoría conserva el gate fallido y su manifiesto separado enlaza el manifiesto original intacto. Cualquier comparación entre versiones GEOS o intento reparado exige protocolo/freeze nuevo; estos resultados originales permanecen fallidos.

`gate1_passed=false`, `physical_footprints_verified=false`, `pixel_exposure_times_verified=false` y `scientific_eligibility_certified=false`. Esta entrega no calcula concordancia, sensibilidad/especificidad, discrepancia eliminada, causalidad o promoción de modelos. No prueba exposición comparable ni resuelve Suspect. La propiedad nominal evita doble área; conservar los positivos originales permite descubrir dónde ese operador excluye información, incluyendo los dos bordes Aqua. Esa auditoría debe preceder a cualquier comparación de clases.
