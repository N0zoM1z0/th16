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

Incremental builds were used only to diagnose these changes. Final claims
require a clean build, complete independent boundaries, unique PDB owners,
exhaustive relocation fields and byte replay through `scripts/audit-reference.py`.

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
