"""Review bounded switch code and its complete trailing tables."""
import hashlib
import struct
import tomllib

import capstone
from capstone import x86_const as x86


def switch_owner_size(record):
    if "dispatches" in record:
        return record["size"]
    return record["table_offset"] + record["case_count"] * 4 + len(record.get("remap_values", []))


def compound_data_parts(record):
    parts = []
    for row in record["dispatches"]:
        parts.append(dict(kind="targets",offset=row["table_offset"],width=row["case_count"]*4))
        if "remap_values" in row:
            parts.append(dict(kind="remap",offset=row["remap_offset"],width=len(row["remap_values"])))
    return sorted(parts,key=lambda part:part["offset"])


def validate_compound_record(record):
    required = {"profile","target_address","code_size","size","dispatches","target_sha256","evidence"}
    frame_profile = record.get("profile") == "compound-frame-store-v1"
    if (set(record) != required or record["profile"] not in {"compound-bounded-v1", "compound-frame-store-v1"}
            or any(type(record[k]) is not int for k in ("target_address","code_size","size"))
            or not 0 < record["code_size"] < record["size"] or not record["evidence"]
            or not isinstance(record["dispatches"],list) or len(record["dispatches"]) < 2):
        raise ValueError("invalid explicit compound switch owner")
    sites = set()
    frame_stores = 0
    for row in record["dispatches"]:
        keys = {"table_offset","case_count","guard_offset","dispatch_offset","case_offsets"}
        row_keys = set(row)
        if "frame_store_offset" in row_keys and frame_profile:
            row_keys.remove("frame_store_offset")
            frame_stores += 1
        if row_keys not in (keys,keys | {"remap_offset","remap_values"}):
            raise ValueError("invalid compound dispatch fields")
        if (any(type(row[k]) is not int for k in keys-{"case_offsets"})
                or not 0 <= row["guard_offset"] < row["dispatch_offset"] < record["code_size"]
                or row["dispatch_offset"] in sites or not 0 < row["case_count"] <= record["size"]//4
                or not isinstance(row["case_offsets"],list) or len(row["case_offsets"]) != row["case_count"]
                or any(type(v) is not int or not 0 <= v < record["code_size"] for v in row["case_offsets"])):
            raise ValueError("invalid complete compound dispatch extent")
        if "frame_store_offset" in row:
            if ("remap_values" not in row or type(row["frame_store_offset"]) is not int
                    or not row["guard_offset"] < row["frame_store_offset"] < row["dispatch_offset"]):
                raise ValueError("invalid explicit remap frame-store site")
        sites.add(row["dispatch_offset"])
        if "remap_values" in row:
            values = row["remap_values"]
            if (type(row["remap_offset"]) is not int or not isinstance(values,list)
                    or not 0 < len(values) <= record["size"]
                    or any(type(v) is not int or not 0 <= v < min(row["case_count"],256) for v in values)
                    or max(values) != row["case_count"]-1):
                raise ValueError("invalid complete compound remap extent")
    if frame_profile and not frame_stores:
        raise ValueError("frame-store profile requires an explicit remap store")
    cursor = record["code_size"]
    for part in compound_data_parts(record):
        if (not 0 <= part["offset"]-cursor <= 3
                or part["kind"]=="targets" and (record["target_address"]+part["offset"])%4
                or (part["offset"] != cursor and part["kind"] != "targets")
                or part["offset"]+part["width"] > record["size"]):
            raise ValueError("compound data overlaps or leaves an unreviewed gap")
        cursor = part["offset"]+part["width"]
    if cursor != record["size"]:
        raise ValueError("compound owner omits or expands its final data extent")


def load_switch_owners(path):
    records = {}
    for row in tomllib.loads(path.read_text()).get("switch_owners", []):
        address = row["target_address"]
        if address in records:
            raise ValueError("duplicate reviewed switch owner")
        if "dispatches" in row:
            validate_compound_record(row)
            records[address] = row
            continue
        count, code_size = row["case_count"], row["code_size"]
        if (count <= 0 or code_size <= 0 or not 0 <= row["table_offset"] - code_size <= 3
                or len(row["case_offsets"]) != count or not row["evidence"]):
            raise ValueError("invalid reviewed switch ownership record")
        remap_keys = {"remap_offset", "remap_values"} & row.keys()
        if remap_keys:
            if remap_keys != {"remap_offset", "remap_values"}:
                raise ValueError("incomplete reviewed switch remap record")
            values = row["remap_values"]
            if (row["remap_offset"] != row["table_offset"] + count * 4
                    or not 0 < len(values) <= 256
                    or any(type(v) is not int or not 0 <= v < count for v in values)
                    or max(values) != count - 1):
                raise ValueError("invalid complete switch remap extent")
        records[address] = row
    return records


