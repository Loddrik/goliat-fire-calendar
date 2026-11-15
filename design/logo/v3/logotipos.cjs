// Cuatro tratamientos del nombre GOLIAT, combinables con cualquiera de las marcas.
// Cada glifo es un SVG que reemplaza una letra; mide 1em de alto (línea base en y = 100 de 128).
const { P, D } = require('./marcas.cjs');

let _id = 0;
const id = p => `lg${p}${++_id}`;
const FL = 'M64 14 C74 32 96 50 96 80 C96 101 81 116 64 116 C47 116 32 101 32 80 C32 64 41 54 48 44 C50 55 54 60 59 62 C56 47 57.5 30 64 14 Z';

// La I como termómetro: tubo con la columna caliente y el bulbo bajo la línea base.
function iTermometro(c) {
  const g = id('t');
  return `<svg class="gl" viewBox="0 0 46 128" style="width:.36em"><defs><linearGradient id="${g}" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0" stop-color="${c.red}"/><stop offset=".5" stop-color="${c.orange}"/><stop offset="1" stop-color="${c.amber}"/></linearGradient></defs>
    <path d="M10 32 A13 13 0 0 1 36 32 V92 A18 18 0 1 1 10 92 Z" fill="${c.navy}"/>
    <path d="M17.5 42 H28.5 V96 A11.5 11.5 0 1 1 17.5 96 Z" fill="url(#${g})"/></svg>`;
}

// La O como llama en curvas de nivel (la isoterma), del mismo ancho que la O.
function oIsoterma(c) {
  const fills = [c.red, c.orange, c.amber, c.pale];
  const sc = [1, 0.72, 0.47, 0.24];
  const m = id('m');
  const cuts = sc.slice(1).map(s => `<path d="${FL}" fill="none" stroke="#000" stroke-width="${(5 / s).toFixed(1)}" transform="translate(63 100) scale(${s}) translate(-63 -100)"/>`).join('');
  return `<svg class="gl" viewBox="28 14 72 104" style="width:.74em"><defs><mask id="${m}" maskUnits="userSpaceOnUse" x="0" y="0" width="128" height="128"><rect width="128" height="128" fill="#fff"/>${cuts}</mask></defs>
    <g mask="url(#${m})" transform="translate(0 -6)">${fills.map((f, i) => `<path d="${FL}" fill="${f}" transform="translate(63 100) scale(${sc[i]}) translate(-63 -100)"/>`).join('')}</g></svg>`;
}

// La A como haz del satélite: sin travesaño, el punto ámbar arriba y la llama en la base.
function aHaz(c) {
  const g = id('a');
  return `<svg class="gl" viewBox="10 0 108 128" style="width:.86em"><defs><linearGradient id="${g}" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0" stop-color="${c.amber}"/><stop offset="1" stop-color="${c.orange}"/></linearGradient></defs>
    <path d="M54 30 H74 L114 116 H90 L64 58 L38 116 H14 Z" fill="${c.navy}"/>
    <path d="${FL}" fill="url(#${g})" transform="translate(64 116) scale(.36) translate(-64 -116)"/>
    <circle cx="64" cy="15" r="8" fill="${c.amber}"/></svg>`;
}

// El punto de la i minúscula es una brasa.
function puntoBrasa(c) {
  return `<svg class="gl" viewBox="0 0 40 128" style="width:.31em"><path d="${FL}" fill="${c.orange}" transform="translate(20 41) scale(.3) translate(-64 -116)"/>
    <path d="${FL}" fill="${c.amber}" transform="translate(20 41) scale(.15) translate(-64 -116)"/>
    <rect x="8" y="49" width="24" height="52" fill="${c.navy}"/></svg>`;
}

const LOGOTIPOS = [
  { key: 'i-termometro', nombre: 'La I es un termómetro', nota: 'Dice "medimos temperatura" dentro del nombre. Combina con cualquier marca.', html: c => `GOL${iTermometro(c)}AT` },
  { key: 'o-isoterma', nombre: 'La O es una isoterma', nota: 'La llama en curvas de nivel ocupa el lugar de la O. Sirve sin símbolo aparte.', html: c => `G${oIsoterma(c)}LIAT` },
  { key: 'a-haz', nombre: 'La A es el haz', nota: 'La A sin travesaño es el barrido del satélite; la llama queda en su base.', html: c => `GOLI${aHaz(c)}T` },
  { key: 'minuscula-brasa', nombre: 'goliat, con brasa', nota: 'En minúscula, más cercano; el punto de la i es una brasa chica.', html: c => `<span class="lc">gol${puntoBrasa(c)}at</span>` },
];

module.exports = { LOGOTIPOS, theme: t => (t === 'dark' ? D : P) };
