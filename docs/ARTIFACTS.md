# Local artifacts and storage

Ignored files include required private inputs, incremental caches and evidence.
Do not treat every ignored directory as disposable. Shared tool selectors point
outside this repository; never follow them when cleaning local outputs.

## Preserve for continued work

Historical evidence may be stored in verified archives instead of expanded
directories. The work-directory entries below describe evidence to retain;
they do not require keeping every historical fixture output uncompressed.
Use `scripts/evidence-archive.py list` to resolve archived paths before assuming
that evidence is missing. Never remove an archive because its old path is absent.

| Local path | Reason |
| --- | --- |
| `resources/th16.exe`, `../game_exe/` | Canonical private target and supplied game files |
| `.tools/wine/`, `.tools/shared-runtimes.json`, tool selectors | Game-owned runtime and attached shared installations |
| `.venv/` | Locked comparison dependencies |
| `ghidra-project/` | Imported and analyzed target database |
| `build/reference-candidate/` | Current PE/MAP/PDB, function map, receipt, object/dependency cache and non-LTCG symbol-discovery cache |
| `.analysis/reference-audit.json` | Last saved fingerprinted 2026-11-15 results; stale against the 2026-11-17 candidate; strict audit refresh still needs EH-parent preflight resolution |
| `.analysis/claude-tools/` | Diagnostic scripts and probe sources; historical audit/source/log/binary outputs are compressed, rebuildable probe outputs removed, active exp.json/cur-audit.json/build.log retained |
| `.analysis/projectile-ex-source-work/` | PDB 619 baseline/PDB 624 restoration, reviewed curve/sound/animation trials, explicitly unreviewed duplicated-sound image, all restored sources and complete static handoff regression |
| `.analysis/upper-ecl-case-work/` | PDB 614 baseline/PDB 619 restored image, four complete 21 KB source trials, registered original 4,519-instruction CFG/three tables/map, frame-store proof, initial/final 79-control logs, baseline count check and complete raw-image regression |
| `.analysis/large-owner-operands-work/` | PDB 600 baseline/PDB 614 restored image, twelve complete Boss/motion/menu/curve source trials, original 768-instruction music CFG, full scope/field census, trial images/snapshots and complete raw-image restoration |
| `.analysis/ecl-interpreter-order-work/` | PDB 591 baseline/PDB 600 restored image, eight full ECL source trials and images, original 1,645-instruction CFG, complete tables/map, source-qualified private helper proof, static controls and complete raw-image regression |
| `.analysis/audio-release-baseline/` | Historical audio checkpoint regression inputs, kept uncompressed; not the current baseline |
| `.analysis/audio-initialize-baseline/`, `.analysis/experiments/audio-initialize-unvalidated/` | Unvalidated initialization draft, its clean base and review notes |
| `.analysis/enemy-motion-work/` | Boss, spellcard and projectile source trials, baseline report and final regression evidence |
| `.analysis/bullet-ex-work/` | Curve laser exact comparison, large projectile dispatcher trials, private helper controls and partial instruction-emulation diagnostics |
| `.analysis/boss-core-work/` | Boss damage/feedback and Player damage traversal trials, native layout probe, partial instruction-emulation diagnostics and strict regression evidence |
| `.analysis/boss-flow-work/` | Boss shield/collision source trials, complete logic/damage packets, historical NaN-payload control, native shield/collision fixtures, explicit SEH/no-frame prefix controls, failed combined image and final regression evidence |
| `.analysis/interpolation-exact-work/` | PDB 342 baseline/PDB 356 retained static geometry work; complete original table/CFG evidence, rectangle packets, actual Oracle input fields, unaccepted cursor/GUID alias record and restored interpolation/Player/rotation trials |
| `.analysis/rectangle-exact-work/` | PDB 356 baseline/PDB 362 final artifacts; complete Gui destructor exact graph/CFG, static controls and canonical regression; five restored geometry trials and full owner packets |
| `.analysis/boss-register-work/` | PDB 362 baseline, first exact PDB 373/final PDB 374 spellcard startup; original CFG/stage-index witnesses, discarded class-return evidence, restored Boss/source trials and complete 1,719-owner raw regression |
| `.analysis/bullet-tick-exact-work/` | PDB 391 baseline, PDB 402 first-exact/PDB 403 final easing owner; 388-instruction original CFG, full 31-entry table and 131-field strict proof, restored Bullet/easing trials and complete raw 1,718-owner regression |
| `.analysis/vector-owner-work/` | PDB 403 baseline/PDB 420 retained Float3 timer result; complete 906-byte strict 899/906 mismatch, original CFG, restored interpolation trials and complete raw 1,718-owner regression; no new exact credit |
| `.analysis/boss-damage-exact-work/` | PDB 420 baseline/PDB 430 retained Boss suppression expression; complete original 534-instruction CFG, restored damage/life/owner trials, full 2,197/2,207-byte owner packets and raw 1,718-owner regression; no new exact credit |
| `.analysis/boss-credit-join-work/` | PDB 430 baseline, four restored Boss result-boundary trials, complete logic/motion packets and static build logs; final restoration evidence shared with laser EX work |
| `.analysis/laser-ex-static-work/` | PDB 430 baseline/PDB 443 restoration; complete 1,588/1,748-byte EX owners with both tables, 327-instruction original CFG, 36-operand encoding diagnostic, seven restored source trials and complete 1,719-owner/raw-text regression |
| `.analysis/laser-pointer-lifetime-work/` | PDB 443 baseline, three restored outer-pointer/shared-advance/index-snapshot source trials and complete EX owner/table packets; final restoration checked with enemy VM-return work |
| `.analysis/enemy-vm-return-work/` | PDB 443 baseline/PDB 450 first-complete/PDB 462 retained motion owner; complete 1,682/1,692-byte mismatch with 48 links, original 421-instruction CFG, rejected intrinsic/return/copy forms, isolated mode overload and raw 1,718-owner regression |
| `.analysis/ecl-owner-work/` | PDB 384 baseline/PDB 391 restored image; complete 4,519-instruction upper-ECL original CFG, three dispatch tables/map, failed owner/member-position/motion sources, final failed image and complete raw 1,719-owner restoration proof |
| `.analysis/curve-exact-work/` | Complete 986-byte reverse-step packets, squared-speed register diagnostic, three restored source forms and static build logs; no runtime tests |
| `.analysis/boss-vm-work/` | PDB 374 baseline, first exact PDB 383/final PDB 384 ECL animation dispatcher; complete original CFG/19-entry table, argument/owner/byte-value trials and full 1,719-owner symbolic regression, including preserved failed data-mapping helpers |
| `.analysis/boss-static-work/` | Static Boss/spellcard/collision source trials; PDB 330 baseline/PDB 342 retained images, complete owner packets, restored source forms and unchanged exact-unit regression |
| `.analysis/boss-credit-work/` | Complete 1,348-byte masked draw exact result; PDB 322 baseline/PDB 330 restoration, fixed literal/CFG/table evidence, static mutation controls, restored Boss/menu/vector source trials, rejected forecasts and final strict regression record |
| `.analysis/boss-interrupt-work/` | Boss/ECL restart call-context repair; PDB 316 baseline and PDB 322 final images, complete caller scopes, 927-field upper-dispatch regression, typed ECL frame/argument probe, 408 sub-call and 360 dual-phase native cases per image, live-async prefixes, original-first controls and final regression record |
| `.analysis/bullet-accel-work/` | Projectile dispatcher angle-consumer repairs; PDB 301 baseline and PDB 316 final image, complete data-aware code/table packets, rejected movement/flag forms, 560-call native matrices, typed layout, original-first whole-state model controls and final regression record |
| `.analysis/shot-live-work/` | Successful shot initialization with real pool/ANM state; PDB 296 baseline, PDB 301 restoration, invalid sequential image, complete shot/table scopes, 390-condition native matrix, four controls, typed slot/layout versions and failed source/control prototypes |
| `.analysis/boss-accounting-work/` | Restored Boss/motion/shot trials; PDB 288 baseline, PDB 296 restored image, complete invalid scratch image, all owner/table packets, 978-condition native shot rejection matrix, typed layout and original-first/invalid-image guards |
| `.analysis/ecl-float-work/` | ECL ring precision repair; PDB 277 baseline and PDB 288 final images, complete interpreter/upper-dispatch scopes, 3,288-condition native matrices, RNG/layout models, negative controls, restored source trials and final regression record |
| `.analysis/ecl-predicate-work/` | ECL expression-exit source work; corrected PDB 277 image/full scopes, typed native models and negative controls; rejected NEG_F draft/image and authenticating replay; upper-dispatch relink evidence and corrected regression record |
| `.analysis/boss-restart-work/` | Large ECL shared-result source trials, data-aware complete interpreter spans, Boss dual-phase live async fixtures/prefixes, typed layout, negative controls, final image and strict regression evidence |
| `.analysis/curve-layout-work/` | Curve elapsed/integration source trials, complete motion owners, typed layout probe, starting/final images, expanded native matrix, independent-model negative control and strict regression evidence |
| `.analysis/boss-stats-work/` | Restored Boss statistics trials; curve state/vector source work, complete owner packets, typed layout probe, three-image native matrices, historical control, final tested image and regression evidence |
| `.analysis/boss-lifetimes-work/` | Planar damage/frame-context trials, final complete owners, initialized native Boss phase fixtures and independent models, no-op control, typed layout evidence, prior-suite replay and strict regression evidence |
| `.analysis/boss-damage-work/` | Damage traversal/impact source trials, complete owner packets, typed snapshot fixtures and historical control, initialized-CRT geometry/Boss execution, protocol controls, invalid ABI/startup notes and final regression evidence |
| `.analysis/laser-core-work/` | Laser/context source trials, large ECL context, native debugger and complete fixtures, parameter observation controls, failed prototypes and restored-build regression evidence |
| `.analysis/ecl-dispatch-work/` | Large ECL shared-position and spell-name source trials, complete diagnostic code/table/map packets, native movement and spell-prefix fixtures, final tested image, scope refusals and regression evidence |
| `.analysis/ecl-context-work/` | ECL coordinate evaluation and animation operand trials, typed lookup fixtures, native animation snapshots and historical-image control, invalid-opcode notes and final source regression evidence |
| `.analysis/ecl-angle-work/` | ECL angle/orbit initialization trials, complete code/table/map packets, native full-state angle/orbit fixtures, pre-rebuild receipt refusal, final tested image and source regression evidence |
| `.analysis/archives/`, `.analysis/cleanup-handoff-*.json` | Verified historical evidence and dated recovery indexes |
| `.analysis/factory-registration.toml`, `.analysis/factory-validation*` | Staged private registration and isolated validation evidence |
| `.analysis/ghidra/`, diagnostic notes and regression records | Analysis evidence and failed-experiment context |
| `_reference/johnthreekay-th16/` | Pinned, unchanged upstream checkout |

