"""Explicit complete private-function identities; no public-symbol promotion."""
from collections import deque
from pathlib import Path
import hashlib
import re
import struct
import tomllib

import capstone

from eh_identity import private_owner, EHEvidenceError
from linked_image import map_statics, pdb_section_contributions, linked_code_fields
from switch_ownership import inspect_switch


class StaticEvidenceError(ValueError):
    pass


SINCOS_SCALE = bytes.fromhex('558bec51894dfc8b45fcd94508d9fbd84d0cd918d84d0cd958048be55dc20800')
SINCOS_SCALE_XY = bytes.fromhex('558bec83ec088955f8894dfc8b45fcd94508d9fbd84d0cd918d84d0c8b45f8d9188be55dc20800')
# ECX is the output vector; angle, x radius and y radius occupy distinct
# stack arguments. The complete owner stores only X/Y and returns twelve bytes.
SINCOS_ELLIPSE = bytes.fromhex('558bec51894dfc8b45fcd94508d9fbd84d0cd918d84d10d958048be55dc20c00')
PROFILES = {'x87-sincos-scale-v1': SINCOS_SCALE, 'x87-sincos-scale-xy-v1': SINCOS_SCALE_XY,
            'x87-sincos-ellipse-v1': SINCOS_ELLIPSE}


def require(condition, message):
    if not condition:
        raise StaticEvidenceError(message)


def witness_dispatch(context, spec, by):
    """Review one bounded byte-remap edge for original witness paths only."""
    fields = {'profile','guard','branch','remap','dispatch','map_address','map_count',
              'map_sha256','targets_address','targets_count','targets_sha256'}
    require(set(spec) in (fields, fields|{'interleaved'}), 'unsupported private witness dispatch fields')
    require(spec['profile'] == 'bounded-byte-remap-v1', 'unreviewed private witness dispatch profile')
    sites = [spec[k] for k in ('guard','branch','remap','dispatch')]
    require(all(type(a) is int and a in by for a in sites), 'witness dispatch is not at instruction starts')
    guard, branch, remap, jump = [by[a] for a in sites]
    # The scheduler may place frame-constant stores between the remap and the
    # indirect jump. Each must be an explicit, adjacent `mov [ebp-N], imm32`:
    # it writes neither a register nor control flow.
    interleaved = spec.get('interleaved', [])
    require(type(interleaved) is list and len(interleaved) <= 2
            and all(type(a) is int and a in by for a in interleaved),
            'witness dispatch interleaving is not at instruction starts')
    for a in interleaved:
        i = by[a]
        require(i.mnemonic == 'mov' and len(i.operands) == 2
                and i.operands[0].type == capstone.x86.X86_OP_MEM and i.operands[0].size == 4
                and i.operands[0].mem.base == capstone.x86.X86_REG_EBP and not i.operands[0].mem.index
                and i.operands[0].mem.disp < 0 and i.operands[1].type == capstone.x86.X86_OP_IMM,
                'witness dispatch interleaving is not a frame-constant store')
    require(guard.mnemonic == 'cmp' and len(guard.operands) == 2
            and guard.operands[0].type == capstone.x86.X86_OP_REG and guard.operands[0].size == 4
            and guard.operands[1].type == capstone.x86.X86_OP_IMM, 'witness dispatch lacks an index bound')
    register = guard.operands[0].reg
    require(type(spec['map_count']) is int and 0 < spec['map_count'] <= 4096
            and guard.operands[1].imm == spec['map_count']-1, 'witness dispatch map extent differs from bound')
    require(branch.mnemonic == 'ja' and branch.operands[0].type == capstone.x86.X86_OP_IMM
            and branch.operands[0].imm in by, 'witness dispatch requires an owned unsigned default')
    chain = [guard, branch, remap] + [by[a] for a in interleaved] + [jump]
    require(all(a.address+a.size == b.address for a,b in zip(chain,chain[1:])),
            'witness dispatch guard/remap sequence is not adjacent')
    require(remap.mnemonic == 'movzx' and remap.operands[0].type == capstone.x86.X86_OP_REG
            and remap.operands[0].reg == register and remap.operands[0].size == 4
            and remap.operands[1].type == capstone.x86.X86_OP_MEM and remap.operands[1].size == 1
            and remap.operands[1].mem.base == register and not remap.operands[1].mem.index
            and remap.operands[1].mem.disp == spec['map_address'], 'witness dispatch remap index differs')
    require(jump.mnemonic == 'jmp' and jump.operands[0].type == capstone.x86.X86_OP_MEM
            and jump.operands[0].size == 4 and not jump.operands[0].mem.base
            and jump.operands[0].mem.index == register and jump.operands[0].mem.scale == 4
            and jump.operands[0].mem.disp == spec['targets_address'], 'witness dispatch target index differs')
    mapper = context.target.read_address(spec['map_address'],spec['map_count'])
    require(hashlib.sha256(mapper).hexdigest() == spec['map_sha256'], 'witness dispatch complete map hash differs')
    require(type(spec['targets_count']) is int and spec['targets_count'] == max(mapper)+1,
            'witness dispatch target extent differs from mapped index range')
    raw = context.target.read_address(spec['targets_address'],spec['targets_count']*4)
    require(hashlib.sha256(raw).hexdigest() == spec['targets_sha256'], 'witness dispatch complete targets hash differs')
    targets = struct.unpack('<'+'I'*spec['targets_count'],raw)
    require(set(targets) <= set(by), 'witness dispatch target is not an owned instruction start')
    code_end = max(a+i.size for a,i in by.items())
    m0,m1 = spec['map_address'],spec['map_address']+len(mapper)
    t0,t1 = spec['targets_address'],spec['targets_address']+len(raw)
    require(m0 >= code_end and t0 >= code_end and (m1 <= t0 or t1 <= m0),
            'witness dispatch data overlaps code or another table')
    forbidden = set(range(branch.address,jump.address+jump.size))
    require(not set(targets)&forbidden and not any(
        i.group(capstone.CS_GRP_JUMP) and i.operands[0].type == capstone.x86.X86_OP_IMM
        and i.operands[0].imm in forbidden for i in by.values()), 'witness dispatch guard can be bypassed')
    return dict(at=jump.address,guard=guard.address,mapper=list(mapper),targets=list(targets),
                mapped_targets=sorted({targets[v] for v in mapper}))


