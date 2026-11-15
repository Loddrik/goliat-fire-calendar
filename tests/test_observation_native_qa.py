import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from observation_native_qa import inventory, local_screen, plain, validate_shapes


class ArrayField:
    def __init__(self, values, attrs=None):
        self.values = np.asarray(values)
        self.shape = self.values.shape
        self.attrs = attrs or {}

    def __getitem__(self, key):
        return self.values[key]


class IdentityProjection:
    def transform(self, x, y):
        return x, y


class NativeQATests(unittest.TestCase):
    def test_nested_native_byte_attributes_are_json_serializable(self):
        import json
        attrs = {"legend": np.array([b"water", b"land"])}
        self.assertEqual(json.loads(json.dumps(plain(attrs))), {"legend": ["water", "land"]})

    def fields(self):
        # Ten native detector rows; deliberately no nearest-neighbor resampling.
        mask = np.full((10, 1), 5, dtype=np.uint8)
        qa = np.full((10, 1), 2, dtype=np.uint32)
        lat, lon = np.zeros((10, 1)), np.zeros((10, 1))
        geo = np.zeros((10, 1), dtype=np.uint8)
        return [ArrayField(x) for x in [mask, qa, lat, lon, geo]]

    def test_exhaustive_mask_fill_unknown_and_reserved_qa_reconcile(self):
        f = self.fields()
        f[0].values[:, 0] = [0, 3, 5, 7, 8, 9, 4, 6, 254, 255]
        f[0].attrs = {"_FillValue": 254}
        f[1].values[1] = 0  # Water, not MODLAND optimum confidence.
        f[1].values[2] = 0xFFFFFFFF
        f[1].values[3] = 2 | (1 << 6)
        f[1].attrs = {"_FillValue": 0xFFFFFFFF}
        r = inventory("MYD14", "061", *f, IdentityProjection(), [0, 0])
        c = r["counts"]
        self.assertEqual(c["mask_partition"], {"known": 8, "fill": 1, "unknown": 1})
        self.assertEqual(c["qa_partition"]["fill"], 1)
        self.assertEqual(c["qa_partition"]["reserved_bits_active"], 1)
        self.assertEqual(sum(c["qa_partition"].values()), 10)
        self.assertEqual(sum(c["mask_classes"].values()), 8)
        self.assertEqual(c["mask_classes"]["7:low_confidence_detection"], 1)
        self.assertTrue(r["all_exhaustive_partitions_reconciled"])

    def test_geoflag_inside_is_counted_but_not_a_local_candidate(self):
        f = self.fields()
        f[4].values[0] = 128
        f[2].values[1] = 100  # Invalid latitude; cannot be placed in the AOI.
        r = inventory("MYD14", "061", *f, IdentityProjection(), [0, 0])
        c = r["counts"]
        self.assertEqual(c["partition"]["inside_aoi"], 9)
        self.assertEqual(c["partition"]["unassignable_invalid_coordinates"], 1)
        self.assertEqual(c["geo_partition"]["documented_active_bits"], 1)
        self.assertEqual(c["local_screen_states"]["local_candidate"], 8)
        self.assertEqual(c["local_exclusion_reasons"]["geolocation_policy_not_accepted"], 1)
        self.assertEqual(sum(c["partition"].values()), 10)

    def test_native_shape_mismatch_and_wrong_scan_multiple_raise(self):
        f = self.fields()
        with self.assertRaises(ValueError):
            validate_shapes(f + [ArrayField(np.zeros((1, 10)))], 10)
        with self.assertRaises(ValueError):
            validate_shapes(f, 32)
        f[1] = ArrayField(f[1].values.astype(np.int32))
        with self.assertRaisesRegex(ValueError, "dtype"):
            inventory("MYD14", "061", *f, IdentityProjection(), [0, 0])

    def test_water_land_and_low_confidence_remain_distinct(self):
        water = local_screen("MYD14", "061", 3, 0, 0)
        land = local_screen("MYD14", "061", 5, 2, 0)
        low = local_screen("MYD14", "061", 7, 2, 0)
        self.assertEqual([x["state"] for x in [water, land, low]], ["local_candidate"] * 3)
        self.assertEqual([water["surface"], land["surface"]], ["water", "land"])
        self.assertTrue(low["mask"]["detection"])
        self.assertFalse(low["mask"]["no_detection"])

    def test_viirs_mask_vs_qa_and_detection_tests_are_not_quality_failures(self):
        self.assertEqual(local_screen("VNP14IMG", "002", 1, 0, 0)["state"], "excluded")
        self.assertIn("input_quality_non_nominal", local_screen("VNP14IMG", "002", 5, 2, 0)["excluded"])
        r = local_screen("VNP14IMG", "002", 9, 1 << 16, 0)
        self.assertEqual(r["state"], "local_candidate")
        self.assertEqual(r["surface"], "detection_surface_unknown")
        self.assertIn("requires_separate_land_water_mask", r["cautions"])

    def test_local_screen_has_no_fake_global_pass_and_does_not_clear_glint(self):
        with self.assertRaises(TypeError):
            local_screen("MYD14", "061", 5, 2, 0, global_quality_flag="Passed")
        r = local_screen("MYD14", "061", 5, 2 | (1 << 22), 0)
        self.assertEqual(r["state"], "unresolved")
        # Neither scientific acceptance nor substituted zero observations exists.
        self.assertNotIn("gate1_passed", r)
        self.assertNotIn("accepted_scientific_count", r)


if __name__ == "__main__":
    unittest.main()
