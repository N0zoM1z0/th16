#!/usr/bin/env python3
"""Mutation controls for three explicit saved-register empty EH3 frame profiles."""
import copy
import hashlib
import importlib.util
import struct
import tomllib
import unittest

import capstone

from eh_identity import EHEvidenceError, handler_field, inspect_saved_register_frame, review_handler, validate_field
from linked_image import map_statics, pdb_section_contributions
from strict_oracle import Context, ROOT

_spec = importlib.util.spec_from_file_location("empty_eh_controls", ROOT / "scripts/test-eh-identities.py")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
Overlay = _base.Overlay
PROFILE = "empty-eh3-saved-ebx-esi-edi-v1"


class SavedRegisterEHControls(unittest.TestCase):
    PROFILE = PROFILE
    TARGETS = {0x409550, 0x4190b0, 0x419450, 0x41b1a0,
               0x41ba10, 0x4264a0, 0x43afe0, 0x441a50}
    COOKIE_OFFSET = -20
    COOKIE_FIELD = 22
    COOKIE_SLOT_BYTE = 0xe0
    OTHER_COOKIE_BYTE = 0xf0
    PREFIX_SIZE = 38

    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        cls.records = [r for r in tomllib.loads((ROOT / "config/eh-handlers.toml").read_text())["handlers"]
                       if r.get("profile") == cls.PROFILE]
        cls.statics = map_statics(cls.context.directory / "th16.map")
        cls.pdb = pdb_section_contributions(cls.context.directory / "th16.pdb")
        cls.units = tomllib.loads((ROOT / "config/match-units.toml").read_text())["units"]

    def proof(self, record):
        return self.context.eh_handlers[(record["source"], record["parent_symbol"])]

    def review(self, record, context=None, pdb=None):
        return review_handler(context or self.context, record, self.statics, pdb or self.pdb)

    def mutate(self, side, address, payload):
        context = copy.copy(self.context)
        changes = {address + i: value for i, value in enumerate(payload)}
        setattr(context, side, Overlay(getattr(context, side), changes))
        return context

    def test_all_reviewed_complete_graphs_pass(self):
        self.assertEqual(len(self.records), len(self.TARGETS))
        self.assertEqual({r["parent_target"] for r in self.records}, self.TARGETS)
        for record in self.records:
            proof = self.review(record)
            self.assertEqual((proof["profile"], proof["cookie_offset"]), (self.PROFILE, self.COOKIE_OFFSET))
            self.assertEqual((proof["handler"]["size"], proof["descriptor"]["size"]), (27, 36))

    def test_profile_is_explicit_and_cookie_offset_is_not_configurable(self):
        for record in self.records:
            missing = {k: v for k, v in record.items() if k != "profile"}
            for changed in (missing, dict(record, profile="unknown"), dict(record, profile=None),
                            dict(record, cookie_offset=self.COOKIE_OFFSET), dict(record, cookie_offset=-4)):
                with self.subTest(parent=record["parent_symbol"], changed=changed), self.assertRaises(EHEvidenceError):
                    self.review(changed)

    def test_handler_cannot_use_the_legacy_or_an_arbitrary_cookie_slot(self):
        for record in self.records:
            proof = self.proof(record)
            for slot in (0xfc, self.OTHER_COOKIE_BYTE, 0xe8):
                context = self.mutate("image", proof["handler"]["address"] + 9, bytes([slot]))
                with self.subTest(parent=record["parent_symbol"], slot=slot), self.assertRaises(EHEvidenceError):
                    self.review(record, context)

    def test_other_registered_profile_cannot_replace_this_frame(self):
        other = ("empty-eh3-saved-ebx-esi-v1" if self.PROFILE == PROFILE else PROFILE)
        for record in self.records:
            with self.assertRaisesRegex(EHEvidenceError, "handler differs"):
                self.review(dict(record, profile=other))

    def test_target_cookie_slot_is_verified_even_with_an_updated_hash(self):
        for record in self.records:
            context = self.mutate("target", record["target"] + 9, b"\xfc")
            changed = dict(record, target_sha256=hashlib.sha256(
                context.target.read_address(record["target"], 27)).hexdigest())
            with self.assertRaisesRegex(EHEvidenceError, "handler differs"):
                self.review(changed, context)

    def test_saved_registers_registration_and_restore_are_verified(self):
        for record in self.records:
            proof = self.proof(record)
            parent, size = proof["parent_candidate"], proof["parent_size"]
            for offset in (17, 18, 19, 20, 22, 31, 32, size - 16, size - 15, size - 7, size - 1):
                original = self.context.image.read_address(parent + offset, 1)[0]
                context = self.mutate("image", parent + offset, bytes([original ^ 1]))
                with self.subTest(parent=record["parent_symbol"], offset=offset), self.assertRaises(EHEvidenceError):
                    self.review(record, context)

    def test_original_frame_is_verified_after_a_parent_hash_update(self):
        for record in self.records:
            context = self.mutate("target", record["parent_target"] + 18, b"\x56")
            changed = dict(record, parent_sha256=hashlib.sha256(
                context.target.read_address(record["parent_target"], record["parent_size"])).hexdigest())
            with self.assertRaisesRegex(EHEvidenceError, "saved-register frame"):
                self.review(changed, context)

    def test_pe_load_config_cookie_is_an_independent_witness(self):
        for record in self.records:
            location = self.context.image.image_base + self.context.image.directories[10][0] + 60
            cookie = struct.unpack("<I", self.context.image.read_address(location, 4))[0]
            context = self.mutate("image", location, struct.pack("<I", cookie + 4))
            with self.assertRaisesRegex(EHEvidenceError, "saved-register frame"):
                self.review(record, context)

    def test_empty_state_and_cookie_slots_cannot_be_used_by_the_body(self):
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        decoder.detail = True
        for record in self.records:
            proof = self.proof(record)
            parent, size = proof["parent_candidate"], proof["parent_size"]
            writes = [i for i in decoder.disasm(self.context.image.read_address(parent, size), parent)
                      if i.address >= parent + self.PREFIX_SIZE and i.mnemonic == "mov"
                      and i.operands[0].type == capstone.x86.X86_OP_MEM
                      and i.operands[0].mem.base == capstone.x86.X86_REG_EBP
                      and i.operands[0].mem.disp == -16 and i.disp_size == 1]
            self.assertTrue(writes)
            for displacement in (0xfc, 0xf8, self.COOKIE_SLOT_BYTE):
                context = self.mutate("image", writes[0].address + writes[0].disp_offset, bytes([displacement]))
                with self.subTest(parent=record["parent_symbol"], displacement=displacement), self.assertRaisesRegex(
                        EHEvidenceError, "EH-sensitive parent frame"):
                    self.review(record, context)

    def test_body_cannot_replace_the_frame_pointer(self):
        for record in self.records:
            parent = self.proof(record)["parent_candidate"]
            context = self.mutate("image", parent + self.PREFIX_SIZE, bytes.fromhex("8be9"))
            with self.assertRaisesRegex(EHEvidenceError, "EH-sensitive parent frame"):
                self.review(record, context)

    def test_nonempty_candidate_metadata_and_changed_flags_are_rejected(self):
        for record in self.records:
            descriptor = self.proof(record)["descriptor"]["address"]
            for offset, value in ((4, 1), (8, 1), (12, 1), (32, 1)):
                context = self.mutate("image", descriptor + offset, struct.pack("<I", value))
                with self.subTest(parent=record["parent_symbol"], offset=offset), self.assertRaises(EHEvidenceError):
                    self.review(record, context)
            with self.assertRaises(EHEvidenceError):
                self.review(dict(record, eh_flags=1))

    def test_nonempty_original_metadata_is_rejected_even_with_a_new_hash(self):
        for record in self.records:
            context = self.mutate("target", record["func_info_target"] + 4, struct.pack("<I", 1))
            changed = dict(record, func_info_sha256=hashlib.sha256(
                context.target.read_address(record["func_info_target"], 36)).hexdigest())
            with self.assertRaisesRegex(EHEvidenceError, "nonempty tables"):
                self.review(changed, context)

    def test_every_complete_auxiliary_extent_is_required(self):
        for record in self.records:
            proof = self.proof(record)
            for role in ("handler", "descriptor"):
                pdb = copy.deepcopy(self.pdb)
                address = proof[role]["address"]
                contribution = next(r for r in pdb["contributions"] if self.context.image.image_base
                                    + self.context.image.section(r["section_number"]).rva
                                    + r["section_offset"] == address)
                contribution["size"] -= 1
                with self.subTest(parent=record["parent_symbol"], role=role), self.assertRaises(EHEvidenceError):
                    self.review(record, pdb=pdb)

    def test_prefix_auxiliary_and_crossing_relocations_are_required(self):
        for record in self.records:
            proof = self.proof(record)
            parent, size = proof["parent_candidate"], proof["parent_size"]
            handler, descriptor = proof["handler"]["address"], proof["descriptor"]["address"]
            cases = [([parent + self.COOKIE_FIELD], []), ([], [parent + self.COOKIE_FIELD]), ([], [parent + 10]),
                     ([], [parent + 35]), ([], [parent + size - 2]), ([handler + 18], []),
                     ([], [descriptor])]
            for remove, add in cases:
                context = copy.copy(self.context)
                context.image = Overlay(self.context.image, remove=remove, add=add)
                with self.subTest(parent=record["parent_symbol"], remove=remove, add=add), self.assertRaisesRegex(
                        EHEvidenceError, "relocation"):
                    self.review(record, context)

    def test_identical_descriptor_or_handler_of_the_other_parent_is_rejected(self):
        for index, record in enumerate(self.records):
            proof = self.proof(record)
            other = self.proof(self.records[(index + 1) % len(self.records)])
            self.assertEqual(self.context.image.read_address(proof["descriptor"]["address"], 36),
                             self.context.image.read_address(other["descriptor"]["address"], 36))
            for address, destination in ((proof["handler"]["address"] + 18, other["descriptor"]["address"]),
                                         (proof["parent_candidate"] + 6, other["handler"]["address"])):
                context = self.mutate("image", address, struct.pack("<I", destination))
                with self.assertRaises(EHEvidenceError):
                    self.review(record, context)

    def test_parent_fields_keep_their_complete_source_scope(self):
        for record in self.records:
            proof = self.proof(record)
            unit = self.units[f'reference-{record["parent_target"]:08x}']
            field = handler_field(proof)
            validate_field(self.context.eh_handlers, unit, field, proof["handler"]["address"])
            for changed in (dict(unit, source="src/Item.cpp"), dict(unit, target_address=unit["target_address"] + 1),
                            dict(unit, compare_size=unit["size"] - 1)):
                with self.assertRaises(EHEvidenceError):
                    validate_field(self.context.eh_handlers, changed, field, proof["handler"]["address"])
            with self.assertRaises(EHEvidenceError):
                validate_field(self.context.eh_handlers, unit, dict(field, addend=1), proof["handler"]["address"])

    def test_complete_parent_units_replay(self):
        for record in self.records:
            unit = self.units[f'reference-{record["parent_target"]:08x}']
            result = self.context.compare(unit)
            self.assertEqual((result["result"], result["compared_size"]), ("exact", record["parent_size"]))

    def test_ordinary_parent_body_is_still_compared_without_masks(self):
        for record in self.records:
            proof = self.proof(record)
            parent = proof["parent_candidate"]
            offset = self.PREFIX_SIZE + 1
            original = self.context.image.read_address(parent + offset, 1)[0]
            context = self.mutate("image", parent + offset, bytes([original ^ 8]))
            self.review(record, context)
            unit = self.units[f'reference-{record["parent_target"]:08x}']
            result = context.compare(unit)
            self.assertEqual(result["result"], "mismatch")
            self.assertLess(result["matched_bytes"], record["parent_size"])


