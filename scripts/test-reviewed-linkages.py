#!/usr/bin/env python3
"""Mutate fixed linkage evidence without changing the private target or artifacts."""
import copy
import csv
import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

import capstone

from strict_oracle import Context, Incomplete, ROOT, literal_memory_witness, reviewed_linkages, replay_owner


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

    def test_gather_timer_literal_requires_its_own_typed_read(self):
        for field, value in [("witness_instruction", "0x405f6f"),
                             ("witness_instruction", "0x405f68"),
                             ("witness_mnemonic", "addss"), ("size", "8")]:
            with self.subTest(field=field, value=value):
                rows = copy.deepcopy(self.rows)
                next(r for r in rows if r["symbol"] == "__real@43960000")[field] = value
                with self.assertRaises(Incomplete):
                    self.check_rows(rows)

    def test_fixed_numeric_literals_require_their_own_complete_typed_reads(self):
        for symbol, witness, duplicate, size in [
                ("__real@41a00000", 0x4549a9, 0x4917e8, 4),
                ("__real@4020000000000000", 0x454b8f, 0x494bc8, 8),
                ("__real@42200000", 0x454bfb, 0x4917f0, 4),
                ("__real@42480000", 0x405abc, 0x4917f4, 4),
                ("__real@42700000", 0x40c534, 0x491ec8, 4),
                ("__real@41f00000", 0x42640c, 0x4917ec, 4),
                ("__real@40200000", 0x443a56, 0x49457c, 4),
                ("__real@43300000", 0x40f501, 0x490254, 4),
                ("__real@44000000", 0x442649, 0x494868, 4)]:
            mutations = [("witness_instruction", hex(witness + 1)),
                         ("witness_instruction", "0x454970"),
                         ("witness_mnemonic", "subss"), ("size", str(size * 2)),
                         ("target_address", hex(duplicate))]
            for field, value in mutations:
                with self.subTest(symbol=symbol, field=field, value=value):
                    rows = copy.deepcopy(self.rows)
                    next(r for r in rows if r["symbol"] == symbol)[field] = value
                    with self.assertRaises(Incomplete):
                        self.check_rows(rows)

    def test_timing_and_collision_scalars_require_their_fixed_typed_reads(self):
        for symbol, witness, duplicate, size in [
                ("__real@30000000", 0x402cd4, 0x496e58, 4),
                ("__real@40a00000", 0x414edd, 0x4917e0, 4),
                ("__real@3fc00000", 0x45b2ac, 0x49452c, 4),
                ("__real@3fc0000000000000", 0x471c29, 0x496640, 8),
                ("__real@4004000000000000", 0x45aa2c, 0x496d60, 8),
                ("__real@400c000000000000", 0x45afd0, 0x497060, 8),
                ("__real@42400000", 0x40fee2, 0x491f68, 4),
                ("__real@42600000", 0x410a5a, 0x491ec0, 4)]:
            for field, value in [("witness_instruction", hex(witness + 1)),
                                 ("witness_instruction", "0x402cb0"),
                                 ("witness_mnemonic", "addss"),
                                 ("size", str(size * 2)),
                                 ("target_address", hex(duplicate))]:
                rows = copy.deepcopy(self.rows)
                next(r for r in rows if r["symbol"] == symbol)[field] = value
                with self.subTest(symbol=symbol, field=field, value=value):
                    with self.assertRaises(Incomplete):
                        self.check_rows(rows)

    def test_comisd_literals_require_their_fixed_complete_double_reads(self):
        for symbol, witness, duplicate in [
                ("__real@3ff0000000000000", 0x42631c, 0x490170),
                ("__real@0000000000000000", 0x42dbf2, 0x48b300),
                ("__real@3ff8000000000000", 0x45ac95, 0x496a60)]:
            for field, value in [("witness_instruction", hex(witness + 1)),
                                 ("witness_instruction", "0x4262f0"),
                                 ("witness_mnemonic", "ucomisd"), ("size", "16"),
                                 ("target_address", hex(duplicate))]:
                rows = copy.deepcopy(self.rows)
                next(r for r in rows if r["symbol"] == symbol)[field] = value
                with self.subTest(symbol=symbol, field=field, value=value):
                    with self.assertRaises(Incomplete):
                        self.check_rows(rows)

    def test_comisd_absolute_reads_have_an_eight_byte_footprint(self):
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        decoder.detail = True
        for register in range(8):
            raw = bytes.fromhex("660f2f") + bytes([5 | (register << 3)]) + bytes.fromhex("78563412")
            context = SimpleNamespace(boundaries={0: {"size": len(raw)}},
                                      target=SimpleNamespace(read_address=lambda base, size: raw[base:base+size]))
            instruction = next(decoder.disasm(raw, 0))
            with self.subTest(register=register):
                self.assertTrue(literal_memory_witness(context, instruction, 0x12345678, 8))
                self.assertFalse(literal_memory_witness(context, instruction, 0x12345678, 16))
                self.assertFalse(literal_memory_witness(context, instruction, 0x12345678, 4))

    def test_comisd_unreviewed_addressing_and_prefixes_are_rejected(self):
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        decoder.detail = True
        for text in ("660f2f9078563412", "660f2f148578563412", "64660f2f1578563412",
                     "66660f2f1578563412", "660f2fd1"):
            raw = bytes.fromhex(text)
            context = SimpleNamespace(boundaries={0: {"size": len(raw)}},
                                      target=SimpleNamespace(read_address=lambda base, size: raw[base:base+size]))
            instruction = next(decoder.disasm(raw, 0))
            self.assertEqual(instruction.mnemonic, "comisd")
            with self.subTest(encoding=text):
                self.assertFalse(literal_memory_witness(context, instruction, 0x12345678, 8))

    def test_comisd_witness_requires_one_complete_parent_instruction(self):
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        decoder.detail = True
        instruction = next(decoder.disasm(self.context.target.read_address(0x42631c, 16), 0x42631c))
        for mode in ("missing", "ambiguous", "shortened"):
            context = copy.copy(self.context)
            context.boundaries = copy.deepcopy(self.context.boundaries)
            if mode == "missing":
                del context.boundaries[0x4262f0]
            elif mode == "ambiguous":
                context.boundaries[0x4262ef] = {"size": "236"}
            else:
                context.boundaries[0x4262f0]["size"] = str(0x42631c - 0x4262f0 + 7)
            with self.subTest(mode=mode):
                self.assertFalse(literal_memory_witness(context, instruction, 0x494540, 8))

    def test_comisd_encoded_address_and_register_must_match_decoder_operands(self):
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        decoder.detail = True
        instruction = next(decoder.disasm(self.context.target.read_address(0x42631c, 16), 0x42631c))
        for byte, mask in ((0, 1), (2, 1), (3, 8), (4, 1)):
            changed = bytearray(instruction.bytes)
            changed[byte] ^= mask
            altered = SimpleNamespace(bytes=changed, operands=instruction.operands,
                                      mnemonic=instruction.mnemonic, address=instruction.address)
            with self.subTest(byte=byte):
                self.assertFalse(literal_memory_witness(self.context, altered, 0x494540, 8))

    def test_replay_fps_format_requires_its_complete_storage_and_fixed_push(self):
        symbol = "??_C@_03GOOLIKIF@?$CF3d?$AA@"
        candidate = next(p["address"] for p in self.context.publics if p["symbol"] == symbol)
        self.assertEqual(self.context.data_contributions[candidate], [4])
        self.assertEqual(self.context.image.read_address(candidate, 4), b"%3d\0")
        for key, value in [("witness_instruction", "0x44837b"),
                           ("witness_instruction", "0x448379"),
                           ("witness_mnemonic", "lea"),
                           ("target_address", "0x492a06")]:
            rows = copy.deepcopy(self.rows)
            next(r for r in rows if r["symbol"] == symbol)[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(Incomplete):
                self.check_rows(rows)
        rows = copy.deepcopy(self.rows)
        shortened = next(r for r in rows if r["symbol"] == symbol)
        shortened.update(size="3", target_sha256=hashlib.sha256(b"%3d").hexdigest())
        with self.assertRaisesRegex(Incomplete, "complete NUL-terminated PDB storage"):
            self.check_rows(rows)
        for sizes in ([3], [4, 4]):
            context = copy.copy(self.context)
            context.data_contributions = dict(context.data_contributions)
            context.data_contributions[candidate] = sizes
            with self.subTest(sizes=sizes), self.assertRaisesRegex(Incomplete, "complete NUL-terminated PDB storage"):
                reviewed_linkages(context)

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
