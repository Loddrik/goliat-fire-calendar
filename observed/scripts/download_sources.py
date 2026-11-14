"""Fuentes oficiales de la etapa 2. Descargas acotadas, originales y hashes.

python3 scripts/download_sources.py [--history-only | --boundaries-only]
"""
import argparse
import csv
import hashlib
import io
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CATALOG = "https://firms.modaps.eosdis.nasa.gov/data/country/yearly_summary_files.txt"
DPA = "https://geoportal.cl/geoportal/catalog/download/912598ad-ac92-35f6-8045-098f214bd9c2"
DPA_METADATA = "https://geoportal.cl/geoportal/catalog/36391/division-politica-administrativa-2023"


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def download(url, target, max_bytes, expected_size=None):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and (expected_size is None or target.stat().st_size == expected_size):
        return {"bytes": target.stat().st_size, "sha256": digest(target), "cached": True}
    temporary = target.with_suffix(target.suffix + ".part")
    request = Request(url, headers={"User-Agent": "FireChronos/0.2 official-data-inventory"})
    total = 0
    hasher = hashlib.sha256()
    with urlopen(request, timeout=60) as response, temporary.open("wb") as output:
        length = response.headers.get("Content-Length")
        if length and int(length) > max_bytes:
            raise ValueError("Archivo supera el límite de descarga")
        while block := response.read(1024 * 1024):
            total += len(block)
            if total > max_bytes:
                raise ValueError("Descarga supera el límite")
            output.write(block)
            hasher.update(block)
    if expected_size is not None and total != expected_size:
        raise ValueError(f"Tamaño inesperado: {total}; catálogo: {expected_size}")
    temporary.replace(target)
    return {"bytes": total, "sha256": hasher.hexdigest(), "cached": False}


def fetch_history():
    raw = ROOT / "data/raw/history"
    raw.mkdir(parents=True, exist_ok=True)
    catalog_target = raw / "yearly_summary_files.txt"
    request = Request(CATALOG, headers={"User-Agent": "FireChronos/0.2"})
    with urlopen(request, timeout=30) as response:
        catalog_bytes = response.read(12 * 1024 * 1024 + 1)
    if len(catalog_bytes) > 12 * 1024 * 1024:
        raise ValueError("Catálogo demasiado grande")
    catalog_target.write_bytes(catalog_bytes)
    entries = []
    for row in csv.DictReader(io.StringIO(catalog_bytes.decode("utf-8-sig"))):
        name = row["filename"]
        if not name.endswith("_Chile.csv"):
            continue
        sensor, year_text, _ = name.split("_", 2)
        year = int(year_text)
        if sensor not in ("modis", "viirs-snpp", "viirs-jpss1"):
            continue
        if sensor == "modis" and year < 2002:
            continue
        if year > 2025:
            continue
        entries.append({"filename": name, "sensor": sensor, "year": year,
                        "catalog_size": int(row["size"]), "catalog_updated": row["updated"],
                        "url": f"https://firms.modaps.eosdis.nasa.gov/data/country/{sensor}/{year}/{name}"})
    if not entries:
        raise ValueError("El catálogo no contiene los archivos esperados de Chile")

    def fetch(entry):
        target = raw / entry["filename"]
        result = {**entry, "retrieved_at": now(), "local_path": str(target.relative_to(ROOT))}
        try:
            result.update(download(entry["url"], target, 30 * 1024 * 1024, entry["catalog_size"]))
            with target.open(encoding="utf-8-sig", newline="") as stream:
                fields = next(csv.reader(stream))
            if not {"latitude", "longitude", "acq_date", "satellite", "instrument"}.issubset(fields):
                raise ValueError("Esquema FIRMS inesperado")
            result.update(status="downloaded", columns=fields)
        except Exception as error:
            result.update(status="failed", error=f"{type(error).__name__}: {error}")
        print(json.dumps({key: result.get(key) for key in ("filename", "status", "bytes", "error")}), flush=True)
        return result

    results = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        for task in as_completed([pool.submit(fetch, entry) for entry in entries]):
            results.append(task.result())
    results.sort(key=lambda row: (row["sensor"], row["year"]))
    report = {"schema_version": 1, "generated_at": now(), "catalog_url": CATALOG,
              "catalog_sha256": hashlib.sha256(catalog_bytes).hexdigest(),
              "country": "Chile", "files": results,
              "missing": [row["filename"] for row in results if row["status"] != "downloaded"],
              "notes": ["Archivos anuales por país; no son recuentos de incendios.",
                        "La presencia del archivo no demuestra observación diaria completa.",
                        "No se concatena la muestra NRT con los históricos."]}
    (ROOT / "reports/history-download.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def fetch_boundaries():
    target = ROOT / "data/raw/boundaries/dpa-2023.zip"
    result = {"schema_version": 1, "url": DPA, "metadata_url": DPA_METADATA,
              "provider": "SUBDERE / IDE Chile", "version": "DPA 2023", "retrieved_at": now(),
              "local_path": str(target.relative_to(ROOT))}
    try:
        result.update(download(DPA, target, 400 * 1024 * 1024))
        with target.open("rb") as stream:
            if stream.read(4) != b"PK\x03\x04":
                raise ValueError("La descarga no es ZIP")
        result["status"] = "downloaded"
    except Exception as error:
        result.update(status="failed", error=f"{type(error).__name__}: {error}")
    (ROOT / "reports/boundaries-download.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--history-only", action="store_true")
    group.add_argument("--boundaries-only", action="store_true")
    args = parser.parse_args()
    (ROOT / "reports").mkdir(exist_ok=True)
    if not args.boundaries_only:
        fetch_history()
    if not args.history_only:
        fetch_boundaries()


if __name__ == "__main__":
    main()
