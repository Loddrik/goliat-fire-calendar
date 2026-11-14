"""Consulta comunal observada y agregados reproducibles, sin armonización.

Requiere descargar_sources y prepare_boundaries antes de ejecutar.
"""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from contextlib import ExitStack
from datetime import date, datetime, timezone
from pathlib import Path

from shapely.geometry import shape

from geo import CanonicalAssignment, cell_of

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["latitude", "longitude", "acq_date", "acq_time", "satellite", "instrument", "confidence",
          "version", "brightness", "bright_ti4", "bright_t31", "bright_ti5", "scan", "track", "frp",
          "daynight", "type", "cut_com", "comuna", "grid_x", "grid_y", "source_file"]
SOURCES = {
    "modis": {"id": "aqua-history", "title": "MODIS Aqua · histórico observado", "platform": "Aqua",
              "instrument": "MODIS", "start": "2002-07", "accepted_satellites": ["Aqua", "A"]},
    "viirs-snpp": {"id": "snpp-history", "title": "VIIRS S-NPP · histórico observado", "platform": "Suomi-NPP",
                   "instrument": "VIIRS", "start": "2012-01", "accepted_satellites": ["N", "NPP", "Suomi-NPP"]},
    "viirs-jpss1": {"id": "noaa20-history", "title": "VIIRS NOAA-20 · histórico observado", "platform": "NOAA-20",
                    "instrument": "VIIRS", "start": "2018-04", "accepted_satellites": ["N20", "NOAA-20"]},
}


