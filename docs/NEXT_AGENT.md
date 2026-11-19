# TH16 reconstruction: current agent handoff

**Updated 2026-11-19.** Read [AGENTS.md](../AGENTS.md) before editing. Work in
natural C/C++; do not use inline assembly, fake padding, or inert code to force
machine-code similarity. Commit coherent improvements as `gpt-web: ...` and do
not push unless the user requests it. Always inspect the live worktree and
preserve any dirty changes before editing; an older handoff's dirty-file list
must not override `git status`.

## Repository checkpoint and validation boundaries

- Latest locally built source checkpoint: a8ec90d
  (gpt-web: restore float frame decrement for bullet offscreen timer). Six
  later commits on 2026-11-19 recovered typed ECL expression-stack addressing,
  carried ReplayManagerMode into GameThread, typed bullet cancellation
  script selectors, and reconstructed Bullet::step_ex_08 / Bullet::step_ex_17
  source ordering and scratch storage. All source changes retain native field
  widths and public function ABI. Consult Git history and focused owner
  comparisons; do not treat normalized ratios as strict Oracle results.
- The worktree was clean after the 2026-11-19 incremental build and focused
  comparisons. The 2026-11-18 `ScreenEffect.cpp` / `ZunTimer.h` experiment is
  **not currently a dirty change**; its old evidence is historical.
- The latest incremental MSVC/LTCG build succeeded on 2026-11-19 with
  **1,166 annotated functions**. This is a build/annotation count, not an
  accepted exact count. Focused normalized diagnostics from that build:
  EclRunContext::ecl_run 1,807 target / 1,776 candidate instructions,
  ratio **0.9205**; Bullet::step_ex_08 327 / 336, ratio **0.8929**;
  Bullet::step_ex_17 130 / 130, ratio **0.9769**. The bullet offscreen
  function is intentionally kept as a natural C++ scratch union: separate
  vector locals were tested but gave a lower **0.682** ratio due to stack-slot
  placement. AnmVm::run last measured 3,837 / 3,827, ratio **0.9504**;
  GuiMsgVm::run last measured 1,211 / 1,153, ratio **0.9590**. These are
  local normalized comparisons, not strict complete-owner receipts.
