# TH16 next-agent handoff

Updated 2026-11-28 after tracing menu return aliases and load-address reuse.
All source controls from this investigation are restored. `take_snapshot`
remains 443/464 bytes and `tick_open` retains its single SIB difference.
The existing ECL opcode 601 experiment remains dirty and preserved.
Read [AGENTS.md](../AGENTS.md); keep checkpoints local and push `main` only
when asked.

## Current baseline

- **Latest checkpoint**: see `git log -1`; use the user's `gpt-6.1-sol: ...` message format.
- **Incremental build**: `build/reference-candidate/th16.exe` (1,166 annotated
  functions; preserve its object/dependency graph for fast incremental builds).
- **Last full local strict audit** (`.analysis/reference-audit.json` and
  `resources/progress.svg`; not rerun during this focused session):
  - **1,061 / 1,215 functions exact** (**257,831 / 442,168 bytes = 58.31%**)
  - **36 mismatch · 118 incomplete** (90.29% complete extents compared)
- **Factory status**: `not-submitted` (local strict comparisons only; the shared
  Factory accepted snapshot is inventory-only and returns no Oracle results).
- **Latest restoration result**:
  `.analysis/title-compiler/menu-context-restored-strict.json` compares 280
  related complete owners: 245 local passes, 30 incomplete and five
  mismatches. All 280 verdicts, owner sizes and recorded differences agree
  with the preceding baselines. No source control is retained and no complete
  function is newly exact in this checkpoint.
  The last retained source change remains the snapshot surface-copy exits:
  443/464 bytes, with 21 frame/stack-displacement bytes different.
  `tick_open` retains its complete 4,676-byte scope, linked fields and both
  reviewed switch tables; only SIB +0xb28 differs. All 34 preceding Bullet
  passes survive. The earlier 86-owner source checkpoint and 125-owner
  shared-state reports remain under `.analysis/pause-compiler/` and
  `.analysis/bullet-compiler/`; the broad totals above remain historical.

## Working commands

```sh
git status --short --branch
scripts/repo-python scripts/build.py
scripts/repo-python scripts/audit-reference.py --address 0x416f40 --json .analysis/audit_tmp.json
```

Verify the complete affected TU with `audit-reference.py`. Keep focused reports
for routine iterations; refresh the global ledgers and progress graphic at a
broader milestone. Preserve the incremental build graph.

## Current reconstruction frontier

Follow [the remaining-function roadmap](ROADMAP.md) for the next batches and
their affected comparison scopes. The existing dirty opcode 601 vector
assignment in `src/EnemyEcl.cpp` is preserved for review.

- Continue the menu frame and copy questions from
  [the compiler-context finding](knowledge/pause-menu-compiler-context.md).
  Keep the snapshot surface-copy exits. Its remaining stack gap is one extra
  color: the created AnmId return area does not share the later source-surface
  slot. The validated `snapshot-lifetime` trace finds that return object in
  later loaded-anm and flush_sprites alias sets. A single opaque creator
  allows sharing but changes other ABI/frame choices. Scalar-copy and scoped
  handle controls do not repair the ordinary source. Follow alias-summary
  provenance rather than repeating declarations.
  Keep `tick_open`'s const name-reading receiver. Its copy SIB remains 0x0e
  versus target 0x31 at +0xb28. The validated `copy-provenance` trace has
  separate cursors at PreLower and source plus delta by Lower. Freed operands
  can be reused by another copy; follow source provenance. The smaller
  `trace-copy-address-routines.py` observer is prepared but unexecuted.

- `TitleInf::do_difficulty_select` (`0x44fe20`) has a specific source gap;
  read [the title menu context](knowledge/title-menu-compiler-context.md).
  Its 1,180-byte extent matches, but `[ecx]` replaces `[esi+0x24]` for the last
  menu reload. The shorter instruction leaves the reviewed code range inside
  a two-byte NOP. Keep the independent switch record unchanged. A const
  receiver and opaque pop provider do not repair it. Trace when the ready
  menu address replaces the title-based load address.
  GameThread's BGM store remains 622/623 bytes. Its validated AddrModes entry
  receives g_Scorefile before music (keys 0x104e0 and 0x10040). Same-TU and
  cross-TU BGM sharing retain that order. The pilot's FinishBreakpoints at
  unprologued entries observe enclosing returns: use entry facts only. The
  explicit return-PC/ESP observer `trace-stage-address-returns.py` is prepared
  with verified cleanup sizes, but is unexecuted.