Deleting object or symbol-discovery caches would force substantial recompilation
and defeat the requested incremental workflow. Even repeated per-unit PDB names
belong to separate compiler invocations. Keep the complete current graph.

## Current handoff cleanup: 2026-11-17

Archived **62 retired, top-level native Boss, damage and laser fixture, output
and expected-result files** from the five historical `.analysis/` directories:
`boss-flow-work`, `boss-stats-work`, `boss-lifetimes-work`,
`boss-damage-work` and `laser-core-work`. They were not part of the active
build graph. Their original **3,770,298,368 allocated bytes** are represented
by **22,265,856 allocated archive bytes**, reclaiming **3,748,032,512 bytes
(approximately 3.49 GiB)**. The five directories retain their source trials,
runner scripts, smaller logs, reviews and other historical evidence. This is
archival, not deletion of unique evidence.

Each original was independently hashed, compressed to
`.analysis/archives/20261117/WORK/FILENAME.gz`, decompressed, then checked
against its original **SHA-256 and byte count** before removal. Five ignored
`.analysis/cleanup-handoff-20261117-WORK.json` indexes retain every original
path, compressed path, hashes, mode, timestamp and allocated size. The index
was written atomically **before** deleting its verified originals. A test
restored a historical 23 MB output file, checked its hash, size, mode and
nanosecond modification time, then discarded only that temporary restoration.

