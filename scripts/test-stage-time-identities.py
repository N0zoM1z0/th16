#!/usr/bin/env python3
"""Mutate complete stage/time identities without editing linked artifacts."""
import copy
import csv
import hashlib
from pathlib import Path
import struct
import tempfile
import tomllib
import unittest
from unittest.mock import patch

from strict_oracle import (Context, Incomplete, ROOT, review_stage_table,
                           reviewed_linkages, pdb_section_contributions)


class ImageOverlay:
    def __init__(self, image, changes=None, removed=(), added=()):
        self.image = image
        self.changes = changes or {}
        self.removed, self.added = set(removed), set(added)

    def __getattr__(self, name):
        return getattr(self.image, name)

    def read_address(self, address, size):
        data = bytearray(self.image.read_address(address, size))
        for at, value in self.changes.items():
            if address <= at < address + size:
                data[at - address] = value
        return bytes(data)

    def base_relocations(self):
        return sorted((set(self.image.base_relocations()) - self.removed) | self.added)


class StageTimeControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        with (ROOT / 'config/linkage-bindings.csv').open() as stream:
            rows = list(csv.DictReader(stream))
        cls.rows = [r for r in rows if r['kind'] == 'stage-table-v1' or r['symbol'] == '__time64']
        cls.table = next(r for r in cls.rows if r['kind'] == 'stage-table-v1')
        cls.runtime = next(r for r in cls.rows if r['symbol'] == '__time64')
        cls.candidate = next(p['address'] for p in cls.context.publics if p['symbol'] == cls.table['symbol'])
        cls.target = int(cls.table['target_address'], 0)
        cls.pointer_offsets = {n * 212 + i for n in range(8) for i in range(4, 40, 4)}

    def review(self, context=None, rows=None):
        with tempfile.TemporaryDirectory(dir=ROOT / '.analysis') as directory:
            path = Path(directory) / 'bindings.csv'
            with path.open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=self.table)
                writer.writeheader()
                writer.writerows(self.rows if rows is None else rows)
            return reviewed_linkages(context or self.context, path)

    def mutation(self, side, address, raw):
        context = copy.copy(self.context)
        setattr(context, side, ImageOverlay(getattr(context, side),
                {address + n: value for n, value in enumerate(raw)}))
        return context

    def test_complete_fixed_bindings_pass(self):
        result = self.review()
        self.assertEqual(result[self.table['symbol']]['target'], 0x4a22d0)
        self.assertEqual(result['__time64']['target'], 0x47a09e)

    def test_table_extent_cannot_be_shortened_or_expanded(self):
        for size in (212, 1692, 1695, 1697, 1700):
            row = dict(self.table, size=str(size))
            with self.subTest(size=size), self.assertRaises(Incomplete):
                review_stage_table(self.context, row, self.candidate)

    def test_profile_is_specific_to_the_stage_table_symbol(self):
        row = dict(self.table, symbol='?unreviewed_table@@3PAUStageData@@A')
        with self.assertRaisesRegex(Incomplete, 'explicit complete profile'):
            review_stage_table(self.context, row, self.candidate)

    def test_unrelated_profile_fields_are_refused(self):
        for key, value in [('candidate_library', 'libucrt.lib'), ('candidate_size', '1696'),
                           ('witness_mnemonic', 'add')]:
            with self.subTest(key=key), self.assertRaises(Incomplete):
                review_stage_table(self.context, dict(self.table, **{key: value}), self.candidate)

    def test_typed_owner_must_be_unique_and_complete(self):
        for change in ('missing', 'duplicate', 'size', 'address'):
            context = copy.copy(self.context)
            context.typed_globals = copy.deepcopy(context.typed_globals)
            owner = next(g for g in context.typed_globals if g['name'] == 'g_stage_table')
            if change == 'missing': context.typed_globals.remove(owner)
            elif change == 'duplicate': context.typed_globals.append(dict(owner))
            elif change == 'size': owner['size'] -= 4
            else: owner['address'] += 4
            with self.subTest(change=change), self.assertRaisesRegex(Incomplete, 'typed PDB owner'):
                review_stage_table(context, self.table, self.candidate)

    def test_table_contribution_must_be_unique_and_complete(self):
        for sizes in ([], [1692], [1700], [1696, 1696]):
            context = copy.copy(self.context)
            context.data_contributions = dict(context.data_contributions)
            context.data_contributions[self.candidate] = sizes
            with self.subTest(sizes=sizes), self.assertRaisesRegex(Incomplete, 'typed PDB owner'):
                review_stage_table(context, self.table, self.candidate)

    def test_table_requires_its_actual_source_object(self):
        contributions = copy.deepcopy(pdb_section_contributions(self.context.directory / 'th16.pdb'))
        owner = next(r for r in contributions['contributions']
                     if r['section_number'] == 3 and r['section_offset'] == 0)
        owner['object'] = owner['object'].replace('Opaque.obj', 'Other.obj')
        with patch('strict_oracle.pdb_section_contributions', return_value=contributions):
            with self.assertRaisesRegex(Incomplete, 'declared PDB source owner'):
                review_stage_table(self.context, self.table, self.candidate)

    def test_every_scalar_dword_is_required_on_both_sides(self):
        for offset in set(range(0, 1696, 4)) - self.pointer_offsets:
            for side, base in [('image', self.candidate), ('target', self.target)]:
                value = getattr(self.context, side).read_address(base + offset, 1)[0] ^ 1
                context = self.mutation(side, base + offset, bytes([value]))
                with self.subTest(offset=offset, side=side), self.assertRaisesRegex(Incomplete, 'scalar field'):
                    review_stage_table(context, self.table, self.candidate)

    def test_every_pointer_slot_requires_its_relocation(self):
        for offset in self.pointer_offsets:
            context = copy.copy(self.context)
            context.image = ImageOverlay(context.image, removed=[self.candidate + offset])
            with self.subTest(offset=offset), self.assertRaisesRegex(Incomplete, 'pointer relocations'):
                review_stage_table(context, self.table, self.candidate)

    def test_extra_and_crossing_relocations_are_refused(self):
        for offset in (-3, -1, 0, 5, 40, 1695):
            context = copy.copy(self.context)
            context.image = ImageOverlay(context.image, added=[self.candidate + offset])
            with self.subTest(offset=offset), self.assertRaisesRegex(Incomplete, 'pointer relocations'):
                review_stage_table(context, self.table, self.candidate)

    def test_every_pointer_must_name_a_complete_string(self):
        for offset in self.pointer_offsets:
            pointer = struct.unpack('<I', self.context.image.read_address(self.candidate + offset, 4))[0]
            context = self.mutation('image', self.candidate + offset, struct.pack('<I', pointer + 1))
            with self.subTest(offset=offset), self.assertRaisesRegex(Incomplete, 'original PDB payload'):
                review_stage_table(context, self.table, self.candidate)

    def test_every_candidate_string_byte_and_terminator_is_required(self):
        visited = set()
        for offset in self.pointer_offsets:
            pointer = struct.unpack('<I', self.context.image.read_address(self.candidate + offset, 4))[0]
            data = self.context.image.read_address(pointer, 64)
            for n, value in enumerate(data[:data.index(0) + 1]):
                if pointer + n in visited: continue
                visited.add(pointer + n)
                context = self.mutation('image', pointer + n, bytes([value ^ 1]))
                with self.subTest(address=hex(pointer + n)), self.assertRaisesRegex(Incomplete, 'original PDB payload'):
                    review_stage_table(context, self.table, self.candidate)

    def test_string_contributions_cannot_be_partial_or_ambiguous(self):
        pointer = struct.unpack('<I', self.context.image.read_address(self.candidate + 4, 4))[0]
        for sizes in ([], [8], [9, 9]):
            context = copy.copy(self.context)
            context.data_contributions = dict(context.data_contributions)
            context.data_contributions[pointer] = sizes
            with self.subTest(sizes=sizes), self.assertRaisesRegex(Incomplete, 'original PDB payload'):
                review_stage_table(context, self.table, self.candidate)

    def test_strings_cannot_be_redirected_into_writable_storage(self):
        context = self.mutation('image', self.candidate + 4, struct.pack('<I', self.candidate))
        with self.assertRaisesRegex(Incomplete, 'data storage'):
            review_stage_table(context, self.table, self.candidate)

    def test_index_witness_must_be_a_complete_instruction(self):
        for address in (0x43cfd4, 0x43cfd9, 0x43cfde):
            with self.subTest(address=hex(address)), self.assertRaises(Incomplete):
                review_stage_table(self.context, dict(self.table, witness_instruction=hex(address)), self.candidate)

    def test_index_witness_requires_the_real_row_stride(self):
        context = self.mutation('target', 0x43cfd5, b'\xd0')
        with self.assertRaisesRegex(Incomplete, 'stride witness'):
            review_stage_table(context, self.table, self.candidate)

    def test_whole_original_table_hash_is_required(self):
        context = self.mutation('target', self.target + 1695, b'\x01')
        with self.assertRaisesRegex(Incomplete, 'hash mismatch'):
            self.review(context)
        with self.assertRaisesRegex(Incomplete, 'hash mismatch'):
            self.review(rows=[dict(self.table, target_sha256='0' * 64)])

    def test_time_entry_requires_both_complete_extents(self):
        for key in ('size', 'candidate_size'):
            row = dict(self.runtime, **{key: '65'})
            if key == 'size':
                row['target_sha256'] = hashlib.sha256(self.context.target.read_address(0x47a09e, 65)).hexdigest()
            with self.subTest(key=key), self.assertRaisesRegex(Incomplete, 'complete function extents'):
                self.review(rows=[row])

    def test_time_entry_requires_the_pinned_ucrt_owner(self):
        with self.assertRaisesRegex(Incomplete, 'pinned Microsoft library'):
            self.review(rows=[dict(self.runtime, candidate_library='LIBCMT.lib')])

    def test_stage_consumers_replay_their_complete_owners(self):
        units = tomllib.loads((ROOT / 'config/match-units.toml').read_text())['units']
        for address, size in [(0x42e150, 896), (0x43ce10, 815)]:
            result = self.context.compare(units[f'reference-{address:08x}'])
            self.assertEqual(result['result'], 'exact')
            self.assertEqual(result['compared_size'], size)

    @classmethod
    def tearDownClass(cls):
        cls.context.finish()


if __name__ == '__main__':
    unittest.main()
