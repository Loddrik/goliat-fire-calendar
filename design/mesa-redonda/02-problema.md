# Mesa redonda · Informe 2 — Análisis de problema (agente analista, 14-11-2026)

Fuentes: `manifiesto.md` (M), `decisiones.md` (D), `CLAUDE.md` (C), `method.md` (Me), `alcances.md` §2 (A), `investigacion/criterios-revisores.md` (CR, rúbrica J10–J15 y P4–P6).

### 1. El problema en una frase
El encargado municipal de emergencias de Biobío/Ñuble no puede decir en qué meses se concentra la actividad de fuego de su comuna ni si la temporada en curso va fuera de lo normal, porque hoy caracteriza la amenaza con una tabla de CONAF que llega con dos temporadas de atraso, sin meses, y la copia a mano (M §1). FIRMS crudo no lo resuelve: MODIS (1 km, 2000→) y VIIRS (375 m, 2012→) no son comparables (VIIRS ve ~2,3× más), juntarlos produce un salto falso en 2012 y MODIS se apaga en 2026–27 (M §1, Me §1). Las familias, además, "no saben que viven en un lugar que se quema cada tantos años" (Lirquén 2026, M §1).

### 2. Qué promete y qué no
**Promesa:** "antecedentes reproducibles de actividad de fuego mensual por comuna, con lo observado, lo estimado y sus límites a la vista, para complementar la planificación municipal y la preparación de las familias" (M §2). Dos preguntas: ¿en qué meses se concentra? y ¿cómo va esta temporada vs. las anteriores, mismo territorio, mismo corte? (M §2).

**Prohibido en lenguaje (C regla 1):** "incendios", "hectáreas", "alerta", "riesgo", "pronóstico", "predicción". Se usa "actividad de fuego detectada", "celdas-día", "detecciones". Tampoco "calendario de quemas" (término legal de CONAF, D 14-11).
**Prohibido en alcance (M §3, C regla 3–4):** alerta, pronóstico, clasificación quema/incendio, comparación con CONAF, clima, población, IA/chat, polígono libre, Terra, noche. Nadie "durante" el incendio: para la emergencia, Botón Rojo de CONAF y SENAPRED. "Herramienta para ayudarse en la planificación, no plan listo." Nunca nombrar predio, empresa o persona. Ningún número se calcula en la web (C, A §1).
**Textos fijos obligatorios:** "una detección no es un incendio; una celda-día no es una hectárea" (Me §6, CR P6); "un mes con cero detecciones puede ser nublado, no sin fuego" (Me §6); acknowledgement FIRMS y disclaimer LANCE visibles (CR P5).

### 3. Los tres estados y lo provisional
Siempre visibles y distinguibles sin color (C regla 2, M §3):
- **Observado**: VIIRS diurno, S-NPP 2012–2017 y NOAA-20 desde 2018, una plataforma por temporada (Me §5). Es el único estado que entra en comparación de temporada y mapa de recurrencia.
- **Estimado**: Aqua × 2,353, solo jul-2002→jun-2012 y solo en las **14 de 54** comunas que pasan las compuertas; cada celda lleva su **"error típico"** (± MAE LOSO; cobertura 70 %/88 % a ±2; "no es una banda de confianza") (Me §4–5, D 14-11). Error relativo típico ~35 %.
- **No habilitado (∅)**: las otras 40 comunas antes de 2012; se muestra el porqué (poca Aqua / no supera climatología / no supera Aqua crudo) (Me §4). El JSON trae `gates{}` para eso (A §2).
- **Provisional (NRT)**: meses tocados por datos NRT, que FIRMS reemplaza a ~5 meses (Me §2); marca explícita, no solo color (C regla 2, CR P12).
Para distinguir sin color: etiqueta de texto o glifo por celda (ej. valor liso / valor con "± e" / "∅"), textura o borde, leyenda con los tres estados siempre a la vista y tabla equivalente accesible por teclado (M §3).

### 4. Jerarquía propuesta para una sola pantalla
1. **Primero (la pregunta 1):** comuna seleccionada + calendario mes × temporada con los tres estados y la leyenda pegada. Lectura en 5 s: qué meses concentran actividad (CR P13). Corte de datos visible (M §4).
2. **Segundo (la pregunta 2):** "¿cómo va esta temporada?": acumulado al día de corte vs. mediana/p25/p75/p90 de 14 temporadas observadas, truncadas al mismo día; avisar que el p90 es débil (C regla 5, Me §5).
3. **Tercero:** mapa de recurrencia (nº de temporadas con detección por celda, 2013→) con la advertencia fija "detecciones de 375 m, no predios ni incendios" (M §3).
4. **Plegable:** "Cómo armonizamos" (factor 2,353, compuertas de la comuna, error típico, limitaciones), fuentes y citas, descargas CSV (serie + detecciones), imprimir, ES/EN. Recorrido obligatorio: comuna → calendario → temporada → mapa → método → imprimir/CSV (M §3). Pantalla, impresión y CSV: mismos números (C regla 6).

### 5. Lo que evalúa el jurado (CR J10–J14) y qué debe mostrar la pantalla
- **Impact:** usuario con nombre (encargado municipal / familias), decisión (plan comunal Ley 21.364; preparar el entorno) y alcance (54 comunas). Sin cifras de hectáreas.
- **Creativity:** lo que los repos rivales no tienen: incertidumbre visible, temporada jul–jun, estados honestos, recurrencia, vista imprimible.
- **Validity:** panel de método accesible desde la principal con validación fuera de muestra (LOSO: M0 1 080,6 · M1 881,2 · M2 1 335,2), compuertas por comuna y limitaciones (nubes, quemas, fin de S-NPP, deriva de Aqua) (Me §3–6).
- **Relevance:** FIRMS como núcleo: calendario, mediana, CSV.
- **Presentation:** se entiende sin contexto; una comuna que pasa compuertas y una que no, para mostrar cómo se comunica el límite (M §7).
Puntuar bien sin exagerar = mostrar el límite como rasgo, no como pie de página.

### 6. Tres riesgos de diseño que violan el manifiesto
1. **Mapa que parece de culpables:** recurrencia con zoom a predio, tooltip con lugar o color "rojo peligro" sin la advertencia fija → viola C regla 4 y M §3.
2. **Número sin su estado:** celda estimada sin "error típico", o 2002–2012 pintado igual que lo observado, o distinción solo por color → viola C regla 2 y Me §4 ("no es banda de confianza").
3. **Lenguaje o afordancia de alerta:** semáforos, "riesgo alto", "pronóstico de temporada", botón de "alerta", o p90 presentado como umbral firme → viola C reglas 1, 3 y 5 y CR P4. Añadido: cualquier dato que no venga de `web/public/data/` (A §1).
