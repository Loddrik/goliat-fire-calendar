import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from affine_experiment import (LAMBDAS, POLICIES, b_name, calibrate_bands, choose_policies,
                               fit_affine, predict_affine)
from scientific_audit import CANDIDATES, fit_models


def training(x, y):
    return pd.DataFrame({"cut": ["A"] * len(x), "g": ["JJA"] * len(x),
                         "m": [7] * len(x), "season": list(range(2012, 2012 + len(x))),
                         "aqua": np.array(x, dtype=float), "snpp": np.array(y, dtype=float)})


class AffineExperimentTests(unittest.TestCase):
    def test_affine_recovers_positive_offset_and_solves_normal_equations(self):
        tr = training([0, 1, 2, 3], [4, 6, 8, 10])
        reference = fit_models(tr); params = fit_affine(tr, reference)
        row = params.loc["A", "JJA"]
        self.assertAlmostEqual(row.scale, np.sqrt(np.mean(tr.aqua ** 2)))
        for lam in LAMBDAS:
            name = b_name(lam)
            a, beta = row[name + "_a"], row[name + "_b"] * row.scale
            z = tr.aqua / row.scale
            residual = a + beta * z - tr.snpp
            self.assertAlmostEqual(residual.mean() + lam * a, 0, places=10)
            self.assertAlmostEqual((residual * z).mean() + lam * (beta - row.prior_beta), 0, places=10)
        result = predict_affine(tr, params)
        self.assertGreater(result["B_0.01"].iloc[0], 3)
        self.assertLess(abs(result["B_0.01"].iloc[0] - 4), 1)

    def test_negative_slope_is_projected_to_the_exact_boundary_solution(self):
        tr = training([0, 1, 2, 3], [9, 6, 3, 0])
        params = fit_affine(tr, fit_models(tr))
        row = params.loc["A", "JJA"]
        self.assertEqual(row["B_0.01_b"], 0)
        self.assertAlmostEqual(row["B_0.01_a"], tr.snpp.mean() / 1.01)
        result = predict_affine(tr, params)
        self.assertTrue((result["B_0.01"] >= 0).all())

    def test_test_truth_cannot_change_coefficients_or_normalization(self):
        tr = training([0, 1, 2, 3], [4, 6, 8, 10])
        params = fit_affine(tr, fit_models(tr)); frozen = params.copy(deep=True)
        test = training([0, 10000], [0, 0])
        a = predict_affine(test, params)
        test["snpp"] = [100000, 100000]
        b = predict_affine(test, params)
        pd.testing.assert_frame_equal(params, frozen)
        for lam in LAMBDAS:
            np.testing.assert_array_equal(a[b_name(lam)], b[b_name(lam)])
            self.assertGreaterEqual(a[b_name(lam)].iloc[1], a[b_name(lam)].iloc[0])

    def test_zero_local_aqua_is_finite_with_a_regional_prior(self):
        tr = pd.concat([training([0, 0, 0], [6, 6, 6]), training([10, 10, 10], [12, 12, 12]).assign(cut="B")], ignore_index=True)
        params = fit_affine(tr, fit_models(tr))
        result = predict_affine(tr, params)
        for lam in LAMBDAS:
            self.assertTrue(np.isfinite(result[b_name(lam)]).all())
            self.assertGreater(result.loc[result.cut == "A", b_name(lam)].iloc[0], 0)

    def test_policy_requires_an_extra_one_percent_over_the_previous_choice(self):
        inner = pd.DataFrame({"cut": ["A"], "snpp": [100.]})
        for method in CANDIDATES:
            inner[method] = 109.5
        inner["M1"] = 110.
        for lam in LAMBDAS:
            inner[b_name(lam)] = 109.45
        choices, _ = choose_policies(inner)
        self.assertEqual(choices["M1_A"]["A"], "A_1000000000")
        self.assertEqual(choices["M1_B"]["A"], "B_10")
        self.assertEqual(choices["M1_A_B"]["A"], "A_1000000000")
        for lam in LAMBDAS:
            inner[b_name(lam)] = 108.
        choices, _ = choose_policies(inner)
        self.assertEqual(choices["M1_A_B"]["A"], "B_10")

    def test_matched_bands_use_same_calibration_rows_and_ignore_outer_truth(self):
        inner = pd.DataFrame({"cut": ["A", "A"], "M1": [8., 12.], "snpp": [10., 10.]})
        external = pd.DataFrame({"cut": ["A", "B"], "M1": [10., 10.], "snpp": [10., 10.]})
        choices = {p: {"A": "M1", "B": "M1"} for p in POLICIES}
        for policy in POLICIES:
            external[policy] = external.M1
        a = calibrate_bands(external, inner, choices)
        external["snpp"] = [10000., 10000.]
        b = calibrate_bands(external, inner, choices)
        for policy in ("M1", *POLICIES):
            self.assertEqual(a[policy + "_abs80_radius"].iloc[0], 2.)
            self.assertEqual(a[policy + "_calibration_n"].iloc[0], 2)
            for kind in ("abs80", "scaled80"):
                pd.testing.assert_series_equal(a[policy + "_" + kind + "_radius"], b[policy + "_" + kind + "_radius"])
                self.assertTrue(pd.isna(a[policy + "_" + kind + "_radius"].iloc[1]))


if __name__ == "__main__":
    unittest.main()
