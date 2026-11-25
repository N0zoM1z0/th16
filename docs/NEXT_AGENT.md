# TH16 reconstruction: next-agent handoff

**Updated 2026-11-25.** Read AGENTS.md first. This is the active handoff;
the dated 2026-11-19 and 2026-11-21 notes are historical.

## Active reconstruction (2026-11-25)

`LaserCurveNode::step_back` (`0x438370`) now passes its complete local strict
comparison: 986 / 986 bytes, 248 instructions and 14 independently bound linked
fields. The final report is
`.analysis/step-back-compiler/curve-step-back-final-strict.json`.
Factory acceptance remains `not-submitted`; the shared snapshot is inventory-only.

The retained natural source uses scalar planar coordinates, an explicit used Z
sum, a movement-speed accumulator and `D3DXVec3Scale` in the straight branch.
Read-only compiler traces explain both the square-register order and the last
multiply form. A zero-offset memory canonicalization key retains only three
bits of its base symbol ordinal; changing the real component path crosses its
wrap at `0x108`. The final compiler replay reproduces the complete ordinary
owner. See [the compiler investigation](knowledge/curve-step-back-compiler-trace.md)
for the derivation, failed controls and private evidence. Preserve the separate
scheduler counterfactual's diagnostic label, `.analysis/step-back-compiler/`
and the current build graph.

Continue only `LaserCurveInf::on_tick` (`0x4377d0`) until its complete owner
is resolved. The retained speedup branch now uses `again += step_ex_speedup()`
after explicitly clearing `again`. Its complete local strict comparison is
1301 / 1305 bytes, with all 30 linked fields bound. Only the 192/448 boundary
registers differ, at offsets 791, 799, 915 and 941. The focused checkpoint
report is `.analysis/curve-tick-compiler/checkpoint-strict.json`.

The call-register fix follows a measured non-local cause: the accumulator has
an EAX preference window of tuples 37–47. Compound accumulation introduces
three intermediate tuples, moving the later call target from 44–46
to 47–49. It can then use EAX without an interior preference overlap, and no
native instructions are added. Read
[the curve-tick compiler note](knowledge/curve-tick-compiler-trace.md) before
further edits. It also corrects misleading unwind-derived GDB return captures;
use explicit call sites. Keep `.analysis/curve-tick-compiler/`.

The remaining investigation now distinguishes allocation priority from tuple
order. A private compiler-state control raising only 448's priority from 239
to 240 repairs all four bytes while retaining the 30 linked fields. Swapping
the two preload tuples instead also swaps their machine load order and fails.
Neither control is a source reconstruction result. Both complete replays and
their separate diagnostic images/reports are retained under
`.analysis/curve-tick-compiler/`.

`LoConvertFPConstToGlobal` materializes 192 before 448; the actual caller
`AvoidAirlocks+0x25c` later inserts their preloads. NColor indexes them in tuple
order and both priorities are 239. Continue from that chain: find a natural
priority or scheduling distinction that retains the target load and comparison
order. A pool-order swap alone is insufficient. Trace the benefit and lifetime
cost terms that produce 239 in `NColPrioritizeCandidates`. The full vertical
predicate control exchanges the registers but materializes AL and grows to
1315 bytes. A used Float2 bounds object and
reversing the last comparison's operands were byte-neutral. Reversed lexical
block layout regressed. All failed source controls were restored.

The fresh verification after restoration is
`.analysis/curve-tick-compiler/priority-investigation-checkpoint-strict.json`:
curve tick remains 1301 / 1305 and reverse step remains 986 / 986. Preserve
the retained source and build graph. Do not push unless the user asks.

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

Focused strict results (both curve owners are current; the enemy rows require
a focused refresh before further work):

| Owner | Local strict result | Remaining difference |
| --- | --- | --- |
| EnemyData::ecl_run_over_300 (0x41dcb0) | incomplete | Two linked fields lack independent symbol/addend bindings |
| EnemyData::step_interpolators (0x41bb50) | mismatch | 24 bytes differ; frame size and several stack slots differ |
| LaserCurveInf::on_tick (0x4377d0) | mismatch | 4 bytes differ at offsets 791, 799, 915 and 941 |
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

2. **Curve laser — LaserCurveInf::on_tick.** Its earlier normalized
   instruction similarity was 1.0000. Its strict audit now has four differing
   bytes, as described in the active investigation above. The earlier positive-bounds
   rewrite regressed and was reverted. `LaserCurveNode::step_back` has since
   closed its local strict comparison.

3. **Enemy interpolation — EnemyData::step_interpolators (0x41bb50).**
   It is at 0.9976 normalized similarity but still has a 24-byte strict
   mismatch. The prologue uses sub esp, 0x48 instead of target
   sub esp, 0x38; multiple temporary stack slots also differ. Avoid
   broad helper extraction until the stack layout is understood.

4. **Large interpreters and laser owners.** AnmVm::run is 0.9514,
   EclRunContext::ecl_run 0.9042, LaserLineInf::run_ex 0.9159,
   LaserLineInf::on_tick 0.9408 and LaserCurveInf::run_ex 0.9698.
   Work on complete owners and preserve call order, register lifetimes and
   branch layout through ordinary C++.

5. **Radial interpolation.** InterpFloat2::step_radial_dist is 0.9175
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
