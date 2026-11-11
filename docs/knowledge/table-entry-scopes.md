# Callback table entries and startup initialization

The 2026-11-11 original-only review derives 24 complete original owners from
callback-cell use and startup initialization. The scope evidence is independent
of candidate extents. Candidate annotations supply proposed names only after
the original entry roles and boundaries are established. The resulting replay
has **767 exact, 53 mismatch and 395 incomplete** candidates, covering 120,612
exact primary bytes. This batch adds 23 complete exact owners and 1,395 bytes;
the preceding 744 exact results remain exact.

## Function-valued cells

Each reviewed callback cell has an original indexed load and an actual indirect
call, or a producer store into a callback field with a separate original call
through that same field. Complete parent bytes, hashes, decoded instructions,
the argument/receiver sequences and trap-free instruction paths from parent
entries are retained. Ordinary call continuations do not prove callee execution
or exact parent comparisons.

| Original base | Reviewed cells | Entry role and original use |
| --- | ---: | --- |
| `0x00491B0C` | 4 | switch callback; Stage loads VM+`0x5D0`, passes VM in ECX and event in EDX, calls EAX at `0x0040B335` |
| `0x00491B1C` | 4 | sprite mapping; VM interpreter loads VM+`0x5DC`, passes VM and sprite, calls EAX at `0x00460BDF` |
| `0x00491B2C` | 7 | drawing; draw_vm loads VM+`0x5C8`, passes VM in ECX, calls EAX at `0x004684B3` |
| `0x00491B58` | 4 | destruction; snapshot disposal loads VM+`0x5CC`, passes VM in ECX, calls EAX at `0x0046ECAD` |
| `0x004919C0` | 7 | shot initialization; file reader replaces shooter+`0x28` index with a function pointer; bullet creation calls it at `0x004452F5` |
| `0x004919A0` | 8 | shot tick; file reader replaces shooter+`0x2C` index with a function pointer; bullet ticking calls it at `0x00445763` |
| `0x004919DC` | 3 | damage-source hit; damage processing loads source+`0x2C` index, passes the callback arguments and calls EAX at `0x00445CDA` |
| `0x004917B8` | 3 | ECL function set; interpreter uses its integer argument as the index, passes the enemy in ECX and calls EAX at `0x00420348` |
| `0x00490EB4` | 3 | ECL extra damage; interpreter stores the selected pointer at enemy+`0x4520`; damage processing loads and calls it at `0x0041C5F0` |

These are reviewed cell windows, including their null cells. Their element
width, function-valued use and selected entry addresses are established.
The event consumers do not check an upper bound. The review does not prove
complete C++ array storage extents, arbitrary selector validity, actual runtime
execution of each event, or source-level function types. It grants no table
data exact credit and introduces no table-sized comparison exception.

The shot reader's `lea eax, [eax+0x58]` precedes stores through EAX-`0x30`
and EAX-`0x2C`, preserving the original record's +`0x28` and +`0x2C` fields.
The independent consumers load those same offsets. The ECL extra-damage
producer and consumer likewise agree on +`0x4520`; a raw address occurrence
alone does not establish that role.

### Interpreter witness paths

The sprite mapping witness is reachable through ordinary branches in the
original VM interpreter. Its primary switch tables are not traversed or
accepted as complete comparison owners by this review.

The ECL witness requires its original bounded compressed dispatch. At
`0x0041DD35`, EAX is compared with `0x2BD`; the adjacent unsigned `ja` rejects
larger values. A 702-byte remap at `0x00422D70` yields indices 0 through 173.
The dispatch at `0x0041DD51` reads 174 four-byte destinations at `0x00422AB8`.
All mapper bytes and destination bytes are retained; every destination is a
decoded instruction start in the original inventoried code. No direct branch
bypasses the guard into its remap/dispatch sequence. Each retained witness path
records the concrete selector, remapped index and destination used.

This proves entry reachability for the reviewed callback uses. It does not
accept ECL's full owned-data boundary, other dispatches or exception graph.
The Oracle's comparison rules and switch profiles remain unchanged.

