# Ronda 2 · Voz de los usuarios (sobre 02-problema.md y 03-app-actual.md)

## 1. De acuerdo
Calendario como respuesta a la pregunta 1; "para quién" arriba, no al pie (P3 bloqueante); quitar veredicto y KPI p90; mapa con título y aviso que impidan la lectura de culpa; reencuadrar "no habilitada" como "serie observada 2012→" sin chip naranjo; nada que no esté en el JSON.

## 2. Donde no coincido
- **El calendario no va primero: primero una frase.** El encargado lee tablas; la dirigenta, el alcalde y el periodista leen una línea y la mandan por WhatsApp. Esa línea sale sin calcular nada: `season_compare.current`, `median`, `n`, `cutoff_day`. Si ponemos 25 filas × 14 columnas arriba, el vecino de Lirquén cierra la pestaña. Jerarquía: frase → calendario → temporada → mapa.
- **La ficha WhatsApp no es otra pantalla**, es el encabezado bien hecho: comuna, corte, frase, leyenda. Una captura del primer scroll debe bastar.
- **No pedir fila de mediana por mes** para esta entrega: no está en el JSON y es issue `ciencia`. El usuario lee los meses altos por los números mismos.
- **Mapa: conservar n = 1**, más tenue. Para la señora de El Maitén "aquí pasó una vez" es información; para la lectura de culpa lo que importa es el aviso fijo, no esconder datos.

## 3. Pantalla única, de arriba a abajo
- **Título:** "GOLIAT · Actividad de fuego detectada por satélite". **Subtítulo:** "Biobío y Ñuble, 54 comunas, 2002–2026. Datos NASA FIRMS (MODIS y VIIRS), puestos en una sola escala."
- **Para quién:** "Para quien prepara su comuna antes de la temporada: planes comunales, juntas de vecinos, prensa e investigación. No es una alerta ni un pronóstico. En una emergencia: CONAF (Botón Rojo) y SENAPRED."
- **Encabezado de comuna:** "Penco · Biobío · CUT 08107" / "Datos hasta el 13-11-2026 · Serie 2002–2026: observada desde 2012, estimada antes" (o "Serie observada 2012–2026; antes de 2012 no habilitada").
- **Bloque 1 "En una línea":** "Temporada 2026-27, hasta el 13 de noviembre: 12 celdas-día con detección. En 14 temporadas anteriores, a esta misma fecha, la mitad llevaba 9 o menos."
- **Bloque 2 "¿En qué meses se concentra?"** Subtítulo: "Celdas-día con detección por mes y temporada (julio a junio)."
- **Bloque 3 "¿Cómo va esta temporada?"** Subtítulo: "Acumulado al 13-11, comparado con las 14 temporadas observadas al mismo día. Pocas temporadas: compara con cuidado."
- **Bloque 4 "¿Dónde se ha repetido?"** Subtítulo: "Temporadas con detección por sector, 2012–2026."
- **Bloque 5 (plegado) "Cómo se hizo y qué no muestra".**
- **Bloque 6 "Llevar":** "Imprimir / PDF · CSV de la serie · CSV de detecciones".
- **Leyenda:** "Observado — lo vio el satélite VIIRS (desde julio 2012)." / "Estimado ± — calculado desde el satélite Aqua (2002–2012); el ± es el error típico." / "— No habilitado — en esta comuna no estimamos 2002–2012: la prueba no fue suficiente." / "Provisional (·) — últimos meses, cifras preliminares que FIRMS corrige en unos 5 meses."
- **Aviso del mapa (fijo, bajo el mapa):** "Cada cuadro es una detección satelital de 375 m, no un predio, una empresa ni un incendio. Indica en cuántas temporadas hubo detección ahí."
- **Pie:** "Datos: NASA FIRMS (MODIS/VIIRS), usados tal cual · Límites: geoBoundaries/BCN · Mapa: OpenFreeMap. Una detección no es un incendio; un mes en cero puede haber estado nublado. Código abierto, Apache 2.0."

## 4. Tres estados sin color
- Observado: número liso, fondo rampa de un solo tono.
- Estimado: número **seguido de "±e" en cuerpo menor** ("41 ±14"), fondo con trama diagonal gruesa (≥ 4 px), nunca cursiva sola.
- No habilitado: celda blanca con "—" centrado, sin trama (lo "vacío" se lee como "no mostramos", no como cero).
- Provisional: punto "·" tras el número y borde punteado.
- **Regla horizontal con rótulo** entre 2011-12 y 2012-13: "↓ estimado (Aqua) · ↑ observado (VIIRS)".
En blanco y negro sobreviven los cuatro: número, "±", "—", "·", trama, borde y la regla. La rampa pasa a grises; el dato lo carga el número.

## 5. Celular
Primero: encabezado de comuna + "En una línea" + leyenda (una captura). Selector arriba como buscador plegable, no lista de 180 px. Calendario: por defecto las últimas 6 temporadas, botón "ver 2002–2026" (filtro, no cálculo); scroll horizontal con la columna de temporada fija. Temporada: barras a ancho completo con la mediana como línea y valores. Mapa plegado ("Ver dónde se ha repetido"), carga al tocar. "Llevar" al final, botones en dos filas.

## 6. Veto y conserva
**Veto:** el veredicto en cursiva ("sobre el percentil 90") y el KPI p90: se calculan en la web y suenan a alerta. **Conservar sí o sí:** "Datos hasta {corte}" junto al nombre de la comuna y la temporada julio–junio como fila; es lo que el encargado pega en su plan y lo que el periodista necesita para citar.
