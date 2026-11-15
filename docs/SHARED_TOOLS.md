# Shared tools

The game-local `scripts/shared_runtime.py` forwards to Factory's
`runtime/run.py` through the ignored `.tools/factory-runtime.py` selector. No
MCP connection is required. `.tools/shared-runtimes.json` selects the shared
Ghidra/JDK installation and this repository's `.tools/wine` win32 prefix.
Java settings, caches and temporary files live in `.analysis/factory-runtime/`.

```sh
./scripts/shared_runtime.py --describe ghidra
./scripts/shared_runtime.py --describe wine
./scripts/shared_runtime.py java -- -version
xvfb-run -a ./scripts/shared_runtime.py wine -- cmd /c ver
./scripts/shared_runtime.py wineserver -- -k
```

The final command recovers only this game's Wine server. Ghidra commands take
both `.analysis/ghidra/headless.lock` and `ghidra-project/workflow.lock` so local
operations coordinate with the native Factory provider. `import` refuses an
existing project. `check` verifies the original file, Ghidra's stored hashes,
image base, entry function and mapped-byte samples. Ordinary read-only queries
reuse the selected project without repeating auto-analysis.

## Reattach or provision

Factory's `scripts/provision-shared-runtimes.py` accepts a TOML file containing
just this game's `[[repositories]]` entry with `id = "th16"` and its absolute
`path`. Run it first without `--apply`, review the selection, then apply. Do
not move or replace another game's installation or state.

Historical compiler and SDK packages have pinned Microsoft URLs, sizes and
SHA-256 hashes in `config/toolchain-payloads.json`. Install them once into a
Factory-owned shared location:

```sh
scripts/repo-python scripts/provision-toolchain.py --destination /path/to/factory/.factory/shared-tools/msvc-14.10.25017-v141-xp
uv venv --python /usr/bin/python3 .venv
uv pip install --python .venv/bin/python -r requirements.lock.txt
scripts/repo-python scripts/verify-toolchain.py --execute
```

Provisioning requires `msiextract`, `cabextract` and optionally `aria2c`.
Compiler use requires system Wine, `xvfb-run` and the attached shared runtime.
`.tools/toolchain` points to the shared payload, while compiler invocations
always use the game's prefix. SDK MSI files are extracted natively; installing
their registry entries in Wine is unnecessary. Build output goes through files
because the compiler's persistent PDB server can keep stdout pipes open.

## Factory registration

`.analysis/factory-registration.toml` contains the private `th16` repository and
`th16-ghidra` native provider blocks. `.analysis/factory-validation.toml` is an
isolated one-game configuration used to validate discovery and an entry-function
query. Factory state/evidence live outside the game repository. The shared
service configuration and endpoint have not been changed.

Activation is a separate operator step: merge the reviewed blocks into the
existing private service configuration, retain shared runtime/compiler mounts,
coordinate active jobs, and restart at a safe boundary. Use the existing single
Factory endpoint. The inventory adapter imports provisional boundaries only.
