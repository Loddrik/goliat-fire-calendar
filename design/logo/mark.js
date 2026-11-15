// GOLIAT · marca "Dos sensores, una llama" (elegida por Rubén el 15-11-2026, propuesta 02 de design/logo/v3/).
// Fuente única de la geometría del logo. Lienzo de 128 × 128.
// Una sola llama partida en dos: la mitad izquierda en líneas de barrido (MODIS, el registro largo desde 2002)
// y la derecha sólida en la rampa térmica (VIIRS, desde 2012). Dos sensores leídos en la misma escala.
// Reemplaza a C1 "Señal de calor" (14-11-2026). Sin anillo alrededor y sin llama sola en rojo plano.

const THEMES = {
  light: { stripe: '#2B7BB9', hot: ['#FDB022', '#F06A1D', '#C7302A'] },
  navy:  { stripe: '#9ECAE1', hot: ['#FFC24B', '#FF8A3D', '#F0553F'] },
  print: { stripe: '#000000', hot: ['#000000', '#000000', '#000000'], flat: true },
};

// Llama base: punta en (64, 14), base en y = 116. Va espejada para que la lengua secundaria quede en la mitad sólida.
const FL = 'M64 14 C74 32 96 50 96 80 C96 101 81 116 64 116 C47 116 32 101 32 80 C32 64 41 54 48 44 C50 55 54 60 59 62 C56 47 57.5 30 64 14 Z';
const MIRROR = 'translate(128 0) scale(-1 1)';
// La llama se agranda 1,2 veces sobre su centro para llenar el cuadrado (queda entre y = 3,8 y y = 126).
const FIT = 'translate(64 65) scale(1.2) translate(-64 -65)';
// Separación entre las dos mitades: la izquierda termina en x = 62,5 y la derecha parte en x = 65,5.
const SPLIT = [62.5, 65.5];
// Ancho visible de la llama ya agrandada (x = 64 ± 32 × 1,2): los logotipos horizontales recortan a esto.
const INK_X = [25.6, 102.4];

let _uid = 0;
const uid = p => `${p}${++_uid}`;

// stripe: [alto, paso] de las líneas de barrido. La versión grande usa líneas finas; la chica, gruesas y pocas.
function body(theme, stripe) {
  const t = THEMES[theme];
  const [h, step] = stripe;
  const L = uid('gl'), R = uid('gr'), F = uid('gf'), G = uid('gg');
  const rows = [];
  for (let y = 12; y < 120; y += step) rows.push(`<rect x="20" y="${y}" width="44" height="${h}"/>`);
  const fill = t.flat ? t.hot[2] : `url(#${G})`;
  const grad = t.flat ? '' : `<linearGradient id="${G}" gradientUnits="userSpaceOnUse" x1="64" y1="116" x2="64" y2="14">
      <stop offset="0" stop-color="${t.hot[0]}"/><stop offset=".55" stop-color="${t.hot[1]}"/><stop offset="1" stop-color="${t.hot[2]}"/></linearGradient>`;
  return `<defs>${grad}
      <clipPath id="${L}"><rect x="0" y="0" width="${SPLIT[0]}" height="128"/></clipPath>
      <clipPath id="${R}"><rect x="${SPLIT[1]}" y="0" width="${128 - SPLIT[1]}" height="128"/></clipPath>
      <clipPath id="${F}"><path d="${FL}" transform="${MIRROR}"/></clipPath></defs>
    <g transform="${FIT}">
      <g clip-path="url(#${L})"><g clip-path="url(#${F})" fill="${t.stripe}">${rows.join('')}</g></g>
      <g clip-path="url(#${R})"><path d="${FL}" transform="${MIRROR}" fill="${fill}"/></g>
    </g>`;
}

// Marca completa (≥ 48 px): líneas de 4 con paso 7.
function markBody(theme) { return body(theme, [4, 7]); }
// Marca chica (≤ 32 px): líneas de 9 con paso 16, para que a 16 px sigan siendo líneas y no un gris.
function smallBody(theme) { return body(theme, [9, 16]); }

function mark(theme, size, label = 'GOLIAT') {
  return `<svg viewBox="0 0 128 128" width="${size}" height="${size}" role="img" aria-label="${label}">${markBody(theme)}</svg>`;
}
function small(theme, size, label = 'GOLIAT') {
  return `<svg viewBox="0 0 128 128" width="${size}" height="${size}" role="img" aria-label="${label}">${smallBody(theme)}</svg>`;
}
if (typeof module !== 'undefined') module.exports = { THEMES, FL, INK_X, markBody, smallBody, mark, small };
