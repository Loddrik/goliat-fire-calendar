# GOLIAT · propuestas de logo v3 (15-11-2026)

Encargo de Rubén (14-11 en la noche): rehacer el logo, "más creativo", con las herramientas de vf-Studio,
al menos 10 propuestas, tope de USD 5 en fal.ai. No reemplaza nada en `web/`: el logo vigente sigue siendo
C1 (`design/logo/mark.js`) hasta que Rubén elija.

## Qué hay

| ruta | qué es |
| --- | --- |
| `marcas.cjs` | Las 16 marcas en SVG (lienzo 128 × 128), tema claro y oscuro. Fuente única de su geometría. |
| `logotipos.cjs` | Cuatro tratamientos del nombre (I termómetro, O isoterma, A haz, goliat con brasa). |
| `build.cjs` | `node build.cjs` arma `propuestas.html` y exporta `svg/NN-nombre[-oscuro].svg`. |
| `propuestas.html` | Una lámina 1080 × 1350 por propuesta, para `vf-lamina`. |
| `render/` | `vf-lamina propuestas.html --out render --min-texto 16`: `slide-N.png`, mini de 150 px y `hoja.jpg`. |
| `exploracion/` | Lo generado con IA (vf-gen): `r1/` Recraft v3 vectorial, `r2/` Nano Banana + Ideogram v3. Cada imagen con su `.json` de procedencia (prompt, modelo, requestId). |
| `ronda2.cjs` | Ronda 2 (15-11 mañana): mezclas H1–H4 de las favoritas de Rubén (13, 14, 02, 05) y la A del logotipo a la altura de mayúscula. `node pagina.cjs` la pone arriba en la página. |
| `GASTOS.md` | Lo gastado en fal.ai, lote por lote. |

## Cómo se hizo

1. Exploración barata con IA (`vf-gen`, lotes en `exploracion/*.json`) para abrir ideas: 15 conceptos en
   Recraft (salieron todos como parches circulares con anillo, que la marca prohíbe: sirvieron solo como
   ideas), 15 símbolos en Nano Banana y 8 logotipos en Ideogram.
2. Las propuestas finales están dibujadas a mano en SVG, no son imágenes generadas: escalan a 16 px,
   tienen versión oscura y se pueden editar. Tres ideas vinieron de la IA (satélite calado, facetas,
   la I como termómetro); el resto son conceptos propios.
3. `vf-lamina` renderiza las láminas y audita recortes y letra chica; el mini de 150 px dice si se entiende.

## Reglas que se respetaron

Sin anillo alrededor de la marca (Space Apps); nada de llama sola en rojo plano (alerta); el producto mide
"actividad de fuego detectada", no incendios ni riesgo. La "curva de temporada" es una silueta estilizada,
no un dato del pipeline.
