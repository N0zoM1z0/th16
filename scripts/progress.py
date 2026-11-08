#!/usr/bin/env python3
"""Summarize the current local strict comparison without importing upstream totals."""
from collections import Counter
import hashlib
import json
import tomllib

from strict_oracle import Context, ROOT

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
print(json.dumps({"local_strict_results": dict(counts), "annotated_candidates": len(report["functions"]),
                  "factory_acceptance": "not-submitted", "source_origin_review": "open"}, indent=2))
