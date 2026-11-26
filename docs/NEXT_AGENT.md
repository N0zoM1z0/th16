# TH16 reconstruction: next-agent handoff

**Updated 2026-11-26.** Read AGENTS.md first. This is the active handoff;
the dated 2026-11-19 and 2026-11-21 notes are historical.

## Active reconstruction (2026-11-26)

`LaserCurveInf::run_ex` (`0x438cb0`) now passes the complete local strict
comparison: 1548 / 1548 bytes and 29 independently bound linked fields.
The extent includes 1512 code bytes, five absolute jump entries and a
16-byte selector map. SHOOT advances the actual instruction cursor for its
paired command, giving NColor two different definitions and preventing the
full pointer from being folded into every field address. A named integer
duration then repairs conversion-tree ordering. Read
[the compiler investigation](knowledge/curve-run-ex-compiler-trace.md) and
preserve `.analysis/curve-run-ex-compiler/` and the incremental build. The
completed read-only replay reproduces the full ordinary owner, confirms the
nonzero definition comparison and records the repaired conversion keys.

The final focused report rechecks all four completed owners:
`.analysis/curve-run-ex-compiler/final-strict.json`. Enemy interpolation passes
1692 / 1692 bytes and 48 fields; curve tick passes 1305 / 1305 and 30 fields;
curve reverse-step passes 986 / 986 and 14 fields. Their evidence remains in
[the interpolation note](knowledge/enemy-interpolators-compiler-trace.md),
[the tick note](knowledge/curve-tick-compiler-trace.md) and
[the reverse-step note](knowledge/curve-step-back-compiler-trace.md).
Preserve their three compiler-evidence directories. Factory acceptance remains
not-submitted; the current shared accepted snapshot is inventory-only.

Continue only `LaserLineInf::run_ex` (`0x431fe0`). Its target extent is
1588 bytes, including 1550 code bytes, two alignment bytes, five jump entries
and 16 selector bytes. The current typed-blend candidate is 1592 bytes and
remains incomplete in the local strict audit. TAG uses the saved entry index,
SHOOT advances the same cursor, and the existing blend-mode field view
restores EDX/ECX roles and both original member INCs. Remaining code differences
are the late common loop/return block and SHOOT X input order. The focused
report `.analysis/line-run-ex-compiler/corrected-coordinate-baseline-strict.json` also
rechecks the four completed owners.

Read [the active compiler note](knowledge/line-run-ex-compiler-trace.md) and
preserve `.analysis/line-run-ex-compiler/`. A semantic-label trace proves the
first FgChangeNextToDFOEx moves the advance block from index 29 to 73/81.
Simple continuation/default/goto forms and the shared-index loop controls did
not repair it; their failed source and native controls remain. EmitFunction
entry precedes allocation, and RVA 0x78774 is NColProcessCandidate entry;
the corrected trace uses real pass returns. Continue from the typed field view,
not the earlier 1596-byte paired-cursor source or any verbose goto trial.
The additional typed-source controls are summarized in the note. Signed-switch
and size-policy controls discard the target's jump table; explicit loop-check
placement and a vector-add control are byte-neutral. A separate polar offset
grows the frame and does not repair X. The original X/Y label in earlier notes
was corrected against the actual field offsets. The native diagnostic helper
now rejects executable/report identity mismatches; use the signed replay and
preserve the quarantined wrong-build diagnostic separately.

The current compiler probe compares an unmodified replay with a diagnostic
X-input-chain swap at the actual FactCanonSort return. Its purpose is to test
whether X ordering also controls common-loop placement; a modified-compiler
image cannot establish source exactness. Preserve both controls and ordinary
build inputs. Keep coherent checkpoints local and do not push unless asked.

## Historical checkpoint (2026-11-23)

- Latest source checkpoint: de0cb82a22e2921813d893c5ea592f04de22bc14
  (gpt-web: return packed laser shot origins). A documentation-only handoff
  commit follows this source checkpoint.
- The six source commits listed below are local and have not been pushed.
- Worktree: clean after the handoff commit. Do not push unless the user asks.
- The latest incremental build completed and contains **1,166 annotated
  functions**. Keep build/reference-candidate/ and its object/dependency
  graph for incremental builds.
- The six source commits ahead of origin/main, oldest first:
  99d173a align enemy interpolated velocity stores;
  a9d6924 restore ET_ON origin and offset read order;
  cf7aa4d align curve step-back local layout;
  4af7f10 restore curve step-back local declaration order;
  a5a5bbb inline enemy interpolated velocity updates;
  de0cb82 return packed laser shot origins.

The uncommitted LaserCurveInf::on_tick positive-bounds rewrite tested during
the 2026-11-23 handoff pass was reverted. It reduced the local ratio from
1.0000 to 0.976 and made the strict owner incomplete. The committed source is
the baseline to continue from.

## Verification boundary

The current Factory accepted snapshot for th16 is inventory-only:
oracle_results is empty and the adapter reports inventory-import-only.
Historical isolated pilot jobs did accept individual owners, but those
receipts are separate from the current shared snapshot. Do not describe local
similarity, local strict reports, imported labels or historical pilot receipts
as current accepted exactness.

Focused strict results (the three curve owners and enemy interpolation are current;
the ECL row requires a focused refresh before further work):

