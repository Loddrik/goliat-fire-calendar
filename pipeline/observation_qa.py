"""Pure, versioned inspection of documented observation fields; never passes G1.

No I/O, raw granule readers, UTC conversion, footprint inference or fire scoring.
Canonical versions refer to filename collection identifiers, not CMR aliases.
Sources and unresolved eligibility are recorded in the observation G1 design.
"""
from __future__ import annotations

import math
from numbers import Integral, Real


VERSIONS = {"MYD14": "061", "MYD03": "061", "VNP14IMG": "002", "VNP03IMG": "002"}
POLICY = "observation-inspection-conservative-v1"
SOURCES = {
    "MYD14": "https://modis-fire.umd.edu/files/MODIS_C6_C6.1_Fire_User_Guide_1.0.pdf#page=23",
    "VNP14IMG": "https://www.earthdata.nasa.gov/s3fs-public/2024-07/VIIRS_C2_AF-375m_User_Guide_1.0.pdf",
    "MYD03": "https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/61/MOD03",
    "VNP03IMG": "https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP03IMG",
}
MASKS = {
    "MYD14": {
        0: "missing_input", 1: "obsolete_not_processed", 2: "obsolete_not_processed",
        3: "water_no_detection", 4: "cloud", 5: "land_no_detection",
        6: "unknown", 7: "low_confidence_detection",
        8: "nominal_confidence_detection", 9: "high_confidence_detection",
    },
    "VNP14IMG": {
        0: "not_processed", 1: "bowtie_deleted", 2: "sun_glint",
        3: "water_no_detection", 4: "cloud", 5: "land_no_detection",
        6: "unclassified", 7: "low_confidence_detection",
        8: "nominal_confidence_detection", 9: "high_confidence_detection",
    },
}
VIIRS_BITS = {
    0: "I1_non_nominal", 1: "I2_non_nominal", 2: "I3_non_nominal",
    3: "I4_non_nominal", 4: "I5_non_nominal", 5: "geolocation_non_nominal",
    6: "M13_non_nominal", 7: "unambiguous_night_fire", 8: "background_candidate",
    9: "bright_pixel_rejection", 10: "fire_candidate", 11: "scene_background",
    12: "contextual_test_1", 13: "contextual_test_2", 14: "contextual_test_3",
    15: "contextual_test_4", 16: "saturation", 17: "glint_condition",
    18: "potential_SAA", 19: "fire_over_water", 20: "persistence_test_1",
    21: "persistence_test_2", 22: "residual_bowtie",
}


def _version(product: str, version: str, allowed: set[str]) -> None:
    if product not in allowed or VERSIONS.get(product) != version:
        raise ValueError("Unsupported product/collection; no inferred QA compatibility")


def _uint(value: int, bits: int) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ValueError("Unsigned integer required")
    if not 0 <= value < 1 << bits:
        raise ValueError("Integer outside declared unsigned field range")
    return int(value)


def decode_mask(product: str, version: str, value: int, *, fill_value: int | None = None) -> dict:
    _version(product, version, set(MASKS))
    value = _uint(value, 8)
    if fill_value is not None:
        fill_value = _uint(fill_value, 8)
    classification = MASKS[product].get(value, "unknown_class")
    return {
        "product": product, "version": version, "raw": value,
        "status": "fill" if value == fill_value else ("known" if value in MASKS[product] else "unknown"),
        "classification": classification,
        "detection": value != fill_value and value in {7, 8, 9},
        "no_detection": value != fill_value and value in {3, 5},
        "physical_fire_absence_inferred": False,
    }


def decode_algorithm_qa(product: str, version: str, value: int, *, fill_value: int | None = None) -> dict:
    _version(product, version, set(MASKS))
    value = _uint(value, 32)
    if fill_value is not None:
        fill_value = _uint(fill_value, 32)
    if value == fill_value:
        return {"product": product, "version": version, "status": "fill", "fields": {}}
    if product == "MYD14":
        fields = {
            "surface": ("water", "coast", "land", "unused")[value & 3],
            "band_22": bool(value & (1 << 2)),
            "atmospheric_correction": bool(value & (1 << 3)),
            "day_algorithm": bool(value & (1 << 4)),
            "potential_fire": bool(value & (1 << 5)),
            "background_window_parameter": (value >> 7) & 15,
            "adjacent_cloud": bool(value & (1 << 20)),
            "adjacent_water": bool(value & (1 << 21)),
            "sun_glint_level": (value >> 22) & 3,
        }
        # Individual physical test definitions are deliberately not reconstructed.
        fields["detection_test_bits"] = {bit: bool(value & (1 << bit)) for bit in range(11, 17)}
        fields["rejection_test_bits"] = {bit: bool(value & (1 << bit)) for bit in range(24, 29)}
        reserved = [6, 17, 18, 19, 29, 30, 31]
    else:
        fields = {name: bool(value & (1 << bit)) for bit, name in VIIRS_BITS.items()}
        reserved = list(range(23, 32))
    return {
        "product": product, "version": version, "status": "decoded", "raw": value,
        "fields": fields,
        "active_reserved_bits": [bit for bit in reserved if value & (1 << bit)],
    }


def decode_geolocation_qa(product: str, version: str, value: int, *, fill_value: int = 255) -> dict:
    _version(product, version, {"MYD03", "VNP03IMG"})
    value, fill_value = _uint(value, 8), _uint(fill_value, 8)
    if value == fill_value:
        return {"product": product, "version": version, "status": "fill", "policy_accepted": False}
    bits = (
        {7: "invalid_input", 6: "no_ellipsoid_intersection", 5: "invalid_terrain",
         4: "inferior_or_missing_DEM", 3: "invalid_sensor_range", 2: "near_limb"}
        if product == "MYD03" else
        {0: "input_invalid", 1: "pointing_bad", 2: "terrain_bad", 3: "solar_angle_bad"}
    )
    documented_mask = sum(1 << bit for bit in bits)
    return {
        "product": product, "version": version, "status": "decoded",
        "fields": {name: bool(value & (1 << bit)) for bit, name in bits.items()},
        "undocumented_active_bits": value & (255 ^ documented_mask),
        # Conservative design restriction, not a universal NASA QA rule.
        "policy_accepted": value == 0,
        "policy_declared": POLICY,
    }


