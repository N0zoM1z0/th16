# Current handoff

Updated 2026-11-12 after shared ECL expression exits and floating-negation guards.
The user resumed reconstruction and explicitly prioritizes substantial enemy,
boss and projectile functions over small helpers. No build or audit writer is
running at this checkpoint. Read AGENTS.md before work.

## Authoritative checkpoint

The exact-credit checkpoint is `a95321e` (curve laser initialization and the
elliptical drop helper). Source checkpoint `291be6e` recovers inline boss
feedback and damage-source traversal. Checkpoint `a29e605` retains shared ECL
position setup, spell-name traversal and difficulty dispatch. The current source
continuation recovers the common result exit for 20 ECL expression handlers,
while retaining distinct arithmetic metadata behavior and floating negation.
The preceding curve, Boss and async source work is retained. No new exact credit is claimed.
The canonical report is **885 exact, 65 mismatch, 265 incomplete** among 1,215
annotations: **169,575 exact primary bytes and 950 retained units**.
Source-origin review is **open**; Factory acceptance is **not submitted**.
Use `.venv/bin/python scripts/progress.py` to verify current state.

The source input is
`0dd36c03a6cba531ccff7352c69de0ad2bf2c7b9f493525aa184907fcc5fe65d`.
PDB age is **277**. The final incremental build, strict replay and progress check
validate current source, artifact and comparison identities. Cleanup preserves
the current incremental build, target, canonical report, Wine prefix, Ghidra
project and pinned reference.

Recent accepted work:

| Review | Result |
| --- | --- |
| [ECL expression exits](knowledge/ecl-expression-result-exits.md) | One result exit for 20 handlers; complete interpreter 7,370 to 6,950 bytes; 3,457 complete calls and 360 prefixes agree; wrong floating-negation draft rejected |
| [ECL integer exits and live async cleanup](knowledge/ecl-integer-exits-and-boss-async.md) | Three-handler shared result push; interpreter 7,462 to 7,370 bytes; 1,192 complete Boss/ECL calls and 360 live-head prefixes agree; no new exact credit |
| [Curve elapsed time and integration](knowledge/curve-laser-elapsed-and-loop.md) | Original loop accumulator registers and acceleration operands; 372 historical differences removed in 1,488 complete calls; both owners remain incomplete |
| [Curve laser vectors and speed](knowledge/curve-laser-vectors-and-speed.md) | Original X multiplication/addition and speed accumulator operands; 216 historical output differences removed in 768 complete cases; both owners remain incomplete |
| [Boss damage frame context and phases](knowledge/boss-damage-frame-context-and-phases.md) | Natural planar vector recovers original alignment arrangement; 400 complete phase calls agree; complete owners remain incomplete |
| [Boss damage snapshots and CRT startup](knowledge/boss-damage-snapshots-and-crt-startup.md) | Original pointer/count sequence and XYZ read-before-write order; 96 historical impact-output failures removed; damage owner remains incomplete |
| [Boss shield flow and collision operands](knowledge/boss-shield-and-collision-operands.md) | Complete 2,207-byte logic owner now compares as mismatch; shield flow recovered, 27 historical collision payload failures removed; no new exact credit |
| [ECL angle and orbit initialization](knowledge/ecl-angle-and-orbit-initialization.md) | Original angle field order and vector tangent copies; 744 angle and 768 orbit complete calls agree; dispatcher remains incomplete |
| [ECL coordinate evaluation](knowledge/ecl-coordinate-evaluation.md) | Original coordinate getter/read sequence and animation X operand order; 18 historical NaN-payload failures now agree; complete dispatcher remains incomplete |
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

Read [ECL expression result exits](knowledge/ecl-expression-result-exits.md) first.
The starting checkpoint is `73643b8`. Twenty comparison, logic, bit-operation
and integer-negation handlers now share one result push. A single integer scratch
value feeds it and the separate add/subtract/multiply exit. Expressions preserve
the instruction's stack-reference byte; arithmetic clears it. Direct push,
division, remainder, decrement and floating negation retain separate exits.

