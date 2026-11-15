// GOLIAT · propuestas de logo v3 (15-11-2026). Cada marca es un SVG de 128 × 128.
// Paleta heredada de C1: azul noche + rampa térmica (ámbar → naranja → rojo). Nada de anillos.

const P = {
  navy: '#0B2545', ink: '#13294B', sky: '#2B7BB9', mist: '#A9CFE3',
  pale: '#FFE29A', amber: '#FDB022', orange: '#F06A1D', red: '#C7302A',
  night: '#07173F',
};
// Tema oscuro: el azul pasa a hielo, la rampa se aclara.
const D = { ...P, navy: '#E6F0F8', ink: '#E6F0F8', sky: '#9ECAE1', pale: '#FFF1C4', amber: '#FFC24B', orange: '#FF8A3D', red: '#F0553F' };

let _id = 0;
const id = p => `${p}${++_id}`;

// Llama base: centrada en x = 64, base en y = 116, punta en y = 14, lengua secundaria a la izquierda.
const FL = 'M64 14 C74 32 96 50 96 80 C96 101 81 116 64 116 C47 116 32 101 32 80 C32 64 41 54 48 44 C50 55 54 60 59 62 C56 47 57.5 30 64 14 Z';
// Gota de llama simétrica (para lo que necesita una silueta tranquila).
const DROP = 'M64 14 C76 36 96 56 96 82 C96 101 82 116 64 116 C46 116 32 101 32 82 C32 56 52 36 64 14 Z';

const scaleAbout = (s, cx, cy) => `translate(${cx} ${cy}) scale(${s}) translate(${-cx} ${-cy})`;
const grad = (gid, stops, x1, y1, x2, y2) =>
  `<linearGradient id="${gid}" gradientUnits="userSpaceOnUse" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}">${stops
    .map(([o, c]) => `<stop offset="${o}" stop-color="${c}"/>`).join('')}</linearGradient>`;

// Satélite mínimo: cuerpo + un panel (eco de C1, más simple). (x, y) = centro del cuerpo.
function sat(c, x, y, s = 1, deg = 0) {
  // Satélite simétrico de dos paneles (el de un panel, inclinado, se leía como martillo).
  return `<g transform="translate(${x} ${y}) rotate(${deg}) scale(${s})">
    <rect x="-5" y="-6" width="10" height="12" rx="1.8" fill="${c.navy}"/>
    <rect x="8" y="-4.5" width="14" height="9" rx="1" fill="${c.navy}"/>
    <rect x="-22" y="-4.5" width="14" height="9" rx="1" fill="${c.navy}"/>
    <rect x="-8" y="-1" width="16" height="2" fill="${c.navy}"/>
    <rect x="-2.2" y="6" width="4.4" height="2.4" rx=".8" fill="${c.amber}"/>
  </g>`;
}

// ── 01 Isoterma: la llama como mapa de temperatura, cuatro curvas de nivel.
function isoterma(c) {
  const fills = [c.red, c.orange, c.amber, c.pale];
  const scales = [1, 0.74, 0.5, 0.27];
  const ax = 63, ay = 100;
  const m = id('im');
  // Las curvas de nivel se separan con un calado transparente (no depende del fondo).
  const cuts = scales.slice(1).map(s => `<path d="${FL}" fill="none" stroke="#000" stroke-width="${(3.2 / s).toFixed(2)}" transform="${scaleAbout(s, ax, ay)}"/>`).join('');
  return `<defs><mask id="${m}" maskUnits="userSpaceOnUse" x="0" y="0" width="128" height="128"><rect width="128" height="128" fill="#fff"/>${cuts}</mask></defs>
    <g mask="url(#${m})">${fills.map((f, i) => `<path d="${FL}" fill="${f}" transform="${scaleAbout(scales[i], ax, ay)}"/>`).join('')}</g>`;
}

