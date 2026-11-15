# Consejo de dirección tras la iteración 23

## Fase 1: criterios acordados antes de puntuar

Los miembros hurdle_design (estadística), observation_gate0 (observación) y loco_observation (hipótesis alternativas) ratificaron expresamente los mismos pesos. Se conserva su acuerdo antes de solicitar las notas de las opciones. Horizonte de trabajo: 2026-11-15 11:30 UTC.

| Criterio | Peso | Evidencia exigida |
|---|---:|---|
|Validez e identificabilidad|30%|Estimando, operador, unidad, población y pérdida; una entrega G0 no demuestra G1. Cotas condicionales honestas son admisibles.|
|Información discriminante|25%|Pregunta, dos desenlaces que cambien una decisión, y estado inconcluso. Un resultado negativo puede ser informativo.|
|Factibilidad y reproducción|20%|Primer artefacto revisable en ≤60 minutos; dependencias, presupuesto y coste de revisión y oportunidad.|
|Transporte y selección|15%|Fechas, escaneos, regiones, condiciones y no detecciones; vecinos o regímenes dependientes no equivalen a réplicas independientes.|
|Utilidad interpretativa|10%|Distinguir demostrado, desconocido y condicionado; especificar qué decisión cambia.|

Reglas no compensables: desconocido no equivale a cero; no inventar verdad física, causalidad o G1; no sustituir el primary negativo por un año, unidad, promedio o secundario favorable; no modificar producción. Cambiar representación exige control equivalente. Variables nuevas sobre fechas consultadas no constituyen holdout nuevo. G1 falso limita las afirmaciones, pero permite experimentos condicionales acotados.

Notas de 1 a 5 por criterio, con evidencia y rango cuando corresponda. Lo desconocido se marca no evaluable o como intervalo, sin redistribuir pesos. Si los intervalos se superponen, la comparación puede quedar indeterminada.

## Opciones comunes de la fase 2

**A. Contexto en las celdas de actividad.** El contexto medio comunal de 23 falló su prueba principal. Construir una representación de cobertura terrestre 2010 sobre las mismas celdas 0,01° y rasgos derivados únicamente de Aqua para cada consulta; ningún target SNP reservado puede definir rasgos. Primer artefacto: cubo y balances de masa, sin nueva grilla de parámetros ni modelo seleccionado por resultados. Distinguir contexto local insuficiente de promedio comunal demasiado grueso. MCD12Q1 reprocesado en 2022 sigue siendo retrospectivo, no información disponible en 2012.

**B. Operadores nominales emparejados en los dos casos L2 existentes.** Validación dimensional MODIS pasó en ambos casos; VIIRS pasó sólo 13 referencias del mismo escaneo 2023. Primer artefacto: partición geométrica y ledger de retención, antes de concordancia. Fijar propiedad en superposiciones por geometría antes de QA/actividad (prioridad de escaneo más temprano, último como sensibilidad), luego átomos comunes. Positivos registrados 7–9 se conservan; nubes/glint/no procesado son desconocidos; M13 no nominal es eje de sensibilidad, no borra positivos conocidos. Registrar clases 3/5 como no detección observada bajo el operador. Geometría nominal no es PSF ni área quemada. Desplazamientos 75/150 m y prioridades son escenarios, no IC. Si el resultado cambia con estas elecciones, resolver representación; si persiste, orientar próxima pregunta instrumental. G1 físico sigue falso y Suspect global sigue sin semántica L2 resuelta.

**C. Sensibilidad del modelo congelado al contrato de producto.** Nuevo protocolo futuro para panel común 20A: 3456 filas, 54 comunas, julio 2020–diciembre 2025 excluyendo agosto/septiembre 2020. Factorial entrada Aqua C/O × target NOAA20 C/O; seis estimadores fijos de 18, sin refit, presupuesto coherente sobre las 54. C es contrato científico; O contrato real publicado. Reproducir CC primero sobre las mismas fechas, no comparar con el score previo de 3780 filas. Para f,g fijos, el cambio absoluto de ganancia por target está acotado por 2 media|Yc−Yo|; en 20A es 2×220/3456. Primer artefacto: identidad CC y cotas antes de nuevos rankings. Si estable, priorizar otra fuente; si cambia ranking, acordar contrato antes de ajustar. Es sensibilidad de definiciones, no validación física ni prueba de bridge SNP–NOAA20.

**D. Evidencia de tercer instrumento/caso documentado.** Preflight metadata, QA, proyección y tiempo de GOES16 ABI-L2-FDCF alrededor del caso fijo 2023, o evidencia oficial de incidente con fechas/imágenes alineadas. Primer artefacto ≤60 min; nuevo presupuesto independiente ≤50 MiB y sin cuentas ni cargos. Selección por metadata antes de actividad, sin rescatar positivos. Un instrumento de resolución más gruesa triangula pero no prueba ausencia a 375 m; correlaciones de nubes y algoritmos persisten. Si no hay evidencia localizada y temporalmente útil, declarar G0 negativo y detener.

**E. Observabilidad mediante productos gridded existentes.** Preflight de catálogo/esquema antes de descargar un piloto ≤50 MiB. NASA documenta MYD14A1 como máscaras diarias empaquetadas en ocho días, compuestos diarios de clases L2, no historia completa de cada pasada. VNP14A1 deriva de bandas de 750 m: no equivale a VNP14IMG de 375 m. Verificar si QA/clases permiten un proxy explícito de oportunidad sin confundir compuesto con denominador físico. Primer artefacto: tabla de operadores, historia, campos, pérdidas por composición y compatibilidad. Si proxy utilizable, protocolo de calendario consciente de faltantes; si no, volver a L2 sin dividir conteos por fracción despejada no comparable.

Fuentes verificadas para E: [NASA MYD14A1](https://data.nasa.gov/dataset/modis-aqua-thermal-anomalies-fire-daily-l3-global-1km-sin-grid-v061-a6350), [guía MODIS C6 §5.2](https://www.earthdata.nasa.gov/s3fs-public/imported/MODIS_C6_Fire_User_Guide_B.pdf), [guía VIIRS](https://lpdaac.usgs.gov/documents/427/VNP14_User_Guide_V1.pdf). Ninguna compatibilidad adicional de campos ha sido demostrada todavía.

La fase 2 solicita votos independientes sobre estas mismas opciones. Todavía no se ha elegido una opción ni ejecutado un nuevo experimento por sus notas.

## Resultado de ambos consejos

C recibió la mayor prioridad operativa de los tres miembros multifocales: media descriptiva86,33–89,33/100. B72–75,67,E69–76,A68,33–71,33,D49,67–73,67; los rangos son juicios, no intervalos de confianza ni réplicas independientes. Las posiciones secundarias no son un consenso estadístico. El adversario acotóC a60minincluidarevisión, exigiócontratospor significado yno porganador, cotasaplicables,estratosfijosyledgerpositivosexcluidos. Los seisratificaron el plan conjunto separado.
