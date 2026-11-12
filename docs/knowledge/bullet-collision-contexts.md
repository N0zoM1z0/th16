# Bullet collision source contexts

## Result

Six natural source contexts for `Bullet::check_player_collision` were built
incrementally and rejected. Baseline BulletManager.cpp is restored byte for
byte and freshly rebuilt. No game source change or exact credit is retained.
Canonical results remain **815 exact, 63 mismatch and 337 incomplete**, covering
145,004 exact primary bytes and 878 retained units.

The original at `0x4124b0` owns **448 bytes**, with 130 reachable instructions
and no trailing padding before the next entry at `0x412670`. This independent
boundary proof was established during the
[Player context review](player-context-trials.md). Baseline source produces a
complete **449-byte** source-qualified PDB owner in BulletManager.obj. Every
trial retains the strict complete-boundary refusal. No unequal prefix receives
a byte score or exact credit.

## Remaining source context

The cancellation-effect path contains several independent differences:

- The original copies game speed with `MOVAPS`, then multiplies the X velocity
  directly from memory. Baseline instead loads X with `MOVSS` and multiplies
  registers, costing one additional instruction byte.
- The original goal vector occupies EBP-0x10 through EBP-8; baseline uses
  EBP-0x0c through EBP-4. Both allocate a 16-byte local frame. Neither frame
  size nor a presumed missing local establishes a source declaration.
- Original invulnerability and negative cancellation-script branches share
  the first hit-return epilogue. Baseline routes them to the later graze-return
  epilogue. These branch destinations remain real differences even where
  instructions have equal lengths.

The observed differences do not establish the original vector expression,
temporary lifetime or return structure. Register scheduling, stack offsets
and branch destinations cannot be normalized to recover exact credit.

## Rejected trials

| Trial | Natural source context | Complete candidate | Linked owners changed |
| --- | --- | ---: | ---: |
| Baseline | `g_game_speed * velocity * 10.0f` | 449 | 0 |
| Vector first | `velocity * g_game_speed * 10.0f` | 449 | 0 |
| In place | Initialize from velocity; apply both scales with `*=` | 458 | 1 |
| Components | Assign each goal coordinate from its scaled velocity | 449 | 1 |
| Hit return | Return the collision result inside the hit branch | 452 | 1 |
| Constructor | Initialize the goal from three scaled coordinates | 449 | 1 |
| Named ID | Store the returned `AnmId` before calling `find_or_clear` | 451 | 1 |

Each changed linked owner is the complete collision function itself. All other
1,718 complete linked owners retain their address, extent and raw hash. The
vector-first trial produces identical bytes across all 1,719 owners. Component
assignment and constructor forms change scheduling but retain 449-byte extents.
The explicit hit return introduces an immediate return value, still differing
from the original register return. The named handle allows VM lookup to move
after vector computation and retains the baseline goal stack location; it
does not recover the original temporary context. These six forms should not
be repeated or combined merely to manipulate layout.

## Validation and evidence

Restoration checks establish baseline source/build input identity, current
artifact hashes, all 1,719 complete linked owners and all 192 dependency stamps.
The current graph is freshly built incrementally; archived outputs are not
substituted. Every previous comparison result and all 878 units remain
unchanged. All 209 existing controls across nine suites pass.

`.analysis/bullet-collision-source-trials.json` records complete original and
candidate payloads, source-qualified PDB producers, all linked fields and PE
relocations, instruction streams, source/artifact identities, strict reports
and every changed complete linked owner. Its reproducer is
`.analysis/review-bullet-collision-trials.py`; instruction alignment is diagnostic
evidence with no acceptance authority. The original scope proof remains
`.analysis/player-secondary-original-scope.json`.

Full source/output sets are retained in
`.analysis/bullet-collision-source-baseline/` and
`.analysis/bullet-collision-{vector-first,in-place,components,hit-return,constructor,named-id}-artifacts/`.
Build logs use `.analysis/bullet-collision-<trial>-build.log`; focused strict
captures use matching `-audit.json` and `-unit.json` paths. Restoration and
canonical evidence are `.analysis/bullet-collision-restored-build.log`,
`.analysis/bullet-collision-restored-check.json`,
`.analysis/bullet-collision-full-audit.log`,
`.analysis/bullet-collision-regression-check.json` and
`.analysis/bullet-collision-controls-summary.json`.

Source-origin review remains open and Factory acceptance remains unsubmitted.
Nothing is published.
