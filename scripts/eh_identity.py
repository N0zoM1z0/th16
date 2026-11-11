"""Review the complete, empty x86 EH3 graphs of explicitly named parents."""
from __future__ import annotations

import hashlib
from pathlib import Path
import struct
import tomllib

from linked_image import map_statics, pdb_section_contributions, _object_path


class EHEvidenceError(ValueError):
    """An EH owner or an edge lacks its independently reviewed evidence."""


def require(condition, message):
    if not condition:
        raise EHEvidenceError(message)


def extent_hash(image, address, size, expected):
    payload = image.read_address(address, size)
    require(hashlib.sha256(payload).hexdigest() == expected, "EH target extent hash mismatch")
    return payload


def check_relocations(image, address, size, offsets):
    # Include fields crossing either boundary, and preserve duplicate records.
    observed = [p - address for p in image.base_relocations()
                if p < address + size and address < p + 4]
    require(observed == offsets, "EH owner has missing, extra or crossing PE relocations")


def private_owner(context, statics, pdb, symbol, source, size, code):
    """Join a private name to one complete contribution in its producer object."""
    expected = context.directory / "obj" / Path(source).with_suffix(".obj")
    basename = expected.name.lower()
    matches = [r for r in statics if r["symbol"] == symbol
               and str(r["object"]).replace("\\", "/").rsplit("/", 1)[-1].lower() == basename]
    require(len(matches) == 1, "EH owner lacks one qualified MAP static")
    selected = matches[0]
    section_number, offset = selected["section_number"], selected["section_offset"]
    contributions = [r for r in pdb["contributions"]
                     if (r["section_number"], r["section_offset"]) == (section_number, offset)]
    require(len(contributions) == 1, "EH owner lacks one same-start PDB contribution")
    contribution = contributions[0]
    require(contribution["size"] == size, "EH PDB extent differs from the complete reviewed owner")
    modules = [r for r in pdb["modules"]
               if str(r["object"]).replace("\\", "/").rsplit("/", 1)[-1].lower() == basename]
    require(len(modules) == 1 and modules[0]["index"] == contribution["module_index"]
            and _object_path(contribution["object"]) == _object_path(expected)
            and _object_path(modules[0]["object"]) == _object_path(expected),
            "EH PDB owner leaves its source producer object")
    if any(c in selected["object"] for c in ("/", "\\", ":")):
        require(_object_path(selected["object"]) == _object_path(expected),
                "EH MAP owner leaves its source producer object")
    for other in pdb["contributions"]:
        if other is contribution or other["section_number"] != section_number:
            continue
        require(not (other["size"] > 0 and other["section_offset"] < offset + size
                     and offset < other["section_offset"] + other["size"]),
                "EH owner overlaps another PDB contribution")
    names = [r for r in context.publics + statics if r["section_number"] == section_number
             and offset <= r["section_offset"] < offset + size]
    require(names == [selected], "EH owner has a colliding or interior MAP symbol")
    section = context.image.section(section_number)
    for characteristics in (section.characteristics, contribution["characteristics"]):
        required = 0x60000020 if code else 0x40000040
        forbidden = 0x80000000 if code else 0xA0000020
        require(characteristics & required == required and not characteristics & forbidden,
                "EH owner has wrong code/data section permissions")
    require(("f" in selected["flags"]) == code, "EH static has wrong code/data MAP role")
    address = context.image.image_base + section.rva + offset
    require(address == selected["address"], "EH static VA disagrees with PE section layout")
    context.image.read_address(address, size)
    return dict(symbol=symbol, address=address, size=size, object=contribution["object"],
                module_index=contribution["module_index"], visibility="static")


def inspect_handler(image, address, info, cookie, frame_handler):
    """All 27 bytes: GS frame check, EAX FuncInfo, and the EH3 tail transfer."""
    code = image.read_address(address, 27)
    expected = (bytes.fromhex("8b5424088d420c8b4afc33c8e8")
                + struct.pack("<I", (cookie - address - 17) & 0xFFFFFFFF)
                + b"\xb8" + struct.pack("<I", info) + b"\xe9"
                + struct.pack("<I", (frame_handler - address - 27) & 0xFFFFFFFF))
    require(code == expected, "EH handler differs from its complete GS/FuncInfo/runtime graph")


def inspect_parent(image, address, handler):
    expected = bytes.fromhex("558bec6aff68") + struct.pack("<I", handler) + bytes.fromhex("64a10000000050")
    require(image.read_address(address, len(expected)) == expected,
            "EH parent lacks its fixed frame-registration prologue")


