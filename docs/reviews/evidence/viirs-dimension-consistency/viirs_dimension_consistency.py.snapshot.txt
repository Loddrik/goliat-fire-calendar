"""Selective provider-size consistency, not fire truth or all-pixel validation.

Reads local prefiltered S-NPP CSVs and pinned GEO NPZs only. No FIRMS API,
credentials, FIRE raster arrays, FRP analysis or cross-sensor association.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np
from pyproj import Transformer

from observation_mesh import build_scan_mesh
from observation_mesh_validation import crop_columns, spacing_transitions, polygon_crosses_transition

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/reviews/2026-11-15-viirs-dimension-consistency-protocol.md"
MANIFEST = ROOT / "observed/dist/data/history-manifest.json"
EXPORT = ROOT / ".runtime/observation-mesh-validation"
OUT = ROOT / "docs/reviews/evidence/viirs-dimension-consistency"
SATELLITES = {"N", "NPP", "Suomi-NPP"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def aggregation_I(sample):
    if isinstance(sample, bool) or not isinstance(sample, (int, np.integer)) or not 0 <= sample <= 6399:
        raise ValueError("Native zero-based I-band column required")
    for start, end, factor in [(0, 1279, 1), (1280, 2015, 2), (2016, 4383, 3),
                                (4384, 5119, 2), (5120, 6399, 1)]:
        if start <= sample <= end:
            return {"start": start, "end": end, "factor": factor}


def hhmm(value):
    text = str(value).strip()
    if not text.isdigit() or len(text) > 4:
        raise ValueError("Invalid finite HHMM time")
    text = text.zfill(4)
    if int(text[:2]) >= 24 or int(text[2:]) >= 60:
        raise ValueError("Invalid HHMM clock range")
    return text


def verified_rows(payload, segment, source):
    if digest(payload) != segment["sha256"] or len(payload) != segment["bytes"]:
        raise ValueError("Published CSV hash/size mismatch")
    rows = list(csv.DictReader(io.StringIO(payload.decode("utf-8-sig"))))
    if len(rows) != segment["rows"]:
        raise ValueError("Published CSV manifest row count mismatch")
    names = {f["filename"]: f for f in source["files"]}
    for row in rows:
        source_file = names.get(row.get("source_file"))
        if (row.get("satellite") not in SATELLITES or row.get("instrument") != "VIIRS"
                or row.get("daynight") != "D" or row.get("type") != "0"
                or row.get("confidence", "").lower() not in {"n", "h"}
                or row.get("version") not in source["versions"] or source_file is None
                or row.get("cut_com") != segment["cut"]):
            raise ValueError("Published selective S-NPP source/filter mismatch")
        acquired = datetime.strptime(row["acq_date"], "%Y-%m-%d")
        if acquired.year != source_file["year"]:
            raise ValueError("Source file year mismatch")
        hhmm(row["acq_time"])
        latitude, longitude = float(row["latitude"]), float(row["longitude"])
        if not math.isfinite(latitude) or not math.isfinite(longitude) or abs(latitude) > 90 or abs(longitude) > 180:
            raise ValueError("Invalid published geographic coordinate")
    return rows


def finite_positive(value):
    try:
        value = float(value)
        return value if math.isfinite(value) and value > 0 else None
    except (ValueError, TypeError):
        return None


def deduplicate(records):
    groups = defaultdict(list)
    for row in records:
        groups[("Suomi-NPP", row["acq_date"], hhmm(row["acq_time"]), float(row["latitude"]), float(row["longitude"]))].append(row)
    output = []
    for identity, rows in sorted(groups.items()):
        geometries = {(finite_positive(r.get("scan")), finite_positive(r.get("track"))) for r in rows}
        record = {"identity": list(identity), "acq_date": identity[1], "acq_time": identity[2],
                  "latitude": identity[3], "longitude": identity[4], "source_files": sorted({r["source_file"] for r in rows}),
                  "duplicate_count": len(rows), "source_csvs": sorted({r["source_csv"] for r in rows})}
        if len(geometries) != 1:
            record["source_state"] = "ambiguous_source_geometry"
        else:
            scan, track = next(iter(geometries))
            record.update(scan_km=scan, track_km=track,
                          source_state="reference_candidate" if scan is not None and track is not None else "invalid_reference_dimensions")
        output.append(record)
    return output


def unique_center_associations(xy, centers, tolerance):
    """All centers within tolerance count; no nearest rescue of ambiguity."""
    output = []
    for point in np.asarray(xy):
        distance = np.linalg.norm(centers - point, axis=1)
        choices = np.flatnonzero(distance <= tolerance)
        if len(choices) == 1:
            i = int(choices[0])
            output.append({"state": "unique_center", "center_index": i, "distance_m": float(distance[i])})
        else:
            output.append({"state": "unmatched" if not len(choices) else "ambiguous_centers", "candidate_centers": int(len(choices))})
    use = Counter(x["center_index"] for x in output if x["state"] == "unique_center")
    for record in output:
        if record["state"] == "unique_center" and use[record["center_index"]] > 1:
            record["state"] = "multiple_CSV_identities_for_center"
    return output


def measures(polygon):
    p = np.asarray(polygon.exterior.coords)[:4]
    return ((np.linalg.norm(p[1] - p[0]) + np.linalg.norm(p[2] - p[3])) / 2,
            (np.linalg.norm(p[3] - p[0]) + np.linalg.norm(p[2] - p[1])) / 2,
            polygon.area)


def gate(errors):
    errors = np.asarray(errors, dtype=float)
    return bool(len(errors) >= 5 and np.isfinite(errors).all() and np.median(errors) <= .2 and np.percentile(errors, 95) <= .3)


def metric_stats(values):
    return {"n": len(values), "percentiles": None if not len(values) else {
        str(i): float(v) for i, v in zip(range(101), np.percentile(values, range(101)))}}


def case_times():
    old = json.loads((ROOT / "docs/reviews/evidence/observation-preflight/summary.json").read_text())["chosen_probe_pair"]
    selection = json.loads((ROOT / "docs/reviews/evidence/observation-case2023/result.json").read_text())["selected_pair"]
    catalog = json.loads((ROOT / "docs/reviews/evidence/observation-case2023/VNP14IMG-catalog.json").read_text())["granules"]
    chosen = next(e for e in catalog if e["producer_granule_id"] == selection["viirs_id"])
    return {"2019": (old["viirs_start"], old["viirs_end"]), "2023": (chosen["time_start"], chosen["time_end"])}


def in_interval(date, minute, start, end):
    when = datetime.fromisoformat(date + "T" + hhmm(minute)[:2] + ":" + hhmm(minute)[2:] + ":00+00:00")
    return datetime.fromisoformat(start.replace("Z", "+00:00")) <= when < datetime.fromisoformat(end.replace("Z", "+00:00"))


def load_native_geometry(index, case):
    key = case + "_VNP03IMG"
    product = index["cases"][key]
    coordinates, native_keys, polygons, states = [], [], {}, {}
    center = index["center_xy"]
    for window in product["windows"]:
        path = EXPORT / window["npz"]
        if digest(path.read_bytes()) != window["sha256"]:
            raise ValueError("Pinned GEO NPZ hash mismatch")
        with np.load(path, allow_pickle=False) as data:
            x, y, valid = data["x"], data["y"], data["valid"]
            # Association includes invalid-flag centers with finite coordinates;
            # their original mesh state, not a neighboring valid pixel, governs.
            for r, c in zip(*np.nonzero(np.isfinite(x) & np.isfinite(y))):
                coordinates.append((x[r, c], y[r, c]))
                native_keys.append((window["native_row_start"] + int(r), window["native_col_start"] + int(c)))
            left, right = crop_columns(x, y, center, 40000)
            x, y, valid = x[:, left:right], y[:, left:right], valid[:, left:right]
            mesh = build_scan_mesh(x, y, valid, 32)
            gaps, _ = spacing_transitions(x, y, valid)
            for record in mesh["states"]:
                r, c = record["row"], record["col"]
                native_key = (window["native_row_start"] + r, window["native_col_start"] + left + c)
                state = record["state"]
                if state == "nominal_core_polygon" and polygon_crosses_transition(gaps, r, c):
                    state = "geometry_transition_unresolved"
                states[native_key] = state
            for record in mesh["polygons"]:
                native_key = (window["native_row_start"] + record["row"], window["native_col_start"] + left + record["col"])
                if states[native_key] == "nominal_core_polygon":
                    polygons[native_key] = record["polygon"]
    if len(set(native_keys)) != len(native_keys):
        raise ValueError("Repeated native GEO keys in exported windows")
    domain_columns = sorted({key[1] for key in native_keys})
    domain = {"native_centers": len(native_keys), "native_sample_min": min(domain_columns), "native_sample_max": max(domain_columns),
              "aggregation_regions": sorted({(aggregation_I(c)["start"], aggregation_I(c)["end"], aggregation_I(c)["factor"]) for c in domain_columns})}
    return np.asarray(coordinates), native_keys, polygons, states, domain


def evaluate(records, geometry, tolerance, transform):
    centers, native_keys, polygons, states, domain = geometry
    result = [dict(r) for r in records]
    # All source identities participate in collision detection, including those
    # whose dimensions are unavailable/conflicting; no favorable duplicate wins.
    candidates = list(range(len(result)))
    points = np.asarray([transform.transform(result[i]["longitude"], result[i]["latitude"]) for i in candidates]).reshape(-1, 2)
    matched = unique_center_associations(points, centers, tolerance)
    for row in result:
        row["state"] = row["source_state"]
    for i, match in zip(candidates, matched):
        row = result[i]
        row.update(match)
        row["association_state"] = match["state"]
        if row["source_state"] != "reference_candidate":
            row["state"] = row["source_state"]
        if "center_index" not in match:
            continue
        nr, nc = native_keys[match["center_index"]]
        row.update(native_row=nr, native_col=nc, native_scan=nr // 32, detector=nr % 32, aggregation=aggregation_I(nc))
        if match["state"] != "unique_center" or row["source_state"] != "reference_candidate":
            continue
        state = states.get((nr, nc), "outside_CORE_window")
        if state != "nominal_core_polygon":
            row["state"] = state
            continue
        scan, track, area = measures(polygons[nr, nc])
        row.update(state="eligible_selective_geometry_reference", mesh_scan_m=float(scan), mesh_track_m=float(track), mesh_area_m2=float(area),
                   scan_relative_error=float(abs(scan / (1000 * row["scan_km"]) - 1)),
                   track_relative_error=float(abs(track / (1000 * row["track_km"]) - 1)),
                   area_relative_error=float(abs(area / (1e6 * row["scan_km"] * row["track_km"]) - 1)))
    eligible = [r for r in result if r["state"] == "eligible_selective_geometry_reference"]
    metrics = {key: [r[key] for r in eligible] for key in ["scan_relative_error", "track_relative_error", "area_relative_error"]}
    n = len(eligible)
    status = "not_evaluable" if not result else ("insufficient_reference" if n < 5 else "evaluated")
    return {"tolerance_m": tolerance, "status": status, "unique_source_records": len(result), "eligible_CORE_references": n,
            "states": dict(Counter(r["state"] for r in result)), "metrics": {k: metric_stats(v) for k, v in metrics.items()},
            "engineering_gates": {k: gate(v) for k, v in metrics.items()},
            "selective_size_consistency_passed": bool(n >= 5 and all(gate(v) for v in metrics.values())),
            "eligible_native_sample_span": None if not eligible else [min(r["native_col"] for r in eligible), max(r["native_col"] for r in eligible)],
            "eligible_detectors": sorted({r["detector"] for r in eligible}), "GEO_exported_domain": domain}, result


def run():
    started = datetime.now(timezone.utc).isoformat()
    if OUT.exists() and any(OUT.iterdir()):
        raise ValueError("Refuse selective evidence overwrite")
    manifest_payload = MANIFEST.read_bytes()
    manifest = json.loads(manifest_payload)
    source = next(s for s in manifest["sources"] if s["id"] == "snpp-history")
    if len(source["communes"]) != 54:
        raise ValueError("Unexpected published source segment inventory")
    if source["platform"] != "Suomi-NPP" or source["instrument"] != "VIIRS" or manifest["filters"]["daynight"] != "D" or manifest["filters"]["type"] != "0" or set(manifest["filters"]["viirs_confidence"]) != {"n", "h"}:
        raise ValueError("Selective source contract changed")
    index_payload = (EXPORT / "index.json").read_bytes()
    index = json.loads(index_payload)
    benchmark_manifest_path = ROOT / "docs/reviews/evidence/observation-mesh-validation/manifest.json"
    benchmark_manifest = json.loads(benchmark_manifest_path.read_text())
    if digest(index_payload) != benchmark_manifest["files"]["export-index.json"]["sha256"]:
        raise ValueError("GEO export index no longer matches frozen B benchmark")
    helper_paths = [ROOT / "pipeline/observation_mesh.py", ROOT / "pipeline/observation_mesh_validation.py"]
    if digest(helper_paths[0].read_bytes()) != index["mesh_helper_sha256"] or digest(helper_paths[1].read_bytes()) != index["code_sha256"]:
        raise ValueError("Pinned mesh helpers changed")
    transform = Transformer.from_crs(4326, 32718, always_xy=True)
    center = index["center_xy"]
    intervals = case_times()
    selected = {case: [] for case in intervals}
    csv_inputs = {}
    for segment in source["communes"]:
        path = ROOT / "observed/dist" / segment["url"]
        payload = path.read_bytes()
        rows = verified_rows(payload, segment, source)
        csv_inputs[str(path.relative_to(ROOT))] = {"sha256": digest(payload), "bytes": len(payload)}
        for row in rows:
            for case, (start, end) in intervals.items():
                if row["acq_date"] != start[:10] or not in_interval(row["acq_date"], row["acq_time"], start, end):
                    continue
                x, y = transform.transform(float(row["longitude"]), float(row["latitude"]))
                if abs(x - center[0]) <= 25000 and abs(y - center[1]) <= 25000:
                    # Persist no FRP, brightness or fire-class arrays.
                    selected[case].append({k: row[k] for k in ["latitude", "longitude", "acq_date", "acq_time", "scan", "track", "source_file"]} | {"source_csv": str(path.relative_to(ROOT))})
    report = {"scope": "Selective provider-size consistency only; no MODIS or fire-class associations",
              "started_utc": started, "protocol_sha256": digest(PROTOCOL.read_bytes()),
              "code_sha256": digest(Path(__file__).read_bytes()), "source_manifest_sha256": digest(manifest_payload),
              "GEO_export_index_sha256": digest(index_payload), "CSV_inputs": csv_inputs,
              "B_manifest_sha256": digest(benchmark_manifest_path.read_bytes()),
              "helper_sha256": {p.name: digest(p.read_bytes()) for p in helper_paths}, "cases": {},
              "selectivity": {"type": "0", "confidence": ["n", "h"], "platform": "Suomi-NPP", "reference": "provider nominal dimensions on recorded detections, not independent ground truth"},
              "physical_detector_dimensions_verified": False, "all_pixel_dimensions_verified": False,
              "gate1_passed": False, "scientific_eligibility_certified": False,
              "primary_tolerance_m": 25, "secondary_tolerance_m": 75}
    OUT.mkdir(parents=True, exist_ok=True)
    for case, interval in intervals.items():
        records = deduplicate(selected[case])
        geometry = load_native_geometry(index, case)
        case_report = {"UTC_granule_interval_half_open": list(interval), "source_rows_before_identity_dedup": len(selected[case]),
                       "source_identity_records": len(records), "tolerances": {}}
        for tolerance in [25, 75]:
            stats, details = evaluate(records, geometry, tolerance, transform)
            case_report["tolerances"][str(tolerance)] = stats
            (OUT / (case + "-" + str(tolerance) + "m-records.json")).write_text(json.dumps(details, indent=2, allow_nan=False) + "\n")
        case_report["primary_selective_size_consistency_passed"] = case_report["tolerances"]["25"]["selective_size_consistency_passed"]
        report["cases"][case] = case_report
    report["completed_utc"] = datetime.now(timezone.utc).isoformat()
    (OUT / "summary.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    for path in [Path(__file__), PROTOCOL, *helper_paths]:
        (OUT / (path.name + ".snapshot.txt")).write_bytes(path.read_bytes())
    packing = {"files": {p.name: {"bytes": p.stat().st_size, "sha256": digest(p.read_bytes())} for p in sorted(OUT.iterdir()) if p.is_file()}}
    (OUT / "manifest.json").write_text(json.dumps(packing, indent=2) + "\n")
    return report


if __name__ == "__main__":
    result = run()
    print(json.dumps({k: {"source_records": v["source_identity_records"],
                         "primary_status": v["tolerances"]["25"]["status"],
                         "eligible_primary": v["tolerances"]["25"]["eligible_CORE_references"],
                         "primary_passed": v["primary_selective_size_consistency_passed"]}
                      for k, v in result["cases"].items()}, indent=2))
