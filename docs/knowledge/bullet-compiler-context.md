# Bullet compiler context

Investigated 2026-11-28 with the maintained v141 `/GL` graph. Private evidence
is under `.analysis/bullet-compiler/`. The restored-source focused report
`restored-tu-strict.json` compares all 40 annotated function owners in
`src/BulletManager.cpp`: 30 pass locally, seven have incomplete extents and
three mismatch. These results agree with the preceding ledger. Factory
acceptance is unchanged.

The completed manager timer passes all 502 bytes and nine linked fields;
the wrap update now passes all 519 bytes and eight linked fields. The move
update also passes all 597 bytes and 12 linked fields after restoring its
shared scalar/vector state layout. Clear-all now passes all 500 bytes and
11 linked fields; `clear-all-final-strict.json` retains 34 local passes and
six incomplete owners across the Bullet TU. The earlier
`step17-final-consumers-strict.json` covers
all 125 annotated owners in BulletManager, Laser and LaserLine: 102 local
passes, 20 incomplete and three mismatches. Every preceding local pass holds.
`step12-explicit-returns-strict.json` compares all 40 bullet owners: 32 local
passes, six incomplete and two mismatches. The earlier
`manager-final-timer-consumers.json` also keeps both
EnemyManager update and the out-of-line timer increment exact. The earlier
controls below explain the recovered alignment and source lifetimes.

## Alignment belongs to a call chain

The original `BulletManager::on_tick_body` (`0x412860`) begins with
`push ebp; mov ebp, esp; and esp, -8`. Its original `Bullet::on_tick` callee
(`0x411e70`) has an ordinary EBP frame without that realignment. The starting
candidate instead realigned `Bullet::on_tick`, leaving the manager without an
EBP frame. Both owners initially had incomplete extents. Treat these two
prologue differences together before trying to repair the manager in isolation.

The same diagnostic scan finds the opposite mismatch in the menu chain:
`TitleInf::on_tick` realigns only in the candidate, while several of its menu
callees have different alignment forms. `alignment-callgraph.txt` records the
scan using current MAP addresses, rather than stale candidate addresses from
the historical audit. This is a routing aid, not an ownership comparison.

## Constant loading and callee visibility

`Bullet::step_ex_12` (`0x415d80`) initially compares 515 / 519 bytes locally.
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

The later scheduler controls isolate the source of that ordering. In the
first DAG, both loads have priority `0x8c00` at node +`0x28`, with only the
graph entry and exit as dependencies. The ready-list insertion at C2 RVA
`0x21ae36` breaks equal priorities by the ascending WORD ordinal at +`0x34`.
Static priorities are computed at `Schedule +0x1d7`, before the graph-entry
sample at `+0x1e2`.

| Constant | Destination | Starting ordinal | Explicit-return ordinal |
| --- | --- | ---: | ---: |
| 192 | XMM4 | 20 | 19 |
| 448 | XMM2 | 19 | 21 |

Returning `bool` from the predicate and using an actual `Float2` boundary
value are byte-neutral controls. Their focused reports are
`step12-bool-strict.json` and `step12-bounds-strict.json`. The retained
`outside_range` instead returns one immediately for either boundary test,
then zero for the inside case. This preserves the predicate's behavior but
changes the constant loads' input order before scheduling. Both priorities
remain `0x8c00`, so the existing tie-breaker now selects the target order.

Use graph-entry records from `step12-priority.jsonl` and
`step12-explicit-returns-priority.jsonl` for this comparison. The earlier
`FinishBreakpoint` sampler observed recycled graph storage at delayed
returns. The replacement binds return points to a thread and exact stack
position. Both read-only controls exit normally and reproduce every ordinary
bullet owner; their corresponding `*-control.json` records bind the inputs.
The ordinary final comparison passes the complete 519-byte owner and all
eight linked fields. The original manager pass and every other preceding
local pass survive.

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

The next checkpoint used the existing `tick_nested` variant for the state
timer. It recovered the target's loop-invariant 1.0f load and reload after
Bullet tick, bringing the complete manager to 498/502 bytes.
`manager-begin-nested-strict.json` retains the same 30 local passes across all
40 owners. The timer then used speed/1.0f/1.01f in XMM0/XMM1/XMM2 rather
than XMM1/XMM2/XMM0, and added `current_f` through a memory operand instead of
loading it first. Those ranges and operand lowering were the next issue.
The four-byte extent gap did not mean that only four encoded bytes differed.

This isolates a real cross-function effect of a reconstructed helper
boundary. The `/INCLUDE` difference recorded in the call graph was a useful
lead, but the successful control does not need to change entry rooting or
noinline policy.

## Closing the timer with a real field reference

The read-only `manager-timer-fast.jsonl` follows the complete 498-byte
checkpoint through canonicalization, lowering and allocation. It exits
normally and reproduces every ordinary bullet owner byte for byte; see
`manager-timer-debug-control.json` and the `manager-timer-*` replay image/logs.

