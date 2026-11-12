# ECL angle and orbit initialization

This continuation starts at `90e049a` and works inside the large
`EnemyData::ecl_run_over_300` dispatcher at `0x0041dcb0`. It retains the original
angle-interpolator field order and vector copies for circular and elliptical
interpolation. The dispatcher remains incomplete; no comparison profile,
binding, owner boundary or exact-credit rule changes.

Preserve `.analysis/ecl-angle-work/`, including its final image and source,
complete dispatcher packets, compiler layout/enum probe, native fixtures,
rejected forms and pre-rebuild evidence.

## Angle interpolation

Instructions 441/443 now explicitly initialize the angle interpolator in the
original order: end time, method, both zero tangents, initial angle, goal, and
timer reset. The shared `InterpFloat::start` writes the initial angle earlier.
The retained source generates the original field-write sequence while keeping
the goal's `delta + initial` floating operand order.

The original reads angle argument 2 before checking duration. Positive durations
read argument 0 again during initialization. Mode 7 negates mirrored angles and
uses zero for sentinel fallback; other modes mirror through two normalization
calls and fall back to the current angle. Both paths apply the shortest-turn
calculation. These existing behaviors remain, including the double-precision
sentinel comparison and the final float addition.

A trial overwriting `angle` with the delta changed the final ADDSS operands and
moved the initial write before end time. It was restored despite producing fewer
bytes. The retained angle case slice is still 482 bytes against 531 original
bytes. Pointer retention, branch merging and intermediate spills remain different.

## Circular and elliptical interpolation

`InterpFloat2::start` now assigns each tangent as a complete `D3DXVECTOR2`.
The compiler emits integer word copies from the live `g_zero_vec2` object,
recovering the original copying operation in instructions 409/411 and 421/423.
The previous component assignments generated scalar floating loads and stores.
The current compiler still merges the two source reads and schedules some
initial-value writes differently; the original performs four component reads.
This is partial source progress, not an exact initializer or dispatcher.

The circular case slice changes from 531 to 518 bytes against 507 original
bytes; the elliptical slice changes from 824 to 809 against 780. Slices are
spatial diagnostics inside the dispatcher and have no independent acceptance
authority. The complete packet contains three dispatches, all 182 target slots,
the 702-byte opcode map and alignment: 21,408 original / 21,316 candidate bytes,
compared with 21,348 candidate bytes at the preceding checkpoint. The smaller
total does not measure matching code. The candidate frame grows from `0x490`
to `0x498`, against `0x478` original bytes; this remains open.

The strict refusal now lists seven unbound fields instead of ten. Vector
assignment reduces six emitted `g_zero_vec2` references to four; a former
incidental decode inside the owned map no longer contributes another field.
The EH handler, four vector references, private sin/cos helper and BossDead
literal remain unbound. No independent symbol binding was added. The existing
switch proof also does not cover the original store between remap and dispatch.

## Native checks

The game-local Win32 debugger runs unmodified original and candidate images at
their preferred bases. Only fixture data is written; instructions, imports and
callees are not patched or stubbed. Complete calls check return value, stack
cleanup, preserved registers, floating controls and exception-chain restoration,
plus full enemy/context storage and declared resource/script data.

All **744 complete angle calls** agree: absolute/relative movement, mirroring,
modes 0/7/8/-1, nonpositive and positive duration, sentinel fallback, shortest-turn
boundaries, large angles, signed zero, NaNs, infinities, immediate and local
arguments, and three x87 precisions. Independent expectations cover unchanged
fields, flags, initialization and timers. Finite goals also have an independent
float-rounding model. NaN/infinite goal bits use the native original rather than
Python NaN arithmetic; the paired object comparison still includes every byte.

All **768 complete orbit calls** agree for all four circular/elliptical time
instructions, four durations, four interpolation modes, four parameter sets and
three precisions. The independent model checks full object state, sentinel/NaN
fallback, both timer initialization states, flags, centers and final coordinates.
Nonzero NaN/signed-zero tangent components check copies from the live vector.
Circular interpolation retains its center; elliptical interpolation restarts
around the current position even when already in a circular or elliptical mode.

Orbit geometry uses finite starting angles of zero, finite radii/ratios and
integer coordinates. Arbitrary rotated geometry is outside these fixtures.
These calls initialize interpolators and execute the existing position helpers;
they do not run subsequent interpolation frames, complete Boss scripts,
allocation, effects or resource startup.

The same final image also passes **1,157 movement**, **108 difficulty** and
**612 lookup** complete calls, **140 spell prefixes**, **42 animation prefixes**
and the spell-prefix negative control. The historical animation image retains
18 expected payload failures; the candidate retains none. Prefixes retain their
previous resource limitations. The final image passes 3,389 complete paired
calls and 182 prefixes in total.

The final incremental build uses PDB age 205. The isolated strict replay
preserves all 885 exact results and classifications, 169,575 exact primary bytes
and 950 retained units. `final-regression.json` verifies common PE/MAP/PDB/receipt
identities across reports and complete dispatcher packets. Source-origin review
remains open; Factory acceptance is not submitted.
The unit refresh changes only 529 candidate addresses; identities and accepted
scopes are unchanged.

One diagnostic ran before the header rebuild finished. `Context` refused the
stale receipt before reading an owner. Preserve
`vector-tangents-before-build-refusal.log`; use the final complete packet and
reports. The `before-comment/` image and reports precede a source-comment
correction. Its complete owner bytes equal the final packet, but its artifact
identities are historical and must not substitute for the final reports.
