# TH16 next-agent handoff

Updated 2026-11-28 after closing clear-all at 500 bytes and 11 linked fields
through construction of the scaled velocity vector. The manager tick,
wrap and move updates remain locally exact. The existing ECL opcode 601
vector assignment experiment remains dirty and preserved. Read
[AGENTS.md](../AGENTS.md) before editing; keep checkpoints local and push `main`
only when asked.

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
- **Latest focused result**: the complete Bullet TU has 34 local passes and
  six incomplete owners. Clear-all passes 500/500 bytes and 11 linked fields;
  the standalone cancel retains all 444 bytes and 10 linked fields.
  The preceding shared-state comparison covers 125 complete owners in
  BulletManager, Laser and LaserLine: 102 local passes, 20 incomplete and
  three mismatches, including the 597-byte move update with 12 linked fields.
  Evidence: `.analysis/bullet-compiler/clear-all-final-strict.json`
  and `step17-final-consumers-strict.json`.
  The broad totals above remain historical.

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

- Continue with `Bullet::on_tick` (`0x411e70`, 1,568/1,592 bytes). Its full
  step keeps three scaled velocity values live before position updates, and
  its half-step cases have different partial sharing. Prior vector-delta,
  D3DX API and scalar controls did not close the complete owner.
  Clear-all is now closed by constructing the game-speed-scaled vector
  before the half-step multiplication. The controlled allocator traces
  distinguish initial symbol order from later coalescing; use that evidence
  when investigating the movement branches, rather than changing only the
  final instruction scheduler.
  Preserve `step_ex_17`: the retained `BulletExState` has a vector at `+0x28`
  and a move-specific saved-speed scalar at `+0x14`, rather than accessing both
  through an eight-float array. This closes the completed-movement branch
  without changing its timer tail. Read
  [the compiler-context finding](knowledge/bullet-compiler-context.md) before
  choosing source controls.

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
- `0x43f980` (`PauseMenu::tick_open`): 4,674/4,676 bytes. Pointer-addition
  reordering and integer-address casts did not change either scale-1 SIB
  encoding; retain natural indexing rather than keeping those experiments.

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
   `incomplete` to 4,674 / 4,676 bytes, leaving only 2 scale-1 SIB base/index
   tie-breakers).

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
  4,674 / 4,676; only 2 scale-1 SIB base/index tie-breakers remain)
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
