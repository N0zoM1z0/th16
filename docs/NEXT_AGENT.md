# TH16 reconstruction: current agent handoff

**Updated 2026-11-19.** Read [AGENTS.md](../AGENTS.md) before editing. Work in
natural C/C++; do not use inline assembly, fake padding, or inert code to force
machine-code similarity. Commit coherent improvements as `gpt-web: ...` and do
not push unless the user requests it. Always inspect the live worktree and
preserve any dirty changes before editing; an older handoff's dirty-file list
must not override `git status`.

## Repository checkpoint and validation boundaries

- Latest locally built game-source checkpoint: `35b2062`
  (`gpt-web: type ANM script opcodes as signed 16-bit records`). Five subsequent
  source commits on 2026-11-19 corrected EX tag cursor dataflow in both laser
  interpreters and recovered typed binary opcodes in the ECL, bullet-transform
  and ANM records. The earlier signed sound-ID, typed ECL stack/call argument
  and laser-timing phase checkpoints remain in history. Use `git log` and
  `git status -sb` for the live HEAD and upstream relation.
- The worktree was clean after the 2026-11-19 incremental build and focused
  comparisons. The 2026-11-18 `ScreenEffect.cpp` / `ZunTimer.h` experiment is
  **not currently a dirty change**; its old evidence is historical.
- The incremental MSVC/LTCG build succeeded on 2026-11-19 with **1,166 annotated
  functions**. This is a build/annotation count, not an accepted exact count.
  Focused normalized complete-function diagnostics: `EclRunContext::ecl_run`
  1,807 target / 1,641 candidate instructions, ratio **0.9171**;
  `EclRunContext::call_sub` 177 / 173, ratio **0.9086**;
  `LaserLineInf::run_ex` 344 / 343, ratio **0.9141**. The currently built
  `LaserCurveInf::run_ex` is 360 / 363 instructions, ratio **0.9737**.
  These figures can include
  non-code bytes in the disassembler's linear window and are **not** strict
  complete-owner receipts.
- The saved strict-audit/progress image dates to **2026-11-15** and is stale.
  Its **1,033 exact / 51 mismatch / 131 incomplete** and **1,215 annotated
  units** are historical only; do not present them as today's result.
- The last Factory inspection reported **0 imported Oracle results** and an
  `inventory-import-only` diagnostic. Exactness, provenance acceptance and
  production closure are unknown in the current Factory registry. The last
  known local strict Oracle attempt was blocked in EH-owner preflight by
  **"EH parent lacks one complete candidate PDB owner"**; this blocker has not
  been re-certified. A successful build or normalized ratio of `1.0` is not
  an accepted complete-owner/relocation receipt.
- `resources/th16.exe` is the private original Japanese v1.00a target;
  `build/reference-candidate/` is the incremental PE/MAP/PDB and object/symbol
  cache. Keep both, together with `.tools/`, `.venv/`, `ghidra-project/` and
  the pinned `_reference/` checkout.

## Immediate working commands

```sh
# Incremental rebuild only; do not run the full cold replay by default.
scripts/repo-python scripts/build.py

# Complete function comparison, register/address normalization: investigation only.
scripts/repo-python .analysis/measure-leaf.py 0x41dcb0 ecl_run_over_300@EnemyData
scripts/repo-python .analysis/measure-leaf.py 0x4162d0 step_ex_08@Bullet
scripts/repo-python .analysis/measure-leaf.py 0x45cd30 on_tick_shake@ScreenEffect
scripts/repo-python .analysis/measure-leaf.py 0x41c330 step_logic@EnemyData

# Locally scoped opcode-group differences in the two large interpreters.
scripts/repo-python .analysis/claude-tools/cases.py 0x41dcb0 125,126,134,135,138,139
scripts/repo-python .analysis/claude-tools/cases.py 0x45f980 4,124,132

# Find, read or restore archived private historical evidence on demand.
scripts/repo-python scripts/evidence-archive.py list boss-flow-work/native-boss
scripts/repo-python scripts/evidence-archive.py show claude-tools/AMV.orig.cpp
scripts/repo-python scripts/evidence-archive.py restore boss-flow-work/native-boss-target-output.bin
```

The ECL case extractor indexes cases by **opcode minus 300** (opcode 425
`MOVE_BEZIER` is case `125`). For ANM it indexes by **opcode plus 1**
(`ANM_OP_CIRCLE_POS_RAND`, opcode 131, is case `132`). These are diagnostic
code blocks, not full-owner strict comparisons. `cases.py` omits groups with
no normalized differences; this is useful but does not prove byte exactness.

## Large owners: current frontier

The table mixes the last saved 2026-11-18 complete-function normalized
measurements with refreshed 2026-11-19 owner comparisons where noted. They
are diagnostic only: they do not prove byte identity, relocation identity or
Factory acceptance.

