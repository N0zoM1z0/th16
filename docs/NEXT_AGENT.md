# Current handoff

Updated 2026-11-12 after shared ECL position setup, spell-name decoding and difficulty dispatch.
The user resumed reconstruction and explicitly prioritizes substantial enemy,
boss and projectile functions over small helpers. No build or audit writer is
running at this checkpoint. Read AGENTS.md before work.

## Authoritative checkpoint

The exact-credit checkpoint is `a95321e` (curve laser initialization and the
elliptical drop helper). Source checkpoint `291be6e` recovers inline boss
feedback and damage-source traversal. The current source continuation retains
shared ECL position setup, destination-pointer spell-name decoding and explicit
difficulty dispatch, with no new exact credit.
The canonical report is **885 exact, 65 mismatch, 265 incomplete** among 1,215
annotations: **169,575 exact primary bytes and 950 retained units**.
Source-origin review is **open**; Factory acceptance is **not submitted**.
Use `.venv/bin/python scripts/progress.py` to verify current state.

The source input is
`71e0dc6fd0fafbfdc9d83f91765d1e17d3e8c4c21c6ea45e5ee5aadbaa2a99cc`.
PDB age is **195**. The final incremental build, strict replay and progress check
validate current source, artifact and comparison identities. Cleanup preserves the current incremental
build, target, canonical report, Wine prefix, Ghidra project and pinned reference.

Recent accepted work:

| Review | Result |
| --- | --- |
| [ECL position and spell names](knowledge/ecl-position-and-spell-name.md) | Shared interpolation finish, forward destination traversal and both difficulty tables; candidate 21,586 to 21,384 bytes against 21,408 original bytes, still incomplete |
| [Curve laser and projectile dispatch](knowledge/laser-initialization-and-bullet-dispatch.md) | Complete 1,726-byte initializer and 32-byte private helper; projectile dispatcher 5,988 to 5,500 bytes, still incomplete |
| [Audio release and strncmp](knowledge/audio-release-strncmp.md) | Complete 370/88-byte primary owners; complete 120-byte UCRT identity; fixed ESI-only terminal frame |
| [Sound data](knowledge/audio-scalar-and-sound-data.md) | Complete 1,656-byte aggregate; complete 145/168-byte queue entries |
| [ISA and aligned audio EH](knowledge/audio-isa-aligned-eh.md) | Complete 856/809-byte initialization owners, startup-derived ISA storage and private EH graphs |

See the [knowledge index](knowledge/README.md) for other topics. Older findings,
counts and open-item statements are historical; use this file and the canonical
report for current status. The full former handoff remains available through
`python3 scripts/evidence-archive.py show handoff-next-agent-6427da9.md`.

## Current gameplay source work

Read [ECL position setup and spell-name decoding](knowledge/ecl-position-and-spell-name.md)
first. `ecl_run_over_300` now shares the position/curve initial-goal-timer path,
advances the spell-name destination with a forward counter, and retains separate
Lunatic/default branches to recover both four-entry difficulty tables. The
complete diagnostic scope contains **three dispatches**, 182 target slots and
702 map bytes: **21,408 original / 21,384 candidate bytes**. An early main-only
scope omitted the two nested tables; its 21,374 target total is incomplete.
Keep its warning and use `.analysis/ecl-dispatch-work/complete-scope/`.

Final native checks agree in **1,157 complete movement calls**, **108 complete
difficulty-selector calls** and **140 spell prefixes**. Independent expected
objects, stack-variable writes, decoded names and actual call arguments also
agree. A negative control refuses a default return that never reaches the
spell call. Prefix cases stop before `Spellcard::start`; resource startup and
the rest of that path are untested. The complete calls check preserved registers,
stack cleanup, floating controls and exception-chain restoration. Constant
arguments and positive-offset local destinations leave other ECL variables,
stack references and most handlers outside the fixtures.

