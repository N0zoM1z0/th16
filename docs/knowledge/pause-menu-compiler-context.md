# Pause menu compiler context

Investigated 2026-11-28 with the maintained v141 `/GL` graph. Private evidence
is under `.analysis/pause-compiler/`. The current 26-owner PauseMenu scope has 23 local passes, one incomplete
owner and two mismatches.
The initial `tick_open` investigation covered all 4,676 bytes and passed its
extents, linked fields and reviewed switch tables, with two SIB differences.
The retained receiver change below reduces that to one. Factory acceptance
is unchanged.

## Two addresses have the same base/index difference

| Instruction | Target base / index | Candidate base / index | SIB byte |
| --- | --- | --- | --- |
| Name copy at +0xb26 | ECX destination delta / ESI source | ESI source / ECX delta | 31 / 0e |
| Trailing-space compare at +0xdd0 | EAX count / EDI menu | EDI menu / EAX count | 38 / 07 |

The differing bytes are at +0xb28 and +0xdd2. Scale is one in both cases, so
printed sums can hide the distinction. Preserve the physical SIB encoding.
The target places the source/menu pointer in the index slot in both
instructions; their arithmetic addresses are equivalent.

`baseline-phases.jsonl` captures Lower entry/return and PreEncode entry/return.
The normal debugger link reproduces all 66 ordinary owners in the baseline
scope (BulletManager and PauseMenu); see `baseline-phases-control.json`.
All four tuple snapshots are complete rather than capped at the row limit.

At Lower, the name compare already has a base temporary holding menu+0x2d3
and a separate `_i` index. Folding that LEA leaves `_this$GSCopy$1` as base
and `_i$1` as index at PreEncode. The copy store also keeps source as base
and destination delta as index. PreEncode advances the source before the
store and adjusts its displacement to -1, without exchanging those roles.
For these memory tuples, +0x30 is the base, +0x34 the index and +0x38 the
displacement. Investigate address formation before final encoding.

## Retained name-reading receiver

`tick_open` now binds `const PauseMenu *name_owner = this` and uses it for
name reads in replay saving, score copying, comparison and trailing-space
scanning. Name writes keep their existing receiver. The trailing-space
compare now has the target's physical base/index order, with no added field
writes or changed switch destinations.

`name-read-const-receiver-final-strict.json` compares 82 complete owners:
BulletManager, PauseMenu, GameThread and the two real game-over callers.
It retains 70 local passes, ten incomplete owners and two mismatches. The
menu owner matches 4,675/4,676 bytes; only +0xb28 remains different. No complete
function is newly exact. The original Bullet passes and Gui's 470-byte
`start_dialogue` survive; `open_game_over_menu` remains 425/428 bytes and
Player's update remains incomplete at 4,524 bytes.

A full-function receiver capture is not interchangeable with this read-only
binding. It fixes the scan but changes other name-write addresses, matching
4,668/4,676 bytes. Its read-only GS trace exits normally and reproduces all
26 ordinary menu owners (`receiver-gs-phases-control.json`). GSShadow entry
has `_this` and `_menu`; return also has `_this$GSCopy`. Protection is still
generated after an explicit receiver capture. Those two early snapshots hit
the 2,000-row limit; the complete PreLower snapshots have 1,857 and 1,563 rows.
The later GSRecord snapshots also complete at 1,563 rows.

## Rejected source controls

All controls below were rejected and restored. Their source snapshots,
build logs and complete focused comparisons remain in the private directory.

| Control | Complete owner result | Finding |
| --- | --- | --- |
| Scan directly through `name_cursor` | 4,676 bytes; reviewed switch mapping fails | Compare gets the target SIB, but the loop writes the field each iteration and copy-address folding changes |
| Share one real inline scan between score and replay entry | Same two-byte mismatch | The 401-byte `begin_score_entry` and all 23 preceding PauseMenu passes survive |
| Model the name as eight characters plus NUL, with implicit tail padding | Same two-byte mismatch | Known header consumers are PauseMenu, GameThread and the pointer-only unit6 harness; changing array capacity does not explain the SIB pair |
| Reuse one real loop index across the three menu loops | Same two-byte mismatch | Shared variable scope alone does not recover address roles |
| Put replay file operations in real inline helpers owning their path buffers | 4,673/4,676 | Both original differences remain and another copy SIB changes |
| Capture the Scorefile receiver at the replay-save copy | Same one-byte mismatch | The local receiver is eliminated without changing the copy address |
| Share a real inline last-name saver between both writes | 4,674/4,676 | The first copy remains different and the second copy gains a SIB difference |
| Copy the saved replay name with an explicit byte loop | 4,692-byte extent refusal | Source/destination lifetimes diverge from the intrinsic copy |
| Retain a real double BGM-time value before its game-over store | Game-over: 428-byte mismatch, 188 matching bytes | Matching the extent does not restore the frame and stack operands |

