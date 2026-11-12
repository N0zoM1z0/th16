# Curve laser vectors and speed accumulation

This continuation starts at `d56cd1c`. It changes the complete curve-node motion
functions in `src/Laser.cpp`, after restoring two unsuccessful Boss statistics
trials. Three natural vector expressions recover original floating operands and
remove **216 historical raw-output differences**. No new exact credit is claimed.

## Retained source

`LaserCurveNode::step_back`, at `0x00438370`, now scales velocity directly by
`speed - speed_delta` in its mode-1 sentinel branch. The former named `dt`
compiles with velocity X as the multiplication's first operand. The inline
expression instead retains the speed difference and folds velocity X into the
multiply, as in the original. This also removes the extra byte in that branch.

A real native example has different NaN payloads in velocity X and the speed
difference. The original X output retains `0x2222`; the old image retains
`0x1111`. The new image agrees with the original. This is an observed property
of the pinned compiler's generated instructions, not a C++ guarantee about
commutative expressions.

`LaserCurveNode::get_state`, at `0x00437ee0`, uses `D3DXVec3Add` for the two
polar vectors in mode 1. The previous `b + a` constructor expression gives X
different operands from the original. The explicit add recovers the original
X payload, including the resulting position and speed outputs.

Mode 2 now accumulates position with `pos += d`, followed by the speed update.
The original keeps speed in a register across whole-frame steps; the old image
spills it and adds the node's speed delta as the first operand. With distinct
NaN payloads, the old result retains the delta while the original retains the
current speed. The vector update keeps speed in a register and restores that
operand order. It also keeps position X in its stack slot, as in the original.
The tested `D3DXVec3Add(&pos, &pos, &d)` form produces identical complete code;
the shorter compound assignment is retained.

No alignment directive, register constraint, unused local, extra double or
comparison mask is introduced. `Enemy.cpp`, `Player.cpp` and `Collision.cpp`
are restored byte for byte to the starting checkpoint.

## Complete owners and remaining differences

| Owner | Original bytes | Starting candidate | Retained candidate |
| --- | ---: | ---: | ---: |
| Curve state, `0x00437ee0` | 1,164 | 1,149 | 1,162 |
| Curve reverse step, `0x00438370` | 986 | 987 | 986 |

All executable bytes are decoded and retained in
`.analysis/boss-stats-work/complete-scope/`. The packet also retains complete
Boss logic, damage and collision owners because they belong to the same final
linked image. Original extents are unchanged.

The reverse step still has different registers and operands in its mode-1
squared-length calculation. State mode 2 still has different local slots and
scheduling: its retained speed is XMM5, while the original uses XMM6. Equal or
nearby extents do not establish exactness.

Strict replay refuses two unbound call fields in each curve owner: the floor
dependency and intrinsic atan2 entry lack accepted identity proofs. The
[atan2 dependency investigation](atan2-runtime-dependencies.md) remains open.
Executing these real callees does not authorize bindings, normalization or
partial-owner acceptance.

## Native comparison

The final **768 paired complete curve calls** run after actual executable CRT
startup and stop at the existing WinMain entry before fixture execution. The
original, preserved `d56cd1c` image and final image execute their actual motion,
sin/cos and CRT routines. No callee or import is replaced.

The matrix includes both functions, modes 0/1/2, two unsupported modes, negative
and fractional times, multiple whole frames, the mode-1 sentinel, and three x87
precisions. Raw positive/negative quiet and signaling NaNs exercise distinct
velocity, angle, speed and speed-delta payloads.

| Historical difference | Cases | Retained differences |
| --- | ---: | ---: |
| Reverse-step X multiplication | 96 | 0 |
| State polar-vector X addition | 24 | 0 |
| State multi-frame speed accumulation | 96 | 0 |

Every case checks the entire node, its canary and the complete input/output
arena. **168 cases** have independent full-output expectations: straight motion,
unsupported-mode preservation and an analytic sentinel displacement. The latter
also checks the incoming speed/angle ABI and that this branch ignores time.
Other arithmetic outputs use the unmodified original as their raw-bit reference.
The runner checks preserved registers, stack cleanup, exception-chain restoration
and floating controls. EAX is not compared as a result of these void functions.

The fixed inputs and separate output objects leave overlapping-output behavior,
CRT errno/matherr state and general caller/resource effects outside this matrix.
These are diagnostics, not an end-to-end run of shipped Boss scripts.

## Restored trials

- A Boss current-life local gives 2,226 bytes and leaves the statistics reload.
  An explicit life-object pointer gives 2,223 bytes with another address reload;
  neither is retained.
- Scalar-left multiplication and `D3DXVec3Scale` leave the original reverse-step
  problem. Component vectors give 981 bytes, component positions 987, and copied
  velocity/position forms 1,012; they do not recover the original sequence.
- Replacing the reverse-step sum with `b + a` leaves its squared-length problem
  and introduces 24 additional turning-payload failures. It is restored.
- Moving state scalar declarations before the position gives 1,165 bytes and
  leaves speed spilled. The expanded matrix refuses its 96 discrete-speed
  failures. It is restored.

History review confirms that four unused integer locals were previously removed
from state evaluation in `1da68af`. They are not reintroduced to influence code
generation. Earlier driver versions, their hashes, full trial packets and failed
native reports remain in the private evidence directory.

## Final checkpoint

The same final image passes **3,364 complete native cases and 204 prefixes**:
the 768 new curve cases and all 2,596 preceding Boss-phase, damage, impact,
geometry, collision and shield cases. The preceding 96 impact and 27 collision
historical failures remain zero in the current image. Observation, protocol,
exception-chain and phase negative controls also pass; 23 actual CRT startup
stops are authenticated.

The first copied observation control lacked its layout-probe source/executable;
those retained files were supplied. A manual control continuation then used the
system Python, which the locked Capstone check correctly refused. The controls
were rerun under the repository interpreter. No game suite was rerun merely to
replace a failed wrapper log, and neither setup failure is passing evidence.

The source input is
`47b99f84e47d04f3983ea93f1b716a841b562b7c12e87ba2be5c03ceace42942`,
PDB age **253**. The full strict replay and progress check preserve **885 exact,
65 mismatch, 265 incomplete**, **169,575 exact primary bytes** and **950 units**.
No classification changes or lost exact owners occur. Only the generated unit
ledger's linked addresses change; original geometry and comparison rules remain
unchanged. All builds are incremental.

Keep `.analysis/boss-stats-work/`, especially `final-image/`, complete owner
packets, the typed curve layout probe, `native-curve-final/`, historical-image
receipt, rejected source forms, replayed Boss reports, controls and
`final-regression.json`. Source-origin review remains open; Factory acceptance
is not submitted. No repository contents were pushed.