Preserve `.analysis/ecl-dispatch-work/`, including the tested final image,
partial-scope warning, multibyte-padding refusal and restored source forms.
The strict Oracle still refuses the large dispatcher. Its existing adjacency
proof does not cover the original frame-slot store between remap and dispatch;
several linked identities and code differences also remain. No acceptance
profile or normalization is changed. The full replay preserves all 885 exact
owners and classifications, 169,575 exact primary bytes and 950 units.

Read [native boss and laser diagnostics](knowledge/native-boss-and-laser-diagnostics.md)
before repeating calling-context or laser trials. At the preceding `8eb77c0`
checkpoint, a Win32 debug child runs
the unmodified original and candidate at their preferred image bases under this
game's Wine prefix. Redirect only after the loader's initial breakpoint. Native
execution agrees in **278 boss, 118 damage and 596 laser cases**, including
**140 complete 856-byte new-segment parameter captures**. Native observations
also agree with the corresponding instruction emulation. One positive and three
negative native observation controls pass. These partial fixtures skip real
allocation/effects, deaths and ECL transitions and grant no exact credit.

`.analysis/laser-core-work/` retains the final tested PE/MAP/PDB/receipt,
debugger host, fixtures, native reports, observation schema controls and failed
prototypes. Its first REP observer result is invalid; callback errors were
swallowed and EDI was recorded after advancing. Its first native loader stop
also did not execute game code. Keep both failures and use the final reports.
The final isolated strict replay preserves all 885 exact owners and all
comparison classifications; `final-regression.json` records PDB age 188.

The earlier 21,402-byte ECL owner snapshot removes original reloads after calls
and is restored. The target primary boundary is provisionally 19,976 bytes;
the newer diagnostic accounts for all three trailing tables as described above,
while formal scope review remains open. Binding unresolved fields alone cannot
make the body exact. The retained Ghidra context warns about switch recovery.
The compiler call graph also finds
`ecl_ext_damage_anm_hurtbox` as a second damage caller; retaining that real
callback does not fix the boss/damage alignment arrangement. See the review
for the other restored source forms and their complete extents.

`EnemyData::step_logic` at `0x0041c330` now contains the original inline
200/900 low-life hit-sound test. Its private helper is removed, and spell flags
are read within the boss/large-life short-circuit conditions, including the
100/500 periodic flash test. The complete candidate is 2,196 bytes against
2,207 original bytes; it remains incomplete. New shield pointer/state snapshots
hoisted reads and were restored.

`Player::compute_damage_to_enemy` at `0x00445a30` advances a source pointer
with a bounded remaining count and reuses the timer's multiple-frame query.
The candidate recovers separate source/timer pointers and grows from 735 to
769 bytes against 774 original bytes. It remains incomplete. The timer query
alone does not change code. Original boss logic realigns its frame while its
damage callee does not; the candidate has the opposite arrangement. Recover
the actual source/call context rather than forcing either alignment.

Read [boss damage and hit feedback](knowledge/boss-damage-and-hit-feedback.md).
`.analysis/boss-core-work/` retains complete original/trial scopes, game-owned
Ghidra context, native compiler layout evidence and partial instruction
diagnostics: 118 damage cases and 278 boss cases agree with zero faults. These
exercise actual mapped callees, sound queuing, timers and threshold boundaries;
no function is patched or stubbed. They grant no exact credit and leave real
resources, shield replacement, allocation, deaths and ECL transitions untested.

Relinking exposed a coverage error in the already proved 680-byte window
procedure: Capstone stopped in its first target table, before the middle byte
map. Replay now revalidates the existing compound code/table/relocation proof
against the same images and requires decoding all real code, then compares
every owned byte. It adds no owner, boundary or normalization allowance.
All 885 prior exact results are preserved. Compound controls (26), switch
controls (40), Oracle controls (14) and focused-audit controls (3) pass. The
window procedure also passes standalone complete replay. Preserve the failed
decode record and final regression evidence in `.analysis/boss-core-work/`.

