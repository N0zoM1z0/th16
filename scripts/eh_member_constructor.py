"""Review the complete single-member EH aggregates of Stage and ItemManager."""
from __future__ import annotations

import struct

from eh_identity import (check_relocations, complete_game_entry, extent_hash, inspect_handler,
                         load_config_cookie, private_owner, require, target_owner_section)
from linked_image import linked_code_fields


PROFILE = "single-member-constructor-v1"
_SPECS = {
    ("src/Stage.cpp", "??0Stage@@QAE@XZ"): {
        "parent": 0x409670, "size": 249, "member": 12,
        "saves": bytes.fromhex("5657"), "restores": bytes.fromhex("5f5e"),
        "this": bytes.fromhex("8bf9897df0"),
        "cleanup": ("??1StageInner@@QAE@XZ", 0x409770, 73),
        "frame": [(0, "55"), (1, "8bec"), (10, "64a100000000"), (27, "33c5"),
                  (30, "8d45f4"), (33, "64a300000000"), (41, "897df0"),
                  (104, "8975ec"), (125, "c745fc00000000"), (189, "8975ec"),
                  (232, "8b4df4"), (235, "64890d00000000"), (245, "8be5"), (247, "5d")],
    },
    ("src/Item.cpp", "??0ItemManager@@QAE@XZ"): {
        "parent": 0x42f0b0, "size": 160, "member": 20,
        "saves": bytes.fromhex("56"), "restores": bytes.fromhex("5e"),
        "this": bytes.fromhex("8bf18975f0"),
        "cleanup": ("??1ItemManagerInner@@QAE@XZ", 0x42f150, 70),
        "frame": [(0, "55"), (1, "8bec"), (10, "64a100000000"), (26, "33c5"),
                  (29, "8d45f4"), (32, "64a300000000"), (40, "8975f0"),
                  (67, "8945ec"), (96, "c745fc00000000"), (109, "8945ec"),
                  (144, "8b4df4"), (147, "64890d00000000"), (156, "8be5"), (158, "5d")],
    },
}


def inspect_frame(image, parent, handler, spec):
    """Check both local words, saved this, the single live state and full restoration."""
    import capstone
    cookie = load_config_cookie(image)
    prefix = (bytes.fromhex("558bec6aff68") + struct.pack("<I", handler)
              + bytes.fromhex("64a1000000005083ec08") + spec["saves"]
              + b"\xa1" + struct.pack("<I", cookie)
              + bytes.fromhex("33c5508d45f464a300000000") + spec["this"])
    suffix = bytes.fromhex("8b4df464890d0000000059") + spec["restores"] + bytes.fromhex("8be55dc3")
    size = spec["size"]
    require(image.read_address(parent, len(prefix)) == prefix
            and image.read_address(parent + size - len(suffix), len(suffix)) == suffix,
            "EH member constructor registration, saved this, cookie or restoration differs")
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    instructions = list(decoder.disasm(image.read_address(parent, size), parent))
    require(sum(i.size for i in instructions) == size,
            "EH member constructor does not decode its complete parent")
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
            "EH member constructor state, saved-this or protected frame uses differ")
    return len(prefix), len(suffix)