The complete interpreter is **6,950 bytes**, against the unchanged **7,046-byte
provisional target span**. Do not promote that boundary or infer exactness from
size. All 362 switch-data bytes and decoded code/padding are retained in
`interpreter-corrected/`; every table destination/remap index is checked. The
original and corrected candidate both use a 56-byte frame aligned to eight.
Shared-block placement, stack slots/addressing, interpolation VM registers and
three unbound linked fields remain. Boss statistics and restart inlining remain.

Only the **corrected PDB 277** evidence is authoritative. The first batch edit
also redirected neighboring NEG_F after its floating push, adding an unwanted
integer item. Its 2,163-case subset missed that path; full diff review caught the
error before commit. The corrected source restores the direct advance. All 42
new float-negation guards agree with the original. A replay first passes the
original, then rejects the preserved wrong image (stack offset 16 versus eight).
The CFG guard also distinguishes one floating tag from floating-then-integer.
`invalid-negf-image/`, initial `final-image/`, `interpreter-final/`, `*-final`
reports and `final-regression.json` belong to the rejected **PDB 276** draft.

The corrected image passes **3,457 complete native Boss/ECL calls**: 2,205 unique
expression/guard cases, 492 arithmetic cases, 360 live-async dual phases and 400
preceding phases. Another **360 live-head prefixes** pass. All 20 handlers have
zero/eight metadata cases; arithmetic includes 60 new nonzero-byte cases. NaNs,
signed zeros, infinities, fractional conversions and the float integer-precision
boundary are modeled. Four controls reject the original on missing expressions,
wrong metadata clearing/preservation or missing async creation. Full scripts,
resources and general heap/leak behavior remain unproved.

Strict replay preserves **885/65/265**, 169,575 exact primary bytes and 950 units,
with no classification change. One generated upper-dispatch reason changes from
seven to eight unbound fields. Its new field is within the unchanged 702-byte
opcode map (offset 20,986, bytes `9f a0`), not new executable code. The complete
old/new 21,316-byte candidate scopes, original 21,408-byte scope, all three tables
and link-field differences are retained in `enemy-dispatch-corrected/` and the
relink diagnostic. The Oracle refusal remains; no binding, profile or rule is
changed. The ignored checker allows only this reviewed reason update.

Preserve `.analysis/ecl-predicate-work/`, especially `corrected-image/`,
`interpreter-corrected/`, `complete-scope-corrected/`, `enemy-dispatch-corrected/`,
`native-*-corrected/`, `corrected-result-exits-diagnostic.json`,
`dispatch-relink-diagnostic.json`, `corrected-negative-controls.json`, the invalid
image/control, driver snapshots, `TRIALS.md` and `corrected-regression.json`.
Do not overwrite the corrected driver using its retained early generator.
Only `src/EclRunContext.cpp` is a retained game-source change. All builds are
incremental; older broad gameplay reports retain their own image identities.

### Earlier ECL integer exits and live Boss async cleanup

Read [ECL integer result exits and Boss async cleanup](knowledge/ecl-integer-exits-and-boss-async.md)
first. Starting checkpoint `aba6395` is preserved. The large interpreter now
uses one integer-result exit for add/subtract/multiply, retaining separate
division/remainder exits. A CFG diagnostic through both pop conversions proves
that the original and candidate share one integer-tag write and compute each
result before it. The starting image has three writes and sinks addition after
its tag write. The candidate still places the shared block after multiplication,
while the original places it after addition.

The interpreter is **7,370 bytes**, down from 7,462, against the existing
**7,046-byte provisional target span**. Do not promote that boundary. The final
packet explicitly separates 67 four-byte switch targets and a 94-byte remap
from code/padding, validates every target/index and retains all 362 data bytes.
The generic early interpreter listing decodes table data as instructions; use
`interpreter-final/` instead. Three linked fields remain unbound. Comparison
exits, stack addressing/slots and interpolation-loop registers remain open.
Boss statistics, life-restart inlining and damage owner differences also remain.

The final image passes **1,192 complete native Boss calls**: 432 mixed integer/
float typed-stack arithmetic cases, 360 time-then-life phase cases, and the
preceding 400 phase cases. The dual programs create 1/3/8 real heap asyncs via
ECL, then trigger a life restart that calls the unchanged exact async cleanup.
Another **360 prefixes** stop before cleanup and require a live non-fixture
async head, then check the remaining complete observed storage. The head address
is image-dependent; it is validated before cross-image normalization. Prefixes
do not count or inspect every heap node, and they discard live allocations when
the diagnostic process ends. Full shipped scripts, resource effects, allocation
failure and general leak freedom are not proved.

