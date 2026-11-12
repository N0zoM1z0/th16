# Complete noexcept destructor and terminate graphs

Reviewed 2026-11-12. Stage and ItemManager destruction each have two unwind
states whose actions call the shared noexcept termination entry. The complete
original maps and parent frames establish these roles independently of the
candidate. Both complete primary owners now pass, adding 1,354 exact bytes.
No game source or compiler artifact changes occur.

## Complete original and candidate scopes

| Parent | Original / complete bytes | Reachable instructions | Original handler | Original FuncInfo / map |
| --- | --- | ---: | --- | --- |
| `Stage::~Stage` | `0x004099A0` / 994 | 251 | `0x0048A450` | `0x0049B010` / `0x0049B034` |
| `ItemManager::~ItemManager` | `0x0042F2D0` / 360 | 98 | `0x0048A800` | `0x0049B3AC` / `0x0049B3D0` |

Original-only review reaches every parent instruction, accounts for the final
return and following alignment, and excludes interior inventory entries. Each
registration PUSH selects its complete 27-byte handler; the handler selects
FuncInfo, which selects the entire two-entry map. Both entries transition to
state -1 through original `___std_terminate` at `0x00476B19`.

| Candidate producer | Parent | Complete handler | Complete data / interior FuncInfo |
| --- | --- | --- | --- |
| `Stage.obj` | `0x0046A3E0` | `0x0048AAD0`, 27 bytes | `0x0049B3C0`, 52 bytes / `0x0049B3D0` |
| `Item.obj` | `0x00440560` | `0x0048A830`, 27 bytes | `0x0049B10C`, 52 bytes / `0x0049B11C` |

The original stores its complete 36-byte FuncInfo followed by sixteen map
bytes. The candidate's complete PDB data contribution stores the map first,
then FuncInfo at offset sixteen. Both layouts are checked in full: magic
`0x19930522`, exactly two states, flags five, zero other fields and two fixed
terminal actions. The candidate actions select `___std_terminate` at
`0x00476B18`; no private cleanup action is inferred from adjacent code.

The handler and data require complete source-qualified PDB contributions,
module agreement with the primary parent, correct permissions and no other
overlapping owners. The handler has one private name. The data has exactly
`__unwindtable$<parent>` at zero and `__ehfuncinfo$<parent>` at sixteen. Handler
instruction fields are exactly 13/18/23, with its sole PE relocation at 18.
The complete data relocations are exactly 4/12/24.

## Independent runtime chain and SEH roles

| Runtime identity | Original / complete extent | Candidate / complete PDB extent | Pinned producer |
| --- | --- | --- | --- |
| `___std_terminate` | `0x00476B19` / 5 | `0x00476B18` / 5 | libvcruntime:frame.obj |
| `_terminate` | `0x0047B825` / 59 | `0x0047A0D5` / 60 | libucrt:terminate.obj |
| `__SEH_prolog4_GS` | `0x00486CE0` / 73 | `0x00486F00` / 90 | LIBCMT:_sehprolg4gs_.obj |
| `___acrt_getptd` | `0x0047CAD3` / 131 | `0x0047C5B1` / 132 | libucrt:per_thread_data.obj |
| `_abort` | `0x0047BBDB` / 67 | `0x0047B47B` / 67 | libucrt:abort.obj |

These are callee identities, with no runtime primary exact credit. Neither
side is shortened or extended to equalize extents. The original prolog's
separate seventeen-byte epilog starts at `0x00486D29`; the candidate's complete
ninety-byte contribution includes its epilog at offset 73. The extra candidate
terminate/getptd bytes are owned terminal INT3 instructions. Complete original
prolog/getptd/abort reviews account for 22/49/23 reachable instructions.

Pinned `frame.cpp` defines the noexcept helper as a call to `terminate`.
Pinned UCRT `terminate.cpp` reads the per-thread terminate handler, invokes it
inside SEH and calls `abort` whether it returns or faults. Its PTD declaration
places `_terminate` at offset twelve. The complete original implements this
same sequence; its thunk JMP selects the terminate entry, and fixed direct
CALLs at `0x0047B82C`, `0x0047B831` and `0x0047B85B` select the prolog, PTD
getter and abort. The complete getter preserves last error, gets or allocates
the 868-byte PTD, stores it through FLS and aborts on failure. The abort entry
checks SIGABRT, report-fault behavior and fast-fail availability before fatal
exit status three. Their source roles and complete bodies establish callee
identities without assigning identities or exact credit to nested helpers.

