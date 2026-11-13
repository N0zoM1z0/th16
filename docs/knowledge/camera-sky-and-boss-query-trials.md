# Complete camera-sky and Boss query source trials

Starting checkpoint: `1048422`, PDB age 525. Eight camera-sky forms and three
Boss damage-query forms are rejected and restored. **No new exact credit or
game-source change is retained.** All comparisons are static; no game runtime,
native fixture or emulation is used. Compiler options, Oracle rules and existing
inline/safebuffers qualifications are unchanged.

## Complete original camera-sky owner

`InterpCameraSky::step` at **`0x0040CD10`** owns **1,623 original bytes**.
An independent original-only CFG traversal reaches all **408 instructions**,
with six calls, 23 branches and returns at offsets 319, 353 and 1,620.
The complete original SHA-256 is
`52f687ca1f3101baea26c5e628a496da22b5d382d24bfa888ac822dcba319bba`.
The baseline candidate owns **1,630 bytes** and remains incomplete.

The original allocates `0xC8` local bytes and saves EBX, ESI and EDI at entry.
EBX is saved/restored without another explicit use in this owner. The candidate
allocates `0xC4`, retains the hidden result pointer in EBX and saves ESI later.
The original reloads the result pointer at each return. Neither a four-byte
frame difference nor an unused saved register justifies source padding.

The arithmetic differs as well. In the general easing path, the original
computes float color differences after the packed-color loop, then reuses six
scalar weighted values for the float and byte outputs. The baseline materializes
the float differences earlier, uses a packed `MULPS` for four values, and
repeats color products in its byte-output loop. Method 8 also has different
multiply operand order. Removing `MULPS` alone does not recover the owner.

| Source form | Complete candidate bytes | Finding |
| --- | ---: | --- |
| D3DXVECTOR4 color-components member | 1,630 | Packed multiply remains; changes timer scheduling; only this owner changes among all 1,719 native owners |
| Coefficient-first CameraSky multiplication | 1,630 | Complete raw step remains identical to baseline |
| Shared scalar products in general easing | 1,635 | Removes packed multiply but retains a four-color loop and wrong frame/return flow |
| Explicit float/byte product pairs | 1,679 | Wrong difference lifetime and additional stack accesses |
| Multiplication scalar passed by const reference | 1,630 | Complete raw step remains identical to baseline |
| Typed member-pointer call from StageInner::run_std | 1,630 | All native owners and the entire raw .text remain unchanged |
| Packed difference before float difference, explicit product pairs | 1,635 | Complete strict comparison refuses the different owner extent |
| Same difference order with the original composed expression | 1,677 | Removes packed multiply; frame, return and arithmetic sequence still differ |

The member-pointer trial also preserves all addresses/extents and image base
relocations. Its complete caller is raw-identical. It provides no evidence for
a missing code-generation context. The const-reference trial similarly does
not explain the original frame size. CameraSky's existing exact constructor
and addition operator are retained unchanged after restoration. No original
C++ declaration is inferred from these failed alternatives.

Keep `.analysis/camera-sky-exact-work/`: original CFG, complete original and
candidate packets, all eight source snapshots/build logs, baseline/final and
selected trial image sets, focused strict refusal, member-context regression
and full restoration regression. Address-replaced instruction diffs are
diagnostic only and carry no exact acceptance authority.

## Boss damage-query boundaries

The complete **2,207-byte** `EnemyData::step_logic` at **`0x0041C330`** has
534 reachable original instructions. Its retained **2,197-byte** candidate
still exchanges raw damage in ESI and selected damage in EBX, loads the
statistics manager too early, and does not preserve the original life pointer
and damage registers. The previously recovered flag TEST widths are retained.

All three new trials move only Player query work into ordinary inline helpers
and use conditional dialogue-damage selection. Multiplication, callback,
pending damage, statistics and life handling remain in the caller.

| Source form | Complete candidate bytes | Finding |
| --- | ---: | --- |
| One circle/rectangle helper shared by both query modes | 2,027 | Adds out-of-line calls and changes frame alignment; damage registers still exchanged |
| Separate circle and rectangle helpers | 2,167 | The normal rectangle query remains out of line; frame and damage registers still wrong |
| One normal-damage helper with fixed mode zero | 2,131 | Still outlined despite its single source call site; adds an unbound linked call |

The final trial's extra call is at candidate offset `0x250`, targeting
`0x00428FA0`. Static decoding of that target shows the mode-zero circle/rectangle
query branches. The full strict diagnostic reports one linked field without an
independent symbol/addend binding. Its shorter extent and changed registers
also fail the complete original owner. No forced-inlining attribute, new binding
or Oracle exception is introduced to retain the helper.

Keep `.analysis/boss-query-result-work/`: baseline and last-trial image sets,
all three source snapshots/build logs, complete Boss packets, the static
outlined-query excerpt and final focused refusal. These helpers are rejected
source hypotheses, not partial exact results.

## Read-only Float2 inspection

`.analysis/float2-time-result-work/` contains a baseline and complete static
packets only. No Float2 source trial was built. Both Float2 step owners retain
their 757-byte extent; the first difference is in Bezier scheduling at offset
453, after their matching timer prefix. The successful Float3 timer helper
therefore supplies no direct evidence for another Float2 timer rewrite.

## Final restoration

The final incremental build is **PDB age 537**, source input
`80da752f1d593ebbb54bc5fecf92210566c8ba0ed0acb6e05ce1e4659e99259d`,
unchanged from the starting checkpoint. Full strict replay preserves all
**1,215 annotation results and diagnostics**, **893 exact / 63 mismatch /
259 incomplete**, **182,330 exact primary bytes**, and all **956 unit definitions**.
All **1,719 native owners** remain raw-identical (**527,136 bytes**), including
every address/extent, all image base relocations and the entire raw `.text`.
All trial game source is restored. Source-origin review remains open; Factory
acceptance is not submitted. Preserve the incremental build graph and ignored
evidence. No contents are pushed or published.
