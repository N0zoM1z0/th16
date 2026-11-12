# Reference repair evidence

This work uses the original Japanese TH16 v1.00a target pinned in
`config/target.toml`. The upstream checkout remains unchanged. All comparison
results come from the local Factory/TH10-style Oracle.
Sections below are successive historical batches; their counts and test totals
describe those checkpoints. Use [NEXT_AGENT.md](../NEXT_AGENT.md) and
`scripts/progress.py` for current state. Historical JSON reports are now stored
as `.json.gz`; see [ARTIFACTS.md](../ARTIFACTS.md).

## Formatting buffers

Two imported formatting functions used `char buf[0x104]`. Changing the buffers
to `char buf[0x100]`, the capacity of `AsciiStr::text`, restores the original
stack layout under the pinned compiler and build context:

| Target | Function | Complete extent | Relevant frame layout |
| --- | --- | ---: | --- |
| `0x00408260` | `AsciiInf::create_stringf` | 77 | Frame `0x110`, cookie `[ebp-8]`, buffer `[ebp-0x10c]` |
| `0x004083B0` | `AsciiInf::create_number_with_digit` | 316 | Frame `0x10c`, cookie `[ebp-8]`, buffer `[ebp-0x10c]` |

No assembly, emitted bytes, padding variables or per-function compiler-option
exceptions are used. The nearby `create_number` retains its existing buffer;
its complete 255-byte owner matches once the independently reviewed `%d`
storage binding is available. See [shared linkage evidence](reviewed-linkages.md)
for the string witness and the allocator entry identities.

The formatting-buffer results below were finalized with a clean build, complete
independent boundaries, unique PDB owners, exhaustive relocation fields and byte
replay through `scripts/audit-reference.py`. The current incremental workflow is
described in [REFERENCE_IMPORT.md](../REFERENCE_IMPORT.md).

## Unsuccessful source experiments

`EclRunContext::get_int_arg_ptr` at `0x00474330` still differs in its stack-base
address arithmetic. Reversing the expression, using `EclStack::local_ptr`, an
inlined frame helper and integer-address forms did not reproduce the complete
98-byte target. Helpers moved the base calculation into the correct register
but reversed the final additions. The imported expression is retained.

Moving Fog's vertical-step computation after the initial position calculation
also failed to reproduce its complete target owner. That experiment was
reverted. These failures do not justify instruction normalization or byte masks.

A texture-data local in `draw_vertex_strip` and an inline VM-node initialization
helper also left their complete byte differences unchanged. Replacing the four
dialogue text-position setters with D3DXVECTOR3 value assignments increased the
constructor contribution from 1223 to 1248 bytes and introduced a new unresolved
field. These experiments were reverted.

## Removing artificial alignment helpers

The imported source explicitly described eight `*_want_aligned_stack` helpers
as non-original dead-double code. Each helper only initialized an unused double
and discarded it; its purpose was to influence MSVC's LTCG stack-alignment pass.
All eight helpers and their calls have been removed:

| Target | Affected function |
| --- | --- |
| `0x0040B2F0` | `Stage::interrupt_vms` |
| `0x0040E5C0` | `AnmLoaded::create_vm` |
| `0x00418C70` | `Fog::Fog` |
| `0x00426160` | `AnmLoaded::create_vm_front` |
| `0x0042C920` | `AnmLoaded::create_ui_effect` |
| `0x0042EFB0` | `AnmLoaded::create_ui_vm` |
| `0x00431A70` | `LaserManager::cancel_in_radius` |
| `0x0045F160` | `AnmLoaded::set_vm_script` |

The circular-cancellation traversal now keeps its saved successor inside the
loop, as the other cancellation routines do. Removing the two dummy calls
reduces its diagnostic contribution from 119 to 109 bytes. Its target owner
remains 119 bytes; no boundary is shortened and the result remains unaccepted.
Recover stack requirements from actual callers and callees before claiming a
match. Other imported dead-local and dead-arithmetic tricks remain a separate
source-review task; this change only removes the eight named alignment helpers.

## Formatting-buffer validation

The baseline before this batch is local commit `23f09b2`: 550 exact, 30 mismatch
and 634 incomplete annotated candidates. Its ignored report is preserved under
`.analysis/baselines/23f09b2/`. The original import audit remains historical.

The clean build and strict audit for this batch report **581 exact, 30 mismatch
and 603 incomplete**, covering 1214 annotated candidates and 98,442 exact owned
bytes. All 550 previously exact candidates remain exact. Thirty incomplete
candidates become exact, and `create_stringf` moves from mismatch to exact.
`BombReimuAInf::on_tick` at `0x00410DE0` becomes decidable and remains a mismatch
(937 of 1145 bytes agree); it is not promoted. Both formatting-buffer fixes pass
independent standalone replay. The unchanged ECL pointer function still fails
at byte offset `0x45` in its 98-byte owner.

The clean-build source input identity is
`2904192bfecdcba7a67313632c2010139779f5b279a633bd24f2d37dca6beccc`.
The candidate executable SHA-256 is
`d52197acbfea15fac4cf5311c86f5788d25a41b6cd366f227c879b019fae55e2`.
The ignored build log is `.analysis/reference-repair-clean-build.log`; the full
report is `.analysis/reference-audit.json`. The build receipt binds the PE, MAP,
PDB and function inventory. These hashes identify evidence, not expected output
hashes for a future link with fresh timestamp and PDB identity.

Validation passed 12 complete-owner replay controls, 7 PDB type/storage controls
and 13 reviewed-linkage controls. The last group includes complete allocator
thunk replays and rejects wrong targets, wrong libraries, instruction interiors,
missing reviewed parents, truncated strings and ambiguous PDB storage. Current
progress also validates the cold-build and report identities and every retained
comparison-unit hash.

Remaining incomplete groups include 196 candidate/target extent
differences, 169 candidates with one missing linkage binding and 40 candidates
without a unique same-start PDB contribution. Preserve these ownership limits;
do not truncate a candidate or infer an address from the operand being compared.

Use `scripts/progress.py` for the current result; it checks source, artifact,
Oracle and comparison-unit freshness. Local byte results do not establish
source authorship or Factory Truth Kernel acceptance. Origin review remains
open and no Factory acceptance receipt has been submitted. Keep all Git
checkpoints local; pushing or remotely publishing this repository is prohibited.

## Alignment-helper cleanup validation

The subsequent clean build reports **603 exact, 40 mismatch and 571 incomplete**,
with 110,360 exact owned bytes. Twenty-nine incomplete candidates become exact
after six scalar bindings and the complete unsigned-conversion table proof.
Seven previously exact results are withdrawn after removing artificial helpers:
Stage::interrupt_vms, create_vm, create_vm_front, create_ui_effect and create_ui_vm
now mismatch; Fog::Fog and set_vm_script lack matching complete extents. These
are the seven directly changed functions that were previously exact. All other
574 prior exact results remain exact. Six other incomplete candidates become
decidable mismatches. The circular laser cancellation remains incomplete.

The clean source input is
`70c5735b1b26cb8f60a2556df77fb7c6fd5f9d12a9b6b415e8cc2eec3a636bee`;
the linked executable is
`49359ca8c11071475a38395950c5e5c12f4b67b865ecb85fb6e9283f14b328e0`.
Evidence is in `.analysis/natural-source-clean-build.log` and the current audit.
The prior report is preserved under `.analysis/baselines/93c58d3/`. Twenty-one
reviewed-linkage controls and twelve complete-owner controls passed, including
the indexed-table mutations described in `reviewed-linkages.md`.

The user subsequently requested faster source progress: use incremental builds
and focused complete-owner comparisons during reconstruction. Repeat a broad
clean build at a meaningful milestone or when a dependency/cache issue requires
it, rather than after every source batch.

The local Oracle now accepts either a current incremental receipt or a clean
receipt. It still checks the source input identity, artifact hashes, PE/PDB/MAP
identities, complete boundaries and exhaustive fields. Focused JSON results
record `build_kind`; `--require-cold` retains the stricter build-kind option.
Four build-context controls verify current artifacts, explicit cold rejection,
stale-source rejection and changed-artifact rejection without editing receipts.
Incremental replay of the 56-byte RNG function and the 77-byte ASCII formatter
passes, and the full incremental audit retains 603 exact, 40 mismatch and 571
incomplete results.

Two further source trials were reverted: integerizing the slot address in
`EnemyManager::destroy_all` leaves the same SIB encoding difference, and using
aggregate Int2 assignment in `Player::set_position_subpixel` leaves its early
coordinate-conversion load unchanged.

## Float2 timer and vector scheduling

Both `InterpFloat2::step` (`0x00463D40`) and `step_radial_dist` (`0x00425570`)
now use the regular timer helper, which merges the floating-frame store after
the speed branches. Their four unused integer placeholders have been removed.
The resulting diagnostic replay has a complete 757-byte contribution and first
differs at offset `0x104`: the 260-byte timer/early-return prefix agrees, while
vector load/store scheduling remains different. Both functions remain mismatch.

Four explicit weighted-vector terms produced 749-byte contributions; four
named scalar subexpressions produced 761; a switch dispatcher produced 769.
Directly expanding the timer preserved the same vector differences. Swapping
the acceleration sum did not help, and a named horizontal-wrap predicate in
`Bullet::step_ex_12` left its four differing bytes unchanged. These experiments
were reverted. Keep the remaining vector problem separate from the corrected
timer store; no prefix-only result receives exact credit.

The unannotated original at `0x0042F150` is the implicit
`ItemManagerInner::~ItemManagerInner` (70 bytes): it destroys `0x1258` items of
size `0xc78` through the EH vector destructor iterator. The candidate already
has a complete 70-byte PDB contribution from Item.obj. Its EH-handler address
and iterator linkage still need independent bindings, so no annotation or exact
claim has been added merely from the similar compiler-generated wrapper.

## Sign mask and derived cursor validation

The complete sign-mask witness makes `collision_line_intersection` (982 bytes)
and `zun_fabsf` (25 bytes) decidable and exact. The separately checked square-root
runtime extents make `draw_sprite_fog` decidable, exposing its mistaken
nearest-global binding for the loop limit. The bounded cursor proof described
in `reviewed-linkages.md` fixes that provenance and replays all 522 bytes exactly.

The final incremental audit has **606 exact, 41 mismatch and 567 incomplete**
among 1214 annotated candidates. All 603 exact results from `e91bf45` remain
exact. Two other previously incomplete candidates become decidable mismatches.
The two Float2 functions remain mismatch after removing their unused locals;
their partial timer agreement receives no exact credit. Twenty-three reviewed
linkage controls, thirteen cursor-limit controls and twelve complete-owner
controls passed. The relevant private evidence is
`.analysis/pointer-limit-final-audit.log`, `.analysis/draw-sprite-fog-exact.json`
and `.analysis/fabsf-exact.json`. No further cold build was used after the user
requested incremental iteration.

## Directory, copy and math linkage review

The eleven-byte directory-changing UCRT root is independently identified through
its `common_chdir<char>` child and the configuration loader's directory-selection
paths. This makes `Supervisor::load_game_config` (799 bytes) and
`Scorefile::Scorefile` (145 bytes) exact under complete replay.

The SSE2 sine and cosine identities are independently corroborated by their
original x87 fallback instructions, `fsin` and `fcos`. The runtime copy algorithm
and the Ghidra-identified EH vector iterators supply three further reviewed
identities. Their entire target and candidate extents remain mandatory; separate
candidate sizes record the differing iterator and sine contributions. These
records identify external callees, with no separate runtime exact-code credit.
See `reviewed-linkages.md` for addresses, contracts and evidence. The Oracle's
comparison and ownership rules were not changed for this batch.

Four additional scalar witnesses fix the storage of 100.0f (coordinate
quantization), 224.0f (bounce midpoint), 480.0f (loading indicator x) and 10.0f
(small font line height). Every consumer still needs complete owner, relocation
and byte replay. Equal payloads at other addresses are not substituted.

Several bounded natural-source trials were rejected and reverted:

- A Float2 length-square expression for circle/rectangle collision retained the
  400-byte extent but worsened agreement; in-place rotation produced 403 bytes.
- Caching shake duration and extracting the rising-shot damage configuration
  left the respective 476/472 and 349/333 comparisons unchanged.
- Moving the vertical fog spacing calculation after position initialization,
  including a named origin and interval count, produced 329 bytes rather than
  the original 326.
- Using the cached VM for deletion produced 108 bytes rather than 112. Loading
  the next node before the VM retained 112 bytes and the same 105 matching bytes.
- Reversing the two angle-operand local declarations retained the same
  142-byte contribution and 130 matching bytes.

All production source from these experiments was restored before the final
incremental rebuild. Logs include `.analysis/fog-cached-vm-build.log`,
`.analysis/scalar-load-order-build.log` and
`.analysis/restore-scalar-trials-build.log`. No padding locals, inline assembly,
forced volatile accesses or partial-range exact claims were introduced.

The final current-source incremental audit reports **622 exact, 43 mismatch and
549 incomplete** among 1214 annotated candidates, totaling 119,976 exact owned
bytes. All 606 exact results from checkpoint `0170209` remain exact; sixteen
previously incomplete candidates become exact. New complete passes include
Stage::load_std (414 bytes), Bullet::bounce_top/bottom (207/202),
BulletManager::cancel_rectangle_as_bomb (283), Scorefile::load_sections (374),
scorefile_save (624), TitleInf::update_options_sprites (3255),
AnmManager::save_vm_tree (361) and AnmVm::copy_from (603). The two newly
decidable mismatches retain their full mismatching bytes.

