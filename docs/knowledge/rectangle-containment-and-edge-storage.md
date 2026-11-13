# Rectangle containment and edge storage

Starting at `d77ba42`, this static reconstruction restores the first point-array
containment pass inside `collision_test_rect_rect` at `0x004049C0`. The complete
candidate changes from **2,002 to 2,155 bytes**, against **2,168 original bytes**.
It remains **incomplete**. There is no new exact owner or primary-byte credit.

## Inlined containment

The original performs eight statically expanded absolute-value conversions
for the four transformed corners. The previous candidate had two conversion
instructions in a four-iteration loop. The retained source shares the complete
point/rectangle calculation in `points_in_rect`, explicitly inlines its first
use in the rectangle/rectangle owner, and retains the second call to
`collision_test_points_in_rect` at the original call boundary.

The shared calculation includes translation, conditional rotation and four
explicit corner checks. The standalone point function calls the same inline
body. Its full 661-byte result remains 651 matching bytes, with the same ten
rotation register-encoding differences. No new standalone function annotation,
compiler profile, padding, dead local or comparison rule is added.

The complete original, baseline and retained rectangle packets all contain
three cosine calls and one out-of-line point-array call. The original and
retained containment passes each contain eight absolute-value conversions;
the baseline has two in its rolled loop. The original has 479 decoded
instructions and the retained owner has 480. These structural observations
explain the source change; they do not establish whole-function exactness.
Rotation, scratch slots and edge-intersection dataflow still differ. The
13-byte extent difference is not a count of mismatching instruction bytes.

## Complete edge table

The edge table is the complete read-only 32-byte object at `0x00490E90`:

```text
(0, 1), (1, 2), (2, 3), (3, 0)
```

Its SHA-256 is
`95853d8881732e63777cf081ef757e3a1d025544145d488f88f1a2c2a6fca008`.
It has no pointer relocation and is the only aligned occurrence of that complete
payload in the original `.rdata`. Complete CFG and byte packets for the
947-byte line/rectangle and 2,168-byte rectangle/rectangle parents retain the
fixed original table initializers, indexed reads and end comparisons.

The existing `GLOBAL` annotation now has an external const definition, giving
the candidate a unique public and a complete 32-byte typed PDB owner. Its
payload equals the original in full. The four-row/two-column representation is
inferred from the paired 32-bit reads and eight-byte row stride; the original
C++ declaration and visibility remain unproven. This storage review grants no
primary credit and adds no linkage profile or verifier exception.

The two functions now reach the strict independent-boundary refusal instead
of stopping at their first missing table bindings. Line/rectangle remains
940 candidate / 947 original bytes. Rectangle/rectangle remains 2,155 / 2,168.

## Cursor limits remain unaccepted

The captured comparison input exposes an additional role issue. Candidate
rectangle cursor limits physically coincide with `IID_IDirectSoundNotify` and
its +4 interior. Generic symbol lookup therefore describes those two fields
as GUID references. Their original roles are the edge-table limits
`0x00490EB0` and `0x00490EB4`, not GUID accesses. Those captured mappings are
**not promoted** as independent collision identities. A future exact result
must prove the iterator limits and their side exits through the complete
32-byte table; do not enlarge it to include adjacent data. The current extent
refusal prevents acceptance of either parent.

`complete-field-packets.json` records the actual unchanged-Oracle inputs:
9 fields for the point function, 16 for line/rectangle and 23 for
rectangle/rectangle. The capture wrapper records arguments and invokes the
original comparison method without modifying its result. It grants no extra
acceptance authority.

## Checkpoint

Incremental compilation, focused complete-owner comparisons, the full strict
audit and progress check preserve **886 exact / 65 mismatch / 264 incomplete**,
**170,923 exact primary bytes** and **951 units**. All prior exact functions
remain exact. Only 643 unit candidate addresses change; all other unit fields
are unchanged. Consequently 604 exact-unit hashes change because their hash
includes the candidate address. Source-origin review stays open and Factory
acceptance is not submitted. No game runtime or dynamic fixture is executed.

The source input is
`cfbea2fb7262af493ea44cc4005f42eccf2841c09b9cc83bee4cdb28c67aa7a3`;
PDB age is **356**. Preserve `.analysis/interpolation-exact-work/`, including
both full artifact sets, original table/CFG evidence, complete rectangle
packets, comparison inputs, restored source trials and
`retained-regression.json`. Its first regression helper incorrectly expected
address-dependent unit hashes to remain unchanged; that failed version/log is
retained. The corrected check verifies every prior exact result and every unit
field after accounting solely for candidate relocation.
