# Further fixed numeric identities and music-room source trials

## Complete comparison results

Seven reviewed numeric bindings resolve four existing whole candidates:

| Original entry | Candidate | Complete primary bytes | Result |
| --- | --- | ---: | --- |
| `0x0041CBD0` | EnemyData::update_fog | 1,547 | Exact |
| `0x004263E0` | FpsCounter::draw | 174 | Exact |
| `0x004439E0` | Player::check_hit_circle | 258 | Mismatch, 181 matching bytes |
| `0x004546F0` | TitleInf::do_music_room | 3,136 | Mismatch, 3,133 matching bytes |

These add **1,721 exact primary bytes**. Canonical replay reports **811 exact,
63 mismatch and 341 incomplete**, covering 143,208 exact primary bytes. All
809 preceding exact results remain exact and all 870 preceding comparison
units remain identical. Four new complete units give 874 total. Neither
complete mismatch receives exact credit. No game source change is retained
in this batch. Source-origin review remains open and Factory acceptance
remains unsubmitted.

## Independent numeric storage review

All seven values occur more than once in the original read-only data. Some
single-precision patterns also occur within double-precision values. No
destination is selected by whichever address would make a consumer pass.
Each binding names a fixed, independently decoded instruction in a complete
original owner, its actual typed memory read, complete value bytes and hash.
The existing literal profile verifies the candidate symbol's encoded value,
its complete payload and that fixed original witness. No verifier or field
normalization changes are made.

| Candidate symbol | Value / width | Original storage | Original witness |
| --- | --- | --- | --- |
| `__real@41a00000` | 20.0 / 4 bytes | `0x004945E8` | `0x004549A9`, MULSS |
| `__real@4020000000000000` | 8.0 / 8 bytes | `0x00494578` | `0x00454B8F`, MOVSD |
| `__real@42200000` | 40.0 / 4 bytes | `0x00494604` | `0x00454BFB`, ADDSS |
| `__real@42480000` | 50.0 / 4 bytes | `0x00494610` | `0x00405ABC`, FMUL |
| `__real@42700000` | 60.0 / 4 bytes | `0x00494620` | `0x0040C534`, MOVSS |
| `__real@41f00000` | 30.0 / 4 bytes | `0x004945F8` | `0x0042640C`, MOVSS |
| `__real@40200000` | 2.5 / 4 bytes | `0x00494570` | `0x00443A56`, DIVSS |

The music-room values govern scrolling, selected-row displacement and vertical
spacing. Their witnesses are checked from the independently reviewed complete
3,136-byte original: 3,118 code bytes, two alignment bytes and four DWORD
targets. The four further witnesses have independently checked dense reachable
code owners of 1,973, 2,156, 174 and 258 bytes, respectively, with all following
INT3 padding accounted for. The enemy fog update independently covers 1,547
code bytes, 367 reachable instructions and five following INT3 bytes. No
candidate size or artifact enters these original scope derivations.

Original value bytes, hashes, duplicate locations, instructions and complete
owner evidence are in `.analysis/menu-literal-original-identities.json`,
`.analysis/additional-literal-original-identities.json` and
`.analysis/enemy-fog-original-scope.json`. Their original-only reproducers are
`.analysis/review-menu-literal-originals.py`,
`.analysis/review-additional-literal-originals.py` and
`.analysis/review-enemy-fog-original-scope.py`.

## Music-room initialization difference

The complete baseline music-room candidate differs at only `+0x174`, `+0x17C`
and `+0x184`: three displacement bytes in zero-initialization stores. The
original initializes the loop index at `[ESP+0x18]` before position X/Y at
`[ESP+0x28]` and `[ESP+0x2C]`. The candidate emits X/Y before the index. The
position Z initialization and its cached register, all case mappings, extents,
other bytes and linkage contracts pass. This is a real whole-owner mismatch;
the verifier does not normalize store order or stack displacements.

Three natural source contexts were compiled incrementally:

