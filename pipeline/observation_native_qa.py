"""Native per-product QA inventory; never associates fire classifications.

All counts refer to native pixel centers, not area or comparable observations.
The frozen protocol controls the existing four files and the exact projected AOI.
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
import re

import numpy as np

from observation_qa import decode_algorithm_qa, decode_geolocation_qa, decode_mask

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/reviews/2026-11-14-observation-native-qa-protocol.md"
EVIDENCE = ROOT / "docs/reviews/evidence/observation-native-qa"
ACQUISITION = ROOT / "docs/reviews/evidence/observation-authenticated/acquisition.json"


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
        return plain(value.tolist())
    if isinstance(value, np.generic):
        return plain(value.item())
    if isinstance(value, (list, tuple)):
        return [plain(x) for x in value]
    if isinstance(value, dict):
        return {key: plain(x) for key, x in value.items()}
    return value


def field_attrs(dataset):
    attrs = dataset.attrs if hasattr(dataset, "attrs") else dataset.attributes()
    return {k: plain(attrs[k]) for k in ["_FillValue", "valid_range", "units", "legend", "flag_masks", "flag_meanings"] if k in attrs}


def fill_value(attrs):
    if "_FillValue" not in attrs:
        return None
    value = np.asarray(attrs["_FillValue"]).reshape(-1)
    if len(value) != 1:
        raise ValueError("Non-scalar fill definition")
    return int(value[0])


def shape_of(dataset):
    return tuple(dataset.shape if hasattr(dataset, "shape") else dataset.info()[2])


def validate_shapes(datasets, rows_per_scan):
    shapes = [shape_of(x) for x in datasets]
    if not shapes or len(shapes[0]) != 2 or any(s != shapes[0] for s in shapes) or shapes[0][0] % rows_per_scan:
        raise ValueError("Native shape/scan alignment mismatch; resampling forbidden")
    return shapes[0]


def local_screen(product, version, mask, qa, geo, *, mask_fill=None, qa_fill=None, geo_fill=255):
    """Screen only supplied local fields; deliberately no global/time argument."""
    m = decode_mask(product, version, mask, fill_value=mask_fill)
    q = decode_algorithm_qa(product, version, qa, fill_value=qa_fill)
    g = decode_geolocation_qa("MYD03" if product == "MYD14" else "VNP03IMG", version, geo, fill_value=geo_fill)
    excluded, unresolved, cautions = [], [], []
    if m["status"] != "known":
        excluded.append("mask_fill_or_unknown")
    elif not (m["detection"] or m["no_detection"]):
        excluded.append(m["classification"])
    if not g["policy_accepted"]:
        excluded.append("geolocation_policy_not_accepted")
    surface = "unknown"
    if q["status"] == "fill":
        excluded.append("algorithm_qa_fill")
    elif q["active_reserved_bits"]:
        excluded.append("algorithm_qa_reserved_active")
    if q["status"] != "fill":
        f = q["fields"]
        if product == "MYD14":
            surface = f["surface"]
            if surface == "unused":
                excluded.append("surface_unused")
            if (mask == 3 and surface == "land") or (mask == 5 and surface == "water"):
                excluded.append("mask_surface_conflict")
            if f["sun_glint_level"] != 0:
                unresolved.append("glint_policy_unresolved")
        else:
            if any(f[k] for k in ["I1_non_nominal", "I2_non_nominal", "I3_non_nominal", "I4_non_nominal", "I5_non_nominal", "geolocation_non_nominal", "M13_non_nominal"]):
                excluded.append("input_quality_non_nominal")
            if f["residual_bowtie"]:
                excluded.append("residual_bowtie_policy")
            surface = "water_mask_class3" if mask == 3 else ("land_mask_class5" if mask == 5 else "unknown")
            if m["detection"]:
                surface = "detection_surface_unknown"
                cautions.append("requires_separate_land_water_mask")
    return {
        "state": "excluded" if excluded else ("unresolved" if unresolved else "local_candidate"),
        "surface": surface, "excluded": excluded, "unresolved": unresolved,
        "cautions": cautions, "mask": m, "qa": q, "geo": g,
    }


def inventory(product, version, mask, qa, lat, lon, geo, transformer, center):
    shape = validate_shapes([mask, qa, lat, lon, geo], 10 if product == "MYD14" else 32)
    for dataset, expected in [(mask, np.uint8), (qa, np.uint32), (geo, np.uint8)]:
        if np.asarray(dataset[0:1, 0:1]).dtype != np.dtype(expected):
            raise ValueError("Native mask/QA storage dtype incompatible with documented layout")
    attrs = {key: field_attrs(value) for key, value in [("mask", mask), ("algorithm_qa", qa), ("geolocation_qa", geo)]}
    mf, qf, gf = fill_value(attrs["mask"]), fill_value(attrs["algorithm_qa"]), fill_value(attrs["geolocation_qa"])
    if gf is None:
        gf = 255  # Documented product geolocation fill, absent attribute is explicit.
    counters = {key: Counter() for key in ["partition", "mask_partition", "mask_classes", "qa_partition", "qa_active_bits",
                                           "geo_partition", "geo_flags_raw", "surface_states", "local_screen_states",
                                           "local_exclusion_reasons", "local_unresolved_reasons", "local_cautions",
                                           "local_candidate_mask_classes", "local_candidate_surfaces",
                                           "qa_surface", "qa_glint", "qa_day_algorithm"]}
    counters["mask_partition"].update({"known": 0, "fill": 0, "unknown": 0})
    counters["qa_partition"].update({"decoded_no_reserved": 0, "reserved_bits_active": 0, "fill": 0, "unknown_layout": 0})
    for value in range(10):
        counters["mask_classes"][str(value) + ":" + decode_mask(product, version, value)["classification"]] = 0
    n_total = int(np.prod(shape))
    for row in range(0, shape[0], 128):
        end = min(row + 128, shape[0])
        la, lo = np.asarray(lat[row:end, :]), np.asarray(lon[row:end, :])
        valid_coords = np.isfinite(la) & np.isfinite(lo) & (la >= -90) & (la <= 90) & (lo >= -180) & (lo <= 180)
        counters["partition"]["unassignable_invalid_coordinates"] += int((~valid_coords).sum())
        x, y = transformer.transform(lo[valid_coords], la[valid_coords])
        x, y = np.asarray(x), np.asarray(y)
        projected = np.isfinite(x) & np.isfinite(y)
        inside = projected & (np.abs(x - center[0]) <= 25000) & (np.abs(y - center[1]) <= 25000)
        counters["partition"]["unassignable_projection"] += int((~projected).sum())
        counters["partition"]["outside_aoi"] += int((projected & ~inside).sum())
        counters["partition"]["inside_aoi"] += int(inside.sum())
        if not inside.any():
            continue
        # Select by coordinates, never by fire mask or geographic quality flags.
        native_rows, native_cols = np.nonzero(valid_coords)
        native_selection = np.zeros(la.shape, dtype=bool)
        native_selection[native_rows[inside], native_cols[inside]] = True
        mm, qq, gg = [np.asarray(d[row:end, :])[native_selection] for d in [mask, qa, geo]]
        for mv, qv, gv in zip(mm, qq, gg):
            r = local_screen(product, version, mv, qv, gv, mask_fill=mf, qa_fill=qf, geo_fill=gf)
            m, q, g = r["mask"], r["qa"], r["geo"]
            counters["mask_partition"][m["status"]] += 1
            if m["status"] == "known":
                counters["mask_classes"][str(int(mv)) + ":" + m["classification"]] += 1
            qp = "fill" if q["status"] == "fill" else ("reserved_bits_active" if q["active_reserved_bits"] else "decoded_no_reserved")
            counters["qa_partition"][qp] += 1
            if q["status"] != "fill":
                for bit in range(32):
                    if int(qv) & (1 << bit):
                        counters["qa_active_bits"][str(bit)] += 1
                if product == "MYD14":
                    counters["qa_surface"][q["fields"]["surface"]] += 1
                    counters["qa_glint"][str(q["fields"]["sun_glint_level"])] += 1
                    counters["qa_day_algorithm"][str(q["fields"]["day_algorithm"])] += 1
            gp = "fill" if g["status"] == "fill" else ("zero" if g["policy_accepted"] else (
                "undocumented_active_bits" if g["undocumented_active_bits"] else "documented_active_bits"))
            counters["geo_partition"][gp] += 1
            counters["geo_flags_raw"][str(int(gv))] += 1
            counters["surface_states"][r["surface"]] += 1
            counters["local_screen_states"][r["state"]] += 1
            for key in ["excluded", "unresolved", "cautions"]:
                target = {"excluded": "local_exclusion_reasons", "unresolved": "local_unresolved_reasons", "cautions": "local_cautions"}[key]
                counters[target].update(r[key])
            if r["state"] == "local_candidate":
                counters["local_candidate_mask_classes"][str(int(mv))] += 1
                counters["local_candidate_surfaces"][r["surface"]] += 1
    inside_n = counters["partition"]["inside_aoi"]
    if sum(counters["partition"].values()) != n_total:
        raise ValueError("Granule localization partition failed to reconcile")
    for key in ["mask_partition", "qa_partition", "geo_partition", "surface_states", "local_screen_states"]:
        if sum(counters[key].values()) != inside_n:
            raise ValueError("AOI exhaustive partition failed: " + key)
    if sum(counters["mask_classes"].values()) != counters["mask_partition"]["known"]:
        raise ValueError("Known mask classes do not reconcile")
    if sum(counters["local_candidate_mask_classes"].values()) != counters["local_screen_states"]["local_candidate"]:
        raise ValueError("Local candidates do not reconcile")
    return {"native_shape": list(shape), "native_pixel_count": n_total, "field_attributes": attrs,
            "effective_fill_values": {"mask": mf, "algorithm_qa": qf, "geolocation_qa": gf},
            "counts": {k: dict(v) for k, v in counters.items()}, "all_exhaustive_partitions_reconciled": True,
            "nonexclusive_counters": ["qa_active_bits", "local_exclusion_reasons", "local_unresolved_reasons", "local_cautions"],
            "qa_unknown_layout_count": 0,
            "qa_unknown_layout_note": "Supported uint32 layout; out-of-range or unsupported collections raise, reserved bits kept separate"}


def odl(text, key):
    match = re.search(r"OBJECT\s*=\s*" + re.escape(key) + r"\s.*?VALUE\s*=\s*\"([^\"\n]+)\"", text, re.S)
    return match.group(1) if match else None


def run(output_dir=EVIDENCE):
    import h5py
    from pyhdf.SD import SD, SDC
    import pyproj

    output_dir = Path(output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("Refuse evidence overwrite")
    acq = json.loads(ACQUISITION.read_text())
    paths = {key: ROOT / acq["files"][key]["file"] for key in ["MYD14", "MYD03", "VNP14IMG", "VNP03IMG"]}
    hashes = {k: sha_file(p) for k, p in paths.items()}
    if any(hashes[k] != acq["files"][k]["sha256"] for k in paths):
        raise ValueError("Authenticated hash mismatch")
    for key, p in paths.items():
        expected = ".061." if key in {"MYD14", "MYD03"} else ".002."
        if not p.name.startswith(key + ".A2019003.") or expected not in p.name:
            raise ValueError("Pinned native product/date/collection mismatch")
    transformer = pyproj.Transformer.from_crs(4326, 32718, always_xy=True)
    center = transformer.transform(-72.5, -37)
    report = {"scope": "Independent native-center counts by product; no paired fire outcomes or concordance",
              "started_utc": datetime.now(timezone.utc).isoformat(), "input_sha256": hashes,
              "protocol_sha256": sha_file(PROTOCOL), "code_sha256": sha_file(__file__),
              "decoder_sha256": sha_file(ROOT / "pipeline/observation_qa.py"),
              "aoi": {"epsg": 32718, "center_lonlat": [-72.5, -37], "center_xy": list(center), "half_side_m": 25000},
              "products": {}, "gate1_passed": False, "common_footprints_verified": False,
              "pixel_exposure_times_verified": False, "scientific_eligibility_certified": False,
              "environment": {"python": platform.python_version(), "platform": platform.platform(),
                              "packages": {k: importlib.metadata.version(k) for k in ["numpy", "h5py", "pyhdf", "pyproj"]},
                              "proj_version": pyproj.proj_version_str}}
    fire, geo = SD(str(paths["MYD14"]), SDC.READ), SD(str(paths["MYD03"]), SDC.READ)
    try:
        attrs = fire.attributes()
        if Path(str(attrs.get("MOD03 input file", ""))).name != paths["MYD03"].name:
            raise ValueError("Exact MODIS geolocation input pointer mismatch")
        datasets = [fire.select("fire mask"), fire.select("algorithm QA"), geo.select("Latitude"), geo.select("Longitude"), geo.select("gflags")]
        if validate_shapes(datasets, 10) != (2030, 1354):
            raise ValueError("Pinned Aqua granule dimensions changed")
        report["products"]["MYD14"] = inventory("MYD14", "061", *datasets, transformer, center)
        core = str(attrs.get("CoreMetadata.0", ""))
        report["products"]["MYD14"]["global_quality"] = {
            "automatic_flag": odl(core, "AUTOMATICQUALITYFLAG"),
            "explanation": odl(core, "AUTOMATICQUALITYFLAGEXPLANATION"),
            "decision": "quarantined_pending_global_eligibility",
            "local_screen_is_conditional_only": True,
        }
        for d in datasets:
            d.endaccess()
    finally:
        fire.end()
        geo.end()
    with h5py.File(paths["VNP14IMG"], "r") as fire, h5py.File(paths["VNP03IMG"], "r") as geo:
        pointer = str(plain(fire.attrs.get("InputPointer", "")))
        if paths["VNP03IMG"].name not in re.findall(r"VNP03IMG\.[A-Za-z0-9_.-]+\.nc", pointer):
            raise ValueError("Exact VIIRS geolocation input pointer mismatch")
        datasets = [fire["fire mask"], fire["algorithm QA"], geo["geolocation_data/latitude"], geo["geolocation_data/longitude"], geo["geolocation_data/quality_flag"]]
        if validate_shapes(datasets, 32) != (6464, 6400):
            raise ValueError("Pinned VIIRS granule dimensions changed")
        report["products"]["VNP14IMG"] = inventory("VNP14IMG", "002", *datasets, transformer, center)
        report["products"]["VNP14IMG"]["global_quality"] = {
            "automatic_flag": plain(fire.attrs.get("AutomaticQualityFlag", None)),
            "decision": "not_certified_by_this_inventory", "local_screen_is_conditional_only": True,
        }
    report["completed_utc"] = datetime.now(timezone.utc).isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "counts.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    for source, name in [(Path(__file__), "code-snapshot.py.txt"), (PROTOCOL, "protocol-snapshot.md.txt"),
                         (ROOT / "pipeline/observation_qa.py", "decoder-snapshot.py.txt")]:
        (output_dir / name).write_bytes(source.read_bytes())
    (output_dir / "environment.json").write_text(json.dumps(report["environment"], indent=2) + "\n")
    manifest = {"files": {p.name: {"bytes": p.stat().st_size, "sha256": sha_file(p)} for p in sorted(output_dir.iterdir()) if p.is_file()}}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=EVIDENCE)
    args = parser.parse_args()
    result = run(args.output_dir)
    print(json.dumps({k: v["counts"] for k, v in result["products"].items()}, indent=2))
