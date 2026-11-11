#!/usr/bin/env python3
"""Mutate fixed linkage evidence without changing the private target or artifacts."""
import copy
import csv
import hashlib
from pathlib import Path
import tempfile
import unittest

from strict_oracle import Context, Incomplete, ROOT, reviewed_linkages, replay_owner


class ReviewedLinkageControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        with (ROOT / "config/linkage-bindings.csv").open() as stream:
            cls.rows = list(csv.DictReader(stream))

    def check_rows(self, rows):
        with tempfile.TemporaryDirectory(dir=ROOT / ".analysis") as directory:
            path = Path(directory) / "bindings.csv"
            with path.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=rows[0])
                writer.writeheader()
                writer.writerows(rows)
            return reviewed_linkages(self.context, path)

    def test_fixed_bindings_pass(self):
        result = self.check_rows(self.rows)
        self.assertEqual(len(result), len(self.rows))
        self.assertEqual(result["@__security_check_cookie@4"]["target"], 0x47499B)
        self.assertEqual(result["__real@3f800000"]["target"], 0x4944D8)

    def test_wrong_extent_hash_is_rejected(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["target_sha256"] = "0" * 64
        with self.assertRaisesRegex(Incomplete, "hash mismatch"):
            self.check_rows(rows)

    def test_wrong_literal_witness_is_rejected(self):
        rows = copy.deepcopy(self.rows)
        next(r for r in rows if r["kind"] == "literal")["witness_instruction"] = "0x00402CD0"
        with self.assertRaisesRegex(Incomplete, "instruction witness"):
            self.check_rows(rows)

    def test_screen_center_literal_requires_its_own_typed_read(self):
        for field, value in [("witness_instruction", "0x4079ce"),
                             ("witness_mnemonic", "movaps"), ("size", "8")]:
            with self.subTest(field=field):
                rows = copy.deepcopy(self.rows)
                next(r for r in rows if r["symbol"] == "__real@43700000")[field] = value
                with self.assertRaises(Incomplete):
                    self.check_rows(rows)

    def test_wrong_runtime_library_is_rejected(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["candidate_library"] = "unreviewed.lib"
        with self.assertRaisesRegex(Incomplete, "pinned Microsoft library"):
            self.check_rows(rows)

    def test_runtime_identity_requires_the_full_candidate_extent(self):
        for symbol, truncated_size in [("__libm_sse2_sqrt_precise", 254),
                                       ("__chkstk", 44), ("__beginthreadex", 132)]:
            with self.subTest(symbol=symbol):
                rows = copy.deepcopy(self.rows)
                next(r for r in rows if r["symbol"] == symbol)["candidate_size"] = str(truncated_size)
                with self.assertRaisesRegex(Incomplete, "complete function extents"):
                    self.check_rows(rows)

    def test_runtime_identity_requires_the_full_target_extent(self):
        for symbol in ["__libm_sse2_sqrt_precise", "__chkstk", "__beginthreadex"]:
            with self.subTest(symbol=symbol):
                rows = copy.deepcopy(self.rows)
                row = next(r for r in rows if r["symbol"] == symbol)
                size = int(row["size"]) - 1
                row["size"] = str(size)
                row["target_sha256"] = hashlib.sha256(
                    self.context.target.read_address(int(row["target_address"], 0), size)).hexdigest()
                with self.assertRaisesRegex(Incomplete, "complete function extents"):
                    self.check_rows(rows)

    def test_stack_probe_and_thread_entries_require_their_own_libraries(self):
        for symbol, wrong_library in [("__chkstk", "libucrt.lib"),
                                      ("__beginthreadex", "LIBCMT.lib")]:
            with self.subTest(symbol=symbol):
                rows = copy.deepcopy(self.rows)
                next(r for r in rows if r["symbol"] == symbol)["candidate_library"] = wrong_library
                with self.assertRaisesRegex(Incomplete, "pinned Microsoft library"):
                    self.check_rows(rows)

    def test_string_must_have_its_complete_pdb_extent(self):
        rows = copy.deepcopy(self.rows)
        row = next(r for r in rows if r["kind"] == "string-literal")
        row["size"] = "2"
        row["target_sha256"] = hashlib.sha256(b"%d").hexdigest()
        with self.assertRaisesRegex(Incomplete, "complete NUL-terminated PDB storage"):
            self.check_rows(rows)

    def test_string_requires_a_fixed_push_of_its_address(self):
        rows = copy.deepcopy(self.rows)
        next(r for r in rows if r["kind"] == "string-literal")["witness_instruction"] = "0x4082d6"
        with self.assertRaisesRegex(Incomplete, "instruction witness"):
            self.check_rows(rows)

    def test_string_rejects_ambiguous_pdb_storage(self):
        context = copy.copy(self.context)
        context.data_contributions = copy.deepcopy(context.data_contributions)
        symbol = next(r["symbol"] for r in self.rows if r["kind"] == "string-literal")
        address = next(p["address"] for p in context.publics if p["symbol"] == symbol)
        context.data_contributions[address] *= 2
        with self.assertRaisesRegex(Incomplete, "complete NUL-terminated PDB storage"):
            reviewed_linkages(context)

    def check_indexed_mutation(self, address, replacement):
        context = copy.copy(self.context)
        original = context.target

        class Overlay:
            def read_address(self, start, size):
                data = bytearray(original.read_address(start, size))
                for offset, byte in enumerate(replacement):
                    if start <= address + offset < start + size:
                        data[address + offset - start] = byte
                return bytes(data)

        context.target = Overlay()
        with self.assertRaisesRegex(Incomplete, "instruction witness"):
            reviewed_linkages(context)

    def test_table_shift_cannot_select_four_elements(self):
        self.check_indexed_mutation(0x402C86, b"\x1e")

    def test_table_shift_must_be_logical(self):
        self.check_indexed_mutation(0x402C85, b"\xf8")

    def test_table_shift_must_define_the_index_register(self):
        self.check_indexed_mutation(0x402C85, b"\xe9")

    def test_table_index_must_match_the_shifted_register(self):
        self.check_indexed_mutation(0x402C8B, b"\xcd")

    def test_table_stride_must_match_the_double_width(self):
        self.check_indexed_mutation(0x402C8B, b"\x85")

    def test_table_witness_cannot_start_inside_an_instruction(self):
        rows = copy.deepcopy(self.rows)
        next(r for r in rows if r["kind"] == "indexed-literal")["witness_instruction"] = "0x402c88"
        with self.assertRaisesRegex(Incomplete, "instruction witness"):
            self.check_rows(rows)

    def test_table_requires_its_full_sixteen_byte_payload(self):
        rows = copy.deepcopy(self.rows)
        row = next(r for r in rows if r["kind"] == "indexed-literal")
        row["size"] = "8"
        row["target_sha256"] = hashlib.sha256(bytes(8)).hexdigest()
        with self.assertRaisesRegex(Incomplete, "complete typed value"):
            self.check_rows(rows)

    def test_table_requires_a_unique_complete_pdb_extent(self):
        context = copy.copy(self.context)
        context.data_contributions = copy.deepcopy(context.data_contributions)
        symbol = next(r["symbol"] for r in self.rows if r["kind"] == "indexed-literal")
        address = next(p["address"] for p in context.publics if p["symbol"] == symbol)
        context.data_contributions[address] = [8]
        with self.assertRaisesRegex(Incomplete, "instruction witness"):
            reviewed_linkages(context)

    def test_ucrt_cannot_claim_vcruntime_ownership(self):
        rows = copy.deepcopy(self.rows)
        next(r for r in rows if r["symbol"] == "_malloc")["candidate_library"] = "LIBCMT.lib"
        with self.assertRaisesRegex(Incomplete, "pinned Microsoft library"):
            self.check_rows(rows)

    def test_wrong_allocator_parent_instruction_is_rejected(self):
        rows = copy.deepcopy(self.rows)
        next(r for r in rows if r["symbol"] == "_malloc")["witness_instruction"] = "0x4749b4"
        with self.assertRaisesRegex(Incomplete, "direct instruction witness"):
            self.check_rows(rows)

    def test_allocator_witness_must_start_an_instruction(self):
        rows = copy.deepcopy(self.rows)
        next(r for r in rows if r["symbol"] == "_malloc")["witness_instruction"] = "0x4749d4"
        with self.assertRaisesRegex(Incomplete, "direct instruction witness"):
            self.check_rows(rows)

    def test_allocator_witness_requires_its_reviewed_parent(self):
        rows = [r for r in copy.deepcopy(self.rows) if r["symbol"] != "??2@YAPAXI@Z"]
        with self.assertRaisesRegex(Incomplete, "unique reviewed parent"):
            self.check_rows(rows)

    def test_allocator_thunks_replay_complete_owners(self):
        context = self.context
        for symbol, address, size, offset, child, destination in [
            ("??3@YAXPAX@Z", 0x47514B, 5, 1, "_free", 0x477FB2),
            ("_free", 0x477FB2, 5, 1, "__free_base", 0x47BCB2),
            ("_malloc", 0x477FA7, 11, 7, "__malloc_base", 0x47BCEC),
        ]:
            with self.subTest(symbol=symbol):
                function = next(r for r in context.linked["functions"] if r["symbol"] == symbol)
                unit = dict(size=size, compare_size=size, target_address=address, linkages=[
                    dict(offset=offset, type="REL32", symbol=child, target=destination)])
                self.assertEqual(replay_owner(context.image, context.target, context.publics, function, unit)["result"], "exact")

    def test_security_check_complete_owner_replays(self):
        context = self.context
        function = next(r for r in context.linked["functions"] if r["symbol"] == "@__security_check_cookie@4")
        unit = dict(size=17, compare_size=17, target_address=0x47499B, linkages=[
            dict(offset=2, type="DIR32", symbol="___security_cookie", target=0x49EA4C),
            dict(offset=13, type="REL32", symbol="___report_gsfailure", target=0x474F5D)])
        self.assertEqual(replay_owner(context.image, context.target, context.publics, function, unit)["result"], "exact")

    @classmethod
    def tearDownClass(cls):
        cls.context.finish()


if __name__ == "__main__":
    unittest.main()
