import datetime as dt
import sys
import unittest
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from scientific_audit import AuditData, TRAIN, add_bands, choose_methods, fit_models, predict


class ScientificAuditTests(unittest.TestCase):
    def test_mask_ignores_withheld_and_future_detections(self):
        data = AuditData.__new__(AuditData)
        data.con = duckdb.connect(); data.mask_cache = {}
        data.con.execute("create table det(cell_x int,cell_y int,acq_date date,type int,season int)")
        rows = [(0, 0, dt.date(2018, 7, 1) + dt.timedelta(days=i), 1, 2018) for i in range(9)]
        rows += [(0, 0, dt.date(2019, 7, 1), 1, 2019)]
        rows += [(9, 9, dt.date(2020, 7, 1) + dt.timedelta(days=i), 1, 2020) for i in range(20)]
        data.con.executemany("insert into det values (?,?,?,?,?)", rows)
        allowed = tuple(s for s in TRAIN if s != 2019)
        self.assertEqual(data.fit_mask(allowed), set())
        self.assertEqual(len(data.fit_mask(TRAIN)), 25)  # volcano + two rings
        data.con.execute("insert into det values (0,0,date '2019-07-02',1,2019)")
        data.mask_cache.clear()
        self.assertEqual(data.fit_mask(allowed), set())
        with self.assertRaises(ValueError):
            data.fit_mask((2020,))

    def test_zero_local_denominator_never_creates_infinite_predictions(self):
        frame = pd.DataFrame({"cut": ["A", "B"], "season": [2012, 2012], "m": [7, 7],
                              "g": ["JJA", "JJA"], "aqua": [10., 0.], "snpp": [20., 5.]})
        pred = predict(frame, fit_models(frame))
        self.assertTrue(np.isfinite(pred.A_0).all())
        self.assertEqual(pred.loc[pred.cut == "B", "A_0"].iloc[0], 0)
        self.assertEqual(pred.loc[pred.cut == "A", "M1"].iloc[0], 25)

    def test_method_choice_keeps_M1_when_improvement_is_under_one_percent(self):
        from scientific_audit import CANDIDATES
        frame = pd.DataFrame({"cut": ["A", "B"], "snpp": [100., 100.]})
        for method in CANDIDATES:
            frame[method] = [109.95, 109.]
        frame["M1"] = [110., 110.]
        choices, _ = choose_methods(frame)
        self.assertEqual(choices["A"], "M1")
        self.assertEqual(choices["B"], "A_1000000000")

    def test_outer_truth_cannot_change_calibration_widths(self):
        inner = pd.DataFrame({"cut": ["A", "A"], "M1": [10., 10.], "snpp": [8., 12.]})
        outer = pd.DataFrame({"cut": ["A", "B"], "M1": [10., 10.], "snpp": [10., 10.]})
        a = add_bands(outer, inner)
        outer["snpp"] = [1000., 1000.]
        b = add_bands(outer, inner)
        self.assertEqual(a.band_mae_radius.iloc[0], b.band_mae_radius.iloc[0])
        self.assertEqual(a.band_scaled_radius.iloc[0], b.band_scaled_radius.iloc[0])
        self.assertEqual(a.calibration_n.iloc[1], 0)
        self.assertTrue(pd.isna(a.band_mae_radius.iloc[1]))


if __name__ == "__main__":
    unittest.main()
