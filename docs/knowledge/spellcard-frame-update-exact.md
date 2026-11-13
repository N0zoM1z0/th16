# Complete spellcard frame update

Starting checkpoint: `4eb32e4`. `Spellcard::on_tick_body` at `0x00417930`
is now **exact over its complete 650-byte owner**, improving from 461 matching
bytes. This covers bonus decay, scaled frame advancement, title movement,
boss-marker smoothing and early-bomb state. No game runtime or instruction
emulation is used.

## Source and complete original evidence

A local inline helper returns fractional time and reports the integer frame
through an output reference. It retains the existing speed lookup, previous
frame write and scaled/unscaled arithmetic. The caller writes both current
fields and uses the integer result for the frame-120 predicate:

```cpp
i32 frame;
f32 frame_f = advance_spellcard_time(time, frame);
time.current = frame;
time.current_f = frame_f;
if (frame >= 120)
```

Returning only fractional time while writing integer time inside the helper
recovers the original floating sum/conversion, but leaves a memory comparison
and different loop padding: strict 493/650 mismatch. Reporting both values to
the caller recovers the original register comparison, conditional-branch
widths and both title loops. The earlier planar marker repair remains intact.
No title-loop padding is inserted in source.

The helper is source organization, not evidence of an original out-of-line
helper or its source spelling. It introduces no physical-register constraint,
dead local, intrinsic, alignment directive, compiler option or Oracle exception.
Only `src/Spellcard.cpp` retains game-source changes in this continuation.

The complete original has **167 instructions, all reachable**, three direct
calls and returns at offsets 642 and 649. Six following `CC` bytes are outside
the owner; the next independent entry is `0x00417BC0`. Original owner SHA-256:
`cd4b445630fbd8b3a56859673ab06f1b4c169c04f2e88f1c544cb71aa106023f`.
Strict comparison resolves all **17 fields: 14 DIR32 and three REL32**. The
entire owner decodes as code, with no data spans or omitted alignment bytes.

## Static acceptance and regression

The focused comparison, full canonical replay and standalone unit replay all
pass the complete owner. Canonical totals are **891 exact, 65 mismatch and
259 incomplete** among 1,215 annotations, with **176,036 exact primary bytes**
and **956 units**. All prior 890 exact owners and the other 1,214 annotation
results/diagnostics are preserved.

The existing unit refreshes seven relocation offsets to follow the recovered
instruction positions. All 17 field identities, unit boundaries and addresses
remain unchanged; the other 955 unit definitions are identical. This is a
generated position update, not a new binding, scope or comparison allowance.

All other **1,718 candidate owners** remain raw-identical (**526,486 bytes**),
with unchanged addresses/extents and all relocations outside the 650-byte
owner. Every raw `.text` byte outside that owner is unchanged. The retained
payload is raw-identical to the first exact build. Final incremental PDB age
is **476**, source input
`0b4ce2bd4813b5d00ec1b2b6195a252d17684eb07e1bb8cf2a9e2201819119ea`.
Source-origin review remains open; Factory acceptance is not submitted.

The same two-output form fails the complete `InterpFloat3::step`: 905 candidate
bytes against 906 original bytes, with different integer/speed registers,
comparison and vector arithmetic. `Interp.cpp` is restored byte for byte. Its
retained 899/906 mismatch is unchanged.

Preserve `.analysis/spellcard-timer-result-work/`: all source snapshots/build
logs, complete owner packets, original-only CFG, focused reports, standalone
replay, baseline/first-exact/final five-artifact images and final regression.
An initial focused request is refused for an unannotated extra address; use
`frame-output-verified-audit.json` for the corrected complete pair. The first
regression refuses an overbroad expectation that every unit definition stays
identical; its corrected version verifies the seven offset-only changes and
the unchanged field identities. Both refusals remain preserved.
