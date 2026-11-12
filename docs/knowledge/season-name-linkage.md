# Season-name linkage and complete menu drawing

## Source declaration

The existing `g_season_names` definition was a namespace-scope const array
without a preceding external declaration. Its `GLOBAL` annotation therefore
had no matching public symbol: LTCG placed the five pointers in an anonymous
constant contribution, without a named PDB global type. The neighboring
difficulty-name definition already has external linkage through MainMenu.h.

The season-name definition now explicitly uses `extern`, retaining the same
const pointer type, five initializers and runtime representation. It produces
one `?g_season_names@@3QBQBDB` public from MainMenuStates.obj and one complete
20-byte PDB array type. This is a named typed global, not a newly claimed
20-byte PDB section contribution: its enclosing physical CIL contribution
remains separate metadata. No wrapper, forced access, compiler option or
Oracle admission rule changes.

Every complete linked function retains its prior entry, extent and raw bytes
across this source change: all 1,719 owners are identical. The table's 20 raw
bytes also retain their baseline representation. The change makes the existing
annotated global identity available to the ordinary binding rules.

## Independent original table and callers

The original table at `0x004918C0` contains all five pointers to the complete
NUL-terminated values Spring, Summer, Autumn, Winter and Full with two trailing
spaces. The candidate table's five strings match those original values, and
all five candidate PE relocations occur exactly at offsets 0, 4, 8, 12 and 16.
Both complete 20-byte tables reside in read-only storage. No table or string
receives primary exact-byte credit.

The original score-name drawing owner at `0x004538B0` independently covers
861 bytes and 223 reachable instructions. Its indexed table PUSH at
`0x0045398B` uses four-byte elements. A separate fixed ADDSS at `0x00453ABD`
reads the complete 58.0f value from `0x0049461C`. That value also occurs at
another read-only address; only this fixed original read selects storage.

The player-data drawing owner at `0x00453030` independently covers 698 bytes
and 196 reachable instructions. Its three unsigned-division CALLs at
`0x0045320B`, `0x0045321A` and `0x0045322D` reach `0x004876B0`.
That entry has an independently complete 104-byte, 43-instruction original
scope, already derived as the predecessor of the
[conversion-runtime contribution](conversion-runtime.md). Its complete candidate
PDB owner comes from pinned LIBCMT:ulldiv.obj; all 104 raw bytes equal the
original, without address normalization. Its ordinary runtime binding grants
no additional primary callee credit.

The two complete source candidates now replay exactly: player-data drawing
(698) and score-name drawing (861), adding **1,559 exact primary bytes**.
Canonical replay reports **835 exact, 65 mismatch and 315 incomplete**, covering
152,002 exact primary bytes and 900 units. All 833 preceding exact results,
65 complete mismatches and 898 previous units remain retained. All **246
controls across eleven suites** pass, including the seven PDB-type controls.
Existing numeric and runtime mutation cases now cover the new 58.0f read and
both complete unsigned-division extents.
The replay-list owner still has unresolved private formatting-array addresses;
this source change does not give those arrays inferred bounds or identities.

## Evidence

Original table, complete strings, indexed PUSH, 58.0f read and dense score-name
scope are in `.analysis/season-name-original-review.json`, reproduced by
`.analysis/review-season-name-originals.py`. The complete player-data owner and
three original division witnesses are in
`.analysis/season-menu-player-original-scope.json`. The full original/candidate
division pair is `.analysis/season-menu-division-review.json`.

The retained declaration, complete typed table, all strings and relocations,
current artifact hashes, all 1,719 linked owners and all 192 incremental
dependency stamps are checked in `.analysis/season-name-linkage-check.json`,
reproduced by `.analysis/check-season-name-linkage.py`. The baseline source,
configuration, report and complete PE/MAP/PDB output set are retained in
`.analysis/season-name-linkage-baseline/`; the fresh incremental build log is
`.analysis/season-name-linkage-build.log`. No archived outputs are substituted.

Complete caller payloads, fields, relocations, units and strict results are in
`.analysis/season-name-caller-scopes.json`. Canonical and retained-pass evidence
is `.analysis/season-name-full-audit.log`,
`.analysis/season-name-regression-check.json` and
`.analysis/season-name-controls-summary.json`; the regression reproducer is
`.analysis/check-season-name-regression.py`. Control logs use
`.analysis/season-name-<suite>-controls.log`.

Source-origin review remains open and Factory acceptance remains unsubmitted.
Nothing is published.
