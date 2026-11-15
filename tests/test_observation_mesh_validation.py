import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from observation_mesh_validation import (nominal_modis_dimensions, dimensions_at_scan_angle,
                                          dimension_gate, crop_columns, spacing_transitions,
                                          polygon_crosses_transition)


class MeshValidationTests(unittest.TestCase):
    def test_nominal_modis_formula_nadir_symmetry_units_and_positivity(self):
        scan, track = dimensions_at_scan_angle(0)
        self.assertAlmostEqual(float(scan), .0014184397 * 705 * 1000, delta=1e-8)
        self.assertAlmostEqual(float(track), float(scan), delta=1e-8)
        columns = np.arange(1354)
        a, b = nominal_modis_dimensions(columns)
        self.assertTrue(np.isfinite(a).all() and np.isfinite(b).all())
        self.assertTrue((a > 0).all() and (b > 0).all())
        np.testing.assert_allclose(a, a[::-1], rtol=1e-12)
        np.testing.assert_allclose(b, b[::-1], rtol=1e-12)
        # km²→m² happens by multiplying two lengths already converted to metres.
        self.assertAlmostEqual(float(scan * track / 1e6), (.0014184397 * 705) ** 2, delta=1e-10)

    def test_native_column_offset_must_not_restart_after_crop(self):
        full = nominal_modis_dimensions(np.arange(1354))[0]
        crop = nominal_modis_dimensions(500 + np.arange(10))[0]
        np.testing.assert_array_equal(crop, full[500:510])
        self.assertNotAlmostEqual(float(crop[0]), float(full[0]))
        for invalid in [-1, 1354, float("nan")]:
            with self.assertRaises(ValueError):
                nominal_modis_dimensions(invalid)

    def test_dimension_gate_uses_fixed_median_and_p95_not_only_mean(self):
        self.assertTrue(dimension_gate([.2] * 100))
        self.assertFalse(dimension_gate([.21] * 100))
        self.assertFalse(dimension_gate([0] * 90 + [.31] * 10))
        self.assertFalse(dimension_gate([]))
        self.assertFalse(dimension_gate([float("nan")]))

    def test_crop_keeps_full_rows_and_two_neighbor_columns_mapping(self):
        rows, cols = np.indices((10, 12), dtype=float)
        left, right = crop_columns(cols, rows, [6, 4], 1, padding=2)
        self.assertEqual((left, right), (3, 10))
        self.assertEqual(cols[:, left:right].shape[0], 10)
        self.assertEqual(left + 3, 6)
        self.assertIsNone(crop_columns(cols, rows, [100, 100], 1))

    def test_spacing_transition_is_geometric_and_marks_both_contributing_gaps(self):
        x = np.tile([0., 1., 2., 4., 6., 8.], (10, 1))
        y = np.repeat(np.arange(10.)[:, None], 6, axis=1)
        bad, report = spacing_transitions(x, y, np.ones_like(x, dtype=bool))
        self.assertEqual(report["flagged_adjacent_gap_ratios"], 10)
        self.assertTrue(bad[:, 1:3].all())
        self.assertTrue(polygon_crosses_transition(bad, 4, 2))
        self.assertFalse(polygon_crosses_transition(bad, 4, 4))
        bad, report = spacing_transitions(np.tile(np.arange(6.), (10, 1)), y, np.ones_like(x, dtype=bool))
        self.assertFalse(bad.any())
        self.assertEqual(report["flagged_adjacent_gap_ratios"], 0)

    def test_halo_symmetric_difference_detects_equal_area_shift(self):
        from shapely.geometry import box
        a, b = box(0, 0, 10, 10), box(1, 0, 11, 10)
        self.assertEqual(a.area, b.area)
        self.assertGreater(a.symmetric_difference(b).area, 0)

    def test_translation_happens_before_clipping(self):
        from shapely.geometry import box
        from shapely.affinity import translate
        aoi, halo_union = box(0, 0, 10, 10), box(-5, -5, 15, 15)
        self.assertEqual(translate(halo_union, xoff=1).intersection(aoi).area, 100)
        self.assertEqual(translate(halo_union.intersection(aoi), xoff=1).intersection(aoi).area, 90)


if __name__ == "__main__":
    unittest.main()
