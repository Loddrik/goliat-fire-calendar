import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from coherent_allocation import reconcile,risk,expected_risk,means,kkt_residual


def oracle_two(distributions,baseline):
    total=float(np.sum(baseline));first=distributions[0][0];second=distributions[1][0]
    candidates=np.unique(np.r_[0.,total,first,total-np.asarray(second)])
    candidates=candidates[(candidates>=0)&(candidates<=total)]
    losses=np.array([risk(distributions,[a,total-a]) for a in candidates])
    minimum=losses.min();optimal=candidates[np.abs(losses-minimum)<=1e-11]
    nearest=float(np.clip(baseline[0],optimal.min(),optimal.max()))
    return minimum,np.array([nearest,total-nearest])


class CoherentAllocationTests(unittest.TestCase):
    def test_two_row_breakpoint_oracle_and_secondary_proximity(self):
        rng=np.random.default_rng(20261115)
        for _ in range(150):
            distributions=[]
            for _ in range(2):
                values=rng.integers(0,20,size=5).astype(float)
                weights=rng.dirichlet(np.ones(5))
                distributions.append((values,weights))
            baseline=rng.uniform(0,15,size=2)
            minimum,nearest=oracle_two(distributions,baseline)
            answer=reconcile(distributions,baseline)
            self.assertAlmostEqual(risk(distributions,answer),minimum,places=9)
            np.testing.assert_allclose(answer,nearest,rtol=0,atol=1e-8)
            self.assertLessEqual(kkt_residual(distributions,answer),1e-8)

    def test_equal_cost_face_uses_closest_baseline_not_row_priority(self):
        # Cost is constant on [0,10] for each variable. Projection of [12,0]
        # onto that box with total12 is uniquely [10,2].
        d=[([0.,10.],[.5,.5]),([0.,10.],[.5,.5])]
        np.testing.assert_allclose(reconcile(d,[12.,0.]),[10.,2.],rtol=0,atol=1e-10)
        np.testing.assert_array_equal(reconcile(d,[7.,5.]),[7.,5.])

    def test_all_zero_distributions_return_baseline_exactly(self):
        d=[([0.],[1.])]*4;b=np.array([0.,.1,3.3,18.7])
        np.testing.assert_array_equal(reconcile(d,b),b)
        self.assertAlmostEqual(risk(d,b),b.sum())

    def test_zero_budget_and_single_variable(self):
        d=[([2.,10.],[.3,.7]),([0.,4.],[.4,.6])]
        np.testing.assert_array_equal(reconcile(d,[0.,0.]),[0.,0.])
        np.testing.assert_allclose(reconcile([d[0]],[12.3]),[12.3],rtol=0,atol=1e-10)

    def test_unbounded_tail_and_atoms_above_budget(self):
        d=[([1.],[1.]),([2.],[1.])]
        # Above the last atoms, total excess is indifferent. Proximity returnsB.
        np.testing.assert_array_equal(reconcile(d,[10.,20.]),[10.,20.])
        d=[([100.],[1.]),([0.],[1.])]
        np.testing.assert_allclose(reconcile(d,[0.,5.]),[5.,0.],rtol=0,atol=1e-10)

    def test_permutations_of_variables_atoms_and_duplicates(self):
        d=[([0.,1.,1.,20.],[.2,.1,.3,.4]),([0.,5.,30.],[.7,.2,.1]),
           ([0.],[1.]),([2.,10.],[.6,.4])]
        b=np.array([7.2,2.1,.2,3.5]);answer=reconcile(d,b)
        p=np.array([2,0,3,1]);changed=[]
        for index in p:
            v,w=d[index];changed.append((list(reversed(v)),list(reversed(w))))
        reordered=reconcile(changed,b[p]);np.testing.assert_allclose(reordered,answer[p],rtol=0,atol=1e-10)

    def test_expected_risk_never_worse_than_baseline_and_total_is_preserved(self):
        rng=np.random.default_rng(18)
        for n in [3,7,54]:
            for _ in range(15):
                d=[(rng.uniform(0,100,size=12),rng.dirichlet(np.ones(12))) for _ in range(n)]
                b=rng.uniform(0,40,size=n);a=reconcile(d,b)
                self.assertTrue((a>=0).all());self.assertAlmostEqual(a.sum(),b.sum(),places=8)
                self.assertLessEqual(expected_risk(d,a),expected_risk(d,b)+1e-8)
                self.assertLessEqual(kkt_residual(d,a),1e-8)

    def test_means_use_target_atoms_and_expected_risk_alias(self):
        d=[([0.,1.,10.],[.5,.3,.2]),([0.],[1.])]
        np.testing.assert_allclose(means(d),[2.3,0.])
        self.assertEqual(risk(d,[2.,0.]),expected_risk(d,[2.,0.]))

    def test_invalid_distributions_or_baselines_are_rejected(self):
        good=[([0.,2.],[.5,.5])]
        for b in [[-1.],[np.nan],[np.inf],[],[1.,2.],[[1.]]]:
            with self.assertRaises(ValueError):reconcile(good,b)
        bad=[([0.,2.],[-.1,1.1]),([0.,2.],[0.,0.]),([0.,2.],[.3,.3]),
             ([0.,np.inf],[.5,.5]),([-1.,2.],[.5,.5]),([0.,2.],[1.]),([],[])]
        for distribution in bad:
            with self.assertRaises(ValueError):reconcile([distribution],[1.])


if __name__=='__main__':unittest.main()