def review_member_constructor(context, record, statics, pdb):
    require(set(record) == {"profile", "source", "parent_symbol", "parent_target", "parent_size",
                            "parent_sha256", "target", "code_target", "size", "target_sha256",
                            "func_info_target", "func_info_size", "func_info_sha256", "eh_flags",
                            "evidence", "cleanup_entry"} and record["profile"] == PROFILE,
            "unsupported EH member constructor declaration")
    source, symbol = record["source"], record["parent_symbol"]
    spec = _SPECS.get((source, symbol))
    require(spec is not None and record["parent_target"] == spec["parent"]
            and record["parent_size"] == spec["size"] and record["size"] == 38
            and record["func_info_size"] == 44 and record["eh_flags"] == 1,
            "EH member constructor requires its complete fixed parent and 38/44-byte aggregates")
    parent, code, info, handler = spec["parent"], record["code_target"], record["func_info_target"], record["target"]
    require(handler == code + 11, "EH member constructor handler is not its reviewed interior entry")
    owner, candidate_parent = complete_game_entry(context, source, symbol, parent, spec["size"],
                                                  record["parent_sha256"])
    extent_hash(context.target, code, 38, record["target_sha256"])
    metadata = extent_hash(context.target, info, 44, record["func_info_sha256"])
    target_owner_section(context, code, 38, True)
    target_owner_section(context, info, 44, False)
    overlaps = {a: r for a, r in context.boundaries.items()
                if a < code + 38 and code <= int(r["span_end"], 0)}
    require(set(overlaps) == {code} and int(overlaps[code]["size"]) == 11
            and int(overlaps[code]["span_end"], 0) == code + 10,
            "EH member constructor aggregate conflicts with its original cleanup scope")
    require(not any(a < info + 44 and info <= int(r["span_end"], 0)
                    for a, r in context.boundaries.items()), "EH member constructor metadata overlaps code")
    code_names = {"__unwindfunclet$" + symbol + "$0": 0, "__ehhandler$" + symbol: 11}
    data_names = {"__unwindtable$" + symbol: 0, "__ehfuncinfo$" + symbol: 8}
    code_owner = private_owner(context, statics, pdb, "__unwindfunclet$" + symbol + "$0",
                               source, 38, True, internal_symbols=code_names)
    descriptor = private_owner(context, statics, pdb, "__unwindtable$" + symbol,
                               source, 44, False, internal_symbols=data_names)
    require(code_owner["module_index"] == descriptor["module_index"] == owner["pdb_module_index"],
            "EH member constructor graph leaves its parent PDB module")
    candidate_code, candidate_data = code_owner["address"], descriptor["address"]
    candidate_info = candidate_data + 8
    entry = record["cleanup_entry"]
    require(set(entry) == {"source", "symbol", "target", "size", "sha256"}
            and entry["source"] == source
            and (entry["symbol"], entry["target"], entry["size"]) == spec["cleanup"],
            "EH member constructor cleanup differs from its fixed member destructor")
    _, candidate_cleanup = complete_game_entry(context, source, entry["symbol"], entry["target"],
                                               entry["size"], entry["sha256"])
    runtime = []
    for name in ("@__security_check_cookie@4", "___CxxFrameHandler3"):
        binding = context.reviewed_linkages.get(name, {})
        entries = [p for p in context.publics if p["symbol"] == name]
        require(binding.get("kind") == "runtime-function" and len(entries) == 1,
                "EH member constructor runtime lacks its independent complete binding")
        runtime.append((binding["target"], entries[0]["address"]))
    # Two local words follow the EBP-12 registration node. The fixed register
    # saves and final cookie give node-(12 + 4 * save_count), not a configured offset.
    cookie_offset = -(12 + 4 * len(spec["saves"]))
    for image, base, fi, checker, dispatcher, cleanup in (
            (context.target, code, info, runtime[0][0], runtime[1][0], entry["target"]),
            (context.image, candidate_code, candidate_info, runtime[0][1], runtime[1][1], candidate_cleanup)):
        action = (bytes.fromhex("8b4df083c1") + bytes([spec["member"]]) + b"\xe9"
                  + struct.pack("<I", (cleanup - base - 11) & 0xffffffff))
        require(image.read_address(base, 11) == action,
                "EH member constructor complete saved-this cleanup action differs")
        inspect_handler(image, base + 11, fi, checker, dispatcher, cookie_offset=cookie_offset)
    fields = linked_code_fields(context.image, context.publics, candidate_code, 38)
    require(fields["decoded_bytes"] == 38 and fields["normalization_complete"]
            and [(f["offset"], f["width"], f["type"]) for f in fields["fields"]]
            == [(7, 4, "REL32"), (24, 4, "REL32"), (29, 4, "DIR32"), (34, 4, "REL32")],
            "EH member constructor aggregate has unreviewed instruction fields")
    check_relocations(context.image, candidate_code, 38, [29])
    require(metadata == struct.pack("<9IiI", 0x19930522, 1, info + 36, 0, 0, 0, 0, 0, 1, -1, code),
            "EH member constructor original metadata is not the complete one-state graph")
    # The original stores FuncInfo before the map; the complete candidate PDB
    # object stores the map before FuncInfo. Both full layouts are checked.
    expected_data = struct.pack("<iI9I", -1, candidate_code, 0x19930522, 1, candidate_data,
                                0, 0, 0, 0, 0, 1)
    require(context.image.read_address(candidate_data, 44) == expected_data,
            "EH member constructor complete metadata or unwind action differs")
    check_relocations(context.image, candidate_data, 44, [4, 16])
    prefix_size, suffix_size = inspect_frame(context.target, parent, handler, spec)
    require(inspect_frame(context.image, candidate_parent, candidate_code + 11, spec)
            == (prefix_size, suffix_size), "EH member constructor frame extents differ")
    check_relocations(context.image, candidate_parent, prefix_size, [6, 21 + len(spec["saves"])])
    check_relocations(context.image, candidate_parent + spec["size"] - suffix_size, suffix_size, [])
    code_owner["internal_symbols"] = code_names
    descriptor.update(internal_symbols=data_names, func_info_offset=8, unwind_offset=0)
    return dict(source=source, parent_symbol=symbol, parent_target=parent, parent_size=spec["size"],
                parent_candidate=candidate_parent, target=handler, profile=PROFILE,
                handler=dict(symbol="__ehhandler$" + symbol, address=candidate_code + 11,
                             owner_symbol=code_owner["symbol"], owner_offset=11),
                code_target=code, code_owner=code_owner, func_info_target=info, descriptor=descriptor,
                cleanup_entry=entry, cookie_offset=cookie_offset, eh_flags=1, evidence=record["evidence"])
