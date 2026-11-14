import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from scaled_band_audit import scale,calibrate,interval_loss,apply_bands,statistics,outer_fold,BAND_POLICIES
from test_frozen_temporal import past_fixture


def observations(y,point):
    f=pd.DataFrame({'cut':['A']*len(y),'season':[2012]*len(y),'m':list(range(1,len(y)+1)),'snpp':y})
    for p in BAND_POLICIES:f[p]=point
    return f


class ScaledBandTests(unittest.TestCase):
    def test_interval_score_penalizes_width_and_both_exceedances(self):
        np.testing.assert_allclose(interval_loss([2,5,0],[1,1,1],[3,3,3]),[2,22,12])
        with self.assertRaises(ValueError):interval_loss([1],[3],[2])
        with self.assertRaises(ValueError):interval_loss([1],[0],[2],0)
        self.assertTrue(np.isnan(interval_loss([1],[np.nan],[np.nan]))[0])

    def test_scale_preserves_nonzero_radius_at_point_zero(self):
        for power in [0.,.5,1.]:self.assertEqual(scale([0],power)[0],1)
        np.testing.assert_allclose(scale([3],.5),[2])
        with self.assertRaises(ValueError):scale([-1],.5)
        with self.assertRaises(ValueError):scale([1],.75)

    def test_normalized_quantiles_use_only_active_calibration_rows(self):
        f=observations([0.,2.,4.],[99.,1.,1.]);c=calibrate(f)
        self.assertTrue(c.n_calibration.eq(2).all())
        for power,value in [(0.,2.6),(.5,2.6/np.sqrt(2)),(1.,1.3)]:
            np.testing.assert_allclose(c[c.power==power].q80,value)

    def test_missing_calibration_is_not_zero_uncertainty(self):
        c=calibrate(observations([0.,0.],[0.,0.]))
        self.assertTrue(c.q80.isna().all());self.assertTrue(c.n_calibration.eq(0).all())
        result=apply_bands(observations([1.],[0.]),c);report=statistics(result)
        self.assertEqual(report['n_scored'],0);self.assertEqual(report['missing_calibration'],15)
        self.assertIsNone(report['coverage']);self.assertIsNone(report['mean_interval_score'])

    def test_future_labels_do_not_change_radius_and_lower_bound_is_clipped(self):
        c=calibrate(observations([2.,4.],[1.,1.]));f=observations([3.],[0.]);a=apply_bands(f,c)
        f.snpp=1e9;b=apply_bands(f,c);absent=apply_bands(f.drop(columns='snpp'),c)
        for column in ['point','radius','lower','upper']:
            np.testing.assert_array_equal(a[column],b[column]);np.testing.assert_array_equal(a[column],absent[column])
        self.assertTrue(a.lower.eq(0).all())
        absolute=a[(a.policy=='M1')&(a.power==0)].iloc[0]
        self.assertAlmostEqual(absolute.interval_score,6.6)

    def test_outer_fold_excludes_external_season_from_every_fit_and_calibration(self):
        _,base=past_fixture();base['M0']=base.aqua;base['M2']=1.;calls=[]
        def fit(data,allowed,held):
            calls.append((allowed,held));self.assertNotIn(2012,allowed)
            self.assertFalse(set(allowed)&set(held))
            return base[base.season.isin(held)].copy(),pd.DataFrame()
        a,cal,intervals,record,_=outer_fold(None,2012,fit=fit)
        self.assertEqual(len(calls),8)
        for allowed,held in calls[:-1]:self.assertEqual(len(allowed),6);self.assertNotIn(2012,held)
        self.assertEqual(len(calls[-1][0]),7);self.assertEqual(calls[-1][1],(2012,))
        base.loc[base.season==2012,'snpp']=1e9
        b,cal2,intervals2,_,_=outer_fold(None,2012,fit=fit)
        pd.testing.assert_frame_equal(cal,cal2)
        np.testing.assert_array_equal(intervals.radius,intervals2.radius)


if __name__=='__main__':unittest.main()
