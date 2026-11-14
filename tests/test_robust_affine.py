import datetime as dt
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"pipeline"))
from affine_experiment import fit_affine, LAMBDAS as B_LAMBDAS, b_name
from scientific_audit import CANDIDATES
from robust_affine_experiment import fit_huber,predict_huber,choose,DELTAS,LAMBDAS,name,check_deadline


def sample(x,y):
    return pd.DataFrame({"cut":["A"]*len(x),"g":["JJA"]*len(x),"aqua":np.array(x,dtype=float),"snpp":np.array(y,dtype=float)})


def prior():
    return {"regional":pd.DataFrame({"rR":[2.]},index=pd.Index(["JJA"],name="g"))}


class RobustAffineTests(unittest.TestCase):
    def test_real_slow_irls_case_converges_with_acceleration(self):
        fixture=json.loads((Path(__file__).parent/'fixtures/huber_slow_case.json').read_text())
        self.assertGreater(fixture['pure_irls_1000_kkt'],1e-6)
        training=pd.DataFrame(fixture['training'])
        params=pd.DataFrame([fixture['parameters']],index=pd.MultiIndex.from_tuples([(fixture['cut'],fixture['group'])],names=['cut','g']))
        _,diag=fit_huber(training,params)
        self.assertTrue(all(d['max_kkt']<=1e-6 for d in diag))
        self.assertLess(max(d['iterations'] for d in diag),1000)

    def test_huber_matches_quadratic_when_residuals_are_small(self):
        tr=sample([0,1,2,3],[4,6,8,10]);b=fit_affine(tr,prior());h,diag=fit_huber(tr,b)
        for lam in LAMBDAS:
            np.testing.assert_allclose(h[name(10.,lam)+"_a"],b[b_name(lam)+"_a"],atol=1e-6)
            np.testing.assert_allclose(h[name(10.,lam)+"_b"],b[b_name(lam)+"_b"],atol=1e-6)
        self.assertTrue(all(d["max_kkt"]<=1e-6 for d in diag))

    def test_training_outlier_has_less_influence_with_fixed_prior(self):
        x=np.arange(10);y=4+2*x;y[-1]=200
        tr=sample(x,y);b=fit_affine(tr,prior());h,diag=fit_huber(tr,b)
        quadratic=b.loc[("A","JJA"),"B_0.01_a"]+b.loc[("A","JJA"),"B_0.01_b"]*3
        robust=h.loc[("A","JJA"),name(1.,.01)+"_a"]+h.loc[("A","JJA"),name(1.,.01)+"_b"]*3
        self.assertLess(abs(robust-10),abs(quadratic-10))
        self.assertLess(abs(robust-10),1.)

    def test_boundary_slope_and_truth_independence(self):
        tr=sample([0,1,2,3],[9,6,3,0]);b=fit_affine(tr,prior());h,diag=fit_huber(tr,b)
        self.assertTrue((h[[c for c in h if c.endswith("_b")]]>=0).all().all())
        self.assertTrue(all(d["max_kkt"]<=1e-6 for d in diag))
        a=predict_huber(tr,h);tr.snpp=100000;z=predict_huber(tr,h)
        for d in DELTAS:
            for l in LAMBDAS:np.testing.assert_array_equal(a[name(d,l)],z[name(d,l)])

    def test_no_silent_acceptance_of_unconverged_model(self):
        tr=sample([0,1,2,3],[0,0,0,100]);b=fit_affine(tr,prior())
        with self.assertRaisesRegex(RuntimeError,"convergence"):
            fit_huber(tr,b,max_iter=0)

    def test_parsimony_requires_improvement_over_existing_affine(self):
        frame=pd.DataFrame({"cut":["A"],"snpp":[100.]})
        for c in CANDIDATES:frame[c]=109.5
        frame["M1"]=110.
        for l in B_LAMBDAS:frame[b_name(l)]=109.
        for d in DELTAS:
            for l in LAMBDAS:frame[name(d,l)]=108.95
        choices,_=choose(frame)
        self.assertEqual(choices["M1_B_H"]["A"],"B_10")
        self.assertEqual(choices["M1_H"]["A"],name(10.,1.))

    def test_deadline_is_enforced_when_requested(self):
        with patch('robust_affine_experiment.DEADLINE',dt.datetime(2000,1,1,tzinfo=dt.timezone.utc)):
            with self.assertRaises(TimeoutError):check_deadline()


if __name__=='__main__':unittest.main()
