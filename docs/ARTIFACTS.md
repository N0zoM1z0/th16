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
| `.analysis/audio-release-baseline/` | Latest accepted checkpoint regression inputs, kept uncompressed |
| `.analysis/audio-initialize-baseline/`, `.analysis/experiments/audio-initialize-unvalidated/` | Unvalidated initialization draft, its clean base and review notes |
| `.analysis/enemy-motion-work/` | Boss, spellcard and projectile source trials, baseline report and final regression evidence |
| `.analysis/bullet-ex-work/` | Curve laser exact comparison, large projectile dispatcher trials, private helper controls and partial instruction-emulation diagnostics |
| `.analysis/boss-core-work/` | Boss damage/feedback and Player damage traversal trials, native layout probe, partial instruction-emulation diagnostics and strict regression evidence |
| `.analysis/boss-flow-work/` | Boss shield/collision source trials, complete logic/damage packets, historical NaN-payload control, native shield/collision fixtures, explicit SEH/no-frame prefix controls, failed combined image and final regression evidence |
| `.analysis/curve-layout-work/` | Curve elapsed/integration source trials, complete motion owners, typed layout probe, starting/final images, expanded native matrix, independent-model negative control and strict regression evidence |
| `.analysis/boss-stats-work/` | Restored Boss statistics trials; curve state/vector source work, complete owner packets, typed layout probe, three-image native matrices, historical control, final tested image and regression evidence |
| `.analysis/boss-lifetimes-work/` | Planar damage/frame-context trials, final complete owners, initialized native Boss phase fixtures and independent models, no-op control, typed layout evidence, prior-suite replay and strict regression evidence |
| `.analysis/boss-damage-work/` | Damage traversal/impact source trials, complete owner packets, typed snapshot fixtures and historical control, initialized-CRT geometry/Boss execution, protocol controls, invalid ABI/startup notes and final regression evidence |
| `.analysis/laser-core-work/` | Laser/context source trials, large ECL context, native debugger and complete fixtures, parameter observation controls, failed prototypes and restored-build regression evidence |
| `.analysis/ecl-dispatch-work/` | Large ECL shared-position and spell-name source trials, complete diagnostic code/table/map packets, native movement and spell-prefix fixtures, final tested image, scope refusals and regression evidence |
| `.analysis/ecl-context-work/` | ECL coordinate evaluation and animation operand trials, typed lookup fixtures, native animation snapshots and historical-image control, invalid-opcode notes and final source regression evidence |
| `.analysis/ecl-angle-work/` | ECL angle/orbit initialization trials, complete code/table/map packets, native full-state angle/orbit fixtures, pre-rebuild receipt refusal, final tested image and source regression evidence |
| `.analysis/archives/`, `.analysis/cleanup-handoff-20261112.json` | Verified historical evidence and recovery index |
| `.analysis/factory-registration.toml`, `.analysis/factory-validation*` | Staged private registration and isolated validation evidence |
| `.analysis/ghidra/`, diagnostic notes and regression records | Analysis evidence and failed-experiment context |
| `_reference/johnthreekay-th16/` | Pinned, unchanged upstream checkout |

Deleting object or symbol-discovery caches would force substantial recompilation
and defeat the requested incremental workflow. Even repeated per-unit PDB names
belong to separate compiler invocations. Keep the complete current graph.

## Current handoff cleanup: 2026-11-12

The handoff cleanup reclaimed about **703 MiB** of allocated local storage.
Eighty-two historical baseline/trial directories are stored as individual
`.analysis/archives/NAME.tar.gz` files. Large historical root reports are stored
as `.json.gz`. The original 1,000-plus-line handoff is retained as
`.analysis/handoff-next-agent-6427da9.md.gz`; its statements are historical.
The exact file/member list, original and archive SHA-256 hashes, modes, times,
byte counts and protected current artifact hashes are in
`.analysis/cleanup-handoff-20261112.json`.

Every archive was read back and every member checked before its source copy
was removed. Evidence was compressed rather than discarded. Both recent
baselines named in the preservation table remain directly usable. The active
build graph, canonical report, private inputs, shared installations, game-owned
Wine prefix, analyzer project and pinned checkout were not cleaned.

Read or restore indexed evidence with the standard-library helper:

```sh
python3 scripts/evidence-archive.py list audio-scalar
python3 scripts/evidence-archive.py show audio-scalar-baseline/build/reference-candidate/build-receipt.json
python3 scripts/evidence-archive.py restore audio-scalar-baseline
python3 scripts/evidence-archive.py show handoff-next-agent-6427da9.md
```

`show` emits one file without restoring its directory. `restore` verifies the
archive and member hashes, stages the result, and refuses an existing destination.
Use the directory name for a directory archive or the original filename for an
individual gzip report. Older diagnostic helpers use their original literal
paths, so restore the named snapshot before rerunning them. Do not rerun a
historical helper as if its expected counts described the current checkpoint.

The initialization proof draft was withdrawn from `scripts/` and Oracle
configuration before cleanup. A positive focused result under those draft rules
is retained only inside the clearly marked experiment directory; it does not
change the accepted 883/65/267 checkpoint. No compiler run or Oracle acceptance
change was performed as part of cleanup.

## Earlier compressed evidence: 2026-11-08

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

That earlier operation reclaimed about **78 MiB** of allocated local storage. The exact
paths, byte counts, source hashes for archived files and preserved current
artifact hashes are recorded in `.analysis/cleanup-20261108.json`. Current build
artifacts, the active audit and private target were unchanged. The user-supplied
extraction and shared Factory installations were not cleaned.

For later cleanup, inspect sizes first, identify consumers, check for active
jobs, and remove only known reproducible scratch outputs. Compress historical
evidence when practical. Verify `scripts/progress.py` afterwards; no cold build
is needed solely to clean unused outputs or edit documentation.
