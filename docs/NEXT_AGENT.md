# Current TH16 reconstruction handoff

Updated 2026-11-16. Read AGENTS.md first. Keep local commits under the
gpt-web: ... prefix; do not push without the user's request. Work in natural
C/C++, without inline-assembly or padding substitutes. Preserve existing dirty
work and the ignored .analysis/ evidence. Rebuild incrementally and compare
the affected owner, not the whole cold replay.

## Repository checkpoint

- main code HEAD entering this handoff: dcd922d, directly reloaded ECL transform opcode.
- The branch is 39 commits ahead of origin/main before this note; the worktree
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