def inspect_switch(image, address, record):
    if "dispatches" in record:
        return inspect_compound_switch(image,address,record)
    code_size, count = record["code_size"], record["case_count"]
    size = switch_owner_size(record)
    payload = image.read_address(address, size)
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    alignment = payload[code_size:record["table_offset"]]
    padding = list(decoder.disasm(alignment, address + code_size))
    if ((address + record["table_offset"]) % 4
            or sum(i.size for i in padding) != len(alignment)
            or any(i.mnemonic not in {"nop", "int3"} for i in padding)):
        raise ValueError("switch table lacks its reviewed alignment padding")
    instructions = list(decoder.disasm(payload[:code_size], address))
    if sum(i.size for i in instructions) != code_size:
        raise ValueError("switch code is not completely decoded")
    dispatch,_,_ = inspect_dispatch(payload,address,record,instructions)
    return instructions, dispatch, payload


def inspect_frame_store(address, instructions, store, index_register):
    """Prove one immediate store belongs to an established, stable GS/EH frame.

    This recognizes a concrete x86 compiler prologue. It does not skip arbitrary
    instructions or normalize the store's displacement, immediate or bytes.
    """
    if len(instructions) < 10:
        raise ValueError("frame store lacks its complete GS/EH prologue")
    prefix = instructions[:10]
    p, base, state, handler, chain, saved, allocation, cookie, mix, home = prefix
    if (p.bytes != b"\x55" or base.bytes != b"\x8b\xec"
            or state.bytes != b"\x6a\xff"
            or handler.mnemonic != "push" or len(handler.operands) != 1
            or handler.operands[0].type != x86.X86_OP_IMM or handler.operands[0].size != 4
            or chain.mnemonic != "mov" or len(chain.operands) != 2
            or chain.operands[0].type != x86.X86_OP_REG or chain.operands[0].reg != x86.X86_REG_EAX
            or chain.operands[1].type != x86.X86_OP_MEM or chain.operands[1].size != 4
            or chain.operands[1].mem.segment != x86.X86_REG_FS
            or chain.operands[1].mem.base or chain.operands[1].mem.index or chain.operands[1].mem.disp
            or saved.bytes != b"\x50"
            or allocation.mnemonic != "sub" or len(allocation.operands) != 2
            or allocation.operands[0].type != x86.X86_OP_REG
            or allocation.operands[0].reg != x86.X86_REG_ESP
            or allocation.operands[1].type != x86.X86_OP_IMM
            or allocation.operands[1].imm <= 0 or allocation.operands[1].imm % 4
            or cookie.mnemonic != "mov" or len(cookie.operands) != 2
            or cookie.operands[0].type != x86.X86_OP_REG or cookie.operands[0].reg != x86.X86_REG_EAX
            or cookie.operands[1].type != x86.X86_OP_MEM or cookie.operands[1].size != 4
            or cookie.operands[1].mem.segment or cookie.operands[1].mem.base or cookie.operands[1].mem.index
            or mix.bytes != b"\x33\xc5" or home.bytes != b"\x89\x45\xf0"):
        raise ValueError("frame store lacks its complete GS/EH prologue")
    if index_register in {x86.X86_REG_EBP, x86.X86_REG_ESP}:
        raise ValueError("frame store aliases its bounded index register")
    if (store is None or store.mnemonic != "mov" or len(store.operands) != 2
            or store.operands[0].type != x86.X86_OP_MEM or store.operands[0].size != 4
            or store.operands[0].mem.segment or store.operands[0].mem.index
            or store.operands[0].mem.base != x86.X86_REG_EBP
            or store.operands[1].type != x86.X86_OP_IMM):
        raise ValueError("remap frame store is not one EBP-relative immediate MOV")
    displacement = store.operands[0].mem.disp
    # Three EH words precede SUB ESP; the cookie occupies EBP-16 .. EBP-13.
    if not -12-allocation.operands[1].imm <= displacement <= -20:
        raise ValueError("remap frame store leaves its allocated local area")
    for n, instruction in enumerate(instructions):
        if x86.X86_REG_EBP not in instruction.regs_access()[1]:
            continue
        terminal_pop = (instruction.bytes == b"\x5d" and n+1 < len(instructions)
                        and instructions[n+1].group(capstone.CS_GRP_RET))
        if instruction.address != base.address and not terminal_pop:
            raise ValueError("remap frame base is modified inside the owner")
    # Prologue instructions cannot be entered from another block or table.
    return set(range(address, home.address + home.size))


