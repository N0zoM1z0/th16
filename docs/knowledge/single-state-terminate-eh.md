# Complete single-state terminal graphs and array deletion

Reviewed 2026-11-12. Arcfile close and the UpdateFuncRegistry scalar deleting
destructor each have one terminal unwind state, with different fixed flags.
Their complete graphs now pass. Independent sized/unsized array-delete
identities also resolve the complete audio buffer recreation owner. These
three primary owners add 956 exact bytes.

The later [sound review](sound-eh-vftables.md) resolves CSound destruction with
a separate empty node-12 frame and complete class table identities. It retains
both single-state terminal proofs below and refuses reuse of their nonempty
frames under the empty profile.

## Original scopes and private ownership

| Parent | Complete original | Reachable instructions | Original handler | Original FuncInfo / map | Flags |
| --- | --- | ---: | --- | --- | ---: |
| `Arcfile::close` | `0x00457060`, 189 bytes | 63 | `0x0048A9C0` | `0x0049B570` / `0x0049B594` | 1 |
| UpdateFuncRegistry scalar deleting destructor | `0x0045A3A0`, 162 bytes | 46 | `0x0048AA30` | `0x0049B5D0` / `0x0049B5F4` | 5 |

Original-only review reaches every parent instruction, accounts for the final
return and following alignment, and excludes interior inventory entries. The
registration PUSH, complete 27-byte handler and whole FuncInfo/map identify
the graph independently of candidate layout. The sole map entry transitions
to -1 through the previously reviewed `___std_terminate` at `0x00476B19`.

| Candidate producer | Parent | Complete handler | Complete data / FuncInfo |
| --- | --- | --- | --- |
| `Arcfile.obj` | `0x00414C80` | `0x0048A400`, 27 bytes | `0x0049AD30`, 44 bytes / `0x0049AD38` |
| `WinMain.obj` | `0x00473FC0` | `0x0048AB60`, 27 bytes | `0x0049B454`, 44 bytes / `0x0049B45C` |

Original metadata stores the full 36-byte FuncInfo before its eight-byte map;
the complete candidate PDB contribution stores the map first. The explicit
`single-state-terminate-v1` profile fixes each source/symbol/parent tuple,
extent and flag value. It checks both layouts, magic `0x19930522`, one state,
zero reserved fields and the terminal action. Handler fields are exactly
13/18/23, with one PE relocation at 18. Data relocations are exactly 4/16.
Source-qualified private roots, PDB modules, complete extents, permissions
and absence of overlapping or additional names are required.

Shared owner/map handling now serves the two fixed one-state roles and the
two earlier two-state destructor roles. No state count, flags, producer or
frame displacement is configurable. Both earlier proof dictionaries remain
identical. The complete runtime/SEH checks from the
[terminate review](terminate-destructor-eh.md) remain required in full.

## Synthetic source annotation correction

The registry destructor body is defined in UpdateFunc.cpp, but LTCG emits
the scalar deleting entry in WinMain.obj for its delete expression. The
previous synthetic marker in UpdateFunc.cpp selected the right symbol but
failed the strict primary source-owner check after the EH field resolved.
That refusal is retained in `.analysis/one-state-before-owner-correction.json`.

The marker is moved to the actual delete expression in WinMain.cpp; the
UpdateFunc.cpp comment now points there. These are comment changes only.
The primary Oracle continues to require the declared source's own PDB object;
there is no source override or relaxed ownership rule. The fixed profile now
declares WinMain.cpp and independently requires the complete deleting caller.
Synchronizing the source-file ledger changes the boundary input fingerprint;
canonical replay is refreshed after that update and the freshness gate passes.

Original WinMain owns 2,919 bytes and 725 reachable instructions. Its unique
direct deletion CALL is at offset 2,495, under the registry null check. The
complete 2,919-byte candidate caller has its corresponding unique CALL at
offset 2,493. The original caller hash, both full extents and both decoded
instruction boundaries are required. WinMain remains a complete mismatch;
this witness grants it no exact credit.

Both new parents save ESI/EDI without local words. Their complete 36-byte
registration places the encoded cookie at EBP-24, node minus twelve. Arcfile
writes state zero at offset 103 and has a seventeen-byte restoration ending
in RET at 188. The deleting destructor writes state zero at 43 and has a
nineteen-byte restoration ending in all three RET 4 bytes at 159. Every EBP/FS
use, state write and return is checked. Prefix relocations are 6/20; suffixes
have none. Other profiles retain their independently fixed frames.

