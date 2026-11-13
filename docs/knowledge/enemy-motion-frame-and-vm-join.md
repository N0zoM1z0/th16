# Enemy motion frame and VM lookup join

Starting checkpoint: `2c5b015`. The complete `EnemyData::step_interpolators`
at `0x0041BB50` now compares as **mismatch, 1,682/1,692 bytes**, instead of
incomplete with a 1,691-byte candidate. **No exact credit is added.** All
48 linked fields bind independently: 20 REL32 and 28 DIR32. No game execution,
native fixture or instruction emulation is used.

## Retained source and original witnesses

The original owner has 421 instructions, all reachable in an original-only
CFG traversal, 22 calls and returns at offsets 1638, 1664 and 1691. Four
following `CC` bytes are outside the owner; the next entry is `0x0041C1F0`.
Its full SHA-256 is
`9ca261d7e40d56d4e50cb7634ac8ef5c1285affb61b0904a1dbc2cf87d4952f3`.

The creation sequence stores child-mode value **8** at `0x0041C0A5`, into VM
offset `0x51C`. The existing four-argument inline creator writes zero. A
separate explicit-mode overload reproduces the observed sequence without
changing that four-argument implementation. This overload is reconstruction
source organization, not an identified original out-of-line method or proof
of its original signature. The meaning of additional mode bits is not inferred.

Using the inline creation path recovers the original **0x38-byte local frame**
and separate zero-vector slot. Constructing the zero position **before** the
animation-file lookup then recovers the original VM/manager register sequence:
the VM moves from EAX to EDX, the animation index uses ECX, and the manager
loads into EAX. All subsequent GP instructions agree under full comparison.

A typed member-function-pointer call with a named initialized handle preserves
the original camera X sequence. A direct call, or assigning the returned
handle straight to the member, changes X operand order in this context. The
retained source keeps the named handle and selects the five-argument overload
explicitly. It names no physical registers and adds no register/alignment
constraint, floating-point pragma, padding or dead local.

An initial optional-parameter version changes the still-unaccepted 2,178-byte
Player options owner. The separate overload keeps the four-argument source
body byte-identical and restores that complete native owner. The retained
1,692-byte motion payload is raw-identical to the saved first complete image;
the collateral Player change is not retained.

## Remaining difference

Only the original camera Y load/add pair remains different, within the
13-byte window at offsets `[0x36C,0x379)`:

```asm
; Original
movss xmm0, [camera_delta_y]
addss xmm0, [esi+4]
; Candidate
movss xmm0, [esi+4]
addss xmm0, [camera_delta_y]
```

Ten normalized bytes differ. This operand exchange is not excused or masked.
Position memcpy, scalar-return helpers, D3DXVec3Add, a named accumulator and
separate handle assignment do not close it. Full vector addition adds packing
and temporary instructions. SSE intrinsic trials change registers, scheduling
or extent; all are restored. No intrinsic remains in maintained game source.

Three additional laser-pointer lifetime/control-flow trials are also restored:
an outer EX declaration and a single shared advance label produce the same
complete 1,748 bytes; an explicit index snapshot produces 1,752 bytes.

## Complete static regression

Canonical totals are **890 exact, 66 mismatch, 259 incomplete** among 1,215
annotations, with **175,386 exact primary bytes**. A new comparison unit records
this complete mismatch, giving **956 units**. The boundary ledger changes only
this owner's state from provisional to strict-compared; all target addresses,
sizes and inclusive span ends are unchanged. That state is not exact credit.

All previous 890 exact results, the other 1,214 annotation results/diagnostics
and all previous 955 unit definitions/addresses are unchanged. All other
**1,718 candidate owners** remain raw-identical (**525,444 bytes**), with
unchanged addresses/extents and relocations outside this owner. Every raw
`.text` byte outside the final 1,692-byte owner is unchanged as well.

Final incremental PDB age is **462**, source input
`129507e1a5cf66bdd4fa39501a6397298df804dbbd706f11e18246383221c1ef`.
Source-origin review is open; Factory acceptance is not submitted.

Keep `.analysis/enemy-vm-return-work/`: original CFG, full logic/motion packets,
first-complete/isolated/final images, focused and canonical reports, rejected
sources and build logs, `TRIALS.md`, four-argument source proof, boundary-ledger
check and complete regression. Also preserve
`.analysis/laser-pointer-lifetime-work/` for the restored laser trials.
