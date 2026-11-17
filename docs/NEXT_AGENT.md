# TH16 reconstruction: current agent handoff

**Updated 2026-11-17.** Read [AGENTS.md](../AGENTS.md) before editing. Work in
natural C/C++; do not use inline assembly, fake padding, or inert code to force
machine-code similarity. Commit coherent improvements as `gpt-web: ...` and do
not push unless the user requests it. Continue the existing dirty work if any;
there is no other active editing agent to defer it to.

## Repository checkpoint and validation boundaries

- Latest **game-source reconstruction** checkpoint before handoff maintenance:
  `298a435` (`gpt-web: align paired ECL animation and hit-sound context reloads`).
  `main` and `origin/main` were synchronized when this cleanup started. The
  subsequent documentation/archival-tool commits are separate; use `git log`
  and `git status -sb` for the actual HEAD rather than a frozen ahead-count.
- The current incremental candidate has **1,166 annotated functions**. This
  is a build/annotation count, **not** the population of the older strict
  audit and **not** a count of exact matches.
- The saved strict-audit/progress image dates to **2026-11-15** and is stale
  for the current source. Its reported **1,033 exact / 51 mismatch / 131
  incomplete** and **1,215 annotated units** belong only to that historical
  snapshot. Do not present those totals as today's result.
- The last known focused strict Oracle attempt was blocked in EH-owner
  preflight with **"EH parent lacks one complete candidate PDB owner"**.
  This blocker was not resolved or re-certified during the recent local
  reconstruction sessions. A successful build or normalized ratio of `1.0`
  is **not** an accepted strict complete-owner/relocation receipt.
- `resources/th16.exe` is the private original Japanese v1.00a target;
  `build/reference-candidate/` is the **current incremental** PE/MAP/PDB
  and object/symbol cache. Keep both, together with `.tools/`, `.venv/`,
  `ghidra-project/` and the pinned `_reference/` checkout.

## Immediate working commands

```sh
# Incremental rebuild only; do not run the full cold replay by default.
scripts/repo-python scripts/build.py

# Complete function comparison, register/address normalization: investigation only.
scripts/repo-python .analysis/measure-leaf.py 0x435050 initialize@LaserInfiniteInf
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

| Owner / source | Local finding and specific next issue |
| --- | --- |
| `EnemyData::ecl_run_over_300`, target `0x41dcb0`, `src/EnemyEcl.cpp` | **174/174 dispatch targets**. Roughly 21 KB owner. `MOVE_BEZIER` cases 125/126: 86 target vs 88 candidate instructions, ~0.91; `MOVE_CURVE` cases 134/135/138/139: 80/79, ~0.99. Laser creation cases 402/403/411/413 remain ~0.71–0.75; preserve their distinct origin-before-copy vs copy-before-origin logic. |
| `AnmVm::run`, target `0x45f980`, `src/AnmVmRun.cpp` | **134/134 dispatch targets**. `FOLLOW_CAMERA` case 4 ~0.98, `FSET_RAND` case 124 ~0.96, random circle case 132 ~0.97. Remaining mismatches include x87 result lifetime, radial multiplication and source/load order. |
| `LaserLineInf::run_ex`, target `0x431fe0`, `src/Laser.cpp` | Complete owner locally ~0.817 (344 target/candidate normalized instructions). `BulletEx` cursor and indexed-address scheduling remain different; changing to volatile cursor/payload regressed badly. |
| `LaserCurveInf::run_ex`, target `0x438cb0`, `src/Laser.cpp` | Complete owner locally ~0.860 (360 target / 363 candidate normalized instructions). Same cursor/payload scheduling problem. |
| `EnemyData::step_logic`, target `0x41c330`, `src/Enemy.cpp` | 534 target / 530 candidate instructions, ~0.987. Current branchless dialogue-damage selection is an improvement; avoid earlier staged life/overkill changes that regressed it. |

The ECL owner's **dispatch map** and its **complete PDB owner** are different
verification scopes: do not infer exactness from the dispatch coverage or the
case ratios. Keep existing natural C++ branches, object layouts and typed
calls; a local improvement that causes other cases to regress should be
rechecked before committing.

## Recent natural-source checkpoints

The latest code work spans multiple sessions. For exact diffs consult
`git show COMMIT`, not an old note's guessed source form.

- `298a435`: coordinated live-context loads for `ANM_SELECT` and `HIT_SOUND`;
  both short diagnostic blocks align when changed **together**, while editing
  only one had disrupted other case allocation.
- `a2c2cec`: spell-practice `SET_NEXT` reloads the live enemy before
  registering BossEscape timeout; case 214 has no normalized difference.
- `fbb42e5` after `aab16cb`: restored center-X and random-radius sampling
  order in `EnemyDrop::eject_extra_drops`; complete local 138/138, 1.0.
- `275d101`: live X/Y position updates in
  `LaserInfiniteInf::initialize`; complete local 144/144, 1.0.
- `195c942`, `e86f0b4`, `4fbdb15`: live context access for ECL `Z_INDEX`,
  `SCORE_ADD`, `DIFF_WAIT`; each corresponding local block aligns.
- `829f609`: Boss interrupt subroutine is reloaded after context reset;
  the case 502 result improved to ~0.99.
- `1b86ce2`, `8186f6f`: Bezier duration/VM slot lifetime work; still not
  complete for the large ECL owner.

Useful already-aligned **local normalized** leaves: the four laser
`initialize` variants (line 226/226, infinite 144/144, beam 145/145,
curve 403/403), `Player::check_hit_rect` (76/76),
`Player::check_hit_circle` (69/69), `InterpFloat3::step` (230/230),
`EnemyDrop::eject_extra_drops` (138/138), both laser
`step_ex_angle` functions (84/84), `sht_on_hit_burst_rising` (92/92)
and the four `AnmManager` VM-list insertion functions (47/47 each).
These numbers are **not** strict Oracle exactness credits.

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
about **3.49 GiB** without removing the current build graph or scripts.
The tests that used the expanded historical captures need their named files
restored first. `scripts/evidence-archive.py` now handles both the legacy
archive records and the 2026-11-16 per-file gzip index. See
[artifact retention and recovery](ARTIFACTS.md); do not delete private
inputs, build caches, archived evidence or Ghidra data as generic scratch.