- Recent focused trials that were not kept: writing STACK_SIN directly to
  the ECL stack reduced the complete ecl_run ratio to **0.9005**, so the
  shared push_float path was restored. The direct typed-entry stack-sin
  variant was also rejected. The GameThread::replay_mode type restoration
  remains in c064a92; its PauseMenu::tick_open local ratio measured
  **0.9705** versus **0.9735** before the change, while GameThread creation,
  tick and transition leaves remained 1.0. Revisit only with a concrete
  source-level explanation, not register-allocation forcing.
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
| EnemyData::ecl_run_over_300 (0x41dcb0), src/EnemyEcl.cpp | Before d96eead: 4,562 / 4,616 linear instructions, 0.9022. After the EnemyLife field-type change, a linear window reported 4,562 / 5,449, 0.8277; its jump-table/data extent is not a reliable code boundary. Focused laser opcodes 402/403/411/413 remain 0.78/0.75/0.79/0.75, and bosses-interrupt case 502 remains 0.99. Investigate the case bodies and complete owner extent, not the raw linear ratio. |
| AnmVm::run (0x45f980), src/AnmVmRun.cpp | After 82b1cfa: 14,177 / 14,160 bytes; 3,837 / 3,817 linear instructions, 0.9485 (previously 0.9474). In FSET_RAND, the candidate case-124 span shrank from 24 to 13 instructions, normalized ratio 0.70, while the full owner improved slightly; check whether the destination write was merged into a shared path. Follow-camera case 4 and circle-random case 132 still need register-order work. |
| `LaserLineInf::run_ex`, target `0x431fe0`, `src/Laser.cpp` | **Latest incremental build:** 1,588 / 1,600 bytes; 344 / 343 instructions; **0.9141**. Commit `01bc889` restored the target's TAG cursor-from-index assignment; other live-index sound checks and direct/register `BulletEx` cursor trials regressed. |
| `LaserCurveInf::run_ex`, target `0x438cb0`, `src/Laser.cpp` | **Latest incremental build:** 1,548 / 1,568 bytes; 360 / 363 instructions; **0.9737**. Commit `ae81387` restored the target's TAG index update while keeping the loop's transform pointer; other cursor variants regressed. |
| `EnemyData::step_logic`, target `0x41c330`, `src/Enemy.cpp` | 2,207 / 2,208 bytes; 534 / 530 instructions; **0.9868**. Keep the branchless dialogue-damage selection; staged life/overkill rewrites previously regressed this owner. |
| `Bullet::step_ex_08`, target `0x4162d0`, `src/BulletManager.cpp` | 1,390 / 1,424 bytes; 327 / 336 instructions; **0.8929**. The committed `DirectionCornerScratch` union models the direction/corner stack overlap naturally; continue investigating corner math and register scheduling. |
| `EnemyData::step_interpolators`, target `0x41bb50`, `src/Enemy.cpp` | 1,692 / 1,696 bytes; 421 / 421 instructions; **0.9976**. The camera Y operand order checkpoint is committed. |
| `ScreenEffect::on_tick_shake`, target `0x45cd30`, `src/ScreenEffect.cpp` | **Latest incremental build:** 476 / 480 bytes; 121 / 121 instructions; **0.9917**, with one `push esi` occurring before rather than after the timer's current-frame store. Changing `tick_goto` to return the current frame did not fix it, so that trial was restored. |
| `StageInner::run_std`, target `0x40b3b0`, `src/Stage.cpp` | **2026-11-19:** 3,204 / 3,184 bytes; 677 / 688 instructions; **0.9275** after typing the signed 16-bit STD opcode (previously 0.9240). The later typed rocking-mode union kept the same local comparison. |
| `Player::on_tick_body`, target `0x442560`, `src/Player.cpp` | **2026-11-19:** 4,540 / 4,528 bytes; 929 / 925 instructions; **0.9137** with typed player/player-shot states. |
| `GuiMsgVm::run`, target `0x42a1d0`, `src/Gui.cpp` | **2026-11-19:** 1,211 target / 1,188 candidate linear instructions; **0.9504**, up from 0.9468 after recovering the byte-sized `MsgOpcode`. Its switch ownership still has an independent incomplete-audit warning. |
| `EndingScriptVm::run`, target `0x4199f0`, `src/Ending.cpp` | **2026-11-19:** 640 / 611 linear instructions; **0.9768**, up from 0.9742 after restoring `EndingOpcode : u8`. |
| `PauseMenu::tick_open`, target `0x43f980`, `src/PauseMenu.cpp` | **2026-11-19:** 1,322 / 1,318 linear instructions; **0.9674** after typing its lifecycle and substate enums; `PauseMenu::on_tick` remains 83 / 83, 1.0. |
| `TitleInf::on_tick`, target `0x44af80`, `src/MainMenu.cpp` | **2026-11-19:** 386 / 379 linear instructions; **0.9098** after typing the title lifecycle states. `TitleInf::set_state` remains 21 / 21, 1.0. |
| `HelpManual::on_tick_body`, target `0x42eab0`, `src/HelpManual.cpp` | **2026-11-19:** 336 / 338 linear instructions; **0.9763** after typing manual lifecycle and page states. |

Additional 2026-11-19 focused owner diagnostics (local normalized, not
accepted strict Oracle evidence): SoundManager::update_sound_thread 379/385
instructions at 0.9529; ReplayManager::on_tick_record 87/65 at 0.7632;
Stage::draw_layer 206/206 at 1.0, with StageInner::run_std remaining 0.9275.
The sound queue still spills the count and omits a second positivity check
before division. PlayerBullet::create and Player::shoot_one_bullet remain
376/376 and 88/88 at 1.0; GameWindow::update_window and
do_frame_sleeping remain 60/60 and 78/78 at 1.0.

Focused ECL opcode diagnostics from the latest 2026-11-19 incremental build:
cases 402/403/411/413 (line/infinite/curve/beam laser) are respectively
74/77 at 0.78, 80/83 at 0.75, 68/71 at 0.79 and 65/66 at 0.75. These are inline case spans, not complete
owners. The ECL dispatch map and its complete PDB owner are different scopes;
never infer exactness from dispatch coverage or case ratios.

## Recent natural-source checkpoints

