"""Standalone explanation of frozen evidence and the six-member direction council.

Reads summaries only; never fits models, accesses credentials or reads raw products.
"""
from pathlib import Path
import hashlib
import html
import json

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'docs/artifacts/science-observation-plan-2026-11-15.html'
SOURCES = {
    'context': 'data/processed/context_cdf_audit/summary.json',
    'cold': 'data/processed/cold_region_audit/summary.json',
    'geometry': 'docs/reviews/evidence/observation-mesh-validation/summary.json',
    'viirs': 'docs/reviews/evidence/viirs-dimension-consistency/summary.json',
    'votes': 'docs/reviews/evidence/direction-council-24/votes.json',
    'agreement': 'docs/reviews/evidence/direction-council-24/ratification.json',
    'contract': 'data/processed/contract_model_sensitivity_audit/summary.json',
    'daily': 'docs/reviews/evidence/gridded-observability-preflight/result.json',
    'ledger': 'docs/reviews/evidence/observation-ownership-ledger/summary.json',
    'closure': 'docs/reviews/evidence/observation-ownership-ledger/diagnostic/failed-common-closure.json',
    'engine': 'docs/reviews/evidence/geometry-engine-diagnostic/comparison.json',
    'origin': 'docs/reviews/evidence/coordinate-origin-diagnostic/results.json',
    'exact': 'docs/reviews/evidence/coordinate-origin-diagnostic/exactness-certificate.json',
    'witness': 'docs/reviews/evidence/exact-geometry-witness/results.json',
    'full_failure': 'docs/reviews/evidence/centered-observation-ledger/attempt-01/failure-run.json',
    'points': 'docs/reviews/evidence/point-ownership-audit/attempt-01/summary.json',
    'local_exact': 'docs/reviews/evidence/exact-local-overlay-audit/results.json',
    'council31': 'docs/reviews/evidence/direction-council-31/ratification.json',
}
D = {k: json.loads((ROOT / v).read_text()) for k, v in SOURCES.items()}


def esc(value):
    return html.escape(str(value))


def number(value, digits=3):
    return f'{value:.{digits}f}'.replace('.', ',')


def table(headers, rows, caption):
    return ('<div class="scroll"><table><caption>' + esc(caption) + '</caption><thead><tr>'
            + ''.join('<th scope="col">' + esc(h) + '</th>' for h in headers)
            + '</tr></thead><tbody>'
            + ''.join('<tr>' + ''.join('<td>' + esc(c) + '</td>' for c in row) + '</tr>' for row in rows)
            + '</tbody></table></div>')


def diagram(nodes, links, label, height=300):
    """Own SVG diagrams, with visible labels and equivalent adjacent prose."""
    body = []
    for x, y, w, h, title, lines, color in nodes:
        body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{color}" stroke="#a7bfbd"/>')
        body.append(f'<text x="{x+16}" y="{y+30}" font-weight="700" font-size="18">{esc(title)}</text>')
        for i, line in enumerate(lines):
            body.append(f'<text x="{x+16}" y="{y+57+22*i}" font-size="14">{esc(line)}</text>')
    for x1, y1, x2, y2 in links:
        body.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="#346b72" stroke-width="2" marker-end="url(#arrow)"/>')
    prefix = hashlib.sha256(label.encode()).hexdigest()[:8]
    result = ('<div class="scroll" tabindex="0" role="region" aria-label="Diagrama desplazable"><svg '
              f'viewBox="0 0 1000 {height}" role="img" aria-label="{esc(label)}" xmlns="http://www.w3.org/2000/svg">'
              '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
              '<path d="M0 0 L8 4 L0 8" fill="#346b72"/></marker></defs>' + ''.join(body) + '</svg></div>')
    return result.replace('id="arrow"', f'id="arrow-{prefix}"').replace('url(#arrow)', f'url(#arrow-{prefix})')


operator = diagram([
    (10, 20, 285, 130, 'Actividad del territorio', ['No observada completamente', 'Nube, humo, horario y geometría', 'pueden ocultar actividad'], '#eef2ed'),
    (355, 20, 285, 130, 'Operador satelital', ['Bandas, tamaño, vista, QA', 'Cada sensor registra una parte', 'No equivale a verdad física'], '#e4f0ef'),
    (700, 20, 285, 130, 'Registro y calendario', ['Celda–día → comuna–mes', 'La armonización compara registros', 'Desconocido conserva su estado'], '#f8ecd9'),
], [(295, 85, 355, 85), (640, 85, 700, 85)], 'Del territorio al registro: el operador media la observación', 175)

