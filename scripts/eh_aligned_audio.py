"""Two complete audio EH graphs with stack alignment and dual GS checks."""
import struct

import capstone

from eh_identity import (EHEvidenceError, check_relocations, complete_game_entry, extent_hash, load_config_cookie,
                         private_owner, require, target_owner_section)
from linked_image import linked_code_fields
from runtime_identity import RuntimeEvidenceError, decode_scope


PROFILE = "aligned-audio-allocation-v1"
_SPECS = {
    "?CreateStreaming@CSoundManager@@QAEJPAPAVCStreamingSound@@PBDKU_GUID@@KKPAXPAUThBgmFormat@@@Z":
        dict(parent=0x470320, size=856, code=0x48ab50, info=0x49b6c4, ret=44, push=724,
             saved=737, live=743, ctor=759, instructions=236,
             pointer=[(148, "8975b4"), (642, "8b75b4"), (737, "8945b4")]),
    "?CreateStreamingFromMemory@CSoundManager@@QAEJPAPAVCStreamingSound@@PAEKPAUThBgmFormat@@KU_GUID@@KKPAX@Z":
        dict(parent=0x470680, size=809, code=0x48ab90, info=0x49b6f0, ret=48, push=677,
             saved=690, live=696, ctor=712, instructions=224,
             pointer=[(160, "897db4"), (595, "8b7db4"), (690, "8945b4")]),
}


def inspect_frame(image, parent, handler, allocator, cookie_check, constructor, spec):
    size = spec["size"]
    prefix = (bytes.fromhex("538bdc83ec0883e4f083c404558b6b04896c24048bec6aff68")
              + struct.pack("<I", handler) + bytes.fromhex("64a100000000505383ec78a1")
              + struct.pack("<I", load_config_cookie(image))
              + bytes.fromhex("33c58945ec5657508d45f464a300000000"))
    require(len(prefix) == 62 and image.read_address(parent, 62) == prefix,
            "EH aligned registration, argument base, alignment or dual cookie storage differs")
    suffix = (bytes.fromhex("8b4df464890d00000000595f5e8b4dec33cde8")
              + struct.pack("<I", (cookie_check - parent - size + 9) & 0xffffffff)
              + bytes.fromhex("8be55d8be35bc2") + struct.pack("<H", spec["ret"]))
    require(len(suffix) == 32 and image.read_address(parent + size - 32, 32) == suffix,
            "EH aligned complete restoration, cookie check or RET argument size differs")
    allocation = (bytes.fromhex("68a0000000e8")
                  + struct.pack("<I", (allocator - parent - spec["push"] - 10) & 0xffffffff)
                  + bytes.fromhex("83c40c8945b4ff75bcc745fc000000008bc8")
                  + (b"\x56" if spec["ret"] == 44 else b"\x57")
                  + bytes.fromhex("ff75b0ff75c0e8")
                  + struct.pack("<I", (constructor - parent - spec["ctor"] - 5) & 0xffffffff))
    require(image.read_address(parent + spec["push"], len(allocation)) == allocation,
            "EH aligned allocation, pointer ownership, state activation or constructor differs")
    try:
        instructions, _ = decode_scope(image, parent, size, [0])
    except RuntimeEvidenceError as error:
        raise EHEvidenceError(str(error)) from error
    require(len(instructions) == spec["instructions"], "EH aligned complete control-flow extent differs")
    protected, pointer, fs, ebp, ebx, returns, jumps = [], [], [], [], [], [], []
    # Each protected slot is a whole DWORD. Reject straddling accesses too.
    slots = [-4, -8, -12, -16, -20, -148]
    for i in instructions:
        offset = i.address - parent
        _, writes = i.regs_access()
        if capstone.x86.X86_REG_EBP in writes:
            ebp.append(offset)
        if capstone.x86.X86_REG_EBX in writes:
            ebx.append(offset)
        if i.group(capstone.CS_GRP_RET):
            returns.append(offset)
        if i.group(capstone.CS_GRP_JUMP):
            jumps.append((offset, bytes(i.bytes).hex()))
        for op in i.operands:
            if op.type != capstone.x86.X86_OP_MEM:
                continue
            if op.mem.segment == capstone.x86.X86_REG_FS:
                fs.append(offset)
            if op.mem.base == capstone.x86.X86_REG_EBX:
                require(not op.access & capstone.CS_AC_WRITE,
                        "EH aligned original argument stack is overwritten")
            if op.mem.base != capstone.x86.X86_REG_EBP:
                continue
            require(op.mem.index == 0, "EH aligned frame access has a variable index")
            if any(op.mem.disp < slot + 4 and slot < op.mem.disp + op.size for slot in slots):
                protected.append((offset, bytes(i.bytes).hex()))
            if op.mem.disp < -72 and -76 < op.mem.disp + op.size:
                pointer.append((offset, bytes(i.bytes).hex()))
    require(protected == [(47, "8945ec"), (53, "8d45f4"), (spec["live"], "c745fc00000000"),
                          (size - 32, "8b4df4"), (size - 19, "8b4dec")]
            and pointer == spec["pointer"] and fs == [29, 56, size - 29]
            and ebp == [13, 20, size - 7] and ebx == [1, size - 4] and returns == [size - 3],
            "EH aligned protected slots, pointer lifetime, register bases or returns differ")
    return jumps