def temporal_relation(a: tuple[float, float] | None, b: tuple[float, float] | None,
                      maximum_gap_seconds: float = 600) -> dict:
    """Classify already justified exposure intervals on the SAME time scale.

    Does not derive intervals from granule names, convert TAI93 or bound samples.
    """
    if isinstance(maximum_gap_seconds, bool) or not isinstance(maximum_gap_seconds, Real) or not math.isfinite(maximum_gap_seconds) or maximum_gap_seconds < 0:
        raise ValueError("A finite nonnegative time threshold is required")
    if a is None or b is None:
        return {"state": "time_unknown", "compatible": None}
    for interval in (a, b):
        if len(interval) != 2 or any(isinstance(v, bool) or not isinstance(v, Real) or not math.isfinite(v) for v in interval) or interval[1] < interval[0]:
            raise ValueError("Expected ordered finite exposure interval")
    minimum = max(0.0, a[0] - b[1], b[0] - a[1])
    maximum = max(abs(a[0] - b[1]), abs(a[1] - b[0]))
    compatible = True if maximum <= maximum_gap_seconds else (False if minimum > maximum_gap_seconds else None)
    return {
        "state": "within" if compatible is True else ("outside" if compatible is False else "time_uncertain"),
        "compatible": compatible, "minimum_gap_seconds": minimum, "maximum_gap_seconds": maximum,
    }


def inspect_observation(product: str, version: str, mask: int, algorithm_qa: int | None,
                        geolocation_qa: int | None, *,
                        time_compatible: bool | None = None,
                        common_support_verified: bool | None = None,
                        global_quality_flag: str = "unresolved",
                        mask_fill: int | None = None,
                        algorithm_fill: int | None = None,
                        geolocation_fill: int = 255) -> dict:
    """Conservative inspection states, not scientific eligibility certification.

    Even all declared checks passing yields a policy candidate with G1=false.
    Caller remains responsible for coordinates, scan QA, timing and footprints.
    """
    for v in (time_compatible, common_support_verified):
        if v is not None and not isinstance(v, bool):
            raise ValueError("Support/time states must be explicit booleans or unknown")
    m = decode_mask(product, version, mask, fill_value=mask_fill)
    q = None if algorithm_qa is None else decode_algorithm_qa(product, version, algorithm_qa, fill_value=algorithm_fill)
    geo_product = "MYD03" if product == "MYD14" else "VNP03IMG"
    g = None if geolocation_qa is None else decode_geolocation_qa(geo_product, version, geolocation_qa, fill_value=geolocation_fill)
    excluded, pending, cautions = [], [], []
    surface = None
    if m["status"] != "known":
        excluded.append("mask_fill_or_unknown")
    elif not (m["detection"] or m["no_detection"]):
        excluded.append(m["classification"])
    if q is None:
        pending.append("algorithm_qa_missing")
    elif q["status"] == "fill":
        excluded.append("algorithm_qa_fill")
    else:
        f = q["fields"]
        if q["active_reserved_bits"]:
            excluded.append("reserved_qa_bits_active")
        if product == "MYD14":
            surface = f["surface"]
            if surface == "unused":
                excluded.append("surface_unknown")
            if (mask == 3 and surface == "land") or (mask == 5 and surface == "water"):
                excluded.append("mask_surface_conflict")
            if f["sun_glint_level"]:
                pending.append("MODIS_glint_policy_unresolved")
            if f["adjacent_cloud"] or f["adjacent_water"]:
                cautions.append("adjacency_flag_not_automatic_rejection")
        else:
            if any(f[VIIRS_BITS[bit]] for bit in range(7)):
                excluded.append("VIIRS_input_quality_non_nominal")
            if f["residual_bowtie"]:
                excluded.append("VIIRS_residual_bowtie_policy")
            if any(f[VIIRS_BITS[bit]] for bit in range(18, 22)):
                cautions.append("VIIRS_water_SAA_persistence_review")
            # The separate VNP03IMG land_water_mask is not inferred from QA.
            surface = "water" if mask == 3 else ("land" if mask == 5 else None)
            if m["detection"]:
                pending.append("VIIRS_surface_requires_land_water_mask")
    if g is None:
        pending.append("geolocation_qa_missing")
    elif not g["policy_accepted"]:
        excluded.append("geolocation_quality_not_accepted")
    for value, name in ((time_compatible, "time"), (common_support_verified, "common_support")):
        if value is None:
            pending.append(name + "_unknown")
        elif value is False:
            excluded.append(name + "_not_compatible")
    if global_quality_flag != "Passed":
        pending.append("global_quality_" + ("suspect_quarantine" if global_quality_flag == "Suspect" else "unresolved"))
    state = "not_observable_under_policy" if excluded else ("eligibility_pending" if pending else (
        "policy_candidate_detection" if m["detection"] else "policy_candidate_observed_no_detection"))
    return {
        "inspection_state": state, "policy_declared": POLICY,
        "mask": m, "algorithm_qa": q, "geolocation_qa": g,
        "surface_inspection": surface, "exclusion_reasons": excluded,
        "pending_reasons": pending, "cautions": cautions,
        "physical_fire_absence_inferred": False, "gate1_passed": False,
        "scientific_eligibility_certified": False,
    }
