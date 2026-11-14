import math
import sys
import unittest
from pathlib import Path

from shapely.geometry import Polygon,box,mapping

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from geography_experiment import GeometryAssignment,decimal_cell


def feature(cut,geometry):return {'properties':{'cut':cut},'geometry':mapping(geometry)}


class GeographySensitivityTests(unittest.TestCase):
    def test_decimal_floor_handles_negative_boundaries(self):
        self.assertEqual(decimal_cell(-72.9),-7290)
        self.assertEqual(decimal_cell(-36.85),-3685)
        self.assertEqual(decimal_cell(-72.900001),-7291)
        self.assertEqual(decimal_cell(-72.899999),-7290)
        self.assertEqual(decimal_cell(0),0)
        self.assertEqual(decimal_cell(-.000001),-1)

    def test_nonfinite_coordinates_rejected(self):
        for value in [math.nan,math.inf,-math.inf]:
            with self.assertRaises(ValueError):decimal_cell(value)

    def test_shared_edge_is_unique_and_independent_of_order(self):
        features=[feature('02',box(.005,0,.015,.01)),feature('01',box(-.005,0,.005,.01))]
        for ordered in [features,features[::-1]]:
            assign=GeometryAssignment(ordered,True)
            self.assertEqual(assign.assign((0,0)),('01','shared-edge-min-cut'))
        self.assertEqual(GeometryAssignment(features,False).assign((0,0))[0],None)

    def test_interior_overlap_is_excluded(self):
        features=[feature('01',box(0,0,.02,.02)),feature('02',box(.001,.001,.015,.015))]
        self.assertEqual(GeometryAssignment(features,True).assign((0,0)),(None,'ambiguous-interior-overlap'))

    def test_holes_do_not_gain_detections(self):
        geometry=Polygon([(0,0),(.03,0),(.03,.03),(0,.03)],holes=[[(.001,.001),(.009,.001),(.009,.009),(.001,.009)]])
        assign=GeometryAssignment([feature('01',geometry)],True)
        self.assertEqual(assign.assign((0,0)),(None,'outside'))
        self.assertEqual(assign.assign((2,2))[0],'01')

    def test_invalid_geometry_is_not_repaired_silently(self):
        bowtie=Polygon([(0,0),(.02,.02),(0,.02),(.02,0)])
        with self.assertRaisesRegex(ValueError,'Invalid'):GeometryAssignment([feature('01',bowtie)],True)


if __name__=='__main__':unittest.main()
