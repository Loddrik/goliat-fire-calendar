import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from observation_geotiming import (inside_square, nearest_centers, quantiles,
                                   read_centers, scan_indices, valid_scan_references)


class IdentityProjection:
    def transform(self, longitude, latitude):
        return longitude, latitude


class GeotimingTests(unittest.TestCase):
    def test_nearest_exact_ties_use_native_row_then_column_and_allow_reuse(self):
        a = np.array([[0, 0], [0, 0]])
        b = np.array([[1, 0], [-1, 0], [0, 1]])
        rows, cols = np.array([2, 1, 1]), np.array([0, 3, 2])
        indices, distance = nearest_centers(a, b, rows, cols)
        self.assertEqual(indices.tolist(), [2, 2])
        np.testing.assert_array_equal(distance, [1, 1])
        permutation = [2, 0, 1]
        new, _ = nearest_centers(a, b[permutation], rows[permutation], cols[permutation])
        self.assertEqual(np.array(permutation)[new].tolist(), [2, 2])

    def test_threshold_fixed_inclusive_and_no_candidates_is_valid(self):
        indices, distance = nearest_centers([[0, 0], [1000.1, 0]], [[500, 0]], [0], [0])
        self.assertEqual(indices.tolist(), [0, -1])
        self.assertTrue(np.isnan(distance[1]))
        indices, _ = nearest_centers([[0, 0]], np.empty((0, 2)), [], [])
        self.assertEqual(indices.tolist(), [-1])

    def test_primary_square_and_guard_ring_are_distinct(self):
        x = np.array([25000, 25000.1, 25500, 25500.1])
        y = np.zeros(4)
        self.assertEqual(inside_square(x, y, [0, 0]).tolist(), [True, False, False, False])
        self.assertEqual(inside_square(x, y, [0, 0], 25500).tolist(), [True, True, True, False])

    def test_scan_indices_use_native_detector_rows_and_reject_bad_shapes(self):
        self.assertEqual(scan_indices(np.array([0, 9, 10, 19]), (20, 8), 10, 2).tolist(), [0, 0, 1, 1])
        self.assertEqual(scan_indices(np.array([31, 32]), (64, 8), 32, 2).tolist(), [0, 1])
        for shape, nscans in [((21, 8), 2), ((20, 8), 3)]:
            with self.assertRaises(ValueError):
                scan_indices(np.array([0]), shape, 10, nscans)

    def test_time_fill_nan_and_invalid_order_are_unknown_not_zero(self):
        valid = valid_scan_references([0, -999, 2, 3], [.2, -999, np.nan, 2.9], fill_values=[-999])
        self.assertEqual(valid.tolist(), [True, False, False, False])
        valid = valid_scan_references([0, 1], [.2, 1.2], end=[.4, 1.1])
        self.assertEqual(valid.tolist(), [True, False])
        self.assertEqual(valid_scan_references([0, 0], [.2, .2]).tolist(), [False, False])

    def test_geographic_quality_exclusion_does_not_use_fire_information(self):
        lat = np.array([[0., 1., 2., 100., 4.]])
        lon = np.zeros((1, 5))
        flags = np.array([[0, 128, 255, 0, 0]], dtype=np.uint8)
        result, counts = read_centers(lat, lon, flags, lat.shape, IdentityProjection(), [0, 0], 10)
        self.assertEqual(result["col"].tolist(), [0, 4])
        self.assertEqual(counts["coordinate_invalid"], 1)
        self.assertEqual(counts["geo_flag_fill"], 1)
        self.assertEqual(counts["geo_flag_nonzero_nonfill"], 1)

    def test_quantiles_empty_stays_unknown(self):
        self.assertIsNone(quantiles([])["quantiles"])
        self.assertEqual(quantiles([0, 1, 2, 3, 4])["quantiles"]["0.5"], 2)


if __name__ == "__main__":
    unittest.main()
