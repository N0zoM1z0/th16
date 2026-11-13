"""Review one-state allocation cleanups in GS-buffer frames (stored GS cookie)."""
from __future__ import annotations

import struct

from eh_identity import check_relocations, load_config_cookie, require, single_state_owners
from linked_image import linked_code_fields


PROFILE = "gs-allocation-cleanup-v1"
# Each parent reserves a local buffer (SUB ESP, imm32), stores the GS cookie at
# EBP-16, saves EBX/ESI/EDI and pushes the encoded EH cookie. Every use of the
# saved allocation slot is listed; nothing else may touch the protected slots.
_SPECS = {
    ("src/Gui.cpp", "?start_dialogue@Gui@@QAEXH@Z"):
        dict(parent=0x429ff0, size=470, locals=0x108, allocation=0x1c8, saved=-0x114, push=0x7e,
             uses=[(0x8b, "8985ecfeffff"), (0x91, "c745fc00000000"), (0x1ac, "8d85ecfeffff")],
             returns=[(0x1d3, "c20400")]),
    ("src/MainMenuStates.cpp", "?load_replay_list@TitleInf@@SAXXZ"):
        dict(parent=0x451560, size=475, locals=0x18c, allocation=0x31c, saved=-0x198, push=0x56,
             uses=[(0x65, "89b568feffff"), (0x7f, "c745fc00000000"), (0x9c, "c745fcffffffff"),
                   (0x120, "898568feffff"), (0x17a, "ffb568feffff"), (0x193, "8b8568feffff")],
             returns=[(0x1da, "c3")]),
}
_SUFFIX_HEAD = bytes.fromhex("8b4df464890d00000000595f5e5b8b4df033cde8")
_SUFFIX_TAIL = bytes.fromhex("8be55d")


def _rel(target, end):
    return struct.pack("<I", (target - end) & 0xffffffff)


def inspect_frame(image, parent, handler, allocator, check, spec):
    import capstone
    x86 = capstone.x86
    cookie = load_config_cookie(image)
    prefix = (bytes.fromhex("558bec6aff68") + struct.pack("<I", handler) + bytes.fromhex("64a10000000050")
              + b"\x81\xec" + struct.pack("<I", spec["locals"]) + b"\xa1" + struct.pack("<I", cookie)
              + bytes.fromhex("33c58945f053565750" "8d45f464a300000000"))
    require(image.read_address(parent, len(prefix)) == prefix,
            "EH GS allocation registration, buffer or cookie storage differs")
    push = spec["push"]
    require(image.read_address(parent + push, 10)
            == b"\x68" + struct.pack("<I", spec["allocation"]) + b"\xe8" + _rel(allocator, parent + push + 10),
            "EH GS allocation size or independently bound allocator differs")
    expected = [(1, "8bec"), (10, "64a100000000"), (0x1e, "8945f0"), (0x25, "8d45f4"), (0x28, "64a300000000"),
                *spec["uses"]]
    for end, tail in spec["returns"]:
        start = end - len(_SUFFIX_HEAD) - 4 - len(_SUFFIX_TAIL)
        suffix = _SUFFIX_HEAD + _rel(check, parent + start + len(_SUFFIX_HEAD) + 4) + _SUFFIX_TAIL + bytes.fromhex(tail)
        require(image.read_address(parent + start, len(suffix)) == suffix,
                "EH GS allocation restoration or GS cookie check differs")
        expected += [(start, "8b4df4"), (start + 3, "64890d00000000"), (start + 14, "8b4df0"), (end - 1, "5d")]
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    instructions = list(decoder.disasm(image.read_address(parent, spec["size"]), parent))
    require(sum(i.size for i in instructions) == spec["size"], "EH GS allocation parent is not completely decoded")
    eh_cookie = -(0xc + spec["locals"] + 16)
    protected = {-4, -8, -0xc, -0x10, spec["saved"], eh_cookie}
    observed, returns = [], []
    for instruction in instructions:
        _, writes = instruction.regs_access()
        memory = [op for op in instruction.operands if op.type == x86.X86_OP_MEM]
        if (x86.X86_REG_EBP in writes or any(op.mem.segment == x86.X86_REG_FS for op in memory)
                or any(op.mem.base == x86.X86_REG_EBP and op.mem.disp in protected for op in memory)):
            observed.append((instruction.address - parent, instruction.bytes.hex()))
        if instruction.group(capstone.CS_GRP_RET):
            returns.append(instruction.address - parent)
    require(observed == sorted(expected) and returns == [end for end, _ in spec["returns"]],
            "EH GS allocation saved pointer, state lifetime or protected frame uses differ")
    return eh_cookie + 0xc


