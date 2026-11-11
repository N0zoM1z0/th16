# Replay FPS and further numeric storage identities

## Result

Three independently reviewed storage bindings resolve four complete existing
candidates:

| Original entry | Candidate | Complete exact bytes |
| --- | --- | ---: |
| `0x0040F240` | BombCirnoAInf::on_tick | 585 |
| `0x0040F4C0` | BombCirnoAInf::cancel_bullets | 174 |
| `0x0040FB00` | BombMarisaAInf::on_tick | 857 |
| `0x004482F0` | ReplayManager::draw_fps | 180 |

These add **1,796 exact primary bytes**. Canonical replay reports **815 exact,
63 mismatch and 337 incomplete**, covering 145,004 exact primary bytes. All
811 preceding exact results and 63 complete mismatches remain identical;
all 874 previous comparison units remain identical. Four new units give 878
total. No game source, verifier, build profile or artifact changes occur.
Source-origin review remains open and Factory acceptance remains unsubmitted.

## Fixed original witnesses

| Candidate symbol | Complete value | Original storage | Owned original witness |
| --- | --- | --- | --- |
| `__real@43300000` | single 176.0, four bytes | `0x00494654` | `0x0040F501`, ADDSS |
| `__real@44000000` | single 512.0, four bytes | `0x004946C0` | `0x00442649`, MULSS |
| `??_C@_03GOOLIKIF@?$CF3d?$AA@` | `%3d` plus NUL, four bytes | `0x00492218` | `0x0044837A`, PUSH |

The radius witness adds 176 after the later Cirno bomb growth calculation.
The player witness scales the death-state cancellation radius by 512. The
FPS callback compares the recorded rate with 30/50, selects a color and pushes
the complete three-column decimal format before the reviewed Ascii formatter.
All three payloads have duplicate read-only copies. The fixed typed reads or
PUSH establish storage identity; duplicate bytes do not select whichever
destination would pass a consumer.

The original-only reproducer `.analysis/review-replay-literal-originals.py`
reads no candidate artifact or compared operand. Its complete witness-owner
proofs include all reachable instruction starts, original payload hashes and
following padding. Cirno cancellation is a dense 174-byte owner with 51
reachable instructions and two following INT3 bytes. Replay FPS is a dense
180-byte owner with 43 instructions and twelve following INT3 bytes.

Player::on_tick_body already has a reviewed complete 4,540-byte switch owner:
4,519 code bytes, one alignment byte and five DWORD targets. That whole
original hash and dispatch proof are rechecked. Its 512 witness lies at a
reachable instruction start. The 4,508-byte candidate retains its genuine
32-byte whole-owner difference; resolving the numeric field grants it no
exact credit.

The two complete update entries are independently reviewed as dense 585/857
byte code owners with 153/208 reachable instructions and seven INT3 bytes
following each. Their original derivation likewise uses no candidate size or
artifact. Full evidence is `.analysis/replay-literal-original-identities.json`
and `.analysis/bomb-update-original-scopes.json`; the latter is reproduced by
`.analysis/review-bomb-update-original-scopes.py`.

## Existing acceptance rules

The two numeric records use the existing fixed literal profile, requiring the
full encoded typed value and its original memory witness. The format uses the
existing string-literal profile: one complete four-byte NUL-terminated candidate
PDB contribution, exact payload and fixed original PUSH. The other original
`%3d` payload at `0x00492A06` is explicitly refused for this record because the
fixed instruction does not push that address.

No generic data fallback, interior alias, byte mask, relocation exception or
partial comparison is added. All source-qualified complete PDB ownership,
linkage bindings and raw replay checks remain required. Storage identities
receive no separate primary exact credit.

Other consumers remain refused: the player body and player laser tick expose
extent differences after their last field resolves; masked Anm drawing, Reimu
orb update and GUI drawing retain unresolved fields. StageInner::run_std's
remaining candidate destination is private exception-handling code. It is not
promoted to a runtime or literal binding by this review.

## Validation

All **209 controls across nine suites** pass. The reviewed-linkage suite has
28 controls. Numeric controls now also reject altered/interior witnesses,
expanded typed extents and duplicate storage for 176/512. The FPS format control
checks its complete payload/PDB extent and rejects a wrong or interior PUSH,
changed mnemonic, duplicate original storage, missing NUL and shortened or
ambiguous candidate contributions. The preceding complete-owner and relocation
controls remain unchanged.

Focused reports are `.analysis/replay-literal-focused.json` and
`.analysis/replay-literal-other-focused.json`. Canonical replay and retained-unit
evidence are `.analysis/replay-literal-full-audit.log` and
`.analysis/replay-literal-regression-check.json`. Suite logs use
`.analysis/replay-literal-<suite>-controls.log`, matching `scripts/test-<suite>.py`.
The preceding report, units, inventory and bindings remain under
`.analysis/replay-literal-baseline/`. Every build input/artifact fingerprint
equals that checkpoint; no compile, analyzer run, cleanup or receipt refresh
is needed. Nothing is published.
