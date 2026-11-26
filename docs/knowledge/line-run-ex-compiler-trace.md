# Line EX cursor, aliasing and loop layout

The active owner is `LaserLineInf::run_ex` at `0x431fe0`, in `src/Laser.cpp`.
Its independently reviewed target owns 1,588 bytes: 1,550 code bytes, two
alignment bytes, five absolute jump entries and a 16-byte selector map.
There are 327 actual code instructions. Older linear measurements also
decode the tables and must not be used as code-only instruction counts.
The scope comes from [the remapped-owner review](remapped-owner-scopes.md).

The retained typed-blend checkpoint owns 1,592 bytes and remains incomplete
in the local strict audit. Its cursor calculation, EDX entry index, ECX type,
BLEND masks and both branch-local member increments agree with the target.
The remaining operation differences after code alignment are the common
loop/return block's late position and SHOOT's X input order.
`blend-field-view-focused.json` also rechecks the four completed owners.
All private controls and scripts below are in
`.analysis/line-run-ex-compiler/`; preserve that directory and the incremental
build. These diagnostic controls do not establish Factory acceptance.

## Cursor and index repairs

At checkpoint `2933b80`, the owner is 1,596 bytes. A volatile instruction
pointer introduces an extra stack store/reload. Following the finding in
[the curve EX investigation](curve-run-ex-compiler-trace.md), SHOOT should
advance the actual cursor for its paired command. The target computes
`this + 0x60c` and adds the scaled index, retaining the resulting pointer.

TAG consumes the saved entry index: `ex_index = index + 1`, rather than a
member increment. With the volatile pointer still present, this restores
EDX for that index. Removing the volatile pointer and advancing `ex` in
SHOOT fixes the pointer calculation, but initially puts index/type in
ECX/EDX and turns both BLEND member INCs into cached-index LEA/store updates.

Returning BLEND to the common completion path restores register roles but
shares away one required branch-local increment. Keeping its continuation
and assigning through the existing four-bit
`AnmVmFlagsLoFields::blend_mode` view instead preserves both memory INCs,
the target masks and EDX/ECX roles. This is the retained source checkpoint.
Its complete raw body SHA-256 is
`9c3967ecdd40c11ea6cea8afbe00847a383337fcc3b9465910a4c5b846763b64`.
The four-byte extent difference still prevents a local strict pass.

## Loop placement is not lexical placement

The target's common increment, loop test and return follow SPEEDUP, beginning
at +0xae. The candidate puts them near WAIT at the function tail. This also
forces longer entry-guard and selector-range branches. Those branch sizes
are part of the complete owner and cannot be ignored as alignment.

An explicit shared `advance_ex` label provides a semantic marker without
changing the paired-cursor candidate's complete 1,596-byte body. At
`dop2_InitialOptsAndSetup` entry, the label and actual increment are directly
after SPEEDUP. Hardware link watches locate expression rewrites, but tuple
links also serve as temporary expression scratch and tuple addresses can be
reused. Follow the label in the current flow graph to measure block order.

`shared-advance-dfo-block-order.jsonl` follows `$advance_ex`, label ID
100088, at pass entry and actual return. `FgThreadDFOAndFreeDeadCode` first
reduces the graph from 82 to 80 blocks while leaving this block at index 29.
The following `FgChangeNextToDFOEx` moves it to index 73 of 81. Later graph
rebuilds change addresses and counts but keep its late placement. The normal
read-only replay reproduces all 1,596 ordinary bytes, SHA-256
`2ca7d5acb6655cc4c8209a223e567a4365366d4845b08c5bfb3937bdb1ea08cc`.

The graph layout derived from `FgChangeNextToDFOEx` is: graph +0 first block,
+4 last block, +8 DFO head; block +0 next, +0x10 DFO successor, +0x1c starting
tuple marker. A label record stores its character pointer directly at +4
and numeric ID at +0x28. This differs from the indirection used for backend
variable names.

Controls before the typed blend repair retain the earlier aliasing context:

| Control prefix | Complete bytes | Finding |
| --- | ---: | --- |
| `tag-index` | 1596 | Repairs saved-index use with the volatile cursor still present |
| `paired-command-cursor` | 1596 | Repairs cursor; exposes BLEND cached-index updates |
| `speedup-continue` | 1604 | Adds a SPEEDUP INC; loop test/return stay late |
| `explicit-default` | 1612 | Default/SPEEDUP share an early INC; another common INC stays late |
| `shared-advance` | 1596 | Explicit single advance label is byte-identical to paired cursor |
| `loop-index-guard` | 1608 | Loop-carried index moves to EBX and adds entry/latch copies |
| `fresh-index-guard` | 1608 | Same entire body as the loop-carried for-index control |
| `blend-common-advance` | 1580 | Repairs index roles but loses one BLEND increment |

