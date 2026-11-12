# Complete x87 atan2 dependency evidence

`__CIatan2` remains unbound. The current evidence establishes the complete
candidate stub contribution, the full original dispatcher aggregate and its
literal pool. It also exposes a nonadjacent producer used by the operation
descriptor. No new Oracle profile, interior alias or primary exact credit is
added. This advances the earlier
[unfinished investigation](reference-repairs.md#unfinished-atan2-entry-investigation).

## Original entry and complete wrapper

The original intrinsic entry is the complete ten-byte stub at `0x00487AAA`:
it loads descriptor `0x00494E50` into EDX and jumps to `0x00488BB0`.
The complete 57-byte wrapper at `0x004052A0` has a fixed direct CALL at
`0x004052C4` to that entry. Its complete dense control flow and payload are
retained independently of candidate artifacts.

The adjacent ten-byte companion at `0x00487AA0` uses the same descriptor and
a different dispatcher. Its original entry/parent ownership is still not
independently established. The recorded 20-byte diagnostic envelope is not
an accepted original function and cannot supply a primary boundary.

## Complete candidate stub contribution

The current candidate `_atan2` public starts the complete 20-byte
`libucrt:87ctriga.obj` contribution at `0x00487A30`. `__CIatan2` is ten bytes
inside it. Two explicit MASM S_GPROC32 records, `atan2` and `_CIatan2`, have
sizes ten and offsets zero/ten, each ending at its own S_END. They partition
the complete contribution. Native LLVM 18 output independently confirms
both names, addresses, sizes and terminators in the current PDB.

The research parser extracted from the withdrawn draft is used only for this
investigation. It is not part of the Oracle. It still rejects the different
symbol/scope shapes in `87triga.obj` and `87cdisp.obj`; those refusals are
recorded rather than bypassed.

All four stub fields are retained: descriptor DIR32 fields at offsets 1/11
and dispatcher REL32 fields at offsets 6/16. Candidate PE relocations are
exactly 1/11. Both function publics, the module record and the complete PDB
contribution agree on the pinned UCRT producer. The direct jumps identify
`__ctrandisp2` and `__cintrindisp2`; this evidence alone does not prove their
complete implementations or authorize an interior call binding.

## The entire operation descriptor

The descriptor is a complete **80-byte** read-only contribution from
`libucrt:87triga.obj`, at candidate `0x00494BC0` and original `0x00494E50`.
The first eight bytes are the length-prefixed operation name
`05 61 74 61 6e 32 00 00`. Bytes 8-15 are also retained and agree; their
unknown flag meanings are not inferred from the name.

Bytes 16-79 contain sixteen code pointers. Every candidate pointer has a PE
relocation, with no extra or missing descriptor relocations. The original PE
has no relocation directory. Every complete original pointer and candidate
pointer is retained; the original addresses are not selected from caller
operands to make a comparison pass.

The pointers fall into two complete candidate code contributions:

| Producer | Complete bytes | Referenced offsets | Candidate names where public |
| --- | ---: | --- | --- |
| `87triga.obj` | 168 | 28, 117, 152 | `__fFATN2` at offset 28 |
| `87disp.obj` | 500 | 330, 332, 372, 464 | `__nosnan2`, `__tosnan2`, `__nan2`, `__rtatan2inf` |

All six complete candidate code/data records now have retained payloads,
fields, PE relocations and producer metadata: the 20-byte stub, 80-byte
descriptor, 168-byte operation code, 500-byte shared code, 645-byte dispatcher
and 48-byte dispatcher pool. The names in the table describe candidate publics;
the original counterpart identities still require review. In particular,
checking only the eight-byte operation name omits the NaN/infinity paths
and most of the descriptor's storage.

## Complete original dispatcher aggregate

Seven contiguous original inventory scopes form a complete 645-byte aggregate:

| Original entry | Bytes |
| --- | ---: |
| `0x00488BB0` | 68 |
| `0x00488BF4` | 67 |
| `0x00488C37` | 65 |
| `0x00488C78` | 7 |
| `0x00488C7F` | 327 |
| `0x00488DC6` | 51 |
| `0x00488DF9` | 60 |

An original-only traversal from all seven roots reaches all 209 instructions,
checks every direct branch target and accounts for every byte through
`0x00488E34`. Eleven INT3 bytes follow. Code resumes at `0x00488E40`, whose
entry ownership remains unreviewed; the next inventoried entry is
`0x00488ECF`. The aggregate is not relabeled as a single original function.
The complete candidate `87cdisp.obj` code contribution also owns 645 bytes;
its 68-byte named intrinsic procedure cannot replace that containing extent.

Six fixed original x87 qword reads independently establish the complete
48-byte read-only pool at `0x00494EA0`: two FLD, two FCOMP and two FMUL
instructions cover all six eight-byte slots exactly. The candidate pool at
`0x00494C10` is one complete 48-byte contribution and agrees in all raw bytes,
with no PE relocations. No pool data receives primary exact credit.

All fourteen dispatcher fields are traced between complete original/candidate
scopes. Seven REL32 calls refer to candidate `___acrt_has_user_matherr`,
`__trandisp1`, `__trandisp2` and `__87except`. Seven DIR32 fields contain the
six literal-pool reads and `___fastflag`. The original absolute fields are
derived from its decoded memory operands, independently of candidate PE
relocations. These field traces do not authorize normalization or establish
all external callee identities.

## Remaining acceptance work

A future explicit profile must establish the original companion/parent scope,
review the full descriptor matrix and its separate 500-byte producer, and
validate every dispatcher field role against its complete external producer.
It must preserve the whole containing contributions and all relocations.
The current research parser needs independent negative controls before any
production use. No generic interior public, primary game-function split,
shortened runtime owner or runtime primary exact claim is permitted.

The current authoritative report stays at **837 exact, 65 mismatch and
313 incomplete**, with 152,600 exact primary bytes and 902 retained units.
All previous results and unit definitions are unchanged after the separate
snapshot-ID source trial was restored and freshly rebuilt. All 1,719 linked
owner entries/extents/raw hashes and 192 dependency stamps validate.
Seventeen controls pass in the strict Oracle and focused-audit suites.
No cold build, cleanup, archived-output substitution, Factory submission or
remote publication occurs.

Original-only evidence and reproducer are
`.analysis/atan2-original-dispatcher-scope.json` and
`.analysis/review-atan2-original-dispatcher.py`. Complete candidate dependencies
and field traces are `.analysis/atan2-complete-dependencies.json`, reproduced
by `.analysis/review-atan2-dependencies.py`. Current independent native symbol
output is `.analysis/atan2-current-module-symbols.txt`; the research parser is
`.analysis/atan2-masm-procedures.py`. Current source restoration and regression
proofs are `.analysis/snapshot-id-restored-check.json` and
`.analysis/snapshot-atan2-regression-check.json`.
