# Pause menu compiler context

Investigated 2026-11-28 with the maintained v141 `/GL` graph. Private evidence
is under `.analysis/pause-compiler/`. The ordinary baseline compares all 26
PauseMenu owners: 23 local passes, two incomplete owners and one mismatch.
`tick_open` owns all 4,676 bytes and passes its extents, linked fields and
reviewed switch tables; two SIB bytes differ. Factory acceptance is unchanged.

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
