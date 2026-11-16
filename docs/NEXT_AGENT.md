# Current TH16 reconstruction handoff

Updated 2026-11-16. Read AGENTS.md first. Keep local commits under the
gpt-web: ... prefix; do not push without the user's request. Work in natural
C/C++, without inline-assembly or padding substitutes. Preserve existing dirty
work and the ignored .analysis/ evidence. Rebuild incrementally and compare
the affected owner, not the whole cold replay.

## Repository checkpoint

- main code HEAD entering this handoff: f1d808d, ANM randomized-circle operand ordering.
- The branch is 68 commits ahead of origin/main before this note; the worktree
  is clean before the documentation edit.
- The historical broad reference audit and frontier metadata are stale for
  these changes. Do not cite their old exactness totals as current.
- Focused audit-reference.py --address 0x00431A70 is currently blocked during
  EH preflight: "EH parent lacks one complete candidate PDB owner". This
  prevents a strict receipt even for an unrelated small owner. Do not
  misrepresent local instruction similarity as accepted exactness.

## Large owner: EnemyData::ecl_run_over_300

- Target entry 0x0041DCB0. The separately reviewed dispatch/table boundary
  is 21,408 bytes; the annotated function record includes a wider 21,516-byte
  scope. Keep these distinct when comparing owners.
- src/EnemyEcl.cpp now contains no inline assembly and no artificial
  ecl_stack_reserve. Its former hand-coded EBP laser scratch frame is gone.
  The dispatcher still has 174 target and 174 candidate dispatch entries.
- Naturalized opcode families include MOVE_VEL, MOVE_VEL_TIME, MOVE_RAND,
  MOVE_CURVE, MOVE_POS_TIME, MOVE_BEZIER, ET_ON, ET_EX, SPELL,
  ANM_PLAY_HIGH/ABS/ROTATE, ANM_SET_MAIN/RESET/SELECTED_PLAY/316/SWITCH,
  laser controls, ET_CANCEL/CLEAR variants, HITBOX_RECT and
  BOSSES_INTERRUPT. EnemyData float argument wrappers were also
  reconstructed in C++.
- Four laser creation helpers now use LaserLineInner, LaserInfiniteInner,
  LaserCurveInner and LaserBeamInner and share the natural
  ecl_laser_start_pos() calculation. The Laser.h parameter layouts and
  the original source/destination field offsets were checked. The laser
  creation case ratios currently range about 0.54-0.63, so
  complete-owner work remains.
- Some naturalized handlers compile differently from the target. The focused
  case extractor normalizes registers, address operands and branches; use it
  only to find structural differences, not to assert a strict match.
  Important remaining investigations include the timed velocity, timed
  position and timed angle source expressions, ECL getter ordering, switch
  frame allocation and the complete owner/PDB boundary.

## Leaf functions: LaserManager cancellation

- LaserManager::cancel_in_radius (0x00431A70, 119 target bytes) and
  LaserManager::cancel_in_rectangle (0x00431950) are now ordinary
  C++ methods, not naked functions. src/Laser.cpp has no inline assembly.
- The rectangle traversal skips cancelled or unticked lasers; the radius
  traversal skips cancelled lasers. Both save the cancellation geometry,
  traverse safely using next before a virtual call, and sum results.
- After placing the manager list-head read before geometry stores, the local
  register/address-normalized instruction-sequence ratios were approximately
  0.964 (radius) and 0.970 (rectangle). The rectangular virtual call passes
  mode 5 and skip-invulnerability 1 in the candidate, matching the target's
  specialized call. These are not strict Oracle receipts.

## Second large owner: AnmVm::run

- Target 0x0045F980, 14,177 bytes. Prior natural C++ changes split
  END/DELETE and STATIC return paths and restored the frozen-world early
  return. FSET_RAND is partially aligned; its shared store tail and
  FSET_MOD, opcode 106/112 and circle-position cases need more work.
- For ANM only, the byte dispatch map is indexed by opcode + 1.
  A direct opcode index selects the wrong blocks.

## Follow-up reconstruction of the ANM and ECL interpreter owners