def file_hash(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def valid_time(value):
    text = str(value).zfill(4)
    return len(text) == 4 and text.isdigit() and int(text[:2]) < 24 and int(text[2:]) < 60


def eligible(row, sensor, file_year):
    """Retorna motivo de exclusión o None; contabilidad mutuamente excluyente."""
    try:
        latitude, longitude = float(row["latitude"]), float(row["longitude"])
        if not (math.isfinite(latitude) and math.isfinite(longitude) and -90 <= latitude < 90 and -180 <= longitude < 180):
            return "invalid_coordinate"
        acquired = date.fromisoformat(row["acq_date"])
        if not valid_time(row.get("acq_time", "")):
            return "invalid_time"
    except (TypeError, ValueError, KeyError):
        return "invalid_row"
    if acquired.year != file_year:
        return "outside_file_year"
    if row["acq_date"][:7] < SOURCES[sensor]["start"]:
        return "before_source_start"
    if row.get("satellite") not in SOURCES[sensor]["accepted_satellites"]:
        return "other_platform"
    if str(row.get("daynight", "")).upper() != "D":
        return "night_or_unknown"
    confidence = row.get("confidence", "").strip().lower()
    if sensor == "modis":
        try:
            if not 30 <= float(confidence) <= 100:
                return "confidence"
        except (ValueError, TypeError):
            return "confidence"
    elif confidence not in ("n", "h", "nominal", "high"):
        return "confidence"
    if row.get("type", "").strip() != "0":
        return "non_vegetation_or_unknown_type"
    return None


def months_for(source, files):
    years = sorted({entry["year"] for entry in files})
    return [f"{year:04d}-{month:02d}" for year in years for month in range(1, 13)
            if f"{year:04d}-{month:02d}" >= source["start"]]


def prepare():
    download = json.loads((ROOT / "reports/history-download.json").read_text())
    boundaries = json.loads((ROOT / "reports/boundaries.json").read_text())
    geojson = ROOT / "data/processed/communes-full.geojson"
    if file_hash(geojson) != boundaries["geometry_sha256"]:
        raise ValueError("La geometría no coincide con su metadato")
    features = json.loads(geojson.read_text())["features"]
    communes = [{**feature["properties"], "geometry": shape(feature["geometry"])} for feature in features]
    assignment = CanonicalAssignment(communes)
    commune_by_cut = {commune["cut"]: commune for commune in communes}
    extent = (min(commune["bbox"][0] for commune in communes), min(commune["bbox"][1] for commune in communes),
              max(commune["bbox"][2] for commune in communes), max(commune["bbox"][3] for commune in communes))
    prepared_at = datetime.now(timezone.utc).isoformat()
    public_manifest = {"schema_version": 1, "created_at": prepared_at, "harmonization": "not-started",
                       "geography": {key: boundaries[key] for key in ("source", "geometry_sha256", "regions", "retrospective_geography", "assignment_rule")},
                       "communes": boundaries["communes"], "sources": [],
                       "filters": {"daynight": "D", "modis_min_confidence": 30, "viirs_confidence": ["n", "h"],
                                   "type": "0", "type_meaning": "presumed vegetation fire, not confirmation",
                                   "additional_static_mask": "not-applied"},
                       "grid": {"degrees": 0.01, "longitude_origin": -180, "latitude_origin": -90,
                                "time_basis": "UTC", "assignment": "cell-centre", "counting": "per-platform-cell-day"},
                       "limitations": ["Geografía fija DPA 2023 aplicada retrospectivamente.",
                                       "Type=0 es una clasificación del producto, no identificación de incendios ni de causa.",
                                       "Cero detecciones no demuestra ausencia de fuego ni cobertura suficiente.",
                                       "Los meses sin archivo no se rellenan con ceros.",
                                       "La cola NRT reciente no se concatena con los archivos anuales."]}
    all_file_reports, all_monthly = [], []
    for sensor, description in SOURCES.items():
        files = [entry for entry in download["files"] if entry["sensor"] == sensor and entry["status"] == "downloaded"]
        public_dir = ROOT / "dist/data/history" / description["id"]
        public_dir.mkdir(parents=True, exist_ok=True)
        monthly = defaultdict(lambda: {"detections": 0, "cells": set()})
        commune_stats = {cut: {"rows": 0, "date_min": None, "date_max": None} for cut in commune_by_cut}
        source_versions, selected_versions, global_dates, report_rows = set(), set(), [], []
        total = Counter()
        with ExitStack() as stack:
            writers = {}
            for cut in commune_by_cut:
                stream = stack.enter_context((public_dir / (cut + ".csv")).open("w", encoding="utf-8", newline=""))
                writer = csv.DictWriter(stream, fieldnames=FIELDS)
                writer.writeheader()
                writers[cut] = writer
            for entry in sorted(files, key=lambda item: item["year"]):
                target = ROOT / entry["local_path"]
                if file_hash(target) != entry["sha256"]:
                    raise ValueError("Hash no coincide: " + entry["filename"])
                counts = Counter()
                fingerprints = set()
                input_versions, file_selected_versions = set(), set()
                with target.open(encoding="utf-8-sig", newline="") as stream:
                    reader = csv.DictReader(stream)
                    for row in reader:
                        counts["input"] += 1
                        if None in row or any(value is None for value in row.values()):
                            counts["invalid_shape"] += 1
                            continue
                        source_versions.add(row.get("version", "unknown"))
                        input_versions.add(row.get("version", "unknown"))
                        reason = eligible(row, sensor, entry["year"])
                        if reason:
                            counts[reason] += 1
                            continue
                        lon, lat = float(row["longitude"]), float(row["latitude"])
                        # El margen contempla centros de celda a un lado de la caja.
                        if not (extent[0] - .01 <= lon <= extent[2] + .01 and extent[1] - .01 <= lat <= extent[3] + .01):
                            counts["outside_pilot_bbox"] += 1
                            continue
                        cell = cell_of(lon, lat)
                        cut, location = assignment.assign_cell(cell)
                        if cut is None:
                            counts[location] += 1
                            continue
                        if location == "shared-edge-min-cut":
                            counts["shared_edge_tie"] += 1
                        counts["selected"] += 1
                        selected_versions.add(row.get("version", "unknown"))
                        file_selected_versions.add(row.get("version", "unknown"))
                        fingerprint = (lon, lat, row["acq_date"], row["acq_time"], row["satellite"])
                        if fingerprint in fingerprints:
                            counts["exact_duplicates_selected"] += 1
                        fingerprints.add(fingerprint)
                        observed = {field: row.get(field, "") for field in FIELDS}
                        observed.update(cut_com=cut, comuna=commune_by_cut[cut]["name"], grid_x=cell[0], grid_y=cell[1],
                                        source_file=entry["filename"])
                        writers[cut].writerow(observed)
                        stats = commune_stats[cut]
                        stats["rows"] += 1
                        stats["date_min"] = min(stats["date_min"] or row["acq_date"], row["acq_date"])
                        stats["date_max"] = max(stats["date_max"] or row["acq_date"], row["acq_date"])
                        global_dates.append(row["acq_date"])
                        group = monthly[(cut, row["acq_date"][:7])]
                        group["detections"] += 1
                        group["cells"].add((row["acq_date"], cell))
                total.update(counts)
                report = {"filename": entry["filename"], "url": entry["url"], "sha256": entry["sha256"],
                          "bytes": entry["bytes"], "year": entry["year"], "counts": dict(counts),
                          "input_versions": sorted(input_versions), "selected_versions": sorted(file_selected_versions)}
                all_file_reports.append(report)
                report_rows.append(report)
                print(json.dumps({"file": entry["filename"], "input": counts["input"], "selected": counts["selected"]}), flush=True)
        dataset_communes = []
        for cut in commune_by_cut:
            target = public_dir / (cut + ".csv")
            dataset_communes.append({"cut": cut, **commune_stats[cut], "url": f"data/history/{description['id']}/{cut}.csv",
                                     "sha256": file_hash(target), "bytes": target.stat().st_size})
        # Los ceros son ausencia de detecciones registradas en archivos presentes.
        # No se añaden años de archivos ausentes ni se infiere cobertura.
        for cut in commune_by_cut:
            for month in months_for(description, files):
                group = monthly.get((cut, month), {"detections": 0, "cells": set()})
                all_monthly.append({"source_id": description["id"], "cut": cut, "month": month,
                                    "detections": group["detections"], "cell_days": len(group["cells"]),
                                    "observation_coverage": "unknown"})
        excluded = sum(value for key, value in total.items() if key not in ("input", "selected", "shared_edge_tie", "exact_duplicates_selected"))
        if total["input"] != total["selected"] + excluded:
            raise ValueError("No cierra la contabilidad de filas")
        source = {key: value for key, value in description.items() if key != "accepted_satellites"}
        source.update(kind="historical-observed", status="prepared", end="2025-12", rows=total["selected"],
                      input_rows=total["input"], counts=dict(total), columns=FIELDS, versions=sorted(selected_versions),
                      input_versions=sorted(source_versions),
                      acquisition_min=min(global_dates) if global_dates else None,
                      acquisition_max=max(global_dates) if global_dates else None,
                      files=report_rows, available_years=sorted(entry["year"] for entry in files),
                      missing_years=sorted(set(range(int(description["start"][:4]), 2026)) - {entry["year"] for entry in files}),
                      communes=dataset_communes)
        public_manifest["sources"].append(source)
    output_dir = ROOT / "data/processed"
    with (output_dir / "observed-monthly.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["source_id", "cut", "month", "detections", "cell_days", "observation_coverage"])
        writer.writeheader()
        writer.writerows(all_monthly)
    monthly_json = json.dumps(all_monthly, ensure_ascii=False, separators=(",", ":"))
    (ROOT / "dist/data/observed-monthly.json").write_text(monthly_json + "\n")
    (ROOT / "dist/data/history-manifest.json").write_text(json.dumps(public_manifest, ensure_ascii=False, separators=(",", ":")) + "\n")
    report = {"schema_version": 1, "generated_at": prepared_at, "communes": len(communes), "geography_sha256": boundaries["geometry_sha256"],
              "source_summary": [{key: source[key] for key in ("id", "input_rows", "rows", "counts", "available_years", "missing_years", "versions")} for source in public_manifest["sources"]],
              "files": all_file_reports, "monthly_rows": len(all_monthly), "harmonization": "not-started",
              "filters": public_manifest["filters"], "grid": public_manifest["grid"], "limitations": public_manifest["limitations"]}
    (ROOT / "reports/history-processing.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"communes": len(communes), "monthly_rows": len(all_monthly),
                      "selected_by_source": {source["id"]: source["rows"] for source in public_manifest["sources"]}}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    prepare()
