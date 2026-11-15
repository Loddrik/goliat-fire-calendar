import csv
import hashlib
import contextlib
import io
import json
import shutil
from pathlib import Path
import tempfile
import unittest

from pipeline.verify_raw_inventory import InventoryError, main, verify_inventory


class RawInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inventory = self.root / "inventory.csv"
        self.rows = []
        for i, content in enumerate((b"a,b\n1,2\n", b"x\n", b"")):
            rel = f"data/raw/sensor/{i}.csv"
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(content)
            self.rows.append({"path": rel, "bytes": len(content),
                              "sha256": hashlib.sha256(content).hexdigest()})
        self.write_inventory()

    def write_inventory(self):
        with self.inventory.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["path", "bytes", "sha256"])
            writer.writeheader()
            writer.writerows(self.rows)

    def verify(self):
        return verify_inventory(self.root, self.inventory, details=True, expected_count=3,
                                expected_inventory_sha256=None)

    def test_complete_and_inputs_preserved(self):
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result = self.verify()
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(result["exact_files"], 3)
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_missing(self):
        (self.root / self.rows[0]["path"]).unlink()
        result = self.verify()
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertEqual(result["missing"], [self.rows[0]["path"]])

    def test_absent_raw_directory_is_incomplete(self):
        shutil.rmtree(self.root / "data/raw")
        result = self.verify()
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertEqual(result["missing_files"], 3)

    def test_same_size_tampering(self):
        (self.root / self.rows[1]["path"]).write_bytes(b"y\n")
        result = self.verify()
        self.assertEqual(result["different_files"], 1)
        self.assertEqual(result["status"], "INCOMPLETE")

    def test_additional_csv_invalidates_otherwise_complete_set(self):
        extra = self.root / "data/raw/sensor/unverified.csv"
        extra.write_bytes(b"not an inventoried original")
        result = self.verify()
        self.assertEqual(result["exact_files"], 3)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertEqual(result["additional"], ["data/raw/sensor/unverified.csv"])

    def test_unsafe_inventory_paths(self):
        for path in ("/tmp/private.csv", "data/raw/../private.csv", "data/raw//x.csv",
                     "data/raw/./x.csv", "data/raw\\x.csv", "other/file.csv"):
            with self.subTest(path=path):
                self.rows[0]["path"] = path
                self.write_inventory()
                with self.assertRaises(InventoryError):
                    self.verify()

    def test_duplicate_and_invalid_hash(self):
        self.rows[1]["path"] = self.rows[0]["path"]
        self.write_inventory()
        with self.assertRaises(InventoryError):
            self.verify()
        self.rows[1]["path"] = "data/raw/unique.csv"
        self.rows[1]["sha256"] = "z" * 64
        self.write_inventory()
        with self.assertRaises(InventoryError):
            self.verify()

    def test_symlink_escape(self):
        target = self.root / "outside.csv"
        target.write_bytes(b"x\n")
        p = self.root / self.rows[1]["path"]
        p.unlink()
        p.symlink_to(target)
        with self.assertRaises(InventoryError):
            self.verify()

    def test_default_contract_does_not_accept_tiny_inventory(self):
        with self.assertRaises(InventoryError):
            verify_inventory(self.root, self.inventory)

    def test_cli_rejects_replacement_inventory_with_json_and_exit_two(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["--root", str(self.root), "--inventory", str(self.inventory)])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