- Five new natural C++ code commits follow the previous handoff:
  63127c5 (FSET_RAND uses the RNG range helper before resolving its
  destination), fc019b5 (CIRCLE_POS explicitly stages radius, angle and
  Y/X output pointers), 95d3892 (FSET_ADD/SUB/MUL/DIV and FSET_MOD use
  target-observed argument evaluation order), 9700df8 (integer ECL
  argument stack lookup is typed C++ instead of naked early-return
  assembly), and 5b59bd7 (the ADD opcode of EclRunContext::ecl_run
  is natural stack.pop_int / stack.push_int arithmetic).
- AnmVm::run still has 134 target and candidate dispatch entries.
  FSET_RAND draws and scales before resolving the output pointer. In
  63127c5 the compiler cross-jumped into the FSET_MOD write tail,
  yielding a 54-byte prelude. The subsequent 0357108 checkpoint stages
  the output destination separately: it now has a dedicated 102-byte,
  25-instruction case versus the 96-byte, 24-instruction target case.
  Its register allocation and source layout remain unresolved.
- ANM circle position opcode 130 now has explicit input/output
  evaluation order. The current target and candidate blocks measure
  146 and 150 bytes respectively. FSET arithmetic opcodes 113, 115,
  117, and 119 each retain 103-byte, 27-instruction blocks on both
  sides after their C++ rewrite; do not mistake same-size code for
  exactness.
- EclRunContext::get_int_arg_given_value (target 0x00473E40) no longer
  uses naked ASM to return from local/typed stack branches. It reads
  EclStackEntry and converts only float-tagged values to integer.
  The target's 175-byte original owner was previously marked exact
  when the source still contained ASM; that old status is stale.
  The new local normalized instruction comparison was approximately
  0.93 and still differs in its stack-entry address calculation.
- EclRunContext::ecl_run (target 0x00472030, 7,046 bytes) now handles
  ECL_OP_ADD by popping right then left, adding and pushing an integer,
  the same way its SUB/MUL handlers are expressed. Its local
  normalized case-50 similarity was about 0.59; the complete owner
  remains unverified. src/EclRunContext.cpp currently has no __asm.
- Each code change was compiled using the preserved incremental
  build graph. The branch has not been pushed and no full cold replay
  was run. Full strict Oracle work remains blocked by the existing
  EH-parent PDB ownership preflight, not by the local case comparator.

## Subsequent 2026-11-16 interpreter reconstruction

Eight additional C++ checkpoints from the latest session are:

- c7738ef: ET_EX/FULL/NEXT/FULL_NEXT use direct opcode cases to choose
  argument starts, additional transform fields and next-slot updates.
  This improved their shared case ratio from about 0.48 to 0.82.
- 0357108: restores a dedicated FSET_RAND result-store path in
  AnmVm::run instead of the former FSET_MOD cross-jump.
- b0a7192: updates MOVE_VEL_TIME to read the duration and store each
  interpolator's initial, end time, method, bezier tangents and goal in
  the target-observed order; the case ratio rose from ~0.59 to ~0.71.
- 7b47342: LaserManager::cancel_in_rectangle passes the target's fixed
  CANCEL_BOMB and protected-laser arguments (5, 1) to the virtual
  cancel call, rather than passing through unused function parameters.
  Target Ghidra showed the two hardcoded values and the function's
  bomb callers; this is a semantic correction in a leaf.
- 0a85e4b: MOVE_CURVE selectors evaluate opcode predicates directly
  instead of maintaining separate booleans; ratio rose ~0.64 to ~0.78.
- e68be56: same direct-opcode selection for MOVE_POS_TIME variants;
  ratio rose ~0.71 to ~0.83.
- f56b83e: MOVE_VEL_TIME keeps the absolute and mirrored opcode tests
  at each use instead of cached booleans; ratio rose ~0.71 to ~0.82.
- dcd922d: ET_EX rereads the opcode at each decision after getters;
  ratio improved further from ~0.82 to ~0.85.

