# Curve EX instruction addresses and compiler folding

`LaserCurveInf::run_ex` at `0x438cb0`, in `src/Laser.cpp`, now passes the
complete local strict comparison: 1,548 / 1,548 bytes and 29 independently
bound linked fields.
Its independently reviewed complete target extent is 1,548 bytes: 1,512 code
bytes, five absolute jump-table entries and a 16-byte selector map. The target
code contains 347 instructions. Older linear measurements decoded the tables
as instructions; their counts of 360 or more are not code-only counts.

At starting checkpoint `ffe9a9b`, the candidate's complete PDB contribution is
1,556 bytes. The local strict audit refuses this unequal boundary before
comparing bytes. Private evidence is in `.analysis/curve-run-ex-compiler/`.
The target scope remains the one established in
[the remapped-owner review](remapped-owner-scopes.md); none of these controls
changes its boundary or excludes its tables.

## Baseline differences

A diagnostic alignment of code instructions isolates two issues. The volatile
instruction-pointer local forces a stack store and reload, followed by the
ordinary pointer's spill to that same slot. Its address arithmetic adds 0x600
to the scaled index before adding `this`; the target first computes
`this + 0x600` and then adds the scaled index. The extra seven code bytes
also require one alignment NOP before the tables, accounting for the complete
eight-byte extent difference.

The common acceleration tail also exchanges the input values assigned to
XMM0 and XMM1. The target converts `b` into XMM1 and the already-tested `a`
into XMM0; the candidate does the reverse. Both perform the XMM1 conversion
first and add XMM0 into XMM1. This is an input-order issue, not evidence that
changing the final sum's destination register alone will fix it. The case-8
entry joins the case-4 body after setting the different node mode.

`baseline-native.bin`, `baseline-native.txt`, `target-native.bin` and
`target-native.txt` retain the complete bodies and code-only listings.
`baseline-code-differences.txt` is diagnostic; it does not grant exact credit.

## Removing volatile exposes address folding

The archived `20261123-laser-curve-run-ex-clean-strict.json` has the same
1,556-byte baseline extent. Earlier nonvolatile pointer controls already show
expanded base/index addressing, so merely deleting the qualifier is a known
failed solution. The fresh plain-pointer control reproduces that behavior:
its complete extent is 1,720 bytes. The table pointer is folded into individual
field operands, growing accesses from `[ex + field]` to
`[this + scaled_index + 0x600 + field]`.

`plain-pointer-phases.jsonl` follows the head through initial optimization,
prelowering, address-mode construction and lowering. A complete read-only
link reproduces all 1,720 ordinary bytes, SHA-256
`f9abe95c1e83b92d1a08dfd0b2c29b92f470a233dd1c8008c75cc763adb01f66`.
Its normal-exit control is `plain-pointer-phases-control.json`.

Binding the current instruction as a `BulletEx` reference instead of a pointer
produces that same entire body. `instruction-reference-ncolor.jsonl` records
the more useful transition: NColor entry still has a complete LEA containing
both `this`, the scaled index and displacement 0x600, followed by assignment
to `_ex`. At NColor exit that definition is gone and the field load has a
combined effective address with displacement 0x620. Thus the address survives
lowering; it is folded during NColor. The completed debugger link and ordinary
image agree over all 1,720 bytes.

The first `NColMdFoldDef` probe mislabeled its fastcall arguments. Its first
argument is the using tuple, the second is the specific use operand, and the
third stack argument is the definition. This follows the call at RVA
`0xab6f5` in `NColFoldTooCheap`. Filtering ECX for a LEA therefore captures LEA
uses, not necessarily the instruction-pointer definition. The phase snapshots
establish the NColor interval, but those five events do not identify the exact
folding call for `_ex`. Preserve that distinction when extending the trace.

## A shared named table base keeps the pointer but moves its base

A natural table-base control binds `BulletEx *instructions = inner.ex`, uses
`instructions + index` for the current entry and reuses `instructions` for
the SHOOT table copy. Its complete extent falls to 1,560 bytes. Field accesses
again use the current-entry pointer, but the table-base LEA appears before
the loop and again at the loop latch. The multiply writes ESI instead of EAX,
and loop alignment changes. The floating input-order difference remains.

