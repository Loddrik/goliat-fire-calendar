import hashlib
import json
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from contract_gap_audit import research_grid, observed_grid, observed_variants, type_cell_days, close_deltas, attach_observed_support, verify_series, validate_csv


class ContractGapTests(unittest.TestCase):
    def test_literal_grid_border_can_disagree_with_rounded_observed_grid(self):
        lon,lat=-73.29,-36.8
        c=research_grid(lon,lat);o=observed_grid(lon,lat)
        self.assertEqual(c,(int(np.floor(lon/.01)),int(np.floor(lat/.01))))
        self.assertEqual((o[0]-18000,o[1]-9000),(-7329,-3680))
        # Deliberately just below the border: O rounds, scientific floor does not.
        self.assertNotEqual(research_grid(-73.29000000001,lat)[0],observed_grid(-73.29000000001,lat)[0]-18000)

    def test_type_filter_precedes_cell_day_dedup_and_unknown_is_not_type0(self):
        x=pd.DataFrame({'cut':['A']*4,'cell_x':[1,1,2,3],'cell_y':[2]*4,
                        'acq_date':['2020-07-01']*4,'type':[1,0,None,0]})
        all_days,zero,mix=type_cell_days(x)
        self.assertEqual(len(all_days),3);self.assertEqual(len(zero),2)
        self.assertTrue(mix.loc[mix.cell_x==1,'other'].iloc[0]);self.assertTrue(mix.loc[mix.cell_x==1,'type0'].iloc[0])
        self.assertFalse(mix.loc[mix.cell_x==2,'type0'].iloc[0]);self.assertTrue(mix.loc[mix.cell_x==2,'unknown'].iloc[0])

    def test_missing_mapping_is_excluded_and_cut_movement_explicit(self):
        def row(lon):
            x,y=observed_grid(lon,-36.805)
            return dict(acq_date='2020-07-01',cut_com='A',longitude=str(lon),latitude='-36.805',grid_x=x,grid_y=y)
        rows=[row(-73.295),row(-73.315)]
        mapping={research_grid(-73.295,-36.805):'B'}
        sets,diag=observed_variants(rows,mapping,set())
        self.assertEqual(len(sets['Omask']),2);self.assertEqual(len(sets['Omap']),1)
        self.assertEqual(next(iter(sets['Omap']))[0],'B')
        self.assertEqual(diag['mapping_unavailable_detection_rows'],1);self.assertEqual(diag['moved_cut_detection_rows'],1)

    def test_closure_algebra_does_not_imply_attribution(self):
        x=pd.DataFrame(dict(O0=[4,7],Ogrid=[5,6],Omask=[3,4],Omap=[2,5],Cmaskedtype0=[8,2],Cmaskedall=[9,6]))
        y=close_deltas(x);self.assertEqual(y.closure_error.tolist(),[0,0]);self.assertEqual(y.residual_cohort.tolist(),[6,-3])

    def test_missing_observed_month_remains_unknown_not_zero(self):
        p=pd.DataFrame(dict(cut=['A','A'],season=[2025,2025],m=[12,1]))
        s=pd.DataFrame(dict(cut=['A'],month=['2025-12'],O0=[0]))
        x=attach_observed_support(p,s)
        self.assertEqual(x.month.tolist(),['2025-12','2026-01']);self.assertEqual(x.available.tolist(),[True,False]);self.assertTrue(pd.isna(x.O0.iloc[1]))

    def test_series_mismatch_is_rejected(self):
        row=dict(acq_date='2020-07-01',grid_x='1',grid_y='2')
        verify_series([row],[dict(month='2020-07',cell_days=1,detections=1)])
        with self.assertRaisesRegex(ValueError,'do not reproduce'):
            verify_series([row],[dict(month='2020-07',cell_days=0,detections=1)])

    def test_corrupt_csv_rejected_before_interpreting_rows(self):
        payload=b'bad csv\n'
        segment=dict(sha256=hashlib.sha256(payload).hexdigest(),bytes=len(payload),rows=0)
        with self.assertRaisesRegex(ValueError,'hash/size'):
            validate_csv(payload+b'x',segment,{}, {})


if __name__=='__main__':unittest.main()
