import sys,unittest
from pathlib import Path
from datetime import date
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from daily_adjacency_cube import calendar_year,season_of,month_columns,hash_permutation,permute_columns,adjacency,preserve,regimes_from_code
class DailyAdjacencyTests(unittest.TestCase):
    def test_same_cell_required_not_any_cell_each_day(self):
        self.assertEqual(adjacency(month_columns([((1,1),1),((2,2),2)],2015,1)),(0,0))
        self.assertEqual(adjacency(month_columns([((1,1),1),((1,1),2)],2015,1)),(1,1))
    def test_calendar_leaps_and_season(self):
        self.assertEqual(calendar_year(2015,2),2016);self.assertEqual(calendar_year(2019,2),2020)
        self.assertEqual(len(month_columns([],2016,2)),29);self.assertEqual(len(month_columns([],2015,2)),28)
        self.assertEqual(season_of(date(2016,6,30)),2015);self.assertEqual(season_of(date(2016,7,1)),2016)
    def test_no_pair_across_month_year_or_season(self):
        for year,month,day in [(2015,12,31),(2016,1,1),(2016,6,30),(2016,7,1)]:self.assertEqual(adjacency(month_columns([((1,1),day)],year,month)),(0,0))
    def test_empty_or_one_record_Dzero(self):
        self.assertEqual(adjacency(month_columns([],2020,2)),(0,0));self.assertEqual(adjacency(month_columns([((1,2),29)],2020,2)),(0,0))
    def test_duplicate_is_not_silently_deduplicated(self):
        with self.assertRaises(ValueError):month_columns([((1,1),2),((1,1),2)],2016,1)
    def test_fullcalendar_joint_permutation_includes_zero_columns(self):
        c=month_columns([((1,1),1),((2,2),1),((1,1),3)],2016,2);mapping=hash_permutation('08101',2016,2);other=permute_columns(c,mapping)
        self.assertEqual(len(mapping),29);self.assertEqual(other[mapping[0]-1],c[0]);self.assertTrue(preserve(c,other));self.assertEqual(mapping,hash_permutation('08101',2016,2))
    def test_individual_cell_shuffle_breaks_set_invariant(self):
        c=[frozenset({(1,1),(2,2)}),frozenset()];bad=[frozenset({(1,1)}),frozenset({(2,2)})]
        with self.assertRaises(ValueError):preserve(c,bad)
    def test_permutation_may_preserve_D(self):
        c=[frozenset({(1,1)}) for _ in range(31)];other=permute_columns(c,hash_permutation('08101',2015,1));self.assertEqual(adjacency(c),adjacency(other))
    def test_regimes_expression_only_not_module_import(self):
        text="REGIMES={f'{region}_{direction}':(region,origin,dest) for region in ('08','16') for direction,origin,dest in [('forward',(2012,2013,2014,2015),(2016,2017,2018,2019)),('backward',(2016,2017,2018,2019),(2012,2013,2014,2015))]}"
        self.assertEqual(len(regimes_from_code(text)),4)
        with self.assertRaises(ValueError):regimes_from_code("REGIMES=print('not allowed')")
if __name__=='__main__':unittest.main()
