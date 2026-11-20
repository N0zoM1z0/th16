# TH16 reconstruction: next-agent handoff

**Verified 2026-11-20; source checkpoint `b814004`.** Follow
[AGENTS.md](../AGENTS.md). Use natural C/C++, incremental compilation and
affected complete-owner comparisons, not ASM or padding. Treat every dirty
file as intentional work to inspect before editing; `git status` is more
authoritative than a dated note. Do not push unless requested.

The preceding long investigation is preserved in the
[2026-11-19 handoff archive](HANDOFF_20261119.md). Its commit IDs and failed
experiments remain useful, but its "latest" tables and branch statements are
historical. This file is the short operational entry point.

## Checkpoint and verification boundary

- Latest *code* commit at handoff preparation: `b814004`
  (`gpt-web: restore ECL timed-position finish path`). The preceding commits
  include `874e939` (ANM randomized radius), `7ec3361` (follow-camera Z),
  `b0f537e` (movement scratch), `faa61a3` (snapshot restore order),
  `e013bb2` (ECL scratch reuse), `310ea94` (ANM corner scratch),
  `ed1bd98` (ECL Bezier finish) and `aad0d32` (enemy creation scope).
  Use `git log` for the authoritative complete sequence; documentation and
  archival commits may have landed after this source checkpoint.
- The worktree was clean when the 2026-11-20 documentation pass began.
  Reconfirm the live status after any cleanup. Keep ignored build and
  evidence files, except individually verified historical duplicates handled
  under [ARTIFACTS.md](ARTIFACTS.md).
- The latest checked **incremental** `scripts/build.py` produced
  `build/reference-candidate/th16.exe` with **1,166 annotated functions**.
  Keep `build/reference-candidate/` for incremental work.
- `.analysis/reference-audit.json` and `resources/progress.svg` describe an
  old **2026-11-15** local audit: **1,033 exact / 51 mismatch / 131 incomplete**
  out of **1,215 historical units**. The current incremental candidate
  passed **1,032 exact / 44 mismatch / 139 incomplete** in a separate local
  audit at `.analysis/oracle-acceptance-current.json`. Eleven annotations
  gained local exactness and twelve lost it. The frontier also detects six
  regressions in previously mismatching owners. Its incomplete entries now
  hash the original extents from the historical boundary inventory. The
  historical report and match ledgers are retained for comparison.
- Two previously reviewed proofs fail on the current candidate.
  `Gui::start_dialogue` (`0x429ff0`) differs in its GS/EH cleanup aggregate.
  `enemy_ecl_sincosmul` (`0x426260`) has a 73-byte candidate PDB contribution
  against the reviewed 32-byte target extent. Repair these scopes before
  treating their historical results as current. The upper ECL owner
  (`0x41dcb0`) has three unresolved linked fields in the current report.
- Commit `6eb8bd5` records three ANM matches from existing source. A cold
  build confirmed `insert_in_world_list_back` (`0x46e7d0`, 177 bytes),
  `insert_in_ui_list_back` (`0x46e940`, 177 bytes), and
  `restore_snapshot` (`0x46f8f0`, 128 bytes).
- The isolated Factory v141 pilot accepted `restore_snapshot` as
  `codegen_exact` after a clean build and comparison of all 128 bytes and
  11 linked fields. Its job is `job:2f8b4061e97642dda9c3411794203fe5`.
  The dedicated worktree keeps the pilot config, reports, and live fact
  query under `.analysis/factory-replay-th16/.analysis/`. The
  `th16-linked-pe-replay` branch in Factory contains the driver and policy.
  The shared Web service still reports inventory-only TH16. Its existing
  receipts bind a different runner fingerprint.
- Commit `2e6d711` makes single-unit replay check stored relocation targets
  against the audit's independent bindings. A forged target in
  `BulletManager::cancel_radius` previously hid four differing bytes. The
  current replay rejects that binding, missing relocation fields, truncated
  owners, and a foreign function symbol.
- Commit `133ed62` records eight more existing candidates after focused
  audit and single-unit replay. See `.analysis/oracle-follow-up-focused.json`
  for the 3,202 compared bytes and `.analysis/oracle-follow-up/full-final.json`
  for the full audit. All 1,215 per-function results agree with the previous
  full audit.
