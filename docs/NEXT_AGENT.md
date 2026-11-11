# Current handoff

Updated 2026-11-11 after complete private sincos helper ownership review.
This file describes current state; the repair log records historical batches.

## Constraints

- Do not push branches or tags, mirror the repository or publish its contents.
  Local commits are allowed. Only the user can revoke the publication restriction.
- Maintained code, comments, documents and commit messages must be English,
  except for the Japanese game title. Do not use REA.
- Use our Factory/TH10-style strict Oracle. Upstream similarity scores,
  comparison scripts and exact labels have no acceptance authority.
- Write natural C/C++ and compare complete owners. Do not restore dead locals,
  padding helpers, byte masks or truncated ranges to recover a match.
- Use incremental builds and focused complete-owner comparisons for iterations.
  Reserve a clean build and broad replay for a milestone or a cache problem.

## Verified checkpoint

The current report has **779 exact, 58 mismatch and 378 incomplete** among
1215 annotated candidates, covering 125,082 exact owned bytes. All 767 exact
results at `effbba5` remain exact. Three explicitly reviewed complete 32-byte
private helpers now have qualified source/MAP/PDB identities. Their callers
retain exact whole-entry CALL bindings without public-symbol promotion.
Twelve complete exact owners add 4,470 bytes; five formerly incomplete owners
become complete mismatches. All 820 preceding units remain unchanged, with
17 new complete units, for 837 total. See
[private sincos ownership](knowledge/static-sincos-ownership.md).

The preceding original-only review establishes
24 callback-table/startup owners, including the Camera entry and the global
initializer which calls it. Twenty-two complete owners pass. The independently
reviewed `300.0f` binding also resolves Stage::load_data's final field, allowing
its complete 473-byte owner to pass. These 23 additions cover 1,395 primary
bytes. All 797 preceding comparison units remain identical, alongside 23 new
units, for 820 total. See [table entry scopes](knowledge/table-entry-scopes.md).

The preceding original-only review establishes
13 missing runtime callback/helper entries and partitions the unreviewed
313-byte LZSS aggregate into three complete owners plus all 25 INT3 bytes.
All 14 complete owners pass, adding 1,305 bytes. See
[runtime entry scopes](knowledge/runtime-entry-scopes.md). All 783 preceding
comparison units remain identical, alongside 14 new units, for 797 total.

The preceding original-only review establishes
20 registered manager callbacks and one Ascii drawing helper reached by a
registered callback's tail transfer. All 21 complete owners pass, adding
604 bytes. See [manager wrapper scopes](knowledge/manager-wrapper-scopes.md).
All 762 previous comparison units remain identical, alongside 21 new units.

The original AnmManager constructor independently
establishes 39 draw registrations and two tick registrations. All 41 complete
callbacks pass, adding 1,182 bytes. See
[AnmManager callback evidence](knowledge/anm-callback-scopes.md). The constructor
entry also has an original WinMain direct-call witness. Neither candidate sizes
nor artifacts enter the original callback scope derivation.

The constructor's nonempty EH graph now has an explicit complete-owner profile:
136 code bytes and 76 metadata bytes, with all interior names, relocations,
state edges, frame dependencies and cleanup/runtime entries checked. Its entire
5,071-byte primary owner now compares as a mismatch, with 5,054 matching bytes
and 17 differences in one UpdateFunc constructor store-order interval. See
[the aggregate review](knowledge/anm-constructor-eh.md). No new exact credit
is granted by the EH review. Its complete constructor mismatch unit is retained.

The preceding 26 passes, including the 442-byte Replay playback body, remain
exact; see [registered callbacks](knowledge/registered-callbacks.md). The seven
earlier Bullet, Effect and Item callbacks also remain exact; see
[manager callbacks](knowledge/manager-callbacks.md). PosVel remains a 696/700-byte
mismatch after its earlier source improvement.

The preceding EH review established complete passes for the 70-byte
`ItemManagerInner::~ItemManagerInner` and 73-byte `StageInner::~StageInner`.
Their complete private graphs remain checked; see
[EH ownership evidence](knowledge/eh-handlers.md). Auxiliary handlers and runtime
bindings receive no additional primary exact credit.

The preceding batch established six passes with complete bounded switch tables
and a seventh masked-effect initialization pass using its reviewed `240.0f`
literal. See [switch ownership evidence](knowledge/switch-ownership.md).

These are local code-comparison results. Source-origin review remains open;
`config/implemented.csv` has no implemented entries. Factory registration is
inventory-only, has not been activated on the live service, and no Truth Kernel
acceptance receipts have been submitted.

