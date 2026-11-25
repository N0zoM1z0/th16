# Curve tick: v141 register allocation

The retained `LaserCurveInf::on_tick` source (`0x4377d0`) now passes the
complete local strict comparison: 1305 / 1305 bytes, 332 instructions and
30 independently bound linked fields. The final report is
`.analysis/curve-tick-compiler/curve-tick-final-strict.json`. Factory acceptance
remains not-submitted.

Compound accumulation in the speedup branch repairs the acceleration call's
register preference. The boundary checks use a real mutable two-component
point and one width snapshot; Y is loaded after the horizontal checks. This
changes allocation costs without adding native copies, and the named width
restores the target's addition and load order. The closing investigation is
at the end of this note. Earlier sections retain the failed baselines and
the explicit-site traces that led to these changes.

The original refreshed baseline after reverse-step checkpoint `9c64980` was
1299 / 1305. It also differed at offsets 68 and 73, selecting EDX instead of
EAX for the acceleration virtual-call target. Instruction order and lengths
otherwise agreed. That baseline report is
`.analysis/step-back-compiler/next-curve-tick-baseline-strict.json`.

Private evidence lives in `.analysis/curve-tick-compiler/`. It uses the same
pinned v141 DLL and public symbols as the
[reverse-step investigation](curve-step-back-compiler-trace.md). The initial
baseline's completed read-only replays reproduce its entire 1305-byte owner,
SHA-256 `c92ca8e55156cfa0d330e414fab9495c914834d643312c934dc6a8a42d08f017`.
The controls, phase snapshots and logs retain the original observations.
The physical writes below and the explicit Schedule entry show that the
virtual-table pointer is in ECX, its call target is in EDX, and the promoted
192.0f/448.0f values use XMM3/XMM4 before scheduling. The unwind-derived
post-NColor capture is diagnostic; explicit sites establish these choices.

## Baseline candidate order and register writes

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

## Constant candidates and a bounded priority control

A fresh trace of the retained accumulator source confirms equal priorities of
239 (`0xef`) for both bounds. At `NColInitializeSyms`, the 192.0f and 448.0f
loads receive candidate indices 111 and 112. The initializer walks the tuple
chain, processing each destination list before its source list; its candidate
index store is at RVA `0x23fc4e`. The sorted candidates remain consecutive,
with 192.0f first. Keep `constant-candidates-complete.jsonl`,
`constants-after-initialize-complete.json` and `constant-candidates-control.json`.
The completed replay reproduces the retained 1305-byte ordinary body.

The first capture of that probe stopped on an indexing error: the prioritizer's
input count includes entries omitted from its zero-terminated output array.
The corrected capture stops at the terminator. Its incomplete predecessor and
GDB log remain separate; a batch debugger exit code alone does not establish a
completed replay.

A bounded compiler-state control changes only the computed priority of
`__real@43e00000$1`, from 239 to 240, immediately before the ordinary priority
store. The unmodified source then produces diagnostic agreement for all 1305
bytes after replaying the 30 independently bound linkage fields. Only the four
known register bytes change; the linked fields remain unchanged. This isolates
the allocation choice without changing instruction scheduling or the scalar
arithmetic. It is not a source reconstruction result.

Keep `priority-counterfactual.exe`, its map, GDB log,
`priority-counterfactual.jsonl` and `priority-counterfactual-comparison.json`.
The diagnostic raw body SHA-256 is
`f86ea5e64cc92cafa9486544122742caa10c08a050bac7c81e3db6b55a1e6fad`.
The retained source still has four differences.

The preload trace reaches `CmdInsertEnter` between global allocation setup and
NColor. Its boundary symbols have ordinals `0x30`, `0x32`, `0x34` for -192,
192 and 448, and all three insert before the same loop marker. Symbol
enumeration scans allocation pools; NColor later numbers the resulting
preloads in tuple order. `SYM+0x38` holds a pointer during global promotion and
an integer candidate index after NColor initialization, so its interpretation
must follow the phase. Keep `constant-enterloads.jsonl`, `enterloads-control.json`
and its completed GDB log. Use explicit stack return addresses to identify
callers; the older-frame names produced by unwinding at function entry can
skip a caller in this stripped DLL.

## Source and lowering controls after the accumulator checkpoint

A real `Float2` boundary object initialized Y then X, with both components used
by the tests, was byte-neutral at 1301 / 1305. It did not change the emitted
constant assignments. The object was removed.