Reports use `field-cursor`, `shared-name-scan`, `nine-byte-name` and
`shared-loop-index` prefixes. The header control compares all 40 annotated
PauseMenu/GameThread owners. Earlier pointer-sum reordering, integer-address
casts and name-pointer controls also failed; see the preserved
`.analysis/pause-open-*.json` reports.

The source and full switch owner must agree together. A correct SIB in a
loop with extra field writes does not close the menu function.

## Next address-formation boundary

The private compiler project is `ghidra-project/compiler-addresses/`, using
this game's shared v141 C2 and its existing `c2.pdb`. The selected decompiler
output is `compiler-addresses-pdb.c`; the PDB import completes, although the
subsequent general analysis reaches its time limit. The function decompiler
also warns about type propagation in BuildAddr, so check decisions against
raw code and the runtime tuples.

The focused `compiler-string-copy.c` output identifies `MscStringCopy` at
RVA `0x28569e`. It emits separate source and destination cursors, byte loads
and stores, pointer increments and a zero test. The source-plus-destination-
delta address appears later. Follow that expression through loop address
formation (`LoptBuildAddressModes`, `0x18ce4b`, and
`LoptGenAddressModeExpressionCommon`, `0x8734d`) and `BuildAddr` (`0x174230`).
Changing only the final SIB encoder would bypass the remaining source question.

## Follow the copy through regenerated tuples

The read-only `copy-provenance` trace exits normally and reproduces all 82
ordinary owners (`copy-provenance-control.json`). It selects the final
`MscStringCopy` expansion by decorated function name and function-relative
source location, then verifies the same owner at later phases. The pinned baseline's
first last-name write has function-relative IR location 410 rather than its
absolute source-file line.
There are three frontend/backend instances of the menu function, each with
four string-copy expansions; a single saved FUNC pointer does not identify
all instances.

`OptPureExpr` splits the byte assignment through a temporary and releases
its old memory operand. A later copy can reuse that address. The first
lifetime pilot followed such a reused operand at PreLower; those writes do
not describe the selected copy. Reacquire the byte store by source provenance
rather than preferring the old memory address. The corrected trace follows
the original assignment across complete GSShadow, PreLower, Lower and
PreEncode snapshots (2,497, 1,865, 1,542 and 1,410 statements).

At PreLower entry the destination is still a single-cursor memory operand.
`GoptCanonicalize` replaces its base with temporary 1327;
`GoptReverseCopyProp` then restores destination cursor 836. By Lower entry,
the same store instead has source cursor 834 as base and delta temporary
2220 as index. The memory operand is regenerated again between these
observations, so the watch does not yet identify the instruction that forms
the final two-register address. Trace that replacement before attributing
the choice to integer-add sorting or the final encoder.

The two receiver/helper source controls above are restored. Their complete
26-owner reports are `destination-receiver-strict.json` and
`shared-save-name-strict.json`. `copy-controls-restored-strict.json` restores
the 82-owner baseline: 70 local passes, ten incomplete and two mismatches.

## Snapshot follow-up

Before the surface-helper change, a fresh disassembly of `take_snapshot`
showed that its 462-byte candidate already aligned ESP to eight bytes and
spilled the VM pointer.
The source TODO predates those changes. Compared with the 464-byte target,
the current frame reserves 0x38 rather than 0x30 bytes, several stack slots
and the loaded-animation slot/entry schedule differ, and the target retains
`test eax, eax` after `D3DXLoadSurfaceFromSurface`. Inspect the actual surface
copy and result lifetimes; forcing alignment would not address this baseline.
The private `snapshot-target.asm` and `snapshot-candidate.asm` capture it.

## Retained surface-copy exits

`copy_snapshot_surface` now owns the texture check, surface acquisition,
D3DX copy and release. It returns failure if the texture is absent or surface
acquisition fails, then releases the acquired surface on both copy-result
paths before returning zero or minus one. `take_snapshot` ignores this status.

This natural helper restores the target's `test eax, eax` after the D3DX call
and the slot/entry load schedule. The complete owner is now 464 bytes, with
443 matching bytes; all 21 differing bytes are frame or stack-displacement
values (`snapshot-copy-exits-strict.json`). It remains a local mismatch.
The frame still reserves 0x38 bytes instead of the target's 0x30.

