# ECL expression result exits

This continuation starts at `73643b8`. It recovers a common result-push exit
for 20 comparison, logic, bit and integer-negation handlers in the large ECL
interpreter. The complete candidate changes from **7,370 to 6,950 bytes**.
The corrected image passes **3,457 complete native Boss/ECL calls and 360
prefixes**. No new exact credit is claimed.

## Source and control flow

The original handlers for integer/float equality and ordering, integer/float
logical NOT, integer AND/OR/XOR and bit operations, and integer negation reach
one integer stack-tag write. The starting candidate has 16 distinct writes
across these 20 handlers. The retained source computes into `stack_result` and
branches to `push_expression_result`.

The same integer scratch value also feeds the preceding arithmetic exit, while
the two exits preserve distinct instruction-metadata behavior:

| Exit | Handlers | Stack-reference byte |
| --- | --- | --- |
| Arithmetic result | Integer add/subtract/multiply | Writes zero |
| Expression result | The 20 handlers above | Preserves the byte |
| Separate exits | Division, remainder, direct push, decrement, floating negation | Retained independently |

The data-aware CFG diagnostic walks both type-conversion branches of every pop.
It verifies the one common expression tag write, the separate arithmetic write,
and their suffixes through the next-instruction advance. It also verifies that
floating negation writes exactly one floating tag and reaches that advance.
The nonzero byte value eight is metadata stress coverage; its preservation does
not establish a general interpretation of every possible byte value.

The compiler still places the shared expression block after integer negation;
the original places it after integer equality. Instruction placement, stack
slots/addressing and the interpolation loop's VM register remain different.
The original and retained candidate both use a 56-byte local frame aligned to
eight bytes. No padding, alignment/register constraint, assembly or compiler
profile is added.

## Whole spans

| Scope | Annotated target | Starting candidate | Retained candidate |
| --- | ---: | ---: | ---: |
| Complete current span | 7,046 | 7,370 | 6,950 |
| Code and alignment padding | 6,684 | 7,008 | 6,588 |
| Embedded switch data | 362 | 362 | 362 |

The target's existing **7,046-byte boundary remains provisional**. The retained
candidate is smaller and still has body/layout differences; size alone is not
matching evidence. All bytes, 67 switch destinations and the 94-byte opcode map
are retained and checked in
`.analysis/ecl-predicate-work/interpreter-corrected/`. The interpreter remains
incomplete with three unbound linked fields. No comparison span is shortened.

## Complete native models

The final **2,205 unique expression fixtures** execute through complete Boss
time-interrupt calls, using real ECL, lookup and typed-stack routines after
executable CRT startup. The 20 expression handlers account for 2,163 fixtures;
an additional 42 guard the neighboring floating-negation handler.

Finite cases exercise all integer/float type pairs, fractional truncation,
positive/negative/zero operands, and the float precision boundary at 16,777,216.
Other cases cover signed zeros, infinities and distinct signed quiet/signaling
NaNs. Every handler is tested with stack-reference byte zero and eight, under
three x87 precisions. Expectations check full observed objects, residual stack
storage, tag bytes, result words, script offsets, instruction bytes and canaries.
NaN comparisons use independent unordered predicates; floating negation flips
the raw sign bit, including signed zero and NaN payloads. Integer overflow and
out-of-range float-to-int conversion are outside this matrix.

The final image also passes **492 arithmetic cases**, including 60 new cases
that require nonzero reference bytes to become zero, plus the preceding 360
live-async dual-phase calls and 400 phase calls. The 360 live-head prefixes
pass. These total 3,457 complete calls; the prefixes remain separate diagnostics.
The existing limits on heap observation, allocations, resource effects and
complete shipped scripts still apply, as described in the
[preceding Boss async review](ecl-integer-exits-and-boss-async.md).

Four negative controls reject on the original before candidate execution:
removing an expression, falsely clearing expression metadata, falsely retaining
arithmetic metadata, and removing async creation. They confirm that the new
expectations participate in observation. They are expected failures, not passes.

## Rejected neighboring-path edit

The first batch edit also redirected `ECL_OP_NEGF` to the integer exit after it
had already pushed a float. The first 2,163-case matrix missed this neighboring
path. Full diff review found the mistake before a maintained-source commit.

The source is corrected to retain floating negation's direct next-instruction
jump. All 42 added guards pass the original and corrected image. In a replay
against the preserved incorrect PDB 276 image, the original passes all 42 guards
and the incorrect image fails on its first guard: it appends an integer item
and leaves stack offset 16 instead of eight. The CFG diagnostic independently observes its floating-then-integer
tag writes, versus the required single floating write.

Preserve `invalid-negf-image/` and its receipt. The initial `final-image/`,
`interpreter-final/`, `native-*-final/` and `final-regression.json` belong to that
rejected draft. Its green subset results are not validation of the complete
change. Only the explicitly corrected paths are the current checkpoint. The
corrected image uses PDB **277**; the wrong draft uses **276**.

## Relinked upper dispatcher and strict checkpoint

The unchanged `EnemyData::ecl_run_over_300` source has the same complete
21,316-byte candidate scope before and after this change. Its opcode map and
relative switch destinations agree. All changed bytes belong to existing PE
relocation or direct-control-transfer fields. The original complete 21,408-byte
span, all three guarded tables and their owned data are retained in
`enemy-dispatch-corrected/`.

The normal strict writer changes that dispatcher's reason from seven to eight
unbound fields. The additional field at candidate offset 20,986 lies inside its
unchanged 702-byte opcode map; its bytes are `9f a0`. Linear decoding of owned
data yields an incidental operand after relinking. The diagnostic establishes
that location and unchanged data, but does not change Oracle handling or bind
that operand. The dispatcher remains incomplete. The regression checker permits
only this precise generated reason change, after reviewing the whole scope.

The final source input is
`0dd36c03a6cba531ccff7352c69de0ad2bf2c7b9f493525aa184907fcc5fe65d`,
PDB age **277**. Full strict replay and progress preserve **885 exact, 65 mismatch,
265 incomplete**, **169,575 exact primary bytes** and **950 units**, with no
classification change. The unit ledger rebinds linked addresses. Original
geometry, profiles, bindings and acceptance rules are unchanged.

Preserve `.analysis/ecl-predicate-work/`, especially `corrected-image/`,
`interpreter-corrected/`, `complete-scope-corrected/`, `enemy-dispatch-corrected/`,
`native-*-corrected/`, both corrected diagnostics, corrected negative controls,
invalid-image replay, source/driver snapshots, `TRIALS.md` and
`corrected-regression.json`. All builds are incremental. Source-origin review
remains open; Factory acceptance is not submitted. No repository contents were
pushed.
