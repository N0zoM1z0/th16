# Reconstruction knowledge index

Start with [the current handoff](../NEXT_AGENT.md). These reviews record evidence
at specific checkpoints; their historical counts and open-item statements are
not the current ledger. [Reference repairs](reference-repairs.md) is the
chronological experiment log. Use `scripts/progress.py` for authoritative totals.

| Topic | Starting points |
| --- | --- |
| Strict comparison and provenance | [Reference evaluation](../REFERENCE_IMPORT.md), [reviewed linkages](reviewed-linkages.md) |
| Latest accepted audio work | [Release/strncmp](audio-release-strncmp.md), [sound data and rejected scalar trials](audio-scalar-and-sound-data.md), [ISA/aligned audio EH](audio-isa-aligned-eh.md), [rand/vector identities](audio-rand-vector-identities.md) |
| EH and class metadata | [EH handlers](eh-handlers.md), [single-state terminal graphs](single-state-terminate-eh.md), [terminate chain](terminate-destructor-eh.md), [allocation cleanup](allocation-cleanup-eh.md), [sound RTTI](sound-eh-vftables.md) |
| Complete dispatch owners | [Bounded switches](switch-ownership.md), [compound owners](compound-owner-scopes.md), [remapped owners](remapped-owner-scopes.md), [direct owner scopes](direct-owner-scopes.md) |
| Original roots and private entries | [Runtime roots](runtime-entry-scopes.md), [registered callbacks](registered-callbacks.md), [Anm callbacks](anm-callback-scopes.md), [static sin/cos](static-sincos-ownership.md) |
| Native gameplay diagnostics | [Boss, damage and laser execution, complete parameter observations and controls](native-boss-and-laser-diagnostics.md) |
| Source/context trials | [Boss damage and feedback](boss-damage-and-hit-feedback.md), [curve laser initialization and projectile dispatch](laser-initialization-and-bullet-dispatch.md), [boss, spellcard and projectile motion](boss-motion-source-trials.md), [Player](player-context-trials.md), [bullet collisions](bullet-collision-contexts.md), [pause/replay slot](pause-replay-slot.md), [full repair history](reference-repairs.md) |
| CRT/math dependencies | [Conversion runtime](conversion-runtime.md), [atan2 dependency research](atan2-runtime-dependencies.md), [tangent/failure runtime](failure-tangent-runtime.md) |
| Setup and stored evidence | [Bootstrap](../BOOTSTRAP.md), [shared tools](../SHARED_TOOLS.md), [artifact policy and archive access](../ARTIFACTS.md) |

The initialization proof draft is intentionally outside the active Oracle. Its
location, missing checks and known review gaps are listed in the current handoff.
Other focused review files remain alongside this index. Historical artifact
paths may require `scripts/evidence-archive.py`; retain their original evidence
rather than treating an absent uncompressed path as lost work.
