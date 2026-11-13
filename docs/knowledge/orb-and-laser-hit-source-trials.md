# Laser endpoint operands and complete orb source trials

Starting checkpoint: `34cb7fe`, PDB age 579. The complete 1,409-byte
`sht_on_hit_laser` improves from **910 to 912 matching bytes**, still
**mismatch**. Only `src/PlayerShot.cpp` retains a source change. Fifteen other
source forms are restored. No new exact credit, game runtime, native fixture,
emulation, compiler option or Oracle rule change is involved.

## Retained endpoint expression

The spark endpoint now adds its copied start position through the existing
D3DX helper:

```cpp
D3DXVec3Add(&end, &start, &end);
```

This replaces three component assignments. In the pinned build, it recovers
the original Z addition's operand order: load the copied start Z, then add the
relative endpoint Z. X/Y code remains unchanged and still differs from the
original. The source expression itself does not guarantee a particular machine
operand order across other compiler contexts.

Exactly **two raw candidate bytes** change, at owner offsets **0x44A and
0x450** (1,098 and 1,104). They are the two memory displacements in the Z
load/add pair. Both now match the original. All other bytes in this complete
candidate, all 41 independently verified linked fields, its address, extent,
control flow and relocation footprint are unchanged. These are ordinary
instruction differences, not address normalization or masked bytes.

The original still has 336 instructions against 335 candidate instructions.
The complete function remains 912/1,409 after strict canonical and separate
unit replay. The remaining 497 differing bytes receive no exact credit.
The later Z clear remains in place; no runtime observation or general output
claim is inferred from the recovered instruction operands.

## Independent complete original scopes

Original-only dense CFG review decodes the complete spans and checks their
branches and returns. Original hashes, bytes and disassemblies are retained
under `.analysis/orb-and-laser-hit-work/`.

| Original address | Function | Bytes | Instructions | Return offsets |
| --- | --- | ---: | ---: | --- |
| `0x00410550` | `BombReimuAOrb::update` | 1,148 | 262 | 1,110; 1,147 |
| `0x00446870` | `sht_on_hit_laser` | 1,409 | 336 | 1,350; 1,385; 1,406 |

Orb update retains the object in ESI instead of EDI, schedules radial work
inside the start-position copy, and differs in the timer's final register and
store sequence. Its complete retained candidate remains 959/1,148.

Laser hit still lacks the original early position-pointer reload, has different
source-pointer and floating-local stack slots, uses different multiplication
destinations/conversion instructions, and differs in rectangle and spark setup.
Matching the endpoint pair does not close any of these other differences.

## Rejected source forms

All rows below are restored. Equal extents do not grant exactness.

| Complete owner and source form | Candidate bytes | Outcome |
| --- | ---: | --- |
| Orb: local reference to its PosVel member | 1,136 | Keeps separate motion/object bases and changes the complete owner |
| Orb: ordinary fastcall function with explicit orb parameter and matching caller pointer type | 1,148 | Same 959 matching bytes; caller remains 937/1,145 |
| Orb: current-frame snapshot before the predicate | 1,148 | Same 959 matching bytes |
| Orb: start-position writes through the existing motion.velocity view | 1,148 | Same 959 matching bytes |
| Orb: ordinary memcpy for the two start-position copies | 1,148 | Same 959 matching bytes |
| Orb: D3DXVec3Subtract for per-frame displacement | 1,145 | Complete original extent remains 1,148; refused |
| Laser hit: Float2 rotation-result helper | 1,383 | Shrinks frame to 0x40 and changes the complete owner; refused |
| Laser hit: typed pointer parameters throughout the hit callback API | 1,409 | Same 910 matching bytes; all native code unchanged |
| Laser hit: four named rotation products | 1,409 | Same 910 matching bytes |
| Laser hit: damage-source references in both branches | 1,409 | Same 910 matching bytes |
| Laser hit: accumulated rotation products | 1,409 | Same 910 matching bytes |
| Laser hit: position/size aliases declared after interrupt setup | 1,409 | Same 910 matching bytes |
| Laser hit: displacement reads before damage-source lookup | 1,407 | Recovers the early pointer reload, but moves actual coordinate reads before source lookup and changes registers/layout; refused |
| Laser hit: whole-vector result assignment for the endpoint | 1,414 | Complete extent refused |
| Curve reverse step: sqrtf instead of the explicit double-sqrt conversion | 986 | Same 982/986; all four square-register differences remain |

The callback typing trial updates both callback types, all eight definitions
and declarations, and their dispatcher call consistently. It uses ordinary
Float3 pointers and removes the integer address casts. The source-qualified
static regression proves that all **1,719 complete owners (527,136 bytes)**,
addresses/extents, all image base relocations and raw `.text` remain unchanged;
only eight function signatures are renamed. It provides no evidence that the
original source used those signatures and adds no exact progress, so the
three-file API change is restored. Keep `.analysis/shot-hit-pointer-work/` and
its complete `typed-callbacks-native-regression.json` rather than repeating it
as a new code-generation hypothesis.

The first explicit-orb-function compilation missed the qualification of
`anm_id` and failed. The missing member qualification is corrected before the
successful trial; the failed compiler log is retained separately. No output
from that failed build is used for comparison. The final orb API and body
are restored to the original maintained method.

The curve trial is retained as evidence in
`.analysis/curve-sqrt-interface-work/`; its complete packets are also present
under the new `sqrtf-interface` tag in `.analysis/curve-square-result-work/`.
The curve's four-byte mismatch and original boundaries remain unchanged.

## Complete static regression

The final canonical report remains **903 exact / 67 mismatch / 245 incomplete**,
**185,784 exact primary bytes** and **970 comparison units**. All 903 previous
exact results and every unit definition are preserved. The only annotation
change is the laser-hit matched-byte count; all other **1,214 annotation
results and diagnostics** are unchanged, excluding current image/PDB identities.

All other **1,718 complete native owners (525,727 bytes)** remain raw-identical,
including both orb functions, Boss logic, the large ECL/ANM interpreters and
curve motion. All candidate addresses/extents and every base relocation are
unchanged. The entire raw `.text` differs only at the two operand bytes above.
The complete laser-hit difference set strictly decreases; no new differing
byte is introduced. The final candidate equals the first improved endpoint
candidate over the entire 1,409-byte owner.

Final incremental build: **PDB age 591**, source input
`ef45258398eb6fe5c3cb4fd560aed06455b5f5695cfb4d398602eb739e51ccc5`.
The focused and canonical strict reports, separate complete-unit replay,
full regression and current progress check agree. The unit replay deliberately
returns mismatch, not exact. Source-origin review stays open; Factory acceptance
is not submitted.

Preserve `.analysis/orb-and-laser-hit-work/`: original CFGs, baseline/final
five-artifact images, all complete packets, source snapshots and build logs,
trial images, `end-vector-byte-diagnostic.json`, `standalone-hit.json`, canonical
reports, `progress.json` and `final-regression.json`. Preserve the pointer-API
and curve trial directories and the current incremental build graph. No local
outputs are cleaned and nothing is pushed or published.
