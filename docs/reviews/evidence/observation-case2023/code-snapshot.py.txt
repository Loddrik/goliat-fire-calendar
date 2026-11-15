"""One metadata-selected 2023 case; no selection or pairing by fire outcomes."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import ssl
import time
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

import numpy as np

from observation_authenticated import download, safe_url, file_sha
from observation_preflight import PRODUCTS, BBOX, acquisition_key, interval_bounds, scrub_links, utc
from observation_native_qa import inventory, odl, plain, validate_shapes
from observation_geotiming import read_centers, scan_indices, valid_scan_references, nearest_centers, quantiles

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/reviews/2026-11-14-observation-case2023-protocol.md"
OUT = ROOT / "docs/reviews/evidence/observation-case2023"
RAW = ROOT / ".runtime/observation-case2023/raw"
START = "2023-02-03T00:00:00Z"
END = "2023-02-11T00:00:00Z"
PREVIOUS_BYTES = 193748806
EXTRA_CAP = 200 * 1024 ** 2
TOTAL_CAP = 400 * 1024 ** 2


def remaining_budget(spent, previous=PREVIOUS_BYTES):
    if spent < 0 or previous < 0:
        raise ValueError("Negative byte accounting")
    return max(0, min(EXTRA_CAP - spent, TOTAL_CAP - previous - spent))


def choose_pair(aqua, viirs):
    def eligible(entry):
        return entry.get("day_night_flag") == "DAY" and utc(START) <= utc(entry["time_start"]) < utc(END) and utc(entry["time_end"]) <= utc(END)
    candidates = []
    for a in aqua:
        if not eligible(a):
            continue
        for v in viirs:
            if eligible(v):
                minimum, maximum = interval_bounds(a, v)
                if maximum <= 10:
                    candidates.append({"aqua_start": a["time_start"], "viirs_start": v["time_start"],
                                       "aqua_id": a["producer_granule_id"], "viirs_id": v["producer_granule_id"],
                                       "minimum_gap_minutes": minimum, "maximum_gap_minutes": maximum})
    candidates.sort(key=lambda p: (p["aqua_start"], p["viirs_start"], p["aqua_id"], p["viirs_id"]))
    return (candidates[0] if candidates else None), candidates


def unique_geo(fire, entries):
    matches = [e for e in entries if acquisition_key(e) == acquisition_key(fire)]
    if len(matches) != 1:
        raise ValueError("Expected exactly one metadata geolocation acquisition match")
    return matches[0]


def native_url(entry):
    candidates = [e["href"] for e in entry.get("links", []) if e.get("rel", "").endswith("/data#")
                  and urlsplit(e.get("href", "")).hostname in {
                      "data.lpdaac.earthdatacloud.nasa.gov", "data.laadsdaac.earthdatacloud.nasa.gov"}]
    if not candidates:
        raise ValueError("No permitted native HTTPS data link")
    url = sorted(candidates)[0]
    if urlsplit(url).scheme != "https" or urlsplit(url).username or urlsplit(url).password:
        raise ValueError("Unsafe native link")
    return url


def query(parameters, deadline, endpoint="granules.json"):
    import certifi
    if time.time() >= deadline:
        raise TimeoutError("Case deadline")
    url = "https://cmr.earthdata.nasa.gov/search/" + endpoint + "?" + urlencode(parameters)
    with urlopen(Request(url, headers={"Accept": "application/json", "User-Agent": "GOLIAT-case2023/1"}),
                 context=ssl.create_default_context(cafile=certifi.where()), timeout=min(30, max(1, deadline - time.time()))) as response:
        return json.loads(response.read()), int(response.headers["CMR-Hits"]) if "CMR-Hits" in response.headers else None


def catalog(product, deadline):
    collection, _ = query({"concept_id": PRODUCTS[product]["concept_id"]}, deadline, "collections.json")
    entries = collection["feed"]["entry"]
    if len(entries) != 1 or entries[0]["short_name"] != product or entries[0]["version_id"] != PRODUCTS[product]["version"]:
        raise ValueError("Pinned collection identity mismatch")
    granules, expected = [], None
    for page in range(1, 11):
        payload, hits = query({"collection_concept_id": PRODUCTS[product]["concept_id"], "temporal": START + "," + END,
                               "bounding_box": BBOX, "page_size": 2000, "page_num": page, "sort_key": "start_date"}, deadline)
        batch = payload["feed"]["entry"]
        if expected is None:
            expected = hits
        if hits is not None and expected != hits:
            raise ValueError("CMR inventory changed")
        granules.extend(batch)
        if len({e["id"] for e in granules}) != len(granules):
            raise ValueError("Duplicate catalog identifier")
        if len(batch) < 2000:
            if expected is not None and len(granules) != expected:
                raise ValueError("Incomplete catalog inventory")
            return {"collection": scrub_links(collection), "granules": scrub_links(granules), "cmr_hits": expected}
    raise ValueError("Catalog pagination cap")


def inspect_case(paths):
    import h5py
    from pyhdf.SD import SD, SDC
    import pyproj
    import importlib.metadata

    transformer = pyproj.Transformer.from_crs(4326, 32718, always_xy=True)
    center = transformer.transform(-72.5, -37)
    # Validate both input pointers and all native shapes before any AOI mask counts.
    mf, mg = SD(str(paths["MYD14"]), SDC.READ), SD(str(paths["MYD03"]), SDC.READ)
    try:
        with h5py.File(paths["VNP14IMG"], "r") as vf, h5py.File(paths["VNP03IMG"], "r") as vg:
            if Path(str(mf.attributes().get("MOD03 input file", ""))).name != paths["MYD03"].name:
                raise ValueError("Exact MODIS InputPointer mismatch")
            vp = str(plain(vf.attrs.get("InputPointer", "")))
            import re
            if paths["VNP03IMG"].name not in re.findall(r"VNP03IMG\.[A-Za-z0-9_.-]+\.nc", vp):
                raise ValueError("Exact VIIRS InputPointer mismatch")
            md = [mf.select("fire mask"), mf.select("algorithm QA"), mg.select("Latitude"), mg.select("Longitude"), mg.select("gflags")]
            vd = [vf["fire mask"], vf["algorithm QA"], vg["geolocation_data/latitude"], vg["geolocation_data/longitude"], vg["geolocation_data/quality_flag"]]
            ms, vs = validate_shapes(md, 10), validate_shapes(vd, 32)
            if ms[1] != 1354 or vs[1] != 6400:
                raise ValueError("Unexpected native scan width")
            products = {"MYD14": inventory("MYD14", "061", *md, transformer, center),
                        "VNP14IMG": inventory("VNP14IMG", "002", *vd, transformer, center)}
            core = str(mf.attributes().get("CoreMetadata.0", ""))
            products["MYD14"]["global_quality"] = {"automatic_flag": odl(core, "AUTOMATICQUALITYFLAG"),
                "explanation": odl(core, "AUTOMATICQUALITYFLAGEXPLANATION"), "decision": "unresolved_global_eligibility",
                "local_candidates_conditional_only": True}
            products["VNP14IMG"]["global_quality"] = {"automatic_flag": plain(vf.attrs.get("AutomaticQualityFlag", None)),
                "decision": "not_certified_by_inventory", "local_candidates_conditional_only": True}
            a, count_a = read_centers(md[2], md[3], md[4], ms, transformer, center, 25000)
            b, count_v = read_centers(vd[2], vd[3], vd[4], vs, transformer, center, 25500)
            ma = {key: np.asarray(mg.select(key)[:]) for key in ["EV start time", "EV center time"]}
            va = {key: vg["scan_line_attributes/" + key][:] for key in ["scan_start_time", "scan_end_time", "ev_mid_time"]}
            # Exactly the same fill/order policy as the fixed technical 2019 run.
            valid_a = valid_scan_references(ma["EV start time"], ma["EV center time"], fill_values=[-2e9])
            valid_v = valid_scan_references(va["scan_start_time"], va["ev_mid_time"], end=va["scan_end_time"], fill_values=[-999.9])
            sa, sv = scan_indices(a["row"], ms, 10, len(valid_a)), scan_indices(b["row"], vs, 32, len(valid_v))
            ids, dist = nearest_centers(np.column_stack([a["x"], a["y"]]), np.column_stack([b["x"], b["y"]]), b["row"], b["col"])
            matched = np.flatnonzero(ids >= 0)
            v_ids = ids[matched]
            good = valid_a[sa[matched]] & valid_v[sv[v_ids]]
            refs = {}
            for name, mt, vt in [("center_reference", ma["EV center time"], va["ev_mid_time"]),
                                  ("start_reference", ma["EV start time"], va["scan_start_time"])]:
                delta = mt[sa[matched[good]]] - vt[sv[v_ids[good]]]
                refs[name] = {"definition": "Aqua_minus_SNPP native TAI93 scan-reference seconds; NOT pixel time",
                              "signed_seconds": quantiles(delta), "absolute_seconds": quantiles(np.abs(delta))}
            usage = Counter(int(i) for i in v_ids)
            timing = {"selection_counts": {"Aqua": count_a, "VIIRS": count_v}, "nearest_distance_m": quantiles(dist[matched]),
                      "reference_offsets": refs, "matched_Aqua_seeds": len(matched), "unmatched_Aqua_seeds": int((ids < 0).sum()),
                      "VIIRS_centers_reused": sum(v > 1 for v in usage.values()), "distinct_VIIRS_used": len(usage),
                      "matches_outside_primary_square": int((~b["primary_aoi"][v_ids]).sum()),
                      "associations_unknown_reference_time": int((~good).sum())}
            for dataset in md:
                dataset.endaccess()
    finally:
        mf.end()
        mg.end()
    return {"products": products, "geotiming": timing, "input_pointer_exact": True,
            "environment": {"packages": {k: importlib.metadata.version(k) for k in ["numpy", "h5py", "pyhdf", "pyproj", "certifi"]},
                            "proj_version": pyproj.proj_version_str}}


def run(deadline):
    import certifi
    OUT.mkdir(parents=True, exist_ok=True)
    if any(OUT.iterdir()):
        raise ValueError("Refuse existing case evidence overwrite")
    if RAW.exists() and any(RAW.iterdir()):
        raise ValueError("Refuse existing new-case raw/partial files")
    previous = sum(p.stat().st_size for p in (ROOT / ".runtime/observation-pilot/raw").iterdir() if p.is_file())
    if previous != PREVIOUS_BYTES:
        raise ValueError("Previous raw budget baseline changed")
    helpers = ["observation_authenticated.py", "observation_preflight.py", "observation_native_qa.py", "observation_geotiming.py", "observation_qa.py"]
    record = {"scope": "One metadata-selected additional case, not positive fire selection or validation",
              "started_utc": datetime.now(timezone.utc).isoformat(), "deadline_utc": datetime.fromtimestamp(deadline, timezone.utc).isoformat(),
              "previous_raw_bytes": previous, "extra_cap_bytes": EXTRA_CAP, "total_cap_bytes": TOTAL_CAP,
              "downloaded_extra_bytes_including_failures": 0, "files": {}, "protocol_sha256": file_sha(PROTOCOL),
              "code_sha256": file_sha(Path(__file__)), "helper_sha256": {h: file_sha(ROOT / "pipeline" / h) for h in helpers},
              "gate1_passed": False, "scientific_eligibility_certified": False,
              "common_footprints_verified": False, "pixel_exposure_times_verified": False,
              "all_four_acquired": False, "gate0_access_schema_passed": False}
    def save():
        (OUT / "result.json").write_text(json.dumps(record, indent=2, allow_nan=False) + "\n")
    try:
        all_entries = {}
        for product in PRODUCTS:
            data = catalog(product, deadline)
            (OUT / (product + "-catalog.json")).write_text(json.dumps(data, indent=2) + "\n")
            all_entries[product] = data["granules"]
        pair, candidates = choose_pair(all_entries["MYD14"], all_entries["VNP14IMG"])
        record.update(catalog_counts={k: len(v) for k, v in all_entries.items()}, selected_pair=pair, metadata_candidates=len(candidates))
        # Persist choice before downloading/opening any new fire file.
        (OUT / "selection.json").write_text(json.dumps({"pair": pair, "candidates": candidates, "outcomes_used": False}, indent=2) + "\n")
        save()
        if pair is None:
            record["status"] = "no_metadata_pair_no_relaxation"
        else:
            selected = {"MYD14": next(e for e in all_entries["MYD14"] if e["producer_granule_id"] == pair["aqua_id"]),
                        "VNP14IMG": next(e for e in all_entries["VNP14IMG"] if e["producer_granule_id"] == pair["viirs_id"])}
            selected["MYD03"] = unique_geo(selected["MYD14"], all_entries["MYD03"])
            selected["VNP03IMG"] = unique_geo(selected["VNP14IMG"], all_entries["VNP03IMG"])
            token = (ROOT / ".runtime/secrets/earthdata-token").read_text().strip()
            if not token:
                raise ValueError("Configured credential unavailable")
            os.environ["SSL_CERT_FILE"] = certifi.where()
            for product in ["MYD14", "MYD03", "VNP14IMG", "VNP03IMG"]:
                entry = selected[product]
                result, spent = download(native_url(entry), RAW / entry["producer_granule_id"], token,
                                         remaining_budget(record["downloaded_extra_bytes_including_failures"], previous), deadline)
                record["files"][product] = result
                record["downloaded_extra_bytes_including_failures"] += spent
                save()
                if result.get("status") not in {"downloaded", "existing_file"}:
                    record["status"] = "fixed_candidate_acquisition_failed_no_substitution"
                    break
            if len(record["files"]) == 4 and all(v.get("status") in {"downloaded", "existing_file"} for v in record["files"].values()):
                paths = {k: ROOT / v["file"] for k, v in record["files"].items()}
                if any(file_sha(p) != record["files"][k]["sha256"] for k, p in paths.items()):
                    raise ValueError("Downloaded file hash mismatch")
                record["all_four_acquired"] = True
                if time.time() >= deadline:
                    raise TimeoutError("No time remaining for technical inventory")
                record["inspection"] = inspect_case(paths)
                record["gate0_access_schema_passed"] = True
                record["status"] = "technical_inventory_complete_no_G1"
    except Exception as error:
        # Never serialize exceptions: they may embed credential-bearing URLs.
        record["status"] = "failed_closed_no_substitution"
        record["error_class"] = type(error).__name__
    record["completed_utc"] = datetime.now(timezone.utc).isoformat()
    record["cumulative_transferred_raw_bytes"] = previous + record["downloaded_extra_bytes_including_failures"]
    save()
    for source, name in [(Path(__file__), "code-snapshot.py.txt"), (PROTOCOL, "protocol-snapshot.md.txt")]:
        (OUT / name).write_bytes(source.read_bytes())
    manifest = {"files": {p.name: {"bytes": p.stat().st_size, "sha256": file_sha(p)} for p in sorted(OUT.iterdir()) if p.is_file()}}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deadline-utc", required=True)
    args = parser.parse_args()
    end = utc(args.deadline_utc).timestamp()
    if end > min(time.time() + 1200, utc("2026-11-15T03:00:00Z").timestamp()):
        raise SystemExit("Deadline exceeds authorized timebox")
    result = run(end)
    print(json.dumps({k: result.get(k) for k in ["status", "catalog_counts", "selected_pair", "downloaded_extra_bytes_including_failures", "gate0_access_schema_passed", "gate1_passed"]}, indent=2))
