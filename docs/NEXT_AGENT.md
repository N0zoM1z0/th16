# Current handoff

Updated 2026-11-16. Read AGENTS.md first. This handoff supersedes the older
agent-specific instructions and checkpoint figures; historical investigation
notes remain in docs/knowledge/ and .analysis/.

## Repository checkpoint

| Item | Current value |
| --- | --- |
| Branch | main |
| Code checkpoint entering cleanup | 3f7371f — gpt-web: align ECL move-curve handler |
| Source commits | 16 ahead of origin/main at the start of handoff cleanup |
| Worktree | clean after the handoff commits |
| Commit prefix | gpt-web: |
| Publication | local commits only; do not push unless the user asks |
| Candidate build | incremental; receipt timestamp 2026-11-16 14:37:07 UTC |
| Build input SHA-256 | 1295c7d5a4a25471198017bc8be5b7a428286cd1f710c041d88396b0b3fa58b5 |
| Latest saved strict audit | 2026-11-15 06:37:29 UTC; stale for the current candidate |

The saved audit reports **1,033 exact / 51 mismatch / 131 incomplete** of 1,215
annotations, but it predates all 16 commits made on 2026-11-16. It is not the
current result. config/frontiers.toml was last refreshed on 2026-11-15 and is
also historical until regenerated from a fresh audit. The progress report still
lists Factory acceptance as not-submitted.

The current candidate was rebuilt incrementally at 14:37:07 UTC after the
comment-only documentation correction in EnemyEcl.cpp. The build succeeded
with existing C4244 (camera float-to-u8), C4101 (unused local name) and C4731
(EclRunContext inline-assembly frame-pointer) warnings. No fresh whole-project audit,
cold replay or accepted Factory snapshot has been recorded after the 2026-11-16
source changes. scripts/progress.py deliberately refuses a stale report;
run scripts/audit-reference.py before using totals or refreshing the frontier.
Do not treat a successful incremental build or a case-level similarity score
as strict exactness.

## Main active owner: upper enemy ECL dispatcher

EnemyData::ecl_run_over_300() is in src/EnemyEcl.cpp at target address
0x0041DCB0. Its annotated target extent is 21,516 bytes. The separately
reviewed original dispatch/table owner in
docs/knowledge/upper-ecl-frame-store-scope.md is 21,408 bytes; those are
different boundary records and must not be subtracted as if they were the same
scope.

The current candidate PDB contribution is at 0x004344C0, size 20,568 bytes.
Its prologue allocates 0x474 bytes, while the target prologue allocates 0x478.
The saved strict-audit row for this owner is incomplete and has no unit_sha256;
there is no current complete-owner strict pass for it. The historical frame-store
note describes the original boundary and static controls, not the current
candidate layout.

The focused case tool currently finds 174 target and 174 candidate dispatch
targets. Its current non-perfect normalized instruction-sequence groups include:

| Opcode group | Handler family | Ratio |
| --- | --- | ---: |
| [7] | ANM_PLAY | 0.94 |
| [101, 103, 136, 137] | MOVE_POS_TIME variants | 0.86 |
| [109, 111] | MOVE_CIRCLE_TIME variants | 0.85 |
| [134, 135, 138, 139] | MOVE_CURVE variants | 0.95 |
| [140, 142] | MOVE_ANGLE variants | 0.84 |
| [141, 143] | MOVE_ANGLE_TIME variants | 0.85 |

The case tool prints groups below 0.999; omitted groups match under that
normalized case comparator. This is a diagnostic only: it normalizes registers
and branch addresses, and does not compare the complete function extent,
relocations, data tables or ownership. It does not grant Oracle credit.

The 2026-11-16 source work substantially rewrote animation and movement
handlers. The current case report no longer lists the groups for ANM_RESET,
ANM_SET_MAIN, ANM_PLAY_ABS, ANM_PLAY_HIGH, ANM_PLAY_ROTATE,
ANM_SELECTED_PLAY, ANM_316, ANM_SWITCH, MOVE_VEL, MOVE_VEL_TIME,
MOVE_RAND or MOVE_BEZIER as non-perfect. Treat that only as a local
instruction-sequence result, not as proof that the large owner is exact.

### Recommended next work