The current build receipt is incremental. Its PE, MAP, PDB, function map, object
cache and non-LTCG symbol-discovery cache are retained. The preceding callback
batch added 41 original inventory rows and unknown/review source-origin rows.
The preceding batch extended the EH verifier with one explicitly reviewed
aggregate profile. The preceding callback-table batch adds a fixed literal
binding. The current batch adds `scripts/static_identity.py` and
`config/static-functions.toml`, with explicit private primary/callee selection
in the strict Oracle and audit. Default public ownership, unreviewed static
names and EH profiles retain their refusal behavior. All whole private bytes,
producer identity, annotation identity, original witness paths and absence of
linked fields/relocations are required. Game source, compiler/linker profiles
and the attested incremental outputs are unchanged; no rebuild is needed.

An ordinary out-of-line UpdateFunc constructor was built incrementally as a
source-context experiment. It removes redundant initialization stores and
changes eight complete linked owner extents, including create_func 106 to 77
bytes and AnmManager 5071 to 4046. It does not reproduce the original. Trial
sources and complete outputs are retained under
`.analysis/updatefunc-ordinary-out-of-line-artifacts/`. Baseline sources and
attested outputs were restored after checking the full source-input identity
and every artifact hash; see `.analysis/updatefunc-context-restore-check.json`.
That checkpoint retained the baseline incremental receipt and invalidated 104
trial dependency stamps naturally. The current batch has now rebuilt those
dependencies incrementally, tried two PlayerShot source contexts and rebuilt
the restored source. The current artifacts and receipt are freshly produced;
all 192 object dependency stamps are valid. See
`.analysis/piercing-restored-cache-check.json`. No archived outputs were
substituted and no clean build was run.

The piercing hit callback at `0x004474A0` has a complete 39-byte original and
40-byte baseline candidate. An element pointer gives 37 bytes; a bullet-array
base pointer gives 41 bytes. Both natural contexts fail complete-owner
comparison and are restored. Their full outputs, source and instructions are
retained under `.analysis/piercing-{element-pointer,array-base}-artifacts/` and
`.analysis/piercing-source-context-trials.json`. Do not repeat these trials or
force registers/accesses to reproduce the original operand allocation.
The preceding Replay local cleanup remains: its ordinary recorded-input local
produces a complete 281-byte candidate against the 337-byte original. The body
is incomplete. Do not restore forced accesses to imitate its unexplained spill.
PosVel retains its direct wave vector addition and indexed circle/drift-center
forms. Other recent source trials were restored; read the repair log before
repeating them. WinMain's earlier natural cleanup remains; its complete 2919-byte
extent still mismatches.

The current batch passes **114 controls across six relevant suites**: private
identities (21), strict Oracle (14), reviewed linkages (26), focused audit (3),
constructor EH (25) and empty EH (25). Logs use
`.analysis/static-sincos-{controls,oracle-controls,linkage-controls,focused-controls}.log`
and `.analysis/static-sincos-{constructor,empty}-eh-controls.log`. The preceding
callback-table batch passes 43 controls; its logs use
`.analysis/table-entry-{linkage,oracle,focused}-controls.log`. The preceding
runtime entry batch passed 17 controls; its logs use
`.analysis/runtime-entry-{oracle,focused}-controls.log`. The manager wrapper
checkpoint's corresponding logs use
`.analysis/manager-wrapper-{oracle,focused}-controls.log`. The preceding EH
checkpoint passed 92 controls across five suites; its logs use
`.analysis/anm-constructor-{eh,empty-eh,oracle,linkage,focused}-controls.log`.
The earlier full control checkpoint passed 140 controls across nine suites.
Original scope derivation and disassembly are in
`.analysis/reviewed-anm-layer-scopes.json`; its original-only
reproducer is `.analysis/review-anm-layer-scopes.py`. The manager wrapper
reproducer and scopes are `.analysis/review-manager-wrapper-scopes.py` and
`.analysis/reviewed-manager-wrapper-scopes.json`. The preceding original-only
runtime derivation is `.analysis/review-runtime-entry-scopes.py` and
`.analysis/reviewed-runtime-entry-scopes.json`. The latest original-only
table derivation is `.analysis/review-table-entry-scopes.py` and
`.analysis/reviewed-table-entry-scopes.json`. The current original-only private
scope evidence is `.analysis/static-sincos-original-scopes.json`; the maintained
verifier rechecks the full originals and paths. Current replay and retained-pass
evidence are `.analysis/static-sincos-full-audit.log` and
`.analysis/static-sincos-regression-check.json`. The current incremental build
log is `.analysis/piercing-restored-build.log`; the older baseline is
`.analysis/record-input-cleanup-build.log`. The rejected
source trial is `.analysis/updatefunc-ordinary-out-of-line-build.log`.

```sh
.venv/bin/python scripts/progress.py
```