Computing the entire vertical outside predicate before the horizontal tests
instead yields a 1315-byte owner. It does give 448 to XMM3 and 192 to XMM4, but
computes Y first and materializes the predicate in AL before checking X. Its
size and instruction order fail the complete comparison. This differs from
the earlier single bottom-predicate staging, which was byte-neutral. Preserve
`Laser.cpp.vertical-predicate-first`, its complete extent report and native
listing; it proves that source can exchange the constant registers while also
showing the cost of this particular control flow.

A private source-layout control places the vertical block text first but jumps
to the horizontal block first. It remains 1305 bytes but matches only 1254;
the boundary-register differences remain, and component scheduling changes.
It was restored. Reversing the lexical block order alone is not a solution.

Standalone COFF lowering controls also reject two broader rewrites before a
whole-owner trial: a double 448.0 comparison emits `cvtps2pd` and `comisd`, and
bitwise OR of the Boolean comparisons emits `setae` and integer OR operations.
Their sources and disassemblies are retained as `literal-comparison-*control*`.
These controls establish those lowering behaviors, not an owner match.

## Materialization precedes preload insertion

The completed `float-materialization` replay records actual callee-entry stack
return addresses and the explicit `MscFloatConst` return site (`0x1c88d4`).
The earlier frame-unwind attribution of the preload caller was wrong: its
actual caller is `AvoidAirlocks+0x25c`, not `Globregs+0x1d6`. The scalar
parameter/local loads later come from `Enterloads+0x72e`.

`LoConvertFPConstToGlobal+0x17` calls `MscFloatConst` for -192 first, then 192,
then zero, then 448. `MscFloatConst` is at RVA `0x1c888a`; its FloatConstTuple
contains a ten-byte extended floating value at `+0x24`. Decoding that value and
recording the returned symbol/root proves the bounds become symbols `0x30`,
`0x32`, `0x34` in that order. Repeated zero and timer-constant lookups reuse
the earlier symbols. `AvoidAirlocks` subsequently inserts the bound preloads
in the same order, before the common loop marker. This locates the ordering
before NColor's candidate indexing; changing declaration order after constants
have folded does not address its origin.

Keep `trace-float-materialization.py`, `float-materialization.jsonl`,
`float-materialization-control.json` and its GDB log. The read-only replay
completed and reproduced the retained ordinary body. A fresh focused audit
in `after-float-controls-strict.json` confirms that the source was restored:
curve tick remains 1301 / 1305, and reverse step still passes 986 / 986.

A standalone named-constant control also shows that local/static floating
constants and an address taken into a local pointer fold back to
`__real@43e00000`. Only an undefined external constant retains its own data
symbol in that COFF control.

A second bounded compiler-state control swaps the adjacent 192/448 preload
tuples before NColor. It exchanges the constant registers in their uses, but
also emits the 448 load before the 192 load. The target loads 192 first. This
control therefore differs from increasing 448's priority while preserving the
original tuple order. Its absolute linked fields move with those loads, so
the comparison deliberately does not replay the old field bindings at the old
offsets. Preserve `preload-order-counterfactual.*`, its native listing and the
explicit diagnostic comparison. A candidate-order swap by itself does not
reproduce the target stream.

Swapping only the operands of the last comparison (`448.0f <= y - width`)
was byte-neutral at 1301 / 1305, including the same four differing bytes.
The source was restored. A separate COFF control with a `register float`
local also showed no register-preference effect in the one-comparison and
scan-loop examples. These do not provide the needed priority distinction.

## The equal priorities come from block costs

Explicit sites in `NColPrioritizeCandidates` now account for both priorities
of 239. `priority-terms.jsonl` records the credit at RVA `0x2463dd`, the cost
subtraction at `0x24637b`, and the final store at `0x24622b`. Both constants
span blocks 73–79, with block costs 18, 17, 31, 20, 22, 20 and 17. Blocks 73
and 74 have loop depth zero; the remaining blocks have depth one. The base
benefit is the maximum block cost plus four: 31 + 4 = 35.

For a block containing a use, the credit is
`8 * use_count * (35 - block_cost) * 4^loop_depth`; an intervening block costs
`block_cost * 4^loop_depth`. The 192 constant has a definition/use in block 73
and a comparison use in block 76. The 448 constant shares the first block and
has its comparison use in block 78. Their sums are:

- 192: `136 - 17 - 124 + 480 - 88 - 80 - 68 = 239`.
- 448: `136 - 17 - 124 - 80 - 88 + 480 - 68 = 239`.

Thus the equal costs of the two comparison blocks explain the tie. These
costs count compiler symbol encounters, including values that will not occupy
separate physical registers. A watch on block 76 catches its value 20 being
written at `NColBuildInfo+0x3d3` (RVA `0x114283`). This function initializes
its running count with `SbvCount` at `0x1145b0`, then increments it when backward scanning
encounters a symbol absent from the current set. Removing a definition from the
set does not decrement that count: neither the initial nor the final set size
is the block cost. Also track the actual thread-state base: this routine adds
`0x10`, so its field `+0x106a4` is the true thread-state `+0x106b4` cost table.

