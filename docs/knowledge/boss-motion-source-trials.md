# Boss and projectile motion source trials

The later [complete spellcard frame update](spellcard-frame-update-exact.md)
closes the spellcard owner as exact. Earlier counts and open items below are
historical. The additional offscreen review at the end starts from `7e363a0`.

This investigation starts at `0d53abd`, with 883 exact, 65 mismatch and 267
incomplete annotations. It changes no Oracle rules, compiler profiles, owner
boundaries or relocation treatment. The private evidence directory is
`.analysis/enemy-motion-work/`; it retains source snapshots, complete-owner
disassemblies, build logs and isolated strict reports.

## Retained spellcard candidate

`Spellcard::on_tick_body` at `0x00417930` owns 650 bytes. Its work includes bonus
decay, the scaled timer, moving the spell title away from the player, smoothing
the boss marker, updating its animation and ending the early-bomb state.

Representing the marker's planar delta as `Float2`, while keeping the depth
delta scalar, retains the complete 650-byte owner. The isolated strict replay
improves from 437 to 451 matching bytes. It remains a **mismatch**, with no new
exact function or primary-byte credit. This is a candidate representation, not
evidence that the original source used this particular type decomposition.

The original loads the scaled timer's float frame into XMM0 before adding the
speed in XMM1; the candidate folds the load into the addition in XMM1. The
remaining smoothing differences include the allocation of the y and z results
and instruction scheduling. Branch encodings and loop alignment remain part of
the complete comparison.

Rejected spellcard forms:

| Form | Complete candidate | Observation |
| --- | ---: | --- |
| A three-component vector delta and vector accumulation | 692 bytes | Smoothing instructions agree diagnostically, but a new security cookie and frame refuse the owner |
| A leaf smoothing helper and nested timer | 650 bytes, 406 matching | Removes the cookie, but reuses marker loads where the target reloads them |
| A by-value delta helper | 676 bytes | Adds a cookie and changes title-loop traversal |
| Indexed scalar deltas and mixed timer | 650 bytes, 440 matching | Different timer stores and smoothing scheduling |
| A float-frame snapshot and planar vector | 650 bytes, 415 matching | Hoists the frame load before the speed checks |
| Indexed access to the planar delta | 650 bytes, 393 matching | Worse than the retained named-component form |

The baseline timer, early-bomb handling, title movement and bonus arithmetic are
retained. No safebuffers annotation or artificial alignment code was added.

## Enemy motion and damage

`EnemyData::step_interpolators` at `0x0041BB50` owns 1,692 bytes; its baseline
candidate owns 1,691. The complete function includes absolute and relative
interpolators, camera displacement, directional animation replacement, sprite
bounds and offscreen deletion.

The directional replacement writes **8** to `mode_of_create_child`. The common
`create_vm_inline` writes zero, so using it unchanged is not equivalent. An
experimental explicit child-mode parameter reproduces the target's 56-byte
local allocation and separate zero-vector slot, but the owner remains 1,691
bytes. VM register allocation and camera-add ordering still differ. That header
change and every other enemy-motion trial were restored.

Other rejected forms include a conditional vector reference (new cookie), a
branch-local zero constructor (1,690 bytes), separate origin and result vectors
(1,703 bytes), a function-entry origin (1,687 bytes), an outlined creation helper
(1,497 bytes), direct VM lookup (new cookie), a singleton accessor (no change),
camera scalar/indexed updates and reusing the VM variable across both lookups.
The helper and the non-inline creation path are not independent accepted owners.

`EnemyData::step_logic` at `0x0041C330` owns 2,207 bytes; the baseline candidate
owns 2,092. Expanding the once-called hit-sound helper recovers the target's
inlined boss-specific 200/900 life checks and removes that unreviewed private
call field. Reading
spell flags inside the short-circuit flash condition also recovers the target's
tail control flow. The combined trial still owns only 2,196 bytes and has
the wrong frame and earlier dataflow. It is not accepted and was restored.