`LaserCurveInf::initialize` at `0x004370a0` is exact over its complete
1,726-byte owner. The initial distance is cleared between computing and storing
the translated X coordinate. Pointer-based component arithmetic retains the
original floating operand order. The independent ellipse helper at `0x00426240`
is exact over all 32 bytes; its 500-byte drop caller remains 455/500 mismatch.
The new helper profile preserves all existing complete-owner and witness checks.

`Bullet::run_ex` at `0x00413860` now retains a command pointer by advancing it
for paired shooting and laser commands. The candidate shrank from 5,988 to
5,500 bytes against the complete 5,436-byte original. The nested laser switch
and signed packed-parameter shift follow the original. No exact credit is
claimed. Remaining differences are spread across handlers and frame layout.
An extracted readiness helper and pointer declaration reorder did not help.

Read [the laser and dispatcher review](knowledge/laser-initialization-and-bullet-dispatch.md)
and preserve `.analysis/bullet-ex-work/`. Its final diagnostic executes actual
mapped instructions in Unicorn: 488 identical cases, no faults, and identical
complete laser parameter snapshots for 16 cases with allocation declined by a
full manager. This is partial emulation evidence, not native execution or exact
credit. Real allocations, resource paths and several side effects are untested.
Those historical Wine host-mapping prototypes failed before entering game code;
the later debug-child approach above overcomes that mapping problem.

The full strict replay preserves all 883 previous exact owners. Standalone
comparisons confirm both new exact entries. Private-function controls (34),
Oracle controls (14) and focused-audit controls (3) pass. See the regression
record and logs in `.analysis/bullet-ex-work/`. No failed source trial remains.

`Spellcard::on_tick_body` at `0x00417930` retains its complete 650-byte scope.
A planar vector delta and scalar depth delta improve strict matching from
437 to 451 bytes. It remains a mismatch. Source-origin review remains open.

Read [the boss and projectile source trials](knowledge/boss-motion-source-trials.md)
before retrying the enemy motion, damage, projectile corner tests or shared
circle/wave movement. Failed forms were restored byte for byte and rebuilt
incrementally. Their source snapshots, diagnostics and final regression record
are in `.analysis/enemy-motion-work/`. Those historical trials left no Oracle
or compile-profile change; the later compound-coverage repair is described above.

The unresolved substantial owners include `EnemyData::step_interpolators`
(1,692/1,691 bytes), `EnemyData::step_logic` (2,207/2,196 bytes) and
`Bullet::step_ex_08` (1,390/1,382 bytes). The directional animation's child mode
is 8, whereas the common creation helper uses zero. Recover real source/type
and calling context; do not add cookies, padding, dead arithmetic or register
forcing to close these differences. `PosVel::step` remains 696/700 matching.

## Work rules

- **Never push**, mirror or publish this repository. Coherent local commits are
  permitted. Do not use REA or borrow another game's prefix/analyzer project.
- Preserve dirty work and required ignored evidence. See [ARTIFACTS.md](ARTIFACTS.md)
  before deleting anything. Tool selectors can point outside this repository.
- Write maintained source, comments, documentation and commits in English; only
  the Japanese game title is excepted.
- Use the Factory/TH10 strict Oracle. Upstream labels, similarity scores,
  successful builds and analyzer annotations do not grant exact credit.
- Compare complete independent owners, extents, fields and relocations. Never
  force registers, insert dead locals/padding, mask bytes or truncate owners.
- Use natural C/C++ and incremental builds for source experiments. Restore failed
  trials byte for byte and rebuild incrementally before declaring restoration.
  Reserve a cold build for a milestone or demonstrated dependency/cache failure.
- Do not edit maintained source/verifiers while a build or Oracle Context is live.
  Do not run tests, progress or ledger readers concurrently with
  `audit-reference.py --write-units`. A diagnostic must use a separate JSON path.
- Documentation edits and storage cleanup require diff review and focused
  verification; they do not require a compiler/analyzer run or receipt refresh.

## Unvalidated initialization draft