Twenty-three reviewed-linkage controls and twelve complete-owner controls pass.
The final report is `.analysis/reference-audit.json`; the audit log is
`.analysis/runtime-literal-final-audit.log`, and the explicit baseline comparison
is `.analysis/runtime-literal-regression-check.json`. `scripts/progress.py`
validates report, artifact and retained-unit freshness. All builds in this batch
were incremental. Source-origin review is still open, and no Factory acceptance
or remote publication was performed.

## Vector source and world-position cleanup

`AnmManager::draw_line` at `0x00469330` now writes the second endpoint's y
coordinate through D3DXVECTOR4 indexing. The original computes and stores that
coordinate before the diffuse and homogeneous-coordinate stores; member access
had allowed the candidate to sink it below those stores. This one source
change restores the complete 569-byte owner under the same compiler/link
profiles. Every instruction and relocation is compared; there is no field mask,
new linkage binding, assembly patch or comparison-rule change.

Both Float2 interpolation functions now add velocity in the original operand
order and use scalar-left weighted vectors in the cubic expression. Each retains
a complete 757-byte contribution. The first difference moves from offset 260
to 453, and 603 bytes match rather than 591. The early exits, timer and constant
motion branches agree; the cubic branch still schedules vector loads and
registers differently. Both remain mismatch, with no prefix-only exact credit.

The four-point collision rotation now writes y before x, as in the original.
The complete points-in-rectangle owner still has 10 differing bytes out of 661,
caused by rotation register assignments. Saving both rotated scalar results
before writing them produces the same result. Copying the original Float2 into
a local instead produces a 677-byte contribution and was reverted. Other
consumers of this shared helper remain subject to complete comparison.

`AnmVm::world_pos` no longer uses the explicitly artificial dead integer,
volatile-cast reload or safebuffers/forceinline parent-position workaround.
It adds the parent's recursive result directly. This removes source tricks but
does not solve its code generation: the candidate now contains a GS cookie and
has a 315-byte extent, while the independent original remains 297 bytes with no
cookie. Its result is incomplete; neither extent is changed to conceal this.
Recover the actual compiler/temporary context before claiming an exact result.
Other explicitly artificial locals elsewhere in the imported source still need
review.

Two other bounded trials were reverted. A device getter or local in
`draw_vertex_fan` retains the same four register-encoding differences in its
313-byte owner. Naming the slow-path snapshot discriminator before storing it
produces 234 bytes rather than the original 235. These experiments do not justify
register normalization or padding variables.

Private evidence includes `.analysis/render-owner-diff.txt`,
`.analysis/interp2-left-weight-owner.txt`,
`.analysis/world-pos-owner-natural.txt`, and the incremental build logs
`.analysis/render-device-vector-build.log`,
`.analysis/snapshot-device-local-build.log`,
`.analysis/rotation-y-first-build.log` and
`.analysis/vector-source-final-build.log`.

The final incremental audit reports **623 exact, 41 mismatch and 550 incomplete**
among 1214 candidates, with 120,545 exact owned bytes. All 622 exact results
from `c5eff1f` remain exact. The sole new exact result is the complete line
renderer. The world-position cleanup changes its state from mismatch to
incomplete because its complete extents now differ; this is not an exact-code
improvement for that function. Collision and interpolation improvements remain
full-owner mismatches.

Evidence is `.analysis/vector-source-final-audit.log`,
`.analysis/vector-source-regression-check.json` and the refreshed complete-owner
record `.analysis/draw-line-exact.json`. `scripts/progress.py` validates current
source, artifact, report and retained-unit identities. No cold build, new
Oracle rule or additional acceptance authority was used in this source batch.
Source-origin review and Factory acceptance remain open.

## Removing explicit compiler-perturbation locals

A controlled probe of `world_pos` temporary ownership tested direct expression,
const-reference, named-vector and component-wise forms under the pinned compiler.
All four non-LTCG COFF procedures contain a GS cookie. The existing non-LTCG
symbol-discovery object also contains it. This rules out simply assuming that a
const reference or scalar component additions remove the cookie. It does not
settle the original LTCG context or authorize disabling GS for one function.
The ignored probe and disassembly are `.analysis/world-position-gs-probe.cpp`
and `.analysis/world-position-gs-probe-disasm.txt`.

The remaining source contained variables explicitly documented as non-original
and used only to perturb MSVC's named-variable allocation or double-stack
alignment passes. This batch removes 80 declaration statements containing
86 variables (22 doubles and 64 integers), their discarded-value casts, and
self-multiplications of a dead zero. The declarations occur in 39 blocks across
18 C++ files. Compiler-context comments in AnmManager.h were updated to stop
asserting alignment properties caused by these removed variables.

| Source | Doubles removed | Integers removed |
| --- | ---: | ---: |
| `src/AnmManager.cpp` | 1 | 0 |
| `src/AnmManagerVms.cpp` | 1 | 0 |
| `src/AnmVmCallbacks.cpp` | 2 | 3 |
| `src/BulletManager.cpp` | 1 | 8 |
| `src/Collision.cpp` | 0 | 6 |
| `src/Enemy.cpp` | 1 | 0 |
| `src/Globals.cpp` | 2 | 0 |
| `src/Gui.cpp` | 5 | 0 |
| `src/HelpManual.cpp` | 1 | 0 |
| `src/Interp.cpp` | 0 | 4 |
| `src/Laser.cpp` | 3 | 24 |
| `src/LaserInfinite.cpp` | 1 | 2 |
| `src/MainMenu.cpp` | 1 | 0 |
| `src/MainMenuStates.cpp` | 0 | 4 |
| `src/PlayerShot.cpp` | 1 | 0 |
| `src/PosVel.cpp` | 0 | 5 |
| `src/Stage.cpp` | 1 | 8 |
| `src/ZunAngle.cpp` | 1 | 0 |

The removal is limited to these reviewed standalone locals. Unused function
parameters, unknown/padding structure fields, mathematical operations that feed
real results, source annotations, ABI macros and compiler-context harnesses are
preserved. All function/global/vtable annotations in the 19 changed source files
were compared with checkpoint `54c6d82` and remain identical. Compiler/link flags,
Oracle code, target boundaries and reviewed linkage inputs are unchanged.

The exact original fragments are retained in
`.analysis/artificial-locals-removal.json`; this is also the source for the table
above. No surviving exact result is inferred from the removal. Every affected
and unaffected annotated owner must pass the new current-source replay. A
previous exact result that depended on these artificial inputs is withdrawn
rather than kept through padding, forced arithmetic or a changed comparison.
Other compiler-context helpers, forced accesses and type hypotheses still need
separate source review; this cleanup is not whole-source origin acceptance.

The completed incremental replay reports **600 exact, 49 mismatch and 565
incomplete** among the same 1214 annotated candidates, totaling 107,651 exact
owned bytes. Twenty-three previous exact results from `54c6d82` are withdrawn:
fifteen no longer have equal complete extents, and eight have complete byte
differences. No new exact result is claimed for this cleanup. All other 600
previous exact owners remain exact, including the 569-byte line renderer.

The withdrawals include directly edited effect/notice functions and callers
whose LTCG frame context changes, including shooting, menu cursors and input
polling. Full per-function changes are in
`.analysis/artificial-locals-regression-check.json`; generated canonical ledgers
and retained units reflect these withdrawals. The current report is
`.analysis/reference-audit.json`, and the incremental build/audit logs are
`.analysis/artificial-locals-final-build.log` and
`.analysis/artificial-locals-final-audit.log`.

Fifty-five controls pass against the new artifacts: twelve complete-owner,
twenty-three reviewed-linkage, thirteen cursor-limit and seven PDB type/storage
checks. `scripts/progress.py` confirms current source, artifact, report and unit
identities. This source cleanup does not change the Oracle or confer Factory
acceptance. Do not recover the withdrawn exact labels by restoring the removed
dead metadata; reconstruct the real dataflow, types and calling context instead.

The withdrawn `InterpInt3::step` is a complete 926-byte owner with one differing
SIB byte at offset 872: the target's final y-coordinate LEA uses `[edx + ebx]`,
while the candidate uses `[ebx + edx]`. Reversing the outer addition to
`initial + (goal - initial) * x`, or naming the live delta and scaled offset,
leaves exactly the same difference. Both trials were reverted. The function
remains mismatch; neither operand equivalence nor the old three dead locals
grants exact credit. The ignored records are `.analysis/int3-anchor-first.json`
and `.analysis/int3-displacement.json`.

After reverting those trials, the restored source was rebuilt incrementally and
replayed again. The same 600 exact owners and 23 withdrawals are confirmed;
canonical units have no additional change. The final log is
`.analysis/artificial-locals-restored-audit.log`, and the refreshed regression
record points to the current artifacts. Four additional build-context controls
pass, including stale-input/artifact rejection and explicit cold-build policy.

## String, local-time and array allocation identities

Five reviewed runtime entries now have independent role evidence and complete
original/candidate extents: strchr, strrchr, stricmp, localtime64 and array new.
The byte-search directions are established from their full original algorithms;
the comparison's ASCII child is independently identified by Ghidra. The time
wrapper's conflicting auto-label is resolved by its child's two-word time input,
timezone and daylight-saving logic. The array allocation thunk forwards to the
previously reviewed scalar new and is used by an array-cookie allocation path.
Detailed addresses and contracts are in `reviewed-linkages.md`.

No game source, compiler profile or Oracle comparison rule changes in this
batch. Twenty-three reviewed-linkage controls pass. The current replay reports
**608 exact, 49 mismatch and 557 incomplete** among 1214 candidates, with all
600 exact results at `95bfc44` retained. New complete passes include the replay
and high-score drawing functions, Arcfile::find_entry, make_full_path, startup
shortcut handling and SoundManager::find_bgm. Evidence is
`.analysis/string-time-runtime-audit.log` and `.analysis/reference-audit.json`.
These are local code results; runtime callee exactness, source-origin acceptance
and Factory Truth Kernel acceptance are not inferred.

## RTTI-backed primary vftable evidence

The new linkage proof identifies ThreadInf and Pbg::File's primary vftable
address points from their full original RTTI class names and single-inheritance
contracts. It checks complete PDB data contributions, locator prefixes, all
virtual slots, every slot relocation, complete code ownership and previously
fixed original function identities. The original callable extent cannot stop
before another code pointer. Interior addresses and direct code calls to a vftable
address point remain unsupported.

Twenty-nine controls include both real table sizes, complete ThreadInf destructor
replay, changed names/namespaces, partial or ambiguous storage, an omitted base
array byte, missing relocation, wrong slots, absent function identities, zero
callee extent, conflicting owners, wrong data protection, unsupported inheritance
and misuse of the address point. A proof-module mutation also invalidates the
Oracle identity. Tests and implementation are in `scripts/test-vtable-identities.py`
and `scripts/vtable_identity.py`; complete formats and original addresses are
recorded in `reviewed-linkages.md`.

The final report has **614 exact, 49 mismatch and 551 incomplete** among 1214
candidates, with 110,914 exact owned bytes. All 608 exact results from `1a32210`
remain exact. Six complete consumers become exact: ThreadInf::~ThreadInf
(11 bytes), LoadingThread::create (147), Arcfile::read_file (367), Pbg::File::open
(328), Pbg::File::read_whole (246) and D3DThreadInf's scalar deleting destructor
(41). Their full code extents and exhaustive fields are replayed; no prefix,
vftable data or virtual callee receives separate exact credit.

All 88 controls pass (29 new vftable controls and the existing 59 Oracle,
linkage, cursor, PDB type and build-context controls). The final audit is
`.analysis/vtable-identity-final-audit.log`, and the full retained-pass check is
`.analysis/vtable-identity-regression-check.json`, against the committed
`1a32210` match ledger. Game source and compiled artifacts are unchanged in
this metadata batch. No new game build was needed. Complete code-comparison
rules stay in force; source-origin review and Factory acceptance remain open.

## Laser primary vftables

All five laser primary tables now pass the existing RTTI/PDB proof without a
checker change. Each has 26 callable slots, with a complete 108-byte candidate
contribution including its locator prefix. All 130 slot identities agree with
the fixed original function bindings. There is no virtual destructor slot;
cloning is slot 25. The complete source contract and original type names were
reviewed alongside the pointer inventory in `.analysis/laser-vtable-slots.csv`.

The report advances to **620 exact, 49 mismatch and 545 incomplete** among 1214
candidates, retaining every previous 614 exact result. New complete passes are
LaserDataInf's constructor (138 bytes), LaserLineInf::clone (117), and the line,
infinite, beam and curve constructors (83, 81, 61 and 72). Thirty vftable controls
pass, including the new full 138-byte, 26-slot constructor replay. Evidence is
`.analysis/laser-vtable-audit.log` and `.analysis/laser-vtable-controls.log`.
No game rebuild, code-comparison relaxation or source-origin acceptance is used.


## Unfinished atan2 entry investigation

Work stopped at the user's handoff request before this experiment was tested
or accepted. There is no `__CIatan2` row in the active linkage bindings and no
change to the Oracle's same-start contribution rule.

The current candidate public `__CIatan2` is at `0x00487A4A`, ten bytes into the
complete 20-byte UCRT `87ctriga.obj` contribution rooted at `_atan2`
(`0x00487A40`). The owning module's CodeView symbol substream has explicit
S_GPROC32 records for `atan2` and `_CIatan2`, each with code size 10 and its own
S_END. In the current PDB these are module 266, stream 279, symbol-byte extent
380, procedure records 276/328 and S_END records 324/376. These indices describe
this artifact and must be rediscovered after linking. Native LLVM output is
retained in `.analysis/atan2-module-symbols.txt`.