// ── 02 Barrido: el satélite barre franjas hacia abajo y la última toca una brasa.
function barrido(c) {
  // Cuatro franjas de frío a caliente; la última toca el foco.
  const cols = ['#1F6F8B', c.sky, c.amber, c.orange];
  const lines = cols.map((col, i) => {
    const y = 40 + i * 13, half = 12 + i * 10;
    return `<line x1="${64 - half}" y1="${y}" x2="${64 + half}" y2="${y}" stroke="${col}" stroke-width="8" stroke-linecap="round"/>`;
  }).join('');
  return `<g transform="translate(64 18)">
      <rect x="-7" y="-9" width="14" height="15" rx="2.6" fill="${c.navy}"/>
      <rect x="-31" y="-6" width="20" height="9" rx="1.2" fill="${c.navy}"/>
      <rect x="11" y="-6" width="20" height="9" rx="1.2" fill="${c.navy}"/>
      <rect x="-11" y="-2.5" width="22" height="2" fill="${c.navy}"/>
      <rect x="-3" y="6" width="6" height="3" rx="1" fill="${c.amber}"/>
    </g>${lines}
    <path d="${FL}" fill="${c.orange}" transform="translate(64 124) scale(.36) translate(-64 -116)"/>
    <path d="${FL}" fill="${c.amber}" transform="translate(64 124) scale(.2) translate(-64 -116)"/>`;
}

// ── 03 G de fuego: la G de GOLIAT guarda la llama en su hueco.
function gFuego(c) {
  const g = id('g');
  // Arco de la G: centro (64, 66), radio 44, abierto arriba a la derecha.
  const r = 44, cx = 64, cy = 66;
  const a0 = -38 * Math.PI / 180, a1 = 8 * Math.PI / 180; // se abre entre -38° y +8°
  const p0 = [cx + r * Math.cos(a0), cy + r * Math.sin(a0)];
  const p1 = [cx + r * Math.cos(a1), cy + r * Math.sin(a1)];
  return `<defs>${grad(g, [[0, c.amber], [0.55, c.orange], [1, c.red]], 64, 104, 70, 40)}</defs>
    <path d="M${p0[0].toFixed(2)} ${p0[1].toFixed(2)} A${r} ${r} 0 1 0 ${p1[0].toFixed(2)} ${p1[1].toFixed(2)} L${(p1[0] - 22).toFixed(2)} ${p1[1].toFixed(2)}" fill="none" stroke="${c.navy}" stroke-width="15" stroke-linejoin="miter"/>
    <path d="${FL}" fill="url(#${g})" transform="translate(64 96) scale(.44) translate(-64 -116)"/>`;
}

// ── 04 Dos sensores: mitad rayada (MODIS, el registro largo) + mitad sólida (VIIRS) = una sola llama.
function dosSensores(c) {
  const left = id('l'), right = id('r'), g = id('g');
  const stripes = [];
  for (let y = 12; y < 120; y += 7) stripes.push(`<rect x="20" y="${y}" width="44" height="4" fill="${c.sky}"/>`);
  return `<defs>
      <clipPath id="${left}"><rect x="0" y="0" width="62.5" height="128"/></clipPath>
      <clipPath id="${right}"><rect x="65.5" y="0" width="64" height="128"/></clipPath>
      ${grad(g, [[0, c.amber], [0.55, c.orange], [1, c.red]], 64, 116, 64, 14)}
    </defs>
    <clipPath id="${left}f"><path d="${FL}" transform="translate(128 0) scale(-1 1)"/></clipPath>
    <g clip-path="url(#${left})"><g clip-path="url(#${left}f)">${stripes.join('')}</g></g>
    <g clip-path="url(#${right})"><path d="${FL}" fill="url(#${g})" transform="translate(128 0) scale(-1 1)"/></g>`;
}

// ── 05 Órbita abierta: una traza que pasa sobre la brasa (arco abierto, nunca anillo).
function orbita(c) {
  const g = id('o');
  return `<defs>${grad(g, [[0, c.sky], [1, c.navy]], 10, 100, 118, 30)}</defs>
    <path d="M12 98 C 26 54 62 28 98 30" fill="none" stroke="url(#${g})" stroke-width="7" stroke-linecap="round"/>
    ${sat(c, 100, 28, 0.9, 32)}
    <path d="${FL}" fill="${c.orange}" transform="translate(70 118) scale(.5) translate(-64 -116)"/>
    <path d="${FL}" fill="${c.amber}" transform="translate(70 118) scale(.27) translate(-64 -116)"/>`;
}

