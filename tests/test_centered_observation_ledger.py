import sys
import unittest
from pathlib import Path
import numpy as np
from shapely.geometry import box, Polygon, MultiPolygon
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from centered_observation_ledger import certify_coordinates, GeometryChecks, assign_ownership, disjoint_check, polygon_parts, cross_owned_pairs, assert_close

def r(key,scan,p):return {'key':key,'scan':scan,'polygon':p}

class CenteredLedgerTests(unittest.TestCase):
    def test_exact_world_vertices_before_operations(self):
        world=np.asarray(box(700000,5900000,700010,5900010).exterior.coords);local,c=certify_coordinates(world,[700000.25,5900000.5])
        self.assertTrue(c['passed']);self.assertEqual(c['tuples'],5);np.testing.assert_array_equal(local[0],local[-1]);self.assertEqual(Polygon(local).area,100)
    def test_nonexact_and_signed_zero_cannot_pass(self):
        self.assertFalse(certify_coordinates(np.array([[1.,1.]]),[1e20,1e20])[1]['passed'])
        self.assertFalse(certify_coordinates(np.array([[-0.,0.]]),[0.,0.])[1]['passed'])
    def test_nonfinite_and_dimension_rejected(self):
        for c in [np.array([[1,2,3]]),np.array([[np.nan,0]])]:
            with self.assertRaises(ValueError):certify_coordinates(c,[0,0])
    def test_overlay_all_orders_and_complements(self):
        e=GeometryChecks();i,d=e.overlay(box(0,0,10,10),box(5,0,15,10));self.assertEqual(i.area,50);self.assertEqual(d.area,50);self.assertGreater(e.operations['intersection'],1)
    def test_unknown_time_support_blocks_known(self):
        e=GeometryChecks();rows=[r((1,1),1,box(0,0,3,2)),r((2,1),2,box(1,0,2,2))]
        owned,u,union,unknown,summary=assign_ownership(rows,{1:10.,2:None},'early',e)
        self.assertIsNone(owned[(2,1)]);self.assertEqual(owned[(1,1)].area,4);self.assertEqual(unknown.area,2)
    def test_priority_reassigns_without_activity(self):
        rows=[r((1,1),1,box(0,0,2,2)),r((2,1),2,box(1,0,3,2))]
        early=assign_ownership(rows,{1:10.,2:20.},'early',GeometryChecks());late=assign_ownership(rows,{1:10.,2:20.},'late',GeometryChecks())
        self.assertEqual(early[0][(1,1)].area,4);self.assertEqual(late[0][(1,1)].area,2);self.assertEqual(early[2].area,late[2].area)
    def test_material_overlap_fails_disjoint_control(self):
        with self.assertRaises(ValueError):disjoint_check([box(0,0,10,10),box(5,0,15,10)],GeometryChecks())
    def test_contacts_and_small_fragments_preserved(self):
        d=disjoint_check([box(0,0,1,1),box(1,0,2,1)],GeometryChecks());self.assertEqual(d['contact_zero_area_pairs'],1)
        p=MultiPolygon([box(0,0,1,1),box(2,0,2.000001,1)])
        self.assertEqual(len(list(polygon_parts(p))),2)
    def test_same_scan_overlap_not_repaired(self):
        with self.assertRaises(ValueError):assign_ownership([r((1,1),1,box(0,0,10,10)),r((1,2),1,box(5,0,15,10))],{1:1.},'early',GeometryChecks())
    def test_holes_and_center_outside_aoi(self):
        p=Polygon([(0,0),(10,0),(10,10),(0,10)],holes=[[(2,2),(4,2),(4,4),(2,4)]])
        i,d=GeometryChecks().overlay(p,box(5,0,15,10));self.assertEqual(i.area,50);self.assertEqual(d.area,46)
        i,d=GeometryChecks().overlay(box(-2,0,2,2),box(0,0,10,10));self.assertEqual(i.area,4)
    def test_all_cross_candidates_contacts_and_per_id_close(self):
        e=GeometryChecks();left=[((1,1),box(0,0,10,10))];right=[((2,1),box(0,0,5,10)),((2,2),box(5,0,10,10)),((2,3),box(10,0,15,10))]
        atoms,candidates,pm,pv,contacts=cross_owned_pairs(left,right,e)
        self.assertEqual(len(candidates),3);self.assertEqual(contacts,1);self.assertEqual(len(atoms),2);self.assertEqual(pm[(1,1)],100)
        self.assertEqual(pv[(2,1)],50);self.assertEqual(pv.get((2,3),0),0)
        common=e.operation('intersection',e.union(g for _,g in left),e.union(g for _,g in right))
        self.assertEqual(assert_close(sum(a['area_m2'] for a in atoms),common.area,'independent expressions'),0)
    def test_pairwise_resource_limit_does_not_drop_fragment(self):
        with self.assertRaisesRegex(RuntimeError,'resource_limit'):
            cross_owned_pairs([((1,1),box(0,0,10,10))],[((2,1),box(0,0,5,10)),((2,2),box(5,0,10,10))],GeometryChecks(),max_atoms=1)
    def test_either_expression_mismatch_blocks(self):
        with self.assertRaises(ValueError):assert_close(10,100,'one expression failed')

if __name__=='__main__':unittest.main()