Both negative controls reject on the original before candidate execution:
NOP arithmetic fails the typed-stack model; NOP async creation fails the live-head
requirement. First model drafts mis-handle fractional timer decrements and
primary time after early returns. The first prefix setup leaves its hardware
stop unarmed. Preserve those refused logs and exact driver snapshots; only the
corrected final reports are passing evidence.

Only `src/EclRunContext.cpp` is retained as a game-source change. Boss life-sub
and health-reference trials are restored, as are compound stack arithmetic
assignments and an over-shared five-operator result exit. Preserve
`.analysis/boss-restart-work/`, especially `final-image/`, `interpreter-final/`,
`complete-scope/`, native full/prefix outputs, `shared-exit-diagnostic.json`,
`negative-controls.json`, `TRIALS.md`, driver versions and `final-regression.json`.
Do not overwrite the corrected driver using its retained early generator.

Full strict replay and progress preserve **885/65/265**, 169,575 exact primary
bytes and 950 units, with no classification change or lost exact owner. The
ledger only rebinds candidate addresses. Original geometry, profiles, bindings
and Oracle rules are unchanged. All builds are incremental. No prior broad
native replay was repeated; older curve/Boss results belong to their images.

### Earlier curve elapsed time and integration order

Read [Curve elapsed time and integration order](knowledge/curve-laser-elapsed-and-loop.md)
first. The starting checkpoint for this continuation is `2add62b`. State now
uses `f32 elapsed = time - start_time` throughout. Its discrete loop advances
speed before `pos += d`, after computing displacement at the incoming speed.
Together these recover the original XMM6 speed, XMM7 position Y and XMM5
position Z, the loop addition schedule and both sentinel acceleration operands.
The elapsed local alone removes 132 historical output differences; the combined
source removes all 372 differences found by the expanded fixtures.

The complete reverse-step owner remains **986/986 bytes**; state is now
**1,168/1,164 bytes**. Both remain incomplete. State stack slots, polar-vector
registers/scheduling, reverse-step squared-length registers and two unbound
floor/atan2 call fields per owner remain. No register/alignment constraint,
unused local, extra double or Oracle change is added. Do not restore the four
unused integer locals removed in `1da68af`.

The final **1,488 native curve calls** agree with the original, including the
preceding 768 cases, 600 new state-sentinel cases and 120 new straight-state
cases. All use real CRT startup, complete storage observation and three x87
precisions. There are **192 independent complete-output expectations**, including
24 finite state-sentinel cases. Deliberately changing that model's doubled speed
is rejected on the original before historical/candidate execution. The
receipt-authenticated `2add62b` image fails 372 new sentinel cases; the current
image fails none. Overlapping outputs and CRT errno/matherr remain unmodeled.

A frame-speed local looked better in the initial matrix but introduces failures
when start X is NaN; the expanded matrix rejects its 417 differences against
372 historical differences. Named speed changes, vector copies/scale APIs,
start snapshots, displacement and operand reversals are restored. Preserve
`.analysis/curve-layout-work/`, especially `final-image/`, `complete-scope/`,
`native-final/`, the negative model control, exact historical driver versions,
`TRIALS.md` and `final-regression.json`. All retained final artifacts use PDB 265.

Full strict replay and progress preserve **885/65/265**, 169,575 exact primary
bytes and 950 units, with no classification change or lost exact owner. The
generated unit ledger is unchanged. Builds are
incremental; this checkpoint uses focused curve execution and full strict
replay, without repeating the preceding broad native gameplay replay.

The preceding [curve vector and speed checkpoint](knowledge/curve-laser-vectors-and-speed.md)
remains in `.analysis/boss-stats-work/`, at PDB 253. Its three expressions recover
reverse-step X multiplication, state polar X addition and speed accumulation,
removing 216 older `d56cd1c` differences. Its 3,364 complete gameplay cases and
204 prefixes belong to that preceding image. The final current curve matrix
replays its 768 curve cases. Keep the older Boss, damage, geometry, collision,
shield and phase reports and their observation/protocol negative controls;
they are not new execution claims for the current image.

