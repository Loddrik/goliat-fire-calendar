// Arma pagina/index.html: la hoja de revisión publicada como Artifact.
// Uso: node pagina.cjs  (lee marcas.cjs, logotipos.cjs, pagina/ia/*.jpg y pagina/maquetas/*.jpg)
const fs = require('fs');
const path = require('path');
const { MARCAS, svg } = require('./marcas.cjs');
const { LOGOTIPOS, theme } = require('./logotipos.cjs');
const R2 = require('./ronda2.cjs');

const dir = path.join(__dirname, 'pagina');
const ls = sub => (fs.existsSync(path.join(dir, sub)) ? fs.readdirSync(path.join(dir, sub)).filter(f => f.endsWith('.jpg')).sort() : []);
const ia = ls('ia');
const maq = ls('maquetas');
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');

const rec = MARCAS.filter(m => m.rec).sort((a, b) => a.rec - b.rec);
const otras = MARCAS.filter(m => !m.rec);

const star = m => `<button class="star" type="button" id="fav-${m.n}" data-n="${m.n}" data-nombre="${esc(m.nombre)}" aria-pressed="false"><span aria-hidden="true">☆</span> Me gusta</button>`;

const recCard = m => {
  const fotos = maq.filter(f => f.startsWith(`m${m.n}-`));
  return `<article class="rec" id="m${m.n}">
  <header class="rec-h"><span class="tag">Recomendada ${m.rec}</span><span class="code">${m.n}</span><h3>${esc(m.nombre)}</h3></header>
  <div class="rec-body">
    <div class="tiles">
      <div class="tile light big">${svg(m.fn, 'light', 220)}</div>
      <div class="tile night big">${svg(m.fn, 'dark', 220)}</div>
    </div>
    <div class="rec-info">
      <p>${esc(m.idea)}</p>
      <div class="sizes" aria-label="Tamaños 64, 32 y 16 px">${svg(m.fn, 'light', 64)}${svg(m.fn, 'light', 32)}${svg(m.fn, 'light', 16)}<span class="mono">64 · 32 · 16 px</span></div>
      <div class="lockup">${svg(m.fn, 'light', 56)}<div><div class="word">GOLIAT</div><div class="lema mono">Calendario de fuego detectado · Biobío y Ñuble</div></div></div>
      ${star(m)}
    </div>
  </div>
  ${fotos.length ? `<div class="fotos">${fotos.map(f => `<figure><img src="maquetas/${f}" alt="Maqueta de ${esc(m.nombre)}: ${f.includes('libreta') ? 'tapa de libreta' : 'sticker en notebook'}" loading="lazy"><figcaption class="mono">${f.includes('libreta') ? 'Libreta' : 'Sticker'} · maqueta IA</figcaption></figure>`).join('')}</div>` : ''}
</article>`;
};

const otraCard = m => `<article class="otra" id="m${m.n}">
  <div class="tiles"><div class="tile light">${svg(m.fn, 'light', 120)}</div><div class="tile night">${svg(m.fn, 'dark', 120)}</div></div>
  <div class="otra-t"><span class="code">${m.n}</span><h3>${esc(m.nombre)}</h3></div>
  <p>${esc(m.idea)}</p>
  ${m.nota ? `<p class="nota"><b>Ojo:</b> ${esc(m.nota)}</p>` : ''}
  <div class="otra-f"><div class="sizes">${svg(m.fn, 'light', 32)}${svg(m.fn, 'light', 16)}</div>${star(m)}</div>
</article>`;

const logoRow = l => `<div class="lt">
  <div class="lt-w"><div class="lw light">${l.html(theme('light'))}</div><div class="lw night">${l.html(theme('dark'))}</div></div>
  <p><b>${esc(l.nombre)}.</b> ${esc(l.nota)}</p>
  <button class="star" type="button" id="fav-${l.key}" data-n="${l.key}" data-nombre="${esc('Logotipo: ' + l.nombre)}" aria-pressed="false"><span aria-hidden="true">☆</span> Me gusta</button>
</div>`;

