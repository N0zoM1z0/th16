#!/usr/bin/env python3
"""Refuse partial sound/anchor aggregates and unreviewed sound-table address points."""
import copy
import csv
from dataclasses import replace
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

import capstone
from unittest.mock import patch

from linked_image import map_statics, pdb_section_contributions
from runtime_identity import RuntimeEvidenceError
from sound_data_identity import PROFILE, SYMBOL, review_sound_data, validate_sound_field
from strict_oracle import Context, Incomplete, ROOT

_spec = importlib.util.spec_from_file_location("aggregate_controls", ROOT / "scripts/test-eh-constructor.py")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
Overlay = _base.Overlay


class SoundDataControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        with (ROOT / "config/linkage-bindings.csv").open() as stream:
            cls.row = next(r for r in csv.DictReader(stream) if r["kind"] == PROFILE)
        cls.candidate = next(p["address"] for p in cls.context.publics if p["symbol"] == SYMBOL)
        cls.pdb = pdb_section_contributions(cls.context.directory / "th16.pdb")
        cls.statics = map_statics(cls.context.directory / "th16.map")
        cls.proof = review_sound_data(cls.context, cls.row, cls.candidate)
        with tempfile.TemporaryDirectory(dir=ROOT / ".analysis") as directory:
            output = Path(directory) / "focused.json"
            run = subprocess.run([sys.executable, str(ROOT / "scripts/audit-reference.py"),
                                  "--address", "0x45e150", "--address", "0x45e1f0", "--json", str(output)],
                                 cwd=ROOT, capture_output=True, text=True, timeout=90)
            if run.returncode:
                raise RuntimeError(run.stderr)
            reports = json.loads(output.read_text())["functions"]
        cls.units = [dict(source=r["source"], symbol=r["symbol"], artifact_kind="linked-pe",
                         object="SoundManager.obj", candidate_address=r["candidate_address"],
                         target_address=r["target_address"], size=r["size"], compare_size=r["size"],
                         profile=cls.context.receipt["compiler_profile"], link_profile=cls.context.receipt["linker_profile"],
                         linkages=[{k:v for k,v in f.items() if k not in ("candidate_target", "encoded")}
                                   for f in r["linkages"]]) for r in reports]

    def review(self, context=None, row=None, pdb=None, statics=None):
        with patch("sound_data_identity.pdb_section_contributions", return_value=self.pdb if pdb is None else pdb), \
             patch("sound_data_identity.map_statics", return_value=self.statics if statics is None else statics):
            return review_sound_data(context or self.context, row or self.row, self.candidate)

    def mutate(self, side, address, payload=None):
        context = copy.copy(self.context)
        image = getattr(context, side)
        if payload is None:
            payload = bytes([image.read_address(address, 1)[0] ^ 1])
        setattr(context, side, Overlay(image, {address+i: value for i, value in enumerate(payload)}))
        return context

    def test_complete_aggregate_and_both_original_witnesses_pass(self):
        self.assertEqual(self.review(), self.proof)
        self.assertEqual((self.proof["size"], self.proof["table_size"]), (1656, 1560))
        self.assertEqual(self.proof["bound_symbols"], [SYMBOL])
        self.assertEqual(self.proof["primary_exact_credit"], 0)
        self.assertEqual([(r["size"], r["instructions"], r["stride"], r["field_offset"], r["read_size"])
                          for r in self.proof["witnesses"]], [(145, 43, 20, 10, 2), (168, 51, 20, 10, 2)])
        self.assertEqual(self.context.data_contributions[self.candidate], [1656])

    def test_profile_symbol_extent_address_and_witness_are_fixed(self):
        for key, value in [("kind", "literal"), ("symbol", "g_other"), ("size", "1560"), ("size", "1655"),
                           ("size", "1657"), ("target_address", "0x4a2a34"), ("candidate_library", "LIBCMT.lib"),
                           ("candidate_size", "1560"), ("witness_instruction", "0x45e15b"),
                           ("witness_mnemonic", "movsx")]:
            with self.subTest(key=key, value=value), self.assertRaises(RuntimeEvidenceError):
                self.review(row=dict(self.row, **{key: value}))

    def test_every_candidate_byte_including_both_anchor_arrays_is_compared(self):
        for offset in range(1656):
            with self.subTest(offset=offset), self.assertRaises(RuntimeEvidenceError):
                self.review(context=self.mutate("image", self.candidate + offset))

    def test_original_hash_covers_the_entire_aggregate(self):
        for offset in (0, 1559, 1560, 1607, 1608, 1655):
            with self.subTest(offset=offset), self.assertRaisesRegex(RuntimeEvidenceError, "hash"):
                self.review(context=self.mutate("target", 0x4a2a30 + offset))
        with self.assertRaisesRegex(RuntimeEvidenceError, "hash"):
            self.review(row=dict(self.row, target_sha256="0" * 64))

    def test_record_and_anchor_semantics_survive_hash_updates(self):
        for offset, payload in [(0, struct.pack("<i", 1)), (4, struct.pack("<i", 67)),
                                (8, struct.pack("<h", 1)), (10, struct.pack("<h", 101)),
                                (12, struct.pack("<i", 2)), (16, struct.pack("<i", 2)),
                                (1560, struct.pack("<f", -1.0)), (1652, struct.pack("<f", 1.0))]:
            context = self.mutate("target", 0x4a2a30 + offset, payload)
            row = dict(self.row, target_sha256=hashlib.sha256(context.target.read_address(0x4a2a30, 1656)).hexdigest())
            with self.subTest(offset=offset), self.assertRaises(RuntimeEvidenceError):
                self.review(context=context, row=row)

    def test_both_full_original_witnesses_are_required(self):
        for witness in self.proof["witnesses"]:
            for offset in (0, 8, witness["read"]-witness["parent"]-3,
                           witness["read"]-witness["parent"]+3, witness["size"]-1):
                with self.subTest(parent=witness["parent"], offset=offset), self.assertRaises(RuntimeEvidenceError):
                    self.review(context=self.mutate("target", witness["parent"]+offset))

    def test_original_witness_boundaries_cannot_be_shortened_or_overlapped(self):
        for witness in self.proof["witnesses"]:
            for mode in ("short", "span", "overlap"):
                context = copy.copy(self.context)
                context.boundaries = copy.deepcopy(context.boundaries)
                row = context.boundaries[witness["parent"]]
                if mode == "short":
                    row["size"] = str(witness["size"]-1)
                elif mode == "span":
                    row["span_end"] = hex(witness["parent"]+witness["size"])
                else:
                    context.boundaries[witness["parent"]+1] = dict(row, size="1", span_end=hex(witness["parent"]+1))
                with self.subTest(mode=mode), self.assertRaises(RuntimeEvidenceError):
                    self.review(context=context)

    def test_original_data_cannot_overlap_a_code_owner(self):
        context = copy.copy(self.context)
        context.boundaries = dict(context.boundaries, **{})
        context.boundaries[0x4a2a30] = dict(size="1", span_end="0x4a2a30")
        with self.assertRaises(RuntimeEvidenceError):
            self.review(context=context)

    def test_complete_same_start_pdb_owner_and_source_module_are_required(self):
        for mode in ("short", "table-only", "long", "duplicate", "missing", "producer", "module", "permissions", "extra"):
            pdb = copy.deepcopy(self.pdb)
            row = next(r for r in pdb["contributions"] if r == self.proof["owner"])
            if mode == "short": row["size"] -= 1
            elif mode == "table-only": row["size"] = 1560
            elif mode == "long": row["size"] += 1
            elif mode == "duplicate": pdb["contributions"].append(copy.deepcopy(row))
            elif mode == "missing": pdb["contributions"].remove(row)
            elif mode == "producer": row["object"] = str(ROOT / "other.obj")
            elif mode == "module": row["module_index"] += 1
            elif mode == "permissions": row["characteristics"] |= 0x20
            else: pdb["contributions"].append(dict(row, section_offset=row["section_offset"]+1656, size=4))
            with self.subTest(mode=mode), self.assertRaises(RuntimeEvidenceError):
                self.review(pdb=pdb)

    def test_crossing_contribution_from_another_module_is_rejected(self):
        pdb = copy.deepcopy(self.pdb)
        owner = self.proof["owner"]
        pdb["contributions"].append(dict(owner, section_offset=owner["section_offset"]-1, size=2, module_index=1))
        with self.assertRaisesRegex(RuntimeEvidenceError, "overlaps"):
            self.review(pdb=pdb)

    def test_all_three_typed_objects_are_complete_and_unique(self):
        for name, offset, size in self.proof["names"].values():
            for mode in ("missing", "duplicate", "size", "address"):
                context = copy.copy(self.context)
                context.typed_globals = copy.deepcopy(context.typed_globals)
                row = next(g for g in context.typed_globals if g["name"] == name)
                if mode == "missing": context.typed_globals.remove(row)
                elif mode == "duplicate": context.typed_globals.append(copy.deepcopy(row))
                elif mode == "size": row["size"] -= 1
                else: row["address"] += 4
                with self.subTest(name=name, mode=mode), self.assertRaises(RuntimeEvidenceError):
                    self.review(context=context)

    def test_public_names_cannot_be_missing_duplicated_or_replaced_by_private_names(self):
        for name in self.proof["names"]:
            for mode in ("missing", "duplicate", "alias", "private", "producer", "address", "role"):
                context = copy.copy(self.context)
                context.publics = copy.deepcopy(context.publics)
                row = next(p for p in context.publics if p["symbol"] == name)
                statics = list(self.statics)
                if mode == "missing": context.publics.remove(row)
                elif mode == "duplicate": context.publics.append(copy.deepcopy(row))
                elif mode == "alias": context.publics.append(dict(row, symbol="unreviewed_alias"))
                elif mode == "private": context.publics.remove(row); statics.append(row)
                elif mode == "producer": row["object"] = "Other.obj"
                elif mode == "address": row["address"] += 4
                else: row["flags"] = ["f"]
                with self.subTest(name=name, mode=mode), self.assertRaises(RuntimeEvidenceError):
                    self.review(context=context, statics=statics)

    def test_raw_storage_permissions_and_complete_end_are_required(self):
        for side, address in (("image", self.candidate), ("target", 0x4a2a30)):
            for mode in ("readonly", "code", "short"):
                context = copy.copy(self.context)
                image = Overlay(getattr(context, side))
                image.sections = list(image.sections)
                at = next(i for i, s in enumerate(image.sections) if image.image_base+s.rva <= address < image.image_base+s.rva+s.raw_size)
                s = image.sections[at]
                if mode == "readonly": s = replace(s, characteristics=s.characteristics & ~0x80000000)
                elif mode == "code": s = replace(s, characteristics=s.characteristics | 0x20)
                else: s = replace(s, raw_size=address-image.image_base-s.rva+1655)
                image.sections[at] = s
                setattr(context, side, image)
                with self.subTest(side=side, mode=mode), self.assertRaises(RuntimeEvidenceError):
                    self.review(context=context)

    def test_relocations_anywhere_including_crossing_boundaries_are_rejected(self):
        for side, base in (("image", self.candidate), ("target", 0x4a2a30)):
            for offset in (-3, 0, 10, 1559, 1560, 1608, 1655):
                context = copy.copy(self.context)
                setattr(context, side, Overlay(getattr(context, side), add=[base+offset]))
                with self.subTest(side=side, offset=offset), self.assertRaises(RuntimeEvidenceError):
                    self.review(context=context)

    def test_anchor_addresses_and_other_field_types_cannot_use_the_sound_binding(self):
        binding = self.context.reviewed_linkages[SYMBOL]
        field = dict(type="DIR32", width=4, target=binding["target"], addend=10,
                     storage_name="g_sound_effect_table", storage_size=1560)
        validate_sound_field(field, binding)
        for key, value in (("type", "REL32"), ("width", 8), ("local", True), ("pointer_limit", True),
                           ("addend", -1), ("addend", 1560), ("addend", 1608), ("storage_size", 1656),
                           ("storage_name", "g_anchor_corners_x"), ("target", binding["target"]+4)):
            with self.subTest(key=key), self.assertRaises(RuntimeEvidenceError):
                validate_sound_field(dict(field, **{key: value}), binding)

    def test_both_complete_primary_owners_and_field_restrictions_pass(self):
        self.assertEqual([u["size"] for u in self.units], [145, 168])
        for unit in self.units:
            result = self.context.compare(unit)
            self.assertEqual((result["result"], result["compared_size"]), ("exact", unit["size"]))
            for change in (dict(type="REL32"), dict(addend=1560), dict(local=True), dict(storage_size=1656)):
                changed = copy.deepcopy(unit)
                field = next(f for f in changed["linkages"] if f.get("symbol") == SYMBOL)
                field.update(change)
                with self.subTest(change=change), self.assertRaises(Incomplete):
                    self.context.compare(changed)

    def test_body_mutation_keeps_data_identity_but_fails_complete_primary_replay(self):
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        decoder.detail = True
        for unit in self.units:
            instructions = decoder.disasm(self.context.image.read_address(unit["candidate_address"], unit["size"]),
                                          unit["candidate_address"])
            instruction = next(i for i in instructions if i.mnemonic == "cmp" and any(
                o.type == capstone.x86.X86_OP_IMM and o.imm == 60 for o in i.operands))
            context = self.mutate("image", instruction.address + instruction.size - 1)
            self.assertEqual(self.review(context=context), self.proof)
            self.assertEqual(context.compare(unit)["result"], "mismatch")

    def test_verifier_is_fingerprinted(self):
        name = "scripts/sound_data_identity.py"
        self.assertEqual(self.context.before[name], hashlib.sha256((ROOT/name).read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