The early scaled add reads through named `_speed`, ordinal 7. In the second
canonicalization, the speed value is temporary 648, with sort key `0x1a200`.
The frame's address is temporary 652, whose zero-offset memory key is
`0x10008`. Descending order puts the speed value first. The resulting scaled
add uses the speed register as its destination and folds the frame read into
its memory operand. These keys describe the 498-byte checkpoint, not the
final source.

Saving the old float value before selecting the branch restores the desired
speed and 1.0f registers, but emits an early frame load and moves the 1.01f
threshold into XMM3. Its complete owner is 494 bytes and is rejected in
`manager-early-frame-strict.json`. A value snapshot and a field reference do
not have the same lifetime.

The retained code instead binds the actual `current_f` field by reference,
computes `next_frame` in each branch and writes it back once. This preserves
the field identity without reading the value before the comparison. The
first reference control recovers every float instruction and the 502-byte
extent, but reads the integer counter before `speed()` normalizes the index;
that changes the EAX/ECX allocation. `manager-frame-reference-strict.json`
records that complete mismatch at 465/502 bytes.

Declaring the used integer counter with the other timer locals, then reading
it after `speed()`, restores the original read schedule and register roles.
The ordinary complete-owner comparison now passes 502/502 bytes, all 119
instructions and all nine independently bound linked fields. Validation uses
the normal incremental build and complete linked-owner scope.

For future allocation traces, RVA `0x79391` is
`NColDeterminePhysregAvail`, an availability query. Its zero returns in this
control do not identify a final physical register. The canonical operands,
pass snapshots and ordinary native instructions supply the relevant evidence.
Filter small tuple reads before expanding trees; reading whole pages at every
generic hash breakpoint made the earlier private sampler unnecessarily slow.

## Closing movement through the shared state layout

`Bullet::step_ex_17` (`0x415f90`) begins this control at 541/597 bytes. Its
timer tail already matches. The completed-movement branch instead writes XY
before reading goal Z, clears the active flag too late, and writes Z before
the speed/angle loads. Moving only the flag clear earlier gives 530/597.
The by-value goal control recovers the early goal reads but changes the
timer tail, growing the complete owner to 612 bytes.

The controlled baseline scheduler trace is `step17-baseline-schedule.jsonl`.
It exits normally and reproduces all 40 ordinary bullet owners;
`step17-baseline-schedule-control.json` binds that check. In graph 1, the
XY store has a `0x20` edge to the goal-Z load. The Z store also has a `0x20`
edge to the saved-speed load. These dependencies prevent the target order
regardless of the ready-list priorities.

The old state represents both data shapes through `floats[8]`, with casts
for its final three slots. Its Bullet, Laser and LaserLine consumers use
those slots as a vector. Restoring a real `D3DXVECTOR3` member at `+0x28`
recovers the goal-read/flag/XY sequence and retains the existing timer tail:
568/597 bytes. A state reference instead grows the owner to 612 bytes;
moving the speed assignment first gives 547/597. Both are rejected.

The retained state also provides a move-specific scalar view of the five
preceding float slots. `run_ex` saves the current speed to `move.speed` at
`+0x14`; `step_ex_17` restores that same field. Only this scalar is used by
MOVE in the five-slot view. The vector, integer arguments and full state
remain at `+0x28`, `+0x34` and 72 bytes respectively, checked by static
assertions. All vector consumers now use the real member.

In graph 1 of `step17-final-schedule.jsonl`, both `0x20` edges are absent.
The Z store's static priority falls from `0x2c00` to `0x1000`, allowing the
angle load (`0x9c00`) to precede it. The original source assignment order and
timer helper remain in place. This final read-only link exits normally and
reproduces all 125 ordinary consumer owners byte for byte;
`step17-final-schedule-control.json` binds the image check and build inputs.

This source passes the complete 597-byte move owner and all 12 linked fields.
`step17-final-consumers-strict.json` compares all 125 annotated owners in
the three changed consumer TUs: 102 exact, 20 incomplete, three mismatches.
The Bullet subset has 33 exact, six incomplete and one mismatch. Every
preceding local pass survives, including manager tick and wrap update.
These are local strict results; Factory acceptance remains unchanged.

Private control sources and reports use the `step17-` prefix. The intermediate
`typed-state` debugger image was retained before its ordinary comparison was
completed; use it only as provisional diagnostic evidence. The baseline and
final controls have separate image comparisons.

## Clear-all allocation and movement controls

`clear_all` (`0x416f40`) now passes all 500 bytes and 11 linked fields locally;
`Bullet::cancel` (`0x416840`) retains its 444-byte pass. The final TU report
is `clear-all-final-strict.json`: 34 local passes and six incomplete owners,
retaining every preceding pass. The controls below start from 491/500 bytes.
In `clear-all-allocation.jsonl`, the
PreEncode entry already assigns the half-step X and Y velocity loads to
XMM1 and XMM2, respectively. Their SROA values are `$T1$sroa$66$1` and
`$T1$sroa$65$1`; Z uses `$T1$sroa$431$1` in XMM3. The target instead uses
XMM2 for X and XMM1 for Y. Investigate allocation and its input lifetimes
before changing the final scheduler. This read-only link exits normally
and reproduces all 40 ordinary Bullet owners; see
`clear-all-allocation-control.json`.