| Owner | Local strict result | Remaining difference |
| --- | --- | --- |
| EnemyData::ecl_run_over_300 (0x41dcb0) | incomplete | Two linked fields lack independent symbol/addend bindings |
| EnemyData::step_interpolators (0x41bb50) | pass | 1692 / 1692 bytes; 48 linked fields; Factory not-submitted |
| LaserCurveInf::run_ex (0x438cb0) | pass | 1548 / 1548 bytes; 29 linked fields; Factory not-submitted |
| LaserCurveInf::on_tick (0x4377d0) | pass | 1305 / 1305 bytes; 30 linked fields; Factory not-submitted |
| LaserCurveNode::step_back (0x438370) | pass | 986 / 986 bytes; 14 linked fields; Factory not-submitted |

A strict result is only as complete as its audited owner boundary and
independent linkage bindings. The local audit does not promote Factory facts.

## Earlier focused measurements

The following predate the step-back closure and were measured with
.analysis/measure-leaf.py. Candidate map spans include alignment bytes. Ratios are normalized
instruction similarity only; byte extents and instruction counts are included
so apparent changes can be checked against the whole owner.

| Owner (target VA) | Target / candidate bytes | Target / candidate instructions | Ratio |
| --- | ---: | ---: | ---: |
| EnemyData::ecl_run_over_300 (0x41dcb0) | 21,408 / 21,584 | 4,562 / 4,833 | **0.9224** |
| AnmVm::run (0x45f980) | 14,177 / 14,192 | 3,837 / 3,825 | **0.9514** |
| EclRunContext::ecl_run (0x472030) | 7,046 / 6,976 | 1,807 / 1,701 | **0.9042** |
| LaserLineInf::run_ex (0x431fe0) | 1,588 / 1,600 | 344 / 346 | **0.9159** |
| LaserCurveInf::run_ex (0x438cb0) | 1,548 / 1,568 | 360 / 368 | **0.9698** |
| LaserLineInf::on_tick (0x432f40) | 1,473 / 1,488 | 356 / 354 | **0.9408** |
| LaserCurveInf::on_tick (0x4377d0) | 1,305 / 1,312 | 332 / 332 | **1.0000** |
| LaserCurveNode::step_back (0x438370) | 986 / 992 | 248 / 248 | **1.0000** |
| EnemyData::step_interpolators (0x41bb50) | 1,692 / 1,696 | 421 / 421 | **0.9976** |
| InterpFloat2::step_radial_dist (0x425570) | 757 / 752 | 207 / 205 | **0.9175** |

Do not compare these figures directly with the 2026-11-21 handoff's
0.9386 ECL measurement or its 0.8655 earlier build. Those figures came
from different candidate/source states. Rebuild incrementally after a source
edit and remeasure the complete owner.

## Broader backlog after the active owner

1. **Large ECL boss — EnemyData::ecl_run_over_300 (0x41dcb0).**
   Continue with natural C++ in src/EnemyEcl.cpp. The latest whole-owner
   comparison is 0.9224, but two linked fields remain unbound in the strict
   audit. Focus the relative/time movement and laser construction paths:
   opcode cases 402, 403, 411 and 413. The ECL case helper indexes by opcode
   minus 300; these case spans are diagnostics, not complete owner scopes.
   Resolve linkage and frame/stack-layout differences rather than optimizing
   only a local opcode ratio.

2. **Large interpreters and laser owners.** AnmVm::run is 0.9514,
   EclRunContext::ecl_run 0.9042, LaserLineInf::run_ex 0.9159,
   LaserLineInf::on_tick 0.9408 and LaserCurveInf::run_ex 0.9698.
   Work on complete owners and preserve call order, register lifetimes and
   branch layout through ordinary C++.

3. **Radial interpolation.** InterpFloat2::step_radial_dist is 0.9175
   (207 target instructions versus 205 candidate). The prior declaration,
   operand-order and local-result trials did not improve the whole owner;
   remeasure the complete function after each source change.

No ASM, NOP/padding or byte-shaped scaffolding is acceptable progress.
Do not run a full cold replay for routine iterations. Use the incremental
build and only the affected complete-owner comparisons; reserve broad replay
for an explicit milestone or a demonstrated cache/dependency problem.

## Commands

    git status --short --branch
    git log -10 --oneline
    scripts/repo-python scripts/build.py
    scripts/repo-python .analysis/measure-leaf.py 0x41dcb0 ecl_run_over_300@EnemyData
    scripts/repo-python .analysis/measure-leaf.py 0x45f980 run@AnmVm
    scripts/repo-python .analysis/measure-leaf.py 0x472030 ecl_run@EclRunContext
    scripts/repo-python .analysis/measure-leaf.py 0x4377d0 '?on_tick@LaserCurveInf@@UAEHXZ'
    scripts/repo-python .analysis/measure-leaf.py 0x438370 '?step_back@LaserCurveNode@@QAEXPAUD3DXVECTOR3@@PAM10MMM@Z'
    scripts/repo-python .analysis/claude-tools/cases.py 0x41dcb0 402,403,411,413
    scripts/repo-python scripts/audit-reference.py --address 0x41dcb0 --json .analysis/ecl-boss-focused.json
    scripts/repo-python scripts/evidence-archive.py list

The ANM case helper indexes by opcode plus 1. A local strict audit is not a
Factory acceptance receipt. For the target identity, shared toolchain and
evidence rules, see AGENTS.md; for private outputs and restoration, see
ARTIFACTS.md. The 2026-11-21 handoff and 2026-11-19 chronology are retained
as historical diagnostics, not current status.