All these changes use ordinary typed C++ with no ASM or padding. Each
was compiled with the existing incremental build and compared only by
the relevant case diagnostics. Current ECL case extraction still
reports 174 target and 174 candidate dispatch entries; recent local
ratios include MOVE_POS_TIME 0.84, MOVE_VEL_TIME 0.82, MOVE_CURVE 0.78
and ET_EX 0.85. Their differences are real and none is strict exact.
The laser creation cases remain around 0.54-0.63 and need substantial
future work. An experimental change to the multiplication operand
order of ANM circle interpolation did not improve codegen and was
reverted before commit. No cold replay or push was run.

The saved broad strict audit still predates this work and the
EH-parent candidate PDB ownership preflight remains the known blocker
for targeted strict audit. Do not bypass that evidence requirement.
The existing ignored .analysis/ build logs contain incremental proof.

## Current laser creation and ANM circle follow-up

The latest session committed six incremental natural C++ source checkpoints:

- fc2ebaa: choose the original staged-origin-and-transform-copy idiom for
  beam and curve laser creation, without regressing the line/infinite paths.
- 7abbf59: put laser line shooter type/color before angle normalization,
  and restore speed, position, sound and distance assignment order.
  Focused line-case similarity rose from roughly 0.60 to 0.70.
- df15b56: restore infinite laser shooter fields in the observed order,
  including type/color, timing, speed, origin, flags and argument 1.
  The relevant case ratio rose from about 0.54 to 0.65.
- 181a5a1: stage curve laser type/color, segment count, flags, sounds,
  speed and distance in the observed source sequence. The case ratio
  rose from about 0.56 to 0.68.
- 68bd661: compute laser origin coordinates locally and assign one
  D3DXVECTOR3 after selecting the absolute or relative path; restore
  beam laser color, angle, timing, length and distance order. The
  infinite and curve cases now have the same local instruction counts
  as the target, though they are not byte-equal. Beam's local
  similarity is about 0.74 versus about 0.63 at session start.
- 32a5134: in AnmVm::run's CIRCLE_POS opcode 130, read radius and angle
  first, then explicitly resolve the Y destination followed by X.
  This changed the candidate block to 146 bytes and 41 instructions,
  exactly the target's block extent and count; normalized similarity
  rose from about 0.83 to 0.951. The remaining discrepancy in the
  scoped block is a stack displacement (target esp+0x10 versus
  candidate esp+0xc), not proof of whole-owner exactness.

The current incremental build succeeds and the ECL dispatcher still has
174 target and 174 candidate entries. The current normalized laser case
ratios are roughly 0.70 (straight), 0.68 (infinite), 0.71 (curve),
and 0.74 (beam). These are local diagnostics, not strict acceptance.

Rejected, uncommitted experiments: an early-loaded radial-speed local
in LaserCurveInf::step_ex_angle_accel degraded its local sequence
similarity (about 0.973 to 0.568) and was reverted. Explicitly
separating the ECL typed stack payload offset in
get_int_arg_given_value gave no gain (~0.934) and was reverted.
AnmVm::transform_coords is approximately 0.93 locally with differing
Y/Z operation operand order; it was only inspected. Do not reinstate
these scheduling probes as padding or artificial fixes.

Full owner/relocation matching and the strict EH-parent provenance
preflight remain unresolved. Keep using focused builds and local case
inspection until the evidence gate can be satisfied. No full cold replay
or push was run, and the private target and build artifacts remain ignored.

## Further 2026-11-16 ECL dispatcher reconstruction

This session resumed at clean HEAD 4415938, built only the affected
candidate, and saved four natural C++ source checkpoints:

- e5b41c4: the five SPELL opcode variants now decrypt only the
  positive-length script bytes and use a native switch for the three
  contiguous difficulty-adjusted spell IDs. The shared block's local
  normalized case similarity rose from roughly 0.49 to 0.68.
- 4654a8b: the ET_ON opcode constructs its absolute or enemy-relative
  launch position as a Float3 instead of three unrelated writes. The
  local block similarity rose from roughly 0.47 to 0.56.
- 53cf666: the SPELL name decryptor advances the encrypted-source and
  decoded-destination pointers together, matching the observed source
  traversal more closely. The local ratio rose to roughly 0.71.
- e5dae3e: ET_ON uses the existing typed get_shot_origin helper shared
  with laser/bullet generation, removing duplicated branch logic; its
  local ratio rose to roughly 0.60. The two cases are semantically
  equivalent for the script's absolute-origin flag and offset.

