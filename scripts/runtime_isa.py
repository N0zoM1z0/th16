"""Bind the ISA address point through its complete startup and storage graph."""
import hashlib
from pathlib import Path
import struct
import tomllib

import capstone
import pefile

from linked_image import linked_code_fields, map_statics, pdb_section_contributions, _object_path
from runtime_identity import RuntimeEvidenceError, decode_scope, require


PROFILE = "msvc-x86-isa-storage-v1"
KIND = "runtime-global-isa-v1"
_STARTUP = [
    (0x47537b, "e8ab040000", 0x475380), (0x475380, "e98efeffff", 0x475213),
    (0x475213, "6a14", 0x475215), (0x475215, "6818b84900", 0x47521a),
    (0x47521a, "e8b1050000", 0x47521f), (0x47521f, "6a01", 0x475221),
    (0x475221, "e85df8ffff", 0x474a83), (0x474a83, "55", 0x474a84),
    (0x474a84, "8bec", 0x474a86), (0x474a86, "837d0800", 0x474a8a),
    (0x474a8a, "7507", 0x474a93), (0x474a93, "e898090000", 0x475430),
]
_ROLES = {
    "___isa_available": (0x4a65fc, [5, 57, 309, 372, 395]),
    "___favor": (0x4a6600, [205, 214, 222, 282]),
    "___isa_enabled": (0x49ea50, [19, 46, 302, 363, 381, 404]),
}


def relocations(image, address, size, expected):
    require([r - address for r in image.base_relocations()
             if r < address + size and address < r + 4] == expected,
            "ISA graph has missing, duplicate, extra or crossing relocations")


def section(image, address, size, *, zero=False, code=False):
    matches = [s for s in image.sections if image.image_base + s.rva <= address
               and address + size <= image.image_base + s.rva + max(s.raw_size, s.virtual_size)]
    require(len(matches) == 1, "ISA graph leaves one complete mapped section")
    s = matches[0]
    required, forbidden = (0x60000020, 0x80000000) if code else (0xc0000000, 0x20000020)
    require(s.characteristics & required == required and not s.characteristics & forbidden,
            "ISA graph section permissions differ")
    raw_end = image.image_base + s.rva + s.raw_size
    if zero:
        require(raw_end <= address and address + size <= image.image_base + s.rva + s.virtual_size,
                "ISA storage must lie wholly in virtual zero fill")
    else:
        require(address + size <= raw_end, "ISA initialized owner leaves raw storage")


def original_boundary(context, address, size):
    overlapping = [(a, r) for a, r in context.boundaries.items()
                   if a < address + size and address <= int(r["span_end"], 0)]
    require(len(overlapping) == 1 and overlapping[0][0] == address
            and int(overlapping[0][1]["size"]) == size
            and int(overlapping[0][1]["span_end"], 0) == address + size - 1,
            "ISA graph lacks its complete independent original boundary")
    section(context.target, address, size, code=True)


def public(context, name, producer):
    rows = [p for p in context.publics if p["symbol"] == name]
    require(len(rows) == 1 and rows[0]["object"].lower() == producer.lower(),
            "ISA graph lacks its unique pinned public producer")
    return rows[0]


def contribution(context, pdb, statics, entry, size, names, *, code=False, zero=False):
    address = entry["address"]
    section(context.image, address, size, code=code, zero=zero)
    at = (entry["section_number"], entry["section_offset"])
    rows = [r for r in pdb["contributions"] if (r["section_number"], r["section_offset"]) == at]
    require(len(rows) == 1 and rows[0]["size"] == size,
            "ISA graph requires a unique complete same-start PDB contribution")
    row = rows[0]
    s = context.image.section(at[0])
    require(address == context.image.image_base + s.rva + at[1], "ISA MAP VA differs from PE layout")
    required = 0x60000020 if code else 0xc0000080 if zero else 0xc0000040
    forbidden = 0x80000000 if code else 0x20000020
    require(row["characteristics"] & required == required and not row["characteristics"] & forbidden,
            "ISA contribution has wrong storage permissions or initialization kind")
    for other in pdb["contributions"]:
        if other is row or other["section_number"] != at[0]:
            continue
        require(not (other["size"] > 0 and other["section_offset"] < at[1] + size
                     and at[1] < other["section_offset"] + other["size"]),
                "ISA contribution overlaps another owner")
    observed = [p for p in context.publics + statics if p["section_number"] == at[0]
                and at[1] <= p["section_offset"] < at[1] + size]
    require(sorted((p["symbol"], p["address"] - address) for p in observed) == sorted(names.items())
            and all(p in context.publics and p["address"] == context.image.image_base + s.rva + p["section_offset"]
                    and p["object"].lower() == entry["object"].lower()
                    and ("f" in p["flags"]) == code for p in observed),
            "ISA contribution has missing, duplicate or unreviewed interior names")
    modules = [m for m in pdb["modules"] if m["index"] == row["module_index"]]
    require(len(modules) == 1 and modules[0]["module"] == row["module"]
            and _object_path(modules[0]["object"]) == _object_path(row["object"]),
            "ISA contribution disagrees with its PDB producer module")
    return row