| Owner / source | Current local measurement and next issue |
| --- | --- |
| `EnemyData::ecl_run_over_300`, target `0x41dcb0`, `src/EnemyEcl.cpp` | 21,408 target / 21,456 candidate bytes; 4,562 / 5,435 normalized instructions; **0.8633**. Hard groups: laser cases 402/403/411/413 score about 0.73–0.77; Bezier 125/126 about 0.89; curve 134/135/138/139 about 0.98. `MOVE_POS_3D` 116/117 is about 0.90 and random movement 112/113 about 1.00. Continue with the four laser creation paths and preserve their distinct origin/copy order. |
| `AnmVm::run`, target `0x45f980`, `src/AnmVmRun.cpp` | 14,177 / 14,208 bytes; 3,837 / 3,843 instructions; **0.9474**. Cases 4 (`FOLLOW_CAMERA`) ~0.98, 124 (`FSET_RAND`) ~0.96, and 132 (random circle) ~0.97. Remaining differences include x87 result lifetime, radial multiplication and load order. |
| `LaserLineInf::run_ex`, target `0x431fe0`, `src/Laser.cpp` | **Latest incremental build:** 1,588 / 1,600 bytes; 344 / 343 instructions; **0.9141**. Commit `01bc889` restored the target's TAG cursor-from-index assignment; other live-index sound checks and direct/register `BulletEx` cursor trials regressed. |
| `LaserCurveInf::run_ex`, target `0x438cb0`, `src/Laser.cpp` | **Latest incremental build:** 1,548 / 1,568 bytes; 360 / 363 instructions; **0.9737**. Commit `ae81387` restored the target's TAG index update while keeping the loop's transform pointer; other cursor variants regressed. |
| `EnemyData::step_logic`, target `0x41c330`, `src/Enemy.cpp` | 2,207 / 2,208 bytes; 534 / 530 instructions; **0.9868**. Keep the branchless dialogue-damage selection; staged life/overkill rewrites previously regressed this owner. |
| `Bullet::step_ex_08`, target `0x4162d0`, `src/BulletManager.cpp` | 1,390 / 1,424 bytes; 327 / 336 instructions; **0.8929**. The committed `DirectionCornerScratch` union models the direction/corner stack overlap naturally; continue investigating corner math and register scheduling. |
| `EnemyData::step_interpolators`, target `0x41bb50`, `src/Enemy.cpp` | 1,692 / 1,696 bytes; 421 / 421 instructions; **0.9976**. The camera Y operand order checkpoint is committed. |
| `ScreenEffect::on_tick_shake`, target `0x45cd30`, `src/ScreenEffect.cpp` | **Latest incremental build:** 476 / 480 bytes; 121 / 121 instructions; **0.9917**, with one `push esi` occurring before rather than after the timer's current-frame store. Changing `tick_goto` to return the current frame did not fix it, so that trial was restored. |

Focused ECL opcode diagnostics from the 2026-11-19 incremental build:
cases 402/403/411/413 (line/infinite/curve/beam laser) are respectively
74/75 at 0.77, 80/83 at 0.75, 68/71 at 0.79 and 65/66 at 0.75. These are inline case spans, not complete
owners. The ECL dispatch map and its complete PDB owner are different scopes;
never infer exactness from dispatch coverage or case ratios.

## Recent natural-source checkpoints

For exact diffs consult `git show COMMIT`, not an old note's guessed source
form. The most relevant recent commits are:

- `35b2062`: recover signed 16-bit `AnmRawInstr::opcode` and verify its
  layout; the full `AnmVm::run` diagnostic remains 3,837 / 3,843 at 0.9474.
- `c09349d`: restore `BulletEx::type` as a signed 32-bit bitmask opcode with
  explicit record offsets; the bullet and laser EX owners still compile.
- `8332037`: type the 16-bit ECL opcode and assert its argument offset; the
  large ECL dispatch and argument getter diagnostics remain unchanged.
- `01bc889` and `ae81387`: use the loop-entry index to advance TAG operations
  in line and curve laser EX interpreters respectively. Focused complete-owner
  normalized comparison improved in both cases before saving.
- `ee73604`: replace numbered ECL laser timing slots with the named original
  phases while retaining the shooter's binary layout; the first field also
  serves beam timing and curve segment count.
- `c06eef1`: distinguish `'f'`/`'g'` call argument tags from expression-stack
  value tags, with explicit call argument size and value-offset checks.
- `20c7ac0` and `6f9470a`: carry typed integer/float expression tags through
  ECL argument getters, setters, pushes and pops, with stack record layout
  checks and the same large `ecl_run` diagnostic as before.
- `33070ba`: restore signed shot and transform-sound IDs; `-1` disables sound.

