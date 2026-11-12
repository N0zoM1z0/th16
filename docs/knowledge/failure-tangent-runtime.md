# Failure, tangent and short-format identities

## Complete source results

Two complete runtime identities and three fixed string PUSHes resolve five
existing whole source candidates:

| Original entry | Function | Complete primary bytes |
| --- | --- | ---: |
| `0x0043DC90` | zun_tanf | 23 |
| `0x0043E730` | PauseMenu::draw_keyboard | 394 |
| `0x004541B0` | TitleInf::on_draw__replay_save | 997 |
| `0x004580E0` | lzss_init | 68 |
| `0x0046D0C0` | AnmLoaded::load_entry | 247 |

These add **1,729 exact primary bytes**. Canonical replay reports **833 exact,
65 mismatch and 317 incomplete**, covering 150,443 exact primary bytes and
898 units. All 828 preceding exact results, all 65 complete mismatches and
all 893 previous units remain retained. Runtime code and string storage receive
no additional primary credit. Existing admission and normalization rules are
unchanged. No game source change is retained after the trials below.

## Complete runtime entries

| Symbol | Original root / full extent | Complete candidate | Pinned producer |
| --- | --- | ---: | --- |
| `___report_rangecheckfailure` | `0x00475058` / 12 | 12 | LIBCMT:gs_report.obj |
| `__libm_sse2_tan_precise` | `0x00488790` / 605 | 624 | libucrt:tan_sse2_precise.obj |

The range-check entry's six reachable instructions establish a frame, push
failure code eight and call the independently inventoried security-failure
entry at `0x00475064`, followed by its complete epilogue. The complete LZSS
initializer has 17 reachable instructions and an explicit final tail JMP to
the range-check entry. That tail is included in its 68-byte owner.

The original tangent entry has 135 reachable instructions over all 605 bytes,
closed direct branches and the error-support CALL at `0x004889DC`. Its complete
candidate PDB contribution owns 624 bytes. The following 19 original bytes
contain neighboring helper/alignment/bridge code and are recorded separately;
they are not appended to the original function to match the candidate. Neither
side is shortened. The existing `candidate_size` contract records both full
extents, as it already does for the square-root entry. This callee identity
does not claim an exact runtime implementation or assign identities to its
internal error-support helpers.

## Fixed short strings

| Complete value | Original storage | Fixed original PUSH | Witness owner |
| --- | --- | --- | --- |
| `%s` plus NUL, 3 bytes | `0x004929B0` | `0x0046D12C` | AnmLoaded::load_entry, 247 |
| Space plus NUL, 2 bytes | `0x00492154` | `0x00452D55` | TitleInf::draw_spell_card_page, 1,011 |
| Underscore plus NUL, 2 bytes | `0x004929B4` | `0x0043E78D` | PauseMenu::draw_keyboard, 394 |

Every value has other raw read-only occurrences. Each binding fixes the actual
PUSH inside an independently decoded complete original owner. Candidate
symbols require unique complete 3/2/2-byte PDB storage and the entire matching
NUL-terminated payload. Equal bytes elsewhere do not select a destination.
The three witness owners have 80, 268 and 101 reachable instructions. The
spell-page owner includes its terminal INT3 at `0x00453022`, after the failure
CALL; thirteen subsequent INT3 padding bytes precede the next independent entry.
That owned trap is not an unreviewed fallthrough or permission to extend the
original by five bytes.

Complete original review also establishes 246 reachable instructions for the
997-byte replay-save drawing owner. All five accepted source candidates replay
their full PDB owners, all linked fields and every PE relocation.

## Spell-page source trials and remaining scope

The complete spell-page original remains **1,011 bytes** against a **1,016-byte**
baseline candidate. Its fields now resolve, exposing the whole-extent refusal.
Original digit lookup is deferred until the argument PUSH, and character
statistics use a retained base with indexed spell accesses.

| Trial | Natural source context | Complete candidate | Strict result |
| --- | --- | ---: | --- |
| Index | Retain the ones-digit remainder until its argument lookup | 1,012 | Extent refusal |
| Index and character | Extend that context with a used character-base pointer | 994 | Extent refusal |

The first context recovers the deferred indexed PUSH shape but does not match
the whole owner. The second also changes link layout: 1,231 complete linked
owner records differ, with only the spell-page extent changing. Every changed
owner is retained with both full payloads, PDB producers, fields and relocations.
No unequal prefix receives a score or credit. Both contexts are rejected;
do not repeat them, force stack offsets or add padding locals.

AnmLoaded::load also exposes an independently complete **430-byte original
with 133 reachable instructions against a 461-byte candidate** after its last
format field resolves. Neither differing owner receives exact credit.
The name-entry drawing path and main interpreter retain unresolved fields.

## Validation and retained evidence

All **239 controls across ten suites** pass. Reviewed-linkage controls increase
from 34 to 36: both complete runtime extents are required, and all three short
strings reject instruction interiors, wrong mnemonics, duplicate original
storage, missing NULs and shortened/ambiguous candidate contributions.

Baseline MainMenuStates.cpp is restored byte for byte and freshly rebuilt
incrementally. Source input identity equals baseline; all 1,719 complete linked
owner entries/extents/raw hashes, current artifacts and 192 dependency stamps
validate. No clean build or archived-output substitution is used.

Original evidence is `.analysis/failure-tangent-runtime-original-review.json`
and `.analysis/failure-format-original-identities.json`, reproduced by
`.analysis/review-failure-tangent-runtime.py` and
`.analysis/review-failure-format-originals.py`. Complete accepted caller scopes,
payloads, producers, fields, relocations, units and strict results are in
`.analysis/failure-format-runtime-caller-scopes.json`. All source-trial owners
and real strict captures are in `.analysis/failure-format-spell-source-trials.json`,
reproduced by `.analysis/review-failure-spell-trials.py`.

Baseline and trial sets remain under `.analysis/failure-tangent-runtime-baseline/`
and `.analysis/failure-format-spell-{index,character}-artifacts/`. Restoration,
canonical and retained-pass evidence is
`.analysis/failure-format-runtime-restored-build.log`,
`.analysis/failure-format-runtime-restored-check.json`,
`.analysis/failure-format-runtime-full-audit.log`,
`.analysis/failure-format-runtime-regression-check.json` and
`.analysis/failure-format-runtime-controls-summary.json`. The regression
reproducer is `.analysis/check-failure-format-regression.py`.
Source-origin review remains open; Factory acceptance remains unsubmitted.
Nothing is published.
