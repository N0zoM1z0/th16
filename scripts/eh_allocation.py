"""Review five complete creation-method EH graphs with sized allocation cleanup."""
from __future__ import annotations

import struct

from eh_identity import (check_relocations, inspect_handler, load_config_cookie,
                         require, single_state_owners)
from linked_image import linked_code_fields


PROFILE = "allocation-cleanup-v1"
_LAYOUTS = {
    "stage": dict(locals=bytes.fromhex("83ec08"), local_bytes=8, saves=bytes.fromhex("5657"),
                  restores=bytes.fromhex("5f5e"),
                  middle=[(54, "8945f0"), (59, "c745fc00000000"), (74, "c745fcffffffff")]),
    "manager": dict(locals=bytes.fromhex("51"), local_bytes=4, saves=bytes.fromhex("56"),
                    restores=bytes.fromhex("5e"),
                    middle=[(49, "8945f0"), (54, "c745fc00000000"), (68, "c745fcffffffff")]),
    "replay": dict(locals=bytes.fromhex("51"), local_bytes=4, saves=bytes.fromhex("5657"),
                   restores=bytes.fromhex("5f5e"),
                   middle=[(54, "897df0"), (77, "c745fc00000000"), (106, "c745fcffffffff")]),
}
_SPECS = {
    ("src/Stage.cpp", "?create@Stage@@SAPAU1@PBD@Z"):
        dict(parent=0x409db0, size=156, allocation=0x66f0, push=41, layout="stage", returns=[136, 155]),
    ("src/BulletManager.cpp", "?create@BulletManager@@SAPAU1@XZ"):
        dict(parent=0x411dd0, size=147, allocation=0x1403b28, push=36, layout="manager", returns=[128, 146]),
    ("src/Item.cpp", "?create@ItemManager@@SAPAU1@XZ"):
        dict(parent=0x42f440, size=147, allocation=0x1c972ec, push=36, layout="manager", returns=[128, 146]),
    ("src/ReplayManager.cpp", "?create@ReplayManager@@SAPAU1@H@Z"):
        dict(parent=0x447e20, size=193, allocation=0x31c, push=39, layout="replay", returns=[173, 192]),
    ("src/ReplayManager.cpp", "?create_from_file@ReplayManager@@SAPAU1@PBD@Z"):
        dict(parent=0x447ef0, size=191, allocation=0x31c, push=39, layout="replay", returns=[171, 190]),
}


def inspect_frame(image, parent, handler, allocator, spec):
    """Check allocation, ownership lifetime, cookie storage and both normal exits."""
    import capstone
    layout = _LAYOUTS[spec["layout"]]
    cookie = load_config_cookie(image)
    prefix = (bytes.fromhex("558bec6aff68") + struct.pack("<I", handler)
              + bytes.fromhex("64a10000000050") + layout["locals"] + layout["saves"]
              + b"\xa1" + struct.pack("<I", cookie) + bytes.fromhex("33c5508d45f464a300000000"))
    suffix = bytes.fromhex("8b4df464890d0000000059") + layout["restores"] + bytes.fromhex("8be55dc3")
    require(image.read_address(parent, len(prefix)) == prefix,
            "EH allocation registration, local storage or cookie differs")
    for end in spec["returns"]:
        require(image.read_address(parent + end + 1 - len(suffix), len(suffix)) == suffix,
                "EH allocation normal restoration differs")
    push = spec["push"]
    expected_allocation = (b"\x68" + struct.pack("<I", spec["allocation"]) + b"\xe8"
                           + struct.pack("<I", (allocator - parent - push - 10) & 0xffffffff))
    require(image.read_address(parent + push, 10) == expected_allocation,
            "EH allocation size or independently bound allocator differs")
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    instructions = list(decoder.disasm(image.read_address(parent, spec["size"]), parent))
    require(sum(i.size for i in instructions) == spec["size"],
            "EH allocation frame does not decode the complete parent")
    frame, returns = [], []
    for instruction in instructions:
        reads, writes = instruction.regs_access()
        if capstone.x86.X86_REG_EBP in reads + writes or any(
                op.type == capstone.x86.X86_OP_MEM and op.mem.segment == capstone.x86.X86_REG_FS
                for op in instruction.operands):
            frame.append((instruction.address - parent, instruction.bytes.hex()))
        if instruction.group(capstone.CS_GRP_RET):
            returns.append(instruction.address - parent)
    expected_frame = [(0, "55"), (1, "8bec"), (10, "64a100000000"),
                      (len(prefix) - 12, "33c5"), (len(prefix) - 9, "8d45f4"),
                      (len(prefix) - 6, "64a300000000")] + layout["middle"]
    for end in spec["returns"]:
        start = end + 1 - len(suffix)
        expected_frame.extend([(start, "8b4df4"), (start + 3, "64890d00000000"),
                               (end - 3, "8be5"), (end - 1, "5d")])
    require(frame == expected_frame and returns == spec["returns"],
            "EH allocation saved pointer, state lifetime or protected frame uses differ")
    cookie_field = 18 + len(layout["locals"]) + len(layout["saves"])
    return len(prefix), cookie_field, len(suffix)


