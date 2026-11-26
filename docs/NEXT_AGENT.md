# TH16 next-agent handoff

Updated 2026-11-26 after the user requested cleanup and handoff. The previous
unattended reconstruction goal was cleared. Read [AGENTS.md](../AGENTS.md)
before editing; keep checkpoints local and push only when asked.

## Retained source and checks

The retained Line EX source is the get_point repair from `4e7e4b0`.
The temporary typed explicit-goto experiment was reverted, then the source
was built incrementally. The build contains 1,166 annotated functions; preserve
`build/reference-candidate/` and its object/dependency graph.

The current focused report is
`.analysis/line-run-ex-compiler/handoff-cleanup-restored-strict.json`:

| Complete owner | Local strict result | Target / candidate bytes |
| --- | --- | ---: |
| EnemyData::step_interpolators, 0x41bb50 | pass | 1692 / 1692 |
| LaserCurveInf::on_tick, 0x4377d0 | pass | 1305 / 1305 |
| LaserCurveNode::step_back, 0x438370 | pass | 986 / 986 |
| LaserCurveInf::run_ex, 0x438cb0 | pass | 1548 / 1548 |
| LaserLineInf::get_point, 0x431050 | pass | 84 / 84 |
| laser_sincosmul, 0x43ad00 | pass | 32 / 32 |
| ZunTimer::set_value, 0x406490 | pass | 68 / 68 |
| LaserLineInf::run_ex, 0x431fe0 | incomplete | 1588 / 1592 |
| LaserLineInf::on_tick, 0x432f40 | incomplete | 1473 / 1475 |

These are local comparisons, with Factory status `not-submitted`. The shared
Factory accepted snapshot is inventory-only and contains no Oracle results.
The older 15-owner caller-context report also leaves AnmVm::run incomplete;
its switch mapping was reviewed, not closed. Earlier global ratios and pilot
totals are historical and do not describe this build.

## Resume Line EX from compiler evidence

The active incomplete owner is `LaserLineInf::run_ex`, 0x431fe0. Its target
owns 1550 code bytes, two alignment bytes and 36 table bytes. The ordinary
candidate owns 1553 code bytes, three alignment bytes and the same table sizes.
Its complete raw SHA-256 is
`29cd1e02444d8935f3ea1cf1a9efb48fefbf898ec06c6a3877541778ae85fdd5`.
The remaining aligned-code difference is the common INC/check/return block
appearing late after WAIT instead of early after SPEEDUP.

Keep the qualified `LaserLineInf::get_point` call in SHOOT, actual paired
`ex++`, saved entry index in TAG and typed BLEND field view. Private restore
snapshots are `Laser.cpp.get-point-x-repair-checkpoint` and
`Laser.cpp.before-wait-jump-trace` under `.analysis/line-run-ex-compiler/`.
Do not restore the older corrected-coordinate baseline: it has wrong X order.

Read [the Line EX compiler trace](knowledge/line-run-ex-compiler-trace.md)
before trying another source form. The useful conclusions are:

- The first threaded traversal reaches the common increment through WAIT.
  Loop recognition copies the bound check; final CodeMotion joins that copy
  to the late increment. WAIT's fall-through store rejects moving the block.
- The typed explicit-goto lifetime trace is complete. Its WAIT jump survives
  the first reorder, then `FgFlowOpts+0x49e` frees it during loop recognition
  because its destination is the immediately following block. Scope markers
  do not preserve the edge. Ordinary source already has WAIT fall-through.
- A diagnostic WAIT-preserving jump inserted at late CodeMotion enables the
  target layout. The composed compiler intervention reproduces all 1588 linked
  target bytes, but supplies no ordinary-source result.
- Caller context matters: adding one vector register to the exact Timer
  setter's known-used-register set reproduces the complete 1636-byte regression.
  Its extra INCs come from small-block copying after unconditional branches.
- Scalar next-index PHIs reach early SSA merge gates, then fail safety on an
  intervening GOTO or ADD. Selector naming and traversal order alone also fail.
  The detailed note records these controls so they need not be repeated.

The next useful question is which natural source completion graph survives
early flow cleanup while preserving WAIT semantics and the required register
and stack context. Compare the complete affected scope. A local layout gain
can change SHOOT ordering or another caller; do not judge only the INC block.

## Evidence and working commands

Current Line EX traces, scripts, source snapshots, debug images and the focused
restoration report remain in `.analysis/line-run-ex-compiler/`. Compiler evidence
for the four closed owners also remains in its corresponding `*-compiler/`
directories; see the [knowledge index](knowledge/README.md).

Old large trial payloads and their compressed copies were permanently deleted
at the user's request. They cannot be restored. Small historical notes and
remaining archives are described in [ARTIFACTS.md](ARTIFACTS.md). Dated handoffs
and older Git revisions preserve chronology, not current measurements.

```sh
git status --short --branch
scripts/repo-python scripts/build.py
scripts/repo-python scripts/audit-reference.py --address 0x431fe0 --json .analysis/line-ex-focused.json
scripts/repo-python scripts/evidence-archive.py list
```

Use incremental builds and affected complete-owner comparisons. Reserve cold
builds and broad replay for a meaningful milestone or a demonstrated dependency
problem. Prose edits need diff review only.
