import sys
import unittest
from pathlib import Path

import numpy as np
from shapely.geometry import Point, box
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from observation_mesh import build_scan_mesh, inspect_quad


def grid(rows=10, cols=6):
    r, c = np.indices((rows, cols), dtype=float)
    return c, r, np.ones((rows, cols), dtype=bool)


class ObservationMeshTests(unittest.TestCase):
    def test_affine_rotation_shear_and_reflection_have_analytic_corners(self):
        x, y, valid = grid()
        for matrix in [np.eye(2), np.array([[0, -1], [1, 0]]),
                       np.array([[2, .3], [.2, 1.5]]), np.array([[-1, 0], [0, 1]])]:
            input_points = np.stack([x, y], axis=-1) @ matrix.T + [10, -4]
            result = build_scan_mesh(input_points[..., 0], input_points[..., 1], valid, 10)
            self.assertEqual(result["counts"]["nominal_core_polygon"], 32)
            for record in result["polygons"]:
                r, c = record["row"], record["col"]
                expected = np.array([[c - .5, r - .5], [c + .5, r - .5],
                                     [c + .5, r + .5], [c - .5, r + .5]]) @ matrix.T + [10, -4]
                np.testing.assert_allclose(np.asarray(record["polygon"].exterior.coords)[:4], expected, rtol=1e-10, atol=1e-10)
                self.assertAlmostEqual(record["polygon"].area, abs(np.linalg.det(matrix)), delta=1e-10)

    def test_adjacent_polygons_reuse_identical_vertices(self):
        x, y, valid = grid()
        result = build_scan_mesh(x, y, valid, 10)
        lookup = {(r["row"], r["col"]): r["polygon"] for r in result["polygons"]}
        a, b = lookup[3, 2], lookup[3, 3]
        common = set(a.exterior.coords) & set(b.exterior.coords)
        self.assertEqual(common, {(2.5, 2.5), (2.5, 3.5)})
        self.assertEqual(a.intersection(b).area, 0)
        self.assertEqual(a.intersection(b).length, 1)

    def test_scan_edges_and_native_indices_are_not_interpolated_across_bowtie(self):
        x, y, valid = grid(rows=20)
        y[10:] -= 7  # Second scan overlaps the first spatially.
        result = build_scan_mesh(x, y, valid, 10)
        states = {(r["row"], r["col"]): r for r in result["states"]}
        self.assertEqual(states[9, 2]["state"], "geometry_edge_unresolved")
        self.assertEqual(states[10, 2]["state"], "geometry_edge_unresolved")
        self.assertEqual(states[11, 2]["scan"], 1)
        self.assertEqual(states[11, 2]["detector"], 1)
        polygons = result["polygons"]
        second = next(r["polygon"] for r in polygons if r["row"] == 11 and r["col"] == 2)
        self.assertEqual(second.bounds, (1.5, 3.5, 2.5, 4.5))
        a = unary_union([r["polygon"] for r in polygons if r["scan"] == 0])
        b = unary_union([r["polygon"] for r in polygons if r["scan"] == 1])
        self.assertGreater(a.intersection(b).area, 0)
        self.assertLess(a.union(b).area, sum(r["polygon"].area for r in polygons))

    def test_missing_and_flagged_input_propagates_without_healing(self):
        for nan_coordinate in [False, True]:
            x, y, valid = grid()
            if nan_coordinate:
                x[4, 3] = np.nan
            else:
                valid[4, 3] = False
            result = build_scan_mesh(x, y, valid, 10)
            lookup = {(r["row"], r["col"]): r for r in result["states"]}
            self.assertEqual(lookup[4, 3]["reasons"], ["native_center_input_invalid"])
            for row in range(3, 6):
                for col in range(2, 5):
                    self.assertEqual(lookup[row, col]["state"], "geometry_input_unresolved")
            self.assertEqual(sum(result["counts"].values()), 60)

    def test_smooth_quadratic_map_has_controlled_nonzero_refinement_error(self):
        errors = []
        for spacing in [1., .5]:
            u, v, valid = grid()
            u, v = u * spacing, v * spacing
            x, y = u + .01 * u ** 2, v + .02 * v ** 2
            result = build_scan_mesh(x, y, valid, 10)
            polygon = next(r["polygon"] for r in result["polygons"] if r["row"] == 3 and r["col"] == 2)
            uv = np.array([[1.5, 2.5], [2.5, 2.5], [2.5, 3.5], [1.5, 3.5]]) * spacing
            exact = np.column_stack([uv[:, 0] + .01 * uv[:, 0] ** 2,
                                     uv[:, 1] + .02 * uv[:, 1] ** 2])
            error = np.max(np.linalg.norm(np.asarray(polygon.exterior.coords)[:4] - exact, axis=1))
            self.assertGreater(error, 0)
            errors.append(error)
        self.assertAlmostEqual(errors[0] / errors[1], 4., delta=1e-10)

    def test_invalid_crossed_degenerate_and_center_outside_are_rejected(self):
        for corners, center in [([[0, 0], [1, 1], [0, 1], [1, 0]], [.5, .5]),
                                ([[0, 0], [1, 0], [2, 0], [3, 0]], [1, 0]),
                                ([[0, 0], [1, 0], [1, 1], [0, 1]], [2, 2])]:
            self.assertIsNone(inspect_quad(corners, center)["polygon"])

    def test_union_invariants_and_list_order_independence(self):
        x, y, valid = grid()
        polygons = [r["polygon"] for r in build_scan_mesh(x, y, valid, 10)["polygons"]]
        a, b = unary_union(polygons), unary_union(polygons[::-1])
        self.assertTrue(a.equals(b))
        self.assertTrue(a.union(a).equals(a))
        shifted = unary_union([p for p in polygons[4:]])
        self.assertLessEqual(a.intersection(shifted).area, min(a.area, shifted.area))

    def test_32_detector_core_and_explicit_input_validation(self):
        x, y, valid = grid(rows=64)
        result = build_scan_mesh(x, y, valid, 32)
        self.assertEqual(result["counts"]["nominal_core_polygon"], 2 * 30 * 4)
        self.assertEqual(sum(result["counts"].values()), 64 * 6)
        for rows, scan in [(11, 10), (10, 32), (10, 16)]:
            xx, yy, vv = grid(rows=rows)
            with self.assertRaises(ValueError):
                build_scan_mesh(xx, yy, vv, scan)
        with self.assertRaises(ValueError):
            build_scan_mesh(x, y, valid.astype(int), 32)
        with self.assertRaises(ValueError):
            build_scan_mesh(x, y[:, :-1], valid, 32)

    def test_halo_is_a_precondition_not_a_claim_from_centers(self):
        x, y, valid = grid()
        result = build_scan_mesh(x, y, valid, 10)
        polygon = next(r["polygon"] for r in result["polygons"] if r["row"] == 4 and r["col"] == 1)
        aoi = box(.6, 3.6, .9, 3.9)
        self.assertFalse(aoi.covers(Point(1, 4)))
        self.assertGreater(aoi.intersection(polygon).area, 0)
        meta = result["metadata"]
        for key in ["halo_verified", "physical_footprints_verified", "gate1_passed", "real_nominal_support_validated"]:
            self.assertFalse(meta[key])
        self.assertTrue(meta["nominal_approximation"])


if __name__ == "__main__":
    unittest.main()
