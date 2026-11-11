# Complete private sincos helper ownership

The 2026-11-11 review establishes three complete private helper identities and
uses them to compare their callers without promoting private names to publics.
Full replay reports **779 exact, 58 mismatch and 378 incomplete** candidates,
covering 125,082 exact primary bytes. All preceding 767 exact results and 820
comparison units remain unchanged. Twelve complete exact owners add 4,470
bytes; five newly comparable complete mismatches remain explicit.

## Original entry and behavior evidence

| Original entry | Complete bytes | Producer annotation | Original call witness |
| --- | ---: | --- | --- |
| `0x00406470` | 32 | AnmVmCallbacks.cpp, gather_sincosmul | gather tick entry `0x00405700`, call `0x00405775` |
| `0x00417510` | 32 | BulletManager.cpp, bullet_sincosmul | shoot_one entry `0x00412CB0`, call `0x00412F9A` |
| `0x0043AD00` | 32 | Laser.cpp, laser_sincosmul | get_point entry `0x00431050`, call `0x00431070` |

The original-only derivation follows each independently located call and a
trap-free instruction path from its original parent entry. Parent bytes,
hashes, full disassembly, witness paths and the complete callee disassembly
are retained in `.analysis/static-sincos-original-scopes.json`. Paths follow
ordinary call continuations and direct branches; no indirect jump is traversed.
They establish entry reachability without granting parent or callee execution
credit. Parent code hashes and decoded witness starts are checked again by the
maintained verifier.

Every helper has one dense linear path ending at `ret 8`, with no call or
branch, no competing original owner, and only INT3 bytes up to the next entry.
The complete original owner is derived by decoding through that return before
checking the declared 32-byte record. The three full byte sequences agree.

The helper saves the ECX destination at EBP-4, loads its first stack float at
EBP+8 and executes `fsincos`. It multiplies each result by the second stack float
at EBP+12, storing cosine times radius at destination+0 and sine times radius
at +4. Destination+8 is untouched. The full frame setup, intermediate EAX use,
restoration and stack cleanup are retained. The caller at `0x00431070` supplies
the output pointer and angle/distance operands, then adds all three position
coordinates; the complete caller comparison checks that argument flow too.

These are existing imported implementations in ZunAsm.h and their translation
unit wrappers. The review emits no machine code and changes no game source.
Local code identity does not settle source authorship or the authenticity of
the retained source/context hypotheses.

## Candidate ownership and replay

`config/static-functions.toml` opts in to exactly three qualified identities
under the explicit `x87-sincos-scale-v1` profile. Each names its original entry,
complete extent/hash, source, private mangled symbol and original caller/hash.
The source annotation must agree with the attested function map. Identical
bytes from another source or another entry do not select the identity.

`scripts/static_identity.py` uses the existing private-owner selector to require
one exact source-qualified MAP static, one same-start complete 32-byte PDB
contribution, its unique module and full producer object path. It rejects
overlapping contributions, public collisions and any interior MAP name. All
32 candidate bytes must satisfy the complete reviewed profile. The function
has complete decode coverage and no linked fields or PE relocations, including
relocations crossing either boundary. Private proof metadata and the verifier
participate in the Oracle fingerprint. The consumed original source/name
inventory fields are fingerprinted alongside its extents.

Primary comparison units explicitly name their `reviewed_static` proof.
Callers likewise opt in for an exact direct REL32 CALL with zero addend to the
qualified entry. Replay validates the candidate address, original target,
symbol, width, relocation kind and proof identity before encoding the bound
field. An interior address, local field, unconfigured helper or tail jump cannot
claim this proof. All other bytes and all affected owner extents are compared
normally. Existing public selection and unreviewed private names retain their
previous refusal behavior. The private symbols remain absent from the public
inventory; no synthetic PDB contribution is created.

This is one explicitly reviewed helper profile, not a generic approval of
private functions, arbitrary assembly, partial PDB extents or the other sincos
variants. Other source wrappers still require independent original witnesses,
complete scopes and producer ownership.

## Results

| Original entry | Complete bytes | Result |
| --- | ---: | --- |
| `0x00406470` | 32 | exact gather helper |
| `0x004153E0` | 387 | exact Bullet::step_ex_03 |
| `0x00415BB0` | 454 | exact Bullet::step_ex_06 |
| `0x00417510` | 32 | exact bullet helper |
| `0x00431050` | 84 | exact LaserLineInf::get_point |
| `0x004311F0` | 84 | exact LaserCurveInf::get_point |
| `0x00431250` | 84 | exact LaserInfiniteInf::get_point |
| `0x004312B0` | 84 | exact LaserBeamInf::get_point |
| `0x00432620` | 1,534 | exact LaserLineInf::step_ex_bounce |
| `0x00433720` | 292 | exact LaserLineInf::on_draw |
| `0x00438750` | 1,371 | exact LaserCurveInf::on_draw |
| `0x0043AD00` | 32 | exact laser helper |
| `0x00432C20` | 412 | mismatch, 401 matching bytes |
| `0x00436C70` | 633 | mismatch, 521 matching bytes |
| `0x004370A0` | 1,726 | mismatch, 1,677 matching bytes |
| `0x004392C0` | 412 | mismatch, 401 matching bytes |
| `0x00439460` | 323 | mismatch, 309 matching bytes |

The last five owners were incomplete before their callee identity was available.
Their differences receive no exact credit. Fifteen other previously unresolved
callers now report their genuine candidate/original extent differences. The
remaining incomplete groups are 205 unresolved-field cases, 128 extent
differences, 37 missing same-start contributions, six producer differences and
two unreviewed dispatch/owned-data cases.

All 837 complete units are retained. No rebuild was necessary: the attested
incremental game artifacts and source inputs are unchanged. Source-origin
review remains open and Factory acceptance remains unsubmitted.

## Controls and evidence

Twenty-one new private-identity controls include every byte of both full 32-byte
owners, truncated/expanded extents, original hashes, source/name identity,
original parent/witness identity, duplicate and interior MAP names, public
collisions, foreign PDB ownership, explicit primary selection, private caller
fields and extra/crossing PE relocations. A direct CALL changed to a tail jump
is rejected. Removing private opt-in preserves the public-owner refusal.

Relevant existing suites cover strict Oracle replay, fixed linkages, focused
audits and both empty and aggregate EH ownership. All 114 controls pass across
six suites. The current report and retained-unit freshness check passes.

Retained ignored evidence:

- `.analysis/static-sincos-original-scopes.json`: original-only entry/extent and
  full parent/witness evidence.
- `.analysis/static-sincos-initial-focused.json`: initial complete-owner review.
- `.analysis/static-sincos-full-audit.log` and
  `.analysis/static-sincos-regression-check.json`: complete replay and retained
  results/units.
- `.analysis/static-sincos-{controls,oracle-controls,linkage-controls,focused-controls}.log`
  and `.analysis/static-sincos-{constructor,empty}-eh-controls.log`: controls.
- `.analysis/static-sincos-baseline/`: preceding report, units and inventory.
