# ECL boss exception-cleanup graph

`EnemyData::ecl_run_over_300` at `0x0041DCB0` owns one EH3 cleanup path for
its inlined `new Fog(0, 0x11, 0)` operation. The original cleanup aggregate at
`0x0048A6B0` is 58 bytes: an 18-byte sized-delete funclet followed by a
40-byte EH3 handler at `0x0048A6C2`. The target handler checks the cookie and
EH state at frame-relative offsets `-0x484` and `-4` respectively. Its one-state
FuncInfo is at `0x0049B274` and its unwind-map entry follows the 36-byte header.

The linked candidate keeps the same 18+40-byte action/handler shape in the
`EnemyEcl.obj` PDB contribution. Its saved Fog pointer, cookie and state are at
different frame offsets (`-0x40c`, `-0x470`, and `-4`) with the current
case-local spell buffer and direct Fog allocation. The pointer offset is
verified against the actual `mov [ebp-0x40c], eax` after allocation and the
matching load in the sized-delete funclet; it is not inferred from the target
frame. Its unwind-map record
precedes the FuncInfo header in the 44-byte data contribution. The review
checks the complete target parent extent, both complete EH aggregates, the
source-qualified PDB contributions, all five instruction fields, and the
independently bound sized-delete, cookie-check and frame-handler calls. It does
not treat the parent function as exact; the main owner still requires its own
strict linked comparison.
