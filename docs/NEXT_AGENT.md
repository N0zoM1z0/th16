# Current handoff

Updated 2026-11-12 for agent handoff after evidence cleanup.
The user ended the active reconstruction goal and requested cleanup. No build,
audit writer or reconstruction experiment is running. Read AGENTS.md before work.

## Authoritative checkpoint

The last reconstruction commit is `6427da9` (audio release EH and strncmp).
The canonical report is **883 exact, 65 mismatch, 267 incomplete** among 1,215
annotations: **167,817 exact primary bytes and 948 retained units**.
Source-origin review is **open**; Factory acceptance is **not submitted**.
Use `.venv/bin/python scripts/progress.py` to verify current state.

The source input is
`356af008e8064e7f8080f6c112145362eea142d1955f371a989e5b65034aca5f`.
PDB age is **124**. All 1,719 complete linked function records and 192 dependency
stamps validated at the checkpoint. Cleanup preserves the current incremental
build, target, canonical report, Wine prefix, Ghidra project and pinned reference.

Recent accepted work:

| Review | Result |
| --- | --- |
| [Audio release and strncmp](knowledge/audio-release-strncmp.md) | Complete 370/88-byte primary owners; complete 120-byte UCRT identity; fixed ESI-only terminal frame |
| [Sound data](knowledge/audio-scalar-and-sound-data.md) | Complete 1,656-byte aggregate; complete 145/168-byte queue entries |
| [ISA and aligned audio EH](knowledge/audio-isa-aligned-eh.md) | Complete 856/809-byte initialization owners, startup-derived ISA storage and private EH graphs |

See the [knowledge index](knowledge/README.md) for other topics. Older findings,
counts and open-item statements are historical; use this file and the canonical
report for current status. The full former handoff remains available through
`python3 scripts/evidence-archive.py show handoff-next-agent-6427da9.md`.

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
