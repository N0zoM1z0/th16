# Current handoff

Updated 2026-11-13 for transfer to another agent. The user replaced ongoing
reconstruction with documentation and storage cleanup. That cleanup is complete;
resume reconstruction only under the next task. Read `AGENTS.md` first.
The previous 1,418-line handoff is preserved as the indexed historical file
`.analysis/handoff-next-agent-fe98fb8.md.gz`. Its older counts and next steps
are historical, not current instructions.

## Current checkpoint

The reconstruction base is local commit `fe98fb8`. All later game-source trials
are restored byte for byte; no game source or Oracle rule changes are retained
by this handoff cleanup. The incremental restoration build and isolated
canonical audit completed before documentation/archive-tool changes.

| Item | Current value |
| --- | --- |
| Local strict results | **904 exact / 67 mismatch / 244 incomplete** |
| Annotations / unit definitions | **1,215 / 971** |
| Exact primary bytes | **185,816** |
| Restored PDB age | **624**; preceding baseline **619** |
| Native source-qualified owners | **1,719**, totaling **527,136 raw bytes** |
| Source-origin review | Open |
| Factory acceptance | Not submitted |

Source input SHA-256 is
`ef45258398eb6fe5c3cb4fd560aed06455b5f5695cfb4d398602eb739e51ccc5`.
All annotation results/diagnostics, unit definitions, native-owner bytes,
addresses/extents, base relocations and complete raw `.text` are unchanged
from the PDB 619 baseline. Source exactness does not imply Factory acceptance.

Evidence remains directly accessible in `.analysis/projectile-ex-source-work/`:
`baseline-image/`, `final-image/`, baseline/final reports, `baseline-units.toml`,
`handoff-regression.py`, `handoff-regression.log`, `final-regression.json`,
`handoff-audit.log` and `handoff-progress.txt`. No game execution or emulation
was used for this restoration or cleanup. No build/audit job remains running.

## Reconstruction priority and constraints

The user explicitly prioritizes **exact source reconstruction**, including
substantial Boss, enemy, interpreter and projectile functions. Dynamic testing
is not requested. Do not create/run native game fixtures, behavior matrices or
emulation as a substitute for exact source work. Historical native diagnostics
remain evidence, not the next workflow.

- **Never push**, mirror or publish this repository. Local commits are permitted.
- Do not use REA or borrow another game's Wine prefix/analyzer project.
- Use natural C/C++ and complete independent owner comparisons, including owned
  tables/maps, extents, linked fields and relocations. Build success, reference
  labels, partial matching bytes and equivalent instructions grant no exact credit.
- Do not force registers, add dead storage/padding, mask differences, truncate
  owners or alias private callees without independent original evidence.
- Preserve dirty work and required ignored evidence. Use incremental builds;
  reserve a cold build for a meaningful milestone or a proven cache problem.
- Do not edit source/verifiers while a build or Oracle Context is live. Do not
  read progress/ledgers or run controls alongside `audit-reference.py --write-units`.
  Focused diagnostics must use a separate report path.
- Write maintained code, comments, documents and commits in English; only the
  Japanese game title is excepted.

## Substantial open owners

Counts below describe complete scopes. Matching-byte counts are diagnostics,
not partial acceptance. Consult the linked review before trying another form.

| Owner | Current complete finding | Review |
| --- | --- | --- |
| `EnemyData::ecl_run_over_300`, `0x0041DCB0` | Original **21,408**, candidate **21,316** bytes; seven unbound fields; frame `0x478` / `0x498` | [Upper ECL scope](knowledge/upper-ecl-frame-store-scope.md) |
| `EclRunContext::ecl_run`, `0x00472030` | Original **7,046**, candidate **6,942** bytes; zero unbound fields, still incomplete | [ECL order/private callee](knowledge/ecl-interpreter-order-and-private-callee.md) |
| `EnemyData::step_logic`, `0x0041C330` | Original **2,207**, candidate **2,197** bytes; damage/statistics/life and collision allocation remain open | [Boss flag expression](knowledge/boss-hit-effect-flag-width.md), [lifetime trials](knowledge/large-owner-source-lifetimes.md) |
| `EnemyData::step_interpolators` | Complete **1,692** bytes; **1,682** matching; camera/VM join remains open | [Motion frame](knowledge/enemy-motion-frame-and-vm-join.md) |
| `Bullet::run_ex`, `0x00413860` | Original **5,436**, candidate **5,500** bytes; differences across handlers and frame | [Dispatcher source](knowledge/laser-initialization-and-bullet-dispatch.md), [last trials](knowledge/projectile-source-trials-handoff.md) |
| Curve reverse-step | Complete **986** bytes; **982** matching; differences at offsets 770, 779, 787, 791 | [Lifetime trials](knowledge/large-owner-source-lifetimes.md), [last trials](knowledge/projectile-source-trials-handoff.md) |
| `sht_on_hit_laser` | Complete **1,409** bytes; **912** matching after retained endpoint operand repair | [Laser/orb review](knowledge/orb-and-laser-hit-source-trials.md) |
| Full animation interpreter | Original **14,177**, candidate **14,141** bytes | [Complete interpreter trials](knowledge/interpreter-and-laser-complete-owner-trials.md) |