Run this first: it checks source, artifact, report and retained-unit freshness.
The current report is `.analysis/reference-audit.json`; complete retained units
are in `config/match-units.toml`. See [REFERENCE_IMPORT.md](REFERENCE_IMPORT.md)
for the comparison contract and [reviewed linkage evidence](knowledge/reviewed-linkages.md)
for fixed runtime, literal and vftable identities.

## Environment and workflow

- Canonical target: `resources/th16.exe`, original Japanese v1.00a, SHA-256
  `c11776019f083978e66027e7394dafb1fb9543afca986f28049a49417e341929`.
- Shared historical MSVC 19.10.25017, SDKs, Ghidra/JDK/Wine and the pinned Wine
  NTLM helper are configured. Prefix, analyzer project and runtime state are
  game-local. See [SHARED_TOOLS.md](SHARED_TOOLS.md).
- Game code is under `src/`; separate compiler-context callers and opaque support
  are under `probes/reference-harness/` and `probes/reference-support/`.
- `_reference/johnthreekay-th16` is unchanged at
  `2b846da735ac71f68b1dc74e8194c8c8d98e2869`. Provenance is recorded in
  `config/reference-sources.csv`; README retains upstream credits and CC0.

For a source iteration:

```sh
.venv/bin/python scripts/build.py
.venv/bin/python scripts/compare-linked-function.py reference-00408260
```

Choose a retained unit relevant to the change. For an annotated owner with no
retained unit, or after an extent/linkage change, run a focused diagnostic:

```sh
.venv/bin/python scripts/audit-reference.py --address 0x407900 --json .analysis/masked-switch-focused.json
```

Repeat `--address` for a bounded batch. This retains all independent symbol
bindings and compares full owners, while writing only a separate ignored
report. It cannot update canonical reports, units or ledgers. A changed source
or header makes the previous audit stale; after a coherent batch, regenerate
units and results:

```sh
.venv/bin/python scripts/audit-reference.py --write-units
.venv/bin/python scripts/progress.py
```

No rebuild is needed for prose edits. Oracle/binding edits require a new audit
because their content is fingerprinted; they do not inherently require a new
compile. Do not run checks that read generated ledgers concurrently with an
audit writing those ledgers.

## Outstanding work

The 378 incomplete candidates comprise 205 with unresolved fields, 128 genuine
candidate/target extent differences, 37 without a same-start contribution,
six with source-object ownership differences and two requiring reviewed switch
or owned-data extents. None is currently refused specifically for a missing
original boundary. Other missing evidence can precede boundary checks; this
does not prove every annotation already has a complete original scope review.
The earlier combined extent reason hid missing inventory rows; the Oracle now
distinguishes these two refusal cases. Start from their recorded reasons.

The new private profile covers gather `0x00406470`, bullet `0x00417510` and
laser `0x0043AD00` only. It requires the full 32-byte x87 sincos/scale body,
source-qualified private MAP name, unique complete PDB producer and exact
annotation/witness identities. Primary units and direct CALL fields opt in
explicitly with `reviewed_static`; no interior/addend, public alias, generic
static fallback or tail transfer is permitted. The consumed source/name
inventory metadata is fingerprinted. Existing sincos wrappers remain source
context hypotheses; no game source or assembly was changed by this review.

Other wrappers listed in build/reference-candidate/functions.txt still require
independent original entry/path and complete producer reviews. The AnmVmRun
helper at `0x00464D60` has calls within `update_special_vertices`, but the
initial direct-branch path search does not reach its first call: its dispatch
needs original review. Do not silently follow arbitrary indirect jumps.
The new full 412-byte LaserLine/LaserCurve angle units each differ in 11 bytes
at +0x33..+0x3D, where a float load and argument push have different order.
Their unit names are reference-00432c20 and reference-004392c0. The curve angle
acceleration unit reference-00439460 differs in 14 bytes around +0x83..+0x90.
These are useful source-context targets; preserve complete extents and avoid
forcing instruction order. Two other newly retained laser owners also mismatch.

The complete AnmManager constructor is now a retained 5,054/5,071-byte mismatch.
Its EH profile checks both whole 136/76-byte contributions; the handler remains
an explicitly scoped interior entry rather than a standalone PDB owner. See
[the aggregate review](knowledge/anm-constructor-eh.md). Its 17 differing bytes
are within `+0xABE..+0xACF`: the original clears two callback fields before flag
bit zero, whereas the candidate clears the flag first. All 164 primary linkages
are compared. The retained volatile-this accesses in the shared UpdateFunc
constructor remain a source/context hypothesis. Recover that context rather
than special-casing one registration or forcing the instruction order. Other
nonempty EH graphs still need independent complete-owner review; do not
generalize this explicit profile to arbitrary tables or interior symbols.
Moving an ordinary constructor definition to UpdateFunc.cpp alone has now
been tested and rejected against complete owners; do not repeat that trial.

