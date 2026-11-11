# Further sincos scopes and laser angle trials

The 2026-11-11 batch reviews eight more complete private helpers using the
existing strict `x87-sincos-scale-v1` profile. Full replay has **788 exact,
61 mismatch and 366 incomplete** candidates, covering 125,979 exact primary
bytes. All 779 preceding exact results and 837 previous comparison units remain
unchanged. Nine new exact owners add 897 bytes, and three formerly incomplete
owners now have complete mismatch units. There are 849 complete units.

## Eight original helper entries

| Original entry | Proposed helper | Producer | Original parent / call |
| --- | --- | --- | --- |
| `0x00406CC0` | jagged_line_sincosmul | AnmVmCallbacks.cpp | `0x00406690` / `0x00406719` |
| `0x0040F570` | cirno_sincosmul | BombMain.cpp | `0x0040F240` / `0x0040F385` |
| `0x00410130` | marisa_sincosmul | BombMain.cpp | `0x0040FB00` / `0x0040FC76` |
| `0x004173A0` | bullet_sincosmul_2 | BulletManager.cpp | `0x004162D0` / `0x0041642E` |
| `0x00430DF0` | item_sincosmul | Item.cpp | `0x0042F4E0` / `0x0042FC95` |
| `0x004476B0` | player_sincosmul | PlayerShot.cpp | `0x00446260` / `0x00446642` |
| `0x00469E00` | primitive_sincosmul | AnmPrimitives.cpp | `0x00469640` / `0x00469705` |
| `0x0046A350` | fan_sincosmul | AnmRender.cpp | `0x00469E20` / `0x00469F71` |

Each original owner is independently decoded from its call-established entry
through `ret 8`: one dense 32-byte linear path, no branch or call, no competing
owner, and only INT3 padding to the next independent entry. Every byte agrees
with the previously reviewed sincos/scale behavior: the first stack float is
the angle, the second is the radius, and ECX points to the output X/Y fields.
The Z field remains untouched. Candidate artifacts do not define these scopes.

Each parent has a retained trap-free path from its original inventory entry
to the witness, following direct branches and ordinary call continuations.
Full parent bytes, disassembly, hashes, paths, callee bytes and padding are in
`.analysis/additional-sincos-original-scopes.json`. The earlier broad scan in
`.analysis/remaining-sincos-original-discovery.json` is discovery evidence only.
No unreviewed indirect jump is traversed to reach a witness.

All eight candidate identities separately require their exact source-qualified
private MAP names, unique whole same-start 32-byte PDB contributions and full
producer object/module paths. Complete candidate bytes, absence of linked
fields and crossing/extra relocations, annotation identity and original witness
identity remain mandatory. The existing verifier implementation is unchanged.
Eight explicit records extend `config/static-functions.toml` to eleven reviewed
helpers. The test's positive inventory follows those explicit records and
compares every complete primary owner. Public symbols are not manufactured.
See [the original profile review](static-sincos-ownership.md) for the contract.

The ellipse helper has a different body and is excluded. The AnmVmRun XY and
ordinary helpers, and the two ECL helpers, still need original dispatch/path
review; their address annotations alone do not establish witness reachability.
No new assembly, emitted bytes or comparison exceptions are introduced.

## New complete comparisons

All eight 32-byte helpers pass, adding 256 primary bytes. The complete 641-byte
`anm_fan_init` at `0x00469E20` also passes once its private callee is bound.
These are the nine new exact results and 897 bytes.

Three other callers now compare over their complete scopes:

| Original entry | Owner | Complete bytes | Matching bytes |
| --- | --- | ---: | ---: |
| `0x00469640` | AnmManager::draw_circle | 588 | 514 |
| `0x00469BD0` | AnmManager::draw_ring | 558 | 428 |
| `0x0046A0B0` | anm_on_tick_fan | 639 | 583 |

They remain mismatches and receive no exact credit. Three further callers
expose genuine original/candidate extent differences after field resolution.
The remaining incomplete groups are 198 unresolved-field cases, 131 extent
differences, 29 missing same-start contributions, six producer differences
and two unreviewed dispatch/owned-data cases.

## Rejected natural laser source contexts

The original 412-byte LaserLine/LaserCurve angle steps each differ from the
baseline candidate in 11 bytes. The operation at +`0x33` is a memory increment
of the completed-round counter, not an argument push. The original loads the
next length before the increment, then stores length and angle; the candidate
increments first. This is instruction scheduling within the same complete
owner, not a relocation or unbound-callee difference.

The first trial folds the counter increment into the completion test after
resetting the turn timer. It expresses the same round-completion decision
without forced accesses or barriers, but retains the increment later than the
original and expands both full comparisons from 11 to 91 differing bytes.
Both owners remain 412 bytes, with only 321 matching bytes. This source context
is rejected; the baseline source is restored before the next trial.

The second trial computes the next curve length into an ordinary float local
before committing both angle and length. It changes the complete candidate
angle-acceleration owner from 323 to 315 bytes, against the 323-byte original.
The Oracle refuses the extent difference. No shortened comparison or partial
similarity result is accepted. This trial is also rejected.

Both full source/output sets remain under
`.analysis/laser-angle-{completion,next-values}-artifacts/`. Diagnostic outcomes
are in `.analysis/laser-angle-{completion,next-values}-focused.json`, and all
nine complete candidate scopes from baseline and both trials are retained in
`.analysis/laser-angle-source-trials.json`. Do not repeat these contexts or
replace them with forced ordering, spills or registers.

The complete preceding Laser.cpp is restored byte for byte and rebuilt
incrementally. The build input identity equals the baseline; PE/MAP/PDB/function
map hashes match the fresh receipt and all 192 dependency stamps are valid.
The current outputs are newly built, without archived-output substitution or
a clean build. See `.analysis/laser-angle-restored-check.json` and
`.analysis/laser-angle-restored-build.log`. Maintained game source is unchanged.

## Validation and evidence

All 38 relevant controls pass: 21 private-identity controls, 14 strict Oracle
controls and three focused-audit controls. The private suite now positively
compares all eleven complete configured owners, while retaining its byte,
extent, source/name, MAP/PDB, witness, relocation and call-boundary mutations.
The preceding six-suite milestone passed 114 controls. Verifier rules and
compiler/linker profiles are unchanged in this batch.

Full replay retains every previous exact result and every previous unit
unchanged; the report freshness check passes. Source-origin review remains
open, and Factory acceptance remains unsubmitted. Nothing is published.

Retained ignored evidence also includes
`.analysis/additional-sincos-full-audit.log`,
`.analysis/additional-sincos-regression-check.json`,
`.analysis/additional-sincos-{controls,oracle-controls,focused-controls}.log`
and `.analysis/laser-angle-baseline/`.
