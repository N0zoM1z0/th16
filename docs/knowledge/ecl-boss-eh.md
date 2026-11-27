# ECL boss exception-cleanup graph

`EnemyData::ecl_run_over_300` at `0x0041DCB0` owns one EH3 cleanup path for
its inlined `new Fog(0, 0x11, 0)` operation. The original cleanup aggregate at
`0x0048A6B0` is 58 bytes: an 18-byte sized-delete funclet followed by a
40-byte EH3 handler at `0x0048A6C2`. The target handler checks the cookie and
EH state at frame-relative offsets `-0x484` and `-4` respectively. Its one-state
FuncInfo is at `0x0049B274` and its unwind-map entry follows the 36-byte header.

The linked candidate keeps the same 18+40-byte action/handler shape in the
`EnemyEcl.obj` PDB contribution. Its saved Fog pointer, cookie and state are at
different frame offsets (`-0x404`, `-0x474`, and `-4`) with the current
case-local spell buffer and direct Fog allocation. The pointer offset is
verified against the actual allocation store and matching load in the
sized-delete funclet; the cookie and state offsets are read from the emitted
EH3 handler loads. Returning the shot-origin helper's `D3DXVECTOR3` by value,
with the original `has_origin` true branch first and y loaded before the
branch, adds 32 bytes over the original output-pointer helper (21,296 to
21,328 bytes), leaving an 80-byte owner difference. It improves full-function
instruction-signature alignment from 0.9390 to 0.9398. The inverted condition
ordering was 48 bytes larger but aligned worse (0.9379). The values are
therefore measured from each emitted build, never inferred from the target
frame. Its unwind-map record
precedes the FuncInfo header in the 44-byte data contribution. The review
checks the complete target parent extent, both complete EH aggregates, the
source-qualified PDB contributions, all five instruction fields, and the
independently bound sized-delete, cookie-check and frame-handler calls. It does
not treat the parent function as exact; the main owner still requires its own
strict linked comparison.
