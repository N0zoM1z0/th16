#!/usr/bin/env python3
"""Positive and mutation controls for strict complete-owner byte replay."""
import copy
import struct
import unittest

from reference_bindings import validate_unit_bindings
from strict_oracle import Context, Incomplete, ROOT, replay_owner


class Image:
    def __init__(self, address, data, relocations=()):
        self.address = address
        self.data = data
        self.relocations = relocations

    def read_address(self, address, size):
        offset = address - self.address
        if offset < 0 or offset + size > len(self.data):
            raise ValueError("fixture read leaves the declared owner")
        return self.data[offset:offset + size]

    def base_relocations(self):
        return self.relocations


class CompleteOwnerReplay(unittest.TestCase):
    def setUp(self):
        self.start = 0x501000
        self.target_start = 0x401000
        candidate = b"\xb8" + struct.pack("<I", 0x503000) + b"\xe8" + struct.pack("<i", 0x502000 - self.start - 10) + b"\xc3"
        target = b"\xb8" + struct.pack("<I", 0x403000) + b"\xe8" + struct.pack("<i", 0x402200 - self.target_start - 10) + b"\xc3"
        self.image = Image(self.start, candidate, [self.start + 1])
        self.target = Image(self.target_start, target)
        self.function = dict(address=hex(self.start), size=len(candidate))
        self.publics = [dict(symbol="_Global", address=0x503000), dict(symbol="_Callee", address=0x502000)]
        self.unit = dict(target_address=self.target_start, compare_size=len(candidate), linkages=[
            dict(offset=1, type="DIR32", symbol="_Global", target=0x403000),
            dict(offset=6, type="REL32", symbol="_Callee", target=0x402200)])

    def compare(self):
        return replay_owner(self.image, self.target, self.publics, self.function, self.unit)

    def test_bound_global_and_call_are_replayed(self):
        result = self.compare()
        self.assertEqual(result["result"], "exact")
        self.assertEqual(result["matched_bytes"], 11)
        self.assertFalse(result["raw_equal"])

    def test_stored_target_cannot_make_a_different_global_match(self):
        self.assertEqual(self.compare()["result"], "exact")
        fixed = {"_Global": 0x403000, "_Callee": 0x402200}
        validate_unit_bindings(self.unit, fixed)
        fixed["_Global"] = 0x403004
        with self.assertRaisesRegex(Incomplete, "independent target binding: _Global"):
            validate_unit_bindings(self.unit, fixed)

    def test_wrong_candidate_global_is_not_masked(self):
        self.image.data = self.image.data[:1] + struct.pack("<I", 0x503004) + self.image.data[5:]
        with self.assertRaisesRegex(Incomplete, "unique linked symbol"):
            self.compare()

    def test_missing_field_is_incomplete(self):
        self.unit["linkages"].pop()
        with self.assertRaisesRegex(Incomplete, "exhaustive"):
            self.compare()

    def test_wrong_semantic_target_fails(self):
        self.unit["linkages"][1]["target"] += 1
        self.assertEqual(self.compare()["result"], "mismatch")

    def test_changed_instruction_fails(self):
        self.image.data = b"\x05" + self.image.data[1:]
        result = self.compare()
        self.assertEqual(result["result"], "mismatch")
        self.assertEqual(result["first_differences"][0]["offset"], 0)

    def test_partial_owner_is_rejected(self):
        self.function["size"] += 1
        with self.assertRaisesRegex(Incomplete, "complete declared extent"):
            self.compare()

    def test_claimed_primary_extent_cannot_exceed_the_compared_owner(self):
        self.unit["size"] = 100
        with self.assertRaisesRegex(Incomplete, "compound ownership"):
            self.compare()

    def test_ambiguous_symbol_is_rejected(self):
        self.publics.append(dict(symbol="_Global", address=0x503004))
        with self.assertRaisesRegex(Incomplete, "unique linked symbol"):
            self.compare()

    def test_changed_local_offset_is_rejected(self):
        self.image.data = b"\xb8" + struct.pack("<I", self.start + 10) + self.image.data[5:]
        self.unit["linkages"][0] = dict(offset=1, type="DIR32", symbol="<local>", local=True, target=self.target_start + 9)
        with self.assertRaisesRegex(Incomplete, "changes its offset"):
            self.compare()

    def test_unlinked_trailing_data_is_compared(self):
        self.image.data += b"\xff"
        self.target.data += b"\xfe"
        self.function["size"] += 1
        self.unit["compare_size"] += 1
        self.unit["data_spans"] = [dict(offset=11, width=1)]
        result = self.compare()
        self.assertEqual(result["result"], "mismatch")
        self.assertEqual(result["matched_bytes"], 11)
        self.assertEqual(result["first_differences"][0]["offset"], 11)

    def test_undeclared_trailing_data_is_incomplete(self):
        self.image.data += b"\xff"
        self.target.data += b"\xff"
        self.function["size"] += 1
        self.unit["compare_size"] += 1
        with self.assertRaisesRegex(ValueError, "Capstone decoded"):
            self.compare()

    def test_overlapping_target_owner_is_incomplete(self):
        context = Context.__new__(Context)
        context.switch_owners = {}
        context.target = self.target
        context.boundaries = {self.target_start - 8: dict(span_end=hex(self.target_start + 1))}
        with self.assertRaisesRegex(Incomplete, "overlaps"):
            context.check_boundary(self.unit)

    def boundary_context(self):
        context = Context.__new__(Context)
        context.directory = ROOT / "build/reference-candidate"
        context.receipt = dict(compiler_profile=["/GL"], linker_profile=["/LTCG"])
        unit = dict(self.unit, source="src/Rng.cpp", object="Rng.obj", symbol="_Fixture",
                    artifact_kind="linked-pe", profile=["/GL"], link_profile=["/LTCG"],
                    candidate_address=self.start)
        function = dict(self.function, symbol="_Fixture",
                        pdb_object="Z:" + str(context.directory / "obj/src/Rng.obj"))
        context.linked = dict(functions=[function])
        context.boundaries = {}
        context.unavailable_eh = {}
        context.unavailable_statics = {}
        return context, unit

    def test_unavailable_eh_evidence_blocks_only_its_parent(self):
        context, unit = self.boundary_context()
        context.unavailable_eh[self.target_start] = "auxiliary owner changed"
        with self.assertRaisesRegex(Incomplete, "reviewed EH parent: auxiliary owner changed"):
            context.compare(unit)
        context.unavailable_eh = {self.target_start + 16: "auxiliary owner changed"}
        with self.assertRaisesRegex(Incomplete, "lacks an independently reviewed function boundary"):
            context.compare(unit)

    def test_missing_original_boundary_is_distinct_from_an_extent_difference(self):
        context, unit = self.boundary_context()
        with self.assertRaisesRegex(Incomplete, "lacks an independently reviewed function boundary"):
            context.compare(unit)

    def test_real_extent_difference_still_refuses_comparison(self):
        context, unit = self.boundary_context()
        context.boundaries[self.target_start] = dict(size=12)
        with self.assertRaisesRegex(Incomplete, "complete candidate owner differs"):
            context.compare(unit)


