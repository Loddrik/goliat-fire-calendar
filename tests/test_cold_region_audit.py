import datetime as dt
import json
import sys
import unittest
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from cold_region_audit import (mask_from_stats,build_mask,training_only,fit_source,raw_predictions,
    predict_all,fingerprint,invariance,FEATURES,METHODS,REGIMES)


class ColdRegionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cuts=[f'08{i:03d}' for i in range(101,134)]+[f'16{i:03d}' for i in range(101,122)]
        cls.source=cls.cuts[:2];cls.origin=(2012,2013,2014,2015)
        x=pd.MultiIndex.from_product([cls.cuts,range(2012,2020),range(1,13)],names=['cut','season','m']).to_frame(index=False)
        x['g']=x.m.map(lambda m:'JJA' if m in (6,7,8) else str(m))
        x['aqua']=((x.m+x.season)%4).astype(int)
        x['snpp']=(2*x.aqua+(x.season%2)).astype(float)
        cls.panel=x
        cls.model,cls.inner=fit_source(x,cls.source,cls.origin)
        cls.features=x[(x.season==2016)&(x.m==1)][FEATURES].copy().reset_index(drop=True)

    def test_four_fixed_regimes_disjoint_regions_and_years(self):
        self.assertEqual(len(REGIMES),4)
        for region,origin,dest in REGIMES.values():
            self.assertFalse(set(origin)&set(dest));self.assertEqual(len(origin),4);self.assertEqual(len(dest),4)
            self.assertIn(region,['08','16'])

    def test_mask_rules_and_morphology_preserved(self):
        stats=pd.DataFrame(dict(cell_x=[0,20,40,60],cell_y=[0]*4,n_days=[100,10,15,29],n_seasons=[8,1,1,7],p1=[0,1,0,0],p2=[0,0,1,0]))
        mask=mask_from_stats(stats)
        self.assertIn((-1,-1),mask);self.assertIn((22,2),mask);self.assertIn((40,0),mask)
        self.assertNotIn((41,0),mask);self.assertNotIn((60,0),mask)
        self.assertEqual(len(mask),9+25+1)

    def test_mask_excludes_snp_and_january2012_even_if_season2011(self):
        rows=[]
        for year in range(2004,2012):
            for day in range(1,5):rows.append(dict(cell_x=1,cell_y=1,acq_date=dt.date(year,7,day),sat='Aqua',type=0))
        for day in range(1,21):
            rows.append(dict(cell_x=9,cell_y=9,acq_date=dt.date(2011,7,day),sat='SNPP',type=1))
            rows.append(dict(cell_x=8,cell_y=8,acq_date=dt.date(2012,1,day),sat='Terra',type=1))
        c=duckdb.connect();c.register('det',pd.DataFrame(rows))
        mask,stats,proof=build_mask(c)
        self.assertEqual(mask,{(1,1)});self.assertEqual(set(proof.sat),{'Aqua'})
        self.assertTrue(all(pd.Timestamp(v)<pd.Timestamp('2012-01-01') for v in proof.max_date))

    def test_source_only_fitting_and_exact_fallback_full_cdf(self):
        tr=training_only(self.panel,self.source,self.origin)
        self.assertEqual(set(tr.cut),set(self.source));self.assertEqual(set(tr.season),set(self.origin))
        x,d,p=raw_predictions(self.features,self.model)
        held=~x.cut.isin(self.source)
        np.testing.assert_array_equal(x.loc[held,'B'],x.loc[held,'M1'])
        np.testing.assert_array_equal(x.loc[held,'E11'],x.loc[held,'E00'])
        for i in x.index[held]:
            for a,b in zip(d[i],p[i]):np.testing.assert_array_equal(a,b)

    def test_forbidden_labels_removed_or_changed_leave_model_and54_predictions_exact(self):
        pred,checks=predict_all(self.features,self.model,self.cuts)
        proof=invariance(self.panel,self.source,self.origin,self.features,self.model,pred,self.cuts)
        self.assertTrue(proof['removed']['model_and_choices_identical']);self.assertTrue(proof['changed']['all54_predictions_identical'])
        for method in ['E11_coherent','E00_coherent','E11_proportional']:
            self.assertAlmostEqual(pred[method].sum(),pred.B.sum(),places=9)
        for row in checks:
            self.assertLessEqual(row['allocated_expected_risk'],row['baseline_expected_risk']+1e-8)
            self.assertLessEqual(row['kkt_residual'],1e-8)

    def test_json_roundtrip_and_prediction_reordering(self):
        model=json.loads(json.dumps(self.model));self.assertEqual(fingerprint(model),fingerprint(self.model))
        a,_=predict_all(self.features,model,self.cuts)
        b,_=predict_all(self.features.sample(frac=1,random_state=4),model,self.cuts)
        np.testing.assert_allclose(a.sort_values('cut')[list(METHODS)],b.sort_values('cut')[list(METHODS)],rtol=0,atol=1e-10)

    def test_missing_source_group_invalid_and_labels_rejected_at_inference(self):
        broken=self.panel.drop(self.panel[(self.panel.cut==self.source[0])&(self.panel.season==2012)&(self.panel.m==3)].index)
        with self.assertRaisesRegex(ValueError,'Missing SOURCE'):
            fit_source(broken,self.source,self.origin)
        with self.assertRaisesRegex(ValueError,'FEATURES only'):
            raw_predictions(self.features.assign(snpp=0),self.model)
        with self.assertRaisesRegex(ValueError,'exact fixed54'):
            predict_all(self.features.iloc[:-1],self.model,self.cuts)


if __name__=='__main__':unittest.main()
