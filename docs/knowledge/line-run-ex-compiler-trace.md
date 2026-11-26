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
| `d3dx-shoot-add` | 1592 | The SDK free-function add is also byte-neutral in this owner, despite useful operand-order differences recorded for other owners |
| `value-vector-shoot-add` | 1588 | Value-returning addition grows the frame to 0x39c and packs the XY result with UNPCKLPS/MOVQ; neither X order nor common-loop placement is repaired |
| `coordinate-loop-shoot-add` | 1592 | A two-coordinate indexed loop is unrolled/normalized to the same entire checkpoint body |
| `scalar-shot-x-accumulator` | 1592 | A real scalar X accumulator also produces the same entire checkpoint body |
| `wait-timer-assignment` | 1592 | The ordinary timer assignment API in WAIT is byte-neutral against the forced inline helper |
| `explicit-ignored-anim` | 1592 | An explicit no-op case for opcode 2 is merged into the same complete default-path body |
| `tail-recursive-dispatch` | 1592 | The self call disappears, but the frame loses ESP realignment and uses EBP-relative slots; the common loop remains late |
| `definition-annotation-only` | 1592 | Removing the definition annotation is byte-neutral because the header declaration still enforces noinline; this does not test the effective inline policy |
| `advancing-origin-component` | 1592 | A real X-to-Y pointer advance is also normalized to the same complete checkpoint body |
| `opaque-polar-interface` | 1592 | Changing the helper destination to void* leaves Line and the complete 32-byte helper unchanged; the new decorated private name lacks bindings, so the trial is restored without changing Oracle configuration |
| `cached-unsigned-opcode` | 1608 | Capturing type once changes dispatch register use and folds ANGLE/WRAP flag updates to constants; X ordering and the late common loop remain wrong |
| `default-at-speedup-exit` | 1592 | An explicit default label at SPEEDUP's existing break, keeping the one common increment, is byte-neutral |
| `speedup-explicit-bound` | 1608 | Explicit SPEEDUP increment and exit guard retain a separate memory comparison and jump, plus the late common increment/test/return; no repair |
| `for-member-advance` | 1572 | Moving the member increment to a for-loop step removes required branch-local increments, folds away the saved TAG index, retains LOOP's decrement, and leaves X and the late common tail wrong |
| `effective-inline-policy` | 1592 | Removing noinline from both the Line declaration and definition is now a real policy control and is byte-neutral; six other focused owners pass and the on_tick diagnostic byte span is unchanged |
| `index-without-register` | 1592 | Removing the saved-index register keyword with the header restored is byte-neutral; the same six other focused owners pass |

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


## A canonical-return swap does not reach native X ordering

`line-x-control-*` is an unmodified-compiler replay from the corrected
coordinate baseline. It exits normally and matches all 1,592 ordinary bytes,
including the switch tables, with the checkpoint's `9c3967...` raw SHA-256.
The paired `line-x-swap-*` replay changes only the X input chain, at six actual
FactCanonSort return PCs with matching stack pointers and threads. Its JSONL
records the memory-first chain before each intervention and the scalar-first
chain afterward. The X field is identified by the `_shooter` parent and its
8-byte subobject offset, rather than by a transient tuple address.

The modified-compiler replay also exits normally and emits the same entire
1,592-byte body, SHA-256
`9c3967ecdd40c11ea6cea8afbe00847a383337fcc3b9465910a4c5b846763b64`.
Its control explicitly records `compiler_modified: true` and
`source_acceptance: false`. This does not establish independence of X ordering
and loop layout: the intended X change did not survive to the native code.
The boundary follow-up below locates the restoration before Lower. Do not
assume that a FactCanonSort return fixes final SSE operand order.

`BombMain.cpp` and `Gui.cpp` contain useful D3DXVec3Add operand-order notes;
the SDK free function has three pointer arguments, unlike the member +=.
Here its complete native control is byte-identical too. The other owners'
source spelling is a hypothesis generator, not evidence that this owner has
been repaired.