## Startup and Camera entry

The original PE entry is `0x0047537B`. After a call to `0x0047582B`, it tail
transfers to `0x00475213`. A path from that entry reaches pushes of end
`0x0048B300` and begin `0x0048B2C0`, then calls the initializer iterator at
`0x0047B9A4`. These explicit arguments define the complete 64-byte, 16-slot
interval. Its contents, including its null slot, are retained.

The complete 92-byte iterator reads each four-byte slot, skips nulls, calls
non-null values and advances by four until its computed count is exhausted.
The cell at `0x0048B2D4` establishes initializer entry `0x00401030`; the next
cell independently establishes entry `0x00401100` as a boundary anchor.
The initializer's complete 194-byte graph returns at `0x004010F1`, followed
by 14 INT3 bytes before the next entry.

Within this initializer, ESI starts at `0x004C1308`, EDI is set to 4, and the
loop passes ESI in ECX to the direct call at `0x004010B8`. Each iteration
advances ESI by `0x12C` and decrements EDI. The destination `0x0040D510`
contains `mov eax, ecx; ret`, followed by INT3 padding. Its complete three-byte
scope is established independently of the Camera annotation. It performs no
field initialization; source/type and ownership provenance remain under review.

The iterator and entry wrapper receive no new runtime exact credit. The
initializer remains subject to a complete same-start candidate PDB contribution
requirement before it can be compared.

## Complete function scopes

| Original entry | Complete bytes | Proposed owner |
| --- | ---: | --- |
| `0x00401030` | 194 | supervisor global initializer |
| `0x00405EC0` | 3 | gather draw callback |
| `0x00405ED0` | 65 | gather destruction callback |
| `0x00405F20` | 127 | gather switch callback |
| `0x00406910` | 3 | jagged-line destruction callback |
| `0x00406920` | 3 | jagged-line switch callback |
| `0x004078F0` | 3 | masked-effect destruction callback |
| `0x0040D510` | 3 | Camera constructor |
| `0x00417140` | 57 | bullet sprite mapping |
| `0x00418C60` | 14 | fog draw callback |
| `0x004252D0` | 222 | ECL cancellation callback |
| `0x004253B0` | 61 | ECL power-reset callback |
| `0x004253F0` | 26 | ECL stored-damage callback |
| `0x0042B5F0` | 21 | textbox draw callback |
| `0x00431FA0` | 55 | straight-laser sprite mapping |
| `0x0043A840` | 18 | curved-laser sprite mapping |
| `0x00445ED0` | 13 | homing-shot initialization |
| `0x00446200` | 83 | laser-shot initialization |
| `0x00446E00` | 30 | accelerating-shot tick |
| `0x004470E0` | 16 | sideways-shot initialization |
| `0x00447450` | 46 | piercing-shot initialization |
| `0x00447480` | 30 | slowly accelerating-shot tick |
| `0x004474A0` | 39 | piercing damage-source hit callback |
| `0x0046A330` | 23 | fan draw callback |

The gather switch entry is additionally required to close the gap after the
destruction callback. Its original function-valued cell at `0x00491B14`
independently establishes the entry; candidate size is not used to select it.
Every new function has a dense, nonoverlapping graph containing every branch,
return and call, no unreviewed indirect transfer, no competing inventory owner,
and only INT3 bytes through the next independently established entry.

## Gather timer literal

The complete four bytes at original `0x0049468C` are `00 00 96 43`, the float
`300.0f`. Original instructions at `0x00405F67` and `0x00405F88` read that
same four-byte address with `mulss` and `addss`, respectively. The reviewed
literal binding `__real@43960000` uses the first instruction as its fixed typed
witness. The existing verifier requires the complete typed value, a unique
candidate public, identical candidate bytes and that instruction's exact
mnemonic, address and read width. No new literal validation rule is added.

Negative controls reject an adjacent member read, an instruction-interior
witness, a wrong mnemonic and a wrong width for this binding.

