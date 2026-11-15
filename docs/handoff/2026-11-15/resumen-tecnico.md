# GOLIAT: resumen técnico para la entrega

**Corte científico y de código: 15 de noviembre de 2026, referencia `6410fcb`/PR64.** El producto conserva M1, factor regional `2.352954072125397`, y 14 de 54 comunas habilitadas. La investigación produjo candidatos y resultados reproducibles; no autorizó sustituir M1, ampliar gates, publicar otras bandas o desplegar automáticamente. Los estados de PR del apéndice proceden de una consulta GitHub fechada: no acreditan despliegue y pueden cambiar.

El resultado práctico es una aplicación integrada, un archivo de evidencia científica y herramientas para verificarlo sin repetir experimentos vencidos. Los avances más claros son una asignación puntual retrospectiva bajo presupuesto, una comparación favorable de CDF marginales y la recuperación de originales con integridad verificable. Sus límites —transporte, sesgos territoriales, referencia instrumental y observabilidad— siguen visibles. [Decisión científica](../../reviews/2026-11-15-final-scientific-decision.md), [addendum GOES](../../reviews/2026-11-15-final-scientific-decision-addendum.md) y [fuentes de este resumen](evidence/technical-source-map.json).

## 1. Producto integrado y contrato que se mantiene

GOLIAT y FireChronos se combinaron preservando dos publicaciones: calendario armonizado y archivo observado por plataforma. React/MapLibre consume datos publicados; Python/DuckDB/Parquet prepara y audita la ciencia. El servidor Node/Express sirve aplicación y archivos. No se reemplazó silenciosamente la cartografía ni la unidad de un proyecto por las del otro.

| Ruta de información | Contrato y cambios implementados |
|---|---|
|Calendario armonizado|54 comunas de Biobío/Ñuble; grilla literal 0,01°; pertenencia comunal por centroide; máscara histórica GOLIAT. Aqua estimado julio 2002–junio 2012 sólo donde pasan gates; S-NPP en temporadas 2012–2017 y NOAA-20 desde 2018, una plataforma por temporada.|
|Historia observada|Archivo FireChronos con DPA 2023, día/confianza/Type=0, sin armonización y con su propia geometría, procedencia y exportación. Archivo anual hasta diciembre 2025; no concatena plataformas como incendios independientes.|
|Integración y publicación|Corrección de JSON no finito; ventana julio–junio truncada al mismo día del corte; fallback a geometría versionada cuando falta el CSV local de CUT; abortado de consultas anteriores, validación de respuesta/hash y exportaciones del contrato seleccionado. El explorador original sigue disponible.|

La unidad central es **celda-día diurna registrada**, agregada por comuna/mes; no incendios, hectáreas o totalidad de actividad física. Un cero no acredita cielo despejado, pasada útil ni ausencia de fuego. El archivo observado y el científico difieren en filtros, mapa, máscara y reglas de grilla; compartir resolución nominal no los hace intercambiables. [Integración y pruebas](../../integracion-firechronos.md), [método publicado](../../method.md).

M1 multiplica Aqua por un factor regional. Las estimaciones históricas se habilitan con Aqua de desarrollo ≥50 celdas-día y dos condiciones LOSO separadas: superar climatología en ≥6/8 temporadas y superar Aqua sin corregir en ≥6/8. No tienen que ser las mismas seis victorias. Son reglas del proyecto, no estándares NASA. La banda pública es error típico empírico, no confianza, cobertura futura o incertidumbre de observación. La continuidad NOAA-20/S-NPP permanece aproximada regionalmente, con discrepancias locales; no se valida por conservar el factor 1.

## 2. Qué se implementó y aprendió al iterar modelos

Las etapas 2–15 introdujeron evaluación anidada, controles, candidatos, intervalos y pruebas de transporte. Las máscaras y ajustes se aprendieron por origen donde correspondía; no se presentan todos los paneles como si usaran las mismas 223 celdas publicadas. Las fechas de desarrollo ya consultadas tampoco vuelven a ser holdout al cambiar de fórmula.

