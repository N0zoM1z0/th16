# Curve tick: v141 register allocation

The retained `LaserCurveInf::on_tick` source (`0x4377d0`) now matches
1301 / 1305 bytes in the complete local strict comparison, with all 30 linked
fields bound. Compound accumulation in the speedup branch repairs the
acceleration call-target registers through a measured intermediate-layout
change. Only offsets 791, 799, 915 and 941 remain: XMM3/XMM4 are exchanged for
192.0f and 448.0f. The final checkpoint report is
`.analysis/curve-tick-compiler/checkpoint-strict.json`. Factory acceptance
remains not-submitted.

The original refreshed baseline after reverse-step checkpoint `9c64980` was
1299 / 1305. It also differed at offsets 68 and 73, selecting EDX instead of
EAX for the acceleration virtual-call target. Instruction order and lengths
otherwise agreed. That baseline report is
`.analysis/step-back-compiler/next-curve-tick-baseline-strict.json`.

Private evidence lives in `.analysis/curve-tick-compiler/`. It uses the same
pinned v141 DLL and public symbols as the
[reverse-step investigation](curve-step-back-compiler-trace.md). Completed
read-only replays reproduce the entire ordinary 1305-byte owner,
SHA-256 `c92ca8e55156cfa0d330e414fab9495c914834d643312c934dc6a8a42d08f017`.
The controls, phase snapshots and logs retain the original observations.
The physical writes below and the explicit Schedule entry show that the
virtual-table pointer is in ECX, its call target is in EDX, and the promoted
192.0f/448.0f values use XMM3/XMM4 before scheduling. The unwind-derived
post-NColor capture is diagnostic; explicit sites establish these choices.

## Candidate order and register writes

`baseline-allocation.jsonl` retains 92 candidate processes, 92 rewrites,
104 availability queries and the candidate priority order. By candidate processing,
the call target is
symbol `0x3f8`, and the constants become named pseudo-locals
`__real@43400000$1` (`0x53d`) and `__real@43e00000$1` (`0x53e`).

The constants have equal priority `0xef`; their lifetime records are adjacent,
at `0xe955094` and `0xe9550f0` in this run, and 192.0f is processed first.
`NColColPriorityCompare`, RVA `0x2585b3`, compares descending signed priority
at record `+0x48`, then ascending record address, dividing its difference by
record size `0x5c`. This identifies the tie rule, not a source repair yet.

Hardware watches in `region-assignment-watch.jsonl` catch each physical-symbol
write at `NColProcessCandidateRegion+0x1e0` (RVA `0x78e5b`). The selected
physical symbol is stored in region `+0x1c`: XMM3, XMM4 and EDX respectively.

The original `FinishBreakpoint` records incorrectly suggested null returns
from `NColDeterminePhysregAvail`. A follow-up probe at its explicit caller
return site, RVA `0x78d3d`, instead observes the actual non-null physical
symbols for all three values. The conjectured fallback search is not taken;
`gap-costs.jsonl` contains no such calls. Keep the corrected evidence in
`availability-callsite.jsonl`, its completed control and GDB log. Native-body
agreement validates the replay's output but cannot validate a debugger's
unwind-derived phase or return address. Use explicit call/return sites when
interpreting this stripped backend. The following section uses explicit
search sites to establish candidate order and rejection conditions.

Older 2026-11-23 controls already rejected reversing the accumulation,
naming the acceleration result, positive screen bounds, named limits and
reordering the bound tests. The simple reversed accumulation was byte-neutral;
other controls changed component addition operands, loop layout or owner size.
Do not repeat them without a new compiler prediction.

## A ten-tuple preference window delays EAX

