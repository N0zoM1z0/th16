# Exact masked-animation draw callback

`anm_on_draw_masked` at `0x004073A0` now passes the strict Oracle over its
complete **1,348-byte** owner. All 355 instructions decode, all **51 DIR32 and
6 REL32 fields** resolve independently, and all bytes match after translating
those fields. The same-start PDB contribution belongs to `src/AnmRender.cpp`.
No primary extent, comparison rule or compiler profile changes.

The function covers the arcade/fullscreen alpha-mask setup, rectangle vertices,
Direct3D state and draw calls, four child VMs, the overlay and final flush.
The game source was already matching; its last unresolved field was the
arcade rectangle's bottom coordinate, `464.0f`.

## Fixed original literal identity

The complete scalar is `00 00 E8 43` at `0x004946B4`, in read-only storage with
no pointer relocation. Its SHA-256 is
`1dfab8fd1d6bbf2a4b473ea29fa395087cbfb6f62ebd1dd5374fd1c905721254`.
The original instruction at `0x004074C4`, offset `0x124` in the callback, is:

```text
F3 0F 10 05 B4 46 49 00    movss xmm0, dword ptr [0x004946B4]
```

The callback's complete original hash is
`c05fe9e38537a36ec31cf0a57a7fbb861ecbe0af30da93d965403033abae1064`.
Its closed internal CFG reaches that read; its six direct external calls use
the existing flush, draw-VM and security-cookie identities. The original draw
callback table at `0x00491B2C` contains seven entries and identifies this entry
at index one, pointer slot `0x00491B30`.

There is another aligned identical four-byte payload at `0x0049486C`.
Payload equality alone cannot select the original storage. The new row in
`config/linkage-bindings.csv` fixes the MOVSS witness and uses the existing
`literal` profile for `__real@43e80000`. It does not add a generic alias,
interior-data exception, new profile or permissive comparison path. The
four auxiliary data bytes receive no separate primary exact credit.

## Static validation and checkpoint

The focused replay is **1,348/1,348 exact**, with zero differing bytes. The full
replay preserves all preceding 885 exact functions and changes only this
callback from incomplete to exact:

- **886 exact / 65 mismatch / 264 incomplete**, 1,215 annotations.
- **170,923 exact primary bytes**, up by 1,348; **951 units**.
- All 47 reviewed-linkage static tests pass. The new controls reject an
  instruction-interior witness, wrong mnemonic, shortened/expanded scalar,
  equal-content alternate storage and every scalar-byte mutation in both
  original and candidate views.

No game runtime or native fixture is executed for this result. Game source,
original boundaries and all previous units remain unchanged. The source input
is still `2790b5687dcf511fab390dea7d6299772fd015e6c966a192525f41222ecfe196`;
the incremental restoration build has PDB age **330**. Source-origin review is
open and Factory acceptance is not submitted.

Preserve `.analysis/boss-credit-work/`, particularly both complete images,
`masked-literal-original-evidence.json`, original/candidate owner packets,
`masked-effect-focused.json`, `literal-controls.log`, the full audit/progress
logs and `final-regression.json`. The early original-scope helper incorrectly
expected no external calls and then looked for constructor registration; the
versioned drafts are retained. The corrected evidence checks all six direct
calls and the actual read-only callback table.

All Boss, music-room and integer-vector source trials in this continuation
are restored. Their full strict results remain diagnostic evidence only. No
new Oracle binding is retained for the rejected anchor-array forecast. Future
work prioritizes complete static exact comparisons; the user's explicit
correction is to stop spending work on dynamic test suites.
