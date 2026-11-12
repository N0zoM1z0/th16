# ECL coordinate evaluation and animation offsets

This continuation starts at `a29e605` and retains two source changes in the
large dispatcher `EnemyData::ecl_run_over_300` at `0x0041dcb0`. It remains
incomplete. Preserve `.analysis/ecl-context-work/`, including the final tested
image, rejected forms, native fixtures and invalid-protocol notes. Comparison
profiles, bindings and accepted owner scopes are unchanged.

## Coordinate output order

Instruction 324 now uses separate found-enemy and self-position branches.
Under the pinned compiler, their common first pointer getter executes before
the branch and coordinate reads, as in the original. The earlier ternary
assignments calculated each coordinate before calling its output-pointer getter,
introducing floating temporaries, spills and reloads. The branch form restores
direct word copies and the original placement of both pointer-getter calls.

The spatial case slice changes from 124 to 88 bytes against 82 original bytes.
Its remaining six bytes load the manager before the lookup call. Both complete
lookup callees still use the global manager and match their existing exact
owners. The helper's public retention and other inline callers need further
review; no calling convention or retention policy is changed here. A named
output-pointer form produced 90 bytes and was restored.

Case slices are diagnostic aids inside the full dispatcher, not independent
exact-credit owners. The original complete code/table/map packet remains
21,408 bytes. The retained candidate is 21,348 bytes, with three dispatches,
182 target slots and the complete 702-byte map. Its frame is still `0x490`
against `0x478` in the original. Other block and register differences remain.

## Animation offset operand order

Instruction 338 now constructs `Float3(x, y, 0.0f) + final_pos.pos`. This gives
the original X operation, adding the position to the returned X argument in
XMM0. The previous reversed vector expression loaded the position into XMM1
and added the argument to it. Y and Z keep their original operand order, and
the Z addition by zero still executes. Argument reads remain Y, X, rotation,
script and file; the first two can consume replay RNG values.

Native snapshots demonstrate a real bit-pattern difference. With origin X
`0x7fc05678` and argument X `0x7fc01234`, the original returns the latter NaN
payload; the previous candidate returns the former. The retained source agrees
with the original. No operand-order normalization or special NaN handling is
added to the comparison or game source.

Explicit component assignment and an address-based accumulator still generated
the reversed X operation. The accumulator reduced the frame to `0x484` but
retained all observed payload failures, so it was restored. The retained vector
expression leaves the frame difference open while recovering the actual result.

## Native checks

All **612 complete lookup calls** agree between original and candidate and
with independently calculated full expected state. They cover instructions
324, 801 and 555, empty/one/two-entry lists, zero/present/absent/negative IDs,
two local-frame bases, immediate and local-variable IDs, aliased output slots,
signed zero, infinities and NaN payloads. Whole self/other enemy objects, context,
manager, list nodes and script storage are compared, including canaries. The
actual lookup, alive-test and argument/pointer getter functions run. Stack
cleanup, preserved registers, floating controls and exception-chain restoration
are checked. Instruction 801's null-dereference paths are outside the fixtures.

The existing lookup returns the last visited enemy when a nonzero ID is absent
from a nonempty list. Consequently, instruction 324 selects self only when the
lookup returns NULL. The model and source preserve that behavior. It must not
be rewritten as a conventional missing-ID lookup returning NULL.

All **42 animation prefixes** agree with the original: seven position/argument
patterns, three x87 precisions, and immediate or positive-offset local arguments.
They include finite coordinates, signed zero, quiet/signaling NaNs with distinct
payloads, infinities and subnormals. The complete position, floating state,
unchanged enemy/context/manager/script storage and the file's incremented VM
count are checked. The independently preserved `a29e605` image fails 18 of these
same cases; its PE/MAP/PDB hashes are verified against its receipt.

These prefixes stop at a hardware execution breakpoint immediately before
`AnmManager::allocate_vm`. Allocation, VM copying/running and effect tracking do
not execute. The debugger restores the canceled frame's exception-chain head
before the next fixture. No game function or import is patched or stubbed. The
fixtures use constants and positive-offset variables; RNG-backed global
arguments and the complete resource path remain untested.

The earlier movement, difficulty-selector and spell-prefix diagnostics are
also replayed against this same final image. Those scoped fixtures retain the
limitations documented in [the preceding ECL review](ecl-position-and-spell-name.md).
They provide behavioral evidence, not exact credit for the dispatcher.

## Invalid protocol attempt

The first lookup harness mistakenly used opcode 800 for the alive test. Opcode
800 is `enmCall`; `enmAlive` is 555. An empty-list smoke happened to return zero,
but the independent positive expected-output check failed on the original image
before candidate execution. Those outputs and the four-case smoke are invalid
as an alive/lookup suite. Keep their `INVALID-OPCODE.txt` notes and raw failure
log. The corrected suite checks the opcode values printed by the historical
compiler's layout/enum probe and passes all 612 cases in both images.

The final strict replay preserves all 885 preceding exact results and all
comparison classifications, with 169,575 exact primary bytes and 950 units.
The tested final PE/MAP/PDB/receipt and source are retained in `final-image/`;
`final-regression.json` verifies their identities across all native suites.
PDB age is 200. Source-origin review remains open and Factory acceptance is
not submitted. The dispatcher receives no new exact credit.
