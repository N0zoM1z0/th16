# Curve reverse step: tracing the v141 allocator

The final 2026-11-25 native audit passes the complete 986-byte PDB contribution
of `LaserCurveNode::step_back` at `0x438370`: 248 instructions, all 14 linked
fields independently bound, and no byte differences after linkage replay.
The report is `.analysis/step-back-compiler/curve-step-back-final-strict.json`.
Its `factory_acceptance` remains `not-submitted`; the shared accepted snapshot
is still inventory-only. This closes the local source comparison, not Factory
acceptance.

The source uses separate planar accumulators, an explicit Z sum, a real
movement-speed accumulator and the SDK scale helper in the straight branch.
The final section explains the zero-offset memory hash wrap that resolves the
last multiplication. Earlier sections retain the failed controls and compiler
observations that led to this source.

## Original frontier

The initial focused audit reported 982 / 986 matching bytes, with differences
at offsets 770, 779, 787 and 791. The target copies X into XMM1 and Y into XMM0
for the two squares; the old candidate copied Y into XMM1 and X into XMM0.
The surrounding stream matched after independent linkage replay.
`D3DXVec2Dot` produced the same old body and was reverted.

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

## Initial allocation observations

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
the final allocation outcome. The later
[curve-tick investigation](curve-tick-compiler-trace.md) found that these
entry-created `FinishBreakpoint` probes can miss the actual return value in
the stripped backend; confirm returns at explicit caller sites before using
these records to explain an allocation.

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
`trace-prelower.py`, and `trace-commute-software.py`. The following controls resolve the field-creation question and expose a later
canonicalization pass. That later pass must be included in further experiments.

## Reader order is overridden by a second canonicalization

`SymNewEquiv` at RVA `0x2584ce`, called through `SymMakeEquiv` and
`RdrExtract`, creates the explicit aggregate component symbols while
`RdrReadProc` imports this function. The baseline creates X at offset zero
with ordinal `0x14`, then Y at offset four with ordinal `0x15`. Reversing
only the squared terms reverses this creation order: Y becomes `0x14` and
X becomes `0x15`. The first `FactCanonSort` consequently places X's square
first, as predicted by its higher key. Both builds still produce the same
complete candidate body with the original four mismatching bytes.

The reverse-expression pipeline brackets the second reversal inside
`dop2_PreLowerGlobalOpts`. At entry the sum reads X's result `0xb6` then
Y's `0xab`; at return it reads Y's `0x5e` then X's `0x1a0`. Lowering,
NColor and scheduling preserve that latter order. A single write watch on
the sum's source-list pointer completed normally and caught the second
`FactCanonSort`, again at RVA `0xdd5c5`. Its leaves are now scalar symbols
`0x12d` for Y and `0x121` for X. Their square keys are `0x01037117` and
`0x01036c97`, respectively, so Y is sorted first again. The trace also
records the intervening hash-table and SDSU rebuilds. Changing Reader field
ordinals alone therefore does not control the final squared-length operands.

These observations are in `field-creation*.jsonl`,
`reverse-expression-fields.jsonl`, `reverse-expression-canonical.jsonl`,
`reverse-expression-pipeline.jsonl`, and `prelower-commute-watch.jsonl`.
The corresponding successful image controls remain alongside them. Internal
addresses changed after a source edit, so the later probes find the selected
sum by its two square definitions instead of assuming an old tuple address.

## Definition order controls both arithmetic and scheduling

Defining the motion sum's Y component before X changes the promoted values
and recovers the target's four square-register bytes. Direct component
assignments in the caller also change the other motion branches. Keeping the
same caller shape through a normal three-pointer inline sum helper restores
those branches, but computes Y before X and saves Y before X, whereas the
target computes and saves X first. The helper owner is still a mismatch.

| Complete owner control | Strict matching bytes / 986 | Finding |
| --- | ---: | --- |
| Reverse the squared terms | 982 | Reader and early tree order reverse, then PreLower sorts Y first again |
| Assign sum components Y/X/Z in the caller | 545 | Square-register bytes recover; other branch scheduling changes |
| Y/X/Z assignments in an inline sum helper | 974 | Squares recover; component sums and saves are reversed |
| Helper computes Y/X/Z locals, writes X/Y/Z | 982 | Returns to the original four differences |
| Helper computes a Y/X/Z aggregate then copies it | 974 | Same complete outcome as direct helper assignments |
| Force-inline the Y/X/Z helper like the SDK | 974 | Same complete outcome; the inline attribute does not repair scheduling |
| Helper assigns a three-argument vector constructor | 980 | Original four differences plus two Y-add operand differences |

