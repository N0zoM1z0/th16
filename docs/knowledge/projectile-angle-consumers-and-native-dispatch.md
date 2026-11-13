# Projectile angle consumers and native transform dispatch

Reviewed 2026-11-13 from checkpoint `5e499b5`. The retained source changes are
inside `Bullet::run_ex` at `0x00413860`, the large projectile transform dispatcher
used by Boss shooting. Evidence is in `.analysis/bullet-accel-work/`.

## Retained source changes

The acceleration handler now consumes the selected temporary angle's float
value directly into `ex_state[1].floats[1]`. The previous persistent `ZunAngle`
introduced a store to a local copy, a reload through XMM0 and a floating store
to the state. The original reads the selected object's word into EAX and stores
it directly before initializing the timer. The new source recovers that data
flow and removes those two local-memory instructions.

The turn handler now selects an angle with a conditional expression and takes
its float value once before dispatching the turn mode. Previously its negative
sentinel branch loaded the bullet angle straight into XMM1 while the other
branch read a constructed object's value. The original captures the sentinel
angle in a temporary, joins both paths through a pointer and reads the chosen
float at that join. The retained scalar consumer recovers this selection and
shared read, including reuse of the raw-angle slot for the resolved value.
The saved-angle and player-aim thresholds remain distinct.

These are partial source/data-flow repairs. The entire candidate remains
**5,500 bytes**, against the complete **5,436-byte** original owner. All three target tables, the byte remap, padding, complete code and candidate
linked fields are retained in `complete-dispatch-scopes/`, together with the
independent original layout. Earlier `run-ex-baseline/` and `angle-consumers/`
packets retain the raw owners; their raw disassembly also decodes table data
as instructions and must not be used as a complete data-aware field review. The function remains incomplete;
no exact credit or improved whole-owner matching percentage is claimed. Frame
layout, flag update operands, constant lifetimes and shared call tails still
differ. The new source uses ordinary expressions without register forcing,
padding, dead storage or comparison-rule changes.

## Initialized native execution

`native-run-ex.py` invokes the actual complete original function, the immutable
PDB-301 baseline and the final PDB-316 candidate. The existing native debugger
runner lets each image initialize its CRT before intercepting WinMain. Every
case calls the real method and its callees, then returns through the checked
stack/ABI boundary. No callee or import is replaced.

The final matrix has **560 complete calls per image**, with zero faults or
cross-image state differences. It preserves the 488 historical instruction
simulation inputs and adds 72 cases with distinct quiet/signaling NaN payloads,
infinities and signed zeros for six transform commands under x87 precision
settings 24, 53 and 64. The typed layout probe independently checks the fixture
sizes and offsets with the pinned compiler.

Each final case compares all **5,240 Bullet bytes**, both canaries, all Player
storage, all LaserManager storage, their canaries, RNG state and the pointer
and game-speed globals supplied by the fixture. Preserved integer registers,
stack cleanup, x87 control and MXCSR control are checked by the runner or the
cross-image comparison. EAX is not treated as a return value for this void
method. Floating exception status is not a claimed observation.

The cases cover command gating, serial/parallel slots, loops, transform chains,
acceleration, turn modes, movement interpolation setup, relative endpoints,
velocity, scale, sentinels and real player aiming. The laser manager is full:
paired laser commands reach the real allocation guard and decline allocation.
The final native driver does not capture their temporary parameter objects.
Their older emulator captures remain separate evidence. Native successful
laser creation, resource loading, cancellation, child-enemy creation, enabled
locks and shipped Boss programs are not proved by this matrix.

For **110 cases per image**, an independent expected result also checks every
Bullet byte. These model unchanged gates, tag commands, initial speedup, saved
motion and movement goals/interpolator state, including relative XY and the
cleared depth. Two controls deliberately corrupt the tag or movement model.
Both reject on the original before either candidate is run; the wrapper checks
that the expected case and model assertion caused rejection. Final evidence:

- `native-run-ex-angle-consumers/report.json`: final three-image matrix.
- `dispatch-layout.cpp/.json` and build/run logs: typed fixture layout.
- `native-control-results.json` and both control logs: original-first rejection.
- `native-run-ex-input/`: immutable historical cases and names.
- `native-run-ex-v1.py`: initial smaller Player/manager observation prototype;
  use the final driver for the complete typed storage claim.

## Rejected source forms

Named vector snapshots, split planar/depth snapshots, late vector assignment,
`memcpy` and a plain `D3DVECTOR` view do not recover the complete movement owner.
They are all restored. Their complete scope packets and source snapshots remain.

For the large dispatcher, named conditional `ZunAngle` values and references
still copy the selected object's word into another object. They do not recover
the original shared float read. The retained scalar consumer does.

Replacing all active flags with the local selector, or with `ex->type`, changes
the dispatch register allocation and fails to recover the original owner.
Limiting that rewrite to the six original register-OR handlers also fails.
Those forms are restored even when a trial's extent is smaller. Their complete
scope packets and available native results are diagnostic evidence only.
The `command-type/` packet follows a failed replacement-count preflight; no
source write occurred, so it is an unchanged angle-value trial, not a distinct
flag experiment. Actual flag trials are `type-flow/`, `command-flags/`,
`active-command-flags/` and `active-type-flow/`.

## Acceleration owners and the refused math edge

The complete 555-byte `step_ex_02` and 507-byte `step_ex_21` bodies are
conditionally byte-identical after translating every independently bound
link-resolved field and one explicitly **unaccepted** `__CIatan2` entry
hypothesis. Their 13/12 fields are retained individually. No bytes are masked.
The 597-byte `step_ex_17` still has 56 actual differing bytes under the same
hypothesis; its complete private sin/cos callee is resolved independently.

These diagnostics do not bind the intrinsic or grant exact credit. The
[complete atan2 dependency review](atan2-runtime-dependencies.md) still has open
original companion/parent, producer and external dependency proof requirements.
Do not promote the entry hypothesis into Oracle configuration or shorten a
runtime owner to accept these callers.

## Checkpoint and continuation

The incremental build, full strict audit and progress verification preserve
**885 exact / 65 mismatch / 265 incomplete**, **169,575 exact primary bytes** and
**950 units**. Source input is
`6d14644784001cc244b22856267cfa70f3c826fd866445b665bc996b38112fb4`;
PDB age is **316**. Source-origin review stays open; Factory was not submitted.

Preserve the complete baseline and final PE/MAP/PDB/receipt sets, all owner
packets, failed source snapshots, versioned drivers, model controls and
`final-regression.json`. Future work should address the remaining complete
projectile dispatcher differences or actual Boss/ECL integrations. Do not
repeat the rejected flag and movement-copy forms or treat native equivalence
as an exact comparison result.