For exact diffs consult `git show COMMIT`, not an old note's guessed source
form. The most relevant recent commits are:

- d96eead: type EnemyLife's pending-kill/spell word and cast the mask
  updates in enemy initialization and ECL spellEnd; step_logic and
  receive_damage retain 0.9868 and normalized 34/34, respectively.
- 82b1cfa: materialize the ANM FSET_RAND scaled result before resolving the
  destination. The case's local scope changes substantially; the full
  AnmVm::run ratio is 0.9485, not strict exactness.
- 4ab0d84: recover signed 16-bit STD quad kind, including the negative
  end-of-list sentinel, and preserve variable-length quad record offsets.
- d655874: type recording, playback and loaded replay modes without changing
  initialize(i32,...) ABI; playback and initialization retain local 1.0.
- 2d0018d: type the enemy's main drop as ItemType through enemy creation,
  dropMain ECL, and drop reset; ECL owner retains 0.9022.
- 4b249d6: type stored ScreenEffectMode, retaining its integer creation ABI.
- 090ff30: consolidate FramePacingMode in the window, frame pacing table and
  saved pause-menu state without changing storage layout.
- 75ed788 and 048b58f: recover sound worker lifecycle and BGM queue opcodes;
  update_sound_thread remains 0.9529, modify_bgm remains 41/41 at 1.0.
- d6eff7e: type the single-byte SHT shooter kind used by player-shot creation.
- `b7ff292`, `9f4944e`, `976688b`: recover the pause, title and manual
  state/substate types without changing the original integer setter ABI.
  The affected large state machines build and retain their local ratios.
- `4362993`, `99cf66b`: restore native 8-bit ending and MSG opcodes and the
  argument offsets in their records; the two complete interpreter ratios
  improve to 0.9768 and 0.9504. No strict exactness inference.
- `e4f27ff`: type `EnemyBulletShooter::aim_type` as `EtAimMode : u16` and
  convert the ECL, bullet EX and laser EX assignments at their integer
  script boundaries. The original low-word encoding is preserved.
- `8339e1e`: model `bullet_mgr_offsets` as a native 3D vector; the ECL
  complete-owner local ratio improved from 0.9019 to 0.9022, laser case 402
  from 0.77 to 0.78, and bosses-interrupt case 502 from 0.97 to 0.99.
- `f910f2f`: restore byte-sized camera rocking mode with names for the
  supported patterns in a four-byte `StageInner` word. The STD interpreter
  remains at local ratio 0.9275.
- `e55469a`, `9b54c61`, `09a6cf2`: type player and player-shot lifecycle
  states (32-bit), item state/type (32-bit), and bullet lifecycle state
  (16-bit); their touched large owners and focused leaves still build.
- `8ad19f6`: separate `BulletOrigin.enabled` (float 0/1 marker for
  `etOffsetAbs`) from a shooter's real relative Z offset. Keep the origin's
  explicit marker when changing laser origin arithmetic.
- `d40b241`: replace generic `InterpStrange1::flag_1d` with typed per-axis
  flag usage across enemy ECL and the interpolator step.
- `b6cefb6`: restore the signed 16-bit stage STD opcode and layout; its
  large interpreter's local normalized ratio rose from 0.9240 to 0.9275.
- `84000e8`: type the 32-bit `InterpMode` fields of `InterpInt`, `InterpInt3`,
  `InterpAngle` and `InterpCameraSky` with explicit casts at ANM and stage
  script boundaries. The full ANM and stage owner diagnostics are unchanged;
  the `InterpInt3::step` and `InterpAngle::step` normalized diagnostics remain
  270/270 and 260/260 respectively.
- `6a7697d`: type the `InterpFloat2` and `InterpFloat3` method fields through
  stage, ANM, enemy ECL and bullet EX. `InterpFloat3::step` remains 230/230
  in its local normalized comparison; the ECL and ANM dispatch owners retain
  their previous ratios.
- `da3c7c6`: type `InterpFloat::method` in the shared ECL, ANM and bullet
  transformations without changing `InterpFloat::start`'s integer ABI.
- `a076964`: type `LaserDataInf::state` and `kind` as fixed-width enums while
  preserving `allocate_new_laser(i32, void*)` and its original PDB symbol.
  Line/curve EX owners and laser construction cases retain their diagnostics.
