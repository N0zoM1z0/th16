"""Review three complete constructor EH aggregates with fixed member cleanup roles."""
from __future__ import annotations

import struct

from eh_identity import (check_relocations, complete_game_entry, inspect_handler,
                         load_config_cookie, require, single_state_owners)
from linked_image import linked_code_fields


PROFILE = "single-member-constructor-v1"
_SPECS = {
    ("src/Stage.cpp", "??0Stage@@QAE@XZ"): {
        "parent": 0x409670, "size": 249, "adjust": bytes.fromhex("83c10c"), "ret": b"\xc3",
        "saves": bytes.fromhex("5657"), "restores": bytes.fromhex("5f5e"),
        "this": bytes.fromhex("8bf9897df0"),
        "cleanup": ("src/Stage.cpp", "??1StageInner@@QAE@XZ", 0x409770, 73),
        "frame": [(0, "55"), (1, "8bec"), (10, "64a100000000"), (27, "33c5"),
                  (30, "8d45f4"), (33, "64a300000000"), (41, "897df0"),
                  (104, "8975ec"), (125, "c745fc00000000"), (189, "8975ec"),
                  (232, "8b4df4"), (235, "64890d00000000"), (245, "8be5"), (247, "5d")],
    },
    ("src/Item.cpp", "??0ItemManager@@QAE@XZ"): {
        "parent": 0x42f0b0, "size": 160, "adjust": bytes.fromhex("83c114"), "ret": b"\xc3",
        "saves": bytes.fromhex("56"), "restores": bytes.fromhex("5e"),
        "this": bytes.fromhex("8bf18975f0"),
        "cleanup": ("src/Item.cpp", "??1ItemManagerInner@@QAE@XZ", 0x42f150, 70),
        "frame": [(0, "55"), (1, "8bec"), (10, "64a100000000"), (26, "33c5"),
                  (29, "8d45f4"), (32, "64a300000000"), (40, "8975f0"),
                  (67, "8945ec"), (96, "c745fc00000000"), (109, "8945ec"),
                  (144, "8b4df4"), (147, "64890d00000000"), (156, "8be5"), (158, "5d")],
    },
    ("src/Ending.cpp", "??0EndingScriptVm@@QAE@PAX@Z"): {
        "parent": 0x4197c0, "size": 551, "adjust": bytes.fromhex("81c1d0000000"), "ret": b"\xc2\x04\x00",
        "saves": bytes.fromhex("5657"), "restores": bytes.fromhex("5f5e"),
        "this": bytes.fromhex("8bf18975f0"),
        "cleanup": ("src/Thread.cpp", "??1ThreadInf@@UAE@XZ", 0x402f20, 11),
        "frame": [(0, "55"), (1, "8bec"), (10, "64a100000000"), (27, "33c5"),
                  (30, "8d45f4"), (33, "64a300000000"), (41, "8975f0"),
                  (182, "c745fc00000000"), (222, "8d45ec"), (324, "8b75f0"), (327, "8b4508"),
                  (532, "8b4df4"), (535, "64890d00000000"), (545, "8be5"), (547, "5d")],
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
    suffix = bytes.fromhex("8b4df464890d0000000059") + spec["restores"] + bytes.fromhex("8be55d") + spec["ret"]
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
    require(frame == spec["frame"] and returns == [size - len(spec["ret"])],
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
    action_size = 8 + len(spec["adjust"]) if spec is not None else 0
    require(spec is not None and record["parent_target"] == spec["parent"]
            and record["parent_size"] == spec["size"] and record["size"] == action_size + 27
            and record["func_info_size"] == 44 and record["eh_flags"] == 1,
            "EH member constructor requires its complete fixed parent and code/data aggregates")
    parent, code, info, handler = spec["parent"], record["code_target"], record["func_info_target"], record["target"]
    candidate_parent, code_owner, descriptor = single_state_owners(context, record, statics, pdb, action_size)
    candidate_code, candidate_data = code_owner["address"], descriptor["address"]
    candidate_info = candidate_data + 8
    entry = record["cleanup_entry"]
    require(set(entry) == {"source", "symbol", "target", "size", "sha256"}
            and (entry["source"], entry["symbol"], entry["target"], entry["size"]) == spec["cleanup"],
            "EH member constructor cleanup differs from its fixed member destructor")
    _, candidate_cleanup = complete_game_entry(context, entry["source"], entry["symbol"], entry["target"],
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
        action = (bytes.fromhex("8b4df0") + spec["adjust"] + b"\xe9"
                  + struct.pack("<I", (cleanup - base - action_size) & 0xffffffff))
        require(image.read_address(base, action_size) == action,
                "EH member constructor complete saved-this cleanup action differs")
        inspect_handler(image, base + action_size, fi, checker, dispatcher, cookie_offset=cookie_offset)
    fields = linked_code_fields(context.image, context.publics, candidate_code, record["size"])
    require(fields["decoded_bytes"] == record["size"] and fields["normalization_complete"]
            and [(f["offset"], f["width"], f["type"]) for f in fields["fields"]]
            == [(action_size - 4, 4, "REL32"), (action_size + 13, 4, "REL32"),
                (action_size + 18, 4, "DIR32"), (action_size + 23, 4, "REL32")],
            "EH member constructor aggregate has unreviewed instruction fields")
    check_relocations(context.image, candidate_code, record["size"], [action_size + 18])
    prefix_size, suffix_size = inspect_frame(context.target, parent, handler, spec)
    require(inspect_frame(context.image, candidate_parent, candidate_code + action_size, spec)
            == (prefix_size, suffix_size), "EH member constructor frame extents differ")
    check_relocations(context.image, candidate_parent, prefix_size, [6, 21 + len(spec["saves"])])
    check_relocations(context.image, candidate_parent + spec["size"] - suffix_size, suffix_size, [])
    return dict(source=source, parent_symbol=symbol, parent_target=parent, parent_size=spec["size"],
                parent_candidate=candidate_parent, target=handler, profile=PROFILE,
                handler=dict(symbol="__ehhandler$" + symbol, address=candidate_code + action_size,
                             owner_symbol=code_owner["symbol"], owner_offset=action_size),
                code_target=code, code_owner=code_owner, func_info_target=info, descriptor=descriptor,
                cleanup_entry=entry, cookie_offset=cookie_offset, eh_flags=1, evidence=record["evidence"])