class SavedEBXESIEHControls(SavedRegisterEHControls):
    PROFILE = "empty-eh3-saved-ebx-esi-v1"
    TARGETS = {0x411ca0, 0x4188d0, 0x4313b0}
    COOKIE_OFFSET = -16
    COOKIE_FIELD = 21
    COOKIE_SLOT_BYTE = 0xe4
    OTHER_COOKIE_BYTE = 0xec
    PREFIX_SIZE = 37

    def test_other_node_minus_16_frames_remain_unsupported(self):
        # Bomb saves ESI/EDI; Spellcard reserves two local words and saves ESI.
        # A shared handler displacement does not establish either frame shape.
        for parent, size, handler in ((0x40d710, 377, 0x48a4e0), (0x417790, 272, 0x48a590)):
            with self.assertRaisesRegex(EHEvidenceError, "saved-register frame"):
                inspect_saved_register_frame(self.context.target, parent, size, handler, profile=self.PROFILE)


class SavedESIEDIEHControls(SavedRegisterEHControls):
    PROFILE = "empty-eh3-saved-esi-edi-v1"
    TARGETS = {0x470e10}
    COOKIE_OFFSET = -12
    COOKIE_FIELD = 20
    COOKIE_SLOT_BYTE = 0xe8
    OTHER_COOKIE_BYTE = 0xf0
    PREFIX_SIZE = 36

    def test_empty_state_and_cookie_slots_cannot_be_used_by_the_body(self):
        record = self.records[0]
        parent = self.proof(record)["parent_candidate"]
        for displacement in (0xfc, 0xf8, self.COOKIE_SLOT_BYTE):
            context = self.mutate("image", parent + 51, b"\x8b\x45" + bytes([displacement]))
            with self.subTest(displacement=displacement), self.assertRaisesRegex(
                    EHEvidenceError, "EH-sensitive parent frame"):
                self.review(record, context)

    def test_identical_descriptor_or_handler_of_the_other_parent_is_rejected(self):
        record = self.records[0]
        proof = self.proof(record)
        other = self.context.eh_handlers[("src/BulletManager.cpp", "??1BulletManager@@QAE@XZ")]
        self.assertEqual(self.context.image.read_address(proof["descriptor"]["address"], 36),
                         self.context.image.read_address(other["descriptor"]["address"], 36))
        for address, destination in ((proof["handler"]["address"] + 18, other["descriptor"]["address"]),
                                     (proof["parent_candidate"] + 6, other["handler"]["address"])):
            with self.assertRaises(EHEvidenceError):
                self.review(record, self.mutate("image", address, struct.pack("<I", destination)))

    def test_nonempty_node_minus_12_frames_remain_outside_this_profile(self):
        for parent, size, handler in ((0x457060, 189, 0x48a9c0), (0x45a3a0, 162, 0x48aa30)):
            with self.subTest(parent=parent), self.assertRaises(EHEvidenceError):
                inspect_saved_register_frame(self.context.target, parent, size, handler, profile=self.PROFILE)


if __name__ == "__main__":
    unittest.main()