All these source experiments were restored. Only the focused TODO comment
was corrected: field-wise sums can change the disputed operands, but have not
yet preserved the complete owner's scheduling. The scheduler comparison below resolves the remaining helper differences.

The source controls are retained as `Laser.cpp.*` under the compiler evidence
directory, with matching `*-build.log` and `*-strict.json` reports. The helper
native listing is also in `.analysis/curve-exact-work/20261125-yx-helper/`.
A small ordinary `/O2` COFF control retains two precise `pow` calls for the
`powf(x, 2)` form; it was not imported into the game source.

## Scheduler ties and an isolated ordinal control

Read-only replays captured all ten scheduling regions for the baseline and
the Y/X/Z helper. Both completed normally. The helper trace was checked against
the completed ordinary build: the entire 986-byte raw body is identical,
SHA-256 `f9f10b401b54fedadcbddb383537afd7714bd83a5fa617ead2de1f940615b532`.

Region 8 contains both planar chains. Their static priorities and weighted
paths are equal in both sources; only their input ordering differs:

| Axis operation | Static priority | Path | Outgoing edges | Baseline ordinal | Helper ordinal |
| --- | ---: | ---: | ---: | ---: | ---: |
| X load | `0x1c400` | 78 | 3 | 19 | 22 |
| X add | `0x1c400` | 76 | 5 | 20 | 23 |
| X save | `0xb000` | 43 | 1 | 21 | 24 |
| Y load | `0x1c400` | 78 | 3 | 22 | 19 |
| Y add | `0x1c400` | 76 | 5 | 23 | 20 |
| Y save | `0xb000` | 43 | 1 | 24 | 21 |

For this pinned backend, a DAG node's tuple is at `+0x1c`, static priority
at `+0x24`, dynamic priority at `+0x28`, and original ordinal at `+0x34`.
The forward node link is `+0`, not `+4`. `SchSelectInstrs` compares dynamic
priorities at RVA `0x219f47`; equal priorities reach the unsigned ordinal
comparison at `0x219f55`. Earlier ordinals win. The observed Y-before-X
order matches this tie-break; the ordinal-only control below isolates its
effect.

A separate compiler-state control swapped only the three X/Y ordinal pairs
at `SchSchedGraph` entry in the private helper compilation. It made no source
change. The resulting owner differs from the ordinary helper at exactly the
12 previously mismatching byte offsets: 688, 690, 694, 696, 700, 702, 706,
708, 756, 758, 762 and 764. All 14 linked fields remain byte-identical to the
ordinary helper. Replaying their independently bound target encodings gives
agreement across all 986 target bytes. This is a diagnostic mutation, not
source exactness or a Factory acceptance result.

Keep `counterfactual.exe`, `counterfactual.map`,
`counterfactual-ordinary-owner.bin`, `counterfactual-ordinary-strict.json`,
`counterfactual-scheduler.jsonl`, `counterfactual-comparison.json`,
`trace-scheduler-counterfactual.py`, and `compare-counterfactual.py` separate
from ordinary build evidence. The read-only graphs are
`baseline-scheduler.jsonl` and `helper-scheduler.jsonl`; the ordinary helper
identity check is `helper-scheduler-control.json`. The counterfactual body
hash is `b889894b5aedbc29f7d215186eea9cc60f20e1aac068c1b559473dff105fa643`.

The source search must now preserve the helper's promoted scalar identities
while either restoring X's earlier scheduler ordinals or adding a real
priority advantage for X. The following complete-source controls did not do so:

- Swapping the position addition to `sum + *pos` reproduces the same 974-byte
  helper match.
- A position helper that copies the input and then applies `+= motion`
  grows the owned extent to 1007 bytes.
- A three-element sum loop using the SDK's float-pointer views introduces
  `/GS` cookie code, a larger frame and a 1056-byte extent.
- Read-only references to the helper's two X inputs also introduce cookie
  code and a 1050-byte extent.

All functional source trials were restored. Ordinary `/O2` COFF controls also
show that `fabsf` and a float/double/float round trip leave actual instructions
in v141; they do not supply a zero-byte scheduling operation here.