### Earlier Boss damage frame context and phases

For the preceding `d56cd1c` checkpoint, read
[Boss damage frame context and phase transitions](knowledge/boss-damage-frame-context-and-phases.md)
before revisiting the frame work. A `Float2` XY difference in the circle/circle
damage branch naturally gives
the original alignment arrangement: Boss logic realigns ESP to eight bytes and
its damage callee does not. No alignment or register constraint is introduced.
The complete owners are now **2,222/2,207 Boss bytes** and **741/774 damage
bytes**, both incomplete. The beginning of Boss logic recovers the original
stack accesses; a 563-byte internal diagnostic binds 14 existing external fields
and agrees. It grants no independent owner or exact credit. The next branch has
a different internal displacement, and statistics, restart inlining, enemy-ID
lifetime and loop layout still need work.

All **400 new complete phase calls** agree with independent full-state models
and the original. They cover time/life interrupt slots and boundaries, script
lookup/reset, missing names, ECL life/rotation/bomb-multiplier commands, return,
delete, spell timeout and chapter accounting. Missing names preserve offset zero
with index -1; executed delete/return set both to -1. Typed probes and original
state corrected the first refused models before candidate execution. Empty async
lists leave actual async deletion, resources, deaths and full Boss scripts open.
A no-op negative entry is refused on the original before candidate fixtures.

The same final image passes **2,596 complete native calls and 204 prefixes**,
including all preceding impact, geometry, Boss, damage, collision and shield
suites after actual CRT startup. Historical controls retain the expected 96
impact and 27 collision failures; current failures are zero. Protocol,
observation and exception-chain controls pass. The first copied chain-control
job lacked its preserved fixture files; keep its failed log and the corrected
fixture hashes. `Enemy.cpp` and `Collision.cpp` are restored byte for byte.

The full strict replay preserves all 885 exact owners and 169,575 exact primary
bytes. Boss logic changes **mismatch to incomplete** because its complete extent
now differs; the normal writer removes its comparison unit. Counts are
**885/65/265**, with **950 units**. Original geometry, bindings and Oracle rules
are unchanged. Preserve `.analysis/boss-lifetimes-work/`, especially the tested
`final-image/`, complete scopes, phase fixtures/models, source trials, prefix
diagnostic, typed probe, controls and `final-regression.json`.

### Earlier Boss damage snapshots and CRT startup

For the preceding `dd3ba35` checkpoint, read
[Boss damage snapshots and initialized native execution](knowledge/boss-damage-snapshots-and-crt-startup.md)
before revisiting snapshot changes. `Player::compute_damage_to_enemy` advances
its source before decrementing the bounded count. Its compiler-generated source/timer advances now precede SUB,
which feeds JNE directly; the extra TEST is removed. A local `Float3 impact`
loads all XYZ bits before publishing the impact output, recovering the original
MOVQ/Z-load/store ordering. Keep that snapshot when working on local lifetimes.

All **384 impact-output calls** agree with the original and independent full-state
expectations. The preserved `d6faeac` image fails 96 of them. Shifted overlapping
storage exposes its late Z read; these are machine-level stress cases, not proof
of a C++ alias contract or of actual callers using overlapping objects. Ordinary
outputs, exact self-alias, four source indices and raw signed-zero/NaN Z bits
are included. The damage owner remains **769 candidate / 774 original bytes**,
incomplete. Its alignment, enemy-ID lifetime and block layout still differ.

The native host now executes actual executable startup and stops at the existing
WinMain entry before redirecting to a fixture. This fixes the missing runtime
precondition found when a nonfinite-angle matrix faulted on an original CRT path
before initialization. The final **1,164 geometry calls** all agree, including
324 independent axis-aligned expectations. The first point-array ABI attempt
passed its pointer on the stack; original instructions instead require ECX.
Keep both failed protocols and their notes; use the initialized final suites.

The same final image passes **2,196 complete native calls** (the 384 impact,
1,164 geometry and preceding 648 Boss/damage/collision/shield calls), plus the
preceding **204 prefixes**. All final native suites execute after actual startup;
18 startup stops, historical-image receipts and common final artifact hashes
are authenticated. Existing observation and prefix-chain controls pass, as do
old-protocol memory replay and a new width-register negative control.

