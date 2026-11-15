import datetime as dt
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from platform_bridge_audit import season_dates,requested_days,complete_seasons,metrics,bootstrap_ratio,overlap,paired_months


class PlatformBridgeTests(unittest.TestCase):
    def test_season_dates_include_leap_day_and_correct_edges(self):
        dates=season_dates(2019)
        self.assertEqual(len(dates),366);self.assertIn(dt.date(2020,2,29),dates)
        self.assertIn(dt.date(2019,7,1),dates);self.assertIn(dt.date(2020,6,30),dates)
        self.assertNotIn(dt.date(2019,6,30),dates);self.assertNotIn(dt.date(2020,7,1),dates)

    def test_requested_intervals_are_not_detection_coverage(self):
        paths=['data/raw/firms_country/viirs-snpp/viirs-snpp_2020_Chile.csv',
               'data/raw/firms_api/VIIRS_SNPP_SP/VIIRS_SNPP_SP_2021-01-01_5d.csv',
               'data/raw/firms_api/VIIRS_SNPP_NRT/VIIRS_SNPP_NRT_2021-01-06_5d.csv']
        days=requested_days(paths,'SNPP')
        self.assertEqual(len(days),371);self.assertIn(dt.date(2021,1,5),days);self.assertNotIn(dt.date(2021,1,6),days)

    def test_missing_requested_day_excludes_whole_season(self):
        complete=season_dates(2019);partial=complete-{dt.date(2020,2,29)}
        valid,excluded=complete_seasons([2019],complete,partial)
        self.assertEqual(valid,[]);self.assertEqual(excluded[0]['comparator_missing_requested_days'],1)

    def test_zero_denominators_are_not_invented_ratios(self):
        f=pd.DataFrame({'reference':[0,0],'comparator':[0,2],'provisional':[False,False]})
        result=metrics(f)
        self.assertIsNone(result['ratio']);self.assertIsNone(result['wape']);self.assertEqual(result['comparator'],2.)

    def test_bootstrap_pairs_whole_seasons(self):
        f=pd.DataFrame({'reference':[10.,20.],'comparator':[10.,20.]})
        result=bootstrap_ratio(f);self.assertEqual(result['interval'],[1.,1.]);self.assertEqual(result['blocks'],2)
        self.assertEqual(result['valid_replicates'],5000)
        self.assertIsNone(bootstrap_ratio(f.iloc[:1])['interval'])

    def test_overlap_is_positive_set_concordance(self):
        result=overlap({1,2},{2,3})
        self.assertEqual(result['intersection'],1);self.assertEqual(result['union'],3);self.assertAlmostEqual(result['jaccard'],1/3)
        self.assertIsNone(overlap(set(),set())['jaccard'])

    def test_paired_months_preserve_platforms_and_unknown_coverage(self):
        monthly=pd.DataFrame({'cut':['A','A'],'season':[2019,2019],'m':[7,7],'sat':['SNPP','NOAA20'],'cell_days':[2,3],'provisional':[False,False]})
        result=paired_months(monthly,['A'],[2019],'SNPP','NOAA20')
        self.assertEqual(len(result),12);self.assertEqual(result.reference.sum(),2);self.assertEqual(result.comparator.sum(),3)
        self.assertEqual(set(result.observation_coverage),{'unknown'})


if __name__=='__main__':unittest.main()
