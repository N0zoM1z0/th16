"""Review fixed one/two-state terminal EH graphs and their terminate entry."""
from __future__ import annotations

import struct

from eh_identity import (check_relocations, complete_game_entry, extent_hash,
                         inspect_handler, load_config_cookie, private_owner,
                         require, target_owner_section)
from linked_image import _object_path, linked_code_fields


PROFILE = "two-state-terminate-v1"
SINGLE_PROFILE = "single-state-terminate-v1"
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
_SINGLE_SPECS = {
    ("src/Arcfile.cpp", "?close@Arcfile@@QAEXXZ"): {
        "parent": 0x457060, "size": 189, "locals": b"", "saves": bytes.fromhex("5657"),
        "restores": bytes.fromhex("5f5e"), "ret": b"\xc3", "flags": 1, "cookie_offset": -12,
        "array_delete": True,
        "frame": [(0, "55"), (1, "8bec"), (10, "64a100000000"), (24, "33c5"),
                  (27, "8d45f4"), (30, "64a300000000"), (103, "c745fc00000000"),
                  (172, "8b4df4"), (175, "64890d00000000"), (185, "8be5"), (187, "5d")],
    },
    ("src/WinMain.cpp", "??_GUpdateFuncRegistry@@QAEPAXI@Z"): {
        "parent": 0x45a3a0, "size": 162, "locals": b"", "saves": bytes.fromhex("5657"),
        "restores": bytes.fromhex("5f5e"), "ret": b"\xc2\x04\x00", "flags": 5, "cookie_offset": -12,
        "deleting_caller": True,
        "frame": [(0, "55"), (1, "8bec"), (10, "64a100000000"), (24, "33c5"),
                  (27, "8d45f4"), (30, "64a300000000"), (43, "c745fc00000000"),
                  (143, "8b4df4"), (146, "64890d00000000"), (156, "8be5"), (158, "5d")],
    },
    ("src/SoundManager.cpp", "?release@SoundManager@@QAEHXZ"): {
        "parent": 0x45d850, "size": 370, "locals": b"", "saves": bytes.fromhex("56"),
        "restores": bytes.fromhex("5e"), "ret": b"\xc3", "flags": 1, "cookie_offset": -8,
        "frame": [(0, "55"), (1, "8bec"), (10, "64a100000000"), (23, "33c5"),
                  (26, "8d45f4"), (29, "64a300000000"), (264, "c745fc00000000"),
                  (354, "8b4df4"), (357, "64890d00000000"), (366, "8be5"), (368, "5d")],
    },
}

GS_SINGLE_PROFILE = "gs-single-state-terminate-v1"
# One terminal state in a frame that also stores a GS cookie at EBP-16 after
# its locals (SUB ESP, imm8) and saves ESI/EDI before pushing the EH cookie.
# The handler checks both cookies. Every EBP and FS use is listed.
_GS_SINGLE_SPECS = {
    ("src/SoundManager.cpp", "?initialize@SoundManager@@QAEHPAUHWND__@@@Z"): {
        "parent": 0x45d510, "size": 708, "locals": 0x54, "saves": bytes.fromhex("5657"),
        "restores": bytes.fromhex("5f5e"), "ret": bytes.fromhex("c20400"), "flags": 1,
        "frame": [(0, "55"), (1, "8bec"), (10, "64a100000000"), (25, "33c5"), (27, "8945f0"),
                  (33, "8d45f4"), (36, "64a300000000"), (44, "8b4508"), (53, "8945b4"),
                  (134, "8975a0"), (187, "ff75b4"), (223, "8d55b8"), (240, "0f1145dc"),
                  (244, "668945e8"), (248, "8d45dc"), (251, "0f1145b8"), (255, "66c745ec0000"),
                  (261, "0f1145c8"), (272, "c745d800000000"), (279, "c745b824000000"),
                  (286, "c745bc08800000"), (293, "c745c000800000"), (300, "c745ea10000000"),
                  (307, "c745dc01000200"), (314, "c745e044ac0000"), (321, "c745e410b10200"),
                  (328, "8945c8"), (348, "8d55ac"), (354, "8d55a8"), (360, "8d55a4"),
                  (364, "8d55b0"), (394, "ff75b0"), (407, "ff75ac"), (412, "ff75a8"),
                  (415, "ff75a4"), (418, "ff75b0"), (439, "8b75b4"), (483, "8945b4"),
                  (529, "ff45b4"), (568, "8b45b4"), (633, "c745fc00000000"), (679, "8b4df4"),
                  (682, "64890d00000000"), (692, "8b4df0"), (695, "33cd"), (702, "8be5"),
                  (704, "5d")],
    },
}
_GS_HANDLER_SIZE = 37


