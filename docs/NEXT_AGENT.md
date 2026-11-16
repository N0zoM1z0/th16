# Current TH16 reconstruction handoff

Updated 2026-11-16. Read AGENTS.md first. Keep local commits under the
gpt-web: ... prefix; do not push without the user's request. Work in natural
C/C++, without inline-assembly or padding substitutes. Preserve existing dirty
work and the ignored .analysis/ evidence. Rebuild incrementally and compare
the affected owner, not the whole cold replay.

## Repository checkpoint

- main code HEAD entering this handoff: 5b59bd7, natural ECL expression stack addition.
- The branch is 30 commits ahead of origin/main before this note; the worktree
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
  The FSET_RAND candidate now draws and scales before resolving the
  output pointer. The compiler cross-jumps to the FSET_MOD write tail;
  target opcode 123 has a separate 96-byte block, while the current
  candidate entry contains a shorter 54-byte prelude. This is
  meaningful semantic restoration, not byte identity.
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