// ── 06 Espectro: la llama hecha de barras, como un histograma de detecciones.
function espectro(c) {
  const clip = id('e'), g = id('g');
  const bars = [];
  const n = 9, w = 6.2, gap = 1.9, x0 = 64 - (n * w + (n - 1) * gap) / 2;
  for (let i = 0; i < n; i++) bars.push(`<rect x="${(x0 + i * (w + gap)).toFixed(2)}" y="0" width="${w}" height="128" fill="url(#${g})"/>`);
  return `<defs><clipPath id="${clip}"><path d="${FL}"/></clipPath>
      ${grad(g, [[0, c.amber], [0.5, c.orange], [1, c.red]], 0, 116, 0, 14)}</defs>
    <g clip-path="url(#${clip})">${bars.join('')}</g>`;
}

// ── 07 Catorce temporadas: catorce franjas (2012→2026), la de arriba es la temporada en curso.
function temporadas(c) {
  const clip = id('t');
  const ramp = (t) => t < 0.5 ? mix(c.amber, c.orange, t * 2) : mix(c.orange, c.red, (t - 0.5) * 2);
  const rows = [];
  const top = 14, bot = 116, n = 14, h = (bot - top) / n;
  for (let i = 0; i < n; i++) {
    const y = bot - (i + 1) * h;
    rows.push(`<rect x="20" y="${(y + 0.9).toFixed(2)}" width="88" height="${(h - 1.8).toFixed(2)}" fill="${ramp(i / (n - 1))}"/>`);
  }
  return `<defs><clipPath id="${clip}"><path d="${DROP}"/></clipPath></defs><g clip-path="url(#${clip})">${rows.join('')}</g>`;
}

// ── 08 Cordillera: Antuco y la cordillera; el calor sube como onda hasta el satélite.
function cordillera(c) {
  const g = id('w');
  const pts = [];
  const A = [52, 92], B = [92, 34];
  const dx = B[0] - A[0], dy = B[1] - A[1], L = Math.hypot(dx, dy), nx = -dy / L, ny = dx / L;
  for (let i = 0; i <= 80; i++) {
    const s = i / 80, env = Math.pow(Math.sin(Math.PI * s), 0.6), o = 3.2 * env * Math.sin(2 * Math.PI * 2.5 * s);
    pts.push(`${(A[0] + dx * s + nx * o).toFixed(2)} ${(A[1] + dy * s + ny * o).toFixed(2)}`);
  }
  return `<defs>${grad(g, [[0, c.orange], [1, c.amber]], A[0], A[1], B[0], B[1])}</defs>
    <path d="M6 112 L36 70 L44 78 L60 54 L74 72 L80 66 L122 112 Z" fill="${c.navy}"/>
    <path d="M52.5 61 L60 54 L67 63 L63 61 L59 65 L56 61 Z" fill="${c.mist}"/>
    <path d="${FL}" fill="${c.orange}" transform="translate(46 108) scale(.24) translate(-64 -116)"/>
    <path d="${FL}" fill="${c.amber}" transform="translate(46 108) scale(.13) translate(-64 -116)"/>
    <path d="M${pts.join(' L')}" fill="none" stroke="url(#${g})" stroke-width="3" stroke-linecap="round"/>
    ${sat(c, 100, 24, 0.85, 38)}
    <line x1="4" y1="117" x2="124" y2="117" stroke="${c.navy}" stroke-width="2.4" stroke-linecap="round"/>`;
}

