#!/usr/bin/env python3
"""Controls for the non-exact frontier ratchet (scripts/check-frontier.py)."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("check_frontier", ROOT / "scripts/check-frontier.py")
frontier = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(frontier)

ORIGINAL = bytes(range(16))


def row(candidate: bytes, result="mismatch", linkages=()):
    replayed = bytearray(candidate)
    for field in linkages:
        offset, width = field["offset"], field["width"]
        replayed[offset:offset + width] = field["encoded"].to_bytes(
            width, "little", signed=field["type"] == "REL32"
        )
    return {"target_address": 0x401000, "candidate_address": 0x402000, "symbol": "?f@@YAXXZ",
            "source": "src/F.cpp", "size": 16, "result": result, "compared_size": 16,
            "linkages": list(linkages),
            "matched_bytes": sum(left == right for left, right in zip(ORIGINAL, replayed))}


def entry(candidate: bytes, **kw):
    return frontier.measure(row(candidate, **kw), lambda a, n: ORIGINAL, lambda a, n: candidate)


def changed(*offsets):
    data = bytearray(ORIGINAL)
    for offset in offsets:
        data[offset] ^= 0xFF
    return bytes(data)


class FrontierControls(unittest.TestCase):
    def test_replayed_linkage_replaces_raw_candidate_bytes(self):
        field = dict(offset=0, width=4, type="DIR32", encoded=0x03020100)
        self.assertEqual(entry(changed(2, 3, 9), linkages=[field])["residual"], ["9"])

    def test_new_replayed_linkage_difference_regresses(self):
        baseline = {0x401000: entry(changed(9))}
        field = dict(offset=0, width=4, type="DIR32", encoded=0x03020200)
        current = {0x401000: entry(changed(9), linkages=[field])}
        lines, regressed, _ = frontier.evaluate(baseline, current)
        self.assertTrue(regressed)
        self.assertIn("newly differing offsets 1", lines[0])

    def test_negative_relative_encoding_is_signed(self):
        field = dict(offset=0, width=4, type="REL32", encoded=-1)
        self.assertEqual(entry(ORIGINAL, linkages=[field])["residual"], ["0-3"])

    def test_report_mismatch_count_must_agree_with_replayed_bytes(self):
        candidate = changed(9)
        report = dict(row(candidate), matched_bytes=14)
        with self.assertRaisesRegex(ValueError, "mismatch count"):
            frontier.measure(report, lambda a, n: ORIGINAL, lambda a, n: candidate)

    def test_unchanged_residual_passes(self):
        recorded = {0x401000: entry(changed(4, 5))}
        lines, regressed, updates = frontier.evaluate(recorded, {0x401000: entry(changed(4, 5))})
        self.assertFalse(regressed)
        self.assertEqual(updates, {})
        self.assertTrue(lines[0].startswith("OK"))

    def test_new_differing_byte_regresses(self):
        recorded = {0x401000: entry(changed(4))}
        lines, regressed, _ = frontier.evaluate(recorded, {0x401000: entry(changed(4, 7))})
        self.assertTrue(regressed)
        self.assertIn("newly differing offsets 7", lines[0])

    def test_exact_function_leaving_exact_regresses(self):
        lines, regressed, _ = frontier.evaluate({}, {0x401000: entry(changed(1))})
        self.assertTrue(regressed)
        self.assertTrue(lines[0].startswith("REGRESSED"))

    def test_mismatch_becoming_incomplete_regresses(self):
        recorded = {0x401000: entry(changed(4))}
        current = {0x401000: dict(entry(changed(4)), result="incomplete")}
        self.assertTrue(frontier.evaluate(recorded, current)[1])

    def test_disappearing_frontier_reports_regression(self):
        recorded = {0x401000: entry(changed(4))}
        for selected in (None, [0x401000]):
            with self.subTest(selected=selected):
                lines, regressed, updates = frontier.evaluate(recorded, {}, selected)
                self.assertTrue(regressed)
                self.assertTrue(lines[0].startswith("MISSING"))
                self.assertFalse(updates)

    def test_improvement_is_recorded(self):
        recorded = {0x401000: entry(changed(4, 5))}
        better = entry(changed(5))
        lines, regressed, updates = frontier.evaluate(recorded, {0x401000: better})
        self.assertFalse(regressed)
        self.assertTrue(lines[0].startswith("IMPROVED"))
        self.assertEqual(updates, {0x401000: better})
        text = frontier.render({0x401000: better})
        import tomllib
        parsed = tomllib.loads(text)["frontier"]["0x00401000"]
        self.assertEqual(parsed["residual"], ["5"])

    def test_new_exact_result_leaves_the_file(self):
        recorded = {0x401000: entry(changed(4))}
        current = {0x401000: entry(ORIGINAL, result="exact")}
        lines, regressed, updates = frontier.evaluate(recorded, current)
        self.assertFalse(regressed)
        self.assertEqual(updates, {0x401000: None})

    def test_exact_result_cannot_replace_a_different_original_extent(self):
        original = ORIGINAL[:-1]
        report = dict(row(ORIGINAL, result="exact"), size=15, compared_size=15, matched_bytes=15)
        exact = frontier.measure(report, lambda a, n: original, lambda a, n: original)
        lines, regressed, updates = frontier.evaluate({0x401000: entry(changed(4))}, {0x401000: exact})
        self.assertTrue(regressed)
        self.assertIn("original extent changed", lines[0])
        self.assertFalse(updates)

    def test_exact_verdict_must_agree_with_replayed_bytes(self):
        candidate = changed(9)
        with self.assertRaisesRegex(ValueError, "verdict differs"):
            entry(candidate, result="exact")

    def test_unknown_name_is_refused(self):
        with mock.patch.object(frontier, "load_recorded", return_value={0x401000: entry(changed(4))}), \
             mock.patch.object(sys, "argv", ["check-frontier.py", "0x41dcb0"]), \
             mock.patch.object(frontier, "current_state", side_effect=AssertionError("not reached")):
            self.assertEqual(frontier.main(), 2)


if __name__ == "__main__":
    unittest.main()