All `Collision.cpp` rotation trials and direct Boss sinf/cosf trials are restored.
Their code/extent results are in `.analysis/boss-damage-work/`. Named rotation
forms did not fix the complete layout; the counted do/while point loop grew from
661 to 664 bytes. Do not keep such changes based on apparent source similarity.
The point helper remains mismatch and the 2,168-byte original rectangle owner
remains incomplete at 2,002 candidate bytes. These source and runtime diagnostics
grant no new exact credit.

Preserve `final-image/`, `complete-scope/`, `native-impact-final/`,
`native-geometry-final/`, the replayed Boss/shield reports, protocol controls,
layout probe and rejected forms under `.analysis/boss-damage-work/`.
`final-regression.json` preserves all 885 exact owners, 169,575 exact primary
bytes, all classifications and 951 units. The four generated comparison/boundary
ledgers are byte-identical to `d6faeac`. Source-origin review remains open and
Factory acceptance is not submitted. Full Boss scripts, due ECL transitions,
resource effects and real deaths remain outside these fixtures.

### Earlier Boss shield and collision work

For the preceding `d6faeac` checkpoint, read
[Boss shield flow and collision operands](knowledge/boss-shield-and-collision-operands.md).
`EnemyData::step_logic` uses nested shield conditions. Compiler common
expression elimination recovers the original main-state reuse, subseason reads
and merged disable path. A 156-byte internal source-shape diagnostic agrees
using existing linked identities; it is not an independent exact owner.

The retained collision position is `final_pos.pos + Float3(x, y, 0.0f)`. In the
final combined source, this keeps the original X floating operands and removes
all 27 historical NaN-payload failures. An explicit branch-local bomb-state
snapshot recovered the shield shape but reintroduced those failures. Preserve
`combined-first/`; do not reuse its failed report as final evidence. The retained
nested condition has no explicit snapshot.

The complete logic candidate grows from 2,196 to **2,207 bytes**, equal to the
independent original extent. The strict Oracle decodes and compares all 2,207
bytes and existing linked fields: **mismatch**, not exact. This replaces its
former incomplete result and adds comparison unit `reference-0041c330`; totals
are now 885 exact / 66 mismatch / 264 incomplete and 951 units. No original extent,
binding, normalization or comparison rule changes. Frame alignment and other
instruction differences remain; equal extents are not a near-exactness measure.
The existing boundary row is now `strict-compared`, with unchanged geometry.

`Player::compute_damage_to_enemy` uses a zero-tested bounded count, recovering
the original JNE instead of JG. It remains 769/774 bytes and incomplete. The
original logic realigns its frame while its damage callee does not; the candidate
still has the opposite arrangement. Do not force either frame.

The same final image passes **648 complete native calls** (278 Boss, 118 damage,
126 collision and 126 shield cases without transitions) and **204 prefixes**
(126 collision, 78 shield transitions). Complete calls include real collision
helpers and independent state expectations. Shield prefixes stop before animation
replacement, so resource startup, effects and allocation remain untested. The
full collision cases use the compiler-probed dead Player state to avoid death
resources. Due ECL transitions and whole Boss scripts remain outside the fixtures.

Keep `.analysis/boss-flow-work/`, especially `final-image/`, `complete-scope/`,
`final-regression.json`, native reports, model/enum probes, rejected forms and
prefix-chain controls. New no-frame prefix mode 5 requires an unchanged exception
chain; existing mode 4 retains its SEH-frame guard. The first reused ECL-host
smoke refused the Boss frame and is invalid. Final controls accept an ECL prefix
in mode 4 and refuse it in mode 5. All 885 prior exact owners and 169,575 exact
primary bytes are preserved; source-origin review remains open and Factory
acceptance is not submitted.

### Earlier ECL work

For the preceding `52ec72d` checkpoint, read
[ECL angle and orbit initialization](knowledge/ecl-angle-and-orbit-initialization.md).
Instructions 441/443 retain end time, method, zero tangents, initial,
goal and reset in the original order. The delta remains a separate value;
overwriting the angle changed floating operands and write order and was restored.
Circular/elliptical initialization now copies complete tangent vectors, recovering
integer copies from live `g_zero_vec2`. The compiler still merges reads and
reorders other initialization writes differently from the original.