Direct sin/cos calls, vector hitbox offsets and a rotation helper do not recover
the original frame. An unsuffixed half-size constant adds double arithmetic
absent from the target. A bomb-status snapshot hoists a read too early, while a
dialogue-damage ternary swaps the damage registers. Do not retain these forms
based on their lengths alone.

## Projectile and shared movement

`Bullet::step_ex_08` at `0x004162D0` owns 1,390 bytes; its candidate owns 1,382.
It normalizes directions to all four expanded screen corners, computes cross
and dot products, and decides whether the offscreen protection can end. The
target retains a multiply by 1.0 in the timer path and uses different local
slots and y-add ordering.

Its private sin/cos helper writes only x and y. A planar destination type is
consistent with those stores, but the tested type change leaves the parent at
1,382 bytes with incorrect slots. Moving all scalar declarations before the
vectors does not fix it. Both source and the experimental private-symbol type
binding were restored; the complete baseline helper remains exact.

`PosVel::step` at `0x00403110` remains a complete 700-byte mismatch with 696
matching bytes. Reversing only the circle constructor's x operands leaves all
four differences unchanged. Replacing just that constructor with a vector sum,
without the historical shake-timer change, retains 700 bytes but drops to 671
matching bytes by also changing wave scheduling. Both trials were restored.
No SIB, operand-order or floating-point difference was normalized away.

## Verification

Only the planar spellcard candidate is retained in maintained source. Failed
trial sources and the temporary shared-header and identity changes are restored
byte for byte before the final incremental build. The final full strict report,
standalone spellcard replay, restoration hashes and regression comparison are
retained in the private evidence directory. The full replay preserves all 883
baseline exact owners; its only comparison-result change is the spellcard's
437-to-451-byte improvement. Totals remain 883 exact, 65 mismatch and 267
incomplete, with 167,817 exact primary bytes and 948 retained units.
`scripts/progress.py` validates the current source, build, report and units.
Source-origin review remains open; Factory acceptance is not submitted. No
repository contents were pushed.

## Complete offscreen follow-up from 7e363a0

The original `Bullet::step_ex_08` is independently traversed over all **1,390
bytes**: all 327 instructions are reachable, with five calls and returns at
offsets 1371 and 1389. Two following `CC` bytes are outside the owner; the next
entry is `Bullet::cancel` at `0x00416840`. Original SHA-256:
`edf53f25364881c4123314bfd4588d6a572654278a9908733d7359202fe28b69`.

Five new source forms are rejected and restored. A typed member-pointer timer
call, a fractional-result helper with a const-reference amount and two Float4
cross/dot result objects all produce the **same complete raw 1,382-byte
candidate**. Do not repeat these forms expecting different local slots or a
retained multiplication. An inline Float2 direction result around the unchanged
private sin/cos helper produces 1,388 bytes with additional/reordered transfers.
An explicit scalar SSE product retains multiplication but adds frame
realignment and other changes, producing 1,490 bytes. No intrinsic, new helper
or header/type change remains in maintained game source.

Full static restoration preserves all **891 exact, 65 mismatch, 259 incomplete**
results, **176,036 exact primary bytes**, all 956 unit definitions and all
1,215 annotation results/diagnostics. All **1,719 complete candidate owners**
are raw-identical (**527,136 bytes**), with unchanged addresses/extents, all
base relocations and the entire raw `.text`. PDB age is **482**; source input
is unchanged from `7e363a0`. No new exact credit, game runtime or emulation.
Source-origin review remains open; Factory acceptance is not submitted.

Preserve `.analysis/bullet-offscreen-work/`: baseline/final five-artifact sets,
all five source snapshots/builds, complete packets, original-only CFG,
identical-owner check, canonical replay and restoration regression. The first
collector refuses an unverified companion tick scope before finishing its
packet index; use `baseline-verified/` and the focused offscreen collector.