| Trial | Source context | Complete candidate | Strict result |
| --- | --- | ---: | --- |
| Counter scope | Declare the used loop index before the position initialization | 3,136 | Same 3,133-byte mismatch |
| Vector zero | Assign a zero Float3 as one value | 3,152 | Complete extent refusal |
| Per-line origin | Initialize X/Y inside each comment-line iteration, with Z outside | 3,136 | Worse mismatch, 3,105 matching bytes |

All three contexts are rejected. Baseline MainMenuStates.cpp is restored byte
for byte and freshly rebuilt. No dead local, forced register/access, helper,
assembly, mask, padding or shortened comparison is introduced. The vector
trial's table is located from its actual dispatch operand after its extent
changes; it is not assumed to stay at the original offset. Do not repeat these
contexts or force the remaining initialization order.

Complete source/output sets are retained under
`.analysis/menu-literal-source-baseline/` and
`.analysis/music-room-{counter-scope,vector-zero,per-line-origin}-artifacts/`.
`.analysis/music-room-source-trials.json` includes full original and candidate
payloads, actual table locations/cases, complete audit units, strict results,
instructions and source/artifact identities. The restored comparison remains
3,133/3,136. Existing PauseMenu replay-slot source progress is preserved.

## Validation and remaining work

All **208 controls across nine suites** pass. The reviewed-linkage suite now
has 27 controls; its new control covers all seven values and rejects an
instruction-interior witness, a different instruction, a changed mnemonic,
an expanded typed extent and an identical payload at another original
address. Existing complete-owner, relocation and raw replay controls remain
unchanged. No acceptance rule is relaxed.

Restored source/build input identity equals the preceding checkpoint. All
1,719 complete linked owners retain their source-qualified symbol, entry,
full extent and raw payload hash. Current artifact hashes match their fresh
incremental receipt, and all 192 dependency stamps validate. See
`.analysis/menu-literal-restored-context-check.json`. No clean build, archived
output substitution or cleanup occurs.

Gather, stage-fog and sound-thread candidates now expose extent refusals after
their final numeric field resolves. Gather's independently complete original
is 1,973 bytes against 1,993; stage fog is 2,156 against 2,172. Other affected
callers retain unresolved fields. The raw consumer differences and exact
refusal changes are retained in `.analysis/menu-literal-regression-check.json`.
These refusals receive no exact credit.

Canonical evidence is `.analysis/menu-literal-full-audit.log` and
`.analysis/menu-literal-regression-check.json`. Focused comparisons are
`.analysis/menu-literal-music-room-focused.json`,
`.analysis/menu-literal-other-focused.json` and
`.analysis/additional-literal-focused.json`. Control logs use
`.analysis/menu-literal-<suite>-controls.log`, matching `scripts/test-<suite>.py`.
The preceding report, inventory, units and bindings remain in
`.analysis/menu-literal-baseline/`. Nothing is published.


## Further result contexts from 132f12a

A fresh original-only traversal retains the complete 3,136-byte owner: 3,118
code bytes, the two-byte alignment instruction and all four jump-table slots.
All 768 instructions are reachable, with 59 calls and six returns. Its existing
original hash, guard, table destinations and boundaries are unchanged.

| Additional source form | Complete candidate result |
| --- | --- |
| Named initialized comment handle | Same strict 3,133/3,136 mismatch |
| Typed member-pointer creator and named handle | Same strict 3,133/3,136 mismatch |
| Explicit counter and do/while | 3,104 bytes; incomplete |
| Ordinary comment-creation helper | 2,880 bytes; incomplete with unresolved fields |
| Reused default-constructed comment handle | Same strict 3,133/3,136 mismatch |

All five forms are rejected and restored. No forced-inlining attribute,
initialization-order normalization or linkage exception is introduced. Keep
`.analysis/music-comment-join-work/`: all sources, focused reports, original CFG,
last music trial image and PDB-489 restoration regression. The separate later
shared callback constructor reconstruction
adds the complete AnmManager exact result; this music-room owner remains the
same three-byte mismatch.