| Etapas | Implementación y decisión conservada |
|---|---|
|2|Auditoría de máscara, selección anidada, gates y bandas. La selección M1/A apenas mejora; no justifica sustituir M1.|
|3–5|Afín regularizado B, Huber y pendientes por tramos con cero exacto. B mejora 7,04 % en su desarrollo; Huber no supera consistentemente B. El paquete por tramos añade beneficios y costes en positivos omitidos/ceros; sus porcentajes no se suman como ganancias independientes.|
|6–7|Sensibilidad de grilla/límites y continuidad VIIRS. Las habilitaciones locales son sensibles a definiciones; totales regionales cercanos no prueban equivalencia mensual local.|
|8–10|Transportes temporalmente invertidos y tamaños de origen. Entrenar tarde para reconstruir temprano no conserva uniformemente las ganancias; seis temporadas ayudan en algunos contratos. CONAF, en 9, cuenta otro objeto y no valida directamente celdas-día.|
|11|Modelos y radios congelados antes de consultas posteriores. Se explicitan deriva Aqua y destinos ya explorados; ningún candidato domina todas las temporadas/subgrupos.|
|12–13/15|Escalas absoluta/raíz/relativa, cohortes, asimetría y optimización de extremos. La escala raíz mejora la pérdida de intervalo con costes de anchura/cobertura. No garantiza cobertura nominal ni sustituye la banda publicada.|
|14|Terra como predictor separado; la familia ensayada no supera B en la primaria. No se suma Terra+Aqua como eventos.|

La numeración de etapas no coincide con la de PRs: también hay preflights y consejos, no sólo nuevas familias. Los informes por etapa y protocolos están en el [índice científico](../../reviews/README.md); los [experimentos 2–15](../../reviews/2026-11-14-research-decision.md) y su reproducción preservan controles, predicciones, manifiestos y decisiones negativas.

**16–18: de corregir cantidades a decidir bajo una distribución.** Forzar cero cuando Aqua=0 no aporta una mejora aislada. Se implementó una CDF hurdle: probabilidad de referencia S-NPP positiva y distribución de cantidades positivas, con pooling parent/local. Modela registros S-NPP, no probabilidad física de incendio. Su mediana puede mejorar error local y deteriorar el total.

MAE significa error absoluto medio mensual, medido aquí en celdas-día. E_coherent minimiza pérdida absoluta esperada bajo esas CDF con asignaciones no negativas y presupuesto mensual ΣB sobre las 54 comunas; entre empates conserva proximidad a B. En las mismas 5184 filas anidadas de 18:

| Método del mismo panel | MAE comuna-mes, celdas-día |
|---|---:|
|M1 reajustado por origen|2,047245|
|B, política afín|1,903194|
|E_coherent|1,797939|

La reducción compuesta M1→E_coherent es **12,1776 %**, calculada entre esos endpoints del mismo panel; no es 7,04 %+5,53 %. Conservar el total, sesgo global y error regional de B es algebraico, no otra validación regional. Hay costes en ceros y territorios; en las 14 del bloque 2020–2021, E_coherent empeora frente a B aunque mejore el agregado 54. Reconciliar sólo el área consultada cambiaría la decisión: se conserva primero el universo 54. [Etapa 18](../../reviews/2026-11-14-science-review-18.md).

**19–24: referencias, contratos y transporte.** Cambiar S-NPP por NOAA-20 conserva alguna ventaja agregada, pero cambia conclusiones locales; es sensibilidad de plataforma. 20 estricto quedó bloqueado por enero–junio 2026 fuera del archivo observado; 20A compara las 3456 filas comunes hasta diciembre 2025, sin rellenar las exclusiones. 21 reserva región y período: la mediana parental mejora sólo uno de cuatro regímenes. Usa máscara 6 pre 2012 distinta del contrato 18; no se comparan sus MAE absolutos. En held, E11 y el parent tienen exactamente la misma CDF, no dos brazos informativos.

