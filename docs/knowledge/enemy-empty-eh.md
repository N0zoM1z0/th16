# Enemy destructor frames and complete virtual table

The complete EnemyManager and EnemyInf destructor graphs use the same empty
36-byte EH3 descriptor as the earlier reviewed destructors, but their saved
register frame places the cookie at a different offset. One explicit frame
profile now validates this variant. The complete EnemyInf vftable is also
independently identified through original RTTI and six fixed method entries.
Three complete source owners pass, adding 1,881 primary bytes.

## Complete original owners and auxiliary graphs

| Parent | Complete parent | Original private handler | Original FuncInfo |
| --- | --- | --- | --- |
| `EnemyManager::~EnemyManager` | `0x0041B1A0`, 414 bytes | `0x0048A670`, 27 bytes | `0x0049B22C`, 36 bytes |
| `EnemyInf::~EnemyInf` | `0x0041BA10`, 306 bytes | `0x0048A690`, 27 bytes | `0x0049B250`, 36 bytes |

The parents independently contain 118/90 reachable instructions. Every branch
target, terminal path and following INT3 interval is checked from the original
alone. Each fixed registration PUSH supplies its parent-specific handler role.
The original handler extents end before five INT3 bytes. Neither range is
trimmed to its final jump or promoted to a public code function.

Each complete descriptor contains the nine words
`19930522 0 0 0 0 0 0 0 5`. Tables remain empty and flags must equal five;
other flags and nonempty unwind/catch graphs remain unsupported by this profile.
Both candidate graphs have unique complete private MAP/PDB owners in
`Enemy.obj`, in the same PDB module as their respective complete parents.
Identical descriptor bytes do not make the two private names interchangeable.

The complete handler remains seven instructions / 27 bytes: recover the
registration node, derive EBP, load and decode the cookie, call its independently
bound checker, load this parent's FuncInfo and tail-transfer to the independently
bound `___CxxFrameHandler3`. The sole handler PE relocation is the FuncInfo
operand at offset 18; both descriptors have no relocations. All 54 auxiliary
code bytes and 72 metadata bytes are checked without receiving additional
primary exact credit.

## Independently derived saved-register frame

The profile is `empty-eh3-saved-ebx-esi-edi-v1`. It is selected explicitly in
`config/eh-handlers.toml`; there is no automatic offset fallback or configurable
cookie displacement. The earlier empty profile still uses node minus four,
and the nonempty AnmManager constructor profile keeps its separate rules.

| EBP-relative slot | Content |
| --- | --- |
| -4 | initial EH state, -1 |
| -8 | this parent's private handler |
| -12 | previous FS head; registration node address |
| -16 | one local word |
| -20 | saved EBX |
| -24 | saved ESI |
| -28 | saved EDI |
| -32 | encoded cookie |

The node is EBP-12 and the cookie is EBP-32, so the handler must read
`[node - 20]`. This relationship is derived from the complete 38-byte parent
registration sequence, rather than accepted from the handler's displacement
byte. Cookie storage is independently obtained from the PE32 load configuration.

The verifier checks the exact saved-register prefix and the complete 18-byte
normal restoration suffix. It decodes the whole parent and checks all direct
uses of the four reserved EH/cookie slots, FS references, EBP writes and the
single final RET. Unexpected state/cookie accesses and alternate restoration
sequences are refused. The candidate prefix requires exactly the handler and
cookie relocations at offsets 6/22; the suffix has none.

This profile binds only the existing four-byte registration field at offset
six in its complete named parent. Every other parent instruction and field
still undergoes ordinary complete byte replay. No frame byte or body interval
is masked, and the handler cannot be reused by another source/parent.

## Complete EnemyInf primary table

Original RTTI name, primary CompleteObjectLocator and locator-pointer references
independently identify the EnemyInf address point at `0x004921A8`. Its complete
six-slot run ends at a non-executable word. The candidate public at `0x00492590`
is four bytes into a complete 28-byte PDB table object, including the locator
pointer. The existing vftable verifier needs no change.

| Slot | Original entry | Contract |
| --- | --- | --- |
| 0 | `0x0041DCA0` | `run_over_300` |
| 1 | `0x00423810` | `get_int_global` |
| 2 | `0x00423F80` | `get_int_global_ptr` |
| 3 | `0x00424110` | `get_float_global` |
| 4 | `0x00424C10` | `get_float_global_ptr` |
| 5 | `0x0041A760` | scalar deleting destructor |

All six entries have pre-existing fixed original identities and complete
candidate code owners. The complete EnemyInf/SptInf inheritance graph has ten
candidate metadata objects, 194 bytes and twenty pointer relocations, including
shared SptInf base records. These totals are not additional primary credit or
an independent new allocation of all shared records. The normal EnemyInf
destructor at `0x0041BA10` is distinct from its table's deleting wrapper.

## Complete primary results

| Primary owner | Whole bytes | Result |
| --- | ---: | --- |
| `EnemyManager::~EnemyManager`, `0x0041B1A0` | 414 | exact |
| `EnemyInf::EnemyInf(const char *)`, `0x0041B580` | 1,161 | exact |
| `EnemyInf::~EnemyInf`, `0x0041BA10` | 306 | exact |

The constructor's original-only scope contains 170 reachable instructions,
all branches and terminal paths, plus the full following INT3 interval.
Whole original/candidate payloads, exhaustive fields, PE relocations, private
owners and standalone replays are retained for all three parents.

Canonical replay reports **849 exact, 65 mismatch and 301 incomplete** among
1,215 annotations, with **156,629 exact primary bytes and 914 units**. All
previous 846 exact results, 65 complete mismatches and 911 unit definitions
remain identical. The new primary bytes total **1,881**.

## Rejection controls and retained evidence

**150 controls pass**: saved-register EH (17), legacy empty EH (25), constructor
EH (25), vftables (30), reviewed linkages (36), strict Oracle (14) and focused
audit (3). New controls cover explicit profile selection, wrong cookie offsets,
forged original hashes, wrong saves/restores, PE cookie witnesses, reserved
state/cookie writes, EBP replacement, nonempty descriptors, truncated private
owners, missing/duplicate/crossing relocations and cross-parent graph reuse.
A body-register mutation preserves a valid EH graph but still fails whole-parent
byte comparison. Existing vftable mutations also cover EnemyInf's six slots.

No game source or compiler artifact changes and no build occurs. The unchanged
input is `c2ac9cc0add85924f097edf2dc772148551601b302607cc480fba1867a1fcd5a`.
All 1,719 complete linked owners and 192 incremental dependency stamps validate.
There is no cold build, cleanup, archived-output substitution, Factory submission
or remote publication.

Original proofs are `.analysis/enemy-eh-original-scopes.json`,
`.analysis/enemy-constructor-original-scope.json` and
`.analysis/enemy-vftable-original-location.json`. Reproducers are
`.analysis/review-enemy-eh-originals.py`,
`.analysis/review-enemy-constructor-original.py` and
`.analysis/review-enemy-vftable-original.py`. Complete private/caller evidence
is `.analysis/enemy-eh-caller-scopes.json`, reproduced by
`.analysis/review-enemy-eh-callers.py`; full table/RTTI evidence is
`.analysis/enemy-vftable-graph-proof.json`. Artifact/graph preservation is
`.analysis/enemy-eh-artifact-check.json`. Canonical replay, controls and regression
proof are `.analysis/enemy-eh-full-audit.log`,
`.analysis/enemy-eh-controls-summary.json` and
`.analysis/enemy-eh-regression-check.json`.
