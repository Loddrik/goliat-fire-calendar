# Pendientes de entrega antes de las 12:30 Santiago

**Estado al cierre, 15-11-2026 12:15 Santiago (15:15 UTC):** #64, #65 y #66 están fusionados en `dev` y publicados en `main` con #67. #31 se cerró sin fusionar: lo reemplazó #66, que estabiliza el mismo orden de la recurrencia. Las menciones a PR abiertos y la guía de merge quedan como registro histórico; no quedan merges pendientes de esta entrega.

**Actualización de originales, 14:11 UTC:** la copia del otro desarrollador completó **1.071/1.071 CSV exactos**. El guard devuelve **COMPLETE, salida 0** en esta máquina. Los 956 recuperados y 115 faltantes citados en informes previos corresponden al corte anterior. No se repitieron ingestión, cartografía ni modelos; el fallo estricto histórico de una fila por lado sigue sin resolverse. [Recibo de la copia](evidence/peer-raw-recovery.json).

**Actualización de integración:** `dev` avanzó a `2fa31b4` durante la preparación. La [consulta de cierre](evidence/repository-at-close.json) registra ahora **23 de los 24 PR científicos seleccionados fusionados y uno abierto (#64)**. El inventario de las 13:41 UTC se conserva como antecedente fechado. Se incorporan localmente la marca nueva y el método en inglés del otro desarrollador; esto no acredita despliegue ni promoción de los modelos de investigación.

**Orden ratificado por los seis integrantes de ambos consejos.** Corte de entrega: **15:30 UTC del 15 de noviembre de 2026**. Esta lista define acciones acotadas y su aceptación; no registra que ya se hayan ejecutado ni autoriza merges, despliegues o cambios científicos.

Los tres roles acordaron primero los [criterios de entrega](evidence/delivery-council/criteria-frozen.json), congelados a las 13:41 UTC: respaldo de las afirmaciones; valor observable para el equipo; factibilidad antes del corte; dependencias; y aceptación verificable/reversibilidad. Se aplican en ese orden, **sin puntajes sintéticos** y sin trasladar los pesos de experimentos anteriores. No se compensa una afirmación falsa con una demo atractiva.

## El mínimo que sí permite presentar

Una versión identificada de la aplicación y un relato verificable bastan para la entrega. **La disponibilidad raw ya está completa y nunca fue requisito de la demo**: ésta usa los derivados y JSON existentes, sin reingestar ni ajustar modelos. El estado actual ya permite mostrar M1 y las 14 comunas habilitadas, sus observaciones, la reconstrucción mensual con sus límites y una exportación.

El primer cierre tenía **956/1.071 archivos exactos**: cuatro snapshots NRT discrepaban de la redescarga y 111 ventanas no se habían consultado. La copia recibida completó los 115 originales exactos; ahora son **1.071/1.071**, sin faltantes. El núcleo de 205 fuentes históricas reproduce 223 celdas de máscara, los conteos y el factor M1 utilizando el mapa comunal congelado. La comparación estricta de detecciones conserva **una fila distinta por cada lado**; esto no es reproducción integral desde la adquisición. Véanse el [estado de recuperación](../../reviews/2026-11-15-raw-recovery-report.md) y la [auditoría histórica](../../reviews/2026-11-15-raw-historical-core-audit.md).

En el corte histórico, el [inventario de PR](evidence/pr-inventory.json), observado a las **13:41 UTC**, contenía 24 PR científicos seleccionados: 21 abiertos y tres fusionados (#23–25). #22, de integración, estaba fusionado; #31 seguía abierto hacia `main`, como caso de publicación separado que requiere un responsable explícito. #64 es un draft hacia `dev`. Esto no acredita un despliegue. El responsable de release debe actualizar el estado si cambia antes de la presentación.

## Seis acciones cortas

**P0** forma el mínimo de entrega. **P1** es opcional y sólo avanza con otra persona disponible o después de cerrar P0; no bloquea la presentación. Los tiempos incluyen revisión de la acción, no se suman como si hubiera recursos infinitos.

| Orden | Prioridad y acción | Responsable por rol | Tiempo | DONE verificable |
| --- | --- | --- | --- | --- |
| 1 | **P0 · Hoja de afirmaciones y respuestas** | Curador científico + presentador | 15–25 min | Diez afirmaciones del guion tienen fuente y alcance; resumen y guía no confunden diagnóstico, publicación o despliegue. Preguntas difíciles tienen respuestas coherentes. |
| 2 | **P0 · Candidato de demo y paquete abrible** | Mantenedor de release + receptor | 20–40 min | Commit/rama, comandos, artefacto y checks quedan identificados; el receptor abre el paquete sin reingestar raw. Hay plan de corte/diff/CI y un responsable de integración, sin fusionar toda la pila. |
| 3 | **P0 · Ensayo de tres decisiones visibles** | Frontend/QA + presentador | 30–45 min | Acta de rutas/commit/resultados y respaldo: Tomé habilitada, Concepción sin reconstrucción y tabla/CSV con separación observado/estimado. No se anuncia un ensayo sólo sugerido como ya pasado. |
| 4 | **P1 · Custodia de raw y faltantes exactos** | Ingeniería de datos + custodio del respaldo | 15–30 min | El receptor sabe dónde está el tar completo verificado, su hash y el manifest que acredita cero faltantes. Se conserva el corte parcial anterior; no se ejecuta ingestión completa ni se altera el inventario. |
| 5 | **P1 · Contrato mínimo de metadatos estacionales** | API/backend + revisor científico | 30–45 min | Esquema/fixture define métricas, fracciones, signo, N, período, máscara, procedencia y null con referencia cero. Se declara que aún no está publicado en API/JSON. |
| 6 | **P1 · RFC de desempate determinista** | Ingeniería de datos + revisor científico | 20–30 min | Política futura y fixture del empate documentan clave/redondeo/orden/filtro y aceptación independiente del orden. No se elige el ganador para copiar al canónico ni se aplica la regla hoy. |

### P0: dependencias, aceptación y alternativa

**1. Afirmaciones.** Usar el [resumen de negocio](resumen-negocio.md), el método y las revisiones existentes. Las cifras de temporada pertenecen al diagnóstico aparente de 112 casos: mediana APE 20,34 % y media relativa firmada −11,46 %. No son MARE, validación de 2002–2011 ni una banda anual. M1 publicado no se sustituye por E_coherent o F21; CRPS favorable no equivale a pronóstico futuro o calibración demostrada. Cero registrado no certifica ausencia de fuego y detección no equivale a incendio individual. Incluir raw, discrepancia estricta y cartografía congelada. Si una afirmación no tiene fuente, retirarla del guion; no abrir otra investigación para salvarla. Fechar o actualizar el estado vigente del cierre de `docs/method.md` que aún menciona los 1.071 CSV faltantes, conservando el antecedente histórico.

**2. Versión y paquete.** Identificar un commit real y los checks de ese commit; “358 tests comunicados” no basta como prueba de la versión que se abre ni como validación científica. Documentar dependencias bloqueadas y un camino pequeño de lectura: verificador portátil CRPS39 y guard de raw, sin ejecutar drivers con deadline vencido. El lector CRPS comprueba evidencia congelada; el guard señala la disponibilidad real (COMPLETE aquí, INCOMPLETE sin respaldo). Un clon sin el respaldo puede no tener ningún raw, mientras el checkout restaurado tiene 1071: no prometer idénticos faltantes en ambos entornos. Si no se puede preparar un corte claro, usar un candidato conocido o capturas atribuidas a su commit. **“Mergear todos los PR” no es una tarea corta**: la pila exige orden, bases, revisión y validación separados. No retargetear ni fusionar #31 automáticamente por estar abierto hacia `main`.

**3. Ensayo.** Depende de identificar el candidato, pero el guion y los respaldos pueden prepararse mientras tanto. Registrar la ejecución de las rutas propuestas en el resumen, la descarga CSV y la distinción de estados. El mapa usa un estilo externo de OpenFreeMap (`web/src/ExploreMap.tsx`): ejecución local **no garantiza** mapa offline. Si falla conectividad o el mapa, completar el relato con calendario/tabla y capturas con versión, indicando qué se está mostrando. No instalar infraestructura nueva ni redescargar NASA durante la demo. Un pase de ese recorrido acredita el ensayo, no utilidad municipal, prevención o impacto medido.

## Secuencia realista y freno de alcance

No se presume que los roles ya tengan personas asignadas. El coordinador debe nombrarlas y registrar la hora real de inicio. Con personas distintas, 1 y 2 avanzan en paralelo; 3 empieza al identificar el candidato. El alcance amplio requiere hasta **100 min de camino crítico**: 40 de preparación paralela, 45 de ensayo y 15 de cierre; sólo cabe si empieza antes de las **13:50 UTC**.

Si se inicia después, usar el alcance compacto con dos operadores: afirmaciones/candidato en paralelo hasta 20 min, ensayo 30 min y cierre 15 min. Son **65 min**, por lo que debe empezar antes de **14:25 UTC**. Los últimos **15 minutos** se reservan al traspaso, sin nuevas funcionalidades. Si una dependencia falla, se utiliza la alternativa declarada y se registra el límite; no se suma trabajo pendiente como si hubiera más capacidad.

Con un solo operador, el mínimo suma 15 min de afirmaciones, 20 de candidato/paquete, 30 de ensayo y 15 de cierre: **80 min**, con inicio máximo **14:10 UTC**. Omitir P1 hoy. Si ni ese mínimo cabe o faltan personas, entregar documentación y un respaldo atribuible a una versión, señalando que el ensayo no se completó; no afirmar funcionamiento o integración que no se pudo comprobar.

## P1: límites para que no se conviertan en otra iteración

**4. Raw:** preparar la lista de rutas/SHA/tamaños y el traspaso al custodio. Los 115 faltantes ya se recuperaron con la copia recibida; documentar ese DONE no autoriza otra ingestión. No fabricar originales a partir de Parquet ni aceptar los cuatro NRT distintos. El respaldo raw ignorado por Git requiere custodia propia; el receptor debe tener acceso real o constancia de que la transferencia sigue pendiente. No ejecutar `inventory.py` para convertir una recuperación parcial en un inventario nuevo.

**5. Metadatos:** usar el [contrato del issue 48](../../reviews/2026-11-15-issue48-product-assessment.md) y las métricas revisadas de 42. El objeto diagnóstico debe estar separado de `gates`, con null y causa cuando la referencia sea cero. DONE hoy es **contrato y aceptación**, no regenerar JSON, cambiar UI o habilitar barras anuales desde 2002. Si no hay revisor disponible, conservar el diseño existente como pendiente, sin anunciar un endpoint.

**6. Deduplicación:** partir del [empate documentado](../../reviews/2026-11-15-raw-ingestion-recovery-review.md). Un desempate reproducible no decide cuál observación representa mejor el fuego. El RFC debe conservar las dos procedencias y exigir una prueba de invariancia al orden antes de una futura aplicación aislada. La igualdad de celda-día no rescata el fallo de 13 columnas. Si no hay acuerdo, dejar la política pendiente; no cambiar canónicos, Parquet, máscaras o modelos hoy.

## Investigación posterior: no ejecutar para esta entrega

- **Disponibilidad resuelta:** la copia recibida completó los 115 originales; conservar el tar completo y verificar su transferencia al receptor. Esto no elimina los límites de ingestión y cartografía.
- Reproducir adquisición y asignación cartográfica, aplicar una política de ingestión acordada en entorno aislado y evaluar su impacto antes de reemplazar derivados.
- Decidir el uso anual mediante una decisión/coste y evaluación posteriores; el diagnóstico de 112 casos no crea una nueva compuerta anual.
- Resolver observabilidad física G1, estados sin detección/desconocidos, soporte espacial, tiempos y QA compatibles. El catálogo GOES no constituye ese denominador.
- Evaluar transporte histórico y nuevas familias de modelo con una pregunta y destino de evaluación realmente reservados; no añadir otra fórmula a los targets ya vistos por urgencia de presentación.
- Diseñar un piloto municipal de comprensión y uso con una decisión observable. No hay clientes, ROI ni reducción de incendios demostrados que puedan anunciarse hoy.

## Trazabilidad y ratificación conjunta

Esta consolidación conserva los aportes individuales: [negocio B1–B4](evidence/delivery-council/business-proposals.json), [ciencia S1–S4](evidence/delivery-council/scientific-proposals.json) e [ingeniería E1–E6](evidence/delivery-council/engineering-proposals.json). B1/S1/E1 sustentan afirmaciones; B3/S2/E2 el paquete verificable; B2/E3 el ensayo; B4 se integra en respuestas y piloto posterior; S3/E4 en custodia; S4/E5/E6 en contratos futuros. Negocio propuso ensayos de 20 min; ingeniería conserva 30–45 min para incluir comprobación de versión y contingencia. Ambos consejos ratificaron el orden y conservaron explícitas esas estimaciones alternativas, sin confundirlas con tiempos medidos.

Los tres adversarios ratificaron el orden; ciencia, negocio e ingeniería del consejo multifocal leyeron sus objeciones y también lo ratificaron. La [resolución conjunta](evidence/delivery-council/joint-resolution.json) enlaza los seis votos y los hashes. Se conserva el [texto exacto revisado](evidence/delivery-council/reviewed-priorities.md), SHA `fbdf5ae695312934ae91b927fc6d7ff5f247efa72699ea9c3e8831ae880ec18f`. Esta versión sólo añade el cierre y estado, sin cambiar el orden ni el alcance de las acciones.

Las condiciones aceptadas son identificar operador y hora, vincular candidato/artefacto/checks, registrar ensayo real con alternativa y declarar la custodia local del tar. El coordinador automatizado ejecuta documentación y comprobaciones locales; presentador y mantenedor receptor siguen sin persona asignada. Véase el [acta local](acta-ensayo.md). Un recorrido automatizado no acredita comprensión municipal, ensayo humano ni despliegue. P1 conserva su carácter opcional y sus contratos siguen pendientes.
