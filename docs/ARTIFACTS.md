# Local artifacts and storage

Updated 2026-11-26. Keep the current reconstruction inputs and incremental
build. The user explicitly authorized permanent deletion of old large evidence
without retaining archives; the deleted set supersedes earlier retention and
recovery instructions in historical handoffs.

## Preserved working state

| Path | Purpose |
| --- | --- |
| `resources/th16.exe`, `../game_exe/` | Canonical private target and supplied game files |
| `.tools/`, `.venv/` | Game-owned Wine runtime, shared-tool selectors and Python dependencies |
| `ghidra-project/` | Imported and analyzed target database |
| `build/reference-candidate/` | Current PE/MAP/PDB, receipt and incremental object/dependency graph |
| `_reference/johnthreekay-th16/` | Pinned original reference checkout |
| `.analysis/line-run-ex-compiler/` | Active compiler traces, scripts, source snapshots and focused checks |
| Other `.analysis/*-compiler/` directories | Compiler evidence for the closed enemy and curve owners |
| `.analysis/claude-tools/`, Factory registration/validation files | Diagnostic scripts and private service inputs |
| Historical source snapshots, small notes and receipts | Context for retained and reverted changes |

The current game Wine prefix remains at `.tools/wine/`. Removing old archived
pilot prefixes did not remove that runtime. Local audit reports and historical
pilot receipts do not establish current shared Factory acceptance.

## Permanent cleanup on 2026-11-26

The cleanup removed retired large native fixtures, expected/output files,
historical audit reports, PDBs and trial binaries, plus their compressed copies
and old pilot-prefix archives. The active compiler directories and current
build graph were excluded. The deletion record is
`.analysis/cleanup-deleted-20261126.json`.

The deleted payloads reclaimed **2,620,059,648 allocated bytes (2.44 GiB)**;
temporary cleanup inventories and Python bytecode caches freed about another
8 MB. The repository fell from about **5.2 GiB to 2.8 GiB**, and `.analysis/`
from about **4.3 GiB to 1.9 GiB**. Remaining archives occupy about **14 MiB**.
The active build is about 108 MiB, `.tools/` 586 MiB, `.venv/` 26 MiB,
Ghidra project 14 MiB and pinned reference checkout 17 MiB.

Deleted evidence is not recoverable through the archive helper. Older notes
may still cite its historical paths; those citations record the experiment,
not present file availability. Recovery records for removed payloads were
pruned from the ignored `cleanup-handoff-*.json` indexes. The temporary archive
set created earlier in this cleanup was also deleted, with no retained backup.

## Remaining archives

Small historical payloads remain in `.analysis/archives/`, indexed by the
remaining `cleanup-handoff-*.json` records. List what is actually available:

```sh
scripts/repo-python scripts/evidence-archive.py list
scripts/repo-python scripts/evidence-archive.py show 20261123-enemy-step-interpolators-direct-assignment-shared-radial-strict.json
scripts/repo-python scripts/evidence-archive.py restore 20261123-enemy-step-interpolators-direct-assignment-shared-radial-strict.json
```

The helper verifies checksums and refuses to overwrite an existing destination.
Remove a temporary restored copy after use when it is no longer needed.

## Further cleanup

Regenerated Python bytecode caches and known temporary outputs can be removed.
Check references and build dependencies before deleting other files. Preserve
source snapshots and concise findings that explain the current reconstruction.
Do not delete the entire `.analysis/` tree, current build graph, toolchain,
canonical target or analyzer project as part of artifact cleanup.