- `ecd04c1`: recover the y and z per-axis ECL interpolator modes in the
  anonymous method union; `MOVE_CURVE` cases 121/123 remain 169/173, 0.97.

- `e6293cb`: restore signed 32-bit `InterpMode` in the ECL curve interpolator;
  local `InterpStrange1::step` remains 313 / 313 instructions at 0.9936.
- `c179d02` and `0ca80c8`: use the chosen typed `PosVel*` for ECL curve and
  Bezier position evaluation; the affected opcode blocks and large owner have
  unchanged normalized diagnostic results. Avoid reintroducing `this + offset`
  casts just to select absolute versus relative position.
- `a91560e` and `da1b8f0`: unify masked ANM effect tick/render allocation and
  type its overlay modes. Creation and draw callbacks retain their local
  normalized match (86 / 86 and 355 / 355, respectively).
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

Latest ignored .analysis/th16-s10-* trials: ECL movePos3D as a vector
temporary lowered its opcode group to 0.69, while a cached ECL context
pointer lowered it to 0.72 (baseline 0.77). For the sound queue, reloading
count for averaging gave 0.9323 and a plain while-sum gave 0.9167, below
the baseline 0.9529. A volatile sound-ID local raised it to 0.9556 but was
rejected as an unnatural forced spill; a normal request snapshot had no
effect. ANM FSET_RAND with direct/inlined multiplication changed the
extracted opcode block from 24 to 13 candidate instructions and lowered
its case ratio to 0.70 (baseline 0.96). Its current expression is committed
in 82b1cfa because the full AnmVm::run diagnostic improved to 0.9485; confirm
the shared writeback before changing it again. The other trial variants
were restored. Do not assume linear disassembly past owner extents is code.

Later scoped comparisons found several natural-source variants that were
restored rather than committed: using a reference to `EnemyInterrupt` in
`BOSSES_INTERRUPT` lowered case 502 from 0.99 to 0.83; direct
`pos_vel->pos` component writes in `MOVE_POS_3D` lowered its case group
from 0.77 to 0.73; sharing the laser origin Y load before the copy lowered
cases 402/403/411 from 0.78/0.75/0.79 to 0.65/0.63/0.65; moving the half
width computation ahead of `fabsf` in `collision_test_circle_rect` lowered
its complete leaf ratio from 0.9612 to 0.8932. Retain the baseline and
consult the ignored `.analysis/th16-s9-*` diagnostics if revisiting them.


The most recent local A/B trials also restored several rejected natural
expressions: `LaserCurveInf::step_ex_angle_accel` using a direct or volatile
speed value (0.9796 unchanged or worse); a derived EX `SHOOT` cursor in the
line/curve large interpreters (0.9141 to 0.8883, 0.9737 to 0.9399);
`EnemyInterrupt &` captured early in bossesInterrupt (case 502 dropped from
0.99 to 0.83); and a `draw_circle` cached vertex count (0.9939 unchanged).
Changing the relative-origin XY addition order was neutral. These trials were
restored and their ignored evidence remains under `.analysis/th16-s8-*`.


The latest local trials also tested, compiled and rejected: a split-base laser
EX transform pointer (line EX ratio 0.9141 to 0.9094); updating the draw-circle
angle parameter directly (0.9939 to 0.9848); separating the recursive ANM
world-position component stores (0.9714 to 0.8936); and a shared `union`
for performance-counter and fallback double temporaries in `get_runtime`
(0.9744 to 0.8846). Direct ANM ID assignment in `EnemyData::step_interpolators`
was locally neutral (421/421, 0.9976) and was also restored. All corresponding
trial sources and diagnostic files are ignored under `.analysis/th16-s5-*`.
No ASM, byte padding or full cold replay was used in these tests.

The latest session also restored a separate, unchanged-result curve-laser
pointer-base trial and two regressive attempts: ANM fan parallel radius/speed
cursors (normalized 1.0000 to 0.9481) and scalarized masked-effect XY-before-Z
stores (0.8148 to 0.6258). Evidence remains ignored in `.analysis/th16-session4-*`.
The natural-source typed-position and typed-mode changes above were retained
only after the affected local build and opcode/owner comparisons.

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