The historical `check-native-protocol.py` scripts may require specific expanded
files first. Restore just the evidence you need, not all five directories:

```sh
scripts/repo-python scripts/evidence-archive.py list boss-flow-work/native-boss
scripts/repo-python scripts/evidence-archive.py restore boss-flow-work/native-boss-target-fixtures.bin
# After investigation, avoid leaving unnecessary expanded historical copies.
```

The archive helper now reads all three index styles: older directory tarballs,
the 2026-11-16 individual-gzip cleanup and these 2026-11-17 per-file gzip
indexes. It refuses to overwrite an already existing restore destination.
No original target, current executable/PDB/MAP, build object cache, Ghidra
project, shared tools or pinned source checkout was removed. No cold build,
full replay or new strict audit was run for the documentation and archival work.

## Previous handoff cleanup: 2026-11-16

This cleanup reclaimed **189,392,627 logical bytes** (about **180.6 MiB**) in
.analysis/claude-tools. It compressed 449 historical files: 31 retired strict
audit snapshots, 118 source snapshots/backups, 291 trial logs, and seven
diagnostic/title artifacts plus two additional backup files. Their combined
original size was **198,084,430 bytes**; the compressed copies occupy
**18,766,121 bytes**. Every compressed file was decompressed and checked
against its original SHA-256 and size before the source was removed.

