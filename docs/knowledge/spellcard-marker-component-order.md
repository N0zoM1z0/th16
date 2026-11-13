# Spellcard marker component order

This static reconstruction starts at `408da53`. The retained change is in
`Spellcard::on_tick_body` at `0x00417930`, which controls bonus decay, the
scaled frame timer, title movement, Boss marker smoothing and early-bomb state.
The complete function remains a **650-byte mismatch**, with **461 matching
bytes instead of 451**. There is no new exact owner or primary-byte credit.

## Retained source

The planar delta now assigns its X and Y components directly rather than
constructing and subtracting two `Float2` values. Depth remains a scalar. All
three component values are live and feed the existing 5% smoothing writes.
The marker pointer, subsequent VM lookup and marker copy are unchanged.

With the pinned compiler, this recovers the original sequence: load the Boss
X/Y/Z coordinates into XMM1/XMM2/XMM3, subtract the marker coordinates, scale
and add the marker again, then write X/Y/Z. The previous source interchanged
XMM2 and XMM3 for Y and Z. No register constraint, padding, dead arithmetic,
alignment directive, compiler profile or Oracle rule is added.

The complete strict comparison resolves all 17 linked fields. A subordinate
check of offsets `0x1C1..0x23A` verifies all 122 bytes and 17 instructions of
the marker calculation, including both linked fields through existing
identities: the 0.05f scalar and `g_AnmManager`. This range is neither a new
owner nor separately credited. Whole-function acceptance still fails.

## Remaining exact work

The original scaled timer path at offset `0xBD` loads `current_f` into XMM0,
then adds the speed held in XMM1. The candidate instead adds the memory value
to XMM1. Its shorter path shifts subsequent title-loop instructions and changes
the compiler's loop alignment. Full original and candidate packets are retained;
do not interpret the 189 differing bytes as 189 independent source defects.

A branch-local accumulator produces the same rejected timer code. Updating
the integer and floating members inside each branch instead gives 409 matching
bytes; that form is restored. The out-of-order depth declaration changes the
smoothing load/store order. A complete three-component vector recovers the
smoothing registers but introduces a cookie/frame and a 692-byte owner. Both
are restored. Historical float-frame snapshots hoist the load too early and
must not be repeated as a solution.

The Boss dialogue inversion produces a CMOV with the wrong damage registers.
A branch-local damage credit leaves the complete Boss owner unchanged at
2,195 bytes against 2,207 original bytes. Conditional-value animation position
initialization grows `step_interpolators` to 1,731 bytes against 1,692. All
three source trials are restored.

Two scalar product/result forms leave the point/rectangle collision owner's
same ten register-encoding differences; a copied planar vector grows its owner
to 677 bytes against 661. These rotation trials are also restored. The original
rectangle edge table is internal in the candidate; no public, binding or
acceptance exception is added for it.

## Verification and evidence

An incremental build, isolated complete-owner comparisons, full strict audit
and progress check preserve **886 exact / 65 mismatch / 264 incomplete**,
**170,923 exact primary bytes** and **951 units**. All preceding exact hashes
and the entire unit configuration are unchanged. Only the spellcard owner's
matching-byte result changes. Source-origin review stays open and Factory
acceptance is not submitted. No game runtime or dynamic fixture is executed.

Source input is
`8e6f8a51c048acafc5d94e82d9b66e2280b661bcdc3ca49150f22ad7c0922d24`;
PDB age is **342**. Preserve `.analysis/boss-static-work/`, including both
complete image/receipt sets, complete function packets, failed source forms,
strict reports, `TRIALS.md` and `retained-regression.json`. The first regression
helper omitted `functions.txt` from its artifact copy and refused the missing
file. Its version and failure log remain; the corrected helper verifies every
receipt-listed artifact and all existing snapshots before continuing.
