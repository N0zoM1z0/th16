# Complete random runtime and audio vector identities

Reviewed 2026-11-12. The independently reviewed CRT random entry resolves
CSound::GetFreeBuffer's final field. Its entire 110-byte owner now passes.
A fixed original vector read also resolves four fields across the two audio
initialization owners, which remain incomplete. No game source, admission
rule or compiler artifact changes occur, and no build is needed.

## Complete random entry and caller

| Role | Complete original | Complete candidate | Original reachable instructions |
| --- | --- | --- | ---: |
| `_rand` | `0x0047A739`, 33 bytes | `0x004793F9`, 33 bytes | 8 |
| `CSound::GetFreeBuffer` | `0x004710B0`, 110 bytes | `0x00422C20`, 110 bytes | 51 |

The complete runtime calls the independently bound `___acrt_getptd` at original
`0x0047CAD3` and candidate `0x0047C5B1`. It reads and writes the unsigned random
state at PTD offset 24, multiplies by 214013, adds 2531011, shifts right sixteen
and masks with 32767 before returning. Pinned UCRT rand.cpp and the PTD
declaration in corecrt_internal.h independently establish this role. The full
candidate PDB owner is libucrt:rand.obj in the pinned 10.0.10240.0 x86 library.
Its only instruction field is REL32 at offset one; it has no PE relocations.
All 33 original/candidate bytes and the nested getter role are retained.

The complete caller returns a free DirectSound buffer when one is available;
otherwise its fixed original CALL at offset 88 selects rand before the buffer
index calculation. Original-only CFG review reaches every instruction,
checks all branches/returns and following alignment, and excludes interior
inventory entries. Whole-owner replay covers every caller byte, field and
relocation. The runtime binding grants no primary runtime exact credit.

## Whole vector and fixed original read

The complete vector contains four little-endian 32-bit values `[0, 1, 2, 3]`.
Its typed public is `__xmm@00000003000000020000000100000000`. The original
has two identical read-only copies, at `0x00490EE0` and `0x004947B0`.
The fixed MOVAPS at `0x004704C9` selects the latter; equal bytes alone do not
choose a destination. Candidate storage at `0x00494520` is one complete
sixteen-byte PDB contribution, with the full matching payload and no pointer
relocations. The existing typed literal/read contract needs no new rule.

| Original consumer | Whole original owner | Reachable instructions | MOVAPS offset | PADDD offset |
| --- | ---: | ---: | ---: | ---: |
| `CSoundManager::CreateStreaming`, `0x00470320` | 856 bytes | 236 | 425 | 528 |
| `CSoundManager::CreateStreamingFromMemory`, `0x00470680` | 809 bytes | 224 | 378 | 481 |

Both complete original CFGs, all four reads and both complete candidate scopes
are retained. The vector identity removes two unbound fields per owner.
Each owner still has an unbound private EH handler and mutable ISA-status
field, so neither receives exact credit or a shortened comparison.

## Open ISA and EH ownership

The ISA field points to original `0x004A65FC` and candidate `0x004A67EC`.
Both addresses lie in virtual zero-fill storage rather than raw file data.
The candidate public is `___isa_available`, from LIBCMT:_cpu_disp_.obj, and
its same-start PDB data contribution owns **eight bytes**. A four-byte access
does not prove a standalone four-byte owner. No runtime-global binding or
literal-zero assumption is added.

The complete candidate initializer `___isa_available_init` at `0x0047548B`
owns 415 bytes. Its complete original identity and startup witness, all
initializer field roles, the full mutable storage contribution and both
nonstandard audio EH graphs remain open. The diagnostic inventory retains
those scopes and questions without assigning acceptance authority to a
candidate name or compiler output.

## Results, controls and evidence

Canonical replay reports **877 exact, 65 mismatch and 273 incomplete** among
1,215 annotations, covering **165,381 exact primary bytes and 942 units**.
The new whole buffer-selection pass adds 110 bytes. All preceding 876 exact
results, 65 complete mismatches and 941 unit definitions remain identical.
The two initialization records only lose their two vector fields each; all
other incomplete records remain identical. Runtime and vector data receive
no extra primary credit.

**60 relevant controls pass**: reviewed linkages (43), strict Oracle (14) and
focused audit (3). The new cases reject shortened runtime extents, the wrong
pinned library, the duplicate original vector copy, instruction interiors,
wrong mnemonics, a shortened typed value and a change to the candidate's final
vector byte. Existing frame/table rules are unchanged. All previous comparison
records and units are checked separately by the complete regression proof.

No build occurs. The receipt/artifacts, all 1,719 complete linked function
records and all 192 dependency stamps remain unchanged. Source input remains
`356af008e8064e7f8080f6c112145362eea142d1955f371a989e5b65034aca5f`.
The current incremental graph is retained. Source-origin review and formal
Factory acceptance remain open.

Original-only proof is `.analysis/rand-audio-original-scopes.json`, reproduced
by `.analysis/review-rand-audio-originals.py`. Complete runtime/vector/caller
payloads, fields, relocations, producers and pending scopes are
`.analysis/rand-audio-caller-scopes.json`, reproduced by
`.analysis/review-rand-audio-callers.py`. Artifact/regression proofs are
`.analysis/rand-audio-{artifact,regression}-check.json` with matching
`check-*.py` reproducers. Control and audit logs use `.analysis/rand-audio-*`.
The open ISA inventory is `.analysis/audio-isa-next-inventory.json`, reproduced
by `.analysis/inspect-audio-isa-storage.py`; earlier field exploration is
`.analysis/audio-fields-inventory.json`. The baseline is
`.analysis/rand-audio-baseline/`.
