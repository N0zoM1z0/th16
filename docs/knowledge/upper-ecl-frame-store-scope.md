# Complete upper ECL frame-store ownership

Starting checkpoint: `cd97ed6`, PDB age 614. The complete original
`EnemyData::ecl_run_over_300` at `0x0041DCB0` is now formally registered as
**21,408 bytes**, including its tables. Four source trials are restored.
**No new exact credit or game-source change is retained.** The candidate remains
21,316 bytes with seven unbound linked fields and further body/frame differences.
No game execution, native fixture or emulation is used.

## Complete original owner

The former 19,976-byte inventory boundary covered only code. The complete
owner ends at `0x0042304F`, immediately before the independent entry
`0x00423050`, without overlapping another function candidate. It contains:

- **19,976 code bytes**, all **4,519 instructions** reachable from the entry;
- a 174-entry main target table and the complete **702-byte** opcode map;
- two zero alignment bytes and two four-entry difficulty tables;
- the sole return at `0x00422AB7`.

There are three guarded indirect jumps and **182 owned target entries**. The
complete SHA-256 is
`6c6f400ca422d9c14e06cb96d7656c71521a61c0f5e6e7dcc4693dab1c1afa49`.
The registration and entry-rooted traversal use original bytes; no candidate
extent or operand selects an original address. The tables, map and alignment
account for all **1,432 bytes** following the code.
The generated comparison-state ledger remains provisional because the
candidate is incomplete; scope registration does not grant a strict pass.

## Explicit frame-store profile

The original main dispatch is:

```asm
cmp eax, 701
ja default_case
movzx eax, byte ptr [opcode_map + eax]
mov dword ptr [ebp - 0x438], 0x88
jmp dword ptr [target_table + eax*4]
```

The existing adjacent-remap profile correctly refuses the intervening MOV.
The new **`compound-frame-store-v1`** profile explicitly declares its site at
parent offset 151. Existing compound records remain unchanged.

Admission requires the complete conventional x86 GS/EH prologue: established
EBP, three saved EH words, a positive aligned SUB ESP allocation and the
cookie sequence at EBP-16. The MOV must immediately follow the bounded remap
and immediately precede the reviewed dispatch. It must write exactly one
32-bit immediate to an EBP-relative local, with no segment or index register.
Its four bytes must fit inside the allocated local area and avoid the cookie
and EH words. The original allocates `0x478` bytes and stores at EBP-`0x438`.

The frame base must remain stable throughout the owner; only the initial base
establishment and terminal POP EBP immediately before a return are supported.
The remap result cannot be EBP or ESP. Direct branches/calls and every compound
table are checked against protected prologue and dispatch entries. All three
unsigned guards, every remap byte, each target and the exhaustive target-entry
relocations remain required. Unsupported interposed instructions remain refused.

The MOV's displacement, immediate and instruction bytes stay in executable
comparison. The profile introduces no instruction equivalence, byte mask,
padding exemption or linkage binding. The whole original hash remains mandatory.
The explicit record, boundary and verifier are part of the Oracle identity.

## Static controls

All **40 simple-switch and 39 compound-switch controls** pass. New controls
cover the full original owner, profile opt-in, altered/shortened prologues,
frame-base reassignment, early POP, register/arithmetic/byte stores, writes
crossing the allocation/cookie/EH boundaries, changed store constants,
direct/table guard bypasses, all three unsigned guards, map endpoints/interior,
alignment and truncated/expanded scopes. Every one of the **182 target-entry
relocations** is individually removed and rejected.

The structural positive fixture overlays original bytes with explicit table
relocations. It supplies no candidate PDB/source owner and receives no primary
credit. Actual different-sized game candidates continue to fail the complete
owner requirement.

The first simple-suite run exposed an older count assertion expecting 25
different direct-owner extents. Independent checks of the unchanged old
records against both PDB 614 and PDB 619 establish the same **24** extents.
That stale count and the explicit compound-profile membership assertion are
updated. Initial failures and the baseline comparison are retained; only the
final 40/39 runs are passing evidence.

## Restored source trials

Each trial retains the complete code and all three tables/map, including
relocations. Every complete trial candidate has **21,332 bytes**:

| Form | Finding |
| --- | --- |
| anmReset file staging and named main-script read | Recovers file-first argument preparation, with other handler changes |
| anmReset file staging alone | Shared exit and surrounding handler differences remain |
| Script assignment before clearing the directional flag | Recovers the native main-script load order, but retains the shared tail and changes other handlers |
| Embedded movement record selected by explicit byte offset | Retains indexed position access across getters; frame, shared exits and whole-body differences remain |

The first three alter movement arithmetic and/or flag-update instruction forms
outside the intended reset sequence. Their local recovery is insufficient for
retention. The offset form is distinct from the older velocity member-pointer
trial, but also fails the complete owner. All four are restored. A capture
attempt during the offset build was refused for stale inputs; its complete
packet was collected only after that same build terminated successfully.

## Final checkpoint

Canonical replay preserves **904 exact / 67 mismatch / 244 incomplete**,
**185,816 exact primary bytes**, all **971 unit definitions** and all **1,215
annotation results/diagnostics**. The upper owner still reports seven unbound
linked fields. Its candidate has 19,884 code bytes plus the full 1,432-byte
data suffix; its local allocation remains `0x498`, versus original `0x478`.
EH, vector, private-callee and string identities and source/layout work remain.
The other private `ecl_sincosmul` producer must not borrow the lower interpreter's
source-qualified identity.

All **1,719 source-qualified native owners (527,136 raw bytes)**, their
addresses/extents, base relocations and complete raw `.text` remain unchanged.
Only the original upper-owner boundary/ownership, verifier, controls and
documentation change. Final PDB age is **619**; source input remains
`ef45258398eb6fe5c3cb4fd560aed06455b5f5695cfb4d398602eb739e51ccc5`.
Source-origin review is open; Factory acceptance is unsubmitted.

Keep `.analysis/upper-ecl-case-work/`: baseline/final artifacts, all four trial
images/sources, complete scope/layout packets, registered original-only CFG,
registration JSON, initial/final control logs, preexisting count check and
canonical/progress/restoration reports. Retain the incremental build graph.
Nothing is pushed, published or deployed.

## Progress update (2026-11-15)

The current candidate `EnemyData::ecl_run_over_300` PDB contribution is **21,260
bytes** against the independently reviewed **21,408-byte** target owner. The
candidate contribution is 148 bytes shorter and is not an exact match. The
current decoded code spans are 19,825 candidate bytes versus 19,976 target
bytes; the remaining contribution tail is 1,435 versus 1,432 bytes, so the
three-byte data-extent difference is also still unaccounted for.

Two structural changes account for the latest progress:

- `LaserInfiniteInner` is split into an inline data-initialization base and an
  ECL-facing out-of-line constructor. This preserves the original constructor
  call in the large ECL dispatcher while allowing `LaserInfiniteInf` to
  initialize its embedded data before its `AnmVm` members. Both constructor
  owners now pass strict comparison (30/30 and 81/81 bytes).
- `MOVE_CURVE` and `MOVE_BEZIER` now branch to one shared interpolation tail,
  restoring a common reset/flag-clear path rather than duplicating it in both
  case bodies.

The candidate parent now reserves the same `0x478`-byte frame as the target,
and its GS-cookie handler displacement matches the target at `-0x484`. One
important EH difference remains: the fog cleanup pointer is at EBP-`0x438`
instead of EBP-`0x420`. The switch-case comparison still shows substantial
register-allocation and instruction-order differences, especially in the
movement/interpolation and high opcode groups. No strict exact credit is
claimed for this function yet.
