# Current handoff

Updated 2026-11-14 for transfer to another agent. Read `AGENTS.md` first. The
2026-11-13 handoff is in Git history (`git show 5481046:docs/NEXT_AGENT.md`);
its counts and open-owner table are superseded.

## Current checkpoint

| Item | Value |
| --- | --- |
| HEAD | latest local `claude-opus-5.5-high: …` commit (nothing pushed) |
| Strict audit | **1024 exact / 133 incomplete / 58 mismatch** of 1,215 annotations |
| Build | incremental graph matches HEAD; no build or audit is running |

Check with `.analysis/claude-tools/bc.sh` (incremental build) followed by
`.venv/bin/python scripts/audit-reference.py`. Before committing, run
`audit-reference.py --write-units` once on the final build.

## Constraints

- **Never push**, mirror or publish the repository. Local commits only, with
  the message prefix `claude-opus-5.5-high: ` and the attribution line.
- Do not use REA. Reference labels and percentages carry no authority.
- Natural C/C++ source, with one approved exception (below). Run only the
  checks a change needs; no cold rebuilds unless a cache problem is proven.

### Approved alignment placeholders

On 2026-11-14 the user explicitly approved clearly marked placeholder dead
code for stack alignment. LTCG's double-alignment pass weighs double
arithmetic **before** dead code is removed. Some original functions carried
double work that was later deleted and left no trace in the binary. The
placeholders restore that weight:

- `DECOMP_DEAD_DOUBLE_0..3` (`src/decomp.h`): dead doubles in place. The
  function itself wants an 8-aligned stack; each multiply adds weight.
- `decomp_want_aligned_stack()`: a separate call-graph node with a dead
  double. Calling it makes the function a caller of a node that wants
  alignment, so it pads, or its callers realign.

Each placeholder was kept only when the full audit gained exact functions
with no losses. They are in `create_effect`, `anm_jagged_line_on_draw`,
`update_callout`, `show_lights_out`, `show_notice`, `show_stage_clear_bonus`,
`HelpManual::on_tick_body`, `create_ui_effect`, `create_ui_vm` and `Fog::Fog`.
`.analysis/claude-tools/placeholder_try.py ADDR SNIPPET...` automates the
try/keep loop; it keeps the first snippet that gains with no losses.
Already tried with no gain: `create_vm`, `create_vm_front`, `set_vm_script`
(costs `LaserCurveInf::initialize`), `cancel_in_radius`, `step_logic`,
`BulletManager::on_tick_body`, `setup_stage_hud`, `sht_on_tick_laser`, and
`on_tick` of LaserLineInf and LaserInfiniteInf.

## Levers found 2026-11-14 (second session)

- **Direct calls instead of member-pointer workarounds** gained 8 exact
  (TitleInf states, title/cursor menus, the extend notice). Converting the
  remaining `create_effect_via_pointer`, `gui_show_notice_func` and other
  `->*` sites was tried per function; the rest lose.
- **Helpers hide call weight**: twelve direct `AnmVm::run` calls made
  `setup_special_anms` realign; a `__forceinline` start helper removed it.
