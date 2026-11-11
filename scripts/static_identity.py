"""Explicit complete private-function identities; no public-symbol promotion."""
from collections import deque
import hashlib
import tomllib

import capstone

from eh_identity import private_owner, EHEvidenceError
from linked_image import map_statics, pdb_section_contributions, linked_code_fields


class StaticEvidenceError(ValueError):
    pass


SINCOS_SCALE = bytes.fromhex('558bec51894dfc8b45fcd94508d9fbd84d0cd918d84d0cd958048be55dc20800')


def require(condition, message):
    if not condition:
        raise StaticEvidenceError(message)


def review_functions(context, path):
    records = tomllib.loads(path.read_text())
    require(set(records) == {'functions'}, 'unsupported private-function configuration')
    statics = map_statics(context.directory / 'th16.map')
    pdb = pdb_section_contributions(context.directory / 'th16.pdb')
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    annotations = [line.split() for line in (context.directory / 'functions.txt').read_text().splitlines()]
    result = {}
    identities = set()
    for name, row in records['functions'].items():
        require(set(row) == {'profile','source','symbol','target','size','sha256',
                             'witness_parent','witness','parent_sha256'}, 'unsupported private-function fields')
        source = row['source']
        require(isinstance(source,str) and source.startswith('src/') and source.endswith('.cpp')
                and '\\' not in source and ':' not in source
                and all(p not in ('','.','..') for p in source.split('/')),
                'private producer requires a canonical maintained source path')
        require(row['profile'] == 'x87-sincos-scale-v1' and row['size'] == len(SINCOS_SCALE),
                'unreviewed private-function profile or complete extent')
        target, size = row['target'], row['size']
        require(type(target) is int and type(size) is int, 'private-function extent must be integral')
        boundary = context.boundaries.get(target)
        require(boundary is not None and int(boundary['size']) == size
                and int(boundary['span_end'],0) == target+size-1, 'private function lacks its whole original boundary')
        require(boundary['source_file'] == row['source'], 'private original source identity differs')
        require(context.target.read_address(target,size) == SINCOS_SCALE
                and hashlib.sha256(SINCOS_SCALE).hexdigest() == row['sha256'], 'private original profile bytes differ')
        require(not any(a < target+size and target <= int(r['span_end'],0)
                        for a,r in context.boundaries.items() if a != target), 'private original owner overlaps')
        next_entry = min(a for a in context.boundaries if a > target)
        require(all(v == 0xcc for v in context.target.read_address(target+size,next_entry-target-size)),
                'private original owner has unexplained trailing bytes')
        try:
            owner = private_owner(context,statics,pdb,row['symbol'],row['source'],size,True)
        except EHEvidenceError as error:
            raise StaticEvidenceError(str(error)) from error
        require([r for r in annotations if int(r[0],0) == target] ==
                [[hex(target),hex(owner['address']),row['symbol']]], 'private annotation identity differs')
        require(context.image.read_address(owner['address'],size) == SINCOS_SCALE,
                'complete private candidate profile bytes differ')
        require(not any(a < owner['address']+size and owner['address'] < a+4
                        for a in context.image.base_relocations()), 'private profile has unreviewed PE relocations')
        fields = linked_code_fields(context.image,context.publics,owner['address'],size)
        require(fields['decoded_bytes'] == size and not fields['fields'], 'private profile has unreviewed linked fields')
        parent, witness = row['witness_parent'], row['witness']
        require(parent in context.boundaries, 'private witness lacks original parent')
        raw = context.target.read_address(parent,int(context.boundaries[parent]['size']))
        require(hashlib.sha256(raw).hexdigest() == row['parent_sha256'], 'private witness parent hash differs')
        ins = list(decoder.disasm(raw,parent))
        require(sum(i.size for i in ins) == len(raw), 'private witness parent does not completely decode')
        by = {i.address:i for i in ins}
        require(witness in by, 'private witness is not an original instruction start')
        call = by[witness]
        require(call.mnemonic == 'call' and call.operands[0].type == capstone.x86.X86_OP_IMM
                and call.operands[0].imm == target, 'private witness is not a call to its entry')
        previous = {parent:None}
        queue = deque([parent])
        while queue and witness not in previous:
            a = queue.popleft()
            i = by[a]
            if i.group(capstone.CS_GRP_RET):
                continue
            destinations = []
            if i.group(capstone.CS_GRP_JUMP):
                if i.operands[0].type != capstone.x86.X86_OP_IMM:
                    continue
                destinations.append(i.operands[0].imm & 0xffffffff)
                if i.mnemonic != 'jmp':
                    destinations.append(a+i.size)
            else:
                if i.group(capstone.CS_GRP_CALL) and i.operands[0].type == capstone.x86.X86_OP_IMM:
                    callee = context.boundaries.get(i.operands[0].imm & 0xffffffff,{})
                    if any(n in callee.get('current_name','').lower()
                           for n in ['throwexception','exitprocess','_invoke_watson','_abort']):
                        continue
                destinations.append(a+i.size)
            for dest in destinations:
                if dest in by and dest not in previous:
                    previous[dest] = a
                    queue.append(dest)
        require(witness in previous, 'private witness has no reviewed original entry path')
        path_to_call = []
        a = witness
        while a is not None:
            require(by[a].mnemonic not in ('int3','ud2','hlt'), 'private witness path crosses a trap')
            path_to_call.append(a)
            a = previous[a]
        identity = (row['source'],row['symbol'])
        require(identity not in identities and target not in {r['target'] for r in result.values()},
                'duplicate private-function identity')
        identities.add(identity)
        function = dict(symbol=row['symbol'],address=hex(owner['address']),size=size,
                        extent_source='pdb-section-contribution',pdb_object=owner['object'],
                        pdb_module_index=owner['module_index'])
        result[name] = dict(**row,candidate=owner['address'],function=function,
                            witness_path=list(reversed(path_to_call)))
    return result


def validate_field(proofs, field, candidate):
    proof = proofs.get(field.get('reviewed_static'))
    require(proof is not None, 'unknown reviewed private callee')
    require(field.get('symbol') == proof['symbol'] and field.get('target') == proof['target']
            and candidate == proof['candidate'] and field.get('type') == 'REL32'
            and field.get('width') == 4 and field.get('addend',0) == 0
            and not field.get('local') and 'storage_size' not in field
            and 'eh_handler' not in field, 'private callee leaves its complete qualified entry')
