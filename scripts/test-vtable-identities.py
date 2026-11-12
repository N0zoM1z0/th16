#!/usr/bin/env python3
"""Reject malformed primary-vftable identities using real pinned artifact views."""
import copy
import csv
from dataclasses import replace
import hashlib
from pathlib import Path
import struct
import tempfile
import tomllib
import unittest
from unittest import mock

import strict_oracle
from strict_oracle import Context, Incomplete, ROOT, reviewed_linkages

THREAD = "??_7ThreadInf@@6B@"
FILE = "??_7File@Pbg@@6B@"
ECL_TABLES = ("??_7EclResourceInf@@6B@", "??_7SptResourceInf@@6B@", "??_7SptInf@@6B@", "??_7EnemyInf@@6B@")
SOUND_TABLES = ("??_7CSound@@6B@", "??_7CStreamingSound@@6B@")


class Overlay:
    def __init__(self, original, changes):
        self.original, self.changes = original, changes

    def __getattr__(self, name):
        return getattr(self.original, name)

    def read_address(self, start, size):
        data = bytearray(self.original.read_address(start, size))
        for address, replacement in self.changes.items():
            for offset, byte in enumerate(replacement):
                if start <= address + offset < start + size:
                    data[address + offset - start] = byte
        return bytes(data)


class VftableControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        with (ROOT / "config/linkage-bindings.csv").open() as stream:
            cls.rows = list(csv.DictReader(stream))

    def row(self, rows, symbol=THREAD):
        return next(r for r in rows if r["symbol"] == symbol)

    def candidate(self, symbol=THREAD):
        return next(p["address"] for p in self.context.publics if p["symbol"] == symbol)

    def words(self, image, address, count):
        return struct.unpack("<" + "I" * count, image.read_address(address, count * 4))

    def locator(self, image, table):
        return self.words(image, table - 4, 1)[0]

    def check(self, rows=None, context=None):
        rows = rows or self.rows
        with tempfile.TemporaryDirectory(dir=ROOT / ".analysis") as directory:
            path = Path(directory) / "bindings.csv"
            with path.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=rows[0])
                writer.writeheader()
                writer.writerows(rows)
            return reviewed_linkages(context or self.context, path)

    def target_change(self, address, data):
        context = copy.copy(self.context)
        context.target = Overlay(context.target, {address: data})
        return context

    def test_real_reviewed_slot_witnesses_pass(self):
        result = self.check()
        for symbol, size in [(THREAD, 4), (FILE, 36), *zip(ECL_TABLES, (12, 8, 24, 24)),
                             *zip(SOUND_TABLES, (4, 4))]:
            with self.subTest(symbol=symbol):
                self.assertEqual(result[symbol]["size"], size)

    def test_sound_tables_require_complete_unambiguous_storage(self):
        for symbol in SOUND_TABLES:
            for sizes in ([4], [8, 8], [12]):
                context = copy.copy(self.context)
                context.data_contributions = copy.deepcopy(self.context.data_contributions)
                context.data_contributions[self.candidate(symbol) - 4] = sizes
                with self.subTest(symbol=symbol, sizes=sizes), self.assertRaisesRegex(Incomplete, "complete PDB storage"):
                    self.check(context=context)

    def test_sound_class_identity_cannot_be_borrowed_from_its_peer(self):
        for symbol, peer in zip(SOUND_TABLES, reversed(SOUND_TABLES)):
            rows = copy.deepcopy(self.rows)
            row, other = self.row(rows, symbol), self.row(rows, peer)
            row["target_address"], row["target_sha256"] = other["target_address"], other["target_sha256"]
            with self.subTest(symbol=symbol), self.assertRaisesRegex(Incomplete, "RTTI class differs"):
                self.check(rows)

    def test_sound_slots_require_complete_independently_identified_entries(self):
        for symbol in SOUND_TABLES:
            rows = copy.deepcopy(self.rows)
            row = self.row(rows, symbol)
            table = int(row["target_address"], 0)
            slot = self.words(self.context.target, table, 1)[0]
            context = self.target_change(table, struct.pack("<I", slot + 1))
            row["target_sha256"] = hashlib.sha256(context.target.read_address(table, 4)).hexdigest()
            with self.subTest(symbol=symbol), self.assertRaisesRegex(Incomplete, "slot lacks"):
                self.check(rows, context)
            candidate_slot = self.words(self.context.image, self.candidate(symbol), 1)[0]
            for key, value in (("extent_source", "next-map-label"), ("size", 0)):
                context = copy.copy(self.context)
                context.linked = copy.deepcopy(self.context.linked)
                for function in context.linked["functions"]:
                    if int(function["address"], 0) == candidate_slot:
                        function[key] = value
                with self.subTest(symbol=symbol, key=key), self.assertRaisesRegex(Incomplete, "slot lacks"):
                    self.check(context=context)

    def test_complete_laser_constructor_with_26_slots_replays(self):
        units = tomllib.loads((ROOT / "config/match-units.toml").read_text())["units"]
        result = self.context.compare(units["reference-00430fc0"])
        self.assertEqual((result["result"], result["compared_size"], result["matched_bytes"]), ("exact", 138, 138))

    def test_pdb_table_cannot_be_truncated(self):
        for symbol in (FILE, *ECL_TABLES):
            context = copy.copy(self.context)
            context.data_contributions = copy.deepcopy(context.data_contributions)
            context.data_contributions[self.candidate(symbol) - 4] = [int(self.row(self.rows, symbol)["size"])]
            with self.subTest(symbol=symbol), self.assertRaisesRegex(Incomplete, "complete PDB storage"):
                self.check(context=context)

    def test_pdb_table_cannot_have_ambiguous_owners(self):
        context = copy.copy(self.context)
        context.data_contributions = copy.deepcopy(context.data_contributions)
        context.data_contributions[self.candidate() - 4] = [8, 8]
        with self.assertRaisesRegex(Incomplete, "complete PDB storage"):
            self.check(context=context)

    def test_original_table_cannot_be_truncated_even_with_forged_candidate_size(self):
        for symbol in (FILE, *ECL_TABLES):
            rows = copy.deepcopy(self.rows)
            row = self.row(rows, symbol)
            size = 4 if symbol == FILE else int(row["size"]) - 4
            row["size"] = str(size)
            address = int(row["target_address"], 0)
            row["target_sha256"] = hashlib.sha256(self.context.target.read_address(address, size)).hexdigest()
            context = copy.copy(self.context)
            context.data_contributions = copy.deepcopy(context.data_contributions)
            context.data_contributions[self.candidate(symbol) - 4] = [size + 4]
            with self.subTest(symbol=symbol), self.assertRaisesRegex(Incomplete, "slot extent is truncated"):
                self.check(rows, context)

    def test_original_class_name_is_required(self):
        table = int(self.row(self.rows)["target_address"], 0)
        locator = self.locator(self.context.target, table)
        descriptor = self.words(self.context.target, locator, 5)[3]
        context = self.target_change(descriptor + 8, b"X")
        with self.assertRaisesRegex(Incomplete, "class-name encoding|RTTI class differs"):
            self.check(context=context)

    def test_namespace_is_part_of_identity(self):
        table = int(self.row(self.rows, FILE)["target_address"], 0)
        locator = self.locator(self.context.target, table)
        descriptor = self.words(self.context.target, locator, 5)[3]
        name = self.context.target.read_address(descriptor + 8, 14)
        context = self.target_change(descriptor + 8, name.replace(b"Pbg", b"Xbg"))
        with self.assertRaisesRegex(Incomplete, "RTTI class differs"):
            self.check(context=context)

    def test_secondary_locator_is_unsupported(self):
        table = int(self.row(self.rows)["target_address"], 0)
        context = self.target_change(self.locator(self.context.target, table) + 4, struct.pack("<I", 4))
        with self.assertRaisesRegex(Incomplete, "non-primary"):
            self.check(context=context)

    def test_construction_locator_is_unsupported(self):
        table = int(self.row(self.rows)["target_address"], 0)
        context = self.target_change(self.locator(self.context.target, table) + 8, struct.pack("<I", 4))
        with self.assertRaisesRegex(Incomplete, "construction"):
            self.check(context=context)

    def test_candidate_type_name_requires_complete_pdb_storage(self):
        locator = self.locator(self.context.image, self.candidate(FILE))
        descriptor = self.words(self.context.image, locator, 5)[3]
        context = copy.copy(self.context)
        context.data_contributions = copy.deepcopy(context.data_contributions)
        context.data_contributions[descriptor] = [22]
        with self.assertRaisesRegex(Incomplete, "complete PDB storage"):
            self.check(context=context)

    def test_complete_base_array_includes_trailing_byte(self):
        locator = self.locator(self.context.image, self.candidate(FILE))
        hierarchy = self.words(self.context.image, locator, 5)[4]
        array = self.words(self.context.image, hierarchy, 4)[3]
        context = copy.copy(self.context)
        context.data_contributions = copy.deepcopy(context.data_contributions)
        context.data_contributions[array] = [8]
        with self.assertRaisesRegex(Incomplete, "complete PDB storage"):
            self.check(context=context)

    def test_base_array_trailing_byte_cannot_be_ignored(self):
        table = int(self.row(self.rows, FILE)["target_address"], 0)
        locator = self.locator(self.context.target, table)
        hierarchy = self.words(self.context.target, locator, 5)[4]
        array = self.words(self.context.target, hierarchy, 4)[3]
        context = self.target_change(array + 8, b"\x01")
        with self.assertRaisesRegex(Incomplete, "trailing byte"):
            self.check(context=context)

    def test_wrong_target_slot_is_rejected_even_with_updated_hash(self):
        rows = copy.deepcopy(self.rows)
        row = self.row(rows)
        table = int(row["target_address"], 0)
        slot = self.words(self.context.target, table, 1)[0]
        context = self.target_change(table, struct.pack("<I", slot + 1))
        row["target_sha256"] = hashlib.sha256(context.target.read_address(table, 4)).hexdigest()
        with self.assertRaisesRegex(Incomplete, "slot lacks"):
            self.check(rows, context)

    def test_wrong_candidate_slot_is_rejected(self):
        for symbol in (FILE, *ECL_TABLES):
            table = self.candidate(symbol)
            wrong = self.words(self.context.image, table + 4, 1)[0]
            context = copy.copy(self.context)
            context.image = Overlay(context.image, {table: struct.pack("<I", wrong)})
            with self.subTest(symbol=symbol), self.assertRaisesRegex(Incomplete, "slot lacks"):
                self.check(context=context)

    def test_each_table_pointer_requires_a_relocation(self):
        for symbol in (THREAD, *ECL_TABLES):
            table = self.candidate(symbol)
            size = int(self.row(self.rows, symbol)["size"])
            for offset in range(-4, size, 4):
                context = copy.copy(self.context)
                context.image = Overlay(context.image, {})
                context.image.base_relocations = lambda removed=table + offset: [
                    a for a in self.context.image.base_relocations() if a != removed]
                with self.subTest(symbol=symbol, offset=offset), self.assertRaisesRegex(Incomplete, "complete relocated"):
                    self.check(context=context)

    def test_writable_vftable_storage_is_rejected(self):
        context = copy.copy(self.context)
        context.image = copy.copy(context.image)
        context.image.sections = [replace(s, characteristics=s.characteristics | 0x80000000)
                                  if s.name == ".rdata" else s for s in context.image.sections]
        with self.assertRaisesRegex(Incomplete, "read-only data"):
            self.check(rows=[self.row(self.rows)], context=context)

    def test_multiple_inheritance_is_explicitly_unsupported(self):
        table = int(self.row(self.rows)["target_address"], 0)
        locator = self.locator(self.context.target, table)
        hierarchy = self.words(self.context.target, locator, 5)[4]
        context = self.target_change(hierarchy + 4, struct.pack("<I", 1))
        with self.assertRaisesRegex(Incomplete, "unsupported multiple"):
            self.check(context=context)

    def test_wrong_base_attributes_are_rejected(self):
        table = int(self.row(self.rows)["target_address"], 0)
        locator = self.locator(self.context.target, table)
        hierarchy = self.words(self.context.target, locator, 5)[4]
        array = self.words(self.context.target, hierarchy, 4)[3]
        descriptor = self.words(self.context.target, array, 1)[0]
        context = self.target_change(descriptor + 20, struct.pack("<I", 0))
        with self.assertRaisesRegex(Incomplete, "base displacement or attributes"):
            self.check(context=context)

    def test_conflicting_callee_owners_are_rejected(self):
        slot = self.words(self.context.image, self.candidate(), 1)[0]
        context = copy.copy(self.context)
        context.linked = copy.deepcopy(context.linked)
        function = next(f for f in context.linked["functions"] if int(f["address"], 0) == slot)
        extra = dict(function, pdb_object="different.obj")
        context.linked["functions"].append(extra)
        with self.assertRaisesRegex(Incomplete, "slot lacks"):
            self.check(context=context)

    def test_cyclic_self_inheritance_is_rejected(self):
        table = int(self.row(self.rows, FILE)["target_address"], 0)
        locator = self.locator(self.context.target, table)
        own_type, hierarchy = self.words(self.context.target, locator, 5)[3:]
        array = self.words(self.context.target, hierarchy, 4)[3]
        base = self.words(self.context.target, array + 4, 1)[0]
        context = self.target_change(base, struct.pack("<I", own_type))
        with self.assertRaisesRegex(Incomplete, "cyclic RTTI"):
            self.check(context=context)

    def test_base_class_name_is_part_of_identity(self):
        table = int(self.row(self.rows, FILE)["target_address"], 0)
        locator = self.locator(self.context.target, table)
        hierarchy = self.words(self.context.target, locator, 5)[4]
        array = self.words(self.context.target, hierarchy, 4)[3]
        base = self.words(self.context.target, array + 4, 1)[0]
        descriptor = self.words(self.context.target, base, 1)[0]
        name = self.context.target.read_address(descriptor + 8, 15)
        context = self.target_change(descriptor + 8, name.replace(b"IFile", b"JFile"))
        with self.assertRaisesRegex(Incomplete, "hierarchies differ"):
            self.check(context=context)

    def thread_unit(self):
        return tomllib.loads((ROOT / "config/match-units.toml").read_text())["units"]["reference-00402f20"]

    def test_complete_thread_destructor_replays(self):
        result = self.context.compare(self.thread_unit())
        self.assertEqual((result["result"], result["compared_size"], result["matched_bytes"]), ("exact", 11, 11))

    def test_consumer_cannot_select_another_reviewed_table(self):
        unit = self.thread_unit()
        field = next(f for f in unit["linkages"] if f.get("symbol") == THREAD)
        field["target"] = int(self.row(self.rows, FILE)["target_address"], 0)
        with self.assertRaisesRegex(Incomplete, "reviewed fixed destination"):
            self.context.compare(unit)

    def test_consumer_cannot_use_an_interior_address(self):
        unit = self.thread_unit()
        next(f for f in unit["linkages"] if f.get("symbol") == THREAD)["addend"] = 4
        with self.assertRaisesRegex(Incomplete, "exact DIR32 address point"):
            self.context.compare(unit)

    def test_consumer_cannot_call_the_data_address(self):
        unit = self.thread_unit()
        next(f for f in unit["linkages"] if f.get("symbol") == THREAD)["type"] = "REL32"
        with self.assertRaisesRegex(Incomplete, "exact DIR32 address point"):
            self.context.compare(unit)

    def test_locator_requires_its_complete_pdb_storage(self):
        locator = self.locator(self.context.image, self.candidate())
        context = copy.copy(self.context)
        context.data_contributions = copy.deepcopy(context.data_contributions)
        context.data_contributions[locator] = [19]
        with self.assertRaisesRegex(Incomplete, "complete PDB storage"):
            self.check(context=context)

    def test_slot_identity_is_not_inferred_without_the_fixed_functions(self):
        original = Path.read_text
        def read_text(path, *args, **kwargs):
            return "" if path.name == "functions.txt" else original(path, *args, **kwargs)
        with mock.patch.object(Path, "read_text", read_text):
            with self.assertRaisesRegex(Incomplete, "slot lacks"):
                self.check()

    def test_unreadable_table_storage_is_rejected(self):
        context = copy.copy(self.context)
        context.image = copy.copy(context.image)
        context.image.sections = [replace(s, characteristics=s.characteristics & ~0x40000000)
                                  if s.name == ".rdata" else s for s in context.image.sections]
        with self.assertRaisesRegex(Incomplete, "read-only data"):
            self.check(rows=[self.row(self.rows)], context=context)

    def test_zero_length_callee_extent_is_rejected(self):
        slot = self.words(self.context.image, self.candidate(), 1)[0]
        context = copy.copy(self.context)
        context.linked = copy.deepcopy(context.linked)
        for function in context.linked["functions"]:
            if int(function["address"], 0) == slot:
                function["size"] = 0
        with self.assertRaisesRegex(Incomplete, "slot lacks"):
            self.check(context=context)

    def test_proof_module_is_part_of_oracle_identity(self):
        path = ROOT / "scripts/vtable_identity.py"
        self.assertIn("scripts/vtable_identity.py", self.context.before)
        original = strict_oracle.digest
        with mock.patch.object(strict_oracle, "digest", side_effect=lambda p: "0" * 64 if Path(p) == path else original(p)):
            with self.assertRaisesRegex(ValueError, "Oracle inputs changed"):
                self.context.finish()


if __name__ == "__main__":
    unittest.main()
