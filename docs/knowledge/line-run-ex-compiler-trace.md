# Line EX cursor, index lifetime and loop layout

The active owner is `LaserLineInf::run_ex` at `0x431fe0`, in `src/Laser.cpp`.
The independently reviewed target owns 1,588 bytes: 1,550 code bytes, two
alignment bytes, five absolute jump entries and a 16-byte selector map. Its
code contains 327 instructions. Older linear measurements decode the tables
as instructions and must not be treated as code-only counts.

The current checkpoint candidate owns 1,592 bytes and remains incomplete in
the local strict audit. Its instruction pointer, index/type register roles
and two blend-arm memory increments now agree with the target. The remaining
code differences are the late common loop/return block and SHOOT's Y input
order. `blend-field-view-focused.json` retains the focused audit.

At checkpoint `2933b80`, the candidate's PDB contribution is 1,596 bytes.
The local strict audit refuses that unequal extent. Private source controls,
complete body snapshots, code-only listings and debugger scripts are under
`.analysis/line-run-ex-compiler/`. The target scope remains the one established
in [the remapped-owner review](remapped-owner-scopes.md).

## Baseline has three separate differences

The volatile instruction pointer repeats the pattern diagnosed in
[the curve EX investigation](curve-run-ex-compiler-trace.md): its stack store
and reload precede the actual current-pointer spill. The target computes
`this + 0x60c` and adds the scaled index, retaining the resulting pointer.

The current TAG source increments the member directly. The target instead
uses the saved entry index: `lea eax, [edx + 1]` followed by the member store.
That keeps the entry index in EDX; the candidate initially loads it into EAX.
Changing TAG to `ex_index = index + 1` restores the target's EDX index, but
leaves the complete extent at 1,596 bytes. This also matches the intent of
historical commit `01bc889`; the inspected starting source no longer had it.

The target's common increment, loop test and return block follow SPEEDUP.
The candidate places them near the function tail and jumps there from
SPEEDUP. The distant exit forces longer entry guards and selector-range
branches. These are complete-owner layout differences, not alignment bytes
that can be ignored or filled manually.

SHOOT also reverses the Y addition's memory inputs: the target loads the
shooter Y from ESP+0x20 and adds the laser Y at `this+0x54`; the candidate
loads the laser Y first. The other compared shooter field accesses agree in
the initial code alignment. The old source TODO about raw shooter offsets
therefore does not precisely describe the current code.

## Paired cursor is useful, but does not close the line owner

After the TAG repair, the next control removes the volatile pointer local and
advances `ex` once for SHOOT's actual second instruction. It restores the
correct pointer LEA/add and removes the redundant store/reload. Unlike the
curve owner, its complete extent stays at 1,596 bytes. The index and type use
ECX and EDX rather than the target's EDX and ECX, and the two blend-arm
paths replace member increments with LEA/store updates from the saved index.
The Y addition and late common loop block also remain different.

`paired-command-cursor-strict.json` retains the incomplete full-owner result;
`paired-command-cursor-code-differences.txt` is diagnostic code alignment.
`Laser.cpp.paired-command-cursor` is the source restored for compiler tracing.
It includes the completed curve owner and must not be confused with that
owner's earlier trial snapshots.

An explicit increment and `continue` in SPEEDUP does not form the desired
common block. It leaves the loop test/return at the tail and adds a separate
increment in SPEEDUP, increasing the complete contribution to 1,604 bytes.
That control is not retained. Preserve `speedup-continue-*` and its source
snapshot rather than repeating equivalent case-local continuation forms.

The next read-only trace follows the actual current candidate through
prelowering, lowering, NColor, post-codegen flow and emission. It also captures
floating canonicalization for the remaining Y input order. Locate the stage
that keeps or chooses the late common block before changing loop syntax again.

## Probe boundaries and the default edge

The first flow trace stops observing at `EmitFunction` entry. That entry is
before global allocation: it calls `dop2_PostLowerPreRegAllocGlobalOpts` and
`dop2_GlobalRegAlloc` internally. Its lack of NColor events cannot identify a
different allocator. A corrected trace kept observers active until the actual
EmitFunction return and recorded the NColor entry, codegen update, post-codegen
flow and pre-encode stages. Its normal-exit control reproduces the entire
ordinary 1,596-byte body, SHA-256
`2ca7d5acb6655cc4c8209a223e567a4365366d4845b08c5bfb3937bdb1ea08cc`.

