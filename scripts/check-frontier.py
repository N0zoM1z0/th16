#!/usr/bin/env python3
"""Ratchet for annotated functions that are not exact yet.

config/frontiers.toml lists every non-exact annotation of the current strict
audit: its symbol, original size and SHA-256, the strict result, the candidate
size and, for same-size mismatches, the byte offsets that still differ after
replaying the reviewed linkage fields. The check reads the fresh strict report
(.analysis/reference-audit.json, written by audit-reference.py) and fails when

- an annotation outside the file is no longer exact (an exact regression),
- a recorded mismatch becomes incomplete or gains a differing byte, or
- the original extent of an entry changed.

Strictly smaller residuals, new exact results and changed incomplete sizes
are reported; record them with --update. Diagnostic only: exact credit still
comes from audit-reference.py and the canonical units.

Usage:
  scripts/check-frontier.py                 check every annotation
  scripts/check-frontier.py 0x41dcb0 ...    check selected frontier entries
  scripts/check-frontier.py --update        record improvements (refused on regression)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/frontiers.toml"
REPORT = ROOT / ".analysis/reference-audit.json"
HEADER = """\
# Annotated functions that are not exact yet, checked by scripts/check-frontier.py.
# residual: hex byte offsets (ranges) that differ from the original after
# replaying reviewed linkage fields (same-size mismatches only). Never edit by
# hand; record improvements with scripts/check-frontier.py --update."""


def parse_offsets(items: list[str]) -> set[int]:
    offsets: set[int] = set()
    for item in items:
        low, _, high = item.partition("-")
        offsets.update(range(int(low, 16), int(high or low, 16) + 1))
    return offsets


def format_offsets(offsets: set[int]) -> list[str]:
    runs: list[str] = []
    ordered = sorted(offsets)
    start = previous = None
    for value in ordered + [None]:
        if start is not None and value == previous + 1:
            previous = value
            continue
        if start is not None:
            runs.append(f"{start:X}" if start == previous else f"{start:X}-{previous:X}")
        start = previous = value
    return runs


def residual(original: bytes, candidate: bytes, linkages: list[dict]) -> set[int]:
    """Offsets that differ after applying the Oracle's encoded fields."""
    replayed = bytearray(candidate)
    for field in linkages:
        offset, width = field["offset"], field["width"]
        replayed[offset:offset + width] = field["encoded"].to_bytes(
            width, "little", signed=field["type"].startswith("REL")
        )
    return {index for index, (left, right) in enumerate(zip(original, replayed, strict=True)) if left != right}


def measure(row: dict, read_target, read_candidate) -> dict:
    """The frontier entry for one strict-report row."""
    address, size = row["target_address"], row["size"]
    original = read_target(address, size)
    entry = {"symbol": row["symbol"], "source": row["source"], "size": size,
             "target_sha256": hashlib.sha256(original).hexdigest(), "result": row["result"]}
    if "compared_size" in row:
        if row["compared_size"] != size:
            raise ValueError(f"Strict comparison size differs from the target extent at {address:#010x}.")
        candidate = read_candidate(row["candidate_address"], size)
        differences = residual(original, candidate, row["linkages"])
        if len(differences) != size - row["matched_bytes"]:
            raise ValueError(f"Strict mismatch count differs from replayed bytes at {address:#010x}.")
        entry["candidate_size"] = size
        entry["residual"] = format_offsets(differences)
    else:
        entry["candidate_size"] = row.get("candidate_size")
    return entry


def evaluate(recorded: dict[int, dict], current: dict[int, dict], exact: set[int], selected=None):
    """Compare recorded and current entries; returns (lines, regressed, updates)."""
    lines, regressed, updates = [], False, {}
    if selected is None:
        for address in sorted(current.keys() - recorded.keys()):
            lines.append(f"REGRESSED 0x{address:08x} {current[address]['symbol']}: was exact, "
                         f"now {current[address]['result']}")
            regressed = True
    for address in sorted(recorded if selected is None else selected):
        old = recorded[address]
        label = f"0x{address:08x} {old['symbol']}"
        if address in exact:
            lines.append(f"EXACT     {label}")
            updates[address] = None
            continue
        new = current.get(address)
        if new is None:
            lines.append(f"MISSING   {label}: no longer annotated")
            regressed = True
            continue
        if new["target_sha256"] != old["target_sha256"] or new["size"] != old["size"]:
            lines.append(f"REGRESSED {label}: original extent changed")
            regressed = True
            continue
        if old["result"] == "mismatch":
            if new["result"] != "mismatch":
                lines.append(f"REGRESSED {label}: mismatch became {new['result']}")
                regressed = True
                continue
            before, after = parse_offsets(old["residual"]), parse_offsets(new["residual"])
            if after - before:
                lines.append(f"REGRESSED {label}: newly differing offsets "
                             + ", ".join(format_offsets(after - before)))
                regressed = True
            elif after < before:
                lines.append(f"IMPROVED  {label}: {len(after)} bytes differ (recorded {len(before)})")
                updates[address] = new
            else:
                lines.append(f"OK        {label}: {len(after)} bytes differ")
        elif new["result"] == "mismatch":
            lines.append(f"IMPROVED  {label}: incomplete became a same-size mismatch")
            updates[address] = new
        elif new.get("candidate_size") != old.get("candidate_size"):
            lines.append(f"CHANGED   {label}: candidate size {old.get('candidate_size')} -> "
                         f"{new.get('candidate_size')} of {new['size']}")
            updates[address] = new
        else:
            lines.append(f"OK        {label}: incomplete")
    return lines, regressed, updates


