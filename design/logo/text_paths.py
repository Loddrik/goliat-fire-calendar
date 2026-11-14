"""Convierte el texto del logotipo en trazos SVG (para que el logo no dependa de fuentes instaladas).

Uso: uv run --with fonttools --with brotli python design/logo/text_paths.py <archivo.woff2> <plexmono.woff2> <salida.json>
Salida: {clave: {d, width, cap}} con la línea base en y = 0 y unidades en px para el tamaño pedido.
"""
import json
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

SPECS = {
    # clave: (fuente, texto, tamaño px, espaciado en em)
    "name": ("archivo", "GOLIAT", 100.0, 0.05),
    "tag": ("mono", "ACTIVIDAD DE FUEGO · DETECTADA POR SATÉLITE", 20.0, 0.14),
    "tag_en": ("mono", "SATELLITE-DETECTED FIRE ACTIVITY", 20.0, 0.14),
}


def outline(font: TTFont, text: str, size: float, tracking: float) -> dict:
    upm = font["head"].unitsPerEm
    scale = size / upm
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    hmtx = font["hmtx"]
    pen = SVGPathPen(gs)
    x = 0.0
    for i, ch in enumerate(text):
        gname = cmap[ord(ch)]
        tp = TransformPen(pen, (scale, 0, 0, -scale, x, 0))
        gs[gname].draw(tp)
        x += hmtx[gname][0] * scale
        if i < len(text) - 1:
            x += tracking * size
    os2 = font["OS/2"]
    cap = getattr(os2, "sCapHeight", 0) * scale
    return {"d": pen.getCommands(), "width": round(x, 2), "cap": round(cap, 2)}


def main() -> None:
    fonts = {"archivo": TTFont(sys.argv[1]), "mono": TTFont(sys.argv[2])}
    out = {k: outline(fonts[f], t, s, tr) for k, (f, t, s, tr) in SPECS.items()}
    with open(sys.argv[3], "w") as fh:
        json.dump(out, fh)
    for k, v in out.items():
        print(k, v["width"], v["cap"], len(v["d"]))


if __name__ == "__main__":
    main()
