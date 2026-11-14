// GOLIAT · marca C1 "Señal de calor" — fuente única de la geometría del logo.
// Lienzo de 128 × 128. La llama abajo a la izquierda emite una onda infrarroja que
// llega al sensor de un satélite de un solo panel (como Suomi NPP y NOAA-20, que llevan VIIRS).

const THEMES = {
  light: { sat: '#0B2545', band: '#5B7FA6', panel: '#1F6F8B', panelLine: '#A9CFE3', lens: '#FDB022',
           hot: ['#FFE29A', '#FDB022', '#F06A1D', '#C7302A'], waveEnd: '#2B7BB9' },
  navy:  { sat: '#E6F0F8', band: '#9FB8D3', panel: '#6BAED6', panelLine: '#07173F', lens: '#FFC24B',
           hot: ['#FFF1C4', '#FFC24B', '#FF8A3D', '#F0553F'], waveEnd: '#9ECAE1' },
  print: { sat: '#000000', band: '#FFFFFF', panel: '#000000', panelLine: '#FFFFFF', lens: '#FFFFFF',
           hot: ['#000000', '#000000', '#000000', '#000000'], waveEnd: '#000000', flat: true },
};

// Llama: base al centro en (40, 117), punta inclinada hacia el satélite, lengua secundaria a la izquierda.
const F_OUT = 'M47 42 C58 58 71 69 71 88 C71 105 57 117 40 117 C23 117 10 105 10 89 C10 76 18 67 23 56 C26.5 66 30 71.5 36.5 74 C33.5 62 37 50 47 42 Z';
// Núcleo calado: la misma llama en chico, donde el calor es mayor.
const F_CORE = 'M43 80 C49.5 88 54.5 93 54.5 101 C54.5 108.5 48.5 112.5 41 112.5 C33.5 112.5 28 108 28 101 C28 95 32 91.5 34.5 87.5 C36.5 92.5 38.5 94.5 41 95 C39.8 90 40.8 85 43 80 Z';

let _uid = 0;
const uid = p => `${p}${++_uid}`;

function flame(t) {
  if (t.flat) return `<path d="${F_OUT} ${F_CORE}" fill-rule="evenodd" fill="${t.hot[3]}"/>`;
  const g = uid('fg');
  return `<defs><linearGradient id="${g}" gradientUnits="userSpaceOnUse" x1="40" y1="117" x2="47" y2="42">
      <stop offset="0" stop-color="${t.hot[1]}"/><stop offset=".5" stop-color="${t.hot[2]}"/><stop offset="1" stop-color="${t.hot[3]}"/></linearGradient></defs>
    <path d="${F_OUT} ${F_CORE}" fill-rule="evenodd" fill="url(#${g})"/>`;
}

// Onda infrarroja: seno entre A y B, con la amplitud que nace y muere en los extremos.
function wave(t, A, B, periods, amp, width) {
  const dx = B[0] - A[0], dy = B[1] - A[1], L = Math.hypot(dx, dy);
  const ux = dx / L, uy = dy / L, nx = -uy, ny = ux;
  const pts = [];
  const N = 90;
  for (let i = 0; i <= N; i++) {
    const s = i / N;
    const env = Math.pow(Math.sin(Math.PI * s), 0.55);
    const o = amp * env * Math.sin(2 * Math.PI * periods * s);
    pts.push(`${(A[0] + dx * s + nx * o).toFixed(2)} ${(A[1] + dy * s + ny * o).toFixed(2)}`);
  }
  const g = uid('wg');
  const stroke = t.flat ? t.waveEnd : `url(#${g})`;
  return `${t.flat ? '' : `<defs><linearGradient id="${g}" gradientUnits="userSpaceOnUse" x1="${A[0]}" y1="${A[1]}" x2="${B[0]}" y2="${B[1]}">
      <stop offset="0" stop-color="${t.hot[3]}"/><stop offset=".55" stop-color="${t.hot[2]}"/><stop offset="1" stop-color="${t.hot[1]}"/></linearGradient></defs>`}
    <path d="M${pts.join(' L')}" fill="none" stroke="${stroke}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round"/>`;
}

// Satélite de un panel. Ejes locales: +y = nadir (mira a la Tierra), +x = ala solar.
function satellite(t, x, y, s, deg, detail = true) {
  const grid = detail ? [23.5, 32, 40.5].map(gx => `<line x1="${gx}" y1="-8" x2="${gx}" y2="8" stroke="${t.panelLine}" stroke-width="1"/>`).join('')
    + `<line x1="15" y1="0" x2="49" y2="0" stroke="${t.panelLine}" stroke-width="1"/>` : '';
  const antenna = detail ? `<line x1="-9" y1="0" x2="-14" y2="0" stroke="${t.sat}" stroke-width="2.2"/>
      <path d="M-13.5 -6.5 Q-19.5 0 -13.5 6.5 Z" fill="${t.sat}"/>` : '';
  const band = detail ? `<rect x="-9" y="-3.2" width="18" height="1.8" fill="${t.band}"/>` : '';
  const lens = detail ? `<rect x="-3.6" y="14.6" width="7.2" height="2.4" rx="1" fill="${t.lens}"/>` : '';
  return `<g transform="translate(${x} ${y}) rotate(${deg}) scale(${s})">
      <line x1="9" y1="0" x2="15" y2="0" stroke="${t.sat}" stroke-width="2.4"/>
      <rect x="15" y="-8" width="34" height="16" rx="1.6" fill="${t.panel}"/>${grid}
      ${antenna}
      <rect x="-9" y="-10" width="18" height="20" rx="2.6" fill="${t.sat}"/>${band}
      <rect x="-6" y="9" width="12" height="6" rx="1.4" fill="${t.sat}"/>${lens}
    </g>`;
}

const MARK_OPTS = { limb: true };
// Borde de la Tierra: arco abierto y bajo bajo la llama (nunca un anillo, para no parecerse a Space Apps).
function limb(t) {
  return `<path d="M6 123.5 Q52 114.5 116 123.5" fill="none" stroke="${t.sat}" stroke-width="2.2" stroke-linecap="round" opacity=".9"/>`;
}
// Marca completa (≥ 48 px).
function markBody(theme) {
  const t = THEMES[theme];
  return (MARK_OPTS.limb ? limb(t) : '') + flame(t) + wave(t, [55, 44.5], [87.5, 33], 2, 3, 3.2) + satellite(t, 97, 22, 0.7, 40, true);
}
// Marca chica (≤ 32 px): sin núcleo fino ni detalles del satélite; onda más gruesa y corta.
function smallBody(theme) {
  const t = THEMES[theme];
  return flame(t) + wave(t, [57, 46], [84, 36], 1, 4.5, 7.5) + satellite(t, 96, 24, 0.92, 40, false);
}
function mark(theme, size, label = 'GOLIAT') {
  return `<svg viewBox="0 0 128 128" width="${size}" height="${size}" role="img" aria-label="${label}">${markBody(theme)}</svg>`;
}
function small(theme, size, label = 'GOLIAT') {
  return `<svg viewBox="0 0 128 128" width="${size}" height="${size}" role="img" aria-label="${label}">${smallBody(theme)}</svg>`;
}
if (typeof module !== 'undefined') module.exports = { THEMES, F_OUT, F_CORE, markBody, smallBody, mark, small };
