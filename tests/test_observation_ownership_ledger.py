import sys
import tempfile
import unittest
from pathlib import Path

from shapely.geometry import box

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from observation_ownership_ledger import assign_ownership, registered_state, write_table, read_table, math_isfinite_coordinate
from observation_native_qa import local_screen


def record(key, scan, poly):
    return {"key": key, "scan": scan, "polygon": poly}


class OwnershipTests(unittest.TestCase):
    def test_earlier_and_later_priorities_conserve_union(self):
        rows = [record((1, 1), 8, box(0, 0, 2, 2)), record((2, 1), 3, box(1, 0, 3, 2))]
        early, _, union, summary = assign_ownership(rows, {8: 10., 3: 20.})
        late, _, later_union, _ = assign_ownership(rows, {8: 10., 3: 20.}, "late")
        self.assertEqual(summary["scan_priority"], [8, 3])
        self.assertEqual([early[r["key"]].area for r in rows], [4, 2])
        self.assertEqual([late[r["key"]].area for r in rows], [2, 4])
        self.assertEqual(union.symmetric_difference(later_union).area, 0)
        self.assertEqual(union.area, 6)

    def test_unknown_scan_blocks_all_known_ownership(self):
        rows = [record((1, 1), 1, box(0, 0, 3, 2)), record((2, 1), 2, box(1, 0, 2, 2))]
        owned, unknown, union, summary = assign_ownership(rows, {1: 10., 2: None})
        self.assertIsNone(owned[(2, 1)])
        self.assertEqual(unknown[(1, 1)], 2)
        self.assertEqual(owned[(1, 1)].area, 4)
        self.assertEqual(summary["unknown_time_union_m2"], 2)
        self.assertEqual(summary["union_conservation_residual_m2"], 0)

    def test_known_empty_owner_is_zero_not_unknown(self):
        rows = [record((1, 1), 1, box(0, 0, 1, 1)), record((2, 1), 2, box(0, 0, 1, 1))]
        owned, _, _, _ = assign_ownership(rows, {1: 0., 2: 1.})
        self.assertIsNotNone(owned[(2, 1)])
        self.assertEqual(owned[(2, 1)].area, 0)

    def test_same_scan_material_overlap_is_not_repaired(self):
        rows = [record((1, 1), 1, box(0, 0, 10, 10)), record((1, 2), 1, box(5, 0, 15, 10))]
        with self.assertRaisesRegex(ValueError, "Same-scan"):
            assign_ownership(rows, {1: 0.})

    def test_adjacent_pixels_same_scan_and_empty_aoi(self):
        rows = [record((1, 1), 1, box(0, 0, 1, 1)), record((1, 2), 1, box(1, 0, 2, 1)), record((1, 3), 1, box(3, 0, 4, 1).intersection(box(0, 0, 2, 1)))]
        owned, _, union, _ = assign_ownership(rows, {1: 0.})
        self.assertEqual(union.area, 2)
        self.assertEqual(owned[(1, 3)].area, 0)

    def test_priorities_ignore_activity_and_input_order(self):
        rows = [record((1, 1), 1, box(0, 0, 2, 2)), record((2, 1), 2, box(1, 0, 3, 2))]
        first = assign_ownership(rows, {1: 10., 2: 20.})[0]
        rows.reverse()
        for r in rows: r["mask"] = 9; r["QA"] = 999
        second = assign_ownership(rows, {1: 10., 2: 20.})[0]
        self.assertEqual(first[(1, 1)].symmetric_difference(second[(1, 1)]).area, 0)

    def test_unknown_classes_and_surfaces_not_zeros(self):
        for product in ["MYD14", "VNP14IMG"]:
            for m in [7, 8, 9]: self.assertEqual(registered_state(product, m), "registered_positive")
            self.assertNotEqual(registered_state(product, 3), registered_state(product, 5))
            for m in [0, 1, 2, 4, 6]: self.assertTrue(registered_state(product, m).startswith("unknown_"))

    def test_M13_screen_exclusion_does_not_delete_registered_positive(self):
        screen = local_screen("VNP14IMG", "002", 7, 1 << 6, 0)
        self.assertEqual(screen["state"], "excluded")
        self.assertEqual(registered_state("VNP14IMG", 7), "registered_positive")

    def test_deterministic_csv_and_unknown_area_blank(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp)/"a.gz", Path(tmp)/"b.gz"
            rows = [{"area": None}, {"area": 0.}]
            write_table(a, rows);write_table(b, rows)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(read_table(a), [{"area": ""}, {"area": "0.0"}])
        self.assertFalse(math_isfinite_coordinate(float("nan"), 0))
        self.assertFalse(math_isfinite_coordinate(91, 0))


if __name__ == "__main__": unittest.main()
