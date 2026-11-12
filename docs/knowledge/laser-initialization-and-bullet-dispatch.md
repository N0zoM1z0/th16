# Curve laser initialization and projectile command cursors

Reviewed 2026-11-12, continuing the complex gameplay work from `059efe5`.
Evidence is retained in `.analysis/bullet-ex-work/`. All comparisons use the
canonical Japanese v1.00a target and the pinned historical compiler.

## Complete curve laser initialization

`LaserCurveInf::initialize` at `0x004370a0` now compares exactly over its
complete **1,726-byte** independent owner, including linked fields. This covers
the animation setup, segment allocation and initialization, initial translation,
copied or new trajectory nodes, initial segment placement, timers and sound.
The baseline matched 1,677 bytes.

The source computes the translated X coordinate through its component pointer,
clears the consumed initial distance, commits X, then translates Y and saves
the starting position. The pointer expression preserves the original operand
load order. No padding, dead locals, forced registers, extent changes or
comparison normalization was introduced.

Moving the clear before the X calculation matched 1,705 bytes. Moving it after
the X store matched 1,712. A direct scalar expression put the stores in order
but reversed the floating operands, matching 1,710. The retained source matches
the whole owner; the trial sources and focused reports remain available.

## Large projectile dispatcher: still incomplete

`Bullet::run_ex` at `0x00413860` has a **5,436-byte** original owner. Its
candidate shrank from **5,988 to 5,500 bytes** when paired shooting and laser
commands advanced the command pointer itself before reading the second entry.
This recovers a full command pointer across the handlers instead of repeated
object-plus-scaled-index addressing. A nested laser subtype switch also recovers
the original selector structure and handler order; the infinite laser's packed
parameter uses the original signed shift before byte extraction.

The dispatcher remains incomplete and earns no exact credit. The remaining
differences include angle temporaries, constant lifetimes, frame layout and
handler construction sequences. The net 64-byte extent difference is not a
single missing block. Reordering the pointer/index declarations did not improve
the complete extent. An extracted command-readiness helper generated identical
code and was removed.

The original does not advance an unsupported laser subtype. Preserve that
behavior. Both supported laser subtypes copy all three position components;
the original defers the Z load rather than omitting it.

## Behavioral diagnostics and limits

`emulated-diff.py` runs the actual mapped original and candidate instructions
in separate instances of the locally available Unicorn 1.0.2 emulator. The
locked repository environment prepares the images and uses `strict_oracle.Context`
to fingerprint the source and artifacts before and after the diagnostic. The
child process uses the existing global Python emulator installation. No callee
or import is patched or stubbed; unexpected accesses fail the case.

The final diagnostic has **488 identical cases**, zero faults and zero state
differences. It compares the complete Bullet storage, RNG state, return/stack
discipline, preserved registers, canary and floating control settings. Inputs
include serial/parallel gating, active masks, loops, command chains, timer and
motion transforms, sentinel angles, player aiming, NaNs and explicit x87
precision settings. Sixteen cases exercise paired laser commands with a full
laser manager that declines allocation; their complete 856/888-byte parameter
snapshots also agree. Captures are taken before the actual manager-limit checks.

These are partial behavioral diagnostics, not native execution, exactness
evidence or full gameplay validation. Real resource loading, child bullet
creation, cancellation, enemy creation and laser allocation remain outside the
exercised paths. The failed Wine host prototypes could not reserve the original
image base because the process heap occupied it; they executed no game code.
The earlier 427-case diagnostic is preserved separately.

## Independent elliptical helper identity

The complete 32-byte private `sincosmul_ellipse` at `0x00426240` has a separate
`x87-sincos-ellipse-v1` profile. It uses separate X/Y radius stack slots and a
twelve-byte callee cleanup, unlike the existing isotropic profile. The proof
retains the existing requirements for complete original boundaries, exact
payloads, candidate MAP/PDB producer and extent, padding, linked fields and
relocations, source annotation, and a reachable original caller witness. The
witness is `0x0041d766` in the complete 500-byte drop owner at `0x0041d700`.

The drop owner remains a **455/500-byte mismatch** after independently binding
that call. Its scalar X product loads the opposite operand first. Vector
in-place scaling and a Float2 temporary did not recover it and were restored.
The helper proof grants no exact credit to its caller. Negative controls mutate
every byte of both helper images and reject wrong extents, radius profiles,
source identities and call boundaries.

Source-origin review remains open. Factory acceptance has not been submitted.
