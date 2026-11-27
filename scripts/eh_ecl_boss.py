"""Review the ECL boss's sized-Fog-cleanup EH3 graph."""
from __future__ import annotations

from pathlib import Path
import struct

from eh_identity import (EHEvidenceError, check_relocations, extent_hash,
                         private_owner, require)
from linked_image import _object_path, linked_code_fields

PROFILE = "ecl-boss-cleanup-v1"
_SOURCE = "src/EnemyEcl.cpp"
_SYMBOL = "?ecl_run_over_300@EnemyData@@QAEHXZ"
_PARENT = 0x41DCB0
_PARENT_SIZE = 21408
_CODE = 0x48A6B0
_ACTION_SIZE = 18
_HANDLER_SIZE = 40
_INFO = 0x49B274
_DELETE = "??3@YAXPAXI@Z"
_COOKIE = "@__security_check_cookie@4"
_FRAME = "___CxxFrameHandler3"


def _rel(target: int, end: int) -> bytes:
    return struct.pack("<I", (target - end) & 0xFFFFFFFF)


def _complete_parent(context, source: str, symbol: str, target: int, size: int, digest: str):
    """Check the original full boundary and one source-qualified candidate PDB owner."""
    root = Path(__file__).resolve().parents[1]
    path = root / source
    require(source == _SOURCE and path.is_file() and path.suffix == ".cpp"
            and path.resolve().is_relative_to(root / "src")
            and path.relative_to(root).as_posix() == source,
            "ECL EH parent source is not canonical game code")
    boundary = context.boundaries.get(target)
    require(boundary and int(boundary["size"]) == size
            and int(boundary["span_end"], 0) == target + size - 1,
            "ECL EH parent lacks its complete original boundary")
    extent_hash(context.target, target, size, digest)
    owners = [f for f in context.linked["functions"] if f["symbol"] == symbol]
    require(len(owners) == 1 and owners[0]["size"] > 0,
            "ECL EH parent lacks one complete candidate PDB owner")
    owner = owners[0]
    expected = context.directory / "obj" / Path(source).with_suffix(".obj")
    require(_object_path(owner["pdb_object"]) == _object_path(expected),
            "ECL EH parent leaves its source producer object")
    candidate = int(owner["address"], 0)
    publics = [p for p in context.publics if p["symbol"] == symbol]
    require(len(publics) == 1 and publics[0]["address"] == candidate,
            "ECL EH parent lacks one matching public entry")
    return owner, candidate


def _aggregate(image, code: int, info: int, delete: int, cookie: int, frame: int,
               saved_offset: int, node_offset: int, state_offset: int) -> bytes:
    """Build the complete 18-byte sized-delete action and 40-byte EH3 handler."""
    action = (bytes.fromhex("6a1c8b85") + struct.pack("<i", saved_offset) + b"\x50\xe8"
              + _rel(delete, code + 14) + bytes.fromhex("83c408c3"))
    handler = code + _ACTION_SIZE
    tail = (bytes.fromhex("8b5424088d420c8b8a") + struct.pack("<i", node_offset)
            + bytes.fromhex("33c8e8") + _rel(cookie, handler + 20)
            + bytes.fromhex("8b4a") + struct.pack("<b", state_offset)
            + bytes.fromhex("33c8e8") + _rel(cookie, handler + 30)
            + b"\xb8" + struct.pack("<I", info) + b"\xe9"
            + _rel(frame, handler + _HANDLER_SIZE))
    expected = action + tail
    require(len(expected) == _ACTION_SIZE + _HANDLER_SIZE,
            "ECL EH action/handler extent differs")
    return expected