// ── 09 Píxel de 375 m: un solo píxel del VIIRS con la llama calada.
function pixel(c) {
  const g = id('p');
  return `<defs>${grad(g, [[0, c.amber], [1, c.orange]], 0, 112, 0, 40)}</defs>
    <path fill-rule="evenodd" fill="${c.navy}" d="M30 10 H98 A20 20 0 0 1 118 30 V98 A20 20 0 0 1 98 118 H30 A20 20 0 0 1 10 98 V30 A20 20 0 0 1 30 10 Z
      M64 26 C72 40 88 52 88 76 C88 92 77 104 64 104 C51 104 40 92 40 76 C40 64 46 56 51 49 C52.5 57 55.5 61 59 62.5 C57 51 58.5 39 64 26 Z"/>
    <path d="${FL}" fill="url(#${g})" transform="translate(64 102) scale(.42) translate(-64 -116)"/>`;
}

// ── 10 Satélite-termómetro: el cuerpo es un termómetro y los paneles, sus alas.
function termometro(c) {
  // El bulbo del termómetro es una llama; los paneles, cortos y bajos, lo vuelven satélite.
  const g = id('m'), gm = id('mm');
  return `<defs>${grad(g, [[0, c.amber], [0.6, c.orange], [1, c.red]], 0, 120, 0, 70)}${grad(gm, [[0, c.orange], [1, c.amber]], 0, 96, 0, 28)}</defs>
    <rect x="16" y="44" width="24" height="18" rx="2" fill="${c.navy}"/>
    <rect x="88" y="44" width="24" height="18" rx="2" fill="${c.navy}"/>
    <line x1="28" y1="44" x2="28" y2="62" stroke="${c.mist}" stroke-width="1.6"/>
    <line x1="100" y1="44" x2="100" y2="62" stroke="${c.mist}" stroke-width="1.6"/>
    <rect x="40" y="50" width="12" height="6" fill="${c.navy}"/><rect x="76" y="50" width="12" height="6" fill="${c.navy}"/>
    <rect x="52" y="10" width="24" height="76" rx="12" fill="${c.navy}"/>
    <path d="${FL}" fill="${c.navy}" transform="${scaleAbout(0.6, 64, 122)}"/>
    <path d="${FL}" fill="url(#${g})" transform="${scaleAbout(0.43, 64, 116)}"/>
    <rect x="59.5" y="20" width="9" height="66" rx="4.5" fill="url(#${gm})"/>`;
}

// ── 11 Detecciones que suben: la llama se deshace en píxeles que suben al satélite.
function detecciones(c) {
  const clip = id('d');
  // La llama se corta en diagonal; sobre el corte, el calor sigue subiendo como píxeles.
  const sq = [
    [70, 42, 9, c.orange], [82, 31, 7.5, c.amber], [93, 21, 6, c.amber], [103, 12, 4.5, c.pale],
    [56, 36, 6, c.orange], [74, 24, 4.5, c.amber],
  ].map(([x, y, s, f]) => `<rect x="${x - s / 2}" y="${y - s / 2}" width="${s}" height="${s}" rx=".8" fill="${f}"/>`).join('');
  return `<defs><clipPath id="${clip}"><path d="M0 128 L0 66 L128 34 L128 128 Z"/></clipPath></defs>
    <g clip-path="url(#${clip})">
      <path d="${FL}" fill="${c.red}"/>
      <path d="${FL}" fill="${c.orange}" transform="${scaleAbout(0.68, 64, 116)}"/>
      <path d="${FL}" fill="${c.amber}" transform="${scaleAbout(0.38, 64, 116)}"/>
    </g>${sq}`;
}

// ── 12 Monolínea: un solo trazo — satélite, onda infrarroja, llama.
function monolinea(c) {
  const g = id('ml');
  // Un trazo: lengua izquierda → borde → base → borde derecho → punta, y la punta sigue como onda hasta el satélite.
  const d = 'M58 80 C50 76 46 68 46 58 C38 68 32 80 32 94 C32 109 44 120 60 120 C76 120 88 109 88 94'
    + ' C88 76 72 66 66 50 C62 45 70 41 66 36 C62 31 70 27 66 22';
  return `<defs>${grad(g, [[0, c.red], [0.45, c.orange], [0.75, c.amber], [1, c.sky]], 40, 120, 66, 20)}</defs>
    <path d="${d}" fill="none" stroke="url(#${g})" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
    <g transform="translate(66 12)">
      <rect x="-5" y="-5.5" width="10" height="11" rx="1.8" fill="${c.navy}"/>
      <rect x="7" y="-4" width="15" height="8" rx="1" fill="${c.navy}"/>
      <rect x="-22" y="-4" width="15" height="8" rx="1" fill="${c.navy}"/>
      <line x1="-7" y1="0" x2="7" y2="0" stroke="${c.navy}" stroke-width="2"/>
    </g>`;
}