`clear-all-ncolor.jsonl` follows the allocator itself. Its read-only link also
exits normally and reproduces all 40 owners; the input bindings and checks are
in `clear-all-ncolor-control.json`. `NColUpdatePhysregAvail` (`0x111850`)
records these selections, which agree with the later PreEncode operands:

| Value | Allocation priority | Register |
| --- | ---: | --- |
| Game-speed `_f$1` | 146 | XMM0 |
| X, `$T1$sroa$66$1` | 134 | XMM1 |
| Y, `$T1$sroa$65$1` | 134 | XMM2 |
| Z, `$T1$sroa$431$1` | 132 | XMM3 |

The observed X/Y comparison reaches `NColColPriorityCompare` (`0x2585b3`).
It subtracts the left lifetime's DWORD at `+0x48` from the right one's,
sorting higher priorities first. A tie returns `(left - right) / 0x5c`,
the relative lifetime-array index. X precedes Y by two records in this
control, so their equal priority still orders X first. The SROA name suffix
is not that lifetime index. Recover the value creation/coalescing context
that feeds this order; the final instruction scheduler already receives the
opposite register assignment from the target.

`clear-all-life-origin.jsonl` follows `NColInitializeSyms` (`0x23fb8f`) and
`NColCombineLifetimes` (`0x1bfd75`). Initialization assigns first-use ordinals
31 to speed, 33 to X, 35 to Y and 37 to Z. Each named component first appears
as the destination of a copy following its anonymous load (32, 34 and 36).
The subsequent combines keep the named lifetime while absorbing that load
and later arithmetic temporaries. They preserve the X/Y order. This control
also exits normally and reproduces all 40 ordinary owners; see
`clear-all-life-origin-control.json`.

Putting game speed on the left of the vector multiplication is byte-neutral
across all 40 owners (`clear-all-left-scale-strict.json`). A lexical operand
swap does not recover the missing lifetime order.

The retained expression explicitly constructs the three game-speed-scaled
velocity components, then multiplies that vector by 0.5 before adding it to
position. This preserves the intermediate vector between the two scaling
operations. Constructing a vector from components that each already include
both multiplications does not close either cancellation owner. The standalone
cancel retains its existing displacement local; the manager loop uses the
constructed scaled value. No compiler flags or allocator state are modified.

The positive `clear-all-final-origin.jsonl` trace shows that X still precedes
Y at initialization, at ordinals 32 and 34. Their allocation priorities now
differ: X is 132 and Y is 133; Z is 131. The priority comparator consequently
selects Y first, assigning XMM1 to Y, XMM2 to X and XMM3 to Z. Construction
changes the allocator's priority inputs rather than reversing the initial
X/Y order. This read-only link exits normally and reproduces all 40 ordinary
owners; see `clear-all-final-origin-control.json`. The ordinary source change
alters only clear-all's raw bytes among those 40 owners, with all extents
unchanged. The complete strict comparison passes all 11 linked fields.

The earlier pointer-filtered `clear-all-baseline-phases.jsonl` captures
frontend/lowering snapshots but misses the backend passes. Its Emit entry
still has virtual symbols. Use the separate PreEncode trace for the physical
register observation. Match the decorated function name at the pass being
observed, and bind returns to that function instance, thread and stack.

The following ordinary source controls were rejected:

| Control | Complete-owner result |
| --- | --- |
| `clear_all` calls the real `cancel` wrapper | clear-all grows to 504 bytes; cancel remains exact |
| One real cancel method with the in-place expression | clear-all stays 491/500; cancel shrinks to 436 bytes |
| One real cancel method with a one-step delta local | clear-all grows to 504 bytes; cancel remains exact |
| Scale a delta local, then halve it in place | clear-all is 504 bytes; cancel is 443 bytes |
| Assign `pos + delta` as a vector value | both cancellation owners have incomplete extents |
| Construct each component with both multiplications in a real cancel method | clear-all is 504 bytes; cancel is 440 bytes |

`Bullet::on_tick` has related movement differences. A named vector delta in
`move_full_step` is byte-neutral across all 40 Bullet owners. Using
`D3DXVec3Scale` and `D3DXVec3Add` instead grows tick from 1,568 to 1,704 bytes.
The scalar delta control captures game speed before the position stores but
still sinks each velocity calculation into its coordinate update; tick is
1,596 bytes. These controls do not recover the target's 1,592-byte owner.
The target's full step keeps three scaled velocity components live before
updating position, and its half-step cases have different partial sharing.
Preserve both data lifetimes and the complete switch when continuing.

Rejected source controls were restored. Their snapshots, build logs and
focused reports use the `clear-all-` and `tick-` prefixes under the private
evidence directory. Continue with Bullet tick's movement branches, preserving
the completed clear-all, cancel, manager, wrap and move owners.

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
