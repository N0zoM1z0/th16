# Five complete allocation-cleanup EH graphs

Five creation methods use one unwind action to release an allocation if object
construction throws. The explicit `allocation-cleanup-v1` profile checks their
complete private code, one-state maps, allocation sizes and parent frames.
All five complete primary owners pass, adding 834 exact bytes.

## Complete original parents and private roles

| Parent | Original scope | Reachable instructions | Allocation size | Cleanup | Handler | FuncInfo |
| --- | --- | ---: | --- | --- | --- | --- |
| `Stage::create` | `0x00409DB0`, 156 bytes | 56 | `0x66F0` | `0x0048A470` | `0x0048A482` | `0x0049B044` |
| `BulletManager::create` | `0x00411DD0`, 147 bytes | 50 | `0x1403B28` | `0x0048A560` | `0x0048A572` | `0x0049B118` |
| `ItemManager::create` | `0x0042F440`, 147 bytes | 50 | `0x1C972EC` | `0x0048A820` | `0x0048A832` | `0x0049B3E0` |
| `ReplayManager::create` | `0x00447E20`, 193 bytes | 66 | `0x31C` | `0x0048A900` | `0x0048A912` | `0x0049B4C8` |
| `ReplayManager::create_from_file` | `0x00447EF0`, 191 bytes | 64 | `0x31C` | `0x0048A930` | `0x0048A942` | `0x0049B4F4` |

Original-only review decodes and reaches every parent instruction, checks all
branch destinations and both terminal paths, excludes interior inventory
entries and accounts for every following INT3 byte. Each fixed registration
PUSH selects its handler, which selects FuncInfo and its one-entry unwind map.
The map selects the cleanup. No candidate labels or matching scores select
these original roles.

Each cleanup is an independently inventoried complete eighteen-byte function:
push the fixed object size, read the saved allocation from EBP-16, push that
pointer, call sized delete, remove both arguments and return. The adjacent
27-byte handler forms a complete 45-byte aggregate, followed by three INT3
bytes. Its internal handler entry at offset eighteen never becomes a standalone
PDB owner or an extra primary match.

## Complete candidate owners and shared map checks

| Source object | Candidate parent | Complete code owner, 45 bytes | Complete data owner, 44 bytes |
| --- | --- | --- | --- |
| `Stage.obj` | `0x0046A7D0` | `0x0048AAF0` | `0x0049B3F4` |
| `BulletManager.obj` | `0x0041B0D0` | `0x0048A510` | `0x0049AE20` |
| `Item.obj` | `0x004406D0` | `0x0048A850` | `0x0049B140` |
| `ReplayManager.obj` | `0x00463C80` | `0x0048A970` | `0x0049B254` |
| `ReplayManager.obj` | `0x00463D50` | `0x0048A9A0` | `0x0049B280` |

Parent-qualified private MAP names must identify exactly the cleanup at code
offset zero and handler at eighteen. Data must have the unwind map at zero
and FuncInfo at eight. Every aggregate requires its complete same-start PDB
contribution, matching source producer/module, correct section permissions
and absence of other overlapping, public or interior names.

The original stores FuncInfo before its map: 36 bytes followed by eight bytes.
The candidate stores the map before FuncInfo. Both complete 44-byte layouts
are checked explicitly, including magic `0x19930522`, one state, flags one,
all zero reserved/try/catch fields and the sole transition from state zero
to -1 through this parent's cleanup. Candidate data relocations are exactly
4/16. The code has exactly four instruction fields at 10/31/36/41, with its
only PE relocation at 36. Every other action and handler byte is checked too.

The ownership, original cleanup boundary and complete map checks are shared
with the [member constructor profile](member-constructor-eh.md). This shared
helper now accepts only four reviewed action lengths, 11/14/18/30, after the
[array/thread constructor review](array-thread-constructor-eh.md);
each caller separately enforces its fixed source roles, action semantics and
parent frames. Both earlier member-constructor proof dictionaries and their
complete primary results remain identical. Array cleanup uses a separate fixed
profile; other map/state shapes receive no implicit support.

