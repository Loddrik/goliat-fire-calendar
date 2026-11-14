"""Verifica datos reales derivados, fuentes y contrato de agregación."""
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from shapely.geometry import shape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from geo import CanonicalAssignment, cell_of


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    manifest = json.loads((ROOT / "dist/data/history-manifest.json").read_text())
    geo_path = ROOT / "data/processed/communes-full.geojson"
    assert sha(geo_path) == manifest["geography"]["geometry_sha256"]
    features = json.loads(geo_path.read_text())["features"]
    communes = [{**feature["properties"], "geometry": shape(feature["geometry"])} for feature in features]
    assert len(communes) == 54
    assert Counter(row["region_cut"] for row in communes) == {"08": 33, "16": 21}
    assignment = CanonicalAssignment(communes)
    month_counts, month_cells = Counter(), defaultdict(set)
    checks = 3
    source_counts = {}
    for source in manifest["sources"]:
        count, regional_cells, sum_commune_cells = 0, set(), 0
        source_files = {entry["filename"]: entry for entry in source["files"]}
        for filename, entry in source_files.items():
            assert sha(ROOT / "data/raw/history" / filename) == entry["sha256"]
            checks += 1
        for segment in source["communes"]:
            path = ROOT / "dist" / segment["url"]
            assert sha(path) == segment["sha256"]
            checks += 1
            local_count, local_cells = 0, set()
            with path.open(newline="") as stream:
                for row in csv.DictReader(stream):
                    assert row["cut_com"] == segment["cut"]
                    assert row["source_file"] in source_files
                    assert row["daynight"] == "D" and row["type"] == "0"
                    cell = cell_of(float(row["longitude"]), float(row["latitude"]))
                    assert cell == (int(row["grid_x"]), int(row["grid_y"]))
                    assigned, _ = assignment.assign_cell(cell)
                    assert assigned == segment["cut"]
                    key = source["id"], row["cut_com"], row["acq_date"][:7]
                    month_counts[key] += 1
                    unit = row["acq_date"], cell
                    month_cells[key].add(unit)
                    local_cells.add(unit)
                    regional_cells.add(unit)
                    local_count += 1
            assert local_count == segment["rows"]
            count += local_count
            sum_commune_cells += len(local_cells)
            checks += 1
        assert count == source["rows"]
        assert len(regional_cells) == sum_commune_cells, "El agregado duplica celdas-día entre comunas"
        source_counts[source["id"]] = {"detections": count, "unique_cell_days": len(regional_cells)}
        checks += 2
    monthly = json.loads((ROOT / "dist/data/observed-monthly.json").read_text())
    for row in monthly:
        key = row["source_id"], row["cut"], row["month"]
        assert row["detections"] == month_counts[key]
        assert row["cell_days"] == len(month_cells[key])
        assert row["observation_coverage"] == "unknown"
    checks += len(monthly)
    result = {"status": "passed", "checks": checks, "communes": len(communes), "monthly_rows": len(monthly),
              "sources": source_counts, "regional_sum_matches_unique_cell_days": True,
              "harmonization_validated": False}
    (ROOT / "reports/history-verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