Se implementaron composiciones territoriales y un modelo contextual en 22–23; la política principal 23 falla, aunque alguna sensibilidad cambie signo. 24C compara contratos científico/publicado con modelos congelados: estabilidad global acotada, fragilidad en 14 y extremos. Los productos diarios gridded no proporcionaron un denominador comparable de pasadas útiles. Ninguna de estas rutas resuelve observabilidad. [Transporte 21](../../reviews/2026-11-14-science-review-21.md), [contexto 23](../../reviews/2026-11-15-science-review-23.md), [contratos 24C](../../reviews/2026-11-15-science-review-24c.md).

Los consejos multifocales y adversarios —con enfoque LOCO y ratificación de seis roles— conservaron criterios científicos y desacuerdos. Los planes 24/31/35/38 separan selección de preguntas, ejecución con protocolo previo y revisión; rangos subjetivos no son probabilidades ni un ganador robusto. Los nuevos criterios cualitativos de entrega no reponderan esos estudios.

## 3. Operadores, negativos y calidad probabilística

El piloto de observación utiliza dos casos fijos 2019/2023, geometría, índices, tiempos y etiquetas nativas. El ledger continuo falló controles de cierre; cambiar motor u origen no validó su ejecución global. 30A obtuvo cotas exactas locales; 30B volvió a fallar. 32B adjudicó una intersección racional pequeña, sin acotar el error global ni autorizar ignorarlo.

32A cambió explícitamente de estimando: puntos nominales prefijados, pertenencia exacta, prioridad de owner y desconocidos; no reparación de áreas continuas. 33 añadió etiquetas sin borrar positivos por QA y conservó catálogo/retención. Su Jaccard conocido 15 % en un escenario 2023 es concordancia de etiquetas sobre puntos; no sensibilidad, precisión física o fracción de desacuerdo explicada. En 2019 la unión positiva conocida vacía da NULL. La grilla pierde representación de píxeles, los bordes conservan desconocidos y los puntos vecinos no son réplicas independientes. G1, PSF, exposición por píxel y semánticas específicas siguen pendientes. [Geometría 30B](../../reviews/2026-11-15-centered-ledger-revalidation-review.md), [operador 32A](../../reviews/2026-11-15-point-ownership-audit-review.md), [etiquetas 33](../../reviews/2026-11-15-discrete-state-comparison-report.md).

| Etapa posterior | Resultado y alcance |
|---|---|
|35: presupuestos separados|No supera su primaria held frente al presupuesto global. Regiones coinciden con SOURCE/held: prueba acoplamiento de asignación, no ecología. Los diagnósticos omitidos B/C se completaron en suplemento transparente; no se reescribió el original.|
|36: cubo diario|5184 claves y 10368 identidades Aqua verificadas. D requiere la misma celda en días UTC consecutivos dentro del mismo mes. Placebo permuta columnas de los 28–31 días, incluidas vacías, compartidas por todas las celdas. Integridad no implica utilidad.|
|37: contexto diario|Real−placebo=−0,004927, pero real−G21=+0,010794: falla el doble criterio. La activación/fallback difiere entre variantes; no demuestra inutilidad universal de cronología. El entorno contemporáneo del productor faltó y no se inventó retrospectivamente.|
|39: CDF original frente a δB|CRPS igual peso de cuatro held=−0,618164, favorable en sus cuatro promedios. Hay costes en 14, ceros y extremos, especialmente SOURCE Ñuble→held Biobío. No se puntúa 37 para rescatar su fallo.|
|40: GOES documental|Diez objetos listados en fechas fijas y documentación, cero objetos científicos adquiridos en esta etapa. Versiones históricas, Mask/DQF y exposición no verificados: contexto grueso condicionado, no adjudicación 375 m ni oportunidad física equivalente.|

F21 es una distribución de **S-NPP del mismo mes histórico condicionado por Aqua ya observado**, no pronóstico operacional futuro. CRPS frente al forecast degenerado δB combina localización y dispersión; no demuestra calibración o valor aislado de incertidumbre/Aqua. F21 precede a la reconciliación y no proporciona bandas alrededor de G ni una distribución conjunta de 54 comunas. [Revisión 39](../../reviews/2026-11-15-crps-independent-review.md), [revisión 37](../../reviews/2026-11-15-daily-context-independent-review.md), [GOES40](../../reviews/2026-11-15-goes-preflight-independent-review.md).

