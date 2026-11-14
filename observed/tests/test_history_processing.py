import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from prepare_history import eligible, months_for


class ProcessingTests(unittest.TestCase):
    def setUp(self):
        self.row = {"latitude": "-36.5", "longitude": "-72.5", "acq_date": "2023-02-01",
                    "acq_time": "1200", "satellite": "Aqua", "daynight": "D", "confidence": "80", "type": "0"}

    def test_aqua_is_separate_from_terra(self):
        self.assertIsNone(eligible(self.row, "modis", 2023))
        self.assertEqual(eligible({**self.row, "satellite": "Terra"}, "modis", 2023), "other_platform")

    def test_type_filter_has_an_explicit_unknown_case(self):
        for kind in ("1", "2", "3", ""):
            self.assertEqual(eligible({**self.row, "type": kind}, "modis", 2023), "non_vegetation_or_unknown_type")

    def test_night_and_confidence(self):
        self.assertEqual(eligible({**self.row, "daynight": "N"}, "modis", 2023), "night_or_unknown")
        self.assertEqual(eligible({**self.row, "confidence": "nan"}, "modis", 2023), "confidence")
        self.assertEqual(eligible({**self.row, "satellite": "N", "confidence": "l"}, "viirs-snpp", 2023), "confidence")

    def test_cross_year_rows_are_not_used_twice(self):
        self.assertEqual(eligible(self.row, "modis", 2022), "outside_file_year")

    def test_missing_year_does_not_gain_zero_months(self):
        months = months_for({"start": "2022-07"}, [{"year": 2022}, {"year": 2024}])
        self.assertEqual(len(months), 18)
        self.assertFalse(any(month.startswith("2023") for month in months))
        self.assertEqual(months[0], "2022-07")


if __name__ == "__main__":
    unittest.main()