The upper ECL scope is already formally registered. Its former **19,976-byte**
boundary was code-only. The complete 21,408-byte original includes all 4,519
reachable instructions, 182 target entries, the 702-byte map and alignment.
The next entry is `0x00423050`. Explicit `compound-frame-store-v1` proves the
remap-adjacent immediate local store with the original stable GS/EH frame;
all store bytes remain comparison input. All 40 simple/39 compound controls
passed at `fe98fb8`. Scope registration does not make the function exact.
Do not reopen its former generic refusal or bind its helper to the lower ECL
producer. The lower private `ecl_sincosmul` closure is independently verified.

Recent rejected forms are documented in
[large-owner lifetimes](knowledge/large-owner-source-lifetimes.md),
[upper ECL cases](knowledge/upper-ecl-frame-store-scope.md) and
[projectile handoff trials](knowledge/projectile-source-trials-handoff.md).
In particular, the last duplicated-sound trial only compiled: it was saved
unreviewed and reverted when the task changed. No pending source edit remains.
Do not report it as validated or exact. Earlier trial details remain in the
[knowledge index](knowledge/README.md) and [repair history](knowledge/reference-repairs.md).

## Unvalidated initialization proof draft

`.analysis/experiments/audio-initialize-unvalidated/` contains a withdrawn
Oracle/source draft based on `6427da9`; `.analysis/audio-initialize-baseline/`
remains uncompressed. A positive focused 708-byte result under draft rules
received no completed negative suite or canonical regression. It is **not
accepted progress**. Do not install the draft or update counts from it.

`SoundManager::initialize` at `0x0045D510` still requires proof of:

1. The complete 37-byte handler, 44-byte metadata and parent cookie/frame/state
   graph (node-96 and node-4, one terminal state, flags one).
2. The ESI cursor from sound-table+4, stride twenty, limit sound-table+1564,
   including all paths, side exits, non-dereferenced limit and preservation
   through every normal return of the complete 702/713-byte loader owners.

Read the draft README and `.analysis/audio-initialize-next-proof-inventory.json`.
Review gaps include DI/DIL Sleep-tag invalidation, SI/SIL cursor uses, complete
metadata ownership, stack writes, cleanup/returns and exceptional paths.
A PUSH or positive caller comparison alone proves no contract. Do not enlarge
the typed table or borrow the adjacent array identity. Active rules still refuse
both fields. `SoundBufferEntry::load` retains an ambiguous data tag and unequal
extents; its two strncmp fields are already resolved.

Other unresolved small differences (volume, Unpause, interpolation SIB bytes)
are recorded in the knowledge files. Do not normalize them or repeat rejected
scalar variants without a new hypothesis. Prefer substantial owners next.

## Tools and evidence access

The canonical private target is `resources/th16.exe`, original Japanese v1.00a,
SHA-256 `c11776019f083978e66027e7394dafb1fb9543afca986f28049a49417e341929`.
Run `python3 scripts/verify-target.py` when explicitly checking identity.
The ignored reference checkout remains pinned to
`2b846da735ac71f68b1dc74e8194c8c8d98e2869`; upstream labels have no authority.

```sh
.venv/bin/python scripts/progress.py
.venv/bin/python scripts/build.py
.venv/bin/python scripts/audit-reference.py --address 0x0041DCB0 --json .analysis/upper-ecl-diagnostic.json
.venv/bin/python scripts/compare-linked-function.py reference-0045d850
```

Build after source changes, then compare the complete affected owner. Run an
isolated `audit-reference.py --write-units` for a coherent validated milestone.
`--require-cold` belongs to `compare-linked-function.py`, not the focused audit.
Do not refresh receipts/analyzers solely for prose or storage cleanup.

Keep `build/reference-candidate/` intact, including object/dependency and
symbol-discovery caches. Preserve private inputs, `.tools/wine`, selectors,
`.venv`, Ghidra project and pinned reference. Historical fixture output subtrees
are now verified archives; their parent scripts, source snapshots and recent
baseline/final images remain accessible. See [ARTIFACTS.md](ARTIFACTS.md).

```sh
python3 scripts/evidence-archive.py list ecl-float-work
python3 scripts/evidence-archive.py list audio-scalar
python3 scripts/evidence-archive.py show handoff-next-agent-fe98fb8.md
python3 scripts/evidence-archive.py restore ecl-float-work/native-baseline
```

`show` reads one indexed file without restoring a tree. `restore` verifies
archive/member hashes and refuses an existing destination. Both dated cleanup
indexes are loaded automatically. Old scripts may need their literal archived
paths restored; their expected historical counts do not describe this checkpoint.
`.analysis/audio-release-baseline/` is an older audio checkpoint, not the current
baseline. The current restoration inputs are the PDB 619/624 sets named above.
Shared Factory deployment was not requested; staged registration stays private.
