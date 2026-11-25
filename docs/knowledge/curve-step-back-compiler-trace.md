# Curve reverse step: tracing the v141 allocator

The selected owner is `LaserCurveNode::step_back` at `0x438370`.
The 2026-11-25 focused strict audit still reports 982 matching bytes out of
986, with differences at offsets 770, 779, 787 and 791. The target copies
X into XMM1 and Y into XMM0 for the two squares; the candidate copies Y into
XMM1 and X into XMM0. The surrounding instruction stream matches after
independent linkage replay. The shared Factory snapshot remains inventory-only.

A `D3DXVec2Dot` formulation produced the same complete candidate bytes as
the scalar expression. It was reverted. Further work should use the compiler
trace rather than repeat equivalent local expressions.

## Applicable compiler and diagnostic controls

TH075's Meiling investigation demonstrated a scratch-register cursor carried
between neighboring action branches. TH09 and TH10 traced live ranges,
preferences and call dependencies before changing source. These are useful
methods, but their VC7.1 addresses and record layouts do not apply to TH16's
19.10.25017 backend. See the TH075 `docs/GIANTS.md` section “Meiling action
998 inherits the scratch register cursor” and TH10's `docs/KNOWLEDGE_BASE.md`
section “Compiler evidence from TH09” in the sibling workspaces.

TH16's pinned x86 `c2.dll` SHA-256 is
`3ca2a4f245e00b4535e6b6845274ea064a68f68d89b0339a71f2f0f73e0d7458`.
Its CodeView GUID is `94E7E617-8ABD-44E5-9324-25295D7D4B80`, requested age 1.
Microsoft's symbol server returned a stripped public PDB with that GUID and
age 2. Its four named compiler-pass exports agree with the DLL's export RVAs.
The retained symbol dump supplies these RVAs:

| Entry | RVA |
| --- | --- |
| `NColor` | `0x770a0` |
| `RegAssign` | `0x2178a2` |
| `Schedule` | `0x219629` |
| legacy `ChoosePhysReg` | `0x3a4a26` |
| legacy `Color` | `0x3a5803` |

A read-only Wine/GDB replay of the existing LTCG response file hit `NColor`
for the selected decorated symbol. The legacy `Color` breakpoint did not
hit. Recover the actual module base at load time: Wine loaded it at
`0x77260000` in these runs, rather than its preferred `0x50d60000`.

Full `/DEBUG` linking under the debugger exited with status 1318 before
allocation. `/DEBUG:NONE` allowed the diagnostic link to finish. A multithreaded
trace then hit GDB's `finish_step_over` assertion. Adding `/CGTHREADS:1` to
the diagnostic response file allowed the trace to complete. Neither flag was
added to the repository build profile.

The single-thread debugger link and the ordinary diagnostic link have identical
complete `.text` bytes and identical base-relocation entries. Against the normal
`/DEBUG` build, the diagnostic image has 170 differing `.text` bytes, all inside
absolute relocation fields. More directly, the selected owner's **entire raw
986-byte body is identical in all three images**, at candidate `0x44fcc0`,
SHA-256 `0d7a0eccc1fad3b515e77f93878056e2e914dfea396cef36252656a88c3e6ff4`.
This validates observation of this candidate; it does not establish target
exactness or equivalence of unrelated owners.

## Captured phases and next question

The debugger identified the selected owner through the symbol at `tagFUNC+0`,
whose decorated-name pointer is at symbol offset `+4`. In this backend the
linked tuple chain used here starts at
`read32(read32(read32(FUNC + 8)) + 0x1c)`; tuple `+4`
is the next pointer and tuple `+8` is the opcode.

The complete circular chain contained 339 tuples at `NColor` entry,
269 at its return and 263 at `Schedule` entry. The first capture retains
96 bytes per tuple. The completed follow-up also retains operand descriptors
and their referenced records. These layouts are observations for the pinned DLL,
not assumptions imported from VC7.1.

The two square tuples have opcode `0x47e`; the following sum is `0x476`.
In the retained run their tuple addresses are `0x3d12d0c`, `0x3d1301c` and
`0x3d1314c`. The source-operand list starts at tuple `+0x30` and links through
operand `+4`; the result descriptor is at tuple `+0x34`. Operand `+0x28`
points to the assigned physical symbol, whose `+0x2c` field gives the register
number for these XMM operands.

At `NColor` return, the square tuples respectively use XMM1/XMM4 with result
XMM1 and XMM0/XMM5 with result XMM0. The sum uses XMM1/XMM0 and returns XMM1.
All three assignments persist at `Schedule` entry. Thus the final discrepancy
is already present at allocator return; scheduling does not introduce the
square-register reversal. This does not yet explain why those assignments won.