def inspect_aggregate(image, code, info, spec, delete, check, frame_handler, node_offset):
    action = (b"\x68" + struct.pack("<I", spec["allocation"]) + b"\x8b\x85" + struct.pack("<i", spec["saved"])
              + b"\x50\xe8" + _rel(delete, code + 17) + bytes.fromhex("83c408c3"))
    handler = code + 21
    expected = (action + bytes.fromhex("8b5424088d420c8b8a") + struct.pack("<i", node_offset)
                + b"\x33\xc8\xe8" + _rel(check, handler + 20) + bytes.fromhex("8b4afc33c8e8")
                + _rel(check, handler + 30) + b"\xb8" + struct.pack("<I", info) + b"\xe9"
                + _rel(frame_handler, handler + 40))
    require(image.read_address(code, 61) == expected,
            "EH GS allocation cleanup or two-cookie handler differs")


def review_gs_allocation(context, record, statics, pdb):
    require(set(record) == {"profile", "source", "parent_symbol", "parent_target", "parent_size",
                            "parent_sha256", "target", "code_target", "size", "target_sha256",
                            "func_info_target", "func_info_size", "func_info_sha256", "eh_flags", "evidence"}
            and record["profile"] == PROFILE, "unsupported EH GS allocation declaration")
    source, symbol = record["source"], record["parent_symbol"]
    spec = _SPECS.get((source, symbol))
    require(spec is not None and record["parent_target"] == spec["parent"] and record["parent_size"] == spec["size"]
            and record["size"] == 61 and record["func_info_size"] == 44 and record["eh_flags"] == 1,
            "EH GS allocation requires its complete fixed parent and 61/44-byte aggregates")
    candidate_parent, code_owner, descriptor = single_state_owners(context, record, statics, pdb, 21, 40)
    runtime = {}
    for name in ("??2@YAPAXI@Z", "??3@YAXPAXI@Z", "@__security_check_cookie@4", "___CxxFrameHandler3"):
        binding = context.reviewed_linkages.get(name, {})
        entries = [p for p in context.publics if p["symbol"] == name]
        require(binding.get("kind") == "runtime-function" and len(entries) == 1,
                "EH GS allocation runtime lacks its independent complete binding")
        runtime[name] = (binding["target"], entries[0]["address"])
    node_offset = -(spec["locals"] + 16)
    candidate_code, candidate_info = code_owner["address"], descriptor["address"] + 8
    for side, image, code, info in ((0, context.target, record["code_target"], record["func_info_target"]),
                                    (1, context.image, candidate_code, candidate_info)):
        inspect_aggregate(image, code, info, spec, runtime["??3@YAXPAXI@Z"][side],
                          runtime["@__security_check_cookie@4"][side], runtime["___CxxFrameHandler3"][side],
                          node_offset)
    fields = linked_code_fields(context.image, context.publics, candidate_code, 61)
    require(fields["decoded_bytes"] == 61 and fields["normalization_complete"]
            and [(f["offset"], f["width"], f["type"]) for f in fields["fields"]]
            == [(13, 4, "REL32"), (37, 4, "REL32"), (47, 4, "REL32"), (52, 4, "DIR32"), (57, 4, "REL32")],
            "EH GS allocation aggregate has unreviewed instruction fields")
    check_relocations(context.image, candidate_code, 61, [52])
    for side, image, parent, handler in ((0, context.target, spec["parent"], record["target"]),
                                         (1, context.image, candidate_parent, candidate_code + 21)):
        require(inspect_frame(image, parent, handler, runtime["??2@YAPAXI@Z"][side],
                              runtime["@__security_check_cookie@4"][side], spec) == node_offset,
                "EH GS allocation cookie displacement differs from its frame")
    check_relocations(context.image, candidate_parent, 0x2e, [6, 0x18])
    return dict(source=source, parent_symbol=symbol, parent_target=spec["parent"], parent_size=spec["size"],
                parent_candidate=candidate_parent, target=record["target"], profile=PROFILE,
                handler=dict(symbol="__ehhandler$" + symbol, address=candidate_code + 21,
                             owner_symbol=code_owner["symbol"], owner_offset=21),
                code_target=record["code_target"], code_owner=code_owner,
                func_info_target=record["func_info_target"], descriptor=descriptor,
                allocation_size=spec["allocation"], normal_returns=[end for end, _ in spec["returns"]],
                cookie_offset=node_offset, eh_flags=1, evidence=record["evidence"])