Both candidate entries are closed ten-byte `mov edx, descriptor; jmp dispatcher`
stubs. The intrinsic jumps to the named `__cintrindisp2`; the standard entry
jumps to `__ctrandisp2`. Their descriptor at `0x00494BC0` starts with the complete
length-prefixed name bytes `05 61 74 61 6e 32 00 00` (atan2).

The original intrinsic entry is the independent ten-byte boundary at
`0x00487AAA`, loading descriptor `0x00494E50` with the same name and jumping to
`0x00488BB0`. That independently bounded 68-byte dispatcher consumes two x87
arguments. The adjacent original standard entry at `0x00487AA0` is not in the
Ghidra boundary inventory; do not fabricate a 20-byte original function from
adjacency. The current `zun_atan2f` consumer at original `0x004052A0` has complete
57-byte candidate/target extents but remains incomplete without the callee
identity. These observations grant no exact claim.

An unvalidated parser/proof draft is archived in
`.analysis/experiments/atan2-intrinsic-draft.py.gz`. Its Oracle integration and
CSV row were withdrawn, restoring the verified `a928c07` comparison inputs.
A future implementation would need to validate complete MASM procedure records,
terminators, unique module/library provenance, matching function publics and
full partition of the entire parent contribution, with negative controls.
It must not broaden primary game-function ownership, accept an arbitrary
interior public, truncate the parent, or credit an external callee as exact.

## Stack probing, thread startup and bounded source trials

The 2026-11-11 batch independently reviews `__chkstk` and `__beginthreadex`.
Their complete original boundaries are 45 and 133 bytes; both candidate
contributions have the same respective sizes and belong to pinned Microsoft
libraries. The stack-probe algorithm and the thread entry's imported
`CreateThread`, error path and ownership transfer establish their roles.
See [reviewed linkages](reviewed-linkages.md). No comparison-rule change or
external-callee exact credit is used. The questionable 2991-byte original
`floor` extent remains unbound, including its distant fallback path.

The final incremental audit reports **626 exact, 49 mismatch and 539
incomplete**, totaling 112,605 exact owned bytes. All 620 exact results from
`e75fbd0` remain exact. The six newly complete passes are:

| Target | Function | Complete bytes |
| --- | --- | ---: |
| `0x004029D0` | `GameErrorContext::log` | 193 |
| `0x00402FB0` | `ThreadInf::restart` | 61 |
| `0x0043AF60` | `LoadingThread::initialize` | 125 |
| `0x0043C5B0` | `Supervisor::start_thread` | 126 |
| `0x00448C10` | `ReplayManager::read_replay_file` | 524 |
| `0x0044AEE0` | `TitleInf::create` | 110 |

Resolving the stack-probe field also exposes `WinMain`'s unequal complete
extent. It remains incomplete; the change in recorded reason grants no credit.

The source trials below were rejected and fully restored before the final
incremental build. They grant no source-code improvement or exact credit:

- `AnmVm::load_from`: using the original source parameter throughout, a separate
  byte pointer after the VM and a block-local consumed count produces 637 bytes
  rather than 650. Keeping the VM alias and advancing the source parameter, but
  moving the count into the callback block, retains 650 bytes with seven
  differences. The count then uses the original argument slot at `[ebp+8]`, but
  the callback-index address moves from `[ebp-8]` to `[ebp+12]`, shrinking the
  frame from 28 to 24 bytes and moving the timer snapshots. An explicit const
  reference to the source callback-index field gives exactly the same result.
  The restored baseline still has just the three count-slot differences.
- `InterpFloat3::step`: using `tick()`, velocity-first acceleration addition
  and scalar-left cubic vector products together produces 902 bytes rather
  than 906. The scaled timer path still adds current time into the speed's
  register; the original loads current time into XMM0 and adds the speed.
  The two-dimensional interpolation repair cannot simply be carried over.
- `BulletManager::clear_all`: a named velocity delta followed by indexed
  component additions retains 500 bytes, but changes instruction scheduling
  and the exhaustive linkage offsets. The source form that helped the line
  renderer does not recover this half-step owner.

Private evidence includes `.analysis/load-from-natural.json`,
`.analysis/load-from-inner-scope.json`,
`.analysis/load-from-index-reference.json`,
`.analysis/interp3-timer-vector.json` and
`.analysis/bullet-half-step-index.json`. Extent/manifest refusals are diagnostic
results, not complete byte comparisons. The final restored-source build log is
`.analysis/source-trials-restored-build.log`.

The final runtime context, audit and retained-pass comparison are
`.analysis/stack-thread-runtime-context.json`,
`.analysis/stack-thread-linkage-audit.log` and
`.analysis/stack-thread-regression-check.json`. All 24 reviewed-linkage and
12 strict-Oracle controls pass, including truncated original/candidate extents
and swapped library ownership for the new entries. Independent focused replay
of the complete error logger and thread restart passes. `scripts/progress.py`
confirms source, artifact, report and retained-unit freshness. Source-origin
review and Factory acceptance remain open; no repository contents were pushed.

## Bounded switch ownership and natural WinMain cleanup

The next 2026-11-11 batch reviews eight original bounded dispatches and their
complete trailing tables. See [switch ownership](switch-ownership.md) for
original bounds, hashes, all slot mappings and the conservative proof contract.
The final incremental audit reports **633 exact, 52 mismatch and 529 incomplete**,
with 114,245 exact owned bytes. All 626 exact results at `544cd9a` remain exact.
The seven gains add 1,640 exact bytes:

| Target | Function | Complete bytes |
| --- | --- | ---: |
| `0x00401460` | `UpdateFuncRegistry::run_all_on_tick` | 308 |
| `0x004015A0` | `UpdateFuncRegistry::run_all_on_draw` | 260 |
| `0x00402FF0` | `PosVel::update_secondary_fields` | 276 |
| `0x004071A0` | `anm_masked_effect_init` | 396 |
| `0x0040DA90` | `BombInf::destroy_all` | 144 |
| `0x0044B530` | `TitleInf::on_draw` | 156 |
| `0x00468C00` | `AnmVm::write_sprite_corners` | 100 |

Six gains follow restored whole-owner scope, including every table relocation;
the initialization gain follows the independently witnessed `240.0f` binding.
`PosVel::step` remains a complete 700-byte mismatch. The masked-effect switch
callback remains a complete 336-byte mismatch, with 45 differing bytes after
that literal is bound. Correct ownership and binding expose differences and
grant no exact credit by themselves.

WinMain's earlier 2918-byte candidate was not a one-byte reconstruction problem.
Removing the explicitly artificial `volatile` result variable, preserving the
original current/previous input-store order, and using the original countdown
cleanup loop produces a natural 2919-byte candidate. The complete original
extent also has 2919 bytes, but 900 bytes differ after exhaustive linkage replay.
The cleanup is retained without exact credit; register allocation, message-loop
scheduling and other control-flow differences remain open. Diagnostic evidence
includes `.analysis/winmain-initial-owner-diff.txt`,
`.analysis/winmain-natural-countdown-owner-diff.txt` and
`.analysis/sound-unpause-winmain-loop.json`.

Rejected source trials were restored before the final build:

- Reordering the floating additions in `CSound::Unpause` retains a 107-byte
  candidate against 103 original bytes. Naming the pause-duration intermediate
  makes it 116 bytes. Neither trial solves floating operation scheduling.
- Replacing the masked-effect callback's chained vector assignment with three
  component-wise assignment chains produces 364 bytes instead of 336. It is
  refused before byte comparison. The restored vector expression retains the
  known load order and zero-store scheduling differences.

Evidence is `.analysis/sound-unpause-swapped-diff.txt`,
`.analysis/sound-unpause-duration-build.log`,
`.analysis/masked-switch-components.json` and
`.analysis/masked-switch-owner-diff.txt`. The final build log is
`.analysis/switch-batch-final-build.log`.

`scripts/audit-reference.py --address ADDRESS --json .analysis/NAME.json` now
supports repeatable focused full-owner diagnostics without replacing canonical
reports or ledgers. Independent bindings still use all annotations. Three
controls verify deduplication, full comparison, forbidden canonical writes and
unannotated-address refusal. The switch proof has 19 controls, and the new
literal adds one reviewed-linkage control with three negative cases. All 113
controls across the eight suites pass. The existing strict-Oracle overlap test
fixture now explicitly supplies an empty switch-review map.

The final audit and regression record are
`.analysis/bounded-switch-full-audit.log` and
`.analysis/bounded-switch-regression-check.json`. `scripts/progress.py` confirms
source, artifacts, report and unit freshness. Source-origin review and formal
Factory acceptance remain open. No outputs were cleaned and nothing was pushed.

## PosVel component arithmetic and bounded scheduling trials

The next source batch starts from `bbfaf02`. Its complete `PosVel::step` owner
at `0x00403110` has 700 bytes, including alignment and its five-slot jump table.
The baseline strict replay matches 669 bytes and differs in 31. Indexed
component addition for the wave center and explicit indexed vector construction
for the circle/wave positions retains the full 700-byte scope and matches 684
bytes, leaving 16 differences. This is source progress within a mismatching
owner; it grants no new exact function or prefix credit. No Oracle, boundary,
binding, compile-profile or harness change is involved.

The wave-center update now follows the original scalar load/add order. The
remaining differences occur at the circle's first component addition and the
wave-position vector's load/add scheduling. The ellipse branch is unchanged.
The reviewed table structure and every table relocation still participate in
complete-owner comparison.

The following trials were rejected. Candidate extent differences are refusals,
not byte comparisons against shortened original ranges:

| Trial | Candidate bytes | Complete result |
| --- | ---: | --- |
| Swap binary vector operands; assign a vector sum to the center | 704 | Incomplete |
| Accumulate into offset vectors before copying to position | 732 | Incomplete |
| Accumulate only the circle's x component; use mixed wave operand order | 724 | Incomplete |
| Rebuild a planar vector from x/y and zero z before vector addition | 700 | Mismatch; 671 matching bytes |
| Mix indexed x with named y/z members in wave construction | 700 | Mismatch; 667 matching bytes |

Reverting just the circle constructor was not tested in isolation: the trial
also changed `ScreenEffect::on_tick_shake` to the regular timer helper. That
combined build did not retain the 684-byte result. Do not infer that a source
expression is dispensable merely because its own branch's initial diagnostic
looks unchanged; evaluate the whole owner and isolate any causal claim.

The regular shake timer produces 474 bytes rather than the independent 476-byte
original. Its original helper is restored. A named precomputed limit in
`draw_triangle_fan` retains 355 bytes with the same six scheduling differences;
it is also restored. The VM deletion alias and next-first traversal trials
repeat earlier rejected observations (108 bytes, or 112 with 105 matching
bytes). Both are restored; see the earlier runtime/literal section before
repeating these paths again.

Private evidence includes `.analysis/posvel-step-baseline.json`,
`.analysis/posvel-step-indexed.json`,
`.analysis/posvel-step-indexed-owner-diff.txt`,
`.analysis/posvel-step-order.json`,
`.analysis/posvel-step-accumulation.json`,
`.analysis/posvel-step-mixed.json`,
`.analysis/posvel-planar-construction.json`,
`.analysis/posvel-mixed-access.json`,
`.analysis/posvel-shake-timer.json`,
`.analysis/triangle-fan-limit.json` and
`.analysis/disable-vms-next-first.json`. The indexed source snapshot is
`.analysis/posvel-step-indexed.cpp`; the final source adds only an explanatory
comment to that form. All other maintained game sources are restored.

The final incremental build and full audit reproduce the 684/700-byte mismatch.
All 633 exact results from `bbfaf02` remain exact; totals stay **633 exact,
52 mismatch and 529 incomplete**, with 114,245 exact owned bytes. The complete
linkage manifest records the zero-literal field's changed candidate offset;
no relocation is omitted or masked. Nineteen switch-ownership and twelve
strict-Oracle controls pass. `scripts/progress.py` confirms current sources,
artifacts, report and retained units. Final evidence is
`.analysis/posvel-source-final-build.log`,
`.analysis/posvel-source-final-audit.log`,
`.analysis/posvel-source-regression-check.json`,
`.analysis/posvel-switch-controls.log` and `.analysis/posvel-oracle-controls.log`.
Source-origin review and Factory acceptance remain open. No clean build,
artifact cleanup, remote publication or Oracle-rule change was needed.

## Complete empty-EH3 destructor graphs

The next bounded evidence batch reviews `ItemManagerInner::~ItemManagerInner`
at `0x0042F150` and `StageInner::~StageInner` at `0x00409770`. Their complete
70/73-byte bodies now pass after the full 27-byte private handlers, full
36-byte empty FuncInfo descriptors, parent registration edges and runtime
entry identities are checked. The Item destructor receives a synthetic symbol
annotation; no handler implementation or padding source is introduced.

See [EH ownership evidence](eh-handlers.md) for the original role witnesses,
qualified private MAP/PDB ownership, complete hashes, runtime source and refusal
conditions. These auxiliary owners are linkage evidence only. Nonempty tables,
other handler shapes and arbitrary private symbols remain unbound.

An incremental build and broad replay retain all 633 prior exact results and
add these two complete parents: **635 exact, 52 mismatch and 528 incomplete**
among 1215 annotated candidates, with 114,388 exact primary bytes. All 137
controls pass across nine suites, including 25 EH mutations. Evidence is
`.analysis/eh-incremental-build.log`, `.analysis/eh-reviewed-graph-evidence.json`,
`.analysis/eh-focused.json`, `.analysis/eh-full-audit.log`,
`.analysis/eh-regression-check.json` and `.analysis/eh-*-controls.log`.
Source-origin review remains open and Factory acceptance is not submitted.
The repository has not been pushed or published.

