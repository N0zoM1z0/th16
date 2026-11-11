# Current handoff

Updated 2026-11-11 after the complete AnmManager callback scope review.
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

The current report has **709 exact, 52 mismatch and 454 incomplete** among
1215 annotated candidates, covering 117,308 exact owned bytes. All 668 exact
results at `efb48b8` remain exact. The original AnmManager constructor independently
establishes 39 draw registrations and two tick registrations. All 41 complete
callbacks pass, adding 1,182 bytes. See
[AnmManager callback evidence](knowledge/anm-callback-scopes.md). The constructor
entry also has an original WinMain direct-call witness. Neither candidate sizes
nor artifacts enter the original callback scope derivation.

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
cache and non-LTCG symbol-discovery cache are retained. This batch adds 41
original inventory rows and unknown/review source-origin rows. No game source,
compiler profile, Oracle or binding implementation changes; no rebuild is needed.
All 720 prior comparison units are unchanged, alongside 41 new complete units.
The preceding Replay local cleanup remains: its ordinary recorded-input local
produces a complete 281-byte candidate against the 337-byte original. The body
is incomplete. Do not restore forced accesses to imitate its unexplained spill.
PosVel retains its direct wave vector addition and indexed circle/drift-center
forms. Other recent source trials were restored; read the repair log before
repeating them. WinMain's earlier natural cleanup remains; its complete 2919-byte
extent still mismatches.

The current batch passes **17 controls across two relevant suites**: focused
audit and strict Oracle. Logs use
`.analysis/anm-layer-{focused,oracle}-controls.log`. The earlier full control
checkpoint passed 140 controls across nine suites. Original scope derivation
and disassembly are in `.analysis/reviewed-anm-layer-scopes.json`; its original-only
reproducer is `.analysis/review-anm-layer-scopes.py`. The current full replay and
retained-pass evidence are `.analysis/anm-layer-boundary-full-audit.log` and
`.analysis/anm-layer-boundary-regression-check.json`. The unchanged incremental
build log remains `.analysis/record-input-cleanup-build.log`.

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

The 454 incomplete candidates comprise 237 with unresolved fields, **56 missing
independently reviewed original boundaries**, 113 genuine candidate/target extent
differences, 40 without a same-start contribution, six with source-object
ownership differences and two requiring reviewed switch or owned-data extents.
The earlier combined extent reason hid missing inventory rows; the Oracle now
distinguishes these two refusal cases. Start from their recorded reasons.

The 5,071-byte AnmManager constructor has one unresolved handler field. Its
nonempty EH graph is investigated in
[AnmManager callback evidence](knowledge/anm-callback-scopes.md#constructor-eh-investigation-remains-separate)
and `.analysis/anm-constructor-eh-investigation.json`. Five unwind actions and
the handler share one complete 136-byte candidate code contribution; FuncInfo
and its five-state unwind map share one complete 76-byte metadata contribution.
The 27-byte handler is an interior entry, not a standalone PDB owner. Review
both whole contributions, all permitted internal symbols, original inventory
subscopes, relocations, state edges, frame dependencies and runtime entries
before extending the Oracle.
The existing empty-EH3 proof remains unchanged and does not accept this graph.

The 35 original references in `.analysis/callback-entry-inventory.json` have
reviewed roots. A second discovery index,
`.analysis/missing-entry-reference-discovery.json`, records 84 instruction
references to 74 formerly missing entries. The 41 AnmManager entries are now
reviewed; 33 other referenced roots remain unreviewed and 23 of the remaining
56 entries lack such a witness. These references were discovered through
original inventory bodies and are discovery evidence only. Their parent paths,
entry roles and complete control-flow/owner scopes still need review.
Establish each role, all reachable paths, complete scope, padding and absence
of conflicting owners before adding a row. Do not import every annotation or
copy candidate sizes into the original ledger. Indirect calls in the reviewed
callbacks have individually recorded operands and ordinary continuations; this
does not authorize indirect jumps or grant callee exact credit.

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
