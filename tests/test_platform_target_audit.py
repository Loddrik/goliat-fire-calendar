import datetime as dt
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'pipeline'))
from platform_target_audit import month_requests, attach_targets, metrics, METHODS


class PlatformTargetAuditTests(unittest.TestCase):
    def predictions(self):
        x = pd.DataFrame({'cut':['A','B','A','B'], 'season':[2021]*4,
                          'm':[1,1,2,2], 'snpp':[2,0,7,0], 'aqua':[1,0,2,0]})
        for i, method in enumerate(METHODS):
            x[method] = np.array([1.,0.,3.,0.])+i/10
        return x

    def monthly(self):
        return pd.DataFrame({'cut':['A','A','A'], 'season':[2021]*3, 'm':[1,1,2],
                             'sat':['SNPP','NOAA20','SNPP'], 'cell_days':[2,3,7],
                             'provisional':[False,True,False]})

    def requests(self):
        return pd.DataFrame({'season':[2021,2021], 'm':[1,2], 'complete_both_requested':[True,False]})

    def test_january_uses_next_calendar_year_and_missing_day_excludes_month(self):
        p = self.predictions()
        jan = {dt.date(2022,1,1)+dt.timedelta(days=i) for i in range(31)}
        feb = {dt.date(2022,2,1)+dt.timedelta(days=i) for i in range(28)}
        r = month_requests(p, {'SNPP':jan|feb, 'NOAA20':jan|feb-{dt.date(2022,2,3)}})
        self.assertEqual(r.y.tolist(), [2022,2022])
        self.assertEqual(r.complete_both_requested.tolist(), [True,False])
        self.assertEqual(r.NOAA20_missing_requested_days.tolist(), [0,1])

    def test_missing_month_rejected_before_zero_filling_and_identical_keys(self):
        x = attach_targets(self.predictions(), self.monthly(), self.requests())
        self.assertEqual(len(x),2)
        self.assertEqual(set(zip(x.cut,x.m)), {('A',1),('B',1)})
        self.assertEqual(x.noaa20.tolist(),[3,0])
        self.assertEqual(x.snpp_reproduced.tolist(),[2,0])
        self.assertEqual(x.noaa20_nrt.tolist(),[True,False])

    def test_target_disagreement_aborts_instead_of_scoring(self):
        m = self.monthly();m.loc[m.sat=='SNPP','cell_days'] = 99
        with self.assertRaisesRegex(ValueError,'did not reproduce'):
            attach_targets(self.predictions(),m,self.requests())

    def test_missing_request_provenance_and_duplicate_targets_rejected(self):
        with self.assertRaisesRegex(ValueError,'Missing requested-month'):
            attach_targets(self.predictions(),self.monthly(),self.requests().iloc[:1])
        m = self.monthly()
        with self.assertRaisesRegex(ValueError,'Duplicate platform'):
            attach_targets(self.predictions(),pd.concat([m,m.iloc[:1]]),self.requests())

    def test_noaa_labels_do_not_change_any_frozen_prediction(self):
        a = attach_targets(self.predictions(),self.monthly(),self.requests())
        m = self.monthly();m.loc[m.sat=='NOAA20','cell_days'] = 999
        b = attach_targets(self.predictions(),m,self.requests())
        for method in METHODS:
            np.testing.assert_array_equal(a[method],b[method])
        self.assertNotEqual(a.noaa20.sum(),b.noaa20.sum())

    def test_metrics_reference_specific_and_constructed_budget_property(self):
        x = attach_targets(self.predictions(),self.monthly(),self.requests())
        x['M1_B']=[1.,2.]; x['E_coherent']=[2.,1.]
        for target in ('snpp','noaa20'):
            m=metrics(x,target)['methods']
            self.assertAlmostEqual(m['M1_B']['bias'],m['E_coherent']['bias'])
            self.assertAlmostEqual(m['M1_B']['regional_monthly_mae'],m['E_coherent']['regional_monthly_mae'])
        self.assertNotEqual(metrics(x,'snpp')['target_sum'],metrics(x,'noaa20')['target_sum'])


if __name__ == '__main__': unittest.main()
