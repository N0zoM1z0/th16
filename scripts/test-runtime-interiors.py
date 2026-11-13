#!/usr/bin/env python3
"""Reject incomplete runtime owners, fields, data and interior aliases."""
import copy
import csv
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import capstone

from linked_image import pdb_section_contributions
from runtime_identity import RuntimeEvidenceError, review_runtime_interiors, validate_runtime_field
from strict_oracle import Context, Incomplete, ROOT, reviewed_linkages


class ImagePatch:
    def __init__(self, image, address=None, relocations=None):
        self.image, self.address, self.relocations = image, address, relocations

    def __getattr__(self, name):
        return getattr(self.image, name)

    def read_address(self, address, size):
        data = bytearray(self.image.read_address(address, size))
        if self.address is not None and address <= self.address < address + size:
            data[self.address - address] ^= 1
        return bytes(data)

    def base_relocations(self):
        return self.image.base_relocations() if self.relocations is None else self.relocations


class RuntimeInteriorControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        cls.path = ROOT / "config/runtime-interiors.toml"
        cls.text = cls.path.read_text()
        cls.bindings, cls.evidence = review_runtime_interiors(cls.context, cls.path)

    def review(self, text=None, context=None):
        with tempfile.TemporaryDirectory(dir=ROOT / ".analysis") as directory:
            path = Path(directory) / "runtime.toml"
            path.write_text(self.text if text is None else text)
            return review_runtime_interiors(context or self.context, path)

    def test_both_complete_contributions_and_entries_pass(self):
        self.assertEqual(set(self.bindings), {"__dtoul3", "__ltod3", "__CIfmod", "__CIatan2"})
        self.assertEqual(self.bindings["__dtoul3"]["target"], 0x487910)
        self.assertEqual(self.bindings["__ltod3"]["target"], 0x487a70)
        self.assertTrue(self.evidence["complete_code_equal"])
        self.assertTrue(self.evidence["complete_data_equal"])
        self.assertEqual(len(self.evidence["fields"]), 24)
        self.assertEqual(len(self.evidence["candidate_relocations"]), 23)
        self.assertEqual(self.evidence["primary_exact_credit"], 0)
        self.assertNotIn("size", self.bindings["__dtoul3"])

    def test_unreviewed_profile_is_rejected(self):
        with self.assertRaises(RuntimeEvidenceError):
            self.review(self.text.replace("msvc-x86-ftol3-v1", "unreviewed"))

    def test_shortened_code_or_data_extents_are_rejected(self):
        for old, new in (("code_size = 887", "code_size = 886"), ("data_size = 130", "data_size = 129")):
            with self.subTest(old=old), self.assertRaises(RuntimeEvidenceError):
                self.review(self.text.replace(old, new))

    def test_original_code_hash_is_required(self):
        changed = self.text.replace('code_sha256 = "', 'code_sha256 = "0')
        with self.assertRaisesRegex(RuntimeEvidenceError, "code hash"):
            self.review(changed)

    def test_original_data_hash_and_address_are_required(self):
        for changed in (self.text.replace('data_sha256 = "', 'data_sha256 = "0'),
                        self.text.replace("0x004948b0", "0x004948b8")):
            with self.assertRaises(RuntimeEvidenceError):
                self.review(changed)

    def test_interior_offsets_are_fixed(self):
        for old, new in (("offset = 496", "offset = 497"), ("offset = 848", "offset = 849")):
            with self.subTest(old=old), self.assertRaises(RuntimeEvidenceError):
                self.review(self.text.replace(old, new))

    def test_call_witness_parent_hash_is_required(self):
        with self.assertRaisesRegex(RuntimeEvidenceError, "parent hash"):
            self.review(self.text.replace('witness_parent_sha256 = "', 'witness_parent_sha256 = "0', 1))

    def test_call_witness_must_be_an_owned_direct_call(self):
        for changed in (self.text.replace("0x0042dc0a", "0x0042dc0b"),
                        self.text.replace("0x0045b190", "0x0045b130")):
            with self.assertRaises(RuntimeEvidenceError):
                self.review(changed)

    def test_candidate_producer_is_pinned(self):
        for field, value in (("pdb_object", "other.lib"), ("map_object", "LIBCMT:other.obj")):
            context = copy.copy(self.context)
            context.linked = copy.deepcopy(context.linked)
            next(f for f in context.linked["functions"] if f["symbol"] == "__ftoui3")[field] = value
            with self.subTest(field=field), self.assertRaises(RuntimeEvidenceError):
                self.review(context=context)

    def test_one_complete_candidate_owner_is_required(self):
        for mode in ("missing", "duplicate", "short"):
            context = copy.copy(self.context)
            context.linked = copy.deepcopy(context.linked)
            functions = context.linked["functions"]
            owner = next(f for f in functions if f["symbol"] == "__ftoui3")
            if mode == "missing":
                functions.remove(owner)
            elif mode == "duplicate":
                functions.append(copy.deepcopy(owner))
            else:
                owner["size"] -= 1
            with self.subTest(mode=mode), self.assertRaises(RuntimeEvidenceError):
                self.review(context=context)

    def test_full_candidate_code_including_owned_alignment_is_compared(self):
        base = self.bindings["__dtoul3"]["parent_candidate"]
        for offset in (1, 0x30f):
            context = copy.copy(self.context)
            context.image = ImagePatch(context.image, base + offset)
            with self.subTest(offset=offset), self.assertRaises(RuntimeEvidenceError):
                self.review(context=context)

    def test_entire_candidate_data_contribution_is_compared(self):
        for offset in (0, 129):
            context = copy.copy(self.context)
            context.image = ImagePatch(context.image, self.evidence["data_address"] + offset)
            with self.subTest(offset=offset), self.assertRaises(RuntimeEvidenceError):
                self.review(context=context)

    def test_both_pdb_contributions_must_be_complete_and_unique(self):
        for mode in ("short", "duplicate", "producer"):
            pdb = copy.deepcopy(pdb_section_contributions(self.context.directory / "th16.pdb"))
            records = pdb["contributions"]
            data = next(c for c in records if c == self.evidence["data_contribution"])
            if mode == "short":
                data["size"] -= 1
            elif mode == "duplicate":
                records.append(copy.deepcopy(data))
            else:
                data["object"] = "other.lib"
            with self.subTest(mode=mode), patch("runtime_identity.pdb_section_contributions", return_value=pdb):
                with self.assertRaises(RuntimeEvidenceError):
                    self.review()

    def test_missing_or_extra_candidate_relocations_are_rejected(self):
        base = self.bindings["__dtoul3"]["parent_candidate"]
        for remove in (True, False):
            relocations = set(self.context.image.base_relocations())
            if remove:
                relocations.remove(base + 9)
            else:
                relocations.add(base + 1)
            context = copy.copy(self.context)
            context.image = ImagePatch(context.image, relocations=relocations)
            with self.subTest(remove=remove), self.assertRaises(ValueError):
                self.review(context=context)

    def test_exception_dependency_requires_its_complete_runtime_identity(self):
        for mode in ("missing", "short", "kind"):
            context = copy.copy(self.context)
            context.reviewed_linkages = copy.deepcopy(context.reviewed_linkages)
            if mode == "missing":
                del context.reviewed_linkages["__except1"]
            elif mode == "short":
                context.reviewed_linkages["__except1"]["size"] = 205
            else:
                context.reviewed_linkages["__except1"]["kind"] = "unreviewed"
            with self.subTest(mode=mode), self.assertRaises(RuntimeEvidenceError):
                self.review(context=context)

    def test_original_code_relocation_absence_is_checked(self):
        context = copy.copy(self.context)
        relocations = set(context.target.base_relocations())
        relocations.add(self.evidence["target_address"] + 9)
        context.target = ImagePatch(context.target, relocations=relocations)
        with self.assertRaises(ValueError):
            self.review(context=context)

    def test_neither_constant_contribution_may_contain_relocations(self):
        for which, address in (("target", self.evidence["data_target"]),
                               ("image", self.evidence["data_address"])):
            context = copy.copy(self.context)
            image = getattr(context, which)
            relocations = set(image.base_relocations()) | {address + 4}
            setattr(context, which, ImagePatch(image, relocations=relocations))
            with self.subTest(which=which), self.assertRaises(RuntimeEvidenceError):
                self.review(context=context)

    def test_unreviewed_interior_alias_is_rejected(self):
        with self.assertRaises(RuntimeEvidenceError):
            self.review(self.text.replace('symbol = "__dtoul3"', 'symbol = "__dtoui3"'))

    def call_fixture(self):
        function = next(f for f in self.context.linked["functions"]
                        if f["symbol"] == "?update_play_time@GameThread@@SAXXZ")
        base = int(function["address"], 0)
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        decoder.detail = True
        reviewed = self.bindings["__dtoul3"]
        call = next(i for i in decoder.disasm(self.context.image.read_address(base, function["size"]), base)
                    if i.mnemonic == "call" and i.operands[0].type == capstone.x86.X86_OP_IMM
                    and i.operands[0].imm == reviewed["candidate"])
        field = dict(type="REL32", width=4, offset=call.address-base+1, target=reviewed["target"], addend=0)
        return function, field, reviewed

    def test_only_exact_rel32_calls_can_use_interior_bindings(self):
        function, field, reviewed = self.call_fixture()
        validate_runtime_field(self.context, function, field, reviewed)
        for key, value in (("type", "DIR32"), ("width", 8), ("addend", 1), ("local", True),
                           ("target", reviewed["target"] + 1), ("offset", 1)):
            changed = dict(field, **{key: value})
            with self.subTest(key=key), self.assertRaises(RuntimeEvidenceError):
                validate_runtime_field(self.context, function, changed, reviewed)

    def test_tail_jump_cannot_use_a_call_identity(self):
        function, field, reviewed = self.call_fixture()
        context = copy.copy(self.context)
        context.image = ImagePatch(context.image, int(function["address"], 0) + field["offset"] - 1)
        with self.assertRaises(RuntimeEvidenceError):
            validate_runtime_field(context, function, field, reviewed)

    def test_runtime_manifest_and_verifier_are_fingerprinted(self):
        identity = self.context.identity()
        self.assertIn("config/runtime-interiors.toml", identity)
        self.assertIn("scripts/runtime_identity.py", identity)

    def test_ordinary_runtime_binding_does_not_admit_an_interior_public(self):
        with (ROOT / "config/linkage-bindings.csv").open() as stream:
            rows = list(csv.DictReader(stream))
        extra = dict.fromkeys(rows[0], "")
        extra.update(symbol="__dtoul3", target_address="0x487910", size="286", kind="runtime-function",
                     target_sha256=hashlib.sha256(self.context.target.read_address(0x487910, 286)).hexdigest(),
                     evidence="docs/knowledge/conversion-runtime.md", candidate_library="LIBCMT.lib", candidate_size="887")
        with tempfile.TemporaryDirectory(dir=ROOT / ".analysis") as directory:
            path = Path(directory) / "bindings.csv"
            with path.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=rows[0])
                writer.writeheader()
                writer.writerows(rows + [extra])
            with self.assertRaisesRegex(Incomplete, "complete function extents"):
                reviewed_linkages(self.context, path)


if __name__ == "__main__":
    unittest.main()
