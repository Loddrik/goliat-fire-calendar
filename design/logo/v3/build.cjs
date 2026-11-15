// Arma propuestas.html (un cuadro por propuesta, para vf-lamina) y exporta cada marca a svg/.
// Uso: node build.cjs
const fs = require('fs');
const path = require('path');
const { MARCAS, svg, P } = require('./marcas.cjs');
const { LOGOTIPOS, theme } = require('./logotipos.cjs');

const out = path.join(__dirname, 'svg');
fs.mkdirSync(out, { recursive: true });
for (const m of MARCAS) {
  fs.writeFileSync(path.join(out, `${m.n}-${m.key}.svg`), svg(m.fn, 'light', 512));
  fs.writeFileSync(path.join(out, `${m.n}-${m.key}-oscuro.svg`), svg(m.fn, 'dark', 512));
}

const inl = (m, theme) => svg(m.fn, theme, 64).replace('<svg ', '<svg class="inl" ');
const word = (m, theme) => m.letra === 'G' ? `${inl(m, theme)}OLIAT` : m.letra === 'A' ? `GOLI${inl(m, theme)}T` : 'GOLIAT';
const lockup = (m, theme) => `<div class="lock ${theme}">
  ${m.letra ? '' : svg(m.fn, theme, 96)}
  <div><div class="word">${word(m, theme)}</div><div class="lema">Calendario de fuego detectado · Biobío y Ñuble</div></div>
</div>`;

const slide = (m) => `<section class="slide" id="s${Number(m.n) + 1}">
  <div class="head"><span class="num">${m.n}</span><h2>${m.nombre}</h2></div>
  <div class="hero">${svg(m.fn, 'light', 420)}</div>
  <div class="row">
    <div class="tile dark">${svg(m.fn, 'dark', 150)}</div>
    <div class="tile sizes">${svg(m.fn, 'light', 64)}${svg(m.fn, 'light', 32)}${svg(m.fn, 'light', 16)}</div>
    <div class="tile tab"><div class="chrome">${svg(m.fn, 'light', 16)}<span data-objeto>GOLIAT · Biobío</span></div></div>
  </div>
  ${lockup(m, 'light')}
  ${lockup(m, 'dark')}
  <p class="idea">${m.idea}</p>
</section>`;

const portada = `<section class="slide" id="s1">
  <div class="head"><span class="num">v3</span><h2>GOLIAT · 16 propuestas de marca</h2></div>
  <div class="grid">${MARCAS.map(m => `<figure>${svg(m.fn, 'light', 170)}<figcaption>${m.n} · ${m.nombre}</figcaption></figure>`).join('')}</div>
</section>`;

const logos = `<section class="slide" id="s${MARCAS.length + 2}">
  <div class="head"><span class="num">+</span><h2>Logotipos: una letra que mide</h2></div>
  ${LOGOTIPOS.map(l => `<div class="lt"><div class="ltrow"><div class="lw light">${l.html(theme('light'))}</div><div class="lw dark">${l.html(theme('dark'))}</div></div><p class="ltn"><b>${l.nombre}.</b> ${l.nota}</p></div>`).join('')}
</section>`;

const html = `<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="lienzo" content="1080x1350">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@125,700;125,800&family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#ddd;font-family:Inter,sans-serif;color:${P.navy}}
.slide{width:1080px;height:1350px;background:#FBF8F2;position:relative;padding:72px;display:flex;flex-direction:column;gap:26px;overflow:hidden}
.head{display:flex;align-items:baseline;gap:22px}
.num{font-family:'IBM Plex Mono';font-size:34px;color:${P.orange};font-weight:500}
h2{font-family:Archivo;font-stretch:125%;font-weight:800;font-size:46px;letter-spacing:.5px}
.hero{display:flex;justify-content:center;align-items:center;height:440px}
.row{display:flex;gap:20px}
.tile{flex:1;height:170px;border-radius:14px;display:flex;align-items:center;justify-content:center;gap:22px;background:#fff;border:1px solid #e6e1d6}
.tile.dark{background:${P.night};border:none}
.chrome{display:flex;align-items:center;gap:10px;background:#EEF1F5;border-radius:10px;padding:10px 16px;font-size:18px}
.lock{display:flex;align-items:center;gap:24px;padding:14px 26px;border-radius:14px}
.lock.light{background:#fff;border:1px solid #e6e1d6}
.lock.dark{background:${P.night};color:#E6F0F8}
.word{font-family:Archivo;font-stretch:125%;font-weight:800;font-size:64px;letter-spacing:3px;line-height:1}
.inl{width:1.06em;height:1.06em;vertical-align:-.2em;margin:0 -.04em}
.lema{font-family:'IBM Plex Mono';font-size:20px;margin-top:8px;opacity:.8}
.idea{font-size:34px;line-height:1.3}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px 16px;margin-top:10px}
figure{background:#fff;border:1px solid #e6e1d6;border-radius:14px;display:flex;flex-direction:column;align-items:center;padding:14px 4px 10px}
figcaption{font-family:'IBM Plex Mono';font-size:17px;margin-top:6px;text-align:center}
.lt{display:flex;flex-direction:column;gap:8px}
.ltrow{display:flex;gap:16px}
.lw{flex:1;border-radius:14px;padding:22px 24px;font-family:Archivo;font-stretch:125%;font-weight:800;font-size:66px;letter-spacing:2px;line-height:1;white-space:nowrap;display:flex;align-items:flex-end}
.lw.light{background:#fff;border:1px solid #e6e1d6;color:${P.navy}}.lw.dark{background:${P.night};color:#E6F0F8}
.lw .gl{height:1.28em;vertical-align:baseline;margin:0 .02em -.27em;flex:none}
.lc{font-stretch:112%;letter-spacing:0;display:flex;align-items:flex-end}
.ltn{font-size:26px;line-height:1.3}
</style></head><body>
${portada}
${MARCAS.map(slide).join('\n')}
${logos}
</body></html>`;
fs.writeFileSync(path.join(__dirname, 'propuestas.html'), html);
console.log('ok', MARCAS.length, 'marcas');