## 4. Totales estacionales y recuperación de originales

**42, issue 48:** se sumaron predicciones LOSO existentes, con máscara publicada fija. Para las 14 seleccionadas con ese mismo desarrollo, 112 comuna-temporadas con Y>0: mediana APE **20,34 %**, MARE **22,81 %**, media relativa firmada **−11,46 %**, WAPE **20,42 %** y sesgo relativo agregado **−10,60 %**. Son fórmulas distintas. Los Y=0 del universo completo mantienen relativos NULL y errores absolutos; no se eliminan silenciosamente.

La reconstrucción independiente usó `bias×n` original y denominadores S-NPP canónicos, sin usar las predicciones primarias como referencia. Es un diagnóstico aparente postselección: no valida 2002–2011, una banda anual ni la causa del salto 2012. No crea gates anuales. Los metadatos `diagnostics.season_total_loso` son propuesta, no API implementada. El intento 01 conserva RSS desconocido; sólo 02 fue medido tras una enmienda instrumental, con CSV idénticos. [Informe 42](../../reviews/2026-11-15-season-total-report.md), [revisión independiente](../../reviews/2026-11-15-season-total-independent-review.md).

**43, recuperación posterior autorizada:** 956 de 1071 originales coinciden con tamaño/SHA256 del inventario; faltan 115 y no hay archivos canónicos diferentes o adicionales. El estado sigue **INCOMPLETE**. Estos crudos son locales/ignorados por Git; un clon no los contiene automáticamente. La nueva guardia verifica inventario y archivos **antes de abrir DuckDB** y bloquea ingestión incompleta; no cambia los SQL científicos.

La auditoría aislada de 38 archivos detectó una colisión de clave redondeada: dos registros S-NPP con distintas coordenadas/FRP, misma prioridad y sin desempate. La comparación exacta de 13 columnas falla 1 fila por lado; una proyección a celdas-día coincidente no rescata esa primaria. Una ampliación prospectiva de 205 fuentes exactas recuperó todas las fuentes inventariadas pertinentes anteriores a julio 2020: reproduce exactamente máscara 223 y conteos de entrenamiento Aqua/S-NPP, y la razón M1, **condicionada al mapa comunal congelado**. La comparación estricta de detecciones en esa fase de 205 fuentes también conserva una fila distinta por lado; esas filas históricas no se atribuyeron individualmente al empate diagnosticado en los 38 archivos. El pase corresponde a máscara/conteos bajo la condición indicada. No reprodujo la asignación geográfica, toda la ingestión 2026 o el pipeline entero desde originales. No se corrigió silenciosamente el canónico. [Ingestión 38](../../reviews/2026-11-15-raw-ingestion-recovery-review.md), [núcleo 205](../../reviews/2026-11-15-raw-historical-core-audit.md), [estado final](../../reviews/evidence/raw-recovery-final/inventory-verification.json).

## 5. Verificación actual y transferencia segura

