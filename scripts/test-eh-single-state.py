#!/usr/bin/env python3
"""Refusal controls for three complete single-state terminal graphs."""
import copy
import hashlib
import importlib.util
from itertools import permutations
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


class SingleStateEHControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        cls.records = [r for r in tomllib.loads((ROOT / "config/eh-handlers.toml").read_text())["handlers"]
                       if r.get("profile") == "single-state-terminate-v1"]
        cls.statics = map_statics(cls.context.directory / "th16.map")
        cls.pdb = pdb_section_contributions(cls.context.directory / "th16.pdb")
        cls.units = tomllib.loads((ROOT / "config/match-units.toml").read_text())["units"]

    def proof(self, record):
        return self.context.eh_handlers[(record["source"], record["parent_symbol"])]

    def review(self, record, context=None, pdb=None, statics=None):
        return review_handler(context or self.context, record,
                              self.statics if statics is None else statics,
                              self.pdb if pdb is None else pdb)

    def mutate(self, side, address, payload):
        context = copy.copy(self.context)
        setattr(context, side, Overlay(getattr(context, side),
                                      {address + i: value for i, value in enumerate(payload)}))
        return context

    def test_three_complete_graphs_and_primary_owners_pass(self):
        self.assertEqual({r["parent_target"] for r in self.records}, {0x457060, 0x45a3a0, 0x45d850})
        self.assertEqual(len(self.records), 3)
        for record in self.records:
            proof = self.review(record)
            self.assertEqual(proof, self.proof(record))
            self.assertEqual((proof["handler"]["size"], proof["descriptor"]["size"]), (27, 44))
            cookie = -8 if record["parent_target"] == 0x45d850 else -12
            self.assertEqual((proof["descriptor"]["func_info_offset"], proof["cookie_offset"]), (8, cookie))
            result = self.context.compare(self.units[f'reference-{record["parent_target"]:08x}'])
            self.assertEqual((result["result"], result["compared_size"]), ("exact", record["parent_size"]))
            self.assertEqual(result["auxiliary_eh_owners"], [proof])

    def test_roles_state_counts_flags_and_extents_are_fixed(self):
        for record in self.records:
            for change in (dict(source="src/Thread.cpp"), dict(parent_symbol=record["parent_symbol"] + "x"),
                           dict(parent_target=record["parent_target"] + 1), dict(parent_size=record["parent_size"] - 1),
                           dict(size=26), dict(size=28), dict(func_info_size=36), dict(func_info_size=52),
                           dict(eh_flags=6 - record["eh_flags"]), dict(states=1), dict(producer="src/WinMain.cpp"),
                           dict(profile="two-state-terminate-v1")):
                with self.subTest(change=change), self.assertRaises(EHEvidenceError):
                    self.review(dict(record, **change))

    def test_all_original_extent_hashes_are_required(self):
        for record in self.records:
            for key in ("parent_sha256", "target_sha256", "func_info_sha256"):
                with self.assertRaisesRegex(EHEvidenceError, "hash mismatch"):
                    self.review(dict(record, **{key: "0" * 64}))

    def test_every_candidate_handler_and_metadata_byte_is_checked(self):
        for record in self.records:
            for role in ("handler", "descriptor"):
                owner = self.proof(record)[role]
                for offset in range(owner["size"]):
                    address = owner["address"] + offset
                    value = self.context.image.read_address(address, 1)[0] ^ 1
                    with self.subTest(role=role, offset=offset), self.assertRaises(ValueError):
                        self.review(record, self.mutate("image", address, bytes([value])))

    def test_original_metadata_semantics_survive_updated_hashes(self):
        for record in self.records:
            for offset in (0, 4, 8, 12, 28, 32, 36, 40):
                address = record["func_info_target"] + offset
                value = self.context.target.read_address(address, 1)[0] ^ 1
                context = self.mutate("target", address, bytes([value]))
                changed = dict(record, func_info_sha256=hashlib.sha256(
                    context.target.read_address(record["func_info_target"], 44)).hexdigest())
                with self.subTest(offset=offset), self.assertRaisesRegex(EHEvidenceError, "state graph"):
                    self.review(changed, context)

    def test_candidate_and_original_state_frame_uses_are_fixed(self):
        for record in self.records:
            state = {0x457060: 106, 0x45a3a0: 46, 0x45d850: 267}[record["parent_target"]]
            for side, base in (("target", record["parent_target"]), ("image", self.proof(record)["parent_candidate"])):
                context = self.mutate(side, base + state, b"\x01")
                changed = dict(record)
                if side == "target":
                    changed["parent_sha256"] = hashlib.sha256(
                        context.target.read_address(base, record["parent_size"])).hexdigest()
                with self.assertRaisesRegex(EHEvidenceError, "protected frame"):
                    self.review(changed, context)
            for offset in (17, 20, 24, 29, record["parent_size"] - 5):
                address = self.proof(record)["parent_candidate"] + offset
                value = self.context.image.read_address(address, 1)[0] ^ 1
                with self.assertRaises(EHEvidenceError):
                    self.review(record, self.mutate("image", address, bytes([value])))

    def test_ret_4_and_interior_returns_cannot_change(self):
        for record in self.records:
            parent = self.proof(record)["parent_candidate"]
            body_offset = 40 if record["parent_target"] == 0x45d850 else 36
            with self.assertRaisesRegex(EHEvidenceError, "protected frame"):
                self.review(record, self.mutate("image", parent + body_offset, b"\xc3\x90"))
            returns = {0x457060: (188,), 0x45a3a0: (159, 160, 161), 0x45d850: (369,)}
            for offset in returns[record["parent_target"]]:
                value = self.context.image.read_address(parent + offset, 1)[0] ^ 1
                with self.assertRaisesRegex(EHEvidenceError, "restoration"):
                    self.review(record, self.mutate("image", parent + offset, bytes([value])))

    def test_synthetic_producer_matches_its_generated_annotation_and_caller(self):
        record = next(r for r in self.records if r["parent_target"] == 0x45a3a0)
        self.assertEqual(record["source"], "src/WinMain.cpp")
        self.assertEqual(self.proof(record)["producer_source"], "src/WinMain.cpp")
        for replacement in ("UpdateFunc.obj", "Arcfile.obj"):
            context = copy.copy(self.context)
            context.linked = copy.deepcopy(self.context.linked)
            owner = next(f for f in context.linked["functions"] if f["symbol"] == record["parent_symbol"])
            owner["pdb_object"] = owner["pdb_object"].replace("WinMain.obj", replacement)
            with self.assertRaisesRegex(EHEvidenceError, "source producer"):
                self.review(record, context)

    def test_synthetic_producer_requires_complete_caller_and_both_call_witnesses(self):
        record = next(r for r in self.records if r["parent_target"] == 0x45a3a0)
        witness = self.proof(record)["producer_witness"]
        self.assertEqual((witness["target"], witness["size"], witness["original_call_offset"]), (0x459830, 2919, 2495))
        for side, base, offset in (("target", witness["target"], 2495),
                                    ("image", witness["candidate"], witness["candidate_call_offset"])):
            with self.assertRaises(EHEvidenceError):
                self.review(record, self.mutate(side, base + offset + 1, b"\0\0\0\0"))
        context = copy.copy(self.context)
        context.linked = copy.deepcopy(self.context.linked)
        next(f for f in context.linked["functions"] if f["symbol"] == "_WinMain@16")["size"] -= 1
        with self.assertRaisesRegex(EHEvidenceError, "complete candidate"):
            self.review(record, context)

    def test_every_array_delete_byte_is_checked_on_both_sides(self):
        record = next(r for r in self.records if r["parent_target"] == 0x457060)
        proof = self.proof(record)["array_delete"]
        for side, entries in (("target", ((proof["target"], 14), (proof["unsized_target"], 5))),
                               ("image", ((proof["candidate"], 14), (proof["unsized_candidate"], 5)))):
            for base, size in entries:
                for offset in range(size):
                    image = getattr(self.context, side)
                    value = image.read_address(base + offset, 1)[0] ^ 1
                    with self.subTest(side=side, offset=offset), self.assertRaises(EHEvidenceError):
                        self.review(record, self.mutate(side, base + offset, bytes([value])))

    def test_array_delete_runtime_roles_and_relocations_are_required(self):
        record = next(r for r in self.records if r["parent_target"] == 0x457060)
        for name in ("??_V@YAXPAXI@Z", "??_V@YAXPAX@Z", "??3@YAXPAX@Z"):
            for key, value in (("kind", "literal"), ("size", 1), ("target", 0)):
                context = copy.copy(self.context)
                context.reviewed_linkages = copy.deepcopy(self.context.reviewed_linkages)
                context.reviewed_linkages[name][key] = value
                with self.assertRaisesRegex(EHEvidenceError, "independent complete runtime"):
                    self.review(record, context)
        proof = self.proof(record)["array_delete"]
        for address in (proof["candidate"] + 7, proof["unsized_candidate"] + 1):
            context = copy.copy(self.context)
            context.image = Overlay(self.context.image, add=[address])
            with self.assertRaises(EHEvidenceError):
                self.review(record, context)

    def test_complete_private_extents_modules_and_names_are_required(self):
        for record in self.records:
            for role in ("handler", "descriptor"):
                owner = self.proof(record)[role]
                for key, value in (("size", owner["size"] - 1), ("module_index", owner["module_index"] + 1)):
                    pdb = copy.deepcopy(self.pdb)
                    row = next(r for r in pdb["contributions"] if self.context.image.image_base
                               + self.context.image.section(r["section_number"]).rva + r["section_offset"] == owner["address"])
                    row[key] = value
                    with self.assertRaises(EHEvidenceError):
                        self.review(record, pdb=pdb)
            for prefix in ("__ehhandler$", "__unwindtable$", "__ehfuncinfo$"):
                row = next(r for r in self.statics if r["symbol"] == prefix + record["parent_symbol"])
                for rows in ([r for r in self.statics if r is not row], self.statics + [dict(row)]):
                    with self.assertRaises(EHEvidenceError):
                        self.review(record, statics=rows)

    def test_every_pointer_relocation_and_crossing_field_is_checked(self):
        for record in self.records:
            proof = self.proof(record)
            h, data, parent = proof["handler"]["address"], proof["descriptor"]["address"], proof["parent_candidate"]
            cookie_field = 19 if record["parent_target"] == 0x45d850 else 20
            for address in (h + 18, data + 4, data + 16, parent + 6, parent + cookie_field):
                for remove, add in (([address], []), ([], [address])):
                    context = copy.copy(self.context)
                    context.image = Overlay(self.context.image, remove=remove, add=add)
                    with self.assertRaises(ValueError):
                        self.review(record, context)
            for address in (h + 25, data + 42, parent + record["parent_size"] - 2):
                context = copy.copy(self.context)
                context.image = Overlay(self.context.image, add=[address])
                with self.assertRaises(ValueError):
                    self.review(record, context)

    def test_foreign_graph_edges_are_rejected(self):
        for record, other in permutations(self.records, 2):
            proof, foreign = self.proof(record), self.proof(other)
            for address, destination in ((proof["parent_candidate"] + 6, foreign["handler"]["address"]),
                                          (proof["handler"]["address"] + 18, foreign["descriptor"]["address"] + 8)):
                with self.assertRaises(EHEvidenceError):
                    self.review(record, self.mutate("image", address, struct.pack("<I", destination)))

    def test_field_scope_uses_annotation_source_and_complete_parent(self):
        for record in self.records:
            proof = self.proof(record)
            unit = self.units[f'reference-{record["parent_target"]:08x}']
            field = handler_field(proof)
            validate_field(self.context.eh_handlers, unit, field, proof["handler"]["address"])
            for changed in (dict(unit, source="src/UpdateFunc.cpp"), dict(unit, compare_size=unit["size"] - 1)):
                with self.assertRaises(EHEvidenceError):
                    validate_field(self.context.eh_handlers, changed, field, proof["handler"]["address"])

    def test_ordinary_body_bytes_remain_unmasked(self):
        for record in self.records:
            proof = self.proof(record)
            offset, value = (353, b"\xc9") if record["parent_target"] == 0x45d850 else (37, b"\xf1")
            context = self.mutate("image", proof["parent_candidate"] + offset, value)
            self.review(record, context)
            result = context.compare(self.units[f'reference-{record["parent_target"]:08x}'])
            self.assertEqual((result["result"], result["compared_size"], result["matched_bytes"]),
                             ("mismatch", record["parent_size"], record["parent_size"] - 1))

    def test_release_uses_one_saved_esi_no_local_and_node_minus_eight(self):
        record = next(r for r in self.records if r["parent_target"] == 0x45d850)
        proof = self.proof(record)
        self.assertEqual(proof["cookie_offset"], -4 - 4)
        self.assertNotIn("array_delete", proof)
        self.assertNotIn("producer_witness", proof)
        base = proof["parent_candidate"]
        self.assertEqual(self.context.image.read_address(base + 17, 2), b"\x56\xa1")
        self.assertEqual(self.context.image.read_address(base + 26, 9), bytes.fromhex("8d45f464a300000000"))
        self.assertEqual(self.context.image.read_address(base + 364, 6), bytes.fromhex("595e8be55dc3"))

    def test_release_cookie_displacement_and_saved_register_are_fixed(self):
        record = next(r for r in self.records if r["parent_target"] == 0x45d850)
        proof = self.proof(record)
        for slot in (-4, -12, -16, -20, -24):
            with self.subTest(slot=slot), self.assertRaises(EHEvidenceError):
                self.review(record, self.mutate("image", proof["handler"]["address"] + 9, struct.pack("<b", slot)))
        for opcode in (b"\x51", b"\x53", b"\x57"):
            with self.subTest(opcode=opcode), self.assertRaises(EHEvidenceError):
                self.review(record, self.mutate("image", proof["parent_candidate"] + 17, opcode))

    def test_release_does_not_admit_another_parent_with_an_unreviewed_frame(self):
        record = next(r for r in self.records if r["parent_target"] == 0x45d850)
        with self.assertRaisesRegex(EHEvidenceError, "fixed complete parent"):
            self.review(dict(record, parent_symbol="?initialize@SoundManager@@QAEHPAUHWND__@@@Z",
                             parent_target=0x45d510, parent_size=708))


if __name__ == "__main__":
    unittest.main()
