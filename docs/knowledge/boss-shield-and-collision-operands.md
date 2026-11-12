# Boss shield flow and collision operands

This continuation starts at `52ec72d`, with 885 exact owners. It changes the
large `EnemyData::step_logic` owner at `0x0041c330` and the damage-source loop in
`Player::compute_damage_to_enemy` at `0x00445a30`. Preserve
`.analysis/boss-flow-work/`, including failed combinations and the final image.
The pinned reference checkout is unchanged and supplies no acceptance authority.

## Shield control flow

The shield-enabled case now has an outer condition of its own. Its inner
conditions enable the shield when a bomb is active and disable an existing
shield when both bombs are inactive. The outer else retains the existing
disable operation even when the shield-enabled flag is absent. Keeping both
source disable bodies allows the compiler to merge the original common path.

This recovers the original main-bomb load, conditional state read, subsequent
subseason-bomb load and reuse of the main state in EDX. The preceding combined
condition hoisted the subseason pointer and reloaded the main state instead.
The generated enable/disable calls, state writes and internal branches now have
the original arrangement. There is no explicit state snapshot in the retained
source: ordinary compiler common-expression elimination supplies the reuse.

A 156-byte diagnostic slice, starting after the original frame realignment,
has equal instructions after checking the identities of its three data fields
and two calls against existing bindings. This is source-shape evidence inside
the full owner, not a separately accepted owner or 156 bytes of exact credit.
No symbol binding, original boundary or comparison rule is added.

## Collision position operands

The rectangular collision path now forms
`final_pos.pos + Float3(x, y, 0.0f)`. Under the pinned compiler and retained
shield structure, this preserves the original X operation: rotated offset first,
enemy position second. Y still adds the offset to the enemy position, and Z
still executes its addition by zero. Trigonometric calls and their order remain.

The difference is observable. With enemy X `0x7fc05678` and a rotated offset
carrying `0x7fc01234`, the original passes the latter payload to the collision
callee. The historical candidate passes the former. All 27 observed historical
payload failures now agree with the original, with no game-side special handling
or floating-operand normalization in the Oracle.

Expression shape alone was insufficient. Offset-first vectors, D3DXVec3Add,
in-place offset storage and a separate fallback branch were tried. Several
produced the same wrong instructions. A position-first vector fixed the issue
before the shield edit, but adding an explicit branch-local bomb-state snapshot
restored all 27 failures. Keep `combined-first/` and its failed prefix report.
Removing that snapshot and retaining ordinary nested conditions recovers both
the shield shape and floating result. This interaction is why final diagnostics
must execute the combined source image, not independently successful trials.

## Complete owners and remaining differences

The logic candidate changes from 2,196 to **2,207 bytes**, equal to the complete
independent original extent. The strict Oracle now decodes and compares every
one of those 2,207 bytes and resolves its linked fields through existing
bindings. Its result changes from **incomplete to mismatch**, not exact.
Equal extents do not imply equal instructions or a small remaining difference.
The existing boundary row becomes `strict-compared`; its start, size and end
remain unchanged. All 62 linked fields use existing identities.

The original logic realigns ESP to eight bytes; the candidate still does not.
Its damage callee has the opposite alignment arrangement. Collision temporaries,
register allocation and other instruction differences remain. No alignment
pragma, dead local, artificial double, padding or shortened comparison is used.

The damage-source loop now tests its bounded remaining count against zero,
recovering the original JNE termination instead of JG. It still visits precisely
256 sources and excludes entry 256. Its complete candidate remains 769 bytes
against 774 original bytes and is incomplete. Separate source/timer pointers
and the previous accounting behavior are retained.

## Native evidence

The game-local debugger executes unmodified original, current candidate and,
for the new cases, the preserved `52ec72d` image. Historical PE/MAP/PDB hashes
are checked against their receipt. Fixtures write data only; game instructions,
imports and callees are not replaced. Complete calls check return value, stack
cleanup, preserved registers, floating controls and exception-chain restoration.

The final image passes **648 complete paired calls**:

- 278 existing Boss logic cases, including hit sound, life thresholds and flash.
- 118 damage cases, including collision shapes, source boundaries and accounting.
- 126 rectangular-collision calls, with a dead Player to avoid death resources.
- 126 shield cases that complete without an animation transition.

It also passes **204 prefixes**:

- 126 collision prefixes observe the actual position pointer and stack arguments
  immediately before `Player::check_hit_rotated_rect`. They cover VM absence or
  presence, three VM angles, three x87 precisions, finite values, signed zero,
  quiet/signaling NaNs, infinities and subnormals. The historical image fails
  27; the retained image fails none. Unchanged fixture objects and finite
  no-VM coordinates are checked independently.
- 78 shield transitions stop immediately before the actual
  `AnmId::replace_with_effect` call. The model checks script arguments,
  `anm_set_main`, unchanged storage and both enable/disable paths. Together
  with the 126 complete shield cases, the matrix covers enabled/raised flags,
  bomb states -1/0/1/2, three precisions and a null subseason pointer when the
  main bomb short-circuits its use.

The preceding 396 Boss/damage cases also agree with independent instruction
emulation and existing observation controls for score, exhaustion, thresholds,
conditional spell access and paused outputs. The new collision calls execute
the real collision helper, while prefixes expose temporary values that do not
persist in the enemy object. Complete calls alone did not detect the payload
regression in the rejected combined image.

Shield transition prefixes do not execute animation replacement, allocation or
effects. The complete collision fixtures use `PLAYER_STATE_DEAD` from the
compiler enum probe. Real Player deaths, grazing, due ECL interrupts, resource
startup and complete Boss scripts remain outside this evidence.

## Prefix host and failed protocol

The initial prefix smoke reused an ECL host that required a stack SEH frame.
The Boss owner has no such frame, so the host refused the original observation.
That smoke grants no behavioral credit; retain its `INVALID.txt` note.

The local host adds explicit no-frame prefix mode 5, requiring the exception
chain to remain exactly at its initial head. Existing mode 4 retains its original
stack-frame guard. Controls accept an actual ECL prefix in mode 4 and reject
that same SEH frame in mode 5. The final Boss suites pass mode 5. A first control
parser expected failure text on stderr; Wine returned it on stdout. The final
parser authenticates the combined output and exit status.

## Checkpoint

The final incremental build has PDB age **216** and source input
`63cfdc1769d7404dc72afbdb9cb0d7903159eb2d65f3c285d9f923ad9f6cacf2`.
The isolated full replay preserves all 885 exact owners and 169,575 exact primary
bytes. The only classification change is the complete logic comparison above:
**885 exact, 66 mismatch, 264 incomplete** among 1,215 annotations.
There are **951 retained comparison units**, including the new mismatch unit
`reference-0041c330`; it adds no exact credit. All preceding units retain their
identities and scopes. Source-origin review remains open and Factory acceptance
is not submitted.

Use `final-regression.json`, `complete-scope/`, `shield-shape.json`,
`native-collision-final/`, `native-collision-complete-final/`,
`native-shield-final/`, `native-focused-report.json` and `prefix-chain-controls.json`.
The regression check verifies their common final PE/MAP/PDB/receipt identities.
Trial directories and `combined-first/` are historical, including passing
individual trials that failed when combined.
