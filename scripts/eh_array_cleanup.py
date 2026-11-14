"""Review an array allocation's cleanup state with its terminate entry."""
from __future__ import annotations

import re
import struct

from eh_identity import (check_relocations, complete_game_entry, extent_hash, inspect_handler,
                         load_config_cookie, private_owner, require, target_owner_section)
from linked_image import linked_code_fields


PROFILE = "array-allocation-cleanup-v1"
# `new T[n]` for a T with a constructor and destructor: state 0 protects the
# eh-vector-constructor call and frees the block with sized operator delete[]
# (the overflow-checked n * size + 4 recomputed from the saved count); state 1
# is the vector constructor's terminate entry. Every EBP and FS use is listed.
_SPECS = {
    ("src/Arcfile.cpp", "?parse_directory@Arcfile@@QAEPAUArcfileEntry@@PAEHI@Z"): dict(
        parent=0x4574b0, size=362, locals=bytes.fromhex("83ec0c"), saves=bytes.fromhex("535657"),
        restores=bytes.fromhex("5f5e5b"), ret=bytes.fromhex("c20c00"), count=-0x14, pointer=-0x18,
        element=0x10, cookie_offset=-0x1c, returns=[337, 359],
        frame=[(0, "55"), (1, "8bec"), (10, "64a100000000"), (28, "33c5"), (31, "8d45f4"),
               (34, "64a300000000"), (40, "8b7d0c"), (55, "8975ec"), (88, "8945e8"),
               (91, "c745fc00000000"), (125, "895df0"), (141, "8b7508"), (155, "897d08"),
               (285, "836d0801"), (295, "8b7d0c"), (298, "8b5df0"), (301, "8b4d10"), (320, "8b4df4"),
               (323, "64890d00000000"), (334, "8be5"), (336, "5d"), (342, "8b4df4"),
               (345, "64890d00000000"), (356, "8be5"), (358, "5d")]),
}
_FUNCLET, _HANDLER, _DATA = 45, 27, 52
_RUNTIME = ("??_V@YAXPAXI@Z", "___std_terminate", "@__security_check_cookie@4", "___CxxFrameHandler3")


def _funclet(spec, address, array_delete):
    return (b"\x33\xdb\x8b\x45" + struct.pack("<b", spec["count"]) + b"\xb9" + struct.pack("<I", spec["element"])
            + bytes.fromhex("f7e10f90c3f7db0bd833c083c3040f92c0f7d80bc3508b45") + struct.pack("<b", spec["pointer"])
            + b"\x50\xe8" + struct.pack("<I", (array_delete - address - 41) & 0xFFFFFFFF) + bytes.fromhex("83c408c3"))


def inspect_frame(image, parent, handler, spec):
    import capstone
    prefix = (bytes.fromhex("558bec6aff68") + struct.pack("<I", handler) + bytes.fromhex("64a10000000050")
              + spec["locals"] + spec["saves"] + b"\xa1" + struct.pack("<I", load_config_cookie(image))
              + bytes.fromhex("33c5508d45f464a300000000"))
    suffix = bytes.fromhex("8b4df464890d0000000059") + spec["restores"] + bytes.fromhex("8be55d") + spec["ret"]
    require(image.read_address(parent, len(prefix)) == prefix
            and all(image.read_address(parent + end + len(spec["ret"]) - len(suffix), len(suffix)) == suffix
                    for end in spec["returns"]),
            "EH array cleanup registration, cookie or restoration differs")
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    instructions = list(decoder.disasm(image.read_address(parent, spec["size"]), parent))
    require(sum(i.size for i in instructions) == spec["size"], "EH array cleanup parent decode is incomplete")
    frame, returns = [], []
    for instruction in instructions:
        reads, writes = instruction.regs_access()
        if capstone.x86.X86_REG_EBP in reads + writes or any(
                op.type == capstone.x86.X86_OP_MEM and op.mem.segment == capstone.x86.X86_REG_FS
                for op in instruction.operands):
            frame.append((instruction.address - parent, instruction.bytes.hex()))
        if instruction.group(capstone.CS_GRP_RET):
            returns.append(instruction.address - parent)
    require(frame == spec["frame"] and returns == spec["returns"],
            "EH array cleanup states, saved count/pointer or protected frame uses differ")
    return len(prefix)


