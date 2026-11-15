import sys
import unittest
import struct
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from exact_local_overlay_audit import Budget,DomainUnknown,ResourceLimit,certify_polygon,parse_operand,adjudicate,clip,intersect_segments

def poly(points):return tuple((F(x),F(y)) for x,y in points)
def box(x0,y0,x1,y1):return poly([(x0,y0),(x1,y0),(x1,y1),(x0,y1)])
def value(r):return F(r['area_exact_m2']['numerator'],r['area_exact_m2']['denominator'])
def wkb(v,kind=3,rings=1):return struct.pack('<BIII',1,kind,rings,len(v)+1)+b''.join(struct.pack('<dd',float(x),float(y)) for x,y in v+v[:1])

class ExactLocalTests(unittest.TestCase):
 def test_analytic_controls_both_orders(self):
  p=box(0,0,10,10)
  for q,expected in [(box(20,0,30,10),0),(box(2,2,4,4),4),(box(5,0,15,10),50),(box(10,0,20,10),0),(p,100)]:
   r=adjudicate(p,q);self.assertEqual(value(r),expected);self.assertTrue(r['both_orders_exactly_equal'])
 def test_clockwise_and_collinear_forward_preserve_area(self):
  p=poly([(0,0),(5,0),(10,0),(10,10),(0,10)])
  r=adjudicate(tuple(reversed(p)),box(0,0,10,10));self.assertEqual(value(r),100)
 def test_rational_triangle_intersection(self):
  p=poly([(0,0),(2,0),(0,2)]);q=box(1,0,2,2)
  self.assertEqual(value(adjudicate(p,q)),F(1,2))
 def test_point_touch_has_zero_area(self):
  self.assertEqual(value(adjudicate(box(0,0,1,1),box(1,1,2,2))),0)
 def test_concave_and_degenerate_and_duplicate_unknown(self):
  for p in [poly([(0,0),(3,0),(1,1),(3,3),(0,3)]),poly([(0,0),(1,0),(2,0)]),poly([(0,0),(1,0),(1,1),(0,0)])]:
   with self.assertRaises(DomainUnknown):certify_polygon(p)
 def test_nonadjacent_crossing_nonzero_area_is_rejected(self):
  p=poly([(0,0),(4,4),(0,3),(4,0),(5,2)])
  with self.assertRaisesRegex(DomainUnknown,'nonadjacent'):certify_polygon(p)
 def test_backtracking_unknown_no_repair(self):
  p=poly([(0,0),(2,0),(1,0),(2,2),(0,2)])
  with self.assertRaisesRegex(DomainUnknown,'backtracking'):certify_polygon(p)
 def test_segment_touch_and_collinear_overlap(self):
  b=Budget();self.assertTrue(intersect_segments((F(0),F(0)),(F(2),F(0)),(F(1),F(0)),(F(3),F(0)),b))
  self.assertFalse(intersect_segments((F(0),F(0)),(F(1),F(0)),(F(2),F(0)),(F(3),F(0)),b))
 def test_parser_polygon_and_reject_holes_multi_dimension_truncation(self):
  p=box(0,0,1,1);v,c=parse_operand(wkb(p),Budget());self.assertEqual(v,p)
  for b in [wkb(p,rings=2),wkb(p,kind=6),wkb(p,kind=1003),wkb(p)[:-1],wkb(p)+b'x']:
   with self.assertRaises((DomainUnknown,ValueError)):parse_operand(b,Budget())
 def test_vertex_bits_operations_limits_pure(self):
  with self.assertRaises(DomainUnknown):certify_polygon(tuple((F(i),F(i*i)) for i in range(257)))
  with self.assertRaises(ResourceLimit):Budget(max_bits=8).guard(F(256))
  with self.assertRaises(ResourceLimit):adjudicate(box(0,0,2,2),box(1,1,3,3),Budget(max_operations=1))
  with self.assertRaises(ResourceLimit):Budget(max_vertices=1).vertices([1,2])
 def test_bitlimit_applies_to_intermediate_result(self):
  b=Budget(max_bits=8)
  with self.assertRaises(ResourceLimit):b.mul(F(128),F(2))
 def test_empty_and_line_output_exact_zero(self):
  p=box(0,0,1,1);q=box(1,0,2,1)
  _,a,_=clip(p,q);self.assertEqual(a,0)
  _,a,_=clip(p,box(2,0,3,1));self.assertEqual(a,0)

if __name__=='__main__':unittest.main()
