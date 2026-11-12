# Loader failure identity and wrap bounds review

One independently witnessed, complete loader-failure string resolves five
whole source functions. The Bullet wrap bounds source context is rejected
and restored. No Oracle, compiler profile, normalization or owner-extent
rule changes.

## Fixed original loader-failure storage

The message at `0x00491C64` contains 23 bytes, including CR/LF and its NUL
terminator. The fixed PUSH at `0x00407CFE` selects it in the complete
326-byte `AsciiInf::initialize` owner. All 102 instructions are reachable;
every branch target, terminal path and following INT3 interval is checked.

The same complete payload occurs at seven original read-only addresses:
`0x00491C64`, `0x00491D04`, `0x00491D3C`, `0x00492020`, `0x00492092`,
`0x004920CC` and `0x00492BC0`. Payload equality alone cannot choose one.
All seven reviewed callers below actually PUSH `0x00491C64`, each from an
independently checked instruction start in its complete dense owner.

| Original owner | Bytes | Reachable instructions | Fixed PUSH |
| --- | ---: | ---: | --- |
| `AsciiInf::initialize`, `0x00407CB0` | 326 | 102 | `0x00407CFE` |
| `Ending::initialize`, `0x004191F0` | 593 | 169 | `0x004193D2` |
| `EclResourceInf::load_includes`, `0x0041B040` | 351 | 134 | `0x0041B14C` |
| `Gui::initialize`, `0x00426B00` | 258 | 76 | `0x00426B20` |
| `Gui::load_stage_files`, `0x00426C10` | 337 | 84 | `0x00426C2E` |
| `load_shared_anms`, `0x0043AD20` | 60 | 20 | `0x0043AD30` |
| `TitleInf::initialize`, `0x0044AC70` | 165 | 54 | `0x0044ACCB` |

The unique candidate MSVC string public is at `0x00492250`, attributed to
`AsciiManager.obj`. Its same-start PDB data contribution owns exactly 23
bytes, and its entire NUL-terminated payload agrees with the original.
The existing `string-literal` rule checks that complete storage and the fixed
original PUSH. The new CSV row records the full public name, fixed address,
extent, payload hash and witness.

The existing mutation table now also covers this message. It rejects an
interior instruction witness, wrong mnemonic, the duplicate at `0x00491D04`,
a missing NUL, a shortened PDB contribution and ambiguous contributions.
The production verifier is unchanged.

## Complete caller outcomes

The ASCII, GUI initialization, stage-file, shared-ANM and title initialization
owners pass all **326 + 258 + 337 + 60 + 165 = 1,146 bytes**. Every complete
candidate has its own source-qualified PDB owner; exhaustive instruction
fields, PE relocations and standalone Oracle replays are retained.

Ending initialization remains incomplete with two fields. ECL include loading
remains incomplete with one field. Neither receives prefix credit or a guessed
alias. The literal itself receives no separate primary exact credit.

The canonical report is **842 exact, 65 mismatch and 308 incomplete** among
1,215 annotations, covering **153,746 exact primary bytes and 907 units**.
All previous 837 exact results, 65 complete mismatches and 902 unit definitions
are retained. The only additional comparison units are the five complete
passes above. Admission rules remain unchanged.

## Rejected Bullet wrap bounds context

`Bullet::step_ex_12` at `0x00415D80` handles playfield wrapping. Its complete
original owns 519 bytes and 124 reachable instructions, followed by nine
INT3 bytes. After reviewed linkage normalization, four encoding bytes differ:
the original loads positive 192.0f into XMM4 before loading 448.0f into XMM2;
the candidate emits those two loads in the opposite order.

A natural context names the used half-width, height and derived width, then
uses those dimensions throughout the wrap checks and coordinate updates.
It produces the identical complete 519-byte candidate and the same 515/519
mismatch. Every one of the 1,719 complete linked owner entries, extents and
raw hashes also remains identical. This context is rejected and the source
is restored byte for byte. Do not repeat it or the earlier named horizontal
predicate, or force a constant read/register to reorder the loads.

A fresh incremental build of restored source validates all 1,719 complete
linked owners and 192 dependency stamps. The source input remains
`c2ac9cc0add85924f097edf2dc772148551601b302607cc480fba1867a1fcd5a`.
Fifty-three controls pass: reviewed linkages (36), strict Oracle (14) and
focused audit (3). No game source change, cold build, cleanup, archived-output
substitution, Factory submission or remote publication is retained.

## Evidence

Original-only loader scopes and reproducer are
`.analysis/loader-error-original-review.json` and
`.analysis/review-loader-error-originals.py`. Complete caller payloads,
fields, relocations, PDB owners and successful Oracle replays are
`.analysis/loader-error-caller-scopes.json`, reproduced by
`.analysis/review-loader-error-callers.py`. Canonical replay and regression
proof are `.analysis/loader-error-full-audit.log` and
`.analysis/loader-error-regression-check.json`; the control summary is
`.analysis/loader-error-controls-summary.json`.

The wrap trial's complete original/candidate scopes and source receipts are
`.analysis/bullet-wrap-bounds-source-trial.json`, reproduced by
`.analysis/review-bullet-wrap-bounds.py`. Full source and artifact snapshots
are retained under `.analysis/bullet-wrap-bounds-{baseline,artifacts}/`.
Current restored build evidence is `.analysis/bullet-wrap-restored-build.log`
and `.analysis/bullet-wrap-restored-check.json`, reproduced by
`.analysis/check-bullet-wrap-restored.py`.
