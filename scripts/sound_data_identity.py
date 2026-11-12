"""Review the complete sound-table/anchor contribution without splitting its owner."""
import hashlib
from pathlib import Path
import struct

import capstone

from linked_image import _object_path, map_statics, pdb_section_contributions
from runtime_identity import decode_scope, require


PROFILE = "sound-data-aggregate-v1"
SYMBOL = "?g_sound_effect_table@@3PAUSoundEffectData@@A"
_NAMES = {SYMBOL: ("g_sound_effect_table", 0, 1560),
          "?g_anchor_corners_x@@3PAUAnmAnchorCorners@@A": ("g_anchor_corners_x", 1560, 48),
          "?g_anchor_corners_y@@3PAUAnmAnchorCorners@@A": ("g_anchor_corners_y", 1608, 48)}
_WITNESSES = [
    (0x45e150, 145, 43, 0x45e15a, "ae81950d821e797cf375232d2be86bd07e5788614ab06220d63eb5e6ff64255a"),
    (0x45e1f0, 168, 51, 0x45e20d, "b2b36bce5fd046b33f28d5b21a8705da3ff442aa353d205f2036e0992fb8d0ff"),
]


def storage(image, address):
    sections = [s for s in image.sections if image.image_base + s.rva <= address
                and address + 1656 <= image.image_base + s.rva + s.raw_size]
    require(len(sections) == 1 and sections[0].characteristics & 0xc0000000 == 0xc0000000
            and not sections[0].characteristics & 0x20000020,
            "sound aggregate must occupy complete writable raw data")
    require(not any(r < address + 1656 and address < r + 4 for r in image.base_relocations()),
            "sound aggregate has an unexpected or crossing pointer relocation")
    return image.read_address(address, 1656)


