# Boss hit-effect flag expression

Starting checkpoint: `eaf9278`. This is static source progress in the complete
`EnemyData::step_logic` at `0x0041C330`, not a new exact result. The original
owner is **2,207 bytes**; the retained candidate changes from **2,195 to 2,197
bytes** and remains **incomplete**. No game runtime, fixture or emulation runs.

## Original evidence and retained source

The complete original has 534 instructions, all reachable from its entry,
38 calls and three returns at offsets 317, 535 and 2206. One following `CC`
byte is outside the owner; the next independent entry is `0x0041CBD0`.
Its full SHA-256 is
`af9d7f867cc330e018536d58aca99d136551b278213bcb8c3fa1e5133077e90c`.
Both original and retained candidate have the eight-byte stack alignment and
`0x1C` local allocation. The old source TODO about frame alignment is removed.

The original damaged-flash condition reads flags at `0x0041CA4E`, tests
`0x200000` at `0x0041CA54`, then tests suppression mask `0x2000` at
`0x0041CA60`. The baseline combines these into an AND/CMP. The retained source
reads a u32 snapshot and narrows only the suppression expression to u16:

```cpp
u32 damage_flags = flags_low;
if ((damage_flags & ENEMY_FLAG_DAMAGED) &&
    !((u16)damage_flags & ENEMY_FLAG_NO_HIT_EFFECT))
```

This restores both original **32-bit TEST instructions**, without changing
the u32 storage declaration. Since suppression mask `0x2000` lies wholly in
the low word, the narrowing cannot change its tested value. It does not claim
that the original flags storage was 16 bits.

The complete retained packet also recovers the original collision and flash
instruction shapes after the death predicate. In particular, the final
385-byte suffix starts at original offset `0x71E` and candidate offset `0x714`
and has matching shapes for all 91 instructions. This is diagnostic source
evidence: field identities are not proved by address replacement, the suffix
has no independent owner and receives no exact credit.

## Remaining source differences and restored forms

The dialogue damage selection still branches instead of using the original
CMOVE. Statistics operands, scaling registers and the life pointer/death
predicate remain different. The ten-byte extent gap does not count incorrect
instructions or justify accepting the complete owner.

A new inline helper returning the affected life pointer recovers ESI
preservation across the season-drop and phase-restart calls. It nevertheless
changes collision allocation and leaves statistics wrong; it is restored.
Combining it with the flag expression or ternary dialogue selection does not
recover the complete original. Preserve the return-flow trial rather than
repeating the earlier plain life-pointer attempt.

Other restored forms cover a scoped life reference, named current-life read,
branch-local statistics credit, an early-return dialogue helper and an explicit
local owner pointer. None is retained merely for a smaller extent or a better
diagnostic score. No new helper, header change, register constraint, padding,
acceptance exception or compiler option remains.

## Static regression

The full canonical replay retains **890 exact, 65 mismatch, 260 incomplete**,
**175,386 exact primary bytes** and **955 unchanged units**. All prior exact
owners and the other 1,214 annotation results/diagnostics remain unchanged,
apart from current build identities. No Boss unit is added.

Complete PE/PDB regression preserves all other **1,718 candidate owners**
byte for byte (**524,938 bytes**), every candidate address, every other extent
and all base relocations outside this owner. Only `src/Enemy.cpp` retains game
source changes; `Enemy.h` is unchanged. Final incremental PDB age is **430**,
source input
`b6676dada1acc3f517c2070de87d75d3308c774a8025fb81cc8dcd70d89f98c0`.
Source-origin review remains open; Factory acceptance is not submitted.

Keep `.analysis/boss-damage-exact-work/`: baseline/final five-artifact images,
canonical reports, original-only CFG script/report, complete logic/motion
packets, all failed source snapshots/build logs, `TRIALS.md`, `suffix-shapes.json`,
diagnostic diffs and `regression.py`/`final-regression.json`. Diagnostics grant no exact
credit. All source trials and builds are incremental and static.


## Later statistics-result trial

From `132f12a`, an ordinary inline helper returns overkill credit and the caller
then updates shot-damage statistics. The complete Boss owner becomes 2,185
bytes against 2,207 original bytes and is rejected. Full code packets show
two original additions to manager offset `0xAC`, at parent offsets `0x338` and
`0x347`; the candidate has one shared addition at `0x33A`. Register/life and
collision differences also remain. Returning a scalar credit loses the original
branch duplication and is not a solution merely because it inlines.

`Enemy.cpp` is restored byte for byte. Keep `.analysis/music-comment-join-work/`,
including the complete logic/motion packets and statistics-write diagnostic.
A conditional-selection variant was prepared but not compiled at that
checkpoint. It is subsequently built and rejected at 2,183/2,207 bytes;
see the [WinMain and Boss follow-up](winmain-and-boss-static-followup.md).
The shared-constructor exact result is reviewed
[separately](updatefunc-construction-exact.md).

A later ordinary inline helper writes shot statistics directly and returns
void. With conditional dialogue suppression, it preserves both additions but
still loads the manager early and exchanges damage registers; the complete
candidate is 2,199/2,207 bytes and is restored. Keep
`.analysis/boss-statistics-call-work/`. The subsequent
[dialogue position-array result](dialogue-position-array-exact.md) changes no
Boss logic bytes and adds no Boss exact credit.
