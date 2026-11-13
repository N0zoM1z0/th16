# Float3 timer result join

Starting checkpoint: `52e7b8b`. This continuation improves the complete
`InterpFloat3::step` at `0x00406E10` from **413 to 899 matching bytes out of
906**, under the unchanged strict Oracle. It remains **mismatch** and adds no
exact owners or bytes. No game runtime, native fixtures or instruction emulation
are used.

## Complete scope and retained source

The original owner contains 230 instructions, all reachable from its entry in
an original-only CFG traversal. Its three returns are at offsets 235, 259 and
903. Its sole call is at offset 799 to `interp_common_methods` at `0x004033F0`.
Six following `CC` bytes are outside the owner; the next independently bounded
entry is `0x004071A0`. The full original SHA-256 is
`d10ea08dd74b8294cedfd90085831845d1b23d43878ae659dcb19bbf0e13e5ee`.

An ordinary inline helper advances the integer frame through a shared join and
returns the fractional time for one writeback by the caller. This recovers the
original XMM0 accumulator, the common integer writeback and the complete Bezier
arithmetic/register sequence. The helper is source organization, not a claimed
original out-of-line callee. No additional public owner or call is introduced.
`ZunTimer.h`, the other interpolators and compiler/Oracle policies are unchanged.

The complete comparison validates six linked fields: five DIR32 references
(1.0f, the timer-speed pointer table, 0.99f, 1.01f and 3.0f) and the single REL32
easing call. The existing 3.0f field moves from candidate offset 561 to 560;
its independently reviewed target identity remains unchanged.

## Remaining difference

The original join is:

```asm
0070  mov   [esi+40h], eax
0073  movss [esi+44h], xmm0
0078  mov   eax, [esi+50h]
007b  cmp   [esi+40h], eax
```

The retained candidate loads the end frame at offset `0x73`, then writes
fractional time at `0x76`. Seven bytes differ within this eight-byte window.
The remainder of the complete owner agrees under strict comparison. These
different-field operations are not normalized or excused as equivalent.
The original field witnesses are `0x00406E83` for fractional time and
`0x00406E88` for the end-frame read. Recovering this ordering remains open.

Returning float through a void wrapper changes the accumulator back to XMM1
and loses the original layout. End-frame snapshots, a getter, a predicate, a
pointer parameter and a float setter leave the same ordering difference.
Conditional timer formulations change register allocation or extent. Preserve
the rejected forms before attempting related changes again.

Other complete-owner trials are restored. Float2 and radial Float2 retain
their Bezier scheduling differences. Int3 still differs in one SIB byte; Angle
still differs in its stack allocation. Strange1's copy/constructor trials
change its walker registers and return order, and its original boundary remains
provisional. No SIB equivalence, padding or boundary promotion is accepted.

## Static regression and evidence

The canonical replay retains **890 exact, 65 mismatch, 260 incomplete**,
**175,386 exact primary bytes** and **955 units**. All 890 previous exact
owners and the other 1,214 annotation results/diagnostics are unchanged, apart
from current build identities. All other 954 unit definitions are identical;
the Float3 unit changes only the existing 3.0f field offset.

Complete PE/PDB regression preserves all other **1,718 candidate owners**
byte for byte (**526,227 bytes**), every candidate address/extent and all image
base relocations outside Float3. Only `src/Interp.cpp` retains game-source
changes. The incremental final build is PDB age **420**, source input
`8e2f94db3add1b0ea77a336e1fea943348372cbf2246ff6908d2fdd26179b2c3`.
Source-origin review remains open; Factory acceptance is not submitted.

Preserve `.analysis/vector-owner-work/`: baseline/final five-artifact images,
canonical reports, focused comparison, original CFG, complete six-interpolator
packets, source snapshots, build logs, `TRIALS.md`, and the static
`regression.py`/`final-regression.json`. Packet address masking is diagnostic
only and grants no exact credit. One failed constructor edit did not compile;
the stale-image comparison was refused, then the corrected source was rebuilt
and rejected. Both the failure and refusal remain in the evidence directory.
