"""Phase B nominal geometry benchmark: GEO only; no fire/atmospheric QA I/O."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime/observation-mesh-validation"
OUT = ROOT / "docs/reviews/evidence/observation-mesh-validation"
PROTOCOLS = [ROOT / "docs/reviews/2026-11-15-observation-mesh-validation-protocol.md",
             ROOT / "docs/reviews/2026-11-15-observation-mesh-validation-clarification.md"]
SOURCE_RECORDS = {"2019": ROOT / "docs/reviews/evidence/observation-authenticated/acquisition.json",
                  "2023": ROOT / "docs/reviews/evidence/observation-case2023/result.json"}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def nominal_modis_dimensions(sample):
    sample = np.asarray(sample, dtype=float)
    if not np.isfinite(sample).all() or np.any(sample < 0) or np.any(sample > 1353):
        raise ValueError("Native zero-based MODIS sample required")
    theta = .0014184397 * (sample - 676.5)
    return dimensions_at_scan_angle(theta)


def dimensions_at_scan_angle(theta):
    theta = np.asarray(theta, dtype=float)
    re, h, s = 6378.137, 705., .0014184397
    r = re + h
    discriminant = (re / r) ** 2 - np.sin(theta) ** 2
    if not np.isfinite(theta).all() or np.any(discriminant <= 0):
        raise ValueError("Nonphysical nominal scan-angle discriminant")
    d = np.sqrt(discriminant)
    along_scan_m = 1000 * re * s * (np.cos(theta) / d - 1)
    along_track_m = 1000 * r * s * (np.cos(theta) - d)
    return along_scan_m, along_track_m


def stats(values):
    values = np.asarray(values, dtype=float)
    finite = values[np.isfinite(values)]
    return {"n": int(values.size), "nonfinite": int(values.size - finite.size),
            "percentiles": None if not finite.size else {
                str(q): float(v) for q, v in zip(range(101), np.percentile(finite, range(101)))}}


def dimension_gate(values):
    values = np.asarray(values, dtype=float)
    return bool(values.size and np.isfinite(values).all()
                and np.median(values) <= .2 and np.percentile(values, 95) <= .3)


def spacing_transitions(x, y, valid):
    """Geometry-only rule: adjacent gap ratio outside [0.8,1.25].

    Both gaps in an offending pair are flagged; a CORE polygon touching either
    gap in one of its three contributing detector rows remains unresolved.
    """
    p = np.stack([x, y], axis=-1)
    gaps = np.linalg.norm(p[:, 1:] - p[:, :-1], axis=-1)
    gap_valid = valid[:, 1:] & valid[:, :-1] & np.isfinite(gaps) & (gaps > 0)
    comparable = gap_valid[:, 1:] & gap_valid[:, :-1]
    ratios = np.full(comparable.shape, np.nan)
    ratios[comparable] = gaps[:, 1:][comparable] / gaps[:, :-1][comparable]
    flagged = comparable & ((ratios > 1.25) | (ratios < .8))
    bad_gaps = np.zeros(gaps.shape, dtype=bool)
    bad_gaps[:, :-1] |= flagged
    bad_gaps[:, 1:] |= flagged
    return bad_gaps, {"comparable_adjacent_gaps": int(comparable.sum()),
                      "flagged_adjacent_gap_ratios": int(flagged.sum()),
                      "flagged_gap_links": int(bad_gaps.sum()),
                      "thresholds": {"lower": .8, "upper": 1.25}}


def polygon_crosses_transition(bad_gaps, row, col):
    return bool(bad_gaps[row - 1:row + 2, col - 1:col + 1].any())


def crop_columns(x, y, center, half_side, padding=2):
    eligible = np.isfinite(x) & np.isfinite(y) & (abs(x - center[0]) <= half_side) & (abs(y - center[1]) <= half_side)
    cols = np.nonzero(eligible)[1]
    return None if not len(cols) else (max(0, int(cols.min()) - padding), min(x.shape[1], int(cols.max()) + padding + 1))


def export_geo():
    """Run with the isolated GEO reader, exporting ignored scan windows only."""
    import h5py
    from pyhdf.SD import SD, SDC
    import pyproj
    import importlib.metadata
    if RUNTIME.exists() and any(RUNTIME.iterdir()):
        raise ValueError("Refuse existing GEO export overwrite")
    RUNTIME.mkdir(parents=True, exist_ok=True)
    transform = pyproj.Transformer.from_crs(4326, 32718, always_xy=True)
    center = transform.transform(-72.5, -37)
    index = {"scope": "Only GEO coordinates and geographic flags; no fire files opened",
             "started_utc": datetime.now(timezone.utc).isoformat(), "code_sha256": sha(__file__),
             "mesh_helper_sha256": sha(ROOT / "pipeline/observation_mesh.py"),
             "protocol_sha256": {p.name: sha(p) for p in PROTOCOLS}, "center_xy": list(center),
             "cases": {}, "environment": {"python": platform.python_version(),
                 "packages": {k: importlib.metadata.version(k) for k in ["numpy", "h5py", "pyhdf", "pyproj"]}}}
    for case, source in SOURCE_RECORDS.items():
        raw = json.loads(source.read_text())
        for product, rows in [("MYD03", 10), ("VNP03IMG", 32)]:
            evidence = raw["files"][product]
            path = ROOT / evidence["file"]
            if sha(path) != evidence["sha256"]:
                raise ValueError("Pinned GEO hash mismatch")
            key = case + "_" + product
            item = {"input": str(path.relative_to(ROOT)), "input_sha256": evidence["sha256"],
                    "source_record_sha256": sha(source), "rows_per_scan": rows, "windows": [],
                    "geo_flag_policy": "nonzero geographic flags retained but geometry input is unresolved"}
            if product == "MYD03":
                handle = SD(str(path), SDC.READ)
                datasets = [handle.select(k) for k in ["Latitude", "Longitude", "gflags"]]
                shape = tuple(datasets[0].info()[2])
            else:
                handle = h5py.File(path, "r")
                datasets = [handle["geolocation_data/" + k] for k in ["latitude", "longitude", "quality_flag"]]
                shape = tuple(datasets[0].shape)
            try:
                shapes = [tuple(d.info()[2]) if product == "MYD03" else tuple(d.shape) for d in datasets]
                if shape[0] % rows or any(s != shape for s in shapes):
                    raise ValueError("Incomplete native scan rows")
                item["native_shape"] = list(shape)
                counts = Counter()
                for offset in range(0, shape[0], rows * 10):
                    end = min(shape[0], offset + rows * 10)
                    lat, lon, flags = [np.asarray(d[offset:end, :]) for d in datasets]
                    finite = np.isfinite(lat) & np.isfinite(lon) & (abs(lat) <= 90) & (abs(lon) <= 180)
                    x, y = np.full(lat.shape, np.nan), np.full(lat.shape, np.nan)
                    x[finite], y[finite] = transform.transform(lon[finite], lat[finite])
                    valid = finite & np.isfinite(x) & np.isfinite(y) & (flags == 0)
                    counts["native_centers"] += lat.size
                    counts["invalid_coordinates"] += int((~finite).sum())
                    counts["nonzero_geographic_flags"] += int((flags != 0).sum())
                    for local in range(0, end - offset, rows):
                        sx, sy = x[local:local + rows], y[local:local + rows]
                        interval = crop_columns(sx, sy, center, 40000)
                        if interval is None:
                            continue
                        c0, c1 = interval
                        scan = (offset + local) // rows
                        filename = key + "_scan" + str(scan) + ".npz"
                        target = RUNTIME / filename
                        np.savez_compressed(target, x=sx[:, c0:c1], y=sy[:, c0:c1],
                                            valid=valid[local:local + rows, c0:c1],
                                            geographic_flags=flags[local:local + rows, c0:c1])
                        item["windows"].append({"npz": filename, "sha256": sha(target), "bytes": target.stat().st_size,
                                                "native_row_start": offset + local, "native_scan": scan,
                                                "native_col_start": c0, "native_col_end_exclusive": c1})
                item["granule_coordinate_inventory"] = dict(counts)
            finally:
                if product == "MYD03":
                    for d in datasets:
                        d.endaccess()
                    handle.end()
                else:
                    handle.close()
            index["cases"][key] = item
    index["completed_utc"] = datetime.now(timezone.utc).isoformat()
    (RUNTIME / "index.json").write_text(json.dumps(index, indent=2) + "\n")
    return index


def polygon_measurements(records, inverse, geod, is_modis):
    if not records:
        return {}, {}
    points = np.asarray([np.asarray(r["polygon"].exterior.coords)[:4] for r in records])
    scan = (np.linalg.norm(points[:, 1] - points[:, 0], axis=1) + np.linalg.norm(points[:, 2] - points[:, 3], axis=1)) / 2
    track = (np.linalg.norm(points[:, 3] - points[:, 0], axis=1) + np.linalg.norm(points[:, 2] - points[:, 1], axis=1)) / 2
    areas = np.asarray([r["polygon"].area for r in records])
    lon, lat = inverse.transform(points[..., 0], points[..., 1])
    gs = (geod.inv(lon[:, 0], lat[:, 0], lon[:, 1], lat[:, 1])[2] + geod.inv(lon[:, 3], lat[:, 3], lon[:, 2], lat[:, 2])[2]) / 2
    gt = (geod.inv(lon[:, 0], lat[:, 0], lon[:, 3], lat[:, 3])[2] + geod.inv(lon[:, 1], lat[:, 1], lon[:, 2], lat[:, 2])[2]) / 2
    ga = np.asarray([abs(geod.polygon_area_perimeter(lon[i], lat[i])[0]) for i in range(len(records))])
    measured = {"scan_length_m": scan, "track_length_m": track, "polygon_area_UTM_m2": areas,
                "projection_scan_relative_error": abs(scan / gs - 1),
                "projection_track_relative_error": abs(track / gt - 1),
                "projection_area_relative_error": abs(areas / ga - 1)}
    gates = {"projection_passed": bool(all(np.isfinite(measured[k]).all() and (measured[k] <= .01).all()
                for k in measured if k.startswith("projection_")))}
    if is_modis:
        ns, nt = nominal_modis_dimensions([r["native_col"] for r in records])
        measured.update(modis_scan_relative_error=abs(scan / ns - 1),
                        modis_track_relative_error=abs(track / nt - 1),
                        modis_area_relative_error=abs(areas / (ns * nt) - 1))
        for key in ["modis_scan_relative_error", "modis_track_relative_error", "modis_area_relative_error"]:
            gates[key + "_passed"] = dimension_gate(measured[key])
    return measured, gates


def grouped_stats(records, measured):
    output = {}
    # Diagnostics only: all fixed strata, never used to select geometry or gates.
    for kind, values in [("native_scan", [r["native_scan"] for r in records]),
                          ("detector", [r["detector"] for r in records]),
                          ("native_sample_band100", [r["native_col"] // 100 for r in records])]:
        array = np.asarray(values)
        output[kind] = {str(v): {name: stats(data[array == v]) for name, data in measured.items()}
                        for v in np.unique(array)}
    return output


def run_validation():
    from observation_mesh import build_scan_mesh
    from shapely.geometry import box
    from shapely.ops import unary_union
    from shapely.affinity import translate
    from pyproj import Transformer, Geod
    import shapely
    import pyproj
    if OUT.exists() and any(OUT.iterdir()):
        raise ValueError("Refuse previous validation overwrite")
    index = json.loads((RUNTIME / "index.json").read_text())
    if index["code_sha256"] != sha(__file__) or index["mesh_helper_sha256"] != sha(ROOT / "pipeline/observation_mesh.py") or index["protocol_sha256"] != {p.name: sha(p) for p in PROTOCOLS}:
        raise ValueError("Code/protocol changed after GEO export")
    center = index["center_xy"]
    aoi = box(center[0] - 25000, center[1] - 25000, center[0] + 25000, center[1] + 25000)
    inverse, geod = Transformer.from_crs(32718, 4326, always_xy=True), Geod(ellps="WGS84")
    report = {"scope": "Nominal CORE geometry benchmark only; no activity or atmospheric QA",
              "started_utc": datetime.now(timezone.utc).isoformat(), "code_sha256": sha(__file__),
              "mesh_helper_sha256": sha(ROOT / "pipeline/observation_mesh.py"),
              "protocol_sha256": index["protocol_sha256"], "export_index_sha256": sha(RUNTIME / "index.json"),
              "environment": {"python": platform.python_version(), "numpy": np.__version__, "shapely": shapely.__version__, "pyproj": pyproj.__version__},
              "metric_population": "Accepted CORE polygons with centers inside each halo; diagnostic strata do not extend outside these ROI subsets",
              "dimensional_primary_metric": "UTM sides/area vs nominal formula; geodesic measures separately check projection",
              "gate1_passed": False, "physical_footprints_verified": False,
              "pixel_exposure_times_verified": False, "scientific_eligibility_certified": False,
              "products": {}, "nominal_intersections": {}}
    unions, unclipped_unions = {}, {}
    for key, item in index["cases"].items():
        is_modis = key.endswith("MYD03")
        product_report = {"input_sha256": item["input_sha256"], "halos": {}, "VIIRS_detector_dimensions_verified": False if not is_modis else None}
        for halo in [10000, 15000]:
            records, state_counts, jump_counts, unresolved_records = [], Counter(), Counter(), []
            selected_state_counts = Counter()
            for window in item["windows"]:
                path = RUNTIME / window["npz"]
                if sha(path) != window["sha256"]:
                    raise ValueError("Exported GEO window hash mismatch")
                with np.load(path, allow_pickle=False) as data:
                    x, y, valid = data["x"], data["y"], data["valid"]
                    interval = crop_columns(x, y, center, 25000 + halo)
                    if interval is None:
                        continue
                    left, right = interval
                    x, y, valid = x[:, left:right], y[:, left:right], valid[:, left:right]
                    if x.shape[1] < 3:
                        state_counts["window_insufficient_columns"] += x.size
                        continue
                    mesh = build_scan_mesh(x, y, valid, item["rows_per_scan"])
                    bad_gaps = None
                    if not is_modis:
                        bad_gaps, diagnostic = spacing_transitions(x, y, valid)
                        jump_counts.update({k: v for k, v in diagnostic.items() if isinstance(v, int)})
                    poly_by_key = {(r["row"], r["col"]): r for r in mesh["polygons"]}
                    for s in mesh["states"]:
                        row, col = s["row"], s["col"]
                        state = s["state"]
                        if state == "nominal_core_polygon" and bad_gaps is not None and polygon_crosses_transition(bad_gaps, row, col):
                            state = "geometry_transition_unresolved"
                        state_counts[state] += 1
                        known = np.isfinite(x[row, col]) and np.isfinite(y[row, col])
                        inside = known and abs(x[row, col] - center[0]) <= 25000 + halo and abs(y[row, col] - center[1]) <= 25000 + halo
                        if inside:
                            selected_state_counts[state] += 1
                        if state != "nominal_core_polygon":
                            unresolved_records.append({"native_row": window["native_row_start"] + row,
                                "native_col": window["native_col_start"] + left + col, "native_scan": window["native_scan"],
                                "state": state, "reasons": s["reasons"] if state != "geometry_transition_unresolved" else ["adjacent_gap_ratio_outside_0.8_1.25"]})
                        if state == "nominal_core_polygon" and inside:
                            p = poly_by_key[row, col]
                            records.append({"polygon": p["polygon"], "native_row": window["native_row_start"] + row,
                                            "native_col": window["native_col_start"] + left + col,
                                            "native_scan": window["native_scan"], "detector": row})
            measured, gates = polygon_measurements(records, inverse, geod, is_modis)
            clipped = [r["polygon"].intersection(aoi) for r in records if r["polygon"].intersects(aoi)]
            full_union = unary_union([r["polygon"] for r in records])
            union = full_union.intersection(aoi)
            unions[key, halo] = union
            unclipped_unions[key, halo] = full_union
            total = sum(state_counts.values())
            accepted_count = state_counts.get("nominal_core_polygon", 0)
            hreport = {"halo_m": halo, "window_state_counts": dict(state_counts), "known_centers_inside_halo_state_counts": dict(selected_state_counts),
                       "window_geometry_unresolved_fraction": None if not total else 1 - accepted_count / total,
                       "measured_CORE_polygons": len(records), "spacing_transition_diagnostics": dict(jump_counts),
                       "unresolved_native_records": unresolved_records,
                       "metrics": {name: stats(values) for name, values in measured.items()}, "engineering_gates": gates,
                       "area_sum_unclipped_m2": float(sum(r["polygon"].area for r in records)),
                       "area_sum_individually_clipped_m2": float(sum(p.area for p in clipped)),
                       "area_union_unclipped_m2": float(full_union.area),
                       "area_union_clipped_m2": float(union.area),
                       "overlap_excess_clipped_m2": float(sum(p.area for p in clipped) - union.area),
                       "union_idempotent": bool(union.union(union).equals(union)),
                       "strata_diagnostics": grouped_stats(records, measured)}
            product_report["halos"][str(halo)] = hreport
            print(key, halo, "CORE", len(records), "gates", gates, flush=True)
        difference = unions[key, 10000].symmetric_difference(unions[key, 15000]).area
        product_report["halo_stability"] = {"symmetric_difference_m2": float(difference), "normalized_by_AOI": float(difference / aoi.area),
                                             "threshold": 1e-6, "passed": bool(difference / aoi.area <= 1e-6)}
        available = product_report["halo_stability"]["passed"] and all(all(h["engineering_gates"].values()) and bool(h["engineering_gates"]) and h["union_idempotent"] for h in product_report["halos"].values())
        product_report["available_engineering_checks_passed"] = bool(available)
        product_report["nominal_geometry_consistency_passed"] = bool(available and is_modis)
        if not is_modis:
            product_report["nominal_geometry_pending_reason"] = "External I-band detector dimension/aggregation reference not verified; sampling-cell checks cannot certify DFOV"
        report["products"][key] = product_report
    for case in SOURCE_RECORDS:
        aqua, viirs = unions[case + "_MYD03", 15000], unions[case + "_VNP03IMG", 15000]
        intersection = aqua.intersection(viirs)
        sensitivities = []
        for distance in [75, 150]:
            for dx, dy in [(distance, 0), (-distance, 0), (0, distance), (0, -distance)]:
                # Translate the uncut halo proxy before clipping to avoid border loss.
                moved = translate(unclipped_unions[case + "_VNP03IMG", 15000], xoff=dx, yoff=dy).intersection(aoi)
                area = aqua.intersection(moved).area
                sensitivities.append({"dx_m": dx, "dy_m": dy, "nominal_intersection_m2": float(area),
                                      "change_from_unshifted_m2": float(area - intersection.area), "assumed_perturbation_not_confidence_interval": True})
        report["nominal_intersections"][case] = {"area_m2": float(intersection.area),
            "not_observed_or_clear_sky_coverage": True,
            "bounded_by_each_union": bool(intersection.area <= min(aqua.area, viirs.area) + 1e-6), "sensitivities": sensitivities}
    report["completed_utc"] = datetime.now(timezone.utc).isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    (OUT / "export-index.json").write_text(json.dumps(index, indent=2) + "\n")
    for source in [Path(__file__), ROOT / "pipeline/observation_mesh.py", *PROTOCOLS]:
        (OUT / (source.name + ".snapshot.txt")).write_bytes(source.read_bytes())
    manifest = {"files": {p.name: {"bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(OUT.iterdir()) if p.is_file()}}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-geolocation", action="store_true")
    args = parser.parse_args()
    if args.export_geolocation:
        result = export_geo()
        print(json.dumps({k: len(v["windows"]) for k, v in result["cases"].items()}))
    else:
        run_validation()
