"""24B staged nominal ownership ledger; no joint fire classes/concordance."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/reviews/evidence/observation-ownership-ledger"
TEMP = ROOT / ".runtime/observation-ownership-ledger"
GEO = ROOT / ".runtime/observation-mesh-validation"
PROTOCOL = ROOT / "docs/reviews/2026-11-15-observation-ownership-ledger-protocol.md"
DEADLINE = datetime.fromisoformat("2026-11-15T05:29:28+00:00").timestamp()
SOURCES = {"2019": ROOT / "docs/reviews/evidence/observation-authenticated/acquisition.json",
           "2023": ROOT / "docs/reviews/evidence/observation-case2023/result.json"}

def check_time():
    if time.time() >= DEADLINE:
        raise TimeoutError("24B first-delivery cap")

def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def dump(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")

def write_table(path, rows, columns=None):
    rows = list(rows)
    columns = columns or sorted(set().union(*(r.keys() for r in rows)))
    with Path(path).open("wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
        with io.TextIOWrapper(zipped, encoding="utf-8", newline="") as text:
            writer = csv.DictWriter(text, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

def read_table(path):
    with gzip.open(path, "rt", newline="") as stream:
        return list(csv.DictReader(stream))

def plain(value):
    if isinstance(value, bytes): return value.decode("utf-8", "replace")
    if hasattr(value, "tolist"): return plain(value.tolist())
    if isinstance(value, (list, tuple)): return [plain(x) for x in value]
    return value

def source_paths(case):
    source = json.loads(SOURCES[case].read_text())
    return {k: (ROOT / source["files"][k]["file"], source["files"][k]["sha256"])
            for k in ["MYD14", "MYD03", "VNP14IMG", "VNP03IMG"]}

def reference_export():
    """Isolated reader: only GEO files and time fields; no FIRE file opens."""
    from pyhdf.SD import SD, SDC
    import h5py
    from observation_geotiming import valid_scan_references
    if (TEMP / "references.json").exists(): raise ValueError("References already exported")
    result = {"code_sha256": sha(__file__), "protocol_sha256": sha(PROTOCOL), "cases": {}}
    for case in SOURCES:
        result["cases"][case] = {}
        for geo, instrument in [("MYD03", "MYD14"), ("VNP03IMG", "VNP14IMG")]:
            check_time()
            path, expected = source_paths(case)[geo]
            if sha(path) != expected: raise ValueError("Pinned GEO changed")
            values, attrs = {}, {}
            if geo == "MYD03":
                f = SD(str(path), SDC.READ)
                try:
                    for key in ["EV start time", "EV center time"]:
                        d = f.select(key); values[key] = np.asarray(d[:]); attrs[key] = {k: plain(v) for k, v in d.attributes().items()};d.endaccess()
                finally: f.end()
                valid = valid_scan_references(values["EV start time"], values["EV center time"], fill_values=[-2e9])
                reference = values["EV center time"]
            else:
                with h5py.File(path, "r") as f:
                    for key in ["scan_start_time", "scan_end_time", "ev_mid_time"]:
                        d = f["scan_line_attributes/" + key]; values[key] = d[:];attrs[key] = {k: plain(v) for k,v in d.attrs.items() if k in {"units", "long_name", "_FillValue", "valid_range"}}
                valid = valid_scan_references(values["scan_start_time"], values["ev_mid_time"], end=values["scan_end_time"], fill_values=[-999.9])
                reference = values["ev_mid_time"]
            result["cases"][case][instrument] = {"GEO_sha256": expected, "scan_reference_TAI93": [float(v) if ok else None for v,ok in zip(reference,valid)],
                "fields": {k: v.tolist() for k,v in values.items()}, "attributes": attrs, "pixel_exposure_verified": False}
    dump(TEMP / "references.json", result)
    return result

def assign_ownership(records, references, priority="early", tolerance_m2=1.):
    """Pure scan ownership; never accepts activity/QA as ordering inputs."""
    from shapely.geometry import GeometryCollection
    from shapely.ops import unary_union
    by_scan = defaultdict(list)
    for r in records: by_scan[r["scan"]].append(r)
    unions = {s: unary_union([r["polygon"] for r in group]) for s,group in by_scan.items()}
    for s, group in by_scan.items():
        excess = sum(r["polygon"].area for r in group) - unions[s].area
        if abs(excess) > tolerance_m2: raise ValueError("Same-scan material overlap: ownership unidentified")
    unknown = unary_union([u for s,u in unions.items() if references.get(s) is None])
    known = [s for s in by_scan if references.get(s) is not None]
    if priority not in {"early", "late"}: raise ValueError("Unknown priority")
    known.sort(key=lambda s: ((references[s] if priority == "early" else -references[s]), s))
    claimed = GeometryCollection()
    own, unidentified = {}, {}
    for scan in known:
        available = unions[scan].difference(unknown).difference(claimed)
        for row in by_scan[scan]:
            key = row["key"]
            own[key] = row["polygon"].intersection(available)
            unidentified[key] = row["polygon"].intersection(unknown).area
        claimed = claimed.union(unions[scan].difference(unknown))
    for scan in by_scan:
        if references.get(scan) is None:
            for row in by_scan[scan]: own[row["key"]] = None;unidentified[row["key"]] = row["polygon"].area
    identified_union = unary_union([p for p in own.values() if p is not None])
    original_union = unary_union(list(unions.values()))
    residual = original_union.area - identified_union.area - unknown.area
    if abs(residual) > tolerance_m2: raise ValueError("Ownership union conservation failed")
    if abs(sum(p.area for p in own.values() if p is not None)-identified_union.area)>tolerance_m2: raise ValueError("Owned pixel areas do not reconcile")
    return own, unidentified, identified_union, {"original_union_m2": original_union.area, "unknown_time_union_m2": unknown.area,
        "identified_union_m2": identified_union.area, "union_conservation_residual_m2": residual, "scan_priority": known,
        "unknown_reference_scans": sorted(set(by_scan)-set(known))}

def registered_state(product, mask):
    from observation_qa import decode_mask
    decoded = decode_mask(product, "061" if product == "MYD14" else "002", mask)
    if decoded["detection"]: return "registered_positive"
    if decoded["no_detection"]: return decoded["classification"]
    return "unknown_" + decoded["classification"]

def geometry_stage():
    from observation_mesh import build_scan_mesh
    from observation_mesh_validation import crop_columns, spacing_transitions, polygon_crosses_transition
    from shapely.geometry import box
    if (OUT / "geometry-stage.json").exists(): raise ValueError("Geometry stage already exists")
    index = json.loads((GEO / "index.json").read_text()); refs = json.loads((TEMP / "references.json").read_text())
    bmanifest = json.loads((ROOT / "docs/reviews/evidence/observation-mesh-validation/manifest.json").read_text())
    if sha(GEO / "index.json") != bmanifest["files"]["export-index.json"]["sha256"]: raise ValueError("Unpinned GEO index")
    if refs["code_sha256"] != sha(__file__) or refs["protocol_sha256"] != sha(PROTOCOL): raise ValueError("Freeze changed")
    cx,cy = index["center_xy"];aoi=box(cx-25000,cy-25000,cx+25000,cy+25000)
    products, pending = {}, {}
    for case in SOURCES:
        for geo, instrument in [("MYD03","MYD14"),("VNP03IMG","VNP14IMG")]:
            check_time();item=index["cases"][case+"_"+geo];rows=[];states=[]
            for w in item["windows"]:
                path=GEO/w["npz"]
                if sha(path)!=w["sha256"]:raise ValueError("GEO export changed")
                with np.load(path,allow_pickle=False) as data:
                    x,y,valid=data["x"],data["y"],data["valid"];left,right=crop_columns(x,y,[cx,cy],40000)
                    x,y,valid=x[:,left:right],y[:,left:right],valid[:,left:right]
                    mesh=build_scan_mesh(x,y,valid,item["rows_per_scan"])
                    gaps=spacing_transitions(x,y,valid)[0] if geo=="VNP03IMG" else None
                    for s in mesh["states"]:
                        r,c=s["row"],s["col"];state=s["state"]
                        if state=="nominal_core_polygon" and gaps is not None and polygon_crosses_transition(gaps,r,c):state="geometry_transition_unresolved"
                        states.append({"row":w["native_row_start"]+r,"col":w["native_col_start"]+left+c,"state":state})
                    state_map={(s["row"],s["col"]):s["state"] for s in states}
                    for p in mesh["polygons"]:
                        nr,nc=w["native_row_start"]+p["row"],w["native_col_start"]+left+p["col"]
                        if state_map[nr,nc]!="nominal_core_polygon":continue
                        if abs(x[p["row"],p["col"]]-cx)>40000 or abs(y[p["row"],p["col"]]-cy)>40000:continue
                        clipped=p["polygon"].intersection(aoi)
                        # Retain known zero area for halo polygons, so original
                        # positives outside AOI are not mistaken for unknown area.
                        rows.append({"key":(nr,nc),"scan":w["native_scan"],"polygon":clipped,"full_area":p["polygon"].area,
                                     "row":nr,"col":nc,"detector":p["row"]})
            products[case,instrument]=rows;pending[case,instrument]=states
    OUT.mkdir(parents=True,exist_ok=True)
    report={"stage":"geometry persisted before FIRE masks/QA", "code_sha256":sha(__file__),"protocol_sha256":sha(PROTOCOL),
            "GEO_index_sha256":sha(GEO/"index.json"),"references_sha256":sha(TEMP/"references.json"),"center_xy":[cx,cy],"cases":{},"tables":{}}
    for case in SOURCES:
        report["cases"][case]={}
        for priority in ["early","late"]:
            assignments={}
            for instrument in ["MYD14","VNP14IMG"]:
                times=refs["cases"][case][instrument]["scan_reference_TAI93"]
                assignments[instrument]=assign_ownership(products[case,instrument],{i:v for i,v in enumerate(times)},priority)
            for instrument in ["MYD14","VNP14IMG"]:
                own,unknown,union,summary=assignments[instrument]
                other=assignments["VNP14IMG" if instrument=="MYD14" else "MYD14"][2]
                output=[];times=refs["cases"][case][instrument]["scan_reference_TAI93"]
                for p in products[case,instrument]:
                    key=p["key"];owned=own[key];common=None if owned is None else owned.intersection(other).area
                    excluded=None if owned is None else p["polygon"].area-unknown[key]-owned.area
                    noncommon=None if owned is None else owned.area-common
                    residual=None if owned is None else p["polygon"].area-unknown[key]-excluded-noncommon-common
                    if residual is not None and abs(residual)>1:raise ValueError("Pixel partition failed")
                    output.append({"case":case,"product":instrument,"priority":priority,"row":p["row"],"col":p["col"],"scan":p["scan"],"detector":p["detector"],
                        "scan_reference_TAI93":times[p["scan"]],"area_full_nominal_m2":p["full_area"],"area_AOI_m2":p["polygon"].area,
                        "area_time_unidentified_m2":unknown[key],"area_owned_m2":None if owned is None else owned.area,
                        "area_excluded_by_priority_m2":excluded,"area_owned_not_common_m2":noncommon,"area_common_m2":common,"conservation_residual_m2":residual})
                filename=f"{case}-{instrument}-{priority}-geometry.csv.gz";write_table(OUT/filename,output)
                report["tables"][filename]=sha(OUT/filename)
                report["cases"][case][instrument+"_"+priority]={**summary,"sum_pixel_AOI_m2":sum(p["polygon"].area for p in products[case,instrument]),
                    "sum_owned_m2":sum(p.area for p in own.values() if p is not None),"common_nominal_union_m2":union.intersection(other).area,
                    "pixels":len(output),"nominal_area_does_not_locate_subpixel_fire":True}
        for instrument in ["MYD14","VNP14IMG"]:
            filename=f"{case}-{instrument}-geometry-states.csv.gz";write_table(OUT/filename,pending[case,instrument]);report["tables"][filename]=sha(OUT/filename)
    dump(OUT/"geometry-stage.json",report)
    return report

def raw_stage():
    """Export each instrument independently, only after geometry is frozen."""
    from pyhdf.SD import SD,SDC
    import h5py
    from pyproj import Transformer
    from observation_native_qa import local_screen, odl
    if (TEMP/"raw-stage.json").exists():raise ValueError("Raw stage already exported")
    geometry=json.loads((OUT/"geometry-stage.json").read_text())
    if geometry["code_sha256"]!=sha(__file__) or geometry["protocol_sha256"]!=sha(PROTOCOL):raise ValueError("Geometry freeze changed")
    for name,expected in geometry["tables"].items():
        if sha(OUT/name)!=expected:raise ValueError("Geometry ledger changed before QA")
    transform=Transformer.from_crs(4326,32718,always_xy=True);cx,cy=geometry["center_xy"]
    result={"geometry_stage_sha256":sha(OUT/"geometry-stage.json"),"code_sha256":sha(__file__),"cases":{}}
    for case in SOURCES:
        result["cases"][case]={}
        for product,geo,rps in [("MYD14","MYD03",10),("VNP14IMG","VNP03IMG",32)]:
            check_time();paths=source_paths(case)
            for name in [product,geo]:
                if sha(paths[name][0])!=paths[name][1]:raise ValueError("Raw input changed")
            targets={(int(r["row"]),int(r["col"])) for r in read_table(OUT/f"{case}-{product}-early-geometry.csv.gz")}
            labels,positives=[],[]
            if product=="MYD14":
                f=SD(str(paths[product][0]),SDC.READ);g=SD(str(paths[geo][0]),SDC.READ)
                attrs=f.attributes();pointer=Path(str(attrs.get("MOD03 input file",""))).name
                if pointer!=paths[geo][0].name:raise ValueError("MODIS InputPointer mismatch")
                fields=[f.select("fire mask"),f.select("algorithm QA"),g.select("Latitude"),g.select("Longitude"),g.select("gflags")]
                shape=tuple(fields[0].info()[2]);global_flag=odl(str(attrs.get("CoreMetadata.0","")),"AUTOMATICQUALITYFLAG")
                description=odl(str(attrs.get("CoreMetadata.0","")),"AUTOMATICQUALITYFLAGEXPLANATION");surface_field=None
            else:
                f=h5py.File(paths[product][0],"r");g=h5py.File(paths[geo][0],"r")
                pointer=plain(f.attrs.get("InputPointer",""))
                if paths[geo][0].name not in str(pointer):raise ValueError("VIIRS InputPointer mismatch")
                fields=[f["fire mask"],f["algorithm QA"],g["geolocation_data/latitude"],g["geolocation_data/longitude"],g["geolocation_data/quality_flag"]]
                shape=tuple(fields[0].shape);global_flag=plain(f.attrs.get("AutomaticQualityFlag",None));description=None
                surface_field=g.get("geolocation_data/land_water_mask")
            try:
                shapes=[tuple(d.shape) if hasattr(d,"shape") else tuple(d.info()[2]) for d in fields]
                if any(s!=shape for s in shapes) or shape[0]%rps:raise ValueError("Raw native shape mismatch")
                for row in range(0,shape[0],128):
                    check_time();end=min(row+128,shape[0]);mask=np.asarray(fields[0][row:end,:]);qa=np.asarray(fields[1][row:end,:])
                    positive=np.isin(mask,[7,8,9]);selected=positive.copy()
                    for nr,nc in targets:
                        if row<=nr<end:selected[nr-row,nc]=True
                    if not selected.any():continue
                    lat,lon,flags=[np.asarray(d[row:end,:]) for d in fields[2:]]
                    land=None if surface_field is None else np.asarray(surface_field[row:end,:])
                    for r,c in zip(*np.nonzero(selected)):
                        nr,nc=row+int(r),int(c);m,q,gq=int(mask[r,c]),int(qa[r,c]),int(flags[r,c])
                        screen=local_screen(product,"061" if product=="MYD14" else "002",m,q,gq)
                        la,lo=float(lat[r,c]),float(lon[r,c]);good=math_isfinite_coordinate(la,lo)
                        if good:
                            x,y=transform.transform(lo,la);scope="centre_AOI" if abs(x-cx)<=25000 and abs(y-cy)<=25000 else ("centre_halo15" if abs(x-cx)<=40000 and abs(y-cy)<=40000 else "outside_halo15")
                        else:scope="geographically_unassignable"
                        surface=screen["surface"]
                        if land is not None:
                            l=int(land[r,c]);surface="land" if l==1 else ("coast" if l==2 else ("water" if l in {0,3,4,5,6,7} else "unknown"))
                        record={"case":case,"product":product,"row":nr,"col":nc,"mask_class":m,"algorithm_QA":q,"geographic_flag":gq,
                            "registered_state":registered_state(product,m),"surface":surface,"scope":scope,"latitude":la if good else None,"longitude":lo if good else None,
                            "screen_sensitivity_state":screen["state"],"screen_exclusion_reasons":"|".join(screen["excluded"]),
                            "screen_unresolved_reasons":"|".join(screen["unresolved"]),"M13_non_nominal":bool(q&(1<<6)) if product=="VNP14IMG" else False,
                            "positive_original_preserved":bool(m in {7,8,9}),"positive_despite_screen_exclusion":bool(m in {7,8,9} and screen["state"]!="local_candidate")}
                        if (nr,nc) in targets:labels.append(record)
                        if positive[r,c]:positives.append(record)
            finally:
                if product=="MYD14":
                    for d in fields:d.endaccess()
                    f.end();g.end()
                else:f.close();g.close()
            if len(labels)!=len(targets):raise ValueError("Missing native labels for geometry ledger")
            write_table(TEMP/f"{case}-{product}-labels.csv.gz",labels)
            positive_columns=list(labels[0]) if labels else ["case","product","row","col","mask_class","registered_state","scope"]
            write_table(TEMP/f"{case}-{product}-all-positive-originals.csv.gz",positives,positive_columns)
            result["cases"][case][product]={"input_sha256":{n:paths[n][1] for n in [product,geo]},"shape":list(shape),"labels":len(labels),
                "original_positive_records_granule":len(positives),"global_quality_flag":global_flag,"global_explanation":description,
                "scientific_eligibility":"pending_global_quality_and_exposure","labels_sha256":sha(TEMP/f"{case}-{product}-labels.csv.gz"),
                "positives_sha256":sha(TEMP/f"{case}-{product}-all-positive-originals.csv.gz")}
    dump(TEMP/"raw-stage.json",result);return result

def math_isfinite_coordinate(latitude,longitude):
    return bool(np.isfinite(latitude) and np.isfinite(longitude) and abs(latitude)<=90 and abs(longitude)<=180)

def join_stage():
    geom=json.loads((OUT/"geometry-stage.json").read_text());raw=json.loads((TEMP/"raw-stage.json").read_text())
    if raw["geometry_stage_sha256"]!=sha(OUT/"geometry-stage.json") or raw["code_sha256"]!=sha(__file__):raise ValueError("Stage freeze changed")
    result={"scope":"Independent nominal ownership/retention ledgers; no paired activity states or concordance", "code_sha256":sha(__file__),"protocol_sha256":sha(PROTOCOL),
        "geometry_stage_sha256":sha(OUT/"geometry-stage.json"),"raw_stage_sha256":sha(TEMP/"raw-stage.json"),"cases":{},
        "gate1_passed":False,"physical_footprints_verified":False,"pixel_exposure_times_verified":False,"scientific_eligibility_certified":False}
    for case in SOURCES:
        result["cases"][case]={}
        for product in ["MYD14","VNP14IMG"]:
            info=raw["cases"][case][product];label_path=TEMP/f"{case}-{product}-labels.csv.gz";pos_path=TEMP/f"{case}-{product}-all-positive-originals.csv.gz"
            if sha(label_path)!=info["labels_sha256"] or sha(pos_path)!=info["positives_sha256"]:raise ValueError("Native export changed")
            labels={(int(r["row"]),int(r["col"])):r for r in read_table(label_path)};positive=read_table(pos_path)
            state_map={(int(r["row"]),int(r["col"])):r["state"] for r in read_table(OUT/f"{case}-{product}-geometry-states.csv.gz")}
            report={"raw_metadata":info,"priorities":{}}
            for priority in ["early","late"]:
                check_time();path=OUT/f"{case}-{product}-{priority}-geometry.csv.gz"
                if sha(path)!=geom["tables"][path.name]:raise ValueError("Geometry table changed after QA")
                rows=read_table(path);by_key={};counts=Counter();areas=defaultdict(float)
                for row in rows:
                    key=int(row["row"]),int(row["col"]);row.update(labels[key]);by_key[key]=row
                    counts[row["registered_state"]]+=1
                    for field in ["area_AOI_m2","area_owned_m2","area_common_m2","area_time_unidentified_m2"]:
                        if row[field]!="":areas[row["registered_state"]+":"+field]+=float(row[field])
                write_table(OUT/f"{case}-{product}-{priority}-ledger.csv.gz",rows)
                positive_rows=[]
                for p in positive:
                    key=int(p["row"]),int(p["col"])
                    if key in by_key:p={**p,**by_key[key],"positive_geometry_state":"nominal_CORE"}
                    else:
                        p={**p,"priority":priority,"positive_geometry_state":state_map.get(key,"outside_exported_geometry_domain"),
                           **{field:None for field in ["area_full_nominal_m2","area_AOI_m2","area_owned_m2","area_common_m2","area_time_unidentified_m2","area_excluded_by_priority_m2","area_owned_not_common_m2"]}}
                    positive_rows.append(p)
                write_table(OUT/f"{case}-{product}-{priority}-positive-originals.csv.gz",positive_rows,list(rows[0])+["positive_geometry_state"])
                report["priorities"][priority]={"ledger_rows":len(rows),"registered_states":dict(counts),"area_by_registered_state_m2":dict(areas),
                    "positive_originals_preserved":len(positive_rows),"positive_scopes":dict(Counter(p["scope"] for p in positive_rows)),
                    "positive_geometry_states":dict(Counter(p["positive_geometry_state"] for p in positive_rows)),
                    "positive_scope_geometry":dict(Counter(p["scope"]+":"+p["positive_geometry_state"] for p in positive_rows)),
                    "original_positives_with_M13_non_nominal":sum(p["M13_non_nominal"]=="True" for p in positive_rows)}
            result["cases"][case][product]=report
    dump(OUT/"summary.json",result)
    for source,name in [(Path(__file__),"code.snapshot.py.txt"),(PROTOCOL,"protocol.snapshot.md.txt"),(TEMP/"references.json","references.json"),(TEMP/"raw-stage.json","raw-stage.json")]:
        (OUT/name).write_bytes(source.read_bytes())
    dump(OUT/"manifest.json",{"files":{p.name:{"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(OUT.iterdir()) if p.is_file()}})
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("stage",choices=["references","geometry","raw","join"]);args=parser.parse_args()
    check_time();result={"references":reference_export,"geometry":geometry_stage,"raw":raw_stage,"join":join_stage}[args.stage]()
    print(json.dumps({"stage":args.stage,"completed":True,"gate1_passed":False}))
