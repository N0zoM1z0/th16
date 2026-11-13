# ECL interpreter order and private callee

This continuation starts at `f976acb` and concentrates on the complete
`EclRunContext::ecl_run` at `0x00472030`. Eight natural source forms are
restored. The interpreter remains **incomplete: 6,942 candidate bytes against
7,046 original bytes**. No large function becomes exact in this checkpoint.
Only an existing 32-byte private helper receives new exact credit after its
identity is independently reviewed. No game runtime or emulation is used.

## Complete original interpreter

The original-only CFG accounts for all **1,645 instructions**, with every
instruction reachable from the entry. The complete scope comprises 6,683 code
bytes, one padding byte, 67 four-byte switch targets and a 94-byte opcode map.
Both returns, at offsets 290 and 6,682, are owned. The whole-scope SHA-256 is
`bd5771b962232fb3ccda37e8609a507ad321801a646b9112d9f1bd98ea4227b2`;
the code SHA-256 is
`4d8e3e5bbe1ec2487a7819d47c3c3c526fdcb9da197183e25cc407586f6c307c`.

The restored candidate has 6,579 code bytes, one padding byte, the complete
362-byte table/map suffix and 1,615 instructions. Its complete SHA-256 is
`9aa2daf0190636a411ccf022307363521da1e28534ed3ac80fdfcc26f529d871`.
All trial packets retain the complete original and candidate scopes, including
every table target, map byte, relocation and decoded linked field. None uses a
shortened comparison span.

## Qualified private dependency

The original calls at `0x00473408` and `0x0047390A` reach the 32-byte
`ecl_sincosmul` at `0x00474510`. The corresponding candidate calls, at owner
offsets 4,958 and 6,251, reach the private producer in `EclRunContext.obj` at
`0x00424650`. Their operand fields were the interpreter's two remaining
unbound fields.

The new `functions.ecl_context` record in `config/static-functions.toml` uses
the existing, unchanged `x87-sincos-scale-v1` verifier. It checks the complete
14-instruction original and candidate, the source-qualified MAP/PDB producer,
the complete original boundary and the absence of relocations or linked fields
inside the helper. The complete helper SHA-256 is
`a50437b23b41970d8419b08c34293566d683282156f7ff73b7e73198b15bd19a`.
The witness independently validates the complete original interpreter's owned
switch data and code hash, the bounded opcode guard/remap/table, and an entry
path through that dispatch to the call. All **34 static identity controls** pass.
No verifier implementation or compiler setting changes.

The same private symbol spelling also occurs in `EnemyEcl.obj`. Its candidate
entry at `0x0042D160` is a different producer; the upper dispatcher calls an
original helper at `0x00426260`. The new record does not bind that producer or
resolve any of the upper dispatcher's seven unbound fields. Its compound
dispatch and complete identity remain separate work.

The lower interpreter now has **zero unbound fields**. Strict comparison still
refuses its complete extent. Closing a callee identity does not establish the
parent's body or layout.

## Restored complete source trials

| Source form | Complete candidate | Finding |
| --- | ---: | --- |
| Reference to the final interpolation destination | 6,942 | Complete bytes identical to baseline |
| Separate arithmetic and expression integer scratch values | 6,942 | Register/addressing changes; original exits and layout remain unmatched |
| Logical NOT instead of comparison with floating zero | 6,942 | Complete bytes identical to baseline |
| Direct SETF tag predicates instead of a named byte local | 6,942 | Does not recover original destination EAX and type/offset ECX |
| Explicit integer ternaries for all 16 predicate results | 6,942 | Complete bytes identical to baseline; does not recover carried EDX = 1 |
| Union-valued floating pop | 6,990 | Broader register changes; distinct original temporary slots remain unrecovered |
| SUB/MUL/ADD source order with the existing shared arithmetic exit | 6,942 | Reorders handlers without recovering the original ADD/SUB/MUL layout |
| Shared floating operand locals across ten binary handlers | 6,942 | Changes 20 memory-address encodings; five recover original operands, fifteen lose previously correct operands |

The last trial illustrates why a similarity summary cannot select source. An
instruction-shape alignment reports fewer unequal blocks, from 227 to 180.
Complete candidate review instead finds unchanged instruction boundaries,
mnemonics, switch data and linked fields, with 20 changed MOV encodings. A
diagnostic review indexed by original/candidate switch entries and their
mnemonic-equal prefixes exposes the five recoveries and fifteen regressions.
That trial is restored. The diagnostic alignment grants no exact credit.

Remaining source problems include the arithmetic and expression exit placement,
stack conversion slots, SETF destination/type registers, comparison branches,
and interpolation-loop ownership/register choices. The candidate reuses a
floating-pop scratch slot where the original uses separate slots. The original
carries `EDX = 1` into predicate handling; explicit ternaries do not reproduce
it. Previously documented floating-exit, countdown-loop and ring trials should
not be repeated as new hypotheses.

## Static checkpoint

The canonical strict writer and progress reader report **904 exact / 67
mismatch / 244 incomplete**, **185,816 exact primary bytes** and **971 units**.
The only result changes are the helper becoming exact and the interpreter's
incomplete reason advancing from missing bindings to differing complete extent.
All 903 previous exact results, all 970 previous unit definitions, and the
other 1,213 annotation results and diagnostics are unchanged.

Every one of the **1,719 source-qualified native owners, totaling 527,136 raw
bytes**, is byte-identical to the starting image. All addresses, extents,
base relocations and the complete raw `.text` are preserved. All game-source
trials are restored. PDB age is **600**; source input remains
`ef45258398eb6fe5c3cb4fd560aed06455b5f5695cfb4d398602eb739e51ccc5`.
Source-origin review remains open and Factory acceptance is not submitted.

Keep `.analysis/ecl-interpreter-order-work/`, including the PDB 591 baseline,
PDB 600 final image, all eight trial images/source snapshots, complete owner
packets, original CFG, qualified private proof, static controls, shared-operand
regression diagnostic, canonical report and final whole-image regression.
Builds are incremental; preserve the current build graph. No repository content
is pushed.
