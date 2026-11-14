import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import Workbook
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from conaf_external_audit import normalize_name,name_mapping,parse_season,parse_count,extract_workbook,spearman,bootstrap_rank,regional_panels


class ConafTests(unittest.TestCase):
    def test_identity_normalization_and_ambiguity(self):
        self.assertEqual(normalize_name(' Ñiquén '),'NIQUEN')
        self.assertEqual(normalize_name('Chillán-Viejo'),'CHILLANVIEJO')
        with self.assertRaises(ValueError):name_mapping([{'cut':'1','name':'Ñiquén'},{'cut':'2','name':'Niquen'}])
        self.assertEqual(name_mapping([{'cut':'16106','name':'Pinto'},{'cut':'16103','name':'Chillán Viejo'}])['PINTO'],'16106')

    def test_count_blanks_are_distinct_from_zero(self):
        self.assertEqual(parse_count(None),(None,'blank_unknown'))
        self.assertEqual(parse_count(0),(0,'numeric'))
        self.assertEqual(parse_count(None,True),(None,'formula_without_cached_value'))
        for x in [True,-1,2.5,'0',math.inf,math.nan,'#VALUE!']:
            with self.assertRaises(ValueError):parse_count(x)

    def test_season_validation(self):
        self.assertEqual(parse_season('2012 - 2013'),2012)
        for x in ['12-13','2012-2014','2012/2013']:
            with self.assertRaises(ValueError):parse_season(x)

    def test_workbook_provenance_unknowns_and_strict_join(self):
        communes=[{'cut':'16106','name':'Pinto'},{'cut':'16103','name':'Chillán Viejo'}]
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'test.xlsx';w=Workbook();s=w.active;s.title='2012 - 2013'
            s.cell(3,1,'2012-2013')
            for j,v in enumerate(['REGION','PROVINCIA','COMUNA','NUMERO INCENDIOS '],1):s.cell(4,j,v)
            s.cell(7,3,'PINTO');s.cell(7,4,0);s.cell(8,3,'CHILLAN VIEJO');w.save(path)
            frame=extract_workbook(path,communes,(2012,))
            self.assertEqual(frame[frame.cut=='16106'].conaf_occurrences.iloc[0],0)
            self.assertTrue(frame[frame.cut=='16103'].conaf_occurrences.isna().all())
            self.assertEqual(frame[frame.cut=='16106'].excel_row.iloc[0],7)
            s.cell(8,4,'=1+1');w.save(path)
            frame=extract_workbook(path,communes,(2012,))
            self.assertEqual(frame[frame.cut=='16103'].value_state.iloc[0],'formula_without_cached_value')
            s.cell(9,3,'PINTO');s.cell(9,4,1);w.save(path)
            with self.assertRaisesRegex(ValueError,'Duplicate commune'):extract_workbook(path,communes,(2012,))
            s.cell(9,3).value=None;s.cell(3,1,'2013-2014');w.save(path)
            with self.assertRaisesRegex(ValueError,'mismatch'):extract_workbook(path,communes,(2012,))
            s.cell(3,1,'2012-2013');s.cell(4,4,'NUMERO FOCOS');w.save(path)
            with self.assertRaisesRegex(ValueError,'Unsupported'):extract_workbook(path,communes,(2012,))
            s.cell(4,4,'NUMERO INCENDIOS');s.cell(8,3,'COMUNA DESCONOCIDA');w.save(path)
            with self.assertRaisesRegex(ValueError,'Unmatched'):extract_workbook(path,communes,(2012,))
            w.close()

    def test_ranks_ties_missing_and_constant_series(self):
        self.assertAlmostEqual(spearman([1,2,2,4],[4,1,1,2]),-1/3)
        self.assertAlmostEqual(spearman([1,2,np.nan,3],[3,2,99,1]),-1)
        self.assertIsNone(spearman([0,0,0],[1,2,3]))
        self.assertIsNone(spearman([1],[2]))
        with self.assertRaises(ValueError):spearman([1,np.inf],[1,2])

    def test_regional_panels_hold_territory_constant(self):
        pairs=pd.DataFrame({'cut':['A']*3+['B']*3,'season':[1,2,3]*2,
            'conaf_occurrences':[1,2,3,10,np.nan,30],'snpp_cell_days':[2,3,4,20,30,40]})
        primary,sensitivity,cuts=regional_panels(pairs)
        self.assertEqual(cuts,['A'])
        self.assertEqual(primary.conaf_occurrences.tolist(),[1,2,3])
        self.assertEqual(sensitivity.season.tolist(),[1,3])
        self.assertEqual(sensitivity.conaf_occurrences.tolist(),[11,33])
        with self.assertRaises(ValueError):regional_panels(pd.concat([pairs,pairs.iloc[:1]]))

    def test_bootstrap_reproducibility_and_degenerate_draws(self):
        frame=pd.DataFrame({'snpp_cell_days':[1,2],'conaf_occurrences':[5,8]})
        a=bootstrap_rank(frame,100);b=bootstrap_rank(frame,100)
        self.assertEqual(a,b);self.assertGreater(a['degenerate_replicates'],0)
        self.assertEqual(a['valid_replicates']+a['degenerate_replicates'],100)
        self.assertAlmostEqual(a['rho'],1)


if __name__=='__main__':unittest.main()
