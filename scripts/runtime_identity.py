"""Explicit interior CALL identities backed by complete runtime contributions."""
import hashlib
from pathlib import Path
import struct
import tomllib

import capstone

from linked_image import linked_code_fields, pdb_section_contributions


class RuntimeEvidenceError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise RuntimeEvidenceError(message)


def decode_scope(image, address, size, entries):
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    instructions = list(decoder.disasm(image.read_address(address, size), address))
    require(sum(i.size for i in instructions) == size, "runtime scope does not decode completely")
    by = {i.address: i for i in instructions}
    pending, seen, outside = [address + n for n in entries], set(), []
    while pending:
        at = pending.pop()
        if at in seen:
            continue
        require(at in by, "runtime edge leaves an instruction start")
        i = by[at]
        seen.add(at)
        if i.group(capstone.CS_GRP_RET):
            continue
        if i.group(capstone.CS_GRP_CALL) and i.operands[0].type == capstone.x86.X86_OP_IMM:
            destination = i.operands[0].imm
            if destination in by:
                pending.append(destination)
            else:
                outside.append((i.address - address, destination))
        if i.group(capstone.CS_GRP_JUMP):
            require(i.operands[0].type == capstone.x86.X86_OP_IMM
                    and i.operands[0].imm in by, "runtime jump leaves its complete owner")
            pending.append(i.operands[0].imm)
            if i.mnemonic == "jmp":
                continue
        pending.append(at + i.size)
    require(all((i.mnemonic, i.op_str) in {("mov", "edi, edi"), ("lea", "esp, [esp]")}
                for i in instructions if i.address not in seen), "runtime scope has unreviewed unreachable bytes")
    return instructions, outside


def readonly(image, address, size):
    require(any(not s.characteristics & (0x20 | 0x80000000)
                and image.image_base + s.rva <= address
                and address + size <= image.image_base + s.rva + s.raw_size
                for s in image.sections), "runtime data leaves complete read-only storage")
    require(not any(address - 3 <= r < address + size for r in image.base_relocations()),
            "runtime constant contribution contains a relocation")
    return image.read_address(address, size)


