#!/usr/bin/env python3
"""Refusal controls for five complete sized-allocation EH graphs."""
import copy
import hashlib
import importlib.util
import struct
import tomllib
import unittest

import capstone

from eh_identity import EHEvidenceError, handler_field, review_handler, validate_field
from linked_image import map_statics, pdb_section_contributions
from strict_oracle import Context, ROOT

_spec = importlib.util.spec_from_file_location("aggregate_controls", ROOT / "scripts/test-eh-constructor.py")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
Overlay = _base.Overlay

CASES = {
    0x409db0: dict(allocation=0x66f0, push=41, prefix=39, cookie=23, displacement=-20,
                   saved=54, live=59, reset=74, returns=[136, 155]),
    0x411dd0: dict(allocation=0x1403b28, push=36, prefix=36, cookie=20, displacement=-12,
                   saved=49, live=54, reset=68, returns=[128, 146]),
    0x42f440: dict(allocation=0x1c972ec, push=36, prefix=36, cookie=20, displacement=-12,
                   saved=49, live=54, reset=68, returns=[128, 146]),
    0x447e20: dict(allocation=0x31c, push=39, prefix=37, cookie=21, displacement=-16,
                   saved=54, live=77, reset=106, returns=[173, 192]),
    0x447ef0: dict(allocation=0x31c, push=39, prefix=37, cookie=21, displacement=-16,
                   saved=54, live=77, reset=106, returns=[171, 190]),
}


class AllocationEHControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        cls.records = [r for r in tomllib.loads((ROOT / "config/eh-handlers.toml").read_text())["handlers"]
                       if r.get("profile") == "allocation-cleanup-v1"]
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

    def unit(self, record):
        return self.units[f'reference-{record["parent_target"]:08x}']

    def body_test(self, record):
        proof = self.proof(record)
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        decoder.detail = True
        return next(i for i in decoder.disasm(self.context.image.read_address(
            proof["parent_candidate"], record["parent_size"]), proof["parent_candidate"])
                    if i.mnemonic == "test" and len(i.bytes) == 2
                    and all(op.type == capstone.x86.X86_OP_REG for op in i.operands))

    def test_all_five_complete_graphs_pass(self):
        self.assertEqual(len(self.records), 5)
        self.assertEqual({r["parent_target"] for r in self.records}, set(CASES))
        for record in self.records:
            proof, case = self.review(record), CASES[record["parent_target"]]
            self.assertEqual(proof, self.proof(record))
            self.assertEqual((proof["code_owner"]["size"], proof["descriptor"]["size"]), (45, 44))
            self.assertEqual((proof["handler"]["owner_offset"], proof["descriptor"]["func_info_offset"]), (18, 8))
            self.assertNotIn("size", proof["handler"])
            self.assertEqual(proof["allocation_size"], case["allocation"])
            self.assertEqual(proof["cookie_offset"], case["displacement"])
            self.assertEqual(proof["normal_returns"], case["returns"])

    def test_complete_primary_units_replay(self):
        for record in self.records:
            result = self.context.compare(self.unit(record))
            self.assertEqual((result["result"], result["compared_size"]), ("exact", record["parent_size"]))
            self.assertEqual(result["auxiliary_eh_owners"], [self.proof(record)])

    def test_verifier_module_is_fingerprinted(self):
        name = "scripts/eh_allocation.py"
        self.assertEqual(self.context.before[name], hashlib.sha256((ROOT / name).read_bytes()).hexdigest())

    def test_profile_roles_extents_and_extra_keys_are_fixed(self):
        for record in self.records:
            for change in (dict(profile="unknown"), dict(profile="single-member-constructor-v1"),
                           dict(source="src/AnmRender.cpp"), dict(parent_symbol=record["parent_symbol"] + "x"),
                           dict(parent_target=record["parent_target"] + 1),
                           dict(parent_size=record["parent_size"] - 1), dict(size=18), dict(size=27),
                           dict(size=44), dict(size=46), dict(func_info_size=36), dict(func_info_size=43),
                           dict(eh_flags=5), dict(target=record["target"] + 1),
                           dict(allocation_size=1), dict(cookie_offset=-12), dict(layout="manager")):
                with self.subTest(change=change), self.assertRaises(EHEvidenceError):
                    self.review(dict(record, **change))

    def test_every_candidate_action_and_handler_byte_is_checked(self):
        for record in self.records:
            code = self.proof(record)["code_owner"]["address"]
            for offset in range(45):
                value = self.context.image.read_address(code + offset, 1)[0] ^ 1
                with self.subTest(parent=record["parent_target"], offset=offset), self.assertRaises(ValueError):
                    self.review(record, self.mutate("image", code + offset, bytes([value])))

    def test_every_candidate_metadata_byte_is_checked(self):
        for record in self.records:
            data = self.proof(record)["descriptor"]["address"]
            for offset in range(44):
                value = self.context.image.read_address(data + offset, 1)[0] ^ 1
                with self.subTest(parent=record["parent_target"], offset=offset), self.assertRaises(EHEvidenceError):
                    self.review(record, self.mutate("image", data + offset, bytes([value])))

    def test_original_hashes_cover_every_complete_owner(self):
        for record in self.records:
            for field in ("parent_sha256", "target_sha256", "func_info_sha256"):
                with self.assertRaisesRegex(EHEvidenceError, "hash mismatch"):
                    self.review(dict(record, **{field: "0" * 64}))

    def test_original_action_semantics_survive_a_hash_update(self):
        for record in self.records:
            for offset in (1, 7, 8, 10, 16, 17, 27, 36):
                address = record["code_target"] + offset
                value = self.context.target.read_address(address, 1)[0] ^ 1
                context = self.mutate("target", address, bytes([value]))
                changed = dict(record, target_sha256=hashlib.sha256(
                    context.target.read_address(record["code_target"], 45)).hexdigest())
                with self.subTest(offset=offset), self.assertRaises(EHEvidenceError):
                    self.review(changed, context)

    def test_original_metadata_semantics_survive_a_hash_update(self):
        for record in self.records:
            for offset in (4, 8, 12, 32, 36, 40):
                address = record["func_info_target"] + offset
                value = self.context.target.read_address(address, 1)[0] ^ 1
                context = self.mutate("target", address, bytes([value]))
                changed = dict(record, func_info_sha256=hashlib.sha256(
                    context.target.read_address(record["func_info_target"], 44)).hexdigest())
                with self.assertRaisesRegex(EHEvidenceError, "one-state graph"):
                    self.review(changed, context)

    def test_original_allocation_and_lifetime_survive_a_hash_update(self):
        for record in self.records:
            case = CASES[record["parent_target"]]
            for offset in (case["push"] + 1, case["push"] + 6, case["saved"] + 2,
                           case["live"] + 3, case["reset"] + 3):
                address = record["parent_target"] + offset
                value = self.context.target.read_address(address, 1)[0] ^ 1
                context = self.mutate("target", address, bytes([value]))
                changed = dict(record, parent_sha256=hashlib.sha256(
                    context.target.read_address(record["parent_target"], record["parent_size"])).hexdigest())
                with self.subTest(offset=offset), self.assertRaises(EHEvidenceError):
                    self.review(changed, context)

    def test_candidate_allocation_and_pointer_lifetime_are_checked(self):
        for record in self.records:
            proof, case = self.proof(record), CASES[record["parent_target"]]
            for offset in (case["push"] + 1, case["push"] + 6, case["saved"] + 2,
                           case["live"] + 3, case["reset"] + 3):
                address = proof["parent_candidate"] + offset
                value = self.context.image.read_address(address, 1)[0] ^ 1
                with self.assertRaises(EHEvidenceError):
                    self.review(record, self.mutate("image", address, bytes([value])))

    def test_both_normal_restoration_paths_are_required(self):
        for record in self.records:
            proof = self.proof(record)
            for end in CASES[record["parent_target"]]["returns"]:
                for offset in (end - 10, end - 3, end):
                    address = proof["parent_candidate"] + offset
                    value = self.context.image.read_address(address, 1)[0] ^ 1
                    with self.subTest(end=end, offset=offset), self.assertRaisesRegex(EHEvidenceError, "restoration"):
                        self.review(record, self.mutate("image", address, bytes([value])))

    def test_additional_returns_cannot_bypass_the_state_and_restoration(self):
        for record in self.records:
            instruction = self.body_test(record)
            with self.assertRaisesRegex(EHEvidenceError, "protected frame uses"):
                self.review(record, self.mutate("image", instruction.address, b"\xc3\x90"))

    def test_cookie_displacement_follows_this_parents_fixed_frame(self):
        for record in self.records:
            proof = self.proof(record)
            for slot in (-4, -12, -16, -20, -24):
                if slot == proof["cookie_offset"]:
                    continue
                with self.subTest(slot=slot), self.assertRaises(EHEvidenceError):
                    self.review(record, self.mutate("image", proof["handler"]["address"] + 9,
                                                     struct.pack("<b", slot)))

    def test_cookie_storage_is_independently_witnessed_by_pe(self):
        for record in self.records:
            location = self.context.image.image_base + self.context.image.directories[10][0] + 60
            value = struct.unpack("<I", self.context.image.read_address(location, 4))[0]
            with self.assertRaisesRegex(EHEvidenceError, "cookie differs"):
                self.review(record, self.mutate("image", location, struct.pack("<I", value + 4)))

    def test_other_profiles_keep_their_explicit_cookie_displacements(self):
        records = tomllib.loads((ROOT / "config/eh-handlers.toml").read_text())["handlers"]
        for record in records:
            if record.get("profile") == "allocation-cleanup-v1":
                continue
            proof = self.proof(record)
            address = proof["handler"]["address"] + 9
            # The later single-state graph independently uses node-12 too.
            # Always change the displacement instead of rewriting that value.
            value = b"\xfc" if self.context.image.read_address(address, 1) == b"\xf4" else b"\xf4"
            with self.subTest(parent=record["parent_symbol"]), self.assertRaises(EHEvidenceError):
                self.review(record, self.mutate("image", address, value))

    def test_all_four_runtime_roles_require_independent_bindings(self):
        for record in self.records:
            for name in ("??2@YAPAXI@Z", "??3@YAXPAXI@Z", "@__security_check_cookie@4", "___CxxFrameHandler3"):
                for mode in ("kind", "destination", "duplicate-public"):
                    context = copy.copy(self.context)
                    if mode == "duplicate-public":
                        row = next(p for p in self.context.publics if p["symbol"] == name)
                        context.publics = self.context.publics + [dict(row)]
                    else:
                        context.reviewed_linkages = copy.deepcopy(self.context.reviewed_linkages)
                        if mode == "kind":
                            context.reviewed_linkages[name]["kind"] = "literal"
                        else:
                            context.reviewed_linkages[name]["target"] += 1
                    with self.subTest(name=name, mode=mode), self.assertRaises(EHEvidenceError):
                        self.review(record, context)

    def test_complete_private_pdb_extents_are_required(self):
        for record in self.records:
            for role, sizes in (("code_owner", (18, 27, 44, 46)), ("descriptor", (8, 36, 43, 45))):
                for size in sizes:
                    pdb = copy.deepcopy(self.pdb)
                    owner = self.proof(record)[role]
                    row = next(r for r in pdb["contributions"] if self.context.image.image_base
                               + self.context.image.section(r["section_number"]).rva + r["section_offset"] == owner["address"])
                    row["size"] = size
                    with self.subTest(role=role, size=size), self.assertRaises(EHEvidenceError):
                        self.review(record, pdb=pdb)

    def test_private_interior_names_cannot_be_missing_or_aliased(self):
        for record in self.records:
            for prefix in ("__ehhandler$", "__ehfuncinfo$"):
                name = prefix + record["parent_symbol"]
                row = next(r for r in self.statics if r["symbol"] == name)
                for statics in ([r for r in self.statics if r is not row], self.statics + [dict(row)]):
                    with self.assertRaises(EHEvidenceError):
                        self.review(record, statics=statics)

    def test_code_data_prefix_and_both_exit_relocations_are_exhaustive(self):
        for record in self.records:
            proof, case = self.proof(record), CASES[record["parent_target"]]
            code, data, parent = proof["code_owner"]["address"], proof["descriptor"]["address"], proof["parent_candidate"]
            for location in (code + 36, data + 4, data + 16, parent + 6, parent + case["cookie"]):
                for remove, add in (([location], []), ([], [location])):
                    context = copy.copy(self.context)
                    context.image = Overlay(self.context.image, remove=remove, add=add)
                    with self.assertRaises(ValueError):
                        self.review(record, context)
            for location in (code + 43, data + 42, parent + case["prefix"] - 2,
                             *[parent + end - 2 for end in case["returns"]]):
                context = copy.copy(self.context)
                context.image = Overlay(self.context.image, add=[location])
                with self.assertRaises(ValueError):
                    self.review(record, context)

    def test_foreign_graph_edges_cannot_substitute_for_parent_roles(self):
        for index, record in enumerate(self.records):
            proof, other = self.proof(record), self.proof(self.records[(index + 1) % len(self.records)])
            for address, target in ((proof["parent_candidate"] + 6, other["handler"]["address"]),
                                    (proof["code_owner"]["address"] + 36, other["descriptor"]["address"] + 8),
                                    (proof["descriptor"]["address"] + 4, other["code_owner"]["address"])):
                with self.assertRaises(EHEvidenceError):
                    self.review(record, self.mutate("image", address, struct.pack("<I", target)))

    def test_fields_remain_scoped_to_the_complete_parent(self):
        for record in self.records:
            proof, unit = self.proof(record), self.unit(record)
            field = handler_field(proof)
            validate_field(self.context.eh_handlers, unit, field, proof["handler"]["address"])
            for changed in (dict(unit, source="src/AnmRender.cpp"), dict(unit, compare_size=unit["size"] - 1),
                            dict(unit, candidate_address=unit["candidate_address"] + 1)):
                with self.assertRaises(EHEvidenceError):
                    validate_field(self.context.eh_handlers, changed, field, proof["handler"]["address"])

    def test_ordinary_body_bytes_still_mismatch_after_valid_eh(self):
        for record in self.records:
            instruction = self.body_test(record)
            context = self.mutate("image", instruction.address + 1, bytes([instruction.bytes[1] ^ 8]))
            self.review(record, context)
            result = context.compare(self.unit(record))
            self.assertEqual((result["result"], result["compared_size"]), ("mismatch", record["parent_size"]))
            self.assertEqual(result["matched_bytes"], record["parent_size"] - 1)


if __name__ == "__main__":
    unittest.main()
