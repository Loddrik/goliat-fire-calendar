"""Descarga dos instantáneas públicas FIRMS; conserva originales y crea muestra acotada.
Uso: python3 scripts/fetch_sample.py
No requiere API key; no descarga el archivo histórico.
"""
import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    {"id": "modis-24h", "platform": "Terra/Aqua", "instrument": "MODIS", "product": "MODIS C6.1 NRT",
     "url": "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_South_America_24h.csv"},
    {"id": "noaa20-24h", "platform": "NOAA-20", "instrument": "VIIRS", "product": "VIIRS NOAA-20 C2 NRT",
     "url": "https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_South_America_24h.csv"},
]
MAX_BYTES = 24 * 1024 * 1024
MAX_PUBLISHED = 500
BBOX = (-73.9, -38.9, -71.0, -35.8)

def main():
    raw_dir = ROOT / "data/raw"
    public_dir = ROOT / "dist/data"
    raw_dir.mkdir(parents=True, exist_ok=True)
    public_dir.mkdir(parents=True, exist_ok=True)
    retrieved = datetime.now(timezone.utc).isoformat()
    sources = []
    for source in SOURCES:
        item = {**source, "retrieved_at": retrieved, "processing_status": "NRT",
                "status": "unavailable", "sample_scope": "pilot_bbox", "rows": []}
        try:
            request = Request(source["url"], headers={"User-Agent": "FireChronos/0.1 NASA-Space-Apps-data-inventory"})
            with urlopen(request, timeout=30) as response:
                payload = response.read(MAX_BYTES + 1)
                item["http_last_modified"] = response.headers.get("Last-Modified")
            if len(payload) > MAX_BYTES:
                raise ValueError("Respuesta excede el límite de descarga")
            text = payload.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text))
            fields = reader.fieldnames or []
            if not {"latitude", "longitude", "acq_date"}.issubset(fields):
                raise ValueError("Respuesta sin esquema mínimo FIRMS")
            rows = list(reader)
            if any(len(row) != len(fields) or None in row for row in rows):
                raise ValueError("Filas CSV con estructura irregular")
            target = raw_dir / (source["id"] + ".csv")
            target.write_bytes(payload)
            selected, invalid_coordinates = [], 0
            for row in rows:
                try:
                    lat, lon = float(row["latitude"]), float(row["longitude"])
                    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                        raise ValueError("coordinates")
                except (ValueError, TypeError):
                    invalid_coordinates += 1
                    continue
                if BBOX[0] <= lon <= BBOX[2] and BBOX[1] <= lat <= BBOX[3]:
                    selected.append(row)
            dates = sorted({row["acq_date"] for row in rows if row.get("acq_date")})
            item.update(status="downloaded", sha256=hashlib.sha256(payload).hexdigest(),
                        bytes=len(payload), columns=fields, source_rows=len(rows),
                        invalid_coordinates=invalid_coordinates, pilot_rows=len(selected),
                        rows=selected[:MAX_PUBLISHED], published_rows=min(len(selected), MAX_PUBLISHED),
                        truncated=len(selected) > MAX_PUBLISHED,
                        acquisition_min=dates[0] if dates else None,
                        acquisition_max=dates[-1] if dates else None,
                        local_raw_file=str(target.relative_to(ROOT)))
        except Exception as exc:
            item["error"] = f"{type(exc).__name__}: {exc}"
        sources.append(item)
        print(json.dumps({key: item.get(key) for key in
                          ("id", "status", "source_rows", "pilot_rows", "published_rows", "error")},
                         ensure_ascii=False))
    snapshot = {"schema_version": 1, "created_at": retrieved,
                "bbox": {"west": BBOX[0], "south": BBOX[1], "east": BBOX[2], "north": BBOX[3]},
                "bbox_is_administrative_boundary": False, "sources": sources}
    (public_dir / "snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
                                             encoding="utf-8")
    print("Instantánea publicada: dist/data/snapshot.json. Revisar status y antigüedad antes de interpretar.")

if __name__ == "__main__":
    main()
