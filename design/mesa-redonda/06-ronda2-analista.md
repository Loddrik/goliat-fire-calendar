# Ronda 2 · Posición del analista del problema

### 1. Acuerdos
Con el informe 1: prioridad de usuarios, los "primeros 10 s" (comuna, meses, leyenda con palabras, "no es alerta" arriba), la lista de desconfianzas y la vista A4 en blanco y negro. Con el 3: nada que no esté en el JSON se muestra; la web hoy ya calcula de más (veredicto, Σ, máximo de rampa); el rayado fino y la cursiva no bastan como "sin color"; naranjo para "no habilitada" y para "provisional" confunde advertencia con dato nuevo.

### 2. Desacuerdos
- **Frase "X detecciones vs. Y habitual a esta fecha" arriba (inf. 1 §5).** Al 13-11 la temporada lleva 4 meses de invierno y la mediana es chica; "12 vs. 4" se lee "3× lo normal" = veredicto, justo lo que el manifiesto prohíbe y lo que un brigadista desarma (inf. 1 §6). Además el veredicto ("sobre el p90") se calcula en la web (inf. 3 §5). Posición: los dos números se muestran, con fecha y "mediana de 14 temporadas", **sin adjetivo ni frase de juicio**, y después del calendario (pregunta 1 antes que pregunta 2, manifiesto §2). La "frase para el oficio del alcalde" es exactamente ese número con fecha y fuente; no necesita calificativo.
- **Mediana por mes no existe (inf. 3 §2).** No se inventa en la web. "Dónde se concentra" lo responde el calendario mismo: la columna que se oscurece en todas las filas. Se abre issue `ciencia` pidiendo `month_median[]` a `publish.py` (cambio compatible, alcances §2); el diseño deja la fila dibujada como opcional y la app sale sin ella si no llega antes del domingo 11:00. Resaltar "3 meses más altos" también es cálculo: va al pipeline o no va.
- **Σ por fila** (inf. 3 §4): calculada en la web y sin unidad. Pedirla al pipeline o quitarla.
- **Ranking/mini-resumen por comuna con `current/median` en la lista** (inf. 3 §2): es un mapa de alerta disfrazado. No.
- **"Comunas vecinas, el fuego vino de Nacimiento"** (inf. 1 §5): fuera de alcance y roza culpables.

### 3. Glosario (manifiesto, method.md §5–6)
Apruebo: "actividad de fuego detectada / detecciones / celdas-día"; "temporada 2024-25 (jul–jun)"; "sectores con detecciones en N temporadas"; "quemas e incendios juntos: el satélite ve calor"; "corte: 13-11-2026" (no "última actualización"); observado = "lo vio el satélite VIIRS (desde 2012)".
Corrijo:
- **Estimado:** "Estimado 2002–2012: calculado desde el satélite Aqua con un factor regional; error típico ±X celdas-día (acierta 7 de cada 10 meses)". Sin "reconstruido", sin "banda de confianza" (method §4).
- **No habilitado:** la etiqueta técnica se conserva en leyenda y CSV (estado del contrato), pero la celda y la leyenda dicen: "∅ Sin estimación antes de 2012: en esta comuna la corrección no pasó la prueba. No significa cero detecciones." El porqué (Aqua escasa / no mejora a la climatología / no mejora a Aqua crudo) va en el panel de método, no en el chip.
- **"Comparado con lo habitual…":** exigir siempre "mediana de 14 temporadas (2012–2025), hasta el mismo día".
- **Provisional:** "preliminar, puede cambiar (datos NRT, ~5 meses)". NRT queda en paréntesis por trazabilidad.
- "No es alerta" debe incluir "una detección puede ser incendio, quema agrícola o falso positivo" (P6, method §6).

### 4. Orden de bloques (pantalla única)
1. Cabecera: GOLIAT · para quién (encargado municipal, familias) · "No es alerta ni pronóstico; para la emergencia, CONAF y SENAPRED" · corte. (Impact, P3/P4.)
2. Selector de comuna (lista, `· 2012→` / `· 2002→`, nunca ∅ solo).
3. Título de comuna + chip neutro de serie disponible.
4. **Calendario** con leyenda de 4 estados en palabras y texto fijo "una detección no es un incendio" (pregunta 1; P13).
5. **Temporada en curso**: dos números con fecha, barras con línea de mediana, p90 solo en ayuda (pregunta 2; regla 5).
6. **Mapa de recurrencia** con advertencia fija encima, sin n=1 destacado.
7. Botones CSV / imprimir visibles pero secundarios (periodista, investigador).
8. Plegado: "Cómo lo calculamos" con compuertas de la comuna y LOSO de `params` (Validity), fuentes con acknowledgement FIRMS, licencia, IA, ES/EN.

### 5. Lista de verificación (sí/no)
1. ¿Ningún texto dice incendios, hectáreas, alerta, riesgo, pronóstico, predicción, tiempo real?
2. ¿Observado, estimado, ∅ y provisional se distinguen con la pantalla en gris (texto/trama/borde, no solo color)?
3. ¿Cada celda estimada muestra o enlaza su "± error típico"?
4. ¿∅ dice explícitamente que no es cero detecciones?
5. ¿"No es alerta; CONAF/SENAPRED" está arriba, antes de cualquier número?
6. ¿La comparación de temporada no tiene adjetivo ni veredicto, y dice n=14 y "mismo día"?
7. ¿El mapa lleva "detecciones de 375 m, no predios ni incendios" pegado y ningún nombre de predio/empresa?
8. ¿La fecha de corte aparece en pantalla, impresión y CSV?
9. ¿Todo número mostrado existe en `index.json` o `comunas/<cut>.json` (nada derivado en la web)?
10. ¿Acknowledgement FIRMS, geoBoundaries/BCN, OpenFreeMap y licencia visibles o a un clic?

### 6. Veto y conservación
**Veto:** cualquier frase de juicio sobre la temporada ("sobre el p90", "fuera de lo normal", ranking de comunas).
**Conservo sí o sí:** la leyenda de los tres estados + provisional con palabras, siempre visible junto al calendario, con el error típico en cada celda estimada.
