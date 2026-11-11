"""Review bounded switch code and its complete trailing absolute-address table."""
import hashlib
import struct
import tomllib

import capstone
from capstone import x86_const as x86


def load_switch_owners(path):
    records = {}
    for row in tomllib.loads(path.read_text()).get("switch_owners", []):
        address = row["target_address"]
        if address in records:
            raise ValueError("duplicate reviewed switch owner")
        count, code_size = row["case_count"], row["code_size"]
        if (count <= 0 or code_size <= 0 or not 0 <= row["table_offset"] - code_size <= 3
                or len(row["case_offsets"]) != count or not row["evidence"]):
            raise ValueError("invalid reviewed switch ownership record")
        records[address] = row
    return records


def inspect_switch(image, address, record):
    code_size, count = record["code_size"], record["case_count"]
    size = record["table_offset"] + count * 4
    payload = image.read_address(address, size)
    if (address + record["table_offset"]) % 4 or any(
            byte not in {0x90, 0xCC} for byte in payload[code_size:record["table_offset"]]):
        raise ValueError("switch table lacks its reviewed alignment padding")
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    instructions = list(decoder.disasm(payload[:code_size], address))
    if sum(i.size for i in instructions) != code_size:
        raise ValueError("switch code is not completely decoded")
    by_address = {i.address: i for i in instructions}
    guard = by_address.get(address + record["guard_offset"])
    dispatch = by_address.get(address + record["dispatch_offset"])
    if (guard is None or guard.mnemonic != "cmp" or len(guard.operands) != 2
            or guard.operands[0].type != x86.X86_OP_REG
            or guard.operands[1].type != x86.X86_OP_IMM
            or guard.operands[1].imm != count - 1):
        raise ValueError("switch lacks its complete unsigned index bound")
    branch = by_address.get(guard.address + guard.size)
    if (branch is None or branch.mnemonic != "ja" or len(branch.operands) != 1
            or branch.operands[0].type != x86.X86_OP_IMM
            or branch.operands[0].imm not in by_address
            or dispatch is None or branch.address + branch.size != dispatch.address):
        raise ValueError("switch lacks its adjacent unsigned default branch")
    if dispatch.mnemonic != "jmp" or len(dispatch.operands) != 1:
        raise ValueError("switch lacks its reviewed indirect dispatch")
    operand = dispatch.operands[0]
    if (operand.type != x86.X86_OP_MEM or operand.size != 4
            or operand.mem.segment or operand.mem.base
            or operand.mem.index != guard.operands[0].reg or operand.mem.scale != 4
            or operand.mem.disp != address + record["table_offset"]):
        raise ValueError("switch dispatch does not address its complete owned table")
    # Neither the default branch nor dispatch may be entered without the cmp.
    guarded_entries = {branch.address, dispatch.address}
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
    return instructions, dispatch, payload


def validate_switch_owner(context, unit, record):
    """Prove both complete extents; no table bytes are excluded from replay."""
    target_address = record["target_address"]
    size = record["table_offset"] + record["case_count"] * 4
    if (unit["target_address"] != target_address or unit["size"] != size
            or unit["compare_size"] != size):
        raise ValueError("switch owner does not include the complete code and table")
    instructions, dispatch, payload = inspect_switch(context.target, target_address, record)
    if hashlib.sha256(payload).hexdigest() != record["target_sha256"]:
        raise ValueError("reviewed switch target extent hash mismatch")
    candidate_address = unit["candidate_address"]
    _, candidate_dispatch, _ = inspect_switch(context.image, candidate_address, record)
    table_start = candidate_address + record["table_offset"]
    table_end = candidate_address + size
    relocations = set(context.image.base_relocations())
    table_relocations = {a for a in relocations if a < table_end and a + 4 > table_start}
    if table_relocations != set(range(table_start, table_end, 4)):
        raise ValueError("switch table lacks exhaustive complete entry relocations")
    if candidate_dispatch.address + candidate_dispatch.disp_offset not in relocations:
        raise ValueError("switch dispatch lacks its table-address relocation")
    return instructions, dispatch.address
