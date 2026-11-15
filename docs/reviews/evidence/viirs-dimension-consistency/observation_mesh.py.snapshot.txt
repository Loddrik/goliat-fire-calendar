"""Pure CORE-only nominal mesh inside native detector scans.

Metric x/y are required caller inputs; this module does not verify a CRS, read
granules, infer observations or identify physical IFOV/DFOV boundaries. Matrix
indices are retained exactly; cropped inputs require external native-index mapping.
"""
from __future__ import annotations

from collections import Counter
from numbers import Integral

import numpy as np
from shapely.geometry import Point, Polygon


def inspect_quad(corners, center):
    """Validate one proposed quadrilateral without repair or coordinate changes."""
    corners, center = np.asarray(corners, dtype=float), np.asarray(center, dtype=float)
    if corners.shape != (4, 2) or center.shape != (2,):
        raise ValueError("Expected four 2D vertices and one 2D center")
    if not np.isfinite(corners).all() or not np.isfinite(center).all():
        return {"polygon": None, "reason": "nonfinite_geometry"}
    polygon = Polygon(corners)
    if not polygon.is_valid or not polygon.exterior.is_simple:
        return {"polygon": None, "reason": "invalid_polygon_topology"}
    if not np.isfinite(polygon.area) or polygon.area <= 0:
        return {"polygon": None, "reason": "nonpositive_or_nonfinite_area"}
    if not polygon.covers(Point(center)):
        return {"polygon": None, "reason": "native_center_not_covered"}
    # A clockwise native matrix is legitimate. Record orientation, never repair.
    shifted = corners - corners[0]
    cross = np.sum(shifted[:, 0] * np.roll(shifted[:, 1], -1)
                   - shifted[:, 1] * np.roll(shifted[:, 0], -1))
    return {"polygon": polygon, "reason": None,
            "ring_orientation": "counterclockwise" if cross > 0 else "clockwise"}


def build_scan_mesh(x, y, valid, rows_per_scan):
    """Return CORE polygons, exhaustive pixel states/counts and scope metadata.

    Missing coordinates/validity invalidate every dependent vertex; neither
    interpolation across missing input nor extrapolation at boundaries occurs.
    ``valid`` must be an explicit boolean geometry-input mask, not inferred QA.
    """
    if isinstance(rows_per_scan, bool) or not isinstance(rows_per_scan, Integral) or rows_per_scan not in {10, 32}:
        raise ValueError("Only native detector scans of 10 or 32 rows are supported")
    x, y, valid = np.asarray(x), np.asarray(y), np.asarray(valid)
    if x.ndim != 2 or y.shape != x.shape or valid.shape != x.shape:
        raise ValueError("Metric x/y and explicit validity must have the same 2D shape")
    if x.dtype.kind not in "fiu" or y.dtype.kind not in "fiu" or valid.dtype.kind != "b":
        raise ValueError("Real metric coordinates and boolean validity are required")
    if not x.shape[0] or x.shape[0] % rows_per_scan or x.shape[1] < 3:
        raise ValueError("Nonempty complete native scans and at least 3 columns required")
    x, y = x.astype(float, copy=False), y.astype(float, copy=False)
    usable = valid & np.isfinite(x) & np.isfinite(y)
    states, polygons = [], []
    counts = Counter({"nominal_core_polygon": 0, "geometry_edge_unresolved": 0,
                      "geometry_input_unresolved": 0, "geometry_topology_unresolved": 0})
    for offset in range(0, x.shape[0], rows_per_scan):
        points = np.stack([x[offset:offset + rows_per_scan], y[offset:offset + rows_per_scan]], axis=-1)
        scan_valid = usable[offset:offset + rows_per_scan]
        with np.errstate(over="ignore", invalid="ignore"):
            # Divide before summing to avoid unnecessary overflow in the mean.
            vertices = points[:-1, :-1] / 4 + points[:-1, 1:] / 4 + points[1:, :-1] / 4 + points[1:, 1:] / 4
        vertex_valid = (scan_valid[:-1, :-1] & scan_valid[:-1, 1:]
                        & scan_valid[1:, :-1] & scan_valid[1:, 1:]
                        & np.isfinite(vertices).all(axis=-1))
        for detector in range(rows_per_scan):
            for col in range(x.shape[1]):
                row = offset + detector
                key = {"row": row, "col": col, "scan": offset // rows_per_scan, "detector": detector}
                reasons = []
                if detector in {0, rows_per_scan - 1} or col in {0, x.shape[1] - 1}:
                    state = "geometry_edge_unresolved"
                    reasons.append("scan_or_input_column_edge_no_extrapolation")
                    if not usable[row, col]:
                        reasons.append("native_center_input_invalid")
                elif not usable[row, col]:
                    state = "geometry_input_unresolved"
                    reasons.append("native_center_input_invalid")
                elif not vertex_valid[detector - 1:detector + 1, col - 1:col + 1].all():
                    state = "geometry_input_unresolved"
                    reasons.append("dependent_vertex_input_invalid")
                else:
                    corners = np.asarray([vertices[detector - 1, col - 1], vertices[detector - 1, col],
                                          vertices[detector, col], vertices[detector, col - 1]])
                    checked = inspect_quad(corners, points[detector, col])
                    if checked["polygon"] is None:
                        state = "geometry_topology_unresolved"
                        reasons.append(checked["reason"])
                    else:
                        state = "nominal_core_polygon"
                        polygons.append({**key, "polygon": checked["polygon"],
                                         "ring_orientation": checked["ring_orientation"]})
                states.append({**key, "state": state, "reasons": reasons})
                counts[state] += 1
    if sum(counts.values()) != x.size or len(polygons) != counts["nominal_core_polygon"]:
        raise RuntimeError("Mesh state partition failed")
    return {
        "polygons": polygons, "states": states, "counts": dict(counts),
        "metadata": {
            "input_shape": list(x.shape), "rows_per_scan": int(rows_per_scan),
            "index_convention": "Unmodified positional matrix indices; caller must preserve native mapping",
            "coordinate_requirement": "Projected metric coordinates; CRS and projection validity are caller preconditions",
            "nominal_approximation": True, "construction": "four-center mean vertices, inside each scan, CORE only",
            "edge_extrapolation": False, "cross_scan_interpolation": False, "automatic_geometry_repair": False,
            "physical_footprints_verified": False, "gate1_passed": False,
            "scientific_eligibility_certified": False, "real_nominal_support_validated": False,
            "halo_verified": False,
            "phase_b_preconditions": [
                "Native-index mapping and complete scan boundaries must be retained",
                "Halo must include polygons crossing the AOI, not only centers inside it",
                "Compare predeclared 10/15km halos; 500m is not a universal footprint halo",
                "Validate MODIS nominal dimensions by sample and ellipsoidal geometry",
                "Validate or leave pending VIIRS aggregation/dimensional reference",
                "No inference of observed/no-detection states from geometry",
            ],
        },
    }
