# 東方天空璋 ～ Hidden Star in Four Seasons

Agent workflow: follow the highest-priority requirements in [AGENTS.md](AGENTS.md). Use incremental builds and focused complete-owner comparisons; prose edits need no build or audit.

<p align="center">
  <img
    src="resources/title-screen.png"
    width="640"
    alt="TH16 title artwork composited from the original title.anm textures">
</p>

<p align="center">
  <img src="resources/progress.svg" alt="Historical TH16 strict-audit snapshot from 2026-11-15, not the current source">
</p>

This project reconstructs C++ source for the original Japanese TH16 version
1.00a executable. The source is built with the historical MSVC 2017 (v141_xp)
toolchain under whole-program optimization (/GL, /LTCG). The intended
strict comparison covers complete owned extents and relocations, but the
current candidate has not received fresh Factory-accepted Oracle results.
Similarity scores and upstream labels grant no exact credit.

## Exact target

Supply your own legal copy at the ignored path `resources/th16.exe`.

| Property | Required value |
| --- | --- |
| Version | original Japanese 1.00a |
| Size | `683,520` bytes |
| SHA-256 | `c11776019f083978e66027e7394dafb1fb9543afca986f28049a49417e341929` |
| MD5 | `cb9caf54ce5738f70086e783ec88fd2a` |
| Image base | `0x00400000` |
| Entry point | `0x0047537B` |

The pinned [thcrap version database](https://github.com/thpatch/thcrap-tsa/blob/25acfe37f0bed5008eb8b94afc3d72679fd50384/base_tsa/versions.js)
classifies this exact SHA-256 as `th16`, `v1.00a`, `(original)`; the Steam
release and patched executables have different digests.

```bash
scripts/repo-python scripts/verify-target.py
```

Original executables, game data, Ghidra projects, decompiler output, build
outputs and downloaded tools are private and never committed. The title image
above is composited from the game's own textures for identification only.

## Current status (2026-11-23)

The current source checkpoint is **de0cb82**
(gpt-web: return packed laser shot origins). The six source commits since
origin/main are local and have not been pushed; this handoff/documentation
update is also local. The worktree is clean. The latest incremental build
compiles **1,166 annotated functions**.

Current focused normalized instruction comparisons:

| Owner (target VA) | Target / candidate bytes | Target / candidate instructions | Local ratio |
| --- | ---: | ---: | ---: |
| EnemyData::ecl_run_over_300 (0x41dcb0) | 21,408 / 21,584 | 4,562 / 4,833 | **0.9224** |
| AnmVm::run (0x45f980) | 14,177 / 14,192 | 3,837 / 3,825 | **0.9514** |
| EclRunContext::ecl_run (0x472030) | 7,046 / 6,976 | 1,807 / 1,701 | **0.9042** |
| LaserLineInf::run_ex (0x431fe0) | 1,588 / 1,600 | 344 / 346 | **0.9159** |
| LaserCurveInf::run_ex (0x438cb0) | 1,548 / 1,568 | 360 / 368 | **0.9698** |
| LaserLineInf::on_tick (0x432f40) | 1,473 / 1,488 | 356 / 354 | **0.9408** |
| LaserCurveInf::on_tick (0x4377d0) | 1,305 / 1,312 | 332 / 332 | **1.0000** |
| LaserCurveNode::step_back (0x438370) | 986 / 992 | 248 / 248 | **1.0000** |
| EnemyData::step_interpolators (0x41bb50) | 1,692 / 1,696 | 421 / 421 | **0.9976** |
| InterpFloat2::step_radial_dist (0x425570) | 757 / 752 | 207 / 205 | **0.9175** |

These are local instruction-similarity measurements, not exactness claims.
The focused strict audits still report ecl_run_over_300 incomplete because
two linked fields lack independent symbol/addend bindings;
step_interpolators differs in 24 bytes; LaserCurveInf::on_tick differs in
6 bytes; and LaserCurveNode::step_back differs in 4 bytes. Even a local
ratio of 1.0000 is not proof of byte-, relocation- or owner-exactness.

The current Factory accepted snapshot is still inventory-only and returns no
Oracle results. Earlier isolated pilot receipts are retained as historical,
separate evidence; they are not current shared accepted facts. Source-origin
review and full production closure remain open. The progress image above is
also historical: it records the 2026-11-15 local audit, not current status.

For the next agent, read AGENTS.md, then the
[current handoff](docs/NEXT_AGENT.md) and
[artifact and recovery notes](docs/ARTIFACTS.md). The dated
[2026-11-21 handoff](docs/HANDOFF_20261121.md) and
[2026-11-19 chronology](docs/HANDOFF_20261119.md) are historical records;
their checkpoint hashes and measurements have been superseded.

## Project map

- [`AGENTS.md`](AGENTS.md) — mandatory session and evidence rules.
- [`src/`](src) — reconstructed game source; [`src/decomp.h`](src/decomp.h)
  holds the clearly marked compiler-context placeholders.
- [`probes/`](probes) — toolchain smoke inputs, compiler-context callers and
  opaque support kept outside the game source.
- [`config/target.toml`](config/target.toml) — target identity and PE facts.
- [`config/tools.lock.toml`](config/tools.lock.toml) — compiler, linker, SDK,
  analyzer and linked-code decoder lock.
- [`config/match-units.toml`](config/match-units.toml) — retained strict
  comparison units; [`config/frontiers.toml`](config/frontiers.toml) — the
  non-exact ratchet.
- [`docs/NEXT_AGENT.md`](docs/NEXT_AGENT.md) — current handoff.
- [`docs/REFERENCE_IMPORT.md`](docs/REFERENCE_IMPORT.md) — comparison scope and
  the reference import.
- [`docs/knowledge/`](docs/knowledge/README.md) — evidence cited by the Oracle
  review profiles and the source.
- [`docs/ARTIFACTS.md`](docs/ARTIFACTS.md) — private inputs, retained evidence
  and cleanup policy.

## Credits

This project imports candidate C++ source, names, structures, build-context
harnesses and historical toolchain research from
[johnthreekay/th16](https://github.com/johnthreekay/th16), pinned to commit
`2b846da735ac71f68b1dc74e8194c8c8d98e2869`. Credit belongs to johnthreekay and
the upstream contributors. Their original project work is dedicated under
[CC0 1.0](docs/licenses/johnthreekay-th16-CC0.txt). The game, its data and strings
remain the work of ZUN / Team Shanghai Alice; upstream also identifies its
`DSUtil.cpp` as an adaptation of a Microsoft DirectX SDK sample.

Our strict PE/MAP/PDB readers and Oracle method derive from the MIT-licensed
[TH10 reconstruction](https://github.com/N0zoM1z0/th10) and the Touhou
Reconstruction Factory series. The upstream comparison scripts are not used by
the strict Oracle.

## License

Repository-authored code and documentation are provided under the MIT License.
This does not grant rights to the original game or its assets.
