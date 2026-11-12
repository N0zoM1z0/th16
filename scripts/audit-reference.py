#!/usr/bin/env python3
"""Evaluate imported candidates with the local strict linked-owner Oracle."""
from __future__ import annotations

import argparse
import bisect
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import struct

import pefile

from strict_oracle import Context, Incomplete, ROOT, pointer_limit
from linked_image import linked_code_fields, pdb_section_contributions


def markers():
    result = defaultdict(list)
    for path in sorted((ROOT / "src").rglob("*")):
        if path.suffix not in {".h", ".cpp"}:
            continue
        lines = path.read_text().splitlines()
        for index, line in enumerate(lines):
            match = re.search(r"//\s*(FUNCTION|SYNTHETIC|LIBRARY|GLOBAL|VTABLE):\s*TH16\s+(0x[0-9a-fA-F]+)", line)
            if not match:
                continue
            kind, address = match.groups()
            following = []
            for next_line in lines[index + 1:index + 12]:
                if next_line.strip().startswith("//"):
                    continue
                following.append(next_line)
                if any(x in next_line for x in [";", "{", "="]):
                    break
            result[kind].append(dict(address=int(address, 16), source=path.relative_to(ROOT).as_posix(),
                                     line=index + 1, declaration=" ".join(following)))
    return result


