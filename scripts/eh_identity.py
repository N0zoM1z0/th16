"""Review complete, parent-scoped x86 EH3 graphs with explicit owner profiles."""
from __future__ import annotations

import hashlib
from pathlib import Path
import struct
import tomllib

from linked_image import map_statics, pdb_section_contributions, linked_code_fields, _object_path


_SAVED_REGISTER_PROFILES = {
    "empty-eh3-saved-ebx-esi-edi-v1": (bytes.fromhex("535657"), bytes.fromhex("5f5e5b")),
    "empty-eh3-saved-ebx-esi-v1": (bytes.fromhex("5356"), bytes.fromhex("5e5b")),
}


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


def private_owner(context, statics, pdb, symbol, source, size, code, *, internal_symbols=None):
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
    if internal_symbols is None:
        require(names == [selected], "EH owner has a colliding or interior MAP symbol")
    else:
        observed = sorted((r["symbol"], r["section_offset"] - offset) for r in names)
        require(observed == sorted(internal_symbols.items()),
                "EH aggregate has missing, duplicate, colliding or unreviewed interior MAP symbols")
        require(all(r in statics and r not in context.publics for r in names),
                "EH aggregate internal entries must remain private MAP statics")
        for row in names:
            producer = str(row["object"]).replace("\\", "/")
            require(producer.rsplit("/", 1)[-1].lower() == basename
                    and (not any(c in producer for c in ("/", ":"))
                         or _object_path(row["object"]) == _object_path(expected)),
                    "EH aggregate internal MAP entry leaves its source producer object")
            require(row["address"] == selected["address"] + internal_symbols[row["symbol"]]
                    and ("f" in row["flags"]) == code,
                    "EH aggregate internal MAP entry has wrong VA or code/data role")
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


def inspect_handler(image, address, info, cookie, frame_handler, *, cookie_offset=-4):
    """All 27 bytes: GS frame check, EAX FuncInfo, and the EH3 tail transfer."""
    require(type(cookie_offset) is int and cookie_offset in (-4, -12, -16, -20),
            "unsupported EH handler cookie displacement")
    code = image.read_address(address, 27)
    expected = (bytes.fromhex("8b5424088d420c8b4a") + struct.pack("<b", cookie_offset)
                + bytes.fromhex("33c8e8")
                + struct.pack("<I", (cookie - address - 17) & 0xFFFFFFFF)
                + b"\xb8" + struct.pack("<I", info) + b"\xe9"
                + struct.pack("<I", (frame_handler - address - 27) & 0xFFFFFFFF))
    require(code == expected, "EH handler differs from its complete GS/FuncInfo/runtime graph")


def inspect_parent(image, address, handler):
    expected = bytes.fromhex("558bec6aff68") + struct.pack("<I", handler) + bytes.fromhex("64a10000000050")
    require(image.read_address(address, len(expected)) == expected,
            "EH parent lacks its fixed frame-registration prologue")