## Complete array-delete chain and audio caller

| Runtime role | Complete original | Complete candidate | Pinned producer |
| --- | --- | --- | --- |
| Sized `operator delete[]` | `0x00475134`, 14 bytes | `0x00474BB6`, 14 bytes | LIBCMT:delete_array_size.obj |
| Unsized `operator delete[]` | `0x00475150`, 5 bytes | `0x00474E65`, 5 bytes | LIBCMT:delete_array.obj |

Pinned delete_array_size.cpp forwards the block to unsized array delete;
delete_array.cpp forwards it to scalar delete. The complete original
fourteen-byte frame forwards its first argument through the fixed CALL at
`0x0047513A`, then restores the frame and returns. The complete five-byte
callee tail-transfers to the independently bound scalar delete at `0x0047514B`.
Both entire candidate bodies and their sole REL32 fields at 7/1 are checked,
with no PE relocations. Runtime rows require both complete extents, pinned
library ownership and the unsized entry's original direct CALL witness.
The bytes following the original five-byte tail are neighboring code whose
ownership remains unreviewed; they are retained as such, without calling them
padding or appending them to the reviewed entry.

Arcfile close independently supplies this role: its entries allocation has
an element-count cookie four bytes before the array. It destroys that many
sixteen-byte entries, computes `count * 16 + 4`, and passes the allocation
start and full size to sized array delete. Ordinary whole-parent comparison
checks all of these body bytes and fields after the EH identity is established.

The same sized-delete identity resolves three existing fields in
`CStreamingSound::recreate_buffers`, original `0x00470BB0`, 605 bytes and 193
reachable instructions. The complete candidate at `0x00423350` passes every
byte, field and relocation. The source deletes the old buffer-pointer array
and notification-position arrays on both failure and normal paths. No audio
source changes occur. `CSound::~CSound` loses one unbound array-delete field
but retains two others and remains incomplete at its full 179-byte scope.

## Results and retained evidence

Canonical replay reports **872 exact, 65 mismatch and 278 incomplete** among
1,215 annotations, covering **164,495 exact primary bytes and 937 units**.
All preceding 869 exact results, 65 complete mismatches and 934 unit definitions
are retained. Their comparison details and both earlier two-state proofs stay
identical; only the image fingerprint and PDB age change in prior complete
records. Aside from the three new passes and the single CSound field removal,
all other incomplete records remain identical. Auxiliary code (54 bytes),
metadata (88 bytes), runtime bodies and the deleting caller grant no extra
primary credit.

**249 controls pass** across eleven suites: single-state EH (16), two-state
terminate EH (23), array constructor EH (18), member constructor EH (25),
allocation cleanup (23), saved-register EH (37), legacy empty EH (25),
AnmManager constructor EH (25), reviewed linkages (40), strict Oracle (14)
and focused audit (3). Controls mutate every new handler/data byte, every
array-delete byte on both sides, original fields after hash updates, frame
states, full extents, private names, modules, caller witnesses and relocations.
Wrong source producers and RET 4 changes are refused; ordinary body changes
still fail full primary comparison. The cross-profile allocation test now
changes the actual cookie value when a later profile also uses node-12.

The annotation correction is freshly rebuilt incrementally. All 1,719 linked
function entries, extents, raw hashes and PDB producer records remain identical
to baseline. Current artifacts match the new receipt and all 192 dependency
stamps validate. The source input is
`356af008e8064e7f8080f6c112145362eea142d1955f371a989e5b65034aca5f`.
The current build graph is retained. Source-origin review and formal Factory
acceptance remain open.

Original-only scopes and their reproducer are
`.analysis/one-state-original-scopes.json` and
`.analysis/review-one-state-originals.py`. Complete graphs, callers, raw
payloads, producers, fields and relocations are
`.analysis/one-state-caller-scopes.json`, reproduced by
`.analysis/review-one-state-callers.py`. Artifact/regression proofs are
`.analysis/one-state-{artifact,regression}-check.json` with matching
`check-*.py` reproducers. Build, audit and control logs and summaries use
`.analysis/one-state-*`; the pre-edit baseline is
`.analysis/one-state-terminate-baseline/`.
