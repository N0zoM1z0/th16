#!/usr/bin/env python3
"""Replay one declared candidate through the Factory/TH10-style strict Oracle."""
import argparse
import json
import tomllib

from strict_oracle import Context, Incomplete, ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("unit")
    parser.add_argument("--json", type=str)
    parser.add_argument("--require-cold", action="store_true", help="require a clean-output-graph build")
    parser.add_argument("--rebind-candidate", action="store_true",
                        help="resolve the declared target and symbol in the current link")
    args = parser.parse_args()
    manifest = tomllib.loads((ROOT / "config/match-units.toml").read_text())
    context = Context(require_cold=args.require_cold)
    if manifest["target_sha256"] != context.manifest["target"]["sha256"]:
        raise ValueError("unit manifest targets another executable")
    unit = manifest["units"][args.unit]
    try:
        if args.rebind_candidate:
            entries = [line.split() for line in (context.directory / "functions.txt").read_text().splitlines()]
            addresses = [int(candidate, 0) for original, candidate, symbol in entries
                         if int(original, 0) == unit["target_address"] and symbol == unit["symbol"]]
            if len(addresses) != 1:
                raise Incomplete("declared target and symbol lack one current function-map entry")
            unit = dict(unit, candidate_address=addresses[0])
        result = context.compare(unit)
    except Incomplete as error:
        result = {"result": "incomplete", "reason": str(error)}
    context.finish()
    result.update(unit=args.unit, artifact_kind=unit["artifact_kind"],
                  input_identity=context.before, build_kind=context.receipt["coldness"])
    text = json.dumps(result, indent=2) + "\n"
    if args.json:
        from pathlib import Path
        Path(args.json).write_text(text)
    else:
        print(text, end="")
    return 0 if result["result"] == "exact" else 1


if __name__ == "__main__":
    raise SystemExit(main())
