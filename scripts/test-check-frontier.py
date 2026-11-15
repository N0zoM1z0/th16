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
    return {"target_address": 0x401000, "candidate_address": 0x402000, "symbol": "?f@@YAXXZ",
            "source": "src/F.cpp", "size": 16, "result": result, "compared_size": 16,
            "linkages": [dict(offset=o, width=4) for o in linkages]}


def entry(candidate: bytes, **kw):
    return frontier.measure(row(candidate, **kw), lambda a, n: ORIGINAL, lambda a, n: candidate)


def changed(*offsets):
    data = bytearray(ORIGINAL)
    for offset in offsets:
        data[offset] ^= 0xFF
    return bytes(data)


class FrontierControls(unittest.TestCase):
    def test_linkage_fields_are_masked(self):
        self.assertEqual(entry(changed(2, 3, 9), linkages=[0])["residual"], ["9"])

    def test_unchanged_residual_passes(self):
        recorded = {0x401000: entry(changed(4, 5))}
        lines, regressed, updates = frontier.evaluate(recorded, {0x401000: entry(changed(4, 5))}, set())
        self.assertFalse(regressed)
        self.assertEqual(updates, {})
        self.assertTrue(lines[0].startswith("OK"))

    def test_new_differing_byte_regresses(self):
        recorded = {0x401000: entry(changed(4))}
        lines, regressed, _ = frontier.evaluate(recorded, {0x401000: entry(changed(4, 7))}, set())
        self.assertTrue(regressed)
        self.assertIn("newly differing offsets 7", lines[0])

    def test_exact_function_leaving_exact_regresses(self):
        lines, regressed, _ = frontier.evaluate({}, {0x401000: entry(changed(1))}, set())
        self.assertTrue(regressed)
        self.assertTrue(lines[0].startswith("REGRESSED"))

    def test_mismatch_becoming_incomplete_regresses(self):
        recorded = {0x401000: entry(changed(4))}
        current = {0x401000: dict(entry(changed(4)), result="incomplete")}
        self.assertTrue(frontier.evaluate(recorded, current, set())[1])

    def test_improvement_is_recorded(self):
        recorded = {0x401000: entry(changed(4, 5))}
        better = entry(changed(5))
        lines, regressed, updates = frontier.evaluate(recorded, {0x401000: better}, set())
        self.assertFalse(regressed)
        self.assertTrue(lines[0].startswith("IMPROVED"))
        self.assertEqual(updates, {0x401000: better})
        text = frontier.render({0x401000: better})
        import tomllib
        parsed = tomllib.loads(text)["frontier"]["0x00401000"]
        self.assertEqual(parsed["residual"], ["5"])

    def test_new_exact_result_leaves_the_file(self):
        recorded = {0x401000: entry(changed(4))}
        lines, regressed, updates = frontier.evaluate(recorded, {}, {0x401000})
        self.assertFalse(regressed)
        self.assertEqual(updates, {0x401000: None})

    def test_unknown_name_is_refused(self):
        with mock.patch.object(frontier, "load_recorded", return_value={0x401000: entry(changed(4))}), \
             mock.patch.object(sys, "argv", ["check-frontier.py", "0x41dcb0"]), \
             mock.patch.object(frontier, "current_state", side_effect=AssertionError("not reached")):
            self.assertEqual(frontier.main(), 2)


if __name__ == "__main__":
    unittest.main()