def _rel(target, end):
    return struct.pack("<I", (target - end) & 0xFFFFFFFF)


def inspect_gs_handler(image, address, info, check, frame_handler, eh_cookie):
    """All 37 bytes: the EH and GS cookie checks, EAX FuncInfo and the EH3 tail."""
    require(-128 <= eh_cookie < 0 and eh_cookie % 4 == 0, "unsupported EH GS handler cookie displacement")
    expected = (bytes.fromhex("8b5424088d420c8b4a") + struct.pack("<b", eh_cookie) + bytes.fromhex("33c8e8")
                + _rel(check, address + 17) + bytes.fromhex("8b4afc33c8e8") + _rel(check, address + 27)
                + b"\xb8" + struct.pack("<I", info) + b"\xe9" + _rel(frame_handler, address + 37))
    require(image.read_address(address, _GS_HANDLER_SIZE) == expected,
            "EH GS handler differs from its complete two-cookie/FuncInfo/runtime graph")


def inspect_gs_frame(image, parent, handler, check, spec):
    """Registration, GS cookie and restoration, and every EBP/FS use of the parent."""
    import capstone
    prefix = (bytes.fromhex("558bec6aff68") + struct.pack("<I", handler) + bytes.fromhex("64a10000000050")
              + b"\x83\xec" + struct.pack("<B", spec["locals"]) + b"\xa1"
              + struct.pack("<I", load_config_cookie(image)) + bytes.fromhex("33c58945f0")
              + spec["saves"] + bytes.fromhex("508d45f464a300000000"))
    size, ret = spec["size"], spec["ret"]
    head = bytes.fromhex("8b4df464890d0000000059") + spec["restores"] + bytes.fromhex("8b4df033cde8")
    start = size - len(head) - 4 - 3 - len(ret)
    suffix = head + _rel(check, parent + start + len(head) + 4) + bytes.fromhex("8be55d") + ret
    require(image.read_address(parent, len(prefix)) == prefix
            and image.read_address(parent + start, len(suffix)) == suffix,
            "EH GS terminate parent registration, cookies or restoration differs")
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    instructions = list(decoder.disasm(image.read_address(parent, size), parent))
    require(sum(i.size for i in instructions) == size, "EH GS terminate parent decode is incomplete")
    frame, returns = [], []
    for instruction in instructions:
        reads, writes = instruction.regs_access()
        if capstone.x86.X86_REG_EBP in reads + writes or any(
                op.type == capstone.x86.X86_OP_MEM and op.mem.segment == capstone.x86.X86_REG_FS
                for op in instruction.operands):
            frame.append((instruction.address - parent, instruction.bytes.hex()))
        if instruction.group(capstone.CS_GRP_RET):
            returns.append(instruction.address - parent)
    require(frame == spec["frame"] and returns == [size - len(ret)],
            "EH GS terminate parent states or protected frame uses differ")
    # The EH cookie sits below the locals and saved registers, relative to
    # the registration node at EBP-12.
    return len(prefix), -(spec["locals"] + 4 * len(spec["saves"]) + 4)


