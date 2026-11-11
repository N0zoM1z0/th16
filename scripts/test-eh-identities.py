#!/usr/bin/env python3
"""Mutation controls for complete, parent-scoped empty EH3 graph identities."""
import copy
import struct
import tomllib
import unittest

from eh_identity import (EHEvidenceError, handler_field, review_handler,
                         validate_field)
from linked_image import map_statics, pdb_section_contributions, linked_code_fields
from strict_oracle import Context, Incomplete, ROOT, replay_owner


class Overlay:
    def __init__(self, image, changes=None, remove=(), add=()):
        self.image, self.changes = image, changes or {}
        self.remove, self.add = set(remove), list(add)

    def __getattr__(self, name):
        return getattr(self.image, name)

    def read_address(self, address, size):
        payload = bytearray(self.image.read_address(address, size))
        for p, value in self.changes.items():
            if address <= p < address + size:
                payload[p - address] = value
        return bytes(payload)

    def base_relocations(self):
        return sorted([p for p in self.image.base_relocations() if p not in self.remove] + self.add)


class EHIdentityControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        cls.records = tomllib.loads((ROOT / "config/eh-handlers.toml").read_text())["handlers"]
        cls.record = cls.records[0]
        cls.statics = map_statics(cls.context.directory / "th16.map")
        cls.pdb = pdb_section_contributions(cls.context.directory / "th16.pdb")
        cls.proof = cls.context.eh_handlers[(cls.record["source"], cls.record["parent_symbol"])]

    def review(self, context=None, record=None, statics=None, pdb=None):
        return review_handler(context or self.context, record or self.record,
                              statics if statics is not None else self.statics,
                              pdb if pdb is not None else self.pdb)

    def mutate(self, side, address, payload):
        context = copy.copy(self.context)
        changes = {address + i: value for i, value in enumerate(payload)}
        setattr(context, side, Overlay(getattr(context, side), changes))
        return context

    def contribution(self, pdb, role):
        address = self.proof[role]["address"]
        return next(r for r in pdb["contributions"] if self.context.image.image_base
                    + self.context.image.section(r["section_number"]).rva + r["section_offset"] == address)

    def unit(self, proof=None):
        proof = proof or self.proof
        target = proof["parent_target"]
        function = next(r for r in self.context.linked["functions"] if r["symbol"] == proof["parent_symbol"])
        address = proof["parent_candidate"]
        size = proof["parent_size"]
        unit = dict(source=proof["source"], symbol=proof["parent_symbol"], object=proof["handler"]["object"].replace("\\", "/").rsplit("/", 1)[-1],
                    artifact_kind="linked-pe", candidate_address=address, target_address=target,
                    size=size, compare_size=size, profile=self.context.receipt["compiler_profile"],
                    link_profile=self.context.receipt["linker_profile"], linkages=[])
        target_fields = {(r["offset"], r["type"]): r for r in linked_code_fields(
            self.context.target, [], target, size)["fields"]}
        original = self.context.target.read_address(target, size)
        for r in linked_code_fields(self.context.image, self.context.publics, address, size)["fields"]:
            if r["offset"] == 6:
                unit["linkages"].append(handler_field(proof))
            else:
                symbols = [p["symbol"] for p in self.context.publics if p["address"] == r["candidate_target"]]
                self.assertEqual(len(symbols), 1)
                destination = (struct.unpack_from("<I", original, r["offset"])[0] if r["type"] == "DIR32"
                               else target_fields[(r["offset"], r["type"])]["candidate_target"])
                unit["linkages"].append(dict(offset=r["offset"], width=r["width"], type=r["type"],
                    symbol=symbols[0], target=destination, addend=0))
        return function, unit

    def test_both_complete_parent_owners_pass(self):
        for proof in self.context.eh_handlers.values():
            with self.subTest(parent=proof["parent_symbol"]):
                _, unit = self.unit(proof)
                result = self.context.compare(unit)
                self.assertEqual((result["result"], result["compared_size"]), ("exact", proof["parent_size"]))
                self.assertEqual(len(result["linkages"]), 4)
                self.assertEqual(result["auxiliary_eh_owners"], [proof])

    def test_all_target_owner_hashes_are_required(self):
        for key in ("parent_sha256", "target_sha256", "func_info_sha256"):
            with self.subTest(key=key), self.assertRaisesRegex(EHEvidenceError, "extent hash"):
                self.review(record=dict(self.record, **{key: "0" * 64}))

    def test_target_graph_byte_mutation_is_rejected(self):
        for key in ("parent_target", "target", "func_info_target"):
            address = self.record[key]
            with self.subTest(key=key), self.assertRaisesRegex(EHEvidenceError, "extent hash"):
                self.review(context=self.mutate("target", address, b"\xcc"))

    def test_partial_or_expanded_auxiliary_extents_are_rejected(self):
        for key, sizes in (("size", [26, 28]), ("func_info_size", [32, 40])):
            for size in sizes:
                with self.subTest(key=key, size=size), self.assertRaisesRegex(EHEvidenceError, "complete 27-byte"):
                    self.review(record=dict(self.record, **{key: size}))

    def test_parent_boundary_cannot_be_truncated(self):
        with self.assertRaisesRegex(EHEvidenceError, "target extent is not complete"):
            self.review(record=dict(self.record, parent_size=69))

    def test_wrong_source_and_parent_symbol_are_rejected(self):
        for key, value in (("source", "src/Stage.cpp"), ("parent_symbol", "??1StageInner@@QAE@XZ")):
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.review(record=dict(self.record, **{key: value}))

    def test_missing_or_duplicate_map_statics_are_rejected(self):
        symbol = self.proof["handler"]["symbol"]
        match = next(s for s in self.statics if s["symbol"] == symbol)
        for statics in ([s for s in self.statics if s is not match], self.statics + [match]):
            with self.assertRaisesRegex(EHEvidenceError, "qualified MAP static"):
                self.review(statics=statics)

    def test_public_or_interior_map_alias_is_rejected(self):
        match = next(s for s in self.statics if s["symbol"] == self.proof["handler"]["symbol"])
        for delta in (0, 1):
            context = copy.copy(self.context)
            context.publics = self.context.publics + [dict(match, symbol="_unreviewed_alias", section_offset=match["section_offset"] + delta)]
            with self.subTest(delta=delta), self.assertRaisesRegex(EHEvidenceError, "colliding or interior"):
                self.review(context=context)

    def test_wrong_map_object_or_va_is_rejected(self):
        for changes in (dict(object="Stage.obj"), dict(address=1), dict(object="Z:/wrong/Item.obj")):
            statics = copy.deepcopy(self.statics)
            next(s for s in statics if s["symbol"] == self.proof["handler"]["symbol"]).update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.review(statics=statics)

    def test_pdb_must_own_both_complete_extents(self):
        for role, sizes in (("handler", [26, 28]), ("descriptor", [32, 40])):
            for size in sizes:
                pdb = copy.deepcopy(self.pdb)
                self.contribution(pdb, role)["size"] = size
                with self.subTest(role=role, size=size), self.assertRaisesRegex(EHEvidenceError, "complete reviewed owner"):
                    self.review(pdb=pdb)

    def test_wrong_or_duplicate_pdb_owner_is_rejected(self):
        for key, value in (("module_index", 0), ("object", "Z:/wrong/Item.obj")):
            pdb = copy.deepcopy(self.pdb)
            self.contribution(pdb, "handler")[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(EHEvidenceError, "source producer object"):
                self.review(pdb=pdb)
        pdb = copy.deepcopy(self.pdb)
        pdb["contributions"].append(copy.deepcopy(self.contribution(pdb, "handler")))
        with self.assertRaisesRegex(EHEvidenceError, "same-start PDB"):
            self.review(pdb=pdb)

    def test_overlapping_pdb_contribution_is_rejected(self):
        pdb = copy.deepcopy(self.pdb)
        other = dict(self.contribution(pdb, "handler"), size=2)
        other["section_offset"] -= 1
        pdb["contributions"].append(other)
        with self.assertRaisesRegex(EHEvidenceError, "overlaps another PDB"):
            self.review(pdb=pdb)

    def test_descriptor_must_be_read_only_non_code(self):
        for bits in (0x80000000, 0x20000000, 0x20):
            pdb = copy.deepcopy(self.pdb)
            self.contribution(pdb, "descriptor")["characteristics"] |= bits
            with self.subTest(bits=bits), self.assertRaisesRegex(EHEvidenceError, "section permissions"):
                self.review(pdb=pdb)

    def test_every_handler_instruction_is_verified(self):
        address = self.proof["handler"]["address"]
        for offset in (0, 3, 6, 9, 11, 12, 13, 17, 22, 23, 26):
            value = self.context.image.read_address(address + offset, 1)[0] ^ 1
            with self.subTest(offset=offset), self.assertRaisesRegex(EHEvidenceError, "complete GS/FuncInfo/runtime graph"):
                self.review(context=self.mutate("image", address + offset, bytes([value])))

    def test_identical_descriptor_of_another_parent_is_rejected(self):
        other = next(p for p in self.context.eh_handlers.values() if p is not self.proof)
        address = self.proof["handler"]["address"] + 18
        self.assertEqual(self.context.image.read_address(other["descriptor"]["address"], 36),
                         self.context.image.read_address(self.proof["descriptor"]["address"], 36))
        with self.assertRaisesRegex(EHEvidenceError, "complete GS/FuncInfo/runtime graph"):
            self.review(context=self.mutate("image", address, struct.pack("<I", other["descriptor"]["address"])))

    def test_nonempty_metadata_and_changed_flags_are_rejected(self):
        address = self.proof["descriptor"]["address"]
        for offset in range(0, 36, 4):
            with self.subTest(offset=offset), self.assertRaisesRegex(EHEvidenceError, "complete reviewed empty descriptor"):
                self.review(context=self.mutate("image", address + offset, struct.pack("<I", 1)))
        with self.assertRaises(EHEvidenceError):
            self.review(record=dict(self.record, eh_flags=1))

    def test_missing_extra_duplicate_and_crossing_relocations_are_rejected(self):
        handler, info, parent = (self.proof["handler"]["address"], self.proof["descriptor"]["address"], self.proof["parent_candidate"])
        for remove, add in (([handler + 18], []), ([], [handler + 18]), ([], [handler - 1]),
                            ([], [handler + 26]), ([], [info]), ([], [info + 35]), ([parent + 6], [])):
            context = copy.copy(self.context)
            context.image = Overlay(context.image, remove=remove, add=add)
            with self.subTest(remove=remove, add=add), self.assertRaisesRegex(EHEvidenceError, "PE relocations"):
                self.review(context=context)

    def test_parent_registration_must_point_to_its_named_handler(self):
        address = self.proof["parent_candidate"]
        for offset in (0, 3, 5, 6, 10, 16):
            value = self.context.image.read_address(address + offset, 1)[0] ^ 1
            with self.subTest(offset=offset), self.assertRaisesRegex(EHEvidenceError, "frame-registration"):
                self.review(context=self.mutate("image", address + offset, bytes([value])))

    def test_runtime_bindings_are_mandatory(self):
        for symbol in ("@__security_check_cookie@4", "___CxxFrameHandler3"):
            context = copy.copy(self.context)
            context.reviewed_linkages = dict(context.reviewed_linkages)
            del context.reviewed_linkages[symbol]
            with self.subTest(symbol=symbol), self.assertRaisesRegex(EHEvidenceError, "independent complete binding"):
                self.review(context=context)

    def test_field_cannot_override_owner_offset_kind_addend_or_locality(self):
        _, unit = self.unit()
        field = handler_field(self.proof)
        for change in (dict(offset=7), dict(type="REL32"), dict(width=2), dict(addend=1),
                       dict(local=True), dict(eh_handler=False), dict(target=1), dict(storage_size=27)):
            with self.subTest(change=change), self.assertRaisesRegex(EHEvidenceError, "exact reviewed parent-scoped"):
                validate_field(self.context.eh_handlers, unit, dict(field, **change), self.proof["handler"]["address"])

    def test_field_cannot_be_reused_by_another_parent_or_source(self):
        _, unit = self.unit()
        for changes in (dict(source="src/Stage.cpp"), dict(symbol="??1StageInner@@QAE@XZ"),
                        dict(candidate_address=1), dict(target_address=1), dict(size=69, compare_size=69)):
            with self.subTest(changes=changes), self.assertRaises(EHEvidenceError):
                validate_field(self.context.eh_handlers, dict(unit, **changes), handler_field(self.proof), self.proof["handler"]["address"])

    def test_low_level_replay_requires_the_reviewed_graph(self):
        function, unit = self.unit()
        with self.assertRaisesRegex(Incomplete, "reviewed parent-scoped"):
            replay_owner(self.context.image, self.context.target, self.context.publics, function, unit)
        unit["linkages"][0].pop("eh_handler")
        with self.assertRaisesRegex(Incomplete, "one unique linked symbol"):
            replay_owner(self.context.image, self.context.target, self.context.publics, function, unit)

    def test_complete_parent_body_is_still_compared_without_masks(self):
        function, unit = self.unit()
        # Alter the array count, outside the registration and all relocation fields.
        context = self.mutate("image", unit["candidate_address"] + 40, b"\x57")
        self.review(context=context)
        result = replay_owner(context.image, context.target, context.publics, function, unit,
                              eh_handlers=self.context.eh_handlers)
        self.assertEqual((result["result"], result["compared_size"], result["matched_bytes"]), ("mismatch", 70, 69))

    def test_low_level_replay_checks_the_actual_parent_identity(self):
        function, unit = self.unit()
        with self.assertRaisesRegex(Incomplete, "actual candidate parent"):
            replay_owner(self.context.image, self.context.target, self.context.publics,
                         dict(function, symbol="_foreign_parent"), unit, eh_handlers=self.context.eh_handlers)

    def test_review_inputs_are_in_the_oracle_identity(self):
        for path in ("config/eh-handlers.toml", "scripts/eh_identity.py"):
            self.assertIn(path, self.context.before)


if __name__ == "__main__":
    unittest.main()
