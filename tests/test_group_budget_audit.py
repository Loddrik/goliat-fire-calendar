import unittest
import numpy as np
from group_budget_audit import allocate_groups, Budget, partition


class GroupBudgetTests(unittest.TestCase):
    def setUp(self):
        self.ds=[(np.array([0.,2.,6.]),np.array([.2,.4,.4])),(np.array([0.,1.,4.]),np.array([.3,.3,.4])),(np.array([0.,3.,8.]),np.array([.1,.6,.3])),(np.array([0.,2.,7.]),np.array([.4,.2,.4]))]
        self.b=np.array([1.,2.,3.,2.])

    def test_one_group_and_singletons(self):
        from coherent_allocation import reconcile
        # Reference is also counted, avoiding hidden calls in the fixture budget.
        budget=Budget();expected=budget.call(self.ds,self.b)
        actual,_=allocate_groups(self.ds,self.b,['all']*4,budget)
        np.testing.assert_array_equal(actual,expected)
        single,_=allocate_groups(self.ds,self.b,list('abcd'),budget)
        np.testing.assert_allclose(single,self.b,atol=1e-10,rtol=0)

    def test_rename_and_permutation(self):
        groups=['a','a','b','b'];base,_=allocate_groups(self.ds,self.b,groups)
        renamed,_=allocate_groups(self.ds,self.b,['z','z','y','y'])
        np.testing.assert_array_equal(base,renamed)
        order=np.array([3,1,0,2]);permuted,_=allocate_groups([self.ds[i] for i in order],self.b[order],[groups[i] for i in order])
        np.testing.assert_allclose(permuted[np.argsort(order)],base,atol=1e-10,rtol=0)

    def test_feasible_global_same_tie_break(self):
        ds=[(np.array([0.,4.]),np.array([.5,.5]))]*4;b=np.ones(4)
        g,_=allocate_groups(ds,b,['all']*4);r,_=allocate_groups(ds,b,['a','a','b','b'])
        np.testing.assert_array_equal(g,b);np.testing.assert_array_equal(r,g)

    def test_held_locality(self):
        a,_=allocate_groups(self.ds,self.b,['source','source','held','held'])
        changed=self.ds.copy();changed[:2]=[(np.array([0.,100.]),np.array([.01,.99]))]*2
        bb=self.b.copy();bb[:2]*=7
        b,_=allocate_groups(changed,bb,['source','source','held','held'])
        np.testing.assert_array_equal(a[2:],b[2:])

    def test_partition_and_invalid(self):
        cuts=[f'08{i:03}' for i in range(33)]+[f'16{i:03}' for i in range(21)]
        p=partition(cuts);self.assertEqual(sum(v=='P33' for v in p.values()),33)
        self.assertEqual(p,partition(cuts[::-1]))
        with self.assertRaises(ValueError):allocate_groups(self.ds,self.b,['x'])
        with self.assertRaises(RuntimeError):allocate_groups(self.ds,self.b,['a']*4,Budget(limit=0))