## OptTree and OptLeftWeightTree restore the input order

`line-x-boundary-swap-*` adds an input-head hardware watch and snapshots at
actual pass entry/return. It uses the same source-input identity and complete
ordinary owner as the unmodified control. Its six canonical-return swaps
produce 20 watched writes, a normal process exit and the same entire ordinary
body. The tracked FADD remains in the actual program: it is root 271 at
prelower return and root 269 at Lower entry. Its first floating input is
already the heap memory at displacement 0x54 again at both boundaries.
Lower then changes opcode 0x723 to the 0x476 floating-add pseudo instruction;
this trace does not implicate Lower as the first restoration point.

The first restoring writes are in `OptTree` at RVA 0xd70bd, followed by
`OptLeftWeightTree` at RVA 0xd6818. Static disassembly from the public function
entries confirms a second source-chain merge sort in each. `OptTree` loads
the left key at 0xd704b and compares it at 0xd704e; the left-weight variant
loads at 0xd679c and compares at 0xd679f. Both read operand +0x18 and use an
unsigned descending comparison. The unchanged heap key 0x10256dd therefore
puts it ahead of the shooter-X field key 0x10120 after a list-only swap.
These RVAs belong to the pinned v141 C2, not the older cross-game compilers.

`line-x-weight-control-*` observes those actual comparisons without changing
them. It records two OptTree comparisons and one left-weight comparison in
each of two optimization rounds: all six have the same key pair. Its normal
exit reproduces all 1,592 ordinary bytes. The corresponding diagnostic
weight intervention changes that heap key from 0x10256dd to 0x1011f, just below
the scalar's 0x10120, at all six comparisons. This time prelower return and
Lower entry retain the scalar-first chain. Lower emits a register input
followed by the heap memory operand, and NColor preserves it.

The normal-exit counterfactual changes exactly the native X MOVSS/ADDSS input
pair into the target's order. All other aligned operations, including the
late common loop block, remain unchanged; the complete owner stays 1,592
bytes. Its raw SHA-256 is
`29cd1e02444d8935f3ea1cf1a9efb48fefbf898ec06c6a3877541778ae85fdd5`.
Preserve `line-x-weight-swap-*`, whose control explicitly excludes source
acceptance. This isolates a causal ordering input and leaves common-loop
placement unresolved. A natural source repair must alter the effective
expression decomposition/key and pass the unmodified compiler comparison.


## Shooter fields are reader equivalents, not SROA replacements

The read-only `line-sroa-control-*` replay exits normally and reproduces the
entire ordinary 1,592-byte owner with the same `9c3967...` raw hash and
`463620c2...` build-input identity. It observes actual entry and return for
prelower, GlobalOptimize, GoptScalarReplacementOfAggregates and Lower.
GlobalOptimize and SROA execute inside prelower in this run; public-symbol
address order alone does not establish the execution order.

SymNewEquiv creates shooter X, Z and Y while RdrReadProc imports the function.
The float equivalents have offsets 8, 16 and 12 and ordinals 9, 10 and 14.
The X creation comes through RdrExtract; its kind-2 field form already exists
at prelower entry. All three remain kind 2 with a zero replacement slot
(symbol +0x2c) across SROA, prelower return and Lower. There are no calls to
DoScalarReplacement in this owner's observed optimization interval. The
ordinary field import therefore explains their origin; a later SROA promotion
is not the cause of this candidate's X ordering. This does not establish which
field/address form the original source used.

Preserve the early `line-sroa-reader-snapshot-failure.*` and
`line-sroa-marker-snapshot-failure.*` traces separately. Their graph snapshots
were invalid: the reader result precedes usable flow state, and tuple marker
storage must not be traversed as an arithmetic destination. The completed
control restricts expression traversal to ordinary instruction nodes.


## The first threaded traversal explains the late common block