- Continue `Bullet::on_tick` (`0x411e70`, 1,568/1,592 bytes) together with
  `check_player_collision` (`0x4124b0`, 449/448 bytes). Read
  [the compiler-context finding](knowledge/bullet-compiler-context.md).
  Controlled C2 links reproduce all 40 ordinary owners. Timer operand sorting
  occurs before lowering: a promoted speed value outranks the frame read.
  A named speed value restores the timer's XMM0 add but changes later movement
  sharing and does not close tick. A shared physics vector gets the full-step
  X/Y/Z registers right while its Y/Z position adds still use the wrong memory
  operands at PreEncode. Do not tune only the final scheduler.
  The collision goal also has a four-byte stack-slot displacement difference;
  naming its animation ID delays the VM lookup and is rejected. Keep its
  temporary-handle call chain. StackPack shows goal and scaled size sharing
  EBP-0x0c, while the ID reuses the parameter home at EBP+8. Directly passing a
  temporary goal does not change packing. Investigate the vector/box lifetimes
  and call summaries before more declaration-order controls.
  Every source control is restored; private snapshots and focused reports use
  `tick-` and `collision-` prefixes under `.analysis/bullet-compiler/`.
  Preserve `step_ex_17`: the retained `BulletExState` has a vector at `+0x28`
  and a move-specific saved-speed scalar at `+0x14`, rather than accessing both
  through an eight-float array. This closes the completed-movement branch
  without changing its timer tail.

- `0x41dcb0` (`EnemyData::ecl_run_over_300`): target and candidate complete
  PDB extents are both 21,408 bytes; both code bodies are 19,976 bytes. The
  owner is still **incomplete**, not exact: the candidate's main switch table
  differs from the reviewed target case mapping. Its EH3 cleanup graph now
  validates with candidate Fog pointer/cookie/state at EBP-`0x40c`/`0x45c`/`4`
  (target: EBP-`0x420`/`0x484`/`4`). The four argument leaves remain strict
  exact: `get_int_arg` (18/18), `get_int_arg_ptr` (14/14), `get_float_arg`
  (18/18), and `get_float_arg_ptr` (18/18).
  - `moveEllipseTime` (421/423): 780/780 bytes, 169/168 instructions
    (target/candidate). The source now models radial and ellipse initial/goal
    values as four `Float2` locals instead of eight scalar locals. This
    restores the target case extent while preserving argument and fallback
    order; the emitted EH cookie moves from EBP-`0x46c` to EBP-`0x45c`.
  - `moveAngleTime`: 537/531 bytes, 115/114 instructions. One effective angle
    local and explicit volatile self-stores remain on mirrored, unmirrored,
    and missing-angle paths.
  - `moveSpeedTime` (445/447): 283/272 bytes, 61/59 instructions. Rewriting
    the fallback ternaries as explicit `if` branches produced identical code;
    the remaining difference includes the compare direction and one extra
    stack self-store. Do not count a size-only adjustment as reconstruction.
  - Opcode 315 (`anmPlayRotate`) now matches at 70/70 bytes and instructions
    after inlining the positioned VM setup in natural C++.
  - Opcode 702 is 439/441 bytes and opcode 711 is 401/394. `diffF` is
    structurally accounted for: target and candidate each have the same
    26-byte / 6-instruction out-of-line Easy block; the apparent contiguous
    difference is block placement, not missing logic.
  Whole-owner instruction alignment is 0.943756 (diagnostic only, not an
  exactness receipt). Continue from the disassembly and full table mapping;
  do not update switch ownership to excuse candidate offsets.
- `0x44b5f0` (`TitleInf::do_title_screen`): 3,899/3,964 bytes after using a
  `MenuHelper *` alias in substate 2, sharing the Quit exit path, and storing
  `g_Globals.difficulty` before `set_state`. The remaining differences are
  mostly stack-slot offsets and argument scheduling; do not add dummy locals.
- `0x43f980` (`PauseMenu::tick_open`): 4,675/4,676 bytes. The retained name
  reader fixes the scan; only the replay-name copy SIB remains. See the active
  frontier above.

## Key compiler findings from this session

