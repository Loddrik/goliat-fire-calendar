import sys
import unittest
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon, MultiPolygon, box, LineString
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from coordinate_origin_diagnostic import translate_certified,signature,bits,evaluate

class FixedOriginTests(unittest.TestCase):
    def test_all_rings_parts_and_closures_roundtrip(self):
        p=Polygon([(700000,5900000),(700010,5900000),(700010,5900010),(700000,5900010)],holes=[[(700002,5900002),(700004,5900002),(700004,5900004),(700002,5900004)]])
        g=MultiPolygon([p,box(700020,5900000,700030,5900010)])
        out,r=translate_certified(g,[700000.25,5900000.5])
        self.assertTrue(r['passed']);self.assertEqual(r['coordinates'],len(shapely.get_coordinates(g)))
        self.assertEqual(signature(g),signature(out));self.assertEqual(r['scalar_subtractions_tested'],2*r['coordinates'])
    def test_nonexact_subtraction_is_not_dropped(self):
        g=LineString([(1.,1.),(2.,2.)]);out,r=translate_certified(g,[1e20,1e20])
        self.assertFalse(r['passed']);self.assertGreater(r['fraction_failures'],0)
        self.assertEqual(r['coordinates'],2)
    def test_signed_zero_roundtrip_must_preserve_bits(self):
        g=LineString([(-0.,0.),(1.,1.)]);out,r=translate_certified(g,[0.,0.])
        self.assertFalse(r['passed']);self.assertFalse(r['roundtrip_bits_identical'])
    def test_3D_is_rejected(self):
        out,r=translate_certified(LineString([(0,0,1),(1,1,2)]),[0,0])
        self.assertIsNone(out);self.assertFalse(r['passed'])
    def test_control_same_expressions_and_analytic_areas(self):
        item={'id':'synthetic','expected_areas_p_q_i_dp_dq_u':[100,100,50,50,50,150]}
        row,extra=evaluate(item,box(0,0,10,10),box(5,0,15,10),{})
        self.assertTrue(row['control_expected_areas_pass']);self.assertTrue(extra['all_required_pass'])
    def test_exact_integer_controls_at_large_origin(self):
        out,r=translate_certified(box(0,0,10,10),[722000.125,5900000.25])
        self.assertTrue(r['passed']);self.assertEqual(out.area,100)
    def test_one_vertex_nonfinite_rejects_whole_geometry(self):
        out,r=translate_certified(LineString([(0,0),(float('nan'),1)]),[0,0])
        self.assertIsNone(out);self.assertFalse(r['passed'])

if __name__=='__main__':unittest.main()
