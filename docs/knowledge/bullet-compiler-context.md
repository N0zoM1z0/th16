# Bullet compiler context

Investigated 2026-11-28 with the maintained v141 `/GL` graph. Private evidence
is under `.analysis/bullet-compiler/`. The restored-source focused report
`restored-tu-strict.json` compares all 40 annotated function owners in
`src/BulletManager.cpp`: 30 pass locally, seven have incomplete extents and
three mismatch. These results agree with the preceding ledger. Factory
acceptance is unchanged.

## Alignment belongs to a call chain

The original `BulletManager::on_tick_body` (`0x412860`) begins with
`push ebp; mov ebp, esp; and esp, -8`. Its original `Bullet::on_tick` callee
(`0x411e70`) has an ordinary EBP frame without that realignment. The current
candidate instead realigns `Bullet::on_tick`, leaving the manager without an
EBP frame. Both complete owners remain incomplete. Treat these two prologue
differences together before trying to repair the manager in isolation.

The same diagnostic scan finds the opposite mismatch in the menu chain:
`TitleInf::on_tick` realigns only in the candidate, while several of its menu
callees have different alignment forms. `alignment-callgraph.txt` records the
scan using current MAP addresses, rather than stale candidate addresses from
the historical audit. This is a routing aid, not an ownership comparison.

## Constant loading and callee visibility

`Bullet::step_ex_12` (`0x415d80`) still compares 515 / 519 bytes locally.
The only differing instructions load 192 into XMM4 and 448 into XMM2 in
opposite order. The complete read-only C2 replay in `baseline-phases.jsonl`
exits normally and reproduces all 40 ordinary bullet owners byte for byte;
`baseline-debug-control.json` records the hashes. The replay image and logs
are retained with the `phase-baseline-` prefix.

After global register allocation, the 448 constant load already precedes the
192 load in the tuple stream. Both move into the entry sequence during
PreEncode; the trace narrows the next investigation to the load ranges and
their scheduling, rather than just lexical constant declarations.

The `sound-boundary-*` control compiles the genuine SoundManager definition
without `/GL`, holding the bullet source fixed. `step_ex_12` grows to 525
code bytes because the sound call now passes literal zero and supplies ECX
for `this`. Its early constant-load order is unchanged. The normalized
instruction streams of `step_ex_17` and the manager tick body are unchanged.
This rejects that callee boundary as the explanation for this load-order
pair; it is not a replacement production recipe.

## Recovering alignment with real iterator setup

Expanding the manager's iterator initialization, iterator advance and timer
tick reproduces the original alignment placement in both functions. The
complete TU report is `manager-expanded-strict.json`; all 30 preceding local
passes survive, while both active owners remain incomplete.

A smaller control expands only `iter_first` into its three actual list-state
operations. That removes a weight-1 helper edge, reducing the competing total
from 16 to 15. The predicted ratio is exactly `15 / 5 = 3`, which the decision
accepts. The ordinary build confirms both target prologue forms without
changing Bullet tick's source, adding stack objects or altering compiler flags.
`manager-begin-strict.json` compares all 40 owners. The manager contribution
is now 475 bytes against 502; Bullet tick is 1,568 against 1,592. Both still
need complete-owner reconstruction, including the manager's timer constant
lifetimes and Bullet tick's movement/data layout.

The retained source also uses the existing `tick_nested` variant for the
state timer. It recovers the target's loop-invariant 1.0f load and reload
after Bullet tick, bringing the complete manager to 498/502 bytes.
`manager-begin-nested-strict.json` retains the same 30 local passes across all
40 owners. The remaining timer uses speed/1.0f/1.01f in XMM0/XMM1/XMM2 rather
than XMM1/XMM2/XMM0, and adds `current_f` through a memory operand instead of
loading it first. Trace those actual ranges and operand lowering next. The
four-byte extent gap does not mean that only four encoded bytes differ.

This isolates a real cross-function effect of a reconstructed helper
boundary. The `/INCLUDE` difference recorded in the call graph was a useful
lead, but the successful control does not need to change entry rooting or
noinline policy.

## Rejected source controls

Expanding only the horizontal boundary helper in `step_ex_12` produces a
506-byte owner and changes register allocation throughout the body. Staging
`step_ex_17`'s destination in a real `goal` local repairs part of its completed
movement branch but changes the timer tail and fails the full extent check.
Splitting that vector assignment into components introduces stack traffic.
All three controls were restored; their source snapshots, build logs and
focused reports remain under `.analysis/20261128-bullet-*`.

The investigation follows TH09's full-carrier/callee-visibility controls and
TH10's read-only allocation/scheduling traces. Compiler offsets below are
specific to TH16's pinned C2, not their VC7.1 toolchain.

## Reading C2 alignment decisions

The relevant whole-program routines are `CgComputeAccumWeight` at RVA
`0x21fa1f`, `CgNewDoubleAlignDecision` at `0x21fb1e`,
`CgHoistForceAlign` at `0x21f8df` and `CgFinalDoubleAlignDecision` at
`0x21fe00`. The call-graph node array, alignment-record pointer array and node
count live at RVAs `0x5d7ebc`, `0x5d7ec0` and `0x5d7ec4` respectively.
Node +`0xbe` is the alignment-record index; node +`0xae` contains decision
flags. These fields are unaligned DWORDs in this compiler.

`CgDoubleAlignCollectInfo` (`0xf6518`) returns its local weight in EAX.
Inspecting the alignment record immediately on return is too early to see
the caller commit that result. A trace that interrupts every collection
also exceeded the existing launcher's 240-second limit before reaching the
whole-program decisions. Its partial events and terminal logs are preserved
as `alignment-baseline.jsonl` and `collect-timeout-*`. Observe the global
stage boundaries instead; they retain the complete call-graph context with
far fewer debugger stops.

`alignment-stages.jsonl` completes that read-only control. It again exits
normally and reproduces all 40 ordinary owners; hashes are in
`alignment-debug-control.json`. After accumulation, the Bullet tick and manager
records are `[0, 30742138, 0, 0]` and `[0, 153783364, 0, 0]`. The new-decision
pass gives Bullet tick node flags `0xc00` and record flag `4`, while leaving
the manager flags zero. Hoisting then records benefit 1 for Bullet tick and 5
for the manager, marking their connecting edge with `0x40`. Final selection
leaves the same alignment placement.

The manager's other call-graph edges have weights 5 for timer tick, 5 for
collision checking, 1 for `iter_first` and 5 for `iter_advance`. These helper
edges participate before the later native inlining. Their total 16 is compared
with the marked Bullet tick edge's weight 5. The final decision at RVA
`0x21fff8` divides the two totals and compares against the double `3.0` at
RVA `0x18d18`; `16 / 5` exceeds that limit. This explains why adding a local
frame declaration is the wrong first experiment. A natural expansion of the
real iterator operations can test the actual call-graph cost instead.
