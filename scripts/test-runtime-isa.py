#!/usr/bin/env python3
"""Refuse partial ISA storage, changed startup paths and incomplete runtime graphs."""
import copy
from dataclasses import replace
import hashlib
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from linked_image import map_statics, pdb_section_contributions
from runtime_isa import KIND, _STARTUP, review_isa, validate_isa_field
from runtime_identity import RuntimeEvidenceError
from strict_oracle import Context, ROOT

_spec = importlib.util.spec_from_file_location('aggregate_controls', ROOT / 'scripts/test-eh-constructor.py')
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
Overlay = _base.Overlay


class ISAControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        cls.path = ROOT / 'config/runtime-globals.toml'
        cls.text = cls.path.read_text()
        cls.pdb = pdb_section_contributions(cls.context.directory / 'th16.pdb')
        cls.statics = map_statics(cls.context.directory / 'th16.map')
        cls.bindings, cls.proof = review_isa(cls.context, cls.path)
        cls.thunk = next(p['address'] for p in cls.context.publics if p['symbol'] == '_IsProcessorFeaturePresent@4')

    def review(self, context=None, text=None, pdb=None, statics=None):
        with tempfile.TemporaryDirectory(dir=ROOT / '.analysis') as directory:
            path = Path(directory) / 'globals.toml'
            path.write_text(self.text if text is None else text)
            with patch('runtime_isa.pdb_section_contributions', return_value=self.pdb if pdb is None else pdb), \
                 patch('runtime_isa.map_statics', return_value=self.statics if statics is None else statics):
                return review_isa(context or self.context, path)

    def mutate(self, side, address):
        context = copy.copy(self.context)
        image = getattr(context, side)
        setattr(context, side, Overlay(image, {address: image.read_address(address, 1)[0] ^ 1}))
        return context

    def test_complete_startup_initializer_and_storage_pass(self):
        bindings, proof = self.review()
        self.assertEqual(bindings, self.bindings)
        self.assertEqual(proof, self.proof)
        self.assertEqual(set(bindings), {'___isa_available'})
        self.assertEqual(bindings['___isa_available']['kind'], KIND)
        self.assertEqual((proof['size'], proof['storage_size'], proof['enabled_size']), (415, 8, 4))
        self.assertEqual(proof['storage_kind'], 'virtual-zero-fill')
        self.assertEqual((len(proof['fields']), len(proof['relocations'])), (16, 15))
        self.assertEqual((proof['decoded_instructions'], proof['primary_exact_credit']), (133, 0))

    def test_profile_addresses_sizes_and_extra_keys_are_fixed(self):
        for old, new in [('msvc-x86-isa-storage-v1', 'unknown'), ('415', '414'),
                         ('storage_size = 8', 'storage_size = 4'), ('enabled_size = 4', 'enabled_size = 3'),
                         ('0x00475430', '0x00475431'), ('0x004a65fc', '0x004a6600'),
                         ('0x0049ea50', '0x0049ea54')]:
            with self.subTest(old=old), self.assertRaises(RuntimeEvidenceError):
                self.review(text=self.text.replace(old, new))
        with self.assertRaises(RuntimeEvidenceError):
            self.review(text=self.text + '\naddress_point = 4\n')

    def test_original_initializer_hash_and_inventory_are_required(self):
        with self.assertRaisesRegex(RuntimeEvidenceError, 'hash'):
            self.review(text=self.text.replace('initializer_sha256 = "', 'initializer_sha256 = "0'))
        for size in (414, 416):
            context = copy.copy(self.context)
            context.boundaries = copy.deepcopy(context.boundaries)
            context.boundaries[0x475430]['size'] = str(size)
            with self.assertRaises(RuntimeEvidenceError):
                self.review(context=context)

    def test_every_candidate_initializer_byte_is_compared(self):
        base = int(self.proof['initializer']['address'], 0)
        for offset in range(415):
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                self.review(context=self.mutate('image', base + offset))

    def test_complete_initialized_mask_and_import_thunks_are_compared(self):
        for side, address, size in [('image', self.proof['enabled_candidate'], 4),
                                    ('target', self.proof['enabled_target'], 4),
                                    ('image', self.thunk, 6), ('target', 0x486aaa, 6)]:
            for offset in range(size):
                with self.subTest(side=side, address=address, offset=offset), self.assertRaises(ValueError):
                    self.review(context=self.mutate(side, address + offset))

    def test_every_startup_instruction_is_required(self):
        for address, payload, _ in _STARTUP:
            for offset in range(len(bytes.fromhex(payload))):
                with self.subTest(address=address, offset=offset), self.assertRaises(RuntimeEvidenceError):
                    self.review(context=self.mutate('target', address + offset))

    def test_pe_entrypoint_is_independent_of_the_consumer(self):
        context = copy.copy(self.context)
        context.target = Overlay(context.target)
        import pefile
        pe = pefile.PE(data=context.target.data, fast_load=True)
        data = bytearray(context.target.data)
        offset = pe.OPTIONAL_HEADER.get_field_absolute_offset('AddressOfEntryPoint')
        struct.pack_into('<I', data, offset, pe.OPTIONAL_HEADER.AddressOfEntryPoint + 1)
        context.target.data = bytes(data)
        with self.assertRaisesRegex(RuntimeEvidenceError, 'entrypoint'):
            self.review(context=context)

    def test_original_operand_roles_survive_hash_updates(self):
        old_hash = hashlib.sha256(self.context.target.read_address(0x475430, 415)).hexdigest()
        for offset in (5, 19, 57, 205, 214, 282, 302, 309, 363, 372, 395, 404):
            context = self.mutate('target', 0x475430 + offset)
            new_hash = hashlib.sha256(context.target.read_address(0x475430, 415)).hexdigest()
            with self.subTest(offset=offset), self.assertRaises(RuntimeEvidenceError):
                self.review(context=context, text=self.text.replace(old_hash, new_hash))

    def test_all_complete_pdb_contributions_are_mandatory(self):
        for baseline in self.proof['contributions'] + [self.proof['import_contribution']]:
            for mode in ('short', 'long', 'duplicate', 'missing', 'object', 'module', 'permissions', 'overlap'):
                pdb = copy.deepcopy(self.pdb)
                row = next(r for r in pdb['contributions'] if r == baseline)
                if mode == 'short': row['size'] -= 1
                elif mode == 'long': row['size'] += 1
                elif mode == 'duplicate': pdb['contributions'].append(copy.deepcopy(row))
                elif mode == 'missing': pdb['contributions'].remove(row)
                elif mode == 'object': row['object'] = str(ROOT / 'other.lib')
                elif mode == 'module': row['module_index'] += 1
                elif mode == 'permissions': row['characteristics'] ^= 0x80000000
                else:
                    other = dict(row, section_offset=row['section_offset'] + 1, size=1)
                    pdb['contributions'].append(other)
                with self.subTest(size=baseline['size'], mode=mode), self.assertRaises(RuntimeEvidenceError):
                    self.review(pdb=pdb)

    def test_missing_duplicate_or_unreviewed_storage_names_are_rejected(self):
        for name in ('___isa_available', '___favor', '___isa_enabled', '___isa_available_init', '_IsProcessorFeaturePresent@4'):
            for mode in ('missing', 'duplicate', 'address', 'producer', 'alias', 'role'):
                context = copy.copy(self.context)
                context.publics = copy.deepcopy(context.publics)
                row = next(p for p in context.publics if p['symbol'] == name)
                if mode == 'missing': context.publics.remove(row)
                elif mode == 'duplicate': context.publics.append(copy.deepcopy(row))
                elif mode == 'address': row['address'] += 1
                elif mode == 'producer': row['object'] = 'other.obj'
                elif mode == 'role': row['flags'] = [] if row['flags'] else ['f']
                else: context.publics.append(dict(row, symbol='unreviewed_alias'))
                with self.subTest(name=name, mode=mode), self.assertRaises(RuntimeEvidenceError):
                    self.review(context=context)

    def test_initializer_must_remain_a_complete_pinned_linked_owner(self):
        for mode in ('missing', 'duplicate', 'size', 'producer', 'map', 'module'):
            context = copy.copy(self.context)
            context.linked = copy.deepcopy(context.linked)
            functions = context.linked['functions']
            owner = next(f for f in functions if f['symbol'] == '___isa_available_init')
            if mode == 'missing': functions.remove(owner)
            elif mode == 'duplicate': functions.append(copy.deepcopy(owner))
            elif mode == 'size': owner['size'] -= 1
            elif mode == 'producer': owner['pdb_object'] = str(ROOT / 'other.lib')
            elif mode == 'map': owner['map_object'] = 'LIBCMT:other.obj'
            else: owner['pdb_module_index'] += 1
            with self.subTest(mode=mode), self.assertRaises(RuntimeEvidenceError): self.review(context=context)

    def test_all_eight_bytes_must_remain_in_writable_virtual_zero_fill(self):
        for side, address in [('target', 0x4a65fc), ('image', self.proof['storage_candidate'])]:
            for mode in ('raw', 'short', 'readonly', 'code'):
                context = copy.copy(self.context)
                image = Overlay(getattr(context, side))
                image.sections = list(image.sections)
                index = next(i for i, s in enumerate(image.sections) if image.image_base+s.rva <= address < image.image_base+s.rva+max(s.virtual_size,s.raw_size))
                s = image.sections[index]
                if mode == 'raw': s = replace(s, raw_size=address-image.image_base-s.rva+1)
                elif mode == 'short': s = replace(s, virtual_size=address-image.image_base-s.rva+7)
                elif mode == 'readonly': s = replace(s, characteristics=s.characteristics & ~0x80000000)
                else: s = replace(s, characteristics=s.characteristics | 0x20)
                image.sections[index] = s
                setattr(context, side, image)
                with self.subTest(side=side, mode=mode), self.assertRaises(RuntimeEvidenceError):
                    self.review(context=context)

    def test_relocation_footprints_preserve_duplicates_and_boundaries(self):
        code = int(self.proof['initializer']['address'], 0)
        for remove, add in [([code+o], []) for o in self.proof['relocations']] + [
                ([], [code+5]), ([], [code-1]), ([], [code+414]), ([], [self.proof['storage_candidate']+7]),
                ([], [self.proof['enabled_candidate']-1]), ([self.thunk + 2], []), ([], [self.thunk + 2])]:
            context = copy.copy(self.context)
            context.image = Overlay(context.image, remove=remove, add=add)
            with self.subTest(remove=remove, add=add), self.assertRaises(ValueError): self.review(context=context)
        context = copy.copy(self.context)
        context.target = Overlay(context.target, add=[0x475435])
        with self.assertRaises(RuntimeEvidenceError): self.review(context=context)

    def test_import_identity_includes_dll_name_iat_and_uniqueness(self):
        import runtime_isa
        original = runtime_isa.imports
        for mode in ('dll', 'name', 'address', 'duplicate'):
            def changed(image):
                rows = original(image)
                entry = next(r for r in rows if r[:2] == (b'kernel32.dll', b'IsProcessorFeaturePresent'))
                rows.remove(entry)
                if mode == 'dll': rows.append((b'other.dll', entry[1], entry[2]))
                elif mode == 'name': rows.append((entry[0], b'OtherFeature', entry[2]))
                elif mode == 'address': rows.append((entry[0], entry[1], entry[2]+4))
                else: rows.extend([entry,entry])
                return rows
            with self.subTest(mode=mode), patch('runtime_isa.imports', side_effect=changed), self.assertRaises(RuntimeEvidenceError):
                self.review()

    def test_only_the_exact_isa_dir32_address_point_is_exported(self):
        binding = self.bindings['___isa_available']
        field = dict(type='DIR32', width=4, target=binding['target'], addend=0)
        validate_isa_field(field, binding)
        for key, value in [('type','REL32'), ('width',8), ('addend',4), ('local',True), ('storage_size',8), ('target',binding['target']+4)]:
            with self.subTest(key=key), self.assertRaises(RuntimeEvidenceError): validate_isa_field(dict(field,**{key:value}),binding)

    def test_manifest_and_verifier_are_fingerprinted(self):
        for name in ('config/runtime-globals.toml', 'scripts/runtime_isa.py'):
            self.assertEqual(self.context.before[name], hashlib.sha256((ROOT/name).read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
