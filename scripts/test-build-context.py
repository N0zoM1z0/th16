#!/usr/bin/env python3
"""Exercise build-kind selection without changing source or stored receipts."""
from pathlib import Path
import unittest
from unittest.mock import patch

import strict_oracle
from strict_oracle import Context, Incomplete, ROOT


class BuildContextControls(unittest.TestCase):
    def test_current_artifacts_keep_the_recorded_build_kind(self):
        context = Context()
        self.assertIn(context.receipt["coldness"], {"incremental", "clean-output-graph"})
        context.finish()

    def test_explicit_cold_requirement_is_enforced(self):
        context = Context()
        kind = context.receipt["coldness"]
        context.finish()
        if kind == "incremental":
            with self.assertRaisesRegex(Incomplete, "clean-output-graph"):
                Context(require_cold=True)
        else:
            Context(require_cold=True).finish()

    def test_incremental_mode_still_rejects_changed_source(self):
        with patch("strict_oracle.source_identity", return_value="0" * 64):
            with self.assertRaisesRegex(Incomplete, "source inputs differ"):
                Context()

    def test_incremental_mode_still_rejects_changed_artifacts(self):
        original = strict_oracle.digest
        candidate = ROOT / "build/reference-candidate/th16.exe"
        with patch("strict_oracle.digest", side_effect=lambda path: "0" * 64 if Path(path) == candidate else original(path)):
            with self.assertRaisesRegex(ValueError, "artifact hash differs"):
                Context()


if __name__ == "__main__":
    unittest.main()