`availability-search.jsonl` and `availability-footprints.jsonl` capture the
search at explicit instruction addresses, followed by its real caller return.
Their completed native-body controls again agree with the ordinary owner.
The float search uses the fixed physical IDs 189–196 (XMM0–XMM7). For 192.0f,
XMM0–XMM2 lack a covering available interval; XMM3 covers the requested range
384–438 and wins. For 448.0f, XMM3 is already excluded from the usable set, and
XMM4 covers 385–438. Simply naming bottom before right did not exchange these
choices: the 1305-byte trial matched only 1283 bytes because Y/Z head additions
also changed their input order. The source was restored and re-audited.

The call-target search tries physical IDs 1, 2 and 3 (EAX, ECX, EDX). EAX has
an available interval covering its requested 44–46, but it overlaps a separate
preference interval 37–47 in the table at thread-state `+0x106b8`. The search
keeps EAX as a fallback at RVA `0x797bc`, then returns EDX, which has no such
preference conflict. ECX lacks a covering interval because the `this` argument
must be restored before the call. These are tuple indices, not native offsets.

`preference-ranges.jsonl` identifies the owner of the EAX interval: `_again$1`.
It is created by `NColAddRegPrefRange`, RVA `0x2464a1`, called from
`NColPrioritizeCandidates+0x373`. The prioritizer caps a preference range at
ten tuples (`lea ecx, [edx + 0xa]`). The first speedup result's copy into
`again` is tuple 37; the acceleration target load is tuple 44, its `this` copy
45, and its call 46. Thus an earlier result-copy preference influences a later
virtual-call target even though EAX could hold that target. Preserve this
range trace, its completed control and the explicit availability traces when
changing the accumulator's initialization or control flow.

## Retained accumulator source

Replacing the speedup branch's `again = step_ex_speedup()` with
`again += step_ex_speedup()` repairs the call-target registers. The accumulator
is explicitly zero before this branch, so this preserves its integer result.
The incremental complete-owner audit is now 1301 / 1305 bytes, with all 30
linked fields bound. Only the four boundary-register bytes remain.
Keep `Laser.cpp.speedup-accumulation` and `speedup-accumulation-strict.json`.

A conditional initializer (`again = flag ? step_ex_speedup() : 0`) was also
checked against the complete owner. It changed the join layout and folded the
acceleration call target into a memory operand, matching only 881 / 1305 bytes.
That control was reverted. The retained compound accumulation preserves the
original instruction order and lengths; its only differences from the earlier
baseline are the two repaired register bytes.

The completed compound-accumulation traces establish the mechanism, rather
than inferring it from the two repaired bytes. The EAX preference remains
37–47. Three additional intermediate tuples appear at 40–42: opcodes
`0x7a1`, `0x7bb` and `0x7ba`. The next table-pointer load moves from 43 to 46,
the call-target load from 44 to 47, the `this` copy from 45 to 48 and the call
from 46 to 49. The search now asks for 47–49, whose beginning meets the old
preference's end; it is not an interior overlap. The explicit return site
observes EAX, and the complete native owner has no added instructions.

Keep `speedup-accumulation-preference-ranges.jsonl`,
`accumulation-availability-footprints.jsonl`, their controls and GDB logs.
Both completed replays reproduce all 1305 raw bytes, SHA-256
`fda3186474a8e1d560096768b6d0c740b3fc68598917f8b65bfde273ddeb6242`.
The dynamic probe identifies the new call-target symbol (`0x3fc`) from the
actual virtual-slot load after NColCanon and symbol initialization; the older
`0x3f8` identity must not be reused after this source change.

An inline screen-bound helper with actual extent parameters was byte-neutral:
its complete strict report still has only the four boundary-register
mismatches. Moving the literal values through call arguments did not change
the emitted assignments. The helper was removed; retain its private source
and `boundary-helper-strict.json` as a control.

Staging the actual bottom-outside predicate before the combined test was also
byte-neutral, leaving 1301 / 1305. Single-use boolean staging did not change
the boundary-register result. It was restored to the simpler condition.
Investigate how the promoted constant candidates acquire their record order
or priority; declarations, call arguments and this predicate staging have not
changed the emitted allocation.
