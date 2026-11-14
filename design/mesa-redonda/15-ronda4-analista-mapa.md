# Ronda 4 · El mapa como puerta: posición del guardián del manifiesto

**1. Lo que dicen las fuentes.** El manifiesto pone el mapa como "beneficiario visible" (§2) y "componente" (§3), nunca como producto principal; las dos preguntas que responde GOLIAT son de meses y de temporada (§2), y el recorrido obligatorio parte en "elegir comuna" (§3). Regla 4 (CLAUDE.md): "detecciones de 375 m, no predios ni culpables; nunca se nombra un predio, empresa o persona". Un mapa regional al abrir no está prohibido, pero cambia el centro de gravedad; acepto si cumple **todas** estas condiciones:
- Zoom máximo tal que una celda de 0,01° nunca ocupe más de ~1/20 del viewport (no se puede "apuntar" a un predio); sin búsqueda de dirección ni geocodificación.
- Celdas como cuadrículas de ~1 km, nunca puntos; sin etiquetas de lugar fuera de nombres de comuna.
- Aviso fijo, no cerrable, encima del mapa: "Cada cuadro es una detección satelital de 375 m, no un predio, una empresa ni un incendio." (texto ya corregido en el brief §9: "sector de ~1 km … píxeles de 375 m")
- Rampa secuencial no roja, sin semáforo, sin rótulos "alto/bajo"; n = 1 visible y tenue.
- Popup solo con: comuna, temporadas con detección, días con detección, primera/última temporada. Nada más.
- Vista regional: **sin colorear comunas por total ni ordenar la lista por `current/median`**; la comuna solo se destaca al pasar el cursor. El coropleta comunal sería un ranking = "mapa de riesgo".
- Con el control en "temporada 2026-27", marcar "preliminar (NRT)" y "hasta el 13-11".

**2. Jurado (Validity, Relevance).** El desafío es armonizar MODIS+VIIRS; el mapa es solo VIIRS 2012→ y no la muestra. Para no bajar: (a) la cabecera dice "Serie 2002–2026, MODIS+VIIRS en una sola escala" con enlace "ver método"; (b) al clicar una comuna, el panel lateral abre **primero** el calendario 2002→ con los tres estados, no otra capa del mapa; (c) el control de tiempo del mapa parte en 2012 con rótulo "VIIRS observado desde 2012; 2002–2012 solo en el calendario (estimado)"; (d) la demo y la página muestran el calendario antes del mapa.

**3. Textos permitidos.** Control: "Temporada 2024-25 (jul–jun)", "Mes del año: enero (todas las temporadas 2012→2026)", "Todas las temporadas (2012→2026)". Leyenda: "Días con detección en el sector", "Temporadas con detección en el sector (de 14)". Prohibido: "incendios", "focos", "hotspots" en la UI, "zona caliente", "riesgo", "peligro", "recurrente" como adjetivo del lugar.

**4. Veto:** coropleta o ranking de comunas en la vista regional. **Innegociable:** cada celda del mapa viene de `derived/` con la misma máscara y regla que `publish.py` (verificación cruzada que ya hace `publish_web.py`), y la comparación de temporada y el calendario siguen siendo los únicos lugares con números de 2002→.