def inspect_frame(image, parent, handler, spec):
    import capstone
    prefix = (bytes.fromhex("558bec6aff68") + struct.pack("<I", handler)
              + bytes.fromhex("64a10000000050") + spec["locals"]
              + spec.get("saves", bytes.fromhex("535657")) + b"\xa1"
              + struct.pack("<I", load_config_cookie(image))
              + bytes.fromhex("33c5508d45f464a300000000"))
    ret = spec.get("ret", b"\xc3")
    suffix = (bytes.fromhex("8b4df464890d0000000059")
              + spec.get("restores", bytes.fromhex("5f5e5b")) + bytes.fromhex("8be55d") + ret)
    size = spec["size"]
    require(image.read_address(parent, len(prefix)) == prefix
            and image.read_address(parent + size - len(suffix), len(suffix)) == suffix,
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
    require(frame == spec["frame"] and returns == [size - len(ret)],
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


def inspect_registry_producer(context, parent):
    """One explicit synthetic role emitted in its deleting caller's object."""
    import capstone
    _, caller = complete_game_entry(
        context, "src/WinMain.cpp", "_WinMain@16", 0x459830, 2919,
        "2401bd15572213d5fbf8c5620ebd8fcf64f82e742b9306027e950c3eaca3166a")
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    witnesses = []
    for image, base, destination in ((context.target, 0x459830, 0x45a3a0),
                                      (context.image, caller, parent)):
        instructions = list(decoder.disasm(image.read_address(base, 2919), base))
        require(sum(i.size for i in instructions) == 2919,
                "EH synthetic producer caller decode is incomplete")
        calls = [i for i in instructions if i.mnemonic == "call" and len(i.operands) == 1
                 and i.operands[0].type == capstone.x86.X86_OP_IMM
                 and i.operands[0].imm == destination]
        require(len(calls) == 1 and bytes(calls[0].bytes)[:1] == b"\xe8",
                "EH synthetic producer lacks its unique complete caller witness")
        witnesses.append(calls[0].address - base)
    require(witnesses[0] == 2495, "EH synthetic producer original call leaves its fixed witness")
    return dict(source="src/WinMain.cpp", symbol="_WinMain@16", target=0x459830,
                size=2919, candidate=caller, original_call_offset=2495, candidate_call_offset=witnesses[1])


def inspect_array_delete(context):
    runtime = []
    for name, target, size in (("??_V@YAXPAXI@Z", 0x475134, 14),
                               ("??_V@YAXPAX@Z", 0x475150, 5),
                               ("??3@YAXPAX@Z", 0x47514b, 5)):
        binding = context.reviewed_linkages.get(name, {})
        entries = [p for p in context.publics if p["symbol"] == name]
        require(binding.get("kind") == "runtime-function" and binding.get("target") == target
                and binding.get("size") == size and len(entries) == 1,
                "EH Arcfile array delete lacks its independent complete runtime role")
        runtime.append((target, entries[0]["address"]))
    for side, image in ((0, context.target), (1, context.image)):
        sized, unsized, scalar = (pair[side] for pair in runtime)
        require(image.read_address(sized, 14) == bytes.fromhex("558becff7508e8")
                + struct.pack("<i", unsized - sized - 11) + bytes.fromhex("595dc3")
                and image.read_address(unsized, 5) == b"\xe9" + struct.pack("<i", scalar - unsized - 5),
                "EH Arcfile complete array-delete chain differs")
    for index, size, offset in ((0, 14, 7), (1, 5, 1)):
        address = runtime[index][1]
        fields = linked_code_fields(context.image, context.publics, address, size)
        require(fields["decoded_bytes"] == size and fields["normalization_complete"]
                and [(f["offset"], f["width"], f["type"]) for f in fields["fields"]] == [(offset, 4, "REL32")],
                "EH Arcfile array delete has unreviewed instruction fields")
        check_relocations(context.image, address, size, [])
    return dict(target=0x475134, size=14, candidate=runtime[0][1],
                unsized_target=0x475150, unsized_size=5, unsized_candidate=runtime[1][1])


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
            and record["profile"] in (PROFILE, SINGLE_PROFILE, GS_SINGLE_PROFILE),
            "unsupported EH terminate declaration")
    source, symbol = record["source"], record["parent_symbol"]
    gs = record["profile"] == GS_SINGLE_PROFILE
    single = record["profile"] == SINGLE_PROFILE or gs
    spec = (_GS_SINGLE_SPECS if gs else _SINGLE_SPECS if single else _SPECS).get((source, symbol))
    states = 1 if single else 2
    data_size, map_size = 36 + states * 8, states * 8
    flags = spec.get("flags", 5) if spec is not None else 0
    handler_size = _GS_HANDLER_SIZE if gs else 27
    require(spec is not None and (record["parent_target"], record["parent_size"], record["size"],
                                  record["func_info_size"], record["eh_flags"])
            == (spec["parent"], spec["size"], handler_size, data_size, flags),
            "EH terminate requires its fixed complete parent and code/data graph")
    if single and not gs:
        require(spec["locals"] == b"" and spec["cookie_offset"] == -4 - 4 * len(spec["saves"]),
                "EH single-state cookie must follow the complete no-local saved-register frame")
    owner, parent = complete_game_entry(context, source, symbol, spec["parent"], spec["size"],
                                        record["parent_sha256"])
    target, info = record["target"], record["func_info_target"]
    extent_hash(context.target, target, handler_size, record["target_sha256"])
    metadata = extent_hash(context.target, info, data_size, record["func_info_sha256"])
    for address, size, code in ((target, handler_size, True), (info, data_size, False)):
        target_owner_section(context, address, size, code)
        require(not any(a < address + size and address <= int(r["span_end"], 0)
                        for a, r in context.boundaries.items()),
                "EH terminate private owner overlaps an original function")
    handler = private_owner(context, statics, pdb, "__ehhandler$" + symbol, source, handler_size, True)
    descriptor = private_owner(context, statics, pdb, "__unwindtable$" + symbol, source, data_size, False,
                               internal_symbols={"__unwindtable$" + symbol: 0,
                                                 "__ehfuncinfo$" + symbol: map_size})
    require(handler["module_index"] == descriptor["module_index"] == owner["pdb_module_index"],
            "EH terminate graph leaves its parent PDB module")
    runtime = runtime_entries(context)
    terminate = inspect_terminate(context, statics, pdb, runtime)
    data = descriptor["address"]
    expected = (struct.pack("<9I", 0x19930522, states, info + 36, 0, 0, 0, 0, 0, flags)
                + struct.pack("<iI", -1, runtime["___std_terminate"][0]) * states)
    candidate_data = (struct.pack("<iI", -1, runtime["___std_terminate"][1]) * states
                      + struct.pack("<9I", 0x19930522, states, data, 0, 0, 0, 0, 0, flags))
    require(metadata == expected and context.image.read_address(data, data_size) == candidate_data,
            "EH terminate metadata differs from its complete one/two-state graph")
    for side, image, base, h, fi in ((0, context.target, spec["parent"], target, info),
                                    (1, context.image, parent, handler["address"], data + map_size)):
        check, frame_handler = runtime["@__security_check_cookie@4"][side], runtime["___CxxFrameHandler3"][side]
        if gs:
            prefix, eh_cookie = inspect_gs_frame(image, base, h, check, spec)
            inspect_gs_handler(image, h, fi, check, frame_handler, eh_cookie)
            spec_cookie = eh_cookie
        else:
            inspect_handler(image, h, fi, check, frame_handler, cookie_offset=spec["cookie_offset"])
            prefix = inspect_frame(image, base, h, spec)
    fields = linked_code_fields(context.image, context.publics, handler["address"], handler_size)
    expected_fields = ([(13, 4, "REL32"), (23, 4, "REL32"), (28, 4, "DIR32"), (33, 4, "REL32")] if gs
                       else [(13, 4, "REL32"), (18, 4, "DIR32"), (23, 4, "REL32")])
    require(fields["decoded_bytes"] == handler_size and fields["normalization_complete"]
            and [(f["offset"], f["width"], f["type"]) for f in fields["fields"]] == expected_fields,
            "EH terminate handler has unreviewed instruction fields")
    check_relocations(context.image, handler["address"], handler_size, [28 if gs else 18])
    check_relocations(context.image, data, data_size, list(range(4, map_size, 8)) + [map_size + 8])
    check_relocations(context.image, parent, prefix, [6, 21] if gs else [6, prefix - 16])
    suffix = (len(spec["restores"]) + 24 + len(spec["ret"]) if gs
              else 14 + len(spec.get("restores", bytes.fromhex("5f5e5b"))) + len(spec.get("ret", b"\xc3")))
    check_relocations(context.image, parent + spec["size"] - suffix, suffix, [])
    descriptor.update(func_info_offset=map_size, unwind_offset=0,
                      internal_symbols={"__unwindtable$" + symbol: 0, "__ehfuncinfo$" + symbol: map_size})
    proof = dict(source=source, parent_symbol=symbol, parent_target=spec["parent"],
                parent_size=spec["size"], parent_candidate=parent, target=target,
                handler=handler, func_info_target=info, descriptor=descriptor,
                profile=record["profile"], cookie_offset=spec_cookie if gs else spec["cookie_offset"],
                eh_flags=flags,
                terminate=terminate, evidence=record["evidence"])
    if single:
        proof["producer_source"] = source
        if spec.get("deleting_caller"):
            proof["producer_witness"] = inspect_registry_producer(context, parent)
        elif spec.get("array_delete"):
            proof["array_delete"] = inspect_array_delete(context)
    return proof