def review_sound_data(context, row, candidate):
    require(row["kind"] == PROFILE and row["symbol"] == SYMBOL
            and int(row["target_address"], 0) == 0x4a2a30 and int(row["size"]) == 1656
            and not row["candidate_library"] and not row.get("candidate_size")
            and int(row["witness_instruction"], 0) == 0x45e15a and row["witness_mnemonic"] == "lea-movsx",
            "sound data requires its fixed complete aggregate and original stride witnesses")
    original = storage(context.target, 0x4a2a30)
    require(hashlib.sha256(original).hexdigest() == row["target_sha256"], "sound aggregate original hash differs")
    require(not any(a < 0x4a2a30 + 1656 and 0x4a2a30 <= int(r["span_end"], 0)
                    for a, r in context.boundaries.items()), "sound aggregate overlaps an original code owner")
    records = [struct.unpack_from("<iihhii", original, i * 20) for i in range(78)]
    require(sorted(r[0] for r in records) == list(range(78))
            and all(0 <= r[1] < 67 and -10000 <= r[2] <= 0 and 0 <= r[3] <= 100
                    and r[4] in (0, 1) and r[5] in (0, 1) for r in records),
            "sound aggregate does not contain all 78 complete scalar records")
    anchors = (-0.5, 0.5, -0.5, 0.5, 0, 1, 0, 1, -1, 0, -1, 0,
               -0.5, -0.5, 0.5, 0.5, 0, 0, 1, 1, -1, -1, 0, 0)
    require(original[1560:] == struct.pack("<24f", *anchors),
            "sound aggregate must include both complete adjacent anchor arrays")
    witnesses = []
    for address, size, count, site, expected_hash in _WITNESSES:
        overlaps = [(a, r) for a, r in context.boundaries.items()
                    if a < address + size and address <= int(r["span_end"], 0)]
        require(len(overlaps) == 1 and overlaps[0][0] == address
                and int(overlaps[0][1]["size"]) == size
                and int(overlaps[0][1]["span_end"], 0) == address + size - 1,
                "sound witness lacks its complete independent original owner")
        raw = context.target.read_address(address, size)
        require(hashlib.sha256(raw).hexdigest() == expected_hash, "sound witness complete original hash differs")
        instructions, outside = decode_scope(context.target, address, size, [0])
        require(len(instructions) == count and not outside, "sound witness complete original CFG differs")
        by = {i.address: i for i in instructions}
        lea, load = by.get(site - 3), by.get(site)
        require(lea is not None and bytes(lea.bytes) == bytes.fromhex("8d0492")
                and load is not None and load.mnemonic == "movsx" and load.size == 8
                and load.operands[0].type == capstone.x86.X86_OP_REG and load.operands[0].size == 4,
                "sound witness lacks its complete original five-times-index LEA and signed load")
        op = load.operands[1]
        require(op.type == capstone.x86.X86_OP_MEM and op.size == 2 and not op.mem.base
                and not op.mem.segment and op.mem.index == capstone.x86.X86_REG_EAX
                and op.mem.scale == 4 and op.mem.disp == 0x4a2a3a,
                "sound witness does not read the signed row field at stride 20 and offset ten")
        witnesses.append(dict(parent=address, size=size, instructions=count, read=site,
                              parent_sha256=expected_hash, field_offset=10, stride=20, read_size=2))

    pdb = pdb_section_contributions(context.directory / "th16.pdb")
    entries = [p for p in context.publics if p["symbol"] == SYMBOL]
    require(len(entries) == 1 and entries[0]["address"] == candidate
            and entries[0]["object"] == "SoundData.obj", "sound aggregate lacks its unique source public")
    entry = entries[0]
    section_number, offset = entry["section_number"], entry["section_offset"]
    owners = [r for r in pdb["contributions"]
              if (r["section_number"], r["section_offset"]) == (section_number, offset)]
    require(len(owners) == 1 and owners[0]["size"] == 1656,
            "sound aggregate requires its complete 1656-byte same-start PDB contribution")
    owner = owners[0]
    expected = context.directory / "obj/probes/reference-support/SoundData.obj"
    modules = [r for r in pdb["modules"] if r["index"] == owner["module_index"]]
    require(_object_path(owner["object"]) == _object_path(expected)
            and len(modules) == 1 and _object_path(modules[0]["object"]) == _object_path(expected)
            and modules[0]["module"] == owner["module"]
            and [r for r in pdb["contributions"] if r["module_index"] == owner["module_index"] and r["size"]] == owners
            and owner["characteristics"] & 0xc0000040 == 0xc0000040
            and not owner["characteristics"] & 0x20000020,
            "sound aggregate leaves its single complete SoundData producer contribution")
    section = context.image.section(section_number)
    require(candidate == context.image.image_base + section.rva + offset,
            "sound aggregate MAP VA differs from the PE layout")
    require(not any(r is not owner and r["section_number"] == section_number and r["size"] > 0
                    and r["section_offset"] < offset + 1656 and offset < r["section_offset"] + r["size"]
                    for r in pdb["contributions"]), "sound aggregate overlaps another PDB owner")
    statics = map_statics(context.directory / "th16.map")
    names = [p for p in context.publics + statics if p["section_number"] == section_number
             and offset <= p["section_offset"] < offset + 1656]
    require(sorted((p["symbol"], p["address"] - candidate) for p in names)
            == sorted((name, values[1]) for name, values in _NAMES.items())
            and all(p in context.publics and p["object"] == "SoundData.obj" and not p["flags"]
                    and p["address"] == context.image.image_base + section.rva + p["section_offset"] for p in names),
            "sound aggregate has missing, duplicate, foreign or unreviewed interior MAP names")
    for name, delta, size in _NAMES.values():
        typed = [g for g in context.typed_globals if g["name"] == name]
        require(len(typed) == 1 and typed[0]["address"] == candidate + delta and typed[0]["size"] == size,
                "sound aggregate must retain all three complete typed objects")
    require(storage(context.image, candidate) == original, "sound complete aggregate payload differs")
    return dict(profile=PROFILE, target=0x4a2a30, candidate=candidate, size=1656, table_size=1560,
                names=_NAMES, owner=owner, witnesses=witnesses, complete_data_equal=True,
                bound_symbols=[SYMBOL], primary_exact_credit=0)


def validate_sound_field(field, reviewed):
    require(field.get("type") == "DIR32" and field.get("width") == 4
            and not field.get("local") and not field.get("pointer_limit")
            and field.get("target") == reviewed["target"] and 0 <= field.get("addend", 0) < 1560
            and ("storage_size" not in field or (field["storage_size"] == 1560
                 and field.get("storage_name") == "g_sound_effect_table")),
            "sound identity permits only DIR32 points within the complete sound table")
