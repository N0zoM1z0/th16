# Boss script restart call context

Reviewed 2026-11-13 from source checkpoint `4823bf3`. This continuation restores
an original call boundary in Boss damage/phase logic and the distinct inline
restart in ECL subroutine calls. Evidence is in `.analysis/boss-interrupt-work/`.

## Retained source and original witnesses

`SptInf::load_sub_by_name` is now `DECOMP_NOINLINE`. The original complete
52-byte function at `0x00474890` already has an accepted identity. Its payload,
linked field and normalized unit SHA-256 are unchanged by this source edit.
This uses the existing reconstruction macro for an actual original out-of-line
call; no register assignment, artificial local or new Oracle rule is added.

The original `EnemyData::step_logic` calls that entry at `0x0041c7ee` after a
life interrupt. Previously the candidate inlined the name lookup and three
context stores. The retained image has the original independent restart call,
while the time-interrupt branch keeps its existing explicit inline restart.
The complete Boss owner changes from **2,222 to 2,195 bytes**, against **2,207
original bytes**. It remains incomplete. Statistics operands, life-state
register allocation and collision temporaries still differ; recovering the
call alone does not recover the retained life pointer.

The original `EclRunContext::call_sub` has the opposite arrangement: it calls
`find_sub_by_name` directly at `0x00471f9b`, then writes the current context's
location and time. It does not call the 52-byte restart entry. Its source now
performs those operations directly. A local `call_vm` retains the VM used for
the restart and the first-instruction check, matching the original stable
owner pointer across the lookup. The final restore of the saved context still
reads through the caller's `vm`.

The complete candidate sub-call owner changes from **584 to 581 bytes**. The
632-byte original span remains **provisional**; this work does not establish
its independent boundary or grant exact credit. A first explicit restart that
repeatedly read `vm` generated 596 bytes and different reloads. Its full packet
and source snapshot are retained, but that form is not selected.

The large `EnemyData::ecl_run_over_300` already called the restart entry for
`BOSSES_INTERRUPT` and `ENM_CALL`; original calls are at `0x0042294a` and
`0x00422993`. Its complete 21,316-byte candidate is preserved by a full image
regression. All **927 linked fields** resolve independently between baseline
and final MAP symbols, owner-local destinations, or same-named bounded PDB data
objects. Translating each complete field leaves zero byte differences. No
field is masked or given its destination from the compared baseline operand.
This is a candidate-to-candidate regression, not original exactness: the
original owner has 21,408 bytes and seven fields still lack accepted bindings.

The initial regression helper refuses to claim a complete result with 59
unresolved interior data addresses, even though those bytes are unchanged. Its
versioned script/report remain. The final helper uses the existing bounded
PDB data reader for those owners and resolves all fields. Raw original upper
text dumps decode trailing table data as instructions; use the existing
compound switch ownership record for its data interpretation. Complete raw
owner bytes are retained throughout.

## Native sub-call frames and arguments

`native-call-sub.py` executes **408 complete calls per image** on the original,
immutable PDB-316 baseline and final PDB-322 candidate. The native debugger lets
each image initialize its CRT, then stops before WinMain and invokes the real
function and its callees. Instructions and imports are not replaced.

Cases cover the same caller/destination context and separate contexts, zero
and existing frame tops, ordinary and named-async argument starts, empty and
mixed argument lists, three successful name positions and a missing name.
Arguments exercise integer/float conversion, the alternate float type, integer
fallback types, local references and tagged expression-stack pops. All three
x87 precision settings are used. The source/destination contexts, SptInf,
resource/table/program storage and eight surrounding canaries are compared in
full, alongside return value, stack cleanup and floating controls. The runner
also guards preserved registers and exception-chain restoration.

**360 cases per image** have an independent complete-state model. It checks
converted argument values, expression consumption, saved call frames, restart
location/time, context restoration and the distinct failed-name state. The
other 48 cases retain raw NaN/infinity results in cross-image comparisons;
only their converted argument word lacks a numeric model. Every remaining
observed byte is independently checked for those cases as well. All cases
agree across all three images.

The typed fixture comes from `call-layout.cpp/.json`, built with the pinned
compiler. The initial 360-case driver is retained as `native-call-sub-v1.py`.
The final driver adds 48 empty-argument calls and independently checks the
remaining storage of raw-result cases. A wrong saved-frame model rejects on
the original before baseline or candidate execution.

## Native Boss phase integration

`native-dual-phase.py` retains the earlier full-state Boss model with a new
immutable baseline and output destination. **360 complete calls per image**
exercise time and life transitions in the same Boss update. The input programs
request one, three or eight real async contexts, with named/unnamed calls,
five final programs, two interrupt slots, two game speeds and three x87
precisions. Final programs include life/rotation/bomb-multiplier updates,
return, deletion and missing names. All observed state and return values agree
with their model on the original, baseline and retained candidate.

Two representative prefixes per image stop before the actual life-interrupt
check and require a nonzero, aligned async head outside every fixture region.
They show that a live heap-backed context exists before the cleanup path.
Replacing the async opcodes with NOPs in fixture data makes that assertion fail
on the original before either candidate runs. The control wrapper checks the
specific assertion and execution order. These observations do not count every
heap node or prove allocator leak freedom.

The final combined matrix is **768 complete calls per image** (2,304 across the
three images), plus six prefixes. The initial progress commentary overstated
the phase count as 720 per image; the authoritative phase report has 360.
Preserve the correction rather than propagating the larger count.

These diagnostics use data-only fixture resources and actual allocation, script
lookup, call and cleanup paths. They do not prove shipped Boss programs,
rendering, real asset loading, general Player deaths, all virtual callbacks,
CRT errno/matherr state or unobserved heap storage.

## Restored trials and next work

A lifetime pointer by itself gives a 2,226-byte Boss candidate and still loses
the original life pointer. Joining the damage-credit calculation before its
manager store gives 2,210 bytes but merges stores that the original keeps
separate. Both are restored. After fixing the restart call, a combined dialogue
ternary/life pointer gives 2,193 bytes, still swaps the damage registers and
rematerializes life. That form is also restored. `Enemy.cpp` is byte-identical
to the starting source. Do not repeat these forms based on smaller extents.

The retained work is confined to `EclRunContext.cpp`. Focus future Boss work on
the remaining damage statistics/life registers with the correct restart call
now present. The full Boss owner and sub-call owner remain incomplete; their
extent differences are not a count of mismatching instructions.

## Checkpoint and evidence

An incremental build, focused replay, full strict audit and progress check
preserve **885 exact / 65 mismatch / 265 incomplete**, **169,575 exact primary
bytes** and **950 units**. All annotation results are unchanged. The regenerated
unit file changes only 550 candidate addresses; unit names, extents, profiles,
linked fields and original destinations are unchanged. Source-origin review
stays open and Factory acceptance is not submitted.

Final source input is
`2790b5687dcf511fab390dea7d6299772fd015e6c966a192525f41222ecfe196`;
PDB age is **322**. Preserve both complete PE/MAP/PDB/receipt sets, all source
snapshots and scope packets, typed layout, versioned drivers, model controls,
`upper-image-regression.json`, `native-call-sub-retained/`,
`native-dual-retained/`, `native-dual-prefix-retained/` and
`final-regression.json`. No old evidence or incremental cache is cleaned, and
no repository content is pushed.
