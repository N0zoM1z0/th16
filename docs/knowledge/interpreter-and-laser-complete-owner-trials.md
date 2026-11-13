# Complete interpreter, laser and menu source trials

Starting checkpoint: `e5c5bd9`, PDB age 537. Three laser forms, two menu forms
and fourteen animation-interpreter forms are rejected and restored. **No new
exact credit or game-source change is retained.** This work uses static PE/PDB,
compiler and complete-owner comparisons only. No game runtime, native fixture,
emulation, cold build, new compiler qualification or Oracle exception is used.

## Straight-laser rectangle cancellation

`LaserLineInf::cancel_as_bomb_rectangle` at **`0x00433860`** owns **1,968
original bytes**. Original-only traversal reaches all **451 instructions**,
with 17 calls, 44 branches and returns at offsets 84, 1,084, 1,471 and 1,965.
Its complete SHA-256 is
`ebe7d80be786823031f6f3afe71d041ffee5bfd49e50b5ef3b078f4e3245c369`.

The original copies the center and size **pointers**, not their Float3 values,
to stack homes near entry. It retains the laser in ESI and a zero/iteration
value in EDI. Baseline keeps the center in ESI and the laser in EDI. Both
allocate `0x4D8` local bytes and retain their security-cookie paths.
Rotation products, sample-coordinate spills and item/effect setup also differ.
The complete function includes hit sampling and reconstruction of surviving
laser segments; the entry discrepancy is not its only mismatch.

| Source form | Complete candidate bytes | Finding |
| --- | ---: | --- |
| Baseline | 2,031 | Complete owner differs |
| Declare rotated X before Y | 2,031 | Changes scheduling without recovering the owner |
| Float2 rotated sample position | 1,999 | Changes spills and registers; still differs throughout |
| Ordinary inline rotation-result helper | 1,999 | Inlines; complete raw owner identical to the Float2 form |

The focused strict diagnostic refuses the complete different extent. Keep
`.analysis/laser-rectangle-copy-work/`: original CFG, source snapshots, all
complete packets/build logs, baseline and last-trial images and strict refusal.
No pointer-copy or register-allocation theory is promoted to an original
source declaration.

## Complete options-cursor owner

`TitleInf::update_options_cursor` at **`0x0044C8C0`** owns **5,034 original
bytes**. All **1,369 instructions** are reachable, with 140 calls, 295 branches
and returns at offsets 1,824 and 5,033. Its SHA-256 is
`5127946cc8fcd57f6a3a97124e009843ebc766d3c0ebe0186d2c68e10a78a5db`.

The complete baseline remains 5,033/5,034: original local allocation is
`0x0C`, candidate `0x08`. Changing the existing inline child lookup's if/else
to a conditional pointer result leaves the complete raw owner unchanged.
Initializing the result from the first lookup instead produces a **4,641-byte**
owner with broader control-flow changes. Both forms are restored. No dead
local, padding, alignment constraint or one-byte exception is added.
Keep `.analysis/menu-search-result-work/`, including full original CFG,
both source forms, complete packets and baseline/last-trial images.

## Main animation interpreter

The already independently bounded `AnmVm::run` at **`0x0045F980`** owns
**14,177 original bytes**: 13,109 code bytes, alignment and both complete
dispatch tables/maps. Its complete SHA-256 is
`e61c159d14ce1de65dc7d2a21c23dfd39e0c9118a180d57466c949b3226d1c58`.
The original code has 3,223 instructions. Baseline owns **14,141 bytes**,
including 13,076 code bytes and 3,216 instructions. The full 215-byte and
313-byte maps and all 53/81 target entries remain comparison scope. See
[independent compound scopes](compound-owner-scopes.md).

| Source form | Complete candidate bytes | Finding |
| --- | ---: | --- |
| Direct float assignment in three result cases | 14,197 | Resolves destinations earlier and changes x87 stores |
| Explicit local float results | 14,141 | Still has store/tail-join differences |
| Separate deletion/static return arms | 14,125 | Moves exit blocks and retains a different complete layout |
| Conditional integer destination pointers | 14,205 | Expands branches instead of recovering EAX destinations |
| Double fmod intermediates | 14,189 | Adds conversion/register differences |
| Stage radius, angle and Y destination | 14,137 | Recovers Y lifetime; X mask/register order still differs |
| Stage both circle destinations | 14,137 | Recovers circle sequence but changes later camera operands |
| Circle staging plus accumulating lerp | 14,141 | Introduces x87 multiplication and shrinks frame to `0x10C` |
| Circle staging plus boolean deletion result | 14,145 | Changes callback/exit joins and return register |
| Reverse D3DX camera-add arguments | 14,137 | Complete raw owner unchanged from both-pointer form |
| Two scalar camera-component forms | 14,137 each | Do not preserve all original component operand orders |
| Declare circle output pointers before inputs | 14,137 | Does not prevent camera regression |
| Vector camera compound update | 14,137 | Does not prevent camera regression |

The native circle-position case has **146 bytes**; baseline has 150.
Explicit radius/angle reads followed by Y then X destination resolution
recover its 146-byte instruction sequence and five-call order. The case also
has one constant reference. It is **not** a comparison unit or an exact result.

The complete-owner regression detects an additional change outside this case:
camera-follow Y switches from field-first to global-first addition, and Z
switches the other way. Original X/Y load the entity coordinate first; original
Z loads the camera delta first. These are real floating operand differences,
not relocations. The independent code-outside-case check refuses them; its
scope is not narrowed to excuse the change. Reversing vector arguments,
scalar component expressions, declaration order and vector compound update
do not retain both the circle recovery and the other original instructions.
The entire source trial is therefore restored, including the proposed TODO
update. Do not repeat these forms as new hypotheses.

The frozen circle-first full strict audit still reports six unbound fields:
two calls each to `__CIfmod`, `__libm_sse2_acos_precise` and
`__libm_sse2_atan_precise`. No binding is invented. Complete extent, integer
destination registers, floating stores/tail sharing, random-radius math,
world-freeze branch direction and the static-script return join also remain
open. Missing-field refusal is not the only reason this owner cannot pass.

Keep `.analysis/anm-interpreter-results-work/`: all source forms/build logs,
complete code/data/relocation packets, trial index, baseline, circle-first,
last-trial and restored images, focused/canonical diagnostics, the failed
partial-retention regression and code-outside-case refusal logs. The old
`final-focused-audit` is the abandoned circle-first diagnostic; the restored
canonical report and restoration regression are authoritative.

## Final restoration

Final incremental **PDB age 558**, source input
`80da752f1d593ebbb54bc5fecf92210566c8ba0ed0acb6e05ce1e4659e99259d`,
matches the starting source. All **1,215 annotation results and diagnostics**,
**893 exact / 63 mismatch / 259 incomplete**, **182,330 exact primary bytes**
and all **956 unit definitions** are preserved. All **1,719 native owners**
remain raw-identical (**527,136 bytes**), with unchanged addresses/extents,
all image base relocations and the entire raw `.text`. The restored strict
audit, progress check and `final-regression.json` pass. Source-origin review
remains open; Factory acceptance is not submitted. The incremental graph and
ignored evidence are retained. Nothing is pushed or published.
