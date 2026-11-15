// Ronda 2 (15-11-2026): Rubén eligió 13 curva de temporada, 14 A de barrido, 02 dos sensores y 05 barrido.
// Aquí van los híbridos de esas cuatro y los sistemas marca + logotipo (la A de GOLIAT como haz).
const { P, D, FL, SEASON, sat, grad, scaleAbout, id, mix, fns } = require('./marcas.cjs');

// Franjas horizontales recortadas por una silueta; el color va de frío (abajo) a caliente (arriba).
const RAMP = c => ['#1F6F8B', c.sky, c.amber, c.orange, c.red];
function rampAt(c, t) { // t: 0 abajo (frío) → 1 arriba (caliente); colores puros, sin mezclas turbias
  const r = RAMP(c);
  return r[Math.min(r.length - 1, Math.floor(t * r.length))];
}
function franjas(c, y0, y1, paso, alto, x0 = 0, x1 = 128) {
  const out = [];
  for (let y = y1 - alto; y >= y0; y -= paso) {
    out.push(`<rect x="${x0}" y="${y.toFixed(1)}" width="${x1 - x0}" height="${alto}" fill="${rampAt(c, (y1 - y) / (y1 - y0))}"/>`);
  }
  return out.join('');
}

// ── H1 Temporada barrida (13 + 05): la silueta de la temporada leída en líneas de barrido,
// frías en los meses tranquilos y calientes en el pico; el satélite arriba del máximo.
function temporadaBarrida(c) {
  const k = id('tb');
  const T = scaleAbout(0.8, 64, 112);
  const ticks = Array.from({ length: 12 }, (_, i) => {
    const x = 12 + i * (104 / 11);
    return `<line x1="${x.toFixed(1)}" y1="119" x2="${x.toFixed(1)}" y2="${i === 6 || i === 7 ? 125 : 122.5}" stroke="${c.navy}" stroke-width="2.2" stroke-linecap="round"/>`;
  }).join('');
  const g = id('tg');
  const r = RAMP(c).slice(0, 3);
  const rows = [[104, r[0]], [94, r[1]], [84, r[2]]].map(([y, f]) => `<rect x="0" y="${y}" width="128" height="7" fill="${f}"/>`).join('');
  return `<defs><clipPath id="${k}"><path d="${SEASON}" transform="${T}"/></clipPath>
      ${grad(g, [[0, c.amber], [0.5, c.orange], [1, c.red]], 0, 81, 0, 36)}</defs>
    <g clip-path="url(#${k})">${rows}<rect x="0" y="30" width="128" height="51" fill="url(#${g})"/></g>
    <line x1="6" y1="114.5" x2="122" y2="114.5" stroke="${c.navy}" stroke-width="3" stroke-linecap="round"/>${ticks}
    ${sat(c, 72, 15, 0.78, 0)}`;
}

// ── H2 Dos sensores barridos (02 + 05): la mitad izquierda son las líneas del barrido (MODIS, el registro largo),
// la derecha es sólida (VIIRS); el satélite que lee las dos, arriba.
function sensoresBarridos(c) {
  const L = id('sl'), R = id('sr'), F = id('sf'), g = id('sg');
  const T = scaleAbout(0.8, 64, 118);
  return `<defs>
      <clipPath id="${L}"><rect x="0" y="0" width="62.5" height="128"/></clipPath>
      <clipPath id="${R}"><rect x="65.5" y="0" width="64" height="128"/></clipPath>
      <clipPath id="${F}"><path d="${FL}" transform="${T} translate(128 0) scale(-1 1)"/></clipPath>
      ${grad(g, [[0, c.amber], [0.55, c.orange], [1, c.red]], 64, 118, 64, 36)}
    </defs>
    <g clip-path="url(#${L})"><g clip-path="url(#${F})">${franjas(c, 36, 118, 9, 6)}</g></g>
    <g clip-path="url(#${R})"><path d="${FL}" fill="url(#${g})" transform="${T} translate(128 0) scale(-1 1)"/></g>
    ${sat(c, 64, 14, 0.78, 0)}`;
}

// ── H3 A barrida (14 + 05): la A es el haz; adentro, las líneas del barrido se calientan hasta la brasa
// de la base. En la punta, el satélite reemplaza al punto.
function aBarrida(c) {
  // Bordes interiores de la A: de (64, 56) a (37, 116) y a (91, 116).
  const lines = [[70, '#1F6F8B'], [81, c.sky], [92, c.amber]].map(([y, col]) => {
    const h = (y - 56) * 27 / 60 - 3.2;
    return `<line x1="${(64 - h).toFixed(1)}" y1="${y}" x2="${(64 + h).toFixed(1)}" y2="${y}" stroke="${col}" stroke-width="6" stroke-linecap="round"/>`;
  }).join('');
  return `<path d="M54 30 H74 L116 116 H91 L64 56 L37 116 H12 Z" fill="${c.navy}"/>
    ${lines}
    <path d="${FL}" fill="${c.orange}" transform="translate(64 116) scale(.2) translate(-64 -116)"/>
    <path d="${FL}" fill="${c.amber}" transform="translate(64 116) scale(.11) translate(-64 -116)"/>
    ${sat(c, 64, 15, 0.72, 0)}`;
}

