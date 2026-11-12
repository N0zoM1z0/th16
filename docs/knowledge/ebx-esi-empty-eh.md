# Complete EBX/ESI empty EH3 frames and a rejected Replay destructor trial

Three complete destructor graphs use one local word, saved EBX/ESI and an empty
EH3 descriptor. Their registration node is EBP-12 and encoded cookie is EBP-28,
so their handlers read node-16. An explicit frame profile now checks this
variant and resolves 865 primary exact bytes. A separate used-pointer source
trial for ReplayManager destruction is rejected and restored.

## Complete original scopes and private roles

| Parent | Complete original parent | Reachable instructions | Private handler | FuncInfo |
| --- | --- | ---: | --- | --- |
| `BulletManager::~BulletManager` | `0x00411CA0`, 292 bytes | 77 | `0x0048A540` | `0x0049B0F4` |
| `EffectManager::~EffectManager` | `0x004188D0`, 345 bytes | 87 | `0x0048A5B0` | `0x0049B168` |
| `LaserManager::~LaserManager` | `0x004313B0`, 228 bytes | 64 | `0x0048A850` | `0x0049B40C` |

Original-only review decodes every parent byte, traverses all instructions from
the entry, checks every branch destination and return, excludes interior
inventory entries and accounts for the full following INT3 intervals. Each
fixed registration PUSH identifies its own complete 27-byte handler, followed
by five INT3 bytes. Each handler selects its own complete 36-byte FuncInfo.
The descriptors contain exactly `19930522 0 0 0 0 0 0 0 5`.

| Source object | Candidate parent | Private handler | FuncInfo |
| --- | --- | --- | --- |
| `BulletManager.obj` | `0x0041AFA0` | `0x0048A4F0` | `0x0049ADFC` |
| `EffectManager.obj` | `0x00426940` | `0x0048A5E0` | `0x0049AEC8` |
| `Laser.obj` | `0x004426A0` | `0x0048A880` | `0x0049B16C` |

Candidate parents have unique same-size, complete source-object PDB owners and
public entries. Parent-qualified private MAP names identify full 27/36-byte
handler/descriptor contributions in their parent's PDB module. Ambiguous,
overlapping or interior owners remain rejected. Identical empty descriptors
do not allow another parent's private role to substitute for the selected one.

## Independently derived frame

The explicit profile is `empty-eh3-saved-ebx-esi-v1`.

| EBP-relative slot | Content |
| --- | --- |
| -4 | initial EH state, -1 |
| -8 | this parent's handler |
| -12 | prior FS head; registration node address |
| -16 | one local word |
| -20 | saved EBX |
| -24 | saved ESI |
| -28 | encoded cookie |

The exact 37-byte prefix establishes the complete registration and save order.
The exact 17-byte suffix restores FS, discards the cookie, restores ESI/EBX and
returns through the original EBP frame. Cookie storage is independently read
from the PE load configuration. Whole-parent decoding checks direct accesses
to the four reserved EH/cookie slots, all FS references, EBP writes and the
single final RET. Prefix relocations are exactly offsets 6/21; the suffix has
none. Every handler instruction and both independently bound runtime transfers
are checked. Handler relocation offset 18 is mandatory; descriptors have none.

The verifier shares these checks between two fixed save/restore sequences:
EBX/ESI and the earlier EBX/ESI/EDI profile. It derives cookie displacement and
prefix/suffix positions from those fixed sequences. Configurations cannot
provide arbitrary register bytes, stack allocation or cookie offsets. Legacy
node-4 and nonempty constructor profiles retain their restrictions; all eight
earlier saved-register proofs retain their complete comparison details.

Matching displacement alone remains insufficient. Bomb destruction saves
ESI/EDI, while Spellcard destruction reserves two local words and saves ESI.
Both handlers also read node-16, but their full frames fail this profile.
No new binding is installed for either parent. Cross-profile substitution is
also explicitly rejected for all eleven reviewed saved-register parents.

All three primary parents pass every byte, field and relocation: 292/345/228
bytes, totaling 865. The 81 auxiliary code bytes and 108 metadata bytes receive
no additional primary credit. No body interval is masked or shortened.

## Rejected ReplayManager pointer snapshot

The complete original destructor at `0x00447C80` remains 416 bytes, with 120
reachable instructions and a final RET immediately before `0x00447E20`.
The retained candidate is 415 bytes. Original code reads each update-function
pointer before the null check and retains it across critical-section entry.
The existing candidate reloads the member when calling `unregister`.

A used `UpdateFunc *func` local snapshots each of the three members before its
null check and supplies the captured value to `unregister`. Registry reads
remain inside the null checks. This ordinary source context produces a complete
437-byte owner, spilling the function pointer beside the registry pointer.
It is rejected. Only this function's complete extent changes, while 1,153
linked owner records change through its payload and later addresses/fields.
No comparison, truncated parent or EH binding grants credit to the trial.

Source is restored byte for byte and freshly rebuilt incrementally. All 1,719
complete linked owner records, including entries, extents and raw hashes, again
equal the pre-trial baseline; all 192 dependency stamps validate. Do not repeat
this used-pointer context or force register/import-address allocation to make
the source match. No game source change is retained.

## Replay, controls and retained evidence

Canonical replay reports **858 exact, 65 mismatch and 292 incomplete** among
1,215 annotations, with **160,210 exact primary bytes and 923 units**. All prior
855 exact results, 65 complete mismatches and 920 unit definitions remain
retained. Every prior comparison detail is identical except the independently
verified fresh image fingerprint and PDB age, which advances from 118 to 120
through the trial and restoration links. All other incomplete records are
identical. The source input remains
`c2ac9cc0add85924f097edf2dc772148551601b302607cc480fba1867a1fcd5a`.

**140 controls pass**: both saved-register profiles (37), legacy empty EH (25),
constructor EH (25), reviewed linkages (36), strict Oracle (14) and focused
audit (3). They exercise all eleven complete saved-register graphs, both wrong
profile directions, same-displacement unsupported frames, wrong cookie slots,
forged hashes, state writes, malformed private extents, source/parent misuse
and missing/duplicate/crossing relocations. Ordinary body mutations still fail
whole-parent byte replay after their EH graphs validate.

Original-only scopes are retained in `.analysis/ebx-esi-eh-original-scopes.json`,
reproduced by `.analysis/review-ebx-esi-eh-originals.py`. Complete graphs,
payloads, fields, relocations and standalone replays are in
`.analysis/ebx-esi-eh-caller-scopes.json`, reproduced by
`.analysis/review-ebx-esi-eh-callers.py`. Artifact/dependency preservation and
prior comparison/provenance checks are in `.analysis/ebx-esi-eh-artifact-check.json`
and `.analysis/ebx-esi-eh-regression-check.json`, reproduced by their matching
`check-*.py` files. Terminal audit/control logs use `.analysis/ebx-esi-eh-*`.
The rejected trial, full artifact backup and fresh-restoration proof are
`.analysis/replay-destructor-snapshot-artifacts/`,
`.analysis/replay-destructor-source-trial.json` and
`.analysis/check-replay-destructor-restored.py`.

The current incremental graph and ignored evidence remain retained. No cold
build, cleanup, archived-artifact substitution, Factory submission or remote
publication occurs. Source-origin review and formal Factory acceptance remain open.