process = diagram([
    (10, 10, 285, 125, '1 · Criterios comunes', ['Tres miembros ratifican pesos', 'Antes de puntuar propuestas', 'Reglas no compensables'], '#e4f0ef'),
    (355, 10, 285, 125, '2 · Votos independientes', ['Estadística · observación · loco', 'Cinco opciones, evidencia y rangos', 'Se preservan desacuerdos'], '#e4f0ef'),
    (700, 10, 285, 125, '3 · Consejo adversario', ['Identificación · medición · coste', 'Encuentra límites y exclusiones', 'Corrige la interpretación'], '#f8ecd9'),
    (355, 195, 285, 100, '4 · Plan ratificado por seis', ['Auditorías acotadas y paralelas', 'Sin promoción ni causalidad física'], '#e4f0ef'),
], [(295, 70, 355, 70), (640, 70, 700, 70), (840, 135, 640, 215), (150, 135, 355, 215)],
    'Los consejos acuerdan criterios, votan, objetan y ratifican un plan', 320)

parallel = diagram([
    (10, 15, 285, 170, 'C · Contratos ≤60 min', ['Identidad de 3.456 filas', 'Funciones congeladas, sin refit', 'Cotas con dominio explícito', 'Revisión incluida en el cap'], '#e4f0ef'),
    (355, 15, 285, 170, 'B · Ledger ≤60 min', ['Propiedad por geometría', 'Áreas y positivos excluidos', 'Desconocidos y QA separados', 'Todavía sin concordancia'], '#e4f0ef'),
    (700, 15, 285, 170, 'E · Documentación ≤30 min', ['Operadores diarios y compuestos', '750 m no equivale a 375 m', 'Sin descargar datos científicos', 'No inventar denominadores'], '#f8ecd9'),
    (355, 240, 285, 95, 'Revisión y siguiente protocolo', ['Avanzar, detener o inconcluso', 'Conservar también lo negativo'], '#eef2ed'),
], [(150, 185, 355, 260), (500, 185, 500, 240), (840, 185, 640, 260)],
    'Tres tareas paralelas con entregables y límites propios', 360)

criteria = table(['Criterio', 'Peso', 'Pregunta'], [
    ['Validez e identificabilidad', '30 %', '¿Qué afirmación permiten operador, unidad y evidencia?'],
    ['Información discriminante', '25 %', '¿Qué desenlace cambia una decisión?'],
    ['Factibilidad y reproducción', '20 %', '¿Hay una entrega revisable dentro del cap?'],
    ['Transporte y selección', '15 %', '¿Qué fechas, escaneos y territorios representa?'],
    ['Utilidad interpretativa', '10 %', '¿Se distingue demostrado, condicionado y desconocido?'],
], 'Criterios acordados antes de los votos')

names = {'A': 'Contexto en celdas', 'B': 'Operadores nominales', 'C': 'Contrato de producto',
         'D': 'Tercer instrumento', 'E': 'Productos diarios existentes'}
ranking = table(['Ruta', 'Juicio medio /100', 'Interpretación'], [
    [k + ' · ' + names[k], '–'.join(number(x, 1) for x in D['votes']['aggregate_mean_ranges'][k]),
     'Primera auditoría operativa' if k == 'C' else 'Posición secundaria incierta; no prueba científica']
    for k in ('C', 'B', 'E', 'A', 'D')
], 'Promedios descriptivos de tres juicios; rangos de incertidumbre subjetiva')

primary = D['context']['primary_and_predeclared_sensitivities']['PRIMARY_2010_alltypes']
context_rows = [[r['regime'], r['n'], number(r['C00_mae'], 6), number(r['C11_mae'], 6), number(r['delta_mae'], 6)]
                for r in primary['regimes']]
context_table = table(['SOURCE/tiempo', 'Filas held', 'Control C00', 'Contexto C11', 'ΔMAE C11−C00'],
                      context_rows, 'Iteración 23: misma población y control, antes de reconciliar')
cold_table = table(['Régimen', 'ΔMAE padre−M1', 'Lectura'], [
    [r['regime'], number(r['delta_mae'], 6), 'Mejora' if r['delta_mae'] < 0 else 'Retrocede']
    for r in D['cold']['primary']['regimes']
], 'Iteración 21: transporte a región y período reservados dentro del desarrollo')

contract_rows = []
for group, label in [('all54', '54 comunas'), ('published14', '14 publicadas'), ('remaining40', '40 restantes')]:
    for population, title in [('all_months', 'Todos los meses'), ('YC_50_plus_FIXED', 'Extremos fijos Y_C≥50')]:
        item = D['contract']['reports'][group][population]
        contract_rows.append([label, title, item['CC']['n'],
                              number(item['CC']['delta_coherent_minus_B'], 6),
                              number(item['OO']['delta_coherent_minus_B'], 6)])
contract_table = table(['Grupo', 'Población fija', 'N', 'ΔCC', 'ΔOO'], contract_rows,
                       '24C terminado: Δ=MAE(E_coherent)−MAE(B); negativo favorece la decisión coherente')
