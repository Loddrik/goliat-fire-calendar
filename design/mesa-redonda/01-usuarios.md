# Mesa redonda · Informe 1 — Voz de los usuarios (agente `usuario-terreno`, 14-11-2026)

Fuentes: `municipios-autoridades.md` [MUN], `combatientes-y-rural.md` [COMB], `cientificos-prensa-datos.md` [CIEN], `vecinos-ciudadania.md` [VEC], `manifiesto.md` [MAN], todos bajo `/Users/loddrik/projects/personal/nasa-space-challenge/docs/`.

## 1. Usuarios por prioridad [MAN §2]

1. **Principal: encargado municipal de emergencias / SECPLAN.** Decide cómo caracterizar la amenaza en el anexo "incendio forestal" del Plan Comunal (Ley 21.364) y qué cifra defender ante el Comité Comunal y el GORE entre agosto y octubre [MAN; MUN h.1, 7]. Sin profesional SIG; copia tablas a mano (Coihueco: tabla de 7 temporadas que no cuadra con su texto) [MUN h.7].
2. **Beneficiario visible: dirigenta vecinal / familia / apicultor.** Decide qué limpiar en invierno y dónde exigir cortafuegos; dónde reconstruir o poner colmenas [VEC h.4, 11; COMB B3].
3. **Secundario: investigador y periodista de datos.** Decide si "esta temporada es peor que lo normal" en una comuna sin esperar el cierre CONAF; calibra su dataset comunal [CIEN H6, H13].
4. **Nombrados, no diseñados: CONAF/SENAPRED/CORMA.** Ya tienen SIDCO [MAN §2].
5. **Para quién NO es:** nadie durante el incendio [MAN §2].

## 2. La pregunta que traen, en sus palabras

- Encargado: "¿En qué meses se concentra el fuego en mi comuna y cómo lleno el cuadro de ocurrencia por temporada sin esperar a CONAF?" [MUN idea A]. Alcalde: "¿Es verdad que esto es 'sin parámetro antes visto'?" (Quillón 2026, dicho de memoria) [MUN h.9].
- Dirigenta El Maitén: "¿Dónde y en qué meses tengo que ir a levantar riesgos en invierno?" [VEC h.11]. Vecina de Santa Juana: "¿Esto ya pasó aquí antes?" / "nunca pensamos que el incendio de Nacimiento iba a venir para acá" [VEC h.2, 4].
- Apicultor Cabrero: "¿En qué sectores reparto las colmenas?" [COMB B3].
- Periodista: "¿Este noviembre es peor que un noviembre normal en Penco, con fecha de corte y fuente?" [CIEN H13; COMB A8].
- Investigador: "¿Me das la serie por CUT, año, mes, con incertidumbre, para unirla a mi tabla CONAF?" [CIEN H6].
- SEREMI/ciudadanía Ñuble: "¿Las quemas se amontonan los días antes de la veda?" [VEC h.12] (fuera de alcance: no separamos quema de incendio [MAN §3]).

## 3. Glosario

| Decir así | No decir | Motivo |
|---|---|---|
| "actividad de fuego detectada", "detecciones", "celdas-día" | "incendios", "focos" como sinónimo de incendio, "hectáreas" | Una detección no es un incendio ni una hectárea; FAQ FIRMS [CIEN H12]; CONAF cuenta incendios por comuna de origen [MAN §1] |
| "temporada 2024-25 (jul–jun)" | "año 2024" | Así piensan CONAF y los planes [MUN h.7; COMB A5] |
| "comparado con lo habitual en esta comuna para esta fecha" | "riesgo", "alerta", "pronóstico", "predicción" | Prohibido; para la emergencia manda Botón Rojo [MAN §2]; 94 % de la gente ya piensa en culpables, no en recurrencia [VEC contexto CADEM] |
| "sectores con detecciones en N temporadas" | nombres de predios, empresas, "zona de culpables" | El mapa son celdas de 375 m, no predios [MAN §3]; la intencionalidad es judicial [MUN h.14] |
| "quemas y incendios juntos: el satélite ve calor" | "quemas ilegales", "quema autorizada" | No distinguimos causa [COMB idea 3] |
| **Observado:** "lo vio el satélite VIIRS (desde 2012)" | "dato real", "medido" | "Real" sugiere que lo otro es falso |
| **Estimado:** "calculado a partir del satélite antiguo (Aqua), con error típico de ±X" | "reconstruido", "interpolado", "modelado", "proyección" | Palabras de técnico; "proyección" suena a pronóstico |
| **No habilitado:** "aquí no mostramos estimación porque la prueba no fue suficiente en esta comuna" | "sin datos", "N/A", "∅" solo | "Sin datos" se lee como "no hubo fuego" [MAN compuertas] |
| **Provisional:** "últimos días, cifras preliminares que pueden cambiar" | "NRT", "near real-time", "tiempo real" | CONAF usa "Información Preliminar por Confirmar" y la gente lo entiende [CIEN H13]; "tiempo real" promete alerta |
| "corte: 10-11-2026" | "última actualización" | Periodistas comparan "mismo período" sin corte explícito; necesitan la fecha [CIEN H13] |

## 4. Contexto de uso

- **Encargado municipal:** notebook de oficina, Windows, Word; pega el cuadro en el PDF del plan e imprime para SENAPRED (planes en PDF escaneado) [MUN h.7]. Implica: vista A4 en blanco y negro con fuente y corte al pie; los tres estados por trama/texto, no solo color; tabla copiable [MAN §3].
- **Alcalde/concejal:** celular, una frase para el oficio o la sesión [MUN idea B]. Implica: un número con fecha y fuente arriba, copiable.
- **Vecinos/dirigentes:** celular, señal rural intermitente; la información corre por el chat de la junta de vecinos [VEC h.1, 11]. Implica: ficha de comuna que quepa en una captura de WhatsApp, letra grande, un solo scroll, sin depender del mapa interactivo para entender.
- **Periodista/investigador:** notebook; exportan PNG y CSV [CIEN tabla §]. Implica: botón CSV visible y figura con fuente incrustada.
- Comunas rurales pequeñas sin equipo técnico [MUN h.2]: cero jerga en la primera pantalla.

## 5. Primeros 10 segundos vs. después

**Primeros 10 s:** (1) nombre de la comuna y temporada en curso; (2) una frase: "hasta el [corte], X detecciones, vs. Y habitual a esta fecha"; (3) los meses donde se concentra la actividad, visibles en el calendario; (4) la leyenda observado/estimado/no habilitado con palabras; (5) "no es alerta; para emergencias, Botón Rojo/SENAPRED".
**Después:** mapa de recurrencia con su advertencia; método, error típico y compuertas; descarga CSV e impresión; comunas vecinas (el fuego vino de Nacimiento [VEC h.2]); fuente, licencia, versión de datos.

## 6. Qué lo haría desconfiar

- Número sin fecha de corte ni fuente (vivieron la disputa de cifras Penco–SENAPRED) [VEC h.8].
- Mezclar observado y estimado en una misma barra o color; "estimado" sin error [MAN §3].
- Que diga "incendios" o "hectáreas" cuando CONAF le da otra cifra; que no cuadre y no explique por qué (quemas agrícolas que CONAF no registra) [CIEN H5].
- Mapa que parezca señalar un predio o una forestal [MAN regla 4].
- Cualquier olor a alerta o pronóstico: un brigadista lo desarma de inmediato [MUN dolores 1].
- Celda vacía que no distinga "no hubo detección" de "no habilitado" o "nublado" [MAN §5].
- Que el p90 con 14 temporadas se presente como certeza [CLAUDE.md regla 5].
