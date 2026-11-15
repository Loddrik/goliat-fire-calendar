import copy
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from scientific_audit import fit_models
from hurdle_model import fit_hurdle,mixture_median
from coherent_allocation import _canonical
from context_cdf_model import ContextCDF,composition,hellinger_squared,normalized_atoms,cdf_equal,FEATURES


def training():
    rows=[]
    for cut,aq,ys in [('A',[0,0,1,2],[0,2,4,6]),('B',[0,1,1,1],[5,0,2,3]),('C',[0,0,0,0],[0,0,0,0])]:
        for s,a,y in zip(range(2012,2016),aq,ys):
            rows.append(dict(cut=cut,season=s,m=1,g='1',aqua=a,snpp=y))
            rows.append(dict(cut=cut,season=s,m=2,g='2',aqua=1,snpp=0))
    return pd.DataFrame(rows)


def contexts():
    def vec(i):x=np.zeros(18);x[i]=1;return x.tolist()
    return {c:{'available':True,'vector':vec(i)} for c,i in [('A',0),('B',1),('C',2),('H',0)]}


class ContextModelTests(unittest.TestCase):
    def setUp(self):
        t=training();self.model=fit_hurdle(t,fit_models(t));self.ctx=contexts()

    def test_composition_roundoff_and_invalid_input(self):
        x=np.zeros(18);x[0]=1+1e-13;x[1]=-1e-13
        np.testing.assert_array_equal(composition(x),np.r_[1.,np.zeros(17)])
        self.assertIsNone(composition(None,False))
        for bad in [np.zeros(18),np.ones(17)/17,np.r_[1.1,-.1,np.zeros(16)],np.r_[np.nan,np.zeros(17)]]:
            with self.assertRaisesRegex(ValueError,'invalid_input'):composition(bad)
        self.assertAlmostEqual(hellinger_squared(np.eye(18)[0],np.eye(18)[1]),1.)

    def test_pool_n_normalization_variable_state_counts(self):
        engine=ContextCDF(self.model,self.ctx);pool=engine.groups[('1',0)]
        w,diag=engine.weights(pool,'H','test')
        self.assertEqual([pool[c]['n'] for c in ['A','B','C']],[2,1,4])
        self.assertAlmostEqual(sum(w[c]*v['n'] for c,v in pool.items()),7.)
        self.assertGreater(w['A'],1.);self.assertLess(w['C'],1.)
        self.assertLessEqual(diag['ESS_CUT'],3.);self.assertLessEqual(diag['ESS_observations'],7.)

    def test_alpha_zero_query_unknown_and_known_identical_exact_control(self):
        same={c:copy.deepcopy(self.ctx['A']) for c in self.ctx}
        unknown=copy.deepcopy(self.ctx);unknown['H']={'available':False,'vector':None}
        queries=[('A','1',1),('H','1',0),('H','2',1),('H','2',0)]
        cases=[(ContextCDF(self.model,self.ctx,alpha=0),queries),(ContextCDF(self.model,unknown),queries[1:]),(ContextCDF(self.model,same),queries)]
        for engine,selected in cases:
            for cut,g,state in selected:
                p0,p1=engine.components(cut,g,state)
                self.assertEqual(p0[0],p1[0]);np.testing.assert_array_equal(p0[1],p1[1]);np.testing.assert_array_equal(p0[2],p1[2])

    def test_unknown_source_keeps_global_half_not_identical_context_claim(self):
        same={c:copy.deepcopy(self.ctx['A']) for c in self.ctx};same['C']={'available':False,'vector':None}
        engine=ContextCDF(self.model,same);w,_=engine.weights(engine.groups[('1',0)],'H','test')
        self.assertEqual(w['C'],.5);self.assertGreater(w['A'],1.)
        p0,p1=engine.components('H','1',0);self.assertNotEqual(p0[0],p1[0])

    def test_positive_fallback_reweights_global_n_before_positives(self):
        engine=ContextCDF(self.model,self.ctx);p0,p1=engine.components('H','2',1)
        self.assertAlmostEqual(p1[0],.5/13)
        weights,diag=engine.weights(engine.global_pool,'H','expected')
        z,w=engine.positive_atoms(engine.global_pool,weights)
        np.testing.assert_array_equal(p1[1],z);np.testing.assert_array_equal(p1[2],w)
        self.assertEqual(diag['N'],24)
        empty=engine.components('H','2',0)
        self.assertTrue(any(d['pool']=='global_group_empty' for d in engine.diagnostics))
        self.assertTrue(any(d['pool']=='global_positive_fallback' and d['N']==24 for d in engine.diagnostics))

    def test_no_kernel_group_falls_back_per_pool_not_entire_pair(self):
        t=training();t=t[(t.g=='1')|(t.cut=='C')]
        model=fit_hurdle(t,fit_models(t));ctx=contexts();ctx['C']={'available':False,'vector':None}
        engine=ContextCDF(model,ctx);p0,p1=engine.components('H','2',1)
        self.assertEqual(p0[0],p1[0])
        self.assertTrue(any(d['pool']=='group:2:1' and d['fallback']=='no_context_mass_in_pool' for d in engine.diagnostics))
        self.assertTrue(any(d['pool']=='global_positive_fallback' and d['fallback']=='context_weighted' for d in engine.diagnostics))
        self.assertFalse(cdf_equal(normalized_atoms(*p0,1.),normalized_atoms(*p1,1.)))

    def test_factorial_swaps_completed_components_and_lower_median(self):
        engine=ContextCDF(self.model,self.ctx)
        features=pd.DataFrame([dict(cut='A',season=2016,m=1,g='1',aqua=1)])[FEATURES]
        out,d0,d1=engine.predict(features);a,b=engine.components('A','1',1)
        scale=1+self.model['regional_ratio']['1']
        self.assertEqual(out.C01.iloc[0],mixture_median(a[0],b[1],b[2],scale))
        self.assertEqual(out.C10.iloc[0],mixture_median(b[0],a[1],a[2],scale))
        for dist,pred in [(d0[0],out.C00.iloc[0]),(d1[0],out.C11.iloc[0])]:
            v,w=_canonical(dist);self.assertAlmostEqual(w.sum(),1.)
            expected=v[np.searchsorted(np.cumsum(w),.5,side='left')]
            self.assertEqual(pred,expected)
        self.assertEqual(mixture_median(.5,[2],[1]),0)

    def test_global_zero_and_invalid_stats_or_labels(self):
        t=training();t.snpp=0;m=fit_hurdle(t,fit_models(t));engine=ContextCDF(m,self.ctx)
        p0,p1=engine.components('H','1',1);self.assertEqual(p0[0],0);self.assertEqual(p1[0],0)
        features=pd.DataFrame([dict(cut='H',season=2016,m=1,g='1',aqua=1)])[FEATURES]
        with self.assertRaisesRegex(ValueError,'labels forbidden'):engine.predict(features.assign(snpp=99))
        corrupted=copy.deepcopy(self.model);corrupted['global']['m']+=1
        with self.assertRaisesRegex(ValueError,'global counts'):ContextCDF(corrupted,self.ctx)


if __name__=='__main__':unittest.main()
