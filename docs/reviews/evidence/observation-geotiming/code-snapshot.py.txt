"""Frozen technical inventory: two geolocation files, no fire-product I/O.

Distances associate centers, never footprints. Offsets compare stored scan
references, never exact pixel times or conservative exposure intervals.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/reviews/2026-11-14-observation-geotiming-protocol.md"
EVIDENCE = ROOT / "docs/reviews/evidence/observation-geotiming"
ACQUISITION = ROOT / "docs/reviews/evidence/observation-authenticated/acquisition.json"
PREVIOUS = ROOT / "docs/reviews/evidence/observation-authenticated/inspection.json"
MAX_DISTANCE_M = 500.0
HALF_SIDE_M = 25000.0


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def plain(value):
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def attrs_selected(attrs):
    return {key: plain(attrs[key]) for key in ["units", "long_name", "_FillValue", "valid_range", "flag_masks", "flag_meanings"] if key in attrs}


def scan_indices(rows, shape, rows_per_scan, number_of_scans):
    if len(shape) != 2 or shape[0] % rows_per_scan or shape[0] // rows_per_scan != number_of_scans:
        raise ValueError("Incompatible row/scan dimensions")
    rows = np.asarray(rows)
    if np.any(rows < 0) or np.any(rows >= shape[0]) or not np.issubdtype(rows.dtype, np.integer):
        raise ValueError("Invalid native row indices")
    return rows // rows_per_scan


def inside_square(x, y, center, half_side=HALF_SIDE_M):
    return (np.abs(x - center[0]) <= half_side) & (np.abs(y - center[1]) <= half_side)


def valid_scan_references(start, center, *, end=None, fill_values=()):
    start, center = np.asarray(start), np.asarray(center)
    if start.ndim != 1 or center.shape != start.shape:
        raise ValueError("Scan reference shape mismatch")
    valid = np.isfinite(start) & np.isfinite(center) & (center >= start)
    for fill in fill_values:
        valid &= (start != fill) & (center != fill)
    if end is not None:
        end = np.asarray(end)
        if end.shape != start.shape:
            raise ValueError("Scan ending shape mismatch")
        valid &= np.isfinite(end) & (end >= center)
        for fill in fill_values:
            valid &= end != fill
    # A nonincreasing sequence makes both adjacent scan references unknown.
    for values in [start, center] + ([] if end is None else [end]):
        bad = np.flatnonzero(valid[:-1] & valid[1:] & np.isfinite(np.diff(values)) & (np.diff(values) <= 0))
        valid[bad] = False
        valid[bad + 1] = False
    return valid


def nearest_centers(a_xy, v_xy, v_rows, v_cols, max_distance=MAX_DISTANCE_M):
    """One nearest candidate per Aqua seed; exact ties prefer row then column."""
    a_xy, v_xy = np.asarray(a_xy, dtype=float), np.asarray(v_xy, dtype=float)
    v_rows, v_cols = np.asarray(v_rows), np.asarray(v_cols)
    if a_xy.ndim != 2 or v_xy.ndim != 2 or a_xy.shape[1] != 2 or v_xy.shape[1] != 2:
        raise ValueError("Expected Nx2 center arrays")
    if len(v_xy) != len(v_rows) or len(v_xy) != len(v_cols):
        raise ValueError("Candidate indices mismatch")
    if not np.all(np.isfinite(a_xy)) or not np.all(np.isfinite(v_xy)) or not np.isfinite(max_distance) or max_distance < 0:
        raise ValueError("Expected finite centers and nonnegative distance")
    indices = np.full(len(a_xy), -1, dtype=np.int64)
    distances = np.full(len(a_xy), np.nan)
    if not len(v_xy):
        return indices, distances
    order = np.lexsort((v_cols, v_rows))
    sorted_xy = v_xy[order]
    for offset in range(0, len(a_xy), 128):
        block = a_xy[offset:offset + 128]
        squared = (block[:, None, 0] - sorted_xy[None, :, 0]) ** 2
        squared += (block[:, None, 1] - sorted_xy[None, :, 1]) ** 2
        nearest = np.argmin(squared, axis=1)
        best = squared[np.arange(len(block)), nearest]
        good = best <= max_distance ** 2
        ids = np.arange(offset, offset + len(block))[good]
        indices[ids] = order[nearest[good]]
        distances[ids] = np.sqrt(best[good])
    return indices, distances


def quantiles(values):
    values = np.asarray(values)
    values = values[np.isfinite(values)]
    return {"count": int(len(values)), "quantiles": None if not len(values) else {
        str(q): float(v) for q, v in zip([0, .25, .5, .75, 1], np.quantile(values, [0, .25, .5, .75, 1]))}}


def read_centers(lat, lon, flags, shape, transformer, center, half_side):
    if tuple(lon.shape if hasattr(lon, "shape") else lon.info()[2]) != tuple(shape) or tuple(flags.shape if hasattr(flags, "shape") else flags.info()[2]) != tuple(shape):
        raise ValueError("Geolocation fields must share native dimensions")
    counts = Counter()
    stored = {key: [] for key in ["row", "col", "x", "y", "primary_aoi"]}
    for row in range(0, shape[0], 128):
        end = min(row + 128, shape[0])
        la, lo, qa = np.asarray(lat[row:end, :]), np.asarray(lon[row:end, :]), np.asarray(flags[row:end, :])
        coordinates_valid = np.isfinite(la) & np.isfinite(lo) & (la >= -90) & (la <= 90) & (lo >= -180) & (lo <= 180)
        counts["native_centers_total"] += la.size
        counts["coordinate_invalid"] += int((~coordinates_valid).sum())
        counts["geo_flag_fill"] += int((qa == 255).sum())
        counts["geo_flag_nonzero_nonfill"] += int(((qa != 0) & (qa != 255)).sum())
        usable = coordinates_valid & (qa == 0)
        local_rows, cols = np.nonzero(usable)
        x, y = transformer.transform(lo[usable], la[usable])
        x, y = np.asarray(x), np.asarray(y)
        projected_valid = np.isfinite(x) & np.isfinite(y)
        counts["projection_invalid_among_valid_coordinates_geo0"] += int((~projected_valid).sum())
        selected = projected_valid & inside_square(x, y, center, half_side)
        counts["geo0_centers_selected"] += int(selected.sum())
        for key, val in {"row": row + local_rows[selected], "col": cols[selected],
                         "x": x[selected], "y": y[selected],
                         "primary_aoi": inside_square(x[selected], y[selected], center)}.items():
            stored[key].append(val)
    arrays = {key: np.concatenate(value) for key, value in stored.items()}
    return arrays, dict(counts)


def run(output_dir=EVIDENCE):
    import h5py
    from pyhdf.SD import SD, SDC
    import pyproj

    output_dir = Path(output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("Refuse to overwrite an existing evidence run")
    acq = json.loads(ACQUISITION.read_text())
    paths = {key: ROOT / acq["files"][key]["file"] for key in ["MYD03", "VNP03IMG"]}
    hashes = {key: sha_file(value) for key, value in paths.items()}
    if any(hashes[key] != acq["files"][key]["sha256"] for key in paths):
        raise ValueError("Geolocation input hash mismatch")
    previous = json.loads(PREVIOUS.read_text())
    transformer = pyproj.Transformer.from_crs(4326, 32718, always_xy=True)
    center = transformer.transform(-72.5, -37)
    result = {
        "scope": "Technical center associations and scan-reference offsets only; no fire outcomes",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_sha256": sha_file(PROTOCOL), "code_sha256": sha_file(__file__),
        "input_sha256": hashes, "input_bytes": {k: p.stat().st_size for k, p in paths.items()},
        "opened_products": ["MYD03", "VNP03IMG"],
        "environment": {"python": platform.python_version(), "platform": platform.platform(),
                        "packages": {k: importlib.metadata.version(k) for k in ["numpy", "h5py", "pyhdf", "pyproj"]},
                        "proj_version": pyproj.proj_version_str},
        "aoi": {"epsg": 32718, "center_lonlat": [-72.5, -37], "center_xy": list(center),
                "half_side_m": HALF_SIDE_M, "VIIRS_guard_m": MAX_DISTANCE_M},
        "geo_policy": "coordinates finite/in range and geolocation QA exactly0; declared conservative policy",
        "global_quality_flag_inherited": previous["platforms"]["Aqua"]["automatic_quality_flag"],
        "inherited_quality_metadata_sha256": sha_file(PREVIOUS),
        "global_quality_quarantined": True, "gate1_passed": False,
        "scientific_eligibility_certified": False, "common_footprints_verified": False,
        "pixel_exposure_times_verified": False,
    }
    m = SD(str(paths["MYD03"]), SDC.READ)
    try:
        lat, lon, flags = [m.select(k) for k in ["Latitude", "Longitude", "gflags"]]
        mshape = tuple(lat.info()[2])
        a, count_a = read_centers(lat, lon, flags, mshape, transformer, center, HALF_SIDE_M)
        time_a, attr_a = {}, {}
        for name in ["EV start time", "EV center time"]:
            dataset = m.select(name)
            time_a[name], attr_a[name] = np.asarray(dataset[:]), attrs_selected(dataset.attributes())
            dataset.endaccess()
        for dataset in [lat, lon, flags]:
            dataset.endaccess()
    finally:
        m.end()
    with h5py.File(paths["VNP03IMG"], "r") as v:
        lat, lon, flags = [v["geolocation_data/" + k] for k in ["latitude", "longitude", "quality_flag"]]
        vshape = tuple(lat.shape)
        b, count_v = read_centers(lat, lon, flags, vshape, transformer, center, HALF_SIDE_M + MAX_DISTANCE_M)
        time_v = {k: v["scan_line_attributes/" + k][:] for k in ["scan_start_time", "scan_end_time", "ev_mid_time"]}
        attr_v = {k: attrs_selected(v["scan_line_attributes/" + k].attrs) for k in time_v}
    scan_a = scan_indices(a["row"], mshape, 10, len(time_a["EV start time"]))
    scan_v = scan_indices(b["row"], vshape, 32, len(time_v["scan_start_time"]))
    fills_a = [float(np.asarray(x["_FillValue"]).reshape(-1)[0]) for x in attr_a.values() if "_FillValue" in x]
    fills_v = [float(np.asarray(x["_FillValue"]).reshape(-1)[0]) for x in attr_v.values() if "_FillValue" in x]
    valid_a = valid_scan_references(time_a["EV start time"], time_a["EV center time"], fill_values=fills_a)
    valid_v = valid_scan_references(time_v["scan_start_time"], time_v["ev_mid_time"], end=time_v["scan_end_time"], fill_values=fills_v)
    index, distance = nearest_centers(np.column_stack([a["x"], a["y"]]), np.column_stack([b["x"], b["y"]]), b["row"], b["col"])
    matched = np.flatnonzero(index >= 0)
    viirs_id = index[matched]
    good_time = valid_a[scan_a[matched]] & valid_v[scan_v[viirs_id]]
    offsets = {}
    for label, ta, tv in [("center_reference", time_a["EV center time"], time_v["ev_mid_time"]),
                          ("start_reference", time_a["EV start time"], time_v["scan_start_time"])]:
        signed = ta[scan_a[matched[good_time]]] - tv[scan_v[viirs_id[good_time]]]
        offsets[label] = {"definition": "Aqua_minus_SNPP native TAI93 seconds; not pixel acquisition time",
                          "signed_seconds": quantiles(signed), "absolute_seconds": quantiles(np.abs(signed))}
    reused = Counter(int(i) for i in viirs_id)
    result.update(
        native_shapes={"MYD03": list(mshape), "VNP03IMG": list(vshape)},
        scan_counts={"MYD03": len(valid_a), "VNP03IMG": len(valid_v)},
        native_field_attributes={"MYD03": attr_a, "VNP03IMG": attr_v},
        selection_counts={"Aqua": count_a, "VIIRS": count_v},
        association_counts={"Aqua_seeds": len(a["row"]), "VIIRS_candidates": len(b["row"]),
                            "matched_Aqua_seeds": len(matched), "unmatched_Aqua_seeds": int((index < 0).sum()),
                            "matched_VIIRS_outside_primary_square": int((~b["primary_aoi"][viirs_id]).sum()),
                            "distinct_VIIRS_centers_used": len(reused),
                            "VIIRS_centers_reused": sum(n > 1 for n in reused.values()),
                            "associations_beyond_first_use": sum(n - 1 for n in reused.values()),
                            "associations_time_unknown": int((~good_time).sum())},
        nearest_distance_m=quantiles(distance[matched]), scan_reference_offsets=offsets,
        valid_reference_scans={"MYD03": int(valid_a.sum()), "VNP03IMG": int(valid_v.sum())},
        completed_utc=datetime.now(timezone.utc).isoformat(),
        limitations=["No fire product opened or detection class used", "No surface coverage or physical opportunity denominator",
                     "Spatial nearest centers may not share footprint", "Scan reference offsets do not bound per-pixel exposure",
                     "One quarantined candidate, not representative or independent observations"],
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for row, viirs, good in zip(matched, viirs_id, good_time):
        record = {"Aqua_row": int(a["row"][row]), "Aqua_col": int(a["col"][row]),
                  "VIIRS_row": int(b["row"][viirs]), "VIIRS_col": int(b["col"][viirs]),
                  "distance_UTM_m": float(distance[row]), "VIIRS_outside_primary_square": bool(not b["primary_aoi"][viirs]),
                  "reference_time_state": "known_scan_reference" if good else "unknown",
                  "center_reference_offset_seconds": None if not good else float(time_a["EV center time"][scan_a[row]] - time_v["ev_mid_time"][scan_v[viirs]]),
                  "start_reference_offset_seconds": None if not good else float(time_a["EV start time"][scan_a[row]] - time_v["scan_start_time"][scan_v[viirs]])}
        records.append(record)
    (output_dir / "associations.json").write_text(json.dumps(records, indent=2, allow_nan=False) + "\n")
    (output_dir / "summary.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    manifest = {"files": {p.name: {"bytes": p.stat().st_size, "sha256": sha_file(p)} for p in output_dir.iterdir() if p.is_file()}}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=EVIDENCE)
    args = parser.parse_args()
    report = run(args.output_dir)
    print(json.dumps({"association_counts": report["association_counts"], "scan_reference_offsets": report["scan_reference_offsets"], "gate1_passed": False}, indent=2))