The two 1,608-byte index controls have raw SHA-256
`dade840526bb654719423dfd20b3935747e57a5421ff1365a94596aa59d2e854`.
Neither is retained.

Controls from the typed-blend checkpoint distinguish source syntax, actual
aliasing changes and duplicated completion paths:

| Control prefix | Complete bytes | Finding |
| --- | ---: | --- |
| `typed-speedup-continue` | 1596 | Still leaves test/return late and adds a separate INC |
| `loop-exit-break` | 1592 | Replacing body returns with loop breaks is byte-neutral |
| `guarded-do-while` | 1592 | Entry guard plus do/while is byte-neutral |
| `named-origin-x` | 1592 | One-use X reference inside SHOOT is byte-neutral |
| `shared-origin-x` | 1588 | Shared PLAY_SOUND/SHOOT reference retains an EBX address and changes ACCEL's parameter setup; X order and late loop remain wrong |
| `speedup-last` | 1592 | Moves SPEEDUP within the jump-table region, without moving the common tail |
| `each-case-advance` | 1632 | Case-local increments remain separate and alter index/type allocation |
| `vector-add-shoot` | 1592 | D3DX vector addition followed by Z flattening is byte-neutral |
| `signed-switch` | 1547 | Removing the unsigned cast replaces the selector/jump table with a signed comparison tree; the cast is required by target evidence |
| `shoot-origin-vector` | 1592 | A shared vector pointer for the two coordinate reads is byte-neutral |
| `size-policy` | 1455 | Temporary size optimization removes the jump table and changes registers and zero materialization; it does not match the target |
| `wait-continue` | 1600 | Moves the common path before WAIT but retains an additional WAIT INC |
| `dispatch-check-header` | 1592 | An explicit shared check entered before dispatch is byte-neutral |
| `separate-shot-offset` | 1592 | Separate polar output grows the frame from 0x394 to 0x39c, without fixing X input order or the common loop position |

The byte-neutral controls reproduce the checkpoint's entire raw body, not
just its code alignment. The shared-X control demonstrates why matching
extent alone is insufficient: its 1,588 bytes still fail strict comparison.
All of these trial source forms are restored after evaluation.

## SHOOT X ordering and complete observer boundaries

Earlier notes called the remaining coordinate mismatch Y. The real layout
is X at `this+0x54` and shooter `ESP+0x20`; Y is at `this+0x58` and
`ESP+0x24`. The target wants stack-first for X and heap-first for Y.
The candidate is heap-first for both. The corrected source TODO and future
controls must follow this field identity.

`loop-exit-break-canonical-full.jsonl` observes actual Lower, NColor,
CodegenUpdate and EmitFunction return PCs with matching stack pointers.
The replay exits normally and reproduces the entire ordinary 1,592-byte
owner; its `*-control.json` records full-body equality and SHA-256.
The observed sorter runs all occur during prelowering. They place the heap
memory expression before the scalarized shooter field: X has memory key
`0x10256dd` and scalar key `0x10120`; Y has memory key `0x10256e5` and scalar
key `0x101c0`. No further calls to that selected sorter are recorded through
actual emission return. The one-use X-reference and vector-add controls do
not repair final native ordering; naming alone is not sufficient.

Two probe boundaries required correction. `EmitFunction` entry precedes
allocation: it calls post-lower global optimization and global allocation
internally. Stopping there cannot establish that NColor was absent.
Also, RVA `0x78774` is `NColProcessCandidate` entry, not NColor return.
The 83 old `ncolor-exit` events in `paired-command-flow-complete.jsonl`
are candidate-entry snapshots. Its later codegen/flow/pre-encode snapshots
and full-body control remain valid. The newer canonicalization replay uses
real returns and preserves observation through emission.

The active questions are which later flow decision can place the actual
common loop block after SPEEDUP, and which real X address/value lifetime
produces the target's operand order. Keep these separate from failed lexical
label moves and byte-neutral syntax changes.


The signed-switch replay owns 1,547 code bytes, with 332 instructions and
no selector/jump table. Use `signed-switch-replay-*` for its native evidence.
The private alignment helper's usual 36-byte table suffix assumption does
not apply to this control; its explicit code extent is 1,547. The size-policy
control likewise has no selector/jump table and uses all 1,455 code bytes.

A retrospective diagnostic accidentally paired the old signed report with
a newer executable. Its native outputs are quarantined under
`signed-switch-wrong-build-*`; the strict reports were unaffected. The helper
now checks the executable SHA-256 against the strict report before writing
anything. `wrong-build-rejected.log` records the negative check, and the
current-owner positive control and signed replay use matching identities.
The signed replay has the same source-input identity as the original signed
build. Do not overwrite old native evidence from a report after replacing
the executable it names.