def inspect_saved_register_frame(image, address, size, handler, *,
                                 profile="empty-eh3-saved-ebx-esi-edi-v1"):
    """Derive the cookie slot from one of the two explicitly reviewed save sequences."""
    import capstone
    require(isinstance(profile, str) and profile in _SAVED_REGISTER_PROFILES,
            "unsupported saved-register EH frame")
    saves, restores = _SAVED_REGISTER_PROFILES[profile]
    save_count = len(saves)
    cookie = load_config_cookie(image)
    prefix = (bytes.fromhex("558bec6aff68") + struct.pack("<I", handler)
              + bytes.fromhex("64a1000000005051") + saves + b"\xa1" + struct.pack("<I", cookie)
              + bytes.fromhex("33c5508d45f464a300000000"))
    suffix = bytes.fromhex("8b4df464890d0000000059") + restores + bytes.fromhex("8be55dc3")
    require(size >= len(prefix) + len(suffix), "EH saved-register frame exceeds its complete parent")
    require(image.read_address(address, len(prefix)) == prefix
            and image.read_address(address + size - len(suffix), len(suffix)) == suffix,
            "EH saved-register frame registration, cookie or restoration differs")
    # The registration node is EBP-12. One local, the fixed save sequence and
    # the encoded cookie extend the frame to EBP-(20 + 4 * save_count).
    cookie_slot = -(20 + 4 * save_count)
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    instructions = list(decoder.disasm(image.read_address(address, size), address))
    require(sum(i.size for i in instructions) == size,
            "EH saved-register frame does not decode the complete parent")
    protected, fs_uses, frame_writes, returns = [], [], [], []
    for instruction in instructions:
        offset = instruction.address - address
        _, writes = instruction.regs_access()
        if capstone.x86.X86_REG_EBP in writes:
            frame_writes.append(offset)
        if instruction.group(capstone.CS_GRP_RET):
            returns.append(offset)
        for op in instruction.operands:
            if op.type != capstone.x86.X86_OP_MEM:
                continue
            if op.mem.segment == capstone.x86.X86_REG_FS:
                fs_uses.append(offset)
            if op.mem.base == capstone.x86.X86_REG_EBP and op.mem.disp in (-4, -8, -12, cookie_slot):
                protected.append((offset, bytes(instruction.bytes)))
    require(protected == [(26 + save_count, bytes.fromhex("8d45f4")),
                          (size - len(suffix), bytes.fromhex("8b4df4"))]
            and fs_uses == [10, 29 + save_count, size - len(suffix) + 3]
            and frame_writes == [1, size - 2] and returns == [size - 1],
            "EH-sensitive parent frame use differs from the reviewed empty frame")
    return cookie


def review_handler(context, record, statics, pdb):
    if record.get("profile") == "anm-manager-constructor-v1":
        return review_anm_constructor(context, record, statics, pdb)
    if record.get("profile") == "single-member-constructor-v1":
        from eh_member_constructor import review_member_constructor
        return review_member_constructor(context, record, statics, pdb)
    if record.get("profile") == "allocation-cleanup-v1":
        from eh_allocation import review_allocation
        return review_allocation(context, record, statics, pdb)
    profile = record.get("profile")
    require("profile" not in record or isinstance(profile, str) and profile in _SAVED_REGISTER_PROFILES,
            "unsupported EH owner profile")
    saved_registers = profile is not None
    if saved_registers:
        require(set(record) == {"profile", "source", "parent_symbol", "parent_target", "parent_size",
                                "parent_sha256", "target", "size", "target_sha256", "func_info_target",
                                "func_info_size", "func_info_sha256", "eh_flags", "evidence"},
                "unsupported saved-register EH declaration")
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
    save_count = len(_SAVED_REGISTER_PROFILES[profile][0]) if saved_registers else 0
    cookie_offset = -(8 + 4 * save_count) if saved_registers else -4
    inspect_handler(context.target, target, info, runtime[0][0], runtime[1][0], cookie_offset=cookie_offset)
    inspect_handler(context.image, handler["address"], descriptor["address"], runtime[0][1], runtime[1][1],
                    cookie_offset=cookie_offset)
    inspect_parent(context.target, parent, target)
    inspect_parent(context.image, candidate_parent, handler["address"])
    if saved_registers:
        inspect_saved_register_frame(context.target, parent, size, target, profile=profile)
        inspect_saved_register_frame(context.image, candidate_parent, size, handler["address"], profile=profile)
        prefix_size, suffix_size = 35 + save_count, 15 + save_count
        check_relocations(context.image, candidate_parent, prefix_size, [6, 19 + save_count])
        check_relocations(context.image, candidate_parent + size - suffix_size, suffix_size, [])
    check_relocations(context.image, handler["address"], 27, [18])
    check_relocations(context.image, descriptor["address"], 36, [])
    check_relocations(context.image, candidate_parent, 17, [6])
    require(context.image.read_address(descriptor["address"], 36) == metadata,
            "EH candidate descriptor differs from the complete reviewed empty descriptor")
    proof = dict(source=source, parent_symbol=symbol, parent_target=parent, parent_size=size,
                parent_candidate=candidate_parent, target=target, handler=handler,
                func_info_target=info, descriptor=descriptor, eh_flags=record["eh_flags"],
                evidence=record["evidence"])
    if saved_registers:
        proof["profile"] = profile
        proof["cookie_offset"] = cookie_offset
    return proof


