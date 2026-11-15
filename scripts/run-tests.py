#!/usr/bin/env python3
"""Run every scripts/test-*.py control in parallel; nonzero exit on any failure."""
from __future__ import annotations

import argparse
import concurrent.futures
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(path: Path) -> tuple[Path, int, float, str]:
    start = time.monotonic()
    result = subprocess.run([sys.executable, str(path)], cwd=ROOT, capture_output=True, text=True)
    return path, result.returncode, time.monotonic() - start, result.stdout + result.stderr


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=6)
    parser.add_argument("names", nargs="*", help="test file names (default: all)")
    args = parser.parse_args()
    tests = sorted((ROOT / "scripts").glob("test-*.py"))
    if args.names:
        tests = [t for t in tests if t.name in args.names or t.stem in args.names]
    failed = 0
    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        for path, code, seconds, output in pool.map(run, tests):
            print(f"{'ok  ' if code == 0 else 'FAIL'} {seconds:6.1f}s {path.name}")
            if code:
                failed += 1
                print(output[-3000:])
    print(f"{len(tests) - failed}/{len(tests)} test files passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
