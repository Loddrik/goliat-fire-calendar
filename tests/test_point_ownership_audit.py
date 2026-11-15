import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from point_ownership_audit import validate_quad,point_relation,integer_range,independent_range,resolve,grid_limits,verify_nested,evaluate_grid

class DummyBudget:
    def check(self,*a):pass
    def candidate(self):pass
    def edge(self,*a):pass
class PointOwnershipTests(unittest.TestCase):
    def test_simple_nonconvex_quad_and_boundary(self):
        q,_=validate_quad([(0,0),(4,0),(1,1),(0,4),(0,0)])
        self.assertEqual(point_relation(q,(1,0)),0);self.assertEqual(point_relation(q,(1,1)),0)
        self.assertEqual(point_relation(q,(1,2)),-1);self.assertEqual(point_relation(q,(0,2)),0)
    def test_self_intersection_and_collapsed_edges_fail(self):
        for ring in [[(0,0),(4,4),(0,4),(4,0),(0,0)],[(0,0),(0,0),(4,0),(0,4),(0,0)],[(0,0),(1,0),(2,0),(3,0),(0,0)]]:
            with self.assertRaises(ValueError):validate_quad(ring)
        with self.assertRaises(ValueError):validate_quad([(0.,0.),(1.,0.),(1.,1.),(0.,1.),(0.,0.)])
    def test_orientation_reversal_preserves_membership(self):
        q=((0,0),(10,0),(10,10),(0,10))
        for p,expected in [((5,5),1),((10,5),0),((11,5),-1)]:
            self.assertEqual(point_relation(q,p),expected);self.assertEqual(point_relation(q[::-1],p),expected)
    def test_dyadic_bbox_and_large_integer_predicate(self):
        q=((-2001,-2001),(2001,-2001),(2001,2001),(-2001,2001))
        self.assertEqual(integer_range(q,8,250,0),(-1,1,-1,1));self.assertEqual(integer_range(q,8,250,0),independent_range(q,8,250,0))
        huge=1<<70;q=tuple((x*huge,y*huge) for x,y in q)
        self.assertEqual(point_relation(q,(0,0)),1);self.assertEqual(point_relation(q,(2001*huge,0)),0)
    def test_closed_rational_bbox_ranges_and_open_domain(self):
        q=((-25000,-25000),(25000,-25000),(25000,25000),(-25000,25000))
        for h in [250,500]:
            for phase in [0,125]:self.assertEqual(integer_range(q,1,h,phase),independent_range(q,1,h,phase))
        self.assertEqual(grid_limits(250,0),(-99,99));self.assertEqual(grid_limits(500,125),(-50,49))
    def test_precedence_and_all_causes_preserved(self):
        code,causes,e,l=resolve([(0,0),(1,1),(2,1)],[1,2,2],[10.,20.,None])
        self.assertEqual(code,1);self.assertEqual(causes,(True,True,True,False));self.assertEqual((e,l),(-1,-1))
        self.assertEqual(resolve([(0,0)],[0],[None])[1],(True,False,False,True))
    def test_time_same_scan_and_no_support_distinct(self):
        self.assertEqual(resolve([(0,1)],[0],[None])[0],2)
        self.assertEqual(resolve([(0,1),(1,1)],[0,0],[10.])[0],3)
        self.assertEqual(resolve([(0,-1)],[0],[10.])[0],4)
    def test_early_late_ties_by_scan_not_quad_order(self):
        code,flags,e,l=resolve([(0,1),(1,1),(2,1)],[2,0,1],[10.,30.,10.])
        self.assertEqual((code,e,l),(0,1,2))
    def test_independent_nested_postings_and_roster(self):
        q=((-1000,-1000),(1000,-1000),(1000,1000),(-1000,1000));g={'quads':[q],'included':np.array([True]),'native':np.array([[1,1,0,1]])}
        fine=evaluate_grid(g,1,250,0,[1.],DummyBudget());coarse=evaluate_grid(g,1,500,0,[1.],DummyBudget())
        self.assertTrue(verify_nested(fine,coarse)['all_passed']);self.assertEqual(fine['roster'][0,0],81);self.assertEqual(fine['roster'][0,1],49)
        coarse['early'][0]=123
        with self.assertRaises(ValueError):verify_nested(fine,coarse)

if __name__=='__main__':unittest.main()