El corte PR64/`6410fcb` tiene 358 pruebas Python aprobadas y checks web/ciencia exitosos en el [recibo de verificación](evidence/verification-snapshot.json), observado a las 13:45 UTC. El [run científico](https://github.com/Loddrik/goliat-fire-calendar/actions/runs/43719314956) también ejecutó el lector portable. Ese pase acredita los casos y contratos ejecutados; no es validación física o una promesa de instalación universal. CI usa Python 3.14.7, `uv==0.11.7`, entorno `uv.lock` y Node 22. En un checkout con sus dependencias, los comandos vigentes son:

```bash
uv sync --frozen
uv run --frozen python -m unittest discover -s tests -p 'test_*.py' -v
uv run --frozen python -O pipeline/verify_crps_evidence.py
uv run --frozen python pipeline/verify_raw_inventory.py --details
npm ci
npm --prefix web ci
npm test
npm --prefix web run lint
npm --prefix web run build
npm start
```

La aplicación se sirve por defecto en `http://localhost:3000`; el estilo base del mapa requiere acceso externo.

El lector 39 reproduce snapshots de pérdidas y su integridad, sin fuentes privadas ni reloj de los experimentos; comparte el oráculo archivado, no es un tercer oráculo independiente. Su membresía 14 usa una copia de gates anclada al freeze 39, para que futuros cambios legítimos de publicación no alteren ese estudio. El verificador raw devuelve salida no exitosa con `INCOMPLETE` mientras falten fuentes; en un clon limpio es esperable que falten más que en esta máquina.

Los drivers históricos tienen caps y rutas originales. **No ejecutar sus comandos antiguos ni importar scripts con efectos como si fueran un replay portable.** Para repetir investigación se necesita orquestación/presupuesto declarados, las fuentes exactas y preservación de evidencia. `publish_observed.py` publica archivos; no es un verificador de sólo lectura. El builder HTML puede regenerarse y comprobarse contra Git sin recalcular ciencia; el [artefacto autónomo](../../artifacts/science-observation-plan-2026-11-15.html) explica hasta 42 con ocho SVG y se complementa con los informes de recuperación.

Para transferir el trabajo se requieren repositorio/commit, inventario de PR fechado, locks, manifiestos y el backup separado de crudos. Nunca incluir claves o tokens en código, documentos o logs compartidos. Ejecutar la app localmente tampoco garantiza mapas offline: el estilo base externo exige conectividad o un fallback explícito. El resumen de fuentes y el estado de PR permiten revisar lo existente sin confundir una rama abierta, un merge y un despliegue.

Las deudas técnicas permanecen nombradas: fuentes 115 pendientes; política de deduplicación determinista aún por acordar; geografía/ingestión integral no reproducidas; uso anual y cambio de política sin evaluación independiente; observabilidad física y continuidad local entre plataformas. Cualquier trabajo posterior debe fijar unidad, decisión, fuentes, controles y aceptación antes de volver a los mismos targets.

---

## Apéndice: inventario seleccionado de PRs

Consulta del **2026-11-15T13:41:06.420134+00:00**, [inventario fuente](evidence/pr-inventory.json). Son **26 entradas seleccionadas**: 24 ramas científicas (3 PR fusionados, 21 abiertos sobre `dev`), integración 22 y corrección 31. No es el historial completo del repositorio. **PR31 sigue abierto sobre `main`; no está fusionado ni cumple una descripción indiscriminada de “todos sobre dev”.** PR64 es borrador. La selección de este inventario no confirma merges posteriores, despliegue o aprobación científica.

| PR | Estado observado | Base | Head | Título verificado |
|---|---|---|---|---|
|[#22](https://github.com/Loddrik/goliat-fire-calendar/pull/22)|Fusionado|`main`|`9ad5fdd6`|Integra FireChronos observado y corrige publicación temporal y JSON|
|[#23](https://github.com/Loddrik/goliat-fire-calendar/pull/23)|Fusionado|`dev`|`43de28f7`|Ciencia: audita máscara por partición, selección anidada y cobertura de bandas|
|[#24](https://github.com/Loddrik/goliat-fire-calendar/pull/24)|Fusionado|`dev`|`c4f5e0d2`|Ciencia: evalúa el modelo afín y el coste de estimar actividad con Aqua cero|
|[#25](https://github.com/Loddrik/goliat-fire-calendar/pull/25)|Fusionado|`dev`|`22acc267`|Ciencia: compara modelos y bandas con reproducción y pruebas de transporte|
|[#31](https://github.com/Loddrik/goliat-fire-calendar/pull/31)|Abierto|`main`|`76c7d3ef`|Publicación: estabiliza el orden de las celdas de recurrencia|
|[#32](https://github.com/Loddrik/goliat-fire-calendar/pull/32)|Abierto|`dev`|`cb6d4cdf`|science: two-part detection model and authenticated observation pilot|
|[#33](https://github.com/Loddrik/goliat-fire-calendar/pull/33)|Abierto|`dev`|`0e30172c`|science: coherent allocation lowers local MAE while preserving B totals|
|[#34](https://github.com/Loddrik/goliat-fire-calendar/pull/34)|Abierto|`dev`|`514c5303`|science: audit frozen model sensitivity to NOAA20 reference|
|[#35](https://github.com/Loddrik/goliat-fire-calendar/pull/35)|Abierto|`dev`|`3cf20cb2`|science: audit observed versus research count contracts on common archive|
|[#43](https://github.com/Loddrik/goliat-fire-calendar/pull/43)|Abierto|`dev`|`43cc4715`|science: native QA cases and standalone evidence report|
|[#46](https://github.com/Loddrik/goliat-fire-calendar/pull/46)|Abierto|`dev`|`4653bd33`|science: cold-region audit exposes nonuniform calibration transport|
|[#49](https://github.com/Loddrik/goliat-fire-calendar/pull/49)|Abierto|`dev`|`accb2f39`|science: soporte nominal por escaneo y cotas parciales exactas|
|[#50](https://github.com/Loddrik/goliat-fire-calendar/pull/50)|Abierto|`dev`|`76a92290`|science: contexto territorial no supera la primaria y límites de observación|
|[#51](https://github.com/Loddrik/goliat-fire-calendar/pull/51)|Abierto|`dev`|`eb9e490e`|science: consejos, sensibilidad contractual y límites de observabilidad diaria|
|[#53](https://github.com/Loddrik/goliat-fire-calendar/pull/53)|Abierto|`dev`|`97dbd330`|science: origen exacto revela dependencia numérica del operador nominal|
|[#54](https://github.com/Loddrik/goliat-fire-calendar/pull/54)|Abierto|`dev`|`c182a284`|science: testigo exacto y revalidación geométrica global aún bloqueada|
|[#55](https://github.com/Loddrik/goliat-fire-calendar/pull/55)|Abierto|`dev`|`74120cb0`|science: propiedad puntual exacta y adjudicación local sin reparar el fallo continuo|
|[#56](https://github.com/Loddrik/goliat-fire-calendar/pull/56)|Abierto|`dev`|`19f2425d`|science: comparación de etiquetas nativas con desconocidos y retención explícitos|
|[#57](https://github.com/Loddrik/goliat-fire-calendar/pull/57)|Abierto|`dev`|`85060f6e`|science: resultado negativo de presupuestos separados con controles y revisión adversaria|
|[#58](https://github.com/Loddrik/goliat-fire-calendar/pull/58)|Abierto|`dev`|`93240603`|science: cubo diario auditado y placebo de calendario completo|
|[#59](https://github.com/Loddrik/goliat-fire-calendar/pull/59)|Abierto|`dev`|`535c2828`|science: contexto diario no supera el doble contraste frente a placebo y G21|
|[#60](https://github.com/Loddrik/goliat-fire-calendar/pull/60)|Abierto|`dev`|`f2c3247e`|science: CRPS marginal favorable frente a deltaB con costes territoriales y extremos|
|[#61](https://github.com/Loddrik/goliat-fire-calendar/pull/61)|Abierto|`dev`|`3faed099`|Ciencia: factibilidad GOES condicionada, sin adquisición científica|
|[#62](https://github.com/Loddrik/goliat-fire-calendar/pull/62)|Abierto|`dev`|`a72b7216`|Ciencia: consolidar decisiones y verificar evidencia CRPS desde un clon limpio|
|[#63](https://github.com/Loddrik/goliat-fire-calendar/pull/63)|Abierto|`dev`|`53824113`|Ciencia: responder issue48 con auditoría de totales estacionales M1|
|[#64](https://github.com/Loddrik/goliat-fire-calendar/pull/64)|Abierto · borrador|`dev`|`6410fcb4`|Recuperar originales FIRMS y bloquear ingestión incompleta|

Los PR científicos posteriores conservan incrementos revisables. Que una propuesta esté abierta no demuestra que esté desplegada; tampoco basta el estado de un PR para reconstruir por sí solo todos los commits incorporados indirectamente por otros merges. Para integrar, revisar diff y dependencias reales sobre el head/base actuales.
