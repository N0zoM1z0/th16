# ECL integer result exits and Boss async phase cleanup

This continuation starts at `aba6395`. It recovers the shared integer-result
exit in the large ECL interpreter and exercises a Boss time interrupt followed
by a life interrupt while actual heap-allocated async contexts are live.
No new exact credit is claimed.

## Retained interpreter source

`EclRunContext::ecl_run`, at `0x00472030`, now computes integer add, subtract
and multiply into a shared `arithmetic_result`, then reaches one result-push
exit. That exit writes the integer stack tag and result, clears the instruction's
stack-reference count, and advances to the next instruction. Division and
remainder retain their separate exits, as in the original.

The original add/subtract/multiply handlers reach the same integer-tag write.
The starting candidate has three writes, and add sinks its arithmetic after the
tag write. A bounded control-flow walk from each dispatch-table entry confirms
that the retained candidate reaches one common write and computes all three
results before it. This includes both type-conversion paths through the typed
stack pops. Division and remainder still reach distinct tag writes.

The pinned compiler places the retained common block after multiplication;
the original places it after addition. Register/addressing choices, comparison
exits, other operator paths and the interpolation loop still differ. This is a
recovered control-flow structure, not an exact-owner claim or merely a size score.
No unused local, assembly, register constraint, compiler profile or comparison
rule is added.

## Whole spans and switch data

| Scope | Annotated target | Starting candidate | Retained candidate |
| --- | ---: | ---: | ---: |
| ECL interpreter | 7,046 | 7,462 | 7,370 |
| Code and alignment padding | 6,684 | 7,100 | 7,008 |
| Embedded switch data | 362 | 362 | 362 |

The target's existing 7,046-byte boundary remains **provisional**. It is not
promoted or shortened. The candidate sizes come from the linked PDB owner.
All bytes are retained in `.analysis/boss-restart-work/interpreter-final/`.

The packet separates the 67 four-byte switch targets and the 94-byte opcode
remap from executable code. Every switch destination must be a decoded
instruction boundary, and every remap index must select a valid target. The
362 table bytes are included in the full scope. Early generic trial listings
linearly decode those bytes; they are superseded by this data-aware packet.
The table extractor's first draft incorrectly searched for an index register in
the byte lookup; selecting its absolute displacement fixes that diagnostic error.

Strict replay still refuses three unbound linked fields in the interpreter.
The provisional extent, complete size difference and remaining body differences
also remain open; none is normalized away. Boss logic remains 2,222 bytes
against 2,207 original bytes, and damage remains 741 against 774.

## Complete native arithmetic

The final image passes **432 complete Boss calls** whose time-interrupt programs
execute integer add, subtract, multiply, division and remainder through the real
ECL interpreter. Fixtures combine integer and float stack entries in all four
type pairs, positive/negative/zero and large finite operands, two subroutine
slots, and three x87 precisions. Division by zero and signed-overflow cases are
excluded from this independent arithmetic model.

Independent expectations cover the complete observed objects, script arena,
stack tags, converted operands, result, residual popped storage, offsets and
canaries. Division truncates toward zero and remainder follows the corresponding
quotient. A negative fixture substitutes NOP for arithmetic; the original is
rejected before candidate fixtures are generated.

## Live async Boss phase transitions

Another **360 complete Boss calls** first take a time interrupt. Its ECL program
creates 1, 3 or 8 async contexts, using either unnamed calls or explicit IDs.
Real game `new`, context initialization, script lookup and list insertion run
after actual executable CRT startup. No callee, import or allocator is replaced.

The same Boss call then applies pending damage and takes a second life interrupt.
That transition calls the real async cleanup, resets the primary context and
loads a different subroutine. The final subroutine waits, initializes life and
rotation, deletes, returns from its outer frame, or is missing. The matrix varies
the first interrupt slot, half/one-and-a-half game speed and x87 precision.

Independent models check all observed EnemyInf, Player, Gui, Spellcard,
EnemyManager, script and relevant Globals storage. They require the final list
head to point at the primary context with null links. The final image also passes
the preceding **400 complete phase cases**. In total this checkpoint runs
**1,192 complete calls**.

A further **360 prefixes** stop at the life-interrupt checker, before cleanup.
They require a nonzero aligned async head outside the fixed fixture regions;
only after that requirement is checked is the image-dependent heap address
removed from the cross-image observation. All other observed bytes must satisfy
the prefix model. A negative program replaces async creation with same-size NOPs;
the original fails the live-head requirement before candidate execution.

The prefix observes a live head, not every heap node or a heap-free counter.
The complete calls run the unchanged exact cleanup routine on the actual lists.
Prefix processes intentionally stop before cleanup and discard their allocations
when terminated. These diagnostics do not establish a general allocation-failure
contract, absence of leaks, resource/effect behavior or complete shipped Boss
script execution.

The first original-image model refuses two assumptions: damaged timers decrement
by game speed, retaining fractional values, and an early second-phase return
leaves primary time zero. Those models are corrected before successful candidate
comparison. The first prefix setup leaves its hardware stop unarmed and reaches
the full return; arming the existing paired breakpoint sites fixes that setup.
Failed logs and exact driver versions are retained, not counted as passing runs.

## Restored source trials and checkpoint

A separate life-subroutine local gives 2,226 Boss bytes; a health reference gives
2,238. Neither recovers statistics or the out-of-line life restart. Both are
restored. Compound arithmetic assignments emit the same complete 7,462-byte
interpreter as the starting image. Sharing all five integer arithmetic exits
gives 7,322 bytes but merges division/remainder exits that the original keeps
separate; it is restored. Only the original three-handler shared exit is kept.

The final source input is
`55d8af3d1b0dd73b97170346069ce664f35f8df125a4fa6031514f7b8b0bbe85`,
PDB age **273**. Full strict replay and progress preserve **885 exact, 65 mismatch,
265 incomplete**, **169,575 exact primary bytes** and **950 units**, without a
classification change. The unit ledger only rebinds linked candidate addresses;
original geometry, profiles, bindings and Oracle rules are unchanged.

Preserve `.analysis/boss-restart-work/`, especially the starting/final images,
data-aware interpreter packet, six other complete owners, shared-exit diagnostic,
typed layout probe, native complete/prefix fixtures and outputs, both negative
controls, failed models, source trials and `final-regression.json`. The older
curve and broad gameplay reports belong to their recorded images and are not
new execution claims for PDB 273. Source-origin review remains open; Factory
acceptance is not submitted. No repository contents were pushed.