`line-threaded-dfo-control-*` pairs GrInitDFOWalk's actual entry/return
inside the first FgThreadDFOAndFreeDeadCode with the following
FgChangeNextToDFOEx. It exits normally and reproduces all ordinary bytes.
The input has 81 blocks; DFS visits 80 and dead-code removal leaves 80.
An independent walk over the captured successor lists reproduces the
compiler's complete DFS completion chain, and reversing that chain exactly
reproduces the reordered block list. GrInitDFOWalk records completion order;
FgChangeNextToDFOEx prepends those nodes to form reverse postorder.

The common increment is input block 78, label 100085, with many incoming
case paths. It ends up at index 72. The first DFS route to it follows the
high-opcode dispatcher to WAIT (input blocks 0, 1, 2, 3, 5, 8, 18, 24, 25,
26, 75, 77, 78), before the low-opcode table is visited. The switch-default
edge is therefore not the sole reason this block appears late. Reversing
one successor list at a time in the captured graph does not move it ten
positions earlier. This graph replay is a diagnostic of the actual pass,
not a source repair or a statement about the original compiler's graph.

The earlier `default-at-speedup-exit-graph.jsonl` starts with a generic
102-block DFS before the threaded traversal. Its first DFS and first
reorder are different graph instances and must not be paired. The default
label source control itself is valid and byte-neutral. Track condition
contents as well as labels through the loop recognition and final
CodeMotion splice described below.


## Loop recognition copies the condition; CodeMotion later moves that copy

The completed `line-loop-rotation-*` replay preserves all ordinary bytes.
Its first FgDFOReorderLoopRecogEx already copies the original index-bound
condition to a latch labeled 213768. The old 100081 label remains at the
body entry and now compares the instruction type against zero. The operand
trees, including constants 18 versus 0, distinguish these roles; a persistent
label alone does not prove persistent semantics. The six observed FgMoveBlock
calls come from LgRemoveBreakBlocks1 and do not hoist the common increment.
FgMoveBlock's second register argument names the new next block, not an
insertion predecessor. The common increment stays late through Lower,
early tail duplication and NColor.

PostCodegenFlow frees the basic-block graph. The old block observer then
records one flattened tuple chain capped at 250 tuples, which is not evidence
that the function has become one basic block. `line-loop-final-flow-*` instead
walks the complete linear tuple list, with actual pass returns and no cap hit.
This normal-exit replay also reproduces all 1,592 ordinary bytes. At final
FgCodeMotion entry, the common label is tuple 327 and the copied condition
label is tuple 349. At return, the common label remains at 327 while the
condition moves to 331, directly behind the increment. This pass joins the
late increment to its condition; it does not move the increment to SPEEDUP.

`get-point-pointer-context-strict.json` checks the same translation unit's
LaserLineInf::get_point at 0x431050: the full 84-byte owner passes locally.
It calls the same polar helper and reads output X before position X, while
reading position Y before output Y. Its pointer-output expression provides
a useful existing source context for comparing operand forms with SHOOT;
this observation does not by itself identify the required SHOOT rewrite.


## WAIT's fall-through rejects hoisting the common increment

`line-can-move-control-*` observes actual FgCanMoveCode entry/return and its
FgSafeLocation result inside this owner's final FgCodeMotion. The replay
exits normally and reproduces the complete ordinary 1,592 bytes. There are
nine attempts targeting common label 100085, starting with the jump following
SPEEDUP. Every attempt returns null because the previous instruction at the
move destination is not a safe location. The observed previous instruction
is the WAIT timer's integer store at this+0x1ec, still falling through into
the common increment. The final native schedule puts the FP timer store
after that integer store, so identify the pre-scheduling predecessor from
the actual compiler snapshot.

The pinned static helper tests the predecessor with FgSafeLocation before
scanning the destination range. That helper rejects ordinary fall-through
instructions. A source repair must preserve WAIT's store and continuation
while changing the resulting
completion-path graph; forcing the safety result would not preserve that
fall-through. The ordinary for-loop-step control changes saved-index use
and completion-path increments without repairing either residual.
