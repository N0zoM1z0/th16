#!/usr/bin/env python3
"""Refusal controls for both complete one-member constructor EH graphs."""
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


CASES = {
    0x409670: dict(action=11, state_byte=128, cookie_field=23, interior=(44, 4), body_byte=231,
                   mutations=(19, 20, 23, 43, 106, 128, 234, 235)),
    0x42f0b0: dict(action=11, state_byte=99, cookie_field=22, interior=(43, 5), body_byte=141,
                   mutations=(19, 20, 22, 42, 69, 99, 146, 147)),
    0x4197c0: dict(action=14, state_byte=185, cookie_field=23, interior=(44, 4), body_byte=524,
                   mutations=(19, 20, 23, 43, 185, 224, 326, 329, 534, 535)),
}


class MemberConstructorEHControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        cls.records = [r for r in tomllib.loads((ROOT / "config/eh-handlers.toml").read_text())["handlers"]
                       if r.get("profile") == "single-member-constructor-v1"]
        cls.statics = map_statics(cls.context.directory / "th16.map")
        cls.pdb = pdb_section_contributions(cls.context.directory / "th16.pdb")
        cls.units = tomllib.loads((ROOT / "config/match-units.toml").read_text())["units"]

    def proof(self, record):
        return self.context.eh_handlers[(record["source"], record["parent_symbol"])]

    def review(self, record, context=None, statics=None, pdb=None):
        return review_handler(context or self.context, record,
                              self.statics if statics is None else statics,
                              self.pdb if pdb is None else pdb)

    def mutate(self, side, address, payload):
        context = copy.copy(self.context)
        setattr(context, side, Overlay(getattr(context, side),
                                      {address + i: value for i, value in enumerate(payload)}))
        return context

    def contribution(self, pdb, owner):
        return next(r for r in pdb["contributions"] if self.context.image.image_base
                    + self.context.image.section(r["section_number"]).rva + r["section_offset"] == owner["address"])

    def test_all_complete_aggregate_graphs_pass(self):
        self.assertEqual(len(self.records), 3)
        self.assertEqual({r["parent_target"] for r in self.records}, set(CASES))
        for record in self.records:
            proof = self.review(record)
            self.assertEqual(proof, self.proof(record))
            action = CASES[record["parent_target"]]["action"]
            self.assertEqual((proof["code_owner"]["size"], proof["descriptor"]["size"]), (action + 27, 44))
            self.assertEqual(proof["handler"]["owner_offset"], action)
            self.assertNotIn("size", proof["handler"])
            self.assertEqual((proof["descriptor"]["func_info_offset"], proof["descriptor"]["unwind_offset"]), (8, 0))

    def test_complete_primary_units_replay(self):
        for record in self.records:
            result = self.context.compare(self.units[f'reference-{record["parent_target"]:08x}'])
            self.assertEqual((result["result"], result["compared_size"]), ("exact", record["parent_size"]))
            self.assertEqual(result["auxiliary_eh_owners"], [self.proof(record)])

    def test_thread_member_keeps_its_cross_source_role_and_ret_4(self):
        record = next(r for r in self.records if r["parent_target"] == 0x4197c0)
        self.assertEqual(record["cleanup_entry"]["source"], "src/Thread.cpp")
        with self.assertRaises(EHEvidenceError):
            self.review(dict(record, cleanup_entry=dict(record["cleanup_entry"], source=record["source"])))
        parent = self.proof(record)["parent_candidate"]
        for offset in (548, 549, 550):
            value = self.context.image.read_address(parent + offset, 1)[0] ^ 1
            with self.subTest(offset=offset), self.assertRaisesRegex(EHEvidenceError, "restoration"):
                self.review(record, self.mutate("image", parent + offset, bytes([value])))

    def test_new_verifier_module_is_fingerprinted(self):
        path = "scripts/eh_member_constructor.py"
        self.assertEqual(self.context.before[path], hashlib.sha256((ROOT / path).read_bytes()).hexdigest())

    def test_profiles_sources_extents_and_declaration_keys_are_fixed(self):
        for record in self.records:
            changes = [dict(profile="unknown"), dict(profile="empty-eh3-saved-ebx-esi-v1"),
                       dict(parent_symbol=record["parent_symbol"] + "x"), dict(source="src/AnmRender.cpp"),
                       dict(parent_target=record["parent_target"] + 1),
                       dict(parent_size=record["parent_size"] - 1), dict(size=27), dict(size=37), dict(size=39),
                       dict(func_info_size=36), dict(func_info_size=43), dict(func_info_size=45),
                       dict(eh_flags=5), dict(target=record["target"] + 1),
                       dict(member_offset=12), dict(cookie_offset=-20), dict(unwind_offset=36)]
            for change in changes:
                with self.subTest(parent=record["parent_target"], change=change), self.assertRaises(EHEvidenceError):
                    self.review(dict(record, **change))

    def test_every_candidate_code_byte_is_checked(self):
        for record in self.records:
            owner = self.proof(record)["code_owner"]
            for offset in range(owner["size"]):
                address = owner["address"] + offset
                value = self.context.image.read_address(address, 1)[0] ^ 1
                with self.subTest(parent=record["parent_target"], offset=offset), self.assertRaises(ValueError):
                    self.review(record, self.mutate("image", address, bytes([value])))

    def test_every_candidate_metadata_byte_is_checked(self):
        for record in self.records:
            owner = self.proof(record)["descriptor"]
            for offset in range(44):
                address = owner["address"] + offset
                value = self.context.image.read_address(address, 1)[0] ^ 1
                with self.subTest(parent=record["parent_target"], offset=offset), self.assertRaises(EHEvidenceError):
                    self.review(record, self.mutate("image", address, bytes([value])))

    def test_all_original_hashes_are_required(self):
        for record in self.records:
            for name in ("parent_sha256", "target_sha256", "func_info_sha256"):
                with self.assertRaisesRegex(EHEvidenceError, "hash mismatch"):
                    self.review(dict(record, **{name: "0" * 64}))
            changed = dict(record, cleanup_entry=dict(record["cleanup_entry"], sha256="0" * 64))
            with self.assertRaisesRegex(EHEvidenceError, "hash mismatch"):
                self.review(changed)

    def test_original_action_semantics_survive_a_forged_hash(self):
        for record in self.records:
            for offset in (2, 5, 7, 20, 29):
                address = record["code_target"] + offset
                value = self.context.target.read_address(address, 1)[0] ^ 1
                context = self.mutate("target", address, bytes([value]))
                changed = dict(record, target_sha256=hashlib.sha256(
                    context.target.read_address(record["code_target"], record["size"])).hexdigest())
                with self.subTest(offset=offset), self.assertRaises(EHEvidenceError):
                    self.review(changed, context)

    def test_original_state_map_semantics_survive_a_forged_hash(self):
        for record in self.records:
            for offset in (4, 8, 12, 32, 36, 40):
                address = record["func_info_target"] + offset
                value = self.context.target.read_address(address, 1)[0] ^ 1
                context = self.mutate("target", address, bytes([value]))
                changed = dict(record, func_info_sha256=hashlib.sha256(
                    context.target.read_address(record["func_info_target"], 44)).hexdigest())
                with self.subTest(offset=offset), self.assertRaisesRegex(EHEvidenceError, "one-state graph"):
                    self.review(changed, context)

    def test_original_parent_state_is_checked_after_a_hash_update(self):
        for record in self.records:
            offset = CASES[record["parent_target"]]["state_byte"]
            context = self.mutate("target", record["parent_target"] + offset, b"\x01")
            changed = dict(record, parent_sha256=hashlib.sha256(
                context.target.read_address(record["parent_target"], record["parent_size"])).hexdigest())
            with self.assertRaisesRegex(EHEvidenceError, "protected frame uses"):
                self.review(changed, context)

    def test_complete_private_pdb_extents_cannot_be_shortened_or_enlarged(self):
        for record in self.records:
            proof = self.proof(record)
            for role, sizes in (("code_owner", (27, 37, 39)), ("descriptor", (36, 43, 45))):
                for size in sizes:
                    pdb = copy.deepcopy(self.pdb)
                    self.contribution(pdb, proof[role])["size"] = size
                    with self.subTest(role=role, size=size), self.assertRaises(EHEvidenceError):
                        self.review(record, pdb=pdb)

    def test_duplicate_overlapping_and_foreign_pdb_owners_are_rejected(self):
        for record in self.records:
            for role in ("code_owner", "descriptor"):
                for mode in ("duplicate", "overlap", "foreign"):
                    pdb = copy.deepcopy(self.pdb)
                    owner = self.contribution(pdb, self.proof(record)[role])
                    if mode == "foreign":
                        owner["object"] = owner["object"].replace(".obj", "-foreign.obj")
                    else:
                        other = dict(owner)
                        if mode == "overlap":
                            other.update(section_offset=owner["section_offset"] + 1, size=4)
                        pdb["contributions"].append(other)
                    with self.subTest(role=role, mode=mode), self.assertRaises(EHEvidenceError):
                        self.review(record, pdb=pdb)

    def test_private_interior_names_must_match_the_complete_owners(self):
        for record in self.records:
            names = ("__ehhandler$" + record["parent_symbol"], "__ehfuncinfo$" + record["parent_symbol"])
            for name in names:
                for mode in ("missing", "duplicate", "wrong-offset", "foreign"):
                    statics = copy.deepcopy(self.statics)
                    row = next(r for r in statics if r["symbol"] == name)
                    if mode == "missing":
                        statics.remove(row)
                    elif mode == "duplicate":
                        statics.append(dict(row))
                    elif mode == "wrong-offset":
                        row["section_offset"] += 1
                        row["address"] += 1
                    else:
                        row["object"] = "foreign.obj"
                    with self.subTest(name=name, mode=mode), self.assertRaises(EHEvidenceError):
                        self.review(record, statics=statics)

    def test_private_handler_cannot_become_a_public_alias(self):
        for record in self.records:
            context = copy.copy(self.context)
            row = next(r for r in self.statics if r["symbol"] == "__ehhandler$" + record["parent_symbol"])
            context.publics = self.context.publics + [dict(row)]
            with self.assertRaises(EHEvidenceError):
                self.review(record, context)

    def test_original_cleanup_scope_and_metadata_overlap_are_checked(self):
        for record in self.records:
            for mode in ("short-cleanup", "metadata-overlap"):
                context = copy.copy(self.context)
                context.boundaries = copy.deepcopy(self.context.boundaries)
                if mode == "short-cleanup":
                    context.boundaries[record["code_target"]]["size"] = "10"
                else:
                    context.boundaries[record["func_info_target"]] = dict(size="1", span_end=hex(record["func_info_target"]))
                with self.subTest(mode=mode), self.assertRaises(EHEvidenceError):
                    self.review(record, context)

    def test_cleanup_destructor_roles_are_independent_and_complete(self):
        for record in self.records:
            entry = record["cleanup_entry"]
            for change in (dict(source="src/AnmVm.cpp"), dict(symbol=entry["symbol"] + "x"),
                           dict(target=entry["target"] + 1), dict(size=entry["size"] - 1), dict(addend=0)):
                with self.subTest(change=change), self.assertRaises(EHEvidenceError):
                    self.review(dict(record, cleanup_entry=dict(entry, **change)))

    def test_parent_and_cleanup_candidate_source_owners_are_required(self):
        for record in self.records:
            for symbol in (record["parent_symbol"], record["cleanup_entry"]["symbol"]):
                context = copy.copy(self.context)
                context.linked = copy.deepcopy(self.context.linked)
                owner = next(f for f in context.linked["functions"] if f["symbol"] == symbol)
                owner["pdb_object"] = owner["pdb_object"].replace(".obj", "-foreign.obj")
                with self.assertRaisesRegex(EHEvidenceError, "source producer"):
                    self.review(record, context)

    def test_all_code_data_prefix_and_crossing_relocations_are_required(self):
        for record in self.records:
            proof = self.proof(record)
            code, data, parent = proof["code_owner"]["address"], proof["descriptor"]["address"], proof["parent_candidate"]
            case = CASES[record["parent_target"]]
            fields = [code + case["action"] + 18, data + 4, data + 16, parent + 6, parent + case["cookie_field"]]
            for location in fields:
                for remove, add in (([location], []), ([], [location])):
                    context = copy.copy(self.context)
                    context.image = Overlay(self.context.image, remove=remove, add=add)
                    with self.subTest(location=location), self.assertRaises(ValueError):
                        self.review(record, context)
            for location in (code + record["size"] - 2, data + 42, parent + record["parent_size"] - 2):
                context = copy.copy(self.context)
                context.image = Overlay(self.context.image, add=[location])
                with self.assertRaises(ValueError):
                    self.review(record, context)

    def test_same_shape_foreign_graph_edges_are_rejected(self):
        for index, record in enumerate(self.records):
            proof = self.proof(record)
            other = self.proof(self.records[(index + 1) % len(self.records)])
            for address, destination in ((proof["parent_candidate"] + 6, other["handler"]["address"]),
                                         (proof["code_owner"]["address"] + CASES[record["parent_target"]]["action"] + 18,
                                          other["descriptor"]["address"] + 8),
                                         (proof["descriptor"]["address"] + 4, other["code_owner"]["address"])):
                with self.assertRaises(EHEvidenceError):
                    self.review(record, self.mutate("image", address, struct.pack("<I", destination)))

    def test_candidate_state_saved_this_and_registration_are_checked(self):
        for record in self.records:
            proof = self.proof(record)
            offsets = CASES[record["parent_target"]]["mutations"]
            for offset in offsets:
                address = proof["parent_candidate"] + offset
                value = self.context.image.read_address(address, 1)[0] ^ 1
                with self.subTest(offset=offset), self.assertRaises(EHEvidenceError):
                    self.review(record, self.mutate("image", address, bytes([value])))

    def test_pe_cookie_storage_is_an_independent_witness(self):
        for record in self.records:
            location = self.context.image.image_base + self.context.image.directories[10][0] + 60
            value = struct.unpack("<I", self.context.image.read_address(location, 4))[0]
            with self.assertRaisesRegex(EHEvidenceError, "cookie or restoration"):
                self.review(record, self.mutate("image", location, struct.pack("<I", value + 4)))

    def test_an_interior_return_cannot_bypass_the_reviewed_restoration(self):
        for record in self.records:
            offset, count = CASES[record["parent_target"]]["interior"]
            context = self.mutate("image", self.proof(record)["parent_candidate"] + offset,
                                  b"\xc3" + b"\x90" * (count - 1))
            with self.assertRaisesRegex(EHEvidenceError, "protected frame uses"):
                self.review(record, context)

    def test_fields_remain_scoped_to_the_exact_complete_parent(self):
        for record in self.records:
            proof = self.proof(record)
            unit = self.units[f'reference-{record["parent_target"]:08x}']
            field = handler_field(proof)
            validate_field(self.context.eh_handlers, unit, field, proof["handler"]["address"])
            for changed in (dict(unit, source="src/AnmRender.cpp"), dict(unit, compare_size=unit["size"] - 1),
                            dict(unit, candidate_address=unit["candidate_address"] + 1)):
                with self.assertRaises(EHEvidenceError):
                    validate_field(self.context.eh_handlers, changed, field, proof["handler"]["address"])
            with self.assertRaises(EHEvidenceError):
                validate_field(self.context.eh_handlers, unit, dict(field, addend=1), proof["handler"]["address"])

    def test_ordinary_body_bytes_still_mismatch_after_valid_eh_review(self):
        for record in self.records:
            proof = self.proof(record)
            offset = CASES[record["parent_target"]]["body_byte"]
            context = self.mutate("image", proof["parent_candidate"] + offset, b"\x03")
            self.review(record, context)
            result = context.compare(self.units[f'reference-{record["parent_target"]:08x}'])
            self.assertEqual((result["result"], result["compared_size"]), ("mismatch", record["parent_size"]))
            self.assertEqual(result["matched_bytes"], record["parent_size"] - 1)


if __name__ == "__main__":
    unittest.main()