class VirtualTailCallControls(unittest.TestCase):
    """A mid-function JMP through a vftable slot is an exit, never a switch."""

    def decode(self, code):
        import capstone
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        decoder.detail = True
        instructions = list(decoder.disasm(bytes.fromhex(code), 0x1000))
        return instructions, instructions[-1]

    def accepted(self, code):
        from strict_oracle import virtual_tail_call
        instructions, jump = self.decode(code)
        return virtual_tail_call(instructions, jump)

    def test_original_get_int_arg_tail_call_is_accepted(self):
        # mov ecx,[esi+0x1018]; pop edi; pop esi; mov eax,[ecx]; mov [ebp+8],edx; pop ebp; jmp [eax+4]
        self.assertTrue(self.accepted("8b8e180100005f5e8b018955085dff6004"))

    def test_jump_tables_and_unproven_pointers_are_rejected(self):
        for code in ("8b8e180100005f5e8b018955085dff248504000000",  # indexed table
                     "8b8e180100005f5e8b018955085dff6002",          # misaligned slot
                     "8b8e180100008b018b4e045dff6004",              # ECX rewritten after the vptr load
                     "8b8e180100008b06895508ff6004",                # vptr not loaded from [ECX]
                     "8b8e180100008b415dff6004",                    # vptr from [ECX+disp]
                     "8b018b8e18010000e800000000ff6004"):           # call between load and jump
            with self.subTest(code=code):
                self.assertFalse(self.accepted(code))


class CompilerGeneratedStaticOwnerControls(unittest.TestCase):
    """Only uniquely named ??__E/??__F statics own their contributions."""

    @classmethod
    def setUpClass(cls):
        from linked_image import linked_functions, map_statics
        cls.directory = ROOT / "build/reference-candidate"
        cls.linked_functions = staticmethod(linked_functions)
        cls.functions = linked_functions(cls.directory / "th16.exe", cls.directory / "th16.map",
                                         cls.directory / "th16.pdb")["functions"]
        cls.statics = map_statics(cls.directory / "th16.map")

    def test_unique_initializers_and_finalizers_are_owned(self):
        symbols = {f["symbol"] for f in self.functions}
        self.assertIn("??__Eg_Arcfile@@YAXXZ", symbols)
        self.assertIn("??__Fg_Arcfile@@YAXXZ", symbols)
        ordinary = {r["symbol"] for r in self.statics if not r["symbol"].startswith("??__")}
        self.assertTrue(ordinary)
        self.assertFalse(ordinary & symbols)

    def test_duplicated_initializer_name_is_not_owned(self):
        import tempfile
        from pathlib import Path
        text = (self.directory / "th16.map").read_text(encoding="cp1252", errors="replace")
        line = next(l for l in text.splitlines() if "??__Eg_Arcfile@@YAXXZ" in l)
        duplicate = line.replace("Arcfile.obj", "Other.obj")
        with tempfile.TemporaryDirectory(dir=ROOT / ".analysis") as directory:
            path = Path(directory) / "th16.map"
            path.write_text(text.replace(line, line + "\n" + duplicate, 1), encoding="cp1252")
            functions = self.linked_functions(self.directory / "th16.exe", path,
                                              self.directory / "th16.pdb")["functions"]
        self.assertNotIn("??__Eg_Arcfile@@YAXXZ", {f["symbol"] for f in functions})


if __name__ == "__main__":
    unittest.main()
