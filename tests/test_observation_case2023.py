import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from observation_case2023 import (EXTRA_CAP, TOTAL_CAP, PREVIOUS_BYTES, choose_pair,
                                   unique_geo, remaining_budget, native_url, scrub_links)


def entry(name, start="2023-02-03T18:00:00Z", end="2023-02-03T18:05:00Z", day="DAY"):
    return {"producer_granule_id": name, "time_start": start, "time_end": end, "day_night_flag": day}


class Case2023Tests(unittest.TestCase):
    def test_selection_uses_fixed_chronology_not_outcomes_or_input_order(self):
        a = [entry("MYD14.A2023034.1800.061.z"), entry("MYD14.A2023034.1800.061.a")]
        v = [entry("VNP14IMG.A2023034.1800.002.z")]
        chosen, _ = choose_pair(a, v)
        self.assertEqual(chosen["aqua_id"], "MYD14.A2023034.1800.061.a")
        for e in a + v:
            e["fire_count"] = 1000000
        self.assertEqual(choose_pair(a[::-1], v)[0], chosen)

    def test_night_and_exclusive_upper_date_are_excluded(self):
        a = [entry("MYD14.A2023034.1800.061.a", day="NIGHT")]
        v = [entry("VNP14IMG.A2023034.1800.002.a")]
        self.assertIsNone(choose_pair(a, v)[0])
        late = entry("MYD14.A2023042.0000.061.a", "2023-02-11T00:00:00Z", "2023-02-11T00:05:00Z")
        self.assertIsNone(choose_pair([late], [late])[0])

    def test_maximum_interval_gap_not_start_gap_controls_gate(self):
        a = entry("MYD14.A2023034.1800.061.a")
        v = entry("VNP14IMG.A2023034.1809.002.a", "2023-02-03T18:09:00Z", "2023-02-03T18:15:00Z")
        self.assertIsNone(choose_pair([a], [v])[0])
        v["time_start"], v["time_end"] = "2023-02-03T18:04:00Z", "2023-02-03T18:10:00Z"
        self.assertEqual(choose_pair([a], [v])[0]["maximum_gap_minutes"], 10)

    def test_unique_geo_is_identifier_match_not_temporal_nearest(self):
        a = entry("MYD14.A2023034.1800.061.a")
        g = entry("MYD03.A2023034.1800.061.a")
        self.assertEqual(unique_geo(a, [g]), g)
        for values in [[], [g, dict(g)]]:
            with self.assertRaises(ValueError):
                unique_geo(a, values)

    def test_extra_and_total_caps_include_failed_transfer_spending(self):
        self.assertEqual(remaining_budget(0), EXTRA_CAP)
        self.assertLessEqual(PREVIOUS_BYTES + EXTRA_CAP, TOTAL_CAP)
        self.assertEqual(remaining_budget(EXTRA_CAP), 0)
        self.assertEqual(remaining_budget(100, previous=TOTAL_CAP - 101), 1)
        self.assertEqual(remaining_budget(101, previous=TOTAL_CAP - 101), 0)

    def test_native_urls_require_exact_host_and_public_metadata_redacts_query(self):
        e = entry("MYD14.A2023034.1800.061.a")
        e["links"] = [{"rel": "https://example.test/data#", "href": "https://data.lpdaac.earthdatacloud.nasa.gov/file?secret=not-real"}]
        self.assertIn("?secret=", native_url(e))
        public = scrub_links(e)
        self.assertNotIn("?", public["links"][0]["href"])
        e["links"][0]["href"] = "https://data.lpdaac.earthdatacloud.nasa.gov.evil.test/file"
        with self.assertRaises(ValueError):
            native_url(e)


if __name__ == "__main__":
    unittest.main()
