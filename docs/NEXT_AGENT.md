# Current handoff

Updated 2026-11-15. Read `AGENTS.md` first. Older handoffs and the removed
session logs are in Git history.

## Current checkpoint

| Item | Value |
| --- | --- |
| HEAD | latest local `claude-opus-5.5-high: …` commit (nothing pushed) |
| Strict audit | **1033 exact / 131 incomplete / 51 mismatch** of 1,215 annotations |
| Build | incremental graph matches HEAD |

Check with `.analysis/claude-tools/bc.sh` (incremental build) followed by
`.venv/bin/python scripts/audit-reference.py` and `scripts/check-frontier.py`.
The ratchet (`config/frontiers.toml`) fails when an exact function stops being
exact, a mismatch gains a differing byte or becomes incomplete; record
improvements with `check-frontier.py --update`. Before committing a gain, run
`audit-reference.py --write-units` once on the final build. Tooling changes
need `scripts/run-tests.py` (all `scripts/test-*.py` controls, about 2 min).

## Constraints

- **Never push**, mirror or publish the repository. Local commits only, with
  the message prefix `claude-opus-5.5-high: ` and the attribution line.
- Do not use REA. Reference labels and percentages carry no authority.
- Natural C/C++ source. The exceptions below are user-approved placeholders,
  clearly marked in the source. Run only the checks a change needs.

### Placeholders

LTCG's stack-alignment pass weighs double arithmetic **before** dead code is
removed, and some original functions carried work that left no trace:

- `DECOMP_DEAD_DOUBLE_0..3` (`src/decomp.h`): dead doubles in place; the
  function itself wants an 8-aligned stack.
- `decomp_want_aligned_stack()`: a separate call-graph node with a dead
  double; callers pad, or their callers realign.
- `decomp_supervisor_scanf_reference` (`src/Supervisor.cpp`): an unreferenced
  `sscanf` user. It makes Supervisor.obj provide
  `___local_stdio_scanf_options`, as in the original.

Placeholders were kept only when the full audit gained with no losses.
`.analysis/claude-tools/placeholder_try.py ADDR SNIPPET...` automates that.

## Levers that worked

- **Call graph and alignment**: direct calls instead of the member-pointer
  workarounds (`create_effect_via_pointer`, `gui_show_notice_func`) where the
  original realigns; `__forceinline` helpers hide call weight (a helper for
  twelve `AnmVm::run` calls fixed `setup_special_anms`); `HARNESS_CALLED` on a
  callee and its intermediate callers tells LTCG they are entered aligned
  (`build_world_matrix`), since /INCLUDE'd functions are roots of unknown
  alignment.
- **COMDAT providers**: a CRT inline's out-of-line copy comes from the first
  object in link order whose IL uses it; the Oracle wants the annotating
  file's object (`scripts/build.py` orders the early files).
- **Intrinsics**: with memset as an intrinsic the compiler folded
  `Config::Config`'s stores into g_Supervisor's static image; `#pragma
  function(memset)` around it restores the original initializer.
- **Per-branch pushes**: where the original pushes a constant in each branch
  before one shared call, write a ternary of calls (`ECL_DIFF_ARG` in
  `src/EnemyEcl.cpp`) or an if/else of whole calls (anm316); arithmetic on the
  argument index compiles to `setne`/`lea` instead.
- **Statement shapes**: return a just-cleared value (`setup_stage_hud`);
  evaluate call arguments into locals in the original's order (ECL cases);
  push each arithmetic result in its own case (`ecl_run`); pointer-to-member
  locals change scheduling (`set_position_subpixel`, `build_world_matrix`);
  read `next` before `entry` in list walks; step vertex pointers per vertex;
  divide a loop step into its parameter in place (`Fog::set_rect`); rotate
  through a `Float3` offset local (a `Float2` adds alignment weight).
- **Timer ticks**: `tick`, `tick_goto`, `tick_mixed`, `tick_nested` and
  `tick_in_place` are equivalent; each gives different codegen.
- **Globals**: a global defined outside /GL
  (`probes/reference-support/Opaque.cpp`) changes alias analysis
  (`g_zero_vec2` lives in `Arcfile.cpp`); local copies of globals can flip
  SIB order (`destroy_all`).
- **Dead code leaves EH states** (`parse_directory`'s NULL-path `delete[]`).

## Open leads

1. **Alignment roots**: `.analysis/claude-tools/alignroots.py` (after a fresh
   audit) lists prologue-form differences (`R` and-esp, `X` ebx, `-` none).
   Ours uses the `X` form where the original uses `R` in `do_options`,
   `do_key_config`, `do_practice_stage_select`, `do_spell_practice_subseason`,
   `do_spell_practice_difficulty` and `repopulate_options`; the trigger is
   unknown. `Bullet::on_tick` realigns in ours, `BulletManager::on_tick_body`
   in the original.
2. **Padded frames** (original `sub esp` 4 larger): `show_notice`,
   `create_vm`, `create_vm_front`, `interrupt_child_and_run`,
   `cancel_in_radius`. A pad needs known-aligned callers; a placeholder makes
   these realign instead.
3. **Large owners**: `.analysis/claude-tools/cases.py ADDR [OPS]` compares
   switch cases of `ecl_run_over_300` (0x41dcb0), `ecl_run` (0x472030) and
   similar dispatchers; `calldiff.py` finds inlining and tail-merge gaps
   (`ecl_run_over_300` calls `LaserInfiniteInner`'s constructor out of line in
   the original).
4. The rest are mostly register-allocation and scheduling tie-breaks. Probe
   them first: `.analysis/claude-tools/p/ltcg2.sh file.cpp` builds one /GL
   file in seconds (read inputs through `*(T *volatile *)0x500000`, write
   outputs as volatile; probes may include `../../../src/X.h`).

## Tools (ignored `.analysis/claude-tools/`)

`bc.sh` (incremental build), `tryaudit.sh` (build, audit, list gains and
losses against `.analysis/reference-audit.json`), `dd.py ADDR` (diff),
`score.py ADDR`, `cases.py`, `calldiff.py`, `callers.py`, `frames.py`,
`alignroots.py`, `ehscan.py`, `placeholder_try.py`, `swaptrial.py`
(adjacent-statement swaps), `ticktrial.py`, `hctrial.py`.

## Do not repeat

- Statement-swap trials (`swaptrial.py`) over 31 mismatching functions found
  no gains.
- `#pragma function(memset)` on other memset users changes nothing.
- Commutative operand order (`Unpause`, `kill_all_no_set_death`, the y/z
  reversal in vector sums) and xmm register swaps (`ZunAngle::operator-`,
  `rotate_points`) did not respond to source order, locals or branch shapes.
- `0.0` vs `0.0f` literals add no alignment weight; double intrinsics in
  `run` add none either.
- `HARNESS_CALLED` on `interrupt_child_and_run` makes the cursor functions
  inline it; on `update_options` it changes nothing. `update_options` keeps a
  /GS cookie: a 12-byte local plus a by-value `AnmId` call with a second
  argument gets one in probes.
- `run_ex` DELAY/WAIT `or ecx, edx` and `LaserInfiniteInf::run_ex`'s ex/type
  register swap resist every rewrite tried.
- `SetVolume`/`SoundBufferEntry::play` tail merges follow the vtable register.
- Address-taking `get_vm_with_id` (to block interprocedural register use)
  loses three exact functions and fixes nothing.
- In `ecl_run`, rewriting the sin/cos/sqrt cases with value locals turns off
  tail duplication across the whole function.
