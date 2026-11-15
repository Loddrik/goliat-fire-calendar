"""Render the handoff Markdown into self-contained HTML. Documentation-only deps."""
from __future__ import annotations

import argparse
import hashlib
import html
import re
import unicodedata
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs/handoff/2026-11-15"
PAGES = {
    "resumen-tecnico": ("Ciencia que se puede revisar", "01 / INFORME TÉCNICO", "technical"),
    "resumen-negocio": ("Una historia del fuego para decidir mejor", "02 / PRODUCTO Y NEGOCIO", "business"),
    "pendientes-priorizados": ("El siguiente paso, con límites claros", "03 / PLAN DE ENTREGA", "plan"),
    "README": ("GOLIAT · entrega al equipo", "HANDOFF / 15 NOVIEMBRE 2026", "index"),
}
CSS = """:root{--ink:#173337;--muted:#51676a;--paper:#f7f5ee;--card:#fffef9;--line:#cbd8d4;--teal:#087e83;--orange:#b65320;--hero:#07393d}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:24px}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.75 system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}a{color:#006c75;text-underline-offset:3px;overflow-wrap:anywhere}a:hover{color:#a94315}a:focus-visible,summary:focus-visible{outline:3px solid #e48635;outline-offset:4px}header{background:var(--hero);color:#fff;padding:26px max(5vw,24px) 60px;position:relative;overflow:hidden}header:after{content:'';position:absolute;width:460px;height:460px;border:1px solid #76b0a944;border-radius:50%;right:-180px;top:-160px;pointer-events:none;box-shadow:0 0 0 60px #76b0a910,0 0 0 120px #76b0a910}nav.top{display:flex;gap:20px;flex-wrap:wrap;align-items:center;position:relative;z-index:1}nav.top a{color:#daeeeb;font-size:13px;text-decoration:none}.brand{font-size:24px!important;letter-spacing:.16em;font-weight:850;margin-right:auto}.eyebrow{font-size:12px;font-weight:750;letter-spacing:.18em;text-transform:uppercase;margin-top:54px;color:#a7ded5}h1.hero{max-width:930px;font-size:clamp(36px,5.2vw,70px);letter-spacing:-.045em;line-height:1.08;margin:18px 0 22px;font-weight:760}.lede{max-width:760px;color:#d0e8e4;font-size:19px;line-height:1.6}.pills{display:flex;flex-wrap:wrap;gap:10px;margin-top:28px}.pill{font-size:12px;border:1px solid #9ac9c76b;border-radius:100px;padding:6px 12px;color:#e2f1ee}.layout{max-width:1380px;margin:0 auto;display:grid;grid-template-columns:245px minmax(0,1fr);gap:52px;padding:48px max(4vw,24px) 70px}.toc{font-size:13px;align-self:start;position:sticky;top:24px}.toc h2{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-top:0}.toc ol{list-style:none;padding:0;border-left:1px solid var(--line)}.toc li a{display:block;padding:7px 0 7px 16px;text-decoration:none;color:var(--muted);line-height:1.4}.toc li a:hover{color:var(--teal);border-left:2px solid var(--teal);margin-left:-1px}.toc .source{display:block;margin-top:20px;font-weight:700}.body{min-width:0;max-width:960px}.body>h1{font-size:28px;letter-spacing:-.025em;line-height:1.3;margin-top:8px}.body h2{font-size:28px;letter-spacing:-.025em;line-height:1.3;margin:50px 0 18px;padding-top:20px;border-top:1px solid var(--line)}.body h3{font-size:20px;margin-top:30px;line-height:1.4}.body p{margin:18px 0}.body strong{font-weight:730}.body li{margin:10px 0}.body blockquote{margin:24px 0;border-left:4px solid var(--teal);padding:8px 22px;background:#e9f0ea}.body code{font-size:.84em;background:#e7eeea;padding:3px 5px;border-radius:4px;overflow-wrap:anywhere}.body pre{padding:24px;background:#15373b;color:#e8f4ef;border-radius:12px;white-space:pre-wrap;overflow-wrap:anywhere;font-size:14px;line-height:1.7}.body pre code{color:inherit;background:none;padding:0}.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;margin:24px 0;background:var(--card)}table{width:100%;border-collapse:collapse;font-size:14px;line-height:1.65}th{text-align:left;background:#e7ede6;font-weight:750;color:#244446}th,td{padding:15px 17px;vertical-align:top;border-bottom:1px solid var(--line);min-width:140px}tr:last-child td{border-bottom:0}table p{margin:0}.diagram{padding:26px;border:1px solid var(--line);background:#fffdf6;border-radius:16px;margin:4px 0 36px}.diagram .label{font-size:11px;letter-spacing:.13em;text-transform:uppercase;color:var(--muted);font-weight:750}.flow{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:18px 0}.step{border-top:3px solid var(--teal);padding:15px;background:#eaf1eb;border-radius:0 0 8px 8px;min-width:0}.step span{font-size:12px;color:var(--muted)}.step b{display:block;line-height:1.35;margin:6px 0 10px;font-size:17px}.step p{font-size:13px;line-height:1.5;margin:0}.diagram figcaption{font-size:12px;line-height:1.6;color:var(--muted)}.boundary{border-top:1px dashed #b98c60;padding-top:16px;font-size:13px;color:#684c30}.reading-note{padding:16px 20px;border-left:3px solid #c57432;background:#f4e9d9;font-size:14px;margin-bottom:30px}.business{--hero:#22443c;--paper:#fbf6eb;--line:#d9dbcb}.technical{--hero:#102f43;--paper:#f4f6f3}.plan{--hero:#413c30}footer{background:#e8eee7;padding:30px max(5vw,24px);font-size:12px;color:var(--muted);overflow-wrap:anywhere}footer .inner{max-width:1220px;margin:auto}.skip{position:absolute;left:-999px}.skip:focus{left:12px;top:12px;background:white;padding:10px;z-index:4}details{border:1px solid var(--line);border-radius:10px;padding:18px}summary{cursor:pointer;font-weight:700}::selection{background:#f4c98b;color:#173337}
@media(max-width:950px){.layout{grid-template-columns:1fr;gap:25px}.toc{position:static}.toc ol{columns:2}.body{max-width:none}.eyebrow{margin-top:35px}}
@media(max-width:550px){body{font-size:16px}.layout{padding:28px 20px 50px}header{padding:22px 22px 40px}nav.top{gap:12px}.brand{width:100%}.lede{font-size:17px}.toc ol{columns:1}.flow{grid-template-columns:1fr}.diagram{padding:20px}.body h2{font-size:24px}th,td{padding:12px;min-width:150px}.pills{gap:7px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{body{font-size:10pt;background:white;color:black}header{background:white;color:black;padding:0 0 20px}header:after,.top,.toc,.pills,.skip{display:none!important}.eyebrow,.lede{color:#333}.eyebrow{margin-top:0}h1.hero{font-size:30pt}.layout{display:block;padding:0;max-width:none}.body{max-width:none}.body h2{font-size:18pt;break-after:avoid}.body h3{break-after:avoid}.table-wrap{overflow:visible}table{font-size:8pt}th,td{min-width:0;padding:8px}tr{break-inside:avoid}.diagram{break-inside:avoid}footer{background:white;padding:18px 0}.body pre{color:black;background:#eee}a{color:#174b50}header .lede{font-size:12pt}}
"""


