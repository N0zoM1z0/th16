#!/usr/bin/env python3
"""Static complete-contribution and refusal controls for the pinned atan2 family."""
import copy
import csv
import hashlib
from pathlib import Path
import struct
import tempfile
import tomllib
import unittest
from unittest.mock import patch

from linked_image import pdb_section_contributions
from runtime_atan2 import review_atan2
from runtime_identity import RuntimeEvidenceError, review_runtime_interiors, validate_runtime_field
from strict_oracle import Context, Incomplete, ROOT, reviewed_linkages


class ImagePatch:
    def __init__(self, image, address=None, relocations=None):
        self.image, self.address, self.relocations = image, address, relocations

    def __getattr__(self, name):
        return getattr(self.image, name)

    def read_address(self, address, size):
        data = bytearray(self.image.read_address(address, size))
        if self.address is not None and address <= self.address < address+size:
            data[self.address-address] ^= 1
        return bytes(data)

    def base_relocations(self):
        return self.image.base_relocations() if self.relocations is None else self.relocations


class Atan2Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        cls.row = tomllib.loads((ROOT/'config/runtime-interiors.toml').read_text())['objects']['atan2']
        cls.support = cls.context.runtime_interiors['fmod']
        cls.bindings, cls.proof = review_atan2(cls.context, cls.row, cls.support)

    def rejected(self, context=None, row=None, support=None):
        with self.assertRaises(RuntimeEvidenceError):
            review_atan2(context or self.context, self.row if row is None else row,
                         self.support if support is None else support)

    def test_complete_family_exposes_only_intrinsic_at_offset_ten(self):
        self.assertEqual(set(self.bindings), {'__CIatan2'})
        b = self.bindings['__CIatan2']
        self.assertEqual((b['target'], b['entry_offset'], b['parent_size']), (0x487aaa, 10, 20))
        self.assertEqual((self.proof['code_bytes'], self.proof['data_bytes']), (188, 80))
        self.assertTrue(self.proof['complete_code_equal'] and self.proof['complete_data_equal'])
        self.assertEqual(self.proof['primary_exact_credit'], 0)

    def test_every_candidate_code_and_descriptor_byte_is_checked(self):
        for name, p in self.proof['parents'].items():
            for offset in range(p['size']):
                with self.subTest(name=name, offset=offset):
                    c = copy.copy(self.context); c.image = ImagePatch(c.image, p['candidate']+offset)
                    self.rejected(c)

    def test_original_hashes_and_padding_are_required(self):
        for name, p in self.proof['parents'].items():
            offsets = [0, p['size']//2, p['size']-1]
            if name != 'data': offsets += [-1, p['size']]
            for offset in offsets:
                with self.subTest(name=name, offset=offset):
                    c = copy.copy(self.context); c.target = ImagePatch(c.target, p['target']+offset)
                    self.rejected(c)

    def test_exact_candidate_relocations_are_required(self):
        original = set(self.context.image.base_relocations())
        required = {self.proof['parents']['entry']['candidate']+n for n in [1, 11]}
        required |= {self.proof['parents']['math']['candidate']+112}
        required |= {self.proof['parents']['data']['candidate']+n for n in range(16, 80, 4)}
        extra = {p['candidate']+n for p in self.proof['parents'].values() for n in [-1, 0]}
        for at in required|extra:
            with self.subTest(address=hex(at)):
                c = copy.copy(self.context)
                c.image = ImagePatch(c.image, relocations=sorted(original-{at} if at in required else original|{at}))
                self.rejected(c)

    def test_no_original_contribution_may_gain_a_relocation(self):
        for p in self.proof['parents'].values():
            c = copy.copy(self.context); c.target = ImagePatch(c.target, relocations=[p['target']])
            self.rejected(c)

    def test_closed_profile_and_integral_addresses_are_required(self):
        for key, value in [('profile', 'unreviewed'), ('alias', '__other'), ('entry_address', 0x487aa1),
                           ('math_address', 0x488b01), ('data_address', 0x494e51), ('entry_address', True)]:
            row = dict(self.row); row[key] = value
            with self.subTest(key=key, value=value): self.rejected(row=row)

    def test_complete_verified_dispatcher_support_is_required(self):
        for key, value in [('profile', 'unknown'), ('complete_code_equal', False), ('complete_data_equal', False)]:
            support = copy.deepcopy(self.support); support[key] = value
            with self.subTest(key=key): self.rejected(support=support)

    def test_all_public_offsets_and_producers_are_required(self):
        for symbol in ['_atan2', '__CIatan2', '__fFATN2', '__rtpiby2', '__OP_ATAN2jmptab']:
            for key, value in [('address', 0x400000), ('object', 'libucrt:wrong.obj')]:
                c = copy.copy(self.context); c.publics = copy.deepcopy(c.publics)
                next(x for x in c.publics if x['symbol'] == symbol)[key] = value
                with self.subTest(symbol=symbol, key=key): self.rejected(c)

    def test_complete_entry_owner_is_required(self):
        for key, value in [('size', 10), ('size', 19), ('size', 21), ('pdb_object', 'wrong.lib'),
                           ('map_object', 'libucrt:wrong.obj'), ('pdb_module_index', -1)]:
            c = copy.copy(self.context); c.linked = copy.deepcopy(c.linked)
            next(x for x in c.linked['functions'] if x['symbol'] == '_atan2')[key] = value
            with self.subTest(key=key, value=value): self.rejected(c)

    def test_every_complete_pdb_contribution_is_required(self):
        original = pdb_section_contributions(self.context.directory/'th16.pdb')
        selected = [i for i, x in enumerate(original['contributions'])
                    if x['module'].replace('\\', '/').lower().split('/')[-1] in ['87ctriga.obj', '87triga.obj']]
        self.assertEqual(len(selected), 3)
        for i in selected:
            for key, value in [('size', 1), ('object', 'wrong.lib'), ('section_offset', 0)]:
                data = copy.deepcopy(original); data['contributions'][i][key] = value
                with self.subTest(index=i, key=key), patch('runtime_atan2.pdb_section_contributions', return_value=data):
                    self.rejected()

    def test_original_wrapper_witness_is_complete_and_fixed(self):
        for key, value in [('witness_parent', 0x438370), ('witness_parent_sha256', '0'*64),
                           ('witnesses', []), ('witnesses', [0x4052c5])]:
            row = dict(self.row); row[key] = value
            with self.subTest(key=key): self.rejected(row=row)
        c = copy.copy(self.context); c.boundaries = copy.deepcopy(c.boundaries)
        c.boundaries[0x4052a0]['span_end'] = '0x4052d7'; self.rejected(c)

    def test_intrinsic_field_requires_an_exact_rel32_call(self):
        f = next(x for x in self.context.linked['functions'] if x['symbol'] == '?zun_atan2f@@YAMMM@Z')
        field = dict(type='REL32', width=4, target=0x487aaa, offset=37)
        validate_runtime_field(self.context, f, field, self.bindings['__CIatan2'])
        for key, value in [('type', 'DIR32'), ('width', 8), ('addend', 1), ('local', True),
                           ('target', 0x487aa0), ('offset', 0)]:
            bad = dict(field); bad[key] = value
            with self.subTest(key=key), self.assertRaises(RuntimeEvidenceError):
                validate_runtime_field(self.context, f, bad, self.bindings['__CIatan2'])

    def test_atan2_profile_cannot_omit_verified_fmod_support(self):
        text = (ROOT/'config/runtime-interiors.toml').read_text()
        a = text.index('[objects.fmod]'); b = text.index('[objects.atan2]')
        with tempfile.TemporaryDirectory(dir=ROOT/'.analysis') as directory:
            p = Path(directory)/'interiors.toml'; p.write_text(text[:a]+text[b:])
            with self.assertRaises(RuntimeEvidenceError): review_runtime_interiors(self.context, p)

    def test_ordinary_runtime_row_cannot_admit_the_intrinsic_interior(self):
        with (ROOT/'config/linkage-bindings.csv').open() as stream: rows = list(csv.DictReader(stream))
        extra = dict.fromkeys(rows[0], '')
        extra.update(symbol='__CIatan2', target_address='0x487aaa', size='10', kind='runtime-function',
                     target_sha256=hashlib.sha256(self.context.target.read_address(0x487aaa, 10)).hexdigest(),
                     candidate_library='libucrt.lib', candidate_size='20',
                     evidence='docs/knowledge/atan2-runtime-identities.md')
        with tempfile.TemporaryDirectory(dir=ROOT/'.analysis') as directory:
            p = Path(directory)/'bindings.csv'
            with p.open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader(); writer.writerows(rows+[extra])
            with self.assertRaises(Incomplete): reviewed_linkages(self.context, p)

    def wrapper_unit(self):
        c = self.context
        symbol = '?zun_atan2f@@YAMMM@Z'
        f = next(x for x in c.linked['functions'] if x['symbol'] == symbol)
        return dict(artifact_kind='linked-pe', source='src/ZunMath.cpp', output_dir='build/reference-candidate',
                    symbol=symbol, object='ZunMath.obj', candidate_address=int(f['address'], 0),
                    target_address=0x4052a0, size=57, compare_size=57,
                    profile=c.receipt['compiler_profile'], link_profile=c.receipt['linker_profile'],
                    linkages=[dict(offset=37, width=4, type='REL32', symbol='__CIatan2', target=0x487aaa, addend=0)])

    def test_complete_wrapper_replay_passes(self):
        q = self.context.compare(self.wrapper_unit())
        self.assertEqual((q['result'], q['compared_size'], q['matched_bytes']), ('exact', 57, 57))

    def test_other_parent_targets_and_changed_owner_bytes_are_not_exact(self):
        unit = self.wrapper_unit(); base = unit['candidate_address']
        parent = self.proof['parents']['entry']['candidate']
        for offset in [0, 9, 11]:
            encoded = struct.pack('<i', parent+offset-(base+41))
            class WrongCall(ImagePatch):
                def read_address(self, address, size):
                    data = bytearray(super().read_address(address, size))
                    for i, value in enumerate(encoded):
                        at = base+37+i
                        if address <= at < address+size: data[at-address] = value
                    return bytes(data)
            c = copy.copy(self.context); c.image = WrongCall(c.image)
            with self.subTest(offset=offset), self.assertRaises(Incomplete): c.compare(unit)
        c = copy.copy(self.context); c.image = ImagePatch(c.image, base)
        self.assertEqual(c.compare(unit)['result'], 'mismatch')
        unit = copy.deepcopy(unit); unit['size'] = unit['compare_size'] = 56
        with self.assertRaises(Incomplete): self.context.compare(unit)


if __name__ == '__main__':
    unittest.main()
