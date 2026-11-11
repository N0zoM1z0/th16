#!/usr/bin/env python3
"""Mutate reviewed switch code, tables and relocations without editing artifacts."""
import copy
import hashlib
import struct
import tomllib
import unittest

from strict_oracle import Context, Incomplete, ROOT
from switch_ownership import inspect_switch, validate_switch_owner


class ImageOverlay:
    def __init__(self, image, changes=None, removed_relocations=(), added_relocations=()):
        self.image = image
        self.changes = changes or {}
        self.removed_relocations = set(removed_relocations)
        self.added_relocations = set(added_relocations)

    def __getattr__(self, name):
        return getattr(self.image, name)

    def read_address(self, address, size):
        data = bytearray(self.image.read_address(address, size))
        for position, value in self.changes.items():
            if address <= position < address + size:
                data[position - address] = value
        return bytes(data)

    def base_relocations(self):
        return sorted((set(self.image.base_relocations()) - self.removed_relocations) | self.added_relocations)


class SwitchOwnershipControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        cls.record = cls.context.switch_owners[0x468C00]
        public = next(p for p in cls.context.publics
                      if p["symbol"] == "?write_sprite_corners@AnmVm@@QAEXPAUD3DXVECTOR3@@@Z")
        cls.unit = {"target_address": 0x468C00, "candidate_address": public["address"],
                    "size": 100, "compare_size": 100}

    def check(self, *, context=None, unit=None, record=None):
        return validate_switch_owner(context or self.context, unit or self.unit, record or self.record)

    def mutate(self, side, offset, payload):
        context = copy.copy(self.context)
        base = self.unit["target_address" if side == "target" else "candidate_address"]
        changes = {base + offset + i: byte for i, byte in enumerate(payload)}
        setattr(context, side, ImageOverlay(getattr(context, side), changes))
        return context

    def test_complete_real_owner_and_table_pass(self):
        instructions, dispatch = self.check()
        self.assertEqual(sum(i.size for i in instructions), 84)
        self.assertEqual(dispatch, 0x468C17)
        self.context.check_boundary(self.unit)

    def test_every_reviewed_original_has_its_complete_table(self):
        for address, record in self.context.switch_owners.items():
            with self.subTest(address=hex(address)):
                _, _, payload = inspect_switch(self.context.target, address, record)
                self.assertEqual(hashlib.sha256(payload).hexdigest(), record["target_sha256"])
                self.assertEqual(int(self.context.boundaries[address]["size"]), len(payload))

    def test_alignment_padding_is_owned_and_cannot_hide_code(self):
        record = self.context.switch_owners[0x4015A0]
        inspect_switch(self.context.target, 0x4015A0, record)
        image = ImageOverlay(self.context.target, {0x4015A0 + record["code_size"]: 0xC3})
        with self.assertRaisesRegex(ValueError, "alignment padding"):
            inspect_switch(image, 0x4015A0, record)

    def test_partial_or_expanded_owner_is_rejected(self):
        for size in [84, 96, 99, 101]:
            with self.subTest(size=size):
                unit = dict(self.unit, size=size, compare_size=size)
                with self.assertRaisesRegex(ValueError, "complete code and table"):
                    self.check(unit=unit)

    def test_every_byte_is_bound_by_the_target_extent_hash(self):
        record = dict(self.record, target_sha256="0" * 64)
        with self.assertRaisesRegex(ValueError, "extent hash mismatch"):
            self.check(record=record)
        context = self.mutate("target", 0, b"\x53")
        with self.assertRaisesRegex(ValueError, "extent hash mismatch"):
            self.check(context=context)

    def test_guard_must_bound_exactly_all_slots(self):
        for side in ["target", "image"]:
            with self.subTest(side=side):
                context = self.mutate(side, 0x14, b"\x04")
                with self.assertRaisesRegex(ValueError, "unsigned index bound"):
                    self.check(context=context)

    def test_default_branch_must_be_unsigned_and_adjacent(self):
        for side in ["target", "image"]:
            with self.subTest(side=side):
                context = self.mutate(side, 0x15, b"\x75")
                with self.assertRaisesRegex(ValueError, "unsigned default branch"):
                    self.check(context=context)

    def test_guard_and_dispatch_must_use_the_same_index(self):
        context = self.mutate("image", 0x13, b"\xf9")
        with self.assertRaisesRegex(ValueError, "complete owned table"):
            self.check(context=context)

    def test_dispatch_cannot_address_an_interior_table_entry(self):
        for side in ["target", "image"]:
            base = self.unit["target_address" if side == "target" else "candidate_address"]
            with self.subTest(side=side):
                context = self.mutate(side, 0x1A, struct.pack("<I", base + 88))
                with self.assertRaisesRegex(ValueError, "complete owned table"):
                    self.check(context=context)

    def test_case_slots_cannot_enter_instruction_interiors_or_leave_the_code(self):
        for side in ["target", "image"]:
            base = self.unit["target_address" if side == "target" else "candidate_address"]
            for destination in [base + 0x1F, base + 84, base + 100]:
                with self.subTest(side=side, destination=destination):
                    context = self.mutate(side, 84, struct.pack("<I", destination))
                    with self.assertRaisesRegex(ValueError, "owned instruction starts"):
                        self.check(context=context)

    def test_all_case_mappings_are_checked(self):
        base = self.unit["candidate_address"]
        for offset, destination in [(84, 0x1E), (88, 0x39), (92, 0x1E), (96, 0x1E)]:
            with self.subTest(offset=offset):
                context = self.mutate("image", offset, struct.pack("<I", base + destination))
                with self.assertRaisesRegex(ValueError, "reviewed case mapping"):
                    self.check(context=context)

    def test_all_entries_and_dispatch_require_relocations(self):
        base = self.unit["candidate_address"]
        for offset in [0x1A, 84, 88, 92, 96]:
            with self.subTest(offset=offset):
                context = copy.copy(self.context)
                context.image = ImageOverlay(context.image, removed_relocations=[base + offset])
                with self.assertRaisesRegex(ValueError, "relocation"):
                    self.check(context=context)

    def test_extra_and_crossing_table_relocations_are_rejected(self):
        base = self.unit["candidate_address"]
        for offset in [82, 85, 98]:
            with self.subTest(offset=offset):
                context = copy.copy(self.context)
                context.image = ImageOverlay(context.image, added_relocations=[base + offset])
                with self.assertRaisesRegex(ValueError, "complete entry relocations"):
                    self.check(context=context)

    def test_complete_replay_keeps_code_padding_and_every_slot(self):
        units = tomllib.loads((ROOT / "config/match-units.toml").read_text())["units"]
        for address, record in self.context.switch_owners.items():
            unit = units[f"reference-{address:08x}"]
            result = self.context.compare(unit)
            self.assertIn(result["result"], {"exact", "mismatch"})
            self.assertEqual(result["compared_size"], record["table_offset"] + record["case_count"] * 4)
            offsets = {r["offset"] for r in result["linkages"] if r["type"] == "DIR32"}
            self.assertTrue(set(range(record["table_offset"], unit["size"], 4)) <= offsets)
        for address, offset, byte in [(0x468C00, 0, 0x53), (0x4015A0, 235, 0xCC)]:
            with self.subTest(address=hex(address), offset=offset):
                unit = units[f"reference-{address:08x}"]
                self.assertEqual(self.context.compare(unit)["result"], "exact")
                context = copy.copy(self.context)
                context.image = ImageOverlay(context.image, {unit["candidate_address"] + offset: byte})
                self.assertEqual(context.compare(unit)["result"], "mismatch")

    def test_direct_edge_cannot_bypass_the_guard(self):
        for destination in [0x15, 0x17]:
            with self.subTest(destination=destination):
                context = self.mutate("image", 0, bytes([0xEB, destination - 2]))
                with self.assertRaisesRegex(ValueError, "unguarded incoming edge"):
                    self.check(context=context)

    def test_table_edge_cannot_bypass_the_guard(self):
        for destination in [0x15, 0x17]:
            with self.subTest(destination=destination):
                context = self.mutate("image", 84, struct.pack("<I", self.unit["candidate_address"] + destination))
                with self.assertRaisesRegex(ValueError, "unguarded incoming edge"):
                    self.check(context=context)

    def test_table_ownership_cannot_overlap_another_function(self):
        context = copy.copy(self.context)
        context.boundaries = dict(context.boundaries)
        context.boundaries[0x468C54] = {"size": "4", "span_end": "0x468c57"}
        with self.assertRaisesRegex(Incomplete, "overlaps another"):
            context.check_boundary(self.unit)

    def test_unreviewed_indirect_dispatch_remains_incomplete(self):
        context = copy.copy(self.context)
        context.switch_owners = {}
        with self.assertRaises(Incomplete):
            context.check_boundary(self.unit)

    def test_proof_and_record_are_part_of_the_oracle_identity(self):
        for path in ["scripts/switch_ownership.py", "config/switch-owners.toml"]:
            with self.subTest(path=path):
                self.assertEqual(self.context.before[path], hashlib.sha256((ROOT / path).read_bytes()).hexdigest())

    @classmethod
    def tearDownClass(cls):
        cls.context.finish()


if __name__ == "__main__":
    unittest.main()