def complete_game_entry(context, source, symbol, target, size, target_hash):
    """Bind a reviewed original role to a complete source-qualified public owner."""
    root = Path(__file__).resolve().parents[1]
    path = root / source
    require(path.is_file() and path.suffix == ".cpp"
            and path.resolve().is_relative_to(root / "src")
            and path.relative_to(root).as_posix() == source,
            "EH game entry source is not canonical game code")
    boundary = context.boundaries.get(target)
    require(boundary and int(boundary["size"]) == size
            and int(boundary["span_end"], 0) == target + size - 1,
            "EH game entry lacks its complete original boundary")
    extent_hash(context.target, target, size, target_hash)
    owners = [f for f in context.linked["functions"] if f["symbol"] == symbol]
    require(len(owners) == 1 and owners[0]["size"] == size,
            "EH game entry lacks one complete candidate PDB owner")
    owner = owners[0]
    expected = context.directory / "obj" / Path(source).with_suffix(".obj")
    require(_object_path(owner["pdb_object"]) == _object_path(expected),
            "EH game entry leaves its source producer object")
    address = int(owner["address"], 0)
    publics = [p for p in context.publics if p["symbol"] == symbol]
    require(len(publics) == 1 and publics[0]["address"] == address,
            "EH game entry lacks one matching public entry")
    return owner, address


def target_owner_section(context, address, size, code):
    sections = [s for s in context.target.sections
                if context.target.image_base + s.rva <= address
                and address + size <= context.target.image_base + s.rva + s.raw_size]
    require(len(sections) == 1, "EH aggregate target leaves one mapped raw section")
    required, forbidden = (0x60000020, 0x80000000) if code else (0x40000040, 0xA0000020)
    flags = sections[0].characteristics
    require(flags & required == required and not flags & forbidden,
            "EH aggregate target has wrong section permissions")


def single_state_owners(context, record, statics, pdb, action_size):
    """Check full owners/maps shared by the two explicitly reviewed action lengths."""
    require(action_size in (11, 18) and record["size"] == action_size + 27
            and record["func_info_size"] == 44 and record["eh_flags"] == 1,
            "EH single-state graph lacks its complete fixed aggregates")
    source, symbol = record["source"], record["parent_symbol"]
    parent, size = record["parent_target"], record["parent_size"]
    code, info, handler = record["code_target"], record["func_info_target"], record["target"]
    code_size = action_size + 27
    require(handler == code + action_size, "EH single-state handler is not its reviewed interior entry")
    owner, candidate_parent = complete_game_entry(context, source, symbol, parent, size, record["parent_sha256"])
    extent_hash(context.target, code, code_size, record["target_sha256"])
    metadata = extent_hash(context.target, info, 44, record["func_info_sha256"])
    target_owner_section(context, code, code_size, True)
    target_owner_section(context, info, 44, False)
    overlaps = {a: r for a, r in context.boundaries.items()
                if a < code + code_size and code <= int(r["span_end"], 0)}
    require(set(overlaps) == {code} and int(overlaps[code]["size"]) == action_size
            and int(overlaps[code]["span_end"], 0) == code + action_size - 1,
            "EH single-state aggregate conflicts with its original cleanup scope")
    require(not any(a < info + 44 and info <= int(r["span_end"], 0)
                    for a, r in context.boundaries.items()), "EH single-state metadata overlaps code")
    code_names = {"__unwindfunclet$" + symbol + "$0": 0, "__ehhandler$" + symbol: action_size}
    data_names = {"__unwindtable$" + symbol: 0, "__ehfuncinfo$" + symbol: 8}
    code_owner = private_owner(context, statics, pdb, "__unwindfunclet$" + symbol + "$0",
                               source, code_size, True, internal_symbols=code_names)
    descriptor = private_owner(context, statics, pdb, "__unwindtable$" + symbol,
                               source, 44, False, internal_symbols=data_names)
    require(code_owner["module_index"] == descriptor["module_index"] == owner["pdb_module_index"],
            "EH single-state graph leaves its parent PDB module")
    require(metadata == struct.pack("<9IiI", 0x19930522, 1, info + 36, 0, 0, 0, 0, 0, 1, -1, code),
            "EH original metadata is not the complete one-state graph")
    candidate_code, candidate_data = code_owner["address"], descriptor["address"]
    expected_data = struct.pack("<iI9I", -1, candidate_code, 0x19930522, 1, candidate_data,
                                0, 0, 0, 0, 0, 1)
    require(context.image.read_address(candidate_data, 44) == expected_data,
            "EH complete metadata or single-state unwind action differs")
    check_relocations(context.image, candidate_data, 44, [4, 16])
    code_owner["internal_symbols"] = code_names
    descriptor.update(internal_symbols=data_names, func_info_offset=8, unwind_offset=0)
    return candidate_parent, code_owner, descriptor