- A second isolated Factory job accepted
  `LaserCurveInf::check_graze_or_kill` (`0x437cf0`) with the new binding
  check. Job `job:527a89f3b52540d69e816535c8de3482` compared all 494 bytes
  and 13 linked fields. Its live result is saved in
  `.analysis/factory-replay-th16-follow-up/.analysis/accepted-facts.json`.
  The fact query uses the worker's environment. A different shell launch
  initially returned a stale environment verdict.
- Commit `743da3f` makes the frontier compare replayed bytes, including
  residual differences inside relocation fields. The historical audit
  supplied the encodings for 14 corrected baselines. The current check
  still reports 18 regressions and now includes the four affected field
  bytes in `BulletManager::clear_all`.
- The second pilot profile now also accepts `InterpFloat3::step`
  (`0x406e10`, 906 bytes, six linked fields). Job
  `job:151c70756a3547b9938c18ca86afb258` completed a cold build and exact
  replay. The live fact query returns this receipt and the earlier laser
  receipt together. All exact results in the current full audit have local
  match entries.
- Commit `5a2a8bf` requires the original size and hash to agree before an
  exact result clears a frontier entry. The check also verifies that each
  exact or mismatch verdict agrees with the replayed bytes. The full
  current report passes this consistency check and retains the 18 known
  frontier regressions.
- The follow-up Factory profile also accepted
  `ecl_ext_damage_anm_hurtbox` (`0x425410`, 285 bytes, ten linked fields)
  and both `step_ex_angle` owners (`0x432c20` and `0x4392c0`, 412 bytes and
  seven linked fields each). It accepted `sht_on_hit_burst_rising`
  (`0x446e20`, 349 bytes, eight linked fields) as well. Each used its own
  cold build. The accepted-facts query returns six receipts for source
  checkpoint `133ed62`.
- Use `scripts/check-frontier.py --report .analysis/oracle-follow-up/full-final.json`
  to check the separately saved audit. Full checks require every current
  annotation. A focused report can check the explicitly selected frontier
  addresses it covers.

## Latest focused normalized owner comparisons

These are from the current committed source and reference candidate, not
Oracle receipts. Target/candidate sizes are in bytes; instruction counts come
from `.analysis/measure-leaf.py`.

| Owner (target VA) | Target / candidate bytes | Target / candidate instructions | Local ratio |
| --- | ---: | ---: | ---: |
| `EnemyData::ecl_run_over_300` (`0x41dcb0`) | 21,408 / 21,472 | 4,562 / 5,465 | **0.8655** |
| `AnmVm::run` (`0x45f980`) | 14,177 / 14,192 | 3,837 / 3,818 | **0.9531** |
| `EclRunContext::ecl_run` (`0x472030`) | 7,046 / 6,944 | 1,807 / 1,777 | **0.9180** |
| `LaserLineInf::run_ex` (`0x431fe0`) | 1,588 / 1,600 | 344 / 336 | **0.9088** |
| `LaserCurveInf::run_ex` (`0x438cb0`) | 1,548 / 1,568 | 360 / 365 | **0.9683** |
| `LaserLineInf::on_tick` (`0x432f40`) | 1,473 / 1,488 | 356 / 355 | **0.9058** |
| `LaserCurveInf::on_tick` (`0x4377d0`) | 1,305 / 1,312 | 332 / 330 | **0.9758** |
| `InterpFloat2::step_radial_dist` (`0x425570`) | 757 / 768 | 207 / 207 | **0.9565** |
| `EnemyData::step_interpolators` (`0x41bb50`) | 1,692 / 1,696 | 421 / 421 | **0.9976** |
| `AnmManager::restore_snapshot` (`0x46f8f0`) | 128 / 128 | 46 / 46 | **1.0000** |
| `AnmVm::load_from` (`0x46ffb0`) | 650 / 656 | 135 / 135 | **0.9778** |