// ── 13 Calor que sube: tres ondas de calor forman la llama; sin fuego literal, solo la señal.
function calor(c) {
  // Cinta que se afina al subir: la onda de calor nace gruesa en el suelo y se vuelve hilo.
  const ribbon = (x, y0, y1, amp, per, col, w0, ph = 0) => {
    const N = 48, L = [], R = [];
    for (let i = 0; i <= N; i++) {
      const s = i / N, y = y0 + (y1 - y0) * s;
      const cx = x + amp * Math.sin(2 * Math.PI * per * s + ph) * (0.35 + 0.65 * s);
      const w = (w0 * Math.pow(1 - s, 0.8) + 0.6) / 2;
      L.push(`${(cx - w).toFixed(2)} ${y.toFixed(2)}`);
      R.unshift(`${(cx + w).toFixed(2)} ${y.toFixed(2)}`);
    }
    return `<path d="M${L.join(' L')} L${R.join(' L')} Z" fill="${col}"/>`;
  };
  return ribbon(40, 114, 54, 6, 1.1, c.amber, 13, 0.4) + ribbon(64, 114, 18, 7, 1.4, c.orange, 15)
    + ribbon(88, 114, 54, 6, 1.1, c.red, 13, Math.PI + 0.4)
    + `<rect x="22" y="114" width="84" height="5" rx="2.5" fill="${c.navy}"/>`
    + sat(c, 104, 22, 0.8, 40);
}

// ── 14 A de barrido: solo para el logotipo; la A es el haz del satélite y la llama queda en su base.
function aBarrido(c) {
  const g = id('ab');
  return `<defs>${grad(g, [[0, c.amber], [1, c.orange]], 0, 112, 0, 70)}</defs>
    <path d="M54 24 H74 L116 116 H91 L64 56 L37 116 H12 Z" fill="${c.navy}"/>
    <path d="${FL}" fill="url(#${g})" transform="translate(64 116) scale(.38) translate(-64 -116)"/>
    <circle cx="64" cy="11" r="7" fill="${c.amber}"/>`;
}

// ── 13 Curva de temporada: la forma de la temporada (pocas detecciones en invierno, el pico en verano)
// se vuelve llama en su máximo. Doce marcas bajo la línea base: los meses, sin celdas.
const SEASON = 'M8 112 C26 112 36 106 44 92 C50 81 53 68 58 54 C61 45 64 33 74 18 C71 34 76 48 84 64 C92 80 100 106 120 112 Z';
function curvaTemporada(c) {
  const g = id('ct');
  const ticks = Array.from({ length: 12 }, (_, i) => {
    const x = 12 + i * (104 / 11);
    return `<line x1="${x.toFixed(1)}" y1="118" x2="${x.toFixed(1)}" y2="${i === 6 || i === 7 ? 125 : 122}" stroke="${c.navy}" stroke-width="2.2" stroke-linecap="round"/>`;
  }).join('');
  return `<defs>${grad(g, [[0, c.amber], [0.55, c.orange], [1, c.red]], 0, 112, 0, 18)}</defs>
    <path d="${SEASON}" fill="url(#${g})"/>
    <path d="${SEASON}" fill="${c.amber}" transform="${scaleAbout(0.52, 66, 112)}"/>
    <path d="${SEASON}" fill="${c.pale}" transform="${scaleAbout(0.24, 66, 112)}"/>
    <line x1="6" y1="114.5" x2="122" y2="114.5" stroke="${c.navy}" stroke-width="3" stroke-linecap="round"/>${ticks}
    ${sat(c, 104, 20, 0.72, 0)}`;
}

