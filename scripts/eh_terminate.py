"""Review two complete noexcept destructor graphs and their terminate entry."""
from __future__ import annotations

import struct

from eh_identity import (check_relocations, complete_game_entry, extent_hash,
                         inspect_handler, load_config_cookie, private_owner,
                         require, target_owner_section)
from linked_image import _object_path, linked_code_fields


PROFILE = "two-state-terminate-v1"
_SPECS = {
    ("src/Stage.cpp", "??1Stage@@QAE@XZ"): {
        "parent": 0x4099a0, "size": 994, "locals": bytes.fromhex("83ec08"),
        "cookie_offset": -24,
        "frame": [(0, "55"), (1, "8bec"), (10, "64a100000000"), (28, "33c5"),
                  (31, "8d45f4"), (34, "64a300000000"), (63, "8945f0"), (66, "894dec"),
                  (95, "8b45f0"), (98, "8b4dec"), (138, "8945ec"), (141, "894df0"),
                  (170, "8b45ec"), (173, "8b4df0"), (216, "8945ec"), (219, "894df0"),
                  (248, "8b45ec"), (251, "8b4df0"), (936, "894dfc"),
                  (963, "c745fc01000000"), (976, "8b4df4"), (979, "64890d00000000"),
                  (990, "8be5"), (992, "5d")],
    },
    ("src/Item.cpp", "??1ItemManager@@QAE@XZ"): {
        "parent": 0x42f2d0, "size": 360, "locals": bytes.fromhex("51"),
        "cookie_offset": -20,
        "frame": [(0, "55"), (1, "8bec"), (10, "64a100000000"), (26, "33c5"),
                  (29, "8d45f4"), (32, "64a300000000"), (54, "8945f0"), (88, "8b4df0"),
                  (133, "894df0"), (162, "8b4df0"), (201, "8945f0"), (234, "8b45f0"),
                  (298, "c745fc00000000"), (329, "c745fc01000000"),
                  (342, "8b4df4"), (345, "64890d00000000"), (356, "8be5"), (358, "5d")],
    },
}


def inspect_frame(image, parent, handler, spec):
    import capstone
    prefix = (bytes.fromhex("558bec6aff68") + struct.pack("<I", handler)
              + bytes.fromhex("64a10000000050") + spec["locals"]
              + bytes.fromhex("535657a1") + struct.pack("<I", load_config_cookie(image))
              + bytes.fromhex("33c5508d45f464a300000000"))
    suffix = bytes.fromhex("8b4df464890d00000000595f5e5b8be55dc3")
    size = spec["size"]
    require(image.read_address(parent, len(prefix)) == prefix
            and image.read_address(parent + size - 18, 18) == suffix,
            "EH terminate parent registration, cookie or restoration differs")
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    instructions = list(decoder.disasm(image.read_address(parent, size), parent))
    require(sum(i.size for i in instructions) == size, "EH terminate parent decode is incomplete")
    frame, returns = [], []
    for instruction in instructions:
        reads, writes = instruction.regs_access()
        if capstone.x86.X86_REG_EBP in reads + writes or any(
                op.type == capstone.x86.X86_OP_MEM and op.mem.segment == capstone.x86.X86_REG_FS
                for op in instruction.operands):
            frame.append((instruction.address - parent, instruction.bytes.hex()))
        if instruction.group(capstone.CS_GRP_RET):
            returns.append(instruction.address - parent)
    require(frame == spec["frame"] and returns == [size - 1],
            "EH terminate parent states or protected frame uses differ")
    if spec["parent"] == 0x4099a0:
        # Stage stores state zero from ECX. Its defining XOR must dominate
        # that store without a write, call or branch entering the interval.
        require(image.read_address(parent + 891, 2) == bytes.fromhex("33c9"),
                "EH terminate Stage state zero lacks its defining XOR")
        for instruction in instructions:
            offset = instruction.address - parent
            if 893 <= offset < 936:
                _, writes = instruction.regs_access()
                require(capstone.x86.X86_REG_ECX not in writes
                        and not instruction.group(capstone.CS_GRP_CALL),
                        "EH terminate Stage state zero is clobbered")
            if instruction.group(capstone.CS_GRP_JUMP):
                require(instruction.operands[0].type == capstone.x86.X86_OP_IMM
                        and not parent + 891 < instruction.operands[0].imm <= parent + 936,
                        "EH terminate Stage state zero definition can be bypassed")
    return len(prefix)


