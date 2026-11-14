# Ronda 3 · Posición final de la voz de los usuarios

**(a) Orden y frase.** Concedo: calendario primero, frase después, sin adjetivo. El analista tiene razón en que "12 vs. 4" en noviembre se lee como veredicto, y el encargado (usuario principal) necesita la tabla antes que la cifra. No concedo que la frase desaparezca ni que se vuelva dos KPI sueltos: el alcalde y la dirigenta necesitan una oración copiable con fecha y fuente. Redacción exacta (todo sale de `season_compare`, `doc.cutoff`, `months`):
"Temporada 2026-27, hasta el 13 de noviembre de 2026: 12 celdas-día con detección. En las 14 temporadas observadas (2012–2025), al mismo día, la mediana fue 4. Van 5 de los 12 meses de la temporada."
Sin "sobre", "bajo", "normal", "veces". El cierre de los meses recuerda que es temprano sin fijar umbral.

**(b) n = 1 en el mapa.** Concedo atenuarlo al tono más claro y nombrarlo en la leyenda ("1 temporada"). No concedo quitarlo: para la junta de vecinos "aquí hubo detección una vez" es información para limpiar, y un filtro oculto que el CSV de detecciones contradice destruye confianza.

**(c) Mini-cifra y Σ.** Concedo las dos. La mini-cifra `current/median` en la lista es un ranking disfrazado; la lista solo lleva "2012→ / 2002→". La fila Σ se quita de pantalla y CSV hasta que `publish.py` entregue `season_total` (issue `ciencia`): el encargado sí quiere ese total por temporada para su cuadro del plan, pero calculado en el pipeline, no en la web. Comunas vecinas: concedo; basta "toca una comuna vecina en el mapa".
