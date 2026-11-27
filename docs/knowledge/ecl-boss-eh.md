# ECL boss exception-cleanup graph

`EnemyData::ecl_run_over_300` at `0x0041DCB0` owns one EH3 cleanup path for
its inlined `new Fog(0, 0x11, 0)` operation. The original cleanup aggregate at
`0x0048A6B0` is 58 bytes: an 18-byte sized-delete funclet followed by a
40-byte EH3 handler at `0x0048A6C2`. The target handler checks the cookie and
EH state at frame-relative offsets `-0x484` and `-4` respectively. Its one-state
FuncInfo is at `0x0049B274` and its unwind-map entry follows the 36-byte header.

The linked candidate keeps the same 18+40-byte action/handler shape in the
`EnemyEcl.obj` PDB contribution. Its saved Fog pointer, cookie and state are at
frame offsets `-0x40c`, `-0x46c`, and `-4`, respectively, with the current
case-local spell buffer and direct Fog allocation. The pointer offset is
verified against the actual allocation store and matching load in the
sized-delete funclet; the cookie and state offsets are read from the emitted
EH3 handler loads. The original uses `-0x420`, `-0x484`, and `-4`.

Returning the shot-origin helper's `D3DXVECTOR3` by value, with the original
`has_origin` true branch first and y loaded before the branch, adds 32 bytes
over the original output-pointer helper (21,296 to 21,328 bytes). The ET_ON
direct-reference experiment then removes 16 bytes, leaving a 21,312-byte owner
and a 96-byte extent difference at the prior checkpoint (whole-owner
instruction-signature alignment 0.93995). Inlining the shot-origin and EX-copy
sequence into the line, infinite, and curve laser cases adds 52 bytes. Reusing
`radial_speed`, `radius`, `ellipse_angle`, and `ellipse_ratio` as their final
fallback-adjusted goal values then removes 16 bytes, leaving a 21,348-byte
owner and a 60-byte extent difference (36 bytes net growth from the 21,312-byte
checkpoint); whole-owner alignment is 0.942702. This natural local reuse also
moves the emitted cookie slot from EBP-`0x470` to EBP-`0x46c`; the Fog pointer
remains at EBP-`0x40c` and the EH state at EBP-`4`. `moveEllipseTime` shrinks
from 804/780 to 796/780 bytes and from 169 to 168 instructions. Opcode 702 is
439/441 bytes and opcode 711 is 401/394.

The remaining dispatch frontier is compiler-sensitive. `moveAngleTime` is
502/531 bytes (110/115 instructions); `moveEllipseTime` is 796/780 bytes
(168/169 instructions). For `moveEllipseTime`, Ghidra's target decompilation
shows each sentinel-checked radial/ellipse argument being overwritten with its
fallback-adjusted value and then used as the goal. Reusing `radial_speed`,
`radius`, `ellipse_angle`, and `ellipse_ratio` in place matches that lifetime
more closely than four separate `goal_*` locals. The candidate case falls from
804 to 796 bytes and the complete owner from 21,364 to 21,348 bytes. Register
hints on the five parsed float arguments did not change the build; ordinary
local declarations are retained.

`diffF` is not missing 26 bytes of logic. The target's switch table at
`0x423040` sends Easy (entry 0) to `0x4207f3`, a 26-byte, six-instruction
block. The candidate's case-local table at `0x4398f4` sends Easy to
`0x438ef2`, also a 26-byte, six-instruction block. The candidate's remaining
three difficulty branches are inline, giving 163 + 26 = 189 bytes and 38 + 6
= 44 instructions, exactly the target's 189-byte / 44-instruction case total.
The apparent contiguous-case deficit is only block placement.

Several source-shape trials on `moveAngleTime` were measured and discarded.
A single angle local with branch-local volatile self-stores reached 537 bytes
and a 21,396-byte owner (alignment 0.942297). Moving the volatile store after
the branch reached 522 bytes and a 21,380-byte owner (alignment 0.941945).
A Ghidra-shaped single-local form without volatile stores reached 493 bytes
(alignment 0.938165); making the local itself volatile grew the case to 576
bytes and the owner to 21,444 bytes (alignment 0.938663). A volatile
`angle_for_delta` local reached 552 bytes and a 21,412-byte owner. Register
hints on `angle`, `angle_for_delta`, and `initial` did not change codegen. The
two-local, branch-local-store source remains the best measured `moveAngleTime`
form, but is not an exact match. Ternary radial-goal expressions and extra
`register` hints had no useful code-size effect. Ordinary vector-field assignments for the
ellipse interpolator changed the owner to 21,428 bytes and invalidated the
reviewed cleanup frame, so the raw volatile field stores remain. The earlier
line-only direct ellipse-field trial also aligned worse (0.93707); a later
all-inline ordinary-float-store trial reached 21,380 bytes and alignment
0.941385. The inverted shot-origin condition ordering was 48 bytes larger and
aligned worse (0.9379).
The values are measured from emitted builds, never inferred from the target
frame. Its unwind-map record
precedes the FuncInfo header in the 44-byte data contribution. The review
checks the complete target parent extent, both complete EH aggregates, the
source-qualified PDB contributions, all five instruction fields, and the
independently bound sized-delete, cookie-check and frame-handler calls. It does
not treat the parent function as exact; the main owner still requires its own
strict linked comparison.
