"""Metamorphic controls on every saved descriptive destination, no refitting.

The labels may change diagnostics, never the frozen estimate or its endpoints.
These are software controls, not additional predictive-validation scores.
"""
import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'pipeline'))
from frozen_temporal_audit import load_frozen,estimate,signature,KEYS,BAND_POLICIES
from temporal_transport_audit import METHODS
from interval_loss_fit_audit import apply_intervals


class SavedModelInvarianceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.future=pd.read_parquet(ROOT/'data/processed/frozen_temporal_audit/predictions.parquet')
        cls.model=load_frozen()

    def variants(self,frame):
        yield frame.assign(snpp=np.roll(frame.snpp.to_numpy(),317))
        yield frame.assign(snpp=0.)
        yield frame.assign(snpp=np.nan)
        yield frame.drop(columns='snpp')
        yield frame.sample(frac=1,random_state=20261114).assign(snpp=1e9)

    def test_saved_points_restore_and_ignore_all_destination_labels_and_order(self):
        features=self.future[[*KEYS,'g','aqua','snpp']].copy()
        original=estimate(features,self.model).sort_values(KEYS).reset_index(drop=True)
        saved=self.future.sort_values(KEYS).reset_index(drop=True)
        self.assertEqual(len(original),3780)
        for method in METHODS:np.testing.assert_allclose(original[method],saved[method],rtol=0,atol=1e-10)
        columns=[c for c in original if c in METHODS or c.startswith(('A_','B_','H_d','P_'))
                 or c.endswith(('_chosen','_abs80_radius'))]
        before=signature(self.model)
        for variant in self.variants(features):
            actual=estimate(variant,self.model).sort_values(KEYS).reset_index(drop=True)
            pd.testing.assert_frame_equal(original[columns],actual[columns],check_exact=True)
        self.assertEqual(signature(self.model),before)

    def test_all_saved_endpoints_restore_and_ignore_destination_labels_and_order(self):
        calibration=pd.read_csv(ROOT/'data/processed/interval_loss_fit_audit/frozen_calibration.csv',dtype={'cut':str})
        before=calibration.copy(deep=True)
        keys=[*KEYS,'policy','calibration_cohort','fit_mode']
        original=apply_intervals(self.future,calibration).sort_values(keys).reset_index(drop=True)
        saved=pd.read_parquet(ROOT/'data/processed/interval_loss_fit_audit/later_intervals.parquet').sort_values(keys).reset_index(drop=True)
        self.assertEqual(len(original),37800)
        self.assertEqual(len(original.groupby(['policy','calibration_cohort','fit_mode'])),10)
        for column in ['point','lower','upper']:
            np.testing.assert_allclose(original[column],saved[column],rtol=0,atol=1e-10,equal_nan=True)
        columns=['point','lower','upper','n_calibration']
        for variant in self.variants(self.future):
            actual=apply_intervals(variant,calibration).sort_values(keys).reset_index(drop=True)
            pd.testing.assert_frame_equal(original[columns],actual[columns],check_exact=True)
        pd.testing.assert_frame_equal(calibration,before,check_exact=True)


if __name__=='__main__':unittest.main()