def diagram(kind: str) -> str:
    """Conceptual, not a data chart; source narrative remains in the Markdown."""
    if kind == "technical":
        steps = [("01 / OBSERVAR", "Fuentes y contrato", "MODIS Aqua y VIIRS. Conservar plataforma, período, filtros y unidad."),
                 ("02 / COMPARAR", "Celda-día → mes", "M1 y compuertas territoriales. La referencia satelital no es verdad física."),
                 ("03 / PUBLICAR", "Calendario revisable", "Observado y estimado separados; método y exportaciones disponibles.")]
        note = "La investigación E_coherent / F21 permanece como evidencia separada. No hay sustitución automática de M1."
    elif kind == "business":
        steps = [("01 / PREGUNTAR", "Elegir el territorio", "¿Cuándo se concentra la actividad registrada en nuestra comuna?"),
                 ("02 / REVISAR", "Comparar temporadas", "Mismo corte temporal, procedencia visible y límites de la reconstrucción."),
                 ("03 / CONTRASTAR", "Preparar una decisión", "Exportar y conversar con el equipo local. La utilidad debe probarse en un piloto.")]
        note = "Flujo de uso propuesto. No representa ahorro, reducción de daños ni efecto preventivo medido."
    else:
        steps = [("P0 / RELATO", "Afirmaciones con fuente", "Un alcance defendible y respuestas claras sobre lo que se sabe."),
                 ("P0 / PAQUETE", "Una versión identificada", "Informes, evidencia, comandos y candidato de demo; revisión de integración aparte."),
                 ("P0 / ENTREGA", "Ensayo y traspaso", "Comprobar rutas y CSV; conservar respaldo y registrar límites reales.")]
        note = "Orden de entrega conceptual. Las prioridades y su estado de ejecución se detallan en los documentos y actas."
    cards = "".join(f'<div class="step"><span>{html.escape(a)}</span><b>{html.escape(b)}</b><p>{html.escape(c)}</p></div>' for a,b,c in steps)
    return f'<figure class="diagram" aria-label="Diagrama conceptual de tres pasos"><div class="label">Diagrama conceptual · leer de izquierda a derecha</div><div class="flow">{cards}</div><figcaption class="boundary">{html.escape(note)}</figcaption></figure>'