def runtime_entries(context):
    result = {}
    for name, target, size in (("___std_terminate", 0x476b19, 5), ("_terminate", 0x47b825, 59),
                               ("__SEH_prolog4_GS", 0x486ce0, 73),
                               ("___acrt_getptd", 0x47cad3, 131), ("_abort", 0x47bbdb, 67),
                               ("@__security_check_cookie@4", 0x47499b, 17),
                               ("___CxxFrameHandler3", 0x475d37, 54)):
        binding = context.reviewed_linkages.get(name, {})
        entries = [p for p in context.publics if p["symbol"] == name]
        require(binding.get("kind") == "runtime-function" and binding.get("target") == target
                and binding.get("size") == size and len(entries) == 1,
                "EH terminate runtime lacks its independent complete role")
        result[name] = (target, entries[0]["address"])
    return result


def inspect_terminate(context, statics, pdb, runtime):
    """Keep both full runtime extents and the complete private SEH table."""
    candidate = runtime["_terminate"][1]
    owner = next(f for f in context.linked["functions"] if f["symbol"] == "_terminate")
    fields = linked_code_fields(context.image, context.publics, candidate, 60)
    require(owner["size"] == 60 and fields["decoded_bytes"] == 60 and fields["normalization_complete"]
            and [(f["offset"], f["width"], f["type"]) for f in fields["fields"]]
            == [(3, 4, "DIR32"), (8, 4, "REL32"), (13, 4, "REL32"),
                (32, 4, "DIR32"), (55, 4, "REL32")],
            "EH terminate runtime lacks its complete 60-byte candidate owner")
    data = fields["fields"][0]["candidate_target"]
    contributions = [r for r in pdb["contributions"]
                     if context.image.image_base + context.image.section(r["section_number"]).rva
                     + r["section_offset"] == data]
    names = [r for r in statics + context.publics if data <= r["address"] < data + 28]
    require(len(contributions) == 1 and contributions[0]["size"] == 28
            and contributions[0]["module_index"] == owner["pdb_module_index"]
            and _object_path(contributions[0]["object"]) == _object_path(owner["pdb_object"])
            and len(names) == 1 and names[0] in statics
            and names[0]["symbol"] == "__sehtable$_terminate" and names[0]["address"] == data
            and names[0]["section_number"] == contributions[0]["section_number"]
            and names[0]["section_offset"] == contributions[0]["section_offset"]
            and "f" not in names[0]["flags"]
            and names[0]["object"].lower() == "libucrt:terminate.obj",
            "EH terminate SEH table lacks its complete private runtime owner")
    selected = contributions[0]
    for row in pdb["contributions"]:
        if row is selected or row["section_number"] != selected["section_number"]:
            continue
        require(not (row["size"] > 0 and row["section_offset"] < selected["section_offset"] + 28
                     and selected["section_offset"] < row["section_offset"] + row["size"]),
                "EH terminate SEH table overlaps a PDB owner")
    section = context.image.section(selected["section_number"])
    require(all(flags & 0x40000040 == 0x40000040 and not flags & 0xa0000020
                for flags in (section.characteristics, selected["characteristics"])),
            "EH terminate SEH table has wrong permissions")
    guard = [p for p in context.publics if p["symbol"] == "___guard_check_icall_fptr"]
    require(len(guard) == 1 and context.data_contributions.get(guard[0]["address"]) == [4],
            "EH terminate guard pointer lacks its complete storage")
    target_owner_section(context, 0x49ba78, 28, False)
    require(not any(a < 0x49ba78 + 28 and 0x49ba78 <= int(r["span_end"], 0)
                    for a, r in context.boundaries.items()),
            "EH terminate original SEH table overlaps code")
    for side, image, base, table, guard_slot in (
            (0, context.target, 0x47b825, 0x49ba78, 0x48b2bc),
            (1, context.image, candidate, data, guard[0]["address"])):
        thunk, terminate = runtime["___std_terminate"][side], runtime["_terminate"][side]
        require(image.read_address(thunk, 5) == b"\xe9" + struct.pack("<i", terminate - thunk - 5),
                "EH terminate thunk does not reach its independently bound runtime")
        expected = (b"\x6a\x0c\x68" + struct.pack("<I", table) + b"\xe8"
                    + struct.pack("<i", runtime["__SEH_prolog4_GS"][side] - base - 12) + b"\xe8"
                    + struct.pack("<i", runtime["___acrt_getptd"][side] - base - 17)
                    + bytes.fromhex("8b700c85f6741e8365fc008bceff15") + struct.pack("<I", guard_slot)
                    + bytes.fromhex("ffd6eb0733c040c38b65e8c745fcfeffffffe8")
                    + struct.pack("<i", runtime["_abort"][side] - base - 59) + (b"\xcc" if side else b""))
        require(image.read_address(base, len(expected)) == expected,
                "EH complete terminate runtime body or terminal trap differs")
        metadata = struct.pack("<5i2I", -28, 0, -44, 0, -2, base + 40, base + 44)
        require(image.read_address(table, 28) == metadata,
                "EH complete terminate SEH offsets, filter or handler differs")
        # The structure declares 104 bytes even when the original PE directory
        # advertises only 64. This is a storage witness, not a loader-use claim.
        load = image.image_base + image.directories[10][0]
        require(struct.unpack("<I", image.read_address(load, 4))[0] >= 76
                and struct.unpack("<I", image.read_address(load + 72, 4))[0] == guard_slot,
                "EH terminate guard slot differs from its load-config storage witness")
    check_relocations(context.image, runtime["___std_terminate"][1], 5, [])
    check_relocations(context.image, candidate, 60, [3, 32])
    check_relocations(context.image, data, 28, [20, 24])
    return dict(target=0x47b825, size=59, candidate=candidate, candidate_size=60,
                original_seh_table=0x49ba78, candidate_seh_table=data, seh_table_size=28)


