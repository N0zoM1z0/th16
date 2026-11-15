# Complete Gui destructor exact comparison

The complete `Gui::~Gui` owner at `0x00427A20` now passes the strict Oracle:
**640 bytes, 172 instructions and 40 linked fields**. Its existing natural C++
source already produces the matching body. This checkpoint resolves its private
exception-handler identity; it changes no game source or compiler options.
Source-origin review remains open and Factory acceptance is not submitted.

## Original frame and complete private graph

Original-only decoding and CFG traversal cover all 640 bytes and all 172
instructions. Every branch stays on an instruction boundary, every instruction
is reachable, and the sole RET is at offset 639. The next inventoried function
starts immediately at `0x00427CA0`. No prefix comparison or inferred padding is
used as the primary extent.

The registration PUSH selects `0x0048A710`. Its complete 27-byte handler reads
the encoded cookie at node minus 28, checks it through the independently bound
security-cookie routine, loads FuncInfo at `0x0049B2C4`, and transfers to the
independently bound `___CxxFrameHandler3`. Five INT3 bytes follow the handler.
The complete 36-byte descriptor is exactly
`19930522 0 0 0 0 0 0 0 5`; there is no unwind action or terminate state.

The original frame reserves twelve bytes and then saves EBX, ESI and EDI.
Its registration node is EBP minus 12. The encoded cookie therefore occupies
EBP minus 40, or node minus 28. This differs from the earlier one-local-word
profile. The new explicit
`empty-eh3-three-locals-saved-ebx-esi-edi-v1` profile fixes the entire reservation,
save sequence, cookie check, FS registration and final restoration. Local word
count is recorded separately from reservation-instruction length. Whole-parent
checks retain the reserved-slot, FS-reference, EBP-write and return restrictions.
Neither the cookie displacement nor frame shape is configurable in the record.

| Original owner | Extent | SHA-256 |
| --- | ---: | --- |
| Parent `0x00427A20` | 640 | `69cb9d5c426203b636fb4702f0686f888f27ef981d2b107903361687160c5118` |
| Handler `0x0048A710` | 27 | `6bd0d965bd85c1da553e232028a9ad67791c4716e56223a995750c44fb89a76a` |
| FuncInfo `0x0049B2C4` | 36 | `deefb3473c3645d1b0e64473dc4d9122bd804dbeee0601d27662e64da29238e5` |

## Candidate ownership and replay

At PDB age 362 the complete parent is `0x00437070`. Parent-qualified private MAP
names select the handler at `0x0048A310` and descriptor at `0x0049B048`. Their
complete PDB contributions are 27 and 36 bytes, in the same `Gui.obj` module as
the unique public, complete 640-byte parent. Other contributions, interior names,
wrong producers and overlapping ownership remain excluded.

Both complete handlers and descriptors undergo the fixed graph checks. The
candidate prefix has exactly its handler and security-cookie relocations at
offsets 6 and 24; its restoration has none. The private handler has exactly one
relocation at offset 18; the descriptor has none. Ordinary complete replay then
compares every parent byte and all 40 fields, including the critical-section
storage addends, VM calls, loops and cleanup paths. The 27/36 auxiliary bytes
receive no primary credit. No parent body mask or target-specific byte exception
is added.

Full replay reports **887 exact, 65 mismatch and 263 incomplete** among 1,215
annotations: **171,563 exact primary bytes and 952 retained units**. All previous
886 exact owners and all 951 previous unit definitions are preserved; candidate
addresses are unchanged. Only this owner's classification changes.

All **134 static controls** pass: saved-register EH 76, legacy EH 25, single-state
EH 19 and strict Oracle 14. Controls reject altered local reservations and save
orders, wrong cookie slots, state/frame writes, wrong private owners, descriptor
reuse from `GuiMsgVm`, incomplete contributions, wrong relocations and scope
overrides. An ordinary body mutation still fails byte comparison after a valid
EH graph review. No game execution or dynamic test is performed.

## Restored geometry trials

The same continuation tested five natural geometry forms and restored all of
them. The complete rectangle owner remains 2,155 versus 2,168 original bytes;
the standalone point owner remains 651 matching bytes out of 661. None receives
new credit.

| Trial | Static result and reason for rejection |
| --- | --- |
| Group the second rectangle's half extents in `Float2` | 2,149-byte rectangle owner; reverses the original first/second radius square-root order |
| Name the two radius results separately | 2,155 bytes; the compiler still reorders the pure square-root calls |
| Component-wise rotated output, X first | Complete point owner falls to 645 matching bytes |
| Component-wise rotated output, Y first | Complete point owner reaches 652 matching bytes; register encodings still differ |
| Component-wise input and Y-first output | Same rejected 652-byte agreement; no whole-owner exact |

Separate source statements do not establish pure intrinsic evaluation order.
Do not repeat these forms or add floating-point pragmas, padding or dead locals
to force register allocation. The previous edge-table cursor/GUID alias remains
unaccepted, as recorded in the rectangle review.

## Retained evidence

`.analysis/rectangle-exact-work/` preserves the PDB 356 baseline, PDB 362 final
artifacts, all five restored trial sources and complete geometry packets,
original-only Gui CFG review, complete graph inventory, diagnostic byte forecast,
focused actual exact report, full audit/progress logs, static-control logs and
the complete baseline regression record. The forecast is diagnostic only; the
focused and canonical strict replays establish the result.

The source input remains
`cfbea2fb7262af493ea44cc4005f42eccf2841c09b9cc83bee4cdb28c67aa7a3`.
The existing incremental build graph is retained. No cold build, cleanup,
deployment or remote publication occurs.
