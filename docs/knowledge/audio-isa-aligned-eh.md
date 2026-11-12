# Complete audio initialization identities

The strict local report is 879 exact, 65 mismatch and 271 incomplete among
1,215 annotated candidates, covering 167,046 exact primary bytes and 944 units.
Both complete audio initialization owners now pass:

| Original entry | Function | Complete bytes | Candidate entry |
| --- | --- | ---: | --- |
| 0x00470320 | CSoundManager::CreateStreaming | 856 | 0x00422020 |
| 0x00470680 | CSoundManager::CreateStreamingFromMemory | 809 | 0x00422380 |

The preceding rand/vector review left each owner with two unresolved fields:
its private EH entry at offset 25 and the mutable ISA address at offset
407/360. Independent complete graphs now establish both identities. No game
source or compiler output changes. The 1,665 newly exact bytes belong only to
these two primary owners; runtime, storage and auxiliary EH graphs add no
primary credit. Source-origin review remains open and Factory acceptance is
not submitted. Nothing is published or pushed.

## Startup-derived ISA storage

An independent original inventory search identifies the unique complete
415-byte function containing CPUID, all three GenuineIntel vendor words and
XGETBV at 0x00475430. Its closed graph has 133 reachable instructions. Twelve
fixed complete instruction witnesses connect the original PE entrypoint
0x0047537B to this function through normal startup, including the direct call
at 0x00474A93. These witnesses establish reachability; they grant no complete
comparison credit to their enclosing startup functions.

The candidate ___isa_available_init at 0x0047548B owns all 415 bytes in its
same-start PDB contribution. Its linked owner, MAP producer, all three PDB
contributions and producer module agree with the pinned LIBCMT:_cpu_disp_.obj
from MSVC 14.10.25017. Those contributions are exactly the initializer, an
eight-byte virtual-zero-fill aggregate and a four-byte initialized enable mask.

| Role | Original | Candidate | Complete storage |
| --- | --- | --- | --- |
| ___isa_available | 0x004A65FC | 0x004A67EC | First DWORD of the eight-byte aggregate |
| ___favor | 0x004A6600 | 0x004A67F0 | Second DWORD of the same aggregate |
| ___isa_enabled | 0x0049EA50 | 0x0049F770 | Four raw bytes initialized to one |

Both adjacent original fields are independently referenced by the startup
initializer. The complete candidate aggregate has precisely the two public
names at offsets zero/four, with no interior alias, overlapping contribution
or foreign producer. Both complete eight-byte ranges lie beyond their PE
section's raw extent and within writable virtual zero fill. They are mutable
storage, never literal-zero data or an invented four-byte owner.

The initializer resets ISA level zero and enables the baseline ISA. A full
six-byte imported tail jump supplies IsProcessorFeaturePresent(10); CPUID and
OSXSAVE/XGETBV checks then select SSE2, SSE4.2, AVX or AVX2, updating the enable
mask and Atom/fast-string preferences. The shipped isa_availability.h records
the level and preference enums. The CPU-dispatch implementation source is not
present in the pinned payload; no source identity is inferred from a filename.

Both complete import thunks are checked against their PE import records for
KERNEL32.dll!IsProcessorFeaturePresent. The original thunk is 0x00486AAA; its
candidate at 0x00486A3A has a complete six-byte same-start PDB contribution in
the pinned SDK kernel32.lib producer. The actual IAT addresses and candidate
DIR32 relocation at offset two are required.

The complete initializer comparison recognizes only fifteen absolute operands
for those three fixed storage roles and one REL32 feature call. Every other
byte is literal; all fifteen candidate PE relocations, including duplicate and
crossing checks, must agree. Original ownership, startup bytes, full hash,
closed control flow and all original field roles are checked first. The new
runtime_isa.py verifier and runtime-globals.toml declaration are fingerprinted.
Only ___isa_available is exported as a binding, permitting its exact DIR32
address point with zero addend. Neither ___favor nor arbitrary mutable globals
are admitted.

## Complete aligned EH graphs

Each parent has a private 58-byte code aggregate: an eighteen-byte sized-delete
action and a forty-byte dual-cookie handler. Its complete metadata aggregate
owns 44 bytes, with one state, no try map, flags one, and the sole unwind edge
from state zero to minus one through the allocation cleanup.

| Parent | Original code / FuncInfo | Candidate code / metadata owner |
| --- | --- | --- |
| CreateStreaming | 0x0048AB50 / 0x0049B6C4 | 0x0048A540 / 0x0049AE4C |
| CreateStreamingFromMemory | 0x0048AB90 / 0x0049B6F0 | 0x0048A580 / 0x0049AE78 |

The original stores the 36-byte FuncInfo before its eight-byte map. Each
complete candidate PDB contribution stores the map first and FuncInfo at
plus eight. Both layouts and all 44 bytes are required, with candidate pointer
relocations at four/sixteen. Original inventory overlap checks require the
complete eighteen-byte cleanup subscope and exclude any interposed owner.
Both candidate code/data owners and all private names belong to the parent's
DSUtil.obj module. The action is specifically unwindfunclet $1; the handler is
an interior entry at plus eighteen, without a fabricated standalone extent.