// ── H4 Barrido de temporada (05 + 13): el barrido original, pero las líneas tienen el largo de los meses
// (pocas en invierno, el pico en verano) y la última toca la brasa. Más tranquilo que H1.
function barridoMeses(c) {
  // Largo relativo por línea, de arriba (frío) a abajo (pico); la brasa en el pico.
  const filas = [[38, 16, '#1F6F8B'], [50, 30, c.sky], [62, 44, c.amber], [74, 52, c.orange]];
  const lines = filas.map(([y, half, col]) => `<line x1="${64 - half}" y1="${y}" x2="${64 + half}" y2="${y}" stroke="${col}" stroke-width="8" stroke-linecap="round"/>`).join('');
  const ticks = Array.from({ length: 12 }, (_, i) => {
    const x = 16 + i * (96 / 11);
    return `<line x1="${x.toFixed(1)}" y1="121" x2="${x.toFixed(1)}" y2="125" stroke="${c.navy}" stroke-width="2.2" stroke-linecap="round"/>`;
  }).join('');
  return `${sat(c, 64, 17, 0.95, 0)}${lines}
    <path d="${FL}" fill="${c.orange}" transform="translate(64 114) scale(.32) translate(-64 -116)"/>
    <path d="${FL}" fill="${c.amber}" transform="translate(64 114) scale(.18) translate(-64 -116)"/>
    <line x1="12" y1="116.5" x2="116" y2="116.5" stroke="${c.navy}" stroke-width="3" stroke-linecap="round"/>${ticks}`;
}

const HIBRIDOS = [
  { key: 'temporada-barrida', n: 'H1', nombre: 'Temporada barrida', de: '13 + 05', fn: temporadaBarrida,
    idea: 'La silueta de la temporada leída en líneas de barrido: frías en los meses tranquilos, calientes en el pico. El satélite mira desde arriba del máximo y las doce marcas son los meses. Junta "cómo se mide" con "qué se muestra".' },
  { key: 'sensores-barridos', n: 'H2', nombre: 'Dos sensores barridos', de: '02 + 05', fn: sensoresBarridos,
    idea: 'La llama de dos sensores, con el satélite encima: la mitad izquierda son las líneas del barrido (MODIS, desde 2002), de frío a caliente, y la derecha es sólida (VIIRS, desde 2012). Las dos se leen en la misma escala.' },
  { key: 'a-barrida', n: 'H3', nombre: 'A barrida', de: '14 + 05', fn: aBarrida,
    idea: 'La A de GOLIAT como haz del satélite: adentro, tres líneas de barrido que se calientan hasta la brasa de la base. Sirve de monograma y de letra del nombre, así que marca y logotipo son la misma pieza.' },
  { key: 'barrido-de-meses', n: 'H4', nombre: 'Barrido de meses', de: '05 + 13', fn: barridoMeses,
    idea: 'El barrido original apoyado en la línea de los doce meses: el satélite lee de arriba abajo, cada línea más caliente y más larga, hasta la brasa. Es la versión más tranquila y la que mejor aguanta chica.' },
];

// Las cuatro originales que eligió Rubén, para compararlas al lado.
const ORIGINALES = [
  { key: 'curva-de-temporada', n: '13', nombre: 'Curva de temporada', fn: fns.curvaTemporada },
  { key: 'a-de-barrido', n: '14', nombre: 'A de barrido', fn: fns.aBarrido },
  { key: 'dos-sensores', n: '02', nombre: 'Dos sensores, una llama', fn: fns.dosSensores },
  { key: 'barrido', n: '05', nombre: 'Barrido', fn: fns.barrido },
];

function svg(fn, theme = 'light', size = 128, cls = '') {
  const c = theme === 'dark' ? D : P;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="${size}" height="${size}"${cls ? ` class="${cls}"` : ''} role="img" aria-label="GOLIAT">${fn(c)}</svg>`;
}

// La A del logotipo en dos versiones: la de la ronda 1 (punto ámbar) y la barrida (H3).
// La altura calza con la mayúscula de Archivo Expanded 800 (0,69 em): el cuerpo de la A (y 30→116) mide eso
// y el punto o el satélite sobresalen arriba. Va en línea, con la base del SVG en la línea base del texto.
const CAP = 0.69;
function aGlifo(c, barrida) {
  const h = (CAP * 110 / 86).toFixed(3);
  if (!barrida) {
    const g = id('ag');
    return `<svg class="gla" viewBox="6 6 116 110" style="height:${h}em"><defs>${grad(g, [[0, c.amber], [1, c.orange]], 0, 116, 0, 76)}</defs>
      <path d="M53 30 H75 L120 116 H94 L64 54 L34 116 H8 Z" fill="currentColor"/>
      <path d="${FL}" fill="url(#${g})" transform="translate(64 116) scale(.38) translate(-64 -116)"/>
      <circle cx="64" cy="15" r="8.5" fill="${c.amber}"/></svg>`;
  }
  return `<svg class="gla" viewBox="10 6 108 110" style="height:${h}em">${aBarrida({ ...c, navy: 'currentColor' })}</svg>`;
}

module.exports = { HIBRIDOS, ORIGINALES, svg, aGlifo, theme: t => (t === 'dark' ? D : P) };
