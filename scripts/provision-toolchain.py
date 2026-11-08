#!/usr/bin/env python3
"""Provision hash-pinned Microsoft payloads in a shared installation.

Adapted from johnthreekay/th16 scripts/setup.py (CC0), commit
2b846da735ac71f68b1dc74e8194c8c8d98e2869. Wine state remains in this game.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREFIX = None
DOWNLOADS = None

# th16.exe 1.00a, the only release.
ORIG_SHA256 = "c11776019f083978e66027e7394dafb1fb9543afca986f28049a49417e341929"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, dest, expected):
    if dest.exists() and (expected is None or sha256(dest) == expected):
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    print(f"  downloading {dest.name}")
    if shutil.which("aria2c"):
        download_env = dict(os.environ)
        for name in ("ALL_PROXY", "all_proxy"):
            if download_env.get(name, "").startswith("socks"):
                download_env.pop(name)
        subprocess.run([
            "aria2c", "--continue=true", "--allow-overwrite=true",
            "--auto-file-renaming=false", "--file-allocation=none", "-x4", "-s4",
            "--console-log-level=warn", "--summary-interval=0", "--download-result=hide",
            "--show-console-readout=false",
            "--max-tries=5", "--retry-wait=2", "--timeout=60",
            "--checksum=sha-256=" + expected, "--dir=" + str(tmp.parent),
            "--out=" + tmp.name, url,
        ], check=True, env=download_env)
    else:
        with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as f:
            shutil.copyfileobj(r, f, 1 << 20)
    got = sha256(tmp)
    if expected is not None and got != expected:
        tmp.unlink()
        sys.exit(f"SHA-256 mismatch for {dest.name}: got {got}, expected {expected}")
    tmp.rename(dest)
    if expected is None:
        print(f"    (unpinned) sha256 {got}")


def extract_vsix(archive, dest):
    # VSIX payloads keep their install layout under Contents/, with
    # percent-encoded member names.
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            name = urllib.parse.unquote(info.filename)
            if not name.startswith("Contents/") or name.endswith("/"):
                continue
            out = dest / name[len("Contents/"):]
            out.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as src, open(out, "wb") as dst:
                shutil.copyfileobj(src, dst)


def extract_msi(msi, dest):
    # Native extraction avoids registering SDK installers in a Wine prefix.
    dest.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["msiextract", "-C", str(dest), str(msi)],
        check=True, stdout=subprocess.DEVNULL,
    )


def extract_dxsdk(exe, dest):
    # DXSDK_Jun10.exe is a cab-based self-extractor. Only the headers and x86
    # import libraries are needed.
    stage = DOWNLOADS / "dxsdk-unpacked"
    if not stage.exists():
        stage.mkdir(parents=True)
        subprocess.run(["cabextract", "-q", "-d", str(stage), str(exe)], check=True)
    src = stage / "DXSDK"
    for sub in ("Include", "Lib/x86"):
        shutil.copytree(src / sub, dest / sub, dirs_exist_ok=True)
    shutil.rmtree(stage)


def setup_toolchain():
    packages = json.loads((ROOT / "config/toolchain-payloads.json").read_text())
    stamp_dir = PREFIX / "stamps"
    stamp_dir.mkdir(parents=True, exist_ok=True)
    for pkg in packages:
        key = f"{pkg['id']}-{pkg['version']}"
        stamp = stamp_dir / key
        if stamp.exists():
            continue
        print(f"{pkg['id']} {pkg['version']}")
        pkg_dir = DOWNLOADS / key
        with ThreadPoolExecutor(max_workers=3) as pool:
            tasks = [pool.submit(download, pl["url"], pkg_dir / pl["file"], pl["sha256"])
                     for pl in pkg["payloads"]]
            for task in tasks:
                task.result()
        first = pkg_dir / pkg["payloads"][0]["file"]
        if pkg["kind"] == "vsix":
            extract_vsix(first, PREFIX / "vs")
        elif pkg["kind"] == "msi":
            extract_msi(first, PREFIX / "sdk")
        elif pkg["kind"] == "dxsdk":
            extract_dxsdk(first, PREFIX / "dxsdk")
        stamp.touch()



def main():
    global PREFIX, DOWNLOADS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    PREFIX = args.destination.expanduser().resolve()
    DOWNLOADS = PREFIX / "downloads"
    PREFIX.mkdir(parents=True, exist_ok=True)
    setup_toolchain()
    selection = ROOT / ".tools/toolchain"
    if selection.is_symlink():
        if selection.resolve() != PREFIX:
            raise ValueError("a different toolchain is already selected")
    elif selection.exists():
        raise ValueError("refusing to replace an existing toolchain")
    else:
        selection.symlink_to(PREFIX, target_is_directory=True)
    print("Historical compiler and SDKs ready; run scripts/verify-toolchain.py --execute.")

if __name__ == "__main__":
    main()
