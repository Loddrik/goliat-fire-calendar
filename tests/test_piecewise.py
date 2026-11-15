import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"pipeline"))
from piecewise_experiment import fit_piecewise,predict_piecewise,choose,name,LAMBDAS
from affine_experiment import fit_affine,b_name
from scientific_audit import fit_models,CANDIDATES


def sample(x,y):
    return pd.DataFrame({"cut":["A"]*len(x),"g":["JJA"]*len(x),"m":[7]*len(x),
        "aqua":np.array(x,dtype=float),"snpp":np.array(y,dtype=float)})


class PiecewiseTests(unittest.TestCase):
    def test_zero_continuity_and_monotonicity(self):
        tr=sample([0,1,2,4,8,16],[0,2,4,8,10,14]);p=fit_piecewise(tr,fit_affine(tr,fit_models(tr)))
        tau=p.threshold.iloc[0];axis=np.sort(np.r_[0,np.linspace(0,100,200),tau-1e-8,tau,tau+1e-8])
        y=predict_piecewise(sample(axis,np.zeros(len(axis))),p)
        for lam in LAMBDAS:
            self.assertEqual(y[name(lam)].iloc[0],0.)
            self.assertTrue((np.diff(y[name(lam)])>=-1e-12).all())
            near=y.loc[np.abs(y.aqua-tau)<2e-8,name(lam)]
            self.assertLess(near.max()-near.min(),1e-5)

    def test_threshold_and_coefficients_are_training_only(self):
        tr=sample([0,1,4,8],[0,2,8,10]);p=fit_piecewise(tr,fit_affine(tr,fit_models(tr)))
        self.assertEqual(p.threshold.iloc[0],4.)
        frozen=p.copy(deep=True);te=sample([0,10000],[0,0]);a=predict_piecewise(te,p);te.snpp=99999;b=predict_piecewise(te,p)
        pd.testing.assert_frame_equal(frozen,p)
        for lam in LAMBDAS:np.testing.assert_array_equal(a[name(lam)],b[name(lam)])

    def test_quadratic_objective_is_optimal_under_feasible_perturbations(self):
        tr=sample([0,1,2,3,8,12],[9,8,7,6,1,0]);p=fit_piecewise(tr,fit_affine(tr,fit_models(tr)))
        row=p.iloc[0];z1=np.minimum(tr.aqua,row.threshold)/row.scale;z2=np.maximum(tr.aqua-row.threshold,0)/row.scale
        for lam in LAMBDAS:
            b=np.array([row[name(lam)+'_b1'],row[name(lam)+'_b2']])*row.scale
            self.assertTrue((b>=0).all());self.assertLessEqual(row[name(lam)+'_kkt'],1e-6)
            objective=lambda beta:np.mean((tr.snpp-beta[0]*z1-beta[1]*z2)**2)+lam*np.sum((beta-row.prior_beta)**2)
            optimum=objective(b)
            for j in [0,1]:
                for delta in [-1e-4,1e-4]:
                    other=b.copy();other[j]+=delta
                    if other[j]>=0:self.assertGreaterEqual(objective(other),optimum-1e-8)

    def test_parsimony_over_existing_affine(self):
        inner=pd.DataFrame({'cut':['A'],'snpp':[100.]})
        for c in CANDIDATES:inner[c]=109.5
        inner['M1']=110.
        for lam in LAMBDAS:inner[b_name(lam)]=109.;inner[name(lam)]=108.95
        choices,_=choose(inner)
        self.assertEqual(choices['M1_B_P']['A'],'B_10');self.assertEqual(choices['M1_P']['A'],'P_10')
        for lam in LAMBDAS:inner[name(lam)]=108.
        choices,_=choose(inner);self.assertEqual(choices['M1_B_P']['A'],'P_10')


if __name__=='__main__':unittest.main()
