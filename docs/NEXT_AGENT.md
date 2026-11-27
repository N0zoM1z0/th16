# TH16 next-agent handoff

Updated 2026-11-27 after a 3,899/3,964-byte title-screen reconstruction
advance and correction of the ECL boss cleanup-frame evidence. No new exact
credit was added. Read [AGENTS.md](../AGENTS.md) before editing; keep
checkpoints local and push `main` only when asked.

## Current baseline

- **Latest source commit**: `9e1616c` (`gpt-web: align TH16 title-screen control flow`)
- **Incremental build**: `build/reference-candidate/th16.exe` (1,166 annotated
  functions; preserve its object/dependency graph for fast incremental builds).
- **Local strict audit** (`.analysis/reference-audit.json` and
  `resources/progress.svg`):
  - **1,061 / 1,215 functions exact** (**257,831 / 442,168 bytes = 58.31%**)
  - **36 mismatch · 118 incomplete** (90.29% complete extents compared)
- **Factory status**: `not-submitted` (local strict comparisons only; the shared
  Factory accepted snapshot is inventory-only and returns no Oracle results).

## Working commands

```sh
git status --short --branch
scripts/repo-python scripts/build.py
scripts/repo-python scripts/audit-reference.py --address 0x450ef0 --json .analysis/audit_tmp.json
# After committing an exact match, refresh config/ and resources/progress.svg:
scripts/repo-python scripts/audit-reference.py --write-units && \
  scripts/repo-python scripts/progress.py --svg resources/progress.svg
```

Focus on one function at a time, verify the complete affected TU with
`audit-reference.py`, update `resources/progress.svg` after exact matches, and
avoid full cold builds unless a dependency/cache problem is demonstrated.

## Current reconstruction frontier

- `0x41dcb0` (`EnemyData::ecl_run_over_300`): the reviewed EH3 cleanup graph
  validates. The original complete owner is 21,408 bytes; the current
  `EnemyEcl.obj` contribution is 21,328 bytes, leaving an 80-byte extent
  difference. Returning the line/infinite/curve shot origin as `D3DXVECTOR3`
  improved instruction-signature alignment from 0.9390 to 0.9398 and adds
  32 bytes over the original output-pointer helper. Keep the original
  `has_origin` true branch first and preload y before branching; the inverted
  condition experiment was 48 bytes larger but aligned worse (0.9379). The
  original Fog cleanup saves its pointer at EBP-`0x420`; the candidate stores
  and cleans up its pointer at EBP-`0x404`, with cookie/state at
  EBP-`0x474`/EBP-`4`. All offsets are read
  from the allocation store and emitted EH3 funclet/handler, not inferred.
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
- `0x412860` (`BulletManager::on_tick_body`, `src/BulletManager.cpp`, ~471 B)

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
