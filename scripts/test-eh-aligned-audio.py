#!/usr/bin/env python3
"""Refusal controls for the complete aligned audio allocation graphs."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import tomllib
import unittest

import capstone

from eh_identity import EHEvidenceError, handler_field, review_handler, validate_field
from linked_image import map_statics, pdb_section_contributions
from strict_oracle import Context, Incomplete, ROOT

_spec = importlib.util.spec_from_file_location('aggregate_controls', ROOT / 'scripts/test-eh-constructor.py')
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
Overlay = _base.Overlay


class AlignedAudioControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context()
        cls.records = [r for r in tomllib.loads((ROOT/'config/eh-handlers.toml').read_text())['handlers']
                       if r.get('profile') == 'aligned-audio-allocation-v1']
        cls.statics = map_statics(cls.context.directory/'th16.map')
        cls.pdb = pdb_section_contributions(cls.context.directory/'th16.pdb')
        with tempfile.TemporaryDirectory(dir=ROOT/'.analysis') as directory:
            output = Path(directory)/'focused.json'
            run = subprocess.run([sys.executable, str(ROOT/'scripts/audit-reference.py'),
                                  '--address', '0x470320', '--address', '0x470680', '--json', str(output)],
                                 cwd=ROOT, capture_output=True, text=True, timeout=90)
            if run.returncode: raise RuntimeError(run.stderr)
            reports = json.loads(output.read_text())['functions']
        cls.units = {}
        for record, report in zip(cls.records, reports):
            proof = cls.proof(record)
            cls.units[record['parent_target']] = dict(source=record['source'], symbol=record['parent_symbol'],
                artifact_kind='linked-pe', object='DSUtil.obj', candidate_address=proof['parent_candidate'],
                target_address=record['parent_target'], size=record['parent_size'], compare_size=record['parent_size'],
                profile=cls.context.receipt['compiler_profile'], link_profile=cls.context.receipt['linker_profile'],
                linkages=[{k:v for k,v in f.items() if k not in ('candidate_target','encoded')} for f in report['linkages']])

    @classmethod
    def proof(cls, record):
        return cls.context.eh_handlers[(record['source'],record['parent_symbol'])]

    def review(self, record, context=None, statics=None, pdb=None):
        return review_handler(context or self.context, record, self.statics if statics is None else statics,
                              self.pdb if pdb is None else pdb)

    def mutate(self, side, address, payload=None):
        context = copy.copy(self.context)
        image = getattr(context, side)
        if payload is None: payload = bytes([image.read_address(address,1)[0]^1])
        setattr(context, side, Overlay(image, {address+i:b for i,b in enumerate(payload)}))
        return context

    def test_both_complete_graphs_and_primary_owners_pass(self):
        self.assertEqual([r['parent_size'] for r in self.records],[856,809])
        for record in self.records:
            proof = self.review(record)
            self.assertEqual(proof,self.proof(record))
            self.assertEqual((proof['code_owner']['size'],proof['descriptor']['size']),(58,44))
            self.assertEqual(proof['cookie_offsets'],[-136,-8])
            self.assertEqual(proof['handler']['owner_offset'],18)
            self.assertEqual(handler_field(proof)['offset'],25)
            result = self.context.compare(self.units[record['parent_target']])
            self.assertEqual((result['result'],result['compared_size']),('exact',record['parent_size']))

    def test_profile_roles_all_extents_and_extra_keys_are_fixed(self):
        for record in self.records:
            for key,value in [('profile','allocation-cleanup-v1'),('source','src/AnmRender.cpp'),
                              ('parent_symbol',record['parent_symbol']+'x'),('parent_target',record['parent_target']+1),
                              ('parent_size',record['parent_size']-1),('target',record['target']+1),
                              ('code_target',record['code_target']+1),('size',45),('size',57),('size',59),
                              ('func_info_size',43),('func_info_target',record['func_info_target']+4),('eh_flags',5),
                              ('handler_field_offset',6),('cookie_offset',-8),('allocation_size',160)]:
                with self.subTest(key=key,value=value),self.assertRaises(EHEvidenceError):
                    self.review(dict(record,**{key:value}))

    def test_every_candidate_code_and_metadata_byte_is_checked(self):
        for record in self.records:
            proof=self.proof(record)
            for role in ('code_owner','descriptor'):
                owner=proof[role]
                for offset in range(owner['size']):
                    with self.subTest(parent=record['parent_target'],role=role,offset=offset),self.assertRaises(ValueError):
                        self.review(record,self.mutate('image',owner['address']+offset))

    def test_all_original_owner_hashes_are_required(self):
        for record in self.records:
            for key in ('parent_sha256','target_sha256','func_info_sha256'):
                with self.subTest(key=key),self.assertRaisesRegex(EHEvidenceError,'hash'):
                    self.review(dict(record,**{key:'0'*64}))

    def test_original_code_and_metadata_semantics_survive_hash_updates(self):
        for record in self.records:
            for key,address,size in [('target_sha256',record['code_target'],58),
                                     ('func_info_sha256',record['func_info_target'],44)]:
                for offset in range(size):
                    context=self.mutate('target',address+offset)
                    changed=dict(record,**{key:hashlib.sha256(context.target.read_address(address,size)).hexdigest()})
                    with self.subTest(key=key,offset=offset),self.assertRaises(ValueError): self.review(changed,context)

    def test_registration_restoration_and_allocation_lifetime_are_complete(self):
        for record in self.records:
            proof=self.proof(record); size=record['parent_size'];push=size-132
            offsets=list(range(62))+list(range(size-32,size))+list(range(push,push+40))
            for offset in offsets:
                with self.subTest(parent=record['parent_target'],offset=offset),self.assertRaises(ValueError):
                    self.review(record,self.mutate('image',proof['parent_candidate']+offset))

    def test_original_frame_semantics_survive_hash_updates(self):
        for record in self.records:
            size=record['parent_size'];parent=record['parent_target']
            for offset in (7,8,13,20,25,38,41,47,50,53,56,size-130,size-119,size-110,size-106,size-95,size-5,size-1):
                context=self.mutate('target',parent+offset)
                changed=dict(record,parent_sha256=hashlib.sha256(context.target.read_address(parent,size)).hexdigest())
                with self.subTest(offset=offset),self.assertRaises(ValueError): self.review(changed,context)

    def test_both_cookie_checks_have_fixed_separate_slots(self):
        for record in self.records:
            handler=self.proof(record)['handler']['address']
            for offset,payload in [(9,struct.pack('<i',-8)),(22,b'\xf4'),(16,b'\x90'),(26,b'\x90')]:
                with self.subTest(offset=offset),self.assertRaises(EHEvidenceError):
                    self.review(record,self.mutate('image',handler+offset,payload))

    def test_cookie_identity_comes_from_pe_load_config(self):
        for record in self.records:
            image=self.context.image
            location=image.image_base+image.directories[10][0]+60
            with self.assertRaises(EHEvidenceError): self.review(record,self.mutate('image',location))

    def body_instruction(self,record):
        proof=self.proof(record)
        d=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);d.detail=True
        return next(i for i in d.disasm(self.context.image.read_address(proof['parent_candidate'],record['parent_size']),proof['parent_candidate'])
                    if i.mnemonic=='test' and len(i.bytes)==2 and all(o.type==capstone.x86.X86_OP_REG for o in i.operands))

    def test_extra_returns_and_base_register_changes_are_rejected(self):
        for record in self.records:
            i=self.body_instruction(record)
            for payload in (b'\xc3\x90',b'\x8b\xe8',b'\x8b\xd8'):
                with self.subTest(payload=payload),self.assertRaises(ValueError): self.review(record,self.mutate('image',i.address,payload))

    def test_additional_state_or_straddling_frame_access_is_rejected(self):
        for record in self.records:
            parent=self.proof(record)['parent_candidate']
            # Existing three-byte saved-this store becomes a protected or straddling store.
            for displacement in (-4,-8,-12,-16,-20,-21):
                with self.subTest(displacement=displacement),self.assertRaises(EHEvidenceError):
                    self.review(record,self.mutate('image',parent+62,bytes.fromhex('894d')+struct.pack('<b',displacement)))

            # An indexed EBP access can reach protected slots despite its base displacement.
            with self.assertRaisesRegex(EHEvidenceError, 'variable index'):
                self.review(record,self.mutate('image',parent+62,bytes.fromhex('894c45b83900')))

    def test_original_cleanup_boundary_and_metadata_separation_are_required(self):
        for record in self.records:
            for mode in ('short','overlap','metadata'):
                context=copy.copy(self.context);context.boundaries=copy.deepcopy(context.boundaries)
                row=context.boundaries[record['code_target']]
                if mode=='short':row['size']='17'
                else:context.boundaries[record['func_info_target'] if mode=='metadata' else record['code_target']+18]=dict(row,span_end=hex(record['func_info_target'] if mode=='metadata' else record['code_target']+18),size='1')
                with self.subTest(mode=mode),self.assertRaises(EHEvidenceError):self.review(record,context)

    def test_complete_private_pdb_owners_and_same_module_are_required(self):
        for record in self.records:
            proof=self.proof(record)
            for role in ('code_owner','descriptor'):
                owner=proof[role]
                baseline=next(r for r in self.pdb['contributions'] if self.context.image.image_base+self.context.image.section(r['section_number']).rva+r['section_offset']==owner['address'])
                for mode in ('short','long','duplicate','missing','module','object','overlap'):
                    pdb=copy.deepcopy(self.pdb);row=next(r for r in pdb['contributions'] if r==baseline)
                    if mode=='short':row['size']-=1
                    elif mode=='long':row['size']+=1
                    elif mode=='duplicate':pdb['contributions'].append(copy.deepcopy(row))
                    elif mode=='missing':pdb['contributions'].remove(row)
                    elif mode=='module':row['module_index']+=1
                    elif mode=='object':row['object']=str(ROOT/'other.obj')
                    else:pdb['contributions'].append(dict(row,section_offset=row['section_offset']+1,size=1))
                    with self.subTest(role=role,mode=mode),self.assertRaises(EHEvidenceError):self.review(record,pdb=pdb)

    def test_private_names_cannot_be_missing_duplicated_or_from_another_parent(self):
        for record in self.records:
            proof=self.proof(record)
            for name in [*proof['code_owner']['internal_symbols'],*proof['descriptor']['internal_symbols']]:
                for mode in ('missing','duplicate','other','producer','public'):
                    statics=copy.deepcopy(self.statics);context=copy.copy(self.context)
                    row=next(r for r in statics if r['symbol']==name and r['object']=='DSUtil.obj')
                    if mode=='missing':statics.remove(row)
                    elif mode=='duplicate':statics.append(copy.deepcopy(row))
                    elif mode=='other':row['symbol']+='x'
                    elif mode=='producer':row['object']=str(ROOT/'other.obj')
                    else:statics.remove(row);context.publics=context.publics+[row]
                    with self.subTest(name=name,mode=mode),self.assertRaises(EHEvidenceError):self.review(record,context,statics=statics)

    def test_all_runtime_roles_require_their_complete_independent_bindings(self):
        for record in self.records:
            for name in ('??2@YAPAXI@Z','??3@YAXPAXI@Z','@__security_check_cookie@4','___CxxFrameHandler3'):
                for mode in ('missing','kind','size'):
                    context=copy.copy(self.context);context.reviewed_linkages=copy.deepcopy(context.reviewed_linkages)
                    if mode=='missing':del context.reviewed_linkages[name]
                    elif mode=='kind':context.reviewed_linkages[name]['kind']='unreviewed'
                    else:context.reviewed_linkages[name]['size']-=1
                    with self.subTest(name=name,mode=mode),self.assertRaises(EHEvidenceError):self.review(record,context)

    def test_missing_duplicate_extra_and_crossing_relocations_are_rejected(self):
        for record in self.records:
            proof=self.proof(record)
            for base,size,offsets in [(proof['code_owner']['address'],58,[49]),(proof['descriptor']['address'],44,[4,16]),(proof['parent_candidate'],62,[25,41]),(proof['parent_candidate']+record['parent_size']-32,32,[])]:
                for remove,add in [([base+o],[]) for o in offsets]+[([],[base-1]),([],[base+size-1])]+[([],[base+o]) for o in offsets]:
                    context=copy.copy(self.context);context.image=Overlay(context.image,remove=remove,add=add)
                    with self.subTest(base=base,remove=remove,add=add),self.assertRaises(ValueError):self.review(record,context)

    def test_handler_field_is_only_offset_25_in_its_whole_parent(self):
        for record in self.records:
            proof=self.proof(record);unit=self.units[record['parent_target']];field=handler_field(proof)
            validate_field(self.context.eh_handlers,unit,field,proof['handler']['address'])
            for key,value in [('offset',6),('offset',26),('addend',1),('type','REL32'),('target',record['target']+1),('width',8)]:
                with self.subTest(key=key),self.assertRaises(EHEvidenceError):validate_field(self.context.eh_handlers,unit,dict(field,**{key:value}),proof['handler']['address'])
            for key,value in [('size',record['parent_size']-1),('compare_size',record['parent_size']-1),('source','src/AnmRender.cpp'),('candidate_address',unit['candidate_address']+1),('target_address',unit['target_address']+1)]:
                with self.subTest(key=key),self.assertRaises(EHEvidenceError):validate_field(self.context.eh_handlers,dict(unit,**{key:value}),field,proof['handler']['address'])

    def test_foreign_handler_cannot_be_used_by_another_complete_parent(self):
        a,b=self.records
        proof=self.proof(a);unit=self.units[b['parent_target']]
        with self.assertRaises(EHEvidenceError):validate_field(self.context.eh_handlers,unit,handler_field(proof),proof['handler']['address'])

    def test_isa_field_restrictions_are_enforced_in_primary_compare(self):
        for record in self.records:
            for change in (dict(addend=4),dict(type='REL32'),dict(width=8),dict(local=True),dict(storage_size=8)):
                unit=copy.deepcopy(self.units[record['parent_target']])
                field=next(f for f in unit['linkages'] if f.get('symbol')=='___isa_available');field.update(change)
                with self.subTest(change=change),self.assertRaises(Incomplete):self.context.compare(unit)

    def test_unrelated_body_change_still_fails_complete_primary_comparison(self):
        for record in self.records:
            i=self.body_instruction(record)
            # TEST reg,reg -> OR reg,reg keeps the frame graph but changes primary code.
            context=self.mutate('image',i.address,b'\x0b')
            self.assertEqual(self.review(record,context),self.proof(record))
            self.assertEqual(context.compare(self.units[record['parent_target']])['result'],'mismatch')

    def test_new_verifier_is_fingerprinted(self):
        name='scripts/eh_aligned_audio.py'
        self.assertEqual(self.context.before[name],hashlib.sha256((ROOT/name).read_bytes()).hexdigest())


if __name__=='__main__':
    unittest.main()