def bindings(context, functions, annotations):
    """Fix semantic destinations independently of the current compared operand."""
    fixed = defaultdict(set)
    provenance = defaultdict(list)

    def add(symbol, address, basis):
        fixed[symbol].add(address)
        provenance[symbol].append(basis)

    for original, candidate, symbol in functions:
        add(symbol, original, "source-function-annotation")
    for symbol, row in context.reviewed_linkages.items():
        add(symbol, row["target"], "reviewed-" + row["kind"])
    for row in context.static_functions.values():
        add(row["symbol"], row["target"], "reviewed-complete-private-function")
    symbols = {r["symbol"] for r in context.publics}
    for row in annotations["GLOBAL"]:
        match = re.search(r"\b([A-Za-z_]\w*)\s*(?:\[[^\]]*\]\s*)*(?==|;|\()", row["declaration"])
        if not match:
            continue
        name = match.group(1)
        possible = [s for s in symbols if s == "_" + name or s.startswith("?" + name + "@@3")]
        if len(possible) == 1:
            add(possible[0], row["address"], "source-global-annotation")

    original_pe = pefile.PE(str(ROOT / "resources/th16.exe"))
    candidate_pe = pefile.PE(str(context.directory / "th16.exe"))

    def imports(pe):
        return {(d.dll.lower(), i.name or i.ordinal): i.address
                for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports}

    target_imports = imports(original_pe)
    candidate_imports = imports(candidate_pe)
    for identifier, address in candidate_imports.items():
        if identifier not in target_imports:
            continue
        for public in context.publics:
            if public["address"] == address:
                add(public["symbol"], target_imports[identifier], "PE-import-dll-and-name")
    if hasattr(original_pe, "DIRECTORY_ENTRY_LOAD_CONFIG") and hasattr(candidate_pe, "DIRECTORY_ENTRY_LOAD_CONFIG"):
        target_cookie = original_pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.SecurityCookie
        candidate_cookie = candidate_pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.SecurityCookie
        for public in context.publics:
            if public["address"] == candidate_cookie and target_cookie:
                add(public["symbol"], target_cookie, "PE-load-config-security-cookie")

    # Constants and strings require one complete, independently located payload.
    # Ambiguous duplicate storage never selects whichever address would pass.
    data_sections = [s for s in context.target.sections if s.name == ".rdata"]
    for public in context.publics:
        symbol, address = public["symbol"], public["address"]
        payload = None
        alignment = 1
        real = re.fullmatch(r"__(?:real|xmm)@([0-9a-fA-F]+)", symbol)
        if real and len(real.group(1)) in {8, 16, 32}:
            payload = int(real.group(1), 16).to_bytes(len(real.group(1)) // 2, "little")
            alignment = min(len(payload), 16)
        elif symbol.startswith("??_C@_"):
            try:
                data = context.image.read_address(address, 1024)
                if symbol.startswith("??_C@_1"):
                    limit = next(i + 2 for i in range(0, len(data) - 1, 2) if data[i:i + 2] == b"\0\0")
                    alignment = 2
                else:
                    limit = data.index(0) + 1
                payload = data[:limit]
            except (ValueError, StopIteration):
                continue
        if not payload:
            continue
        destinations = []
        for section in data_sections:
            data = context.target.read_section(section.number, 0, section.raw_size)
            offset = data.find(payload)
            while offset >= 0:
                destination = context.target.image_base + section.rva + offset
                if destination % alignment == 0:
                    destinations.append(destination)
                offset = data.find(payload, offset + 1)
        if len(destinations) == 1:
            add(symbol, destinations[0], "unique-complete-readonly-payload")
    return {s: next(iter(a)) for s, a in fixed.items() if len(a) == 1}, provenance


def write_units(units, target_hash):
    lines = ["schema_version = 1", "target_sha256 = " + json.dumps(target_hash), ""]
    for name, unit in units.items():
        lines.append("[units." + name + "]")
        for key, value in unit.items():
            if key in {"linkages", "data_spans", "profile", "link_profile"}:
                continue
            lines.append(key + " = " + (json.dumps(value) if isinstance(value, str) else str(value)))
        for key in ["profile", "link_profile"]:
            lines.append(key + " = " + json.dumps(unit[key]))
        for key in ["data_spans", "linkages"]:
            if key not in unit:
                continue
            lines.append(key + " = [")
            for field in unit[key]:
                values = [k + " = " + (json.dumps(v) if isinstance(v, str) else str(v).lower()) for k, v in field.items()]
                lines.append("  { " + ", ".join(values) + " },")
            lines.append("]")
        lines.append("")
    (ROOT / "config/match-units.toml").write_text("\n".join(lines) + "\n")


def write_ledgers(reports, context):
    from build import annotated_functions
    names = {address: name for address, name, *_ in annotated_functions()}
    by_address = {row["target_address"]: row for row in reports}

    def write(name, columns, rows):
        with (ROOT / "config" / name).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    candidates = []
    for row in reports:
        address = row["target_address"]
        candidates.append(dict(address=f"0x{address:08X}", name=names.get(address, row.get("symbol", "")),
            source_file=row["source"], symbol=row.get("symbol", ""), result=row["result"],
            reason=row.get("reason", ""), evidence=".analysis/reference-audit.json"))
    write("reference-functions.csv", list(candidates[0]), candidates)

    functions_path = ROOT / "config/functions.csv"
    with functions_path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames
        functions = list(reader)
    mappings, boundaries = [], []
    for function in functions:
        address = int(function["address"], 0)
        report = by_address.get(address)
        if report:
            name = names.get(address, report.get("symbol", ""))
            function.update(proposed_name=name, module=Path(report["source"]).stem,
                            source_file=report["source"], owner="review",
                            status="local-strict-pass" if report["result"] == "exact" else "candidate",
                            match_percent="100.00" if report["result"] == "exact" else "0.00",
                            notes="Imported candidate; source origin remains under review. See .analysis/reference-audit.json.")
            mappings.append(dict(address=function["address"], name=name, module=function["module"],
                source_file=report["source"], notes="Reference candidate; local comparison is separate from Factory acceptance."))
        boundaries.append(dict(address=function["address"], size=function["size"], span_end=function["span_end"],
            state="strict-compared" if report and report["result"] in {"exact", "mismatch"} else "provisional",
            evidence=".analysis/reference-audit.json" if report else "ghidra-initial-import"))
    write("functions.csv", columns, functions)
    write("reccmp-functions.csv", ["address", "name", "module", "source_file", "notes"], mappings)
    write("function-boundaries.csv", ["address", "size", "span_end", "state", "evidence"], boundaries)
    matches = [dict(address=f"0x{r['target_address']:08X}", name=names.get(r["target_address"], r["symbol"]),
                    unit=f"reference-{r['target_address']:08x}",
                    status="local-strict-pass" if r["result"] == "exact" else "mismatch",
                    size=r["size"], compared_size=r["compared_size"], matched_bytes=r["matched_bytes"],
                    evidence=".analysis/reference-audit.json")
               for r in reports if r["result"] in {"exact", "mismatch"}]
    write("matches.csv", ["address", "name", "unit", "status", "size", "compared_size", "matched_bytes", "evidence"], matches)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-units", action="store_true", help="retain independently bound, complete comparison units")
    parser.add_argument("--address", action="append", type=lambda value: int(value, 0),
                        help="compare only this original function address; repeat for a focused batch")
    parser.add_argument("--json", type=Path, help="write a separate diagnostic report beneath .analysis/")
    args = parser.parse_args()
    if args.address and (not args.json or args.write_units):
        parser.error("--address requires --json and cannot update canonical units or ledgers")
    if args.json and (args.write_units
                      or not args.json.resolve().is_relative_to((ROOT / ".analysis").resolve())
                      or args.json.resolve() == (ROOT / ".analysis/reference-audit.json").resolve()):
        parser.error("--json must name a separate .analysis/ report and cannot be used with --write-units")
    context = Context()
    functions = [(int(a, 16), int(b, 16), symbol) for a, b, symbol in
                 (line.split() for line in (context.directory / "functions.txt").read_text().splitlines())]
    annotations = markers()
    by_address = defaultdict(list)
    for kind in ["FUNCTION", "SYNTHETIC", "LIBRARY"]:
        for row in annotations[kind]:
            by_address[row["address"]].append(row)
    if args.address:
        missing = set(args.address) - by_address.keys()
        if missing:
            parser.error("unannotated original addresses: " + ", ".join(hex(a) for a in sorted(missing)))
        by_address = {a: by_address[a] for a in sorted(set(args.address))}
    by_original = defaultdict(list)
    for row in functions:
        by_original[row[0]].append(row)
    fixed, provenance = bindings(context, functions, annotations)
    public_by_address = defaultdict(list)
    for row in context.publics:
        if row["symbol"] in fixed:
            public_by_address[row["address"]].append(row["symbol"])
    bases = sorted(public_by_address)
    typed_owners = {}
    for public in context.publics:
        typed = [r for r in context.typed_globals if r["address"] == public["address"]
                 and (public["symbol"] == "_" + r["name"] or public["symbol"].startswith("?" + r["name"] + "@@3"))]
        if len(typed) == 1:
            typed_owners[public["symbol"]] = typed[0]
    data_owners = defaultdict(list)
    for contribution in pdb_section_contributions(context.directory / "th16.pdb")["contributions"]:
        if contribution["characteristics"] & 0x20 or not contribution["size"]:
            continue
        section = context.image.section(contribution["section_number"])
        base = context.image.image_base + section.rva + contribution["section_offset"]
        data_owners[base].append(base + contribution["size"])
    owned = defaultdict(list)
    for row in context.linked["functions"]:
        owned[(int(row["address"], 0), row["symbol"])].append(row)
    reports, units = [], {}
    for original, declarations in sorted(by_address.items()):
        report = {"target_address": original, "source": declarations[0]["source"]}
        try:
            choices = by_original[original]
            if len(choices) != 1:
                raise Incomplete(f"annotation has {len(choices)} candidate symbols")
            _, address, symbol = choices[0]
            report.update(symbol=symbol, candidate_address=address)
            owners = owned[(address, symbol)]
            static = [(name,p) for name,p in context.static_functions.items()
                      if (p["target"],p["candidate"],p["symbol"],p["source"]) ==
                      (original,address,symbol,declarations[0]["source"])]
            if static:
                if owners or len(static) != 1:
                    raise Incomplete("reviewed static owner is ambiguous")
                owners = [static[0][1]["function"]]
            if len(owners) != 1:
                raise Incomplete("symbol lacks one complete same-start PDB contribution")
            function = owners[0]
            size = int(function["size"])
            object_name = Path(declarations[0]["source"]).stem + ".obj"
            unit = {"artifact_kind": "linked-pe", "source": declarations[0]["source"],
                    "output_dir": "build/reference-candidate", "symbol": symbol, "object": object_name,
                    "candidate_address": address, "target_address": original, "size": size,
                    "compare_size": size, "profile": context.receipt["compiler_profile"],
                    "link_profile": context.receipt["linker_profile"], "linkages": []}
            if static:
                unit["reviewed_static"] = static[0][0]
            fields = linked_code_fields(context.image, context.publics, address, size)
            record = context.switch_owners.get(original)
            if (record and "remap_values" in record and not fields["normalization_complete"]
                    and size == record["remap_offset"] + len(record["remap_values"])):
                # Classify only the undecoded suffix of a reviewed complete
                # byte map. These bytes are still compared raw by replay_owner;
                # Context.compare checks both complete tables before replay.
                start = max(record["remap_offset"], fields["decoded_bytes"])
                unit["data_spans"] = [dict(offset=start,width=size-start)]
            unresolved = []
            for field in fields["fields"]:
                destination = int(field["candidate_target"])
                eh = context.eh_handlers.get((unit["source"], symbol))
                if (eh and original == eh["parent_target"] and address == eh["parent_candidate"]
                        and size == eh["parent_size"] and field["offset"] == eh.get("handler_field_offset", 6)
                        and field["width"] == 4 and field["type"] == "DIR32"
                        and destination == eh["handler"]["address"]):
                    from eh_identity import handler_field
                    unit["linkages"].append(handler_field(eh))
                    continue
                limit = pointer_limit(context, function, field, unit["linkages"])
                if limit is not None:
                    unit["linkages"].append(dict(offset=field["offset"], width=field["width"], type=field["type"], **limit))
                    continue
                if address <= destination < address + size:
                    unit["linkages"].append(dict(offset=field["offset"], width=field["width"], type=field["type"],
                        local=True, symbol="<local>", target=original + destination - address))
                    continue
                private = [(name,p) for name,p in context.static_functions.items() if p["candidate"] == destination]
                if private and field["type"] == "REL32" and field["width"] == 4 and field["instruction"] == "call":
                    if len(private) != 1:
                        raise Incomplete("private callee is ambiguous")
                    name, proof = private[0]
                    unit["linkages"].append(dict(offset=field["offset"],width=4,type="REL32",
                        symbol=proof["symbol"],target=proof["target"],addend=0,reviewed_static=name))
                    continue
                index = bisect.bisect_right(bases, destination) - 1
                if index < 0:
                    unresolved.append(dict(offset=field["offset"], candidate_target=destination))
                    continue
                base = bases[index]
                # Code calls require an exact entry; data may use a field offset.
                # Interior data bindings are bounded by the next public, never arbitrary.
                next_public = min((r["address"] for r in context.publics if r["address"] > base), default=base + 1)
                possible = public_by_address[base]
                if (len(possible) != 1 or destination >= next_public
                        or (field["type"].startswith("REL") and destination != base)):
                    unresolved.append(dict(offset=field["offset"], candidate_target=destination))
                    continue
                name = possible[0]
                storage = {}
                if destination != base and (len(data_owners[base]) != 1 or destination >= data_owners[base][0]):
                    typed = typed_owners.get(name)
                    if typed is None or not base <= destination < base + typed["size"]:
                        unresolved.append(dict(offset=field["offset"], candidate_target=destination,
                                               reason="interior address lacks one bounded PDB data owner"))
                        continue
                    storage = dict(storage_name=typed["name"], storage_size=typed["size"])
                unit["linkages"].append(dict(offset=field["offset"], width=field["width"], type=field["type"],
                    symbol=name, target=fixed[name], addend=destination - base, **storage))
            report["size"] = size
            if unresolved:
                report["unresolved_fields"] = unresolved
                raise Incomplete(f"{len(unresolved)} linked fields lack independent symbol/addend bindings")
            result = context.compare(unit)
            report.update(result)
            units[f"reference-{original:08x}"] = unit
        except Incomplete as error:
            report.update(result="incomplete", reason=str(error))
        except (ValueError, KeyError) as error:
            report.update(result="error", reason=str(error))
        reports.append(report)
    context.finish()
    counts = Counter(r["result"] for r in reports)
    output = {"oracle": "th16-factory-th10-linked-owner-v1", "counts": dict(counts),
              "input_identity": context.before, "build_receipt": context.receipt,
              "bindings": [{"symbol": s, "target_address": a, "basis": provenance[s]} for s, a in sorted(fixed.items())],
              "functions": reports, "factory_acceptance": "not-submitted"}
    path = args.json or ROOT / ".analysis/reference-audit.json"
    path.write_text(json.dumps(output, indent=2) + "\n")
    if args.write_units:
        write_units(units, context.manifest["target"]["sha256"])
        write_ledgers(reports, context)
    print(json.dumps(dict(counts), sort_keys=True))
    print(f"Compared {len(reports)} annotated candidates; report: {path}")


if __name__ == "__main__":
    main()