The 35 original references in `.analysis/callback-entry-inventory.json` have
reviewed roots. A second discovery index,
`.analysis/missing-entry-reference-discovery.json`, records 84 instruction
references to 74 formerly missing entries. The 41 AnmManager entries and 20
further registered callbacks are now reviewed. That review also derives
the Ascii drawing helper from its registered caller's tail transfer. The latest
review establishes the other 13 referenced roots through worker creation,
array constructor/destructor iteration, registry insertion and LZSS tail
transfers. All 74 roots in that discovery index now have reviewed scopes.
The 21 data-address locators in `.analysis/missing-entry-pointer-discovery.json`
now have reviewed original callback-cell roles and complete scopes. The review
also derives the gather switch entry at `0x00405F20`, which had been hidden
behind an unresolved-field refusal. Camera has an original relative-call
witness at `0x004010B8`; the caller is reached through the complete bounded
16-cell CRT initializer interval. Its complete 194-byte original scope is also
reviewed, but its candidate still lacks a complete same-start PDB contribution.
The original PE has no base-relocation directory; raw occurrences are not
relocation evidence. Event callback cell windows do not prove complete global
array extents or arbitrary selector validity. No table data exact credit or
generic indirect-jump allowance is added. Continue from unresolved fields and
source/context differences, retaining all unknown ownership and bounds.

The LZSS deletion row at `0x00458370` is now 84 bytes through `0x004583C3`.
The independently reached tail helpers at `0x004583D0` and `0x00458430` own
83 and 121 bytes. All 313 bytes in the superseded Ghidra region are accounted
for by those owners and 25 INT3 bytes. Do not restore the overlapping aggregate.
Three bounded parent switches are used only to establish witness paths in the
latest review. They do not have accepted complete comparison-owner profiles.

The eight imported alignment helpers and 86 explicitly artificial standalone
locals were removed. The latter cleanup withdrew 23 earlier exact results;
all 600 passes after cleanup remain exact. Recover real types and calling
context rather than restoring the artificial inputs. Other compiler-context
helpers, forced accesses and type hypotheses still need source review.

The eight reviewed bounded switch scopes are complete. `PosVel::step` and
`anm_masked_effect_on_switch` still mismatch, with four and 45 differing bytes
respectively; neither receives exact credit.
The two remaining unreviewed indirect dispatches have different evidence needs.
Do not generalize the single-table proof to multiple or unbounded tables.
Read the final repair-log section before retrying PosVel vector-expression
variants, VM deletion aliases, precomputed render limits or shake timer helpers.
The circle constructor has now been simplified in isolation: this regresses
the complete owner and also changes wave scheduling. The current 696/700 result
retains the indexed circle form. Remaining circle
operand order needs better source/type/context evidence; do not normalize it.

The two reviewed empty-EH3 graphs are complete. Their selectors require the
exact parent-derived private MAP names, full source-object PDB ownership and
complete 27/36-byte handler/descriptor extents. Do not extend this proof to
nonempty unwind/try tables or another handler shape. Identical metadata from
another parent is explicitly rejected. Continue from unresolved-field reasons
or the remaining source/type differences; the isolated PosVel circle trial is
complete and rejected.

`draw_line` is a complete 569-byte pass. `world_pos` has a GS-cookie/extent
difference. Int3 interpolation at `0x00464590` differs in one SIB byte. Float2
interpolation, points-in-rectangle and ECL argument-pointer trials also remain
unresolved. Read [reference-repairs.md](knowledge/reference-repairs.md) before
repeating their failed expression, temporary-variable or helper variants.

The latest bounded trials also reject source/count-scope changes in
`AnmVm::load_from`, carrying the Float2 timer/vector repair into Float3, and
indexed scalar additions in the bullet cancellation half step. See the final
repair-log section before repeating them. The original `floor` root has a
2991-byte Ghidra extent with a distant fallback, not the candidate's 253-byte
contribution; it remains unbound.

`__CIatan2` is a promising evidence investigation, not an accepted runtime
binding. Its two explicit MASM procedure records share one complete 20-byte
contribution. The [investigation note](knowledge/reference-repairs.md#unfinished-atan2-entry-investigation)
records the native evidence and the withdrawn draft. Do not infer an interior
entry from a public label or shorten a contribution to obtain exact credit.

## Local artifacts

See [ARTIFACTS.md](ARTIFACTS.md) before cleanup. Historical reports and large
unused dumps are compressed; the current report remains plain JSON. The cleanup
manifest is `.analysis/cleanup-20261108.json`. Keep current build objects, PDBs,
receipts, the private target, reference checkout, Wine prefix and Ghidra project.
