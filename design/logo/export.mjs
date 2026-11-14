// Genera los SVG finales de la marca GOLIAT en web/public/brand/ desde mark.js y text-paths.json.
// Uso: node design/logo/export.mjs
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../..');
const out = path.join(root, 'web/public/brand');
fs.mkdirSync(out, { recursive: true });

const M = new Function(`${fs.readFileSync(path.join(here, 'mark.js'), 'utf8')}; return { THEMES, markBody, smallBody, MARK_OPTS };`)();
const T = JSON.parse(fs.readFileSync(path.join(here, 'text-paths.json'), 'utf8'));

const INK = {
  light: { name: '#1A1A1A', tag: '#4A4A4A' },
  navy: { name: '#FFFFFF', tag: '#C9D3E3' },
  print: { name: '#000000', tag: '#000000' },
};
const fmt = n => +n.toFixed(2);
const svg = (w, h, body, label) =>
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${fmt(w)} ${fmt(h)}" width="${fmt(w)}" height="${fmt(h)}" role="img" aria-label="${label}">\n<title>${label}</title>\n${body}\n</svg>\n`;
const iconAt = (theme, x, y, size, small = false) =>
  `<g transform="translate(${fmt(x)} ${fmt(y)}) scale(${fmt(size / 128)})">${small ? M.smallBody(theme) : M.markBody(theme)}</g>`;
const text = (key, x, baseline, fill, k = 1) =>
  `<path transform="translate(${fmt(x)} ${fmt(baseline)}) scale(${k})" fill="${fill}" d="${T[key].d}"/>`;

const PAD = 8;
function horizontal(theme, tagKey) {
  const ICON = 185, GAP = 30;
  const tagW = tagKey ? T[tagKey].width : 0;
  const textW = Math.max(T.name.width, tagW);
  const w = PAD * 2 + ICON + GAP + textW, h = PAD * 2 + ICON;
  const cy = PAD + ICON / 2;
  let body = iconAt(theme, PAD, PAD, ICON);
  const x = PAD + ICON + GAP;
  if (tagKey) {
    const block = T.name.cap + 36;
    const nameBase = cy - block / 2 + T.name.cap;
    body += text('name', x, nameBase, INK[theme].name) + text(tagKey, x, nameBase + 36, INK[theme].tag);
  } else {
    body += text('name', x, cy + T.name.cap / 2, INK[theme].name);
  }
  return svg(w, h, body, 'GOLIAT · Actividad de fuego detectada por satélite');
}
function vertical(theme, tagKey = 'tag') {
  const ICON = 200, GAP = 18;
  const textW = Math.max(T.name.width, T[tagKey].width);
  const w = PAD * 2 + textW, h = PAD * 2 + ICON + GAP + T.name.cap + 36 + 6;
  let body = iconAt(theme, (w - ICON) / 2, PAD, ICON);
  const nameBase = PAD + ICON + GAP + T.name.cap;
  body += text('name', (w - T.name.width) / 2, nameBase, INK[theme].name);
  body += text(tagKey, (w - T[tagKey].width) / 2, nameBase + 36, INK[theme].tag);
  return svg(w, h, body, 'GOLIAT · Actividad de fuego detectada por satélite');
}
const icon = (theme, small = false) => svg(128, 128, small ? M.smallBody(theme) : M.markBody(theme), 'GOLIAT');

const files = {
  'goliat-logo.svg': horizontal('light'),
  'goliat-logo-oscuro.svg': horizontal('navy'),
  'goliat-logo-negro.svg': horizontal('print'),
  'goliat-logo-lema.svg': horizontal('light', 'tag'),
  'goliat-logo-lema-oscuro.svg': horizontal('navy', 'tag'),
  'goliat-logo-lema-negro.svg': horizontal('print', 'tag'),
  'goliat-logo-lema-en.svg': horizontal('light', 'tag_en'),
  'goliat-logo-lema-en-oscuro.svg': horizontal('navy', 'tag_en'),
  'goliat-logo-vertical.svg': vertical('light'),
  'goliat-logo-vertical-oscuro.svg': vertical('navy'),
  'goliat-icono.svg': icon('light'),
  'goliat-icono-oscuro.svg': icon('navy'),
  'goliat-icono-negro.svg': icon('print'),
  'goliat-icono-chico.svg': icon('light', true),
  'goliat-icono-chico-oscuro.svg': icon('navy', true),
  'goliat-icono-chico-negro.svg': icon('print', true),
};
for (const [name, content] of Object.entries(files)) fs.writeFileSync(path.join(out, name), content);
// favicon: versión chica
fs.writeFileSync(path.join(root, 'web/public/favicon.svg'), files['goliat-icono-chico.svg']);
console.log(Object.keys(files).length + 1, 'archivos en', out);