def review_handler(context, record, statics, pdb):
    root = Path(__file__).resolve().parents[1]
    source, symbol = record["source"], record["parent_symbol"]
    path = root / source
    require(path.is_file() and path.suffix == ".cpp" and path.resolve().is_relative_to(root / "src")
            and path.relative_to(root).as_posix() == source, "EH parent source is not canonical game code")
    parent, size = record["parent_target"], record["parent_size"]
    target, info = record["target"], record["func_info_target"]
    require(record["size"] == 27 and record["func_info_size"] == 36 and record["eh_flags"] == 5,
            "EH review supports only the complete 27-byte handler and empty 36-byte descriptor")
    boundary = context.boundaries.get(parent)
    require(boundary and int(boundary["size"]) == size
            and int(boundary["span_end"], 0) == parent + size - 1, "EH parent target extent is not complete")
    extent_hash(context.target, parent, size, record["parent_sha256"])
    extent_hash(context.target, target, 27, record["target_sha256"])
    metadata = extent_hash(context.target, info, 36, record["func_info_sha256"])
    require(struct.unpack("<9I", metadata) == (0x19930522, 0, 0, 0, 0, 0, 0, 0, 5),
            "EH descriptor has nonempty tables or unreviewed flags")
    for address, extent, code in [(target, 27, True), (info, 36, False)]:
        sections = [s for s in context.target.sections
                    if context.target.image_base + s.rva <= address
                    and address + extent <= context.target.image_base + s.rva + s.raw_size]
        require(len(sections) == 1, "EH target owner leaves one mapped raw section")
        flags = sections[0].characteristics
        require(flags & (0x60000020 if code else 0x40000040) == (0x60000020 if code else 0x40000040)
                and not flags & (0x80000000 if code else 0xA0000020), "EH target owner has wrong section permissions")
        require(not any(base < address + extent and address <= int(r["span_end"], 0)
                        for base, r in context.boundaries.items()), "EH target owner overlaps a function boundary")
    owners = [f for f in context.linked["functions"] if f["symbol"] == symbol]
    require(len(owners) == 1 and owners[0]["size"] == size, "EH parent lacks one complete candidate PDB owner")
    owner = owners[0]
    expected = context.directory / "obj" / Path(source).with_suffix(".obj")
    require(_object_path(owner["pdb_object"]) == _object_path(expected), "EH parent has the wrong source object")
    candidate_parent = int(owner["address"], 0)
    publics = [p for p in context.publics if p["symbol"] == symbol]
    require(len(publics) == 1 and publics[0]["address"] == candidate_parent,
            "EH parent lacks one matching public entry")
    handler = private_owner(context, statics, pdb, "__ehhandler$" + symbol, source, 27, True)
    descriptor = private_owner(context, statics, pdb, "__ehfuncinfo$" + symbol, source, 36, False)
    require(handler["module_index"] == descriptor["module_index"] == owner["pdb_module_index"],
            "EH graph leaves its parent PDB module")
    runtime = []
    for name in ("@__security_check_cookie@4", "___CxxFrameHandler3"):
        binding = context.reviewed_linkages.get(name, {})
        entries = [p for p in context.publics if p["symbol"] == name]
        require(binding.get("kind") == "runtime-function" and len(entries) == 1,
                "EH runtime entry lacks its independent complete binding")
        runtime.append((binding["target"], entries[0]["address"]))
    inspect_handler(context.target, target, info, runtime[0][0], runtime[1][0])
    inspect_handler(context.image, handler["address"], descriptor["address"], runtime[0][1], runtime[1][1])
    inspect_parent(context.target, parent, target)
    inspect_parent(context.image, candidate_parent, handler["address"])
    check_relocations(context.image, handler["address"], 27, [18])
    check_relocations(context.image, descriptor["address"], 36, [])
    check_relocations(context.image, candidate_parent, 17, [6])
    require(context.image.read_address(descriptor["address"], 36) == metadata,
            "EH candidate descriptor differs from the complete reviewed empty descriptor")
    return dict(source=source, parent_symbol=symbol, parent_target=parent, parent_size=size,
                parent_candidate=candidate_parent, target=target, handler=handler,
                func_info_target=info, descriptor=descriptor, eh_flags=record["eh_flags"],
                evidence=record["evidence"])


def review_handlers(context, path):
    config = tomllib.loads(path.read_text())
    require(config["schema_version"] == 1, "unsupported EH review schema")
    statics = map_statics(context.directory / "th16.map")
    pdb = pdb_section_contributions(context.directory / "th16.pdb")
    result = {}
    targets = set()
    for record in config["handlers"]:
        key = (record["source"], record["parent_symbol"])
        require(key not in result and record["target"] not in targets, "duplicate EH review")
        result[key] = review_handler(context, record, statics, pdb)
        targets.add(record["target"])
    return result


def handler_field(proof):
    return dict(offset=6, width=4, type="DIR32", symbol=proof["handler"]["symbol"],
                target=proof["target"], addend=0, eh_handler=True)


def validate_field(proofs, unit, field, base):
    proof = proofs.get((unit["source"], unit["symbol"]))
    require(proof is not None and field.get("eh_handler") is True and field == handler_field(proof),
            "EH field lacks its exact reviewed parent-scoped binding")
    require(unit["target_address"] == proof["parent_target"]
            and unit["candidate_address"] == proof["parent_candidate"]
            and unit["compare_size"] == unit.get("size", unit["compare_size"]) == proof["parent_size"]
            and base == proof["handler"]["address"], "EH field leaves its complete reviewed parent graph")
