#!/usr/bin/env python3
"""Mutate fixed linkage evidence without changing the private target or artifacts."""
import copy
import csv
from pathlib import Path
import tempfile
import unittest

from strict_oracle import Context, Incomplete, ROOT, reviewed_linkages, replay_owner


class ReviewedLinkageControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        with (ROOT / "config/linkage-bindings.csv").open() as stream:
            cls.rows = list(csv.DictReader(stream))

    def check_rows(self, rows):
        with tempfile.TemporaryDirectory(dir=ROOT / ".analysis") as directory:
            path = Path(directory) / "bindings.csv"
            with path.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=rows[0])
                writer.writeheader()
                writer.writerows(rows)
            return reviewed_linkages(self.context, path)

    def test_fixed_bindings_pass(self):
        self.assertEqual(len(self.check_rows(self.rows)), 8)

    def test_wrong_extent_hash_is_rejected(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["target_sha256"] = "0" * 64
        with self.assertRaisesRegex(Incomplete, "hash mismatch"):
            self.check_rows(rows)

    def test_wrong_literal_witness_is_rejected(self):
        rows = copy.deepcopy(self.rows)
        next(r for r in rows if r["kind"] == "literal")["witness_instruction"] = "0x00402CD0"
        with self.assertRaisesRegex(Incomplete, "instruction witness"):
            self.check_rows(rows)

    def test_wrong_runtime_library_is_rejected(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["candidate_library"] = "unreviewed.lib"
        with self.assertRaisesRegex(Incomplete, "pinned Microsoft library"):
            self.check_rows(rows)

    def test_security_check_complete_owner_replays(self):
        context = self.context
        function = next(r for r in context.linked["functions"] if r["symbol"] == "@__security_check_cookie@4")
        unit = dict(size=17, compare_size=17, target_address=0x47499B, linkages=[
            dict(offset=2, type="DIR32", symbol="___security_cookie", target=0x49EA4C),
            dict(offset=13, type="REL32", symbol="___report_gsfailure", target=0x474F5D)])
        self.assertEqual(replay_owner(context.image, context.target, context.publics, function, unit)["result"], "exact")

    @classmethod
    def tearDownClass(cls):
        cls.context.finish()


if __name__ == "__main__":
    unittest.main()