## Promoted scalar ordinals come from recycled temporaries

The promoted X/Y ordinals are inherited from a free list. `SymAlloc`'s
temporary-symbol path at RVA `0xd9cc6` takes the head at context `+0x2c`.
It saves the symbol's ordinal (`+0x20`), clears its 100-byte record, and
restores that ordinal at `0xd9ce3`. `SymFree` pushes temporary symbols onto
the same list at `0xda16c`–`0xda175`. A newly promoted scalar can therefore
receive an older, smaller ordinal than the preceding allocation.

The completed baseline trace records `0x12d` and then `0x121` being freed
inside `GlobalOptimize`. `GdfInstrSdsu`, called by `GoptRebuildSdsu`, reuses
them in the opposite order. `GoptRehashLexicalHelper` subsequently frees
`0x12d` then `0x121` again. After nine other scalar promotions, the sum's X
field receives the recycled `0x121` record and its Y field receives `0x12d`.
The earlier tuple snapshot contains these same records as an address-add
temporary and a floating multiply temporary; their numerical identities
are not unique to the final motion components. This explains why Reader
field order alone fails to control the second canonicalization. It does
not yet identify a natural source change that preserves all target bytes.

Private evidence is `baseline-sroa.jsonl`, `baseline-reuse-sroa.jsonl`,
their `*.gdb.log` and `*-control.json` files, and `trace-sroa.py`.
Both completed replays preserve the baseline's whole `.text`, base
relocations and selected raw owner. The useful next source controls change
real aggregate construction or another live expression, then check the
complete owner and trace which recycled identities changed. Adding dead
locals to steer the pool is not a reconstruction.

Further complete-owner source controls rejected moving the angle-acceleration
case before the acceleration case (987 bytes), copy-then-accumulate motion
(1006 bytes), compound assignment for the angle branch's final position
(980 bytes), and a named remaining fraction at that final store (988 bytes).
Consuming `D3DXVec3Add`'s returned pointer, using a two-float length helper,
reversing the angle branch's final scalar/vector multiplication, scaling `d`
in place before its final subtraction, and returning directly from the three
cases each reproduce the baseline's same four differences. A by-value vector
length helper retains a parameter stack copy and `/GS` code (1064 bytes), even
though the helper is inlined. These controls were not retained as reconstruction.

An omission control removes only the angle-acceleration branch's last
position update. The unchanged acceleration branch then uses the target's
square-register order. Its complete owner is 888 bytes and cannot pass;
the omission isolates a non-local influence, not a usable implementation.
Keep `Laser.cpp.omit-angle-final-position`, its strict report and the
native listing under `.analysis/curve-exact-work/omit-angle-final-position/`.
Two completed read-only replays reproduce that entire 888-byte body. In the
omission control, SROA gives X ordinal `0x27a` and Y `0xf9`, instead of the
baseline's `0x121` and `0x12d`. At Lower entry the first square reads the SSA
leaf whose parent is X's `0x27a` record; the second reads Y's `0xf9`. Thus the
non-local omission changes the canonicalized operands before register
allocation. The field mapping is in
`omit-angle-final-position-focused-sroa.jsonl`; the phase snapshots are in
`omit-angle-final-position-pipeline.jsonl`. Preserve both completed body
controls and their GDB logs. Source reconstruction must retain the omitted
motion update while changing this temporary-object path.

## Single-use propagation defeats early component calculation

An inline Y/X/Z helper that first calculates `const f32 x = a->x + b->x`
and later assigns `sum->x = x` still produces the same 974 / 986 helper
result. The helper's own Lower-entry chain computes X before Y. After
inlining, the owner's PreLower-entry chain also computes X first, followed
by the local X copy, Y addition, Y store and X store. By Lower entry the
order is Y addition/store, then X addition/store.

A single hardware watch on the X tuple's next link captures the move.
`SduMoveExpr` changes its previous link from the preceding call to the
sum's Y store. `GoptSingleUseCopyProp` then removes the local X copy,
leaving the X addition immediately before the X store. This occurs inside
`GlobalOptimize`, reached from PreLower at `+0xa5`; the outer call site is
`GlobalOptimize+0xa38`. Later `OptRebuildTuples` passes retain that order.
Precomputing a component only to copy it into the aggregate therefore does
not preserve its earlier arithmetic definition in this owner.