def review_runtime_interiors(context, path):
    config = tomllib.loads(path.read_text())
    require(set(config) == {"objects"} and "ftol3" in config["objects"]
            and set(config["objects"]) <= {"ftol3", "fmod", "atan2"}
            and ("atan2" not in config["objects"] or "fmod" in config["objects"]),
            "unreviewed runtime contribution declaration")
    row = config["objects"]["ftol3"]
    require(set(row) == {"profile", "target_address", "code_size", "code_sha256", "data_address",
                         "data_size", "data_sha256", "entries", "evidence"}
            and row["profile"] == "msvc-x86-ftol3-v1", "unreviewed runtime interior profile")
    require(row["code_size"] == 887 and row["data_size"] == 130,
            "runtime profile requires both complete contribution extents")
    target, data_target = row["target_address"], row["data_address"]
    require(type(target) is int and type(data_target) is int, "runtime addresses must be integral")
    original = context.target.read_address(target, 887)
    require(hashlib.sha256(original).hexdigest() == row["code_sha256"], "runtime original code hash differs")
    pool = readonly(context.target, data_target, 130)
    require(hashlib.sha256(pool).hexdigest() == row["data_sha256"], "runtime original data hash differs")
    require(context.target.read_address(target - 8, 8) == b"\xcc" * 8
            and context.target.read_address(target + 887, 9) == b"\xcc" * 9,
            "runtime original contribution lacks its complete padding anchors")
    instructions, outside = decode_scope(context.target, target, 887, [0, 15, 30, 481, 496, 511, 784, 848])
    exception = context.reviewed_linkages.get("__except1", {})
    require(exception.get("kind") == "runtime-function" and exception.get("size") == 206
            and outside == [(470, exception.get("target"))], "runtime exception edge lacks its reviewed complete callee")

    owners = [f for f in context.linked["functions"] if f["symbol"] == "__ftoui3"]
    require(len(owners) == 1 and owners[0]["size"] == 887, "runtime lacks one complete candidate code owner")
    owner = owners[0]
    root = Path(__file__).resolve().parents[1]
    library = root / ".tools/toolchain/vs/VC/Tools/MSVC/14.10.25017/lib/x86/LIBCMT.lib"
    normalize = lambda p: str(p).replace("\\", "/").lower()
    require(normalize(owner["pdb_object"]) == normalize("Z:" + str(library))
            and owner["map_object"].lower() == "libcmt:_ftol3_.obj",
            "runtime candidate leaves the pinned LIBCMT producer")
    contributions = [c for c in pdb_section_contributions(context.directory / "th16.pdb")["contributions"]
                     if c["module_index"] == owner["pdb_module_index"]]
    code_records = [c for c in contributions if c["characteristics"] & 0x20]
    data_records = [c for c in contributions if not c["characteristics"] & 0x20]
    require(len(contributions) == 2 and len(code_records) == len(data_records) == 1
            and code_records[0]["size"] == 887 and data_records[0]["size"] == 130
            and all(normalize(c["object"]) == normalize(owner["pdb_object"])
                    and c["module"] == owner["pdb_module"] for c in contributions),
            "runtime requires both complete code/data PDB contributions from one producer")
    address = int(owner["address"], 0)
    code_record, data_record = code_records[0], data_records[0]
    require(context.image.image_base + context.image.section(code_record["section_number"]).rva
            + code_record["section_offset"] == address, "runtime code contribution starts elsewhere")
    data_address = (context.image.image_base + context.image.section(data_record["section_number"]).rva
                    + data_record["section_offset"])
    require(readonly(context.image, data_address, 130) == pool, "complete runtime data replay differs")

    original_fields = linked_code_fields(context.target, [], target, 887)["fields"]
    memory_ranges = []
    for i in instructions:
        if i.mnemonic == "lea" and i.op_str == "esp, [esp]" and bytes(i.bytes) == bytes.fromhex("8da42400000000"):
            continue  # Owned alignment is replayed raw, not treated as a memory read.
        for op in i.operands:
            if op.type == capstone.x86.X86_OP_MEM and i.disp_size == 4:
                require(data_target <= op.mem.disp < data_target + 130,
                        "runtime memory displacement leaves its reviewed pool")
                original_fields.append(dict(offset=i.address-target+i.disp_offset, width=4, type="DIR32"))
                memory_ranges.append((op.mem.disp, op.mem.disp + op.size))
    require(min(a for a, _ in memory_ranges) == data_target
            and max(b for _, b in memory_ranges) == data_target + 130,
            "runtime original pool differs from its decoded read extent")
    fields = linked_code_fields(context.image, context.publics, address, 887)
    require(fields["normalization_complete"] and fields["decoded_bytes"] == 887
            and len(fields["fields"]) == 24
            and sorted((f["offset"], f["width"], f["type"]) for f in fields["fields"])
            == sorted((f["offset"], f["width"], f["type"]) for f in original_fields),
            "runtime linked fields differ from the complete original field set")
    relocations = {r-address for r in context.image.base_relocations() if r < address+887 and r+4 > address}
    require(relocations == {f["offset"] for f in fields["fields"] if f["type"] == "DIR32"}
            and len(relocations) == 23
            and not any(target-3 <= r < target+887 for r in context.target.base_relocations()),
            "runtime PE relocation footprint differs")
    patched = bytearray(context.image.read_address(address, 887))
    for field in fields["fields"]:
        if field["type"] == "DIR32":
            require(data_address <= field["candidate_target"] < data_address+130,
                    "runtime candidate field leaves its complete data owner")
            value = data_target + field["candidate_target"] - data_address
        else:
            require(field["type"] == "REL32" and field["offset"] == 471
                    and field["candidate_symbols"] == ["__except1"], "unreviewed runtime external edge")
            value = exception["target"] - (target + field["instruction_end"])
        struct.pack_into("<I", patched, field["offset"], value & 0xffffffff)
    require(bytes(patched) == original, "complete runtime code replay differs")

    allowed = {"__dtoul3": 496, "__ltod3": 848}
    bindings = {}
    for entry in row["entries"]:
        require(set(entry) == {"symbol", "offset", "witness_parent", "witness_parent_sha256", "witnesses"},
                "unsupported runtime entry declaration")
        symbol, offset = entry["symbol"], entry["offset"]
        require(symbol in allowed and offset == allowed[symbol] and symbol not in bindings,
                "unreviewed or duplicate runtime interior entry")
        publics = [p for p in context.publics if p["symbol"] == symbol]
        require(len(publics) == 1 and publics[0]["address"] == address + offset
                and publics[0]["object"].lower() == "libcmt:_ftol3_.obj", "runtime interior public differs from its producer offset")
        parent = entry["witness_parent"]
        boundary = context.boundaries.get(parent)
        require(boundary is not None and entry["witnesses"], "runtime entry lacks original call witnesses")
        size = int(boundary["size"])
        require(int(boundary["span_end"], 0) == parent+size-1
                and hashlib.sha256(context.target.read_address(parent, size)).hexdigest() == entry["witness_parent_sha256"],
                "runtime witness requires its complete original parent hash")
        sequence, _ = decode_scope(context.target, parent, size, [0])
        by = {i.address: i for i in sequence}
        require(len(set(entry["witnesses"])) == len(entry["witnesses"]), "duplicate runtime call witness")
        for site in entry["witnesses"]:
            i = by.get(site)
            require(i is not None and i.mnemonic == "call" and i.size == 5
                    and i.operands[0].type == capstone.x86.X86_OP_IMM
                    and i.operands[0].imm == target+offset, "runtime entry lacks its fixed original direct CALL")
        bindings[symbol] = dict(target=target+offset, kind="runtime-interior-v1", candidate=address+offset,
                                parent_target=target, parent_candidate=address, parent_size=887,
                                entry_offset=offset, evidence=row["evidence"])
    require(set(bindings) == set(allowed), "runtime profile requires both reviewed entry identities")
    evidence = dict(profile=row["profile"], function=owner, data_contribution=data_record,
                    target_address=target, data_target=data_target, data_address=data_address,
                    code_size=887, data_size=130, decoded_instructions=len(instructions),
                    fields=fields["fields"], candidate_relocations=sorted(relocations),
                    complete_code_equal=True, complete_data_equal=True, primary_exact_credit=0)
    if "fmod" in config["objects"]:
        from runtime_fmod import review_fmod
        extra, proof = review_fmod(context, config["objects"]["fmod"])
        require(not set(bindings) & set(extra), "duplicate runtime interior identity")
        bindings.update(extra)
        evidence["fmod"] = proof
    if "atan2" in config["objects"]:
        from runtime_atan2 import review_atan2
        extra, proof = review_atan2(context, config["objects"]["atan2"], evidence["fmod"])
        require(not set(bindings) & set(extra), "duplicate runtime interior identity")
        bindings.update(extra)
        evidence["atan2"] = proof
    return bindings, evidence


def validate_runtime_field(context, function, field, reviewed):
    require(field["type"] == "REL32" and field.get("width") == 4 and not field.get("addend", 0)
            and not field.get("local") and "storage_size" not in field
            and field["target"] == reviewed["target"] and field["offset"] > 0
            and context.image.read_address(int(function["address"], 0) + field["offset"] - 1, 1) == b"\xe8",
            "runtime interior identity permits only its exact REL32 CALL")
