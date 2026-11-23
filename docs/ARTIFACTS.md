# Local artifacts and storage

This repository contains a private target, a historical toolchain, analysis
projects, incremental build products and trial evidence. Ignored does not mean
disposable. Preserve unique evidence and the current build graph; clean only
known regenerable caches or files covered by a verified cleanup index.

## Preserve

| Path | Why it stays |
| --- | --- |
| resources/th16.exe, ../game_exe/ | Canonical private target and supplied game files |
| .tools/, .venv/ | Game-owned Wine runtime, shared-tool selectors and locked Python dependencies |
| ghidra-project/ | Imported and analyzed target database |
| build/reference-candidate/ | Current PE/MAP/PDB, receipt, object/dependency graph and incremental caches |
| _reference/johnthreekay-th16/ | Pinned, unchanged upstream source checkout |
| .analysis/reference-audit.json, .analysis/oracle-acceptance-current.json | Local audit inputs/reports; neither is a current Factory acceptance receipt |
| .analysis/claude-tools/ | Diagnostic scripts, probe sources and active audit configuration |
| .analysis/factory-registration.toml, .analysis/factory-validation* | Private Factory registration and validation inputs |
| .analysis/factory-replay-th16/, .analysis/factory-replay-th16-follow-up/ | Isolated pilot worktrees, configurations and receipts |
| .analysis/*-work/ | Source snapshots, native fixtures, full-owner diagnostics and restoration evidence |
| .analysis/archives/ | Verified recovery archives indexed by cleanup-handoff-*.json |

Do not delete a *-work directory or the whole .analysis tree to save space.
Many trial snapshots are unique and explain why a source form was retained or
reverted. The two archived pilot Wine prefixes are distinct files; keep both
until their isolated replay environments are no longer needed.

## Current storage snapshot

Measured on 2026-11-23 after the trial-output cleanup: the repository occupies
about **4.3 GiB**; .analysis/ is about **3.5 GiB**, including about **916 MiB**
of verified archives. The active build is about **107 MiB**, .tools/ about
**586 MiB**, .venv/ about **25 MiB**, ghidra-project/ about **14 MiB**, and
the pinned reference checkout about **17 MiB**. These are approximate
allocated-size readings, not a target for further deletion.

## Current cleanup and restoration

On 2026-11-23, 1,366 unreferenced root-level trial outputs named
20261123-* were compressed individually. The current baseline measurements
and strict reports named 20261123-handoff-* were deliberately left expanded.
The archived files originally occupied **93,619,766 bytes**; gzip archives
occupy **9,950,208 bytes**. The verified operation recovered
**82,632,704 allocated bytes**. The index
.analysis/cleanup-handoff-20261123.json records each original and archive
SHA-256, byte count, mode and nanosecond timestamp. A restore smoke test passed.

List, inspect or restore a historical output with the standard helper:

    scripts/repo-python scripts/evidence-archive.py list 20261123
    scripts/repo-python scripts/evidence-archive.py show 20261123-enemy-step-interpolators-direct-assignment-shared-radial-strict.json
    scripts/repo-python scripts/evidence-archive.py restore 20261123-enemy-step-interpolators-direct-assignment-shared-radial-strict.json

The restored file is written back under .analysis/ and is never overwritten
by the helper. Remove a temporary restored copy after use if it is no longer
needed. Other verified cleanup indexes cover the 2026-11-12 through
2026-11-21 archive operations.

The 2026-11-23 cleanup also removed regenerable Python __pycache__ and
.pyc files from .analysis/, .venv/, scripts/ and the pinned reference
checkout, recovering about **5.18 MB**. No source, target, toolchain,
Ghidra database or build product was removed. The incremental build graph
was preserved.

## Historical storage recoveries

- **2026-11-21:** two isolated Factory pilot Wine prefixes were archived
  independently under .analysis/archives/20261121/pilot-prefixes/.
  Both archives were verified on extraction. Six historical curve/geometry
  fixture directories in boss-stats-work were also archived; see
  .analysis/cleanup-handoff-20261121-boss-stats.json.
- **2026-11-20:** 35 duplicate historical PDBs and 28 duplicate audit reports
  were archived after byte/hash checks and consumer scans, recovering about
  **273.39 MiB** allocated.
- **2026-11-19:** 24 unreferenced duplicate historical audit/PDB files and
  generated caches were archived or removed, recovering about **111 MiB**.
- **2026-11-18:** 13 unreferenced duplicate audit snapshots were archived,
  recovering about **48.3 MiB**.
- **2026-11-17:** 62 retired native Boss/damage/laser fixture and output files
  were archived, recovering about **3.49 GiB** while preserving their indexes
  and regression context.

For earlier archive formats, use the same evidence-archive.py helper. It
reads the dated cleanup-handoff-*.json indexes and refuses to overwrite an
existing restore destination.

## Incremental-work rules

Keep build/reference-candidate/, the current PE/MAP/PDB and object/dependency
cache. Deleting these caches forces substantial recompilation. Keep
.tools/wine/, shared-tool selectors, .venv/ and ghidra-project/; they are
inputs, not temporary outputs.

Safe routine cleanup is limited to regenerated Python bytecode caches and
known empty temporary directories. Before removing any other ignored file,
check whether it is unique, referenced by a script/document, part of a build
receipt, or covered by an existing archive index. Do not remove the canonical
target, a current build artifact, a Ghidra project, a pilot prefix/archive or
a unique trial fixture to make a storage number look better.
