# Complete conversion-runtime contribution and interior CALL identities

## Complete caller results

GameThread::update_play_time at `0x0042DBC0` now passes its complete **142-byte**
owner. The complete get_runtime owner at `0x0045B130` becomes a **330/332-byte
mismatch**. These add 142 primary exact bytes; no conversion helper, constant
pool or exception routine receives additional primary credit.

Canonical replay reports **828 exact, 65 mismatch and 322 incomplete**, covering
148,714 exact primary bytes and 893 units. All 827 preceding exact results,
64 complete mismatches and 891 previous units remain retained. The two source
contexts below are rejected, baseline GameWindow.cpp is restored byte for byte,
and a fresh incremental build preserves all 1,719 complete linked owner
entries/extents/raw hashes and validates all 192 dependency stamps.

## Complete runtime ownership

The pinned LIBCMT `_ftol3_.obj` contributes one complete **887-byte code owner**
starting at candidate `__ftoui3` and one complete **130-byte read-only owner**
from the same PDB module. `__dtoul3` and `__ltod3` are interior public entries
at offsets **496** and **848**. They are not separate PDB owners. The original
286-byte Ghidra inventory row for the first interior entry does not describe
the complete object contribution and is not substituted for it.

Independent original review establishes code `0x00487720..0x00487A96` and
data `0x004948B0..0x00494931`. The start follows a separately decoded complete
104-byte predecessor and its INT3 padding; the end comes from the final
original entry's straight-line body through RET. The data span comes from
the original reads. Candidate contribution sizes do not select these limits.
The code comprises 207 decoded instructions:
204 reachable from the eight conversion entries and three owned alignment
instructions totaling 11 bytes. All alignment bytes remain compared. Eight
INT3 bytes precede the contribution and nine follow it before the next runtime
entry. The pool's decoded reads span all 130 bytes, including its final
two-byte x87 control word. Every pool byte equals its complete candidate peer.

All **24 fields** are checked: 23 displacements into the complete pool and one
external relative CALL. The candidate has exactly 23 corresponding PE
relocations. The original has no PE relocation entries in this scope; its
23 data displacements are derived from complete instruction decoding, and
its relocation absence is checked separately. No original relocation evidence
is invented. Replaying these legitimate fields makes the entire 887-byte
candidate equal to the independently fixed original payload.

The external CALL reaches `__except1`, independently reviewed at `0x004861DB`:
a complete 206-byte original with 81 reachable instructions, paired with a
complete 206-byte candidate from pinned `libucrt:fpexcept.obj`. Its ordinary
runtime identity is retained in the linkage CSV. This identity is a callee
binding and grants no primary exact credit.

## Explicit interior profile

`config/runtime-interiors.toml` declares only `msvc-x86-ftol3-v1`.
`scripts/runtime_identity.py` requires the fixed full original code/data hashes,
all reachable code and owned alignment, complete candidate PDB extents from
one pinned producer, the complete data replay, exhaustive fields/relocations,
and complete code replay. The two fixed entry offsets must agree with unique
publics from that producer. Original direct CALL witnesses are decoded inside
complete, hash-pinned 142/332-byte caller scopes. The profile and verifier are
fingerprinted by the Oracle.

Only exact, zero-addend REL32 CALL fields may use these two identities. A tail
transfer, generic interior public, byte interior, data pointer or shortened
contribution remains refused. Default ordinary-runtime binding still rejects
`__dtoul3` for lacking a complete same-start owner. The profile returns parent
size and entry offset without inventing an independent function size. No
primary annotation or original inventory boundary is expanded to 887 bytes.

## Remaining timer source context

The timer's two byte differences are stack displacement bytes at `+0x129`
and `+0x141`: the timeGetTime path spills/reloads its result at EBP-8 in the
candidate and EBP-0x10 in the original. That original slot is also used by the
performance-counter local on the alternate path. Both complete owners remain
332 bytes and all fields resolve. Stack displacements are not normalized.

Two natural contexts were compiled incrementally and rejected:

| Trial | Source context | Complete strict result |
| --- | --- | --- |
| Reuse time | Assign the final seconds value to the existing fallback time variable | 330/332 mismatch |
| Fallback scope | Put the fallback declarations in an explicit sibling else scope | 330/332 mismatch |

Both produce identical bytes across all 1,719 complete linked owners. Neither
explains the original local-slot lifetime. Do not repeat them, insert dead
locals, force accesses or retain a change merely to choose a stack slot.
Baseline source is freshly restored; archived outputs are not substituted.

## Validation and retained evidence

All **237 controls across ten suites** pass. The new 22-control runtime suite
covers complete code/data extents and hashes, original call witnesses, fixed
entry offsets, pinned producers, missing/duplicate owners and contributions,
full code including alignment, both ends of the data owner, candidate and
original relocation footprints, dependency identity, unsupported aliases,
CALL-only use and ordinary-runtime refusal. Earlier strict suites remain green.

Original full payloads, control flow, fields, data, padding, dependencies and
the complete diagnostic replay are in
`.analysis/conversion-runtime-original-review.json`, reproduced by
`.analysis/review-conversion-runtime.py`. Formal profile and full caller proofs
are `.analysis/conversion-runtime-profile-proof.json` and
`.analysis/conversion-runtime-caller-scopes.json`. The baseline and two full
source/output sets remain in `.analysis/conversion-runtime-baseline/` and
`.analysis/conversion-runtime-{reuse-time,fallback-scope}-artifacts/`.
Source trials, all linked-owner deltas and strict results are in
`.analysis/conversion-runtime-source-trials.json`, reproduced by
`.analysis/review-runtime-source-trials.py`.

Restoration, canonical and regression evidence is
`.analysis/conversion-runtime-restored-build.log`,
`.analysis/conversion-runtime-restored-check.json`,
`.analysis/conversion-runtime-full-audit.log`,
`.analysis/conversion-runtime-regression-check.json` and
`.analysis/conversion-runtime-controls-summary.json`. Reproducers and all
focused/build/control logs use the same prefix. Source-origin review remains
open and Factory acceptance remains unsubmitted. Nothing is published.
