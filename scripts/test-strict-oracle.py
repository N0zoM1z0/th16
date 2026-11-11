#!/usr/bin/env python3
"""Positive and mutation controls for strict complete-owner byte replay."""
import copy
import struct
import unittest

from strict_oracle import Context, Incomplete, ROOT, replay_owner


class Image:
    def __init__(self, address, data, relocations=()):
        self.address = address
        self.data = data
        self.relocations = relocations

    def read_address(self, address, size):
        offset = address - self.address
        if offset < 0 or offset + size > len(self.data):
            raise ValueError("fixture read leaves the declared owner")
        return self.data[offset:offset + size]

    def base_relocations(self):
        return self.relocations


class CompleteOwnerReplay(unittest.TestCase):
    def setUp(self):
        self.start = 0x501000
        self.target_start = 0x401000
        candidate = b"\xb8" + struct.pack("<I", 0x503000) + b"\xe8" + struct.pack("<i", 0x502000 - self.start - 10) + b"\xc3"
        target = b"\xb8" + struct.pack("<I", 0x403000) + b"\xe8" + struct.pack("<i", 0x402200 - self.target_start - 10) + b"\xc3"
        self.image = Image(self.start, candidate, [self.start + 1])
        self.target = Image(self.target_start, target)
        self.function = dict(address=hex(self.start), size=len(candidate))
        self.publics = [dict(symbol="_Global", address=0x503000), dict(symbol="_Callee", address=0x502000)]
        self.unit = dict(target_address=self.target_start, compare_size=len(candidate), linkages=[
            dict(offset=1, type="DIR32", symbol="_Global", target=0x403000),
            dict(offset=6, type="REL32", symbol="_Callee", target=0x402200)])

    def compare(self):
        return replay_owner(self.image, self.target, self.publics, self.function, self.unit)

    def test_bound_global_and_call_are_replayed(self):
        result = self.compare()
        self.assertEqual(result["result"], "exact")
        self.assertEqual(result["matched_bytes"], 11)
        self.assertFalse(result["raw_equal"])

    def test_wrong_candidate_global_is_not_masked(self):
        self.image.data = self.image.data[:1] + struct.pack("<I", 0x503004) + self.image.data[5:]
        with self.assertRaisesRegex(Incomplete, "unique linked symbol"):
            self.compare()

    def test_missing_field_is_incomplete(self):
        self.unit["linkages"].pop()
        with self.assertRaisesRegex(Incomplete, "exhaustive"):
            self.compare()

    def test_wrong_semantic_target_fails(self):
        self.unit["linkages"][1]["target"] += 1
        self.assertEqual(self.compare()["result"], "mismatch")

    def test_changed_instruction_fails(self):
        self.image.data = b"\x05" + self.image.data[1:]
        result = self.compare()
        self.assertEqual(result["result"], "mismatch")
        self.assertEqual(result["first_differences"][0]["offset"], 0)

    def test_partial_owner_is_rejected(self):
        self.function["size"] += 1
        with self.assertRaisesRegex(Incomplete, "complete declared extent"):
            self.compare()

    def test_claimed_primary_extent_cannot_exceed_the_compared_owner(self):
        self.unit["size"] = 100
        with self.assertRaisesRegex(Incomplete, "compound ownership"):
            self.compare()

    def test_ambiguous_symbol_is_rejected(self):
        self.publics.append(dict(symbol="_Global", address=0x503004))
        with self.assertRaisesRegex(Incomplete, "unique linked symbol"):
            self.compare()

    def test_changed_local_offset_is_rejected(self):
        self.image.data = b"\xb8" + struct.pack("<I", self.start + 10) + self.image.data[5:]
        self.unit["linkages"][0] = dict(offset=1, type="DIR32", symbol="<local>", local=True, target=self.target_start + 9)
        with self.assertRaisesRegex(Incomplete, "changes its offset"):
            self.compare()

    def test_unlinked_trailing_data_is_compared(self):
        self.image.data += b"\xff"
        self.target.data += b"\xfe"
        self.function["size"] += 1
        self.unit["compare_size"] += 1
        self.unit["data_spans"] = [dict(offset=11, width=1)]
        result = self.compare()
        self.assertEqual(result["result"], "mismatch")
        self.assertEqual(result["matched_bytes"], 11)
        self.assertEqual(result["first_differences"][0]["offset"], 11)

    def test_undeclared_trailing_data_is_incomplete(self):
        self.image.data += b"\xff"
        self.target.data += b"\xff"
        self.function["size"] += 1
        self.unit["compare_size"] += 1
        with self.assertRaisesRegex(ValueError, "Capstone decoded"):
            self.compare()

    def test_overlapping_target_owner_is_incomplete(self):
        context = Context.__new__(Context)
        context.switch_owners = {}
        context.target = self.target
        context.boundaries = {self.target_start - 8: dict(span_end=hex(self.target_start + 1))}
        with self.assertRaisesRegex(Incomplete, "overlaps"):
            context.check_boundary(self.unit)

    def boundary_context(self):
        context = Context.__new__(Context)
        context.directory = ROOT / "build/reference-candidate"
        context.receipt = dict(compiler_profile=["/GL"], linker_profile=["/LTCG"])
        unit = dict(self.unit, source="src/Rng.cpp", object="Rng.obj", symbol="_Fixture",
                    artifact_kind="linked-pe", profile=["/GL"], link_profile=["/LTCG"],
                    candidate_address=self.start)
        function = dict(self.function, symbol="_Fixture",
                        pdb_object="Z:" + str(context.directory / "obj/src/Rng.obj"))
        context.linked = dict(functions=[function])
        context.boundaries = {}
        return context, unit

    def test_missing_original_boundary_is_distinct_from_an_extent_difference(self):
        context, unit = self.boundary_context()
        with self.assertRaisesRegex(Incomplete, "lacks an independently reviewed function boundary"):
            context.compare(unit)

    def test_real_extent_difference_still_refuses_comparison(self):
        context, unit = self.boundary_context()
        context.boundaries[self.target_start] = dict(size=12)
        with self.assertRaisesRegex(Incomplete, "complete candidate owner differs"):
            context.compare(unit)


if __name__ == "__main__":
    unittest.main()
