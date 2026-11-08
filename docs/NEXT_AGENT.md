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

The eight imported `*_want_aligned_stack` helpers have been removed because
they only introduced dead doubles to influence LTCG. Recover real caller/callee
alignment before restoring any affected exact result. Other explicitly
non-original dead locals and arithmetic remain in the import and still need
source review; a local byte match alone does not settle that review.

The latest local checkpoint has 623 exact, 41 mismatch and 550 incomplete
candidates from an incremental build. All 622 exact results at `c5eff1f` remain
exact. `draw_line` is now a complete 569-byte strict pass through a source-level
vector-indexing change. Both Float2 interpolation functions first differ at
byte 453 rather than 260; collision rotation writes y before x but still has
register differences. These partial improvements remain mismatch.

`world_pos` now uses a direct recursive vector expression, with its imported
artificial local, volatile cast and safebuffers helper removed. Its new GS
cookie makes the candidate 315 bytes versus the original 297, so it remains
incomplete. Recover that compiler/temporary context before claiming exactness.
The source trials and full regression result are in
`knowledge/reference-repairs.md`; no Oracle comparison rule was changed.
