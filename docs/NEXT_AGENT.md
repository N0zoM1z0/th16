# TH16 reconstruction: next-agent handoff

**Updated 2026-11-26.** Read AGENTS.md first. This is the active handoff;
the dated 2026-11-19 and 2026-11-21 notes are historical.

## Active reconstruction (2026-11-26)

Continue only `LaserLineInf::run_ex` at `0x431fe0`. Its reviewed target owns
1,588 bytes: 1,550 code, two alignment bytes, five jump entries and a 16-byte
selector map. The retained ordinary source owns 1,592 bytes and is incomplete.
The remaining code-alignment difference is the common loop/return placement.
Read [the active compiler investigation](knowledge/line-run-ex-compiler-trace.md)
and preserve `.analysis/line-run-ex-compiler/` and the incremental build graph.

The retained source is commit `4e7e4b0`, also saved privately as
`Laser.cpp.get-point-x-repair-checkpoint`. Restore failed probes from that
checkpoint, never from the older corrected-coordinate or manual-mask sources.
Keep the paired SHOOT cursor advance and typed BLEND view. Qualified
`LaserLineInf::get_point` in SHOOT repairs X input ordering through ordinary
inlining; its read-only compiler replay reproduces every ordinary owner byte.
Shooter X remains a kind-2 field. The inlined `_v` formal makes the memory
input cheaper than that field; Y retains the opposite order.

The latest completed nine-owner checkpoint is
`.analysis/line-run-ex-compiler/selector-ownership-restored-strict.json`:
seven owners pass; Line EX and Line on_tick remain incomplete. The four closed
reconstruction owners are enemy interpolation (1,692 bytes), curve tick
(1,305), curve reverse-step (986) and curve EX (1,548). Their compiler notes
and ignored evidence remain under the matching knowledge/evidence names.
Line get_point (84), the polar helper (32) and Timer set_value (68) also pass
as context. Factory acceptance is not-submitted; the shared accepted snapshot
is inventory-only and has no Oracle results.

The proven layout chain is now:

- SwGenSwitch constructs the comparison tree in RdrReadProc before Initial.
  Late FgLowerSwitches and FgSwitchTailDup do not move the common advance.
- The first threaded traversal reaches the common INC through WAIT. Loop
  recognition duplicates the bound test; later CodeMotion joins it to the INC.
- Nine observed attempts to move the common block are rejected because WAIT's
  timer store still falls through into it. A diagnostic WAIT-preserving JMP at
  CodeMotion enables the target layout. The earlier composed intervention has
  zero differing bytes across the complete bound 1,588-byte owner, but uses a
  modified compiler and grants no source result.
- Reversing the first WAIT/default traversal order alone does not survive flow
  cleanup. FgFlowOpts removes label 100085 and coalesces it with 213780. Follow
  the increment through label replacement, rather than following one ID forever.

Failed source controls are tabulated in the compiler note. In particular,
lexical placement, explicit shared advance, the effective noinline policy,
fresh-index guards and unsigned WAIT case casts do not repair this layout.
The separate SPEEDUP increment is compared with other INC tails, but the
observed one-instruction matches have cost 11 against threshold 20 and are not
merged. Forced command-step helpers regress X; ordinary inline leaves a call.
Tail-recursive forms lose the required ESP alignment. Do not repeat these
controls without a different, evidenced compiler mechanism.

The Timer boundary experiment preserves the same exact 68-byte setter but
changes Line EX substantially. The completed two-by-two control uses both
retained/shared-advance and separate-SPEEDUP sources: ordinary LTCG gives
1,592/1,596 bytes; private COFF Timer substitution gives the same 1,636-byte
body for both. Preserve `timer-boundary-*`; the formal recipe is unchanged.

The current private investigation targets C2 state-machine preparation.
`state-machine-switch-control-*` and `selector-only-state-machine-control-*`
complete normally and reproduce their ordinary owners. The candidate switch
uses an unnamed temporary; LgoTupIsCandidateSwitch, potential-state-machine
and prepare all return zero. Naming a selector local alone is fully byte-neutral;
using it in the zero guard also gives 1,600 bytes without preserving the name.
The paired name-record intervention is complete: one metadata write changes
candidacy/potential to one and finds the common INC, but applicability and
preparation remain zero. The full ordinary owner is unchanged. Preserve
`state-machine-name-*`; naming alone is ruled out and establishes no source
result. The source controls are restored to the retained checkpoint.

Keep coherent checkpoints local and do not push unless asked.

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