A second labeling pitfall is RVA `0x78774`: public symbols identify it as
`NColProcessCandidate` entry, not NColor return. The raw events named
`ncolor-exit` in this trace are 83 candidate-entry snapshots. Use the real
function return PC and expected stack pointer for an allocation-exit stop.
The later codegen/post-flow/pre-encode snapshots remain valid. They retain the
late loop block; native pre-encode still has its first index writes well past
the initial SPEEDUP body.

The target's selector-range fallback jumps to the increment immediately after
SPEEDUP. The current source has an implicit default at the common switch tail;
the failed SPEEDUP-only continuation did not change that fallback edge. The
next control therefore makes the real unknown-command advance path explicit
as a default label after SPEEDUP. This distinguishes the default destination
from a separate case-local continue.

The explicit-default control grows to 1,612 bytes. It keeps a separate early
increment for the default/SPEEDUP path and another late common increment;
the desired full block is not shared. An explicit single `advance_ex` label,
with ordinary completed cases jumping to its actual index increment, is
byte-neutral against the paired-cursor control at 1,596 bytes. The compiler
still lays that shared block at the tail. Preserve both source controls and
complete reports; neither is an exact reconstruction.

The shared-label source is now being observed at `dop2_InitialOptsAndSetup`
entry. Its code is equivalent to the simpler paired-cursor source, but the
explicit source label provides a useful marker for discovering when its
position stops following the lexical placement. No source-layout claim should
be inferred solely from that label's position in C++.

## The first DFO application moves the named block

The initial shared-label trace contains the real advance label immediately
after SPEEDUP, followed by the field increment. A hardware-link trace is a
useful locator for expression rewrites, but the increment tuple changes form
and list links are also used during temporary expression rebuilding. Follow
the semantic label in the current flow graph to measure block placement.

The flow-graph walk derives from `FgChangeNextToDFOEx`: graph+0 is the first
block, +4 the last, and +8 the DFO head. A block's +0 links the next block,
+0x10 the DFO successor, and +0x1c its starting tuple marker. Named label
records store their character pointer directly at +4; they do not use the
backend-variable/frontend-name indirection.

`shared-advance-dfo-block-order.jsonl` follows the `$advance_ex` label, ID
100088, across pass entry and actual return. `FgThreadDFOAndFreeDeadCode`
first reduces the graph from 82 to 80 blocks while leaving it at index 29.
The following `FgChangeNextToDFOEx` moves it to index 73 of 81. Subsequent
DFO applications preserve its late position, even as graph rebuilding changes
block addresses. The completed unmodified-compiler replay reproduces all
1,596 ordinary bytes; keep its normal-exit control and image/map/log.

The next control changes the loop's data flow: a for-loop index supplies both
the bounds check and current-entry lookup, and is refreshed from `ex_index`
at the iteration boundary. TAG consumes that same index. This compares an
actual shared index value with the previous member-bound while condition;
it does not attempt another source-only placement of the advance label.

A loop-carried for index increases the contribution to 1,608 bytes. It puts
the saved index in EBX and adds EBX-to-EDX copies at entry and the latch.
A per-iteration snapshot with an explicit return guard produces the exact
same raw 1,608-byte candidate, SHA-256
`dade840526bb654719423dfd20b3935747e57a5421ff1365a94596aa59d2e854`.
Both controls are restored. Their source, native and strict artifacts remain.

After accounting for code alignment, the paired-cursor candidate's two extra
machine instructions are the two blend-arm LEA/store index updates. The next
control returns BLEND to the common completion path with a normal switch
break. This removes a case-local continuation from the source graph and tests
the index's extra uses without another loop-syntax change.

## Blend's field view restores the member increments

Returning BLEND to the common completion path removes the cached-index updates
and restores EDX for the entry index and ECX for the type. Its complete extent
is 1,580 bytes, however: one branch-local increment and jump are shared away.
That is not the original's two independent updates.

Keeping BLEND's continuation while assigning through the existing four-bit
`AnmVmFlagsLoFields::blend_mode` view preserves both original memory INCs and
the correct register roles. The flags' actual mask operations also agree.
The complete contribution is 1,592 bytes; its code alignment now differs only
in common-block placement and SHOOT Y operand order. The ordinary raw body
SHA-256 is
`9c3967ecdd40c11ea6cea8afbe00847a383337fcc3b9465910a4c5b846763b64`.
Preserve `blend-field-view-*`, including the source snapshot and full body.
This is a useful partial source checkpoint; the local strict comparison still
rejects its unequal extent and gives it no exact owner credit.
