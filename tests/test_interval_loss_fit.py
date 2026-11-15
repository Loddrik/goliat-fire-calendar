import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from interval_loss_fit_audit import fit_extremes,risk,calibrate,apply_intervals,nested_fold,verify_controls
from asymmetric_band_audit import nested_fold as previous_fold
from test_asymmetric_band import observations
from test_frozen_temporal import past_fixture

class IntervalLossFitTests(unittest.TestCase):
    def test_exact_ordered_knots_and_feasible_perturbations(self):
        p=np.array([0.,2.,8.,1.]);y=np.array([1.,0.,19.,4.]);s=np.sqrt(1+p)
        knots=np.unique(np.r_[(y-p)/s,-p/s,0.]);ql,qu,d=fit_extremes(p,y)
        exhaustive=min(risk(p,y,a,b) for i,a in enumerate(knots) for b in knots[i:])
        self.assertAlmostEqual(d['calibration_is'],exhaustive,places=11)
        rng=np.random.default_rng(15)
        for _ in range(200):
            a,b=sorted(rng.uniform(-12,20,2));self.assertLessEqual(risk(p,y,ql,qu),risk(p,y,a,b)+1e-10)

    def test_zero_tie_and_invalid_labels(self):
        ql,qu,d=fit_extremes([0.,0.],[0.,0.]);self.assertEqual((ql,qu),(0.,0.));self.assertEqual(d['calibration_is'],0.)
        for y in [[],[-1.],[np.nan]]:
            with self.assertRaises(ValueError):fit_extremes([0.]*len(y),y)

    def test_fitted_calibration_dominates_empirical_same_cohort(self):
        cal=calibrate(observations([0.,1.,2.,30.],[0.,2.,1.,5.]))
        for _,g in cal[cal.fit_mode!='symmetric_active_reference'].groupby(['policy','calibration_cohort']):
            v=g.set_index('fit_mode').calibration_is
            self.assertLessEqual(v.minimum_interval_score,v.empirical_quantiles+1e-9)

    def test_no_active_data_remains_unknown(self):
        result=apply_intervals(observations([1.],[0.]),calibrate(observations([0.,0.],[0.,0.])))
        self.assertTrue(result[result.calibration_cohort=='active'].lower.isna().all())
        known=result[result.calibration_cohort=='all_months'];self.assertTrue(known.lower.eq(0).all());self.assertTrue(known.upper.eq(0).all())

    def test_destination_labels_cannot_change_endpoints(self):
        cal=calibrate(observations([0.,1.,3.],[0.,1.,1.]));f=observations([2.],[1.]);a=apply_intervals(f,cal)
        for labels in [None,np.nan,1e9]:
            other=f.drop(columns='snpp') if labels is None else f.assign(snpp=labels)
            b=apply_intervals(other,cal)
            for c in ['point','lower','upper','n_calibration']:np.testing.assert_array_equal(a[c],b[c])
        self.assertTrue((a.lower<=a.upper).all());self.assertTrue(a.lower.ge(0).all())

    def test_nested_exclusion_and_previous_controls(self):
        _,base=past_fixture();base['M0']=base.aqua;base['M2']=1.;calls=[]
        def fit(data,allowed,destination):
            self.assertNotIn(2012,allowed);self.assertFalse(set(allowed)&set(destination));calls.append(1)
            return base[base.season.isin(destination)].copy(),pd.DataFrame()
        result,cal,_=nested_fold(None,2012,fit=fit);self.assertEqual(len(calls),8)
        old,_,_,_=previous_fold(None,2012,fit=fit);verify_controls(result,old)
        base.loc[base.season==2012,'snpp']=1e9
        result2,cal2,_=nested_fold(None,2012,fit=fit);pd.testing.assert_frame_equal(cal,cal2)
        np.testing.assert_array_equal(result.lower,result2.lower);np.testing.assert_array_equal(result.upper,result2.upper)

if __name__=='__main__':unittest.main()
