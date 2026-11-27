# ECL boss exception-cleanup graph

`EnemyData::ecl_run_over_300` at `0x0041DCB0` owns one EH3 cleanup path for
its inlined `new Fog(0, 0x11, 0)` operation. The original cleanup aggregate at
`0x0048A6B0` is 58 bytes: an 18-byte sized-delete funclet followed by a
40-byte EH3 handler at `0x0048A6C2`. The target handler checks the cookie and
EH state at frame-relative offsets `-0x484` and `-4` respectively. Its one-state
FuncInfo is at `0x0049B274` and its unwind-map entry follows the 36-byte header.

The linked candidate keeps the same 18+40-byte action/handler shape in the
`EnemyEcl.obj` PDB contribution. Its saved Fog pointer, cookie and state are at
frame offsets `-0x40c`, `-0x470`, and `-4`, respectively, with the current
case-local spell buffer and direct Fog allocation. The pointer offset is
verified against the actual allocation store and matching load in the
sized-delete funclet; the cookie and state offsets are read from the emitted
EH3 handler loads. The original uses `-0x420`, `-0x484`, and `-4`. Returning the shot-origin helper's `D3DXVECTOR3` by value,
with the original `has_origin` true branch first and y loaded before the
branch, adds 32 bytes over the original output-pointer helper (21,296 to
21,328 bytes). The ET_ON direct-reference experiment then removes 16 bytes,
leaving a 21,312-byte owner and a 96-byte extent difference at the prior
checkpoint (whole-owner instruction-signature alignment 0.93995). Inlining the
shot-origin and EX-copy sequence into the line, infinite, and curve laser cases
adds 52 bytes, leaving a 21,364-byte owner and a 44-byte extent difference;
whole-owner alignment improves to 0.94294. Opcode 702 is 439/441 bytes and
opcode 711 is 401/394 bytes. The separate ellipse direct-field-store trial from
the earlier line-only variant grew the owner to 21,344 bytes and reduced the
extent gap to 64 bytes, but lowered whole-owner alignment to 0.93707. A later
ordinary-float-store trial on the all-inline build grew the owner to 21,380
bytes and lowered alignment to 0.94139; it too was restored in favor of the
volatile raw stores. The inverted
shot-origin condition ordering was 48 bytes larger but aligned worse (0.9379).
The values are measured from emitted builds, never inferred from the target
frame. Its unwind-map record
precedes the FuncInfo header in the 44-byte data contribution. The review
checks the complete target parent extent, both complete EH aggregates, the
source-qualified PDB contributions, all five instruction fields, and the
independently bound sized-delete, cookie-check and frame-handler calls. It does
not treat the parent function as exact; the main owner still requires its own
strict linked comparison.
