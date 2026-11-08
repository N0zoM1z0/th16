# Current handoff

The user has authorized importing the pinned reference candidates and evaluating
them with the local Factory/TH10-style strict Oracle. Maintained code, comments
and documentation must be English, except for the Japanese game title. Do not
use REA.
Do not push branches or tags, mirror this repository or publish its contents
remotely. Local commits are allowed; only the user can revoke this restriction.

- The canonical target is `resources/th16.exe`, original Japanese v1.00a.
- The historical compiler/SDKs, shared Ghidra/JDK/Wine and game-local state are
  configured. Full PDB linking also uses the pinned rootless Wine NTLM helper.
- Candidate game source is in `src/`. Compiler-context callers and opaque
  support are in `probes/reference-harness/` and `probes/reference-support/`.
- `_reference/johnthreekay-th16` remains pinned and unchanged at
  `2b846da735ac71f68b1dc74e8194c8c8d98e2869`. Source provenance is recorded in
  `config/reference-sources.csv`; README credits the upstream contributors.
- `scripts/build.py` reuses objects with matching dependency/flag hashes and
  performs a full LTCG link through the game-owned Wine prefix. It records
  source/profile/artifact identity. Use `--clean` for a meaningful milestone or
  a demonstrated dependency/cache problem, rather than each source batch.
- `scripts/audit-reference.py --write-units` performs the independent strict
  comparison. `scripts/progress.py` reads current results after checking their
  freshness. The upstream comparators and library-signature scanner are absent
  from this verification path.
- Local comparison results are separate from source-origin review and Factory
  acceptance. The local Factory registration remains inventory-only; this work
  has not activated it on the live service or submitted acceptance receipts.

See `REFERENCE_IMPORT.md` for comparison scope, limitations and commands. Preserve
ignored reports, logs, projects, prefixes and build artifacts. Start with the
recorded mismatch and incomplete reasons before modifying any game function.
The original import audit is `evidence/reference-import-20261108/README.md`.
See `knowledge/reference-repairs.md` for subsequent source fixes and unsuccessful
experiments, and `knowledge/reviewed-linkages.md` for fixed linkage evidence.
Run `scripts/progress.py` for the current validated result.

The eight imported `*_want_aligned_stack` helpers and 86 explicitly artificial
standalone locals have been removed. Unused parameters, unknown structure
fields, ABI macros and compiler-context harnesses were preserved. The cleanup
withdrew 23 previous exact results; recover real types and calling context rather
than restoring dead metadata. Other compiler-context helpers and forced-access
hypotheses still need source review; a local byte match alone does not settle it.

The current checkpoint has 614 exact, 49 mismatch and 551 incomplete candidates.
All 600 natural-source passes after cleanup and all 608 passes at `1a32210`
remain exact. Five new runtime identities made eight consumers exact; complete
RTTI/PDB proofs for ThreadInf and Pbg::File primary vftables made six more exact.
Game code and build artifacts were unchanged for this linkage-evidence batch.

The new `scripts/vtable_identity.py` is part of the Oracle input fingerprint.
It validates complete storage including the locator prefix, terminated type
names, entire single-inheritance graphs, relocated slot pointers and independent
callee identities. Its 29 controls include full ThreadInf destructor replay and
reject truncated/ambiguous data, wrong class/namespace/slots, missing relocation,
unsupported hierarchy and address-point misuse. The complete 88-control suite
passes. The comparison still requires the same full code extents and exhaustive
byte/field replay; this is not Factory acceptance or source-origin acceptance.

`draw_line` remains a complete 569-byte pass. `world_pos` still has an unresolved
GS-cookie/extent difference. The four-form non-LTCG probe and Int3 interpolation
trials are recorded in `knowledge/reference-repairs.md`; do not repeat those
failed forms or normalize their remaining bytes. Continue from the current
mismatch/incomplete evidence and preserve the ignored analysis artifacts.
