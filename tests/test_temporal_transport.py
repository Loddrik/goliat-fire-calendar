import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from temporal_transport_audit import SPLITS,validate_split,fit_predict,transport,METHODS


class FakeData:
    def __init__(self):
        self.calls=[]
        self.frame=pd.DataFrame([{'cut':cut,'season':s,'m':m,'g':'JJA' if m in (6,7,8) else str(m),
            'aqua':float(1+(s+m)%5),'snpp':float(2*((s+m)%5)+1+(cut=='B'))}
            for cut in ['A','B'] for s in range(2012,2020) for m in range(1,13)])
    def monthly(self,policy,allowed):
        self.calls.append((policy,allowed))
        return self.frame.copy()


class TemporalTests(unittest.TestCase):
    def test_disjoint_and_frozen_development_pool(self):
        for a,b in SPLITS.values():validate_split(a,b)
        for a,b in [((2012,2013,2014),(2014,)),((2012,2012,2013),(2014,)),((2012,2013,2014),(2020,))]:
            with self.assertRaises(ValueError):validate_split(a,b)

    def test_destination_targets_cannot_change_fitted_parameters_or_predictions(self):
        data=FakeData();origin,destination=SPLITS['forward']
        a,pa=fit_predict(data,origin,destination)
        data.frame.loc[data.frame.season.isin(destination),'snpp']=1000000.
        b,pb=fit_predict(data,origin,destination)
        pd.testing.assert_frame_equal(pa,pb)
        cols=[c for c in a if c not in ['snpp']]
        pd.testing.assert_frame_equal(a[cols],b[cols])
        self.assertEqual(data.calls,[('fold_fitted',origin)]*2)

    def test_transport_selection_only_uses_origin(self):
        data=FakeData();origin,destination=SPLITS['backward'];calls=[]
        def spy(data,allowed,held):
            calls.append((allowed,held))
            return fit_predict(data,allowed,held)
        a,sa,pa=transport(data,origin,destination,fit=spy)
        self.assertEqual(len(calls),5)
        for allowed,held in calls[:-1]:
            self.assertEqual(set(allowed)|set(held),set(origin))
            self.assertFalse(set(allowed)&set(held))
            self.assertFalse(set(allowed)&set(destination))
        self.assertEqual(calls[-1],(origin,destination))
        data.frame.loc[data.frame.season.isin(destination),'snpp']=1000000.
        b,sb,pb=transport(data,origin,destination,fit=spy)
        pd.testing.assert_frame_equal(sa,sb)
        pd.testing.assert_frame_equal(pa,pb)
        np.testing.assert_array_equal(a[list(METHODS)],b[list(METHODS)])
        self.assertTrue(np.isfinite(a[list(METHODS)]).all().all())


if __name__=='__main__':unittest.main()