## Allocation lifetime and complete frames

The allocation instruction and cleanup must use the same fixed size from the
method's class role. The original allocator at `0x004749AC` and sized delete at
`0x004749DF` already have independent complete runtime bindings of 51/14 bytes.
Cookie checking and `___CxxFrameHandler3` likewise require their independent
bindings. Source `new` expressions and complete primary replay agree with the
fixed size operands; configuration cannot supply an arbitrary allocation size.

| Frame | Local bytes | Saved registers | Cookie from node | Prefix bytes | Restore bytes | Original RET offsets |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| Stage create | 8 | ESI, EDI | -20 | 39 | 17 | 136, 155 |
| Bullet/Item create | 4 | ESI | -12 | 36 | 16 | 128, 146 |
| Replay create | 4 | ESI, EDI | -16 | 37 | 17 | 173, 192 |
| Replay create from file | 4 | ESI, EDI | -16 | 37 | 17 | 171, 190 |

The registration node is EBP-12. Local storage, fixed register saves and the
encoded cookie derive each displacement. PE load configuration independently
identifies cookie storage. The exact prefixes establish initial state -1 and
the frame layout. Complete parent decoding checks every EBP/FS instruction,
the saved allocation at EBP-16, state zero before construction and state -1
after construction. Both complete restoration sequences and exactly the two
reviewed RET offsets are required. Prefix relocations are 6/23, 6/20 and 6/21
for the three frame layouts; every restoration has none.

Node-12 support is confined to this fixed allocation frame. Existing empty,
member-constructor and AnmManager profiles retain their displacement/state
rules. There is no configurable stack allocation, register sequence or cookie
offset. All ordinary primary body bytes and fields remain fully compared.

## Results and refusal controls

Canonical replay reports **865 exact, 65 mismatch and 285 incomplete** among
1,215 annotations, covering **161,453 primary exact bytes and 930 units**.
All previous 860 exact results, 65 complete mismatches and 925 unit definitions
remain identical. Every other incomplete record is also identical. The five
whole passes contribute 834 bytes; auxiliary code (225 bytes), metadata
(220 bytes) and runtime callees receive no additional primary credit.

**187 controls pass** across eight suites: allocation EH (23), member
constructors (24), saved-register frames (37), legacy empty EH (25), AnmManager
constructor EH (25), reviewed linkages (36), strict Oracle (14) and focused
audit (3). New controls mutate every aggregate byte, original semantic fields
after hash updates, allocation sizes/targets, saved pointers, state lifetimes,
both normal exits, private names/extents, cookie witnesses, all four runtime
roles and exhaustive relocations. Foreign graph edges and extra returns are
rejected. Node-12 mutations are rejected by every earlier profile. Ordinary
body register mutations preserve valid EH but fail whole-primary comparison.

The new module is explicitly fingerprinted. No game source or compiler artifact
changes and no build occurs. All 1,719 complete linked owners and 192 dependency
stamps validate; the source input remains
`c2ac9cc0add85924f097edf2dc772148551601b302607cc480fba1867a1fcd5a`.
The current build graph and ignored evidence remain retained. Source-origin
review and formal Factory acceptance remain open.

Original-only scopes are `.analysis/allocation-eh-original-scopes.json`,
reproduced by `.analysis/review-allocation-eh-originals.py`. Full graphs,
payloads, fields, relocations, both exits and standalone replays are retained in
`.analysis/allocation-eh-caller-scopes.json`, reproduced by
`.analysis/review-allocation-eh-callers.py`. Artifact/regression evidence is
`.analysis/allocation-eh-{artifact,regression}-check.json` with matching
`check-*.py` reproducers. Terminal audit and control logs use
`.analysis/allocation-eh-*`.
