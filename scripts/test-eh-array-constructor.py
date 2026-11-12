#!/usr/bin/env python3
"""Refusal controls for the complete BulletManager array-constructor EH graph."""
import copy
import hashlib
import importlib.util
import struct
import tomllib
import unittest

from eh_identity import EHEvidenceError, handler_field, review_handler, validate_field
from linked_image import map_statics, pdb_section_contributions
from strict_oracle import Context, ROOT

_spec = importlib.util.spec_from_file_location("aggregate_controls", ROOT / "scripts/test-eh-constructor.py")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
Overlay = _base.Overlay


class ArrayConstructorEHControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        cls.record = next(r for r in tomllib.loads((ROOT / "config/eh-handlers.toml").read_text())["handlers"]
                          if r.get("profile") == "bullet-array-constructor-v1")
        cls.proof = cls.context.eh_handlers[(cls.record["source"], cls.record["parent_symbol"])]
        cls.statics = map_statics(cls.context.directory / "th16.map")
        cls.pdb = pdb_section_contributions(cls.context.directory / "th16.pdb")
        cls.unit = tomllib.loads((ROOT / "config/match-units.toml").read_text())["units"]["reference-00411880"]

    def review(self, context=None, record=None, pdb=None, statics=None):
        return review_handler(context or self.context, record or self.record,
                              self.statics if statics is None else statics,
                              self.pdb if pdb is None else pdb)

    def mutate(self, side, address, payload):
        context = copy.copy(self.context)
        setattr(context, side, Overlay(getattr(context, side),
                                      {address + i: value for i, value in enumerate(payload)}))
        return context

    def test_complete_graph_and_primary_owner_pass(self):
        proof = self.review()
        self.assertEqual(proof, self.proof)
        self.assertEqual((proof["code_owner"]["size"], proof["descriptor"]["size"]), (57, 44))
        self.assertEqual(proof["handler"]["owner_offset"], 30)
        self.assertNotIn("size", proof["handler"])
        self.assertEqual((proof["array_count"], proof["element_stride"], proof["member_offset"]), (2001, 0x1478, 0x9c))
        result = self.context.compare(self.unit)
        self.assertEqual((result["result"], result["compared_size"]), ("exact", 181))
        self.assertEqual(result["auxiliary_eh_owners"], [proof])

    def test_module_is_fingerprinted(self):
        path = "scripts/eh_array_constructor.py"
        self.assertEqual(self.context.before[path], hashlib.sha256((ROOT / path).read_bytes()).hexdigest())

    def test_profile_roles_dimensions_and_extents_are_fixed(self):
        for change in (dict(profile="unknown"), dict(source="src/Item.cpp"),
                       dict(parent_symbol="??0ItemManager@@QAE@XZ"), dict(parent_target=0x411881),
                       dict(parent_size=180), dict(size=30), dict(size=27), dict(size=56), dict(size=58),
                       dict(func_info_size=36), dict(func_info_size=43), dict(eh_flags=5),
                       dict(target=self.record["target"] + 1), dict(array_count=2001),
                       dict(element_stride=0x1478), dict(member_offset=0x9c), dict(cookie_offset=-16)):
            with self.subTest(change=change), self.assertRaises(EHEvidenceError):
                self.review(record=dict(self.record, **change))

    def test_every_candidate_code_and_metadata_byte_is_checked(self):
        for role in ("code_owner", "descriptor"):
            owner = self.proof[role]
            for offset in range(owner["size"]):
                address = owner["address"] + offset
                value = self.context.image.read_address(address, 1)[0] ^ 1
                with self.subTest(role=role, offset=offset), self.assertRaises(ValueError):
                    self.review(self.mutate("image", address, bytes([value])))

    def test_all_original_hashes_are_required(self):
        for field in ("parent_sha256", "target_sha256", "func_info_sha256"):
            with self.assertRaisesRegex(EHEvidenceError, "hash mismatch"):
                self.review(record=dict(self.record, **{field: "0" * 64}))
        with self.assertRaisesRegex(EHEvidenceError, "hash mismatch"):
            self.review(record=dict(self.record, cleanup_entry=dict(self.record["cleanup_entry"], sha256="0" * 64)))

    def test_original_action_semantics_survive_updated_hashes(self):
        for offset in (1, 6, 11, 17, 19, 24, 25, 29, 39, 48):
            address = self.record["code_target"] + offset
            value = self.context.target.read_address(address, 1)[0] ^ 1
            context = self.mutate("target", address, bytes([value]))
            record = dict(self.record, target_sha256=hashlib.sha256(
                context.target.read_address(self.record["code_target"], 57)).hexdigest())
            with self.subTest(offset=offset), self.assertRaises(EHEvidenceError):
                self.review(context, record)

    def test_original_metadata_semantics_survive_updated_hashes(self):
        for offset in (4, 8, 12, 32, 36, 40):
            address = self.record["func_info_target"] + offset
            value = self.context.target.read_address(address, 1)[0] ^ 1
            context = self.mutate("target", address, bytes([value]))
            record = dict(self.record, func_info_sha256=hashlib.sha256(
                context.target.read_address(self.record["func_info_target"], 44)).hexdigest())
            with self.assertRaisesRegex(EHEvidenceError, "one-state graph"):
                self.review(context, record)

    def test_original_parent_array_ranges_and_state_survive_updated_hashes(self):
        for offset in (41, 43, 53, 58, 64, 70, 75, 85, 90, 96, 103, 109):
            address = self.record["parent_target"] + offset
            value = self.context.target.read_address(address, 1)[0] ^ 1
            context = self.mutate("target", address, bytes([value]))
            record = dict(self.record, parent_sha256=hashlib.sha256(
                context.target.read_address(self.record["parent_target"], 181)).hexdigest())
            with self.subTest(offset=offset), self.assertRaises(EHEvidenceError):
                self.review(context, record)

    def test_candidate_parent_array_ranges_and_state_are_checked(self):
        for offset in (18, 19, 21, 41, 43, 53, 58, 64, 70, 75, 85, 90, 96, 103, 109, 166, 167, 180):
            address = self.proof["parent_candidate"] + offset
            value = self.context.image.read_address(address, 1)[0] ^ 1
            with self.subTest(offset=offset), self.assertRaises(EHEvidenceError):
                self.review(self.mutate("image", address, bytes([value])))

    def test_element_destructor_requires_its_independent_complete_role(self):
        entry = self.record["cleanup_entry"]
        for change in (dict(source="src/Thread.cpp"), dict(symbol="??1Item@@QAE@XZ"),
                       dict(target=entry["target"] + 1), dict(size=119), dict(addend=0)):
            with self.assertRaises(EHEvidenceError):
                self.review(record=dict(self.record, cleanup_entry=dict(entry, **change)))
        context = copy.copy(self.context)
        context.linked = copy.deepcopy(self.context.linked)
        owner = next(f for f in context.linked["functions"] if f["symbol"] == entry["symbol"])
        owner["pdb_object"] = owner["pdb_object"].replace(".obj", "-foreign.obj")
        with self.assertRaisesRegex(EHEvidenceError, "source producer"):
            self.review(context)

    def test_all_four_runtime_roles_are_independently_bound(self):
        for name in ("??_M@YGXPAXIIP6EX0@Z@Z", "??_L@YGXPAXIIP6EX0@Z1@Z",
                     "@__security_check_cookie@4", "___CxxFrameHandler3"):
            for mode in ("kind", "destination", "duplicate"):
                context = copy.copy(self.context)
                if mode == "duplicate":
                    row = next(p for p in self.context.publics if p["symbol"] == name)
                    context.publics = self.context.publics + [dict(row)]
                else:
                    context.reviewed_linkages = copy.deepcopy(self.context.reviewed_linkages)
                    if mode == "kind":
                        context.reviewed_linkages[name]["kind"] = "literal"
                    else:
                        context.reviewed_linkages[name]["target"] += 1
                with self.subTest(name=name, mode=mode), self.assertRaises(EHEvidenceError):
                    self.review(context)

    def test_complete_private_pdb_extents_are_mandatory(self):
        for role, sizes in (("code_owner", (30, 27, 56, 58)), ("descriptor", (36, 43, 45))):
            for size in sizes:
                pdb = copy.deepcopy(self.pdb)
                owner = self.proof[role]
                row = next(r for r in pdb["contributions"] if self.context.image.image_base
                           + self.context.image.section(r["section_number"]).rva + r["section_offset"] == owner["address"])
                row["size"] = size
                with self.assertRaises(EHEvidenceError):
                    self.review(pdb=pdb)

    def test_private_internal_names_cannot_be_missing_or_duplicated(self):
        for name in ("__ehhandler$" + self.record["parent_symbol"], "__ehfuncinfo$" + self.record["parent_symbol"]):
            row = next(r for r in self.statics if r["symbol"] == name)
            for statics in ([r for r in self.statics if r is not row], self.statics + [dict(row)]):
                with self.assertRaises(EHEvidenceError):
                    self.review(statics=statics)

    def test_every_pointer_relocation_and_crossing_field_is_checked(self):
        code, data, parent = self.proof["code_owner"]["address"], self.proof["descriptor"]["address"], self.proof["parent_candidate"]
        for location in (code + 1, code + 48, data + 4, data + 16, parent + 6, parent + 21):
            for remove, add in (([location], []), ([], [location])):
                context = copy.copy(self.context)
                context.image = Overlay(self.context.image, remove=remove, add=add)
                with self.assertRaises(ValueError):
                    self.review(context)
        for location in (code + 55, data + 42, parent + 40, parent + 179):
            context = copy.copy(self.context)
            context.image = Overlay(self.context.image, add=[location])
            with self.assertRaises(ValueError):
                self.review(context)

    def test_cookie_frame_is_independently_witnessed(self):
        for displacement in (-4, -12, -20, -24):
            with self.assertRaises(EHEvidenceError):
                self.review(self.mutate("image", self.proof["handler"]["address"] + 9, struct.pack("<b", displacement)))
        location = self.context.image.image_base + self.context.image.directories[10][0] + 60
        value = struct.unpack("<I", self.context.image.read_address(location, 4))[0]
        with self.assertRaisesRegex(EHEvidenceError, "cookie or restoration"):
            self.review(self.mutate("image", location, struct.pack("<I", value + 4)))

    def test_an_extra_return_cannot_bypass_the_reviewed_restoration(self):
        context = self.mutate("image", self.proof["parent_candidate"] + 113, b"\xc3\x90")
        with self.assertRaisesRegex(EHEvidenceError, "protected frame uses"):
            self.review(context)

    def test_field_scope_cannot_leave_the_complete_parent(self):
        field = handler_field(self.proof)
        validate_field(self.context.eh_handlers, self.unit, field, self.proof["handler"]["address"])
        for changed in (dict(self.unit, source="src/Item.cpp"), dict(self.unit, compare_size=180),
                        dict(self.unit, candidate_address=self.unit["candidate_address"] + 1)):
            with self.assertRaises(EHEvidenceError):
                validate_field(self.context.eh_handlers, changed, field, self.proof["handler"]["address"])

    def test_body_bytes_remain_unmasked_after_valid_eh_review(self):
        context = self.mutate("image", self.proof["parent_candidate"] + 122, b"\xd0")
        self.review(context)
        result = context.compare(self.unit)
        self.assertEqual((result["result"], result["compared_size"], result["matched_bytes"]), ("mismatch", 181, 180))


if __name__ == "__main__":
    unittest.main()
