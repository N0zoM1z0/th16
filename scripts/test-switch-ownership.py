#!/usr/bin/env python3
"""Mutate reviewed switch code, tables and relocations without editing artifacts."""
import copy
import hashlib
import struct
import tempfile
import tomllib
import unittest

from strict_oracle import Context, Incomplete, ROOT
from switch_ownership import inspect_switch, validate_switch_owner, load_switch_owners, switch_owner_size


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
            if f"reference-{address:08x}" not in units:
                # The newly reviewed original remap owner has a different
                # complete candidate extent; its refusal is checked below.
                self.assertEqual(address, 0x4632f0)
                continue
            unit = units[f"reference-{address:08x}"]
            result = self.context.compare(unit)
            self.assertIn(result["result"], {"exact", "mismatch"})
            self.assertEqual(result["compared_size"], switch_owner_size(record))
            offsets = {r["offset"] for r in result["linkages"] if r["type"] == "DIR32"}
            self.assertTrue(set(range(record["table_offset"], record["table_offset"] + record["case_count"] * 4, 4)) <= offsets)
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


class RemappedSwitchOwnershipControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        cls.base = 0x4632f0
        cls.record = cls.context.switch_owners[cls.base]
        cls.size = switch_owner_size(cls.record)
        cls.unit = dict(target_address=cls.base,candidate_address=cls.base,
                        size=cls.size,compare_size=cls.size)
        # This original-byte fixture exercises only the structural validator.
        # It supplies no candidate PDB owner and cannot earn primary credit.
        cls.relocations = {cls.base+56,cls.base+63,*range(cls.base+2068,cls.base+2084,4)}
        cls.fixture = copy.copy(cls.context)
        cls.fixture.image = ImageOverlay(cls.context.target,added_relocations=cls.relocations)

    def inspect(self, changes=None, record=None):
        return inspect_switch(ImageOverlay(self.context.target,changes),self.base,record or self.record)

    def validate(self, image):
        context = copy.copy(self.fixture)
        context.image = image
        return validate_switch_owner(context,self.unit,self.record)

    def test_complete_original_includes_both_tables(self):
        instructions,dispatch,payload = self.inspect()
        self.assertEqual(sum(i.size for i in instructions),2068)
        self.assertEqual(dispatch.address,self.base+60)
        self.assertEqual(len(payload),2101)
        self.assertEqual(len(payload[2084:]),17)
        self.assertEqual(hashlib.sha256(payload).hexdigest(),self.record['target_sha256'])
        self.assertEqual(int(self.context.boundaries[self.base]['size']),len(payload))

    def test_structural_fixture_requires_all_entry_and_address_relocations(self):
        validate_switch_owner(self.fixture,self.unit,self.record)
        self.fixture.check_boundary(self.unit)
        for at in self.relocations:
            image = ImageOverlay(self.fixture.image,removed_relocations=[at])
            with self.subTest(address=hex(at)),self.assertRaisesRegex(ValueError,'relocation'):
                self.validate(image)

    def test_real_candidate_extent_cannot_be_trimmed_or_expanded(self):
        symbol = '?update_special_vertices@AnmVm@@QAEXXZ'
        function = next(f for f in self.context.linked['functions'] if f['symbol']==symbol)
        size = function['size']
        self.assertNotEqual(size,self.size)
        unit = dict(artifact_kind='linked-pe',source='src/AnmVmRun.cpp',object='AnmVmRun.obj',
                    symbol=symbol,candidate_address=int(function['address'],0),target_address=self.base,
                    size=size,compare_size=size,profile=self.context.receipt['compiler_profile'],
                    link_profile=self.context.receipt['linker_profile'],linkages=[])
        with self.assertRaisesRegex(Incomplete,'complete candidate owner'):
            self.context.compare(unit)
        for value in (2068,2097,2100,2102):
            with self.subTest(size=value),self.assertRaisesRegex(ValueError,'complete code and table'):
                validate_switch_owner(self.fixture,dict(self.unit,size=value,compare_size=value),self.record)

    def test_every_remap_byte_has_its_exact_reviewed_value(self):
        for offset,value in enumerate(self.record['remap_values'],2084):
            with self.subTest(offset=offset),self.assertRaisesRegex(ValueError,'complete reviewed byte map'):
                self.inspect({self.base+offset:value^1})

    def test_guard_and_remap_cannot_use_signed_or_different_indices(self):
        for offset,value in [(0x2e,17),(0x30,0x8f),(0x37,0x81),(0x3e,0x8d)]:
            with self.subTest(offset=offset),self.assertRaises(ValueError):
                self.inspect({self.base+offset:value})

    def test_remap_cannot_skip_or_address_an_interior_byte_map(self):
        changes = {self.base+0x38+i:b for i,b in enumerate(struct.pack('<I',self.base+2085))}
        with self.assertRaisesRegex(ValueError,'bounded byte index'):
            self.inspect(changes)
        record = dict(self.record,dispatch_offset=0x35)
        with self.assertRaisesRegex(ValueError,'unsigned default branch'):
            self.inspect(record=record)

    def test_target_slots_cannot_escape_enter_interiors_or_bypass_the_guard(self):
        for offset in (0x2f,0x35,0x3c,0x44,2068,2101):
            changes = {self.base+2068+i:b for i,b in enumerate(struct.pack('<I',self.base+offset))}
            with self.subTest(target=offset),self.assertRaises(ValueError):
                self.inspect(changes)
        # A direct edge into the remap also bypasses its bound.
        with self.assertRaisesRegex(ValueError,'unguarded incoming edge'):
            self.inspect({self.base:0xeb,self.base+1:0x33})

    def test_every_target_slot_retains_its_reviewed_case_mapping(self):
        for index,offset in enumerate(self.record['case_offsets']):
            other = 0x43 if offset != 0x43 else 0x80b
            changes = {self.base+2068+index*4+i:b for i,b in enumerate(struct.pack('<I',self.base+other))}
            with self.subTest(index=index),self.assertRaisesRegex(ValueError,'reviewed case mapping'):
                self.inspect(changes)

    def test_map_bytes_cannot_hide_extra_or_crossing_relocations(self):
        for offset in (2067,2069,2083,2084,2100):
            image = ImageOverlay(self.fixture.image,added_relocations=[self.base+offset])
            with self.subTest(offset=offset),self.assertRaisesRegex(ValueError,'complete entry relocations'):
                self.validate(image)

    def test_original_whole_owner_hash_remains_required(self):
        context = copy.copy(self.fixture)
        context.target = ImageOverlay(context.target,{self.base:0x57})
        with self.assertRaisesRegex(ValueError,'extent hash mismatch'):
            validate_switch_owner(context,self.unit,self.record)

    def test_loader_refuses_partial_or_expanded_remap_records(self):
        original = (ROOT/'config/switch-owners.toml').read_text()
        invalid = [original.replace('remap_offset = 2084','remap_offset = 2085'),
                   original.replace('remap_offset = 2084\n',''),
                   original.replace('3, 2, 2]','3, 2, 4]'),
                   original.replace('3, 2, 2]','3, 2, 2, 2]')]
        # A length change must disagree with the original CMP even if the
        # configuration describes a contiguous map with valid byte values.
        with tempfile.TemporaryDirectory(dir=ROOT/'.analysis') as directory:
            path = ROOT / directory / 'switch.toml'
            for text in invalid[:3]:
                self.assertNotEqual(text,original)
                path.write_text(text)
                with self.assertRaises(ValueError):
                    load_switch_owners(path)
            path.write_text(invalid[3])
            record = load_switch_owners(path)[self.base]
            with self.assertRaisesRegex(ValueError,'unsigned index bound'):
                self.inspect(record=record)

    @classmethod
    def tearDownClass(cls):
        cls.context.finish()


if __name__ == "__main__":
    unittest.main()