The working draft was removed from the active Oracle and preserved at:

`.analysis/experiments/audio-initialize-unvalidated/`

It contains the two new modules, four changed tracked files, their patch,
checksums and the focused diagnostic. Its base is `6427da9`; the matching
`.analysis/audio-initialize-baseline/` remains uncompressed. A positive focused
run reported one 708-byte owner exact **under the draft rules**. No negative
suite or canonical regression was completed. This result is not accepted
progress; do not install the draft or change counts based on it alone.

The two unfinished requirements are SoundManager::initialize at **0x0045D510**:

1. A complete 37-byte handler checks cookies at node-96 and node-4. Its 44-byte
   metadata has one terminal state, flags one. Prove the full parent-derived
   cookie/frame/state graph; the existing 27/40-byte profiles do not cover it.
2. Its ESI cursor starts at sound-table+4, advances twenty and compares against
   sound-table+1564 (physically anchor-x+4). Prove every path, side exit and
   non-dereferenced limit, including ESI preservation through all normal returns
   of the complete 702/713-byte loader owners. Do not enlarge the typed table,
   borrow the adjacent array identity or relax generic cursor rules.

The draft attempts stack/ESI tracking and explicit call contracts. Review its
assumptions and counterexamples carefully. Known review gaps include partial
register aliases: DI/DIL writes must invalidate a Sleep target tag, and SI/SIL
cursor uses need explicit treatment. Check complete metadata ownership, all
callee contracts, stack writes, argument cleanup, returns and exceptional paths.
A single PUSH or a positive caller comparison does not prove the contract.

Read `.analysis/audio-initialize-next-proof-inventory.json` and the draft README.
The original/candidate payloads, private contributions, cursor uses and all
return sites are retained. The active Oracle still refuses both fields.

## Other open work and rejected forms

- SoundBufferEntry::load retains an ambiguous data tag and unequal complete
  extents (702/713). Its two strncmp fields are now resolved.
- CSound::SetVolume remains 114/116; Unpause remains 103/107. Used buffer/BGM
  snapshots produce the same rejected 115-byte volume candidate. Compound
  accumulation leaves Unpause unchanged. Earlier addend reversal and a named
  pause-duration trial also failed. See [the source trials](knowledge/audio-scalar-and-sound-data.md).
- The Enemy destroy_all and Int3 interpolation one-byte differences are SIB
  encodings, not branch displacements. Do not normalize them as equivalent bytes
  or repeat the already rejected operand/local variants.
- Other source/context trials, ownership limits and missing-entry investigations
  are recorded in [reference repairs](knowledge/reference-repairs.md). Read the
  relevant section before retrying a form. Runtime/EH auxiliary graphs grant no
  additional primary exact credit.

## Commands and evidence access

```sh
.venv/bin/python scripts/progress.py
.venv/bin/python scripts/audit-reference.py --address 0x45d510 --json .analysis/initialize-diagnostic.json
.venv/bin/python scripts/build.py
.venv/bin/python scripts/compare-linked-function.py reference-0045d850
```

Build only after source changes. Refresh canonical units/report after a coherent
validated reconstruction milestone, with an isolated `--write-units` run.
`--require-cold` belongs to `compare-linked-function.py`, not the focused audit.

Historical baselines/trial artifacts are now verified archives; old notes and
helper scripts may name their former uncompressed paths. Restore before running
such a helper, or read an individual file without restoring the whole tree:

```sh
python3 scripts/evidence-archive.py list audio-scalar
python3 scripts/evidence-archive.py show audio-scalar-baseline/build/reference-candidate/build-receipt.json
python3 scripts/evidence-archive.py restore audio-scalar-baseline
```

Restoration checks hashes and refuses existing destinations. The current
`.analysis/audio-release-baseline/` remains directly usable by the latest
artifact/regression check scripts. See [ARTIFACTS.md](ARTIFACTS.md) for the full
preservation policy and cleanup manifest. Shared Factory service deployment is
unchanged and was not requested.
