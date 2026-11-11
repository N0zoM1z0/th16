# Replay-slot snapshot in the open pause menu

## Retained source change

`PauseMenu::tick_open` now reads `item_menu.next_selection` into a meaningful
`replay_slot` local immediately before creating the replacement replay. The
result is stored into that saved array slot. This recovers the original
evaluation order without a forced register, access, padding byte or compiler
context helper.

The independent original at `0x0043F980` reads `[EDI+0x34]` into ESI at
`0x004403F6` (`+0xA76`), then calls the replay factory at `0x004403FD`
(`+0xA7D`). It stores the result through the saved index at `0x00440406`
(`+0xA86`). The preceding source expression left the index read after the
factory call in the linked candidate, and kept the name-buffer pointer live
in ESI instead. The snapshot expresses the original ordering directly.

The retained candidate restores this index read before the factory call,
rematerializes the name-buffer address for the subsequent copy, and recovers
the original copy loop in this replay-save path. Its next case starts at
`+0xC87` (3,207), matching the original instead of the preceding 3,206.
The full original and candidate owners both remain **4,676 bytes**: 4,586 code
bytes, two alignment bytes and 22 DWORD target slots in two complete tables.

## Whole-owner result and limitations

The strict Oracle still refuses the original case mapping. First-table slots
7 and 9 target 1,420 instead of 1,392; slot 10 targets 1,988 instead of 1,982.
All five second-table case offsets remain correct. No original case offset,
scope, relocation addend or verifier rule changes.

A separate diagnostic replays all 4,676 bytes using the audit's independent
bindings and all 306 linked fields. It reports **3,345/4,676 matching bytes
before and 4,067/4,676 after**. This is diagnostic evidence of the source
improvement; it cannot override the case-map refusal and grants no exact
credit. Every code byte, alignment byte and target slot remains compared.

The remaining differences include the location of a shared close-menu tail,
two address-operand encodings in another name-copy/trim path, and the order of
the final name-cursor store relative to argument setup. The original shared
tail follows the confirmation case; the candidate emits it in the earlier
choose case. Do not force registers, base/index encodings or layout to hide
these differences.

Canonical replay remains **809 exact, 61 mismatch and 345 incomplete** among
1,215 candidates, covering 141,487 exact primary bytes and 870 retained units.
No new primary exact credit is claimed. All preceding exact owners and units
remain retained. Source-origin review remains open and Factory acceptance
remains unsubmitted.

## Rejected control-flow trials

Two ordinary equivalent exit forms were compiled incrementally:

| Trial | Source context | Complete candidate | Diagnostic matches | Strict result |
| --- | --- | ---: | ---: | --- |
| Baseline | Original source expression | 4,676 | 3,345 | Case-map refusal |
| Switch exit | Resume branch exits the outer switch instead of returning | 4,676 | 3,345 | Case-map refusal |
| Selected slot | Explicitly reads the replay slot before the factory call | 4,676 | 4,067 | Case-map refusal; retained improvement |
| Quit return | Early return in the quit shortcut, with the slot snapshot | 4,676 | 4,067 | Case-map refusal |

Neither exit-form trial changes the complete generated owner. Both are
rejected; only the replay-slot snapshot is retained. Do not repeat these exit
forms or introduce artificial inputs to select a different shared tail.

## Validation and evidence

All 1,719 complete linked owners were compared with the preceding artifacts
by source-qualified symbol, address, full extent and raw payload hash. Only
`PauseMenu::tick_open` changes; its entry and full extent remain unchanged.
All 207 existing controls across nine suites pass. The retained source is
freshly rebuilt incrementally; artifact hashes match its build receipt and
all 192 dependency stamps validate. No archived output is substituted and no
clean build is used.

Full original/candidate payloads, real audit field declarations, source hashes,
trial outcomes and retained layout are in `.analysis/pause-open-source-trials.json`.
Complete sources and outputs are preserved under
`.analysis/pause-open-{source-baseline,switch-exit-artifacts,selected-slot-artifacts,quit-return-artifacts}/`.
Diagnostic reproducers are `.analysis/review-pause-open-layout.py`,
`.analysis/compare-pause-whole-diagnostic.py` and
`.analysis/compare-pause-archives.py`; none can grant Oracle acceptance.
The full scope delta, build check, canonical replay and regression evidence are
`.analysis/pause-open-complete-owner-delta.json`,
`.analysis/pause-open-retained-build-check.json`,
`.analysis/pause-open-full-audit.log` and
`.analysis/pause-open-regression-check.json`. Control logs use
`.analysis/pause-open-<suite>-controls.log`, matching `scripts/test-<suite>.py`.
Nothing is published.
