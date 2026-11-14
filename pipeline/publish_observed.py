"""Publish the imported, unharmonized FireChronos history under its own contract.

No dependency on GOLIAT's coefficients, gates or geography. Fails closed on
corrupt inputs or aggregates that cannot be reproduced from the selected CSVs.
"""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "observed/dist"
OUT = BASE / "data/publication"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(doc):
    return (json.dumps(doc, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode()


def grid(lon, lat):
    return (math.floor(round((lon + 180) * 1e9) / 1e7),
            math.floor(round((lat + 90) * 1e9) / 1e7))


def publish():
    manifest_bytes = (BASE / "data/history-manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    monthly = json.loads((BASE / "data/observed-monthly.json").read_text())
    groups = defaultdict(list)
    for row in monthly:
        groups[row["source_id"], row["cut"]].append(row)
    if len(manifest["communes"]) != 54 or len(groups) != 162:
        raise ValueError("Expected 54 communes and 162 platform/commune segments")
    geography = manifest["geography"]
    full_geometry = ROOT / "observed/data/processed/communes-full.geojson"
    if sha(full_geometry.read_bytes()) != geography["geometry_sha256"]:
        raise ValueError("Official geography hash mismatch")
    counts, staged = Counter(), {}
    commune_docs = []
    for commune in manifest["communes"]:
        sources = []
        for source in manifest["sources"]:
            segment = next(s for s in source["communes"] if s["cut"] == commune["cut"])
            csv_bytes = (BASE / segment["url"]).read_bytes()
            if sha(csv_bytes) != segment["sha256"] or len(csv_bytes) != segment["bytes"]:
                raise ValueError(f"CSV hash/size mismatch: {segment['url']}")
            detections, cells = Counter(), defaultdict(set)
            source_files = {f["filename"] for f in source["files"]}
            rows = list(csv.DictReader(csv_bytes.decode().splitlines()))
            if len(rows) != segment["rows"]:
                raise ValueError("Unexpected CSV row count")
            for row in rows:
                acquired = date.fromisoformat(row["acq_date"])
                cell = grid(float(row["longitude"]), float(row["latitude"]))
                assert cell == (int(row["grid_x"]), int(row["grid_y"]))
                assert row["cut_com"] == commune["cut"]
                assert row["source_file"] in source_files
                assert row["daynight"] == "D" and row["type"] == "0"
                assert row["instrument"] == source["instrument"]
                assert acquired.year in source["available_years"]
                if source["instrument"] == "MODIS":
                    assert 30 <= float(row["confidence"]) <= 100
                else:
                    assert row["confidence"].lower() in ("n", "h")
                month = row["acq_date"][:7]
                detections[month] += 1
                cells[month].add((row["acq_date"], *cell))
            series = sorted(groups[source["id"], commune["cut"]], key=lambda r: r["month"])
            expected_months = []
            y, m = map(int, source["start"].split("-"))
            while f"{y:04}-{m:02}" <= source["end"]:
                expected_months.append(f"{y:04}-{m:02}")
                m += 1
                if m == 13:
                    y, m = y + 1, 1
            if [r["month"] for r in series] != expected_months:
                raise ValueError("Duplicate or missing months")
            for row in series:
                month = row["month"]
                present = int(month[:4]) in source["available_years"]
                assert row["detections"] == (detections[month] if present else None)
                assert row["cell_days"] == (len(cells[month]) if present else None)
                assert row["observation_coverage"] == "unknown"
                counts["months_verified"] += 1
            assert sum(detections.values()) == sum(r["detections"] or 0 for r in series)
            counts["csv_verified"] += 1
            counts["detections_verified"] += len(rows)
            sources.append({
                "id": source["id"], "title": source["title"], "platform": source["platform"],
                "instrument": source["instrument"], "start": source["start"], "end": source["end"],
                "versions": source["versions"], "available_years": source["available_years"],
                "csv": {"url": "/observed/" + segment["url"], "sha256": segment["sha256"], "rows": segment["rows"]},
                "series": [{"month": r["month"], "detections": r["detections"], "cell_days": r["cell_days"],
                            "status": "missing-file" if r["cell_days"] is None else ("observed-detections" if r["cell_days"] else "no-detections-coverage-unknown"),
                            "observation_coverage": "unknown"} for r in series],
            })
        doc = {"schema_version": 1, "product": "observed-platform-history", "unit": "cell_days_per_platform",
               "harmonization": "none", "commune": commune, "sources": sources,
               "geography": geography, "grid": manifest["grid"], "filters": manifest["filters"],
               "limitations": manifest["limitations"], "source_manifest_sha256": sha(manifest_bytes)}
        payload = encode(doc)
        filename = commune["cut"] + ".json"
        staged[filename] = payload
        commune_docs.append({**commune, "url": "/observed/data/publication/" + filename, "sha256": sha(payload)})
    index = {"schema_version": 1, "product": "observed-platform-history", "unit": "cell_days_per_platform",
             "harmonization": "none", "source_commit": "d61ccf826ed3dbfd6461ad19324b0d65f9ffd4ac",
             "geography": "DPA 2023 · SUBDERE / IDE Chile", "archive_through": "2025-12",
             "source_manifest_sha256": sha(manifest_bytes), "verified": dict(counts), "communes": commune_docs}
    # Finish validating every input before replacing any published payload.
    OUT.mkdir(parents=True, exist_ok=True)
    for filename, payload in staged.items():
        (OUT / filename).write_bytes(payload)
    (OUT / "index.json").write_bytes(encode(index))
    print(json.dumps(dict(counts), indent=2))


if __name__ == "__main__":
    publish()
