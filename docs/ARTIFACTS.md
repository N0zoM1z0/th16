# Local artifacts and storage

Ignored files include required private inputs, incremental caches and evidence.
Do not treat every ignored directory as disposable. Shared tool selectors point
outside this repository; never follow them when cleaning local outputs.

## Preserve for continued work

| Local path | Reason |
| --- | --- |
| `resources/th16.exe`, `../game_exe/` | Canonical private target and supplied game files |
| `.tools/wine/`, `.tools/shared-runtimes.json`, tool selectors | Game-owned runtime and attached shared installations |
| `.venv/` | Locked comparison dependencies |
| `ghidra-project/` | Imported and analyzed target database |
| `build/reference-candidate/` | Current PE/MAP/PDB, function map, receipt, object/dependency cache and non-LTCG symbol-discovery cache |
| `.analysis/reference-audit.json` | Current fingerprinted results read by `scripts/progress.py` |
| `.analysis/factory-registration.toml`, `.analysis/factory-validation*` | Staged private registration and isolated validation evidence |
| `.analysis/ghidra/`, diagnostic notes and regression records | Analysis evidence and failed-experiment context |
| `_reference/johnthreekay-th16/` | Pinned, unchanged upstream checkout |

Deleting object or symbol-discovery caches would force substantial recompilation
and defeat the requested incremental workflow. Even repeated per-unit PDB names
belong to separate compiler invocations. Keep the complete current graph.

## Compressed historical evidence

The 2026-11-08 cleanup retained evidence while reducing its storage:

- `.analysis/baselines/*/reference-audit.json.gz`: historical result snapshots.
- `.analysis/reference-first-audit/report.json.gz`: original 332-pass audit;
  its `build-receipt.json` remains uncompressed in the same directory.
- `.analysis/pdb-types.txt.gz` and `pdb-globals.txt.gz`: unused LLVM text dumps.
- `.analysis/reference-initial-link.tar.xz`: preliminary link artifacts that
  predate the current graph; these are not the active Oracle inputs.
- `.tools/vs2017.manifest.json.gz` and `tools_toolchain_*-tree.json.gz`:
  unused historical tool-discovery downloads. Runtime selectors stay uncompressed.
- `.analysis/experiments/atan2-intrinsic-draft.py.gz`: withdrawn, unvalidated
  proof experiment, outside the active scripts and Oracle identity.

Read a report without expanding it permanently:

```sh
python3 - <<'PY'
import gzip, json
with gzip.open('.analysis/baselines/c1b5ada/reference-audit.json.gz', 'rt') as stream:
    print(json.load(stream)['counts'])
PY
```

If the preliminary link artifacts are needed, restore them with
`tar -xJf .analysis/reference-initial-link.tar.xz -C .analysis/`.
Archives were decompressed and checked against the original bytes before their
uncompressed copies were removed. Paths in older notes may omit the new `.gz`
suffix; those notes describe the original checkpoints.

## Rebuildable outputs removed

Cleanup removed the game-local Ghidra packed-database cache, old toolchain smoke
binaries and standalone probe outputs at the top of `build/`. Their source,
logs and actual Ghidra project are retained. Ghidra recreates its cache on use;
`python3 scripts/verify-toolchain.py --execute` recreates smoke outputs.
Regenerated caches and smoke outputs will consume storage again.

The operation reclaimed about **78 MiB** of allocated local storage. The exact
paths, byte counts, source hashes for archived files and preserved current
artifact hashes are recorded in `.analysis/cleanup-20261108.json`. Current build
artifacts, the active audit and private target were unchanged. The user-supplied
extraction and shared Factory installations were not cleaned.

For later cleanup, inspect sizes first, identify consumers, check for active
jobs, and remove only known reproducible scratch outputs. Compress historical
evidence when practical. Verify `scripts/progress.py` afterwards; no cold build
is needed solely to clean unused outputs or edit documentation.
