# Audio release terminal graph and complete strncmp identity

The local strict report is 883 exact, 65 mismatch and 267 incomplete among
1,215 annotated candidates, covering 167,817 exact primary bytes and 948 units.
Two complete audio owners now pass:

| Original entry | Function | Complete bytes | Candidate entry |
| --- | --- | ---: | --- |
| 0x0045D850 | SoundManager::release | 370 | 0x004676B0 |
| 0x0045D9D0 | get_wav_chunk | 88 | 0x00467830 |

The new runtime and EH identities grant no additional primary credit. Game
source, compiler inputs and all compiler artifacts are unchanged; no build
occurs. Source-origin review remains open, Factory acceptance is not submitted,
and nothing is pushed or published.

## Complete strncmp identity

The direct call at 0x0045D9EF in the independent complete 88-byte chunk walker
selects the original runtime entry at 0x00479A70. Its full 120-byte boundary
matches the complete candidate _strncmp at 0x00479C90. The candidate's unique
same-start PDB contribution and MAP producer identify libucrt:strncmp.obj in
the pinned Windows 10.0.10240.0 x86 libucrt.lib.

The shipped implementation is
.tools/toolchain/sdk/Program Files/Windows Kits/10/Source/10.0.10240.0/ucrt/string/i386/strncmp.asm.
Its explicit MASM procedure saves EBX/ESI, loads the two byte strings and count,
returns equality for zero count, and compares unsigned characters until a
difference, NUL or exhausted count. The second pointer is aligned for DWORD
comparison; the first pointer's page offset is checked against 0xFFC before
reading a block. Equal blocks use the 0xFEFEFEFF/0x80808080 zero-byte test.
Unequal bytes return minus one or plus one through the final carry-dependent
SBB/OR sequence. No external call, ISA global or literal linkage is required.

Both complete bodies have 48 decoded instructions, 44 reached from entry.
The remaining owned interval is the two-byte JMP at plus 107 followed by three
INT3 bytes. It implements the procedure's sixteen-byte alignment before the
unequal-return block. Every one of these five bytes remains in the full
comparison; no padding is excluded. Both 120-byte payloads and hashes are
identical, all branches stay within instruction starts, the complete field
census is empty and both relocation footprints are empty. The next public
symbol does not define or enlarge this owner.

The ordinary complete runtime-function binding is used without widening its
witness schema. The chunk walker's call is independent original research and
is checked in the controls; it is not declared as a call within another
runtime-function binding. The full 88-byte original/candidate primary scopes
have 43 reachable instructions and compare exactly after this identity binds.

SoundBufferEntry::load also loses both unresolved strncmp fields. It retains
one ambiguous data-tag field, and its complete original/candidate extents stay
702/713 bytes. No loader prefix receives credit.

## Complete release terminal graph

Release has a complete 27-byte private handler at original 0x0048AA80 and
candidate 0x0048AA20. The full 44-byte metadata aggregate has original FuncInfo
at 0x0049B628, followed by its eight-byte unwind map. The candidate's complete
owner starts at 0x0049B2FC with the map first and FuncInfo at plus eight.

Both complete layouts declare one state, flags one and a sole unwind edge
from state zero to minus one through the independently reviewed ___std_terminate
entry. The full five-byte thunk, complete terminate bodies and 28-byte SEH
metadata retain their prior independent proofs. Handler and descriptor names,
complete PDB contributions, source/module ownership, every byte and all
pointer relocations are required. Both belong to the complete SoundManager.obj
parent producer. The code owner is not joined to unrelated neighboring bytes.

The fixed single-state profile now includes precisely the 370-byte release
parent. Its complete 35-byte registration saves ESI and has no local word:
the node is EBP-12, saved ESI is EBP-16, and the encoded cookie is EBP-20.
Consequently the handler's cookie address is node minus eight. The shared
single-state calculation requires no local word and derives displacement
minus four minus four times the saved-register count. The previous two-register
parents keep node minus twelve. No configuration may choose an arbitrary
cookie displacement or register sequence.

All original/candidate EBP and FS uses match the fixed parent frame. The sole
state-zero write is at plus 264. The complete sixteen-byte normal restoration
restores FS, discards the cookie, restores ESI and returns through the sole
RET. Parent prefix relocations are at six/nineteen, the handler relocation is
at eighteen, and metadata relocations are at four/sixteen; the restoration has
none. The complete 370-byte parents each have 104 reachable instructions.

