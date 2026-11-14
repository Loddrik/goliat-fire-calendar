"""Descarga incremental de FIRMS por la API de área (máx. 5 días por llamada).

Uso: python pipeline/download_firms.py SOURCE DESDE HASTA
  p. ej. python pipeline/download_firms.py VIIRS_NOAA20_NRT 2026-11-08 2026-11-14

Guarda data/raw/firms_api/<SOURCE>/<SOURCE>_<fecha>_<n>d.csv, igual que la
descarga histórica. Requiere FIRMS_MAP_KEY en .env.
"""
import os, sys, time, pathlib, urllib.request
from datetime import date, timedelta

BBOX = "-76,-56,-66,-17"  # Chile continental y algo de los vecinos; se recorta después
ROOT = pathlib.Path(__file__).resolve().parents[1]

def load_key():
    for line in (ROOT / ".env").read_text().splitlines():
        if line.startswith("FIRMS_MAP_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("Falta FIRMS_MAP_KEY en .env")

def main(source, start, end):
    key = load_key()
    out = ROOT / "data/raw/firms_api" / source
    out.mkdir(parents=True, exist_ok=True)
    d = date.fromisoformat(start); last = date.fromisoformat(end)
    while d <= last:
        n = min(5, (last - d).days + 1)
        f = out / f"{source}_{d}_{n}d.csv"
        if f.exists() and f.stat().st_size > 0:
            print("ya está", f.name); d += timedelta(days=n); continue
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/{source}/{BBOX}/{n}/{d}"
        for intento in range(3):
            try:
                body = urllib.request.urlopen(url, timeout=120).read()
                break
            except Exception as e:
                print("reintento", intento + 1, e); time.sleep(5)
        else:
            sys.exit(f"falló {f.name}")
        f.write_bytes(body)
        print(f.name, body.count(b"\n") - 1, "filas")
        d += timedelta(days=n)
        time.sleep(1)

if __name__ == "__main__":
    main(*sys.argv[1:4])