The read-only priority and write-watch replays completed and reproduced all
1305 ordinary bytes. Keep `priority-terms-control.json`,
`block-cost-write-control.json`, the matching JSONL traces and GDB logs.

Caching the segment Y coordinate before the X tests was rejected by the full
comparison: 1231 / 1305. Its native listing shows X, Y and width alive together,
using an extra XMM register and moving the promoted constants. Caching X
instead gives 1293 / 1305: it keeps both constant priorities at 239 and changes
the width load and addition operand order. The read-only X replay reproduces
that complete trial body; neither source trial is retained. Preserve the
`scalar-y-position-*` and `scalar-x-position-*` reports and listings, and
`scalar-x-priority-members.jsonl` with `scalar-x-members-control.json`.

`baseline-priority-members.jsonl` captures the final sets at the actual block
cost stores, and its completed read-only control reproduces the retained
1305-byte body. A staged X accumulator is identical to the failed cached-X
native body, including the unchanged priority tie. Its `staged-x-priority-costs`
trace follows the initial count and each increment: the X comparison block
starts at 18 and adds two virtual-symbol encounters; the Y block starts at 17
and adds three. Both finish at 20. The separate completed control reproduces
all 1305 bytes of that trial. Keep the `staged-x-position-strict.json` report
and `staged-x-costs-control.json`.

Binding a const reference to the X field instead of copying its value is
byte-neutral at 1301 / 1305 and was removed. Negating both sides of the right
comparison is unsuitable: the pinned COFF control emits an extra `xorps` and
uses the negative constant. Keep `negated-boundary-control.*`; it rejects that
lowering before an unnecessary whole-owner build.

## A source predicate changes exactly the predicted cost

The staged right-boundary integer predicate is the first source control to
produce the predicted unequal priorities. After rejecting the left boundary,
it saves `x - width >= 192.0f` in a used `i32` and tests that value before the
vertical bounds. `integer-x-priority-costs.jsonl` records block 76 increasing
from 20 to 21 while the other six block costs and the maximum remain unchanged.
The measured priorities become 207 for 192 and 235 for 448, exactly as the
formula predicts. The emitted constants use the target's XMM4 and XMM3.

This trial is not retained: materializing the integer adds `xor eax, eax`,
`setae al` and `test eax, eax`, growing the owner from 1305 to 1312 bytes. The
strict report correctly refuses its mismatched complete boundary. Its completed
read-only compiler replay reproduces the entire 1312-byte ordinary trial;
keep `integer-x-predicate-*`, `integer-x-priority-costs.jsonl` and
`integer-x-costs-control.json`. This separates a verified source effect on
priority from a successful reconstruction.

The pinned `boundary-flag-branch-control` COFF experiment distinguishes the
integer materialization from narrow predicates: bool, char and unsigned char
can lower directly to the float branch, whereas int, short and an explicit
comparison with one retain a materialized result. These are lowering controls;
the whole owner and its allocator trace must establish whether a narrow form
also retains the needed cost distinction.

The whole-owner bool and unsigned-byte predicates are byte-neutral at
1301 / 1305. The bool replay restores block 76 to 20 and both priorities to
239; it reproduces the entire retained native body. A separately assigned
integer flag (`outside_x = 0; if (comparison) outside_x = 1`) also becomes
that same body and the same tie. Keep the `boolean-x-*`, `byte-x-*` and
`assigned-x-*` source controls and strict reports, with the completed bool
and assigned-integer allocator controls.

The extra encounter in the direct integer initializer is the materialized
integer result consumed by opcode `0x2f` (the integer test). Its symbol type
is `0x41004`; the other two encounters have float type `0x8e004` and occur
while processing the float comparison (`0x111`) and move (`0x125`). The bool
and conditionally assigned forms have only those two float encounters. Their
native branch simplification has already removed the extra test before
NColor counts symbols. Changing the predicate's spelling alone therefore
does not preserve the useful priority distinction.

A non-local vector-expression control replaces `head += position` with
`head = head + position`. It grows the complete owner to 1314 bytes: the
returned vector introduces packed component assembly and copy instructions,
while the boundary constants still use the wrong registers. Accessing X through
the vector's indexing operator instead of its named field, either for both
tests or only the second, is byte-neutral. These controls are restored; keep
their source snapshots, strict extent reports and the vector-assignment native listing.

