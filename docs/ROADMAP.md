# Remaining reconstruction roadmap

Updated 2026-11-28. Use `config/reference-functions.csv` to find the recorded
candidate verdicts and `config/functions.csv` for the independent target
inventory. These are local comparison records; Factory acceptance remains
separate. Recheck each selected owner against the current incremental build.

## Execution order

The Bullet manager passes all 502 bytes and nine linked fields; wrap update
passes all 519 bytes and eight linked fields after recovering the predicate
control flow that feeds scheduling. Move update now passes all 597 bytes and
12 linked fields after restoring the shared scalar/vector state layout.
Clear-all now passes all 500 bytes and 11 linked fields after recovering the
constructed vector between its two scaling operations. The current menu
focus is `PauseMenu::tick_open`, now 4,675/4,676 bytes with its complete
4,676-byte owner still a mismatch. `Bullet::on_tick` remains open. Follow
[the compiler-context evidence](knowledge/bullet-compiler-context.md) when
choosing allocation or scheduling controls. The clear-all traces show how
first definitions and coalescing feed allocation before the final scheduler;
apply that method to Bullet tick's remaining movement branches.

1. **Bullet leaves and update loop.** Continue the remaining movement/data
   layout in `Bullet::on_tick` (`0x411e70`), together with its collision callee
   (`0x4124b0`). The read-only canonicalization trace now explains why timer
   and position operand choices change across movement-source controls;
   investigate those input values before final scheduling. Preserve clear-all
   (`0x416f40`), manager (`0x412860`), wrap (`0x415d80`) and move (`0x415f90`)
   updates. Compare every annotated owner in `src/BulletManager.cpp` after a
   retained change, including helper callers. Shared transform-state changes
   also require the complete Laser and LaserLine consumer scopes.
2. **Menu control flow and real local lifetimes.** Revisit
   `PauseMenu::tick_open` (`0x43f980`, one remaining copy SIB byte) from
   [the compiler-context finding](knowledge/pause-menu-compiler-context.md),
   then `TitleInf::do_title_screen` (`0x44b5f0`). Recover real call/local shapes
   in `do_practice_stage_select` (`0x450ef0`), `do_player_data` (`0x452330`),
   and `do_score_name_entry` (`0x4532f0`). Do not introduce dead arithmetic or
   dummy locals for stack alignment.
3. **Large ECL dispatch.** Preserve the existing uncommitted opcode 601
   vector-assignment experiment before further changes. Compare
   `EnemyData::ecl_run_over_300` (`0x41dcb0`) as one complete owner, including
   its three switch tables, opcode map and EH cleanup. Work through movement
   cases, bullet positioning and laser cases using the retained case traces.
   Keep target switch mappings independent of candidate offsets. Partial case
   improvements do not establish a matching dispatch owner.
4. **Projectile and collision owners.** Continue `LaserLineInf::run_ex`
   (`0x431fe0`) from its compiler-trace note, then remaining laser, infinite
   laser, bullet, player-shot, bomb and collision candidates. Prioritize
   `sht_on_tick_laser` (`0x446260`) and
   `BombMarisaAInf::cancel_bullets` (`0x40fe80`) when evidence explains their
   missing alignment. Resolve shared helper consumers together.
5. **Remaining subsystem candidates.** Take one translation unit at a time:
   ANM loading/rendering/callbacks, player/enemy/item/GUI, stage/game/replay,
   then sound/file/score/text/window/runtime helpers. Within each unit, close
   reviewed-boundary or linkage gaps before changing already matching code.
   The ledger supplies the individual remaining functions; do not treat a
   reference annotation or similarity score as a completed function.
6. **Inventory closure.** Reconcile target functions absent from the imported
   candidate ledger, recover their ownership and source, and compare their
   complete extents. Only after source and ownership closure is a clean build
   and broad milestone replay useful. Whole-image and runtime validation remain
   later work, not consequences of matching selected functions.

## Iteration and checkpoints

Treat this ordering as a starting point, not a requirement to tune each
function in isolation. When several differences suggest a common compiler
cause, follow the real caller/callee graph, shared definitions and source
lifetimes before rewriting the visible instruction site. TH09's
`docs/RE_WORKFLOW.md` compiler-context procedure and TH10's ECL subroutine
entry investigation in `docs/KNOWLEDGE_BASE.md` are useful methodological
references. Their VC7.1 offsets and thresholds do not apply to TH16's v141 C2.

For a stubborn difference, keep the full carrier and ordinary build inputs,
then use a private control that hides one real callee definition or observes
C2 pass entry/return. Trace the competing live ranges through allocation and
scheduling; an early source load need not survive to the emitted instruction.
Confirm that a read-only debugger link reproduces the ordinary complete owner
before relying on the trace. Diagnostic compiler modifications and alternate
visibility controls are not acceptance evidence.

Use `scripts/build.py` without `--clean`, then repeat `audit-reference.py
--address ... --json .analysis/...json` for the affected complete owners.
Diagnostic disassembly can explain a difference but cannot relax extent,
relocation, EH or switch requirements. Keep useful unsuccessful experiments
under ignored evidence and retain only justified source changes.

Record the result and next unresolved question in `docs/NEXT_AGENT.md`.
Checkpoint coherent changes with `gpt-6.1-sol: ...` commit messages. Push only
when requested. Refresh broad ledgers at a justified milestone; routine focused
iterations do not require a full audit or cold replay.
