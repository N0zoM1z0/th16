"""Factory/TH10-style linked-owner comparison for imported TH16 candidates."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import struct
import tomllib

from linked_image import PEImage, linked_code_fields, linked_functions, map_publics, verify_capstone, pdb_section_contributions
from oracle_fields import expected_data_spans, require_decode_coverage, pack_linked_value
from switch_ownership import load_switch_owners, validate_switch_owner
from eh_identity import review_handlers, validate_field, EHEvidenceError
from pdb_types import globals_with_sizes

ROOT = Path(__file__).resolve().parents[1]
WIDTHS = {"DIR32": 4, "REL8": 1, "REL16": 2, "REL32": 4}


class Incomplete(ValueError):
    """Required ownership or linkage evidence is missing."""


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_identity():
    from build import input_identity
    return input_identity()


def reviewed_linkages(context, path=None):
    """Validate fixed, independently reviewed runtime/literal storage bindings."""
    import capstone
    result = {}
    runtime_witnesses = []
    vftables = []
    with (path or ROOT / "config/linkage-bindings.csv").open(newline="") as stream:
        for row in csv.DictReader(stream):
            symbol, address, size = row["symbol"], int(row["target_address"], 0), int(row["size"])
            if symbol in result or size <= 0:
                raise ValueError("duplicate or invalid reviewed linkage")
            payload = context.target.read_address(address, size)
            if hashlib.sha256(payload).hexdigest() != row["target_sha256"]:
                raise Incomplete("reviewed linkage target extent hash mismatch")
            publics = [p for p in context.publics if p["symbol"] == symbol]
            if len(publics) != 1:
                raise Incomplete("reviewed linkage lacks a unique candidate public")
            if row["kind"] == "runtime-function":
                owners = [f for f in context.linked["functions"] if f["symbol"] == symbol]
                target = context.boundaries.get(address)
                candidate_size = int(row.get("candidate_size") or size)
                if (len(owners) != 1 or owners[0]["size"] != candidate_size or not target
                        or int(target["size"]) != size or candidate_size <= 0):
                    raise Incomplete("reviewed runtime linkage lacks both complete function extents")
                library = row["candidate_library"]
                library_root = (ROOT / ".tools/toolchain/sdk/Program Files/Windows Kits/10/Lib/10.0.10240.0/ucrt/x86"
                                if library == "libucrt.lib" else ROOT / ".tools/toolchain/vs/VC/Tools/MSVC/14.10.25017/lib/x86")
                expected_owner = "Z:" + str(library_root / library)
                normalize = lambda value: re.sub(r"/+", "/", str(value).replace("\\", "/")).lower()
                if library not in {"LIBCMT.lib", "libvcruntime.lib", "libucrt.lib"} or normalize(owners[0]["pdb_object"]) != normalize(expected_owner):
                    raise Incomplete("reviewed runtime linkage leaves its pinned Microsoft library")
                if row["witness_instruction"] or row["witness_mnemonic"]:
                    runtime_witnesses.append((address, int(row["witness_instruction"], 0), row["witness_mnemonic"]))
            elif row["kind"] == "vftable":
                vftables.append((row, publics[0]["address"]))
            elif row["kind"] in {"literal", "indexed-literal", "string-literal"}:
                if row["kind"] != "string-literal":
                    match = re.fullmatch(r"__(?:real|xmm)@([0-9a-fA-F]+)", symbol)
                    if not match or len(match[1]) != size * 2 or int(match[1], 16).to_bytes(size, "little") != payload:
                        raise Incomplete("reviewed literal does not contain its complete typed value")
                elif (not symbol.startswith("??_C@_0") or payload[-1:] != b"\0" or b"\0" in payload[:-1]
                      or context.data_contributions.get(publics[0]["address"]) != [size]):
                    raise Incomplete("reviewed string lacks one complete NUL-terminated PDB storage extent")
                if context.image.read_address(publics[0]["address"], size) != payload:
                    raise Incomplete("candidate literal differs from the reviewed payload")
                witness = int(row["witness_instruction"], 0)
                decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
                decoder.detail = True
                instruction = next(decoder.disasm(context.target.read_address(witness, 16), witness), None)
                memory_witness = instruction is not None and any(
                    op.type == capstone.x86.X86_OP_MEM and not op.mem.base and not op.mem.index
                    and op.mem.disp == address and op.size == size for op in instruction.operands
                )
                string_witness = (instruction is not None and instruction.mnemonic == "push"
                                  and len(instruction.operands) == 1
                                  and instruction.operands[0].type == capstone.x86.X86_OP_IMM
                                  and instruction.operands[0].imm == address)
                if row["kind"] == "indexed-literal":
                    # The supported table is two doubles selected by a logical
                    # right shift of a 32-bit register by 31, immediately before
                    # the indexed read. Decode from its independent owner to
                    # establish both instruction starts and adjacency.
                    parents = [(base, int(r["size"])) for base, r in context.boundaries.items()
                               if base <= witness < base + int(r["size"])]
                    sequence = []
                    if len(parents) == 1:
                        base, extent = parents[0]
                        sequence = list(decoder.disasm(context.target.read_address(base, extent), base))
                    position = next((n for n, i in enumerate(sequence) if i.address == witness), 0)
                    shift = sequence[position - 1] if position else None
                    operand = instruction.operands[-1] if instruction is not None else None
                    memory_witness = bool(
                        size == 16 and symbol.startswith("__xmm@")
                        and context.data_contributions.get(publics[0]["address"]) == [size]
                        and instruction is not None and operand is not None
                        and instruction.mnemonic == "addsd" and operand.type == capstone.x86.X86_OP_MEM
                        and operand.size == 8 and not operand.mem.base and operand.mem.index
                        and operand.mem.disp == address and operand.mem.scale == 8
                        and shift is not None and shift.address + shift.size == witness
                        and shift.mnemonic == "shr" and len(shift.operands) == 2
                        and shift.operands[0].type == capstone.x86.X86_OP_REG
                        and shift.operands[0].size == 4 and shift.operands[0].reg == operand.mem.index
                        and shift.operands[1].type == capstone.x86.X86_OP_IMM and shift.operands[1].imm == 31)
                if (instruction is None or instruction.mnemonic != row["witness_mnemonic"]
                        or not (string_witness if row["kind"] == "string-literal" else memory_witness)):
                    raise Incomplete("reviewed literal lacks its fixed target instruction witness")
            else:
                raise ValueError("unsupported reviewed linkage kind")
            result[symbol] = dict(target=address, size=size, kind=row["kind"], evidence=row["evidence"])
    for address, witness, mnemonic in runtime_witnesses:
        parents = [r for r in result.values() if r["kind"] == "runtime-function"
                   and r["target"] <= witness < r["target"] + r["size"]]
        if len(parents) != 1:
            raise Incomplete("runtime instruction witness lacks a unique reviewed parent")
        parent = parents[0]
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        decoder.detail = True
        instruction = next((i for i in decoder.disasm(
            context.target.read_address(parent["target"], parent["size"]), parent["target"])
                            if i.address == witness), None)
        if (instruction is None or mnemonic not in {"call", "jmp"} or instruction.mnemonic != mnemonic
                or len(instruction.operands) != 1 or instruction.operands[0].type != capstone.x86.X86_OP_IMM
                or instruction.operands[0].imm != address):
            raise Incomplete("reviewed runtime lacks its fixed direct instruction witness")
    from vtable_identity import review_vftable, VftableEvidenceError
    for row, candidate in vftables:
        try:
            review_vftable(context, row, candidate, result)
        except VftableEvidenceError as error:
            raise Incomplete(str(error)) from error
    return result


def expected_fields(unit):
    if not isinstance(unit.get("linkages"), list):
        raise Incomplete("unit lacks an exhaustive linkage manifest")
    fields = []
    occupied = set()
    for row in unit["linkages"]:
        row = dict(row)
        kind = row["type"]
        width = int(row.get("width", WIDTHS.get(kind, 0)))
        if kind not in WIDTHS or width != WIDTHS[kind]:
            raise ValueError("unsupported linkage field type or width")
        row.update(offset=int(row["offset"]), width=width, addend=int(row.get("addend", 0)))
        extent = set(range(row["offset"], row["offset"] + width))
        if min(extent) < 0 or max(extent) >= unit["compare_size"] or occupied & extent:
            raise ValueError("linkage fields overlap or leave the complete owner")
        occupied.update(extent)
        fields.append(row)
    return sorted(fields, key=lambda r: (r["offset"], r["type"]))


def pointer_limit(context, function, field, linkages):
    """Prove a non-dereferenced limit for a bounded field cursor over typed storage."""
    import capstone
    from capstone import x86
    if field["type"] != "DIR32" or field.get("width", 4) != 4 or field.get("local"):
        return None
    start, size = int(function["address"], 0), int(function["size"])
    code = context.image.read_address(start, size)
    cache = context.__dict__.setdefault("_pointer_limit_instructions", {})
    key = (start, code)
    if key not in cache:
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        decoder.detail = True
        cache[key] = list(decoder.disasm(code, start))
    instructions = cache[key]
    positions = {i.address: n for n, i in enumerate(instructions)}
    n = next((n for n, i in enumerate(instructions)
              if i.imm_size == 4 and i.address - start + i.imm_offset == field["offset"]), -1)
    if n < 0 or n + 1 >= len(instructions):
        return None
    compare, branch = instructions[n:n + 2]
    if (compare.mnemonic != "cmp" or len(compare.operands) != 2
            or compare.operands[0].type != x86.X86_OP_REG or compare.operands[1].type != x86.X86_OP_IMM
            or branch.mnemonic != "jl" or branch.operands[0].type != x86.X86_OP_IMM):
        return None
    register = compare.operands[0].reg
    if register not in {x86.X86_REG_EBX, x86.X86_REG_ESI, x86.X86_REG_EDI}:
        return None
    loop_start = branch.operands[0].imm
    if loop_start not in positions or not start < loop_start < compare.address:
        return None
    body = instructions[positions[loop_start]:n]
    writes = [i for i in body if register in i.regs_access()[1]]
    if len(writes) != 1:
        return None
    step = writes[0]
    if (step.mnemonic != "add" or len(step.operands) != 2
            or step.operands[0].type != x86.X86_OP_REG or step.operands[0].reg != register
            or step.operands[1].type != x86.X86_OP_IMM or step.operands[1].imm <= 0):
        return None
    stride = step.operands[1].imm
    prior = [i for i in instructions[:positions[loop_start]] if register in i.regs_access()[1]]
    if not prior:
        return None
    initial = prior[-1]
    if (initial.mnemonic != "mov" or len(initial.operands) != 2
            or initial.operands[0].type != x86.X86_OP_REG or initial.operands[0].reg != register
            or initial.operands[1].type != x86.X86_OP_IMM or initial.imm_size != 4):
        return None
    initial_offset = initial.address - start + initial.imm_offset
    anchors = [f for f in linkages if f["offset"] == initial_offset and f["type"] == "DIR32"
               and "storage_name" in f and "storage_size" in f and not f.get("pointer_limit")]
    if len(anchors) != 1:
        return None
    anchor = anchors[0]
    offset, extent = anchor.get("addend", 0), anchor["storage_size"]
    publics = [p for p in context.publics if p["symbol"] == anchor["symbol"]]
    if len(publics) != 1 or not 0 <= offset < stride or extent <= 0 or extent % stride:
        return None
    base = publics[0]["address"]
    if (initial.operands[1].imm != base + offset or compare.operands[1].imm != base + extent + offset
            or not 0 <= base < base + extent + offset < 0x80000000
            or not 0 <= anchor["target"] < anchor["target"] + extent + offset < 0x80000000):
        return None
    # No preheader edge may enter the loop after skipping its initializer.
    for instruction in instructions[:positions[loop_start]]:
        if instruction.mnemonic.startswith("loop") or instruction.mnemonic in {"jcxz", "jecxz"}:
            return None
        if instruction.group(capstone.CS_GRP_JUMP):
            if instruction.operands[0].type != x86.X86_OP_IMM:
                return None
            destination = instruction.operands[0].imm
            if instruction.address < initial.address and initial.address < destination <= branch.address:
                return None
    # Once the limit is reached, the old cursor may only be discarded/reset.
    for instruction in instructions[n + 2:]:
        reads, writes = instruction.regs_access()
        if register in reads:
            return None
        if register in writes:
            break
    by_offset = {f["offset"]: f for f in linkages}
    count = extent // stride
    for instruction in body:
        if (instruction.mnemonic.startswith("loop") or instruction.mnemonic in {"jcxz", "jecxz"}
                or instruction.group(capstone.CS_GRP_INT) or instruction.group(capstone.CS_GRP_IRET)
                or instruction.group(capstone.CS_GRP_PRIVILEGE)):
            return None
        if instruction.group(capstone.CS_GRP_RET):
            return None
        if instruction.group(capstone.CS_GRP_JUMP):
            if (instruction.operands[0].type != x86.X86_OP_IMM
                    or not instruction.address < instruction.operands[0].imm <= step.address):
                return None
        if instruction.group(capstone.CS_GRP_CALL):
            operand = instruction.operands[0]
            if operand.type == x86.X86_OP_IMM:
                operand_offset, destination = instruction.imm_offset, operand.imm
            elif operand.type == x86.X86_OP_MEM and not operand.mem.base and not operand.mem.index:
                operand_offset, destination = instruction.disp_offset, operand.mem.disp
            else:
                return None
            call = by_offset.get(instruction.address - start + operand_offset, {})
            symbol = call.get("symbol", "")
            addresses = [p["address"] for p in context.publics if p["symbol"] == symbol]
            stdcall_import = symbol.startswith("__imp__") and re.search(r"@\d+$", symbol)
            # This compiler math helper's reviewed x86 contract preserves the
            # nonvolatile cursor. Other private runtime conventions need review.
            runtime = (symbol == "__libm_sse2_sqrt_precise"
                       and context.reviewed_linkages.get(symbol, {}).get("kind") == "runtime-function")
            if addresses != [destination] or call.get("addend", 0) or not (stdcall_import or runtime):
                return None
        if (register in instruction.regs_access()[0] and not any(
                op.type == x86.X86_OP_REG and op.reg == register or
                op.type == x86.X86_OP_MEM and register in {op.mem.base, op.mem.index}
                for op in instruction.operands)):
            return None
        for operand in instruction.operands:
            if operand.type == x86.X86_OP_REG and operand.reg == register and instruction is not step:
                return None
            if operand.type == x86.X86_OP_MEM and register in {operand.mem.base, operand.mem.index}:
                if (instruction.mnemonic == "lea" or operand.mem.base != register or operand.mem.index
                        or operand.mem.segment or operand.size <= 0 or offset + operand.mem.disp < 0
                        or offset + (count - 1) * stride + operand.mem.disp + operand.size > extent):
                    return None
    return dict(symbol=anchor["symbol"], target=anchor["target"], addend=extent + offset,
                storage_name=anchor["storage_name"], storage_size=extent, pointer_limit=True)


def replay_owner(image, target, publics, function, unit, *, eh_handlers=None):
    """Compare every owned byte, permitting only enumerated, bound fields."""
    candidate_address = int(function["address"], 0)
    target_address = unit["target_address"]
    size = unit["compare_size"]
    if int(unit.get("size", size)) != size:
        raise Incomplete("primary and owned extents need an explicit compound ownership graph")
    if int(function["size"]) != size:
        raise Incomplete("candidate PDB contribution differs from the complete declared extent")
    actual = linked_code_fields(image, publics, candidate_address, size)
    expected = expected_fields(unit)
    key = lambda row: (int(row["offset"]), row["type"], int(row["width"]))
    if sorted(map(key, actual["fields"])) != sorted(map(key, expected)):
        raise Incomplete("observed fields differ from the exhaustive linkage manifest")
    occupied = {b for row in expected for b in range(row["offset"], row["offset"] + row["width"])}
    spans = expected_data_spans(unit, size, occupied)
    try:
        require_decode_coverage(actual, spans, size)
    except ValueError as error:
        raise Incomplete(str(error)) from error
    public_addresses = {}
    for row in publics:
        public_addresses.setdefault(row["symbol"], set()).add(int(row["address"]))
    observed = {key(row): row for row in actual["fields"]}
    original = target.read_address(target_address, size)
    raw = image.read_address(candidate_address, size)
    candidate = bytearray(raw)
    replayed = []
    for field in expected:
        item = observed[key(field)]
        base = int(item["candidate_target"]) - field["addend"]
        if "eh_handler" in field:
            if candidate_address != unit["candidate_address"] or function["symbol"] != unit["symbol"]:
                raise Incomplete("EH field does not belong to the actual candidate parent")
            try:
                validate_field(eh_handlers or {}, unit, field, base)
            except EHEvidenceError as error:
                raise Incomplete(str(error)) from error
        elif field.get("local", False):
            if not candidate_address <= base < candidate_address + size:
                raise Incomplete("local field leaves its candidate owner")
            if not target_address <= field["target"] < target_address + size:
                raise Incomplete("local field leaves its target owner")
            if base - candidate_address != field["target"] - target_address:
                raise Incomplete("local field changes its offset within the owner")
        elif public_addresses.get(field["symbol"], set()) != {base}:
            raise Incomplete(f"field lacks one unique linked symbol: {field['symbol']}")
        encoded = pack_linked_value(candidate, field, item["instruction_end"], target_address)
        replayed.append({**field, "candidate_target": int(item["candidate_target"]), "encoded": encoded})
    differences = [dict(offset=i, candidate=a, target=b)
                   for i, (a, b) in enumerate(zip(candidate, original)) if a != b]
    return {"result": "exact" if not differences else "mismatch", "size": size,
            "compared_size": size, "matched_bytes": size - len(differences),
            "candidate_address": candidate_address, "raw_equal": raw == original,
            "decoded_bytes": actual["decoded_bytes"], "data_spans": spans,
            "linkages": replayed, "first_differences": differences[:32]}


class Context:
    """Hold one immutable, source-current build artifact set for a bounded batch."""
    def __init__(self, *, require_cold=False):
        self.manifest = tomllib.loads((ROOT / "config/target.toml").read_text())
        self.directory = ROOT / "build/reference-candidate"
        self.receipt_path = self.directory / "build-receipt.json"
        self.receipt = json.loads(self.receipt_path.read_text())
        self.before = self.identity()
        if self.receipt["coldness"] not in {"clean-output-graph", "incremental"}:
            raise Incomplete("unsupported candidate build kind")
        if require_cold and self.receipt["coldness"] != "clean-output-graph":
            raise Incomplete("strict replay requires a clean-output-graph build")
        if self.receipt["input_sha256"] != source_identity():
            raise Incomplete("source inputs differ from the recorded build")
        for name, value in self.receipt["artifacts"].items():
            if digest(self.directory / name) != value:
                raise ValueError("candidate artifact hash differs from the build receipt")
        target_path = ROOT / "resources/th16.exe"
        if digest(target_path) != self.manifest["target"]["sha256"]:
            raise ValueError("target SHA-256 differs from the manifest")
        if target_path.stat().st_size != self.manifest["target"]["size"]:
            raise ValueError("target size differs from the manifest")
        self.decoder = verify_capstone(tomllib.loads((ROOT / "config/tools.lock.toml").read_text())["capstone"])
        self.image = PEImage(self.directory / "th16.exe")
        self.target = PEImage(target_path)
        if not self.image.base_relocations():
            raise Incomplete("candidate lacks PE relocation evidence; link with /FIXED:NO")
        self.linked = linked_functions(self.directory / "th16.exe", self.directory / "th16.map", self.directory / "th16.pdb")
        self.publics = map_publics(self.directory / "th16.map")
        self.typed_globals = globals_with_sizes(self.directory / "th16.pdb", self.image)
        self.data_contributions = {}
        for row in pdb_section_contributions(self.directory / "th16.pdb")["contributions"]:
            if row["characteristics"] & 0x20 or not row["size"]:
                continue
            section = self.image.section(row["section_number"])
            base = self.image.image_base + section.rva + row["section_offset"]
            self.data_contributions.setdefault(base, []).append(row["size"])
        with (ROOT / "config/functions.csv").open(newline="") as stream:
            self.boundaries = {int(row["address"], 0): row for row in csv.DictReader(stream)}
        self.switch_owners = load_switch_owners(ROOT / "config/switch-owners.toml")
        self.reviewed_linkages = reviewed_linkages(self)
        try:
            self.eh_handlers = review_handlers(self, ROOT / "config/eh-handlers.toml")
        except EHEvidenceError as error:
            raise Incomplete(str(error)) from error

    def identity(self):
        files = [self.receipt_path, self.directory / "th16.exe", self.directory / "th16.map",
                 self.directory / "th16.pdb", ROOT / "resources/th16.exe",
                 self.directory / "functions.txt",
                 ROOT / "config/target.toml", ROOT / "config/tools.lock.toml",
                 ROOT / "config/linkage-bindings.csv",
                 ROOT / "config/reference-sources.csv", ROOT / "scripts/strict_oracle.py",
                 ROOT / "scripts/oracle_fields.py", ROOT / "scripts/linked_image.py",
                 ROOT / "scripts/pdb_types.py", ROOT / "scripts/vtable_identity.py",
                 ROOT / "scripts/switch_ownership.py", ROOT / "config/switch-owners.toml",
                 ROOT / "scripts/eh_identity.py", ROOT / "config/eh-handlers.toml",
                 ROOT / "scripts/audit-reference.py", ROOT / "scripts/compare-linked-function.py"]
        result = {str(p.relative_to(ROOT)): digest(p) for p in files}
        with (ROOT / "config/functions.csv").open(newline="") as stream:
            boundaries = [{key: row[key] for key in ("address", "size", "span_end")}
                          for row in csv.DictReader(stream)]
        result["config/functions.csv#boundaries"] = hashlib.sha256(
            json.dumps(boundaries, sort_keys=True).encode()).hexdigest()
        return result

    def finish(self):
        if self.identity() != self.before or source_identity() != self.receipt["input_sha256"]:
            raise ValueError("Oracle inputs changed during evaluation")

    def compare(self, unit):
        source = (ROOT / unit["source"]).resolve()
        if not source.is_file() or not source.is_relative_to((ROOT / "src").resolve()):
            raise Incomplete("primary source must be maintained game code under src/")
        if unit.get("artifact_kind") != "linked-pe" or "/GL" not in unit.get("profile", []):
            raise Incomplete("unit lacks an explicit linked-PE /GL profile")
        if not any(flag.lower() == "/ltcg" for flag in unit.get("link_profile", [])):
            raise Incomplete("unit lacks an explicit LTCG link profile")
        if unit["profile"] != self.receipt["compiler_profile"] or unit["link_profile"] != self.receipt["linker_profile"]:
            raise Incomplete("unit profile differs from the attested cold build")
        matches = [r for r in self.linked["functions"] if r["symbol"] == unit["symbol"]
                   and int(r["address"], 0) == unit["candidate_address"]]
        if len(matches) != 1:
            raise Incomplete("symbol lacks one complete same-start PDB owner")
        function = matches[0]
        observed_object = str(function["pdb_object"]).replace("\\", "/").rsplit("/", 1)[-1]
        if observed_object.lower() != unit["object"].lower():
            raise Incomplete("PDB object differs from the declared source owner")
        def normalized(value):
            return re.sub(r"/+", "/", str(value).replace("\\", "/")).lower()
        expected_object = "Z:" + str(self.directory / "obj" / Path(unit["source"]).with_suffix(".obj"))
        if normalized(function["pdb_object"]) != normalized(expected_object):
            raise Incomplete("PDB source object path differs from the selected producer")
        boundary = self.boundaries.get(unit["target_address"])
        if boundary is None:
            raise Incomplete("original target lacks an independently reviewed function boundary")
        if int(boundary["size"]) != unit["compare_size"]:
            raise Incomplete("complete candidate owner differs from the independent target boundary")
        if int(boundary["span_end"], 0) != unit["target_address"] + unit["compare_size"] - 1:
            raise Incomplete("target boundary has a different span end")
        self.check_boundary(unit)
        for field in unit["linkages"]:
            if field.get("pointer_limit"):
                proof = pointer_limit(self, function, field, unit["linkages"])
                if proof is None or any(field.get(key) != value for key, value in proof.items()):
                    raise Incomplete("pointer limit lacks its bounded typed-cursor proof")
            reviewed = self.reviewed_linkages.get(field.get("symbol"))
            if reviewed and field["target"] != reviewed["target"]:
                raise Incomplete("linkage differs from the independently reviewed fixed destination")
            addend = field.get("addend", 0)
            if reviewed and reviewed["kind"] == "vftable" and (addend or field["type"] != "DIR32"):
                raise Incomplete("reviewed vftable permits only its exact DIR32 address point")
            if addend and not field.get("local") and "storage_size" not in field:
                addresses = {p["address"] for p in self.publics if p["symbol"] == field["symbol"]}
                sizes = self.data_contributions.get(next(iter(addresses)), []) if len(addresses) == 1 else []
                if len(sizes) != 1 or not 0 <= addend < sizes[0]:
                    raise Incomplete("interior field lacks an explicit bounded PDB storage proof")
            if "storage_size" not in field:
                continue
            addresses = {p["address"] for p in self.publics if p["symbol"] == field["symbol"]}
            typed = [r for r in self.typed_globals if r["name"] == field["storage_name"] and r["address"] in addresses]
            if len(typed) != 1 or typed[0]["size"] != field["storage_size"]:
                raise Incomplete("data addend lacks its declared unique PDB type extent")
            if not field.get("pointer_limit") and not 0 <= field.get("addend", 0) < field["storage_size"]:
                raise Incomplete("data addend leaves its typed global storage")
            target_base = field["target"]
            if not any(not s.characteristics & 0x20 and self.target.image_base + s.rva <= target_base
                       and target_base + field["storage_size"] <= self.target.image_base + s.rva + max(s.raw_size, s.virtual_size)
                       for s in self.target.sections):
                raise Incomplete("typed target storage leaves mapped non-code data")
        result = replay_owner(self.image, self.target, self.publics, function, unit,
                              eh_handlers=self.eh_handlers)
        if any("eh_handler" in field for field in unit["linkages"]):
            result["auxiliary_eh_owners"] = [self.eh_handlers[(unit["source"], unit["symbol"])]]
        return {**result, "symbol": unit["symbol"], "target_address": unit["target_address"],
                "unit_sha256": hashlib.sha256(json.dumps(unit, sort_keys=True).encode()).hexdigest(),
                "extent_source": function["extent_source"], "pdb_object": function["pdb_object"],
                "pdb_module_index": function["pdb_module_index"],
                "image_sha256": self.image.sha256, "pdb_guid": self.linked["pdb_guid"],
                "pdb_age": self.linked["pdb_age"], "target_sha256": self.manifest["target"]["sha256"],
                "factory_acceptance": "not-submitted"}

    def check_boundary(self, unit):
        import capstone
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        decoder.detail = True
        start, size = unit["target_address"], unit["compare_size"]
        end = start + size
        reviewed_dispatch = None
        record = self.switch_owners.get(start)
        if record:
            try:
                instructions, reviewed_dispatch = validate_switch_owner(self, unit, record)
            except ValueError as error:
                raise Incomplete(f"reviewed switch ownership: {error}") from error
        else:
            instructions = list(decoder.disasm(self.target.read_address(start, size), start))
        code_size = record["code_size"] if record else size
        if not instructions or sum(i.size for i in instructions) != code_size:
            raise Incomplete("target owner needs explicit trailing-data coverage")
        starts = {i.address for i in instructions}
        if any(address != start and address < end and int(row["span_end"], 0) >= start
               for address, row in self.boundaries.items()):
            raise Incomplete("target extent overlaps another independent function candidate")
        for instruction in instructions:
            if instruction.group(capstone.CS_GRP_JUMP) and instruction.operands:
                operand = instruction.operands[0]
                if operand.type == capstone.x86.X86_OP_IMM:
                    destination = operand.imm & 0xFFFFFFFF
                    if start <= destination < end and destination not in starts:
                        raise Incomplete("target branch enters the middle of an instruction")
                elif instruction.address != reviewed_dispatch and instruction.address + instruction.size != end:
                    raise Incomplete("indirect jump requires reviewed switch/owned-data extents")
        if instructions[-1].mnemonic not in {"ret", "retf", "jmp", "int3", "ud2"}:
            raise Incomplete("target extent ends in unreviewed fallthrough or non-returning code")