const r2Items = [...R2.HIBRIDOS, ...R2.ORIGINALES.map(o => ({ ...o, de: 'original', idea: (MARCAS.find(m => m.n === o.n) || {}).idea }))];
const palabra = (m, t) => m.n === 'H3' || m.n === '14'
  ? `<span>GOLI${R2.aGlifo(R2.theme(t), m.n === 'H3')}T</span>`
  : `${R2.svg(m.fn, t, 48, 'mk')}<span>GOLI${R2.aGlifo(R2.theme(t), false)}T</span>`;
const r2Card = m => `<article class="rec r2" id="r2-${m.n}">
  <header class="rec-h"><span class="tag">${m.de === 'original' ? 'Tu favorita' : 'Mezcla ' + m.de}</span><span class="code">${m.n}</span><h3>${esc(m.nombre)}</h3></header>
  <div class="rec-body">
    <div class="tiles">
      <div class="tile light big">${R2.svg(m.fn, 'light', 220)}</div>
      <div class="tile night big">${R2.svg(m.fn, 'dark', 220)}</div>
    </div>
    <div class="rec-info">
      <p>${esc(m.idea || '')}</p>
      <div class="sizes" aria-label="Tamaños 64, 32 y 16 px">${R2.svg(m.fn, 'light', 64)}${R2.svg(m.fn, 'light', 32)}${R2.svg(m.fn, 'light', 16)}<span class="mono">64 · 32 · 16 px</span></div>
      <div class="pestana" aria-label="Pestaña del navegador">${R2.svg(m.fn, 'light', 16)}<span>GOLIAT · Biobío y Ñuble</span></div>
      <button class="pick" type="button" data-n="${m.n}" data-nombre="${esc(m.nombre)}" aria-pressed="false"><span aria-hidden="true">○</span> Elijo esta</button>
    </div>
  </div>
  <div class="enapp">
    <div class="hdr light"><div class="hw">${palabra(m, 'light')}</div><nav class="mono">Calendario · Mapa · Método</nav></div>
    <div class="hdr night"><div class="hw">${palabra(m, 'dark')}</div><nav class="mono">Calendario · Mapa · Método</nav></div>
  </div>
</article>`;

const grupos = [
  { pre: 'r1-', t: 'Recraft v3 vectorial · 15 conceptos', d: 'Salieron todos como parches circulares con anillo, aunque el prompt lo prohibía. Sirvieron para ver ideas (el haz que cae sobre un píxel, la llama como estela), no como logo.' },
  { pre: 'r2-n', t: 'Nano Banana · 15 símbolos', d: 'De aquí vinieron el satélite calado, las facetas y la mitad rayada en azul de «Dos sensores».' },
  { pre: 'r2-i', t: 'Ideogram v3 · 8 logotipos', d: 'De aquí vinieron la I como termómetro y la O como llama; están redibujadas en vector más arriba.' },
];
const nombreIA = f => f.replace(/^r\d-/, '').replace(/-(nano|ideogram)\.jpg$|\.jpg$/, '').replace(/^[cni]\d\d-/, '').replace(/-/g, ' ');

const gastos = [
  ['Pruebas (Recraft + Nano Banana)', 2, '0,12'],
  ['Recraft v3 vectorial', 15, '1,20'],
  ['Prueba de Ideogram v3', 1, '0,06'],
  ['Nano Banana + Ideogram v3', 22, '1,02'],
  ['Maquetas con FLUX Kontext', 10, '0,40'],
];

