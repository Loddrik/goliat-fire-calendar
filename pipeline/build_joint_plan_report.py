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
    'allocation18': 'data/processed/coherent_audit/summary.json',
    'adjacency36': 'data/processed/daily_adjacency_audit/summary.json',
    'adjacency36_review': 'docs/reviews/evidence/daily-adjacency-independent-review/summary.json',
    'context37': 'data/processed/daily_context_audit/summary.json',
    'context37_review': 'docs/reviews/evidence/daily-context-independent-review/summary.json',
    'crps39': 'data/processed/crps_audit/summary.json',
    'crps39_review': 'docs/reviews/evidence/crps-independent-review/full-review/summary.json',
    'goes40': 'docs/reviews/evidence/goes-preflight/summary.json',
    'goes40_catalog': 'docs/reviews/evidence/goes-preflight/catalog-summary.json',
    'goes40_review': 'docs/reviews/evidence/goes-preflight-independent-review/summary.json',
    'votes38': 'docs/reviews/evidence/direction-council-38/aggregate.json',
    'ratification38': 'docs/reviews/evidence/direction-council-38/ratification.json',
    'amendment40': 'docs/reviews/evidence/direction-council-38/C-resource-amendment-ratification.json',
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
    'groups35_review': 'docs/reviews/evidence/group-budget-independent-review/summary.json',
    'groups35': 'data/processed/group_budget_audit/summary.json',
    'votes35': 'docs/reviews/evidence/direction-council-35/aggregate.json',
    'ratification35': 'docs/reviews/evidence/direction-council-35/ratification.json',
    'states33_review': 'docs/reviews/evidence/discrete-state-comparison-independent-review/summary.json',
    'states33': 'docs/reviews/evidence/discrete-state-comparison/attempt-01/summary.json',
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

point_rows33 = []
for case in ('2019', '2023'):
    result = D['states33']['scenarios'][case + '-phase0-h250-early']
    n = result['nine']
    point_rows33.append([case, result['Ntotal'], n['00'], n['10'], n['01'], n['11'], result['five']['U'],
                         'No definido: unión positiva vacía' if result['Jaccard_known'] is None else number(100 * result['Jaccard_known'], 1) + ' %'])
point_table33 = table(['Caso', 'N total', '00', '10', '01', '11', 'Algún U', 'Jaccard conocido'], point_rows33,
                      '33: fase (0,0), paso 250 m, prioridad temprana; primer símbolo MODIS. U nunca se convierte en 0.')
point_figure33 = '<div class="scroll" tabindex="0" role="region" aria-label="Diagrama de unidades desplazable"><svg viewBox="0 0 1000 300" role="img" aria-label="Un registro nativo puede asignar su misma etiqueta a varios puntos; no son incendios distintos" xmlns="http://www.w3.org/2000/svg" style="font-family:system-ui,sans-serif;fill:#18343c"><rect x="45" y="55" width="265" height="150" rx="12" fill="#e4f0ef" stroke="#156c65"/><text x="70" y="100" font-size="23">Un píxel nativo</text><text x="70" y="140" font-size="21">Máscara registrada 7–9</text><text x="70" y="177" font-size="18">Su quad es nominal.</text><path d="M330 130 H430" stroke="#18343c" stroke-width="3"/><path d="M415 120 L430 130 L415 140" fill="none" stroke="#18343c" stroke-width="3"/><rect x="450" y="55" width="500" height="150" rx="12" fill="#f8ecd9" stroke="#a8572a"/><text x="475" y="100" font-size="23">Varios puntos reciben la misma etiqueta</text><text x="475" y="140" font-size="20">El número depende de la grilla y la propiedad.</text><text x="475" y="177" font-size="18">No localiza fuego físico en cada punto.</text><text x="55" y="260" font-size="21" font-weight="700">Píxeles positivos, puntos etiquetados e incendios son unidades diferentes.</text></svg></div>'

group_table35 = table(['Régimen', 'N held', 'Global G', 'Separado R', 'ΔR−G'],
                       [[r['regime'], r['n_held'], number(r['G_mae'], 6), number(r['R_mae'], 6), number(r['delta_R_minus_G'], 6)]
                        for r in D['groups35']['primary']['regimes']],
                       '35A: mismas distribuciones y modelo base; primaria igual peso de cuatro regímenes')
group_figure35 = '<div class="scroll" tabindex="0" role="region" aria-label="Diagrama de presupuestos desplazable"><svg viewBox="0 0 1000 325" role="img" aria-label="Las mismas distribuciones alimentan dos reglas de presupuesto, global y separada" xmlns="http://www.w3.org/2000/svg" style="font-family:system-ui,sans-serif;fill:#18343c"><rect x="35" y="95" width="310" height="125" rx="12" fill="#e4f0ef" stroke="#156c65"/><text x="58" y="137" font-size="23">CDF y modelo B fijos</text><text x="58" y="174" font-size="18">Mismos registros, sin nuevo ajuste.</text><path d="M360 155 L450 75 M360 155 L450 235" stroke="#18343c" stroke-width="3" fill="none"/><rect x="460" y="25" width="505" height="120" rx="12" fill="#eef3f6" stroke="#34576c"/><text x="485" y="65" font-size="23">G: presupuesto global de 54 comunas</text><text x="485" y="103" font-size="18">Puede redistribuir entre SOURCE y held.</text><rect x="460" y="175" width="505" height="120" rx="12" fill="#f8ecd9" stroke="#a8572a"/><text x="485" y="215" font-size="23">R: dos presupuestos separados</text><text x="485" y="253" font-size="18">Transferencia entre roles cero por construcción.</text></svg></div>'


# Only arithmetic on already frozen summaries, never a new target loss.
allocation18 = D['allocation18']['nested']['all54']['all_months']['methods']
endpoint18 = 100 * (1 - allocation18['E_coherent']['mae'] / allocation18['M1']['mae'])
allocation_table18 = table(['Método', 'MAE del mismo panel', 'Alcance'], [
    ['M1 por origen', number(allocation18['M1']['mae'], 6), 'Referencia regional reajustada dentro de cada origen'],
    ['B afín', number(allocation18['M1_B']['mae'], 6), 'Política regularizada de investigación'],
    ['E_coherent', number(allocation18['E_coherent']['mae'], 6), 'Asignación global con presupuesto de B'],
], '18: mismas 5.184 filas anidadas; máscaras aprendidas por origen, no 223 celdas fijas')

adj36 = D['adjacency36']['overall']
adj36_verified = D['adjacency36_review']['verified']
adjacency_table36 = table(['Control o descriptor', 'Cantidad', 'Qué permite concluir'], [
    ['CUT-meses únicos', adj36['n'], 'Historia Aqua del contrato21; no se usa SNP'],
    ['Identidades Aqua expandidas', adj36_verified['expanded_Aqua_identity_rows'], 'El cubo reproduce exactamente la entrada21'],
    ['Meses con D real=1', adj36['D_real_1'], 'Existe una pareja en la misma celda y dentro del mes'],
    ['Meses con D placebo=1', adj36['D_placebo_1'], 'La permutación también puede conservar o crear parejas'],
    ['Meses donde D difiere', adj36['D_discordant'], 'Contraste de features; no mejora predictiva'],
], '36: integridad de features y calendario, sin targets, fits o pérdidas')