- **Caller-chain alignment knowledge**: a callee that realigns to 16 for a
  spilled matrix row stops when it and its intermediate callers are
  `HARNESS_CALLED` (an /INCLUDE'd function is a root of unknown alignment).
  This made `build_world_matrix` exact. Applying it to other padded
  functions and their callers gained nothing (`hctrial.py`).
- **Return values**: `build_world_matrix` returns 0 in the original
  (`xor eax, eax` before `ret`).
- **Vector locals for rotations**: rotating through a `Float3`/`Float2`
  offset local gives the original's load-then-multiply form
  (`collision_test_circle_rect`, `sht_on_hit_laser`). A `Float2` local adds
  alignment weight to callers; use `Float3` where that matters.
- Trial tools: `perfunc.py`, `edtrial.py`, `hctrial.py`, `tryaudit.sh`.

## Best next leads

1. **TitleInf menu states** (`do_title_screen`, `do_options`, about 15 `do_*`
   states). They now differ only in their own realign. They reach
   `create_effect` through `create_effect_via_pointer` (`AnmManager.h`), a
   member-pointer workaround that hides the call from LTCG's call graph. That
   workaround predates `create_effect`'s placeholder, so try direct
   `->create_effect(...)` calls there. Do the same for any other
   `create_effect_via_pointer` / `gui_show_notice_func` users whose original
   realigns.
2. **Alignment roots**: run `.analysis/claude-tools/alignroots.py` on a fresh
   audit. It lists functions whose prologue form differs (`R` and-esp
   realign, `X` ebx realign, `-` none) and whether their callees agree; only
   rows with `0` mismatched callees are local roots. Open roots include
   `get_controller_state`, `update_score`, `add_to_score`, `on_tick_record`,
   `repopulate_options`, `Bullet::on_tick` (ours realigns,
   `BulletManager::on_tick_body` should) and `draw_3d`.
3. The remaining mismatches are mostly register allocation and scheduling:
   one swapped register pair or one moved load in otherwise identical code.
   Many look like compiler tie-breaks. Probe before editing (below).

## Techniques that worked this session

- **Probe first**: `.analysis/claude-tools/p/ltcg.sh file.cpp` plus
  `p/lmd.py` build a single /GL+/LTCG file in seconds. Read inputs through
  `*(T *volatile *)0x500000` and write outputs as volatile. Probes found:
  - `ZunTimer::decrement` keeps the multiply by 1.0f only with a negated
    `delta` local shared by both branches;
  - `x++; x %= 3;` gives the original's 0x55555555 idiv-free sequence;
  - `*o = 0; if (t > 0) *o = 1;` gives `cmovg`.
- **Call-count gaps** (`calldiff.py`, `callseq.py`) found cross-jump and tail
  merge differences: `MSG_BOSS_FACE`, and ecl_run's `ANGLE_DIFF` and
  `MATH_ANGLE` stores.
- **Global definition matters**: a global defined outside /GL
  (`probes/reference-support/Opaque.cpp`) changes LTCG alias analysis.
  `g_zero_vec2` moved to `Arcfile.cpp`. `g_stage_table` cannot move: the
  `stage-table-v1` Oracle binding needs its current owner.
- **Dead code leaves EH states**: `parse_directory`'s second (terminate)
  unwind state came from a `delete[]` on a NULL path. It is reviewed by the
  `array-allocation-cleanup-v1` profile (`scripts/eh_array_cleanup.py`).
  `ehscan.py` finds no other EH state-count differences.
- **Local copies flip SIB order** in some loops (`destroy_all`,
  `create_d3d_textures_for_loaded_anms`).

## Tools (ignored `.analysis/claude-tools/`)

`bc.sh ADDR...` (build + diff), `dd.py`, `symdiff.py ORIG SYMBOL N` (diff by
candidate symbol), `rankdiff.py`, `calldiff.py`, `callseq.py`, `cases.py`,
`bigdiff.py`, `frames.py`, `alignroots.py`, `ehscan.py`, `idiom.py`,
`sibscan.py`, `swscan.py`, `cmpaudit.py`, `refcmp.py` / `refshow.py` (bodies
that differ from the reference checkout), `placeholder_try.py`.

## Do not repeat

The full list of dead ends is in the user memory note
`ltcg-alignment-experiments.md`. In short:

- `0.0` vs `0.0f` literals add no alignment weight.
- Making `Bullet::on_tick` / `on_tick_body` HARNESS_CALLED or putting `run`
  in helpers changes nothing.
- Making `interrupt_child_and_run` HARNESS_CALLED makes the cursor functions
  inline it.
- `run_ex` DELAY/WAIT `or ecx, edx`: every rewrite fails because the case
  constant propagates.
- `SetVolume`'s two calls merge depending on which register holds the vtable.
- The y/z operand reversal moves with context; treat it as a tie-break.
- `___local_stdio_scanf_options` needs a scanf user in Supervisor.cpp that
  no longer exists.
