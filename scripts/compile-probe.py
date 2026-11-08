#!/usr/bin/env python3
"""Compile one C/C++ experiment to COFF or MSVC LTCG IR."""
import argparse
from pathlib import Path
import sys
import toolchain as tc

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("-o", "--output", type=Path, required=True)
parser.add_argument("--ltcg", action="store_true")
args, flags = parser.parse_known_args()
args.output.parent.mkdir(parents=True, exist_ok=True)
options = ["/nologo", "/c", "/O2", "/Oy-", "/MT", "/EHsc"]
if args.ltcg:
    options.append("/GL")
status, output = tc.run("cl", [*options, *flags, "/Fo" + tc.winpath(args.output), tc.winpath(args.source)])
print(output, end="")
sys.exit(status)
