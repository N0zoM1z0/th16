# Exact dialogue VM construction and position-array context

Starting checkpoint: `4087c56`, PDB age 504. The complete **1,223-byte**
`GuiMsgVm::GuiMsgVm` at `0x00429B20` is now **exact**, improving from 1,080
matching bytes. Only `Gui.cpp` and `Gui.h` retain game-source changes. No game
runtime, native fixture or emulation is used.

## Retained source and layout

The four default text positions previously had separate `Float3` member
declarations. Existing script source indexed them through
`(&side_text_pos_0)[active_side]`. They are now one ordinary member array:

```cpp
Float3 side_text_pos[4];
```

The constructor still calls the existing `set_float3` helper four times with
`(16, 0, 0)`; script accesses use `side_text_pos[active_side]`. No helper body,
timer, flag declaration, callback argument or compiler option changes.
The array occupies the same **48 bytes at `[0x15C,0x18C)`**. A new offset
assertion and the existing following-member/size assertions preserve
`ecl_resume_timer` at `0x18C`, the bubble position at `0x1B0`, and the complete
`0x1C8` object layout.

With separate members, MSVC places seven scalar state-clear stores after most
coordinate construction. With the array, the original source statement order
produces the original instruction order: next line, cleared state, four colors
and active side are cleared before the coordinate writes. The packed X/Y
stores and stack-to-Z transfers remain intact. Only **143 raw bytes** change,
all inside parent interval **`[0x3A7,0x45A)`**. There is no padding, register
constraint, added volatile access, barrier, forced inlining, cookie suppression
or Oracle exception.

This is a natural source/type organization that reproduces the complete
owner; it does not prove the original C++ declaration or spelling. In
particular, the script case sets `active_side` to zero and its native position
reads can be constant-folded. The old source indexing expression alone is not
independent proof of a general runtime array index or its bounds. The complete
script interpreter remains raw-identical and incomplete, with its existing
nine unbound fields. Source-origin review remains open.

## Complete static acceptance

Independent original-only traversal reaches all **287 instructions** in the
1,223-byte owner, with **26 calls**, **22 branches** and one return at offset
**1,220**. Its complete SHA-256 is
`37aace843463bba3c737163c51862346147fcdcec4c0e4ae613f7f0f49f1c6e2`.
No subrange or reordered-instruction equivalence receives credit.

Focused, canonical and standalone strict comparison pass every owned byte
and all **33 linked fields: 25 REL32 and eight DIR32**. All field identities,
offsets and all 956 comparison-unit definitions remain unchanged. Original
and candidate extents are both 1,223 bytes.

Canonical totals are **893 exact, 63 mismatch and 259 incomplete** among
1,215 annotations, with **182,330 exact primary bytes** and **956 units**.
All prior 892 exact results and the other 1,214 annotation results/diagnostics
are preserved, apart from current build identities. Every original boundary
and comparison address is unchanged.

All other **1,718 native owners** remain raw-identical (**525,913 bytes**),
including Boss logic, the Reimu bomb update and the dialogue interpreter.
All candidate addresses/extents, all image base relocations and every raw
`.text` byte outside this constructor are unchanged. The final constructor
is raw-identical to the first exact PDB-514 image. The final incremental
build is **PDB age 515**, source input
`80da752f1d593ebbb54bc5fecf92210566c8ba0ed0acb6e05ce1e4659e99259d`.
Factory acceptance is not submitted.

## Rejected source forms and substantial-owner follow-up

| Dialogue initialization form | Complete candidate bytes | Result |
| --- | ---: | --- |
| Explicit coordinate component stores | 1,210 | Loses packed vector/stack-to-Z construction and the original frame |
| Combined scalar/position initialization helper | 1,028 | Adds an out-of-line call absent from the original |
| Scalar-state helper only | 1,223 | Inlines but preserves the complete baseline mismatch |
| Position-state helper only | 1,097 | Adds an out-of-line call absent from the original |
| Four-element position array | 1,223 | Complete exact owner; retained |

A Boss statistics helper with direct side effects and a void result is also
rejected. Combined with conditional dialogue suppression, the complete logic
owner is **2,199/2,207 bytes**. It preserves both statistics additions but still
loads the manager too early and exchanges the damage registers. Both original
source changes are restored; see the Boss hit-effect work (Git history).

The complete **1,145-byte** `BombReimuAInf::on_tick` at `0x00410DE0` is also
reviewed: all **298 instructions** are reachable, with 19 calls, 34 branches
and returns at offsets 268, 481 and 1,144. A frame predicate, a predicate with
an explicit frame value, a shared loop index and a frame/changed-state output
helper all fail the complete owner and are restored. Every candidate remains
1,145 bytes; equal size does not resolve the timer-register, pointer-reload
and stack-slot differences. No partial exact credit is added.

Preserve `.analysis/dialogue-initialization-work/`: baseline/first-exact/final
five-artifact images, complete owner inventories and packets, original CFG,
source snapshots/build logs, focused/canonical/standalone reports and both
image regressions. Preserve `.analysis/boss-statistics-call-work/` and
`.analysis/reimu-bomb-tick-work/`, including failed source forms, complete
packets, focused reports and trial images. Keep the current incremental graph.
