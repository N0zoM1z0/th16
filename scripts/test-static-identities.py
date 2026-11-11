#!/usr/bin/env python3
"""Reject partial, foreign or ambiguous private-function ownership and edges."""
import copy
import hashlib
import json
import struct
import tempfile
from pathlib import Path
import tomllib
import unittest
from unittest.mock import patch

import capstone

import static_identity as static
from strict_oracle import Context, Incomplete, ROOT
from linked_image import map_statics, pdb_section_contributions


class StaticIdentityControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        cls.path = ROOT / 'config/static-functions.toml'
        cls.records = tomllib.loads(cls.path.read_text())
        cls.statics = map_statics(cls.context.directory / 'th16.map')
        cls.pdb = pdb_section_contributions(cls.context.directory / 'th16.pdb')
        decoder = capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
        decoder.detail = True
        cls.dispatch_instructions = {}
        for name,row in cls.records['functions'].items():
            if 'witness_dispatch' in row:
                parent = row['witness_parent']
                raw = cls.context.target.read_address(parent,int(cls.context.boundaries[parent]['size']))
                cls.dispatch_instructions[name] = {i.address:i for i in decoder.disasm(raw,parent)}

    def review(self, records=None, context=None):
        if records is None:
            return static.review_functions(context or self.context,self.path)
        lines = []
        for name,row in records['functions'].items():
            lines.append('[functions.'+name+']')
            for k,v in row.items():
                if not isinstance(v,dict):
                    lines.append(k+' = '+json.dumps(v))
            for k,v in row.items():
                if isinstance(v,dict):
                    lines.append('[functions.'+name+'.'+k+']')
                    lines.extend(key+' = '+json.dumps(value) for key,value in v.items())
        with tempfile.TemporaryDirectory(dir=ROOT / '.analysis') as d:
            p = Path(d)/'proof.toml'
            p.write_text('\n'.join(lines))
            return static.review_functions(context or self.context,p)

    def mutated(self, key, value):
        records = copy.deepcopy(self.records)
        records['functions']['laser'][key] = value
        with self.assertRaises(static.StaticEvidenceError):
            self.review(records)

    def unit(self, name):
        p = self.context.static_functions[name]
        return dict(artifact_kind='linked-pe',source=p['source'],symbol=p['symbol'],
            object=Path(p['source']).stem+'.obj',candidate_address=p['candidate'],
            target_address=p['target'],size=p['size'],compare_size=p['size'],
            profile=self.context.receipt['compiler_profile'],link_profile=self.context.receipt['linker_profile'],
            linkages=[],reviewed_static=name)

    def caller(self):
        symbol = '?get_point@LaserLineInf@@UAEXMPAUD3DXVECTOR3@@@Z'
        f = next(f for f in self.context.linked['functions'] if f['symbol']==symbol)
        p = self.context.static_functions['laser']
        return dict(artifact_kind='linked-pe',source='src/Laser.cpp',symbol=symbol,object='Laser.obj',
            candidate_address=int(f['address'],0),target_address=0x431050,size=84,compare_size=84,
            profile=self.context.receipt['compiler_profile'],link_profile=self.context.receipt['linker_profile'],
            linkages=[dict(offset=33,width=4,type='REL32',symbol=p['symbol'],target=p['target'],addend=0,reviewed_static='laser')])

    def test_complete_owners_and_caller_pass(self):
        self.assertEqual(set(self.review()),set(self.records['functions']))
        for name in self.context.static_functions:
            self.assertEqual(self.context.compare(self.unit(name))['result'],'exact')
        self.assertEqual(self.context.compare(self.caller())['result'],'exact')

    def test_wrong_profile(self):
        self.mutated('profile','generic-static')

    def test_both_partial_and_expanded_extents(self):
        for size in (31,33):
            self.mutated('size',size)

    def test_wrong_original_hash(self):
        self.mutated('sha256','0'*64)

    def test_inventory_source_is_pinned(self):
        context = copy.copy(self.context)
        context.boundaries = copy.deepcopy(self.context.boundaries)
        context.boundaries[0x43ad00]['source_file'] = 'src/BulletManager.cpp'
        with self.assertRaises(static.StaticEvidenceError):
            self.review(context=context)

    def test_identical_other_original_is_not_the_same_entry(self):
        self.mutated('target',0x417510)

    def test_source_qualification(self):
        self.mutated('source','src/BulletManager.cpp')

    def test_source_paths_cannot_escape_or_alias_the_producer(self):
        for source in ('/src/Laser.cpp','src/../src/Laser.cpp','src//Laser.cpp',
                       'src\\Laser.cpp','probes/reference-support/Laser.cpp','src/C:/Laser.cpp'):
            self.mutated('source',source)

    def test_wrong_private_name(self):
        self.mutated('symbol','?bullet_sincosmul@@YIXPAUD3DXVECTOR3@@MM@Z')

    def test_wrong_parent_hash(self):
        self.mutated('parent_sha256','0'*64)

    def test_instruction_interior_and_other_witness(self):
        for witness in (0x431071,0x431075):
            self.mutated('witness',witness)

    def test_duplicate_private_record(self):
        r = copy.deepcopy(self.records)
        r['functions']['foreign'] = r['functions']['laser'].copy()
        with self.assertRaises(static.StaticEvidenceError):
            self.review(r)

    def test_every_candidate_and_original_byte_is_required(self):
        for which in ('image','target'):
            context = copy.copy(self.context)
            original = getattr(context,which)
            base = self.context.static_functions['laser']['candidate' if which=='image' else 'target']
            for offset in range(32):
                class Overlay:
                    def __getattr__(self,key):
                        return getattr(original,key)
                    def read_address(self,a,size):
                        raw = bytearray(original.read_address(a,size))
                        if a <= base+offset < a+size:
                            raw[base+offset-a] ^= 1
                        return bytes(raw)
                setattr(context,which,Overlay())
                with self.subTest(which=which,offset=offset),self.assertRaises(static.StaticEvidenceError):
                    self.review(context=context)

    def test_private_map_duplicate_and_public_collision(self):
        selected = next(r for r in self.statics if r['symbol']==self.records['functions']['laser']['symbol'])
        with patch.object(static,'map_statics',return_value=self.statics+[selected.copy()]):
            with self.assertRaises(static.StaticEvidenceError):
                self.review()
        context = copy.copy(self.context)
        context.publics = self.context.publics+[selected.copy()]
        with self.assertRaises(static.StaticEvidenceError):
            self.review(context=context)

    def test_interior_private_name_is_rejected(self):
        selected = next(r for r in self.statics if r['symbol']==self.records['functions']['laser']['symbol'])
        interior = dict(selected,symbol='unreviewed-interior',section_offset=selected['section_offset']+1,address=selected['address']+1)
        with patch.object(static,'map_statics',return_value=self.statics+[interior]):
            with self.assertRaises(static.StaticEvidenceError):
                self.review()

    def test_pdb_extent_and_foreign_producer(self):
        selected = self.context.static_functions['laser']['function']
        for change in ('extent','producer'):
            pdb = copy.deepcopy(self.pdb)
            module = selected['pdb_module_index']
            if change=='extent':
                row = next(r for r in pdb['contributions'] if r['module_index']==module and r['size']==32
                           and r['section_offset']+0x401000==self.context.static_functions['laser']['candidate'])
                row['size'] -= 1
            else:
                for r in pdb['contributions']:
                    if r['module_index']==module:
                        r['object']='Z:/foreign/Laser.obj'
            with patch.object(static,'pdb_section_contributions',return_value=pdb):
                with self.assertRaises(static.StaticEvidenceError):
                    self.review()

    def test_primary_owner_cannot_change_id_target_or_size(self):
        for k,v in [('reviewed_static','bullet'),('target_address',0x417510),('size',31),('candidate_address',0x4420e1)]:
            u = self.unit('laser')
            u[k] = v
            with self.assertRaises(Incomplete):
                self.context.compare(u)

    def test_private_owner_is_not_promoted_to_a_public(self):
        for name,proof in self.context.static_functions.items():
            self.assertFalse(any(p['symbol']==proof['symbol'] for p in self.context.publics))
            u = self.unit(name)
            del u['reviewed_static']
            with self.assertRaises(Incomplete):
                self.context.compare(u)

    def test_extra_and_crossing_relocations_are_rejected(self):
        original = self.context.image
        base = self.context.static_functions['laser']['candidate']
        for location in (base-1,base,base+31):
            class Overlay:
                def __getattr__(self,key):
                    return getattr(original,key)
                def base_relocations(self):
                    return sorted(original.base_relocations()+[location])
            context = copy.copy(self.context)
            context.image = Overlay()
            with self.assertRaises(static.StaticEvidenceError):
                self.review(context=context)

    def test_caller_requires_explicit_matching_full_entry(self):
        for k,v in [('reviewed_static','bullet'),('target',0x43ad01),('addend',1),('local',True),('width',2)]:
            u = self.caller()
            u['linkages'][0][k] = v
            with self.assertRaises((Incomplete,ValueError)):
                self.context.compare(u)
        u = self.caller()
        del u['linkages'][0]['reviewed_static']
        with self.assertRaises(Incomplete):
            self.context.compare(u)

    def test_tail_jump_cannot_claim_a_reviewed_call(self):
        u = self.caller()
        original = self.context.image
        site = u['candidate_address']+32
        class Overlay:
            def __getattr__(self,key):
                return getattr(original,key)
            def read_address(self,a,size):
                raw = bytearray(original.read_address(a,size))
                if a <= site < a+size:
                    raw[site-a] = 0xe9
                return bytes(raw)
        context = copy.copy(self.context)
        context.image = Overlay()
        with self.assertRaisesRegex(Incomplete,'direct CALL'):
            context.compare(u)

    def dispatch_context(self, mutations):
        context = copy.copy(self.context)
        original = context.target
        class Overlay:
            def __getattr__(self,key):
                return getattr(original,key)
            def read_address(self,a,size):
                raw = bytearray(original.read_address(a,size))
                for at,value in mutations.items():
                    if a <= at < a+size:
                        raw[at-a] = value
                return bytes(raw)
        context.target = Overlay()
        return context

    def check_dispatch(self, spec=None, mutations=None, name='anm'):
        context = self.dispatch_context(mutations or {})
        row = self.records['functions'][name]
        parent = row['witness_parent']
        size = int(context.boundaries[parent]['size'])
        by = self.dispatch_instructions[name]
        if any(parent <= a < parent+size for a in (mutations or {})):
            decoder = capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
            decoder.detail = True
            by = {i.address:i for i in decoder.disasm(context.target.read_address(parent,size),parent)}
        return static.witness_dispatch(context,spec or row['witness_dispatch'],by)

    def test_bounded_dispatch_proves_the_annotated_call_path(self):
        p = self.context.static_functions['anm']
        self.assertIn(0x46331c,p['witness_path'])
        self.assertIn(0x46332c,p['witness_path'])
        self.assertIn(0x463333,p['witness_path'])
        self.assertEqual(len(self.check_dispatch()['mapper']),17)
        self.assertEqual(len(self.check_dispatch()['targets']),4)
        xy = self.context.static_functions['anm_xy']
        self.assertIn(0x45fbe3,xy['witness_path'])
        self.assertIn(0x45fbf5,xy['witness_path'])
        self.assertEqual(len(self.check_dispatch(name='anm_xy')['mapper']),215)
        self.assertEqual(len(self.check_dispatch(name='anm_xy')['targets']),53)

    def test_dispatch_cannot_be_omitted_or_replaced_by_generic_edges(self):
        records = copy.deepcopy(self.records)
        del records['functions']['anm']['witness_dispatch']
        with self.assertRaisesRegex(static.StaticEvidenceError,'entry path'):
            self.review(records)
        spec = copy.deepcopy(self.records['functions']['anm']['witness_dispatch'])
        spec['profile'] = 'arbitrary-indirect-jump'
        with self.assertRaises(static.StaticEvidenceError):
            self.check_dispatch(spec)

    def test_dispatch_requires_exact_complete_table_counts(self):
        for key,values in [('map_count',(16,18)),('targets_count',(3,5))]:
            for value in values:
                spec = copy.deepcopy(self.records['functions']['anm']['witness_dispatch'])
                spec[key] = value
                with self.assertRaises(static.StaticEvidenceError):
                    self.check_dispatch(spec)

    def test_every_mapper_and_target_byte_is_retained(self):
        for name,start,size in [('anm',0x463b14,17),('anm',0x463b04,16),
                               ('anm_xy',0x462d8c,215),('anm_xy',0x462cb8,212)]:
            for offset in range(size):
                at = start+offset
                before = self.context.target.read_address(at,1)[0]
                with self.subTest(address=hex(at)),self.assertRaises(static.StaticEvidenceError):
                    self.check_dispatch(mutations={at:before^1},name=name)

    def test_dispatch_requires_unsigned_guard_and_consistent_index(self):
        for mutations in ({0x463320:0x8f},{0x463327:0x81},{0x46332e:0x8d}):
            with self.assertRaises(static.StaticEvidenceError):
                self.check_dispatch(mutations=mutations)

    def test_dispatch_sites_must_be_adjacent_instruction_starts(self):
        for key,value in [('guard',0x46331d),('remap',0x46332c),('dispatch',0x46332d)]:
            spec = copy.deepcopy(self.records['functions']['anm']['witness_dispatch'])
            spec[key] = value
            with self.assertRaises(static.StaticEvidenceError):
                self.check_dispatch(spec)

    def test_dispatch_cannot_target_an_interior_or_bypass_its_guard(self):
        for target in (0x463334,0x46331f):
            spec = copy.deepcopy(self.records['functions']['anm']['witness_dispatch'])
            replacement = struct.pack('<I',target)
            mutations = {0x463b04+i:b for i,b in enumerate(replacement)}
            context = self.dispatch_context(mutations)
            spec['targets_sha256'] = hashlib.sha256(context.target.read_address(0x463b04,16)).hexdigest()
            with self.assertRaises(static.StaticEvidenceError):
                self.check_dispatch(spec,mutations)

    def test_unmapped_destination_does_not_establish_reachability(self):
        context = self.dispatch_context({0x463b14:3})
        records = copy.deepcopy(self.records)
        records['functions']['anm']['witness_dispatch']['map_sha256'] = hashlib.sha256(
            context.target.read_address(0x463b14,17)).hexdigest()
        proof = self.check_dispatch(records['functions']['anm']['witness_dispatch'],{0x463b14:3})
        self.assertNotIn(0x463333,proof['mapped_targets'])
        with self.assertRaisesRegex(static.StaticEvidenceError,'entry path'):
            self.review(records,context)

    def test_xy_profile_requires_every_original_and_candidate_byte(self):
        for which in ('image','target'):
            context = copy.copy(self.context)
            original = getattr(context,which)
            base = self.context.static_functions['anm_xy']['candidate' if which=='image' else 'target']
            for offset in range(39):
                class Overlay:
                    def __getattr__(self,key):
                        return getattr(original,key)
                    def read_address(self,a,size):
                        raw = bytearray(original.read_address(a,size))
                        if a <= base+offset < a+size:
                            raw[base+offset-a] ^= 1
                        return bytes(raw)
                setattr(context,which,Overlay())
                with self.subTest(which=which,offset=offset),self.assertRaises(static.StaticEvidenceError):
                    self.review(context=context)

    def test_xy_profile_cannot_change_extent_or_use_the_vector_abi(self):
        for key,value in [('size',38),('size',40),('profile','x87-sincos-scale-v1')]:
            records = copy.deepcopy(self.records)
            records['functions']['anm_xy'][key] = value
            with self.assertRaises(static.StaticEvidenceError):
                self.review(records)


if __name__=='__main__':
    unittest.main()