The subsequent trace examined `NColDeterminePhysregAvail` for these
live ranges. Its RVA is `0x79391`; disassembly shows a call to
`NColMdGetRegOrder` before the eligible-register search. Compare earlier
requests in the other motion branches and the incoming operand identities
before proposing another source change.

A follow-up records 96 `NColDeterminePhysregAvail` entry/return pairs for
this owner, including five non-null returns. The records do not yet explain
the square-result assignments: the two generated copy symbols `0x427` and
`0x428` do not appear in that call set. Keep the later rewrite and local
allocation paths in scope. Do not interpret an intermediate null return as
the final allocation outcome.

For scalar type `0x8e004`, `NColMdGetRegOrder` (RVA `0xeb2a7`) returns the
constant table at RVA `0x123b0`: physical IDs 189 through 196, followed by
zero. These correspond to XMM0 through XMM7 in the captured descriptors.
This particular search starts from a fixed table; no TH075-style rotating
cursor has been demonstrated for the disputed assignments.

Private evidence and replay helpers are in `.analysis/step-back-compiler/`:
`c2.pdb`, `c2-publics.txt`, `symbols.json`, `debug-link.py`,
`trace-phases.py`, `before-ncolor.json`, `after-ncolor.json`,
`before-schedule.json`, the three `*-operands.json` snapshots,
`phase-events.txt`, `allocation-choices.jsonl`, and `control-comparison.json`.
The ordinary and debugger diagnostic images, response files and logs remain
there. Focused strict baseline, dot-product and restored reports are
`.analysis/20261125-step-back-{baseline,dot,restored}.json`.

## Earlier cause: expression canonicalization

The next trace followed the same three tuple identities back through lowering.
The sum was already Y-square then X-square at `Lower` entry. Lowering changes
its opcode from `0x723` to `0x476` without reversing its inputs. The later
post-lowering optimization renames the operands but preserves their order.

At `dop2_InitialOptsAndSetup` entry the original multiply tuples are ordered
X then Y, and the sum reads their result symbols `0xab`, `0xb6`. By
`dop2_PreLowerGlobalOpts` entry those same identities appear as `0xb6`, `0xab`.
This brackets the reversal before the allocation work discussed above.
The selected NColor run hit 91 `NColProcessCandidate` calls and 91 rewrites,
with no legacy `RegAssign` calls.

A write observation caught `FactCanonSort` rebuilding the sum's tree-source
list at RVA `0xdd5c5` (the stop PC is `0xdd5c8`). Its two multiply-child keys,
stored at tuple `+0x18`, are `0x01030817` for Y and `0x010307b7` for X. The
sort places the larger Y key first. `OptRebuildTuples` then reconstructs the
linear sum with Y's result first. The initial square operand fields belong
to the same aggregate, at offsets zero and four, with symbol ordinals
`0x14` and `0x15`. The sorting routine reads symbol ordinals at `+0x20` when
constructing leaf keys. This is evidence for checking component identity and
inlining context, rather than trying to repair a final register instruction.

The hardware-watch run captured the complete start-to-PreLower transition,
but GDB subsequently crashed after the watches were removed. Its observation
is retained as `commute-watch.jsonl`; it is not a completed build control.
The software breakpoint at the observed store's successor then completed
normally. Its five hits all record the same Y-before-X keys and tree order;
the final PreLower entry records the rebuilt `0xb6`, `0xab` sum. The complete
`.text` and base relocations still equal the ordinary diagnostic link, and
the entire selected body still equals the normal build's raw 986 bytes.
See `commute-software.jsonl` and `commute-software-control.json`.

A source control captured Y then X in scalar locals after the position store
and reused them for magnitude and angle. The complete owner stayed 986 bytes
but fell to 545 strictly matching bytes: code in the sentinel-motion branch
also moved, and the square-register discrepancy remained. The source was
restored and incrementally rebuilt. Keep `Laser.cpp.components-yx`,
`components-yx-strict.json`, and its build log; do not repeat this alias form.

The lowering and pre-lowering snapshots are `*-lowering.json` and
`*-prelower.json`, with corresponding event logs and successful diagnostic
image controls. The relevant probes are `trace-local.py`, `trace-lowering.py`,
`trace-prelower.py`, and `trace-commute-software.py`. The current next question
is where X/Y's aggregate-field symbols first acquire their ordinals, including
the preceding position-vector inline context. Establish that before changing
source again, then check the complete owner's other branches and stack layout.
