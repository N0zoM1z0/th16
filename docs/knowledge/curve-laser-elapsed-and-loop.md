# Curve laser elapsed time and integration order

This continuation starts at `2add62b` and changes the complete
`LaserCurveNode::get_state` owner at `0x00437ee0`. A local elapsed-time value and
an earlier speed update recover original floating operands. The expanded native
matrix removes **372 historical raw-output differences**. Neither curve motion
owner gains exact credit.

## Source and observed code generation

The function now initializes `f32 elapsed = time - start_time` and uses it for
all motion modes. Previously it overwrote the incoming `time` parameter. The
local value recovers velocity X as the first multiplication operand in the
mode-1 sentinel branch, while retaining the original start-position addition
order. With the expanded fixtures, this change alone removes 132 differences
and leaves 240 differences involving a NaN elapsed time.

Mode 2 now advances speed before accumulating position:

```cpp
s += speed_delta;
pos += d;
```

The displacement `d` was already computed with the incoming speed. It therefore
still moves the current frame at that speed, and the increment applies to the
next frame. Both updates operate on local state.

Together with the elapsed local, this ordering gives the original loop's
XMM6 speed accumulator, XMM7 position Y and XMM5 position Z. The scalar speed
update appears between the X and Y position additions, as in the original.
The local stack slots still differ.

The same function context also recovers both mode-1 sentinel multiplications
with speed delta as their first operand: the position formula and the final
speed output. This removes the remaining 240 differences in the expanded
fixtures. These are observations of the pinned compiler's complete generated
function, not a language guarantee about commutative floating expressions.

No unused local, extra double, stack padding, alignment or register constraint
is added. The reverse-step source, compiler profiles, CRT bindings and Oracle
rules are unchanged.

## Complete comparison and native evidence

| Owner | Original bytes | Starting candidate | Retained candidate |
| --- | ---: | ---: | ---: |
| Curve state, `0x00437ee0` | 1,164 | 1,162 | 1,168 |
| Curve reverse step, `0x00438370` | 986 | 986 | 986 |

All executable bytes are decoded in
`.analysis/curve-layout-work/complete-scope/`. The unchanged reverse-step bytes
retain their preceding hash; no shortened comparison or register normalization
is used. State still differs in mode-2 stack slots and mode-1 polar-vector
register allocation and scheduling. Both owners still have two unbound call
fields, floor and intrinsic atan2. The existing
[CRT identity investigation](atan2-runtime-dependencies.md) remains open.

The final **1,488 complete calls** execute the original, receipt-authenticated
`2add62b` image and retained image after their actual executable CRT startup.
No callee or import is replaced. The same previously controlled native runner
checks preserved registers, stack cleanup, exception chains, floating controls,
the entire node and its canary, and the complete input/output arena.

The matrix contains the preceding 768 curve cases, 600 new state-sentinel
cases, and 120 new straight-state cases. The new cases combine finite values,
distinct signed quiet/signaling NaN velocity and acceleration payloads, finite
or NaN speed and time, finite or NaN start X, and three x87 precision settings.
The original 768 cases remain free of candidate differences.

The preserved starting image has 372 differences, all in the new sentinel
cases: 108 use finite time and 264 use NaN time. The retained image has zero.
A representative original result preserves velocity X payload `0x1111` and
speed-delta payload `0x2222`; the starting image instead retains the time
payload `0x9999` in the Y/Z displacement and final speed.

**192 cases** have independent complete-output expectations. These include the
preceding 168 expectations plus 24 finite state-sentinel cases, rounded after
each original scalar operation. A negative control changes the doubled-speed
expectation from eight to nine. It is rejected on the original's first finite
sentinel case, before either historical or candidate execution. This confirms
that the new model participates in observation. It is an expected control
failure, not a passing game comparison.

Overlapping curve outputs, CRT errno/matherr state, asynchronous game activity
and complete shipped Boss scripts remain outside this matrix. The preceding
3,364-case gameplay replay belongs to the preceding image; this checkpoint
runs focused curve diagnostics and a full strict replay, without another cold
build or broad native replay.

## Restored trials

`sqrtf` emits exactly the preceding complete code. A named frame-speed scalar
initially removes 96 differences, but the expanded start-position cases reveal
417 candidate differences against 372 historical differences. Reversing the
written multiplication/addition operands does not repair the generated order.
Those forms are restored.

Explicit speed-change and vector-update forms, a start-position snapshot,
`D3DXVec3Scale`, and a named displacement do not recover the complete desired
sequence. Only the elapsed local and speed-before-position ordering are kept.
The private directory retains full trial scopes, source snapshots, failed
native comparisons and the exact driver versions authenticated by their
reports. Trial failures are not acceptance evidence.

## Checkpoint

The final source input is
`c262f65d5f37e7d96ada30d5d5bd5c5140d60c5feee740415a78d3f249c92681`,
PDB age **265**. Strict replay and progress preserve **885 exact, 65 mismatch,
265 incomplete**, **169,575 exact primary bytes** and **950 units**, with no
classification change. Original owner geometry, comparison rules and the
generated unit ledger are unchanged.

Preserve `.analysis/curve-layout-work/`, including the starting/final images,
complete owners, typed layout probe, native fixtures and outputs, model negative
control, rejected forms, strict report log and `final-regression.json`.
Source-origin review remains open; Factory acceptance is not submitted.
No repository contents were pushed.