def inspect_constructor_frame(image, parent, size, handler, cookie):
    """Check the saved this, GS slot and all EH-sensitive frame uses in the parent."""
    import capstone
    expected = (bytes.fromhex("558bec6aff68") + struct.pack("<I", handler)
                + bytes.fromhex("64a1000000005083ec08535657a1") + struct.pack("<I", cookie)
                + bytes.fromhex("33c5508d45f464a3000000008bf9897dec"))
    require(image.read_address(parent, len(expected)) == expected,
            "EH constructor frame registration, cookie or saved this differs")
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    instructions = list(decoder.disasm(image.read_address(parent, size), parent))
    require(sum(i.size for i in instructions) == size,
            "EH constructor frame scan does not decode the complete parent")
    states = [(i.address - parent, bytes(i.bytes)) for i in instructions
              if any(op.type == capstone.x86.X86_OP_MEM
                     and op.mem.base == capstone.x86.X86_REG_EBP and op.mem.disp == -4
                     for op in i.operands)]
    require(states == [(0x69, bytes.fromhex("c745fc00000000")),
                       (0x90, bytes.fromhex("c645fc01")),
                       (0xbc, bytes.fromhex("c645fc03")),
                       (0xcd, bytes.fromhex("c645fc04"))],
            "EH constructor parent states differ from the reviewed initialization sequence")
    uses = []
    for instruction in instructions:
        reads, writes = instruction.regs_access()
        frame = capstone.x86.X86_REG_EBP in reads + writes or any(
            op.type == capstone.x86.X86_OP_MEM and op.mem.segment == capstone.x86.X86_REG_FS
            for op in instruction.operands)
        if frame:
            uses.append((instruction.address - parent, bytes(instruction.bytes)))
    return uses


def load_config_cookie(image):
    # IMAGE_LOAD_CONFIG_DIRECTORY32.SecurityCookie is the DWORD at offset 60.
    require(len(image.directories) > 10 and image.directories[10][1] >= 64,
            "EH constructor lacks a complete PE32 load-config cookie field")
    address = image.image_base + image.directories[10][0]
    return struct.unpack("<I", image.read_address(address + 60, 4))[0]


