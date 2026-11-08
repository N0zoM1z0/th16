#!/usr/bin/env python3
"""Import, attest and query TH16 using the Factory shared Ghidra runtime."""
import argparse
import fcntl
import importlib.util
from pathlib import Path
import subprocess
import sys

from shared_runtime import command

ROOT = Path(__file__).resolve().parents[1]


def target():
    spec = importlib.util.spec_from_file_location("verify_target", ROOT / "scripts/verify-target.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.verify()


def attestation(manifest, data):
    t, p = manifest["target"], manifest["pe"]
    addresses = [int(p["entry_point"], 0), int(p["text_start"], 0)]
    for section in p["sections"]:
        if section["raw_size"] and section["name"] != ".rsrc":
            addresses.append(int(p["image_base"], 0) + int(section["rva"], 0))
    addresses = sorted(set(addresses))
    samples = []
    for address in addresses:
        rva = address - int(p["image_base"], 0)
        section = next(s for s in p["sections"] if int(s["rva"], 0) <= rva < int(s["rva"], 0) + s["raw_size"])
        offset = int(section["raw_offset"], 0) + rva - int(section["rva"], 0)
        samples += [hex(address), data[offset:offset + 16].hex()]
    return ["-postScript", "VerifyTarget.java", t["sha256"], t["md5"], t["filename"],
            str(t["size"]), p["image_base"], str(p["size_of_image"]), p["entry_point"],
            p["text_start"], str(len(addresses)), *samples]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["import", "check", "export", "query", "decompile", "function_context"])
    parser.add_argument("arguments", nargs="*")
    args = parser.parse_args()
    manifest, data = target()
    factory = (ROOT / ".tools/factory-runtime.py").resolve().parents[1]
    project = ROOT / "ghidra-project"
    project.mkdir(exist_ok=True)
    state = ROOT / ".analysis/ghidra"
    state.mkdir(parents=True, exist_ok=True)
    t, p = manifest["target"], manifest["pe"]
    if args.operation in {"query", "decompile", "function_context"}:
        return subprocess.call([sys.executable, str(factory / "scripts/ghidra-repository-provider.py"),
            "--repository", str(ROOT), "--standalone-project", args.operation, *args.arguments])
    if args.arguments:
        parser.error("this operation takes no additional arguments")
    options = [str(project), "th16", "-max-cpu", "1", "-scriptPath", str(ROOT / "scripts/ghidra")]
    if args.operation == "import":
        if (project / "th16.gpr").exists():
            parser.error("project exists; use check or export to preserve existing analysis")
        options += ["-import", str(ROOT / "resources" / t["filename"]), "-analysisTimeoutPerFile", "600"]
    else:
        options += ["-process", t["filename"], "-readOnly", "-noanalysis"]
    options += attestation(manifest, data)
    if args.operation in {"import", "export"}:
        options += ["-postScript", "ExportInventory.java", str(state / "functions.csv"),
                    str(state / "function-origins.csv"), p["text_start"], p["text_end"], "ghidra-initial-import"]
    with (state / "headless.lock").open("a") as gate, (project / "workflow.lock").open("a") as project_gate:
        fcntl.flock(gate, fcntl.LOCK_EX)
        fcntl.flock(project_gate, fcntl.LOCK_EX)
        result = subprocess.run(command("ghidra", *options), cwd=ROOT, capture_output=True, text=True)
    output = result.stdout + result.stderr
    (state / f"{args.operation}.log").write_text(output)
    print(output)
    if result.returncode or "FACTORY_GHIDRA_ATTESTATION_V1:" not in output or "ERROR REPORT SCRIPT ERROR" in output:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