The handler helper recognizes node minus eight only as an encoding; admission
still requires the fixed complete parent, declaration, frame, graph and source
owner. A different no-local parent remains refused. Arcfile's array-delete
proof is explicitly scoped to its existing profile entry, so it is not attached
to release. The prior Arcfile and registry proof dictionaries remain identical.

## Retention and checks

All preceding 881 exact results, 65 complete mismatches and 946 unit definitions
remain identical, including full comparison records and auxiliary graphs.
Only the two newly exact entries and the loader's two resolved runtime fields
change. The latter retains its data-tag refusal. Every other incomplete record
is identical. No game source or compiler artifact changes, and no build occurs.
All 1,719 complete linked records and 192 dependency stamps validate. PDB age
stays 124 and the source input remains
`356af008e8064e7f8080f6c112145362eea142d1955f371a989e5b65034aca5f`.

Three hundred forty-nine controls pass across fourteen relevant suites:
single-state EH (19), reviewed linkages (46), strict Oracle (14), focused audit
(3), saved-register EH (56), vftables (33), terminate EH (23), array EH (18),
member EH (25), allocation EH (23), legacy EH (25), AnmManager constructor EH
(25), sound data (18) and aligned audio EH (21). The expanded controls cover
all three single-state parents, every handler/metadata byte, alternate cookies,
an extra local/save, all foreign parent pairs, fixed states, full returns,
relocations, source/module extents and ordinary body mutation. The strncmp
controls require both full extents and pinned producer, preserve the original
call and all owned alignment, and check complete bytes/fields/relocations.

Retained evidence:

- `.analysis/audio-release-baseline/`: preceding report, units, declarations,
  verifier/control sources, receipt and complete linked-function records.
- `.analysis/inspect-audio-final-identities.py`,
  `.analysis/audio-final-identity-inventory.json`: full audio parent scopes,
  private graph inventories and runtime location.
- `.analysis/review-audio-release-scopes.py`,
  `.analysis/audio-release-graph-proof.json`: both complete runtime bodies,
  closed graphs, every owned byte, parent scopes and final release proof.
- `.analysis/audio-release-focused.json`: both complete primary comparisons.
- `.analysis/check-audio-release-artifacts.py`,
  `.analysis/audio-release-artifact-check.json`: unchanged full compiler graph,
  receipt, artifact hashes and dependencies.
- `.analysis/audio-release-<suite>-controls.log`,
  `.analysis/audio-release-controls-summary.json`: all 349 controls.
- `.analysis/check-audio-release-regression.py`,
  `.analysis/audio-release-regression-check.json`: all prior units/results and
  the sole incomplete delta.

Reproduce the focused checks with:

```sh
scripts/repo-python scripts/audit-reference.py --address 0x45d850 --address 0x45d9d0 --json .analysis/audio-release-focused.json
scripts/repo-python scripts/test-eh-single-state.py
scripts/repo-python scripts/test-reviewed-linkages.py
scripts/repo-python scripts/progress.py
```

Do not run ledger readers/tests concurrently with audit-reference.py --write-units.

## Initialization remains open

SoundManager::initialize retains both unresolved fields. Its handler owns 37
bytes and checks two cookies at node minus 96 and node minus four. Metadata
owns 44 bytes with one terminal state and flags one. It does not fit the
27-byte single-cookie profile or the aligned audio handler's forty-byte shape.
Its complete parent frame, cookie slots and state lifetime require a separate
fixed review.

Its ESI cursor starts at sound-table plus four, advances by twenty and compares
against sound-table plus 1,564, physically anchor-x-plus-four. The address lies
outside the 1,560-byte typed table even though both arrays share the reviewed
1,656-byte aggregate. The existing generic cursor rule also refuses the
loader call and side exits. Do not relax that rule or borrow the neighboring
array identity. Prove all cursor paths, exact one-past usage, side exits and
nonvolatile ESI preservation through both complete 702/713-byte loader scopes;
a single PUSH is not an ABI proof.

`.analysis/prepare-audio-initialize-next.py` retains both full initialization
and loader payloads, private contributions, return sites and cursor uses in
`.analysis/audio-initialize-next-proof-inventory.json`. Both remaining
requirements are explicitly unproven and receive zero primary credit.

`SoundManager::initialize` (0x45d510) has the same single terminal state, in a
GS-buffer frame: profile `gs-single-state-terminate-v1` (`scripts/eh_terminate.py`)
fixes both cookie checks in its 37-byte handler and every EBP/FS use of the parent.
