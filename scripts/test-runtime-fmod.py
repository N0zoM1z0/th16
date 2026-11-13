#!/usr/bin/env python3
"""Static refusals for the complete pinned x87 fmod entry family."""
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
from runtime_fmod import PARTS, FIELDS, review_fmod
from runtime_identity import RuntimeEvidenceError, validate_runtime_field
from strict_oracle import Context, Incomplete, ROOT, reviewed_linkages


class ImagePatch:
    def __init__(self,image,address=None,relocations=None):
        self.image,self.address,self.relocations=image,address,relocations

    def __getattr__(self,name):
        return getattr(self.image,name)

    def read_address(self,address,size):
        data=bytearray(self.image.read_address(address,size))
        if self.address is not None and address <= self.address < address+size:
            data[self.address-address] ^= 1
        return bytes(data)

    def base_relocations(self):
        return self.image.base_relocations() if self.relocations is None else self.relocations


class FmodControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context=Context()
        cls.row=tomllib.loads((ROOT/'config/runtime-interiors.toml').read_text())['objects']['fmod']
        cls.bindings,cls.evidence=review_fmod(cls.context,cls.row)
        cls.parents=cls.evidence['parents']

    def rejected(self,context=None,row=None):
        with self.assertRaises(RuntimeEvidenceError):
            review_fmod(context or self.context,self.row if row is None else row)

    def test_complete_parent_family_and_only_cifmod_entry_pass(self):
        self.assertEqual(set(self.bindings),{'__CIfmod'})
        b=self.bindings['__CIfmod']
        self.assertEqual((b['target'],b['entry_offset'],b['parent_size']),(0x487aca,10,34))
        self.assertNotIn('size',b)
        self.assertEqual((self.evidence['code_bytes'],self.evidence['data_bytes']),(1179,190))
        self.assertTrue(self.evidence['complete_code_equal'])
        self.assertTrue(self.evidence['complete_data_equal'])
        self.assertEqual(self.evidence['primary_exact_credit'],0)

    def test_changed_original_code_and_data_are_rejected(self):
        for name,(_,_,size,data_size) in PARTS.items():
            for base,n in [(self.row[name+'_address'],size),(self.row[name+'_data_address'],data_size)]:
                for offset in [0,n//2,n-1]:
                    with self.subTest(name=name,address=hex(base+offset)):
                        c=copy.copy(self.context);c.target=ImagePatch(c.target,base+offset);self.rejected(c)

    def test_every_candidate_fmod_and_descriptor_byte_is_checked(self):
        p=self.parents['fmod']
        for base,size in [(p['candidate'],34),(p['data_candidate'],80)]:
            for offset in range(size):
                with self.subTest(address=hex(base+offset)):
                    c=copy.copy(self.context);c.image=ImagePatch(c.image,base+offset);self.rejected(c)

    def test_complete_dispatcher_code_and_constant_pools_are_checked(self):
        for name in ['dispatch','c_dispatch']:
            p=self.parents[name]
            offsets={0,1,p['size']//2,p['size']-1}|{x for x,_ in FIELDS[name]}
            for base,positions in [(p['candidate'],offsets),(p['data_candidate'],range(p['data_size']))]:
                for offset in positions:
                    with self.subTest(name=name,address=hex(base+offset)):
                        c=copy.copy(self.context);c.image=ImagePatch(c.image,base+offset);self.rejected(c)

    def test_all_pointer_relocations_and_no_extra_relocations_are_required(self):
        original=set(self.context.image.base_relocations())
        required=set()
        extras=set()
        for name,p in self.parents.items():
            required |= {p['candidate']+x for x,t in FIELDS[name] if t=='DIR32'}
            extras |= {p['candidate']-1,p['candidate'],p['data_candidate']-1,p['data_candidate']}
        required |= {self.parents['fmod']['data_candidate']+x for x in range(16,80,4)}
        for at in required|extras:
            with self.subTest(address=hex(at)):
                c=copy.copy(self.context)
                c.image=ImagePatch(c.image,relocations=sorted(original-{at} if at in required else original|{at}))
                self.rejected(c)

    def test_original_relocations_are_not_silently_accepted(self):
        c=copy.copy(self.context)
        c.target=ImagePatch(c.target,relocations=[self.row['fmod_address']+1])
        self.rejected(c)

    def test_unknown_profile_and_fields_and_shifted_original_objects_fail(self):
        for key,value in [('profile','unreviewed'),('entry_offset',20),('fmod_address',self.row['fmod_address']+1),
                          ('dispatch_data_address',self.row['dispatch_data_address']+1)]:
            row=copy.deepcopy(self.row);row[key]=value
            with self.subTest(key=key):self.rejected(row=row)

    def test_each_complete_pdb_owner_extent_and_producer_is_required(self):
        for name,(symbol,_,size,_) in PARTS.items():
            for key,value in [('size',size-1),('size',size+1),('pdb_object','wrong.lib'),('map_object','libucrt:other.obj')]:
                c=copy.copy(self.context);c.linked=copy.deepcopy(c.linked)
                f=next(x for x in c.linked['functions'] if x['symbol']==symbol);f[key]=value
                with self.subTest(name=name,key=key,value=value):self.rejected(c)

    def test_complete_pdb_data_and_code_records_are_required(self):
        original=pdb_section_contributions(self.context.directory/'th16.pdb')
        for name,p in self.parents.items():
            for code in [True,False]:
                data=copy.deepcopy(original)
                record=next(x for x in data['contributions'] if x['module_index']==p['owner']['pdb_module_index']
                            and bool(x['characteristics']&0x20)==code)
                record['size']-=1
                with self.subTest(name=name,code=code),patch('runtime_fmod.pdb_section_contributions',return_value=data):
                    self.rejected()

    def test_fixed_family_public_offsets_are_required(self):
        for name in ['__CIfmod','__trandisp2','__cintrindisp1','__ctrandisp2','__OP_FMODjmptab']:
            c=copy.copy(self.context);c.publics=copy.deepcopy(c.publics)
            next(x for x in c.publics if x['symbol']==name)['address']+=1
            with self.subTest(name=name):self.rejected(c)

    def test_fastflag_requires_its_pinned_complete_typed_zero_storage(self):
        for key,value in [('size',8),('type_index',0x75),('address',0x400000)]:
            c=copy.copy(self.context);c.typed_globals=copy.deepcopy(c.typed_globals)
            next(x for x in c.typed_globals if x['name']=='__fastflag')[key]=value
            with self.subTest(key=key):self.rejected(c)
        c=copy.copy(self.context);c.publics=copy.deepcopy(c.publics)
        next(x for x in c.publics if x['symbol']=='___fastflag')['object']='libucrt:other.obj'
        self.rejected(c)

    def test_both_independent_external_runtime_identities_are_required(self):
        for name in ['___acrt_has_user_matherr','__87except']:
            c=copy.copy(self.context);c.reviewed_linkages=copy.deepcopy(c.reviewed_linkages)
            del c.reviewed_linkages[name]
            with self.subTest(name=name):self.rejected(c)

    def test_full_original_call_witness_and_boundary_are_required(self):
        for key,value in [('witnesses',[]),('witnesses',[0x417c2b]),('witness_parent',0x45f980),
                          ('witness_parent_sha256','0'*64)]:
            row=copy.deepcopy(self.row);row[key]=value
            with self.subTest(key=key):self.rejected(row=row)
        c=copy.copy(self.context);c.boundaries=copy.deepcopy(c.boundaries)
        c.boundaries[0x417bc0]['span_end']='0x00417D60'
        self.rejected(c)

    def test_call_field_cannot_become_an_address_or_an_added_interior_offset(self):
        f=next(x for x in self.context.linked['functions'] if x['symbol']=='?measure_real_time@Spellcard@@SAXXZ')
        field=dict(type='REL32',width=4,target=0x487aca,offset=107)
        reviewed=self.bindings['__CIfmod']
        validate_runtime_field(self.context,f,field,reviewed)
        for key,value in [('type','DIR32'),('width',8),('addend',1),('local',True),('target',0x487ad4),('offset',0)]:
            bad=dict(field);bad[key]=value
            with self.subTest(key=key),self.assertRaises(RuntimeEvidenceError):
                validate_runtime_field(self.context,f,bad,reviewed)

    def test_ordinary_runtime_binding_still_cannot_admit_cifmod_interior(self):
        with (ROOT/'config/linkage-bindings.csv').open() as stream:rows=list(csv.DictReader(stream))
        extra=dict.fromkeys(rows[0],'')
        extra.update(symbol='__CIfmod',target_address='0x487aca',size='10',kind='runtime-function',
                     target_sha256=hashlib.sha256(self.context.target.read_address(0x487aca,10)).hexdigest(),
                     candidate_library='libucrt.lib',candidate_size='34',evidence='docs/knowledge/math-runtime-identities.md')
        with tempfile.TemporaryDirectory(dir=ROOT/'.analysis') as d:
            p=Path(d)/'bindings.csv'
            with p.open('w',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows+[extra])
            with self.assertRaises(Incomplete):reviewed_linkages(self.context,p)

    def clock_unit(self):
        return tomllib.loads((ROOT/'config/match-units.toml').read_text())['units']['reference-00417bc0']

    def test_complete_spellcard_clock_replay_passes(self):
        result=self.context.compare(self.clock_unit())
        self.assertEqual((result['result'],result['compared_size'],result['matched_bytes']),('exact',418,418))

    def test_call_to_either_other_fmod_parent_entry_is_rejected(self):
        unit=self.clock_unit();base=unit['candidate_address'];parent=self.parents['fmod']['candidate']
        for offset in [0,11,20]:
            encoded=struct.pack('<i',parent+offset-(base+111))
            class WrongCall(ImagePatch):
                def read_address(self,address,size):
                    data=bytearray(super().read_address(address,size))
                    for i,value in enumerate(encoded):
                        at=base+107+i
                        if address <= at < address+size:data[at-address]=value
                    return bytes(data)
            c=copy.copy(self.context);c.image=WrongCall(c.image)
            with self.subTest(offset=offset),self.assertRaises(Incomplete):c.compare(unit)

    def test_clock_nonfield_byte_and_shortened_owner_are_not_exact(self):
        unit=self.clock_unit();c=copy.copy(self.context)
        c.image=ImagePatch(c.image,unit['candidate_address'])
        self.assertEqual(c.compare(unit)['result'],'mismatch')
        short=copy.deepcopy(unit);short['size']=short['compare_size']=417
        with self.assertRaises(Incomplete):self.context.compare(short)


if __name__=='__main__':
    unittest.main()
