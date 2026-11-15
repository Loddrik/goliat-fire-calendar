#!/usr/bin/env bash
# Genera los derivados en PNG/ICO de la marca desde los SVG de web/public/brand/ (correr después de export.mjs):
# favicon.ico (16, 32, 48), apple-touch-icon.png, brand/icon-192.png, brand/icon-512.png y brand/og-image.png.
# Uso: bash design/logo/png.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
CH="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
B="$PWD/web/public/brand"
SP="$(mktemp -d)"
trap 'rm -rf "$SP"' EXIT

shot() { "$CH" --headless=new --disable-gpu --hide-scrollbars --allow-file-access-from-files --force-device-scale-factor=1 \
  --default-background-color=00000000 --window-size="$2,$3" --virtual-time-budget=4000 --screenshot="$4" "file://$1" 2>/dev/null; }

for s in 16 32 48; do
  printf '<!doctype html><body style="margin:0"><img src="file://%s/goliat-icono-chico.svg" width="%s" height="%s" style="display:block">' "$B" $s $s > "$SP/f$s.html"
  shot "$SP/f$s.html" $s $s "$SP/f$s.png"
done
printf '<!doctype html><body style="margin:0;background:#FCFBF7;width:180px;height:180px;display:grid;place-items:center"><img src="file://%s/goliat-icono.svg" width="146" height="146">' "$B" > "$SP/apple.html"
shot "$SP/apple.html" 180 180 web/public/apple-touch-icon.png
for s in 192 512; do
  p=$((s * 78 / 100))
  printf '<!doctype html><body style="margin:0;background:#FCFBF7;width:%spx;height:%spx;display:grid;place-items:center"><img src="file://%s/goliat-icono.svg" width="%s" height="%s">' $s $s "$B" $p $p > "$SP/i$s.html"
  shot "$SP/i$s.html" $s $s "$B/icon-$s.png"
done

cat > "$SP/og.html" <<EOF
<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400&family=IBM+Plex+Sans:wght@500;600&display=swap">
<body style="margin:0;width:1200px;height:630px;background:#07173F;color:#fff;font-family:'IBM Plex Sans';box-sizing:border-box;padding:64px 72px;display:grid;grid-template-rows:auto 1fr auto;gap:28px">
<img src="file://$B/goliat-logo-oscuro.svg" style="height:120px;width:auto">
<div style="font-size:50px;font-weight:600;line-height:1.16;max-width:980px;align-self:center;letter-spacing:-.005em">Cuándo y dónde los satélites de la NASA han detectado fuego en tu comuna, desde 2012.</div>
<div style="display:flex;justify-content:space-between;font-family:'IBM Plex Mono';font-size:19px;letter-spacing:.1em;text-transform:uppercase;color:#C9D3E3"><span>Biobío y Ñuble · 54 comunas · NASA FIRMS (MODIS + VIIRS)</span><span>No es una alerta</span></div>
</body>
EOF
"$CH" --headless=new --disable-gpu --hide-scrollbars --allow-file-access-from-files --force-device-scale-factor=1 \
  --window-size=1200,630 --virtual-time-budget=4000 --screenshot="$B/og-image.png" "file://$SP/og.html" 2>/dev/null

python3 -I - "$SP" web/public/favicon.ico <<'PY'
import struct, sys
d, out = sys.argv[1], sys.argv[2]
sizes = (16, 32, 48)
imgs = [open(f'{d}/f{s}.png', 'rb').read() for s in sizes]
hdr = struct.pack('<HHH', 0, 1, len(sizes)); off = 6 + 16 * len(sizes); ents = b''
for s, im in zip(sizes, imgs):
    ents += struct.pack('<BBBBHHII', s, s, 0, 0, 1, 32, len(im), off); off += len(im)
open(out, 'wb').write(hdr + ents + b''.join(imgs))
PY
echo "listo: favicon.ico, apple-touch-icon.png, icon-192.png, icon-512.png, og-image.png"