Computing a status after a single common Release does not have the same
compiler effect: that version stays 462 bytes (`snapshot-copy-result`).
Giving the created snapshot handle a named, scoped `const AnmId` local
produces 466 bytes and is restored (`snapshot-named-id`). This narrows the
next question to actual stack lifetimes rather than lexical declaration
order. The existing Bullet collision StackPack observer is reusable here.

The interrupted `copy-expression-return` diagnostic is inconclusive. Its
broad integer-add breakpoint was stopped after substantial overhead without
a relevant sort event; it has no normal-exit or raw-equality attestation.
A smaller prepared `trace-copy-address-routines.py` instead selects calls to
BuildAddr and loop address routines against the current store destination.
It has not been executed. Do not infer integer canonical-sort behavior from
that unfinished trace.

The final `snapshot-exits-final-strict.json` compares 86 complete owners:
74 local passes, nine incomplete and three mismatches. In addition to the
preceding 82-owner scope, it checks `create_ui_vm_at_origin`, `get_vm_with_id`,
`delete_vm` and `flush_sprites`; all four pass. The original 70 passes survive,
and no complete function is newly exact. This is the current retained build.

## Snapshot StackPack allocation

`snapshot-frame-stackpack.jsonl` observes the retained source through the
existing C2 StackPack hooks. The link exits normally and reproduces the raw
bytes of all 86 ordinary owners (`snapshot-frame-control.json`). Seven
objects are enumerated and assigned six colors: the VM pointer and acquired
surface pointer share one slot; the created AnmId return object has its own
slot, separate from the later source-surface pointer.

| Object | Current ESP offset after the saved registers | Target offset |
| --- | --- | --- |
| VM / acquired surface | +0x0c | +0x08 |
| Loaded-animation slot | +0x10 | +0x10 |
| Source surface | +0x14 | +0x0c |
| Hidden AnmId return storage | +0x18 | +0x0c |
| Source RECT | +0x1c | +0x14 |
| Destination RECT | +0x2c | +0x24 |

The anonymous four-byte color maps to the address passed as the hidden
return argument of `create_ui_vm_at_origin` at owner +0x26. The target reuses
that storage for the later source-surface pointer, whereas the candidate
keeps both colors. The extra four-byte color crosses the eight-byte frame
rounding boundary. Both versions already reuse the VM slot for the acquired
surface. This is more specific than a general rectangle-alignment problem.
Investigate why the returned AnmId storage remains separate: follow its
actual uses and the callee's escape/lifetime information, using the same
real-definition visibility controls as TH09 if needed. Matching callee bytes
alone does not establish identical whole-program summaries.

## UI creator visibility and return aliases

The private single-callee visibility control removes only
`create_ui_vm_at_origin` from its ordinary `/GL` object and supplies the same
body from a second object. With `/GL` on both objects, all 86 preceding owners
reproduce the ordinary raw bytes (`ui-single-callee-gl-control.json`). With
only the creator compiled as native COFF, the snapshot return area and later
source-surface pointer share EBP-0x2c. Its prologue, calling sequence and RECT
placement also change, so this native control is diagnostic, not a source
solution. The earlier whole-EffectManager native control shows the same
sharing but is less specific. Inputs and outputs use `ui-single-` and
`ui-boundary-` prefixes.

`snapshot-lifetime-liveness.jsonl` observes the ordinary source after local
liveness and live-on-definition analysis. It exits normally and reproduces
all 141 owners in the expanded menu/Gui/EffectManager scope
(`snapshot-lifetime-control.json`). Both linear walks complete at 135 tuples.
The hidden AnmId return object appears in the alias sets of later
`loaded_anms` reads and the `flush_sprites` call, after its value was copied
into `snapshot_id`. This is a concrete place to investigate the interference;
it is not just a lexical-scope or final offset choice.

The PAS decoder is read-only. `ItfGetPas` at C2 RVA 0x1d83d5 obtains its TLS
pointer by +0x0f, uses the index threshold at TLS+0xfc4c, optionally remaps
through TLS+0xfc20, then loads the list from TLS+0xfbf0. A memory tuple's PAS
index is at +0x28; a kind-11 effect operand uses +0x24. Nested PAS symbols
need their child lists, rather than treating the top list as flat. Selected
PDB decompiles are `compiler-stack-liveness.c` and `compiler-stack-colors.c`.