1. **Historical stack-alignment observation — do not use as a new tactic**:
   In MSVC v141 `/O2 /GL`, a 0-stack-parameter function that aligns its stack
   only for a callee can emit the 24-byte `push ebx; mov ebx, esp; sub esp, 8;
   and esp, -8; add esp, 4; push ebp; ...` prologue with `[ebp-N]` locals.
   Existing `DECOMP_DEAD_DOUBLE_3;` experiments showed that dead floating-point
   arithmetic changes LTCG's alignment weight and can flip that prologue to
   `push ebp; mov ebp, esp; and esp, -8` with `[esp+N]` locals. Although this
   helped older matches (`do_options`, 836 B; `do_spell_practice_difficulty`,
   812 B; `do_spell_practice_subseason`, 776 B), it is artificial dead code,
   not reconstructed game logic. Do not add it to new functions or count it as
   natural-source progress; recover real locals and lifetimes instead.
2. **`HARNESS_CALLED` (`__declspec(noinline)`) blocks LTCG inlining**:
   When a target inlined a `HARNESS_CALLED` helper, adding a `static __forceinline`
   copy restores exact codegen (e.g., `Spellcard::on_tick_body`, 650 B, matched
   100% by inlining `EnemyManager::find_enemy_by_id`).
3. **LICM preheader ordering**:
   Moving loop-invariant initialization inside a `for` loop causes MSVC LICM to
   hoist the stores after loop-counter initialization (e.g., moving `pos = 0`
   inside the comment-line loop matched `TitleInf::do_music_room`, 3,136 B).
4. **Tail-merge direction in large switches**:
   Moving `return;` vs `break;` (fallthrough) between two identical tails flips
   which `case` hosts the shared tail (`PauseMenu::tick_open` improved from
   `incomplete` to 4,674 / 4,676 bytes at that checkpoint). The later const
   name-reader binding recovers one of the two SIB bytes.

## Highest-value next targets

### 1. Large remaining source owners

The active Bullet leaf follows the completed manager and wrap update. The C2 investigation
explains why caller/callee alignment must be handled together; the larger
owners below remain queued in [ROADMAP.md](ROADMAP.md).

- `0x41dcb0` (`EnemyData::ecl_run_over_300`, `src/EnemyEcl.cpp`, 21,408 B):
  continue from the verified EH graph and compare the complete dispatch body,
  frame layout, all three switch tables and the 702-byte opcode map. Do not
  promote the candidate's shorter PDB contribution.
- `0x450ef0` (`TitleInf::do_practice_stage_select`, `src/MainMenuStates.cpp`,
  1,232 B): the current candidate has a different complete extent and stack
  prologue. Recover its original source lifetime and call shape naturally.
- `0x452330` (`TitleInf::do_player_data`, `src/MainMenuStates.cpp`, 2,304 B):
  the current candidate owner is shorter. Do not add `DECOMP_DEAD_DOUBLE_3` or
  other dead arithmetic to manufacture stack alignment.

### 2. Other incomplete functions missing `and esp, -8`

- `0x4532f0` (`TitleInf::do_score_name_entry`, `src/MainMenuStates.cpp`, ~1,444 B)
- `0x446260` (`sht_on_tick_laser`, `src/PlayerShot.cpp`, ~1,522 B)
- `0x40fe80` (`BombMarisaAInf::cancel_bullets`, `src/BombMain.cpp`, ~595 B)

### 3. Near-exact large mismatches & preserved compiler traces

- `0x44b5f0` (`TitleInf::do_title_screen`, `src/MainMenu.cpp`, 3,964 B —
  3,899 / 3,964 after the control-flow changes above; the remaining 65 bytes
  are mainly stack-slot offsets and argument-load scheduling)
- `0x43f980` (`PauseMenu::tick_open`, `src/PauseMenu.cpp`, 4,676 B — currently
  4,675 / 4,676; one replay-name copy SIB byte remains)
- `0x431fe0` (`LaserLineInf::run_ex`, `src/Laser.cpp`, 1,588 B) — full compiler
  trace and restore checkpoints remain in
  [docs/knowledge/line-run-ex-compiler-trace.md](knowledge/line-run-ex-compiler-trace.md)
  and `.analysis/line-run-ex-compiler/`.

## Storage and preserved evidence

Obsolete `.analysis/*-work` directories, detached historical git worktrees, and
13,740 loose trial files were removed on 2026-11-26 (`.analysis/` is now ~467
MiB). Active compiler evidence (`*-compiler/`), `claude-tools/`, `archives/`,
Factory registration/validation files, and `build/reference-candidate/` remain
intact. See [ARTIFACTS.md](ARTIFACTS.md) before cleaning further.
