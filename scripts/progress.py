#!/usr/bin/env python3
"""Summarize the current local strict comparison without importing upstream totals.

With --svg PATH, also write the progress badge shown in README.md.
"""
from collections import Counter
import argparse
import hashlib
import json
import tomllib

from strict_oracle import Context, ROOT

BAR_WIDTH = 512


def bar(y: int, title: str, ratio: float, value: str, detail: str) -> str:
    return (f'  <text x="24" y="{y}" fill="#f4f4f5" font-family="sans-serif" font-size="13" font-weight="600">{title}</text>\n'
            f'  <text x="536" y="{y}" fill="#f4f4f5" text-anchor="end" font-family="monospace" font-size="13">{value}</text>\n'
            f'  <rect x="24" y="{y + 8}" width="{BAR_WIDTH}" height="12" rx="6" fill="#3b4058"/>\n'
            f'  <rect x="24" y="{y + 8}" width="{BAR_WIDTH * ratio:.2f}" height="12" rx="6" fill="#9b6de3"/>\n'
            f'  <text x="24" y="{y + 37}" fill="#c8cad2" font-family="sans-serif" font-size="12">{detail}</text>\n')


def svg(counts: Counter, rows: list[dict]) -> str:
    total = len(rows)
    total_bytes = sum(row["size"] for row in rows)
    exact = [row for row in rows if row["result"] == "exact"]
    exact_bytes = sum(row["size"] for row in exact)
    compared = counts["exact"] + counts["mismatch"]
    byte_ratio = exact_bytes / total_bytes
    label = (f"TH16 reconstruction progress: annotated bytes {byte_ratio:.2%} exact, "
             f"{compared / total:.2%} of annotations compared over their complete extent")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="560" height="176" role="img" aria-label="{label}">\n'
            '  <rect width="560" height="176" rx="8" fill="#1f2335"/>\n'
            '  <text x="24" y="28" fill="#f4f4f5" font-family="sans-serif" font-size="16" font-weight="600">TH16 reconstruction progress</text>\n'
            + bar(52, "Annotated exact bytes", byte_ratio, f"{byte_ratio:.2%} · strict",
                  f"{len(exact):,} / {total:,} functions · {exact_bytes:,} / {total_bytes:,} bytes")
            + bar(116, "Complete extents compared", compared / total, f"{compared / total:.2%}",
                  f"{counts['exact']:,} exact · {counts['mismatch']:,} mismatch · {counts['incomplete']:,} incomplete")
            + "</svg>\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--svg", help="write the README progress badge to this path")
    args = parser.parse_args()
    context = Context()
    report = json.loads((ROOT / ".analysis/reference-audit.json").read_text())
    if report["input_identity"] != context.before:
        raise SystemExit("The strict report is stale; rerun scripts/audit-reference.py.")
    units = tomllib.loads((ROOT / "config/match-units.toml").read_text())["units"]
    for row in report["functions"]:
        if "unit_sha256" not in row:
            continue
        name = f"reference-{row['target_address']:08x}"
        if name not in units or hashlib.sha256(json.dumps(units[name], sort_keys=True).encode()).hexdigest() != row["unit_sha256"]:
            raise SystemExit(f"Comparison unit {name} differs from its strict report.")
    counts = Counter(row["result"] for row in report["functions"])
    context.finish()
    if args.svg:
        path = ROOT / args.svg
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(svg(counts, report["functions"]))
    print(json.dumps({"local_strict_results": dict(counts), "annotated_candidates": len(report["functions"]),
                      "factory_acceptance": "not-submitted", "source_origin_review": "open"}, indent=2))


if __name__ == "__main__":
    main()
