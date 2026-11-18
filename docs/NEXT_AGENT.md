# TH16 reconstruction: current agent handoff

**Updated 2026-11-18.** Read [AGENTS.md](../AGENTS.md) before editing. Work in
natural C/C++; do not use inline assembly, fake padding, or inert code to force
machine-code similarity. Commit coherent improvements as `gpt-web: ...` and do
not push unless the user requests it. This handoff is prepared for the incoming
agent: preserve and inspect the two existing dirty timer files before editing;
do not reset, overwrite or silently discard them.

## Repository checkpoint and validation boundaries

- Latest **game-source** checkpoint before this handoff cleanup:
  `d3aecb675fca4ee69b82bde7d9041b587fbf6216`
  (`gpt-web: avoid caching ECL context owner`, 2026-11-17 21:16 UTC).
  `main` and `origin/main` were synchronized before the documentation work.
  This handoff adds two documentation-only local commits; use `git log` and
  `git status -sb` for the actual post-cleanup HEAD/ahead count. Neither commit
  changes game source.
- The worktree has exactly **two unstaged, uncommitted source changes**:
  `src/ScreenEffect.cpp` and `src/ZunTimer.h`. There are no staged changes,
  untracked files or conflicts. They implement an experimental
  `ZunTimer::tick_goto_volatile(i32 *out_current)` used only by
  `ScreenEffect::on_tick_shake`; see the dedicated section below. Treat this as
  an unproven experiment, not a committed reconstruction improvement.
- An incremental build of that exact dirty worktree succeeded on 2026-11-18:
  **1,166 annotated functions**. This is a build/annotation count, not an
  exactness count. The focused `on_tick_shake` diagnostic is 121 target / 121
  candidate instructions, ratio **0.9917**, with one unmatched `push esi`.
  This normalized diagnostic is not a strict receipt and has not yet been
  compared against a clean-HEAD baseline for this experiment.
- The saved strict-audit/progress image dates to **2026-11-15** and is stale.
  Its **1,033 exact / 51 mismatch / 131 incomplete** and **1,215 annotated
  units** are historical only; do not present them as today's result.
- Factory inspection currently identifies the original Japanese v1.00a target,
  but reports **0 imported Oracle results** and an `inventory-import-only`
  diagnostic. Exactness, provenance acceptance and production closure are
  therefore unknown in the current Factory registry. The last known local
  strict Oracle attempt was blocked in EH-owner preflight by
  **"EH parent lacks one complete candidate PDB owner"**; that historical
  blocker has not been re-certified. A successful build or normalized ratio of
  `1.0` is not an accepted complete-owner/relocation receipt.
- `resources/th16.exe` is the private original Japanese v1.00a target;
  `build/reference-candidate/` is the current incremental PE/MAP/PDB and
  object/symbol cache. Keep both, together with `.tools/`, `.venv/`,
  `ghidra-project/` and the pinned `_reference/` checkout.

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

All ratios below come from local complete-function normalized instruction
comparisons against the current incremental candidate. They are diagnostic
only: they do not prove byte identity, relocation identity or Factory
acceptance.

| Owner / source | Current local measurement and next issue |
| --- | --- |
| `EnemyData::ecl_run_over_300`, target `0x41dcb0`, `src/EnemyEcl.cpp` | 21,408 target / 21,456 candidate bytes; 4,562 / 5,435 normalized instructions; **0.8633**. Hard groups: laser cases 402/403/411/413 score about 0.73–0.77; Bezier 125/126 about 0.89; curve 134/135/138/139 about 0.98. `MOVE_POS_3D` 116/117 is about 0.90 and random movement 112/113 about 1.00. Continue with the four laser creation paths and preserve their distinct origin/copy order. |
| `AnmVm::run`, target `0x45f980`, `src/AnmVmRun.cpp` | 14,177 / 14,208 bytes; 3,837 / 3,843 instructions; **0.9474**. Cases 4 (`FOLLOW_CAMERA`) ~0.98, 124 (`FSET_RAND`) ~0.96, and 132 (random circle) ~0.97. Remaining differences include x87 result lifetime, radial multiplication and load order. |
| `LaserLineInf::run_ex`, target `0x431fe0`, `src/Laser.cpp` | 1,588 / 1,600 bytes; 344 / 342 instructions; **0.9067**. Revisit `BulletEx` cursor and indexed-address scheduling without repeating known volatile cursor regressions. |
| `LaserCurveInf::run_ex`, target `0x438cb0`, `src/Laser.cpp` | 1,548 / 1,552 bytes; 360 / 363 instructions; **0.9654**. The cursor/payload schedule still differs. |
| `EnemyData::step_logic`, target `0x41c330`, `src/Enemy.cpp` | 2,207 / 2,208 bytes; 534 / 530 instructions; **0.9868**. Keep the branchless dialogue-damage selection; staged life/overkill rewrites previously regressed this owner. |
| `Bullet::step_ex_08`, target `0x4162d0`, `src/BulletManager.cpp` | 1,390 / 1,424 bytes; 327 / 336 instructions; **0.8929**. The committed `DirectionCornerScratch` union models the direction/corner stack overlap naturally; continue investigating corner math and register scheduling. |
| `EnemyData::step_interpolators`, target `0x41bb50`, `src/Enemy.cpp` | 1,692 / 1,696 bytes; 421 / 421 instructions; **0.9976**. The camera Y operand order checkpoint is committed. |
| `ScreenEffect::on_tick_shake`, target `0x45cd30`, `src/ScreenEffect.cpp` | 476 / 480 bytes; 121 / 121 instructions; **0.9917** on the dirty experiment, with one unmatched `push esi`. Compare against clean HEAD before deciding whether the new timer helper is worth keeping. |

Focused ECL opcode diagnostics from the current build: cases 402/403/411/413
(line/infinite/curve/beam laser) are 74/76 at 0.75, 80/84 at 0.73, 68/72 at
0.77 and 65/67 at 0.74 respectively. These are inline case spans, not complete
owners. The ECL dispatch map and its complete PDB owner are different scopes;
never infer exactness from dispatch coverage or case ratios.

## Recent natural-source checkpoints

For exact diffs consult `git show COMMIT`, not an old note's guessed source
form. The most relevant recent commits are:

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

## Current dirty timer experiment

`src/ZunTimer.h` adds `tick_goto_volatile(i32 *out_current)`, duplicating the
existing `tick_goto()` control flow but storing `current` through a volatile
pointer before writing the output parameter. `src/ScreenEffect.cpp` calls it
from `on_tick_shake` to try to place the current-frame store before a register
spill. The current incremental build succeeds, but the focused comparison
still has one unmatched `push esi`; no clean-HEAD A/B result or accepted receipt
exists. Before retaining it, compare both versions using a reversible source
swap/build/restore sequence, check timer semantics and other call sites, then
keep or revert deliberately. Do not silently discard the two dirty files.

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
