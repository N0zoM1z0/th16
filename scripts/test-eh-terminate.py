#!/usr/bin/env python3
"""Refusal controls for two complete noexcept destructor and terminate graphs."""
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


class TerminateEHControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        cls.records = [r for r in tomllib.loads((ROOT / "config/eh-handlers.toml").read_text())["handlers"]
                       if r.get("profile") == "two-state-terminate-v1"]
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
                                      {address + i: v for i, v in enumerate(payload)}))
        return context

    def test_both_complete_graphs_and_primary_owners_pass(self):
        self.assertEqual({r["parent_target"] for r in self.records}, {0x4099a0, 0x42f2d0})
        self.assertEqual(len(self.records), 2)
        for record in self.records:
            proof = self.review(record)
            self.assertEqual(proof, self.proof(record))
            self.assertEqual((proof["handler"]["size"], proof["descriptor"]["size"]), (27, 52))
            self.assertEqual((proof["descriptor"]["func_info_offset"], proof["descriptor"]["unwind_offset"]), (16, 0))
            result = self.context.compare(self.units[f'reference-{record["parent_target"]:08x}'])
            self.assertEqual((result["result"], result["compared_size"]), ("exact", record["parent_size"]))
            self.assertEqual(result["auxiliary_eh_owners"], [proof])

    def test_verifier_module_is_fingerprinted(self):
        path = "scripts/eh_terminate.py"
        self.assertEqual(self.context.before[path], hashlib.sha256((ROOT / path).read_bytes()).hexdigest())

    def test_fixed_roles_extents_flags_and_keys_are_required(self):
        for record in self.records:
            for change in (dict(source="src/Thread.cpp"), dict(parent_symbol=record["parent_symbol"] + "x"),
                           dict(parent_target=record["parent_target"] + 1),
                           dict(parent_size=record["parent_size"] - 1), dict(size=26), dict(size=28),
                           dict(func_info_size=36), dict(func_info_size=44), dict(func_info_size=51),
                           dict(eh_flags=1), dict(cookie_offset=-24), dict(states=2), dict(action=0x476b19),
                           dict(profile="empty-eh3-saved-ebx-esi-edi-v1")):
                with self.subTest(change=change), self.assertRaises(EHEvidenceError):
                    self.review(dict(record, **change))

    def test_original_parent_handler_and_metadata_hashes_are_required(self):
        for record in self.records:
            for field in ("parent_sha256", "target_sha256", "func_info_sha256"):
                with self.assertRaisesRegex(EHEvidenceError, "hash mismatch"):
                    self.review(dict(record, **{field: "0" * 64}))

    def test_every_candidate_handler_and_metadata_byte_is_checked(self):
        for record in self.records:
            for role in ("handler", "descriptor"):
                owner = self.proof(record)[role]
                for offset in range(owner["size"]):
                    address = owner["address"] + offset
                    value = self.context.image.read_address(address, 1)[0] ^ 1
                    with self.subTest(role=role, offset=offset), self.assertRaises(ValueError):
                        self.review(record, self.mutate("image", address, bytes([value])))

    def test_every_terminate_body_thunk_and_seh_byte_is_checked(self):
        record = self.records[0]
        proof = self.proof(record)["terminate"]
        thunk = next(p["address"] for p in self.context.publics if p["symbol"] == "___std_terminate")
        for base, size in ((thunk, 5), (proof["candidate"], 60), (proof["candidate_seh_table"], 28)):
            for offset in range(size):
                value = self.context.image.read_address(base + offset, 1)[0] ^ 1
                with self.subTest(base=base, offset=offset), self.assertRaises(ValueError):
                    self.review(record, self.mutate("image", base + offset, bytes([value])))

    def test_original_terminate_body_and_internal_seh_roles_are_checked(self):
        record = self.records[0]
        for base, offsets in ((0x476b19, range(5)), (0x47b825, (0, 3, 8, 13, 19, 24, 32, 38, 40, 43, 44, 47, 55)),
                              (0x49ba78, range(28))):
            for offset in offsets:
                value = self.context.target.read_address(base + offset, 1)[0] ^ 1
                with self.subTest(base=base, offset=offset), self.assertRaises(EHEvidenceError):
                    self.review(record, self.mutate("target", base + offset, bytes([value])))

    def test_original_metadata_semantics_survive_updated_hashes(self):
        for record in self.records:
            for offset in (0, 4, 8, 12, 28, 32, 36, 40, 44, 48):
                address = record["func_info_target"] + offset
                value = self.context.target.read_address(address, 1)[0] ^ 1
                context = self.mutate("target", address, bytes([value]))
                changed = dict(record, func_info_sha256=hashlib.sha256(
                    context.target.read_address(record["func_info_target"], 52)).hexdigest())
                with self.subTest(offset=offset), self.assertRaisesRegex(EHEvidenceError, "two-state graph"):
                    self.review(changed, context)

    def test_original_frame_semantics_survive_updated_parent_hashes(self):
        for record in self.records:
            offset = 966 if record["parent_target"] == 0x4099a0 else 301
            context = self.mutate("target", record["parent_target"] + offset, b"\x02")
            changed = dict(record, parent_sha256=hashlib.sha256(context.target.read_address(
                record["parent_target"], record["parent_size"])).hexdigest())
            with self.assertRaisesRegex(EHEvidenceError, "protected frame"):
                self.review(changed, context)

    def test_stage_zero_state_definition_cannot_change(self):
        record = next(r for r in self.records if r["parent_target"] == 0x4099a0)
        for side, base in (("target", record["parent_target"]), ("image", self.proof(record)["parent_candidate"])):
            context = self.mutate(side, base + 891, bytes.fromhex("33d2"))
            changed = dict(record)
            if side == "target":
                changed["parent_sha256"] = hashlib.sha256(context.target.read_address(base, 994)).hexdigest()
            with self.assertRaisesRegex(EHEvidenceError, "defining XOR"):
                self.review(changed, context)
        parent = self.proof(record)["parent_candidate"]
        for offset, payload, reason in ((893, bytes.fromhex("8bc8"), "clobbered"),
                                        (886, bytes.fromhex("e902000000"), "bypassed")):
            with self.subTest(reason=reason), self.assertRaisesRegex(EHEvidenceError, reason):
                self.review(record, self.mutate("image", parent + offset, payload))

    def test_candidate_states_cookie_and_restoration_are_checked(self):
        for record in self.records:
            offsets = (17, 20, 24, 28, 65, 938, 966, 978, 979, 993) if record["parent_target"] == 0x4099a0 else (
                17, 18, 22, 26, 56, 301, 332, 344, 345, 359)
            for offset in offsets:
                address = self.proof(record)["parent_candidate"] + offset
                value = self.context.image.read_address(address, 1)[0] ^ 1
                with self.subTest(offset=offset), self.assertRaises(EHEvidenceError):
                    self.review(record, self.mutate("image", address, bytes([value])))

    def test_interior_return_cannot_bypass_the_complete_restore(self):
        for record in self.records:
            offset = 40 if record["parent_target"] == 0x4099a0 else 38
            with self.assertRaisesRegex(EHEvidenceError, "protected frame"):
                self.review(record, self.mutate("image", self.proof(record)["parent_candidate"] + offset, b"\xc3\x90"))

    def test_existing_profiles_keep_their_fixed_cookie_displacements(self):
        all_records = tomllib.loads((ROOT / "config/eh-handlers.toml").read_text())["handlers"]
        for record in all_records:
            if record.get("profile") == "two-state-terminate-v1":
                continue
            proof = self.context.eh_handlers[(record["source"], record["parent_symbol"])]
            address = proof["handler"]["address"] + 9
            # The independently reviewed AnmManager aggregate already uses
            # node-24. Mutate its actual value rather than rewriting it unchanged.
            value = b"\xec" if self.context.image.read_address(address, 1) == b"\xe8" else b"\xe8"
            with self.subTest(parent=record["parent_target"]), self.assertRaises(EHEvidenceError):
                self.review(record, self.mutate("image", address, value))

    def test_all_runtime_roles_require_independent_bindings(self):
        for name in ("___std_terminate", "_terminate", "__SEH_prolog4_GS", "___acrt_getptd", "_abort",
                     "@__security_check_cookie@4", "___CxxFrameHandler3"):
            for field, value in (("kind", "literal"), ("target", 0), ("size", 1)):
                context = copy.copy(self.context)
                context.reviewed_linkages = copy.deepcopy(self.context.reviewed_linkages)
                context.reviewed_linkages[name][field] = value
                with self.subTest(name=name, field=field), self.assertRaisesRegex(EHEvidenceError, "runtime"):
                    self.review(self.records[0], context)

    def test_complete_candidate_private_extents_and_modules_are_required(self):
        for record in self.records:
            for role in ("handler", "descriptor"):
                owner = self.proof(record)[role]
                for field, value in (("size", owner["size"] - 1), ("module_index", owner["module_index"] + 1)):
                    pdb = copy.deepcopy(self.pdb)
                    row = next(r for r in pdb["contributions"] if self.context.image.image_base
                               + self.context.image.section(r["section_number"]).rva + r["section_offset"] == owner["address"])
                    row[field] = value
                    with self.subTest(role=role, field=field), self.assertRaises(EHEvidenceError):
                        self.review(record, pdb=pdb)

    def test_terminate_private_seh_owner_cannot_be_split_or_aliased(self):
        record = self.records[0]
        base = self.proof(record)["terminate"]["candidate_seh_table"]
        for mode in ("size", "module", "duplicate"):
            pdb = copy.deepcopy(self.pdb)
            row = next(r for r in pdb["contributions"] if self.context.image.image_base
                       + self.context.image.section(r["section_number"]).rva + r["section_offset"] == base)
            if mode == "size":
                row["size"] = 24
            elif mode == "module":
                row["module_index"] += 1
            else:
                pdb["contributions"].append(dict(row))
            with self.subTest(mode=mode), self.assertRaises(EHEvidenceError):
                self.review(record, pdb=pdb)
        for field, value in (("flags", ["f"]), ("section_number", 1),
                             ("section_offset", 0), ("object", "libucrt:foreign.obj")):
            statics = copy.deepcopy(self.statics)
            row = next(r for r in statics if r["symbol"] == "__sehtable$_terminate")
            row[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(EHEvidenceError, "private runtime owner"):
                self.review(record, statics=statics)

    def test_private_names_cannot_be_missing_duplicated_or_moved(self):
        for record in self.records:
            for prefix in ("__ehhandler$", "__ehfuncinfo$", "__unwindtable$"):
                row = next(r for r in self.statics if r["symbol"] == prefix + record["parent_symbol"])
                for rows in ([r for r in self.statics if r is not row], self.statics + [dict(row)]):
                    with self.assertRaises(EHEvidenceError):
                        self.review(record, statics=rows)

    def test_parent_public_and_source_ownership_are_required(self):
        for record in self.records:
            context = copy.copy(self.context)
            context.linked = copy.deepcopy(self.context.linked)
            row = next(r for r in context.linked["functions"] if r["symbol"] == record["parent_symbol"])
            row["pdb_object"] = row["pdb_object"].replace(".obj", "-foreign.obj")
            with self.assertRaisesRegex(EHEvidenceError, "source producer"):
                self.review(record, context)
            context = copy.copy(self.context)
            context.publics = [r for r in self.context.publics if r["symbol"] != record["parent_symbol"]]
            with self.assertRaises(EHEvidenceError):
                self.review(record, context)

    def test_all_graph_pointer_relocations_and_crossing_fields_are_required(self):
        for record in self.records:
            proof = self.proof(record)
            h, data, parent = proof["handler"]["address"], proof["descriptor"]["address"], proof["parent_candidate"]
            term = proof["terminate"]
            locations = [h + 18, data + 4, data + 12, data + 24, parent + 6,
                         parent + (24 if record["parent_target"] == 0x4099a0 else 22),
                         term["candidate"] + 3, term["candidate"] + 32,
                         term["candidate_seh_table"] + 20, term["candidate_seh_table"] + 24]
            for location in locations:
                for remove, add in (([location], []), ([], [location])):
                    context = copy.copy(self.context)
                    context.image = Overlay(self.context.image, remove=remove, add=add)
                    with self.subTest(location=location), self.assertRaises(ValueError):
                        self.review(record, context)
            for location in (h + 25, data + 50, parent + record["parent_size"] - 2,
                             term["candidate"] + 58, term["candidate_seh_table"] + 26):
                context = copy.copy(self.context)
                context.image = Overlay(self.context.image, add=[location])
                with self.assertRaises(ValueError):
                    self.review(record, context)

    def test_load_config_cookie_and_guard_storage_are_independent_witnesses(self):
        record = self.records[0]
        for offset in (60, 72):
            load = self.context.image.image_base + self.context.image.directories[10][0]
            value = struct.unpack("<I", self.context.image.read_address(load + offset, 4))[0]
            with self.assertRaises(EHEvidenceError):
                self.review(record, self.mutate("image", load + offset, struct.pack("<I", value + 4)))

    def test_foreign_parent_graph_edges_are_rejected(self):
        for record, other in ((self.records[0], self.records[1]), (self.records[1], self.records[0])):
            proof, foreign = self.proof(record), self.proof(other)
            for location, destination in ((proof["parent_candidate"] + 6, foreign["handler"]["address"]),
                                          (proof["handler"]["address"] + 18, foreign["descriptor"]["address"] + 16)):
                with self.assertRaises(EHEvidenceError):
                    self.review(record, self.mutate("image", location, struct.pack("<I", destination)))

    def test_field_binding_cannot_leave_its_whole_parent(self):
        for record in self.records:
            proof = self.proof(record)
            unit = self.units[f'reference-{record["parent_target"]:08x}']
            field = handler_field(proof)
            validate_field(self.context.eh_handlers, unit, field, proof["handler"]["address"])
            for changed in (dict(unit, source="src/Thread.cpp"), dict(unit, compare_size=unit["size"] - 1)):
                with self.assertRaises(EHEvidenceError):
                    validate_field(self.context.eh_handlers, changed, field, proof["handler"]["address"])

    def test_ordinary_body_bytes_remain_unmasked(self):
        for record in self.records:
            proof = self.proof(record)
            stage = record["parent_target"] == 0x4099a0
            context = self.mutate("image", proof["parent_candidate"] + (41 if stage else 39),
                                  b"\xf1" if stage else b"\xf9")
            self.review(record, context)
            result = context.compare(self.units[f'reference-{record["parent_target"]:08x}'])
            self.assertEqual((result["result"], result["compared_size"], result["matched_bytes"]),
                             ("mismatch", record["parent_size"], record["parent_size"] - 1))


if __name__ == "__main__":
    unittest.main()
