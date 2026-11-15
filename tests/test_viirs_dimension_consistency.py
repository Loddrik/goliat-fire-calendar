import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from viirs_dimension_consistency import (aggregation_I, deduplicate, unique_center_associations,
                                         gate, measures, in_interval, hhmm, verified_rows, digest)


def record(**changes):
    d = {"acq_date": "2023-02-10", "acq_time": "1830", "latitude": "-37", "longitude": "-72.5",
         "scan": ".4", "track": ".5", "source_file": "a.csv", "source_csv": "commune.csv"}
    d.update(changes)
    return d


class SelectiveDimensionTests(unittest.TestCase):
    def test_I_band_boundaries_explicit_not_M_band_indices(self):
        expected = [(0, 1), (1279, 1), (1280, 2), (2015, 2), (2016, 3),
                    (4383, 3), (4384, 2), (5119, 2), (5120, 1), (6399, 1)]
        for col, factor in expected:
            self.assertEqual(aggregation_I(col)["factor"], factor)
        for col in [-1, 6400, 1.5, True]:
            with self.assertRaises(ValueError):
                aggregation_I(col)

    def test_source_dedup_keeps_conflicts_without_favorable_dimensions(self):
        same = deduplicate([record(), record(scan=".400")])
        self.assertEqual(len(same), 1)
        self.assertEqual(same[0]["duplicate_count"], 2)
        self.assertEqual(same[0]["source_state"], "reference_candidate")
        conflict = deduplicate([record(), record(scan=".8")])
        self.assertEqual(conflict[0]["source_state"], "ambiguous_source_geometry")
        self.assertEqual(deduplicate([record(scan="nan")])[0]["source_state"], "invalid_reference_dimensions")

    def test_unique25_and75_are_separate_no_nearest_ambiguity_rescue(self):
        centers = np.array([[0., 0.], [60., 0.]])
        self.assertEqual(unique_center_associations([[0, 0]], centers, 25)[0]["state"], "unique_center")
        self.assertEqual(unique_center_associations([[0, 0]], centers, 75)[0]["state"], "ambiguous_centers")
        self.assertEqual(unique_center_associations([[100, 100]], centers, 25)[0]["state"], "unmatched")
        self.assertEqual(unique_center_associations([[25, 0]], centers, 25)[0]["state"], "unique_center")

    def test_two_source_identities_for_one_center_are_both_rejected(self):
        records = unique_center_associations([[0, 0], [1, 0]], np.array([[0., 0.]]), 25)
        self.assertTrue(all(r["state"] == "multiple_CSV_identities_for_center" for r in records))

    def test_time_halfopen_and_invalid_numeric_like_times(self):
        start, end = "2023-02-10T18:30:00Z", "2023-02-10T18:36:00Z"
        self.assertTrue(in_interval("2023-02-10", "1830", start, end))
        self.assertFalse(in_interval("2023-02-10", "1836", start, end))
        self.assertEqual(hhmm("600"), "0600")
        for time in ["nan", "1830.0", "2400", "1860"]:
            with self.assertRaises(ValueError):
                hhmm(time)

    def test_gate_requires_five_unique_and_all_three_metric_thresholds(self):
        self.assertFalse(gate([0] * 4))
        self.assertTrue(gate([.2] * 5))
        self.assertFalse(gate([.21] * 5))
        self.assertFalse(gate([0] * 8 + [.4, .4]))

    def test_complete_polygon_is_not_AOI_clipped_for_dimension_measurement(self):
        from shapely.geometry import Polygon, box
        p = Polygon([(0, 0), (400, 0), (400, 500), (0, 500)])
        scan, track, area = measures(p)
        self.assertEqual((scan, track, area), (400, 500, 200000))
        self.assertNotEqual(measures(p.intersection(box(0, 0, 200, 500)))[2], area)

    def test_manifest_integrity_and_platform_cohort_fail_closed(self):
        fields = "latitude,longitude,acq_date,acq_time,satellite,instrument,daynight,type,confidence,version,cut_com,source_file\n"
        body = "-37,-72.5,2023-02-10,1830,N,VIIRS,D,0,n,2,08101,a.csv\n"
        payload = (fields + body).encode()
        segment = {"sha256": digest(payload), "bytes": len(payload), "rows": 1, "cut": "08101"}
        source = {"files": [{"filename": "a.csv", "year": 2023}], "versions": ["2"]}
        self.assertEqual(len(verified_rows(payload, segment, source)), 1)
        with self.assertRaises(ValueError):
            verified_rows(payload + b"x", segment, source)
        wrong = (fields + body.replace(",N,", ",N20,")).encode()
        segment = {**segment, "sha256": digest(wrong), "bytes": len(wrong)}
        with self.assertRaises(ValueError):
            verified_rows(wrong, segment, source)


if __name__ == "__main__":
    unittest.main()