The final focused build completed successfully with 1166 annotated
functions, 174/174 ECL dispatcher entries, and no full cold replay.
The separate EclRunContext::ecl_run still reports 67/67 entries; its
ADD case remains nonmatching (about 0.59 normalized similarity).
These local counts and scores are diagnostic only; complete-owner
boundaries, relocations and EH-parent provenance still require strict
Oracle verification.

Discarded experiments were evaluated in the same worktree and then
rolled back: an explicit ANM CIRCLE_POS_RAND arithmetic factor changed
the candidate to x87-heavy code, AnmVm::transform_coords vector-add
variants worsened/failed to improve register order, an early texture
cache in AnmManager::reload_texture reduced local similarity, and a
rebound manager object in copy_screen_to_sprite did not improve it.
A simplified FSET_RAND destination branch instead cross-jumped to the
FSET_MOD tail (54-byte block against a 96-byte target); retain the
dedicated natural C++ store path. Reversing named operands in the ECL
integer ADD case did not improve its local match. No downgraded
experiment was committed; all candidate evidence logs remain ignored
under .analysis/.

The next high-value problems are the full 21 KB upper ECL interpreter
owner, the 14 KB AnmVm::run owner (particularly random circle and
arithmetic tails), the four laser creation handlers and the unresolved
EH-owner PDB preflight. Continue to work at both caller and leaf
scope without ASM or artificial padding.

## Additional ECL movement and natural callback reconstruction

Five coherent natural C++ source commits followed the preceding ECL handoff:

- d86e4d0: the ECL MOVE_BEZIER / MOVE_BEZIER_REL cases select both the
  PosVel and InterpStrange1 directly from the instruction opcode rather
  than caching a boolean. The focused local case sequence improved
  from about 0.62 to 0.78.
- ccaf438: MOVE_RAND / MOVE_RAND_REL use direct opcode tests for their
  position, angle interpolation and speed interpolation. Their
  joint focused ratio rose from about 0.76 to 0.86.
- ed70707: the four MOVE_VEL variants use the original double-precision
  -999999.0 sentinel comparison, rather than rounding the sentinel to
  float before comparison. Local ratio rose from about 0.75 to 0.85.
  This also preserves the precision of the sentinel boundary.
- f84ba72: damage_source_on_hit_piercing (target 0x004474A0, 39
  bytes) no longer contains inline assembly. The hit callback finds
  the owning PlayerBullet through the source's bullet_index, returns
  its old damage, and changes subsequent hits to 1. The structure
  assertions check the 0xc0 bullet stride, source index at 0x88,
  and player-relative bullet damage at 0x11ac. Its linked candidate
  is 37 bytes, not the former exact assembler sequence; the old
  local-strict-pass annotation in config/functions.csv is stale.
- bdf7a7b: LaserInfiniteInf::on_tick (target 0x004352F0, 800 bytes)
  now has typed C++ for the formerly hand-assembled last part.
  The VM's scale.x is laser width divided by the ANM sprite width
  (sprite field +0x38); scale.y is laser hit_length divided by sprite
  height (+0x34). Each writes ANM_VM_SCALE_CHANGED. Target disassembly
  confirmed these respective offsets; source static_asserts guard
  the sprite layout. The native target has 210 instructions in the
  800-byte scope; this candidate currently has about 207 and its
  address-normalized local sequence ratio is about 0.84. It is not
  strictly exact. Neither src/PlayerShot.cpp nor
  src/LaserInfinite.cpp now contains direct inline assembly.

Incremental scripts/repo-python scripts/build.py passed for each code
change, still producing 1166 annotated functions. The upper ECL
dispatcher remains 174 target and 174 candidate table entries.
These are local diagnostic observations only, not complete-owner
receipts. The existing EH-parent PDB ownership preflight remains a
separate blocker for strict audit. No full cold replay or push.

