# Large ECL dispatch control flow and restored source trials

The later [complete frame-store scope registration](upper-ecl-frame-store-scope.md)
formally closes the original 21,408-byte ownership, including the interposed
frame store. The generic-refusal and code-only boundary statements below are
historical; the upper game-source candidate still remains incomplete.

This investigation starts at `de396d9`. It runs only static compilation and
complete original/candidate comparisons. All source trials are restored. It
adds no exact function, linkage binding, boundary override or Oracle exception.

## Complete original dispatch graph

The original `EnemyData::ecl_run_over_300` starts at `0x0041DCB0`. Its complete
diagnostic extent is **21,408 bytes**, ending immediately before the independent
entry at `0x00423050`. The 19,976-byte inventory boundary covers its code;
it does not cover all owned tables. The original complete payload SHA-256 is
`6c6f400ca422d9c14e06cb96d7656c71521a61c0f5e6e7dcc4693dab1c1afa49`.

An original-only traversal reaches **all 4,519 decoded code instructions**,
including the sole return at `0x00422AB7`. No unreachable instruction or
code-alignment gap remains in that interval. Every direct branch destination
is a decoded instruction start. Calls retain their actual destinations; they
are not executed or replaced.

The three guarded indirect jumps retain all **182 target entries**: 174 main
selectors and two four-entry difficulty tables. All targets are decoded code
starts. The full 702-byte opcode map contains every main selector and agrees
with the candidate map. The scope packet retains both nested tables, the
two-byte alignment between map and nested tables, all candidate relocations
and all code bytes. A guard-interior check rejects direct incoming edges or
table destinations entering the protected dispatch sequence.

This strengthens the earlier spatial table census with complete entry-rooted
reachability. It does not change formal acceptance: the generic switch proof
still rejects the intervening frame store after the main byte remap. The
unreviewed EH, vector, helper and string identities also remain open. No
address obtained from a candidate operand becomes an original binding.

## Owner access and movement selection

The baseline candidate owns **21,316 bytes**, including 19,884 code bytes.
Its actual frame allocation is `0x498`, against `0x478` in the original.
Historical reports of a `0x490` candidate frame describe older source.

Replacing the 71 direct active-context argument accesses inside this owner
with the existing `SptInf` accessors produces **21,376 bytes**, with 19,944
code bytes. The original's initial `full` in EDX, active context in EAX and
early `MOV ECX,[EDX+0xC]` argument dispatch reappear. This differs from the
rejected historical whole-function owner cache: each accessor still reloads
the owner when required after calls.

The full function nevertheless differs. The extra saved opcode-field address,
frame allocation, movement selection, argument staging and shared exits remain
wrong. A 32-byte extent difference does not measure incorrect instructions.
The accessor trial is restored rather than treated as an exact result.

In the velocity-interpolation arm, the original keeps a position-member offset
until access, while the candidate forms the object pointer earlier. Selecting
`PosVel EnemyData::*` and applying it at each access still produces the same
21,376-byte complete extent; the optimizer again forms the pointer early and
changes local slots. This source form is also restored. Spatial case sizes
cannot establish ownership of the shared interpolation tails.

## Other restored large-owner trials

For the complete 1,692-byte enemy-motion owner, expressing the directional VM
lookup through `get_vm` followed by ID cleanup leaves a 1,691-byte candidate.
An explicit position pointer recovers the camera X addition order, but not
the original Y order, VM registers or separate zero-vector frame. Neither
change is retained. Earlier child-mode and creation-helper trials remain
relevant; an unchanged helper would incorrectly write child mode zero instead
of eight.

For the complete 986-byte curve reverse step, a diagnostic comparison locates
four non-address differences at offsets `0x302`, `0x30B`, `0x313` and `0x317`.
They select the opposite X/Y registers for the squared-speed sum. This is an
address-masked diagnostic, not a strict comparison or exact credit; `floor`
and intrinsic `atan2` still lack accepted identities.

Accumulating the squared length through the output pointer leaves those four
differences unchanged. Computing a length local before the position produces
987 bytes with different scheduling. Replacing position assignment with
`D3DXVec3Add(out_pos, pos, &sum)` produces 980 bytes and changes vector stores
and registers. All three complete-owner failures are restored. No volatile
storage, artificial arithmetic, register constraint or padding is introduced.

## Preserved evidence

Keep `.analysis/ecl-owner-work/`: the PDB-384 baseline artifacts/report,
`original-cfg.json`, `review-original.py`, complete three-dispatch packets,
failed source snapshots, the final failed member-position image and build logs.
Keep `.analysis/curve-exact-work/`: complete curve packets, failed source
snapshots and diagnostic/build logs. These are required ignored evidence.
Neither the diagnostics nor the original CFG census grants acceptance authority.

The restoration build is PDB age **391** with the unchanged source input
`eb7dbf25d10b6a3ca0880708e8e2a40ad60c81d1c30e69e1bc664de4e965d725`.
Full strict replay retains **889 exact, 65 mismatch and 261 incomplete**.
`final-regression.json` confirms all 1,719 complete candidate owners remain
byte-identical over 527,133 bytes, with identical addresses/extents and whole
image relocation records. All 954 units and all 1,215 annotation results,
sizes, matching-byte diagnostics and refusal reasons remain unchanged.
Source-origin review stays open; Factory acceptance is not submitted.
