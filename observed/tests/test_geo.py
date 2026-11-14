import sys
import unittest
from pathlib import Path

from shapely.geometry import Polygon, box

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from geo import CanonicalAssignment, cell_center, cell_of


class GeographyTests(unittest.TestCase):
    def test_float_boundary_and_grid_origin(self):
        self.assertEqual(cell_of(-72.5, -36.5), cell_of(-72.50000000000001, -36.5))
        self.assertNotEqual(cell_of(-72.5, -36.5), cell_of(-72.49, -36.5))
        self.assertAlmostEqual(cell_center(cell_of(-72.5, -36.5))[0], -72.495)

    def test_shared_cell_unique_across_records(self):
        assignment = CanonicalAssignment([{"cut": "08101", "geometry": box(-73, -37, -72, -36)}])
        first = assignment.assign_cell(cell_of(-72.51, -36.51))
        second = assignment.assign_cell(cell_of(-72.511, -36.511))
        self.assertEqual(first, second)
        self.assertEqual(first[0], "08101")

    def test_hole_is_not_part_of_commune(self):
        geometry = Polygon([(-73, -37), (-72, -37), (-72, -36), (-73, -36)],
                           holes=[[(-72.8, -36.8), (-72.2, -36.8), (-72.2, -36.2), (-72.8, -36.2)]])
        assignment = CanonicalAssignment([{"cut": "08101", "geometry": geometry}])
        self.assertEqual(assignment.assign_cell(cell_of(-72.5, -36.5))[1], "outside")

    def test_interior_overlaps_are_not_silently_assigned(self):
        assignment = CanonicalAssignment([{"cut": "08101", "geometry": box(-73, -37, -72, -36)},
                                          {"cut": "08102", "geometry": box(-72.8, -36.8, -72.2, -36.2)}])
        self.assertEqual(assignment.assign_cell(cell_of(-72.5, -36.5)), (None, "ambiguous-interior-overlap"))

    def test_assignment_uses_cell_centre_not_each_detection_point(self):
        assignment = CanonicalAssignment([{"cut": "08101", "geometry": box(-73, -37, -72.497, -36)},
                                          {"cut": "08102", "geometry": box(-72.497, -37, -72, -36)}])
        a = assignment.assign_cell(cell_of(-72.499, -36.5))
        b = assignment.assign_cell(cell_of(-72.491, -36.5))
        self.assertEqual(a[0], "08102")
        self.assertEqual(a, b)

    def test_invalid_coordinates_rejected(self):
        for longitude, latitude in [(float("nan"), -36), (-72, 100), (180, 0)]:
            with self.assertRaises(ValueError):
                cell_of(longitude, latitude)

    def test_shared_edge_has_lowest_cut_independent_of_feature_order(self):
        cell = cell_of(-72.5, -36.5)
        x, _ = cell_center(cell)
        features = [{"cut": "08102", "geometry": box(x, -37, -72, -36)},
                    {"cut": "08101", "geometry": box(-73, -37, x, -36)}]
        self.assertEqual(CanonicalAssignment(features).assign_cell(cell), ("08101", "shared-edge-min-cut"))


if __name__ == "__main__":
    unittest.main()
