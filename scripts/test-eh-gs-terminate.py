#!/usr/bin/env python3
"""Mutation controls for the single terminal state in a GS-buffer frame."""
import copy
import hashlib
import importlib.util
import tomllib
import unittest

from eh_identity import EHEvidenceError
from eh_terminate import GS_SINGLE_PROFILE, review_terminate
from linked_image import map_statics, pdb_section_contributions
from strict_oracle import Context, ROOT

_spec = importlib.util.spec_from_file_location("aggregate_controls", ROOT / "scripts/test-eh-constructor.py")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
Overlay = _base.Overlay


class GSTerminateControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        cls.record = next(r for r in tomllib.loads((ROOT / "config/eh-handlers.toml").read_text())["handlers"]
                          if r.get("profile") == GS_SINGLE_PROFILE)
        cls.statics = map_statics(cls.context.directory / "th16.map")
        cls.pdb = pdb_section_contributions(cls.context.directory / "th16.pdb")

    def review(self, record, context=None):
        return review_terminate(context or self.context, record, self.statics, self.pdb)

    def target_change(self, address, payload):
        context = copy.copy(self.context)
        context.target = Overlay(context.target, {address + i: b for i, b in enumerate(payload)})
        changed = dict(self.record)
        for key, base, size in (("parent_sha256", self.record["parent_target"], self.record["parent_size"]),
                                ("target_sha256", self.record["target"], 37)):
            changed[key] = hashlib.sha256(context.target.read_address(base, size)).hexdigest()
        return context, changed

    def test_complete_graph_passes(self):
        proof = self.review(self.record)
        self.assertEqual((proof["parent_target"], proof["cookie_offset"]), (0x45d510, -0x60))

    def test_cookies_states_and_frame_uses_are_fixed(self):
        parent, handler = self.record["parent_target"], self.record["target"]
        for address, payload in ((handler + 9, b"\xa4"),                       # EH cookie slot
                                 (handler + 19, b"\xf8"),                      # GS cookie slot
                                 (parent + 29, b"\xec"),                       # GS cookie store
                                 (parent + 633, bytes.fromhex("c745fc01000000")),  # state number
                                 (parent + 53, bytes.fromhex("8945b0"))):      # protected local use
            context, changed = self.target_change(address, payload)
            with self.subTest(address=hex(address)), self.assertRaises(EHEvidenceError):
                self.review(changed, context)

    def test_record_schema_is_fixed(self):
        for changed in (dict(self.record, size=27), dict(self.record, eh_flags=5), dict(self.record, extra=1),
                        dict(self.record, parent_size=self.record["parent_size"] + 1)):
            with self.subTest(changed=sorted(set(changed.items()) - set(self.record.items()))), \
                    self.assertRaises(EHEvidenceError):
                self.review(changed)


if __name__ == "__main__":
    unittest.main()