// ── 15 Satélite calado: el satélite vive dentro de la llama como espacio negativo; ver el calor desde adentro.
function satCalado(c) {
  const m = id('sc'), g = id('g');
  return `<defs>${grad(g, [[0, c.amber], [0.55, c.orange], [1, c.red]], 64, 116, 64, 14)}
    <mask id="${m}" maskUnits="userSpaceOnUse" x="0" y="0" width="128" height="128"><rect width="128" height="128" fill="#fff"/>
      <g transform="translate(64 84) scale(1.28)" fill="#000">
        <rect x="-5" y="-6" width="10" height="12" rx="1.8"/>
        <rect x="7.5" y="-4.5" width="15" height="9" rx="1"/><rect x="-22.5" y="-4.5" width="15" height="9" rx="1"/>
        <rect x="-8" y="-1" width="16" height="2"/>
        <rect x="-2.6" y="6" width="5.2" height="3.4" rx=".8"/>
      </g></mask></defs>
    <path d="${FL}" fill="url(#${g})" mask="url(#${m})"/>`;
}

// ── 16 Facetas: la llama doblada en papel; caras claras a la izquierda, oscuras a la derecha.
function facetas(c) {
  const T = [66, 10], L = [38, 44], I = [52, 62], M = [61, 74], RS = [96, 68], RB = [94, 98], B = [64, 120], LB = [32, 96];
  const tri = (pts, f) => `<path d="M${pts.map(p => p.join(' ')).join(' L')} Z" fill="${f}" stroke="${f}" stroke-width=".6" stroke-linejoin="round"/>`;
  return tri([T, I, M], c.amber) + tri([T, M, RS], c.orange) + tri([RS, M, RB], c.red) + tri([M, B, RB], c.orange)
    + tri([I, LB, M], c.pale) + tri([M, LB, B], c.amber) + tri([L, LB, I], c.orange);
}

function mix(a, b, t) {
  const pa = a.match(/\w\w/g).map(h => parseInt(h, 16)), pb = b.match(/\w\w/g).map(h => parseInt(h, 16));
  return '#' + pa.map((v, i) => Math.round(v + (pb[i] - v) * t).toString(16).padStart(2, '0')).join('');
}