def review_aligned_audio(context, record, statics, pdb):
    require(set(record) == {"profile", "source", "parent_symbol", "parent_target", "parent_size",
                            "parent_sha256", "target", "code_target", "size", "target_sha256",
                            "func_info_target", "func_info_size", "func_info_sha256", "eh_flags", "evidence"}
            and record["profile"] == PROFILE, "unsupported aligned audio EH declaration")
    symbol = record["parent_symbol"]
    spec = _SPECS.get(symbol)
    require(spec is not None and record["source"] == "src/DSUtil.cpp"
            and (record["parent_target"], record["parent_size"], record["code_target"], record["target"],
                 record["func_info_target"], record["size"], record["func_info_size"], record["eh_flags"])
            == (spec["parent"], spec["size"], spec["code"], spec["code"] + 18, spec["info"], 58, 44, 1),
            "EH aligned audio requires its fixed complete parent and 58/44-byte aggregates")
    owner, parent = complete_game_entry(context, "src/DSUtil.cpp", symbol, spec["parent"], spec["size"],
                                        record["parent_sha256"])
    code, info = spec["code"], spec["info"]
    extent_hash(context.target, code, 58, record["target_sha256"])
    metadata = extent_hash(context.target, info, 44, record["func_info_sha256"])
    target_owner_section(context, code, 58, True)
    target_owner_section(context, info, 44, False)
    overlaps = {a: r for a, r in context.boundaries.items()
                if a < code + 58 and code <= int(r["span_end"], 0)}
    require(set(overlaps) == {code} and int(overlaps[code]["size"]) == 18
            and int(overlaps[code]["span_end"], 0) == code + 17,
            "EH aligned aggregate conflicts with its complete original cleanup scope")
    require(not any(a < info + 44 and info <= int(r["span_end"], 0)
                    for a, r in context.boundaries.items()), "EH aligned metadata overlaps code")
    action = "__unwindfunclet$" + symbol + "$1"
    names = {action: 0, "__ehhandler$" + symbol: 18}
    data_names = {"__unwindtable$" + symbol: 0, "__ehfuncinfo$" + symbol: 8}
    code_owner = private_owner(context, statics, pdb, action, "src/DSUtil.cpp", 58, True, internal_symbols=names)
    descriptor = private_owner(context, statics, pdb, "__unwindtable$" + symbol,
                               "src/DSUtil.cpp", 44, False, internal_symbols=data_names)
    require(code_owner["module_index"] == descriptor["module_index"] == owner["pdb_module_index"],
            "EH aligned graph leaves the complete parent producer module")
    candidate_code, data = code_owner["address"], descriptor["address"]
    require(metadata == struct.pack("<9IiI", 0x19930522, 1, info + 36, 0, 0, 0, 0, 0, 1, -1, code),
            "EH aligned original metadata is not its complete one-state graph")
    require(context.image.read_address(data, 44) == struct.pack("<iI9I", -1, candidate_code,
            0x19930522, 1, data, 0, 0, 0, 0, 0, 1), "EH aligned complete candidate metadata differs")
    check_relocations(context.image, data, 44, [4, 16])
    runtime = {}
    for name, size in (("??2@YAPAXI@Z", 51), ("??3@YAXPAXI@Z", 14),
                       ("@__security_check_cookie@4", 17), ("___CxxFrameHandler3", 54)):
        binding = context.reviewed_linkages.get(name, {})
        entries = [p for p in context.publics if p["symbol"] == name]
        require(binding.get("kind") == "runtime-function" and binding.get("size") == size and len(entries) == 1,
                "EH aligned runtime role lacks its independently reviewed complete binding")
        runtime[name] = (binding["target"], entries[0]["address"])
    ctor_symbol = "??0CStreamingSound@@QAE@PAUIDirectSoundBuffer@@KPAUCWaveFile@@K@Z"
    # This is an independently complete game owner; it receives no auxiliary credit.
    ctor_hash = "906aa4a35b6f2e5b7ee2bbac32cefe1d0c3739412c17dbdd60b81ba48584062e"
    _, ctor = complete_game_entry(context, "src/DSUtil.cpp", ctor_symbol, 0x471430, 90, ctor_hash)
    jumps = []
    for side, image, base, fi, frame in ((0, context.target, code, info, spec["parent"]),
                                        (1, context.image, candidate_code, data + 8, parent)):
        template = bytearray.fromhex(
            "68a00000008b45b450e80000000083c408c3"
            "8b5424088d420c8b8a78ffffff33c8e8000000008b4af833c8e800000000b800000000e900000000")
        for offset, value in ((10, runtime["??3@YAXPAXI@Z"][side]),
                              (34, runtime["@__security_check_cookie@4"][side]),
                              (44, runtime["@__security_check_cookie@4"][side]),
                              (49, fi), (54, runtime["___CxxFrameHandler3"][side])):
            struct.pack_into("<I", template, offset, (value if offset == 49 else value - base - offset - 4) & 0xffffffff)
        require(len(template) == 58 and image.read_address(base, 58) == bytes(template),
                "EH aligned complete allocation action or dual-cookie handler differs")
        jumps.append(inspect_frame(image, frame, base + 18, runtime["??2@YAPAXI@Z"][side],
                                   runtime["@__security_check_cookie@4"][side], (0x471430, ctor)[side], spec))
    require(jumps[0] == jumps[1], "EH aligned local control flow differs from the original state lifetime")
    fields = linked_code_fields(context.image, context.publics, candidate_code, 58)
    require(fields["decoded_bytes"] == 58 and fields["normalization_complete"]
            and [(f["offset"], f["width"], f["type"]) for f in fields["fields"]]
            == [(10, 4, "REL32"), (34, 4, "REL32"), (44, 4, "REL32"), (49, 4, "DIR32"), (54, 4, "REL32")],
            "EH aligned aggregate contains unreviewed instruction fields")
    check_relocations(context.image, candidate_code, 58, [49])
    check_relocations(context.image, parent, 62, [25, 41])
    check_relocations(context.image, parent + spec["size"] - 32, 32, [])
    code_owner["internal_symbols"] = names
    descriptor.update(internal_symbols=data_names, func_info_offset=8, unwind_offset=0)
    return dict(source="src/DSUtil.cpp", parent_symbol=symbol, parent_target=spec["parent"], parent_size=spec["size"],
                parent_candidate=parent, target=code + 18, profile=PROFILE, handler_field_offset=25,
                handler=dict(symbol="__ehhandler$" + symbol, address=candidate_code + 18,
                             owner_symbol=action, owner_offset=18), code_target=code, code_owner=code_owner,
                func_info_target=info, descriptor=descriptor, allocation_size=160, cookie_offsets=[-136, -8],
                normal_returns=[spec["size"] - 3], return_stack_bytes=spec["ret"], eh_flags=1,
                evidence=record["evidence"])
