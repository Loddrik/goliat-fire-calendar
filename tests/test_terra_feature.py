import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from terra_feature_audit import fit_multi,predict_multi,solve_faces,fit_predict,LAMBDAS,name
from scientific_audit import fit_models
from affine_experiment import fit_affine,predict_affine,b_name


def sample(aqua,terra,y):
    n=len(y)
    return pd.DataFrame({'cut':['A']*n,'g':['JJA']*n,'m':[7]*n,'aqua':np.array(aqua,dtype=float),'terra':np.array(terra,dtype=float),'snpp':np.array(y,dtype=float)})


class TerraFeatureTests(unittest.TestCase):
    def test_zero_terra_reduces_to_existing_affine_for_every_lambda(self):
        tr=sample([0,1,2,4,8,16],[0]*6,[1,3,5,8,12,20]);ref=fit_models(tr);aff=fit_affine(tr,ref);params,clim=fit_multi(tr,aff)
        old=predict_affine(tr,aff);new=predict_multi(tr,params,clim)
        for l in LAMBDAS:
            np.testing.assert_allclose(old[b_name(l)],new[name('C',l)],atol=1e-10,rtol=0)
            np.testing.assert_allclose(params[name('C',l)+'_bT'],0,atol=1e-10)

    def test_exact_faces_respect_kkt_and_negative_slope_boundaries(self):
        h=np.repeat(np.eye(3)[None,:,:],3,axis=0);q=np.array([[-2.,-3.,4.],[-2.,3.,-4.],[2.,-1.,-1.]])
        solution,kkt=solve_faces(h,q)
        np.testing.assert_allclose(solution,[[-2,0,4],[-2,3,0],[2,0,0]])
        self.assertLessEqual(kkt.max(),1e-6)

    def test_solution_beats_feasible_perturbations_for_coupled_quadratic(self):
        h=np.array([[[2.,.7,.4],[.7,2.,.3],[.4,.3,1.5]]]);q=np.array([[2.,-1.,4.]])
        x,kkt=solve_faces(h,q);rng=np.random.default_rng(24)
        candidates=np.column_stack([x[0,0]+rng.normal(size=1000),rng.uniform(0,5,size=1000),rng.uniform(0,5,size=1000)])
        def loss(v):return np.einsum('ni,ij,nj->n',v,h[0],v)-2*v@q[0]
        self.assertLessEqual(loss(x)[0],loss(candidates).min()+1e-9)

    def test_terra_signal_is_detected_without_aqua_variation(self):
        tr=sample([1]*8,[0,1,2,3,4,5,6,7],[3,5,7,9,11,13,15,17]);ref=fit_models(tr);aff=fit_affine(tr,ref);params,clim=fit_multi(tr,aff)
        c=predict_multi(tr,params,clim);b=predict_affine(tr,aff)
        self.assertGreater(params['C_0.01_bT'].iloc[0],0)
        self.assertLess((c['C_0.01']-tr.snpp).abs().mean(),(b['B_0.01']-tr.snpp).abs().mean())

    def test_climatology_ablation_and_parameters_ignore_future_values(self):
        tr=sample([1,2,3,4,5,6],[0,1,1,3,4,8],[1,5,7,8,10,18]);ref=fit_models(tr);params,clim=fit_multi(tr,fit_affine(tr,ref))
        future=sample([0,3],[0,2],[0,1]);a=predict_multi(future,params,clim);saved=params.copy(deep=True)
        future.terra=1000000.;future.snpp=1e9;b=predict_multi(future,params,clim)
        pd.testing.assert_frame_equal(params,saved);self.assertEqual(clim.iloc[0],2.)
        for l in LAMBDAS:np.testing.assert_array_equal(a[name('D',l)],b[name('D',l)])
        # Actual Terra enters C, whereas D uses the saved seasonal median.
        self.assertGreater(b['C_0.01'].max(),a['C_0.01'].max())

    def test_normalization_uses_real_terra_for_both_actual_and_climatology(self):
        tr=sample([1,1,2,3],[0,1,3,8],[1,3,5,9]);params,clim=fit_multi(tr,fit_affine(tr,fit_models(tr)))
        self.assertAlmostEqual(params.scale_t.iloc[0],np.sqrt(np.mean(tr.terra**2)))
        self.assertEqual(clim.iloc[0],2.)

    def test_fitting_and_mask_interface_excludes_destination(self):
        from test_frozen_temporal import past_fixture
        tr,_=past_fixture();tr['terra']=(tr.aqua*2+tr.m)%7
        class Fake:
            def __init__(self):self.calls=[];self.frame=tr.copy()
            def monthly(self,policy,allowed):self.calls.append((policy,allowed));return self.frame.copy()
        data=Fake();origin=(2012,2013,2014,2015);dest=(2016,2017,2018,2019)
        a,pa,ca=fit_predict(data,origin,dest)
        data.frame.loc[data.frame.season.isin(dest),'snpp']=1e9
        b,pb,cb=fit_predict(data,origin,dest)
        self.assertEqual(data.calls,[('fold_fitted',origin)]*2)
        pd.testing.assert_frame_equal(pa,pb);pd.testing.assert_series_equal(ca,cb)
        for mode in ['C','D']:
            for l in LAMBDAS:np.testing.assert_array_equal(a[name(mode,l)],b[name(mode,l)])


if __name__=='__main__':unittest.main()
