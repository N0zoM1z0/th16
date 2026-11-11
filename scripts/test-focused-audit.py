#!/usr/bin/env python3
"""Verify that focused audits replay complete owners without replacing ledgers."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = [ROOT / ".analysis/reference-audit.json"] + [
    ROOT / "config" / name for name in [
        "match-units.toml", "matches.csv", "functions.csv",
        "reference-functions.csv", "function-boundaries.csv", "reccmp-functions.csv",
    ]
]


class FocusedAuditControls(unittest.TestCase):
    def setUp(self):
        self.before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in CANONICAL}
        self.directory = tempfile.TemporaryDirectory(dir=ROOT / ".analysis")
        self.report = Path(self.directory.name) / "focused.json"

    def tearDown(self):
        self.directory.cleanup()
        self.assertEqual(self.before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in CANONICAL})

    def run_audit(self, *arguments):
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts/audit-reference.py"), *map(str, arguments)],
            cwd=ROOT, capture_output=True, text=True, timeout=60,
        )

    def test_focused_replay_deduplicates_addresses_and_keeps_canonical_outputs(self):
        result = self.run_audit("--address", "0x4029d0", "--address", "0x4029d0",
                                "--json", self.report)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(self.report.read_text())
        self.assertEqual(report["counts"], {"exact": 1})
        self.assertEqual(len(report["functions"]), 1)
        owner = report["functions"][0]
        self.assertEqual(owner["target_address"], 0x4029D0)
        self.assertEqual(owner["compared_size"], 193)

    def test_partial_audit_cannot_replace_canonical_outputs(self):
        for arguments in [
            ["--address", "0x4029d0"],
            ["--address", "0x4029d0", "--write-units", "--json", self.report],
            ["--address", "0x4029d0", "--json", CANONICAL[0]],
            ["--address", "0x4029d0", "--json", ROOT / "config/matches.csv"],
            ["--write-units", "--json", self.report],
        ]:
            with self.subTest(arguments=arguments):
                result = self.run_audit(*arguments)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertFalse(self.report.exists())

    def test_unannotated_address_is_rejected_without_a_report(self):
        result = self.run_audit("--address", "0xffffffff", "--json", self.report)
        self.assertEqual(result.returncode, 2)
        self.assertIn("unannotated original addresses", result.stderr)
        self.assertFalse(self.report.exists())


if __name__ == "__main__":
    unittest.main()