def imports(image):
    pe = pefile.PE(data=image.data, fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
    return [(d.dll.lower(), item.name, item.address)
            for d in pe.DIRECTORY_ENTRY_IMPORT for item in d.imports]


def feature_thunk(image, address):
    rows = [r for r in imports(image) if r[:2] == (b"kernel32.dll", b"IsProcessorFeaturePresent")]
    require(len(rows) == 1 and image.read_address(address, 6) == b"\xff\x25" + struct.pack("<I", rows[0][2]),
            "ISA feature dependency is not its complete six-byte imported tail jump")
    section(image, address, 6, code=True)
    return rows[0][2]


def review_isa(context, path):
    config = tomllib.loads(path.read_text())
    require(set(config) == {"isa"}, "unreviewed runtime global declaration")
    row = config["isa"]
    require(set(row) == {"profile", "initializer_target", "initializer_size", "initializer_sha256",
                         "storage_target", "storage_size", "enabled_target", "enabled_size", "evidence"}
            and (row["profile"], row["initializer_target"], row["initializer_size"], row["storage_target"],
                 row["storage_size"], row["enabled_target"], row["enabled_size"])
            == (PROFILE, 0x475430, 415, 0x4a65fc, 8, 0x49ea50, 4),
            "ISA profile requires its complete fixed initializer and both storage owners")
    target = row["initializer_target"]
    original_boundary(context, target, 415)
    original = context.target.read_address(target, 415)
    require(hashlib.sha256(original).hexdigest() == row["initializer_sha256"], "ISA original initializer hash differs")
    pe = pefile.PE(data=context.target.data, fast_load=True)
    require(pe.OPTIONAL_HEADER.AddressOfEntryPoint + context.target.image_base == _STARTUP[0][0],
            "ISA original startup witness does not start at the PE entrypoint")
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    for index, (address, hex_bytes, destination) in enumerate(_STARTUP):
        payload = bytes.fromhex(hex_bytes)
        require(context.target.read_address(address, len(payload)) == payload,
                "ISA original startup witness instruction differs")
        ins = list(decoder.disasm(payload, address))
        require(len(ins) == 1 and ins[0].size == len(payload), "ISA startup witness is not one whole instruction")
        i = ins[0]
        edges = [address + i.size] if i.mnemonic != "jmp" else []
        if i.group(capstone.CS_GRP_CALL) or i.group(capstone.CS_GRP_JUMP):
            require(i.operands[0].type == capstone.x86.X86_OP_IMM, "ISA startup witness has an indirect edge")
            edges.append(i.operands[0].imm)
        require(destination in edges and destination == (_STARTUP[index + 1][0] if index + 1 < len(_STARTUP) else target),
                "ISA startup witness has a disconnected edge")
    instructions, outside = decode_scope(context.target, target, 415, [0])
    require(len(instructions) == 133 and outside == [(25, 0x486aaa)], "ISA initializer graph or feature edge differs")
    original_boundary(context, 0x486aaa, 6)
    original_iat = feature_thunk(context.target, 0x486aaa)
    relocations(context.target, target, 415, [])
    relocations(context.target, 0x486aaa, 6, [])
    section(context.target, 0x4a65fc, 8, zero=True)
    section(context.target, 0x49ea50, 4)
    require(context.target.read_address(0x49ea50, 4) == struct.pack("<I", 1), "ISA original enable mask differs")
    for address, size in ((0x4a65fc, 8), (0x49ea50, 4)):
        require(not any(a < address + size and address <= int(b["span_end"], 0)
                        for a, b in context.boundaries.items()), "ISA original storage overlaps a code owner")
        relocations(context.target, address, size, [])

    pdb = pdb_section_contributions(context.directory / "th16.pdb")
    statics = map_statics(context.directory / "th16.map")
    producer = "LIBCMT:_cpu_disp_.obj"
    entries = {n: public(context, n, producer) for n in ["___isa_available_init", *_ROLES]}
    owners = [f for f in context.linked["functions"] if f["symbol"] == "___isa_available_init"]
    require(len(owners) == 1 and owners[0]["size"] == 415, "ISA initializer lacks one complete linked PDB owner")
    owner = owners[0]
    library = Path(__file__).resolve().parents[1] / ".tools/toolchain/vs/VC/Tools/MSVC/14.10.25017/lib/x86/LIBCMT.lib"
    require(_object_path(owner["pdb_object"]) == _object_path(library)
            and owner["map_object"].lower() == producer.lower()
            and int(owner["address"], 0) == entries["___isa_available_init"]["address"],
            "ISA initializer leaves the pinned LIBCMT producer")
    code = entries["___isa_available_init"]["address"]
    storage, enabled = entries["___isa_available"]["address"], entries["___isa_enabled"]["address"]
    require(entries["___favor"]["address"] == storage + 4, "ISA storage must include the adjacent favor field")
    records = [contribution(context, pdb, statics, entries["___isa_available_init"], 415,
                            {"___isa_available_init": 0}, code=True),
               contribution(context, pdb, statics, entries["___isa_available"], 8,
                            {"___isa_available": 0, "___favor": 4}, zero=True),
               contribution(context, pdb, statics, entries["___isa_enabled"], 4, {"___isa_enabled": 0})]
    require(all(r["module_index"] == owner["pdb_module_index"] and r["module"] == owner["pdb_module"]
                and _object_path(r["object"]) == _object_path(library) for r in records)
            and len([r for r in pdb["contributions"] if r["module_index"] == owner["pdb_module_index"]]) == 3,
            "ISA requires all three complete contributions in its one pinned producer module")
    require(context.image.read_address(enabled, 4) == struct.pack("<I", 1), "ISA complete initialized enable mask differs")
    relocations(context.image, storage, 8, [])
    relocations(context.image, enabled, 4, [])
    thunk = public(context, "_IsProcessorFeaturePresent@4", "kernel32:KERNEL32.dll")
    thunk_row = contribution(context, pdb, statics, thunk, 6, {thunk["symbol"]: 0}, code=True)
    sdk = Path(__file__).resolve().parents[1] / ".tools/toolchain/sdk/Program Files/Microsoft SDKs/Windows/v7.1A/Lib/kernel32.lib"
    require(_object_path(thunk_row["object"]) == _object_path(sdk)
            and thunk_row["module"].lower() == "import:kernel32.dll", "ISA feature thunk leaves its pinned SDK import producer")
    candidate_iat = feature_thunk(context.image, thunk["address"])
    relocations(context.image, thunk["address"], 6, [2])

    fields = linked_code_fields(context.image, context.publics, code, 415)
    roles = {offset: name for name, (_, offsets) in _ROLES.items() for offset in offsets}
    offsets = sorted(roles)
    require(fields["decoded_bytes"] == 415 and fields["normalization_complete"]
            and [(f["offset"], f["width"], f["type"]) for f in fields["fields"]]
            == sorted([(offset, 4, "DIR32") for offset in offsets] + [(26, 4, "REL32")]),
            "ISA complete initializer instruction fields differ")
    expected = bytearray(original)
    for offset, name in roles.items():
        require(struct.unpack_from("<I", original, offset)[0] == _ROLES[name][0], "ISA original storage operand role differs")
        struct.pack_into("<I", expected, offset, entries[name]["address"])
    struct.pack_into("<I", expected, 26, (thunk["address"] - code - 30) & 0xffffffff)
    require(context.image.read_address(code, 415) == bytes(expected), "ISA complete initializer replay differs")
    relocations(context.image, code, 415, offsets)
    binding = dict(target=0x4a65fc, candidate=storage, kind=KIND, storage_size=8, address_point=0,
                   evidence=row["evidence"])
    proof = dict(profile=PROFILE, initializer=owner, target=target, size=415, storage_target=0x4a65fc,
                 storage_candidate=storage, storage_size=8, storage_kind="virtual-zero-fill",
                 enabled_target=0x49ea50, enabled_candidate=enabled, enabled_size=4,
                 contributions=records, import_contribution=thunk_row, original_iat=original_iat,
                 candidate_iat=candidate_iat, startup_witness=_STARTUP, decoded_instructions=133,
                 fields=fields["fields"], relocations=offsets, complete_code_equal=True, primary_exact_credit=0)
    return {"___isa_available": binding}, proof


def validate_isa_field(field, reviewed):
    require(field.get("type") == "DIR32" and field.get("width") == 4
            and not field.get("addend", 0) and not field.get("local") and "storage_size" not in field
            and field.get("target") == reviewed["target"],
            "ISA identity permits only its exact DIR32 address point")