## PosVel wave addition and isolated source trials

The next source batch starts from `b1ea1e8`. In the wave branch of
`PosVel::step` at `0x00403110`, the indexed three-component constructor is
replaced with the direct vector expression `pos = offset + center`. Together
with the existing indexed circle construction and indexed drift-center update,
this improves the complete 700-byte comparison from 684 matching bytes to 696.
The wave-position load/add scheduling now agrees with the original. This is a
natural D3DX vector addition; no helper, unused local, profile or Oracle rule
is introduced.

The complete owner still mismatches. Its only four differing bytes are at
offsets `0x73`, `0x74`, `0x7D` and `0x7E`, in the circle branch. The original
loads `offset.x` into XMM2 and then adds `velocity.x`; the candidate loads
`velocity.x` and adds `offset.x`. No register or operand normalization is
permitted. The full 700 bytes still include the alignment byte and all five
jump-table slots; all 30 linkage fields are enumerated and replayed. There is
no prefix-only credit.

The previously missing isolated circle experiment is now complete. Replacing
only the indexed circle constructor with `pos = velocity + offset`, while
retaining the indexed wave construction, produces 667 matching bytes rather
than 684. The circle's first-component difference remains, and the wave branch
also changes. This demonstrates that a local source expression can affect
another branch's code generation in this owner. Do not discard the indexed
circle construction based only on its own first difference.

All PosVel trials compare the complete original owner. Extent differences are
refusals, not shortened byte comparisons:

| Trial | Candidate bytes | Complete result |
| --- | ---: | --- |
| Circle `velocity + offset`, indexed wave | 700 | Mismatch; 667 matching bytes |
| Circle `offset += velocity; pos = offset`, indexed wave | 732 | Incomplete |
| Circle `offset + velocity`, indexed wave | 700 | Mismatch; 667 matching bytes |
| Indexed circle, wave `offset + center` | 700 | Mismatch; 696 matching bytes; retained |
| Indexed circle, wave `pos = offset; pos += center` | 716 | Incomplete |
| Circle `offset + velocity`, wave `offset + center` | 700 | Mismatch; 671 matching bytes |
| Circle `velocity + offset`, wave `offset + center` | 700 | Mismatch; 671 matching bytes |
| Circle `D3DXVec3Add`, wave `offset + center` | 732 | Incomplete |

Two bounded Fog trials and one return-path trial were also restored. Moving
the vertical grid-step declaration after the position initialization makes
`Fog::set_rect` 329 bytes rather than the independent 326. Constructing the
position vector directly in that form restores 326 bytes but matches only 220,
versus the baseline's 320. Adding an explicit return after the large-strip loop
in `Supervisor::create_fog_vm` retains 186 bytes but matches 167, versus the
baseline's 183. None improves its complete owner. The improved PosVel form
remains 696/700 in both Fog trial builds.

