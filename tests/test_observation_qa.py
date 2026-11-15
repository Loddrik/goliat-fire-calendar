"""Synthetic specification checks; no raw observations or fitted model needed."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from observation_qa import (decode_algorithm_qa, decode_geolocation_qa, decode_mask,
                            inspect_observation, temporal_relation)


class ObservationQATests(unittest.TestCase):
    def inspect_modis(self, **changes):
        args = dict(product="MYD14", version="061", mask=5, algorithm_qa=2,
                    geolocation_qa=0, time_compatible=True,
                    common_support_verified=True, global_quality_flag="Passed")
        args.update(changes)
        return inspect_observation(**args)

    def test_collection_is_explicit_and_unknown_versions_are_not_guessed(self):
        for product, version in [("MYD14", "006"), ("MYD14", "6.1"),
                                 ("VNP14IMG", "001"), ("VNP14", "002")]:
            with self.assertRaises(ValueError):
                decode_algorithm_qa(product, version, 0)
        with self.assertRaises(ValueError):
            decode_geolocation_qa("MYD03", "007", 0)

    def test_modis_low_bits_are_surface_and_not_old_MODLAND_quality(self):
        for raw, expected in enumerate(["water", "coast", "land", "unused"]):
            q = decode_algorithm_qa("MYD14", "061", raw)
            self.assertEqual(q["fields"]["surface"], expected)
            self.assertNotIn("MODLAND_quality", q["fields"])
        # A nonzero QA value (2) correctly represents a land candidate.
        self.assertEqual(self.inspect_modis()["inspection_state"], "policy_candidate_observed_no_detection")
        self.assertIn("mask_surface_conflict", self.inspect_modis(algorithm_qa=0)["exclusion_reasons"])

    def test_modis_packed_fields_have_the_documented_offsets(self):
        raw = 2 | (1 << 4) | (9 << 7) | (1 << 20) | (1 << 21) | (3 << 22) | (1 << 24)
        f = decode_algorithm_qa("MYD14", "061", raw)["fields"]
        self.assertEqual(f["background_window_parameter"], 9)
        self.assertEqual(f["sun_glint_level"], 3)
        self.assertTrue(f["adjacent_cloud"] and f["adjacent_water"] and f["day_algorithm"])
        self.assertTrue(f["rejection_test_bits"][24])
        self.assertIn("MODIS_glint_policy_unresolved", self.inspect_modis(algorithm_qa=raw)["pending_reasons"])

    def test_viirs_mask_one_and_qa_bit_one_have_distinct_meanings(self):
        self.assertEqual(decode_mask("VNP14IMG", "002", 1)["classification"], "bowtie_deleted")
        q = decode_algorithm_qa("VNP14IMG", "002", 1 << 1)
        self.assertTrue(q["fields"]["I2_non_nominal"])
        self.assertFalse(q["fields"]["residual_bowtie"])
        self.assertTrue(decode_algorithm_qa("VNP14IMG", "002", 1 << 22)["fields"]["residual_bowtie"])

    def test_viirs_nonzero_detection_test_is_not_bad_quality_by_itself(self):
        q = decode_algorithm_qa("VNP14IMG", "002", (1 << 10) | (1 << 16))
        self.assertTrue(q["fields"]["saturation"])
        r = inspect_observation("VNP14IMG", "002", 9, (1 << 10) | (1 << 16), 0,
                                time_compatible=True, common_support_verified=True,
                                global_quality_flag="Passed")
        self.assertEqual(r["exclusion_reasons"], [])
        self.assertIn("VIIRS_surface_requires_land_water_mask", r["pending_reasons"])

    def test_each_viirs_input_quality_bit_is_separate_from_tests(self):
        for bit in range(7):
            r = inspect_observation("VNP14IMG", "002", 5, 1 << bit, 0)
            self.assertIn("VIIRS_input_quality_non_nominal", r["exclusion_reasons"])
        residual = inspect_observation("VNP14IMG", "002", 5, 1 << 22, 0)
        self.assertIn("VIIRS_residual_bowtie_policy", residual["exclusion_reasons"])

    def test_fill_unknown_and_absent_qa_are_preserved(self):
        self.assertEqual(decode_mask("MYD14", "061", 255)["status"], "unknown")
        self.assertEqual(decode_mask("MYD14", "061", 255, fill_value=255)["status"], "fill")
        self.assertFalse(decode_mask("MYD14", "061", 5, fill_value=5)["no_detection"])
        self.assertFalse(decode_mask("VNP14IMG", "002", 9, fill_value=9)["detection"])
        self.assertEqual(decode_algorithm_qa("MYD14", "061", 0xFFFFFFFF, fill_value=0xFFFFFFFF)["fields"], {})
        self.assertEqual(self.inspect_modis(mask=255)["inspection_state"], "not_observable_under_policy")
        self.assertIn("algorithm_qa_missing", self.inspect_modis(algorithm_qa=None)["pending_reasons"])
        self.assertIn("algorithm_qa_fill", self.inspect_modis(algorithm_qa=0xFFFFFFFF, algorithm_fill=0xFFFFFFFF)["exclusion_reasons"])

    def test_class_zero_cloud_unknown_are_not_no_fire(self):
        for product, version, classes in [("MYD14", "061", [0, 1, 2, 4, 6]),
                                          ("VNP14IMG", "002", [0, 1, 2, 4, 6])]:
            for value in classes:
                d = decode_mask(product, version, value)
                self.assertFalse(d["no_detection"])
                self.assertFalse(d["physical_fire_absence_inferred"])

    def test_low_confidence_is_detection_not_relabelled_as_zero(self):
        r = self.inspect_modis(mask=7)
        self.assertEqual(r["inspection_state"], "policy_candidate_detection")
        self.assertTrue(r["mask"]["detection"])
        self.assertFalse(r["mask"]["no_detection"])

    def test_water_coast_and_land_remain_distinct(self):
        water = self.inspect_modis(mask=3, algorithm_qa=0)
        coast = self.inspect_modis(mask=5, algorithm_qa=1)
        land = self.inspect_modis()
        self.assertEqual([x["surface_inspection"] for x in [water, coast, land]], ["water", "coast", "land"])
        # Policy candidates are inspection states, not pooled terrestrial support.
        self.assertTrue(all(x["gate1_passed"] is False for x in [water, coast, land]))

    def test_geolocation_fill_known_failures_and_unknown_bits_are_distinct(self):
        self.assertEqual(decode_geolocation_qa("MYD03", "061", 255)["status"], "fill")
        self.assertTrue(decode_geolocation_qa("MYD03", "061", 128)["fields"]["invalid_input"])
        self.assertEqual(decode_geolocation_qa("MYD03", "061", 1)["undocumented_active_bits"], 1)
        self.assertTrue(decode_geolocation_qa("VNP03IMG", "002", 8)["fields"]["solar_angle_bad"])
        for value in [1, 4, 32, 128, 255]:
            self.assertFalse(decode_geolocation_qa("MYD03", "061", value)["policy_accepted"])
        self.assertIn("geolocation_quality_not_accepted", self.inspect_modis(geolocation_qa=128)["exclusion_reasons"])

    def test_reserved_algorithm_bits_fail_the_conservative_policy(self):
        for bit in [6, 17, 18, 19, 29, 30, 31]:
            self.assertIn("reserved_qa_bits_active", self.inspect_modis(algorithm_qa=2 | (1 << bit))["exclusion_reasons"])

    def test_time_and_support_unknown_do_not_become_zero(self):
        r = self.inspect_modis(time_compatible=None, common_support_verified=None)
        self.assertEqual(r["inspection_state"], "eligibility_pending")
        self.assertIn("time_unknown", r["pending_reasons"])
        self.assertIn("common_support_unknown", r["pending_reasons"])
        self.assertEqual(self.inspect_modis(time_compatible=False)["inspection_state"], "not_observable_under_policy")

    def test_suspect_is_quarantined_even_if_local_fields_pass(self):
        r = self.inspect_modis(global_quality_flag="Suspect")
        self.assertEqual(r["inspection_state"], "eligibility_pending")
        self.assertIn("global_quality_suspect_quarantine", r["pending_reasons"])
        self.assertFalse(r["scientific_eligibility_certified"])
        self.assertFalse(r["gate1_passed"])

    def test_conservative_time_boundaries_and_symmetry(self):
        a, b = (0, 300), (180, 540)
        self.assertEqual(temporal_relation(a, b, 600)["state"], "within")
        self.assertEqual(temporal_relation(a, b, 300)["state"], "time_uncertain")
        self.assertEqual(temporal_relation(a, b), temporal_relation(b, a))
        self.assertEqual(temporal_relation((0, 1), (602, 603), 600)["state"], "outside")
        self.assertEqual(temporal_relation((0, 1), (601, 602), 600)["state"], "time_uncertain")
        self.assertEqual(temporal_relation(None, b)["state"], "time_unknown")

    def test_invalid_numerical_inputs_and_implicit_boolean_states_rejected(self):
        for value in [-1, 1 << 32, 2.5, True]:
            with self.assertRaises(ValueError):
                decode_algorithm_qa("MYD14", "061", value)
        for a, b, threshold in [((1, 0), (0, 1), 600), ((0, float("nan")), (0, 1), 600),
                                 ((0, 1), (0, 1), -1)]:
            with self.assertRaises(ValueError):
                temporal_relation(a, b, threshold)
        with self.assertRaises(ValueError):
            self.inspect_modis(common_support_verified=1)


if __name__ == "__main__":
    unittest.main()
