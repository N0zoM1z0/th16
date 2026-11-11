#!/usr/bin/env python3
"""Refusal controls for the complete AnmManager constructor EH aggregate."""
import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import tomllib
import unittest

from eh_identity import EHEvidenceError, handler_field, review_handler, validate_field
from linked_image import map_statics, pdb_section_contributions
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


class ConstructorEHControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        records = tomllib.loads((ROOT / "config/eh-handlers.toml").read_text())["handlers"]
        cls.record = next(r for r in records if r.get("profile") == "anm-manager-constructor-v1")
        cls.proof = cls.context.eh_handlers[(cls.record["source"], cls.record["parent_symbol"])]
        cls.statics = map_statics(cls.context.directory / "th16.map")
        cls.pdb = pdb_section_contributions(cls.context.directory / "th16.pdb")
        # Generate current parent linkages through the actual focused-audit path;
        # a stale canonical report is never the positive integration witness.
        with tempfile.TemporaryDirectory(dir=ROOT / ".analysis") as temporary:
            output = Path(temporary) / "focused.json"
            run = subprocess.run([sys.executable, str(ROOT / "scripts/audit-reference.py"),
                                  "--address", hex(cls.record["parent_target"]), "--json", str(output)],
                                 cwd=ROOT, capture_output=True, text=True, timeout=60)
            if run.returncode:
                raise RuntimeError(run.stderr)
            cls.report = json.loads(output.read_text())["functions"][0]
        cls.unit = dict(source=cls.record["source"], symbol=cls.record["parent_symbol"],
                        artifact_kind="linked-pe", object="AnmRender.obj",
                        candidate_address=cls.proof["parent_candidate"], target_address=cls.record["parent_target"],
                        size=5071, compare_size=5071, profile=cls.context.receipt["compiler_profile"],
                        link_profile=cls.context.receipt["linker_profile"],
                        linkages=[{k: v for k, v in f.items() if k not in ("candidate_target", "encoded")}
                                  for f in cls.report["linkages"]])
        cls.function = next(f for f in cls.context.linked["functions"] if f["symbol"] == cls.unit["symbol"])

    def review(self, context=None, record=None, statics=None, pdb=None):
        return review_handler(context or self.context, record or self.record,
                              statics if statics is not None else self.statics,
                              pdb if pdb is not None else self.pdb)

    def mutate(self, side, address, payload):
        context = copy.copy(self.context)
        setattr(context, side, Overlay(getattr(context, side),
                                      {address + i: b for i, b in enumerate(payload)}))
        return context

    def contribution(self, pdb, role):
        owner = self.proof[role]
        return next(r for r in pdb["contributions"] if self.context.image.image_base
                    + self.context.image.section(r["section_number"]).rva + r["section_offset"] == owner["address"])

    def test_both_whole_owners_and_complete_parent_are_retained(self):
        proof = self.review()
        self.assertEqual(proof, self.proof)
        self.assertEqual((proof["code_owner"]["size"], proof["descriptor"]["size"]), (136, 76))
        self.assertEqual(proof["handler"]["address"] - proof["code_owner"]["address"], 109)
        self.assertNotIn("size", proof["handler"])
        result = self.context.compare(self.unit)
        self.assertEqual(result["compared_size"], 5071)
        self.assertIn(result["result"], ("exact", "mismatch"))
        self.assertEqual(result["matched_bytes"], self.report["matched_bytes"])
        self.assertEqual(result["auxiliary_eh_owners"], [proof])

    def test_profiles_sources_and_all_extents_are_fixed(self):
        for change in (dict(profile="unknown"), dict(source="src/AnmVm.cpp"),
                       dict(parent_symbol="??1AnmManager@@QAE@XZ"), dict(parent_size=5070),
                       dict(size=27), dict(size=135), dict(size=137), dict(func_info_size=36),
                       dict(func_info_size=75), dict(func_info_size=77), dict(eh_flags=5),
                       dict(target=self.record["target"] + 1)):
            with self.subTest(change=change), self.assertRaises(EHEvidenceError):
                self.review(record=dict(self.record, **change))

    def test_every_candidate_code_and_metadata_byte_is_checked(self):
        for role in ("code_owner", "descriptor"):
            owner = self.proof[role]
            for offset in range(owner["size"]):
                address = owner["address"] + offset
                value = self.context.image.read_address(address, 1)[0] ^ 1
                with self.subTest(role=role, offset=offset), self.assertRaises(ValueError):
                    self.review(context=self.mutate("image", address, bytes([value])))

    def test_original_extent_hashes_and_bytes_are_required(self):
        for address_key, hash_key in (("parent_target", "parent_sha256"), ("code_target", "target_sha256"),
                                      ("func_info_target", "func_info_sha256")):
            with self.subTest(hash_key=hash_key), self.assertRaisesRegex(EHEvidenceError, "extent hash"):
                self.review(record=dict(self.record, **{hash_key: "0" * 64}))
            with self.subTest(address_key=address_key), self.assertRaisesRegex(EHEvidenceError, "extent hash"):
                self.review(context=self.mutate("target", self.record[address_key], b"\xcc"))

    def test_rehashed_original_actions_cannot_change_shape(self):
        # Rehashing is not a substitute for the reviewed instruction semantics.
        for offset in (2, 13, 18, 21, 26, 37, 51, 56, 67, 73, 81, 88, 90, 99, 108, 118, 120):
            base = self.record["code_target"]
            value = self.context.target.read_address(base + offset, 1)[0] ^ 1
            context = self.mutate("target", base + offset, bytes([value]))
            record = dict(self.record, target_sha256=hashlib.sha256(context.target.read_address(base, 136)).hexdigest())
            with self.subTest(offset=offset), self.assertRaisesRegex(EHEvidenceError, "original (action/handler|edge)"):
                self.review(context=context, record=record)

    def test_rehashed_original_state_maps_cannot_change_chain_or_flags(self):
        for offset in range(0, 76, 4):
            base = self.record["func_info_target"]
            value = self.context.target.read_address(base + offset, 1)[0] ^ 1
            context = self.mutate("target", base + offset, bytes([value]))
            record = dict(self.record, func_info_sha256=hashlib.sha256(context.target.read_address(base, 76)).hexdigest())
            with self.subTest(offset=offset), self.assertRaisesRegex(EHEvidenceError, "original state map"):
                self.review(context=context, record=record)

    def test_every_internal_name_is_required_exactly_once(self):
        names = self.proof["code_owner"]["internal_symbols"] | self.proof["descriptor"]["internal_symbols"]
        for name in names:
            match = next(r for r in self.statics if r["symbol"] == name)
            for statics in ([r for r in self.statics if r is not match], self.statics + [match]):
                with self.subTest(name=name, duplicate=len(statics) > len(self.statics)), self.assertRaises(EHEvidenceError):
                    self.review(statics=statics)

    def test_internal_name_offsets_vas_objects_and_roles_are_checked(self):
        for name in self.proof["code_owner"]["internal_symbols"] | self.proof["descriptor"]["internal_symbols"]:
            for change in (dict(section_offset=1), dict(address=1), dict(object="Other.obj"),
                           dict(object="Z:/wrong/AnmRender.obj"), dict(flags=["bad"])):
                statics = copy.deepcopy(self.statics)
                match = next(r for r in statics if r["symbol"] == name)
                if "flags" in change:
                    change = dict(flags=[] if "f" in match["flags"] else ["f"])
                match.update(change)
                with self.subTest(name=name, change=change), self.assertRaises(EHEvidenceError):
                    self.review(statics=statics)

    def test_unreviewed_public_or_private_aliases_are_rejected(self):
        for role in ("code_owner", "descriptor"):
            match = next(s for s in self.statics if s["symbol"] == self.proof[role]["symbol"])
            for delta in (0, 1, self.proof[role]["size"] - 1):
                alias = dict(match, symbol="_unreviewed_alias", section_offset=match["section_offset"] + delta,
                             address=match["address"] + delta)
                for public in (True, False):
                    context = copy.copy(self.context)
                    context.publics = context.publics + [alias] if public else context.publics
                    with self.subTest(role=role, delta=delta, public=public), self.assertRaises(EHEvidenceError):
                        self.review(context=context, statics=self.statics if public else self.statics + [alias])

    def test_reviewed_internal_names_cannot_become_public(self):
        for role in ("code_owner", "descriptor"):
            for name in self.proof[role]["internal_symbols"]:
                match = next(r for r in self.statics if r["symbol"] == name)
                context = copy.copy(self.context)
                context.publics = context.publics + [match]
                with self.subTest(name=name), self.assertRaises(EHEvidenceError):
                    self.review(context=context, statics=[r for r in self.statics if r is not match])

    def test_pdb_owners_cannot_be_truncated_extended_or_shifted(self):
        for role in ("code_owner", "descriptor"):
            size = self.proof[role]["size"]
            for change in (dict(size=size - 1), dict(size=size + 1), dict(size=27 if role == "code_owner" else 36),
                           dict(section_offset=self.contribution(self.pdb, role)["section_offset"] + 1)):
                pdb = copy.deepcopy(self.pdb)
                self.contribution(pdb, role).update(change)
                with self.subTest(role=role, change=change), self.assertRaises(EHEvidenceError):
                    self.review(pdb=pdb)

    def test_pdb_duplicates_overlap_source_modules_and_permissions_are_checked(self):
        for role in ("code_owner", "descriptor"):
            for change in (dict(module_index=0), dict(object="Z:/wrong/AnmRender.obj"),
                           dict(characteristics=0xE0000020), dict(characteristics=0xC0000040)):
                pdb = copy.deepcopy(self.pdb)
                self.contribution(pdb, role).update(change)
                with self.subTest(role=role, change=change), self.assertRaises(EHEvidenceError):
                    self.review(pdb=pdb)
            for delta in (0, -1, 1):
                pdb = copy.deepcopy(self.pdb)
                other = dict(self.contribution(pdb, role))
                other["section_offset"] += delta
                pdb["contributions"].append(other)
                with self.subTest(role=role, delta=delta), self.assertRaises(EHEvidenceError):
                    self.review(pdb=pdb)
        pdb = copy.deepcopy(self.pdb)
        next(m for m in pdb["modules"] if m["index"] == self.proof["code_owner"]["module_index"])["object"] = "Z:/wrong/AnmRender.obj"
        with self.assertRaises(EHEvidenceError):
            self.review(pdb=pdb)

    def test_all_pe_relocations_include_duplicates_and_crossing_fields(self):
        for role, offsets in (("code_owner", [9, 39, 83, 127]), ("descriptor", [8, 40, 48, 56, 64, 72])):
            owner = self.proof[role]
            base, size = owner["address"], owner["size"]
            trials = [([base + offset], []) for offset in offsets]
            trials += [([], [base + offset]) for offset in offsets + [-1, 0, size - 1]]
            for remove, add in trials:
                context = copy.copy(self.context)
                context.image = Overlay(context.image, remove=remove, add=add)
                with self.subTest(role=role, remove=remove, add=add), self.assertRaisesRegex(EHEvidenceError, "PE relocations"):
                    self.review(context=context)

    def test_original_owner_sections_must_have_complete_correct_roles(self):
        for key in ("code_target", "func_info_target"):
            base = self.record[key]
            for mode in ("permissions", "truncated"):
                context = copy.copy(self.context)
                context.target = copy.copy(context.target)
                context.target.sections = [
                    replace(s, **({"characteristics": s.characteristics | 0x80000000}
                                   if mode == "permissions" else {"raw_size": base - context.target.image_base - s.rva + 1}))
                    if context.target.image_base + s.rva <= base < context.target.image_base + s.rva + s.raw_size else s
                    for s in context.target.sections]
                with self.subTest(key=key, mode=mode), self.assertRaises(ValueError):
                    self.review(context=context)

    def test_original_inventory_must_match_all_five_complete_subscopes(self):
        base = self.record["code_target"]
        for action in (base, base + 8, base + 38, base + 68, base + 82):
            for mode in ("missing", "size", "end"):
                context = copy.copy(self.context)
                context.boundaries = copy.deepcopy(context.boundaries)
                if mode == "missing":
                    del context.boundaries[action]
                else:
                    context.boundaries[action]["size" if mode == "size" else "span_end"] = "1"
                with self.subTest(action=hex(action), mode=mode), self.assertRaisesRegex(EHEvidenceError, "unwind subscopes"):
                    self.review(context=context)
        for address in (base - 1, base + 1, base + 109, self.record["func_info_target"]):
            context = copy.copy(self.context)
            context.boundaries = dict(context.boundaries)
            context.boundaries[address] = dict(size="2", span_end=hex(address + 1))
            with self.subTest(address=hex(address)), self.assertRaises(EHEvidenceError):
                self.review(context=context)

    def test_cleanup_role_source_size_hash_and_destination_are_required(self):
        for index in range(3):
            for change in (dict(source="src/AnmRender.cpp"), dict(symbol="_wrong"), dict(size=1),
                           dict(sha256="0" * 64), dict(target=self.record["cleanup_entries"][index]["target"] + 1)):
                record = copy.deepcopy(self.record)
                record["cleanup_entries"][index].update(change)
                with self.subTest(index=index, change=change), self.assertRaises(EHEvidenceError):
                    self.review(record=record)
        record = copy.deepcopy(self.record)
        record["cleanup_entries"] = list(reversed(record["cleanup_entries"]))
        with self.assertRaises(EHEvidenceError):
            self.review(record=record)

    def test_parent_and_cleanup_candidate_ownership_are_required(self):
        for symbol in [self.record["parent_symbol"]] + [e["symbol"] for e in self.record["cleanup_entries"]]:
            for change in (dict(pdb_object="Z:/wrong/AnmRender.obj"), dict(size=1)):
                context = copy.copy(self.context)
                context.linked = copy.deepcopy(context.linked)
                next(f for f in context.linked["functions"] if f["symbol"] == symbol).update(change)
                with self.subTest(symbol=symbol, change=change), self.assertRaises(EHEvidenceError):
                    self.review(context=context)
            context = copy.copy(self.context)
            context.publics = [p for p in context.publics if p["symbol"] != symbol]
            with self.subTest(symbol=symbol), self.assertRaises(EHEvidenceError):
                self.review(context=context)

    def test_runtime_and_cookie_public_identities_are_unique(self):
        for symbol in ("??_M@YGXPAXIIP6EX0@Z@Z", "@__security_check_cookie@4",
                       "___CxxFrameHandler3", "___security_cookie"):
            match = next(p for p in self.context.publics if p["symbol"] == symbol)
            for publics in ([p for p in self.context.publics if p is not match], self.context.publics + [match]):
                context = copy.copy(self.context)
                context.publics = publics
                with self.subTest(symbol=symbol, duplicate=len(publics) > len(self.context.publics)), self.assertRaises(EHEvidenceError):
                    self.review(context=context)

    def test_runtime_bindings_are_required_independently(self):
        for symbol in ("??_M@YGXPAXIIP6EX0@Z@Z", "@__security_check_cookie@4", "___CxxFrameHandler3"):
            context = copy.copy(self.context)
            context.reviewed_linkages = dict(context.reviewed_linkages)
            del context.reviewed_linkages[symbol]
            with self.subTest(symbol=symbol), self.assertRaisesRegex(EHEvidenceError, "independent complete binding"):
                self.review(context=context)

    def test_parent_registration_saved_this_cookie_states_and_epilogue_are_required(self):
        base = self.proof["parent_candidate"]
        for offset in list(range(45)) + [0x69, 0x6c, 0x90, 0x93, 0xbc, 0xbf, 0xcd, 0xd0,
                                         0x2b8, 0x2ba, 0x13bd, 0x13bf, 0x13c0, 0x13cb, 0x13cd]:
            value = self.context.image.read_address(base + offset, 1)[0] ^ 1
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                self.review(context=self.mutate("image", base + offset, bytes([value])))
        for remove, add in (([base + 6], []), ([base + 24], []), ([], [base + 44])):
            context = copy.copy(self.context)
            context.image = Overlay(context.image, remove=remove, add=add)
            with self.subTest(remove=remove, add=add), self.assertRaisesRegex(EHEvidenceError, "PE relocations"):
                self.review(context=context)

    def test_cookie_identity_comes_from_both_load_config_directories(self):
        for side in ("image", "target"):
            image = getattr(self.context, side)
            address = image.image_base + image.directories[10][0] + 60
            with self.subTest(side=side), self.assertRaisesRegex(EHEvidenceError, "load-config identity"):
                self.review(context=self.mutate(side, address, struct.pack("<I", 1)))
        with self.assertRaises(EHEvidenceError):
            self.review(record=dict(self.record, cookie_target=1))

    def test_rehashed_original_parent_cannot_change_the_state_sequence(self):
        for offset in (0x6c, 0x93, 0xbf, 0xd0):
            parent = self.record["parent_target"]
            value = self.context.target.read_address(parent + offset, 1)[0] ^ 1
            context = self.mutate("target", parent + offset, bytes([value]))
            record = dict(self.record, parent_sha256=hashlib.sha256(context.target.read_address(parent, 5071)).hexdigest())
            with self.subTest(offset=offset), self.assertRaisesRegex(EHEvidenceError, "parent states"):
                self.review(context=context, record=record)

    def test_field_is_only_the_exact_complete_parent_handler_operand(self):
        field = handler_field(self.proof)
        base = self.proof["handler"]["address"]
        validate_field(self.context.eh_handlers, self.unit, field, base)
        for change in (dict(offset=7), dict(width=2), dict(type="REL32"), dict(addend=109),
                       dict(local=True), dict(target=self.record["code_target"]), dict(eh_handler=False)):
            with self.subTest(change=change), self.assertRaises(EHEvidenceError):
                validate_field(self.context.eh_handlers, self.unit, dict(field, **change), base)
        for change in (dict(source="src/AnmVm.cpp"), dict(symbol="_wrong"), dict(candidate_address=1),
                       dict(target_address=1), dict(size=5070, compare_size=5070)):
            with self.subTest(change=change), self.assertRaises(EHEvidenceError):
                validate_field(self.context.eh_handlers, dict(self.unit, **change), field, base)
        with self.assertRaises(EHEvidenceError):
            validate_field(self.context.eh_handlers, self.unit, field, self.proof["code_owner"]["address"])

    def test_low_level_replay_requires_the_scoped_proof(self):
        with self.assertRaisesRegex(Incomplete, "reviewed parent-scoped"):
            replay_owner(self.context.image, self.context.target, self.context.publics, self.function, self.unit)
        unit = copy.deepcopy(self.unit)
        next(f for f in unit["linkages"] if f.get("eh_handler")).pop("eh_handler")
        with self.assertRaisesRegex(Incomplete, "one unique linked symbol"):
            replay_owner(self.context.image, self.context.target, self.context.publics, self.function, unit)

    def test_complete_parent_body_still_has_no_byte_masks(self):
        # Change an ordinary member initializer outside all EH frame uses.
        context = self.mutate("image", self.proof["parent_candidate"] + 0x36, b"\x01")
        self.review(context=context)
        result = context.compare(self.unit)
        self.assertEqual((result["result"], result["compared_size"]), ("mismatch", 5071))
        self.assertEqual(result["matched_bytes"], self.report["matched_bytes"] - 1)
        self.assertIn(0x36, [r["offset"] for r in result["first_differences"]])


if __name__ == "__main__":
    unittest.main()
