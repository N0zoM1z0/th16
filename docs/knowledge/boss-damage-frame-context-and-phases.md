# Boss damage frame context and phase transitions

This continuation starts at `dd3ba35`. It retains a planar distance vector in
`Player::compute_damage_to_enemy` and exercises real Boss phase transitions.
The original and candidate now have the same alignment arrangement: Boss logic
realigns ESP to eight bytes; the damage callee does not. Neither complete owner
is exact. No compiler profile, calling convention, Oracle rule, linked identity
or original extent is changed.

## Retained source and complete owners

The circle/circle branch represents its XY difference with `Float2` instead of
two independent scalar locals. Depth does not enter the collision equation.
The radius sum, squared-distance comparison, source traversal and impact snapshot
remain in their established order. This is an ordinary D3DX vector constructor;
there is no alignment annotation, extra double, padding or register constraint.

This local representation also changes LTCG's treatment of the callers. In the
previous image, damage realigned its own frame while Boss logic did not. In the
retained image, both choices agree with the original. The first Boss locals and
their stack accesses consequently recover the original layout. This observation
does not establish the compiler's internal reason or the original source type.

| Complete owner | Original bytes | Previous candidate | Retained candidate |
| --- | ---: | ---: | ---: |
| `EnemyData::step_logic`, `0x0041c330` | 2,207 | 2,207 | 2,222 |
| `Player::compute_damage_to_enemy`, `0x00445a30` | 774 | 769 | 741 |
| Rectangle/rectangle collision, `0x004049c0` | 2,168 | 2,002 | 2,002 |
| Point-array collision, `0x00403a90` | 661 | 661 | 661 |

All four complete owners are decoded and retained in
`.analysis/boss-lifetimes-work/complete-scope/`, including their bytes, addresses,
extents and hashes. `Enemy.cpp` and `Collision.cpp` are restored byte for byte.
The existing XYZ impact snapshot and bounded source traversal remain intact.
Damage still retains the size pointer differently from the original's enemy ID;
loop placement, floating registers and other body differences remain unresolved.
Boss statistics and the inlining of the life-interrupt script restart also differ.

A secondary source-shape diagnostic compares the first **563 complete bytes**
of Boss logic, binding all 14 external fields through existing identities. This
covers shield handling, die-on-hit setup and the time-interrupt restart. The
original fixed PE lacks base relocations, so its absolute operands are enumerated
from the fully decoded instructions and checked against the existing destinations.
No fields are masked. The following conditional branch has a different internal
displacement because the rest of the owner differs. A proposed 779-byte diagnostic
correctly refused that difference at offset `0x235`. This prefix is not an
independent owner and earns no exact credit; complete-owner comparison remains
mandatory.

## Complete phase execution

The new native suite contains **400 paired complete calls** of Boss logic after
actual executable CRT startup. It uses the existing WinMain breakpoint protocol
and the original game callees, imports and EnemyInf vtable. It supplies valid
script tables and contexts; no game function is patched or replaced.

The matrix covers:

- Time and life interrupts in slots 0, 3 and 7, with equality, not-yet-due and
  past-boundary cases. Life cases run the actual damage and interrupt routines.
- Three sorted subroutine names and missing names before, within and after the
  table. Searches, primary-context reset and script loading run normally.
- A future instruction, script deletion, outermost return after stack allocation,
  and a phase program that executes ECL 511, 564 and 565 through the real large
  dispatcher: life initialization, rotation and bomb-damage multiplier.
- Ordinary and survival spell states, the 59/60-frame bonus boundary, chapter
  accounting, half/one-and-a-half game speed, and three x87 precisions.

Independent expectations check complete EnemyInf, Player, Gui, Spellcard,
EnemyManager, script arena and relevant Globals storage, including canaries.
Both images must satisfy those expectations before their normalized observations
are compared. The sole image-dependent fixture field is the existing EnemyInf
vtable address; each image must preserve its own verified value. The runner also
checks return value, preserved registers, stack cleanup, floating controls and
exception-chain restoration.

The original confirms that a missing subroutine leaves index `-1` and instruction
offset **0**. Executed delete/outermost return leave **both** location fields at
`-1`. The model distinguishes these paths. Its first drafts were refused on the
original before candidate execution: interpolation layout, timeout flag, location
field order and missing-name offset assumptions were corrected using the typed
historical-compiler probe and observed original state. Preserve the failed logs
and model snapshots; they are not passing suites.

A negative control calls the existing original no-op at `0x0041a4a0` instead of
Boss logic. It returns zero but fails the required phase-state model on the
original, before any candidate fixture is produced. This prevents a zero return
or a loader stop from standing in for actual phase execution.

Async lists are empty. These fixtures do not cover freeing allocated asyncs,
resource creation, effects, real deaths or complete shipped Boss scripts.

## Other trials and verification

The following forms are restored:

- Dialogue ternary and explicit non-null clearing: both produce the same
  2,207-byte historical-context body with swapped damage registers.
- Nested active/timer filtering: separates the skip blocks without recovering
  the original loop placement.
- A three-component difference: gives a 774-byte damage owner and recovers
  additional XY/radius scheduling, but retains the opposite alignment choices.
- Earlier `life_damage` initialization: gives a 2,220-byte Boss owner but changes
  the initial damage register away from the original.

Planar constructor, separate component assignments and brace initialization all
produce identical complete code. The ordinary constructor is retained. An early
scope request during an unfinished build refused the stale receipt; the final
scope packet is collected only after the completed build.

The final image passes **2,596 complete native calls**: 400 new phase cases and
the preceding 2,196 Boss, damage, geometry, impact, collision and shield cases.
The **204 collision/shield prefixes** also pass. The earlier historical controls
still expose 96 impact-output and 27 collision payload failures, with zero in the
retained image. Observation controls, old/new protocol controls and both exception
chain modes pass. The first copied chain-control invocation lacked its required
fixture files and failed to open the job; copying the preserved original fixtures
and verifying their hashes resolves that setup failure.

The final source input is
`3211bb688256a2c841cfbb37df81728faa89b52e2c8e5f70de63448764d58f23`,
PDB age **237**. Only incremental builds were used. The full strict replay and
progress check pass, preserving **885 exact owners and 169,575 exact primary
bytes**. Boss logic changes from mismatch to incomplete because its complete
candidate extent differs; its comparison unit is removed by the normal writer.
Totals are **885 exact / 65 mismatch / 265 incomplete**, with **950 units**.
Original owner geometry is unchanged. The generated ledgers describe this
classification change and the relinked addresses; none grants new exact credit.

Keep `.analysis/boss-lifetimes-work/`, especially `final-image/`, complete scopes,
the full phase fixtures and raw output, the prefix diagnostic, source trials,
typed layout probe, protocol/negative controls and `final-regression.json`.
The regression checker authenticates common artifact identities, all runtime
counts, source restorations, original geometry and preservation of every exact
owner. Source-origin review remains open; Factory acceptance is not submitted.
No repository contents were pushed.
