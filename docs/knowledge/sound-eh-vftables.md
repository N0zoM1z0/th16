# Complete sound class tables and empty ESI/EDI frame

Reviewed 2026-11-12. Original RTTI independently identifies the complete primary
CSound and CStreamingSound tables. A separate empty-EH frame profile covers
CSound destruction, which saves ESI/EDI without a local word. Four whole
primary owners now pass, adding 776 exact bytes. No game source, compiler
artifact or build change occurs.

## Complete original owners

| Original | Owner | Complete bytes | Reachable instructions | Candidate |
| --- | --- | ---: | ---: | --- |
| `0x004709B0` | CSound construction | 463 | 160 | `0x00422780` |
| `0x00470B80` | CSound scalar deleting destructor | 38 | 15 | `0x00422950` |
| `0x00470E10` | CSound destruction | 179 | 58 | `0x00422980` |
| `0x00471430` | CStreamingSound construction | 90 | 24 | `0x00422FA0` |
| `0x00471490` | CStreamingSound scalar deleting destructor | 44 | 16 | `0x00423000` |

Original-only CFG review reaches every instruction, checks each terminal path
and following alignment, and excludes interior inventory entries. The CSound
deleting entry already has an exact primary unit; its slot role adds no credit.
The other four owners pass their full same-start PDB contributions, every
linked field and every PE relocation.

## Tables located from original RTTI

| Class | Original address point | Complete slots | Candidate address point | Independent slot identity |
| --- | --- | ---: | --- | --- |
| CSound | `0x004943A0` | 1 | `0x00492460` | CSound scalar deleting destructor, `0x00470B80`, 38 bytes |
| CStreamingSound | `0x00494398` | 1 | `0x00492458` | CStreamingSound scalar deleting destructor, `0x00471490`, 44 bytes |

Unique terminated original RTTI names identify their primary CompleteObjectLocator
records, whose exact pointer references identify the address points. Each has
one callable slot; the following word is not executable. The class declarations
in SoundManager.h agree: each declares only its virtual destructor. The table
location is established without selecting a consumer operand or candidate address.

Each complete candidate contribution starts four bytes before its public
address point and owns all eight bytes: locator pointer and one function slot.
The unchanged primary-vftable verifier checks the full original/candidate RTTI
class hierarchies, CSound's base graph and CStreamingSound's CSound inheritance.
Every candidate locator, type descriptor, hierarchy, base array including its
trailing byte and base descriptor must have one complete PDB storage owner.

Across both graphs there are **twelve unique complete candidate metadata
objects, 209 bytes and nineteen pointer relocations**. All payloads, object
extents and relocations are retained and checked. Class identities cannot be
borrowed from the peer table. Slot destinations require independent function
annotations, complete same-start candidate PDB owners and original inventory
entries. RTTI/table storage grants no primary data or callee exact credit.

## Empty frame without a local word

The complete CSound destructor registers its original handler at `0x0048ABD0`,
27 bytes, and FuncInfo at `0x0049B71C`, 36 bytes. FuncInfo has magic
`0x19930522`, zero states, no map/try/catch fields and flags five. Candidate
private owners are `0x0048A5C0` and `0x0049AEA4`, with the same full extents.
Source-qualified private names, PDB modules, permissions and absence of
overlapping names/contributions are required.

The explicit `empty-eh3-saved-esi-edi-v1` profile has a complete 36-byte
registration prefix: the EBP-12 registration node, saved ESI/EDI and encoded
cookie, with no local PUSH. The cookie is at EBP-24, node minus twelve. Its
full seventeen-byte restoration ends in the sole RET at offset 178. The two
older saved-register profiles keep their local PUSH and original node-16/-20
slots. The shared calculation derives these depths from the three fixed
local/save sequences; no local count, registers or displacement is configurable.

The complete parent must retain the two registration/restoration accesses,
three FS accesses, frame-pointer writes and sole return. Any body access to
the empty state or cookie slots is refused. Nonempty Arcfile and registry
frames using node-12 fail this empty-frame profile. Handler checking retains
all 27 bytes and the independent cookie checker/dispatcher identities.
Candidate handler relocations are exactly offset 18, metadata has none and
prefix relocations are 6/20; the restoration has none. The two earlier
saved-register profiles and every previous EH proof remain identical.

## Results and controls

Canonical replay reports **876 exact, 65 mismatch and 274 incomplete** among
1,215 annotations, covering **165,271 exact primary bytes and 941 units**.
CSound construction/destruction (463/179), CStreamingSound construction (90)
and its scalar deleting destructor (44) add 776 bytes. All preceding 872
exact results, 65 complete mismatches and 937 unit definitions remain identical.
Every other incomplete record also remains identical. The private handler,
descriptor, tables and RTTI receive no extra primary credit.

**301 controls pass** across twelve suites: saved-register EH (56), vftables
(33), reviewed linkages (40), single-state EH (16), two-state EH (23), array
constructor EH (18), member constructor EH (25), allocation EH (23), legacy
empty EH (25), AnmManager constructor EH (25), strict Oracle (14) and focused
audit (3). The ESI/EDI fixture exercises full graphs, source/module ownership,
cookie witnesses, protected reads, frame-pointer replacement, nonempty maps,
foreign identical metadata, complete extents and pointer relocations. Ordinary
body changes still fail full primary comparison. Sound tables also reject
incomplete/ambiguous storage, wrong peer classes and interior or incomplete
slot entries.

No build occurs. All 1,719 complete linked function records, artifact/receipt
hashes and 192 dependency stamps remain unchanged. The source input remains
`356af008e8064e7f8080f6c112145362eea142d1955f371a989e5b65034aca5f`.
The current incremental build graph and ignored evidence are retained.
Source-origin review and formal Factory acceptance remain open.

Original-only scopes and table locations are `.analysis/sound-original-scopes.json`
and `.analysis/sound-vftable-original-locations.json`, with reproducers
`.analysis/review-sound-originals.py` and
`.analysis/review-sound-vftable-originals.py`. Complete graphs, payloads, fields,
relocations, slot owners and replays are `.analysis/sound-vftable-graph-proof.json`
and `.analysis/sound-eh-caller-scopes.json`, with matching `review-*.py`
reproducers. Artifact/regression checks are
`.analysis/sound-{artifact,regression}-check.json` with matching `check-*.py`
reproducers. Terminal logs and the control summary use `.analysis/sound-*`;
the baseline is `.analysis/sound-eh-baseline/`.