def review_anm_constructor(context, record, statics, pdb):
    """One reviewed five-state graph; both entire PDB contributions are required."""
    source, symbol = record["source"], record["parent_symbol"]
    require(source == "src/AnmRender.cpp" and symbol == "??0AnmManager@@QAE@XZ"
            and record["parent_size"] == 5071 and record["size"] == 136
            and record["func_info_size"] == 76 and record["eh_flags"] == 1,
            "EH constructor profile requires its complete 5071/136/76-byte owners")
    parent, size = record["parent_target"], record["parent_size"]
    code, info, handler = record["code_target"], record["func_info_target"], record["target"]
    require(handler == code + 109, "EH constructor handler is not its reviewed interior entry")
    owner, candidate_parent = complete_game_entry(
        context, source, symbol, parent, size, record["parent_sha256"])
    raw_code = extent_hash(context.target, code, 136, record["target_sha256"])
    metadata = extent_hash(context.target, info, 76, record["func_info_sha256"])
    target_owner_section(context, code, 136, True)
    target_owner_section(context, info, 76, False)
    offsets = [0, 8, 38, 68, 82, 109]
    scopes = {code + start: stop - start for start, stop in zip(offsets, offsets[1:] + [136])}
    overlaps = {base: r for base, r in context.boundaries.items()
                if base < code + 136 and code <= int(r["span_end"], 0)}
    require(set(overlaps) == set(scopes) - {handler}
            and all(int(r["size"]) == scopes[base]
                    and int(r["span_end"], 0) == base + scopes[base] - 1
                    for base, r in overlaps.items()),
            "EH constructor aggregate conflicts with its complete original unwind subscopes")
    require(not any(base < info + 76 and info <= int(r["span_end"], 0)
                    for base, r in context.boundaries.items()),
            "EH constructor metadata overlaps an original function")
    code_names = {"__unwindfunclet$" + symbol + "$" + str(i): offset
                  for i, offset in enumerate(offsets[:-1])}
    code_names["__ehhandler$" + symbol] = 109
    data_names = {"__ehfuncinfo$" + symbol: 0, "__unwindtable$" + symbol: 36}
    code_owner = private_owner(context, statics, pdb, "__unwindfunclet$" + symbol + "$0",
                               source, 136, True, internal_symbols=code_names)
    descriptor = private_owner(context, statics, pdb, "__ehfuncinfo$" + symbol,
                               source, 76, False, internal_symbols=data_names)
    require(code_owner["module_index"] == descriptor["module_index"] == owner["pdb_module_index"],
            "EH constructor aggregate leaves its parent PDB module")
    candidate_code, candidate_info = code_owner["address"], descriptor["address"]
    code_owner["internal_symbols"] = code_names
    descriptor["internal_symbols"] = data_names
    runtime = {}
    for name in ("??_M@YGXPAXIIP6EX0@Z@Z", "@__security_check_cookie@4", "___CxxFrameHandler3"):
        binding = context.reviewed_linkages.get(name, {})
        publics = [p for p in context.publics if p["symbol"] == name]
        require(binding.get("kind") == "runtime-function" and len(publics) == 1,
                "EH constructor runtime lacks its independent complete binding")
        runtime[name] = (binding["target"], publics[0]["address"])
    expected_callees = [("src/Thread.cpp", "??1ThreadInf@@UAE@XZ", 11),
                        ("src/AnmManagerVms.cpp", "??1AnmFastVm@@QAE@XZ", 61),
                        ("src/AnmVm.cpp", "??1AnmVm@@QAE@XZ", 61)]
    require([(r["source"], r["symbol"], r["size"]) for r in record["cleanup_entries"]] == expected_callees,
            "EH constructor cleanup entries differ from the reviewed destructor roles")
    cleanup = {}
    for entry in record["cleanup_entries"]:
        _, address = complete_game_entry(context, entry["source"], entry["symbol"], entry["target"],
                                         entry["size"], entry["sha256"])
        cleanup[entry["symbol"]] = (entry["target"], address)
    # Every byte outside these proven fields is compared literally. Field offsets
    # describe complete instruction operands, not masks or arbitrary local labels.
    destinations = {4: cleanup[expected_callees[0][1]], 9: cleanup[expected_callees[1][1]],
                    33: runtime["??_M@YGXPAXIIP6EX0@Z@Z"], 39: cleanup[expected_callees[1][1]],
                    63: runtime["??_M@YGXPAXIIP6EX0@Z@Z"], 78: cleanup[expected_callees[2][1]],
                    83: cleanup[expected_callees[2][1]], 104: runtime["??_M@YGXPAXIIP6EX0@Z@Z"],
                    122: runtime["@__security_check_cookie@4"], 127: (info, candidate_info),
                    132: runtime["___CxxFrameHandler3"]}
    absolute = [9, 39, 83, 127]
    # Serialize the reviewed instructions, including saved-this displacements,
    # array counts/strides/object offsets, GS displacement and every terminator.
    template = bytes.fromhex(
        "8b4dece900000000"
        "680000000068ff1f000068140600008b45ec05ec00000050e800000000c3"
        "680000000068ff1f000068140600008b45ec05f07ac20050e800000000c3"
        "8b4dec81c1acf58401e900000000"
        "68000000006a2b68fc0500008b45ec0530fcc60150e800000000c3"
        "8b5424088d420c8b4ae833c8e800000000b800000000e900000000")
    original_code, expected_code = bytearray(template), bytearray(template)
    for offset, (original, candidate) in destinations.items():
        observed = struct.unpack_from("<I", raw_code, offset)[0]
        if offset not in absolute:
            observed = (observed + code + offset + 4) & 0xFFFFFFFF
            candidate = (candidate - candidate_code - offset - 4) & 0xFFFFFFFF
        require(observed == original, "EH constructor original edge has an unreviewed destination")
        original_value = original if offset in absolute else (original - code - offset - 4) & 0xFFFFFFFF
        struct.pack_into("<I", original_code, offset, original_value)
        struct.pack_into("<I", expected_code, offset, candidate)
    require(raw_code == bytes(original_code), "EH constructor original action/handler instructions differ")
    check_relocations(context.image, candidate_code, 136, absolute)
    fields = linked_code_fields(context.image, context.publics, candidate_code, 136)
    require(fields["decoded_bytes"] == 136 and fields["normalization_complete"]
            and [(f["offset"], f["width"], f["type"]) for f in fields["fields"]]
            == [(p, 4, "DIR32" if p in absolute else "REL32") for p in sorted(destinations)],
            "EH constructor aggregate has an unreviewed instruction field")
    require(context.image.read_address(candidate_code, 136) == bytes(expected_code),
            "EH constructor complete action/handler code differs")

    def descriptor_bytes(base, actions):
        return (struct.pack("<9I", 0x19930522, 5, base + 36, 0, 0, 0, 0, 0, 1)
                + b"".join(struct.pack("<iI", state - 1, actions + offset)
                           for state, offset in enumerate(offsets[:-1])))
    require(metadata == descriptor_bytes(info, code),
            "EH constructor original state map is not the complete reviewed chain")
    check_relocations(context.image, candidate_info, 76, [8, 40, 48, 56, 64, 72])
    require(context.image.read_address(candidate_info, 76) == descriptor_bytes(candidate_info, candidate_code),
            "EH constructor complete metadata or state/action map differs")
    cookies = [p for p in context.publics if p["symbol"] == "___security_cookie"]
    require(len(cookies) == 1 and cookies[0]["object"] == "LIBCMT:gs_cookie.obj",
            "EH constructor cookie lacks its unique pinned runtime storage role")
    require(record["cookie_target"] == load_config_cookie(context.target)
            and cookies[0]["address"] == load_config_cookie(context.image),
            "EH constructor cookie differs from the PE load-config identity")
    frame = inspect_constructor_frame(context.target, parent, size, handler, record["cookie_target"])
    candidate_frame = inspect_constructor_frame(context.image, candidate_parent, size,
                                                 candidate_code + 109, cookies[0]["address"])
    require(frame == candidate_frame, "EH constructor EH-sensitive frame uses differ")
    check_relocations(context.image, candidate_parent, 45, [6, 24])
    return dict(source=source, parent_symbol=symbol, parent_target=parent, parent_size=size,
                parent_candidate=candidate_parent, target=handler, profile=record["profile"],
                handler=dict(symbol="__ehhandler$" + symbol, address=candidate_code + 109,
                             owner_offset=109, owner_symbol=code_owner["symbol"]),
                code_target=code, code_owner=code_owner, func_info_target=info, descriptor=descriptor,
                cleanup_entries=record["cleanup_entries"], eh_flags=1, evidence=record["evidence"])


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
