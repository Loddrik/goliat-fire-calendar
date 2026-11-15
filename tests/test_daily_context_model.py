import unittest
import numpy as np
import pandas as pd
from daily_context_model import (fit_context,distribution,raw_distribution,old_raw_distribution,empirical_prior_mix,scale_distribution,same_cdf,signature,predict_distributions)
from hurdle_model import fit_hurdle


def fixture():
    t=pd.DataFrame({'cut':['08101','08101','08102','08102'],'season':[2012]*4,'m':[1,2,1,2],'g':['1']*4,'aqua':[2.,2.,2.,2.],'D':[0,1,0,1],'snpp':[0.,4.,2.,0.]})
    ref={'regional':pd.DataFrame({'g':['1'],'rR':[2.]}).set_index('g')}
    base={'source_cuts':['08101','08102'],'origin_seasons':[2012],'regional_ratio':{'1':2.},'hurdle':fit_hurdle(t,ref)}
    return t,base


class DailyContextTests(unittest.TestCase):
    def test_constant_returns_full_old_for_every_query(self):
        t,b=fixture();t.D=0;c=fit_context(t,b)
        for cut in ('08101','08102','16999'):
            for d in (0,1):
                actual,_=raw_distribution(c,b,cut,'1',2.,d)
                self.assertTrue(same_cdf(actual,old_raw_distribution(b,cut,'1',1)))
                self.assertTrue(same_cdf(distribution(c,b,cut,'1',2.,d)[0],scale_distribution(old_raw_distribution(b,cut,'1',1),5.)))
        f=t.drop(columns='snpp');f['D']=1
        ds,*_=predict_distributions(f,c,b)
        self.assertEqual(len(ds),4)

    def test_variable_mixture_probability_and_local_D(self):
        t,b=fixture();c=fit_context(t,b)
        raw,meta=raw_distribution(c,b,'16999','1',2.,0)
        pp=b['hurdle']['parents']['["1",1]']['p']
        self.assertAlmostEqual(float(raw[1][raw[0]>0].sum()),(1+10*pp)/12)
        self.assertEqual(meta['local_n'],0)
        rawlocal,meta=raw_distribution(c,b,'08101','1',2.,0)
        self.assertEqual(meta['local_n'],1);self.assertEqual(meta['local_m'],0)
        self.assertAlmostEqual(float(rawlocal[1][rawlocal[0]>0].sum()),10*((1+10*pp)/12)/11)
        self.assertAlmostEqual(float(rawlocal[1].sum()),1.)
        # Empty class returns prior exactly, with no probability invented.
        prior=(np.array([0.,.2]),np.array([.7,.3]))
        v,w=empirical_prior_mix({'n':0,'m':0,'positive':[]},prior)
        np.testing.assert_array_equal(v,prior[0]);np.testing.assert_array_equal(w,prior[1])

    def test_actual_source_filter_with_poison(self):
        t,b=fixture();original=fit_context(t,b)
        poison=pd.concat([t,pd.DataFrame({'cut':['16999','08101'],'season':[2012,2019],'m':[3,3],'g':['1','1'],'aqua':[2.,2.],'D':[1,1],'snpp':[np.nan,999999.]})],ignore_index=True)
        altered=fit_context(poison,b)
        self.assertEqual(signature(original),signature(altered))
        self.assertEqual(original['training_rows'],4)

    def test_empty_parent_allzero_and_floor(self):
        t,b=fixture();t.snpp=0;t.D=0
        ref={'regional':pd.DataFrame({'g':['1'],'rR':[2.]}).set_index('g')};b['hurdle']=fit_hurdle(t,ref)
        c=fit_context(t,b)
        actual,_=distribution(c,b,'16999','1',0.,1)
        np.testing.assert_array_equal(actual[0],np.array([0.]));np.testing.assert_array_equal(actual[1],np.array([1.]))
        v,w=scale_distribution((np.array([0.,.25]),np.array([.2,.8])),10.)
        np.testing.assert_array_equal(v,np.array([0.,2.5]))
        from hurdle_model import weighted_quantile
        self.assertEqual(weighted_quantile(v,w,.5),2.5)
        self.assertEqual(weighted_quantile(np.array([0.,1.]),np.array([.5,.5]),.5),0.)
