#!/usr/bin/env python3
"""Replay the fog cursor limit and reject unsafe address-provenance mutations."""
import copy
import struct
import tomllib
import unittest

from strict_oracle import Context, Incomplete, ROOT, pointer_limit


class PointerLimitControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        units = tomllib.loads((ROOT / "config/match-units.toml").read_text())["units"]
        cls.template = units["reference-00467200"]
        cls.function = next(r for r in cls.context.linked["functions"] if r["symbol"] == cls.template["symbol"])

    def setUp(self):
        self.unit = copy.deepcopy(self.template)
        self.limit = next(f for f in self.unit["linkages"] if f["offset"] == 438)
        proof = pointer_limit(self.context, self.function, self.limit, self.unit["linkages"])
        self.assertIsNotNone(proof)
        self.limit.update(proof)

    def reject_code_change(self, offset, replacement):
        context = copy.copy(self.context)
        original = context.image
        address = int(self.function["address"], 0) + offset

        class Overlay:
            def read_address(self, start, size):
                data = bytearray(original.read_address(start, size))
                for index, byte in enumerate(replacement):
                    if start <= address + index < start + size:
                        data[address + index - start] = byte
                return bytes(data)

        context.image = Overlay()
        self.assertIsNone(pointer_limit(context, self.function, self.limit, self.unit["linkages"]))

    def test_complete_fog_owner_replays(self):
        result = self.context.compare(self.unit)
        self.assertEqual((result["result"], result["compared_size"], result["matched_bytes"]), ("exact", 522, 522))
        self.assertEqual((self.limit["storage_size"], self.limit["addend"]), (112, 131))

    def test_nearest_neighbor_binding_stays_a_mismatch(self):
        self.limit.pop("pointer_limit")
        self.limit.update(symbol="?g_arcfiles@@3PAUArcfile@@A", target=0x4D7BA0,
                          addend=3, storage_name="g_arcfiles", storage_size=320)
        self.assertEqual(self.context.compare(self.unit)["result"], "mismatch")

    def test_ordinary_data_binding_cannot_escape_storage(self):
        self.limit.pop("pointer_limit")
        with self.assertRaisesRegex(Incomplete, "leaves its typed global storage"):
            self.context.compare(self.unit)

    def test_limit_addend_is_derived_from_the_cursor(self):
        self.limit["addend"] -= 1
        with self.assertRaisesRegex(Incomplete, "typed-cursor proof"):
            self.context.compare(self.unit)

    def test_limit_flag_cannot_authorize_a_memory_access(self):
        store = next(f for f in self.unit["linkages"] if f["offset"] == 473)
        store["pointer_limit"] = True
        with self.assertRaisesRegex(Incomplete, "typed-cursor proof"):
            self.context.compare(self.unit)

    def test_wrong_stride_is_rejected(self):
        self.reject_code_change(0x19D, b"\x20")

    def test_wrong_backedge_condition_is_rejected(self):
        self.reject_code_change(0x1BB, b"\x8f")

    def test_secondary_backedge_cannot_bypass_the_limit(self):
        self.reject_code_change(0x1B0, b"\xe2\xde")

    def test_preheader_cannot_skip_initialization_and_comparison(self):
        import capstone
        start = int(self.function["address"], 0)
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        decoder.detail = True
        instructions = decoder.disasm(self.context.image.read_address(start, self.function["size"]), start)
        call = next(i for i in instructions if i.mnemonic == "call" and i.imm_size == 4)
        self.reject_code_change(call.address - start, b"\xe9" + struct.pack("<i", start + 0x1BA - call.address - 5))

    def test_limit_cursor_cannot_escape_after_the_loop(self):
        self.reject_code_change(0x1C4, b"\x8b\xc7")

    def test_cursor_escape_is_rejected(self):
        self.reject_code_change(0x190, b"\x8b\xc7")

    def test_out_of_bounds_store_is_rejected(self):
        self.reject_code_change(0x18F, b"\x1c")

    def test_unknown_callee_cannot_supply_preservation_evidence(self):
        context = copy.copy(self.context)
        context.reviewed_linkages = dict(context.reviewed_linkages)
        context.reviewed_linkages.pop("__libm_sse2_sqrt_precise")
        self.assertIsNone(pointer_limit(context, self.function, self.limit, self.unit["linkages"]))

    @classmethod
    def tearDownClass(cls):
        cls.context.finish()


if __name__ == "__main__":
    unittest.main()
