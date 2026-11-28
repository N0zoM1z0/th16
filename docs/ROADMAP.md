# Remaining reconstruction roadmap

Updated 2026-11-28. Use `config/reference-functions.csv` to find the recorded
candidate verdicts and `config/functions.csv` for the independent target
inventory. These are local comparison records; Factory acceptance remains
separate. Recheck each selected owner against the current incremental build.

## Execution order

1. **Bullet leaves and update loop.** Start with `Bullet::step_ex_12`
   (`0x415d80`): its recorded complete 519-byte comparison differs only in two
   constant-load instructions. Recover the natural expression/call shape, then
   inspect `step_ex_17` (`0x415f90`) and `clear_all` (`0x416f40`). Follow with
   `BulletManager::on_tick_body` (`0x412860`), whose stack alignment and timer
   register lifetimes remain unresolved. Compare every annotated owner in
   `src/BulletManager.cpp` after a retained change, including helper callers.
2. **Menu control flow and real local lifetimes.** Revisit
   `PauseMenu::tick_open` (`0x43f980`, two recorded SIB encoding differences),
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

Use `scripts/build.py` without `--clean`, then repeat `audit-reference.py
--address ... --json .analysis/...json` for the affected complete owners.
Diagnostic disassembly can explain a difference but cannot relax extent,
relocation, EH or switch requirements. Keep useful unsuccessful experiments
under ignored evidence and retain only justified source changes.

Record the result and next unresolved question in `docs/NEXT_AGENT.md`.
Checkpoint coherent changes with `gpt-6.1-sol: ...` commit messages. Push only
when requested. Refresh broad ledgers at a justified milestone; routine focused
iterations do not require a full audit or cold replay.