def render(stem: str, title: str, eyebrow: str, kind: str) -> str:
    source = DEST / f"{stem}.md"
    raw = source.read_bytes()
    text = raw.decode("utf-8")
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    tokens = md.parse(text)
    headings = []
    seen: dict[str, int] = {}
    for i, token in enumerate(tokens):
        if token.type == "heading_open":
            label = tokens[i+1].content
            slug = unicodedata.normalize("NFKD", label).encode("ascii", "ignore").decode().lower()
            slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-") or "seccion"
            seen[slug] = seen.get(slug, 0)+1
            anchor = slug if seen[slug] == 1 else f"{slug}-{seen[slug]}"
            token.attrSet("id", anchor)
            if token.tag == "h2": headings.append((anchor,label))
    content = md.renderer.render(tokens, md.options, {})
    content = content.replace("<table>", '<div class="table-wrap" tabindex="0" role="region" aria-label="Tabla desplazable"><table>').replace("</table>", "</table></div>")
    toc = "".join(f'<li><a href="#{anchor}">{html.escape(label)}</a></li>' for anchor,label in headings)
    lead = {"technical":"Qué cambió, qué evidencia lo respalda y qué conserva el producto. Un recorrido desde los contratos publicados hasta los límites de la investigación.",
            "business":"El problema municipal, el valor que se puede mostrar y una historia de tres minutos respaldada por evidencia.",
            "plan":"Prioridades acotadas, responsables por rol, aceptación verificable y revisión de ambos consejos.",
            "index":"La puerta de entrada para preparar la presentación: relato, ciencia, pendientes y una versión identificada."}[kind]
    return f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="{html.escape(lead)}"><title>{html.escape(title)} — GOLIAT</title><style>{CSS}</style></head>
<body class="{kind}"><a class="skip" href="#contenido">Ir al contenido</a><header><nav class="top" aria-label="Informes"><a class="brand" href="index.html">GOLIAT</a><a href="resumen-negocio.html">Producto</a><a href="resumen-tecnico.html">Ciencia</a><a href="pendientes-priorizados.html">Pendientes</a><a href="{stem}.md">Markdown ↗</a></nav><div class="eyebrow">{eyebrow}</div><h1 class="hero">{title}</h1><p class="lede">{lead}</p><div class="pills"><span class="pill">M1 conservado</span><span class="pill">14 / 54 comunas habilitadas</span><span class="pill">Investigación ≠ despliegue</span></div></header>
<div class="layout"><aside class="toc" aria-label="En este informe"><h2>En este informe</h2><ol>{toc}</ol><a class="source" href="{stem}.md">Leer fuente Markdown ↗</a><a class="source" href="evidence/verification-snapshot.json">Recibo de verificación ↗</a></aside><main class="body" id="contenido"><div class="reading-note">Entrega documental del 15 de noviembre de 2026. Los estados y cifras tienen el corte y alcance indicados en las fuentes; este informe no acredita despliegue.</div>{diagram(kind)}{content}</main></div>
<footer><div class="inner">GOLIAT · NASA Space Apps · Documento autónomo, sin recursos externos.<br>Fuente: {stem}.md · SHA-256: {hashlib.sha256(raw).hexdigest()}<br>Generado de forma reproducible por pipeline/build_presentation_handoff.py. Imprimir permite guardar como PDF.</div></footer></body></html>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if committed HTML differs from Markdown rendering")
    args = parser.parse_args()
    stale = []
    for stem, (title, eyebrow, kind) in PAGES.items():
        result = render(stem, title, eyebrow, kind)
        path = DEST / ("index.html" if stem == "README" else f"{stem}.html")
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != result: stale.append(path.name)
        else: path.write_text(result, encoding="utf-8")
    if stale: raise SystemExit("Stale HTML: " + ", ".join(stale))
    print("PASS: four handoff documents match their Markdown sources" if args.check else "Rendered four standalone handoff documents")


if __name__ == "__main__":
    main()