def review_allocation(context, record, statics, pdb):
    require(set(record) == {"profile", "source", "parent_symbol", "parent_target", "parent_size",
                            "parent_sha256", "target", "code_target", "size", "target_sha256",
                            "func_info_target", "func_info_size", "func_info_sha256", "eh_flags", "evidence"}
            and record["profile"] == PROFILE, "unsupported EH allocation declaration")
    source, symbol = record["source"], record["parent_symbol"]
    spec = _SPECS.get((source, symbol))
    require(spec is not None and record["parent_target"] == spec["parent"]
            and record["parent_size"] == spec["size"] and record["size"] == 45
            and record["func_info_size"] == 44 and record["eh_flags"] == 1,
            "EH allocation requires its complete fixed parent and 45/44-byte aggregates")
    candidate_parent, code_owner, descriptor = single_state_owners(context, record, statics, pdb, 18)
    code, info = record["code_target"], record["func_info_target"]
    candidate_code, candidate_info = code_owner["address"], descriptor["address"] + 8
    runtime = {}
    for name in ("??2@YAPAXI@Z", "??3@YAXPAXI@Z", "@__security_check_cookie@4", "___CxxFrameHandler3"):
        binding = context.reviewed_linkages.get(name, {})
        entries = [p for p in context.publics if p["symbol"] == name]
        require(binding.get("kind") == "runtime-function" and len(entries) == 1,
                "EH allocation runtime lacks its independent complete binding")
        runtime[name] = (binding["target"], entries[0]["address"])
    layout = _LAYOUTS[spec["layout"]]
    # EBP-12 is the node. Locals, fixed register saves and the encoded cookie
    # derive the displacement; no record may supply an offset or register sequence.
    cookie_offset = -(layout["local_bytes"] + 4 * len(layout["saves"]) + 4)
    for side, image, base, fi in ((0, context.target, code, info),
                                 (1, context.image, candidate_code, candidate_info)):
        action = (b"\x68" + struct.pack("<I", spec["allocation"]) + bytes.fromhex("8b45f050e8")
                  + struct.pack("<I", (runtime["??3@YAXPAXI@Z"][side] - base - 14) & 0xffffffff)
                  + bytes.fromhex("83c408c3"))
        require(image.read_address(base, 18) == action,
                "EH allocation complete sized-delete action differs")
        inspect_handler(image, base + 18, fi, runtime["@__security_check_cookie@4"][side],
                        runtime["___CxxFrameHandler3"][side], cookie_offset=cookie_offset)
    fields = linked_code_fields(context.image, context.publics, candidate_code, 45)
    require(fields["decoded_bytes"] == 45 and fields["normalization_complete"]
            and [(f["offset"], f["width"], f["type"]) for f in fields["fields"]]
            == [(10, 4, "REL32"), (31, 4, "REL32"), (36, 4, "DIR32"), (41, 4, "REL32")],
            "EH allocation aggregate has unreviewed instruction fields")
    check_relocations(context.image, candidate_code, 45, [36])
    inspect_frame(context.target, spec["parent"], record["target"], runtime["??2@YAPAXI@Z"][0], spec)
    prefix, cookie_field, suffix = inspect_frame(context.image, candidate_parent, candidate_code + 18,
                                                runtime["??2@YAPAXI@Z"][1], spec)
    check_relocations(context.image, candidate_parent, prefix, [6, cookie_field])
    for end in spec["returns"]:
        check_relocations(context.image, candidate_parent + end + 1 - suffix, suffix, [])
    return dict(source=source, parent_symbol=symbol, parent_target=spec["parent"], parent_size=spec["size"],
                parent_candidate=candidate_parent, target=record["target"], profile=PROFILE,
                handler=dict(symbol="__ehhandler$" + symbol, address=candidate_code + 18,
                             owner_symbol=code_owner["symbol"], owner_offset=18),
                code_target=code, code_owner=code_owner, func_info_target=info, descriptor=descriptor,
                allocation_size=spec["allocation"], normal_returns=list(spec["returns"]), cookie_offset=cookie_offset,
                eh_flags=1, evidence=record["evidence"])
