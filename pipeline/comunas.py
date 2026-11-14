"""Polígonos de las 54 comunas de Biobío + Ñuble con CUT.
Fuente: geoBoundaries CHL ADM3 (gbOpen, año 2020, derivado de la BCN) + tabla CUT (DPA oficial SUBDERE/INE; los códigos de Ñuble se corrigieron el 14-11 tras revisión: el paquete npm los traía corridos).
Salida: data/processed/comunas_biobio_nuble.geojson (completo) y web/public/data/comunas.geojson (simplificado)."""
import csv, json, pathlib, unicodedata
from shapely.geometry import shape, mapping

ROOT = pathlib.Path(__file__).resolve().parents[1]
norm = lambda t: ''.join(ch for ch in unicodedata.normalize('NFD', t.lower()) if unicodedata.category(ch) != 'Mn').strip()

rows = list(csv.DictReader(open(ROOT / 'data/raw/dpa/comunas_cut.csv', encoding='utf-8')))
d = json.load(open(ROOT / 'data/raw/dpa/geoBoundaries-CHL-ADM3.geojson'))
byname = {norm(f['properties']['shapeName']): f for f in d['features']}
feats, missing = [], []
for r in rows:
    f = byname.get(norm(r['comuna']))
    if not f: missing.append(r['comuna']); continue
    feats.append((r, shape(f['geometry'])))
assert not missing, missing
def fc(simplify=None):
    return {'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'properties': {'cut': r['cut'], 'comuna': r['comuna'], 'region': r['region']},
         'geometry': mapping(g.simplify(simplify, preserve_topology=True) if simplify else g)} for r, g in feats]}
json.dump(fc(), open(ROOT / 'data/processed/comunas_biobio_nuble.geojson', 'w'), ensure_ascii=False)
json.dump(fc(0.002), open(ROOT / 'web/public/data/comunas.geojson', 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(feats), 'comunas listas')
