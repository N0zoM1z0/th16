#!/usr/bin/env python3
"""Mutation controls for one-state allocation cleanups in GS-buffer frames."""
import copy
import hashlib
import importlib.util
import tomllib
import unittest

from eh_identity import EHEvidenceError
from eh_gs_allocation import review_gs_allocation
from linked_image import map_statics, pdb_section_contributions
from strict_oracle import Context, ROOT

_spec = importlib.util.spec_from_file_location("aggregate_controls", ROOT / "scripts/test-eh-constructor.py")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
Overlay = _base.Overlay


class GSAllocationControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        cls.records = [r for r in tomllib.loads((ROOT / "config/eh-handlers.toml").read_text())["handlers"]
                       if r.get("profile") == "gs-allocation-cleanup-v1"]
        cls.statics = map_statics(cls.context.directory / "th16.map")
        cls.pdb = pdb_section_contributions(cls.context.directory / "th16.pdb")

    def review(self, record, context=None):
        return review_gs_allocation(context or self.context, record, self.statics, self.pdb)

    def target_change(self, record, address, payload):
        context = copy.copy(self.context)
        context.target = Overlay(context.target, {address + i: b for i, b in enumerate(payload)})
        changed = dict(record)
        for key, base, size in (("parent_sha256", record["parent_target"], record["parent_size"]),
                                ("target_sha256", record["code_target"], 61)):
            changed[key] = hashlib.sha256(context.target.read_address(base, size)).hexdigest()
        return context, changed

    def test_both_complete_graphs_pass(self):
        self.assertEqual({r["parent_target"] for r in self.records}, {0x429ff0, 0x451560})
        for record in self.records:
            proof = self.review(record)
            self.assertEqual(proof["handler"]["address"], proof["code_owner"]["address"] + 21)

    def test_size_slot_cookies_and_protected_uses_are_fixed(self):
        for record in self.records:
            parent, code = record["parent_target"], record["code_target"]
            push = 0x7e if parent == 0x429ff0 else 0x56
            for address, payload in ((parent + push + 1, b"\xc9"),   # allocation size
                                     (code + 7, b"\xf0"),             # cleanup reads another slot
                                     (code + 21 + 9, b"\xe4"),        # EH cookie displacement
                                     (code + 21 + 23, b"\xf8"),       # GS cookie slot
                                     (parent + 0x30, bytes.fromhex("c745fc00000000"))):  # extra state use
                context, changed = self.target_change(record, address, payload)
                with self.subTest(parent=hex(parent), address=hex(address)), self.assertRaises(EHEvidenceError):
                    self.review(changed, context)

    def test_record_schema_is_fixed(self):
        record = self.records[0]
        for changed in (dict(record, size=48), dict(record, eh_flags=5), dict(record, extra=1),
                        dict(record, parent_size=record["parent_size"] + 1)):
            with self.subTest(changed=sorted(set(changed.items()) - set(record.items()))), \
                    self.assertRaises(EHEvidenceError):
                self.review(changed)


if __name__ == "__main__":
    unittest.main()
