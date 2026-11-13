# Exact spellcard startup and stage configuration reads

`Spellcard::start` at `0x00417F00` now passes the strict Oracle over its complete
**1,007 bytes, 289 instructions and 46 linked fields**. The previous candidate
was 1,004 bytes and failed the independent complete-boundary check. This is a
game-source repair in `src/Spellcard.cpp`; the Oracle, bindings, compiler profile
and original extent are unchanged.

The complete owner includes attempt accounting, name copies, HUD setup, Boss
lookup, position copies, timer-child setup, bonus calculation and background
and decoration creation. The result covers the entire startup function.
The larger Boss update remains open.

## Preserve the selection across creation

The previous source cached a `StageBoss*` before creating the spell background
and read its flag field afterwards. Original instructions instead keep the
selected Boss index and reload `g_stage_data` after the creation call:

| Original offset | Operation |
| --- | --- |
| `0x357` | Load the stage pointer into EDX |
| `0x36E` | Form five times the selected index in ESI |
| `0x376`, `0x37E` | Read the animation slot and script using ESI times eight |
| `0x38D` | Call `AnmLoaded::create_effect` |
| `0x392` | Reload the current stage pointer into EDX |
| `0x39D` | Read the selected entry's flag using the preserved index |

The retained source stores `background_boss_index`, uses indexed stage reads
for the creation arguments, and reads the current table again for the flag.
The final optional decoration uses the requested `boss_index` independently.
The original index and forty-byte entry stride follow from the complete
instruction sequence. No claim is made that this particular creation call
actually changes the global pointer; the original reload boundary is explicit.

This correction also restores the original whole-function register allocation:
EDI holds the spellcard object, ESI holds the name and later the Boss/selection,
and all three saved registers are restored at the final epilogue. The complete
candidate becomes 1,007 bytes, with 1,005 matching bytes. This intermediate
result remains a mismatch and grants no exact credit.

## Discard the two decoration results at their call sites

The two remaining differences are ordinary LEA displacement bytes, outside any
relocation field. At offsets `0x38B` and `0x3D5`, the intermediate candidate
exchanges the two class-return temporary slots:

| Call | Original result temporary | Intermediate result temporary |
| --- | --- | --- |
| Background creation | EBP minus 32 | EBP minus 28 |
| Optional decoration | EBP minus 28 | EBP minus 32 |

The two decoration effects do not retain their returned `AnmId`. Calling the
existing member-function-pointer accessor directly for those two expressions
discards their class results at the call sites, recovering both displacements.
Calls that retain handles continue through the existing value-returning wrapper.
All seven creation calls still encode the original direct callee destination.
Every byte then passes ordinary strict replay, including both temporary slots.

This records a successful source/compiler-context reconstruction. The original
source spelling and compilation partition remain unproven. There is no new
frame pragma, padding, dummy local, normalization mask or admission exception.

## Complete scopes and regression

Original-only traversal covers all 289 instructions and all branch targets.
The single three-byte RET starts at offset 1,004. One following INT3 byte lies
outside the complete 1,007-byte owner; the next function starts at `0x004182F0`.
The original full-owner SHA-256 is
`af3b002623818fc4ffe7cf8dd66985494434b92e91ef69a069ab0618a6ed8da5`.
The first draft scope helper incorrectly assumes no following padding and
refuses. Its preserved correction checks the one INT3 byte separately; the
original boundary never changes.

At final PDB age **374**, the candidate is the complete same-start PDB owner at
`0x00468C80`. All 46 independently bound fields, complete decoded bytes and PE
relocations pass the existing Oracle. Full canonical replay reports
**888 exact, 65 mismatch and 262 incomplete** among 1,215 annotations:
**172,570 exact primary bytes and 953 retained units**. All previous 887 exact
owners and all 952 previous unit definitions remain unchanged. No candidate
address changes, and only this owner's classification changes.

A separate candidate-image regression checks all **1,719 complete linked public
owners**. The other **1,718 owners**, totaling **526,102 bytes**, retain identical
addresses, extents, full raw bytes and complete relocation lists, including
crossing and duplicate records. This includes the large ECL caller and the
unchanged animation creation callee. That regression establishes preservation
of candidate code; it grants no further original exact credit.

Validation uses the incremental build, complete static owner packets, isolated
canonical strict replay and progress check. No game runtime or dynamic test is
used. Source-origin review remains open; Factory acceptance is not submitted.

## Rejected forms and retained evidence

The same continuation restores a Boss damage-accumulator reuse trial: the full
Boss update remains 2,195 versus 2,207 original bytes. No Enemy source change
is retained. Further spell-start forms are also restored:

- A named background handle, explicit handle-field copy, optional-slot snapshot,
  reacquired stage pointer, and use of the existing text animation-manager local
  each retain the same two temporary displacement differences.
- Direct member-pointer calls for all seven creations produce 1,008 bytes and
  alter background argument preparation, despite recovering the final slots.
- Direct calls with a background-file local produce a complete 1,007-byte owner
  but only 797 matching bytes, including earlier scheduling differences.

Preserve `.analysis/boss-register-work/`: the authenticated PDB 362 baseline,
first exact PDB 373 image, final PDB 374 image, trial sources/build logs/audits,
complete dumped owners, original-only CFG/witness review, `TRIALS.md`, complete
public-owner regression, canonical regression and final audit/progress records.
The final source input is
`22f67bfc320de562ce5d6a0df8de8c9ac780dd561ba0e0c1bdde9549999de22e`.
The incremental graph and earlier ignored evidence remain retained.
