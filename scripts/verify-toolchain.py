#!/usr/bin/env python3
"""Verify pinned tools; optionally exercise C, C++, LTCG, RC, PE link and Wine."""
import argparse
import hashlib
import json
import struct
import subprocess
import tomllib

import toolchain as tc
from shared_runtime import command


def execute():
    output = tc.ROOT / "build/toolchain-smoke"
    output.mkdir(parents=True, exist_ok=True)
    logs = []

    def run(tool, *args, accepted=(0,)):
        code, text = tc.run(tool, list(args))
        logs.append(f"{tool} {' '.join(args)}\n{text}")
        (output / "commands.log").write_text("\n".join(logs))
        if code not in accepted:
            raise RuntimeError(f"{tool} exited {code}:\n{text}")
        return text

    compiler = run("cl", "/?")
    # This linker returns 1100 (76 through Wine's Unix exit status) for help.
    linker = run("link", "/?", accepted=(0, 76))
    if "19.10.25017" not in compiler or "14.10.25017" not in linker:
        raise ValueError("unexpected compiler/linker banner")
    run("rc", "/nologo", "/fo" + tc.winpath(output / "smoke.res"),
        tc.winpath(tc.ROOT / "probes/toolchain-smoke.rc"))
    for variant, extra in [("coff", []), ("ltcg", ["/GL"])]:
        objects = []
        for extension in ["c", "cpp"]:
            obj = output / f"{variant}-{extension}.obj"
            run("cl", "/nologo", "/c", "/O2", "/Oy-", "/MT", "/EHsc", *extra,
                "/Fo" + tc.winpath(obj), tc.winpath(tc.ROOT / f"probes/toolchain-smoke.{extension}"))
            data = obj.read_bytes()
            if variant == "coff" and struct.unpack_from("<H", data)[0] != 0x14C:
                raise ValueError("expected i386 COFF")
            if variant == "ltcg" and data[:4] != bytes.fromhex("0000ffff"):
                raise ValueError("expected LTCG intermediate object")
            objects.append(tc.winpath(obj))
        exe = output / f"{variant}.exe"
        run("link", "/nologo", "/LTCG", "/INCREMENTAL:NO", "/MACHINE:X86", "/OPT:NOICF",
            "/SUBSYSTEM:CONSOLE,5.01", "/OUT:" + tc.winpath(exe), "/MAP:" + tc.winpath(exe.with_suffix(".map")),
            *objects, tc.winpath(output / "smoke.res"), "kernel32.lib", "user32.lib", "gdi32.lib",
            "d3d9.lib", "d3dx9.lib", "dinput8.lib", "dsound.lib", "dxguid.lib")
        data = exe.read_bytes()
        offset = struct.unpack_from("<I", data, 0x3C)[0]
        if data[offset:offset + 6] != b"PE\0\0\x4c\x01" or struct.unpack_from("<H", data, offset + 24)[0] != 0x10B:
            raise ValueError("expected PE32 i386 image")
        with (output / f"{variant}-runtime.log").open("w+") as runtime:
            result = subprocess.run(["xvfb-run", "-a", *command("wine", str(exe))],
                stdout=runtime, stderr=subprocess.STDOUT, cwd=tc.ROOT)
            runtime.seek(0)
            text = runtime.read()
        if result.returncode or "TH16 toolchain smoke: 42" not in text:
            raise RuntimeError(f"{variant} runtime failed: {text}")
        print(f"PASS {variant}: C + C++, resources, PE32 link, Wine execution")
    (output / "result.json").write_text(json.dumps({"status": "pass", "compiler": "19.10.25017",
        "variants": ["coff", "ltcg"], "exactness_credit": "none"}, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    lock = tomllib.loads((tc.ROOT / "config/tools.lock.toml").read_text())
    for row in lock.get("compiler_files", []):
        actual = hashlib.sha256((tc.PREFIX / row["path"]).read_bytes()).hexdigest()
        if actual != row["sha256"]:
            raise ValueError(f"toolchain file hash mismatch: {row['path']}")
    if not lock.get("compiler_files"):
        raise ValueError("compiler component hashes are not pinned")
    for path in [*tc.INCLUDE, *tc.LIB]:
        if not path.is_dir():
            raise FileNotFoundError(path)
    print("Pinned historical toolchain files verified")
    if args.execute:
        execute()


if __name__ == "__main__":
    main()