def review_ecl_boss(context, record, statics, pdb):
    require(set(record) == {"profile", "source", "parent_symbol", "parent_target", "parent_size",
                            "parent_sha256", "target", "code_target", "size", "target_sha256",
                            "func_info_target", "func_info_size", "func_info_sha256", "eh_flags", "evidence"}
            and record["profile"] == PROFILE and record["source"] == _SOURCE
            and record["parent_symbol"] == _SYMBOL and record["parent_target"] == _PARENT
            and record["parent_size"] == _PARENT_SIZE and record["code_target"] == _CODE
            and record["target"] == _CODE + _ACTION_SIZE
            and record["size"] == _ACTION_SIZE + _HANDLER_SIZE
            and record["func_info_target"] == _INFO and record["func_info_size"] == 44
            and record["eh_flags"] == 1,
            "ECL EH profile requires the complete reviewed boss/18+40/44-byte graph")
    source, symbol = record["source"], record["parent_symbol"]
    owner, candidate_parent = _complete_parent(context, source, symbol, _PARENT,
                                                _PARENT_SIZE, record["parent_sha256"])
    code, info = record["code_target"], record["func_info_target"]
    extent_hash(context.target, code, record["size"], record["target_sha256"])
    metadata = extent_hash(context.target, info, 44, record["func_info_sha256"])
    require(metadata == struct.pack("<9IiI", 0x19930522, 1, info + 36,
                                    0, 0, 0, 0, 0, 1, -1, code),
            "ECL original FuncInfo is not the complete one-state cleanup graph")
    for address, size, code_owner in ((code, record["size"], True), (info, 44, False)):
        sections = [s for s in context.target.sections
                    if context.target.image_base + s.rva <= address
                    and address + size <= context.target.image_base + s.rva + s.raw_size]
        require(len(sections) == 1, "ECL EH target aggregate leaves one mapped raw section")
        required, forbidden = ((0x60000020, 0x80000000) if code_owner else (0x40000040, 0xA0000020))
        flags = sections[0].characteristics
        require(flags & required == required and not flags & forbidden,
                "ECL EH target aggregate has wrong section permissions")
    overlaps = {a: r for a, r in context.boundaries.items()
                if a < code + record["size"] and code <= int(r["span_end"], 0)}
    require(set(overlaps) == {code} and int(overlaps[code]["size"]) == _ACTION_SIZE
            and int(overlaps[code]["span_end"], 0) == code + _ACTION_SIZE - 1,
            "ECL EH aggregate conflicts with its original cleanup scope")
    require(not any(a < info + 44 and info <= int(r["span_end"], 0)
                    for a, r in context.boundaries.items()),
            "ECL EH FuncInfo overlaps original code")

    funclets = sorted({row["symbol"] for row in statics
                       if row["symbol"].startswith("__unwindfunclet$" + symbol + "$")})
    require(len(funclets) == 1, "ECL EH graph lacks one unique cleanup funclet")
    code_names = {funclets[0]: 0, "__ehhandler$" + symbol: _ACTION_SIZE}
    data_names = {"__unwindtable$" + symbol: 0, "__ehfuncinfo$" + symbol: 8}
    code_owner = private_owner(context, statics, pdb, funclets[0], source,
                               record["size"], True, internal_symbols=code_names)
    descriptor = private_owner(context, statics, pdb, "__unwindtable$" + symbol,
                               source, 44, False, internal_symbols=data_names)
    require(code_owner["module_index"] == descriptor["module_index"] == owner["pdb_module_index"],
            "ECL EH graph leaves its parent PDB module")
    candidate_code, candidate_data = code_owner["address"], descriptor["address"]
    expected_data = struct.pack("<iI9I", -1, candidate_code, 0x19930522, 1, candidate_data,
                                0, 0, 0, 0, 0, 1)
    require(context.image.read_address(candidate_data, 44) == expected_data,
            "ECL candidate FuncInfo or unwind action differs")
    check_relocations(context.image, candidate_data, 44, [4, 16])

    runtime = {}
    for name in (_DELETE, _COOKIE, _FRAME):
        binding = context.reviewed_linkages.get(name, {})
        publics = [p for p in context.publics if p["symbol"] == name]
        require(binding.get("kind") == "runtime-function" and len(publics) == 1,
                "ECL EH runtime lacks its independent complete binding")
        runtime[name] = (binding["target"], publics[0]["address"])
    target_code = _aggregate(context.target, code, info, runtime[_DELETE][0],
                             runtime[_COOKIE][0], runtime[_FRAME][0],
                             -0x420, -0x484, -4)
    candidate_info = candidate_data + 8
    candidate_expected = _aggregate(context.image, candidate_code, candidate_info,
                                    runtime[_DELETE][1], runtime[_COOKIE][1], runtime[_FRAME][1],
                                    -0x410, -0x474, -4)
    require(context.target.read_address(code, record["size"]) == target_code,
            "ECL original Fog cleanup or double-cookie handler differs")
    require(context.image.read_address(candidate_code, record["size"]) == candidate_expected,
            "ECL candidate Fog cleanup or double-cookie handler differs")
    fields = linked_code_fields(context.image, context.publics, candidate_code, record["size"])
    require(fields["decoded_bytes"] == record["size"] and fields["normalization_complete"]
            and [(f["offset"], f["width"], f["type"]) for f in fields["fields"]]
            == [(10, 4, "REL32"), (34, 4, "REL32"), (44, 4, "REL32"),
                (49, 4, "DIR32"), (54, 4, "REL32")],
            "ECL EH aggregate has unreviewed instruction fields")
    check_relocations(context.image, candidate_code, record["size"], [49])
    code_owner["internal_symbols"] = code_names
    descriptor.update(internal_symbols=data_names, func_info_offset=8, unwind_offset=0)
    return dict(source=source, parent_symbol=symbol, parent_target=_PARENT,
                parent_size=_PARENT_SIZE, parent_candidate=candidate_parent,
                candidate_parent_size=owner["size"], target=record["target"], profile=PROFILE,
                handler=dict(symbol="__ehhandler$" + symbol, address=candidate_code + _ACTION_SIZE,
                             owner_symbol=code_owner["symbol"], owner_offset=_ACTION_SIZE),
                code_target=code, code_owner=code_owner, func_info_target=info,
                descriptor=descriptor, eh_flags=1, handler_field_offset=6,
                evidence=record["evidence"])
