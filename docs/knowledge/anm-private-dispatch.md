# Anm private helpers through bounded dispatch

The 2026-11-11 review establishes two complete private helpers in
`src/AnmVmRun.cpp`. Full strict replay reports **790 exact, 61 mismatch and
364 incomplete**, covering 126,050 exact primary bytes. Both helpers pass and
add 71 bytes. All 788 preceding exact results and all 849 preceding comparison
units remain unchanged; there are now 851 complete units. No game source change
is retained.

## Complete helper scopes

| Original entry | Helper | Complete bytes | Original parent / call |
| --- | --- | ---: | --- |
| `0x00464D60` | anm_sincosmul | 32 | `0x004632F0` / `0x0046348B` |
| `0x00464930` | anm_sincosmul_xy | 39 | `0x0045F980` / `0x004606DC` |

Original-only review decodes each call-established helper entry through its
terminal `ret 8`. Neither body contains branches, calls or linked fields.
The 32-byte body ends immediately before the next independent entry; the
39-byte body has nine INT3 bytes before its next independent entry. Neither
scope overlaps another inventoried owner. Complete bytes, hashes, disassembly,
padding and original witness paths are retained in
`.analysis/anm-private-dispatch-original-scopes.json`. The inventory used for
that original-only derivation is `.analysis/anm-private-original-inventory.csv`.
Candidate artifacts do not define the original helper scopes.

The ordinary helper uses the existing `x87-sincos-scale-v1` profile. The new
`x87-sincos-scale-xy-v1` profile covers the entire different 39-byte ABI: ECX
and EDX are separate output pointers, the two stack floats are angle and radius,
and x87 `fsincos` followed by multiplication writes cosine to the first pointer
and sine to the second. Both profiles require their full original and candidate
bytes. The review does not synthesize instructions or shorten a contribution.

Each candidate separately requires its exact source-qualified private MAP name,
unique whole same-start PDB contribution, complete producer object/module,
annotation identity, no interior/public collision, and no extra or crossing
relocations. Both belong to `.obj/src/AnmVmRun.obj`, module 16 in this build.
The two explicit records extend `config/static-functions.toml` from eleven to
thirteen helpers. Public selection and unreviewed private names retain their
previous refusal behavior.

## Original bounded witness paths

The preceding direct-branch traversal stopped at indirect dispatches. This
review adds one explicit `bounded-byte-remap-v1` witness profile with full
original parent-code hashes and complete table hashes:

| Original parent | Guard / dispatch | Complete byte map | Complete target table |
| --- | --- | --- | --- |
| `0x004632F0` | `0x0046331C` / `0x0046332C` | `0x00463B14`, 17 bytes | `0x00463B04`, 4 entries / 16 bytes |
| `0x0045F980` | `0x0045FBE3` / `0x0045FBF5` | `0x00462D8C`, 215 bytes | `0x00462CB8`, 53 entries / 212 bytes |

The verifier requires adjacent CMP, unsigned JA, byte MOVZX and indexed JMP
instructions. CMP bounds the same 32-bit index consumed by the byte map;
the JMP uses that remapped index at scale four. Map length must equal bound
plus one. The target count must cover the maximum mapped index exactly. Every
target must be a decoded instruction start in the original parent code context.
Both tables must follow that code and be disjoint. Direct branches and case
targets cannot bypass the bound into the guard's suffix. Only actually mapped
targets are added to traversal; unused target slots cannot establish a path.
All other indirect jumps remain traversal stops.

The 17-byte map is `[0,3,3,3,1,1,3,3,3,3,3,3,3,3,3,2,2]`; its four entries
point to `0x00463333`, `0x004635ED`, `0x004638DA` and `0x00463AFB`.
Map index zero reaches the ordinary helper's witness. In the main interpreter,
map index 131 reaches `0x00460663` and then the XY helper's witness. The retained
paths include each guard and dispatch and contain no trap instruction.

This batch establishes original witness evidence for the two complete helper
owners. The 460 table bytes receive no exact credit, and neither parent receives
a complete comparison from this proof. At this checkpoint, the original
inventory describes code contexts of 2,068 and 13,109 bytes. The subsequent
[complete special-vertices scope review](special-vertices-scope.md) establishes
that parent's entire 2,101-byte code/table owner and supersedes the 2,068-byte
context. Its candidate remains 2,097 bytes and incomplete. The main interpreter
still needs complete owned-data review and has eight unbound fields.

## Rejected circle source context

The complete 588-byte `AnmManager::draw_circle` baseline has 514 matching bytes.
An ordinary source trial splits `angle = wrap_angle(angle + step)` into
`angle += step` followed by normalization. It builds incrementally but leaves
the complete result at 514/588. The trial is rejected and the source restored
byte for byte. No scheduling barrier, forced register or access is introduced.
The focused report also retains the unchanged 355-byte triangle-fan result
(349 matching) and 558-byte ring result (428 matching).

Baseline sources and outputs remain under `.analysis/primitive-source-baseline/`;
the trial source and complete outputs remain under
`.analysis/circle-angle-advance-artifacts/`. Full original and candidate scopes,
instructions, hashes and strict diagnostics are in
`.analysis/circle-angle-source-trials.json`; the focused report is
`.analysis/circle-angle-advance-focused.json`.

Current outputs are freshly rebuilt from the restored source. Full build-input
identity equals the baseline, all four artifact hashes match the fresh receipt,
and all 192 dependency stamps validate. See
`.analysis/primitive-source-restored-check.json` and
`.analysis/primitive-source-restored-build.log`. No archived outputs are
substituted and no clean build is run.

## Validation and evidence

All 143 controls pass across seven suites: private identities (31), strict
Oracle (14), reviewed linkages (26), focused audit (3), primary switch ownership
(19), constructor EH (25) and empty EH (25). The private suite compares all
thirteen complete owners. New negative controls mutate every byte of both maps
and target tables, every original/candidate byte of the 39-byte helper,
partial/expanded extents, signed guards, register indices, instruction sites,
guard bypass and unreachable unused slots. Existing ownership, relocation and
direct-call controls remain in force.

Logs are `.analysis/anm-private-dispatch-{controls,oracle-controls,linkage-controls,focused-controls,switch-controls,constructor-eh-controls,empty-eh-controls}.log`.
Full replay and retained-unit evidence are
`.analysis/anm-private-dispatch-full-audit.log` and
`.analysis/anm-private-dispatch-regression-check.json`. Source-origin review
remains open and Factory acceptance remains unsubmitted. Nothing is published.