- `d3aecb6`: avoid caching the ECL context owner in the large dispatcher.
- `7e443aa`: preserve camera-delta Y operand order in
  `EnemyData::step_interpolators`.
- `2d1d02e`: recover the overlapping direction/corner scratch layout in
  `Bullet::step_ex_08` using a natural C++ union/struct representation.
- `5fdbbc2`, `7392f7f`: `MOVE_POS_3D` XY/Z operand-order experiments; inspect the
  current source and focused case result before extending them.
- `72f29c3`: restore the ECL random-movement boundary branch layout.
- `298a435` and earlier: coordinated live-context loads for `ANM_SELECT` and
  `HIT_SOUND`; case 214 `SET_NEXT`; Boss interrupt context reload; and earlier
  ECL/ANM ownership work. These remain useful historical checkpoints.

Useful already-aligned **local normalized** leaves from earlier sessions:
the four laser `initialize` variants, `Player::check_hit_rect`,
`Player::check_hit_circle`, `InterpFloat3::step`,
`EnemyDrop::eject_extra_drops`, both laser `step_ex_angle` functions,
`sht_on_hit_burst_rising`, and four `AnmManager` VM-list insertion functions.
Re-measure before relying on any old ratio; none of these figures is a Factory
exactness credit.

## Retained 2026-11-19 trial findings

The previously noted `ZunTimer::tick_goto_volatile` screen-shake experiment is
historical: it is not in the current worktree. Its old 121/121, 0.9917
normalized diagnostic is not a strict receipt.

The following natural-source trials were compiled and compared, then restored
because their affected complete-owner or ECL-case diagnostics regressed:
separate direction and corner locals in `Bullet::step_ex_08`; direct or
`register` transform pointers and live-index sound checks in
`LaserLineInf::run_ex`; shared-origin or direct transform pointers in the ECL
laser/ET_EX cases; altered ANM random-float or camera-offset evaluation;
explicit `EnemyLife` pointers and damage temporaries in
`EnemyData::step_logic`. Evidence from the trials is retained under ignored
`.analysis/th16-*-20261119*` and `.analysis/th16-*-build.log` files. The
recorded positive changes include the five subsequent source commits listed
above; do not mistake a trial's normalized ratio for strict exactness or
reconstructive progress.
Additional 2026-11-19 focused trials after `ee73604`: nonvolatile ECL shooter
references, splitting laser origin vector stores, and factoring ANM random
multiplication through `Rng::randf_0_to` or a precomputed result regressed the
selected opcode spans. Separating the bullet direction/corner scratch, early
collision half-height computation, explicit `AnmVm::world_pos` vector addition,
and alternative curve/line EX index or BLEND update forms also did not improve
comparisons. A `tick_goto` return-value variant was codegen-neutral in the
screen-shake leaf. Each failed trial was restored rather than committed. Local
trial records are retained under `.analysis/th16-session2-*` (ignored).


## Suggested next experiments

1. Attack a **large owner** every session: either the four ECL laser
   constructors, the ECL Bezier selection/writeback sequence, ANM's remaining
   random-float handlers, or the two complete laser EX interpreters. Use
   only affected case/owner comparisons and check nearby shared blocks.
2. In parallel investigate leaves with real dataflow differences, not just
   stack-prologue differences: `AnmVm::world_pos`,
   `LaserCurveInf::check_graze_or_kill`, `ScreenEffect::on_tick_shake`,
   `AnmManager::draw_circle`, and the ECL argument helpers. Many easy rewrites
   already proved neutral or regressive; compare before retaining them.
3. Resolve the strict EH-parent PDB provenance issue **without weakening
   the preflight**, before claiming new strict-exact totals. No strict replay
   or cold build is needed merely to edit prose or restore archived evidence.

## Preserved history and storage

The preceding long, chronological handoff was stale as a **current** status
report. It remains available in Git as
`git show 298a435:docs/NEXT_AGENT.md`; its detailed old experiments,
commit descriptions and failed alternatives are historical evidence, not
current acceptance. Additional source-qualified notes are under
[knowledge](knowledge/README.md).

The 2026-11-17 storage cleanup compressed 62 old native Boss/damage/laser
fixture/expected/output captures (five historical analysis directories) into
verified, indexed `.analysis/archives/20261117/` gzip files, reclaiming
about **3.49 GiB** without removing the current build graph or scripts. The
2026-11-18 cleanup also archived 13 unreferenced, byte-identical historical
audit-report duplicates; see `cleanup-handoff-20261118.json` and the recovery
instructions in [artifact retention](ARTIFACTS.md).
The tests that used the expanded historical captures need their named files
restored first. `scripts/evidence-archive.py` now handles both the legacy
archive records and the 2026-11-16 per-file gzip index. See
[artifact retention and recovery](ARTIFACTS.md); do not delete private
inputs, build caches, archived evidence or Ghidra data as generic scratch.