# Conceptual matrix, not a plot of measured data or a claim about the SHA output.
calendar_parts = []
for left, title, rows in [
    (20, 'Calendario original', [('Celda A', [1, 1, 0, 0]), ('Celda B', [0, 1, 0, 0])]),
    (670, 'Calendario permutado', [('Celda A', [1, 0, 1, 0]), ('Celda B', [1, 0, 0, 0])]),
]:
    calendar_parts.append(f'<rect x="{left}" y="35" width="310" height="265" rx="12" fill="#fff" stroke="#a7bfbd"/>')
    calendar_parts.append(f'<text x="{left+18}" y="69" font-size="21" font-weight="700">{title}</text>')
    for day in range(4):
        calendar_parts.append(f'<text x="{left+105+45*day}" y="113" text-anchor="middle" font-size="16">D{day+1}</text>')
    for row, (label, values) in enumerate(rows):
        cy = 153 + 65*row
        calendar_parts.append(f'<text x="{left+15}" y="{cy+7}" font-size="15">{label}</text>')
        for col, value in enumerate(values):
            cx = left+105+45*col
            calendar_parts.append(f'<rect x="{cx-18}" y="{cy-19}" width="36" height="38" fill="{"#e4f0ef" if value else "#f1f2ed"}" stroke="#a7bfbd"/>')
            calendar_parts.append(f'<text x="{cx}" y="{cy+6}" text-anchor="middle" font-size="22">{"●" if value else "—"}</text>')
calendar_parts.append('<rect x="350" y="35" width="300" height="265" rx="12" fill="#f8ecd9" stroke="#a8572a"/>')
calendar_parts.append('<text x="370" y="70" font-size="21" font-weight="700">Un orden compartido</text>')
for index, dest in enumerate((3, 1, 4, 2)):
    calendar_parts.append(f'<text x="375" y="{110+35*index}" font-size="18">ORIGEN {index+1} → DESTINO {dest}</text>')
calendar_parts.append('<text x="370" y="270" font-size="14">Orden ilustrativo, no resultado SHA real.</text>')
calendar_parts.append('<path d="M330 166 L347 166 M650 166 L667 166" stroke="#18343c" stroke-width="3" fill="none"/>')
calendar_parts.append('<text x="35" y="348" font-size="21" font-weight="700">Cada día original d va a rankedDays[d−1].</text>')
calendar_parts.append('<text x="35" y="384" font-size="19">Los días vacíos también se mueven, junto con todas las celdas.</text>')
calendar_parts.append('<text x="35" y="419" font-size="18">● = detección registrada; — = sin registro. No describe observación física.</text>')
calendar_figure36 = ('<div class="scroll" tabindex="0" role="region" aria-label="Diagrama desplazable de permutación">'
    '<svg viewBox="0 0 1000 445" role="img" aria-label="Ejemplo conceptual de cuatro días: la misma permutación mueve columnas completas y vacías para todas las celdas" xmlns="http://www.w3.org/2000/svg" style="font-family:system-ui,sans-serif;fill:#18343c">'
    + ''.join(calendar_parts) + '</svg></div>')

primary37 = D['context37']['primary']
context_table37 = table(['Régimen', 'N held', 'ΔMAE real−placebo', 'ΔMAE real−G21'], [
    [r['regime'], r['n'], number(r['delta_real_minus_placebo'], 10), number(r['delta_real_minus_G'], 10)]
    for r in primary37['regimes']
], '37: ambos contrastes medios debían ser negativos; menor MAE es mejor')
context_cost_rows37 = []
for regime in ('08_backward', '08_forward', '16_backward', '16_forward'):
    report = D['context37']['reports'][regime]['held_published14']['all_months']
    real, placebo = report['methods']['Q_real']['mae'], report['methods']['Q_placebo']['mae']
    context_cost_rows37.append([regime, report['n'], number(real, 6), number(placebo, 6), number(real-placebo, 6)])
context_cost_table37 = table(['Régimen', 'N held/publicadas', 'MAE real', 'MAE placebo', 'Δ real−placebo'],
    context_cost_rows37, '37: coste en held de las 14 comunas publicadas, visible en los cuatro regímenes')

council_table38 = table(['Ruta', 'Entregable propuesto', 'Rango subjetivo del consejo multifocal'], [
    [code, label, '–'.join(number(v, 2) for v in D['votes38']['options'][code]['mean_subjective_range'])]
    for code, label in [('A', 'Puntuar CDF congelada mediante CRPS'), ('C', 'Preflight documental GOES'), ('D', 'Consolidación y cierre auditable')]
] + [['B', 'Evaluar una decisión con costes de acción', 'N/A: faltan acción y costes; no se imputa cero']],
    '38: promedio de los tres votos multifocales; los tres adversarios revisan límites y secuencia, no se inventa un ranking de seis notas')

primary39 = D['crps39']['primary']
crps_table39 = table(['Régimen', 'N held', 'CRPS F21', 'CRPS δB = MAE B', 'Δ F21−δB'], [
    [r['regime'], r['n'], number(r['mean_CRPS_F21'], 9), number(r['mean_CRPS_delta_B'], 9), number(r['difference_F21_minus_delta_B'], 9)]
    for r in primary39['regimes']
], '39: distribución marginal original21 frente a forecast degenerado; no son dos modelos puntuales')
crps_cost_rows39 = []
for regime, group, pop, label in [
    ('16_forward', 'held_published14', 'all_months', 'Held/publicadas, todos los meses'),
    ('16_backward', 'held', 'zero_reference', 'Held, Y registrado=0'),
    ('08_backward', 'held', 'reference_50_plus', 'Held, extremo Y≥50'),
    ('08_forward', 'held', 'reference_50_plus', 'Held, extremo Y≥50'),
    ('16_backward', 'held', 'reference_50_plus', 'Held, extremo Y≥50'),
    ('16_forward', 'held', 'reference_50_plus', 'Held, extremo Y≥50'),
]:
    item = D['crps39']['reports'][regime][group][pop]
    crps_cost_rows39.append([regime, label, item['n'], number(item['mean_difference_F21_minus_delta_B'], 10)])
crps_cost_table39 = table(['Régimen', 'Población fijada', 'N', 'ΔCRPS F21−δB'], crps_cost_rows39,
    '39: un promedio favorable no borra costes territoriales, ceros o extremos; positivo empeora')
goes_table40 = table(['Caso fijo', 'Catálogo horario 18 UTC', 'Objetos listados', 'Modo en nombre', 'Separación de inicios'], [
    ['2019-01-03', '2019/003/18', D['goes40']['catalogue_objects_2019'], 'M3', '15 min'],
    ['2023-02-10', '2023/041/18', D['goes40']['catalogue_objects_2023'], 'M6', '10 min'],
], '40: metadatos de catálogo; ningún contenido científico de estos objetos fue descargado')
snapshot_utc = D['goes40_review']['completed_utc']

sources = ''.join('<li><code>' + esc(path) + '</code><br><small>SHA256 ' + hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
                  + '</small></li>' for path in SOURCES.values())
