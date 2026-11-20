#!/usr/bin/env python3
"""Replay one declared candidate through the Factory/TH10-style strict Oracle."""
import argparse
import hashlib
import json
import tomllib

from reference_bindings import bindings, function_map, markers, validate_unit_bindings
from strict_oracle import Context, Incomplete, ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("unit")
    parser.add_argument("--json", type=str)
    parser.add_argument("--require-cold", action="store_true", help="require a clean-output-graph build")
    parser.add_argument("--rebind-candidate", action="store_true",
                        help="resolve the declared target and symbol in the current link")
    args = parser.parse_args()
    manifest_path = ROOT / "config/match-units.toml"
    payload = manifest_path.read_bytes()
    manifest = tomllib.loads(payload.decode("utf-8"))
    context = Context(require_cold=args.require_cold)
    if manifest["target_sha256"] != context.manifest["target"]["sha256"]:
        raise ValueError("unit manifest targets another executable")
    unit = manifest["units"][args.unit]
    try:
        functions = function_map(context)
        entries = [(candidate, symbol) for original, candidate, symbol in functions
                   if original == unit["target_address"]]
        if len(entries) != 1 or entries[0][1] != unit["symbol"]:
            raise Incomplete("declared target and symbol lack one current function-map entry")
        if args.rebind_candidate:
            unit = dict(unit, candidate_address=entries[0][0])
        elif unit["candidate_address"] != entries[0][0]:
            raise Incomplete("stored candidate address differs from the current function map")
        fixed, _ = bindings(context, functions, markers())
        validate_unit_bindings(unit, fixed)
        result = context.compare(unit)
    except Incomplete as error:
        result = {"result": "incomplete", "reason": str(error)}
    context.finish()
    if manifest_path.read_bytes() != payload:
        raise ValueError("match unit manifest changed during evaluation")
    result.update(unit=args.unit, artifact_kind=unit["artifact_kind"],
                  input_identity={**context.before, "config/match-units.toml": hashlib.sha256(payload).hexdigest()},
                  build_kind=context.receipt["coldness"])
    text = json.dumps(result, indent=2) + "\n"
    if args.json:
        from pathlib import Path
        Path(args.json).write_text(text)
    else:
        print(text, end="")
    return 0 if result["result"] == "exact" else 1


if __name__ == "__main__":
    raise SystemExit(main())