def review_array_cleanup(context, record, statics, pdb):
    require(set(record) == {"profile", "source", "parent_symbol", "parent_target", "parent_size",
                            "parent_sha256", "target", "code_target", "size", "target_sha256",
                            "func_info_target", "func_info_size", "func_info_sha256", "eh_flags", "evidence"}
            and record["profile"] == PROFILE, "unsupported EH array cleanup declaration")
    source, symbol = record["source"], record["parent_symbol"]
    spec = _SPECS.get((source, symbol))
    code, info, target = record["code_target"], record["func_info_target"], record["target"]
    require(spec is not None and (record["parent_target"], record["parent_size"], record["size"],
                                  record["func_info_size"], record["eh_flags"])
            == (spec["parent"], spec["size"], _FUNCLET + _HANDLER, _DATA, 1)
            and target == code + _FUNCLET,
            "EH array cleanup requires its fixed complete parent and code/data graph")
    owner, parent = complete_game_entry(context, source, symbol, spec["parent"], spec["size"],
                                        record["parent_sha256"])
    extent_hash(context.target, code, _FUNCLET + _HANDLER, record["target_sha256"])
    metadata = extent_hash(context.target, info, _DATA, record["func_info_sha256"])
    target_owner_section(context, code, _FUNCLET + _HANDLER, True)
    target_owner_section(context, info, _DATA, False)
    overlaps = {a: r for a, r in context.boundaries.items()
                if a < code + _FUNCLET + _HANDLER and code <= int(r["span_end"], 0)}
    require(set(overlaps) == {code} and int(overlaps[code]["size"]) == _FUNCLET,
            "EH array cleanup aggregate conflicts with its original cleanup scope")
    require(not any(a < info + _DATA and info <= int(r["span_end"], 0) for a, r in context.boundaries.items()),
            "EH array cleanup metadata overlaps code")
    funclets = sorted({row["symbol"] for row in statics
                       if re.fullmatch(re.escape("__unwindfunclet$" + symbol) + r"\$\d+", row["symbol"])})
    require(len(funclets) == 1, "EH array cleanup lacks one unique cleanup funclet")
    code_names = {funclets[0]: 0, "__ehhandler$" + symbol: _FUNCLET}
    data_names = {"__unwindtable$" + symbol: 0, "__ehfuncinfo$" + symbol: 16}
    code_owner = private_owner(context, statics, pdb, funclets[0], source, _FUNCLET + _HANDLER, True,
                               internal_symbols=code_names)
    descriptor = private_owner(context, statics, pdb, "__unwindtable$" + symbol, source, _DATA, False,
                               internal_symbols=data_names)
    require(code_owner["module_index"] == descriptor["module_index"] == owner["pdb_module_index"],
            "EH array cleanup graph leaves its parent PDB module")
    runtime = {}
    for name in _RUNTIME:
        binding = context.reviewed_linkages.get(name, {})
        entries = [p for p in context.publics if p["symbol"] == name]
        require(binding.get("kind") == "runtime-function" and len(entries) == 1,
                "EH array cleanup runtime lacks its independent complete binding")
        runtime[name] = (binding["target"], entries[0]["address"])
    candidate_code, candidate_data = code_owner["address"], descriptor["address"]
    terminate = runtime["___std_terminate"]
    require(metadata == struct.pack("<9IiIiI", 0x19930522, 2, info + 36, 0, 0, 0, 0, 0, 1,
                                    -1, code, -1, terminate[0]),
            "EH original metadata is not the complete cleanup/terminate graph")
    require(context.image.read_address(candidate_data, _DATA)
            == struct.pack("<iIiI9I", -1, candidate_code, -1, terminate[1], 0x19930522, 2, candidate_data,
                           0, 0, 0, 0, 0, 1),
            "EH candidate metadata or unwind actions differ")
    for side, image, base, aggregate, fi in ((0, context.target, spec["parent"], code, info),
                                            (1, context.image, parent, candidate_code, candidate_data + 16)):
        require(image.read_address(aggregate, _FUNCLET) == _funclet(spec, aggregate, runtime["??_V@YAXPAXI@Z"][side]),
                "EH array cleanup funclet differs from its saved-count sized array delete")
        inspect_handler(image, aggregate + _FUNCLET, fi, runtime["@__security_check_cookie@4"][side],
                        runtime["___CxxFrameHandler3"][side], cookie_offset=spec["cookie_offset"])
        prefix = inspect_frame(image, base, aggregate + _FUNCLET, spec)
    fields = linked_code_fields(context.image, context.publics, candidate_code, _FUNCLET + _HANDLER)
    require(fields["decoded_bytes"] == _FUNCLET + _HANDLER and fields["normalization_complete"]
            and [(f["offset"], f["width"], f["type"]) for f in fields["fields"]]
            == [(37, 4, "REL32"), (58, 4, "REL32"), (63, 4, "DIR32"), (68, 4, "REL32")],
            "EH array cleanup aggregate has unreviewed instruction fields")
    check_relocations(context.image, candidate_code, _FUNCLET + _HANDLER, [63])
    check_relocations(context.image, candidate_data, _DATA, [4, 12, 24])
    check_relocations(context.image, parent, prefix, [6, prefix - 16])
    code_owner["internal_symbols"] = code_names
    descriptor.update(internal_symbols=data_names, func_info_offset=16, unwind_offset=0)
    return dict(source=source, parent_symbol=symbol, parent_target=spec["parent"], parent_size=spec["size"],
                parent_candidate=parent, target=target, profile=PROFILE,
                handler=dict(symbol="__ehhandler$" + symbol, address=candidate_code + _FUNCLET,
                             owner_symbol=code_owner["symbol"], owner_offset=_FUNCLET),
                code_target=code, code_owner=code_owner, func_info_target=info, descriptor=descriptor,
                cookie_offset=spec["cookie_offset"], eh_flags=1, evidence=record["evidence"])