Evaluated but reverted: switching the ECL drop-item x product's
commutative operand order left the compiled leaf unchanged;
staging Y/Z arithmetic in AnmVm::transform_coords left its 0.93
local ratio unchanged; adding an extra named snapshot id in
AnmManager::restore_snapshot degraded its local ratio from about
0.98 to 0.76; separating the ANM FSET_RAND destination into
explicit two-branch stores generated a larger 108-byte opcode
case than its 96-byte target and was reverted. The ignored
.analysis/ logs retain the focused build evidence.

High-value next investigations: restore more of the large ECL
movement families and laser creation handlers; improve the
ANM random circle and FSET_RAND owners; continue checking the
natural LaserInfiniteInf::on_tick against the full original
owner and its relocations. Do not reintroduce ASM or unused
padding solely to obtain instruction equality.

## ECL method guard, movement reset, and death effect reconstruction

This session made four C++ code checkpoints in the 21 KB
EnemyData::ecl_run_over_300 owner:

- 04844ae: ECL laser method opcode 714 evaluates argument 1 after the
  lookup and only invokes the virtual method for non-infinite lasers.
  Target assembly compares its object's vtable against
  LaserInfiniteInf::vftable after argument evaluation. The natural
  representation checks kind != LASER_INFINITE, which corresponds to
  the four initialized concrete laser kinds. This fixes an omitted
  behavior guard, not just scheduling. Local block ratio rose from
  about 0.67 to 0.79; both blocks now have 19 instructions.
- 47218d2: MOVE_RESET folds the first component of rel_pos into
  abs_pos with the target-observed source operand order and maintains
  natural component-wise addition for y and z. Directly after this
  change the local block ratio was 0.97; after changes elsewhere in
  the same large owner and a final incremental rebuild it is 0.92.
  This demonstrates that linked global register scheduling alters
  these normalized local measurements; do not report 0.97 as the
  current final score.
- 76116c4: DIE now calculates vertical distance before horizontal
  distance, checks the squared distance against the nearby-hit
  threshold and explicitly chooses the downward fallback angle
  only in the nearby branch. The local ratio rose from about
  0.66 to 0.79.
- 2e75ebf: DIE's distant-hit direction uses a natural Float3
  difference (final_pos.pos - last_damage_pos), then atan2(y, x).
  This generated 41 instructions, the same number as the target,
  and improved local normalized ratio from about 0.79 to 0.98.
  The remaining normalized difference is an equivalent source
  addressing form (base+0x48 versus final-position pointer+4);
  this is not proof of strict byte identity.

Re-ran incremental scripts/repo-python scripts/build.py after the
last source rollback; the candidate still contains 1166 annotated
functions. ECL has 174/174 dispatch entries and local scoped ratios
of approximately 0.79 (opcode 714), 0.92 (MOVE_RESET) and 0.98
(DIE). The stricter owner/relocation/EH-parent audit remains
unverified. No full cold replay, padding, inline ASM or push.

Exploratory edits reverted without commits: an explicit local
timeout index in ECL opcode 521 reduced its ratio; rewriting
MOVE_SPEED_TIME as a positive branch made no difference;
replacing LaserInfiniteInf::run_ex's BulletEx pointer with a
reference made no difference (195-byte target versus 188-byte
candidate, ratio ~0.77); naming a reusable Float3* for DIE's
position reduced its local ratio to ~0.88. Keep these observations
as starting points rather than treating the attempts as progress.
Preserve the local ignored .analysis/ incremental build logs.

Next work can pursue the large ECL ET_EX and laser-create blocks,
the separate 14 KB AnmVm::run owner (especially its RAND and
float-store operations), and natural caller/leaf improvements.
Do not confuse the previously saved strict-provenance blocker
with a successful exactness verification.

## Further ECL and ANM interpreter reconstruction

Five code checkpoints were added after the previous handoff:

- 08dd9fa: the four ECL laser constructors now share one typed
  EclLaserParamsStorage union. The constructor for the active laser type
  initializes the corresponding union member, then the parameter block is
  passed to allocate_new_laser. The build frame shrank from the previous
  0xea8 candidate allocation to 0x498; target is 0x478. This is a
  substantial stack reduction, not exact frame identity. The four laser
  constructor blocks still differ from target.
