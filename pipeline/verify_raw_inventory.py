"""Read-only, standard-library verification of the frozen 1,071-file raw inventory."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
FROZEN_COUNT = 1071
FROZEN_INVENTORY_SHA256 = "97428b84e89ae70c9d87529a0239a5b4872a453f42b6f853cb51a7377b1090ad"


class InventoryError(ValueError):
    """Invalid inventory or unreadable verification input."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_inventory(path: Path, expected_count: int, expected_sha256: str | None):
    # Parse exactly the same bytes that passed the frozen hash check.
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise InventoryError("inventory SHA256 differs from the frozen inventory")
    entries = []
    seen = set()
    with io.StringIO(payload.decode("utf-8-sig"), newline="") as source:
        reader = csv.DictReader(source)
        if not {"path", "bytes", "sha256"}.issubset(reader.fieldnames or []):
            raise InventoryError("inventory requires path, bytes and sha256 columns")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise InventoryError("duplicate inventory column")
        for number, row in enumerate(reader, 2):
            raw = row.get("path") or ""
            p = PurePosixPath(raw)
            if (not raw or "\\" in raw or ":" in raw or "\x00" in raw
                    or p.is_absolute() or str(p) != raw or ".." in p.parts
                    or len(p.parts) < 3 or p.parts[:2] != ("data", "raw")):
                raise InventoryError(f"unsafe inventory path at row {number}")
            if raw in seen:
                raise InventoryError(f"duplicate inventory path at row {number}")
            n = row.get("bytes") or ""
            h = row.get("sha256") or ""
            if not re.fullmatch(r"[0-9]+", n):
                raise InventoryError(f"invalid byte count at row {number}")
            if not re.fullmatch(r"[0-9a-fA-F]{64}", h):
                raise InventoryError(f"invalid SHA256 at row {number}")
            entries.append({"path": raw, "bytes": int(n), "sha256": h.lower()})
            seen.add(raw)
            if len(entries) > expected_count:
                raise InventoryError("inventory has more entries than the declared contract")
    if len(entries) != expected_count:
        raise InventoryError(f"inventory requires exactly {expected_count} unique entries")
    return digest, entries


def verify_inventory(root: Path, inventory: Path, *, details: bool = False,
                     expected_count: int = FROZEN_COUNT,
                     expected_inventory_sha256: str | None = FROZEN_INVENTORY_SHA256) -> dict:
    """Verify bytes without writing. Override the contract only in synthetic tests."""
    root = Path(root).resolve()
    if not root.is_dir():
        raise InventoryError("root must be an existing directory")
    inventory_sha, entries = _load_inventory(Path(inventory), expected_count,
                                              expected_inventory_sha256)
    expected_paths = {item["path"] for item in entries}
    additional = []
    def walk_error(_error):
        raise InventoryError("cannot enumerate raw CSV paths")
    raw_directory = root / "data/raw"
    walk = os.walk(raw_directory, followlinks=False, onerror=walk_error) if raw_directory.exists() else ()
    for directory, directories, filenames in walk:
        # Do not silently omit a linked subtree that could supply unverified CSVs.
        if any((Path(directory) / name).is_symlink() for name in directories):
            raise InventoryError("raw tree contains a symlink directory")
        for name in filenames:
            if name.lower().endswith(".csv"):
                relative = (Path(directory) / name).relative_to(root).as_posix()
                if relative not in expected_paths:
                    additional.append(relative)
    additional.sort()
    missing, different = [], []
    exact = 0
    expected_bytes = sum(item["bytes"] for item in entries)
    exact_bytes = 0
    # Validate every resolved path before opening any raw input.
    for item in entries:
        resolved = (root / item["path"]).resolve()
        if not resolved.is_relative_to(root / "data" / "raw"):
            raise InventoryError("inventory path resolves outside root/data/raw")
    for item in entries:
        path = root / item["path"]
        try:
            before = path.stat()
        except FileNotFoundError:
            missing.append(item["path"])
            continue
        if not path.is_file():
            different.append({"path": item["path"], "reason": "not_a_regular_file"})
            continue
        actual_sha = sha256_file(path)
        after = path.stat()
        stable = all(getattr(before, field) == getattr(after, field)
                     for field in ("st_dev", "st_ino", "st_size", "st_mtime_ns"))
        if stable and after.st_size == item["bytes"] and actual_sha == item["sha256"]:
            exact += 1
            exact_bytes += item["bytes"]
        else:
            different.append({"path": item["path"],
                              "reason": "bytes_or_sha256_mismatch" if stable else "changed_during_read",
                              "expected_bytes": item["bytes"], "actual_bytes": after.st_size,
                              "expected_sha256": item["sha256"], "actual_sha256": actual_sha})
    result = {"status": "COMPLETE" if exact == expected_count and not additional else "INCOMPLETE",
              "inventory_sha256": inventory_sha, "expected_files": expected_count,
              "exact_files": exact, "missing_files": len(missing),
              "different_files": len(different), "additional_files": len(additional),
              "expected_bytes": expected_bytes,
              "exact_bytes": exact_bytes, "readonly": True}
    if details:
        result.update(missing=missing, different=different, additional=additional)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="Repository or virtual root containing data/raw/...")
    parser.add_argument("--inventory", type=Path, default=ROOT / "data/processed/inventory.csv",
                        help="Copy of the same frozen inventory (SHA256 checked)")
    parser.add_argument("--details", action="store_true", help="Include missing/different relative paths")
    args = parser.parse_args(argv)
    try:
        result = verify_inventory(args.root, args.inventory, details=args.details)
    except (InventoryError, OSError, UnicodeError, csv.Error, RuntimeError) as exc:
        # Avoid exposing OS exception text, which may contain unrelated absolute paths.
        message = str(exc) if isinstance(exc, InventoryError) else "unreadable or invalid verification input"
        print(json.dumps({"status": "ERROR", "error": message, "readonly": True}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "COMPLETE" else 1


if __name__ == "__main__":
    sys.exit(main())
