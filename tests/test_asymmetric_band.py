import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from asymmetric_band_audit import calibrate,apply_recipes,statistics,nested_fold,verify_control,POLICIES
from scaled_band_audit import outer_fold
from test_frozen_temporal import past_fixture


def observations(y,point):
    frame=pd.DataFrame({'cut':['A']*len(y),'season':[2012]*len(y),'m':range(1,len(y)+1),'aqua':[0.]*len(y),'snpp':y})
    for policy in POLICIES:frame[policy]=point
    return frame


class AsymmetricBandTests(unittest.TestCase):
    def test_signed_quantiles_use_correct_sign_and_linear_interpolation(self):
        frame=observations([1.,3.,9.],[4.,4.,4.]);cal=calibrate(frame)
        asym=cal[(cal.policy=='M1')&(cal.calibration_cohort=='active')&(cal['shape']=='asymmetric')].iloc[0]
        self.assertAlmostEqual(asym.q_lower,-2.6/np.sqrt(5));self.assertAlmostEqual(asym.q_upper,3.8/np.sqrt(5))
        result=apply_recipes(observations([2.],[4.]),cal)
        row=result[(result.policy=='M1')&(result.calibration_cohort=='active')&(result['shape']=='asymmetric')].iloc[0]
        self.assertAlmostEqual(row.lower,1.4);self.assertAlmostEqual(row.upper,7.8)

    def test_calibration_population_changes_counts_without_future_selection(self):
        cal=calibrate(observations([0.,0.,2.,6.],[1.,1.,1.,1.]))
        active=cal[(cal.policy=='M1')&(cal['shape']=='symmetric')&(cal.calibration_cohort=='active')].iloc[0]
        allmonths=cal[(cal.policy=='M1')&(cal['shape']=='symmetric')&(cal.calibration_cohort=='all_months')].iloc[0]
        self.assertEqual(active.n_calibration,2);self.assertEqual(allmonths.n_calibration,4)
        self.assertAlmostEqual(active.q_upper,4.2/np.sqrt(2));self.assertAlmostEqual(allmonths.q_upper,2.6/np.sqrt(2))

    def test_clipping_does_not_force_point_into_asymmetric_band(self):
        cal=calibrate(observations([2.,4.],[0.,0.]));result=apply_recipes(observations([0.],[0.]),cal)
        pop=result[(result.policy=='M1')&(result.calibration_cohort=='active')&(result['shape']=='asymmetric')]
        report=statistics(pop);self.assertEqual(report['positive_lower_fraction'],1.)
        self.assertEqual(report['point_outside_fraction'],1.)
        negative=calibrate(observations([1.],[5.]));clipped=apply_recipes(observations([0.],[0.]),negative)
        asym=clipped[clipped['shape']=='asymmetric'];self.assertTrue(asym.lower.eq(0).all());self.assertTrue(asym.upper.eq(0).all())

    def test_missing_active_calibration_stays_unknown_while_all_months_is_defined(self):
        cal=calibrate(observations([0.,0.],[0.,0.]));result=apply_recipes(observations([1.],[0.]),cal)
        active=result[result.calibration_cohort=='active'];allmonths=result[result.calibration_cohort=='all_months']
        self.assertTrue(active.lower.isna().all());self.assertTrue(allmonths.lower.eq(0).all())
        self.assertEqual(statistics(active)['n_scored'],0);self.assertEqual(statistics(active)['missing_calibration'],4)

    def test_unknown_or_changed_future_labels_do_not_change_endpoints(self):
        cal=calibrate(observations([0.,1.,3.],[0.,1.,1.]));future=observations([2.],[1.]);a=apply_recipes(future,cal)
        future.snpp=1e9;b=apply_recipes(future,cal);absent=apply_recipes(future.drop(columns='snpp'),cal)
        future.snpp=np.nan;unknown=apply_recipes(future,cal)
        for column in ['point','lower','upper','n_calibration']:
            np.testing.assert_array_equal(a[column],b[column]);np.testing.assert_array_equal(a[column],absent[column]);np.testing.assert_array_equal(a[column],unknown[column])

    def test_nested_capture_excludes_external_season_and_reproduces_existing_control(self):
        _,base=past_fixture();base['M0']=base.aqua;base['M2']=1.;calls=[]
        def fit(data,allowed,destination):
            self.assertNotIn(2012,allowed);self.assertFalse(set(allowed)&set(destination));calls.append((allowed,destination))
            return base[base.season.isin(destination)].copy(),pd.DataFrame()
        result,cal,record,_=nested_fold(None,2012,fit=fit)
        self.assertEqual(len(calls),8);self.assertTrue(cal.n_total_origin.eq(84).all())
        _,_,old,_,_=outer_fold(None,2012,fit=fit);verify_control(result,old)
        base.loc[base.season==2012,'snpp']=1e9
        result2,cal2,_,_=nested_fold(None,2012,fit=fit)
        pd.testing.assert_frame_equal(cal,cal2)
        np.testing.assert_array_equal(result.lower,result2.lower);np.testing.assert_array_equal(result.upper,result2.upper)


if __name__=='__main__':unittest.main()