plan = ROOT / 'docs/reviews/2026-11-15-joint-plan-24.md'
assert hashlib.sha256(plan.read_bytes()).hexdigest() == D['agreement']['plan_sha256']
assert hashlib.sha256((ROOT / 'docs/reviews/2026-11-15-joint-plan-38.md').read_bytes()).hexdigest() == D['ratification38']['plan_sha256']

page = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Goliat · evidencia científica hasta 40 y decisión final</title>
<style>
:root{{--ink:#18343c;--muted:#51686c;--paper:#f5f3eb;--line:#cbdad5;--teal:#156c65}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.65 system-ui,sans-serif}}header{{background:#18343c;color:white;padding:64px max(24px,calc((100vw - 1080px)/2))}}header p{{color:#dbeae5}}h1{{font-size:clamp(2.3rem,5vw,3.9rem);line-height:1.1;letter-spacing:-.035em;max-width:960px}}h2{{font-size:1.9rem;line-height:1.25}}h3{{font-size:1.14rem}}main{{max-width:1128px;margin:auto;padding:24px}}section{{padding:24px 0;scroll-margin-top:80px}}p{{max-width:970px}}a{{color:#08618c;text-underline-offset:3px}}a:focus-visible,summary:focus-visible,.scroll:focus-visible{{outline:3px solid #a8572a;outline-offset:4px}}nav{{display:flex;gap:20px;flex-wrap:wrap;background:white;padding:14px 24px;border-bottom:1px solid var(--line)}}.eyebrow{{font-size:.8rem;text-transform:uppercase;letter-spacing:.15em}}.lead{{font-size:1.2rem}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}.card,details,figure{{background:white;border:1px solid var(--line);border-radius:14px;padding:22px}}figure{{margin:20px 0}}figure svg{{display:block;width:100%;min-width:720px;height:auto;font-family:system-ui,sans-serif;fill:var(--ink)}}figcaption,small,.muted{{font-size:.85rem;color:var(--muted);overflow-wrap:anywhere}}.scroll{{overflow:auto}}table{{width:100%;border-collapse:collapse;background:white;font-size:.9rem;margin:16px 0}}caption{{text-align:left;font-weight:700;padding:14px;background:#e7efeb}}th,td{{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid var(--line)}}th{{background:#edf2ee}}.note{{background:#fff0dd;border-left:4px solid #a8572a;padding:15px 20px;border-radius:0 12px 12px 0}}.num{{font-size:2rem;font-weight:750;color:var(--teal)}}details{{margin:18px 0}}summary{{cursor:pointer;font-weight:700}}code{{overflow-wrap:anywhere;font-size:.85em}}li{{margin:9px 0}}.skip{{position:absolute;left:-200vw}}.skip:focus{{left:12px;top:12px;background:white;padding:12px;z-index:3}}footer{{padding:24px 0;border-top:1px solid var(--line);font-size:.9rem}}@media(max-width:760px){{.grid{{grid-template-columns:1fr}}header{{padding:40px 24px}}body{{font-size:16px}}h2{{font-size:1.6rem}}}}@media print{{body{{background:white}}header{{background:white;color:var(--ink);padding:15px}}header p{{color:var(--ink)}}nav{{display:none}}figure,.card{{break-inside:avoid}}}}
</style></head><body><a class="skip" href="#objetivo">Saltar al contenido</a>
<header><div class="eyebrow">Goliat · evaluación científica · 15 noviembre 2026</div><h1>Comprender cómo observa cada satélite.</h1><p class="lead">El siguiente avance no exige otra fórmula ganadora: exige separar diferencias de definición, representación y oportunidad de observar.</p><p>Evidencia hasta 40: consejos multifocales y adversarios, comparaciones revisadas y resultados negativos conservados. M1 y las 14 comunas habilitadas permanecen sin cambios.</p></header>
<nav aria-label="Secciones"><a href="#objetivo">Objetivo</a><a href="#evidencia">Evidencia</a><a href="#consejos">Consejos</a><a href="#resultados24">Resultados 24C/E</a><a href="#plan">Plan</a><a href="#decisiones">Decisiones</a><a href="#daily36">36 · Calendario diario</a><a href="#context37">37 · Resultado negativo</a><a href="#council38">38 · Decisión conjunta</a><a href="#cdf39">39 · CDF y CRPS</a><a href="#goes40">40 · Preflight documental</a><a href="#cierre">Decisión final</a><a href="#trazabilidad">Fuentes</a></nav><main>
<section id="objetivo"><h2>Una historia comparable de actividad registrada.</h2><p class="note"><strong>Estado del snapshot:</strong> operador nominal y etiquetas verificados; presupuestos separados y contexto diario no superaron sus criterios. F21 obtuvo menor CRPS que δB, con costes visibles. El operador continuo conserva su fallo y G1 físico sigue pendiente.</p><p>La propuesta es construir un calendario MODIS–VIIRS donde un cambio de sensor no parezca automáticamente un cambio del fuego. El indicador actual cuenta celdas–día por plataforma y las agrega por comuna y mes. No cuenta incendios individuales, hectáreas quemadas ni ocurrencias físicas completas.</p><figure>{operator}<figcaption>El registro depende del instrumento y de sus condiciones. Ninguna fórmula de cantidades recupera por sí sola todas las oportunidades perdidas.</figcaption></figure>
<div class="grid"><div class="card"><h3>La pregunta original</h3><p>¿Cuánto desacuerdo persiste cuando ambos instrumentos tuvieron una oportunidad comparable de observar?</p></div><div class="card"><h3>La entrega defendible hoy</h3><p>Conservar M1/14 publicado y explicar candidatos de investigación por separado. El soporte nominal es auditable; la oportunidad física todavía no está identificada.</p></div><div class="card"><h3>El objetivo de producto</h3><p>Que un gestor distinga actividad habitual o excepcional y comprenda cuándo la evidencia es insuficiente para interpretarla.</p></div></div>
<details><summary>Cómo se relacionan las cinco hipótesis</summary><ol><li><strong>Observabilidad:</strong> prioridad central; puntos FIRMS solos no identifican nubes, humo y todas las oportunidades útiles.</li><li><strong>Comparación equivalente:</strong> el ledger nominal prepara soporte y exclusiones antes de comparar estados.</li><li><strong>Probabilidad y cantidad:</strong> ya se ensayó una distribución hurdle; su decisión puede mejorar MAE local y empeorar totales o subgrupos.</li><li><strong>Compartir por contexto:</strong> se ensayó una política fija de composición territorial; su primaria falló y se conserva.</li><li><strong>Evidencia nueva:</strong> un tercer instrumento queda pendiente de una pregunta localizada que pueda resolver; no es automáticamente verdad terreno.</li></ol></details></section>
<section id="evidencia"><h2>Lo aprendido obliga a cambiar de pregunta.</h2><p>La iteración 18 mejoró la asignación local manteniendo el total de B por construcción. Esa igualdad regional no constituye habilidad adicional.</p>{allocation_table18}<p>Entre los extremos M1 y E_coherent, la reducción compuesta es <strong>{number(endpoint18,4)} %</strong>, calculada sobre las mismas pérdidas congeladas del mismo panel. No es la suma de 7,04 % y 5,53 %, no se combina con CRPS y no implica dominio de todos los guardrails. Después, el transporte regional mostró una mejora concentrada en un régimen, no una solución uniforme.</p>{cold_table}<p class="note">18 aprende su máscara dentro de cada origen; no usa 223 celdas fijas en su panel anidado. 21 usa una máscara distinta de 6 celdas, sólo con MODIS anterior a 2012. Sus MAE no deben compararse como si fueran el mismo experimento. Los cuatro regímenes dependen entre sí y las fechas pertenecen a desarrollo ya consultado.</p>
<h3>23 · El contexto comunal probado no supera su control</h3>{context_table}<div class="grid"><div class="card"><h3>Control uniforme</h3><div class="num">{number(primary['equal_four_regime_MAE_C00'],6)}</div><p>MAE medio con igual peso de cuatro regímenes.</p></div><div class="card"><h3>Contexto territorial</h3><div class="num">{number(primary['equal_four_regime_MAE_C11'],6)}</div><p>El error aumenta {number(-100*primary['relative_gain_from_equal_MAE'],4)} %.</p></div><div class="card"><h3>Resultado que se conserva</h3><p>Mejora uno de cuatro regímenes. El promedio por fila cambia de signo, pero no sustituye la primaria fijada.</p></div></div>
<p>Las sensibilidades 2001 y type0 no autorizan elegir retrospectivamente otra configuración. El contexto MCD12Q1 nominal 2001/2010 se reprocesó en 2022: permite este estudio retrospectivo, sin demostrar disponibilidad antes de 2012 ni mecanismo ecológico.</p>
<h3>La observación avanzó, con alcance selectivo</h3><p>La geometría nominal MODIS pasó sus controles dimensionales en los dos casos fijos, 2019 y 2023. VIIRS pasó un contraste con 13 referencias, todas de un solo escaneo 2023 y una región de agregación. Eso no valida todas las dimensiones VIIRS ni la PSF física.</p><p>La cercanía de centros y las referencias temporales de escaneo no equivalen a exposición por píxel. El flag global <code>Suspect</code> sigue sin semántica L2 resuelta; no lo interpretamos como defecto NASA demostrado. <strong>G1 físico permanece falso.</strong></p></section>
<section id="consejos"><h2>Primero acordar cómo decidir; después votar.</h2><figure>{process}<figcaption>El consejo adversario revisó los resultados del multifocal. La propuesta final volvió a ambos consejos para ratificación explícita.</figcaption></figure>{criteria}<p>Antes de sumar notas se aplicaron límites no compensables: desconocido no es cero; no inventar verdad física o causalidad; no rescatar una primaria fallida con un secundario favorable; no cambiar producción. Una aproximación nominal declarada puede estudiarse sin exigir una PSF exacta, conservando sus límites.</p>{ranking}
<p class="note">Las notas son juicios sobre propuestas y primeros entregables. Sus rangos no son intervalos de confianza, y los miembros no aportan réplicas estadísticas independientes. Hubo acuerdo en la secuencia práctica, no unanimidad en las posiciones B/E/A.</p>
<details><summary>Qué vio el adversario que el primer consejo debía corregir</summary><ul><li><strong>Elegir contrato por significado:</strong> nunca por cuál favorece al modelo.</li><li><strong>Acotar la estabilidad:</strong> dos contratos estables no descartan problemas de observabilidad ni explican el plateau contextual.</li><li><strong>Conservar positivos excluidos:</strong> elegir propietario geométrico puede dejar fuera parte de un píxel positivo; el ledger debe mostrarla.</li><li><strong>No localizar fuego subpíxel:</strong> una etiqueta heredada por un átomo describe el operador nominal.</li><li><strong>Mantener filas equivalentes:</strong> el estrato extremo pareado usa Y_C≥50; Y_O≥50 se presenta aparte.</li><li><strong>Contabilizar coste de oportunidad:</strong> C tiene un cap que incluye revisión y no bloquea B.</li></ul></details></section>
<section id="resultados24"><h2>24C/E: cerrar dos preguntas y mantener sus límites.</h2><p>La auditoría contractual ya terminó y recibió revisión independiente. Reprodujo 108 CSV, las seis funciones congeladas y 128 reconciliaciones sobre las mismas 3.456 filas, sin nuevos ajustes. La ventaja global conserva signo: el cambio de Δ es {number(material['change'],6)}, menor que τ={number(material['tau'],6)}. Esa estabilidad acotada no se extiende automáticamente a los territorios.</p>{contract_table}<p class="note">En las 14 comunas publicadas la ventaja casi desaparece y los 21 meses extremos siguen empeorando frente a B. El resultado global no permite promover el candidato. No se infiere que el contrato haya causado físicamente las diferencias.</p><p>El preflight E también terminó: descarta <em>estos productos</em> como denominador comparable de pasadas despejadas. Dos historias [tierra sin detección, tierra sin detección] y [nube, tierra sin detección] pueden producir el mismo compuesto diario; el historial no queda identificado. VNP14A1 usa bandas de 750 m y la dirección del bit QA 2 discrepa entre documentos. Se conserva desconocida, sin implementar un decoder supuesto.</p><p>Este cierre no afirma inexistencia global de otro producto 375 m ni inutilidad de un calendario de clases compuestas. Hubo {D['daily']['science_data_downloaded_bytes']} bytes de datos científicos descargados para E. En ese momento, B continuó con su ledger sin tabular estados; sus fallos y la ruta discreta posterior se presentan a continuación.</p></section>
<section><h2>24B: la revisión detuvo una comparación inválida.</h2><p>El ledger conservó todos los positivos originales y mostró una pérdida de representación: dos de seis positivos Aqua dentro de la AOI 2023 están en bordes sin polígono CORE. Sus áreas son desconocidas, no cero. Una unión nominal casi completa no acredita retención de todas las detecciones.</p>{positive_table}<p>Además, el control independiente encontró que las áreas comunes por píxel no suman la intersección de las uniones. La partición por píxel y el cierre de áreas propias habían pasado, pero eran controles insuficientes.</p>{closure_table}<p class="note"><strong>Las áreas comunes 2023 no están validadas y la concordancia basada en ese operador continuo queda bloqueada.</strong> Los originales se conservan como intento fallido. El diagnóstico aislado reproduce polígonos válidos con predicados de contención verdaderos, intersección de área cero y diferencia de área completa. Se investiga el motor geométrico con WKB sin etiquetas de fuego; ninguna tolerancia, prioridad o precisión se ajusta para rescatar el resultado.</p><p>Los diseños 25 de estados nominales y 26 de soporte en bordes siguen pendientes. Resolver el motor no probaría oportunidad física ni recuperaría automáticamente los bordes.</p></section>
<section><h2>27 y 29: separar versión del motor y representación numérica.</h2><p>El diagnóstico 27 comparó GEOS 3.14.1 con 3.15.0 en procesos aislados: cuatro de cinco regresores fallan controles en ambas versiones, mediante mecanismos distintos. El quinto y los cuatro controles sintéticos pasan en ambas. Actualizar la biblioteca no resolvió estos ejemplos y no se demostró que el issue 1499 fuera la causa.</p><p>El consejo técnico eligió después un único origen: el centro AOI ya fijado. Antes de cualquier overlay centrado, el estudio 29 certificó <strong>{D['exact']['total_coordinate_tuples_with_multiplicity']} tuplas</strong> mediante igualdad racional exacta de las restas y roundtrip de todos los bits, componentes y anillos. No se escogió un desplazamiento por el acuerdo entre sensores ni se leyó fuego o QA.</p>{origin_table}<p class="note">El cambio es 1/5→5/5 pases locales, no cinco errores demostrados reparados. Aqua tardío 833/1149 ya pasaba y su área cambia de ≈3×10⁻⁸ a 2,5 millones de m²: esos gates locales por sí solos no validan el área. La traducción preserva exactamente las entradas, pero los cálculos internos redondean de otra forma.</p><p>El resultado permite una revalidación ampliada de particiones, disjunción, uniones y áreas comunes, con controles independientes. <strong>El ledger completo y G1 siguen sin validar.</strong> Los cinco ejemplos son regresores seleccionados, no una muestra probabilística. Los resultados negativos 24B/27 se conservan y no se promueve el modelo mensual.</p></section>
<section><h2>30A: una prueba independiente refuta las áreas casi nulas.</h2><figure>{witness_figure}<figcaption>Esquema conceptual, sin escala. Q es un testigo geométrico; no representa fuego, un footprint físico ni una superficie quemada.</figcaption></figure><p>Un segundo método, sin GEOS, usa aritmética racional exacta para certificar un cuadrado contenido estrictamente en ambos operandos. Verifica pertenencia y distancia a todas las fronteras, incluidos agujeros. En los {witness_count} pares encontró un cuadrado de 4 m²; por tanto la intersección de cada par tiene al menos esa área.</p><p>La comparación refuta las {witness_refutations} áreas originales guardadas —los dos órdenes de los cinco pares—, incluido el caso que pasaba los gates anteriores. Las áreas centradas superan la cota: quedan <strong>no refutadas por este testigo, no validadas</strong>. Otro verificador reconstruyó los certificados desde los WKB, sin importar el helper del autor.</p><p>El cuadrado es una cota inferior deliberadamente pequeña, no una estimación del área completa. No encontrarlo habría dejado la búsqueda inconclusa. El estudio 30B se registró por separado para revalidar toda la geometría, con cierres globales y dos expresiones computacionales obligatorias. Su resultado negativo se explica a continuación.</p></section>
<section><h2>30B y 32B: un fallo global y una magnitud local distinta.</h2><p>La revalidación completa 30B terminó negativa y parcial: los dos cruces de 2019 completaron sus controles, pero Aqua 2023 falló por <code>{esc(D['full_failure']['error'])}</code>. No se ejecutó replay QA y no se eligió otro origen, precisión o tolerancia para hacer pasar ese intento.</p><p>El diagnóstico 32B adjudicó exactamente el último par registrado, con dos algoritmos racionales independientes. Su intersección es positiva: aproximadamente <strong>1,82×10⁻¹⁰ m²</strong>. Eso refuta el overlay cero para ese par y cuantifica una discrepancia local minúscula; no prueba que ese registro sea la única causa del fallo ni acota los demás errores.</p><p class="note">Este par es distinto de los cinco regresores anteriores con áreas faltantes de kilómetros cuadrados. Una cota local pequeña no permite llamar despreciable el error global ni convertir retrospectivamente 30B en aprobado.</p></section>
<section><h2>31–32A: cambiar la pregunta sin ocultar el fallo.</h2><p>Los dos consejos volvieron a deliberar con los mismos criterios. Ingeniería prefería adjudicar primero el par local; estadística y el agente loco preferían muestreo puntual. Los seis ratificaron una ejecución paralela acotada, conservando ese desacuerdo. El nuevo estimando no intenta reparar áreas continuas.</p><p>32A fija puntos de consulta a 250 m y una grilla de 500 m realmente anidada, con la misma ancla. Usa fase principal (0,0) y sensibilidad diagonal (125,125) m, ambas declaradas antes de etiquetas. La pertenencia a quads nominales y la propiedad por escaneo se calculan con enteros exactos, sin GEOS para predicados o candidaturas.</p><div class="grid"><div class="card"><h3>Consultas prefijadas</h3><div class="num">{D['points']['queries_total']:,}</div><p>En ocho poblaciones de caso, fase y paso; no se multiplican como réplicas por sensor o prioridad.</p></div><div class="card"><h3>Candidatos verificados</h3><div class="num">{D['points']['candidate_tests_total']:,}</div><p>Todos los candidatos punto–quad se reconstruyeron por un índice independiente.</p></div><div class="card"><h3>Pase exclusivamente GEO</h3><p>Propietarios y causas, simplicidad de los 101.038 quads y anidamiento fueron comprobados independientemente. Sin etiquetas ni QA.</p></div></div><p>El verificador usó búsqueda por grillas y winding number distintos de los del autor. Conservó puntos sin soporte nominal y los estados de frontera, tiempo desconocido y conflicto dentro del mismo escaneo; que no aparezcan algunos en estos datos no elimina sus reglas.</p><p class="note">La etiqueta posterior corresponde al píxel nominal asignado al punto, <strong>no actividad física localizada en ese punto</strong>. Miles de consultas siguen siendo dos casos con píxeles compartidos. Sus frecuencias no son superficies ni incendios, y el pase no habilita automáticamente incorporar QA. El contraste 33 usó un protocolo propio, una cohorte fija y retención nativa visible, como se detalla más adelante.</p></section>
<section id="plan"><h2>El plan 24 y sus entregas acotadas.</h2><figure>{parallel}<figcaption>Inicio acordado de implementación: 04:29:28 UTC. C y el primer ledger B: 05:29:28 UTC; E documental: 04:59:28 UTC. C y E cerraron; B entregó evidencia parcial y quedó bloqueado en la revisión. El horizonte general sigue siendo 11:30 UTC, 08:30 de Santiago.</figcaption></figure>
<h3>C · ¿Cuánto depende el resultado del contrato?</h3><p>Se usan las mismas 3.456 filas disponibles en ambos archivos: 54 comunas y 64 meses. C representa el contrato científico y O el contrato observado del producto. Se reproducen identidades antes de medir pérdidas; no se reajustan modelos ni se agregan fechas faltantes.</p><p>La primaria prefijada fue Δ=MAE(E_coherent)−MAE(B). Los extremos CC/OO aplican sus respectivas entradas y targets; CO/OC son diagnósticos de mezcla de representaciones, no efectos instrumentales. El bridge S-NPP–NOAA20 sigue sin demostrar. Cada entrada requiere su propio presupuesto ΣB sobre 54 comunas antes de filtrar.</p>
<details><summary>Cómo interpretar las cotas y la materialidad</summary><p>Con f y g fijos, el cambio de ganancia MAE al sustituir sólo el target está acotado por 2·media|Y_C−Y_O|. El valor 440/3456 sólo corresponde al panel global conocido; no cubre cambio de entrada, error regional ni todos los subgrupos. Cada población requiere su propia cota.</p><p>Se fija τ=0,01·MAE(B_CC) como regla práctica previa, sin significado NASA ni significación estadística. Hay dependencia material si |ΔOO−ΔCC|≥τ. Toda inversión de signo se registra; se llama material sólo si ambos extremos superan τ en magnitud. Los perjuicios territoriales siguen visibles bajo ese umbral.</p></details>
<h3>B · ¿Qué información conserva la representación nominal?</h3><p>Se fijó como primer resultado un ledger: geometría original, unión, propiedad, exclusiones, soporte común y retención de positivos por instrumento. La prioridad de escaneos se fija por geometría antes de mirar QA o actividad. Escaneo temprano es primario y tardío una sensibilidad; no se elige el que maximice acuerdo.</p><p>Se separan borde CORE, falta de soporte, propiedad y calidad. Tierra, agua y desconocidos conservan su identidad. Los positivos 7–9 originales se registran aun si quedan excluidos; M13 no nominal no los convierte silenciosamente en cero. En esa etapa todavía no se autorizaba una matriz de concordancia entre estados.</p>
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
<section><h2>33: comparar etiquetas sin convertir desconocidos en ceros.</h2><figure>{point_figure33}<figcaption>Diagrama conceptual de la asignación; no representa una escena, escala espacial ni superficie física.</figcaption></figure><p>El protocolo se congeló antes de leer etiquetas. Se enriquecieron por identidad nativa las consultas de 32A, conservando todos sus propietarios y causas. Un verificador independiente reconstruyó las 898.704 filas de consultas, fuentes proyectadas, rosters y retención, con sus propias reglas de QA, sin importar el helper del autor. Los 16 escenarios y las comparaciones anidadas pasaron.</p>{point_table33}<p>En 2023, los 4 positivos Aqua CORE representados asignan su etiqueta a 162 consultas; los 16 VIIRS, a 45. Esto no contradice sus recuentos nativos: cambia la unidad y cada quad puede aportar varios puntos. Los otros 2 positivos Aqua del área permanecen con geometría desconocida. Ninguno se convierte en ausencia de detección.</p><p>La retención cambia con la grilla: VIIRS representa los 16 positivos del área a 250 m en ambas fases, pero sólo 12 y 10 a 500 m. En 2019, cuatro positivos VIIRS del halo siguen en el catálogo aunque no aportan consultas interiores. No se eligió una configuración posterior para maximizar concordancia o retención.</p><p>Los Jaccard secundarios de 2023 varían aproximadamente entre 11,9 % y 15 %. El tier nominal en campos inspeccionados da 11/152, aproximadamente 7,24 %: filtrar calidad no produjo automáticamente más concordancia y cambia la población. Los positivos M13 no nominal permanecen positivos en el resultado principal.</p><p class="note">Este contraste no cuantifica qué parte del desacuerdo desaparece con oportunidades físicas comparables: todavía mezcla etiquetas algorítmicas, soporte nominal, horarios y evolución real. No valida el operador continuo 30B, no resuelve G1 o Suspect global y no modifica el modelo mensual publicado.</p></section>
<section><h2>35: volver al modelo y cerrar una hipótesis negativa.</h2><p>El siguiente consejo conservó los criterios y verificó las ponderaciones. Estadística e ingeniería favorecían un contraste acotado de presupuestos; observación prefería persistencia diaria como información nueva. Los seis ratificaron probar primero A y la mezcla fija C, manteniendo el disenso. No hubo ganador robusto en los rangos subjetivos ni un consejo ciego: ingeniería había visto el voto estadístico.</p><figure>{group_figure35}<figcaption>Diagrama del experimento computacional; no describe un mecanismo ecológico ni cambia las observaciones satelitales.</figcaption></figure><p>Se reconstruyeron exactamente B y la asignación global G del estudio 21 en sus cuatro regímenes, antes de leer respuestas para evaluar. Después se congelaron R, una partición artificial única y C=(B+G)/2. En este panel, regiones y roles de calibración coinciden: la pregunta es sobre acoplamiento asignativo SOURCE–held, no un efecto geográfico.</p>{group_table35}<p>La primaria predeclarada, promedio igual de los cuatro ΔMAE, es <strong>{number(D['groups35']['primary']['equal_four_delta_mae'],6)}</strong>: separar presupuestos empeora el error held y sólo mejora uno de cuatro regímenes. El agregado por filas conserva signo. Una mejora de all54 o de un subgrupo no sustituye esa primaria, y no se probaron otra partición o proporción para rescatarla.</p><p>El revisor reconstruyó las distribuciones, las predicciones originales y todos los reportes. Detectamos una omisión de diagnósticos B/C en la salida original; se completaron en evidencia independiente, sin optimizar otra vez ni modificar predicciones, primaria o manifiesto del autor. El riesgo CDF respeta sus cotas y los KKT se verifican por grupo, con multiplicadores propios.</p><p class="note">Resultado negativo útil: bloquear transferencias no mejoró esta evaluación. La igualdad de presupuestos regionales sigue siendo construida, no habilidad nueva. La persistencia diaria se abrió después mediante decisiones y protocolos propios, como se muestra a continuación; no fue una continuación automática ni transformó los dos casos nominales en verdad física. M1, producción, G1 y el fallo continuo 30B permanecen sin cambios.</p></section>

<section id="daily36"><h2>36: una variable temporal con un placebo que conserva los registros.</h2><p>Una decisión posterior abrió un cubo diario Aqua, sin respuestas SNP ni ajustes. D vale 1 cuando la <strong>misma celda</strong> tiene registros en dos días UTC consecutivos <strong>dentro del mismo mes calendario</strong>. Varias detecciones de un día no son días consecutivos; una pareja que cruza de mes tampoco cuenta.</p><figure>{calendar_figure36}<figcaption>Ejemplo conceptual de cuatro columnas, no un gráfico de datos ni el resultado de un hash. En 36 se permutan los 28–31 días completos del mes: el conjunto de celdas del día original 2 se mueve junto al destino 1; las columnas vacías también se reubican.</figcaption></figure><p>El orden real se obtiene ordenando los días por SHA256 de <code>goliat-daily-adjacency-v1|CUT|YYYYMM|DD</code>, con desempate por día. La dirección literal es <strong>día ORIGEN d → día DESTINO rankedDays[d−1]</strong>, compartida por todas las celdas y por las copias de un mismo mes en distintos regímenes. No se permuta cada celda por separado ni sólo los días positivos.</p>{adjacency_table36}<p>El verificador independiente comprobó {adj36_verified['all_source_event_rows']:,} incidencias y {adj36_verified['fullcalendar_mapping_rows']:,} mappings, incluidos días vacíos y bisiestos 2016/2020. Conservó conteos por celda y el multiconjunto completo de conjuntos de celdas diarios, no sólo sus cantidades. La máscara es la de 6 celdas de 21 y el período UTC va de julio de 2012 a junio de 2020.</p><p class="note">D real aparece en {adj36['D_real_1']} meses y D placebo en {adj36['D_placebo_1']}; difieren en {adj36['D_discordant']}. Estas cifras describen el predictor, no su eficacia. La permutación puede conservar o crear adyacencias y no se cambió para forzar un resultado. Cero registros no acredita oportunidad útil ni adquisición raw completa; una pareja tampoco demuestra continuidad del mismo incendio.</p></section>
<section id="context37"><h2>37: el modelo diario ensayado no supera la condición conjunta prefijada.</h2><p>El modelo requirió otra autorización y protocolo: el cubo auditado no abrió automáticamente los fits. Se usaron CDF completas condicionadas por D, con shrinkage parent y local κ=10, mismos ratios y baseline B de 21. Sólo SOURCE×años de origen entra al ajuste de cada régimen; una etiqueta puede ser origen para un régimen y held para otro, sin fingir exclusión global de todas las respuestas held.</p><p>Si D no varía en un pool SOURCE, se devuelve la CDF original completa para todo CUT, incluido su componente local y consultas D no vistas. No se vuelve a suavizar la probabilidad Jeffreys como si fuera información temporal. Los átomos RAWZ se mezclan antes de escalar y aplicar el floor positivo original.</p>{context_table37}<div class="grid"><div class="card"><h3>Real frente a placebo</h3><div class="num">{number(primary37['equal_four_real_minus_placebo'],10)}</div><p>ΔMAE held, igual peso de cuatro regímenes.</p></div><div class="card"><h3>Real frente a G21</h3><div class="num">{number(primary37['equal_four_real_minus_G'],10)}</div><p>El promedio empeora frente al control existente.</p></div><div class="card"><h3>Condición conjunta</h3><p><strong>No se cumple.</strong> Ambos contrastes debían ser negativos; un promedio favorable frente al placebo no compensa el otro.</p></div></div>{context_cost_table37}<p>En held de las 14 publicadas, real empeora frente al placebo en los cuatro regímenes. Los pools activos y las vueltas al fallback difieren entre real y placebo: el contraste no identifica un efecto puro del orden temporal ni demuestra que toda información diaria sea inútil. Sí cierra esta formulación, sin retocar κ, semilla, pools o rasgo.</p><p class="note">Los modelos y las 10.368 predicciones se congelaron antes de evaluar. La revisión independiente reconstruyó {D['context37_review']['complete_candidate_reconstructions']} modelos y {D['context37_review']['candidate_CDF_query_checks']:,} CDF candidatas, además de los controles constantes y todos los reportes. El resultado negativo permanece aunque una métrica posterior de otra pregunta resulte favorable.</p></section>
<section id="council38"><h2>38: los dos consejos eligen una pregunta distinta y protegen el cierre.</h2><p>Tras el negativo de 37, estadística, observación y el agente loco evaluaron las rutas con los mismos pesos: 30 % validez, 25 % información discriminante, 20 % factibilidad/reproducción/coste, 15 % transporte/selección y 10 % interpretación. Identificación, medición y factibilidad actuaron como consejo adversario. Los criterios se acordaron antes de puntuar; la aritmética de los votos se verificó.</p>{council_table38}<p>Los rangos se solapan: no hay un ganador numérico robusto ni representan probabilidades o intervalos de confianza. Los seis ratificaron la secuencia <strong>A + D</strong>, aunque conservaron prioridades distintas. A compara una CDF ya congelada con δB bajo una pérdida propia de distribuciones; D consolida resultados y límites. No se convierte un fallo de MAE en éxito cambiando después su criterio. B no es ejecutable mientras falten la acción y sus costes.</p><p>C se difirió inicialmente por capacidad de revisión. A terminó con revisión completa a las {esc(D['crps39_review']['completed_utc'])}; los seis ratificaron entonces una ampliación documental C, con cap 09:15–10:00 UTC y cero bytes científicos. La decisión aprovechó capacidad y tiempo liberados; no dependió del signo favorable de CRPS. Conservó D de 10:13 a 11:13 UTC y la contingencia hasta las 11:30 UTC.</p><p>El <a href="../reviews/2026-11-15-joint-plan-38.md">plan conjunto 38</a>, los votos y la ampliación se conservan con hashes. Ratificar una secuencia no prueba que todos prefirieran el mismo orden ni convierte a los agentes en réplicas estadísticas independientes.</p></section>
<section id="cdf39"><h2>39: una distribución marginal responde otra pregunta que una asignación puntual.</h2><p>Se restauró la distribución marginal F21 original, sin volver a ajustar modelos, frente al forecast degenerado δB que concentra toda su masa en B. Su CRPS coincide exactamente con |B−Y|. La pregunta es si F21 describe mejor la <strong>actividad SNP registrada de ese mismo mes histórico, dado Aqua mensual</strong>; no se pronostica un mes futuro ni una ignición.</p><p>CRPS es una pérdida no negativa: combina distancia al registro y dispersión del forecast, y menor es mejor. Los dos forecasts difieren también en localización; por eso una ventaja no aísla el valor de la incertidumbre o de Aqua. Los átomos conservan la escala de la consulta, ceros, empates y floor positivo; no se redondean a conteos enteros ni se aplica corrección de ensemble.</p>{crps_table39}<p>La primaria igual peso de cuatro held es <strong>{number(primary39['equal_four_difference'],10)}</strong>, favorable en cuatro de cuatro promedios. El agregado por filas es secundario y no la sustituye. Las CDF, B, medianas, medias y rosters quedaron congelados antes del join real de respuestas; el entorno del productor se guardó en su freeze.</p>{crps_cost_table39}<p>Los dos regímenes SOURCE16 aprenden en Ñuble y evalúan held de Biobío. Sus extremos Y≥50 empeoran, y held/publicadas de 16_forward también tiene coste. Los ceros y todas las tablas SOURCE/held, 14/40 y CUT permanecen visibles. En ambos registros cero el coste es adverso en los cuatro regímenes: el baseline held B=0 acierta esa respuesta condicionada y δB tiene pérdida 0; esto no demuestra por sí solo mala calibración.</p><p>El revisor usó una integral independiente de la diferencia cuadrática entre CDF e indicador, en lugar de la fórmula de prefijos del productor. Reconstruyó {D['crps39_review']['all_frozen_CDFs_reconstructed']:,} CDF y {D['crps39_review']['atom_elements']:,} elementos de soporte; la máxima diferencia entre algoritmos fue {D['crps39_review']['max_abs_integral_vs_producer_raw_CRPS']:.2e}. Hubo cero fits, solvers y adquisiciones científicas. E11 y su parent son idénticos en held: se comprueba esa identidad, sin inventar otro brazo.</p><p class="note"><strong>Menor CRPS frente a δB, con estos costes, permite mantener una rama de investigación probabilística.</strong> No demuestra calibración, sensibilidad física, generalización fresca, valor aislado de dispersión ni una distribución conjunta de 54 comunas. No rescata 37, 35 o 23. G es una decisión puntual obtenida al reconciliar: F21 no es una CDF alrededor de G y sus bandas crudas no se pueden pegar a G como intervalos reconciliados.</p><p>Los cuatro regímenes se solapan y las fechas ya se consultaron durante el desarrollo. Un oráculo independiente y un protocolo previo acreditan la comparación reproducida; no crean un holdout nuevo ni resuelven PSF, exposición por píxel, oportunidades físicas o Suspect global.</p></section>
<section id="goes40"><h2>40: catálogo disponible, interpretación histórica todavía condicionada.</h2><p>Tras terminar 39 temprano y liberarse revisión, se autorizó un preflight documental separado, conservando el disenso sobre prioridades y el tiempo de cierre. Se consultaron sólo documentación técnica y dos listados de catálogo GOES16 ABI-L2-FDCF para las fechas y AOI ya fijadas; no se eligió una imagen positiva o una fecha favorable.</p>{goes_table40}<p>La revisión independiente confirmó {D['goes40_review']['catalog_objects_independently_verified']} objetos listados en dos catálogos y <strong>{D['goes40']['science_bytes_acquired']} bytes científicos adquiridos</strong>. No se hicieron GET, HEAD o Range de NetCDF, radiancias, máscaras o imágenes; los tamaños listados son metadatos, no contenido verificado. La separación de inicios 15/10 min y las ventanas de scan no proporcionan el tiempo de exposición del AOI o píxel.</p><p>Los esquemas documentados de Mask/DQF y la proyección nominal no identifican las versiones y atributos de esos archivos históricos. DQF=0 no es una regla universal de observación útil. El ReadMe de diciembre de 2019 describe filtrado temporal en el mismo píxel hasta 12 horas y dice diferir del vecindario ±1 píxel del ATBD; la regla realmente desplegada en cada fecha sigue desconocida.</p><p class="note">Conclusión documental condicionada: podría justificar diseñar contexto temporal grueso, no adjudicar discrepancias a 375 m o de minutos. No demuestra ausencia fina a partir de una no detección gruesa, ni verdad física a partir de una detección. La máquina histórica de estados sigue inconclusa; no se autoriza una adquisición ni se reabre el presupuesto L2. G1 permanece falso.</p><p>El <a href="../reviews/2026-11-15-goes-preflight-report.md">reporte 40</a> y su <a href="../reviews/2026-11-15-goes-preflight-independent-review.md">revisión independiente</a> conservan semánticas, versiones y límites de acceso. El pase es de ese alcance documental, no de un decoder de caso o de oportunidades físicas.</p></section>
<section id="cierre"><h2>La decisión final conserva producto, candidatos y límites por separado.</h2><p><strong>Publicado:</strong> M1 con factor 2,352954072125397 y las mismas 14 comunas habilitadas de 54. <strong>Investigación puntual:</strong> E_coherent mejoró la asignación retrospectiva bajo presupuesto de B; no domina territorios, ceros y transportes. <strong>Investigación probabilística:</strong> F21 tiene menor CRPS que δB en la comparación fijada; no tiene calibración o coherencia conjunta demostradas.</p><p>La siguiente decisión necesita evidencia sobre oportunidad de observación o casos independientes compatibles con el operador. Otra feature, semilla, κ o agregación sobre los mismos destinos no produce esa evidencia. La historia observada por plataforma y la serie armonizada conservan contratos distintos; el puente local SNP–NOAA20 y el archivo observado 2026 no se dan por resueltos.</p><p>Los 1.071 CSV raw faltantes son un límite documentado por la auditoría previa, no un recuento nuevo. Los derivados, parámetros y resultados congelados permiten verificaciones; no reconstruyen por sí solos toda la adquisición. Los drivers históricos conservan caps y rutas: una nueva reproducción necesita orquestación declarada, sin fingir un reloj pasado ni sobrescribir evidencia.</p><p>La <a href="../reviews/2026-11-15-final-scientific-decision.md">decisión científica completa</a>, con su <a href="../reviews/2026-11-15-final-scientific-decision-addendum.md">addendum documental 40</a>, explica qué mejora del manifiesto inicial, qué se cierra y qué permanece desconocido. Ningún resultado de este informe modifica M1, gates, bandas o publicación, ni constituye un despliegue.</p></section>

<section id="trazabilidad"><h2>Evidencia verificable y alcance del documento.</h2><p>Este snapshot explica evidencia hasta 40 y la consolidación final, incluidos los fallos 24B/30B, 27 negativo, 35 y el criterio conjunto fallido de 37. Un menor CRPS de F21 frente a δB no rehabilita esas primarias. Incluye comparación descriptiva de etiquetas del operador discreto; no valida el operador continuo ni la verdad física. Se genera leyendo resúmenes congelados, sin abrir crudos, credenciales, ajustar modelos ni recalcular predicciones.</p><p><a href="science-session-2026-11-14.html">Informe anterior: iteraciones 16–20A y casos L2</a>. Revisión incremental: <a href="https://github.com/Loddrik/goliat-fire-calendar/pull/46">PR46</a>, <a href="https://github.com/Loddrik/goliat-fire-calendar/pull/49">PR49</a>, <a href="https://github.com/Loddrik/goliat-fire-calendar/pull/50">PR50</a>, <a href="https://github.com/Loddrik/goliat-fire-calendar/pull/51">PR51</a>, <a href="https://github.com/Loddrik/goliat-fire-calendar/pull/53">PR53</a> y <a href="https://github.com/Loddrik/goliat-fire-calendar/pull/54">PR54</a>. También <a href="https://github.com/Loddrik/goliat-fire-calendar/pull/57">PR57</a>, <a href="https://github.com/Loddrik/goliat-fire-calendar/pull/58">PR58</a>, <a href="https://github.com/Loddrik/goliat-fire-calendar/pull/59">PR59</a> , <a href="https://github.com/Loddrik/goliat-fire-calendar/pull/60">PR60</a> y <a href="https://github.com/Loddrik/goliat-fire-calendar/pull/61">PR61</a>. Los enlaces no certifican estados de aprobación, merge o despliegue posteriores.</p>
<details><summary>Fuentes locales y hashes del snapshot</summary><ul>{sources}</ul><p>Plan conjunto SHA256 <code>{D['agreement']['plan_sha256']}</code>. Ratificación UTC: {esc(D['agreement']['ratified_at_utc'])}.</p></details>
<details><summary>Documentación primaria para el preflight diario</summary><ul><li><a href="https://www.earthdata.nasa.gov/s3fs-public/imported/MODIS_C6_Fire_User_Guide_B.pdf">NASA: guía MODIS C6, §5.2</a>.</li><li><a href="https://lpdaac.usgs.gov/documents/427/VNP14_User_Guide_V1.pdf">Guía VIIRS VNP14: composición de bandas de 750 m</a>.</li><li><a href="https://firms.modaps.eosdis.nasa.gov/alerts/notes.php">NASA FIRMS: notas de interpretación</a>.</li></ul></details>
<footer>Corte de evidencia {esc(snapshot_utc)}. La revisión 39 terminó {esc(D['crps39_review']['completed_utc'])}; el preflight 40, sólo documental, fue revisado {esc(D['goes40_review']['completed_utc'])}. HTML autónomo con diagramas SVG propios, tablas y detalles accesibles. Sin Mermaid, JavaScript ni recursos gráficos remotos. No cambia la publicación M1/14 ni certifica uso operacional.</footer></section></main></body></html>'''
DEST.parent.mkdir(parents=True, exist_ok=True)
DEST.write_text('\n'.join(line.rstrip() for line in page.splitlines()) + '\n')
print(DEST, DEST.stat().st_size, 'bytes')
