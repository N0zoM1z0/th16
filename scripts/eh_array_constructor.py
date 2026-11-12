"""Review the complete BulletManager constructor's first-array unwind graph."""
from __future__ import annotations

import struct

from eh_identity import (check_relocations, complete_game_entry, inspect_handler,
                         load_config_cookie, require, single_state_owners)
from linked_image import linked_code_fields


def inspect_frame(image, parent, handler, constructor_iterator, destructor):
    import capstone
    prefix = (bytes.fromhex("558bec6aff68") + struct.pack("<I", handler)
              + bytes.fromhex("64a10000000050515657a1") + struct.pack("<I", load_config_cookie(image))
              + bytes.fromhex("33c5508d45f464a3000000008bf18975f0"))
    suffix = bytes.fromhex("8b4df464890d00000000595f5e8be55dc3")
    require(image.read_address(parent, 42) == prefix and image.read_address(parent + 164, 17) == suffix,
            "EH Bullet array constructor registration, saved this, cookie or restoration differs")
    dimensions = bytes.fromhex("68d107000068781400008d86")
    for offset, member in ((52, 0x9c), (84, 0x9c + 2001 * 0x1478)):
        require(image.read_address(parent + offset, 16) == dimensions + struct.pack("<I", member),
                "EH Bullet constructor count, stride or complete array range differs")
    for offset in (42, 74):
        require(image.read_address(parent + offset, 5) == b"\x68" + struct.pack("<I", destructor),
                "EH Bullet constructor element destructor differs")
    for offset in (69, 108):
        expected = b"\xe8" + struct.pack("<I", (constructor_iterator - parent - offset - 5) & 0xffffffff)
        require(image.read_address(parent + offset, 5) == expected,
                "EH Bullet constructor lacks its independent array-constructor iterator")
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    instructions = list(decoder.disasm(image.read_address(parent, 181), parent))
    require(sum(i.size for i in instructions) == 181, "EH Bullet array constructor parent decode is incomplete")
    frame, returns = [], []
    for instruction in instructions:
        reads, writes = instruction.regs_access()
        if capstone.x86.X86_REG_EBP in reads + writes or any(
                op.type == capstone.x86.X86_OP_MEM and op.mem.segment == capstone.x86.X86_REG_FS
                for op in instruction.operands):
            frame.append((instruction.address - parent, instruction.bytes.hex()))
        if instruction.group(capstone.CS_GRP_RET):
            returns.append(instruction.address - parent)
    require(frame == [(0, "55"), (1, "8bec"), (10, "64a100000000"), (25, "33c5"),
                      (28, "8d45f4"), (31, "64a300000000"), (39, "8975f0"),
                      (100, "c745fc00000000"), (164, "8b4df4"), (167, "64890d00000000"),
                      (177, "8be5"), (179, "5d")] and returns == [180],
            "EH Bullet array constructor state, saved-this or protected frame uses differ")


def review_array_constructor(context, record, statics, pdb):
    require(set(record) == {"profile", "source", "parent_symbol", "parent_target", "parent_size",
                            "parent_sha256", "target", "code_target", "size", "target_sha256",
                            "func_info_target", "func_info_size", "func_info_sha256", "eh_flags",
                            "evidence", "cleanup_entry"}
            and record["profile"] == "bullet-array-constructor-v1",
            "unsupported EH Bullet array constructor declaration")
    source, symbol = record["source"], record["parent_symbol"]
    require((source, symbol, record["parent_target"], record["parent_size"], record["size"],
             record["func_info_size"], record["eh_flags"])
            == ("src/BulletManager.cpp", "??0BulletManager@@QAE@XZ", 0x411880, 181, 57, 44, 1),
            "EH Bullet array constructor requires its complete fixed parent and 57/44-byte aggregates")
    candidate_parent, code_owner, descriptor = single_state_owners(context, record, statics, pdb, 30)
    code, info = record["code_target"], record["func_info_target"]
    candidate_code, candidate_info = code_owner["address"], descriptor["address"] + 8
    entry = record["cleanup_entry"]
    require(set(entry) == {"source", "symbol", "target", "size", "sha256"}
            and (entry["source"], entry["symbol"], entry["target"], entry["size"])
            == (source, "??1Bullet@@QAE@XZ", 0x4119b0, 120),
            "EH Bullet array cleanup lacks its fixed complete element destructor")
    _, candidate_cleanup = complete_game_entry(context, source, entry["symbol"], entry["target"],
                                               entry["size"], entry["sha256"])
    runtime = []
    for name in ("??_M@YGXPAXIIP6EX0@Z@Z", "??_L@YGXPAXIIP6EX0@Z1@Z",
                 "@__security_check_cookie@4", "___CxxFrameHandler3"):
        binding = context.reviewed_linkages.get(name, {})
        entries = [p for p in context.publics if p["symbol"] == name]
        require(binding.get("kind") == "runtime-function" and len(entries) == 1,
                "EH Bullet array cleanup runtime lacks its independent complete binding")
        runtime.append((binding["target"], entries[0]["address"]))
    for side, image, base, fi, cleanup in ((0, context.target, code, info, entry["target"]),
                                         (1, context.image, candidate_code, candidate_info, candidate_cleanup)):
        action = (b"\x68" + struct.pack("<I", cleanup)
                  + bytes.fromhex("68d107000068781400008b45f0059c00000050e8")
                  + struct.pack("<I", (runtime[0][side] - base - 29) & 0xffffffff) + b"\xc3")
        require(image.read_address(base, 30) == action,
                "EH Bullet array destructor/count/stride/member action differs")
        # One local and saved ESI/EDI place the encoded cookie at EBP-28,
        # sixteen bytes below the EBP-12 registration node.
        inspect_handler(image, base + 30, fi, runtime[2][side], runtime[3][side], cookie_offset=-16)
    fields = linked_code_fields(context.image, context.publics, candidate_code, 57)
    require(fields["decoded_bytes"] == 57 and fields["normalization_complete"]
            and [(f["offset"], f["width"], f["type"]) for f in fields["fields"]]
            == [(1, 4, "DIR32"), (25, 4, "REL32"), (43, 4, "REL32"),
                (48, 4, "DIR32"), (53, 4, "REL32")],
            "EH Bullet array aggregate has unreviewed instruction fields")
    check_relocations(context.image, candidate_code, 57, [1, 48])
    inspect_frame(context.target, 0x411880, record["target"], runtime[1][0], entry["target"])
    inspect_frame(context.image, candidate_parent, candidate_code + 30, runtime[1][1], candidate_cleanup)
    check_relocations(context.image, candidate_parent, 42, [6, 21])
    check_relocations(context.image, candidate_parent + 164, 17, [])
    return dict(source=source, parent_symbol=symbol, parent_target=0x411880, parent_size=181,
                parent_candidate=candidate_parent, target=record["target"], profile=record["profile"],
                handler=dict(symbol="__ehhandler$" + symbol, address=candidate_code + 30,
                             owner_symbol=code_owner["symbol"], owner_offset=30),
                code_target=code, code_owner=code_owner, func_info_target=info, descriptor=descriptor,
                cleanup_entry=entry, array_count=2001, element_stride=0x1478, member_offset=0x9c,
                cookie_offset=-16, eh_flags=1, evidence=record["evidence"])
