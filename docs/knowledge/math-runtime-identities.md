# Exact spellcard clock and complete mathematical runtime identities

The subsequent [closed atan2 review](atan2-runtime-identities.md) resolves the
intrinsic dependency below, adds nine complete exact projectile/math owners
and records the current curve mismatches. The counts in this document describe
the earlier spellcard-clock checkpoint.

The complete **418-byte** `Spellcard::measure_real_time` at `0x00417BC0`
passes the strict local Oracle, including all 107 original instructions and
14 linked fields (five REL32, nine DIR32). The original-only CFG reaches
every instruction, including all three returns at offsets 53, 355 and 417.
Its original SHA-256 is
`70224c81600e64720b75cbe54c557cc1cc839016d6cd08b59d9f2499510b3aea`.

The existing game-source candidate is unchanged. Exactness became provable
after independent complete runtime identities resolved its two missing
fields, `_floor` and `__CIfmod`. No instruction equivalence, shortened scope,
new pragma, compiler-option change or game-source workaround is introduced.
The existing `fenv_access` pragma is unchanged. Runtime support receives zero
primary exact credit. Source-origin review remains open; Factory acceptance
has not been submitted. Evidence is retained in `.analysis/math-runtime-work/`.

## Ordinary complete runtime functions

Original code boundaries come from original-only control-flow traversal,
independently of candidate function sizes. Six bindings use the existing
complete `runtime-function` verifier and the pinned `libucrt.lib`:

| Symbol | Original address | Original bytes | Reachable instructions |
| --- | --- | --- | --- |
| `__libm_sse2_acos_precise` | `0x00487AF0` | 1,311 | 290 |
| `__libm_sse2_atan_precise` | `0x00488010` | 747 | 156 |
| `___acrt_has_user_matherr` | `0x0047B8C6` | 25 | 9 |
| `__87except` | `0x00486086` | 267 | 108 |
| `_floor` | `0x00488A00` | 253 | 59 |
| `__floor_default` | `0x004894F6` | 185 | 79 |

The original `floor` entry at `0x00488A00` has 253 dense code bytes and two
explicit tail edges to the separate fallback at `0x004894F6`. The fallback
has 185 dense code bytes. All 59 and 79 instructions, respectively, are
reachable from their own entries. The former 2,991-byte Ghidra range merged
these functions and unrelated intervening runtime entries. It is replaced by
the complete dense entry and independently traversed fallback; neither tail
edge nor fallback code is dropped.

The corresponding candidate producers are complete, source-qualified pinned
`libucrt.lib` contributions. Acos and atan own one additional terminal
alignment byte in their candidate contributions. That existing explicit
alignment rule does not discard any original instruction or runtime extent.

## Closed x87 fmod family

The `__CIfmod` public remains distinct from an ordinary complete function:
it is at offset 10 within the complete 34-byte `87fmod.obj` contribution.
That contribution also owns a stack-argument entry and a private x87 FPREM
callback. Its complete read-only operation descriptor is 80 bytes and contains
16 code pointers. A public name or a ten-byte stub does not establish the
complete parent or descriptor identity.

The closed `msvc-x86-fmod-v1` profile verifies all code and data contributions
from three pinned producers, before exposing only `__CIfmod` at parent offset
10 through the existing `runtime-interior-v1` call-field rules:

| Producer | Original code | Complete code bytes | Complete data bytes |
| --- | --- | --- | --- |
| `87fmod.obj` | `0x00487AC0` | 34 | 80 |
| `87disp.obj` | `0x00485590` | 500 | 62 |
| `87cdisp.obj` | `0x00488BB0` | 645 | 48 |

All **1,179 code bytes and 190 data bytes** are replayed. Only the exhaustively
enumerated, independently anchored address fields are replaced. Complete PDB
contributions, library/module producers, fixed public offsets, native padding
and exact relocation footprints are required. The descriptor's first pointer
targets the private FPREM callback at parent offset 20; its remaining fifteen
pointers target the verified complete dispatcher. Both constant pools must
match completely and have no relocations.