## Rejected piercing-source contexts

The complete original piercing hit callback is 39 bytes. The preceding source
produces a complete 40-byte owner: it computes the index in EDX, loads g_Player
into EAX and moves the old damage from ECX to EAX before returning. The original
loads g_Player into ECX, leaves the scaled index in EDX and reads the old damage
straight into EAX. All instructions and extents remain part of comparison.

Two natural source contexts were built incrementally with unchanged compiler
and linker profiles. Binding one element pointer produces 37 bytes, combining
the base and scaled index before accessing the damage field. Binding the bullet
array base once produces 41 bytes, preserving separate operands but using EAX
for the index and EDX for g_Player, with an extra return-value move. Neither
complete owner matches. Both trials are rejected and the original source is
restored, including its unresolved scheduling note. No forced register use,
access, instruction order or byte comparison exception is introduced.

The first build naturally invalidates the 104 header-dependent stamps retained
from the earlier UpdateFunc trial; it recompiles those dependencies. Subsequent
source iterations use the refreshed incremental graph. Trial sources and full
PE/MAP/PDB/function-map/receipt sets are retained under
`.analysis/piercing-{element-pointer,array-base}-artifacts/`; the preceding
attested artifacts and source are under `.analysis/piercing-pointer-baseline/`.
Complete original and candidate instructions, bytes and hashes are recorded in
`.analysis/piercing-source-context-trials.json`. The restored source is rebuilt
incrementally before the final audit; no archived outputs are substituted.

## Validation and retained evidence

The original-only reproducer reads the canonical original PE and original
inventory, excluding selected entries from its boundary basis before deriving
their scopes. It reads no candidate artifact or candidate size. The original
initializer is derived before it is used as a parent. All 24 derived extents
remain identical when the reproducer is rerun after adding the inventory rows.

Twenty-two of these owners pass the strict Oracle. The initializer has no
complete same-start candidate PDB contribution; the piercing hit callback
retains its 40-byte candidate against the complete 39-byte original. Both are
incomplete. The `300.0f` binding also resolves Stage::load_data's final unknown
field, and its complete 473-byte owner passes. These are the 23 new exact
results. GUI drawing still has other unresolved fields and receives no credit.

Full replay retains all 797 prior comparison units unchanged and adds 23 units,
for 820 total. All preceding source-origin rows are preserved; 24 unknown/review
rows are added. The restored build input hash equals the preceding attested
input hash, and all 192 current object dependency stamps are valid. The current
PE, MAP, PDB, function map and receipt come from the fresh restored-source
incremental build. Maintained game source, compiler/linker profiles and Oracle
implementation are unchanged. The fixed literal binding and its negative
control are the retained verifier-related additions.

All **43 controls** pass: 26 reviewed-linkage controls, 14 strict Oracle controls
and three focused-audit controls. The report and retained-unit freshness check
also passes. Source-origin review remains open and Factory acceptance remains
unsubmitted.

Retained ignored evidence:

- `.analysis/review-table-entry-scopes.py`,
  `.analysis/reviewed-table-entry-scopes.json` and
  `.analysis/table-entry-original-review.log`: original-only derivation.
- `.analysis/callback-table-reference-discovery.json` and
  `.analysis/camera-relative-entry-discovery.json`: discovery locators.
- `.analysis/table-entry-{without-literal,literal,pointer}-focused.json`:
  complete-owner diagnostic stages; only the final full replay is current.
- `.analysis/table-entry-full-audit.log` and
  `.analysis/table-entry-regression-check.json`: authoritative replay and
  retained results/units.
- `.analysis/table-entry-{linkage,oracle,focused}-controls.log`: passing controls.
- `.analysis/piercing-{pointer,array-base,restored}-build.log`,
  `.analysis/piercing-array-base-focused.json`,
  `.analysis/piercing-source-context-trials.json` and
  `.analysis/piercing-restored-cache-check.json`: source experiment, restored
  input identity and incremental cache state.
- `.analysis/table-entry-baseline/`: preceding report, units and inventories.
