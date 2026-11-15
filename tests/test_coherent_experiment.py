import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'pipeline'))
from coherent_experiment import distributions, extend, NEW


class CoherentExperimentTests(unittest.TestCase):
    def setUp(self):
        self.model = {'schema_version': 1, 'kappas': [3,10,30], 'all_zero': False,
                      'regional_ratio': {'1': 2.}, 'locals': {},
                      'parents': {'["1",1]': {'p': .8, 'positive': [.1, 2.]}}}
        self.frame = pd.DataFrame({'cut': [str(i) for i in range(54)],
                                   'season': 2019, 'm': 1, 'g': '1', 'aqua': 1.,
                                   'M1_B': 1., 'E11_10': 1., 'snpp': 0.})

    def test_mean_integrates_clipped_atoms_and_zero_mass(self):
        v, w = distributions(self.frame.iloc[:1], self.model)[0]
        np.testing.assert_allclose(v, [0., 1., 6.])
        np.testing.assert_allclose(w, [.2, .4, .4])
        self.assertAlmostEqual(np.dot(v,w), 2.8)

    def test_destination_labels_are_not_prediction_features(self):
        expected, _ = extend(self.frame, self.model)
        changed = self.frame.copy(); changed['snpp'] = np.arange(54)*1000
        actual, _ = extend(changed, self.model)
        missing, _ = extend(self.frame.drop(columns='snpp'), self.model)
        np.testing.assert_array_equal(actual[list(NEW)], expected[list(NEW)])
        np.testing.assert_array_equal(missing[list(NEW)], expected[list(NEW)])
        self.assertAlmostEqual(expected.E_coherent.sum(), 54.)

    def test_incomplete_geographical_domain_is_rejected(self):
        with self.assertRaisesRegex(ValueError, '54 communes'):
            extend(self.frame.iloc[:-1], self.model)

    def test_changed_source_median_is_rejected(self):
        changed = self.frame.copy(); changed['E11_10'] = 2.
        with self.assertRaisesRegex(ValueError, 'median'):
            extend(changed, self.model)


if __name__ == '__main__':
    unittest.main()
