# Reference repair evidence

This work uses the original Japanese TH16 v1.00a target pinned in
`config/target.toml`. The upstream checkout remains unchanged. All comparison
results come from the local Factory/TH10-style Oracle.

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
described at the end of this note.

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