- ecc5a10: ET_EX uses a flattened shooter/transform offset with typed
  BulletEx field accesses; FULL's c field follows the target's special
  (ex_index + 0x22) record offset. The focused ET_EX family is now 133
  candidate instructions versus 134 target instructions, local normalized
  ratio about 0.91. The layout is guarded by source-level type offsets in
  the later ET_ON checkpoint.
- df130cb: ANM FSET_RAND now expresses the result as
  *ANM_FLOAT_PTR(0) = random * range;. Its local block is 24 instructions
  on both sides, ratio about 0.96. This is closer than the prior explicit
  destination temporary.
- fca5a51: ET_ON's origin calculation is inlined into the dispatcher and
  the now-unused get_shot_origin helper is removed. Static assertions
  verify BulletEx stride 0x2c, EnemyBulletShooter stride 0x380,
  transform-array offset 0x28, and the combined EnemyData transform
  base at 0x5c0. ET_ON improves from the old helper form's ratio about
  0.60 to about 0.87 (44 target / 46 candidate instructions). It is not
  exact; its branch-local z store and manager setup still differ.
- f1d808d: CIRCLE_POS_RAND reads its lower bound into a volatile local
  before reading the upper bound. This is behaviorally relevant:
  ANM_VAR_RAND_UNSAFE consumes the unsafe RNG, so argument evaluation
  order changes the random stream when either bound uses that variable.
  The focused block is 50 instructions on both sides, ratio about 0.90
  (prior compiler order was reversed and scored about 0.81).

Current focused diagnostics after the final incremental build:
- EnemyData::ecl_run_over_300: 174/174 dispatch entries.
- ECL DIE: 41/41 instructions, local ratio about 0.98.
- ECL ET_ON: 44/46 instructions, local ratio about 0.87.
- ECL ET_EX family: 134/133 instructions, local ratio about 0.91.
- ECL laser method 714: 19/19 instructions, local ratio about 0.79.
- AnmVm::run FSET_RAND: 24/24 instructions, local ratio about 0.96.
- AnmVm::run CIRCLE_POS_RAND: 50/50 instructions, local ratio about 0.90.

The final scripts/repo-python scripts/build.py completed and produced
1166 annotated functions. No full cold replay was run, and no new inline
assembly or padding was introduced. These case ratios are local diagnostic
comparisons, not strict owner or relocation receipts. The EH-parent PDB
ownership preflight blocker above remains unresolved.

Experiments reverted during this session:
- ET_ON's direct per-component writes degraded its local ratio to about
  0.60; a shooter-pointer temporary scored about 0.58. The retained
  aggregate D3DXVECTOR3 assignments are the best tested natural form.
- Reversing CIRCLE_POS_RAND's min/max source order is incorrect for the
  target's RNG read order. Expanding anm_lerp into an explicit expression
  added an instruction without improving the case. Making both bounds
  volatile did not improve on the retained lower-bound-only ordering.
- FSET_RAND volatile temporaries and explicit two-branch stores degraded
  the block. Keep the single ANM_FLOAT_PTR lvalue assignment.
- Shared laser storage and flattened ET_EX pointer arithmetic are retained;
  do not replace them with assembler or padding to force byte counts.

Next useful targets: reduce the remaining ET_ON branch-local z-store
mismatch; investigate the four laser creation handlers against their complete
owners; continue the large ANM run owner (especially modulo/store and
circle handlers); and pursue the strict EH-parent provenance blocker
without suppressing its checks.

## Verification and next actions

- Incremental scripts/repo-python scripts/build.py completed successfully
  after each code group. No full cold replay was run.
- Relevant upper ECL case diagnostics use
  .venv/bin/python .analysis/claude-tools/cases.py 0x41dcb0 <indices>.
  Current results are evidence for investigation, not exactness credit.
- Restore the remaining natural-source/target mismatches in the two large
  interpreters and related leaves. For complete-owner exactness, first resolve
  the EH-parent provenance preflight without suppressing its evidence checks.
  Keep artifacts in ignored .analysis/, and commit each coherent code result.

The latest code checkpoints, newest first, are 27af340, 5a6da44,
0331370, 795435f, 83bb3f0, ebb3ed9, 7f27400, and 9cb005b.
