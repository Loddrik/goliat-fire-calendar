import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'pipeline'))
from hurdle_model import (fit_hurdle, predict_hurdle, mixture_median, weighted_quantile,
                          signature, write_hurdle, load_hurdle, METHODS, PROBABILITIES, KAPPAS)


def sample(aqua, y, cut='A', g='JJA'):
    n = len(y)
    return pd.DataFrame({'cut': [cut] * n, 'g': [g] * n,
                         'season': [2012 + i // 3 for i in range(n)],
                         'm': [6 + i % 3 for i in range(n)],
                         'aqua': np.asarray(aqua, dtype=float), 'snpp': np.asarray(y, dtype=float)})


def reference(frame, ratio=1.):
    return {'regional': pd.DataFrame({'rR': [ratio] * frame.g.nunique()},
                                    index=pd.Index(sorted(frame.g.unique()), name='g'))}


class HurdleModelTests(unittest.TestCase):
    def test_lower_weighted_quantile_ties_and_order(self):
        values = np.array([4., 1., 4., 9.]); weights = np.array([1., 2., 3., 2.])
        for q, expected in [(0., 1.), (.25, 1.), (.2501, 4.), (.75, 4.), (.751, 9.), (1., 9.)]:
            self.assertEqual(weighted_quantile(values, weights, q), expected)
            self.assertEqual(weighted_quantile(values[::-1], weights[::-1], q), expected)
        for w in [[0., 0.], [-1., 2.], [1., np.nan]]:
            with self.assertRaises(ValueError): weighted_quantile([1., 2.], w, .5)

    def test_mixture_median_minimizes_expected_absolute_loss(self):
        values = np.array([.2, 1., 8., 30.]); weights = np.array([1., 4., 2., 1.])
        rng = np.random.default_rng(20261115)
        for p in [0.1, .4, .5, .5001, .7, 1.]:
            for scale in [1., 3., 10.]:
                positive = np.maximum(1., scale * values)
                atoms = np.r_[0., positive]; mass = np.r_[1-p, p*weights/weights.sum()]
                prediction = mixture_median(p, values, weights, scale)
                risk = lambda x: float(np.sum(mass*np.abs(atoms-x)))
                candidates = np.r_[atoms, rng.uniform(0, positive.max(), 100)]
                self.assertLessEqual(risk(prediction), min(map(risk, candidates)) + 1e-10)
        # p times the conditional mean is not the MAE-optimal point.
        self.assertEqual(mixture_median(.4, [2.], [1.]), 0.)
        self.assertNotEqual(mixture_median(.4, [2.], [1.]), .4*2.)

    def test_half_mass_tie_chooses_zero_and_no_positive_support_is_needed_at_p0(self):
        self.assertEqual(mixture_median(.5, [2., 20.], [1., 1.]), 0.)
        self.assertEqual(mixture_median(.5001, [2., 20.], [1., 1.]), 2.)
        self.assertEqual(mixture_median(0., [], []), 0.)
        with self.assertRaises(ValueError): mixture_median(.2, [], [])

    def test_normalization_and_minimum_one_apply_after_destination_scaling(self):
        train = sample([0., 0., 2., 2.], [0., 2., 4., 10.])
        model = fit_hurdle(train, reference(train, 2.))
        result = predict_hurdle(sample([2.], [0.]), model).iloc[0]
        self.assertAlmostEqual(result.p_parent, 5/6)
        self.assertAlmostEqual(result.p_local_10, (2+10*(5/6))/12)
        # Positive residual .8 becomes 4 at s=5, not max(1,.8)*5=5.
        self.assertEqual(result.E00_10, 4.)
        small = predict_hurdle(sample([.01], [0.]), model).iloc[0]
        self.assertEqual(small.E00_10, 1.)

    def test_factorial_and_direct_joint_cdf_are_equivalent(self):
        local_y = np.array([0., 2., 10.]); other_y = np.array([0., 0., 1., 5., 20.])
        train = pd.concat([sample([0.]*3, local_y, 'A'), sample([0.]*5, other_y, 'B')], ignore_index=True)
        model = fit_hurdle(train, reference(train))
        result = predict_hurdle(sample([0.], [99.]), model).iloc[0]
        parent_positive = np.r_[local_y[local_y>0], other_y[other_y>0]]
        parent_p = (len(parent_positive)+.5)/(len(train)+1)
        local_positive = local_y[local_y>0]
        self.assertAlmostEqual(result.p_parent, parent_p)
        for k in KAPPAS:
            # Construct the joint distribution directly from raw local counts and
            # its parent's pseudo-observation masses, not the model's helper CDF.
            atoms = np.r_[0., local_positive, parent_positive]
            mass = np.r_[np.sum(local_y==0)+k*(1-parent_p),
                         np.ones(len(local_positive)),
                         np.repeat(k*parent_p/len(parent_positive), len(parent_positive))]
            order = np.argsort(atoms, kind='stable'); a = atoms[order]; w = mass[order]
            expected = a[np.flatnonzero(np.cumsum(w) >= .5*w.sum())[0]]
            self.assertEqual(result[f'E11_{k}'], expected)
        self.assertEqual(result.E00_10, 1.)
        self.assertEqual(result.E10_10, 1.)
        self.assertEqual(result.E01_10, 2.)
        self.assertEqual(result.E11_10, 2.)

    def test_missing_parent_uses_entire_origin_and_missing_local_is_exact_parent(self):
        train = sample([1., 2., 3., 4.], [1., 2., 0., 8.])
        model = fit_hurdle(train, reference(train))
        parent = model['parents']['["JJA",0]']
        self.assertEqual(parent['source_n'], 0)
        self.assertEqual(parent['n'], len(train))
        self.assertEqual(parent['probability_source'], 'global_no_parent')
        result = predict_hurdle(sample([0.], [0.], 'UNSEEN'), model).iloc[0]
        self.assertEqual(result.p_parent, result.p_local_10)
        for method in METHODS: self.assertEqual(result[method], result.E00_10)

    def test_parent_with_no_positive_borrows_global_conditional_support(self):
        train = sample([0., 0., 1., 2.], [0., 0., 2., 8.])
        model = fit_hurdle(train, reference(train))
        parent = model['parents']['["JJA",0]']
        self.assertEqual(parent['positive_source'], 'global_no_positive')
        self.assertEqual(parent['positive'], model['global']['positive'])
        self.assertAlmostEqual(parent['p'], .5/3)
        result = predict_hurdle(sample([0.], [0.]), model).iloc[0]
        self.assertEqual(result.E01_10, result.E00_10)
        self.assertEqual(result.E11_10, result.E10_10)

    def test_all_zero_origin_is_degenerate_and_all_positive_remains_positive(self):
        for y in [[0.]*4, [1., 2., 4., 8.]]:
            train = sample([1., 2., 3., 4.], y)
            model = fit_hurdle(train, reference(train))
            result = predict_hurdle(sample([0., 1000.], [np.nan, np.nan]), model)
            if max(y)==0:
                self.assertTrue(model['all_zero'])
                self.assertTrue(result[[*METHODS, *PROBABILITIES]].eq(0).all().all())
            else:
                self.assertFalse(model['all_zero'])
                self.assertTrue(result[list(METHODS)].ge(1).all().all())
                self.assertTrue(result[list(PROBABILITIES)].lt(1).all().all())
            json.dumps(model, allow_nan=False)

    def test_future_labels_order_and_input_rows_cannot_change_frozen_predictions(self):
        train = pd.concat([sample([0., 1., 0., 2.], [0., 4., 2., 10.], 'A'),
                           sample([0., 1., 2., 4.], [1., 2., 4., 20.], 'B')], ignore_index=True)
        ref = reference(train)
        model = fit_hurdle(train, ref); frozen = signature(model)
        future = train.copy(); future['season'] += 8
        baseline = predict_hurdle(future, model).sort_values(['cut','season','m']).reset_index(drop=True)
        for altered in [future.assign(snpp=1e9), future.assign(snpp=np.nan), future.drop(columns='snpp'),
                        future.sample(frac=1, random_state=17)]:
            result = predict_hurdle(altered, model).sort_values(['cut','season','m']).reset_index(drop=True)
            pd.testing.assert_frame_equal(result[[*METHODS,*PROBABILITIES]], baseline[[*METHODS,*PROBABILITIES]], check_exact=True)
        self.assertEqual(signature(model), frozen)
        reordered = fit_hurdle(train.sample(frac=1, random_state=18), ref)
        self.assertEqual(signature(model), signature(reordered))

    def test_fit_rejects_future_seasons_invalid_values_and_duplicate_keys(self):
        train = sample([0., 1., 2.], [0., 2., 4.]); ref = reference(train)
        variants = [train.assign(season=2020), train.assign(snpp=np.nan), train.assign(aqua=-1.),
                    train.assign(snpp=-1.), pd.concat([train,train.iloc[:1]]), train.iloc[:0]]
        for variant in variants:
            with self.assertRaises(ValueError): fit_hurdle(variant,ref)
        model = fit_hurdle(train,ref)
        with self.assertRaises(ValueError): predict_hurdle(train.assign(g='UNKNOWN'),model)

    def test_json_roundtrip_stable_signature_and_tamper_rejection(self):
        train = sample([0., 1., 2., 0.], [0., 2., 5., 1.]); model = fit_hurdle(train,reference(train))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'frozen.json'; saved = write_hurdle(model,path); restored = load_hurdle(path)
            self.assertEqual(saved,signature(restored));self.assertEqual(model,restored)
            pd.testing.assert_frame_equal(predict_hurdle(train,model),predict_hurdle(train,restored),check_exact=True)
            payload = json.loads(path.read_text());payload['model']['all_zero'] = True;path.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError,'hash mismatch'): load_hurdle(path)
        reverse = dict(reversed(list(model.items())))
        self.assertEqual(signature(model),signature(reverse))


if __name__=='__main__': unittest.main()
