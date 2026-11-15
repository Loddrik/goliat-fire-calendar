# Estudio30B: revalidación del operador nominal en offsets locales exactos

**Resultado negativo/parcial: fallo de gate geométrico, sin replay QA.** El run terminó05:40:50.932280Z con `Interior predicate vs intersection dimension` en el control de disjunción de propietarios2023/Aqua/temprano. El intento24B original permanece fallido. No se cambió origen, tolerancia, fórmula, política o código para rescatar30B.

Ambos cruces2019 temprano/tardío completaron las dos expresiones y controles;2023 no completó su control de propietarios ni produjo comparación común. `all_geometry_gates_passed=false`, aunque existan salidas parciales correctas de2019. Se conservan `failure-run.json`, los últimos operandosWKB locales y el contexto de la operación, sin sobrescribir resultados previos. El manifiesto final identifica este intento como fallido y confirma que los inputs protegidos permanecieron iguales.

## Alcance del fallo

El último par contiene dos polígonos válidos con áreas aproximadamente2502494.782525 y938019.673208 m². El predicado de relación devuelve `212111212` (interiores con intersección bidimensional), pero la operación intersección produjo dimensión inferior a2, disparando el control estricto preregistrado. Los WKB permiten una auditoría independiente. No se atribuye de antemano el tamaño o causa del desacuerdo a un sliver despreciable, ni se cambia el resultado a cero por una posible explicación numérica.

El cap no fue el bloqueo: se detuvo por identidad/predicado. El último checkpoint de cruces completos registra50772 átomos y468377 candidatos acumulados, correspondientes a la finalización2019; no representa el total final de todos los candidatos intentados después. Las salidas físicas finales son aproximadamente11MiB, por debajo de200MiB. Los conteos del grupo2023 interrumpido no se presentan como un overlay exhaustivo terminado. No hubo fallo por límite de átomos o tiempo.

Este resultado refuta la extrapolación “pasaron los cinco WKB, entonces basta cambiar el origen para validar todo el ledger”. No demuestra que toda la representación sea inútil o que la discrepancia restante tenga magnitud científica material: ese tamaño necesitaría un diagnóstico independiente y protocolo propio. En este estudio el gate fallido es obligatorio y no se relaja después de ver el dato. No se ejecutan los grupos restantes, otra representación, replay o25 para compensarlo.

Protocolo congelado `97dbd33`; cap real2026-11-15T05:24:38.114629Z–06:54:38.114629Z, incluida revisión, sin reinicio. Código nuevo `pipeline/centered_observation_ledger.py`, SHA `9848796bde6cc8e03fcc524c777565159881102855403dd3fd06ce6e6e3ff8f7`; freeze SHA `5c1705a6e012fab2cbd24045f86be6d6c3c012c381821932df31cd6a877416e0`. No se modificaron helpers ni resultados24B/27/29, paquetes, locks o producción.

## Representación y certificado antes de operaciones

Se reconstruyeron los mismos CORE en coordenadas mundiales originales, con idéntica fórmula/orden de operaciones del helper congelado y mapping nativo. El nuevo código sólo introduce el frame local después de construir vértices y antes de clips, propiedad, uniones o intersecciones. No se construyó una malla alternativa desde centros previamente trasladados.

| Caso/producto | CORE construidos, incluidos vecinos | Polígonos incluidos según mismo halo/estado | Máxima diferencia de área completa frente24B m² |
|---|---:|---:|---:|
| 2019 Aqua | 5456 | 4672 | 0 |
| 2019 VIIRS | 48000 | 40707 | 0 |
| 2023 Aqua | 3272 | 2674 | 0 |
| 2023 VIIRS | 44310 | 37398 | 0 |

El certificado cubre101038 polígonos construidos y la AOI:505195 tuplas/1010390 restas escalares racionales, incluidas todas las coordenadas de cierre y polígonos de vecinos/halo que después no contribuyen. Las cuatro poblaciones de índices/estados coinciden exactamente con24B; no se extrapolaron bordes. Todas las restas pasan `Fraction.from_float` y la inversión bitidéntica. No se excluyó una coordenada que fallara para permitir overlays.

Certificado `exactness-certificate.json` SHA `09274448ba09075d6932e86a4e21c0b62a5daae9abd5a87210e73fde06d14f4b`, emitido antes de overlays. Congela los cinco archivos de inputs locales (AOI y cuatro grupos NPZ), incluidos índices/flags de inclusión/áreas completas. El origen único proviene del índice previo SHA `6cbcf6b06506c22330045119378639eca3f392b8125a72d36fb350dab4421cfb`: `[722459.8026976171,5902205.764776958]` en EPSG:32718.

Las geometrías canónicas nuevas son **offsets locales en metros**, con `parent_crs=EPSG:32718` y origen explícito. No se etiquetan como coordenadas absolutas de ese CRS ni se ejecutan overlays tras devolverlas al mundo. No hay snap, cambio de grilla/precisión, `buffer(0)`, simplificación, reparación o búsqueda de origen.

