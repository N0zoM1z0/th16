# TH16 next-agent handoff

Updated 2026-11-26 after matching 28 additional functions, updating
`resources/progress.svg`, and cleaning up ~1.55 GiB of obsolete `.analysis/`
scratch artifacts. Read [AGENTS.md](../AGENTS.md) before editing; keep
checkpoints local and push `main` only when asked.

## Current baseline

- **Latest source commit**: `423f3d5` (`TitleInf::do_spell_practice_subseason`)
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

## Key compiler findings from this session

1. **`DECOMP_DEAD_DOUBLE_3;` flips callee-only `push ebx; mov ebx, esp` alignment
   to compact `push ebp; mov ebp, esp; and esp, -8`**:
   In MSVC v141 `/O2 /GL`, a 0-stack-parameter function that aligns its stack
   only for a callee emits the 24-byte `push ebx; mov ebx, esp; sub esp, 8;
   and esp, -8; add esp, 4; push ebp; ...` prologue with `[ebp-N]` locals.
   Adding `DECOMP_DEAD_DOUBLE_3;` gives the function its own alignment weight
   and flips it to the compact `push ebp; mov ebp, esp; and esp, -8` prologue
   with `[esp+N]` locals. This immediately matched `TitleInf::do_options`
   (836 B), `TitleInf::do_spell_practice_difficulty` (812 B), and
   `TitleInf::do_spell_practice_subseason` (776 B).
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

### 1. Ready-to-test `DECOMP_DEAD_DOUBLE_3;` candidates (`push ebx` vs `push ebp; and esp, -8`)

- `0x450ef0` (`TitleInf::do_practice_stage_select`, `src/MainMenuStates.cpp`, ~1,232 B)
- `0x4440e0` (`PlayerInner::repopulate_options`, `src/Player.cpp`, ~2,178 B)
- `0x44e930` (`TitleInf::do_key_config`, `src/MainMenu.cpp`, ~836 B; also has a
  byte-vs-dword load on `g_hardware_input_pressed`)

### 2. Incomplete functions missing `and esp, -8`

- `0x4532f0` (`TitleInf::do_score_name_entry`, `src/MainMenuStates.cpp`, ~1,444 B)
- `0x446260` (`sht_on_tick_laser`, `src/PlayerShot.cpp`, ~1,522 B)
- `0x40fe80` (`BombMarisaAInf::cancel_bullets`, `src/BombMain.cpp`, ~595 B)
- `0x412860` (`BulletManager::on_tick_body`, `src/BulletManager.cpp`, ~471 B)
- `0x452330` (`TitleInf::do_player_data`, `src/MainMenuStates.cpp`, 2,304 B —
  `DECOMP_DEAD_DOUBLE_3;` reaches 2,302 / 2,304 B; only 2 bytes differ in
  vectorized OR load order `+16` vs `+0`)

### 3. Near-exact large mismatches & preserved compiler traces

- `0x44b5f0` (`TitleInf::do_title_screen`, `src/MainMenu.cpp`, 3,964 B —
  3,875 / 3,964; mainly a +4 byte `esp` slot shift under `sub esp, 0x10` where
  candidate uses 3 slots and target uses 4, plus 3 small diffs: swap
  `g_Globals.difficulty = g_last_difficulty` before `set_state`, use
  `MenuHelper *m = &menu` in `case 2`, and prevent `push ecx; push 9` head-merge
  before `je`)
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