`named-table-ncolor.jsonl` shows that the base LEA is already outside the loop
at NColor entry. It survives allocation as `_instructions$1`; this is distinct
from a base first moved by NColor. The ordinary and completed debugger bodies
agree over all 1,560 bytes, SHA-256
`e742fc5882b2c44038c94f550be6d79602f869cd40647a30e977dfd01e3f1903`.
Preserve the matching normal-exit control and native listing.

A mutable current-entry pointer initialized to `inner.ex` and then advanced
with `ex += index` still gives 1,720 bytes. Naming the base only for entry
lookup while keeping SHOOT's direct `inner.ex` table copy also gives 1,720.
The shared base's second use is material to the 1,560-byte control; a name
alone does not preserve it.

## Advancing the actual paired-command cursor

`NColFoldTooCheap` checks whether a lifetime has one definition. With multiple
definitions, it compares them through `FactXor` before allowing recalculation;
different definitions prevent that cheap-folding path. This suggests examining
SHOOT's actual two-instruction input, rather than introducing a separate base
whose live range crosses the loop.

The retained pointer control advances the existing `ex` cursor once alongside
its first `ex_index++`, then reads the following instruction through that same
cursor. All four following fields still come from the second instruction.
The complete extent becomes the target's 1,548 bytes and all 29 linked fields
bind independently. The strict comparison matches 1,546 bytes; only the two
MOVD input-register fields at offsets 333 and 340 remain. The full raw
ordinary body has SHA-256
`7bb9028e102b66e2ddd623bfd4ca468676e52df48f8aefc5d330cb3738d767d7`.
Preserve `paired-command-cursor-strict.json`, its source snapshot and native
body. The completed read-only replay reproduces the entire ordinary body and
records two different definitions of lifetime `_ex$1`: its initial LEA
(`0x12`) and the actual pointer advance (`0x2d`). Both the final pointer
representation and the lifetime change therefore have direct compiler
evidence. Preserve `paired-command-cursor-control.json` and the paired
canonicalization/NColor traces.

The sum trace shows why reversing the source expression alone is byte-neutral.
After prelowering, the converted register operands are expanded back into
conversion trees and sorted. The already-tested a value is kind-3 integer
temporary `0x3bf`: shifting its ordinal by six gives hash `0xefc0`. Integer to
float conversion (`0x70b`) adds `0x1d`, producing canonical key `0x2efdd`.
The b memory read uses temporary address `0x39f`, giving memory key `0x1c008`
and conversion key `0x2c025`. Descending sorting therefore restores a first.
Naming the actual duration used by both the branch and conversion closes
the remaining input-order difference.

## Closing the converted sum

Both acceleration cases now snapshot `ex->a` in a used `const i32 duration`.
The nonnegative guard and conversion consume that same value; the end time
is written as converted b plus duration. The complete local strict report
`named-duration-strict.json` passes all 1,548 bytes, including the five jump
entries and 16 selector bytes. The raw ordinary body SHA-256 is
`323cb17ebebf382a0b89eaae8e7bae218a337936e74960d0b92930325df17e4c`.
The stale pointer/angle/conversion TODO was removed.

The two pre-existing volatile angle reads remain in this version. Removing
both casts retains the complete extent but matches only 1,531 bytes: the
shared acceleration block moves stack allocation and the start-position Z
store before the angle load. This changes offsets 262 through 278. The
plain-angle control is not retained; preserve its source, build log and
complete strict report.

The final replay records duration as an ordinary named integer symbol, ordinal
`0x7` in one case and `0xa` in the other. Their source keys are `0x100e0` and
`0x10140`; conversion produces `0x200fd` and `0x2015d`. Both are below b's
unchanged `0x2c025`, restoring b first in both expressions and preserving the
shared native tail.

The final NColor trace also records `_ex$1` with its distinct LEA and advance
definitions. Their `FactXor` comparison returns -1 at RVA `0xab838`. The
nonzero result takes the path that skips cheap folding for this lifetime.
This directly confirms the multi-definition mechanism suggested by the
paired-command source change.

`final-control.json` verifies a normal debugger exit and equality of the entire
ordinary 1,548-byte body with the SHA-256 above. Keep `final-canonical.jsonl`,
`final-ncolor.jsonl`, the final debugger image/map/log and `Laser.cpp.final`.
`final-strict.json` passes this owner plus enemy interpolation, curve tick and
curve reverse-step. All retained evidence is from incremental builds and
focused complete-owner comparisons; Factory acceptance remains not-submitted.
