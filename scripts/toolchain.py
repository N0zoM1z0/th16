"""Game-local compiler settings; tool payloads are shared, Wine state is local."""
import os
from pathlib import Path
import subprocess
import tempfile

from shared_runtime import command

ROOT = Path(__file__).resolve().parents[1]
PREFIX = ROOT / ".tools/toolchain"
MSVC = PREFIX / "vs/VC/Tools/MSVC/14.10.25017"
BIN = MSVC / "bin/Hostx86/x86"
SDK71A = PREFIX / "sdk/Program Files/Microsoft SDKs/Windows/v7.1A"
KITS10 = PREFIX / "sdk/Program Files/Windows Kits/10"
DXSDK = PREFIX / "dxsdk"
INCLUDE = [MSVC / "include", KITS10 / "Include/10.0.10240.0/ucrt", SDK71A / "Include", DXSDK / "Include"]
LIB = [MSVC / "lib/x86", KITS10 / "Lib/10.0.10240.0/ucrt/x86", SDK71A / "Lib", DXSDK / "Lib/x86"]


def winpath(path):
    return "Z:" + str(Path(path).absolute()).replace("/", "\\")


def environment():
    env = dict(os.environ)
    env.update(INCLUDE=";".join(map(winpath, INCLUDE)), LIB=";".join(map(winpath, LIB)),
               CL="", _CL_="", LINK="", _LINK_="",
               WINEDLLOVERRIDES="mscoree,mshtml=", WINEDEBUG="-all",
               _MSPDBSRV_ENDPOINT_="th16-reconstruction")
    auth = ROOT / ".tools/wine-auth/bin"
    if auth.is_dir():
        env["PATH"] = str(auth) + os.pathsep + env.get("PATH", os.defpath)
    return env


def run(tool, arguments, cwd=None):
    executable = SDK71A / "Bin/RC.Exe" if tool == "rc" else BIN / (tool + ".exe")
    if not executable.is_file():
        raise FileNotFoundError(f"missing tool: {executable}; run scripts/provision-toolchain.py")
    log_dir = ROOT / "build"
    log_dir.mkdir(exist_ok=True)
    # Persistent mspdbsrv can inherit stdout; a regular file avoids pipe hangs.
    with tempfile.TemporaryFile(dir=log_dir) as output:
        result = subprocess.run(["xvfb-run", "-a", *command("wine", str(executable), *arguments)],
            cwd=cwd or ROOT, env=environment(), stdin=subprocess.DEVNULL,
            stdout=output, stderr=subprocess.STDOUT)
        output.seek(0)
        return result.returncode, output.read().decode("utf-8", "replace")
