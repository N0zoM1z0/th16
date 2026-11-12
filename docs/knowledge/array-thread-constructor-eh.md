# Complete array and thread-member constructor EH graphs

Reviewed 2026-11-12. Original registration and unwind edges identify two more
complete constructor graphs. BulletManager requires a separate fixed array
profile; EndingScriptVm extends the fixed member profile with its thread
member, cross-source destructor and RET 4. Their complete 181/551-byte primary
owners now pass. No game source or compiler artifact changes occur.

## Original scopes and candidate owners

| Parent | Complete original | Reachable instructions | Original code / handler | Original FuncInfo / map |
| --- | --- | ---: | --- | --- |
| BulletManager construction | `0x00411880`, 181 bytes | 53 | `0x0048A500`, 57 bytes / `0x0048A51E` | `0x0049B0C8` / `0x0049B0EC` |
| EndingScriptVm construction | `0x004197C0`, 551 bytes | 128 | `0x0048A640`, 41 bytes / `0x0048A64E` | `0x0049B200` / `0x0049B224` |

Original-only review accounts for every reachable parent instruction, final
return, following alignment and independently inventoried complete cleanup.
Each private aggregate consists of its whole action followed by the 27-byte
handler, then seven INT3 alignment bytes outside the aggregate. No standalone
owner or primary credit is assigned to the interior handler.

| Candidate source | Parent | Complete code / handler | Complete data / FuncInfo |
| --- | --- | --- | --- |
| `BulletManager.cpp` | `0x0041AB80` | `0x0048A4B0`, 57 bytes / `0x0048A4CE` | `0x0049ADD0`, 44 bytes / `0x0049ADD8` |
| `Ending.cpp` | `0x00427560` | `0x0048A670`, 41 bytes / `0x0048A67E` | `0x0049AF60`, 44 bytes / `0x0049AF68` |

Both same-start PDB contributions must have the declared source producer,
matching module, section permissions and exactly the parent-qualified private
roots: unwind funclet at zero, handler at action length, unwind table at data
zero and FuncInfo at eight. Other overlapping or public owners are rejected.

Original metadata stores the entire 36-byte FuncInfo before its eight-byte
map; the candidate's complete 44-byte owner stores the map first. Both layouts
are checked, including magic `0x19930522`, one state, flags one, zero reserved
fields and the sole state-zero transition to -1 through this parent's action.
Candidate metadata relocations are exactly offsets 4/16. Shared owner/map
checks admit only the reviewed action lengths 11/14/18/30; each caller retains
fixed action semantics, source roles and complete parent frame rules.

## BulletManager's first completed array

The complete thirty-byte action pushes the independently bound 120-byte
`Bullet::~Bullet` at original `0x004119B0`, count 2,001 and stride `0x1478`.
It reads saved `this` from EBP-16, adds `0x9C`, and calls the independently
bound array destructor iterator before returning. The first complete array
ends at `0x9C + 2001 * 0x1478 = 0x9FFE94`, the second array's starting offset.
Both parent array constructions must use these fixed ranges, element
destructor and independently bound constructor iterator. State zero is set
after the first array completes and before construction of the second.

The whole code aggregate has instruction fields at 1/25/43/48/53 and PE
relocations exactly at 1/48. Destructor/constructor iterators, cookie checking
and `___CxxFrameHandler3` all require existing independent runtime bindings.
The element destructor's complete candidate owner is `0x0041ACB0`, 120 bytes.

One local word and saved ESI/EDI put the cookie at EBP-28, sixteen bytes below
the registration node. The full 42-byte prefix includes saved `this`; the
17-byte restoration ends in the sole RET at offset 180. Every EBP/FS use,
state write and saved-pointer access is checked. Prefix relocations are 6/21;
the suffix has none. This profile admits only the fixed BulletManager role.

## EndingScriptVm's completed thread member

The complete fourteen-byte action reads `this` from EBP-16, adds the fixed
imm32 offset `0xD0` and jumps to `ThreadInf::~ThreadInf`. The member layout in
`Ending.h` agrees with the original offset. The destructor's fixed identity
is `src/Thread.cpp`, original `0x00402F20`, eleven bytes; its complete candidate
is `0x00472680`, eleven bytes. Substitution of the parent's source is rejected.
The original destructor writes its vftable and tail-transfers to `0x00402F30`;
the terminal jump ends exactly at its independently inventoried boundary.
Following alignment and the next complete entry are retained in the evidence.

This action's six-byte adjustment differs from the older Stage/ItemManager
three-byte adjustments. Its complete 41-byte aggregate has fields at
10/27/32/37 and its sole PE relocation at 32. Cookie and dispatcher identities
remain independently required. The two earlier member proofs remain identical.

Two local words and saved ESI/EDI put the cookie at EBP-32, node minus twenty.
The 44-byte prefix saves `this`; state zero is established at offset 182 after
the thread completes. All EBP/FS uses, argument access and restoration are
fixed. The complete 19-byte suffix ends in RET 4 at offset 548, including both
immediate bytes. Prefix relocations are 6/23; the suffix has none. The profile
contains exactly three reviewed member roles, with no configurable offsets.

## Results and refusal controls

Canonical replay reports **867 exact, 65 mismatch and 283 incomplete** among
1,215 annotations, covering **162,185 exact primary bytes and 932 units**.
The new owners add 732 primary bytes. All preceding 865 exact results, 65
complete mismatches and 930 unit definitions remain identical. Every other
incomplete record also remains identical. The 98 auxiliary code bytes, 88
metadata bytes and previously bound callees grant no extra primary credit.

**206 controls pass** across nine suites: array constructors (18), member
constructors (25), allocation cleanup (23), saved-register EH (37), legacy
empty EH (25), AnmManager constructor EH (25), reviewed linkages (36), strict
Oracle (14) and focused audit (3). Controls cover every candidate aggregate
byte, forged original hashes, source/module ownership, fixed array ranges,
state/this/cookie accesses, all relocations, foreign edges, interior returns
and all three RET 4 bytes. Ordinary body mutations preserve valid EH but fail
the complete primary comparison. The new array module is fingerprinted.

No build occurs. All 1,719 complete linked owner records and 192 dependency
stamps validate against the unchanged receipt. The source input remains
`c2ac9cc0add85924f097edf2dc772148551601b302607cc480fba1867a1fcd5a`.
Source-origin review and formal Factory acceptance remain open.

Original-only evidence is `.analysis/array-member-original-scopes.json`,
reproduced by `.analysis/review-array-member-originals.py`. Complete graphs,
raw payloads, fields, relocations and primary replays are retained in
`.analysis/array-member-caller-scopes.json`, reproduced by
`.analysis/review-array-member-callers.py`. Artifact/regression checks are
`.analysis/array-member-{artifact,regression}-check.json` with matching
`check-*.py` reproducers. Control logs and summary use `.analysis/array-member-*`.

## Open terminate dependency

Stage and ItemManager destruction have two-state maps targeting a shared
terminate thunk, rather than these private actions. Original `___std_terminate`
at `0x00476B19` and its candidate at `0x00476B18` are complete five-byte jumps.
Their targets are original `_terminate` at `0x0047B825` (59 bytes) and candidate
`0x0047A0D5` (a complete 60-byte PDB owner). The latter must not be truncated to
recover equal extents. Full terminal/filter control flow, SEH scope metadata
and all external dependency roles still require independent review. No
terminate binding, new destructor profile or exact credit is added.
`.analysis/terminate-entry-investigation.json` retains both full chains and
candidate fields for that next investigation.
