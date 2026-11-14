"""Inventario congelado de los archivos de entrada: ruta, bytes, sha256, filas, rango de fechas.
Salida: data/processed/inventory.csv. Se corre una vez antes de ajustar nada."""
import csv, hashlib, pathlib, sys
import duckdb

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
OUT = ROOT / "data/processed/inventory.csv"

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

rows = []
con = duckdb.connect()
for p in sorted(RAW.rglob("*.csv")):
    try:
        n, dmin, dmax = con.execute(
            f"select count(*), min(acq_date), max(acq_date) from read_csv_auto('{p}', header=true, all_varchar=true)"
        ).fetchone()
    except Exception as e:
        n, dmin, dmax = -1, None, str(e)[:60]
    rows.append(dict(path=str(p.relative_to(ROOT)), bytes=p.stat().st_size, sha256=sha(p), rows=n, acq_min=dmin, acq_max=dmax))
    print(rows[-1]["path"], n, dmin, dmax)
OUT.parent.mkdir(exist_ok=True)
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(len(rows), "archivos →", OUT)
