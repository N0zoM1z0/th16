#!/usr/bin/env python3
"""Exercise complete compound dispatch graphs without changing artifacts."""
import copy
import hashlib
import struct
import tomllib
import unittest

import capstone

from strict_oracle import Context, Incomplete, ROOT
from switch_ownership import (compound_data_parts, inspect_dispatch, inspect_switch,
                              switch_owner_size, validate_compound_record, validate_switch_owner)


class ImageOverlay:
    def __init__(self,image,changes=None,removed=(),added=()):
        self.image=image
        self.changes=changes or {}
        self.removed=set(removed)
        self.added=set(added)

    def __getattr__(self,name):
        return getattr(self.image,name)

    def read_address(self,address,size):
        raw=bytearray(self.image.read_address(address,size))
        for at,value in self.changes.items():
            if address<=at<address+size:
                raw[at-address]=value
        return bytes(raw)

    def base_relocations(self):
        return sorted((set(self.image.base_relocations())-self.removed)|self.added)


class CompoundSwitchControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context=Context()
        cls.units=tomllib.loads((ROOT/'config/match-units.toml').read_text())['units']
        cls.records={a:r for a,r in cls.context.switch_owners.items() if 'dispatches' in r}
        cls.decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
        cls.decoder.detail=True

    def unit(self,address):
        return self.units[f'reference-{address:08x}']

    def mutation(self,address,side,offset,raw):
        context=copy.copy(self.context)
        base=address if side=='target' else self.unit(address)['candidate_address']
        setattr(context,side,ImageOverlay(getattr(context,side),{base+offset+n:b for n,b in enumerate(raw)}))
        return context

    def fixture(self,address):
        """Original-byte structural fixture; supplies no candidate PDB owner."""
        record=self.records[address]
        instructions,_,_=inspect_switch(self.context.target,address,record)
        by={i.address:i for i in instructions}
        relocations={address+p['offset']+n for p in compound_data_parts(record)
                     if p['kind']=='targets' for n in range(0,p['width'],4)}
        for row in record['dispatches']:
            jump=by[address+row['dispatch_offset']]
            relocations.add(jump.address+jump.disp_offset)
            if 'remap_values' in row:
                guard=by[address+row['guard_offset']]
                branch=by[guard.address+guard.size]
                remap=by[branch.address+branch.size]
                relocations.add(remap.address+remap.disp_offset)
        context=copy.copy(self.context)
        context.image=ImageOverlay(context.target,added=relocations)
        unit=dict(target_address=address,candidate_address=address,size=record['size'],compare_size=record['size'])
        return context,unit,record

    def test_all_nine_originals_have_complete_code_and_data(self):
        self.assertEqual(len(self.records),9)
        for address,record in self.records.items():
            with self.subTest(address=hex(address)):
                instructions,dispatches,payload=inspect_switch(self.context.target,address,record)
                self.assertEqual(sum(i.size for i in instructions),record['code_size'])
                self.assertEqual(dispatches,{address+r['dispatch_offset'] for r in record['dispatches']})
                self.assertEqual(len(payload),switch_owner_size(record))
                self.assertEqual(hashlib.sha256(payload).hexdigest(),record['target_sha256'])
                self.assertEqual(int(self.context.boundaries[address]['size']),len(payload))

    def test_real_window_and_renderer_pass_their_whole_owners(self):
        for address,size in [(0x45a450,680),(0x468490,1896)]:
            with self.subTest(address=hex(address)):
                result=self.context.compare(self.unit(address))
                self.assertEqual(result['result'],'exact')
                self.assertEqual(result['compared_size'],size)
                self.assertFalse(result['data_spans'])

    def test_every_target_slot_and_address_operand_requires_its_relocation(self):
        for address in (0x45a450,0x468490):
            unit=self.unit(address);record=self.records[address];base=unit['candidate_address']
            instructions,_,_=inspect_switch(self.context.image,base,record)
            by={i.address:i for i in instructions}
            required={base+p['offset']+n for p in compound_data_parts(record)
                      if p['kind']=='targets' for n in range(0,p['width'],4)}
            for row in record['dispatches']:
                jump=by[base+row['dispatch_offset']];required.add(jump.address+jump.disp_offset)
                if 'remap_values' in row:
                    guard=by[base+row['guard_offset']];branch=by[guard.address+guard.size]
                    remap=by[branch.address+branch.size];required.add(remap.address+remap.disp_offset)
            for at in required:
                context=copy.copy(self.context);context.image=ImageOverlay(context.image,removed=[at])
                with self.subTest(address=hex(address),relocation=hex(at)),self.assertRaisesRegex(Incomplete,'relocation'):
                    context.compare(unit)

    def test_every_raw_mapper_byte_is_required_on_both_sides(self):
        for address in (0x45a450,0x468490):
            record=self.records[address]
            for row in record['dispatches']:
                for n,value in enumerate(row.get('remap_values',[])):
                    for side in ('target','image'):
                        context=self.mutation(address,side,row['remap_offset']+n,bytes([value^1]))
                        with self.subTest(address=hex(address),index=n,side=side),self.assertRaises(Incomplete):
                            context.compare(self.unit(address))

    def test_selector_bytes_are_never_linkage_normalization_fields(self):
        for address in (0x45a450,0x468490):
            result=self.context.compare(self.unit(address))
            fields={b for f in result['linkages'] for b in range(f['offset'],f['offset']+f['width'])}
            for part in compound_data_parts(self.records[address]):
                if part['kind']=='remap':
                    self.assertFalse(fields & set(range(part['offset'],part['offset']+part['width'])))

    def test_cross_register_remap_is_explicit_and_keeps_the_bounded_input(self):
        address=0x43ce10;record=self.records[address]
        instructions,_,payload=inspect_switch(self.context.target,address,record)
        row=record['dispatches'][1]
        with self.assertRaisesRegex(ValueError,'bounded byte index'):
            inspect_dispatch(payload,address,row,instructions)
        inspect_dispatch(payload,address,row,instructions,same_remap_register=False)
        # Change the input base from ECX to EAX while leaving the ECX bound.
        image=ImageOverlay(self.context.target,{0x43cea5:0x80})
        with self.assertRaisesRegex(ValueError,'bounded byte index'):
            inspect_switch(image,address,record)

    def test_wide_313_byte_bound_is_complete_and_structurally_valid(self):
        context,unit,record=self.fixture(0x45f980)
        self.assertEqual(len(record['dispatches'][1]['remap_values']),313)
        validate_switch_owner(context,unit,record)
        instructions,_,_=inspect_switch(context.target,unit['target_address'],record)
        guard=next(i for i in instructions if i.address==0x45f980+record['dispatches'][1]['guard_offset'])
        context=copy.copy(context)
        context.target=ImageOverlay(context.target,{guard.address+guard.imm_offset:0x37})
        with self.assertRaisesRegex(ValueError,'unsigned index bound'):
            validate_switch_owner(context,unit,record)

    def test_each_guard_requires_an_unsigned_branch(self):
        address=0x45a450;record=self.records[address]
        for side in ('target','image'):
            base=address if side=='target' else self.unit(address)['candidate_address']
            image=getattr(self.context,side)
            instructions,_,_=inspect_switch(image,base,record);by={i.address:i for i in instructions}
            for row in record['dispatches']:
                guard=by[base+row['guard_offset']];branch=by[guard.address+guard.size]
                opcode_offset=1 if branch.bytes[0]==0x0f else 0
                value=0x8f if opcode_offset else 0x7f
                context=self.mutation(address,side,branch.address-base+opcode_offset,bytes([value]))
                with self.assertRaisesRegex(Incomplete,'unsigned default branch'):
                    context.compare(self.unit(address))

    def test_sites_must_be_instruction_starts_and_adjacent(self):
        address=0x45a450
        for key in ('guard_offset','dispatch_offset'):
            record=copy.deepcopy(self.records[address]);record['dispatches'][0][key]+=1
            with self.subTest(key=key),self.assertRaises(ValueError):
                inspect_switch(self.context.target,address,record)

    def test_a_table_cannot_bypass_another_dispatch_guard(self):
        address=0x45a450;record=copy.deepcopy(self.records[address])
        instructions,_,_=inspect_switch(self.context.target,address,record)
        guard=next(i for i in instructions if i.address==address+record['dispatches'][1]['guard_offset'])
        target=guard.address+guard.size
        row=record['dispatches'][0];row['case_offsets'][0]=target-address
        changes={address+row['table_offset']+n:b for n,b in enumerate(struct.pack('<I',target))}
        with self.assertRaisesRegex(ValueError,'another dispatch guard'):
            inspect_switch(ImageOverlay(self.context.target,changes),address,record)

    def test_direct_incoming_edges_cannot_bypass_a_guard(self):
        address=0x45a450;record=self.records[address]
        image=ImageOverlay(self.context.target,{address:0xeb,address+1:0x21})
        with self.assertRaisesRegex(ValueError,'unguarded incoming edge'):
            inspect_switch(image,address,record)

    def test_target_slots_cannot_enter_interiors_or_data(self):
        address=0x45a450
        for target_offset in (0x39,612,632,680):
            record=copy.deepcopy(self.records[address]);row=record['dispatches'][0]
            row['case_offsets'][0]=target_offset
            changes={address+row['table_offset']+n:b for n,b in enumerate(struct.pack('<I',address+target_offset))}
            with self.subTest(target=target_offset),self.assertRaises(ValueError):
                inspect_switch(ImageOverlay(self.context.target,changes),address,record)

    def test_additional_indirect_jumps_are_not_implicitly_traversed(self):
        address=0x45a450;record=self.records[address]
        raw=b'\xff\x24\x85'+struct.pack('<I',address+record['dispatches'][0]['table_offset'])
        image=ImageOverlay(self.context.target,{address+n:b for n,b in enumerate(raw)})
        with self.assertRaisesRegex(ValueError,'unreviewed indirect jump'):
            inspect_switch(image,address,record)

    def test_layout_rejects_partial_overlapping_or_unowned_parts(self):
        address=0x45a450
        mutations=[('size',679),('size',681),('code_size',608),('code_size',610)]
        for key,value in mutations:
            record=copy.deepcopy(self.records[address]);record[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):
                inspect_switch(self.context.target,address,record)
        for key,value in [('table_offset',613),('table_offset',608),('remap_offset',631),('remap_offset',636)]:
            record=copy.deepcopy(self.records[address]);record['dispatches'][0][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):
                inspect_switch(self.context.target,address,record)

    def test_profile_and_every_nested_component_are_required(self):
        for change in ('profile','missing','unknown','one','duplicate'):
            record=copy.deepcopy(self.records[0x45a450])
            if change=='profile':record['profile']='generic-indirect'
            elif change=='missing':del record['dispatches'][0]['remap_offset']
            elif change=='unknown':record['dispatches'][0]['mask']=True
            elif change=='one':record['dispatches'].pop()
            else:record['dispatches'][1]=copy.deepcopy(record['dispatches'][0])
            with self.subTest(change=change),self.assertRaises(ValueError):
                validate_compound_record(record)

    def test_raw_alignment_bytes_remain_compared(self):
        context=self.mutation(0x45a450,'image',609,b'\x90\x90\x90')
        result=context.compare(self.unit(0x45a450))
        self.assertEqual(result['result'],'mismatch')
        self.assertEqual(result['compared_size'],680)
        self.assertEqual(result['matched_bytes'],677)

    def test_extra_or_crossing_data_relocations_are_rejected(self):
        address=0x45a450;unit=self.unit(address)
        for offset in (608,609,613,632,655,679):
            context=copy.copy(self.context)
            context.image=ImageOverlay(context.image,added=[unit['candidate_address']+offset])
            with self.subTest(offset=offset),self.assertRaisesRegex(Incomplete,'entry relocations'):
                context.compare(unit)

    def test_whole_original_hash_is_required(self):
        record=dict(self.records[0x45a450],target_sha256='0'*64)
        with self.assertRaisesRegex(ValueError,'extent hash mismatch'):
            validate_switch_owner(self.context,self.unit(0x45a450),record)
        context=self.mutation(0x45a450,'target',0,b'\x57')
        with self.assertRaisesRegex(Incomplete,'extent hash mismatch'):
            context.compare(self.unit(0x45a450))

    def test_primary_extents_cannot_omit_code_maps_or_final_slots(self):
        for size in (609,612,632,656,676,679,681):
            unit=dict(self.unit(0x45a450),size=size,compare_size=size)
            with self.subTest(size=size),self.assertRaises(Incomplete):
                self.context.compare(unit)

    def test_different_real_candidate_extents_remain_refused(self):
        annotations=[line.split() for line in (self.context.directory/'functions.txt').read_text().splitlines()]
        count=0
        for address,record in self.records.items():
            _,candidate,symbol=next(row for row in annotations if int(row[0],0)==address)
            function=next(f for f in self.context.linked['functions'] if f['symbol']==symbol and int(f['address'],0)==int(candidate,0))
            if function['size']==record['size']:continue
            source=self.context.boundaries[address]['source_file']
            unit=dict(artifact_kind='linked-pe',source=source,object=source.rsplit('/',1)[1].replace('.cpp','.obj'),
                      symbol=symbol,candidate_address=int(candidate,0),target_address=address,size=function['size'],
                      compare_size=function['size'],profile=self.context.receipt['compiler_profile'],
                      link_profile=self.context.receipt['linker_profile'],linkages=[])
            with self.subTest(address=hex(address)),self.assertRaisesRegex(Incomplete,'complete candidate owner'):
                self.context.compare(unit)
            count+=1
        self.assertEqual(count,5)

    def test_memory_reload_and_interposed_store_shapes_remain_unreviewed(self):
        self.assertNotIn(0x408650,self.context.switch_owners)
        self.assertNotIn(0x41dcb0,self.context.switch_owners)

    @classmethod
    def tearDownClass(cls):
        cls.context.finish()


if __name__=='__main__':
    unittest.main()
