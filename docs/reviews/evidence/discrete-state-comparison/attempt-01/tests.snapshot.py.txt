import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from discrete_state_comparison import base_state,enrich_native,qa_pair,surface_pair,normalized_surface,summarize_nine,retention_category,validate_universal,point_row

def record(mask=7,qa=64,surface='land'):
    from observation_native_qa import local_screen
    s=local_screen('VNP14IMG','002',mask,qa,0)
    return {'case':'2023','product':'VNP14IMG','row':1,'col':2,'mask_class':mask,'algorithm_QA':qa,'geographic_flag':0,'surface':surface,'screen_sensitivity_state':s['state'],'screen_exclusion_reasons':'|'.join(s['excluded']),'screen_unresolved_reasons':'|'.join(s['unresolved']),'M13_non_nominal':bool(qa&64)}
class DiscreteComparisonTests(unittest.TestCase):
    def test_all_positive_classes_survive_M13(self):
        for mask in [7,8,9]:
            r=enrich_native('VNP14IMG',record(mask));self.assertEqual(r['basic_state'],'1');self.assertEqual(r['qa_status'],'non_nominal')
    def test_null_and_cloud_are_U_not_zero(self):
        self.assertEqual(base_state('MYD14',None)[0],'U');self.assertEqual(base_state('VNP14IMG',4)[0],'U')
        for mask in [3,5]:self.assertEqual(base_state('VNP14IMG',mask)[0],'0')
    def test_missing_expected_ID_is_failure_not_fallback(self):
        with self.assertRaises(ValueError):validate_universal({}, {(1,2)})
    def test_surface_real_geo_and_unknown_preserved(self):
        self.assertEqual(enrich_native('VNP14IMG',record(surface='land'))['surface_normalized'],'land')
        self.assertEqual(enrich_native('VNP14IMG',record(surface='detection_surface_unknown'))['surface_normalized'],'unknown')
        self.assertEqual(surface_pair('land','unknown'),'surface_unknown');self.assertEqual(surface_pair('water','coast'),'coast')
    def test_QA_incomplete_cannot_be_nominal(self):
        r=record(5,0);r['algorithm_QA']=None
        self.assertEqual(enrich_native('VNP14IMG',r)['qa_status'],'unknown')
        r=record();r['algorithm_QA']=None
        self.assertEqual(enrich_native('VNP14IMG',r)['qa_status'],'non_nominal')
        self.assertEqual(qa_pair('unknown','non_nominal'),'some_non_nominal')
    def test_unverifiable_exclusion_is_unknown(self):
        r=record(5,0);r['screen_sensitivity_state']='excluded';r['screen_exclusion_reasons']='invented'
        self.assertEqual(enrich_native('VNP14IMG',r)['qa_status'],'unknown')
    def test_Jaccard_empty_union_null_and_partitions(self):
        r=summarize_nine({'00':100,'1U':2,'UU':3});self.assertIsNone(r['Jaccard_known']);self.assertEqual(r['five']['U'],5);self.assertEqual(r['Ntotal'],105)
    def test_strict_interior_not_bbox_retention(self):
        self.assertEqual(retention_category(True,True,0,0),'included_quad_without_strict_interior_query')
        self.assertEqual(retention_category(False,False,None,None),'quad_unavailable_geometry_null')
        self.assertEqual(retention_category(True,False,0,0),'quad_outside32A_universe')
        self.assertEqual(retention_category(True,True,4,0),'strict_interior_present_without_ownership')
    def test_label_permutation_and_deletion_cannot_change_GEO(self):
        geo={'m_GEO_state':4,'v_GEO_state':0,'point_id':4,'m_quad_index':-1,'v_quad_index':0,'m_row':None,'v_row':1}
        a=point_row(geo,None,enrich_native('VNP14IMG',record()),['Suspect',None]);b=point_row(geo,None,None,['Suspect',None])
        self.assertEqual({k:a[k] for k in geo},{k:b[k] for k in geo});self.assertEqual(a['m_state'],'U');self.assertEqual(a['v_state'],'1')

if __name__=='__main__':unittest.main()
