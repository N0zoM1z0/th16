# Current handoff

Updated 2026-11-08 after local checkpoint `a928c07` and handoff cleanup.
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

The current report has **620 exact, 49 mismatch and 545 incomplete** among
1214 annotated candidates, covering 111,466 exact owned bytes. All 614 exact
results at `c1b5ada` remain exact. The last six gains are complete laser
constructors and a clone consumer after reviewing all five 26-slot vftables.

These are local code-comparison results. Source-origin review remains open;
`config/implemented.csv` has no implemented entries. Factory registration is
inventory-only, has not been activated on the live service, and no Truth Kernel
acceptance receipts have been submitted.

The current build receipt is incremental. Its PE, MAP, PDB, function map, object
cache and non-LTCG symbol-discovery cache are retained. Handoff cleanup changed
no maintained game C++ or Oracle comparison code. The unvalidated atan2 draft
was withdrawn before handoff, so it grants no binding or exact credit.

Handoff verification passed all 89 controls across the six existing test suites
(strict Oracle, reviewed linkages, pointer limits, PDB types, build context and
vftable identities). The log is `.analysis/handoff-controls.log`. Toolchain
component hashes and report freshness also passed; no game build was needed.

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

Choose a retained unit relevant to the change. A changed source or header makes
the previous audit stale; after a coherent batch, regenerate units and results:

```sh
.venv/bin/python scripts/audit-reference.py --write-units
.venv/bin/python scripts/progress.py
```

No rebuild is needed for prose edits. Oracle/binding edits require a new audit
because their content is fingerprinted; they do not inherently require a new
compile. Do not run checks that read generated ledgers concurrently with an
audit writing those ledgers.

## Outstanding work

The 545 incomplete candidates comprise 247 with unresolved fields, 250 with
candidate/target extent differences, 40 without a same-start contribution,
six with source-object ownership differences and two requiring reviewed switch
or owned-data extents. Start from their recorded reasons.

The eight imported alignment helpers and 86 explicitly artificial standalone
locals were removed. The latter cleanup withdrew 23 earlier exact results;
all 600 passes after cleanup remain exact. Recover real types and calling
context rather than restoring the artificial inputs. Other compiler-context
helpers, forced accesses and type hypotheses still need source review.

`draw_line` is a complete 569-byte pass. `world_pos` has a GS-cookie/extent
difference. Int3 interpolation at `0x00464590` differs in one SIB byte. Float2
interpolation, points-in-rectangle and ECL argument-pointer trials also remain
unresolved. Read [reference-repairs.md](knowledge/reference-repairs.md) before
repeating their failed expression, temporary-variable or helper variants.

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
