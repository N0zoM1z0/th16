#!/usr/bin/env python3
"""Fail-closed CodeView size controls and real typed-global proof mutations."""
import copy
import struct
import unittest

from pdb_types import Types
from strict_oracle import Context, Incomplete, ROOT
import tomllib


def stream(records):
    payload = b"".join(struct.pack("<HH", len(data) + 2, kind) + data for kind, data in records)
    return struct.pack("<5I", 20040203, 56, 0x1000, 0x1000 + len(records), len(payload)) + b"\0" * 36 + payload


class CodeViewSizeControls(unittest.TestCase):
    def test_complete_structure_size(self):
        types = Types(stream([(0x1505, struct.pack("<HHIIIH", 0, 0, 0, 0, 0, 352) + b"Example\0")]))
        self.assertEqual(types.size(0x1000), 352)

    def test_forward_declaration_is_not_storage(self):
        types = Types(stream([(0x1505, struct.pack("<HHIIIH", 0, 0x80, 0, 0, 0, 0) + b"Example\0")]))
        self.assertIsNone(types.size(0x1000))

    def test_complete_array_extent_and_modifier(self):
        types = Types(stream([(0x1503, struct.pack("<IIH", 0x74, 0x74, 400) + b"\0"),
                              (0x1001, struct.pack("<IH", 0x1000, 1))]))
        self.assertEqual(types.size(0x1001), 400)

    def test_unknown_type_remains_unsupported(self):
        types = Types(stream([(0xFFFF, b"\0" * 20)]))
        self.assertIsNone(types.size(0x1000))


class TypedGlobalProofControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        units = tomllib.loads((ROOT / "config/match-units.toml").read_text())["units"]
        cls.unit = next(u for u in units.values() if any("storage_size" in f for f in u["linkages"])
                        and cls.context.compare(u)["result"] == "exact")

    def test_real_typed_global_unit_passes(self):
        self.assertEqual(self.context.compare(self.unit)["result"], "exact")

    def test_wrong_type_size_is_rejected(self):
        unit = copy.deepcopy(self.unit)
        next(f for f in unit["linkages"] if "storage_size" in f)["storage_size"] += 1
        with self.assertRaisesRegex(Incomplete, "PDB type extent"):
            self.context.compare(unit)

    def test_omitted_type_proof_is_rejected(self):
        unit = copy.deepcopy(self.unit)
        field = next(f for f in unit["linkages"] if "storage_size" in f)
        field.pop("storage_size")
        field.pop("storage_name")
        with self.assertRaisesRegex(Incomplete, "storage proof"):
            self.context.compare(unit)

    @classmethod
    def tearDownClass(cls):
        cls.context.finish()


if __name__ == "__main__":
    unittest.main()