The `52ec72d` image passes **744 angle**, **768 orbit**, **1,157 movement**,
**108 difficulty** and **612 lookup** complete paired calls, plus **140 spell**
and **42 animation** prefixes and a prefix negative control. The new independent
state models check timer initialization, modes, sentinel fallback and final
coordinates. Raw special-value angle goals use the unmodified original as the
bit-pattern reference. Orbit geometry starts with finite zero angles; subsequent
interpolation frames and full Boss scripts remain untested.

At that checkpoint, the complete packet is **21,408 original / 21,316 candidate
bytes**, with all three tables, 182 target slots and the 702-byte map. Smaller size is not exact
credit. Its frame is **`0x478` original / `0x498` candidate**, eight bytes
larger than the previous candidate frame; register and lifetime work remains.
Preserve `.analysis/ecl-angle-work/`, especially `final-image/`, `complete-scope/`,
`final-regression.json`, rejected forms and native fixtures. Its `before-comment/`
image is historical; the final source-comment correction leaves complete owner
bytes unchanged but changes artifact identities. A premature diagnostic correctly
refused a stale build receipt; retain its refusal log.

The isolated full replay preserves all 885 exact owners and classifications,
169,575 exact primary bytes and 950 units. Source-origin review remains open;
Factory acceptance is not submitted. The Oracle still refuses the dispatcher;
no binding, boundary or comparison rule changes.

That ECL refusal lists seven unbound fields: EH handler, four `g_zero_vec2`
references, private sin/cos helper and BossDead literal. The previous count of
ten included six vector references and an incidental decode inside the map;
the reduction does not establish any new identity. The original store between
remap and dispatch still exceeds the existing switch proof.

The preceding coordinate work is documented in
[ECL coordinate evaluation and animation offsets](knowledge/ecl-coordinate-evaluation.md).
Instruction 324 now uses explicit found/self branches, recovering the
original pointer-getter and coordinate-read sequence without floating spills.
Its case slice is 88 bytes against 82 original bytes; an extra manager load
remains. Instruction 338 now adds the offset vector to the enemy position.
This recovers the original X operand and its NaN payload result, while retaining
the Y/X argument-read order and the Z addition by zero.

All **612 complete lookup calls** agree with original and independent full-state
expectations. All **42 animation prefixes** agree; the preserved `a29e605` image
fails 18 of those same cases. The prefixes stop before allocation, so VM creation
and effect/resource behavior remain untested. The earlier **1,157 movement**,
**108 difficulty**, **140 spell-prefix** and default-return negative controls also
pass on the coordinate checkpoint image. At `90e049a`, the complete dispatcher
diagnostic was **21,408 original / 21,348 candidate bytes**, including all three
tables and the full map. Its frame was `0x478` original / `0x490` candidate.

Keep `.analysis/ecl-context-work/`, especially its historical-image control,
typed layout/enum probe and `INVALID-OPCODE.txt` notes. The first lookup protocol
mistook opcode 800 for alive opcode 555; its positive expected-state assertion
refused it before candidate execution. Use `native-lookup-verified/`, not that
failed protocol or its empty-list smoke. Preserve the lookup's existing
last-visited-enemy result for a missing nonzero ID in a nonempty list.

The full strict replay preserves all 885 exact results and classifications,
169,575 exact primary bytes and 950 units. No Oracle rule, binding or accepted
owner scope changes. The large function still needs formal table/EH identity
review and further source work; its local case slices grant no exact credit.

Read [ECL position setup and spell-name decoding](knowledge/ecl-position-and-spell-name.md)
for the preceding `a29e605` checkpoint. `ecl_run_over_300` shares the position/curve initial-goal-timer path,
advances the spell-name destination with a forward counter, and retains separate
Lunatic/default branches to recover both four-entry difficulty tables. The
complete diagnostic scope contains **three dispatches**, 182 target slots and
702 map bytes: **21,408 original / 21,384 candidate bytes at that checkpoint**. An early main-only
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