The retained source change is only the wave-position expression in
`src/PosVel.cpp`. The diagnostic summaries and source snapshots are
`.analysis/posvel-circle-only.json`, `.analysis/posvel-bounded-trials.json`,
`.analysis/posvel-circle-wave-trials.json`, `.analysis/fog-source-trials.json`,
`.analysis/posvel-wave-offset-sum.cpp` and the per-trial build/audit reports.
The earlier [component-arithmetic trials](#posvel-component-arithmetic-and-bounded-scheduling-trials)
remain relevant to the indexed drift-center update and rejected combined forms.

The final incremental build and full audit reproduce the 696/700-byte mismatch
and retain all 635 exact results from `b1ea1e8`. Totals remain **635 exact,
52 mismatch and 528 incomplete**, with 114,388 exact owned bytes. Nineteen
switch-ownership and twelve strict-Oracle controls pass. Current-state evidence
is `.analysis/wave-source-final-build.log`,
`.analysis/wave-source-final-focused.json`,
`.analysis/wave-source-final-owner-diff.txt`,
`.analysis/wave-source-final-audit.log`,
`.analysis/wave-source-regression-check.json`,
`.analysis/wave-switch-controls.log` and `.analysis/wave-oracle-controls.log`.
`scripts/progress.py` verifies source, artifact, report and retained-unit
freshness. Source-origin review and Factory acceptance remain open.

## Original manager callback scopes

The next review starts from `16eca1e`. The old combined extent-difference
diagnostic also covered missing original inventory entries. An original-only
registration and control-flow investigation establishes seven complete callback
scopes: two BulletManager callbacks, two EffectManager callbacks and three
ItemManager callbacks. The scope derivation reads no candidate artifacts or
candidate sizes. See [manager callback evidence](manager-callbacks.md) for
registration instructions, parent hashes, every original extent and behavior.

The seven existing C++ candidates all pass complete same-start PDB owner and
byte/relocation replay after those original scopes are fixed. No game source
or build profile changes, so the current incremental artifacts are reused.
The original Ghidra inventory is preserved. Seven native-review rows and seven
unknown/review origin rows are added with explicit evidence provenance.

The Oracle now reports missing independently reviewed original boundaries
separately from actual extent differences. Both remain refusals. Two controls
exercise the distinction without changing any acceptance condition.

The full replay retains all 635 prior exact results and adds seven complete
owners, totaling **642 exact, 52 mismatch and 521 incomplete**, with 114,622
exact owned bytes among 1215 annotated candidates. The incomplete groups now
include 124 missing original boundaries and 112 genuine extent differences;
previously both used the same reason. All 140 controls pass across nine suites.
The target verifier confirms the canonical executable identity.

Evidence is `.analysis/reviewed-manager-callbacks.json`,
`.analysis/manager-callbacks-focused.json`,
`.analysis/callback-boundary-full-audit.log`,
`.analysis/callback-boundary-regression-check.json` and
`.analysis/callback-*-controls.log`. Source-origin review and Factory acceptance
remain open. No compiler rebuild, analyzer mutation or remote publication is
needed for this review.

## Registered callback closure and recorded-input cleanup

Starting from `b32d469`, the remaining 24 registered roots in the original-only
callback discovery index are reviewed. Their original relationships establish
three more entries: a second HelpManual worker and two Replay callback bodies.
All 27 complete scopes are derived from original instruction witnesses and
closed dense control flow, with no candidate sizes or artifacts as inputs.
See [registered callback evidence](registered-callbacks.md) for every scope,
hash, registration witness and the individually reviewed indirect call sites.
The Ghidra inventory is preserved; native-review provenance and unknown/review
source-origin rows are explicit.

The initial focused audit passes 26 complete owners totaling 1,504 bytes,
including Replay playback's complete 442-byte body. Replay record's complete
original scope is 337 bytes; its 298-byte candidate initially fails the extent
check. Its unsupported `volatile` recorded-input local explicitly stood in for
an unexplained original stack spill. Remove that artificial qualifier and its
upstream-percentage comment, retaining the ordinary input-selection/recording
logic. The incremental build yields a 281-byte candidate; it remains incomplete
and receives no new exact credit. Original frame alignment and local lifetime
still require source/type/context evidence. Do not restore forced accesses to
imitate those bytes.

The final full audit retains all 642 previous exact results and adds the 26
complete passes: **668 exact, 52 mismatch and 495 incomplete**, totaling 116,126
exact owned bytes among 1215 annotated candidates. The missing-boundary group
falls from 124 to 97; the actual extent-difference group grows from 112 to 113
because record's original boundary is now known. All 21 relevant controls pass
across the build-context, focused-audit and strict-Oracle suites. No Oracle or
binding implementation changes, cold build or analyzer mutation is needed.

Evidence is `.analysis/reviewed-registered-callbacks.json`,
`.analysis/registered-callback-focused.json`,
`.analysis/record-input-cleanup-build.log`,
`.analysis/registered-callback-cleanup-focused.json`,
`.analysis/registered-callback-full-audit.log`,
`.analysis/registered-callback-regression-check.json` and
`.analysis/registered-{build,focused,oracle}-controls.log`. The original-only
reproducer is `.analysis/review-registered-callbacks.py`; all review roots are
excluded from its input boundary basis before re-deriving their scopes.
Source-origin review and Factory acceptance remain open. Nothing is published.

## AnmManager registry callbacks and constructor EH investigation

Starting from `efb48b8`, an original-only review derives all 41 callback roots
from the 5,071-byte AnmManager constructor, rather than using annotation sizes.
Original WinMain directly calls the constructor at `0x00459E70`. Every normal
constructor instruction and registration witness is reachable from its entry.
Each registration block establishes its callback field, manager argument,
cleared registration/cleanup callbacks, registry kind and priority.

All 39 draw callbacks and both tick callbacks have independently reviewed
complete dense scopes. Thirty-three draw callbacks are complete eight-byte
push/call/return owners; six include camera and device state transitions.
Fifteen individually reviewed virtual calls have ordinary continuations.
Every gap to the next independent entry is INT3 alignment, and no new scope
overlaps an existing owner. Candidate artifacts and sizes are absent from the
scope derivation. See [AnmManager callback scopes](anm-callback-scopes.md).

All 41 existing C++ candidates pass unchanged complete-owner and relocation
replay, adding 1,182 exact primary bytes. The full audit retains all 668 prior
exact results and reports **709 exact, 52 mismatch and 454 incomplete**, with
117,308 exact owned bytes among 1215 annotated candidates. All 720 prior
comparison units remain identical. Missing independently reviewed original
boundaries fall from 97 to 56. All 17 relevant focused-audit and strict-Oracle
controls pass. No game source, compiler profile, Oracle or binding implementation
changes, rebuild or analyzer mutation is needed.

The constructor remains incomplete on its offset-six private handler field.
An independent native investigation finds five unwind states, a complete
136-byte action/handler code bundle and a complete 76-byte FuncInfo/unwind-map
bundle. Candidate PDB ownership aggregates all five actions and the handler in
one contribution, and both metadata symbols in another. The 27-byte handler is
an interior entry and cannot be passed to the existing standalone-owner proof.
The current empty-EH3 validator intentionally remains unchanged. Supporting
this graph requires complete aggregate ownership, interior-symbol, relocation,
state-map, frame and runtime evidence with corresponding refusal controls.
No constructor or auxiliary exact credit is granted by this investigation.

Retained evidence is `.analysis/reviewed-anm-layer-scopes.json`,
`.analysis/anm-layer-scope-focused.json`,
`.analysis/anm-layer-boundary-full-audit.log`,
`.analysis/anm-layer-boundary-regression-check.json`,
`.analysis/anm-layer-{focused,oracle}-controls.log` and
`.analysis/anm-constructor-eh-investigation.json`. The original-only callback
reproducer is `.analysis/review-anm-layer-scopes.py`. A broader discovery index,
`.analysis/missing-entry-reference-discovery.json`, records 84 original instruction
references to 74 formerly missing roots; it is not acceptance evidence for the
33 referenced entries outside the current 41-entry review. Source-origin review
and Factory acceptance remain open. Nothing is published.

## Complete AnmManager constructor EH aggregate

The next 2026-11-11 batch completes the preceding nonempty-EH investigation.
An explicit `anm-manager-constructor-v1` profile independently checks the whole
136-byte action/handler contribution and whole 76-byte FuncInfo/unwind-map
contribution. It requires all eight private names at their reviewed offsets,
complete source-qualified PDB ownership, original action inventory agreement,
every relocation, the five-state chain, cleanup/runtime entry roles and the
parent frame/cookie dependencies. See [the aggregate review](anm-constructor-eh.md).
The default empty-EH3 profile keeps its strict standalone-owner behavior.

The constructor now receives a complete comparison over all 5,071 bytes and
164 primary linkages. Its result is **mismatch: 5,054 matching bytes, 17
differences**. The difference occupies an 18-byte interval at parent
`+0xABE..+0xACF`, preceding draw priority `0x24` for layer 17: the original
clears the function and registration fields before clearing flag bit zero;
the candidate clears the flag first. The existing volatile-this constructor
remains a source/context hypothesis, not an established original source form.
No source special case, forced instruction ordering, mask or shortened owner
is introduced. No game source, compiler profile, build graph or analyzer is
changed, and no new exact credit is granted.

The broad replay reports **709 exact, 53 mismatch and 453 incomplete**, with
117,308 exact primary bytes. All 709 exact results at `0f46eaf` remain exact;
all 761 previous comparison units remain identical, alongside the new complete
constructor mismatch unit. The only primary status transition is this
constructor's incomplete-to-mismatch result. All 92 relevant controls pass
across five suites, including 25 new aggregate controls with every auxiliary
candidate byte mutated individually and the 25 existing empty-EH3 controls.

Retained evidence includes `.analysis/anm-constructor-eh-focused.json`,
`.analysis/anm-constructor-eh-full-audit.log`,
`.analysis/anm-constructor-eh-regression-check.json`,
`.analysis/anm-eh-baseline-audit.json` and the
`.analysis/anm-constructor-{eh,empty-eh,oracle,linkage,focused}-controls.log`
logs. The preceding original-first investigation and its reproducer are
preserved. Source-origin review and Factory acceptance remain open. Nothing
is published.

## Manager wrapper scopes and ordinary constructor context

The next 2026-11-11 batch reviews 20 further original registry callbacks and
the Ascii drawing helper reached through one registered callback's tail.
All 21 complete owners pass, adding 604 exact primary bytes. The original-only
proof retains actual witness paths from nine inventoried parent entries,
record/priority argument flow, all callback branches and exits, complete owner
bytes, nonoverlap and INT3 padding. Four Ascii device calls have exact-site
receiver/slot/operand reviews. No indirect-jump allowance or static device
callee binding is added. See [manager wrapper scopes](manager-wrapper-scopes.md).

The broad replay reports **730 exact, 53 mismatch and 432 incomplete**, with
117,912 exact primary bytes. All 709 exact results at `f89675d` and all 762
previous comparison units remain unchanged. The 21 additions reduce missing
original boundaries from 56 to 35. All 17 relevant strict-Oracle and
focused-audit controls pass. Maintained source, compiler profile, Oracle and
binding rules are unchanged; pending source-origin review remains explicit.

This batch also tests the unresolved UpdateFunc constructor context. Removing
volatile-this accesses and moving the ordinary constructor into UpdateFunc.cpp
builds successfully with the unchanged historical profiles. It changes eight
complete linked owner extents: create_func 106 to 77 bytes, Effect initialization
241 to 212, Ending 593 to 570, Enemy 459 to 430, GUI 258 to 229, HelpManual
243 to 214, ReplayManager 1309 to 1193 and AnmManager 5071 to 4046. Redundant
initialization writes disappear. The strict EH profile correctly refuses the
changed complete AnmManager parent. This source-placement hypothesis is
rejected; no acceptance credit or source special case is introduced.

The complete trial outputs, receipt and both modified source files are retained
under `.analysis/updatefunc-ordinary-out-of-line-artifacts/`; baseline
counterparts are `.analysis/updatefunc-context-baseline/`. After restoring the
baseline source, its full input hash and all artifact hashes were checked
before restoring the attested PE/MAP/PDB/function map and receipt. The receipt
remains incremental. Trial object caches are retained, with 104 dependency
stamps correctly identifying the restored header as an input change. The next
incremental build will recompile those dependencies normally; no clean build
or forced cache reuse is needed.

Evidence is `.analysis/reviewed-manager-wrapper-scopes.json`, its reproducer
`.analysis/review-manager-wrapper-scopes.py`,
`.analysis/manager-wrapper-focused.json`,
`.analysis/manager-wrapper-full-audit.log`,
`.analysis/manager-wrapper-regression-check.json`,
`.analysis/manager-wrapper-{oracle,focused}-controls.log`,
`.analysis/updatefunc-ordinary-out-of-line-build.log`,
`.analysis/updatefunc-ordinary-out-of-line-owner-differences.json` and
`.analysis/updatefunc-context-restore-check.json`. Source-origin review and
Factory acceptance remain open. Nothing is published.

## Runtime callback and LZSS scopes

The original-only review establishes the 13 remaining roots in the earlier
instruction-reference discovery through thread creation, vector construction
and destruction, registry insertion and LZSS tail transfers. It also replaces
the unreviewed 313-byte Ghidra LZSS deletion aggregate with three independent
owners of 84, 83 and 121 bytes, accounting for every intervening INT3 byte.
All 14 complete annotated owners pass, adding 1,305 primary exact bytes. See
[runtime entry scopes](runtime-entry-scopes.md) for the original witnesses,
runtime argument roles, parent paths, switch-path limits and complete scopes.

Full replay reports **744 exact, 53 mismatch and 418 incomplete**, with 119,217
exact primary bytes. All 730 preceding exact results and all 783 previous
comparison units remain unchanged; 14 complete units are added. Missing
original boundaries fall to 22 and genuine extent differences to 112. Strict
Oracle and focused audit controls pass all 17 checks. No game source, compiler
profile, Oracle implementation, binding rule or attested build output changes.

Evidence is `.analysis/review-runtime-entry-scopes.py`,
`.analysis/reviewed-runtime-entry-scopes.json`,
`.analysis/runtime-entry-original-review.log`,
`.analysis/runtime-entry-focused.json`,
`.analysis/runtime-entry-full-audit.log`,
`.analysis/runtime-entry-regression-check.json` and
`.analysis/runtime-entry-{oracle,focused}-controls.log`.
The preceding inventories, report and units are retained under
`.analysis/runtime-entry-baseline/`. Source-origin review remains open;
Factory acceptance remains unsubmitted and nothing is published.

## Callback-table and startup entries

The original-only review follows the remaining 21 data-address discoveries
through actual indexed callback use and producer/consumer field flow. It also
derives the gather switch entry and the Camera constructor's original caller.
The original PE entry reaches a bounded 16-cell CRT initializer interval;
one cell establishes the complete 194-byte supervisor initializer, whose
four-element loop calls the three-byte Camera entry. All 24 scopes are derived
before candidate comparison. Event-table cell windows retain unknown total
array bounds and receive no table data exact credit. See
[table entry scopes](table-entry-scopes.md).

The newly reviewed gather switch reads a complete `300.0f` at `0x0049468C`.
A fixed typed literal binding resolves that callback and the final unknown
field in Stage::load_data. Twenty-two newly reviewed owners and the complete
473-byte Stage body pass. Full replay reports **767 exact, 53 mismatch and
395 incomplete**, covering 120,612 exact primary bytes. All 744 previous exact
results and 797 previous comparison units remain unchanged; 23 exact owners
and 1,395 bytes are added, for 820 complete units. All 43 controls pass across
reviewed linkages, strict Oracle and focused audit, including four negative
mutations for the new literal's witness and width.

The piercing hit callback still has a 39-byte original and a 40-byte candidate.
Two natural source trials fail complete-owner comparison: an element pointer
gives 37 bytes; an array base pointer gives 41. Both source/output sets and
complete disassembly are retained. The preceding source is restored byte for
byte and rebuilt incrementally. The old 104 invalid header dependency stamps
are refreshed naturally; all 192 current stamps validate. Current artifacts
come from the fresh restored-source build, with its complete input identity
equal to the baseline. No archived outputs are substituted. No game source,
compiler/linker profile or Oracle implementation change is retained.

Evidence is `.analysis/review-table-entry-scopes.py`,
`.analysis/reviewed-table-entry-scopes.json`,
`.analysis/table-entry-original-review.log`,
`.analysis/table-entry-full-audit.log`,
`.analysis/table-entry-regression-check.json`,
`.analysis/table-entry-{linkage,oracle,focused}-controls.log`,
`.analysis/piercing-source-context-trials.json`,
`.analysis/piercing-restored-cache-check.json` and
`.analysis/piercing-restored-build.log`. Trial outputs are retained under
`.analysis/piercing-{element-pointer,array-base}-artifacts/`. Source-origin
review remains open; Factory acceptance remains unsubmitted. Nothing is
published.

## Complete private sincos helper ownership

Three existing imported private helpers now have explicit whole-owner proofs:
gather at `0x00406470`, bullet at `0x00417510` and laser at `0x0043AD00`.
Each original entry is established through a decoded call and a trap-free
path from its inventoried parent. Each complete 32-byte linear owner performs
x87 sincos and radius multiplication, then returns with eight stack bytes
removed. The complete candidate contribution, exact private MAP name, full
producer object/module, absence of interior names and all relocation/decode
requirements are checked. See [private sincos ownership](static-sincos-ownership.md).

An explicit reviewed private profile supplies primary ownership and exact
direct CALL identity. The helpers remain private; public selection, unreviewed
static entries and EH profiles retain their previous refusal behavior. No game
source, compiler/linker profile or attested build artifact changes. The review
introduces no emitted instructions, truncated extent or comparison mask.

Complete replay reports **779 exact, 58 mismatch and 378 incomplete**, covering
125,082 exact primary bytes. Twelve complete exact owners add 4,470 bytes.
All 767 prior exact results and all 820 prior units remain unchanged. Five
previously incomplete laser owners now compare as complete mismatches; none
receives exact credit. Seventeen new complete units give 837 total. Fifteen
other callers now expose genuine complete-owner extent differences.

All 114 controls pass across six suites, including 21 new private-identity
controls with every original/candidate helper byte mutated, partial/expanded
extents, foreign producers, MAP collisions/interiors, original witnesses,
explicit private selection, extra/crossing relocations and tail-jump rejection.
Both a private primary and its public caller also replay through the normal
retained-unit command. Freshness checks pass.

Evidence is `.analysis/static-sincos-original-scopes.json`,
`.analysis/static-sincos-initial-focused.json`,
`.analysis/static-sincos-full-audit.log`,
`.analysis/static-sincos-regression-check.json`,
`.analysis/static-sincos-{controls,oracle-controls,linkage-controls,focused-controls}.log`
and `.analysis/static-sincos-{constructor,empty}-eh-controls.log`.
The preceding report, units and inventory are retained under
`.analysis/static-sincos-baseline/`. Source-origin review remains open and
Factory acceptance remains unsubmitted. Nothing is published.

## Further sincos scopes and laser angle trials

Eight more original private helper entries now have independent call witnesses,
trap-free parent paths and complete linear 32-byte scopes. Their complete
candidate MAP/PDB producers pass the existing sincos/scale profile. Eight
explicit records extend the reviewed set to eleven; no verifier rule changes.
The different ellipse body and helpers lacking proved dispatch paths remain
unreviewed. See [further scopes and laser trials](further-sincos-scopes.md).

All eight helpers and the complete 641-byte fan initializer pass, adding nine
exact owners and 897 primary bytes. Three formerly incomplete primitive/fan
callers now compare as complete mismatches. Full replay reports **788 exact,
61 mismatch and 366 incomplete**, with 125,979 exact primary bytes. All 779
previous exact results and all 837 previous units remain unchanged; 12 complete
units are added, for 849 total. All 38 relevant controls pass: private identity,
strict Oracle and focused audit. Source-origin review remains open and Factory
acceptance remains unsubmitted.

Two natural laser source contexts are independently built and rejected.
Folding the completed-round increment into the completion condition leaves
both angle owners at 412 bytes but increases differences from 11 to 91.
Computing next length before committing both angle/length fields produces a
315-byte acceleration candidate against the complete 323-byte original. No
partial comparison or similarity credit is accepted. The original operation
at angle-step +0x33 is a memory increment, correcting the preceding handoff's
description as an argument push.

Baseline Laser.cpp is restored byte for byte and rebuilt incrementally. Its
full input identity equals the preceding baseline, all artifact hashes match
the fresh receipt, and all 192 dependency stamps validate. Neither source trial
is retained in game code. Complete source/output sets, all nine baseline/trial
owners, and strict outcomes are preserved. No clean build or archived-output
substitution is used.

Evidence is `.analysis/remaining-sincos-original-discovery.json`,
`.analysis/additional-sincos-original-scopes.json`,
`.analysis/additional-sincos-full-audit.log`,
`.analysis/additional-sincos-regression-check.json`,
`.analysis/additional-sincos-{controls,oracle-controls,focused-controls}.log`,
`.analysis/laser-angle-{completion,next-values}-focused.json`,
`.analysis/laser-angle-source-trials.json`,
`.analysis/laser-angle-restored-check.json` and
`.analysis/laser-angle-restored-build.log`. Trial sources and full outputs are
under `.analysis/laser-angle-{completion,next-values}-artifacts/`; preceding
source, report and units are under `.analysis/laser-angle-baseline/`.
Nothing is published.

## Anm bounded dispatch and circle angle trial

Original-only review establishes two AnmVmRun private helper call paths through
explicitly bounded byte-remap dispatches. The ordinary 32-byte helper at
`0x00464D60` and separate-output 39-byte helper at `0x00464930` both pass their
complete source-qualified private PDB owners. Full replay reports **790 exact,
61 mismatch and 364 incomplete**, with 126,050 exact primary bytes. All 788
previous exact results and all 849 previous units are retained unchanged;
two new complete units add 71 exact bytes. See
[Anm private dispatch review](anm-private-dispatch.md).

The verifier hashes all 460 original table bytes, checks unsigned bounds and
adjacent same-index remapping, and traverses only mapped owned instruction
starts. Other indirect jumps remain stops. The new XY profile requires every
byte of the complete different ABI. No public identity is manufactured and no
parent or table comparison credit is granted. The original parent inventory
contains code contexts, so the special-vertices extent refusal is not proof of
a genuine whole-source size difference. Complete parent code/data review is
still required. The main interpreter retains eight unresolved fields.

A natural source trial splits circle angle advancement from wrap normalization.
It builds incrementally but leaves the complete result at 514/588 matching
bytes. The trial is rejected and restored byte for byte. Full original and
baseline/trial candidate scopes are retained in
`.analysis/circle-angle-source-trials.json`, with complete output sets under
`.analysis/{primitive-source-baseline,circle-angle-advance-artifacts}/`.
Fresh restored outputs match the baseline input identity, all four artifact
hashes match their receipt, and all 192 dependency stamps validate; see
`.analysis/primitive-source-restored-check.json`. No clean build, archived-output
substitution or forced scheduling is used.

All 143 controls across seven relevant suites pass, including complete map,
target and XY-body byte mutations, guard bypass and unused-slot rejection.
Evidence is `.analysis/anm-private-dispatch-original-scopes.json`,
`.analysis/anm-private-dispatch-full-audit.log`,
`.analysis/anm-private-dispatch-regression-check.json`,
`.analysis/anm-private-dispatch-{controls,oracle-controls,linkage-controls,focused-controls,switch-controls,constructor-eh-controls,empty-eh-controls}.log`,
`.analysis/circle-angle-advance-focused.json` and
`.analysis/primitive-source-restored-build.log`. Source-origin review remains
open; Factory acceptance remains unsubmitted. Nothing is published.

## Complete special-vertices scope and countdown trial

Original-only bounded CFG traversal establishes the complete owner at
`0x004632F0`: 2,068 bytes of code, a 16-byte target table and a 17-byte byte-remap
table, ending at `0x00463B24`. All 501 decoded instructions are reachable. The
following 11 INT3 bytes belong to alignment before the next independent entry.
The inventory now records the entire **2,101-byte** owner, superseding its
preceding code-only context. See
[the scope review](special-vertices-scope.md).

An explicit primary switch profile now verifies both complete tables, the
unsigned adjacent same-index remap, owned case starts, guard bypass rejection,
all candidate table/address relocations and the full original hash. Every map
byte remains in the primary extent and is never masked or normalized. Private
helper witness review checks this complete parent payload before decoding its
code portion. Other indirect dispatches and generic private identities retain
their refusal behavior.

The complete candidate is 2,097 bytes: 2,062 bytes of code, two alignment bytes
and 33 table bytes. A natural guarded do/while countdown expresses the
original loops' positive-entry checks and nonzero decrement backedges. The
trial changes register allocation but does not change that complete extent;
it is rejected and source restored. No shortened comparison or partial credit
is accepted. Current source and full build-input identity equal the baseline,
all artifact hashes match the fresh incremental receipt, and all 192 dependency
stamps validate. No clean build or archived outputs are substituted.

Full strict replay retains **790 exact, 61 mismatch and 364 incomplete**, with
126,050 exact primary bytes. All 790 preceding exact results and all 851 prior
units remain unchanged; this batch claims no additional exact credit. All 156
controls across seven relevant suites pass. New controls include every map
byte, case slots, signed or mismatched indices, guard bypass, omitted/expanded
remap records, whole parent hashes/extents and missing/extra/crossing map or
target relocations. The structural fixture grants no candidate PDB identity;
the real candidate's extent refusal is separately checked.

Evidence is `.analysis/review-special-vertices-scope.py`,
`.analysis/special-vertices-original-scope.json`,
`.analysis/special-vertices-full-audit.log`,
`.analysis/special-vertices-regression-check.json`,
`.analysis/special-vertices-source-trial.json`,
`.analysis/special-vertices-restored-check.json` and
`.analysis/special-vertices-{static-controls,oracle-controls,linkage-controls,focused-controls,switch-controls,constructor-eh-controls,empty-eh-controls}.log`.
Baseline and trial source/output sets are under
`.analysis/special-vertices-{baseline,countdown-artifacts}/`. Source-origin
review remains open; Factory acceptance remains unsubmitted. Nothing is
published.

## Further complete remapped-switch scopes

Original-only traversal establishes ten more complete code/alignment/target/map
owners. The enemy allocator, EnemyInf integer/float global-pointer getters and
AnmVm integer/value-pointer getters pass their complete 876, 391, 549, 364, 272
and 170-byte scopes. These add **2,622 exact primary bytes**. Full replay reports
**796 exact, 61 mismatch and 358 incomplete**, covering 128,672 exact primary
bytes. All 790 preceding exact results and all 851 prior units remain unchanged;
six new complete units give 857 total. See
[further remap scopes](remapped-owner-scopes.md).

The four other complete original scopes remain refused: line/curve run_ex,
texture conversion and the ECL interpreter. Original scope derivation does not
read candidate sizes or artifacts, and all ten original patterns are retained,
including those whose candidates differ. No target is resized to a candidate.

The verifier now fully decodes original multi-byte NOP alignment intervals;
only NOP/INT3 padding is allowed, and all bytes remain compared. For five
otherwise complete candidates whose byte-map suffix cannot decode as x86,
the audit records and serializes the existing Oracle raw trailing-data coverage
declaration. All code, both tables and every map byte remain within the full
primary extent. No byte is masked or normalized by the coverage declaration.
The full map profile and all table/address relocations are still required.
A control isolates raw replay on the real 391-byte PDB owner and verifies that
changing an undecoded selector byte gives a full 390/391 mismatch. Missing,
shortened or overlapping declarations are rejected. Neither raw replay nor
`oracle_fields.py` changes.

A natural circle/rectangle collision source trial reverses rotation product
operands into matrix-coefficient-first form. It leaves the complete result at
243/400 matching bytes and is rejected. Source is restored byte for byte and
freshly rebuilt; full input identity equals baseline, all artifact hashes match
the receipt and all 192 dependency stamps validate. No clean build, archived
output substitution or forced instruction allocation is used.

All 162 controls pass across seven relevant suites. Evidence is
`.analysis/review-remapped-owner-scopes.py`,
`.analysis/remapped-owner-original-scopes.json`,
`.analysis/remapped-owner-full-audit.log`,
`.analysis/remapped-owner-regression-check.json`,
`.analysis/remapped-owner-{switch,static,oracle,linkage,focused,constructor-eh,empty-eh}-controls.log`,
`.analysis/circle-rect-source-trial.json` and
`.analysis/circle-rect-restored-check.json`. Source and complete output sets
remain under `.analysis/circle-rect-{source-baseline,matrix-products-artifacts}/`.
Source-origin review remains open, Factory acceptance remains unsubmitted and
nothing is published.

## Further complete direct-table scopes and interpolation source trials

Original-only bounded traversal establishes 37 further complete direct-table
owners, accounting for all code, alignment, target slots and following INT3
padding. No candidate artifact or size enters the derivation. Seven existing
candidates pass: Bullet::step_ex_04, both EnemyInf global-value getters,
draw_text, resolution_dialog_proc, AnmVm::get_float_var and render-state setup.
Their complete 532, 1,900, 2,808, 868, 396, 824 and 876-byte owners add **8,204
exact primary bytes**. Full replay reports **803 exact, 61 mismatch and 351
incomplete**, covering 136,876 exact primary bytes. All 796 preceding exact
results and all 857 previous units remain unchanged; seven new units give 864
total. See [complete direct-table scopes](direct-owner-scopes.md).

Twenty-five other reviewed candidates retain their different full extents.
Four equal-size candidates still lack independent fields, and the complete
1,692-byte interpolation curve owner retains its reviewed case-map refusal.
Ten additional/multiple-dispatch roots are explicitly excluded, without partial
profiles or inferred ownership. Existing verifier rules, raw replay, source/
PDB ownership and every table/address relocation remain required. No game
source or verifier change is retained.

Two natural interpolation source contexts are built and rejected. A shared
quadratic scaling return plus direct sine returns retains 1,692 bytes but
changes case starts without reproducing the original mapping. Separate reflected
coordinate assignments plus constant-first sine addition gives 1,696 bytes.
Diagnostic case mappings use the candidate's actual table operand after this
extent change. Neither shortened scopes nor relocation addends hide the layout
differences. Baseline source is restored byte for byte and freshly rebuilt;
input identity equals baseline, all artifact hashes match their receipt and
all 192 dependency stamps validate. No clean build, archived-output substitution,
dead locals, forced registers, assembly or padding is used.

All 166 controls pass across seven suites. New controls replay all seven full
owners, remove each of the two enemy getters' 98 table relocations, retain
25 whole-extent refusals and keep ten unsupported graph roots unreviewed.
Evidence is `.analysis/review-direct-owner-scopes.py`,
`.analysis/direct-owner-original-scopes.json`,
`.analysis/direct-owner-full-audit.log`,
`.analysis/direct-owner-regression-check.json`,
`.analysis/direct-owner-{switch,static,oracle,linkage,focused,constructor-eh,empty-eh}-controls.log`,
`.analysis/interp-methods-source-trials.json` and
`.analysis/interp-methods-restored-check.json`. Full sources and outputs are
retained under `.analysis/interp-methods-{source-baseline,return-flow-artifacts,reflected-curve-artifacts}/`.
Source-origin review remains open; Factory acceptance remains unsubmitted.
Nothing is published.

## Complete compound switch ownership

Original-only traversal establishes nine complete owners with 20 target tables
and six byte maps. Eight supersede earlier multiple-dispatch exclusions; the
ninth is the main Anm interpreter. Existing window_proc and AnmManager::draw_vm
candidates pass their complete 680/1,896-byte owners, adding **2,576 exact
primary bytes**. Full replay reports **805 exact, 61 mismatch and 349 incomplete**,
covering 139,452 exact primary bytes. All 803 preceding exact results and all
864 previous units remain identical; two new units give 866 total. Every other
audit result is unchanged. See [compound scopes](compound-owner-scopes.md).

The new explicit compound profile checks all dispatch sites, owned code/data,
case mappings, bounded byte maps, cross-table guard bypasses and exhaustive
relocations. Supervisor's ECX-to-EAX remap and the interpreter's 313-entry input
map have separate structural controls. The original interpreter now owns
14,177 bytes against its 14,141-byte candidate; it still exposes eight unbound
fields first. Seven reviewed originals receive no candidate credit. Ascii's
memory-bound/reload flow and the large enemy ECL body's interposed frame store
remain unreviewed. No partial profile, mask, raw replay or field-normalization
change is introduced. No game source change, rebuild or cleanup occurs.

All 187 controls pass across eight suites. Evidence is
`.analysis/review-compound-owner-scopes.py`,
`.analysis/compound-owner-original-scopes.json`,
`.analysis/compound-owner-focused.json`,
`.analysis/compound-owner-full-audit.log`,
`.analysis/compound-owner-regression-check.json` and
`.analysis/compound-owner-<suite>-controls.log`, with suite names matching
`scripts/test-<suite>.py`. The preceding report, units and original inventory
remain in `.analysis/compound-owner-baseline/`. Build inputs and artifacts are
unchanged. Source-origin review remains open; Factory acceptance remains
unsubmitted. Nothing is published.

## Complete stage-table and current-time identities

An original-only scan identifies one complete eight-row, 1,696-byte stage table
at `0x004A22D0`. Its 212-byte stride, all 352 scalar DWORDs, all 72 complete
string pointees and the independent indexed Supervisor witness are reviewed.
The explicit stage-table profile requires one complete typed/source PDB owner,
matching scalar/pointee contents and exhaustive pointer relocations. It grants
no generic mutable-data fallback. The existing imported non-LTCG support context
remains a source-context hypothesis.

The 66-byte current-time root at `0x0047A09E` is independently identified through
its 64-bit return/output contract, complete time-conversion child and original
GetSystemTimeAsFileTime import path. Both complete extents and the pinned UCRT
producer remain required. These two bindings resolve four existing whole
candidates: stage_clear (896 bytes), Supervisor::switch_gamemodes (815),
ScorefileChara::insert_score (246) and ReplayManager::set_end_stage (78).
They add **2,035 exact primary bytes**. Full replay reports **809 exact,
61 mismatch and 345 incomplete**, covering 141,487 primary exact bytes. All
805 preceding exact results and all 866 previous units remain identical; four
new units give 870 total. See [stage/time identities](stage-time-identities.md).

PauseMenu::tick_open remains incomplete after its final binding resolves: its
complete 4,676-byte candidate has four different first-table case offsets.
The original offsets are preserved. Six menu candidates now expose extent
refusals and TitleInf::on_tick still lacks one field. No table/runtime primary
credit, raw replay change, game source edit, rebuild or cleanup occurs.

All 207 controls pass across nine suites. Twenty new controls check every
scalar DWORD on both sides, every table relocation, every distinct candidate
string byte/terminator, complete source/typed PDB ownership, fixed stride
witness and both runtime extents/library ownership. Evidence is
`.analysis/stage-time-original-identities.json`,
`.analysis/stage-time-consumer-scopes.json`,
`.analysis/pause-open-case-layout.json`,
`.analysis/stage-time-full-audit.log`,
`.analysis/stage-time-regression-check.json` and
`.analysis/stage-time-<suite>-controls.log`. Original-only reproducers and
`.analysis/stage-time-baseline/` are retained. Build inputs and artifact
identities are unchanged. Source-origin review remains open and Factory
acceptance remains unsubmitted. Nothing is published.

## Replay-slot snapshot source improvement

PauseMenu::tick_open now explicitly saves item_menu.next_selection immediately
before creating the replacement replay and stores the result through that
saved slot. The original reads its slot into ESI at `0x004403F6`, calls the
factory at `0x004403FD` and stores through the saved index at `0x00440406`.
The used local recovers this ordering, releases the name-buffer register and
restores the replay-save path's original name-copy loop. It also restores the
next case offset to 3,207 from 3,206. See
[the source review](pause-replay-slot.md).

Both original and candidate owners remain 4,676 bytes, including all code,
alignment and 22 target slots. Whole diagnostic replay with all 306 linked
fields improves from 3,345 matching bytes to 4,067. The strict Oracle still
refuses three original case offsets, so **no exact credit is added**. Canonical
results remain **809 exact, 61 mismatch and 345 incomplete**, with 141,487 exact
primary bytes and 870 unchanged retained units. All preceding exact results
remain retained. Only tick_open changes among 1,719 complete source-qualified
linked owners; its entry and full extent are unchanged.

A resume branch exiting the outer switch instead of returning changes no
complete generated owner. An early return in the quit shortcut, after adding
the slot snapshot, also changes no complete generated owner. Both exit forms
are rejected; only the meaningful slot snapshot is retained. Do not repeat
these forms or force registers, SIB encodings, padding or shared-tail layout.
No verifier, target scope or normalization rule changes.

All 207 existing controls pass across nine suites. The retained source is
freshly built incrementally; artifact hashes match its receipt and all 192
dependency stamps validate. No archived output substitution or clean build is
used. Full sources/outputs are retained under
`.analysis/pause-open-{source-baseline,switch-exit-artifacts,selected-slot-artifacts,quit-return-artifacts}/`.
Evidence is `.analysis/pause-open-source-trials.json`,
`.analysis/pause-open-retained-layout.json`,
`.analysis/pause-open-complete-owner-delta.json`,
`.analysis/pause-open-retained-build-check.json`,
`.analysis/pause-open-full-audit.log`,
`.analysis/pause-open-regression-check.json` and
`.analysis/pause-open-<suite>-controls.log`. Source-origin review remains open;
Factory acceptance remains unsubmitted. Nothing is published.

## Further fixed numeric identities and music-room source contexts

Seven original-only typed read witnesses establish fixed identities for single
20, 40, 50, 60, 30 and 2.5 values and double 8. Every payload has duplicate
original read-only copies; no address is selected to make a consumer pass.
The original witness owners, full values, instruction starts and all following
padding are reviewed independently of candidate extents. The existing literal
profile is unchanged. See [the numeric review](menu-literal-identities.md).

Complete EnemyData::update_fog (1,547 bytes) and FpsCounter::draw (174) pass,
adding **1,721 exact primary bytes**. Player::check_hit_circle becomes a complete
181/258 mismatch; TitleInf::do_music_room becomes a complete 3,133/3,136 mismatch,
including its alignment and four target slots. Canonical replay reports
**811 exact, 63 mismatch and 341 incomplete**, covering 143,208 exact primary
bytes. All 809 preceding exact results and all 870 previous units remain
retained; four new complete units give 874 total. Neither mismatch receives
exact credit. Three further candidates now expose extent refusals; other
callers retain unresolved fields.

The music-room difference is three zero-store displacement bytes: the original
initializes its loop index before position X/Y, and the candidate reverses that
order. Three ordinary source contexts are rejected. Declaring the used counter
before the position stores leaves 3,133/3,136. A single zero-Float3 assignment
gives a 3,152-byte owner and is refused. Initializing X/Y per comment line gives
3,105/3,136. Actual candidate table operands locate the vector trial's changed
data extent; the original scope stays 3,136. Do not repeat these contexts or
force stores/registers. No dead local, padding helper, mask or shortened scope
is introduced.

Baseline MainMenuStates.cpp is restored byte for byte and freshly rebuilt.
Source input identity equals the preceding checkpoint, all 1,719 complete
linked source-qualified owners retain their entries/extents/raw hashes, every
artifact matches its current receipt and all 192 dependency stamps validate.
The preceding PauseMenu source improvement is preserved. No clean build or
archived-output substitution is used; no game source change is retained here.

All 208 controls pass across nine suites. The new linkage control checks all
seven values against instruction-interior/different witnesses, changed
mnemonics, expanded extents and duplicate original storage. Evidence is
`.analysis/menu-literal-original-identities.json`,
`.analysis/additional-literal-original-identities.json`,
`.analysis/enemy-fog-original-scope.json`,
`.analysis/music-room-source-trials.json`,
`.analysis/menu-literal-restored-context-check.json`,
`.analysis/menu-literal-full-audit.log`,
`.analysis/menu-literal-regression-check.json` and
`.analysis/menu-literal-<suite>-controls.log`. Original-only reproducers and full
source/output sets are retained locally. Source-origin review remains open;
Factory acceptance remains unsubmitted. Nothing is published.

## Replay FPS and further numeric identities

Three original-only witnesses establish single 176/512 identities and the
complete `%3d` format. All payloads have duplicate original read-only copies;
typed direct reads and the fixed original PUSH select storage. The complete
174-byte Cirno cancellation and 180-byte replay FPS witness owners are checked,
as is the previously reviewed complete 4,540-byte player switch owner. The
585/857-byte Cirno/Marisa update entries also have independent dense original
CFG and following-padding reviews. No candidate size enters these derivations.
See [the review](replay-literal-identities.md).

Four existing complete candidates now pass: Cirno update (585), Cirno
cancellation (174), Marisa update (857) and replay FPS drawing (180). These add
**1,796 exact primary bytes**. Full replay reports **815 exact, 63 mismatch
and 337 incomplete**, covering 145,004 exact primary bytes. All 811 preceding
exact results, all 63 complete mismatches and all 874 previous units remain
identical; four new units give 878 total. The player body retains its complete
4,540-versus-4,508 difference; player laser tick exposes another extent refusal.
Other callers retain unresolved fields. The remaining STD destination is private
exception-handling code and receives no inferred runtime/literal identity.

All 209 controls pass across nine suites. Numeric refusal controls cover the
two new values, and the complete FPS string control rejects wrong/interior
PUSHes, a changed mnemonic, duplicate original storage, a missing terminator
and shortened/ambiguous PDB contributions. Existing literal/string profiles,
source-qualified PDB ownership, whole replay and relocation rules are unchanged.
No game source, verifier, build artifact or compiler profile changes.

Evidence is `.analysis/replay-literal-original-identities.json`,
`.analysis/bomb-update-original-scopes.json`,
`.analysis/replay-literal-focused.json`,
`.analysis/replay-literal-other-focused.json`,
`.analysis/replay-literal-full-audit.log`,
`.analysis/replay-literal-regression-check.json` and
`.analysis/replay-literal-<suite>-controls.log`. Original-only reproducers and
`.analysis/replay-literal-baseline/` are retained. Build input/artifact
fingerprints equal the preceding checkpoint; no compile, analyzer, receipt
refresh or cleanup occurs. Source-origin review remains open and Factory
acceptance remains unsubmitted. Nothing is published.

## Player update and circle-check source contexts

Complete instruction alignment of the 4,540-byte original Player update and
4,508-byte candidate locates several independent differences: item-drop
power/address handling, two timer-decrement identity multiplies, afterimage
mode-word handling and scaled collision-box scheduling. The missing timer
multiplies are the existing unresolved ZunTimer context, not new permission to
insert forced operations. Bitfield/type and alias explanations remain open.
See [Player source contexts](player-context-trials.md).

Four natural source contexts are built incrementally and rejected. A used
position pointer for coordinate reads and item creation produces a complete
4,504-byte update; limiting it to item creation gives 4,508. Both retain
whole-extent/case-map differences. Float2 circle displacement gives 261 bytes
against the complete 258-byte original. Combining equivalent dialogue and
non-graze invalid-state rejection remains a complete 190/258 mismatch against
baseline 181/258. It does not recover original load/shared-return layout and
is not retained for nine matching bytes. Do not repeat these four forms or
force registers, stack offsets, branches or arithmetic identities.

The Float2 context also changes Bullet::check_player_collision from 449 to
460 bytes. Its original now has an independent complete 448-byte scope proof,
with 130 reachable instructions and a contiguous next entry. Full original and
candidate payloads/fields/relocations are recorded in
`.analysis/player-secondary-original-scope.json`; both candidates retain extent
refusals. This cross-translation-unit inlining effect is included in the review.

Baseline Player.cpp is restored byte for byte and freshly rebuilt. No game
source or exact credit is retained. Canonical results remain **815 exact,
63 mismatch and 337 incomplete**, covering 145,004 exact primary bytes and
878 unchanged retained units. All previous comparison results remain retained.
Every complete source-qualified linked owner (1,719) retains its entry, full
extent and raw payload hash. Current artifacts match their incremental receipt,
source input identity equals baseline and all 192 dependency stamps validate.
No clean build or archived-output substitution is used.

All 209 existing controls pass across nine suites. Complete original/trial
payloads, PDB producers, every linked field/relocation, actual table/case layouts,
source/artifact identities, strict reports and all changed complete owners are
retained in `.analysis/player-context-source-trials.json`. Full source/output
sets remain under `.analysis/player-tick-source-baseline/`,
`.analysis/player-tick-{drop-pointer,call-origin}-artifacts/` and
`.analysis/player-circle-{vector2,combined-guard}-artifacts/`. Evidence also
includes `.analysis/player-tick-baseline-layout.json`,
`.analysis/player-context-restored-check.json`,
`.analysis/player-context-full-audit.log`,
`.analysis/player-context-regression-check.json` and
`.analysis/player-context-<suite>-controls.log`. Diagnostic alignment has no
acceptance authority. Source-origin review remains open; Factory acceptance
remains unsubmitted. Nothing is published.

## Bullet collision source contexts

Six natural contexts for `Bullet::check_player_collision` are built
incrementally and rejected against its independently bounded 448-byte original.
Vector-first multiplication produces the identical 449-byte baseline owner;
in-place scaling gives 458 bytes, coordinate assignment and construction each
give 449, an explicit hit return gives 452, and a named `AnmId` gives 451.
Only this complete linked owner changes in the five nonidentical trials.
See [Bullet collision contexts](bullet-collision-contexts.md).

The remaining differences include memory versus register multiplication,
goal-vector stack location and shared-return branch destinations. A named
handle moves VM lookup after vector computation while retaining the baseline
goal location; an explicit hit return produces an immediate return value.
Neither establishes original source context. No forced register, local,
access, branch or normalization change is retained.

BulletManager.cpp is restored byte for byte and freshly rebuilt. All 1,719
complete linked owner entries/extents/raw hashes and 192 dependency stamps
validate against baseline. Canonical replay retains every prior result and
all 878 units: **815 exact, 63 mismatch and 337 incomplete**, covering
145,004 exact primary bytes. No exact credit is added. All 209 existing
controls across nine suites pass. No clean build or archived-output
substitution occurs.

Full original/trial payloads, source-qualified producers, all linked fields
and relocations, instruction streams, artifact/source identities and strict
outcomes remain in `.analysis/bullet-collision-source-trials.json` and the
matching baseline/trial artifact directories. Restoration, replay and controls
use `.analysis/bullet-collision-restored-check.json`,
`.analysis/bullet-collision-full-audit.log`,
`.analysis/bullet-collision-regression-check.json` and
`.analysis/bullet-collision-controls-summary.json`. Source-origin review
remains open and Factory acceptance remains unsubmitted. Nothing is published.

## Timing, collision and audio scalar identities

Eight independently decoded original scalar reads establish complete bindings
for 2^-31, 5.0f, 1.5f, 0.125, 2.5, 3.5, 48.0f and 56.0f. Every value has
other read-only occurrences, including embedded or unaligned patterns; only
the fixed original typed read selects storage. Complete original witness
owners, control flow, inter-entry padding and the update_window tail exit
are independently reviewed before candidate comparison. No verifier or
normalization rule changes. See
[the complete review](timing-literal-identities.md).

Nine existing full source candidates now pass: RNG normalization (64),
jagged-line animation (455), Reimu orb start (263), bullet step_ex_00 (227),
line-laser graze/hit (514), sleeping window update (597), resolution selection
(174), audio track switch (199) and audio play time (178). These add
**2,671 exact primary bytes**. Supervisor surface setup is a complete
682/693 mismatch; its two pops precede the flag clear in the original and
follow it in the candidate. Marisa cancellation retains the independently
reviewed 621-byte original against a 595-byte candidate. Neither receives
exact credit. Reimu orb update and window update retain unresolved fields.

Canonical replay reports **824 exact, 64 mismatch and 327 incomplete**, covering
147,675 exact primary bytes and 888 units. All 815 prior exact results, all
63 prior complete mismatches and all 878 prior units remain identical.
All 210 controls pass across nine suites. The reviewed-linkage suite now has
29 controls, including mutation refusal for each new scalar's instruction
interior, wrong instruction, changed mnemonic, expanded width and duplicate
original storage. Game source, compiler/linker profiles, build receipt and
all current artifacts remain unchanged; no compilation occurs.

Original identities and complete consumer evidence are
`.analysis/timing-literal-original-identities.json` and
`.analysis/timing-literal-consumer-scopes.json`. Full replay, retained-pass and
control evidence is `.analysis/timing-literal-full-audit.log`,
`.analysis/timing-literal-regression-check.json` and
`.analysis/timing-literal-controls-summary.json`; the baseline is
`.analysis/timing-literal-baseline/`. Source-origin review remains open,
Factory acceptance remains unsubmitted and nothing is published.

## COMISD scalar-width correction and complete consumers

Capstone 5.0.7 reports a 16-byte memory operand for the observed legacy COMISD
instructions, whereas the encoded scalar read is eight bytes. Intel's manual
and an independent GNU objdump 2.42 synthetic probe confirm the m64 form.
The literal-witness check now handles only the exact eight-byte absolute
`66 0F 2F /r` encoding, with matching ModRM register, decoded and encoded
disp32, eight-byte literal size and a unique fully decoded original parent
instruction start. Unsupported addressing/prefix forms and sixteen-byte
literal claims remain refused. Byte/relocation replay is unchanged. See
[COMISD evidence](comisd-literal-identities.md).

Original-only full scopes and fixed typed reads establish doubles 1.0, 0.0
and 1.5. Complete FPS update (235), frame-skipping (416) and window update
(246) now pass, adding **897 exact primary bytes**. GameThread play-time
update retains one unbound `__dtoul3` CALL. That candidate label is an interior
entry of the complete 887-byte `__ftoui3` PDB contribution from pinned LIBCMT;
it is not promoted to an ordinary same-start runtime owner.

Canonical replay reports **827 exact, 64 mismatch and 324 incomplete**, covering
148,572 exact primary bytes and 891 units. All 824 previous exact results,
64 complete mismatches and 888 previous units remain identical. All 215
controls across nine suites pass. Reviewed-linkage controls increase to 34,
covering all eight destination registers, read footprints, unsupported encodings,
original parent ownership, encoded/decoded disagreement and each fixed binding's
witness/extent/duplicate-storage mutations. Game source, compiler/linker
profiles, build receipt and all current artifacts remain unchanged.

Decoder/original evidence is `.analysis/comisd-decoder-probe.json`,
`.analysis/comisd-objdump-probe.log` and
`.analysis/comisd-original-identities.json`. Complete replay and regression
evidence is `.analysis/comisd-literal-consumer-scopes.json`,
`.analysis/comisd-literal-full-audit.log`,
`.analysis/comisd-literal-regression-check.json` and
`.analysis/comisd-literal-controls-summary.json`. The unresolved aggregate
is `.analysis/comisd-time-conversion-unresolved.json`; baseline evidence remains
under `.analysis/comisd-literal-baseline/`. Source-origin review remains open,
Factory acceptance remains unsubmitted and nothing is published.

## Complete conversion-runtime contribution and caller identities

The pinned LIBCMT conversion object has a complete 887-byte code contribution
and 130-byte read-only contribution. Independent original review covers all
207 decoded instructions, 204 reachable instructions, 11 owned alignment
bytes, surrounding INT3 padding, the entire data pool and complete caller/
exception scopes. All 24 fields replay: 23 pool displacements and one CALL.
Candidate PE relocations cover the 23 data fields; original relocation absence
is checked separately. No alignment or original displacement is masked.
See [conversion-runtime evidence](conversion-runtime.md).

An explicit profile establishes only the `__dtoul3` and `__ltod3` interior
CALL entries at offsets 496 and 848. It requires both complete PDB contributions
from one pinned producer, fixed original hashes, complete code/data replay,
unique entry publics and original direct-call witnesses. Only exact zero-addend
REL32 CALLs are admitted. The ordinary 206-byte `__except1` runtime identity
supports the one external edge. No runtime code, data, helper or exception
routine receives primary exact credit, and ordinary interior bindings remain
refused.

Complete GameThread play-time update (142) now passes. Complete get_runtime
compares at 330/332; two spill/reload displacement bytes remain different.
Reusing the fallback time variable and putting fallback declarations in a
sibling else scope produce identical complete bytes across all 1,719 linked
owners and are rejected. GameWindow.cpp is restored byte for byte and freshly
rebuilt. All owner entries/extents/raw hashes and all 192 dependency stamps
validate against baseline. No clean build or archived-output substitution occurs.

Canonical replay reports **828 exact, 65 mismatch and 322 incomplete**, covering
148,714 exact primary bytes and 893 units. All 827 previous exact results,
64 complete mismatches and 891 previous units remain retained. The 22 new
runtime controls bring the total to **237 across ten suites**. Complete original
and formal evidence is `.analysis/conversion-runtime-original-review.json`,
`.analysis/conversion-runtime-profile-proof.json` and
`.analysis/conversion-runtime-caller-scopes.json`. Trial/restoration/replay
evidence is `.analysis/conversion-runtime-source-trials.json`,
`.analysis/conversion-runtime-restored-check.json`,
`.analysis/conversion-runtime-full-audit.log`,
`.analysis/conversion-runtime-regression-check.json` and
`.analysis/conversion-runtime-controls-summary.json`. Source-origin review
remains open, Factory acceptance remains unsubmitted and nothing is published.

## Failure, tangent and short-format identities

Independent complete original review establishes the 12-byte range-check
failure entry and 605-byte precise tangent entry. Candidate owners remain
complete at 12/624 bytes from pinned Microsoft producers; the differing
tangent extents are explicit and confer no callee exact-code credit. Fixed
original PUSHes also establish complete `%s`, space and underscore storage,
with unique full candidate PDB extents and NUL-terminated payloads. No
admission or normalization rule changes. See
[the complete review](failure-tangent-runtime.md).

Five whole source candidates pass: tangent wrapper (23), keyboard drawing
(394), replay-save drawing (997), LZSS initialization (68) and ANM entry
loading (247), adding **1,729 exact primary bytes**. Canonical replay reports
**833 exact, 65 mismatch and 317 incomplete**, covering 150,443 exact primary
bytes and 898 units. All 828 previous exact results, 65 complete mismatches
and 893 previous units remain retained. All **239 controls across ten suites**
pass; reviewed-linkage controls increase to 36.

The complete spell-page original is independently reviewed at 1,011 bytes,
including its terminal INT3 and excluding thirteen subsequent padding bytes.
Baseline source owns 1,016 bytes. Retaining the digit remainder until argument
lookup gives 1,012; adding a used character-base pointer gives 994. Both are
complete extent refusals and are rejected. All changed linked owners, including
1,231 records for the second trial, retain full old/new payloads, producers,
fields and relocations in the evidence. No unequal prefix receives credit.
MainMenuStates.cpp is restored byte for byte and freshly rebuilt; all 1,719
complete linked owner entries/extents/raw hashes and 192 dependency stamps
validate against baseline. No clean build or archived-output substitution occurs.
ANM load retains an independently complete 430-byte original against 461.

Original, caller and trial evidence is
`.analysis/failure-tangent-runtime-original-review.json`,
`.analysis/failure-format-original-identities.json`,
`.analysis/failure-format-runtime-caller-scopes.json` and
`.analysis/failure-format-spell-source-trials.json`. Restoration/replay evidence
is `.analysis/failure-format-runtime-restored-check.json`,
`.analysis/failure-format-runtime-full-audit.log`,
`.analysis/failure-format-runtime-regression-check.json` and
`.analysis/failure-format-runtime-controls-summary.json`. Full baseline/trial
sets and reproducers remain local. Source-origin review remains open, Factory
acceptance remains unsubmitted and nothing is published.

## Explicit season-table linkage and complete menu drawing

The existing annotated readonly season-name array lacked an external
declaration and therefore had internal C++ linkage. Its anonymous CIL storage
provided no named PDB global for the ordinary annotation rules. The definition
now explicitly uses extern, preserving its const type, five initializers,
20 raw table bytes and all complete function code. The table gains one public
from MainMenuStates.obj and one complete 20-byte PDB array type. No separate
20-byte PDB section contribution is claimed. See
[the source and table review](season-name-linkage.md).

Independent original review checks all five pointers and complete strings,
the indexed table PUSH in the 861-byte score-name drawing owner, and the fixed
58.0f ADDSS read. The complete 104-byte unsigned-division owner from pinned
LIBCMT equals the original raw bytes; its three original CALL witnesses occur
inside the complete 698-byte player-data drawing owner. Table data and runtime
helpers receive no additional primary credit. Admission and normalization
rules remain unchanged.

Both complete source callers pass, adding **1,559 exact primary bytes**.
Canonical replay reports **835 exact, 65 mismatch and 315 incomplete**,
covering 152,002 exact primary bytes and 900 units. All 833 previous exact
results, 65 complete mismatches and 898 previous units remain retained.
All **246 controls across eleven suites** pass, including seven relevant
PDB-type controls. Existing numeric/runtime mutations cover the new literal
and both complete division extents.

The retained source declaration is freshly built incrementally. All 1,719
complete linked owner entries/extents/raw hashes remain identical to baseline;
current artifact hashes and all 192 dependency stamps validate. No clean build
or archived-output substitution occurs. Original/caller/table evidence is
`.analysis/season-name-original-review.json`,
`.analysis/season-menu-player-original-scope.json`,
`.analysis/season-menu-division-review.json`,
`.analysis/season-name-caller-scopes.json` and
`.analysis/season-name-linkage-check.json`. Canonical/regression/control
evidence is `.analysis/season-name-full-audit.log`,
`.analysis/season-name-regression-check.json` and
`.analysis/season-name-controls-summary.json`. Source-origin review remains
open; Factory acceptance remains unsubmitted and nothing is published.

## Replay format declarations and complete pause entries

The two existing readonly replay format arrays now have explicit external
linkage, consistent with their maintained GLOBAL annotations. Each has a
unique source-qualified public and complete 16/4-byte named PDB global type.
Neither is a standalone physical PDB contribution. All five full strings
match the original and every candidate table-pointer relocation is checked;
candidate bytes remain unchanged. No verifier or compiler profile changes.

The complete original replay drawing entry is 1,500 bytes / 375 reachable
instructions, followed by four INT3 bytes. Resolving its seven format fields
reveals a complete 1,500/1,501 extent refusal. A direct bool cast retains
1,501; a used replay-kind local gives 1,509 and changes 1,229 linked owner
records. Both are rejected. Full original/candidate bytes, fields, relocations
and every changed owner are retained. The function source is restored and
freshly rebuilt, preserving only the two declaration changes. All 1,719 linked
owner entries/extents/raw hashes and 192 dependency stamps validate.

A fixed original PUSH at `0x0043F186` selects the six-byte NUL-terminated
`Pause` at `0x00492AC4`, rather than its duplicate at `0x00492ABE`.
The three original menu entry scopes are independently complete at
331/267/428 bytes. The first two source candidates pass completely, adding
598 primary exact bytes; the game-over entry retains a 428/425 extent refusal
with frame and loop-alignment differences. No artificial frame forcing occurs.

The canonical report is 837 exact, 65 mismatch and 313 incomplete among
1,215 candidates, with 152,600 primary exact bytes and 902 units. All previous
835 exact results, 65 complete mismatches and 900 units remain retained.
Sixty controls pass across reviewed linkages, strict Oracle, focused audit
and PDB types. Existing string mutation cases now include the pause label.
See [the full review](replay-format-linkage.md),
`.analysis/replay-format-regression-check.json` and
`.analysis/replay-format-pause-caller-scopes.json`. No cold build, cleanup,
archived-output substitution, Factory submission or remote publication occurs.

## Snapshot-ID local rejection and complete x87 dependencies

AnmManager::restore_snapshot has an independently complete 128-byte original:
46 reachable instructions, two returns and a contiguous next entry. Its
remaining mismatch is the protected request-ID reload preceding the enabled
flag reload. A used local copy, refreshed after critical-section acquisition,
changes the whole candidate to 122 bytes by retaining the ID in a register.
It is rejected. Only this complete linked owner changes; full original/trial
bytes, fields, relocations and receipts are retained. The source is restored
byte for byte and freshly rebuilt. All 1,719 linked owner entries/extents/raw
hashes and 192 dependency stamps validate. Do not repeat this local-copy form
or force a reload to recover the order. Evidence is
`.analysis/snapshot-id-source-trial.json` and
`.analysis/snapshot-id-restored-check.json`.

The atan2 investigation now retains complete candidate contributions of
20-byte stub code, 80-byte descriptor data, 168-byte operation code, 500-byte
shared code, 645-byte dispatcher code and 48-byte dispatcher data. Both MASM
S_GPROC32/S_END pairs partition the entire stub contribution and agree with
current native LLVM output. The descriptor's sixteen relocated pointer slots
reach both the operation producer and nonadjacent shared NaN/infinity entries.
The original dispatcher is independently complete as a 645-byte aggregate of
seven inventoried scopes: all 209 instructions are reached, every direct branch
is checked and eleven following INT3 bytes are accounted for. Six fixed x87
qword reads establish the complete 48-byte original pool, equal to candidate
storage. All fourteen dispatcher fields are traced without granting bindings.

The original companion scope and external callee/field roles remain open;
no __CIatan2 identity or generic interior rule is added. The research parser
still refuses the other modules' unsupported record shapes and remains outside
the Oracle. See [the full dependency review](atan2-runtime-dependencies.md).
Current source/report freshness is regenerated after restoration, retaining
all 1,215 function outcomes and all 902 unit definitions. Counts remain
837 exact, 65 mismatch and 313 incomplete, with 152,600 exact primary bytes.
Seventeen strict-Oracle/focused-audit controls pass. No exact credit, cold
build, cleanup, archived-output substitution, Factory submission or remote
publication occurs. Regression evidence is
`.analysis/snapshot-atan2-regression-check.json`.

## Loader failure identity and rejected wrap bounds context

The complete original 23-byte loader-failure message at `0x00491C64` is selected
by the fixed PUSH at `0x00407CFE` in AsciiInf::initialize. Seven original copies
have identical payloads; all seven independently reviewed callers actually
PUSH the selected address. The candidate has one source-qualified MSVC public
and a complete 23-byte PDB contribution. Existing string rules validate the
whole NUL-terminated payload and witness. The mutation table now also checks
this string's interior/wrong witness, duplicate original storage, missing NUL,
shortened contribution and ambiguous contribution refusals. No verifier changes.

Five complete source owners pass: ASCII initialization (326), GUI initialization
(258), stage-file loading (337), shared-ANM loading (60) and title initialization
(165). These add 1,146 primary exact bytes. Ending initialization and ECL include
loading retain two/one unresolved fields. All seven original scopes are fully
decoded, reachable and bounded independently of candidate artifacts.

The Bullet wrap owner at `0x00415D80` is independently complete at 519 bytes
and 124 reachable instructions, followed by nine INT3 bytes. A used half-width,
height and derived width context leaves the same 515/519 result and all 1,719
complete linked owner entries/extents/raw hashes unchanged. It is rejected.
The earlier named horizontal predicate remains excluded too. Source is restored
byte for byte and freshly rebuilt; all 192 dependency stamps validate.

Canonical replay reports 842 exact, 65 mismatch and 308 incomplete among
1,215 candidates, with 153,746 exact primary bytes and 907 units. All previous
837 exact results, 65 complete mismatches and 902 unit definitions remain
retained. Fifty-three reviewed-linkage, strict-Oracle and focused-audit controls
pass. See [the full review](loader-error-identities.md),
`.analysis/loader-error-regression-check.json` and
`.analysis/bullet-wrap-bounds-source-trial.json`. No game source change,
primary literal credit, cold build, cleanup, archived-output substitution,
Factory submission or remote publication is retained.