The old exp.json and cur-audit.json snapshots remain uncompressed because
diagnostic helpers read them directly; they are historical and are not current
audit results. build.log also remains uncompressed because existing scripts use
it as a build-success sentinel. The canonical
.analysis/reference-audit.json remains in place but is stale for the current
candidate. The extracted dat/title.anm, old before.exe/map, callgraph
cg.exe/pdb/map/dgml and historical source backups are retained as individual
.gz files. Restore any one with gzip -dc COMPRESSED_PATH > ORIGINAL_PATH;
the cleanup index records original hashes, modes and nanosecond timestamps.

Rebuildable probe outputs were removed: 375 of the original 377 p/ object,
executable and map outputs (two outputs without a matching retained source
were kept), all four fp/ outputs, and two top-level vectorcall probe objects.
Their source probes and generators remain. Twenty-three zero-byte abandoned
scratch outputs were removed. The p/mbi.exe and p/mbi.map outputs were kept
because no matching C++ source was present. The cleanup index is
.analysis/cleanup-handoff-20261116.json.

The incremental build graph, original target, title-screen image, Ghidra
project, Wine/toolchain installation, pinned reference checkout and the large
historical .analysis work directories were not removed. No cold build, full
replay, Oracle or Factory acceptance operation was run as part of artifact
cleanup. A subsequent incremental build refreshed the candidate after the
comment-only source documentation correction.

## Earlier handoff cleanup: 2026-11-13

This cleanup reclaimed **42.27 GiB** of allocated storage. `.analysis/` fell
from **49.04 GiB to 6.77 GiB** at the cleanup checkpoint. Eighty-nine retired
fixture/output subdirectories, previously about 42.58 GiB, are now individual
archives under `.analysis/archives/20261113/WORK/LEAF.tar.gz`. Their parent
scripts, source snapshots, reports and recent baseline/final image sets remain
uncompressed. No historical game fixture was executed for cleanup.

The former 1,418-line handoff is preserved byte for byte as
`.analysis/handoff-next-agent-fe98fb8.md.gz`. Its old counts, baseline labels
and workflow suggestions are superseded by the current handoff. The complete
90-record index is `.analysis/cleanup-handoff-20261113.json`; it records file
and archive SHA-256 hashes, modes, nanosecond timestamps, directory metadata,
allocated/apparent sizes and protected current artifact hashes.

Every archive was fully read back, every file checked, and the source copies
rechecked before removal. All archive checksums were checked again afterwards.
An actual nested fixture restore verified content, modes and timestamps; that
temporary expanded copy was then removed. Legacy archive reading also passed.
The helper loads both completed dated indexes and supports nested paths:

```sh
scripts/repo-python scripts/evidence-archive.py list ecl-float-work
scripts/repo-python scripts/evidence-archive.py show handoff-next-agent-fe98fb8.md
scripts/repo-python scripts/evidence-archive.py restore ecl-float-work/native-baseline
```

The private target, current audit, unit ledger and every file in the incremental
build graph retain their pre-cleanup hashes. Wine/tool selectors, dependencies,
analyzer project and pinned reference were not cleaned. The preceding source
trial restoration finished first: PDB 624 preserves **904 exact / 67 mismatch /
244 incomplete**, all 971 units and all 1,719 raw native owners (the
restoration report is in Git history).
No cold build or Oracle rule change was performed for cleanup.

## Earlier handoff cleanup: 2026-11-12

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
scripts/repo-python scripts/evidence-archive.py list audio-scalar
scripts/repo-python scripts/evidence-archive.py show audio-scalar-baseline/build/reference-candidate/build-receipt.json
scripts/repo-python scripts/evidence-archive.py restore audio-scalar-baseline
scripts/repo-python scripts/evidence-archive.py show handoff-next-agent-6427da9.md
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
change that historical 883/65/267 checkpoint. No compiler run or Oracle acceptance
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
`scripts/repo-python scripts/verify-toolchain.py --execute` recreates smoke outputs.
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