def review_terminate(context, record, statics, pdb):
    require(set(record) == {"profile", "source", "parent_symbol", "parent_target", "parent_size",
                            "parent_sha256", "target", "size", "target_sha256", "func_info_target",
                            "func_info_size", "func_info_sha256", "eh_flags", "evidence"}
            and record["profile"] == PROFILE, "unsupported EH terminate declaration")
    source, symbol = record["source"], record["parent_symbol"]
    spec = _SPECS.get((source, symbol))
    require(spec is not None and (record["parent_target"], record["parent_size"], record["size"],
                                  record["func_info_size"], record["eh_flags"])
            == (spec["parent"], spec["size"], 27, 52, 5),
            "EH terminate requires its fixed complete parent and 27/52-byte graph")
    owner, parent = complete_game_entry(context, source, symbol, spec["parent"], spec["size"],
                                        record["parent_sha256"])
    target, info = record["target"], record["func_info_target"]
    extent_hash(context.target, target, 27, record["target_sha256"])
    metadata = extent_hash(context.target, info, 52, record["func_info_sha256"])
    for address, size, code in ((target, 27, True), (info, 52, False)):
        target_owner_section(context, address, size, code)
        require(not any(a < address + size and address <= int(r["span_end"], 0)
                        for a, r in context.boundaries.items()),
                "EH terminate private owner overlaps an original function")
    handler = private_owner(context, statics, pdb, "__ehhandler$" + symbol, source, 27, True)
    descriptor = private_owner(context, statics, pdb, "__unwindtable$" + symbol, source, 52, False,
                               internal_symbols={"__unwindtable$" + symbol: 0,
                                                 "__ehfuncinfo$" + symbol: 16})
    require(handler["module_index"] == descriptor["module_index"] == owner["pdb_module_index"],
            "EH terminate graph leaves its parent PDB module")
    runtime = runtime_entries(context)
    terminate = inspect_terminate(context, statics, pdb, runtime)
    data = descriptor["address"]
    expected = struct.pack("<9IiIiI", 0x19930522, 2, info + 36, 0, 0, 0, 0, 0, 5,
                           -1, runtime["___std_terminate"][0], -1, runtime["___std_terminate"][0])
    candidate_data = struct.pack("<iIiI9I", -1, runtime["___std_terminate"][1],
                                 -1, runtime["___std_terminate"][1],
                                 0x19930522, 2, data, 0, 0, 0, 0, 0, 5)
    require(metadata == expected and context.image.read_address(data, 52) == candidate_data,
            "EH terminate metadata differs from its complete two-state graph")
    for side, image, base, h, fi in ((0, context.target, spec["parent"], target, info),
                                    (1, context.image, parent, handler["address"], data + 16)):
        inspect_handler(image, h, fi, runtime["@__security_check_cookie@4"][side],
                        runtime["___CxxFrameHandler3"][side], cookie_offset=spec["cookie_offset"])
        prefix = inspect_frame(image, base, h, spec)
    fields = linked_code_fields(context.image, context.publics, handler["address"], 27)
    require(fields["decoded_bytes"] == 27 and fields["normalization_complete"]
            and [(f["offset"], f["width"], f["type"]) for f in fields["fields"]]
            == [(13, 4, "REL32"), (18, 4, "DIR32"), (23, 4, "REL32")],
            "EH terminate handler has unreviewed instruction fields")
    check_relocations(context.image, handler["address"], 27, [18])
    check_relocations(context.image, data, 52, [4, 12, 24])
    check_relocations(context.image, parent, prefix, [6, prefix - 16])
    check_relocations(context.image, parent + spec["size"] - 18, 18, [])
    descriptor.update(func_info_offset=16, unwind_offset=0,
                      internal_symbols={"__unwindtable$" + symbol: 0, "__ehfuncinfo$" + symbol: 16})
    return dict(source=source, parent_symbol=symbol, parent_target=spec["parent"],
                parent_size=spec["size"], parent_candidate=parent, target=target,
                handler=handler, func_info_target=info, descriptor=descriptor,
                profile=PROFILE, cookie_offset=spec["cookie_offset"], eh_flags=5,
                terminate=terminate, evidence=record["evidence"])
