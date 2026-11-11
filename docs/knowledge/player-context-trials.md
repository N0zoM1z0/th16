# Player update and circle-check source contexts

## Result

Four natural source contexts were compiled, compared over their complete
affected owners and rejected. Player.cpp is restored byte for byte and freshly
rebuilt. No game source change or exact credit is retained in this batch.
Canonical results remain **815 exact, 63 mismatch and 337 incomplete**, covering
145,004 exact primary bytes and 878 retained comparison units.

The full player update remains an independently reviewed **4,540-byte** original
against a **4,508-byte** candidate. Its original comprises 4,519 code bytes,
one alignment byte and five DWORD targets. The candidate has 4,487 code bytes,
one alignment byte and the same number of target slots. Both complete scopes
and their actual table locations are retained; neither is shortened to the
other's code prefix.

## Update-body differences

Diagnostic alignment of the full instruction streams locates several distinct
differences behind the net 32-byte extent gap:

- The item-drop path uses NEG plus ADD in the original power calculation and
  a subtraction in the candidate. The original carries the item-position
  address in EDI; the baseline candidate saves/reloads it through a stack slot.
- Two inlined timer-decrement paths retain a multiplication by the fixed
  1.0f value in the original. The candidate folds these operations away. This
  is the same unresolved context already documented in ZunTimer.cpp; the
  Player review does not establish a replacement timer implementation.
- The afterimage path clears and reloads the original mode word differently
  from the candidate's cached ECX value. Bitfield/type and alias context
  remain unproven; no new flag type or forced access is introduced.
- Scaled hurt/collection/attraction boxes have different load, multiply,
  packing and store schedules, including different memory operand choices.
  Register or scheduling normalization would hide real byte differences.

These are diagnostic findings, not independent exact credit for matching
subranges. The existing strict complete-owner profile still refuses the body.

Two used position-pointer contexts were tested:

| Trial | Natural source context | Complete candidate | Code / alignment / table bytes | Result |
| --- | --- | ---: | --- | --- |
| Baseline | Direct member coordinates and repeated item-origin expression | 4,508 | 4,487 / 1 / 20 | Extent refusal |
| Drop pointer | Read coordinates and pass the item origin through a local pointer | 4,504 | 4,482 / 2 / 20 | Extent refusal |
| Call origin | Keep direct coordinate reads; use the local pointer for item creation | 4,508 | 4,487 / 1 / 20 | Extent refusal |

The first pointer context changes stack/data flow but also reloads Y from the
short pointer-relative address instead of retaining the original cached value.
The second still has a different complete owner. Neither context recovers the
original five-case mapping or full extent. Matching one stack slot is not a
reason to retain the surrounding differences. Both contexts are restored.

## Complete circle-check trials

The original and baseline Player::check_hit_circle both own 258 bytes; baseline
replay is **181/258**. The original first loads Y, then X, before completing the
two coordinate differences. Its shared zero return appears beside the dialogue
guard; the candidate places that return after its final successful return.
These choices affect instruction order and branch offsets throughout the tail.

| Trial | Natural source context | Complete candidate | Strict result |
| --- | --- | ---: | --- |
| Float2 displacement | Construct the two coordinates actually used by circle distance | 261 | Full extent refusal against 258 |
| Combined guard | Combine dialogue and non-graze invalid-state rejection, preserving short-circuit behavior | 258 | Complete mismatch, 190/258 |

The Float2 trial also changes the separate LTCG caller
`Bullet::check_player_collision` from a complete 449-byte candidate to 460
bytes. Its original is now independently reviewed as a dense complete
448-byte owner with 130 reachable instructions, immediately followed by the
next entry. Thus the trial also widens that existing extent refusal. This
side effect is recorded with its full payload, PDB producer, linked fields and
relocations; no prefix comparison or credit is taken. Restoration returns the
caller to 449 bytes. See `.analysis/player-secondary-original-scope.json` and
`.analysis/review-player-secondary-owner.py`.

Both contexts are rejected and restored. The latter's nine additional matching
bytes do not recover the original complete control flow or load order. No
register, stack displacement, branch location or timer operation is normalized.
No dead local, volatile access, padding helper or artificial arithmetic is
introduced. Do not repeat these four contexts or force the unresolved timer
multiplications or shared-return placement.

## Validation and retained evidence

All 209 existing controls across nine suites pass. Every preceding exact result,
complete mismatch and retained unit remains retained. Restoration checks prove
baseline source/build input identity, all 1,719 complete source-qualified linked
owner entries/extents/raw hashes, current artifact hashes and all 192 dependency
stamps. No clean build or archived-output substitution is used.

`.analysis/player-context-source-trials.json` retains full original/trial
payloads, complete PDB producers, every linked field and PE relocation, actual
table locations/cases, artifact/source identities and strict outcomes. It also
records each trial's complete linked-owner changes. Source/output sets remain
under `.analysis/player-tick-source-baseline/`,
`.analysis/player-tick-{drop-pointer,call-origin}-artifacts/` and
`.analysis/player-circle-{vector2,combined-guard}-artifacts/`.

Diagnostic instruction evidence is `.analysis/player-tick-baseline-layout.json`
and `.analysis/player-tick-{drop-pointer,call-origin}-layout.json`. Reproducers
are `.analysis/review-player-tick-layout.py` and
`.analysis/review-player-context-trials.py`; their diagnostic alignment is not
an Oracle or an acceptance source. Restoration and canonical evidence are
`.analysis/player-context-restored-build.log`,
`.analysis/player-context-restored-check.json`,
`.analysis/player-context-full-audit.log` and
`.analysis/player-context-regression-check.json`. Suite logs use
`.analysis/player-context-<suite>-controls.log`, matching `scripts/test-<suite>.py`.
Source-origin review remains open; Factory acceptance remains unsubmitted.
Nothing is published.