const html = `<title>Marca GOLIAT v3</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,400..800&family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@400;500;600&display=swap">
<style>
/* Hoja de revisión: el logo manda; superficie fría de papel técnico, azul noche y la rampa térmica solo en las marcas. */
:root{
  --bg:#EEF1F5; --surface:#FFFFFF; --ink:#0B2545; --muted:#4F607A; --line:#D5DCE6; --accent:#C2410C;
  --tile-light:#FFFFFF; --tile-night:#07173F; --tile-night-ink:#E6F0F8; --chip:#E3E9F1;
  --display:'Archivo','Helvetica Neue',Arial,sans-serif; --body:'Inter',system-ui,-apple-system,sans-serif; --mono:'IBM Plex Mono',ui-monospace,Menlo,monospace;
  color-scheme:light;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#0A1230; --surface:#111C40; --ink:#E6F0F8; --muted:#9DB0CC; --line:#24325C; --accent:#FF9A57; --chip:#1A2850; color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0A1230; --surface:#111C40; --ink:#E6F0F8; --muted:#9DB0CC; --line:#24325C; --accent:#FF9A57; --chip:#1A2850; color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:var(--body);font-size:16px;line-height:1.55;margin:0}
.wrap{max-width:1180px;margin:0 auto;padding-block:40px 120px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
h1,h2,h3{font-family:var(--display);font-stretch:125%;text-wrap:balance;margin:0;line-height:1.1}
h1{font-size:clamp(30px,5vw,52px);font-weight:800;letter-spacing:.01em}
h2{font-size:clamp(22px,3vw,30px);font-weight:800}
h3{font-size:20px;font-weight:700}
p{margin:0}
.mono{font-family:var(--mono)}
.lede{max-width:66ch;color:var(--muted);font-size:17px}
.intro{display:grid;gap:18px;margin-bottom:44px}
.intro ol{margin:0;padding-left:20px;color:var(--muted);max-width:66ch}
.kicker{font-family:var(--mono);font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}
section{margin-top:56px;display:grid;gap:20px}
.sec-h{display:grid;gap:6px}
.sec-h p{color:var(--muted);max-width:70ch}
.tile{border-radius:12px;display:grid;place-items:center;padding:14px;aspect-ratio:1;min-width:0}
.tile svg{width:100%;height:auto;max-width:220px}
.tile.light{background:var(--tile-light);border:1px solid var(--line)}
.tile.night{background:var(--tile-night)}
.rec{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:22px;display:grid;gap:18px}
.rec-h{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.tag{font-family:var(--mono);font-size:12px;letter-spacing:.06em;text-transform:uppercase;background:var(--ink);color:var(--bg);padding:3px 8px;border-radius:4px}
.code{font-family:var(--mono);color:var(--accent);font-weight:500}
.rec-body{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:22px;align-items:start}
.rec .tiles{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.rec-info{display:grid;gap:16px;min-width:0}
.sizes{display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.sizes .mono{font-size:12px;color:var(--muted)}
.lockup{display:flex;align-items:center;gap:14px;padding:12px 16px;border-radius:12px;background:var(--tile-light);border:1px solid var(--line);color:#0B2545;min-width:0;overflow:hidden}
.lockup svg{flex:none}
.word{font-family:var(--display);font-stretch:125%;font-weight:800;font-size:clamp(26px,4vw,38px);letter-spacing:.06em;line-height:1}
.lema{font-size:11.5px;margin-top:5px;color:#4F607A}
.fotos{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,260px));gap:12px}
.fotos figure,.galeria figure{margin:0;display:grid;gap:6px}
.fotos img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:10px;display:block}
figcaption{font-size:12px;color:var(--muted)}
.star{justify-self:start;font:500 15px var(--body);color:var(--ink);background:var(--chip);border:1px solid var(--line);border-radius:999px;padding:8px 16px;cursor:pointer}
.star:hover{border-color:var(--accent)}
.star:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.star[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.r2 .enapp{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.hdr{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 16px;border-radius:10px;min-width:0;overflow:hidden}
.hdr.light{background:#fcfbf7;border:1px solid #e2e2dc;color:#0B2545}
.hdr.night{background:var(--tile-night);color:var(--tile-night-ink)}
.hdr nav{font-size:12px;opacity:.75;white-space:nowrap}
.hw{display:flex;align-items:center;gap:12px;font-family:var(--display);font-stretch:125%;font-weight:800;font-size:28px;letter-spacing:.06em;line-height:1;white-space:nowrap}
.hw .mk{width:40px;height:40px;flex:none;align-self:center}
.hw span{display:inline-block}
.gla{width:auto;vertical-align:baseline;margin:0 .03em}
.pestana{display:flex;align-items:center;gap:8px;background:var(--chip);border-radius:8px 8px 0 0;padding:7px 12px;font-size:13px;justify-self:start;max-width:100%}
.pick{justify-self:start;font:600 15px var(--body);color:var(--ink);background:var(--chip);border:1px solid var(--line);border-radius:999px;padding:9px 18px;cursor:pointer}
.pick:hover{border-color:var(--accent)}
.pick:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.pick[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.r2s{display:grid;gap:18px}
.otras{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}
.otra{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px;display:grid;gap:10px;align-content:start}
.otra .tiles{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.otra-t{display:flex;gap:10px;align-items:baseline}
.otra p{font-size:14.5px}
.nota{color:var(--muted)}
.otra-f{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:4px}
.lt{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px;display:grid;gap:12px}
.lt-w{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.lw{border-radius:10px;padding:18px 20px;font-family:var(--display);font-stretch:125%;font-weight:800;font-size:clamp(28px,5vw,52px);letter-spacing:.04em;line-height:1;white-space:nowrap;display:flex;align-items:flex-end;overflow:hidden;min-width:0}
.lw.light{background:var(--tile-light);border:1px solid var(--line);color:#0B2545}
.lw.night{background:var(--tile-night);color:var(--tile-night-ink)}
.lw .gl{height:1.28em;margin:0 .02em -.27em;flex:none}
.lc{font-stretch:112%;letter-spacing:0;display:flex;align-items:flex-end}
.galeria{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.galeria img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:8px;background:#fff;display:block}
.grupo{display:grid;gap:10px}
.grupo h3{font-size:17px}
.grupo p{color:var(--muted);font-size:14.5px;max-width:75ch}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line)}
td.n,th.n{text-align:right}
.tabla{overflow-x:auto;background:var(--surface);border:1px solid var(--line);border-radius:12px}
.notas{display:grid;gap:10px;max-width:75ch;color:var(--muted)}
.notas code{font-family:var(--mono);font-size:13.5px;color:var(--ink)}
.barra{position:fixed;left:0;right:0;bottom:0;background:var(--ink);color:var(--bg);padding-block:12px calc(12px + env(safe-area-inset-bottom,0px));padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:flex;gap:14px;align-items:center;justify-content:space-between;flex-wrap:wrap;z-index:5}
.barra p{font-size:14.5px;min-width:0}
.barra button{font:600 14px var(--body);background:var(--bg);color:var(--ink);border:none;border-radius:999px;padding:8px 16px;cursor:pointer}
.barra button:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
@media (max-width:760px){.rec-body{grid-template-columns:1fr}.r2 .enapp{grid-template-columns:1fr}.hdr nav{display:none}.lt-w{grid-template-columns:1fr}}
@media (prefers-reduced-motion:no-preference){.star{transition:background .15s,border-color .15s}}
</style>

<div class="wrap">
  <div class="intro">
    <span class="kicker">GOLIAT · marca v3 · ronda 2 · 15-11-2026</span>
    <h1>Tus cuatro favoritas y cuatro mezclas entre ellas</h1>
    <p class="lede">Elegiste 13 curva de temporada, 14 A de barrido, 02 dos sensores y 05 barrido. Lo que tienen en común es el satélite que lee línea a línea y la temporada como forma, así que las crucé: H1 a H4 son mezclas, y abajo están tus cuatro tal cual. Cada una se ve en tamaño chico, en una pestaña del navegador y en el encabezado de la app, con el nombre usando la A como haz.</p>
    <p class="lede"><b>Elige una sola</b> con «Elijo esta» y copia tu elección con el botón de abajo. Con eso la dejo puesta en la app.</p>
  </div>

  <section aria-labelledby="h-r2">
    <div class="sec-h"><span class="kicker">Ronda 2</span><h2 id="h-r2">Cuatro mezclas y tus cuatro favoritas</h2></div>
    <div class="r2s">${r2Items.map(r2Card).join('\n')}</div>
  </section>

  <div class="intro" style="margin-top:72px">
    <span class="kicker">Ronda 1 · madrugada del 15-11</span>
    <h2>Las dieciséis marcas y cuatro logotipos de la primera ronda</h2>
    <p class="lede">Todas están dibujadas en vector (escalan a 16 px y tienen versión oscura). La IA se usó para explorar ideas y para las maquetas; ninguna marca final es una imagen generada. Respetan las reglas de la marca: sin anillo alrededor, sin llama sola en rojo plano y sin tono de alerta.</p>
    <ol>
      <li>Mira primero las cinco recomendadas: pasaron por una revisión de producto y ya tienen sus correcciones.</li>
      <li>Marca con «Me gusta» las que te sirvan, también de las otras once o de los logotipos.</li>
      <li>Copia tu selección con el botón de abajo y pégamela: con eso dejo lista la que elijas en <span class="mono">web/public/brand/</span>.</li>
    </ol>
  </div>

  <section aria-labelledby="h-rec">
    <div class="sec-h"><span class="kicker">Recomendadas</span><h2 id="h-rec">Las cinco que mejor dicen «medimos calor desde un satélite»</h2>
      <p>Ordenadas por la revisión: lectura a 16 px, distancia de los íconos de fuego genéricos, tono tranquilo y relato para el pitch.</p></div>
    ${rec.map(recCard).join('\n')}
  </section>

  <section aria-labelledby="h-logos">
    <div class="sec-h"><span class="kicker">Logotipos</span><h2 id="h-logos">Una letra del nombre que mide</h2>
      <p>Se combinan con cualquier marca. La I termómetro conversa con la recomendada 1; la O isoterma funciona sola, sin símbolo.</p></div>
    ${LOGOTIPOS.map(logoRow).join('\n')}
  </section>

  <section aria-labelledby="h-otras">
    <div class="sec-h"><span class="kicker">Las otras once</span><h2 id="h-otras">También dibujadas, con lo que la revisión les encontró</h2>
      <p>No rompen las reglas duras, pero cada una tiene un problema de lectura que va anotado. Si alguna te gusta igual, márcala y la corrijo.</p></div>
    <div class="otras">${otras.map(otraCard).join('\n')}</div>
  </section>

  <section aria-labelledby="h-ia">
    <div class="sec-h"><span class="kicker">Exploración con IA</span><h2 id="h-ia">De dónde salieron las ideas</h2>
      <p>${ia.length} imágenes generadas con <span class="mono">vf-gen</span> antes de dibujar. Cada una tiene su prompt y modelo en <span class="mono">design/logo/v3/exploracion/</span>.</p></div>
    ${grupos.map(g => { const fs_ = ia.filter(f => f.startsWith(g.pre)); return `<div class="grupo"><h3>${g.t}</h3><p>${g.d}</p><div class="galeria">${fs_.map(f => `<figure><img src="ia/${f}" alt="${esc(nombreIA(f))}" loading="lazy"><figcaption class="mono">${esc(nombreIA(f))}</figcaption></figure>`).join('')}</div></div>`; }).join('\n')}
  </section>

  <section aria-labelledby="h-como">
    <div class="sec-h"><span class="kicker">Cómo se hizo</span><h2 id="h-como">Herramientas y gasto</h2></div>
    <div class="notas">
      <p><span class="mono">vf-gen</span> (fal.ai) para explorar con Recraft, Nano Banana e Ideogram, y para las maquetas con FLUX Kontext. <span class="mono">vf-lamina</span> para renderizar cada propuesta a 1080 × 1350 con su mini de 150 px y auditar recortes. Las marcas están en <code>design/logo/v3/marcas.cjs</code> y los SVG sueltos en <code>design/logo/v3/svg/</code>.</p>
      <p>El logo vigente (C1) no se tocó: la web sigue igual hasta que elijas.</p>
    </div>
    <div class="tabla"><table>
      <thead><tr><th>Lote</th><th class="n">Imágenes</th><th class="n">USD</th></tr></thead>
      <tbody>${gastos.map(([a, b, c]) => `<tr><td>${a}</td><td class="n">${b}</td><td class="n">${c}</td></tr>`).join('')}
      <tr><td><b>Total estimado</b> (tope autorizado: USD 5)</td><td class="n"><b>${gastos.reduce((s, g) => s + g[1], 0)}</b></td><td class="n"><b>${gastos.reduce((s, g) => s + parseFloat(g[2].replace(',', '.')), 0).toFixed(2).replace('.', ',')}</b></td></tr></tbody>
    </table></div>
  </section>
</div>

<div class="barra" role="region" aria-label="Tu selección">
  <p id="sel">Todavía no marcas ninguna.</p>
  <button type="button" id="copiar">Copiar mi elección</button>
</div>

<script>
(function () {
  var KEY = 'goliat-marca-v3-favs';
  var favs = {};
  try { favs = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { favs = {}; }
  var btns = Array.prototype.slice.call(document.querySelectorAll('.star'));
  function texto() {
    var ks = Object.keys(favs);
    if (!ks.length) return '';
    return 'Me gustan: ' + ks.map(function (k) { return favs[k]; }).join('; ') + '.';
  }
  function pintar() {
    btns.forEach(function (b) {
      var on = !!favs[b.dataset.n];
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.firstElementChild.textContent = on ? '★' : '☆';
    });
    var t = texto();
    document.getElementById('sel').textContent = t || 'Todavía no marcas ninguna.';
  }
  btns.forEach(function (b) {
    b.addEventListener('click', function () {
      var k = b.dataset.n;
      if (favs[k]) delete favs[k]; else favs[k] = (/^\\d/.test(k) ? k + ' ' : '') + b.dataset.nombre;
      try { localStorage.setItem(KEY, JSON.stringify(favs)); } catch (e) {}
      pintar();
    });
  });
  var copiar = document.getElementById('copiar');
  copiar.addEventListener('click', function () {
    var t = texto() || 'No marqué ninguna todavía.';
    function listo(msg) { copiar.textContent = msg; setTimeout(function () { copiar.textContent = 'Copiar mi elección'; }, 1800); }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(t).then(function () { listo('Copiado'); }, function () { seleccionar(); });
    } else { seleccionar(); }
    function seleccionar() {
      var r = document.createRange(); r.selectNodeContents(document.getElementById('sel'));
      var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); listo('Selecciona y copia');
    }
  });
  var PK = 'goliat-marca-v3-r2';
  var pick = null;
  try { pick = JSON.parse(localStorage.getItem(PK) || 'null'); } catch (e) { pick = null; }
  var picks = Array.prototype.slice.call(document.querySelectorAll('.pick'));
  var texto1 = texto;
  texto = function () {
    var t = pick ? 'Elijo ' + pick.n + ' ' + pick.nombre + '.' : '';
    var f = texto1();
    return [t, f].filter(Boolean).join(' ');
  };
  function pintarPick() {
    picks.forEach(function (b) {
      var on = !!pick && pick.n === b.dataset.n;
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.firstElementChild.textContent = on ? '●' : '○';
    });
    pintar();
  }
  picks.forEach(function (b) {
    b.addEventListener('click', function () {
      pick = pick && pick.n === b.dataset.n ? null : { n: b.dataset.n, nombre: b.dataset.nombre };
      try { localStorage.setItem(PK, JSON.stringify(pick)); } catch (e) {}
      pintarPick();
    });
  });
  pintarPick();
})();
</script>
`;
fs.writeFileSync(path.join(dir, 'index.html'), html);
console.log('pagina/index.html', (html.length / 1024).toFixed(0), 'KB ·', ia.length, 'IA ·', maq.length, 'maquetas');