def render(entries: dict[int, dict]) -> str:
    out = [HEADER]
    for address in sorted(entries):
        e = entries[address]
        out.append(f'\n[frontier."0x{address:08x}"]')
        out.append(f'symbol = {json.dumps(e["symbol"])}')
        out.append(f'source = {json.dumps(e["source"])}')
        out.append(f'size = {e["size"]}')
        out.append(f'target_sha256 = "{e["target_sha256"]}"')
        out.append(f'result = "{e["result"]}"')
        if e.get("candidate_size") is not None:
            out.append(f'candidate_size = {e["candidate_size"]}')
        if "residual" in e:
            out.append(f'residual = {json.dumps(e["residual"])}')
    return "\n".join(out) + "\n"


def load_recorded() -> dict[int, dict]:
    if not CONFIG.exists():
        return {}
    return {int(k, 16): v for k, v in tomllib.loads(CONFIG.read_text()).get("frontier", {}).items()}


def current_state():
    sys.path.insert(0, str(ROOT / "scripts"))
    from linked_image import PEImage
    from strict_oracle import Context

    context = Context()
    report = json.loads(REPORT.read_text())
    if report["input_identity"] != context.before:
        raise SystemExit("The strict report is stale; rerun scripts/audit-reference.py.")
    target = PEImage(ROOT / "resources/th16.exe")
    candidate = PEImage(ROOT / "build/reference-candidate/th16.exe")
    sizes = {f["symbol"]: f["size"] for f in context.linked["functions"]}
    exact, current = set(), {}
    for row in report["functions"]:
        if row["result"] == "exact":
            exact.add(row["target_address"])
            continue
        boundary = context.boundaries.get(row["target_address"])
        if boundary is None:
            raise SystemExit(f"No target extent for frontier 0x{row['target_address']:08x}.")
        row = dict(row, size=int(boundary["size"]), candidate_size=sizes.get(row.get("symbol")),
                   symbol=row.get("symbol") or boundary["current_name"])
        current[row["target_address"]] = measure(row, target.read_address, candidate.read_address)
    context.finish()
    return exact, current


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("addresses", nargs="*", help="frontier entries to check (default: all)")
    parser.add_argument("--update", action="store_true", help="record improvements")
    args = parser.parse_args()
    recorded = load_recorded()
    selected = None
    if args.addresses:
        selected = [int(a, 16) for a in args.addresses]
        unknown = [hex(a) for a in selected if a not in recorded]
        if unknown:
            print(f"unknown frontier(s): {', '.join(unknown)}", file=sys.stderr)
            return 2
    exact, current = current_state()
    if not recorded:
        if not args.update:
            print(f"{CONFIG.relative_to(ROOT)} is missing; create it with --update", file=sys.stderr)
            return 2
        CONFIG.write_text(render(current))
        print(f"recorded {len(current)} frontier(s) in {CONFIG.relative_to(ROOT)}")
        return 0
    lines, regressed, updates = evaluate(recorded, current, exact, selected)
    print("\n".join(lines))
    if args.update:
        if regressed:
            print("not recording: resolve the regressions first", file=sys.stderr)
            return 1
        for address, entry in updates.items():
            if entry is None:
                recorded.pop(address, None)
            else:
                recorded[address] = entry
        CONFIG.write_text(render(recorded))
        print(f"recorded {len(updates)} change(s) in {CONFIG.relative_to(ROOT)}")
    return 1 if regressed else 0


if __name__ == "__main__":
    raise SystemExit(main())
