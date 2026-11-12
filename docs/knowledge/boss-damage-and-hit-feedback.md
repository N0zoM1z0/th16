# Boss damage, hit feedback and source traversal

This continuation starts at `a95321e`, with 885 exact owners. Private evidence
is retained in `.analysis/boss-core-work/`. Compiler profiles, original
boundaries and normalization fields are unchanged. A replay coverage repair
uses an existing compound-table proof, as described below.

## Retained source work

`EnemyData::step_logic` at `0x0041c330` now contains the original inline
low-life hit-sound decision. Its once-called private helper is removed. Spell
flags are read inside the boss/large-life short-circuit condition, including
the separate periodic flash condition. The complete candidate grows from
2,092 to **2,196 bytes**, against the independent **2,207-byte** original.
It remains incomplete and receives no exact credit.

The recovered sound thresholds are strictly below 200 during a spell and 900
otherwise. A survival spell suppresses that alternate sound. Periodic low-life
flashing uses strictly below 100/500, with the same survival-spell exclusion.
The regular hit flash still lasts four frames and the explicit hit-sound
override remains in place.

`Player::compute_damage_to_enemy` at `0x00445a30` now advances a source pointer
with a bounded remaining count, recovering separate source and timer pointers
in the generated loop. Its complete candidate grows from 735 to **769 bytes**
against **774 original bytes**. The timer query reuses
`ZunTimer::ticked_on_multiple_of`; that change alone generated the same code
as the original direct condition. The traversal change recovers the two-pointer
shape. This owner also remains incomplete, with no exact credit.

The complete prologues still differ: the original boss logic realigns ESP to
eight bytes, while its damage callee does not; the candidate has the opposite
arrangement. Register lifetimes, loop layout and collision temporaries also
differ. These observations do not establish which source or calling-context
change will recover the original. Do not force alignment, add dead doubles,
pad either owner or accept a shared prefix.

## Rejected shield forms

A main-bomb pointer snapshot produced a 2,195-byte logic owner, but hoisted
the subseason pointer and changed the flag registers. A conditional main-state
snapshot with a common shield exit also produced 2,195 bytes and hoisted the
state read. Neither recovered the original conditional reads or frame. Both
are restored; the original shield condition is retained. Their sources, full
disassemblies, build logs and focused extent refusals remain in the evidence
directory.

The earlier inline-sound experiment was restored at its historical checkpoint.
This continuation retains that source direction after adding complete-path
behavioral diagnostics. It does not reinterpret the historical failed extent
comparison as an exact match.

## Actual instruction diagnostics

The diagnostics map the unmodified original and candidate PE images into
separate Unicorn instances. No game function, callee or API is patched or
stubbed. The parent uses the locked repository environment and
`strict_oracle.Context` to fingerprint inputs before and after execution; the
child uses the existing global Python Unicorn 1.0.2 installation. Unexpected
memory accesses, instruction limits and calling-convention failures fail a case.

The historical compiler builds a small native layout probe. Wine executes that
probe only to print Win32 field offsets and object sizes; it does not execute
the game. Those offsets are checked against the original instruction accesses.
The probe source, executable, output and hashes are retained.

The **118 damage cases** compare the full Player storage, source updates,
output pointers, score state, return value, preserved registers, stack cleanup
and floating control settings. They cover:

- Circle/circle, circle/rectangle, rectangle/circle and rectangle/rectangle
  tests, with inside, boundary and outside positions and three x87 precisions.
- Source indices 0, 1, 127 and 255, and the unused extra entry at 256.
- Paused and repeated frames, hit intervals, signed frame values, inactive and
  bomb sources, repeated enemy IDs, damage caps and nullable output pointers.
- Source damage accounting, exhaustion, score updates and multiple sources.

The **278 boss cases** execute the complete logic function with valid fixture
objects and no due life/time interrupt. They compare the full enemy, Player,
VM, sound manager, Globals, enemy manager, Spellcard and GUI storage, along with
returns, register preservation, stack cleanup and floating controls. Cases cover
boss/large-life flags, active and survival spell combinations, threshold
boundaries, existing flashes, sound overrides and a missing VM. Actual sound
queuing and timer callees execute. A non-boss, undamaged case with no Spellcard
object verifies the original conditional spell-state access.

All **396 cases agree**, with zero faults. Independent observation controls
also check known return values, the source-array boundary, source exhaustion,
score changes, sound IDs 34/35 and their 900/200 boundaries, the 500/100 flash
boundaries, survival sound selection and untouched paused-frame outputs. The
complete core cases run with pending damage or zero-sized hurtboxes, so they
do not replace the separate damage-collection cases.

This is partial instruction-emulation evidence, not native game execution,
whole-game validation or exactness credit. Bomb virtual damage, nonzero source
hit callbacks, real animation resources, shield replacement, graze/death paths,
season item creation, active ECL transitions and allocation paths remain outside
these fixtures. The net five/eleven-byte extent gaps do not prove that only
five/eleven individual instruction bytes differ.

## Verification and evidence

Relinking moved the already accepted 680-byte window procedure. Its first
target-table entry then stopped Capstone after 612 bytes; earlier addresses
happened to decode through the byte map and second target table. The existing
`compound-bounded-v1` record already proves all 609 code bytes, three padding
bytes, both target tables, the intervening 24-byte map, every guard/edge and
exhaustive relocations on both sides. The observed code and complete replay
remain equal.

Replay now revalidates that existing proof against the same image objects and
requires decoding through the full executable extent. It does not require
table bytes to be x86 instructions. All 680 bytes are still replayed, including
raw map/padding bytes and every bound relocation. Unreviewed owners retain the
existing decoder/data-span rules. Controls reject a failure inside real code,
missing ownership, foreign images and a modified original hash; existing map,
slot, guard, relocation and padding controls remain in force. This restores an
existing exact result and grants no new credit.

The final incremental build retains the historical profiles. Focused strict
reports refuse both complete extents. Full strict regression and current
progress evidence are retained alongside the diagnostic reports. All 885 prior
exact owners are preserved, with 169,575 exact primary bytes and 950 units.
Compound controls (26), switch controls (40), Oracle controls (14) and focused
audit controls (3) pass. Standalone window-procedure replay is exact over all
680 bytes. Source-origin review remains open and Factory acceptance is not
submitted.

Useful files:

- `final-focused.json`, `full-audit.log`, `regression-check.json`, `progress.log`.
- `emulated-{damage,core}-report.json`, `observations-check.json`, case inputs,
  separate image/job/output files and emulator source.
- `logic-context.txt` and its game-owned Ghidra outputs; baseline and trial
  complete disassemblies, source snapshots and build logs.

Use current ledger totals from `docs/NEXT_AGENT.md`; this review grants no new
exact owner or primary-byte credit.