def inspect_dispatch(payload, address, record, instructions, *, same_remap_register=True,
                     frame_store=False):
    count = record["case_count"]
    by_address = {i.address: i for i in instructions}
    guard = by_address.get(address + record["guard_offset"])
    dispatch = by_address.get(address + record["dispatch_offset"])
    bound_count = len(record["remap_values"]) if "remap_values" in record else count
    if (guard is None or guard.mnemonic != "cmp" or len(guard.operands) != 2
            or guard.operands[0].type != x86.X86_OP_REG
            or guard.operands[1].type != x86.X86_OP_IMM
            or guard.operands[0].size != 4
            or guard.operands[1].imm != bound_count - 1):
        raise ValueError("switch lacks its complete unsigned index bound")
    branch = by_address.get(guard.address + guard.size)
    if (branch is None or branch.mnemonic != "ja" or len(branch.operands) != 1
            or branch.operands[0].type != x86.X86_OP_IMM
            or branch.operands[0].imm not in by_address or dispatch is None):
        raise ValueError("switch lacks its adjacent unsigned default branch")
    next_address = branch.address + branch.size
    index_register = guard.operands[0].reg
    if "remap_values" in record:
        remap = by_address.get(next_address)
        if (remap is None or remap.mnemonic != "movzx" or len(remap.operands) != 2
                or remap.operands[0].type != x86.X86_OP_REG or remap.operands[0].size != 4
                or same_remap_register and remap.operands[0].reg != guard.operands[0].reg
                or remap.operands[1].type != x86.X86_OP_MEM or remap.operands[1].size != 1
                or remap.operands[1].mem.segment or remap.operands[1].mem.index
                or remap.operands[1].mem.base != guard.operands[0].reg
                or remap.operands[1].mem.disp != address + record["remap_offset"]):
            raise ValueError("switch remap does not use its bounded byte index")
        next_address += remap.size
        index_register = remap.operands[0].reg
        if payload[record["remap_offset"]:record["remap_offset"]+bound_count] != bytes(record["remap_values"]):
            raise ValueError("switch remap differs from the complete reviewed byte map")
    frame_entries = set()
    if "frame_store_offset" in record:
        if not frame_store or "remap_values" not in record:
            raise ValueError("unreviewed interposed remap frame store")
        store = by_address.get(next_address)
        if next_address != address + record["frame_store_offset"]:
            raise ValueError("remap frame store is not adjacent to its byte remap")
        frame_entries = inspect_frame_store(address, instructions, store, index_register)
        next_address += store.size
    if next_address != dispatch.address:
        raise ValueError("switch lacks its adjacent unsigned default branch")
    if dispatch.mnemonic != "jmp" or len(dispatch.operands) != 1:
        raise ValueError("switch lacks its reviewed indirect dispatch")
    operand = dispatch.operands[0]
    if (operand.type != x86.X86_OP_MEM or operand.size != 4
            or operand.mem.segment or operand.mem.base
            or operand.mem.index != index_register or operand.mem.scale != 4
            or operand.mem.disp != address + record["table_offset"]):
        raise ValueError("switch dispatch does not address its complete owned table")
    # Neither the default branch nor dispatch may be entered without the cmp.
    guarded_entries = set(range(branch.address, dispatch.address + dispatch.size)) | frame_entries
    for instruction in instructions:
        if ((instruction.group(capstone.CS_GRP_JUMP) or instruction.group(capstone.CS_GRP_CALL))
                and instruction.operands and instruction.operands[0].type == x86.X86_OP_IMM
                and instruction.operands[0].imm in guarded_entries):
            raise ValueError("switch dispatch has an unguarded incoming edge")
    entries = struct.unpack_from(f"<{count}I", payload, record["table_offset"])
    case_offsets = []
    for entry in entries:
        if entry in guarded_entries:
            raise ValueError("switch dispatch has an unguarded incoming edge")
        if entry not in by_address or by_address[entry].mnemonic in {"int3", "ud2"}:
            raise ValueError("switch table does not target owned instruction starts")
        case_offsets.append(entry - address)
    if case_offsets != record["case_offsets"]:
        raise ValueError("switch table differs from the reviewed case mapping")
    return dispatch, guarded_entries, entries


