# Reconstruction knowledge index

Start with [the current handoff](../NEXT_AGENT.md). Every file here is
evidence that a config file, Oracle review profile or source comment names;
counts inside them are those of the checkpoint they were written at. Historical
session logs and source-trial reports were removed on 2026-11-15 and remain in
Git history. Use `scripts/progress.py` for authoritative totals.

| Topic | Files |
| --- | --- |
| Strict comparison and linkages | [Reference evaluation](../REFERENCE_IMPORT.md), [reviewed linkages](reviewed-linkages.md), [replay format](replay-format-linkage.md), [season names](season-name-linkage.md) |
| EH and class metadata | [EH handlers](eh-handlers.md), [empty EBX/ESI frames](ebx-esi-empty-eh.md), [shared empty frames](shared-empty-eh-frames.md), [enemy](enemy-empty-eh.md), [single-state terminal graphs](single-state-terminate-eh.md), [terminate chain](terminate-destructor-eh.md), [allocation cleanup](allocation-cleanup-eh.md), [member constructors](member-constructor-eh.md), [array/thread constructors](array-thread-constructor-eh.md), [AnmManager constructor](anm-constructor-eh.md), [sound tables](sound-eh-vftables.md), [ECL vftables](ecl-vftable-identities.md), [Gui destructor](gui-destructor-exact.md) |
| Owner scopes and dispatch | [Bounded switches](switch-ownership.md), [compound owners](compound-owner-scopes.md), [remapped owners](remapped-owner-scopes.md), [direct-table owners](direct-owner-scopes.md), [upper ECL frame store](upper-ecl-frame-store-scope.md), [special vertices](special-vertices-scope.md), [masked effect](masked-effect-exact.md), [dialogue VM](dialogue-position-array-exact.md) |
| Entries and callbacks | [Runtime entries](runtime-entry-scopes.md), [registered callbacks](registered-callbacks.md), [callback tables](table-entry-scopes.md), [Anm callbacks](anm-callback-scopes.md), [Anm private dispatch](anm-private-dispatch.md), [manager callbacks](manager-callbacks.md), [manager wrappers](manager-wrapper-scopes.md), [static sin/cos](static-sincos-ownership.md), [further sin/cos](further-sincos-scopes.md) |
| Runtime and literal identities | [Conversion runtime](conversion-runtime.md), [math runtime](math-runtime-identities.md), [atan2](atan2-runtime-identities.md), [failure/tangent](failure-tangent-runtime.md), [loader errors](loader-error-identities.md), [COMISD literals](comisd-literal-identities.md), [timing literals](timing-literal-identities.md), [replay literals](replay-literal-identities.md), [menu literals](menu-literal-identities.md), [stage/time](stage-time-identities.md) |
| Audio | [Initialization](audio-isa-aligned-eh.md), [rand/vector](audio-rand-vector-identities.md), [release/strncmp](audio-release-strncmp.md), [sound data](audio-scalar-and-sound-data.md) |
| Source-context notes cited by code | [Player](player-context-trials.md), [Boss counter/stage fog](boss-counter-and-stage-fog-trials.md), [camera sky/Boss query](camera-sky-and-boss-query-trials.md), [interpreter/laser/menu](interpreter-and-laser-complete-owner-trials.md) |
| Setup | [Bootstrap](../BOOTSTRAP.md), [shared tools](../SHARED_TOOLS.md), [artifacts](../ARTIFACTS.md) |
