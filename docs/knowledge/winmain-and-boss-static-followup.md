# Complete WinMain and Boss source-context trials

Starting checkpoint: `5f3d25c`. Ten WinMain forms and one Boss form are
rejected and restored. There is **no new exact credit** and no retained game
source change. All work uses incremental compilation and static PE/PDB/target
inspection; no game runtime, native fixture or emulation is used.

## WinMain ownership and data flow

The complete original `_WinMain@16` at `0x00459830` owns **2,919 bytes**.
Independent traversal reaches all **725 instructions**, with 127 calls,
81 branches and one return at offset 2,916. Its complete SHA-256 is
`2401bd15572213d5fbf8c5620ebd8fcf64f82e742b9306027e950c3eaca3166a`.
The retained candidate also owns 2,919 bytes, but the strict baseline reports
only **900 matching bytes**, not 900 differing bytes as an older repair note
states. Equal extents do not make this a small byte-repair problem.

The original caches `PeekMessageA` in EDI across its main message loop. The
baseline calls the IAT directly and uses EDI for other values. An explicit
local API pointer is propagated away and leaves the complete candidate raw
identical to baseline.

A separate, concrete source difference occurs during fullscreen mode changes:
the original reads resolution X/Y before calling `SetWindowLongA`. Saving
both values in ordinary locals before that call restores those reads and
also recovers the original imported-function caching and many register and
alignment choices elsewhere. It nevertheless produces a **2,935-byte**
candidate. This data-flow observation is useful diagnostic evidence, not an
accepted reconstruction.

| Source form | Complete candidate bytes | Finding |
| --- | ---: | --- |
| Cached message API | 2,919 | Entire raw owner identical to baseline |
| Fullscreen width/height snapshots | 2,935 | Import caching recovered; status joins and input allocation still differ |
| Frame-return helper, separate result locals, input-exchange helper, conditional frame expression | 2,935 each | All four complete owners raw-identical to the snapshot trial |
| Assignment predicates plus ordinary previous/current input writes | 2,935 | Original input load/store/register sequence recovered; status joins still differ |
| Boolean frame helper with status output, startup-state aggregate | 2,935 each | Both complete owners raw-identical to the preceding combined trial |
| Initialization status switch | 2,935 | Reorders zero/-1 tests; status registers and frame joins still fail |

The combined input/predicate form has seven unequal instruction-shape groups.
The original copies initialization and frame results into ECX and writes the
shared stack result at the common frame-call join. The candidate uses ESI and
duplicates result writes in the three frame-call arms. Loop padding also
differs. Shape comparison replaces addresses only for diagnosis; it does not
prove linked identities or grant credit to matching subranges.

The unchanged EH reviewer refuses the 2,935-byte trial because its synthetic
registry-deleting entry requires a complete 2,919-byte WinMain producer. Keep
that refusal. Diagnostic packets read the entire independently identified
PDB contribution without constructing an Oracle Context; they are not an
alternative acceptance path. No boundary, reviewer, compiler option, padding,
barrier or register constraint is changed.

## Boss dialogue and statistics selection

The previously prepared conditional-selection variant is now actually built:
an ordinary inline overkill-credit helper is combined with conditional
dialogue damage selection. The complete `EnemyData::step_logic` at
`0x0041C330` becomes **2,183 bytes** against **2,207 original bytes** and fails
the focused strict audit.

CMOVE reappears, but raw and selected damage still occupy each other's
registers. The helper also merges the two original shot-statistics additions
at offsets `0x338` and `0x347` into one candidate addition. Life and collision
allocation remain different. This confirms the previously built scalar-credit
trial's failure; combining it with conditional selection is not a solution.
The helper and both trial source changes are restored.

## Restoration and evidence

The final full strict replay preserves all **1,215 annotation results and
diagnostics**, **892 exact / 64 mismatch / 259 incomplete**, **181,107 exact
primary bytes**, and all **956 unit definitions and addresses**. Complete
PE/PDB regression preserves all **1,719 native owners**, **527,136 raw owner
bytes**, all addresses/extents, all image base relocations and the entire raw
`.text`. Source input remains
`326e30f1f12bd961bebf860a20069050474879caa1d4526c49690076d945d317`;
the final incremental build is **PDB age 504**. Source-origin review remains
open and Factory acceptance is not submitted.

Preserve `.analysis/winmain-static-work/`: baseline/final and last-trial image
sets, source snapshots, complete target/candidate packets, original CFG,
`trials.json`, build logs, EH refusal, canonical reports and restoration
regression. Preserve `.analysis/boss-selection-followup-work/`: source
snapshots, complete 2,207/2,183-byte packets, focused audit, diagnostic diff
and the trial image/receipt. The current incremental build graph is retained.