**Do not substitute an earlier session's 0.9134 or 0.9274 ECL figure for
the currently measured 0.8655.** Historical candidates, local comparison
settings and inline ownership differ. Re-evaluate the *complete* affected
function, code size, relocation/data scope and PDB ownership before
interpreting an apparent improvement. Even a ratio of 1.0000 is not proof
of a complete byte/relocation-exact owner.

## Source priorities for the next agent

1. **Large ECL boss:** `src/EnemyEcl.cpp`, `EnemyData::ecl_run_over_300`
   (`0x41dcb0`). Inspect its `MOVE_POS_TIME`, `MOVE_CURVE`, `MOVE_BEZIER`,
   and laser construction paths (402/403/411/413). Commit `b814004`
   restored a separate time-position finalization path; keep that semantic
   change and test the complete owner as well as the local case spans.
   The candidate still has a different dispatcher stack alignment/frame.
   Avoid reviving older register/union experiments without new evidence.
2. **ANM dispatcher:** `src/AnmVmRun.cpp`, `AnmVm::run`
   (`0x45f980`). Investigate world-freeze branch layout, IMUL/ISET_ADD
   register lifetimes, randomized circle radius and follow-camera code.
   Recent versions of temporary-variable, `volatile` and goto experiments
   generally did not improve the complete owner. `FSET_RAND` advances
   `instr_offset` in its own dispatch block.
3. **Laser and ECL interpreters:** `LaserLineInf::on_tick` has a low local
   ratio; `LaserCurveInf::on_tick` is closer. `EclRunContext::ecl_run`
   still differs in arithmetic shared exits and opcode code placement.
   Preserve natural data flow, rather than forcing machine-code bytes.
4. **Leaf work:** `InterpFloat2::step_radial_dist` still has reversed
   float-add operands and a Bezier register schedule difference;
   `AnmVm::load_from` differs at the serialize callback's `read` stack
   slot. Both were tried again: alternate `tick_nested`, split vector
   component writes, preinitialized `read`, and a separate serialized-data
   pointer all regressed. Their committed versions were restored.

## Practical commands and preserved evidence

```sh
git status --short --branch
git log -10 --oneline
scripts/repo-python scripts/build.py  # incremental, only after source edits
scripts/repo-python scripts/audit-reference.py --address 0x46f8f0 --json .analysis/oracle-focused.json
scripts/repo-python .analysis/measure-leaf.py 0x41dcb0 ecl_run_over_300@EnemyData
scripts/repo-python .analysis/measure-leaf.py 0x45f980 run@AnmVm
scripts/repo-python .analysis/measure-leaf.py 0x472030 ecl_run@EclRunContext
scripts/repo-python .analysis/claude-tools/cases.py 0x41dcb0 101,103,125,126,134,135,138,139
scripts/repo-python .analysis/claude-tools/cases.py 0x41dcb0 402,403,411,413
scripts/repo-python .analysis/claude-tools/cases.py 0x45f980 107,113,132
scripts/repo-python scripts/evidence-archive.py list
```

The ECL case utility indexes by **opcode minus 300**; the ANM utility
indexes by **opcode plus 1**. These do not delimit complete owner scopes.
Keep `resources/th16.exe`, `.tools/`, `.venv/`, `ghidra-project/`,
`build/reference-candidate/`, `.analysis/reference-audit.json`,
`.analysis/claude-tools/` and the pinned `_reference/` checkout.
Historical evidence may be restored by `scripts/evidence-archive.py`
using a checksummed `.analysis/cleanup-handoff-*.json` index.
The 2026-11-20 cleanup archived 35 redundant historical PDBs and 28
redundant audit reports, preserving a content-identical expanded peer per
group. The 63-record `cleanup-handoff-20261120.json` restored about
**273.39 MiB of allocated storage**; historical PDBs may need restoration
before using their sibling build receipts. The active candidate remains
unchanged.

The old [handoff archive](HANDOFF_20261119.md) retains detailed chronology,
rejected trial source paths and deeper ownership notes. Also consult
[ARTIFACTS.md](ARTIFACTS.md) before touching any ignored files and
[REFERENCE_IMPORT.md](REFERENCE_IMPORT.md) for strict-Oracle boundaries.