Closing the head vector's source scope after the horizontal tests, before the
vertical tests, is also byte-neutral. The completed `horizontal-head-scope`
replay reproduces the retained body and the same seven block costs and two
priorities. Scope markers alone do not shorten these allocator lifetimes.

The common loop sets are not simply a count of active scalar registers.
`constants-after-initialize-complete.json` identifies address-producing tuples
for `this+0x5f4` (segment count), `this+0x70` (hit length), `this+0x6c` (angle),
`this+0x54` (position), the position reference's offsets 4 and 8, and
`this+0x74` (width). The corresponding candidates appear in the sets captured
by `baseline-priority-members.jsonl` throughout the comparison blocks. Their
native accesses use base-plus-displacement operands rather than separate
address registers. These temporary identities and lifetimes explain why
allocator cost can change without extra native address calculations.

## Closing the boundary allocation with real component lifetimes

A scalar Y accumulator loaded after the horizontal checks still costs 20 in
the bottom-comparison block. It adds two operand-order differences and gives
1299 / 1305, so it is not retained. A real position aggregate provides the
useful distinction instead:

| Source control | Owner size | X / Y comparison cost | 192 / 448 priority | Result |
| --- | ---: | --- | --- | --- |
| Earlier retained direct fields | 1305 | 20 / 20 | 239 / 239 | Four register bytes differ |
| Mutable Float3 copy | 1318 | 22 / 20 | 215 / 271 | Registers repaired; stack copy remains |
| Float2 scalar construction | 1305 | 23 / 20 | 219 / 303 | Y stays live during X; constants shift up one register |
| Delayed Y component assignment | 1305 | 22 / 20 | 175 / 231 | Registers repaired; ten load/addition bytes differ |
| Delayed Y plus named width | 1305 | 22 / 20 | 175 / 231 | Complete strict pass |

The Float3 copy lowers to a `movq` load/store of X and Y, then scalar reads
from that stack copy. Scalar construction removes the stack copy but makes
X, Y, width and the arithmetic scratch live together. Delaying the actual
Y assignment until both X checks pass removes that fourth simultaneous value.
The 192 and 448 preloads can then use XMM4 and XMM3, matching the target.

The delayed-component NColor input retains extra X copies around its in-place
subtraction: the arithmetic temporary feeds the updated SROA field, which
feeds a comparison temporary. These increase block 76's modeled cost from
20 to 22. They coalesce away before native emission. The Y field's final
update does not retain those same copies. This yields the verified unequal
priorities without the earlier integer predicate's seven extra bytes.
Keep `position-copy-*`, `point-scalars-*`, `point-delayed-y-*`, their source
snapshots and their completed read-only controls. Both the initialized tuple
chains and the explicit Schedule-entry chains are retained.

Two controls separate this lifetime change from arithmetic order. Direct
component-to-edge assignments and using the original position fields only
for the plus tests both restore the earlier 1301 / 1305 result and the priority
tie. Explicit left/top scalar accumulators instead reproduce the delayed
point's same ten differences. None is retained.

`point-delayed-y-add-canonical.jsonl` records the second canonicalization:
by Lower entry the width operand precedes the point component in both adds.
The width SSA leaf has ordinal `0x50e`, parent `0x3aa`; the point leaves have
ordinals `0x2aa`/`0x2ab`, parents `0x217`/`0x216`. The component parents carry
SROA names. This establishes the ordering before physical allocation and
native scheduling, rather than inferring it from the final register bytes.

The final source snapshots width once after loading X. This real value is
used in all four tests; its NColor symbol is `_segment_width$1`, with flags
`0x20004` instead of an unnamed temporary's `0x3`. The block costs and both
constant priorities stay unchanged, while the two adds and the initial
X/width loads regain the target order. The complete strict result binds all
30 fields and covers the full PDB owner extent.

The completed final allocator replay reproduces all 1305 ordinary bytes,
SHA-256 `f86ea5e64cc92cafa9486544122742caa10c08a050bac7c81e3db6b55a1e6fad`.
Keep `point-named-width-costs-control.json`, its JSONL trace, both tuple
snapshots and GDB log. This is now a source result; it also reproduces the
body previously isolated by the private priority-only control.

A separate completed canonicalization replay of the final source confirms the
ordering at Lower entry. Both adds now read the point component before
`_segment_width`. The component parents are SROA symbols `0x208` and `0x207`;
the width parent is the named local `0x12`. Their SSA leaves are
`0x28b`/`0x28d` and `0x28c`. Keep
`point-named-width-add-canonical.jsonl` and its completed full-owner control.
This places the repaired ordering before lowering, allocation and scheduling.
