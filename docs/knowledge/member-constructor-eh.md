# Complete single-member constructor EH graphs

Stage and ItemManager construction each register a single unwind action for
their first completed member. Their complete private code and metadata have
different internal roles from the empty destructor graphs. The explicit
`single-member-constructor-v1` profile independently checks these two graphs.
Both complete primary parents now pass, adding 409 exact bytes.

## Original scopes and fixed roles

| Parent | Complete original | Reachable instructions | Cleanup | Handler | FuncInfo | Unwind map |
| --- | --- | ---: | --- | --- | --- | --- |
| `Stage::Stage` | `0x00409670`, 249 bytes | 65 | `0x0048A400` | `0x0048A40B` | `0x0049AFC0` | `0x0049AFE4` |
| `ItemManager::ItemManager` | `0x0042F0B0`, 160 bytes | 47 | `0x0048A7B0` | `0x0048A7BB` | `0x0049B35C` | `0x0049B380` |

Original-only review decodes and reaches every parent instruction, checks the
final return and all following alignment, and excludes interior inventory
entries. Stage has seven following INT3 bytes. ItemManager ends immediately
before its inner destructor. Each parent's fixed registration PUSH identifies
the handler; the handler identifies FuncInfo; its one-entry map identifies the
cleanup. These original edges establish the scopes before candidate comparison.

Each cleanup has an independently inventoried complete eleven-byte scope:
read the complete-object pointer from EBP-16, add the fixed member offset and
tail-transfer to that member's normal destructor. Its adjacent complete
27-byte handler forms a 38-byte aggregate, followed by ten INT3 bytes. The
handler remains an interior private entry and receives no standalone owner.

| Parent | Fixed member | Offset | Complete destructor identity |
| --- | --- | ---: | --- |
| Stage | `inner` | 12 | `StageInner::~StageInner`, `0x00409770`, 73 bytes, `src/Stage.cpp` |
| ItemManager | `inner` | 20 | `ItemManagerInner::~ItemManagerInner`, `0x0042F150`, 70 bytes, `src/Item.cpp` |

Source layouts and the original cleanup instructions agree on both offsets.
The destructor roles require fixed source/symbol/target/extent tuples, complete
original hashes and unique complete source-qualified candidate PDB/public
owners. Both destructors already have independent exact primary units; their
use here grants no additional credit.

## Complete candidate aggregates and metadata order

| Source object | Parent | Code aggregate | Handler interior entry | Data aggregate | FuncInfo interior entry |
| --- | --- | --- | --- | --- | --- |
| `Stage.obj` | `0x0046A0B0` | `0x0048AA80`, 38 bytes | `0x0048AA8B` | `0x0049B370`, 44 bytes | `0x0049B378` |
| `Item.obj` | `0x00440340` | `0x0048A7E0`, 38 bytes | `0x0048A7EB` | `0x0049B0BC`, 44 bytes | `0x0049B0C4` |

Each code object must have exactly the parent-qualified private names
`__unwindfunclet$<parent>$0` at zero and `__ehhandler$<parent>` at eleven. Each
data object must have exactly `__unwindtable$<parent>` at zero and
`__ehfuncinfo$<parent>` at eight. The complete same-start PDB contributions,
source objects, module agreement, section permissions and absence of other
overlapping, public or interior owners are mandatory.

Original and candidate metadata have different complete layouts:

| Layout | First bytes | Remaining bytes |
| --- | --- | --- |
| Original, 44 bytes | FuncInfo, 36 bytes | unwind entry, 8 bytes |
| Candidate PDB owner, 44 bytes | unwind entry, 8 bytes | FuncInfo, 36 bytes |

Both full layouts are checked explicitly. FuncInfo has magic `0x19930522`,
exactly one state, its independently located map pointer, zero try/catch and
other reserved fields, and flags one. The sole unwind entry transitions to
state -1 and names this parent's complete cleanup action. There is no automatic
layout search, empty-table fallback or configurable member/state offset.
Candidate data relocations are exactly offsets 4/16. The complete code has
exactly four instruction fields, at 7/24/29/34, and one PE relocation at 29.
All action and handler bytes are checked, including the independently bound
cookie checker and `___CxxFrameHandler3` transfers.

## Parent frame and state lifetime

Both parents reserve two local words after their EBP-12 registration node.
EBP-16 retains the complete `this` pointer; EBP-20 holds a member/array scratch
pointer. Stage saves ESI/EDI, placing the cookie at EBP-32, or node-20.
ItemManager saves ESI, placing the cookie at EBP-28, or node-16. The cookie
storage pointer is independently read from each image's PE load configuration.

Stage's exact 44-byte prefix includes registration, both local words, saves,
cookie setup and saved `this`; ItemManager's prefix has 43 bytes. Their complete
normal restoration suffixes have 17/16 bytes. Required prefix relocations are
6/23 and 6/22 respectively; suffixes have none. Every EBP/FS instruction in
each complete parent is fixed, including initial state -1, the sole explicit
state-zero write, saved-this/scratch accesses and the final restoration/return.
State zero is established after the first member is complete and before the
second member construction can throw. Its action destroys only the first member.

This verifier binds only the existing registration operand at offset six in
its exact complete parent. All other body bytes and fields undergo ordinary
whole-owner replay. The profile is restricted to these two fixed constructor
roles. Allocation cleanups in `Stage::create` and `ItemManager::create`, array
cleanup graphs and other nonempty graphs remain outside its scope.

## Results, refusal controls and retained evidence

Canonical replay reports **860 exact, 65 mismatch and 290 incomplete** among
1,215 annotations, with **160,619 exact primary bytes and 925 units**. The new
249/160-byte passes add 409 bytes. All previous 858 exact results, 65 complete
mismatches and 923 unit definitions remain identical. Every other incomplete
record is also identical. Auxiliary code (76 bytes), metadata (88 bytes) and
already bound cleanup callees receive no additional primary credit.

**164 controls pass** across seven suites: member constructors (24), saved
register frames (37), legacy empty EH (25), AnmManager constructor EH (25),
reviewed linkages (36), strict Oracle (14) and focused audit (3). New controls
mutate every candidate aggregate byte, original semantic fields after hash
updates, complete extents, module ownership, private labels, source roles,
state/saved-this accesses, cookie storage, graph edges and exhaustive relocation
sets. Interior returns and wrong parent scopes are rejected. A body flag-byte
mutation preserves valid EH but still fails the complete primary comparison.
The new verifier module is explicitly included in the Oracle input fingerprint.

No game source or compiler artifact changes and no build occurs. All 1,719
complete linked owner records and 192 dependency stamps validate. The source
input remains `c2ac9cc0add85924f097edf2dc772148551601b302607cc480fba1867a1fcd5a`.
The current build graph and ignored evidence are retained. Source-origin review
and formal Factory acceptance remain open.

Retained ignored evidence includes `.analysis/member-constructor-original-scopes.json`
and its reproducer `.analysis/review-member-constructor-originals.py`;
`.analysis/member-constructor-caller-scopes.json` and
`.analysis/review-member-constructor-callers.py`; and the artifact/regression
checks `.analysis/member-constructor-{artifact,regression}-check.json` with
their matching `check-*.py` reproducers. Complete raw payloads, decoded fields,
relocations, private roles and standalone replays are retained. Terminal audit
and control logs use `.analysis/member-constructor-*`.
