"""Inventario reproducible de CSV locales FIRMS, sin depender de pandas."""
import argparse
import csv
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {"latitude", "longitude", "acq_date"}

def inspect(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    item = {"path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
            "bytes": path.stat().st_size, "sha256": digest.hexdigest(), "rows": 0,
            "invalid_rows": 0, "duplicate_rows": 0, "date_min": None, "date_max": None,
            "platforms": [], "instruments": [], "daynight": [], "columns": [],
            "issues": [], "administrative_assignment": "not-performed"}
    seen, dates, platforms, instruments, daynight = set(), [], set(), set(), set()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        item["columns"] = reader.fieldnames or []
        missing = sorted(REQUIRED - set(item["columns"]))
        if missing:
            item["issues"].append("missing_columns:" + ",".join(missing))
            return item
        for row in reader:
            item["rows"] += 1
            try:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError("row_shape")
                lat, lon = float(row["latitude"]), float(row["longitude"])
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    raise ValueError("coordinates")
                acquisition = date.fromisoformat(row["acq_date"])
            except (ValueError, TypeError):
                item["invalid_rows"] += 1
                continue
            dates.append(acquisition.isoformat())
            key = tuple(row.get(field, "") for field in
                        ("latitude", "longitude", "acq_date", "acq_time", "satellite", "instrument"))
            if key in seen:
                item["duplicate_rows"] += 1
            seen.add(key)
            for field, values in (("satellite", platforms), ("instrument", instruments), ("daynight", daynight)):
                if row.get(field):
                    values.add(row[field])
    item.update(date_min=min(dates) if dates else None, date_max=max(dates) if dates else None,
                platforms=sorted(platforms), instruments=sorted(instruments), daynight=sorted(daynight))
    return item

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=ROOT / "data/raw")
    args = parser.parse_args()
    files = sorted(args.directory.glob("*.csv")) if args.directory.exists() else []
    results = []
    for path in files:
        try:
            results.append(inspect(path))
        except (OSError, UnicodeError, csv.Error) as exc:
            results.append({"path": str(path), "status": "unreadable", "error": str(exc)})
    def read_report(name):
        path = ROOT / "reports" / name
        return json.loads(path.read_text()) if path.exists() else None
    history = read_report("history-download.json")
    geography = read_report("boundaries.json")
    processing = read_report("history-processing.json")
    historical_files = history.get("files", []) if history else []
    def historical_status(sensor):
        entries = [entry for entry in historical_files if entry["sensor"] == sensor]
        if not entries:
            return "missing"
        return "downloaded" if all(entry["status"] == "downloaded" for entry in entries) else "partial"
    historical_summary = {"source_report": "reports/history-download.json", "files": len(historical_files),
                          "missing": history.get("missing", []) if history else [],
                          "processing_report": "reports/history-processing.json" if processing else None}
    report = {"schema_version": 2, "generated_at": datetime.now(timezone.utc).isoformat(),
              "files": results,
              "history": historical_summary,
              "geography": {"report": "reports/boundaries.json", "communes": geography["commune_count"],
                            "geometry_sha256": geography["geometry_sha256"]} if geography else None,
              "availability": {
                  "recent_firms_snapshot": "available" if results else "missing",
                  "modis_historical": historical_status("modis"), "viirs_historical": historical_status("viirs-snpp"),
                  "noaa20_historical": historical_status("viirs-jpss1"),
                  "current_year_2026_history": "not-downloaded-annual-catalog-ends-2025",
                  "communal_boundaries": "prepared-DPA-2023" if geography else "missing",
                  "static_source_mask": "product-type-0-only-additional-mask-pending" if processing else "missing",
                  "harmonization": "not-started"},
              "notes": ["La muestra reciente no sustituye las series históricas.",
                        "Las consultas comunales preparadas usan DPA 2023 fija y centro de celda; las cargas locales no se asignan automáticamente.",
                        "Los originales en data/raw no se publican automáticamente."]}
    target = ROOT / "reports/inventory.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(target), "files": len(results),
                      "rows": sum(item.get("rows", 0) for item in results),
                      "invalid_rows": sum(item.get("invalid_rows", 0) for item in results)},
                     ensure_ascii=False))

if __name__ == "__main__":
    main()
