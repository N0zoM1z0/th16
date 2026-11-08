"""Factory/TH10-style linked-owner comparison for imported TH16 candidates."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import struct
import tomllib

from linked_image import PEImage, linked_code_fields, linked_functions, map_publics, verify_capstone
from oracle_fields import expected_data_spans, require_decode_coverage, pack_linked_value

ROOT = Path(__file__).resolve().parents[1]
WIDTHS = {"DIR32": 4, "REL8": 1, "REL16": 2, "REL32": 4}


class Incomplete(ValueError):
    """Required ownership or linkage evidence is missing."""


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_identity():
    from build import input_identity
    return input_identity()


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


def replay_owner(image, target, publics, function, unit):
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
        if field.get("local", False):
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
    """Hold one immutable cold-build artifact set for a bounded batch."""
    def __init__(self):
        self.manifest = tomllib.loads((ROOT / "config/target.toml").read_text())
        self.directory = ROOT / "build/reference-candidate"
        self.receipt_path = self.directory / "build-receipt.json"
        self.receipt = json.loads(self.receipt_path.read_text())
        self.before = self.identity()
        if self.receipt["coldness"] != "clean-output-graph":
            raise Incomplete("strict replay requires a clean-output-graph build")
        if self.receipt["input_sha256"] != source_identity():
            raise Incomplete("source inputs differ from the cold build")
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
        with (ROOT / "config/functions.csv").open(newline="") as stream:
            self.boundaries = {int(row["address"], 0): row for row in csv.DictReader(stream)}

    def identity(self):
        files = [self.receipt_path, self.directory / "th16.exe", self.directory / "th16.map",
                 self.directory / "th16.pdb", ROOT / "resources/th16.exe",
                 self.directory / "functions.txt",
                 ROOT / "config/target.toml", ROOT / "config/tools.lock.toml",
                 ROOT / "config/reference-sources.csv", ROOT / "scripts/strict_oracle.py",
                 ROOT / "scripts/oracle_fields.py", ROOT / "scripts/linked_image.py",
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
        if not boundary or int(boundary["size"]) != unit["compare_size"]:
            raise Incomplete("complete candidate owner differs from the independent target boundary")
        if int(boundary["span_end"], 0) != unit["target_address"] + unit["compare_size"] - 1:
            raise Incomplete("target boundary has a different span end")
        self.check_boundary(unit)
        result = replay_owner(self.image, self.target, self.publics, function, unit)
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
        instructions = list(decoder.disasm(self.target.read_address(start, size), start))
        if not instructions or sum(i.size for i in instructions) != size:
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
                elif instruction.address + instruction.size != end:
                    raise Incomplete("indirect jump requires reviewed switch/owned-data extents")
        if instructions[-1].mnemonic not in {"ret", "retf", "jmp", "int3", "ud2"}:
            raise Incomplete("target extent ends in unreviewed fallthrough or non-returning code")