The fixed 62-byte parent registration saves the original argument stack in
EBX, aligns ESP to sixteen bytes, establishes EBP, reserves 120 local bytes,
and installs the EH node at EBP-12. It saves one encoded cookie at EBP-20 and
pushes a second at EBP-148 after the ESI/EDI saves. The forty-byte handler
checks node minus 136 and node minus eight before loading FuncInfo and tail
transferring to CxxFrameHandler3. The full 32-byte normal restoration checks
the EBP-20 cookie, restores both stack bases and returns with RET 44/RET 48.

The late 160-byte allocation, saved pointer at EBP-76, sole state-zero store,
constructor call and complete cleanup action are required. The allocator,
sized delete, cookie checker and CxxFrameHandler3 retain their independently
reviewed complete runtime owners. The constructor retains its independently
complete ninety-byte DSUtil owner. All frame-base writes, reserved-slot
accesses (including straddling/indexed accesses), saved-pointer accesses,
returns and local jump instructions are checked over the complete parent.
The frame cannot acquire another return, state access or stack-base overwrite.

All 58 code bytes are compared against the fixed instruction graph, including
both cookie checks, the saved-pointer displacement, allocation size, stack
cleanup and every terminal transfer. Its only DIR32 relocation is at 49;
REL32 fields are at 10/34/44/54. Parent registration has relocations at 25/41;
normal restoration has none. The new eh_aligned_audio.py profile admits only
these two complete parents and 58/44-byte aggregates. Existing 27-byte-handler,
$0, empty, allocation, member, array and terminate profiles retain their rules.
Shared field plumbing derives offset 25 solely from this verified profile;
other profiles continue to require offset six. The primary binding also
requires the exact parent source, symbol, both addresses and complete size.

## Validation and retained evidence

All preceding 877 exact results, 65 complete mismatches and 942 unit definitions
are identical. Every other incomplete record is also identical. Compiler input
identity remains
`356af008e8064e7f8080f6c112145362eea142d1955f371a989e5b65034aca5f`.
No build occurs; the retained incremental graph has unchanged EXE/MAP/PDB/
function-list hashes, all 1,719 complete linked function records and all 192
valid dependency stamps.

The fifteen relevant suites pass 363 tests: ISA storage (16), aligned audio EH
(21), reviewed linkages (43), strict Oracle (14), focused audit (3), saved-register
EH (56), vftables (33), single-state EH (16), terminate EH (23), array EH (18),
member EH (25), allocation EH (23), legacy EH (25), AnmManager constructor EH
(25) and runtime interiors (22). The controls mutate every candidate initializer
byte, every candidate action/handler/metadata byte, both complete parent
registrations/restorations, all allocation-lifetime operands and every original
action/metadata byte with refreshed hashes. Wrong producers, incomplete owners,
startup changes, duplicate names, raw/BSS confusion, wrong imports, missing/extra/
duplicate/crossing relocations, foreign parents and alternate handler offsets
are refused. An unrelated body mutation preserves its EH proof but still fails
the complete primary comparison.

Useful retained evidence:

- `.analysis/isa-aligned-source-baseline/`: preceding report, units, declarations,
  verifier plumbing and build receipt.
- `.analysis/locate-original-isa-init.py`, `.analysis/isa-original-location.json`:
  independent initializer locator, full bytes/CFG and startup witness.
- `.analysis/prepare-isa-audio-proof.py`, `.analysis/isa-owner-inventory.json`:
  complete producer/storage/field inventory.
- `.analysis/aligned-audio-eh-inventory.json`: complete original/candidate parent,
  private names, code, descriptors and frame instructions.
- `.analysis/review-isa-aligned-graphs.py`, `.analysis/isa-aligned-graph-proof.json`:
  final complete graph proofs from an immutable current Context.
- `.analysis/isa-aligned-focused.json`: focused comparison of both whole parents.
- `.analysis/isa-aligned-<suite>-controls.log`,
  `.analysis/isa-aligned-controls-summary.json`: refusal controls.
- `.analysis/check-isa-aligned-artifacts.py`,
  `.analysis/isa-aligned-artifact-check.json`: retained build/input/dependency checks.
- `.analysis/check-isa-aligned-regression.py`,
  `.analysis/isa-aligned-regression-check.json`: full report/unit retention.

Reproduce focused comparison and the new controls with:

```sh
.venv/bin/python scripts/audit-reference.py --address 0x470320 --address 0x470680 --json .analysis/isa-aligned-focused.json
.venv/bin/python scripts/test-runtime-isa.py
.venv/bin/python scripts/test-eh-aligned-audio.py
.venv/bin/python scripts/progress.py
```

Do not run ledger readers/tests concurrently with audit-reference.py --write-units.
The remaining DSUtil candidates are SetVolume at 0x004711F0 and Unpause at
0x00471380. Their candidate extents are 116/107 bytes against complete
originals 114/103; neither receives prefix credit. Their natural source
and calling/type contexts are useful next reconstruction targets.
