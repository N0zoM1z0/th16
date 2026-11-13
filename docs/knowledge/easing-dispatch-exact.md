# Complete easing-dispatch reconstruction

`interp_common_methods` at `0x004033F0` now passes the strict Oracle over its
complete **1,692-byte owner**, including all **131 linked fields**. This source
checkpoint starts at `046a7bf`; it changes only `src/Interp.cpp`. The shared
easing function serves scalar, angle and vector interpolation used throughout
enemy, projectile and animation movement. No game runtime or dynamic test runs.

## Retained source and original dataflow

The quadratic ease-in/out and sine ease-out/in cases now return their selected
piecewise expressions through C++ conditional expressions. Each expression
retains the original comparison, arithmetic order, constants and selected
branch. No helper, new type, attribute, register constraint or artificial
arithmetic is added.

The quadratic case puts the `0.5f` multiplication inside both conditional
operands. This restores the original false-path transfer from XMM1 back to
XMM3 before the multiplication. The former early `return` omitted that
three-byte transfer. Assigning the conditional result to `x` and multiplying
afterwards instead reloads `2.0f` and still fails the original sequence.

The sine conditional restores the original XMM1 result paths. Its second
branch converts the runtime result directly in XMM0, loads `0.5f` once into
XMM1, multiplies the sample by it and adds into the same constant register.
The former two assignment statements produce an XMM2 result, an extra XOR
and two memory-operand constant reads.

Those two old discrepancies cancel in the complete extent: both old and new
candidates own 1,692 bytes. The old table destinations differ from the reviewed
mapping, so the strict scope proof refuses it. The new source recovers every
instruction and table destination. Neither a size comparison nor a case slice
is used as exact acceptance.

## Complete scope and links

The unchanged independently reviewed switch record contains:

| Part | Bytes or count |
| --- | ---: |
| Original executable code | 1,566 bytes / 388 instructions |
| Alignment before the table | 2 bytes: `66 90` |
| Complete target table | 31 entries / 124 bytes |
| Distinct table destinations | 29 |
| Full compared owner | 1,692 bytes |
| DIR32 fields | 125 |
| REL32 fields | 6 |

An original-only traversal reaches all 388 instructions, all 34 return sites
and all six runtime call sites. Every direct branch destination and every table
target is a decoded instruction start. The four following `CC` bytes remain
outside this owner; the next independent entry is `0x00403A90`.

The complete original owner SHA-256 is
`662065b1d97e4367c33d85b4773cba2e8da96826b699e2c0807d568ce09b450c`.
Existing scope, runtime and literal identities validate all links. No original
extent, switch record, linkage binding or Oracle rule changes. The generic
decoder's `decoded_bytes` value of 1,691 includes attempted table decoding;
the independent code/table census above supplies the actual code accounting.

## Rejected source forms

Before the easing repair, complete static trials also examine the 1,592-byte
original `Bullet::on_tick`. Component goal construction gives 1,700 candidate
bytes; vector-position staging gives 1,712; expanded scalar movement gives
1,568. All retain incorrect frame, movement or shared-branch behavior.
Removing the manager's redundant link root leaves the complete 1,572-byte
baseline bullet owner unchanged. All Bullet source and root changes are restored.

For easing, shared assignments, early returns, explicit sine casts, a separate
result local and an ordinary quadratic helper all fail complete comparison.
The protected trial log records their sources, extents and packets. No failed
form receives exact credit, and the inline helper is removed.

## Static regression and checkpoint

The first exact build is PDB age **402**. PDB age **403** replaces the obsolete
upstream-percentage TODO with a source comment; its complete exact owner is
byte-identical to the first exact build.

Full strict replay changes only this function from incomplete to exact. Totals
are **890 exact, 65 mismatch and 260 incomplete**, with **175,386 exact primary
bytes and 955 units**. All previous **889 exact owners** and all **954 prior
unit definitions and addresses** remain unchanged. All other **1,718 complete
candidate owners**, totaling **525,441 bytes**, retain identical raw payloads,
addresses and extents. Image base relocations outside the changed owner also
remain identical; the strict Oracle validates the changed owner's complete
relocation fields.

The source input is
`a830aa87cb06c813b647365844fd9dd051595cd493e86eb10adef28f7e5415ef`.
Source-origin review stays open; Factory acceptance is not submitted.

Keep `.analysis/bullet-tick-exact-work/`: PDB 391 baseline, PDB 402 first-exact
and PDB 403 final PE/MAP/PDB/receipt sets; original CFG/table evidence; complete
packets; focused/full strict reports; failed source snapshots; `TRIALS.md` and
`final-regression.json`. Packet address masking is diagnostic only. The exact
claim comes from the complete strict comparison with all 131 links validated.
