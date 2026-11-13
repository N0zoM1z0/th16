# Boss counter layout and complete stage-fog source trials

Starting checkpoint: `4e01372`, PDB age 515. Two Boss counter-layout forms
and seven complete stage-fog forms are rejected and restored. **No new exact
credit or game-source change is retained.** No game runtime, native fixture,
emulation, cold build, compiler-option change or Oracle exception is used.

## Boss statistics layout

The current reconstructed source accesses `damage_this_frame[2]` only through
constant indices. One source hypothesis replaces it with separate direct-hit
and other-damage fields, preserving their widths, order and layout.

With conditional dialogue damage selection, the complete `EnemyData::step_logic`
is **2,195/2,207 bytes** and still exchanges raw/selected damage registers.
Manager-load, life and scaling differences remain. With the retained dialogue
`if` instead, the full 2,197-byte Boss candidate is raw-identical to baseline.

The latter layout-only form also preserves all **1,719 native owners**, all
**527,136 raw owner bytes**, every address/extent, all image base relocations
and the entire raw `.text`. This field-layout change does not address the
exact mismatch. It is restored, and is not proof of the original declaration.
Keep `.analysis/boss-statistics-layout-work/`, including both source forms,
complete Boss packets and `named-if-image-regression.json`.

## Complete original stage-fog owner

`StageInner::step_fog` at **`0x0040C4A0`** owns **2,156 original bytes**. An
independent original-only traversal reaches all **522 instructions**, with
**nine calls**, **77 branches** and one return at offset **2,155**. Its complete
SHA-256 is
`ba417e64d663cc56c5b2ec06abdf32a7941c955d8355bb355ca86b0e4b0d2f39`.
The retained candidate is **2,172 bytes** and remains incomplete.

Both baseline frames align to eight bytes and allocate `0x48` local bytes.
The discrepancy is not just a sixteen-byte padding problem:

- The wave branch reverses the X addition's floating operand order.
- Original amplitude/radius spills use `[esp+0x2C]`, while radius squared uses
  `[esp+0x28]`; the candidate exchanges those homes.
- Original disc math accumulates the X/Y squares in X's register and copies
  the radius-squared value before constructing the offset. The candidate
  accumulates into Y and copies that value after the sum.
- The original loads 255.0 inside the accepted-disc path. The candidate caches
  it across loop work, changing zero, radius, weight and color registers.

Complete packets, not address-replaced instruction shapes, remain the scope
of comparison. Equivalent arithmetic, matching frame size or a shorter body
does not grant exact credit.

| Source form | Complete candidate bytes | Finding |
| --- | ---: | --- |
| Float2 planar length squared | 2,172 | Disc differences persist; also reverses the wave Y addition |
| Early disc-factor accumulator | 2,172 | Complete raw owner identical to baseline |
| Offset output plus scalar weight result | 2,172 | Inlines; complete raw owner identical to baseline |
| Vector subtraction from the disc center | 2,172 | Complete raw owner identical to baseline |
| Branch-local Float2/Float3 with direct disc construction | 2,140 | Reduces local allocation to `0x38` and changes many instructions |
| Branch-local vectors with disc assignment | 2,156 | Full strict mismatch: 813 matching bytes despite all 56 fields binding |
| Typed drawn/undistorted buffer pointers | 2,172 | All 1,719 native owners and the entire raw `.text` remain unchanged |

The typed-buffer form replaces `void *` with `FogVertex *` and
`D3DXVECTOR3 *`, and adds corresponding casts at the unchanged allocations.
It changes no allocation count, stride or layout. Its code neutrality is
verified across every native owner, address/extent and image base relocation;
it supplies no exact reconstruction gain and is restored.

Do not repeat these forms as new hypotheses, or add volatile scalars, forced
float stores, padding or instruction normalization to exchange spill slots
or SSE registers. Keep both equal-length refusal and complete original CFG.

## Final restoration

The final incremental build is **PDB age 525**, source input
`80da752f1d593ebbb54bc5fecf92210566c8ba0ed0acb6e05ce1e4659e99259d`,
unchanged from the starting checkpoint. Full strict replay preserves all
**1,215 annotation results and diagnostics**, **893 exact / 63 mismatch /
259 incomplete**, **182,330 exact primary bytes** and all **956 units**.
All 1,719 candidate owners remain raw-identical (527,136 bytes), with unchanged
addresses/extents, image base relocations and the entire raw `.text`.
Source-origin review remains open; Factory acceptance is not submitted.

Keep `.analysis/stage-disc-fog-work/`: baseline/final, scoped-trial and typed
buffer image/receipt sets, all source snapshots/build logs, original CFG,
complete packets, `trials.json`, the focused equal-length audit, typed-buffer
regression, canonical report, progress result and final restoration regression.
All trial game-source files are restored; the incremental graph is retained.