## Dos expresiones geométricas obligatorias

Primera: propiedad por scan con referencia más temprana (primaria) o más tardía (sensibilidad), conservando desconocidos y excluyendo de propietarios conocidos toda zona cubierta por scans de orden desconocido. La intersección de ambas uniones de propiedad identificada define el común. Cada propietario se cruza con la unión ajena y se comprueban sumas, uniones, diferencias simétricas, complementos, predicados, bounds, tipos y validez/finitud.

Segunda: STRtree de propietarios individuales, consultando **todos** los candidatos bbox geométricos. Sus intersecciones se descomponen en todas las componentes poligonales positivas; contactos de área0 se cuentan aparte. Suma y unión de átomos deben reproducir el mismo común y las áreas por cada ID nativo. Se comprueba también disjunción con pares candidatos intra-scan, entre propietarios y entre átomos; sus índices quedan exportados para auditoría.

Ambas expresiones deben pasar. No se elige la que retenga más superficie. Este control es independiente de la expresión computacional con megauniones, **no** de la bibliotecaGEOS ni una verdad física. Tolerancia fija de reconciliación1m², sin compensar fallos entre casos/prioridades. La comparación contra áreas completas anteriores es un gate de representación; diferencias frente al antiguo **clip** mundial se guardan como diagnóstico, porque ese clip era ya una operación del operador bajo evaluación, no verdad de entrada.

Límites fijos:250000 átomos por caso/prioridad,2M total,5M pares candidatos y200MiB salida; ante exceso se conserva `resource_limit`, sin aproximación favorable. Los ocho grupos instrumentales y cuatro cruces deben estar completos para declarar pase global. El programa guarda un fallo explícito y último contexto geométrico si se interrumpe; ese contexto no se atribuye automáticamente como causa.

## Trazabilidad, pruebas y deuda científica

Trece tests sintéticos pasaron antes de reales: exactitud/cero firmado/dimensión/finitud, overlays/complementos/ambos órdenes, tiempo desconocido, prioridades, disjunción material y contactos, agujeros/fragmentos pequeños, clip con centro exterior, todos los candidatos y cierres por ID, resource_limit y bloqueo si una expresión difiere. Los helpers puros y tests no dependen del cap o archivos `.runtime`; sólo la orquestación real lee su cap congelado.

Freeze de entradas sólo incluye fuentes efectivas e inmutables nombradas (NPZ/ref/helpers/24B/29/origen/binarios/cap/protocolo). No congeló archivos30A o HTML ajenos mientras se escribían. No hubo nuevos datos, dependencias, instalaciones, credenciales, RAW, máscaras FIRE/QA o modelos.

Durante el inicio de operaciones se observó `RuntimeWarning: invalid value encountered in create_collection` deShapely, también observado antes al procesar colecciones vacías. Se registra el warning; no se usa como criterio de aceptación o de verdad. Cada salida se valida de manera explícita. Una salida no válida/no finita bloquea, aunque las áreas parezcan cerrar.

Comandos del intento:

```sh
.venv/bin/python -m unittest discover -s tests -p test_centered_observation_ledger.py
.venv/bin/python pipeline/centered_observation_ledger.py freeze
.venv/bin/python pipeline/centered_observation_ledger.py prepare
.venv/bin/python pipeline/centered_observation_ledger.py run
```

Los stages no sobrescriben el intento existente. Toda reproducción posterior requiere nuevo cap/ruta/código de orquestación identificado, sin eludir el reloj del intento original.

30A aporta testigos exactos/cotas de los mismos cinco ejemplos, independientes deGEOS;29 mostró dependencia del origen en esos ejemplos. Ninguno reemplaza el control de toda la representación aquí. Incluso un pase geométrico no valida PSF, exposición comparable, instantes por píxel o causalidad interna deGEOS. Los13 contrastes dimensionalesVIIRS anteriores siguen selectivos. SuspectMODIS sigue pendiente.

No se ejecuta replay de etiquetas mientras no pasen todos los gates y revisión. Los dos de seis registros positivos Aqua2023 en bordes sinCORE **deben seguir con área null**; el operador no los completa por la etiqueta positiva ni por la propiedad de otro scan. No se suman sensores ni se comparan clases conjuntas. `gate1_passed`, `physical_footprints_verified`, `pixel_exposure_times_verified` y `scientific_eligibility_certified` permanecen falsos. 25 continúa pendiente de un protocolo y autorización propios.

Revisión independiente completada sin bloqueantes para publicar como fallo: trece tests,40hashes y11.118.234bytes, fuentes/binarios, certificado505195tuplas con1010390igualdadesracionales/inversiónbit, cierres porID2019 y últimoWKB/predicado/overlay reproducidos por separado. Esto confirma el negativo, no un pase geométrico.
