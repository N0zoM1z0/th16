#!/usr/bin/env python3
"""Run a selected historical MSVC tool; remaining arguments use MSVC syntax."""
import argparse
import sys
import toolchain

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("tool", choices=["cl", "link", "lib", "dumpbin", "rc", "cvtres"])
parser.add_argument("arguments", nargs=argparse.REMAINDER)
args = parser.parse_args()
status, output = toolchain.run(args.tool, args.arguments)
print(output, end="")
sys.exit(status)
