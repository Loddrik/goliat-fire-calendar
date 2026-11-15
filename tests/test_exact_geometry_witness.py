import struct
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from exact_geometry_witness import parse_wkb,strict_inside,segment_distance_squared,dyadic_square,find_witness,Budget,LimitReached,compare_area

def ring(x0,y0,x1,y1):return tuple((F(x),F(y)) for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)])
def polygon(*rings,endian='<'):
 return struct.pack('B',1 if endian=='<' else 0)+struct.pack(endian+'II',3,len(rings))+b''.join(struct.pack(endian+'I',len(r))+b''.join(struct.pack(endian+'dd',float(x),float(y)) for x,y in r) for r in rings)

class ExactWitnessTests(unittest.TestCase):
 def test_parser_both_endians_and_multi(self):
  r=ring(0,0,10,10)
  for endian in ['<','>']:self.assertEqual(parse_wkb(polygon(r,endian=endian)),((r,),))
  p=polygon(r);multi=struct.pack('<BII',1,6,2)+p+p
  self.assertEqual(len(parse_wkb(multi)),2)
 def test_parser_rejects_trailing_truncated_3d_nonfinite_open(self):
  p=polygon(ring(0,0,10,10))
  for b in [p+b'x',p[:-1],struct.pack('<BI',1,1003),polygon(((0,0),(1,0),(1,1),(0,1))),polygon(((0,0),(1,0),(float('nan'),1),(0,0)))]:
   with self.assertRaises(ValueError):parse_wkb(b)
 def test_inside_hole_boundary_vertices_horizontal_orientation(self):
  exterior=ring(0,0,10,10);hole=ring(4,4,6,6);p=((exterior,hole),)
  for c,expected in [((2,2),True),((5,5),False),((4,5),False),((0,0),False),((5,0),False),((11,2),False)]:
   c=tuple(map(F,c));self.assertEqual(strict_inside(c,p)[0],expected)
   self.assertEqual(strict_inside(c,((tuple(reversed(exterior)),tuple(reversed(hole))),))[0],expected)
 def test_union_and_other_component_boundary_is_conservatively_rejected(self):
  p=((ring(0,0,10,10),),(ring(4,4,6,6),))
  self.assertTrue(strict_inside((F(5),F(5)),p)[0]);self.assertFalse(strict_inside((F(4),F(5)),p)[0])
 def test_exact_segment_distances(self):
  a=(F(0),F(0));b=(F(2),F(0))
  self.assertEqual(segment_distance_squared((F(1),F(3)),a,b),9)
  self.assertEqual(segment_distance_squared((F(-1),F(3)),a,b),10)
  self.assertEqual(segment_distance_squared((F(3),F(3)),a,b),10)
  self.assertEqual(segment_distance_squared((F(1),F(3)),a,a),10)
 def test_dyadic_strict_boundary_and_rational_center(self):
  r=dyadic_square((F(1,3),F(1,7)),F(2))
  self.assertEqual(r['k'],1);self.assertEqual(r['h'],dict(numerator=1,denominator=2));self.assertEqual(r['lower_area_m2'],dict(numerator=1,denominator=1))
  self.assertIsNone(dyadic_square((F(0),F(0)),F(1,2**600)))
 def test_square_witness_and_no_witness_not_no_overlap(self):
  p=((ring(0,0,10,10),),);r=find_witness(p,p)
  self.assertEqual(r['status'],'certified_witness');self.assertEqual(r['candidate_index'],0)
  self.assertEqual(r['square']['lower_area_m2'],dict(numerator=4,denominator=1))
  q=((ring(20,0,30,10),),);r=find_witness(p,q)
  self.assertEqual(r['status'],'no_witness_in_fixed_search');self.assertTrue(r['does_not_prove_no_overlap'])
 def test_hole_mean_rejected_then_first_valid_seed(self):
  p=((ring(0,0,10,10),ring(4,4,6,6)),);r=find_witness(p,p)
  self.assertFalse(r['attempts'][0]['strict_inside_p']);self.assertGreater(r['candidate_index'],0)
 def test_concave_mean_not_assumed_inside(self):
  r=tuple((F(x),F(y)) for x,y in [(0,0),(6,0),(6,1),(1,1),(1,6),(0,6),(0,0)])
  z=find_witness(((r,),),((r,),));self.assertFalse(z['attempts'][0]['strict_inside_p'])
 def test_global_budget_not_reset(self):
  b=Budget(max_segments=1)
  with self.assertRaises(LimitReached):strict_inside((F(1),F(1)),((ring(0,0,2,2),),),b)
  self.assertEqual(b.segments,1)
  with self.assertRaises(LimitReached):parse_wkb(polygon(ring(0,0,1,1)),Budget(max_coordinates=4))
 def test_area_lower_refutes_only(self):
  self.assertEqual(compare_area(.001,F(1))['status'],'refuted_below_exact_lower_bound')
  self.assertEqual(compare_area(2,F(1))['status'],'not_refuted_NOT_validated')
  self.assertEqual(compare_area(None,F(1))['status'],'not_comparable')
 def test_128_candidates_fixed_limit(self):
  p=tuple((ring(3*i,0,3*i+1,1),) for i in range(50));q=((ring(0,20,1,21),),)
  z=find_witness(p,q);self.assertEqual(len(z['attempts']),128);self.assertTrue(z['search_truncated'])

if __name__=='__main__':unittest.main()
