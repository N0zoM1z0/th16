"""Closed pinned x87 atan2 identity using the already verified fmod dispatchers."""
import hashlib
from pathlib import Path
import struct

from linked_image import LinkedImageError, linked_code_fields, pdb_section_contributions
from runtime_fmod import unique_public
from runtime_identity import RuntimeEvidenceError, decode_scope, require


def review_atan2(context, row, support):
    require(set(row) == {'profile', 'evidence', 'entry_address', 'entry_sha256',
                        'math_address', 'math_sha256', 'data_address', 'data_sha256',
                        'witness_parent', 'witness_parent_sha256', 'witnesses'}
            and row['profile'] == 'msvc-x86-atan2-v1', 'unreviewed atan2 declaration')
    require(support['profile'] == 'msvc-x86-fmod-v1' and support['complete_code_equal']
            and support['complete_data_equal'], 'atan2 requires the complete verified dispatcher family')
    require(all(type(row[k]) is int for k in ['entry_address', 'math_address', 'data_address', 'witness_parent']),
            'atan2 addresses must be integral')
    root = Path(__file__).resolve().parents[1]
    library = 'Z:' + str(root/'.tools/toolchain/sdk/Program Files/Windows Kits/10/Lib/10.0.10240.0/ucrt/x86/libucrt.lib')
    normalize = lambda x: str(x).replace('\\', '/').lower()
    pdb = pdb_section_contributions(context.directory/'th16.pdb')['contributions']
    parts = {}
    for name, symbol, producer, public_offset, code_size, data_size in [
            ('entry', '_atan2', '87ctriga.obj', 0, 20, 0),
            ('math', '__fFATN2', '87triga.obj', 28, 168, 80)]:
        public = unique_public(context, symbol, producer)
        code_address = public-public_offset
        records = [p for p in pdb if normalize(p['object']) == normalize(library)
                   and p['module'].replace('\\', '/').lower().split('/')[-1] == producer]
        code = [p for p in records if p['characteristics'] & 0x20]
        data = [p for p in records if not p['characteristics'] & 0x20]
        require(len(records) == 1+bool(data_size) and len(code) == 1 and len(data) == bool(data_size)
                and code[0]['size'] == code_size and len({p['module_index'] for p in records}) == 1,
                'atan2 requires each complete pinned producer contribution')
        address = lambda p: context.image.image_base+context.image.section(p['section_number']).rva+p['section_offset']
        require(address(code[0]) == code_address, 'atan2 code contribution starts elsewhere')
        parts[name] = dict(target=row[name+'_address'], candidate=code_address, size=code_size)
        if name == 'entry':
            owners = [f for f in context.linked['functions'] if f['symbol'] == symbol]
            require(len(owners) == 1 and owners[0]['size'] == 20
                    and int(owners[0]['address'], 0) == code_address
                    and normalize(owners[0]['pdb_object']) == normalize(library)
                    and owners[0]['map_object'].lower() == 'libucrt:'+producer
                    and owners[0]['pdb_module_index'] == code[0]['module_index'],
                    'atan2 lacks its complete source-qualified entry parent')
        else:
            require(data[0]['size'] == 80, 'atan2 descriptor contribution is incomplete')
            parts['data'] = dict(target=row['data_address'], candidate=address(data[0]), size=80)
    entry, math, data = [parts[n] for n in ['entry', 'math', 'data']]
    require(unique_public(context, '__CIatan2', '87ctriga.obj') == entry['candidate']+10
            and unique_public(context, '__rtpiby2', '87triga.obj') == math['candidate']+108
            and unique_public(context, '__OP_ATAN2jmptab', '87triga.obj') == data['candidate'],
            'atan2 public differs from its fixed complete contribution offset')
    dispatch = support['parents']['dispatch']; c_dispatch = support['parents']['c_dispatch']
    for name, part in parts.items():
        original = context.target.read_address(part['target'], part['size'])
        require(hashlib.sha256(original).hexdigest() == row[name+'_sha256'], 'atan2 original hash differs')
        require(not any(part['target']-3 <= x < part['target']+part['size']
                        for x in context.target.base_relocations()), 'atan2 original unexpectedly relocates')
        replay = bytearray(context.image.read_address(part['candidate'], part['size']))
        relocations = {x-part['candidate'] for x in context.image.base_relocations()
                       if part['candidate']-3 <= x < part['candidate']+part['size']}
        if name == 'data':
            for image, at in [(context.target, part['target']), (context.image, part['candidate'])]:
                require(any(not s.characteristics & (0x20|0x80000000)
                            and image.image_base+s.rva <= at and at+80 <= image.image_base+s.rva+s.raw_size
                            for s in image.sections), 'atan2 descriptor leaves complete read-only storage')
            require(relocations == set(range(16, 80, 4)) and replay[:16] == original[:16]
                    and replay[:6] == b'\x05atan2', 'atan2 descriptor header or relocation footprint differs')
            for offset in range(16, 80, 4):
                value = struct.unpack_from('<I', replay, offset)[0]
                parents = [p for p in [math, dispatch] if p['candidate'] <= value < p['candidate']+p['size']]
                require(len(parents) == 1, 'atan2 descriptor handler leaves verified complete code')
                parent = parents[0]; value += parent['target']-parent['candidate']
                struct.pack_into('<I', replay, offset, value)
        else:
            try:
                fields = linked_code_fields(context.image, context.publics, part['candidate'], part['size'])
            except LinkedImageError as error:
                raise RuntimeEvidenceError('atan2 complete linked fields are invalid: '+str(error)) from error
            expected = [(1, 'DIR32'), (6, 'REL32'), (11, 'DIR32'), (16, 'REL32')] if name == 'entry' else [
                (104, 'REL32'), (112, 'DIR32'), (148, 'REL32'), (164, 'REL32')]
            require(fields['normalization_complete'] and fields['decoded_bytes'] == part['size']
                    and [(f['offset'], f['type']) for f in fields['fields']] == expected
                    and all(f['width'] == 4 for f in fields['fields']), 'atan2 complete code field set differs')
            require(relocations == {f['offset'] for f in fields['fields'] if f['type'] == 'DIR32'},
                    'atan2 complete code relocation footprint differs')
            for field in fields['fields']:
                value = field['candidate_target']
                if name == 'entry':
                    if field['type'] == 'DIR32':
                        require(value == data['candidate'], 'atan2 entry uses another descriptor')
                        value = data['target']
                    else:
                        offset = 135 if field['offset'] == 6 else 0
                        require(value == c_dispatch['candidate']+offset, 'atan2 entry dispatch edge differs')
                        value = c_dispatch['target']+offset
                elif field['type'] == 'DIR32':
                    require(value == dispatch['data_candidate']+10, 'atan2 pi/2 constant role differs')
                    value = dispatch['data_target']+10
                else:
                    require(dispatch['candidate'] <= value < dispatch['candidate']+dispatch['size'],
                            'atan2 math tail leaves its complete verified dispatcher')
                    value += dispatch['target']-dispatch['candidate']
                if field['type'] == 'REL32': value -= part['target']+field['instruction_end']
                struct.pack_into('<I', replay, field['offset'], value & 0xffffffff)
        require(bytes(replay) == original, 'atan2 complete contribution replay differs')
    for name, before, after in [('entry', 9, 12), ('math', 3, 8)]:
        part = parts[name]
        require(context.target.read_address(part['target']-before, before) == b'\xcc'*before
                and context.target.read_address(part['target']+part['size'], after) == b'\xcc'*after,
                'atan2 original complete contribution padding differs')
    parent = row['witness_parent']; boundary = context.boundaries.get(parent)
    require(parent == 0x4052a0 and boundary and int(boundary['size']) == 57
            and int(boundary['span_end'], 0) == parent+56
            and hashlib.sha256(context.target.read_address(parent, 57)).hexdigest() == row['witness_parent_sha256'],
            'atan2 witness requires its complete original wrapper')
    instructions, _ = decode_scope(context.target, parent, 57, [0])
    call = next((i for i in instructions if i.address == parent+36), None)
    require(row['witnesses'] == [parent+36] and call is not None and call.mnemonic == 'call'
            and call.size == 5 and bytes(call.bytes)[0] == 0xe8 and call.operands[0].imm == entry['target']+10,
            'atan2 interior lacks its fixed original x87 CALL witness')
    binding = dict(target=entry['target']+10, candidate=entry['candidate']+10, kind='runtime-interior-v1',
                   parent_target=entry['target'], parent_candidate=entry['candidate'], parent_size=20,
                   entry_offset=10, evidence=row['evidence'])
    return {'__CIatan2': binding}, dict(profile=row['profile'], code_bytes=188, data_bytes=80,
        complete_code_equal=True, complete_data_equal=True, primary_exact_credit=0, parents=parts,
        shared_dispatcher_profile=support['profile'])
