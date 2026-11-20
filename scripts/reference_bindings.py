"""Independent TH16 bindings shared by audit discovery and unit replay."""
from collections import defaultdict
import re

import pefile

from strict_oracle import Incomplete, ROOT


def function_map(context):
    with (context.directory / "functions.txt").open() as stream:
        return [(int(original, 16), int(candidate, 16), symbol)
                for original, candidate, symbol in (line.split() for line in stream)]


def validate_unit_bindings(unit, fixed):
    for field in unit["linkages"]:
        # The owning graph supplies these bindings during replay.
        if any(field.get(key) for key in ("local", "eh_handler", "reviewed_static")):
            continue
        symbol = field["symbol"]
        if symbol not in fixed or fixed[symbol] != field["target"]:
            raise Incomplete(f"stored linkage lacks its independent target binding: {symbol}")


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
            symbol = None
            if kind == "GLOBAL" and re.search(r"TH16\s+0x[0-9a-fA-F]+\s+SYMBOL\b", line) and index + 1 < len(lines):
                # Storage declared in an SDK header (a CRT inline function's
                # local static) is named by its decorated symbol on the next line.
                symbol = lines[index + 1].strip().lstrip("/").strip()
            following = []
            for next_line in lines[index + 1:index + 12]:
                if next_line.strip().startswith("//"):
                    continue
                following.append(next_line)
                if any(x in next_line for x in [";", "{", "="]):
                    break
            result[kind].append(dict(address=int(address, 16), source=path.relative_to(ROOT).as_posix(),
                                     line=index + 1, declaration=" ".join(following), symbol=symbol))
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
        if row["symbol"] is not None:
            if row["symbol"] in symbols:
                add(row["symbol"], row["address"], "source-global-symbol-annotation")
            continue
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