def review_functions(context, path, *, unavailable=None):
    records = tomllib.loads(path.read_text())
    require(set(records) == {'functions'}, 'unsupported private-function configuration')
    statics = map_statics(context.directory / 'th16.map')
    pdb = pdb_section_contributions(context.directory / 'th16.pdb')
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    annotations = [line.split() for line in (context.directory / 'functions.txt').read_text().splitlines()]
    result = {}
    identities, targets = set(), set()
    for name, row in records['functions'].items():
        semantic_sse2 = row.get('profile') == 'x87-sincos-scale-sse2-candidate-v1'
        required = {'profile','source','symbol','target','size','sha256',
                    'witness_parent','witness','parent_sha256'}
        if semantic_sse2:
            required |= {'candidate_size','candidate_sha256'}
        require(set(row)-{'witness_dispatch'} == required, 'unsupported private-function fields')
        source = row['source']
        require(isinstance(source,str) and source.startswith('src/') and source.endswith('.cpp')
                and '\\' not in source and ':' not in source
                and all(p not in ('','.','..') for p in source.split('/')),
                'private producer requires a canonical maintained source path')
        payload = (PROFILES['x87-sincos-scale-v1'] if semantic_sse2
                   else PROFILES.get(row['profile']))
        require(payload is not None and row['size'] == len(payload),
                'unreviewed private-function profile or complete extent')
        target, size = row['target'], row['size']
        candidate_size = row['candidate_size'] if semantic_sse2 else size
        require(type(candidate_size) is int and candidate_size > 0,
                'private candidate extent must be integral')
        require(type(target) is int and type(size) is int, 'private-function extent must be integral')
        boundary = context.boundaries.get(target)
        require(boundary is not None and int(boundary['size']) == size
                and int(boundary['span_end'],0) == target+size-1, 'private function lacks its whole original boundary')
        require(boundary['source_file'] == row['source'], 'private original source identity differs')
        require(context.target.read_address(target,size) == payload
                and hashlib.sha256(payload).hexdigest() == row['sha256'], 'private original profile bytes differ')
        require(not any(a < target+size and target <= int(r['span_end'],0)
                        for a,r in context.boundaries.items() if a != target), 'private original owner overlaps')
        next_entry = min(a for a in context.boundaries if a > target)
        require(all(v == 0xcc for v in context.target.read_address(target+size,next_entry-target-size)),
                'private original owner has unexplained trailing bytes')
        parent, witness = row['witness_parent'], row['witness']
        require(parent in context.boundaries, 'private witness lacks original parent')
        raw = context.target.read_address(parent,int(context.boundaries[parent]['size']))
        if parent in context.switch_owners:
            record = context.switch_owners[parent]
            try:
                _, _, complete = inspect_switch(context.target,parent,record)
            except ValueError as error:
                raise StaticEvidenceError('private witness parent switch: '+str(error)) from error
            require(raw == complete and hashlib.sha256(complete).hexdigest() == record['target_sha256'],
                    'private witness parent lacks its complete reviewed switch owner')
            raw = complete[:record['code_size']]
        require(hashlib.sha256(raw).hexdigest() == row['parent_sha256'], 'private witness parent hash differs')
        ins = list(decoder.disasm(raw,parent))
        require(sum(i.size for i in ins) == len(raw), 'private witness parent does not completely decode')
        by = {i.address:i for i in ins}
        dispatch = witness_dispatch(context,row['witness_dispatch'],by) if 'witness_dispatch' in row else None
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
                    if dispatch and a == dispatch['at']:
                        for dest in dispatch['mapped_targets']:
                            if dest not in previous:
                                previous[dest] = a
                                queue.append(dest)
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
        if dispatch and dispatch['at'] in path_to_call:
            require(dispatch['guard'] in path_to_call, 'private witness path bypasses its dispatch guard')
        identity = (row['source'],row['symbol'])
        require(identity not in identities and target not in targets, 'duplicate private-function identity')
        identities.add(identity)
        targets.add(target)
        try:
            owner = private_owner(context,statics,pdb,row['symbol'],row['source'],candidate_size,True)
            require([r for r in annotations if int(r[0],0) == target] ==
                    [[hex(target),hex(owner['address']),row['symbol']]], 'private annotation identity differs')
            candidate_payload = context.image.read_address(owner['address'],candidate_size)
            if semantic_sse2:
                normalized = bytearray(candidate_payload)
                for offset in (19, 48):
                    normalized[offset:offset + 4] = b'\0' * 4
                require(hashlib.sha256(normalized).hexdigest() == row['candidate_sha256'],
                        'complete private SSE2 sincos candidate differs')
                source_text = (Path(__file__).resolve().parents[1] / source).read_text()
                require(re.search(r'static\s+void\s+__fastcall\s+enemy_ecl_sincosmul\s*'
                                  r'\(Float3\s*\*dst,\s*f32\s+angle,\s*f32\s+radius\)\s*'
                                  r'\{\s*dst->x\s*=\s*radius\s*\*\s*cosf\(angle\);\s*'
                                  r'dst->y\s*=\s*radius\s*\*\s*sinf\(angle\);\s*\}',
                                  source_text) is not None,
                        'private SSE2 sincos source is not the reviewed natural C++ implementation')
                fields = linked_code_fields(context.image,context.publics,owner['address'],candidate_size)
                require(fields['decoded_bytes'] == candidate_size and fields['normalization_complete']
                        and [(f['offset'],f['width'],f['type'],f.get('candidate_symbols'))
                             for f in fields['fields']]
                        == [(19,4,'REL32',['__libm_sse2_cos_precise']),
                            (48,4,'REL32',['__libm_sse2_sin_precise'])],
                        'private SSE2 sincos candidate does not compute cosine then sine into XY')
            else:
                require(candidate_payload == payload, 'complete private candidate profile bytes differ')
                fields = linked_code_fields(context.image,context.publics,owner['address'],candidate_size)
                require(fields['decoded_bytes'] == candidate_size and not fields['fields'],
                        'private profile has unreviewed linked fields')
            require(not any(a < owner['address']+candidate_size and owner['address'] < a+4
                            for a in context.image.base_relocations()), 'private profile has unreviewed PE relocations')
        except (EHEvidenceError, StaticEvidenceError) as error:
            if unavailable is None:
                raise StaticEvidenceError(str(error)) from error
            unavailable[target] = str(error)
            continue
        function = dict(symbol=row['symbol'],address=hex(owner['address']),size=candidate_size,
                        extent_source='pdb-section-contribution',pdb_object=owner['object'],
                        pdb_module_index=owner['module_index'])
        result[name] = dict(**row,candidate=owner['address'],function=function,
                            witness_path=list(reversed(path_to_call)))
        if dispatch:
            result[name]['dispatch_proof'] = dispatch
    return result


def validate_field(proofs, field, candidate):
    proof = proofs.get(field.get('reviewed_static'))
    require(proof is not None, 'unknown reviewed private callee')
    require(field.get('symbol') == proof['symbol'] and field.get('target') == proof['target']
            and candidate == proof['candidate'] and field.get('type') == 'REL32'
            and field.get('width') == 4 and field.get('addend',0) == 0
            and not field.get('local') and 'storage_size' not in field
            and 'eh_handler' not in field, 'private callee leaves its complete qualified entry')