const MARCAS = [
  { key: 'isoterma', n: '01', nombre: 'Isoterma', idea: 'La llama dibujada como un mapa de temperatura: cuatro curvas de nivel, del borde tibio al núcleo caliente. Dice "medimos calor" sin satélite ni texto.', fn: isoterma , nota: 'Se lee como emoji de fuego con contornos; las isotermas las ve solo un técnico.' },
  { key: 'dos-sensores', n: '02', nombre: 'Dos sensores, una llama', idea: 'Mitad en líneas de barrido (MODIS, el registro largo desde 2002) y mitad sólida (VIIRS, desde 2012): dos sensores leídos en la misma escala. Es lo que distingue a GOLIAT frente al jurado.', fn: dosSensores , rec: 5 },
  { key: 'catorce-temporadas', n: '03', nombre: 'Catorce temporadas', idea: 'La llama apilada en 14 franjas, una por temporada observada (2012→2026). Abajo lo tibio, arriba la temporada en curso. Es un calendario sin celdas.', fn: temporadas , nota: 'La rampa hacia el rojo arriba sugiere "cada año peor", algo que el método no afirma; recuerda la grilla rechazada.' },
  { key: 'g-de-fuego', n: '04', nombre: 'G de fuego', idea: 'Monograma: la G de GOLIAT abraza una llama en su hueco. Funciona como favicon y como inicial en el logotipo.', fn: gFuego, letra: 'G' , nota: 'La G casi cerrada alrededor de la llama es un anillo con otro nombre, y recuerda a Google.' },
  { key: 'barrido', n: '05', nombre: 'Barrido', idea: 'El satélite barre línea a línea (así lee VIIRS) y las franjas van de frío a caliente hasta tocar un foco chico. Cuenta el método completo, con calma.', fn: barrido , rec: 2 },
  { key: 'pixel-375', n: '06', nombre: 'Píxel de 375 m', idea: 'Un solo píxel del VIIRS con la llama calada. Un ícono de app rotundo: se lee a 16 px. Es una celda, no una grilla.', fn: pixel , nota: 'Ícono de app genérico; lo de 375 m hay que explicarlo.' },
  { key: 'satelite-termometro', n: '07', nombre: 'Satélite-termómetro', idea: 'El cuerpo del satélite es un termómetro y su bulbo es una llama. Dice "medimos calor desde arriba" sin dibujar un incendio. Frase para el pitch: GOLIAT no ve incendios, lee temperatura.', fn: termometro , rec: 1 },
  { key: 'espectro', n: '08', nombre: 'Espectro', idea: 'La llama hecha de barras verticales, como un histograma de detecciones. Puente entre fuego y datos.', fn: espectro , nota: 'Llama a rayas tipo código de barras, sin satélite; genérica.' },
  { key: 'calor-que-sube', n: '09', nombre: 'Calor que sube', idea: 'Tres cintas de calor nacen gruesas en el suelo y se afinan al subir hacia el satélite: la señal infrarroja más que el fuego. Cálida y tranquila, nada de alarma.', fn: calor , nota: 'Puede leerse como quemador de cocina o el símbolo de termas.' },
  { key: 'detecciones', n: '10', nombre: 'Detecciones', idea: 'La llama se deshace en píxeles que suben: el fuego se vuelve dato. Lectura de "de la tierra al satélite".', fn: detecciones , nota: 'Las chispas que suben se leen como pavesas: propagación, tono de alerta.' },
  { key: 'orbita-abierta', n: '11', nombre: 'Órbita abierta', idea: 'Una traza abierta pasa sobre la brasa; el satélite al final. Movimiento y escala (Goliat arriba, la brasa abajo). Arco abierto, nunca anillo.', fn: orbita , nota: 'Parece velocímetro o ícono de carga; el arco roza la regla del anillo.' },
  { key: 'cordillera', n: '12', nombre: 'Cordillera', idea: 'El Antuco y la cordillera de Biobío-Ñuble; desde el valle sube la onda de calor al satélite. La más territorial: dice dónde.', fn: cordillera , nota: 'Se lee como volcán y pone el fuego en la cordillera, cuando la actividad está en el secano y la costa.' },
  { key: 'curva-de-temporada', n: '13', nombre: 'Curva de temporada', idea: 'La forma de una temporada (poco en invierno, el máximo en verano) se vuelve llama en su pico; doce marcas son los meses y el satélite mira desde arriba. Calendario sin celdas. Silueta estilizada, no un dato.', fn: curvaTemporada , rec: 4 },
  { key: 'a-de-barrido', n: '14', nombre: 'A de barrido', idea: 'Pensada para el logotipo: la A de GOLIAT es el haz del satélite (el punto ámbar arriba) y la llama queda en su base.', fn: aBarrido, letra: 'A' , nota: 'Sola parece camping; sirve mejor como letra del logotipo (ver logotipos).' },
  { key: 'satelite-calado', n: '15', nombre: 'Satélite calado', idea: 'El satélite está calado dentro de la llama, mirando hacia abajo. Satélite y fuego en una sola silueta: la que mejor se lee a 32 y 64 px.', fn: satCalado , rec: 3 },
  { key: 'facetas', n: '16', nombre: 'Facetas', idea: 'La llama doblada en papel: siete caras, claras a la izquierda y oscuras a la derecha. Geométrica, artesanal y distinta de cualquier ícono de fuego de catálogo.', fn: facetas , nota: 'Se parece al ícono de Firebase; sin satélite ni temperatura.' },
];

function svg(fn, theme = 'light', size = 128, label = 'GOLIAT') {
  const c = theme === 'dark' ? D : P;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="${size}" height="${size}" role="img" aria-label="${label}">${fn(c)}</svg>`;
}

module.exports = { P, D, MARCAS, svg, FL, DROP, SEASON, sat, grad, scaleAbout, id, mix, fns: { barrido, dosSensores, curvaTemporada, aBarrido } };