Both read-only replays completed and reproduce the entire ordinary
986-byte helper body, SHA-256
`f9f10b401b54fedadcbddb383537afd7714bd83a5fa617ead2de1f940615b532`.
Keep `staged-x-{helper,owner}-before-*-prelower.json`,
`staged-x-phase-events.txt`, `staged-x-link-watch.jsonl`, both
`staged-x-*-control.json` reports and their GDB logs. The probes are
`trace-staged-x-order.py` and `trace-staged-x-link-watch.py`.

Using actual scalar coordinates in all three outputs exposes a different
control. Initializing Y from `a.y`, calculating X, then accumulating `b.y`
into Y recovers the target square-register order. Initializing Y from `b.y`
instead reverses the Y addition's input loads; keep the forward input order.
Plain single-assignment X/Y locals do not recover the squares. The complete
owner still fails because the straight and sentinel branches choose different
X multiplication forms, shifting the curved branch by one byte.

Keeping the scalar Y accumulator and using `D3DXVec3Scale` for the straight
branch recovers that branch too. The resulting owner is 987 bytes. A
diagnostic instruction alignment preserving every register and instruction
size leaves only the sentinel's X multiplication: it loads velocity X into
XMM0 then multiplies by XMM1, whereas the target copies the speed difference
from XMM1 into XMM0 and multiplies by velocity X in memory. The candidate's
sequence is one byte longer. This is not a complete-owner match.

The completed read-only `near-mul-order` replay reproduces all 987 raw owner
bytes, SHA-256
`24d9a1543d8ce1a6e2540742a038838aa213cd3d4e759965fb63a6284b1a4fea`.
At Lower entry, the baseline sentinel X multiply reads scalar symbol `0x443`
before its indirect operand. The near candidate reads the indirect operand
before scalar `0x423`. Its velocity base is `0x106`, versus baseline `0x101`.
The discrepancy therefore precedes lowering and allocation. Keep
`Laser.cpp.y-accumulator-straight-scale-api`, its 987-byte strict report and
native listing, `straight-scale-register-sensitive-diagnostic.json`,
`near-mul-owner-before-*-prelower.json`, and the completed replay control/log.
This 987-byte control isolated the last multiplication but was not retained
as the final source.

## Closing the zero-offset memory hash wrap

The multiply-key trace explains the remaining operand order. For the observed
non-temporary scalar-symbol bases with ordinals below `0x800`, `OptHashNode`
shifts the ordinal left five bits and returns its low 16 bits. The memory
case shifts that address hash left eight bits, adds the displacement and
opcode contribution, and again keeps 16 bits. `FactCanonSort` adds the
operand-class bit at `0x10000`. For this zero-displacement float load its key
is therefore `0x10000 | ((8 + (base_ordinal << 13)) & 0xffff)`. Only the base
ordinal's low three bits survive. This derives the observed period-eight
effect without treating declaration counts as an acceptance rule.

In the 987-byte control, base `0x107` gives memory key `0x1e008`, above the
movement-speed scalar's `0x10180`. The descending sort puts the memory
operand first. Naming the already-used Z sum moves this base to `0x108` and
wraps its key to `0x10008`; the scalar now sorts first and the target's
`movaps` plus memory-source `mulss` appears. The straight branch's SDK scale
base moves from `0x104` to `0x105`; both memory keys remain above its scalar
key `0x10020`, preserving its correct order.

The relevant instructions are in `FactCanonSort` at RVAs `0xdd6e7`–`0xdd720`
and `OptHashNode` at `0xd7de1`–`0xd7e0d` in the pinned compiler. Private
`mul-canonical-keys.jsonl` and `matched-mul-canonical-keys.jsonl` capture the
before/after keys. Both completed read-only replays reproduce their entire
ordinary owner; their controls and GDB logs remain alongside them.

After removing the stale TODO, the incremental build and focused strict
audit again pass all 986 bytes and 14 linked fields. The final raw candidate
body at `0x44fcc0` has SHA-256
`b889894b5aedbc29f7d215186eea9cc60f20e1aac068c1b559473dff105fa643`.
The final read-only compiler replay has that same body. This equals the
earlier scheduler counterfactual's bytes, now generated by the retained
natural source and the unmodified compiler. Preserve the counterfactual's
separate diagnostic label.