Terminate contains eighteen original instructions across its main entry,
four-byte filter at offset 40 and exceptional continuation at offset 44.
Its original 28-byte SEH table at `0x0049BA78` independently selects both
interior entries. The candidate table at `0x0049B750` is one complete private
28-byte `__sehtable$_terminate` PDB contribution from terminate.obj. Its four
cookie fields are -28/0/-44/0, followed by state -2 and pointers to those same
relative filter/continuation roles. All table bytes, permissions, names,
module ownership and pointer relocations 20/24 are checked. Candidate runtime
instruction fields are exactly 3/8/13/32/55, with PE relocations 3/32. Every
terminate byte, including its candidate's final trap, and every thunk byte is
checked against the independently bound roles.

The guarded indirect call uses original slot `0x0048B2BC` and the unique
complete four-byte candidate `___guard_check_icall_fptr` storage. Both agree
with their load-config structure's field at offset 72. The original structure
declares 104 bytes although its PE data-directory entry advertises 64; this
is a storage witness and makes no claim about loader use of the later fields.
Cookie storage remains independently identified at load-config offset 60.

## Complete frames and state lifetime

Stage reserves two local words and saves EBX/ESI/EDI. Its full forty-byte
registration places the encoded cookie at EBP-36, node minus twenty-four.
ItemManager reserves one local word with the same three saves; its full
38-byte registration places the cookie at EBP-32, node minus twenty. Both
complete eighteen-byte restorations end in the sole RET. Prefix relocations
are 6/24 and 6/22 respectively; suffixes have none.

Every EBP/FS use, saved pointer, state write and restoration is fixed. Stage
writes state zero from ECX at offset 936, after the defining XOR at 891; the
verifier rejects intervening ECX writes/calls and branch entries that could
bypass that definition. State one is set at 963. ItemManager writes states
zero/one at 298/329. The states cover the final two member-array destructor
iterator calls; either escaping exception reaches the terminal action.

Only these two fixed roles are admitted by `two-state-terminate-v1`. Adding
node-24 to the shared handler decoder does not broaden existing frame rules.
The separately checked AnmManager constructor already has its own node-24
aggregate and retains it. All earlier profile proof dictionaries and results
remain identical. Other terminate-only state counts, flags and frames remain
outside this profile.

## Results, controls and retained evidence

Canonical replay reports **869 exact, 65 mismatch and 281 incomplete** among
1,215 annotations, covering **163,539 exact primary bytes and 934 units**.
All preceding 867 exact results, 65 complete mismatches and 932 unit definitions
remain identical, as do all other incomplete records. The 54 auxiliary code
bytes, 104 metadata bytes, SEH table and runtime chain receive no extra primary
credit. Ordinary parent body mutations still fail whole-owner comparison.

**231 controls pass** across ten suites: terminate EH (23), array constructor
EH (18), member constructor EH (25), allocation cleanup (23), saved-register
EH (37), legacy empty EH (25), AnmManager constructor EH (25), reviewed
linkages (38), strict Oracle (14) and focused audit (3). Controls cover every
candidate handler/data byte, every terminate/thunk/SEH-table byte, semantic
changes after original hash updates, state-definition bypass/clobbering,
cross-parent edges, source/module ownership, full extents, private names and
all pointer relocations. Runtime rows reject shortened original/candidate
owners, wrong pinned libraries and incorrect direct instruction witnesses.

No build occurs. The source input remains
`c2ac9cc0add85924f097edf2dc772148551601b302607cc480fba1867a1fcd5a`.
All 1,719 complete linked owner records, the receipt/artifacts and 192
dependency stamps remain unchanged. The build graph and ignored evidence are
retained. Source-origin review and formal Factory acceptance remain open.

Original-only scope evidence is `.analysis/terminate-original-scopes.json`,
reproduced by `.analysis/review-terminate-originals.py`. Complete primary and
auxiliary payloads, fields, relocations, runtime producers and pinned source
hashes are `.analysis/terminate-caller-scopes.json`, reproduced by
`.analysis/review-terminate-callers.py`. Earlier investigation remains in
`.analysis/terminate-{entry-investigation,runtime-scopes}.json`.
Artifact/regression checks are `.analysis/terminate-{artifact,regression}-check.json`
with matching `check-*.py` reproducers. Terminal logs and the control summary
use `.analysis/terminate-*`.