def inspect_compound_switch(image, address, record):
    validate_compound_record(record)
    payload = image.read_address(address,record["size"])
    decoder = capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    decoder.detail = True
    instructions = list(decoder.disasm(payload[:record["code_size"]],address))
    if sum(i.size for i in instructions) != record["code_size"]:
        raise ValueError("compound switch code is not completely decoded")
    cursor = record["code_size"]
    for part in compound_data_parts(record):
        if part["kind"]=="targets" and (address+part["offset"])%4:
            raise ValueError("compound target table is not aligned")
        padding = payload[cursor:part["offset"]]
        decoded = list(decoder.disasm(padding,address+cursor))
        nop_padding = sum(i.size for i in decoded)==len(padding) and all(i.mnemonic in {"nop","int3"} for i in decoded)
        if padding and not (nop_padding or cursor != record["code_size"] and all(b==0 for b in padding)):
            raise ValueError("compound data lacks its reviewed alignment padding")
        cursor = part["offset"]+part["width"]
    dispatches,forbidden,all_targets = set(),set(),set()
    for row in record["dispatches"]:
        dispatch,guarded,entries = inspect_dispatch(
            payload,address,row,instructions,same_remap_register=False,
            frame_store=record["profile"] == "compound-frame-store-v1")
        dispatches.add(dispatch.address)
        forbidden.update(guarded)
        all_targets.update(entries)
    if forbidden & all_targets:
        raise ValueError("compound table bypasses another dispatch guard")
    observed = {i.address for i in instructions if i.group(capstone.CS_GRP_JUMP)
                and i.operands and i.operands[0].type != x86.X86_OP_IMM}
    if observed != dispatches:
        raise ValueError("compound owner contains an unreviewed indirect jump")
    return instructions, dispatches, payload


def validate_switch_owner(context, unit, record):
    """Prove both complete extents; no table bytes are excluded from replay."""
    target_address = record["target_address"]
    size = switch_owner_size(record)
    if (unit["target_address"] != target_address or unit["size"] != size
            or unit["compare_size"] != size):
        raise ValueError("switch owner does not include the complete code and table")
    instructions, dispatch, payload = inspect_switch(context.target, target_address, record)
    if hashlib.sha256(payload).hexdigest() != record["target_sha256"]:
        raise ValueError("reviewed switch target extent hash mismatch")
    candidate_address = unit["candidate_address"]
    candidate_instructions, candidate_dispatch, _ = inspect_switch(context.image, candidate_address, record)
    if "dispatches" in record:
        expected = {candidate_address+p["offset"]+n for p in compound_data_parts(record)
                    if p["kind"]=="targets" for n in range(0,p["width"],4)}
        begin,end = candidate_address+record["code_size"],candidate_address+size
        relocations = set(context.image.base_relocations())
        observed = {a for a in relocations if a < end and a+4 > begin}
        if observed != expected:
            raise ValueError("compound data lacks exhaustive complete entry relocations")
        by = {i.address:i for i in candidate_instructions}
        for row in record["dispatches"]:
            jump = by[candidate_address+row["dispatch_offset"]]
            if jump.address+jump.disp_offset not in relocations:
                raise ValueError("compound dispatch lacks its table-address relocation")
            if "remap_values" in row:
                guard = by[candidate_address+row["guard_offset"]]
                branch = by[guard.address+guard.size]
                remap = by[branch.address+branch.size]
                if remap.address+remap.disp_offset not in relocations:
                    raise ValueError("compound remap lacks its byte-map address relocation")
        return instructions, dispatch
    table_start = candidate_address + record["table_offset"]
    table_end = table_start + record["case_count"] * 4
    data_end = candidate_address + size
    relocations = set(context.image.base_relocations())
    table_relocations = {a for a in relocations if a < data_end and a + 4 > table_start}
    if table_relocations != set(range(table_start, table_end, 4)):
        raise ValueError("switch table lacks exhaustive complete entry relocations")
    if candidate_dispatch.address + candidate_dispatch.disp_offset not in relocations:
        raise ValueError("switch dispatch lacks its table-address relocation")
    if "remap_values" in record:
        guard = next(i for i in candidate_instructions if i.address == candidate_address + record["guard_offset"])
        branch = next(i for i in candidate_instructions if i.address == guard.address + guard.size)
        remap = next(i for i in candidate_instructions if i.address == branch.address + branch.size)
        if remap.address + remap.disp_offset not in relocations:
            raise ValueError("switch remap lacks its byte-map address relocation")
    return instructions, dispatch.address
