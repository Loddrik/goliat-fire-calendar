import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from contract_gap_common_archive_audit import common_archive,aggregate_sets,contrasts

class CommonArchiveTests(unittest.TestCase):
    def test_calendar_support_excludes2026_independent_of_counts(self):
        x=pd.DataFrame(dict(cut=['A']*4,season=[2020,2025,2025,2020],m=[7,12,1,1],activity=[0,999,999,0]))
        s=dict(start='2020-07',end='2025-12',available_years=[2020,2025])
        included,excluded=common_archive(x,s)
        self.assertEqual(included.month.tolist(),['2020-07','2025-12'])
        self.assertEqual(excluded.month.tolist(),['2026-01','2021-01'])
        x.activity=0
        self.assertEqual(common_archive(x,s)[0].index.tolist(),included.index.tolist())

    def test_transform_dedup_and_no_support_invention(self):
        panel=pd.DataFrame(dict(cut=['A','B'],season=[2020]*2,m=[7]*2))
        x=aggregate_sets({'O0':{('A',2020,7,'2020-07-01',1,2)},'Omap':{('B',2020,7,'2020-07-01',1,2)}},panel)
        self.assertEqual(x.O0.tolist(),[1,0]);self.assertEqual(x.Omap.tolist(),[0,1])

if __name__=='__main__':unittest.main()
