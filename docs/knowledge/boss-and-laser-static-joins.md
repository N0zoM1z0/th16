# Boss result joins and line-laser EX addressing

Starting checkpoint: `df4c20e`. Four Boss source trials and seven line-laser
EX trials are restored after complete static comparison. **No new exact credit**
is claimed. No game runtime, native fixtures or instruction emulation are used.

## Boss result boundaries

An inline conditional-result helper for dialogue suppression produces CMOV
but still exchanges the raw and selected damage registers. A player-state
division/filter helper also inlines without restoring the complete original.
Larger collection and callback/pending/state helpers remain out of line,
introducing calls absent from the original. Their smaller parent extents are
not progress toward the original call topology. All four sources/build logs
and complete logic/motion packets remain in `.analysis/boss-credit-join-work/`.

## Complete laser owner and encoding difference

The independently reviewed `LaserLineInf::run_ex` at `0x00431FE0` owns **1,588
bytes**: 1,550 code bytes, two NOP alignment bytes, a five-entry/20-byte target
table and a 16-byte remap. An original-only traversal reaches all **327 code
instructions**, all five indirect destinations, 15 calls and one RET at offset
218. The code ends in a JMP to the loop, not in that early RET. The first packet
helper's terminal-RET assumption is preserved as a failed diagnostic; the
corrected helper checks the actual code and both complete tables. Owner
boundaries and production verifiers are unchanged.

The restored candidate owns **1,748 bytes**: 1,711 code bytes, one alignment
byte and the same table/remap widths. The original computes and spills a full
current-instruction pointer:

```asm
imul eax, edx, 2Ch
lea  esi, [edi+60Ch]
add  esi, eax
mov  [esp+10h], esi
```

The candidate retains the scaled array index in ESI and includes EDI plus a
32-bit displacement in each EX field address. It spills the index rather than
the full pointer. Both values are reloaded by SET_SPRITE after ESI becomes the
VM pointer. The initial index/type registers are also exchanged.

The candidate has **36 such EX memory operands**. Their hypothetical encoding
saving with short pointer accesses is **149 bytes**, against the 161-byte
code-size gap. This locates a substantial encoding cost; it does not validate
individual instruction pairing, linked target identities or exactness.

Six ordinary source forms generate the **same complete 1,748 raw bytes** as the
baseline: a pointer-result getter, local owner alias, guarded do/while, loop
breaks, base-pointer-then-index addition and a reference-output getter. The
addresses are unchanged, so these comparisons mask no fields. An explicit
default-advance arm instead produces 1,764 bytes and still misses the original
early common advance. All seven forms are restored. Basic pointer/loop syntax
does not recover the original materialized address; investigate its dataflow
and call context before repeating these forms.

## Final static restoration

All **1,719 complete candidate owners** remain raw-identical over **527,135
bytes**, with identical addresses/extents and all image relocations. The entire
**563,712-byte raw `.text` section** is identical as well. All 1,215 annotation
results/diagnostics and all 955 unit definitions/addresses are unchanged.
Canonical totals remain **890 exact, 65 mismatch, 260 incomplete** and
**175,386 exact primary bytes**. Source input is unchanged; final incremental
PDB age is **443**. Source-origin review is open; Factory is not submitted.

Keep `.analysis/laser-ex-static-work/`: complete original/candidate code and both
table packets, original CFG, encoding-cost report, rejected sources/build logs,
`TRIALS.md`, immutable baseline/final artifact sets, canonical reports and
`regression.py`/`final-regression.json`. Also keep the Boss directory above.
The latest retained source remains the Boss hit-effect expression at `df4c20e`.