These natural return-copy controls were checked and restored:

| Control | Result |
| --- | --- |
| Initialize the creator's local AnmId directly from insertion | Creator becomes 180/193 bytes; snapshot stays 443/464 |
| Copy only the returned handle's integer field in the creator | Creator remains exact at 193 bytes; snapshot unchanged |
| Copy only the returned integer field at the snapshot assignment | Snapshot unchanged |
| Return a local handle populated from `vm->id.id` in UI-list insertion | Insertion remains exact at 177 bytes; snapshot unchanged |

The first three controls cover 141 owners. The last uses a conservative
reverse closure of direct calls and tail jumps in both target inventory and
candidate PDB extents, plus the preceding scope and the full edited TU.
Its 356-owner comparison retains 286 local passes, 53 incomplete owners and
17 mismatches. The scan does not infer indirect edges; two closure entries
have no candidate annotations. No new exact function follows from these
controls. Their reports and source snapshots remain under the corresponding
`ui-return-`, `snapshot-scalar-handle` and `ui-value-return` prefixes.

The following ordinary-source controls were restored after complete affected
comparisons. Directly initializing the creator's local ID changes that exact
callee from 193 to 180 bytes. Copying its returned scalar field instead of
the whole class preserves all 141 results but leaves snapshot at 443/464.
The caller-side scalar assignment has the same result. Constructing a local
value in `insert_in_ui_list_back` before returning it also leaves every result
unchanged in the 356-owner caller scope; the provider stays exact at 177 bytes.
That scope combines the known source consumers with the reverse direct-call
and tail-jump closure from target inventory and candidate PDB contributions
(`ui-value-return-callers.json`). It does not infer indirect call edges.
Reports use `ui-return-`, `snapshot-scalar-handle` and `ui-value-return`
prefixes. These spellings do not recover the needed lifetime separation.

The neighboring GameThread BGM-unlock difference is another complete-owner
SIB issue: `finish_stage_transition` remains 622/623 bytes, with +0x208 encoded
as 0x30 rather than target 0x06. Extracting the real `Supervisor::play_bgm`
body into a local inline helper and independently capturing a Scorefile
receiver do not change it. Both controls preserve all 13 preceding passes in
the 15-owner GameThread-plus-BGM scope and are restored (`stage-play-helper`
and `stage-score-owner`). Follow integer address formation for this smaller
owner before extrapolating the Bullet float canonical-sort findings.

## Integer address inputs and return-hook timing

The stage address pilot reproduces 142 ordinary owners
(`stage-address-baseline-control.json`). At AddrModes entry, the BGM store is
fed by an integer add of `g_Scorefile` and `_music`, followed by the 0x19fa6
field offset. The global pointer has key 0x104e0 and symbol ordinal 39;
`_music` has key 0x10040 and ordinal 2. The pointer-first ordering therefore
already exists before BuildAddr processes the expression.

Passing `music_ids[0]` directly into the same-file inline BGM implementation
does not recover the target order. Its entry snapshot still has `_track` at
ordinal 2 and key 0x10040, while `g_Scorefile` is at ordinal 57 with key
0x10720. That trace reproduces all 15 selected ordinary owners
(`stage-direct-track-address-control.json`). Moving the shared BGM body to
Supervisor.cpp and calling it across TUs also leaves every result unchanged
in the 203-owner BGM-consumer scope (`stage-cross-tu-strict.json`). Both
source controls are restored. An immutable reference to the stage's track
field instead generates 624 bytes; the target owns 623. A block-scoped const
reference to the snapshot's returned AnmId generates 466 bytes, like the
named-value control. It is restored too.

Only the entry records establish the BuildAddr input facts above. The
pilot's GDB FinishBreakpoints were installed before the C2 function prologue;
all 146 purported BuildReturn callbacks occurred after all 146 entries.
They observed a later enclosing return, not each BuildAddr return, and may
follow reused tuples. The prepared `trace-stage-address-returns.py` uses the
saved return PC and expected ESP instead: BuildAddr pops 12 argument bytes,
while AddrModes pops none. Those cleanup sizes are verified against all
returns in the two public C2 functions. This corrected observer is not yet
executed; attest its complete ordinary owners before interpreting its output.

The unexecuted copy-address observer now uses the same explicit return
handling and checks that the selected statement still has its source
provenance. Its additional LoptFoldIntoAddressMode and
LoptGenAddressModeExpression cleanup sizes are verified as 20 and zero bytes.
This fixes the prepared observer, not the unresolved source address choice.
