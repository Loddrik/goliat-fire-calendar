import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from observation_preflight import interval_bounds,time_state,candidate_pairs,acquisition_key,public_url,fetch_granules


def entry(name,start,end,identity='a'):
    return {'id':identity,'producer_granule_id':name,'time_start':start,'time_end':end,'day_night_flag':'DAY'}


class ObservationPreflightTests(unittest.TestCase):
    def test_interval_edges_do_not_invent_pixel_simultaneity(self):
        a=entry('MYD14.A2019001.1800.061.x','2019-01-01T18:00:00Z','2019-01-01T18:05:00Z')
        b=entry('VNP14IMG.A2019001.1809.002.x','2019-01-01T18:09:00Z','2019-01-01T18:15:00Z')
        self.assertEqual(interval_bounds(a,b),(4.,15.))
        self.assertEqual(time_state(4,15,10),'uncertain')
        self.assertEqual(time_state(4,15,15),'definitely_within')
        self.assertEqual(time_state(4,15,3),'definitely_outside')
        self.assertEqual(interval_bounds(b,a),(4.,15.))

    def test_overlapping_intervals_can_still_be_temporally_uncertain(self):
        a=entry('A','2019-01-01T18:00:00Z','2019-01-01T18:05:00Z')
        b=entry('B','2019-01-01T18:03:00Z','2019-01-01T18:09:00Z')
        self.assertEqual(interval_bounds(a,b),(0.,9.))
        self.assertEqual(time_state(*interval_bounds(a,b),5),'uncertain')
        bad=dict(a,time_end='2019-01-01T17:59:00Z')
        with self.assertRaises(ValueError):interval_bounds(bad,b)

    def test_many_to_many_candidates_are_order_invariant_and_no_outcomes_used(self):
        aqua=[entry('MYD14.A2019001.1800.061.x','2019-01-01T18:00:00Z','2019-01-01T18:05:00Z','a'),
              entry('MYD14.A2019001.1805.061.x','2019-01-01T18:05:00Z','2019-01-01T18:10:00Z','b')]
        viirs=[entry('VNP14IMG.A2019001.1800.002.x','2019-01-01T18:00:00Z','2019-01-01T18:06:00Z','c')]
        first=candidate_pairs(aqua,viirs)
        for x in aqua+viirs:x['detection_count']=1000000
        self.assertEqual(first,candidate_pairs(aqua[::-1],viirs))
        self.assertEqual(len(first),2)
        self.assertEqual(acquisition_key(aqua[0]),('2019001','1800'))

    def test_public_evidence_strips_credential_material(self):
        self.assertEqual(public_url('https://user:secret@host.example/data.hdf?token=secret#fragment'),'https://host.example/data.hdf')

    def test_incomplete_inventory_and_duplicate_records_are_rejected(self):
        def incomplete(*args):return {'feed':{'entry':[{'id':'one'}]}},2,'https://example.test'
        with self.assertRaisesRegex(ValueError,'Incomplete'):fetch_granules('pinned',fetch=incomplete)
        def duplicate(*args):return {'feed':{'entry':[{'id':'one'},{'id':'one'}]}},2,'https://example.test'
        with self.assertRaisesRegex(ValueError,'Duplicate'):fetch_granules('pinned',fetch=duplicate)

if __name__=='__main__':unittest.main()
