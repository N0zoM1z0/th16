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

## Validation and remaining work

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
