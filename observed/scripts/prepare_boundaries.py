"""Normaliza la DPA oficial, conservando geometría completa y procedencia."""
import hashlib
import json
import shutil
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import shapefile
from pyproj import CRS, Transformer
from shapely import transform
from shapely.geometry import mapping, shape
from shapely.validation import explain_validity

ROOT = Path(__file__).resolve().parents[1]


def prepare():
    provenance = json.loads((ROOT / "reports/boundaries-download.json").read_text())
    if provenance["status"] != "downloaded":
        raise ValueError("No existe descarga DPA verificada")
    source = ROOT / provenance["local_path"]
    directory = ROOT / "data/processed/dpa-source"
    directory.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as archive:
        for member in archive.infolist():
            if member.filename.startswith("COMUNAS/") and Path(member.filename).suffix in (".shp", ".shx", ".dbf", ".prj", ".cpg"):
                target = directory / Path(member.filename).name
                if not target.exists() or target.stat().st_size != member.file_size:
                    with archive.open(member) as stream, target.open("wb") as output:
                        shutil.copyfileobj(stream, output, 1024 * 1024)
    prj = (directory / "COMUNAS_v1.prj").read_text()
    source_crs = CRS.from_wkt(prj)
    transformer = Transformer.from_crs(source_crs, "EPSG:4326", always_xy=True)
    reader = shapefile.Reader(str(directory / "COMUNAS_v1.shp"), encoding="utf-8")
    expected = {"CUT_REG", "CUT_COM", "COMUNA", "REGION"}
    if not expected.issubset({field[0] for field in reader.fields[1:]}):
        raise ValueError("Campos DPA inesperados")
    features, invalid = [], []
    for index in range(len(reader)):
        record = reader.record(index).as_dict()
        region = str(record["CUT_REG"]).strip().zfill(2)
        if region not in ("08", "16"):
            continue
        cut = str(record["CUT_COM"]).strip().zfill(5)
        if not cut.isdigit() or len(cut) != 5 or not cut.startswith(region):
            raise ValueError(f"CUT inconsistente: {cut}, región {region}")
        geometry = transform(shape(reader.shape(index).__geo_interface__), transformer.transform, interleaved=False)
        if geometry.is_empty or not geometry.is_valid or geometry.geom_type not in ("Polygon", "MultiPolygon"):
            invalid.append({"cut": cut, "reason": explain_validity(geometry)})
            continue
        representative = geometry.representative_point()
        features.append({"type": "Feature", "properties": {
            "cut": cut, "name": record["COMUNA"].strip(), "region_cut": region,
            "region": record["REGION"].strip(), "bbox": list(geometry.bounds),
            "representative_point": [representative.x, representative.y]},
            "geometry": mapping(geometry)})
    features.sort(key=lambda row: row["properties"]["cut"])
    counts = Counter(row["properties"]["region_cut"] for row in features)
    if invalid or counts != {"08": 33, "16": 21}:
        raise ValueError(f"DPA no habilitada: conteos={dict(counts)}, inválidos={invalid}")
    if len({row["properties"]["cut"] for row in features}) != len(features):
        raise ValueError("CUT duplicados")
    collection = {"type": "FeatureCollection", "features": features}
    encoded = json.dumps(collection, ensure_ascii=False, separators=(",", ":")).encode()
    output = ROOT / "data/processed/communes-full.geojson"
    output.write_bytes(encoded)
    operation = transformer.get_last_used_operation()
    metadata = {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
                "source": provenance, "source_crs_wkt": prj, "target_crs": "EPSG:4326",
                "transformation": operation.description, "transformation_accuracy_metres": operation.accuracy,
                "geometry_sha256": hashlib.sha256(encoded).hexdigest(),
                "geometry_bytes": len(encoded), "commune_count": len(features),
                "regions": dict(counts), "invalid_geometries": invalid,
                "retrospective_geography": "Fixed DPA 2023 used for all observation years; not historical boundaries",
                "assignment_rule": "0.01-degree cell centre; shared edge lowest CUT; interior overlaps excluded",
                "communes": [row["properties"] for row in features]}
    (ROOT / "reports/boundaries.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
    (ROOT / "dist/data/communes.json").write_text(json.dumps(metadata, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps({"communes": len(features), "regions": dict(counts), "geometry_bytes": len(encoded),
                      "transformation": operation.description}, ensure_ascii=False), flush=True)
    return metadata


if __name__ == "__main__":
    prepare()