material = D['contract']['primary']
closure_table = table(['Instrumento', 'Prioridad', 'Residuo común (km²)', 'Control 1 m²'], [
    [r['product'], r['priority'], number(r['residual_m2']/1e6, 6), 'Falla' if not r['passed'] else 'Pasa']
    for r in D['closure']['rows'] if r['case'] == '2023'
], '24B: suma de áreas comunes por píxel menos intersección de uniones')
positive_rows = []
for product in ('MYD14', 'VNP14IMG'):
    counts = D['ledger']['cases']['2023'][product]['priorities']['early']['positive_scope_geometry']
    total = sum(v for k, v in counts.items() if k.startswith('centre_AOI:'))
    positive_rows.append([product, total, counts.get('centre_AOI:nominal_CORE', 0),
                          counts.get('centre_AOI:geometry_edge_unresolved', 0)])
positive_table = table(['Instrumento', 'Positivos originales AOI', 'CORE nominal', 'Borde sin área identificada'],
                       positive_rows, 'Conteos individuales revisados; no son una concordancia entre sensores')
original_rows = {r['id']: r for r in D['origin']['original']}
origin_rows = []
for row in D['origin']['centered']:
    if row['kind'] != 'selected_GEO_regression_counterexample':
        continue
    old = original_rows[row['id']]
    old_area = old['intersection_pq']['area_m2']
    origin_rows.append([row['id'], 'Pasa' if old['regression_checks_pass'] else 'Falla',
                        'Pasa' if row['regression_checks_pass'] else 'Falla',
                        f'{old_area:.3e}' if 0 < old_area < .001 else number(old_area, 3),
                        number(row['intersection_pq']['area_m2'], 3)])
origin_table = table(['Ejemplo fijo', 'Gate original', 'Gate centrado', 'I original m²', 'I centrada m²'],
                     origin_rows, '29: la misma geometría exacta puede producir overlays distintos por redondeo interno')
witness_count = len(D['witness']['rows'])
witness_refutations = sum(v['status'] == 'refuted_below_exact_lower_bound'
                          for r in D['witness']['rows'] for v in r['area_comparisons'].values())
witness_figure = '''<div class="scroll" tabindex="0" role="region" aria-label="Diagrama desplazable"><svg viewBox="0 0 1000 315" role="img" aria-label="Un cuadrado contenido en ambos polígonos fija una cota inferior de intersección" xmlns="http://www.w3.org/2000/svg" style="font-family:system-ui,sans-serif;fill:#18343c"><rect x="55" y="65" width="530" height="175" fill="#e4f0ef" stroke="#156c65" stroke-width="2"/><rect x="355" y="30" width="570" height="185" fill="#f8ecd9" fill-opacity=".65" stroke="#a8572a" stroke-width="2"/><text x="85" y="100" font-size="21">Polígono p</text><text x="735" y="70" font-size="21">Polígono q</text><rect x="430" y="105" width="90" height="90" fill="#18343c"/><text x="443" y="145" font-size="18" fill="white">Q ⊂ p∩q</text><text x="443" y="173" font-size="18" fill="white">4 m²</text><text x="80" y="285" font-size="23" font-weight="700">Si Q está contenido en ambos, el área común no puede ser casi cero.</text></svg></div>'''

sources = ''.join('<li><code>' + esc(path) + '</code><br><small>SHA256 ' + hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
                  + '</small></li>' for path in SOURCES.values())
plan = ROOT / 'docs/reviews/2026-11-15-joint-plan-24.md'
assert hashlib.sha256(plan.read_bytes()).hexdigest() == D['agreement']['plan_sha256']

page = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>De corregir cantidades a comprender observaciones · Goliat</title>
<style>
:root{{--ink:#18343c;--muted:#51686c;--paper:#f5f3eb;--line:#cbdad5;--teal:#156c65}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.65 system-ui,sans-serif}}header{{background:#18343c;color:white;padding:64px max(24px,calc((100vw - 1080px)/2))}}header p{{color:#dbeae5}}h1{{font-size:clamp(2.3rem,5vw,3.9rem);line-height:1.1;letter-spacing:-.035em;max-width:960px}}h2{{font-size:1.9rem;line-height:1.25}}h3{{font-size:1.14rem}}main{{max-width:1128px;margin:auto;padding:24px}}section{{padding:24px 0;scroll-margin-top:80px}}p{{max-width:970px}}a{{color:#08618c;text-underline-offset:3px}}a:focus-visible,summary:focus-visible,.scroll:focus-visible{{outline:3px solid #a8572a;outline-offset:4px}}nav{{display:flex;gap:20px;flex-wrap:wrap;background:white;padding:14px 24px;border-bottom:1px solid var(--line)}}.eyebrow{{font-size:.8rem;text-transform:uppercase;letter-spacing:.15em}}.lead{{font-size:1.2rem}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}.card,details,figure{{background:white;border:1px solid var(--line);border-radius:14px;padding:22px}}figure{{margin:20px 0}}figure svg{{display:block;width:100%;min-width:720px;height:auto;font-family:system-ui,sans-serif;fill:var(--ink)}}figcaption,small,.muted{{font-size:.85rem;color:var(--muted);overflow-wrap:anywhere}}.scroll{{overflow:auto}}table{{width:100%;border-collapse:collapse;background:white;font-size:.9rem;margin:16px 0}}caption{{text-align:left;font-weight:700;padding:14px;background:#e7efeb}}th,td{{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid var(--line)}}th{{background:#edf2ee}}.note{{background:#fff0dd;border-left:4px solid #a8572a;padding:15px 20px;border-radius:0 12px 12px 0}}.num{{font-size:2rem;font-weight:750;color:var(--teal)}}details{{margin:18px 0}}summary{{cursor:pointer;font-weight:700}}code{{overflow-wrap:anywhere;font-size:.85em}}li{{margin:9px 0}}.skip{{position:absolute;left:-200vw}}.skip:focus{{left:12px;top:12px;background:white;padding:12px;z-index:3}}footer{{padding:24px 0;border-top:1px solid var(--line);font-size:.9rem}}@media(max-width:760px){{.grid{{grid-template-columns:1fr}}header{{padding:40px 24px}}body{{font-size:16px}}h2{{font-size:1.6rem}}}}@media print{{body{{background:white}}header{{background:white;color:var(--ink);padding:15px}}header p{{color:var(--ink)}}nav{{display:none}}figure,.card{{break-inside:avoid}}}}
</style></head><body><a class="skip" href="#objetivo">Saltar al contenido</a>
<header><div class="eyebrow">Goliat · evaluación científica · 15 noviembre 2026</div><h1>Comprender cómo observa cada satélite.</h1><p class="lead">El siguiente avance no exige otra fórmula ganadora: exige separar diferencias de definición, representación y oportunidad de observar.</p><p>Plan acordado por dos consejos de tres miembros, con resultados negativos y límites visibles.</p></header>
<nav aria-label="Secciones"><a href="#objetivo">Objetivo</a><a href="#evidencia">Evidencia</a><a href="#consejos">Consejos</a><a href="#resultados24">Resultados 24C/E</a><a href="#plan">Plan</a><a href="#decisiones">Decisiones</a><a href="#trazabilidad">Fuentes</a></nav><main>
<section id="objetivo"><h2>Una historia comparable de actividad registrada.</h2><p class="note"><strong>Estado del snapshot:</strong> operador nominal de puntos verificado; todavía sin nueva comparación de etiquetas. El operador continuo conserva su fallo y G1 físico sigue pendiente.</p><p>La propuesta es construir un calendario MODIS–VIIRS donde un cambio de sensor no parezca automáticamente un cambio del fuego. El indicador actual cuenta celdas–día por plataforma y las agrega por comuna y mes. No cuenta incendios individuales, hectáreas quemadas ni ocurrencias físicas completas.</p><figure>{operator}<figcaption>El registro depende del instrumento y de sus condiciones. Ninguna fórmula de cantidades recupera por sí sola todas las oportunidades perdidas.</figcaption></figure>
<div class="grid"><div class="card"><h3>La pregunta original</h3><p>¿Cuánto desacuerdo persiste cuando ambos instrumentos tuvieron una oportunidad comparable de observar?</p></div><div class="card"><h3>La entrega defendible hoy</h3><p>Medir sensibilidad a contratos y construir un soporte nominal auditable. Mantener como desconocida la oportunidad física que aún no identificamos.</p></div><div class="card"><h3>El objetivo de producto</h3><p>Que un gestor distinga actividad habitual o excepcional y comprenda cuándo la evidencia es insuficiente para interpretarla.</p></div></div>
<details><summary>Cómo se relacionan las cinco hipótesis</summary><ol><li><strong>Observabilidad:</strong> prioridad central; puntos FIRMS solos no identifican nubes, humo y todas las oportunidades útiles.</li><li><strong>Comparación equivalente:</strong> el ledger nominal prepara soporte y exclusiones antes de comparar estados.</li><li><strong>Probabilidad y cantidad:</strong> ya se ensayó una distribución hurdle; su decisión puede mejorar MAE local y empeorar totales o subgrupos.</li><li><strong>Compartir por contexto:</strong> se ensayó una política fija de composición territorial; su primaria falló y se conserva.</li><li><strong>Evidencia nueva:</strong> un tercer instrumento queda pendiente de una pregunta localizada que pueda resolver; no es automáticamente verdad terreno.</li></ol></details></section>
<section id="evidencia"><h2>Lo aprendido obliga a cambiar de pregunta.</h2><p>La iteración 18 mejoró la asignación local manteniendo el total de B por construcción. Esa igualdad regional no constituye habilidad adicional. Después, el transporte regional mostró una mejora concentrada en un régimen, no una solución uniforme.</p>{cold_table}<p class="note">La máscara y el soporte de 21 difieren de 18. Sus MAE no deben compararse como si fueran el mismo experimento. Los cuatro regímenes dependen entre sí y las fechas pertenecen a desarrollo ya consultado.</p>
<h3>23 · El contexto comunal probado no supera su control</h3>{context_table}<div class="grid"><div class="card"><h3>Control uniforme</h3><div class="num">{number(primary['equal_four_regime_MAE_C00'],6)}</div><p>MAE medio con igual peso de cuatro regímenes.</p></div><div class="card"><h3>Contexto territorial</h3><div class="num">{number(primary['equal_four_regime_MAE_C11'],6)}</div><p>El error aumenta {number(-100*primary['relative_gain_from_equal_MAE'],4)} %.</p></div><div class="card"><h3>Resultado que se conserva</h3><p>Mejora uno de cuatro regímenes. El promedio por fila cambia de signo, pero no sustituye la primaria fijada.</p></div></div>
<p>Las sensibilidades 2001 y type0 no autorizan elegir retrospectivamente otra configuración. El contexto MCD12Q1 nominal 2001/2010 se reprocesó en 2022: permite este estudio retrospectivo, sin demostrar disponibilidad antes de 2012 ni mecanismo ecológico.</p>
<h3>La observación avanzó, con alcance selectivo</h3><p>La geometría nominal MODIS pasó sus controles dimensionales en los dos casos fijos, 2019 y 2023. VIIRS pasó un contraste con 13 referencias, todas de un solo escaneo 2023 y una región de agregación. Eso no valida todas las dimensiones VIIRS ni la PSF física.</p><p>La cercanía de centros y las referencias temporales de escaneo no equivalen a exposición por píxel. El flag global <code>Suspect</code> sigue sin semántica L2 resuelta; no lo interpretamos como defecto NASA demostrado. <strong>G1 físico permanece falso.</strong></p></section>
<section id="consejos"><h2>Primero acordar cómo decidir; después votar.</h2><figure>{process}<figcaption>El consejo adversario revisó los resultados del multifocal. La propuesta final volvió a ambos consejos para ratificación explícita.</figcaption></figure>{criteria}<p>Antes de sumar notas se aplicaron límites no compensables: desconocido no es cero; no inventar verdad física o causalidad; no rescatar una primaria fallida con un secundario favorable; no cambiar producción. Una aproximación nominal declarada puede estudiarse sin exigir una PSF exacta, conservando sus límites.</p>{ranking}
<p class="note">Las notas son juicios sobre propuestas y primeros entregables. Sus rangos no son intervalos de confianza, y los miembros no aportan réplicas estadísticas independientes. Hubo acuerdo en la secuencia práctica, no unanimidad en las posiciones B/E/A.</p>
<details><summary>Qué vio el adversario que el primer consejo debía corregir</summary><ul><li><strong>Elegir contrato por significado:</strong> nunca por cuál favorece al modelo.</li><li><strong>Acotar la estabilidad:</strong> dos contratos estables no descartan problemas de observabilidad ni explican el plateau contextual.</li><li><strong>Conservar positivos excluidos:</strong> elegir propietario geométrico puede dejar fuera parte de un píxel positivo; el ledger debe mostrarla.</li><li><strong>No localizar fuego subpíxel:</strong> una etiqueta heredada por un átomo describe el operador nominal.</li><li><strong>Mantener filas equivalentes:</strong> el estrato extremo pareado usa Y_C≥50; Y_O≥50 se presenta aparte.</li><li><strong>Contabilizar coste de oportunidad:</strong> C tiene un cap que incluye revisión y no bloquea B.</li></ul></details></section>
<section id="resultados24"><h2>24C/E: cerrar dos preguntas y mantener sus límites.</h2><p>La auditoría contractual ya terminó y recibió revisión independiente. Reprodujo 108 CSV, las seis funciones congeladas y 128 reconciliaciones sobre las mismas 3.456 filas, sin nuevos ajustes. La ventaja global conserva signo: el cambio de Δ es {number(material['change'],6)}, menor que τ={number(material['tau'],6)}. Esa estabilidad acotada no se extiende automáticamente a los territorios.</p>{contract_table}<p class="note">En las 14 comunas publicadas la ventaja casi desaparece y los 21 meses extremos siguen empeorando frente a B. El resultado global no permite promover el candidato. No se infiere que el contrato haya causado físicamente las diferencias.</p><p>El preflight E también terminó: descarta <em>estos productos</em> como denominador comparable de pasadas despejadas. Dos historias [tierra sin detección, tierra sin detección] y [nube, tierra sin detección] pueden producir el mismo compuesto diario; el historial no queda identificado. VNP14A1 usa bandas de 750 m y la dirección del bit QA 2 discrepa entre documentos. Se conserva desconocida, sin implementar un decoder supuesto.</p><p>Este cierre no afirma inexistencia global de otro producto 375 m ni inutilidad de un calendario de clases compuestas. Hubo {D['daily']['science_data_downloaded_bytes']} bytes de datos científicos descargados para E. B continúa con su ledger; todavía no hay nueva concordancia entre estados.</p></section>
<section><h2>24B: la revisión detuvo una comparación inválida.</h2><p>El ledger conservó todos los positivos originales y mostró una pérdida de representación: dos de seis positivos Aqua dentro de la AOI 2023 están en bordes sin polígono CORE. Sus áreas son desconocidas, no cero. Una unión nominal casi completa no acredita retención de todas las detecciones.</p>{positive_table}<p>Además, el control independiente encontró que las áreas comunes por píxel no suman la intersección de las uniones. La partición por píxel y el cierre de áreas propias habían pasado, pero eran controles insuficientes.</p>{closure_table}<p class="note"><strong>Las áreas comunes 2023 no están validadas y la concordancia queda bloqueada.</strong> Los originales se conservan como intento fallido. El diagnóstico aislado reproduce polígonos válidos con predicados de contención verdaderos, intersección de área cero y diferencia de área completa. Se investiga el motor geométrico con WKB sin etiquetas de fuego; ninguna tolerancia, prioridad o precisión se ajusta para rescatar el resultado.</p><p>Los diseños 25 de estados nominales y 26 de soporte en bordes siguen pendientes. Resolver el motor no probaría oportunidad física ni recuperaría automáticamente los bordes.</p></section>
<section><h2>27 y 29: separar versión del motor y representación numérica.</h2><p>El diagnóstico 27 comparó GEOS 3.14.1 con 3.15.0 en procesos aislados: cuatro de cinco regresores fallan controles en ambas versiones, mediante mecanismos distintos. El quinto y los cuatro controles sintéticos pasan en ambas. Actualizar la biblioteca no resolvió estos ejemplos y no se demostró que el issue 1499 fuera la causa.</p><p>El consejo técnico eligió después un único origen: el centro AOI ya fijado. Antes de cualquier overlay centrado, el estudio 29 certificó <strong>{D['exact']['total_coordinate_tuples_with_multiplicity']} tuplas</strong> mediante igualdad racional exacta de las restas y roundtrip de todos los bits, componentes y anillos. No se escogió un desplazamiento por el acuerdo entre sensores ni se leyó fuego o QA.</p>{origin_table}<p class="note">El cambio es 1/5→5/5 pases locales, no cinco errores demostrados reparados. Aqua tardío 833/1149 ya pasaba y su área cambia de ≈3×10⁻⁸ a 2,5 millones de m²: esos gates locales por sí solos no validan el área. La traducción preserva exactamente las entradas, pero los cálculos internos redondean de otra forma.</p><p>El resultado permite una revalidación ampliada de particiones, disjunción, uniones y áreas comunes, con controles independientes. <strong>El ledger completo y G1 siguen sin validar.</strong> Los cinco ejemplos son regresores seleccionados, no una muestra probabilística. Los resultados negativos 24B/27 se conservan y no se promueve el modelo mensual.</p></section>
<section><h2>30A: una prueba independiente refuta las áreas casi nulas.</h2><figure>{witness_figure}<figcaption>Esquema conceptual, sin escala. Q es un testigo geométrico; no representa fuego, un footprint físico ni una superficie quemada.</figcaption></figure><p>Un segundo método, sin GEOS, usa aritmética racional exacta para certificar un cuadrado contenido estrictamente en ambos operandos. Verifica pertenencia y distancia a todas las fronteras, incluidos agujeros. En los {witness_count} pares encontró un cuadrado de 4 m²; por tanto la intersección de cada par tiene al menos esa área.</p><p>La comparación refuta las {witness_refutations} áreas originales guardadas —los dos órdenes de los cinco pares—, incluido el caso que pasaba los gates anteriores. Las áreas centradas superan la cota: quedan <strong>no refutadas por este testigo, no validadas</strong>. Otro verificador reconstruyó los certificados desde los WKB, sin importar el helper del autor.</p><p>El cuadrado es una cota inferior deliberadamente pequeña, no una estimación del área completa. No encontrarlo habría dejado la búsqueda inconclusa. El estudio 30B se registró por separado para revalidar toda la geometría, con cierres globales y dos expresiones computacionales obligatorias. Su resultado negativo se explica a continuación.</p></section>
<section><h2>30B y 32B: un fallo global y una magnitud local distinta.</h2><p>La revalidación completa 30B terminó negativa y parcial: los dos cruces de 2019 completaron sus controles, pero Aqua 2023 falló por <code>{esc(D['full_failure']['error'])}</code>. No se ejecutó replay QA y no se eligió otro origen, precisión o tolerancia para hacer pasar ese intento.</p><p>El diagnóstico 32B adjudicó exactamente el último par registrado, con dos algoritmos racionales independientes. Su intersección es positiva: aproximadamente <strong>1,82×10⁻¹⁰ m²</strong>. Eso refuta el overlay cero para ese par y cuantifica una discrepancia local minúscula; no prueba que ese registro sea la única causa del fallo ni acota los demás errores.</p><p class="note">Este par es distinto de los cinco regresores anteriores con áreas faltantes de kilómetros cuadrados. Una cota local pequeña no permite llamar despreciable el error global ni convertir retrospectivamente 30B en aprobado.</p></section>
<section><h2>31–32A: cambiar la pregunta sin ocultar el fallo.</h2><p>Los dos consejos volvieron a deliberar con los mismos criterios. Ingeniería prefería adjudicar primero el par local; estadística y el agente loco preferían muestreo puntual. Los seis ratificaron una ejecución paralela acotada, conservando ese desacuerdo. El nuevo estimando no intenta reparar áreas continuas.</p><p>32A fija puntos de consulta a 250 m y una grilla de 500 m realmente anidada, con la misma ancla. Usa fase principal (0,0) y sensibilidad diagonal (125,125) m, ambas declaradas antes de etiquetas. La pertenencia a quads nominales y la propiedad por escaneo se calculan con enteros exactos, sin GEOS para predicados o candidaturas.</p><div class="grid"><div class="card"><h3>Consultas prefijadas</h3><div class="num">{D['points']['queries_total']:,}</div><p>En ocho poblaciones de caso, fase y paso; no se multiplican como réplicas por sensor o prioridad.</p></div><div class="card"><h3>Candidatos verificados</h3><div class="num">{D['points']['candidate_tests_total']:,}</div><p>Todos los candidatos punto–quad se reconstruyeron por un índice independiente.</p></div><div class="card"><h3>Pase exclusivamente GEO</h3><p>Propietarios y causas, simplicidad de los 101.038 quads y anidamiento fueron comprobados independientemente. Sin etiquetas ni QA.</p></div></div><p>El verificador usó búsqueda por grillas y winding number distintos de los del autor. Conservó puntos sin soporte nominal y los estados de frontera, tiempo desconocido y conflicto dentro del mismo escaneo; que no aparezcan algunos en estos datos no elimina sus reglas.</p><p class="note">La futura etiqueta será la del píxel nominal asignado al punto, <strong>no actividad física localizada en ese punto</strong>. Miles de consultas siguen siendo dos casos con píxeles compartidos. Sus frecuencias no son superficies ni incendios, y el pase no habilita automáticamente incorporar QA. El siguiente contraste necesita protocolo propio, cohorte fija y retención nativa visible.</p></section>
<section id="plan"><h2>El plan acordado y sus entregas acotadas.</h2><figure>{parallel}<figcaption>Inicio acordado de implementación: 04:29:28 UTC. C y el primer ledger B: 05:29:28 UTC; E documental: 04:59:28 UTC. C y E cerraron; B entregó evidencia parcial y quedó bloqueado en la revisión. El horizonte general sigue siendo 11:30 UTC, 08:30 de Santiago.</figcaption></figure>
<h3>C · ¿Cuánto depende el resultado del contrato?</h3><p>Se usan las mismas 3.456 filas disponibles en ambos archivos: 54 comunas y 64 meses. C representa el contrato científico y O el contrato observado del producto. Se reproducen identidades antes de medir pérdidas; no se reajustan modelos ni se agregan fechas faltantes.</p><p>La primaria propuesta es Δ=MAE(E_coherent)−MAE(B). Los extremos CC/OO aplican sus respectivas entradas y targets; CO/OC son diagnósticos de mezcla de representaciones, no efectos instrumentales. El bridge S-NPP–NOAA20 sigue sin demostrar. Cada entrada requiere su propio presupuesto ΣB sobre 54 comunas antes de filtrar.</p>
<details><summary>Cómo interpretar las cotas y la materialidad</summary><p>Con f y g fijos, el cambio de ganancia MAE al sustituir sólo el target está acotado por 2·media|Y_C−Y_O|. El valor 440/3456 sólo corresponde al panel global conocido; no cubre cambio de entrada, error regional ni todos los subgrupos. Cada población requiere su propia cota.</p><p>Se fija τ=0,01·MAE(B_CC) como regla práctica previa, sin significado NASA ni significación estadística. Hay dependencia material si |ΔOO−ΔCC|≥τ. Toda inversión de signo se registra; se llama material sólo si ambos extremos superan τ en magnitud. Los perjuicios territoriales siguen visibles bajo ese umbral.</p></details>
<h3>B · ¿Qué información conserva la representación nominal?</h3><p>El primer resultado será un ledger: geometría original, unión, propiedad, exclusiones, soporte común y retención de positivos por instrumento. La prioridad de escaneos se fija por geometría antes de mirar QA o actividad. Escaneo temprano es primario y tardío una sensibilidad; no se elige el que maximice acuerdo.</p><p>Se separan borde CORE, falta de soporte, propiedad y calidad. Tierra, agua y desconocidos conservan su identidad. Los positivos 7–9 originales se registran aun si quedan excluidos; M13 no nominal no los convierte silenciosamente en cero. Todavía no se autoriza una matriz de concordancia entre estados.</p>
<h3>E · ¿Sirven los productos diarios para representar oportunidad?</h3><p>MYD14A1 contiene compuestos diarios empaquetados en ocho días; esa composición pierde la historia individual de pasadas. VNP14A1 deriva de bandas de 750 m y no equivale al producto 375 m VNP14IMG. El preflight verifica qué proxy es defendible y qué sigue desconocido, sin dividir conteos por una fracción despejada no comparable.</p></section>
<section id="decisiones"><h2>Un plan sólido también sabe cuándo detenerse.</h2>{table(['Resultado', 'Acción', 'Afirmación que no permite'],[
['Falla identidad CC o fuente O','Detener comparaciones y registrar discrepancia','No calcular un ranking con panel sustituido'],
['C cambia materialmente entre contratos','Documentar dependencia y significado del contrato','No elegir el contrato favorable'],
['C permanece estable','Cerrar esta sensibilidad acotada y continuar B','No declarar resuelta la observabilidad'],
['C vence o resulta inconcluso','Conservar la entrega verificable alcanzada','No reiniciar el cap para rescatar la auditoría'],
['B muestra pérdida o dependencia de propiedad','Resolver representación y preservar exclusiones','No llamar mejora a eliminar casos difíciles'],
['E no conserva información suficiente','Descartar su uso como denominador físico','No equiparar accesibilidad con identificabilidad'],
], 'Bifurcaciones predefinidas, sin seleccionar el desenlace favorable')}
<p>La agregación de ganancias marginales consiste aquí en acumular controles reproducidos, negativas conservadas y ambigüedades resueltas. No se suman porcentajes de estudios con distintos targets, máscaras, períodos o unidades. Una ganancia cuantitativa exige comparar contra el mismo control y la misma población.</p></section>
<section id="trazabilidad"><h2>Evidencia verificable y alcance del documento.</h2><p>Este snapshot explica evidencia hasta 32A/B, incluidos los fallos 24B/30B y 27 negativo. No contiene nueva concordancia ni validación del operador continuo. Se genera leyendo resúmenes congelados, sin abrir crudos, credenciales, ajustar modelos ni recalcular predicciones.</p><p><a href="science-session-2026-11-14.html">Informe anterior: iteraciones 16–20A y casos L2</a>. Revisión incremental: <a href="https://github.com/Loddrik/goliat-fire-calendar/pull/46">PR46</a>, <a href="https://github.com/Loddrik/goliat-fire-calendar/pull/49">PR49</a>, <a href="https://github.com/Loddrik/goliat-fire-calendar/pull/50">PR50</a>, <a href="https://github.com/Loddrik/goliat-fire-calendar/pull/51">PR51</a>, <a href="https://github.com/Loddrik/goliat-fire-calendar/pull/53">PR53</a> y <a href="https://github.com/Loddrik/goliat-fire-calendar/pull/54">PR54</a>. Los enlaces no certifican estados de aprobación o merge posteriores.</p>
<details><summary>Fuentes locales y hashes del snapshot</summary><ul>{sources}</ul><p>Plan conjunto SHA256 <code>{D['agreement']['plan_sha256']}</code>. Ratificación UTC: {esc(D['agreement']['ratified_at_utc'])}.</p></details>
<details><summary>Documentación primaria para el preflight diario</summary><ul><li><a href="https://www.earthdata.nasa.gov/s3fs-public/imported/MODIS_C6_Fire_User_Guide_B.pdf">NASA: guía MODIS C6, §5.2</a>.</li><li><a href="https://lpdaac.usgs.gov/documents/427/VNP14_User_Guide_V1.pdf">Guía VIIRS VNP14: composición de bandas de 750 m</a>.</li><li><a href="https://firms.modaps.eosdis.nasa.gov/alerts/notes.php">NASA FIRMS: notas de interpretación</a>.</li></ul></details>
<footer>HTML autónomo con diagramas SVG propios, tablas y detalles accesibles. Sin Mermaid, JavaScript ni recursos gráficos remotos. No cambia la publicación M1/14 ni certifica uso operacional.</footer></section></main></body></html>'''
DEST.parent.mkdir(parents=True, exist_ok=True)
DEST.write_text('\n'.join(line.rstrip() for line in page.splitlines()) + '\n')
print(DEST, DEST.stat().st_size, 'bytes')
