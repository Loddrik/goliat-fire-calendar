import math
import unittest
from fractions import Fraction as F
import numpy as np
from crps_score import crps,prepare,finalize


def integral_oracle(values,weights,y):
    """Independent CDF integral, no producer prefix or score function."""
    knots=sorted(set([float(y),*map(float,values)]));total=math.fsum(map(float,weights))
    contributions=[]
    for left,right in zip(knots,knots[1:]):
        mid=(left+right)/2
        cdf=math.fsum(float(w) for x,w in zip(values,weights) if x<=mid)/total
        contributions.append((right-left)*(cdf-float(y<=mid))**2)
    return math.fsum(contributions)


def rational_oracle(values,weights,y):
    x=list(map(F,values));w=list(map(F,weights));y=F(y)
    return sum(a*abs(v-y) for v,a in zip(x,w))-sum(a*b*abs(v-u) for v,a in zip(x,w) for u,b in zip(x,w))/2


class CRPSTests(unittest.TestCase):
    def compare(self,x,w,y,expected=None):
        r=crps(x,w,y);oracle=integral_oracle(x,w,y)
        self.assertLessEqual(abs(r['score']-oracle),r['tolerance'])
        if expected is not None:self.assertLessEqual(abs(r['score']-float(expected)),r['tolerance'])
        return r['score']

    def test_delta_exact_MAE(self):
        for b in (0.,1.25,8.):
            for y in (-3.,0.,1.25,20.):self.assertEqual(self.compare([b],[1.],y),abs(b-y))

    def test_two_atoms_rational(self):
        for y in ('-2','0','1/2','2','4'):
            self.compare([0.,2.],[.25,.75],float(F(y)),rational_oracle(['0','2'],['1/4','3/4'],y))

    def test_ties_zero_masses_splitting_permutation(self):
        x=[0.,1.25,1.25,4.];w=[.2,.3,0.,.5];y=.7
        v=self.compare(x,w,y)
        self.assertAlmostEqual(v,self.compare(x[::-1],w[::-1],y))
        self.assertAlmostEqual(v,self.compare([0.,1.25,4.,4.],[.2,.3,.25,.25],y))
        self.assertEqual(self.compare([2.,2.,2.],[0.,.5,.5],8.),6.)

    def test_scale_and_translation(self):
        x=np.array([0.,1.,2.75]);w=[.2,.3,.5];y=.7;base=self.compare(x,w,y)
        self.assertAlmostEqual(self.compare(3*x,w,3*y),3*base)
        self.assertAlmostEqual(self.compare(x-7,w,y-7),base)

    def test_validation_and_roundoff(self):
        for x,w in [([],[]),([0.],[0.]),([0.,1.],[1.01,-.01]),([0.],[float('nan')]),([float('inf')],[1.]),([0.],[1.00001]),([0.,1.],[1.])]:
            with self.assertRaises(ValueError):prepare(x,w)
        x,w,total=prepare([0.,2.],[.25,.75+1e-13]);self.assertEqual(len(w),2);self.assertLess(abs(math.fsum(w)-1),1e-15)
        self.assertTrue(finalize(-.5e-10,0.,1.)['negative_roundoff_clamped'])
        with self.assertRaises(ValueError):finalize(-2e-10,0.,1.)
