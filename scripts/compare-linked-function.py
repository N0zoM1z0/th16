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
    args = parser.parse_args()
    manifest = tomllib.loads((ROOT / "config/match-units.toml").read_text())
    context = Context()
    if manifest["target_sha256"] != context.manifest["target"]["sha256"]:
        raise ValueError("unit manifest targets another executable")
    unit = manifest["units"][args.unit]
    try:
        result = context.compare(unit)
    except Incomplete as error:
        result = {"result": "incomplete", "reason": str(error)}
    context.finish()
    result.update(unit=args.unit, input_identity=context.before)
    text = json.dumps(result, indent=2) + "\n"
    if args.json:
        from pathlib import Path
        Path(args.json).write_text(text)
    else:
        print(text, end="")
    return 0 if result["result"] == "exact" else 1


if __name__ == "__main__":
    raise SystemExit(main())