1. Continue with MOVE_ANGLE_TIME / MOVE_ANGLE_REL_TIME (groups 441/443,
   case indices [141, 143]) and MOVE_ANGLE / MOVE_ANGLE_REL
   (440/442, [140, 142]). These remain ordinary C++ in the dispatcher and
   are still materially different from the target.
2. Revisit MOVE_POS_TIME (401/403/436/437) after understanding the target's
   reused stack slots and getter order. Earlier attempts to inline all getters,
   jump across C++ switch scopes, or overlay frame locals regressed other cases;
   those experiments were restored. The current selector plus first-getter
   sequence is the stable checkpoint.
3. Improve MOVE_CURVE (434/435/438/439) beyond its current 0.95 case score.
   The selector/getter and interpolation setup are partly inline assembly, but
   the shared initial/goal/reset tail and complete owner frame still differ.
4. Revisit ANM_PLAY (307) after the movement work; it remains at 0.94.
5. Once a complete owner scope and comparison unit are available, use the strict
   Oracle on the affected owner. Do not infer exactness from cases.py.

Useful source locations: MOVE_POS_TIME around line 1178, MOVE_CURVE around
1243, MOVE_BEZIER around 1351, MOVE_VEL around 1449, MOVE_VEL_TIME around
1518, and MOVE_ANGLE_TIME around 1723. Line numbers may move.

## Recent committed work

The 16 local commits since the previous checkpoint cover:

- ANM_SELECTED_PLAY, ANM_RESET, ANM_SET_MAIN, ANM_PLAY_ABS,
  ANM_PLAY_HIGH, ANM_PLAY_ROTATE, ANM_316 and ANM_SWITCH;
- MOVE_BEZIER, MOVE_VEL, MOVE_VEL_TIME, MOVE_RAND and MOVE_CURVE.

The commits are local checkpoints, not accepted Oracle receipts. Keep future
commit messages in the user's requested gpt-web: ... format.

## Workflow and retained tools

- Use scripts/repo-python for project scripts and the pinned interpreter.
- Use scripts/repo-python scripts/build.py for incremental builds.
- Use .venv/bin/python .analysis/claude-tools/cases.py 0x41dcb0 for the
  current switch-case diagnostic. It depends on the saved audit to resolve the
  owner symbol, so refresh that audit before relying on it after annotation or
  unit-ledger changes.
- scripts/audit-reference.py refreshes the local strict report;
  scripts/progress.py and scripts/check-frontier.py require that report to
  match current inputs.
- Avoid --clean and whole-project replay for ordinary iterations. The user
  explicitly prefers affected-owner work and multiple local checkpoints.
- Keep build/reference-candidate/ intact: its objects, dependencies, PDB,
  MAP, receipt and symbol-discovery cache support incremental work.
- Keep resources/th16.exe, .venv/, .tools/wine/, ghidra-project/ and the
  pinned _reference/johnthreekay-th16/ checkout. See docs/ARTIFACTS.md before
  any further cleanup.
- Historical .analysis/claude-tools audit JSON, source snapshots, trial logs
  and diagnostic binaries are now gzip-compressed. The cleanup index
  .analysis/cleanup-handoff-20261116.json records hashes and restore metadata;
  use gzip -dc to restore an individual file. exp.json and cur-audit.json are
  old audit snapshots, not current results; they remain uncompressed because
  tryaudit.sh and moved.py read those literal paths. build.log also remains
  uncompressed as a build-success sentinel.
- Most generated p/ and fp/ probe outputs were removed; their source probes
  and generators remain. The two p/mbi.exe and p/mbi.map outputs were retained
  because no matching C++ source was found.

## Historical findings worth retaining

- Direct calls and __forceinline helpers can change LTCG alignment and
  inlining; pointer-to-member workarounds often alter register scheduling.
- Where the original pushes a different constant in each branch before one
  shared call, preserve whole branch-specific calls rather than computing an
  argument index arithmetically.
- Read call arguments into locals in the original order when the call sequence
  matters. Statement shape, temporary type and local lifetime can change
  register allocation and frame alignment.
- COMDAT providers depend on link order; a CRT inline's out-of-line copy may
  come from the first object whose IL uses it.
- Intrinsic treatment can fold static initialization; pragma function around
  the affected operation can restore the original initializer.
- Dead code can retain EH states and affect frame layout.
- Historical dead ends and source trials are preserved in the dated .analysis/
  evidence archives; do not replay their expected counts as if they described
  this checkpoint.
