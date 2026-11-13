# Projectile source trials before handoff

Starting checkpoint: `fe98fb8`, PDB age 619. The user then replaced ongoing
reconstruction with documentation/storage cleanup and handoff. All trial game
source was restored byte for byte to that checkpoint. No new exact credit,
game-source change, runtime execution or emulation is retained.

| Source form | Complete finding |
| --- | --- |
| Curve squared-length operands through an ordinary inline scalar-square helper | Complete 986-byte owner remains 982 matching bytes; differences at offsets 770, 779, 787 and 791 remain |
| Bullet sound side effect through an ordinary inline helper instead of the shared goto | Complete owner grows to 5,516 bytes, including 5,280 code bytes and 1,055 instructions; original is 5,436 / 5,197 / 1,046 |
| Bullet animation-position subtraction as separate X/Y/Z assignments | Complete owner is 5,500 bytes, including 5,264 code bytes and 1,050 instructions; register/order differences remain |
| Bullet sound side effect duplicated into the two branches | Compilation finished before the task changed; saved but unreviewed, then reverted. No complete-owner conclusion is claimed |

Do not repeat the reviewed forms without a new source hypothesis. A successful
compile of the last form is not comparison evidence. Source snapshots and all
five linked artifacts for each trial remain directly accessible under
`.analysis/projectile-ex-source-work/`; `HANDOFF_DISPOSITION.md` labels the
interrupted trial explicitly.

The final incremental restoration is PDB age **624**. Its isolated canonical
audit retains **904 exact / 67 mismatch / 244 incomplete**, **185,816 exact
primary bytes** and all **971 unit definitions**. `handoff-regression.py`,
`handoff-regression.log` and `final-regression.json` independently establish:

- All 1,215 annotation results and diagnostics are unchanged from PDB 619.
- All 1,719 source-qualified native owners, their 527,136 raw bytes,
  addresses/extents, image-base relocations and complete raw `.text` are unchanged.
- Source input remains
  `ef45258398eb6fe5c3cb4fd560aed06455b5f5695cfb4d398602eb739e51ccc5`.
- Source-origin review remains open; Factory acceptance remains unsubmitted.

The restoration build/audit completed before the archive-helper edits. No cold
build or reconstruction experiment was run for the subsequent prose/storage
cleanup. Keep the current incremental graph and the PDB 619/624 artifact sets.