The dispatcher flag requires the unique pinned `fp_flags.obj` public and its
complete typed four-byte integer in writable virtual zero-fill storage. It
is an internal proof role, not a new exported global binding. External calls
require the independently verified complete matherr predicate and x87
exception-handler identities. The complete original 418-byte Spellcard owner
and its fixed E8 CALL at `0x00417C2A` independently witness offset 10. Other
parent entry points, generic interior aliases, data addresses and nonzero
addends remain forbidden. The primary owner replay rules are unchanged.

## Static controls and preserved state

All 101 static controls pass: 18 fmod-family, 22 existing runtime-interior,
47 reviewed-linkage and 14 strict-Oracle controls. They mutate or reject
bytes, relocation footprints, public offsets, producers, extents, typed flag
storage and call fields. The persisted complete Spellcard unit passes; calls
to parent offsets 0, 11 or 20, a changed nonfield byte and a shortened 417-byte
owner do not pass. No target code is run or emulated.

The canonical audit reports **894 exact, 63 mismatch and 258 incomplete**,
with **182,748 exact primary bytes and 957 units**. All previous 893 exact
owners and 956 unit definitions are retained. All 1,719 complete native
candidate owners (527,136 bytes), addresses/extents, image relocations and
the entire raw `.text` remain unchanged from `489ae61`. The final incremental
PDB age is 569; source input remains
`80da752f1d593ebbb54bc5fecf92210566c8ba0ed0acb6e05ce1e4659e99259d`.

Exactly four other diagnostics advance while remaining incomplete:
`_floorf` reaches its existing PDB source-owner refusal; both curve-node
functions still lack `__CIatan2`; `AnmVm::run` now has all six previously
missing math fields bound but fails the complete owner extent (14,141
candidate bytes against 14,177 original). No credit is granted for these.
The other 1,210 annotation results and diagnostics are unchanged, excluding
current image/PDB identities.

Keep `original-runtime-scopes.json`, `review-originals.py`, original byte/CFG
packets, `fmod-support.json`, all four control logs, `standalone-clock.json`,
`final-regression.json`, `final-image/` and the initial refused-control and
diagnostic-regression logs under `.analysis/math-runtime-work/`. Those initial
failures remain evidence; the final controls and regression pass.

## Rejected complete source trials

These trials are restored and add no exact credit. Preserve their full
original/candidate packets, source snapshots, incremental build logs and
last-trial images; do not repeat them as new hypotheses.

| Complete owner | Trials and outcome | Evidence directory |
| --- | --- | --- |
| `AnmManager::load_next_entry`, 485 bytes | Array subscripts, direct timer `set(-1)` and named timer references all preserve the same 18 SIB-byte differences (467 matching bytes). All 119 original instructions are reachable. | `.analysis/anm-entry-timer-work/` |
| `Supervisor::setup_special_anms`, 693 bytes | Surface early-return produces 689 bytes; flag-clear return and inline void-helper return retain 693 bytes but the wrong final flag-write/pop order (682 matching bytes). All 152 original instructions are reachable. | `.analysis/surface-exit-work/` |
| `EnemyData::step_logic`, 2,207 bytes | Local `{amount, hit}` and `{hit, amount}` result aggregates produce 2,201 and 2,215 bytes, with the wrong 0x14 frame instead of 0x1C and unresolved damage/life register allocation. The retained candidate remains 2,197 bytes. | `.analysis/boss-local-sample-work/` |
| `AnmVm` script clocks and complete 14,177-byte `run` owner | A natural adjacent two-timer member array updates all seven source files and preserves every layout assertion. It changes none of the 1,719 native owners, raw `.text` or relocations, so it is restored. | `.analysis/anm-clock-array-work/` |

The current source and build graph retain none of these experimental game
changes. Boss logic and the large animation interpreter still require source
work against their complete original owners.
