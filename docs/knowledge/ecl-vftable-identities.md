# Complete ECL vftable identities

Three complete primary vftables now have independently reviewed identities:
`EclResourceInf`, `SptResourceInf` and `SptInf`. Existing RTTI, whole-storage
and fixed-function rules accept all eleven slots without a verifier change.
Four whole source owners become exact, adding 1,002 primary bytes. Two ordinary
ANM insertion source contexts are rejected and restored.

## Original class selection and complete storage

The original address points are located from unique terminated RTTI class
names, unique zero-signature primary CompleteObjectLocators and their exact
read-only pointer references. The producer does not select a convenient table
from a constructor or comparison operand. It walks the original callable
pointer sequence to its first non-executable word, corroborating the complete
class method contract and every pre-existing function identity.

| Class | Original address point | Candidate address point | Slots | Complete candidate table with locator pointer |
| --- | --- | --- | ---: | ---: |
| `EclResourceInf` | `0x00492198` | `0x004925AC` | 3 | 16 bytes |
| `SptResourceInf` | `0x004921E0` | `0x00492584` | 2 | 12 bytes |
| `SptInf` | `0x004921C4` | `0x004939F4` | 6 | 28 bytes |

The four-byte locator pointer belongs to each complete PDB contribution;
it is not padding or an interior-table allowance. Candidate publics come
from `Enemy.obj` for the resource tables and `SptInf.obj` for the VM table.

`EclResourceInf` inherits `SptResourceInf` through the supported non-virtual
single-inheritance graph. Their shared load-data entry and each override
are checked separately. `SptInf` has its own primary class graph. All names,
base containment, displacement tuples, attributes and uninitialized type
caches satisfy the existing verifier in both images.

The complete supporting candidate graph has **18 unique objects, 346 bytes
and 36 pointer relocations**. Every table prefix, CompleteObjectLocator,
ClassHierarchyDescriptor, BaseClassArray, BaseClassDescriptor and complete
terminated TypeDescriptor has a unique complete PDB contribution. The
independent diagnostic also checks every object's full expected relocation
footprint, including the extra terminating byte of each base-class array.
Original relocation absence is recorded separately. These are identity
checks; no RTTI or table data receives primary exact credit.

## All eleven virtual slots

`SptResourceInf` has two slots:

| Slot | Original entry | Contract |
| --- | --- | --- |
| 0 | `0x00474530` | `SptResourceInf::load_ecl_data` |
| 1 | `0x0041A3F0` | `SptResourceInf::load_includes` |

`EclResourceInf` has three slots:

| Slot | Original entry | Contract |
| --- | --- | --- |
| 0 | `0x00474530` | inherited `load_ecl_data` |
| 1 | `0x0041B040` | overridden `load_includes` |
| 2 | `0x0041A860` | `load_file` |

`SptInf` has six slots:

| Slot | Original entry | Contract |
| --- | --- | --- |
| 0 | `0x0041A4A0` | `run_over_300` |
| 1 | `0x0041A4B0` | `get_int_global` |
| 2 | `0x0041A4C0` | `get_int_global_ptr` |
| 3 | `0x0041A4D0` | `get_float_global` |
| 4 | `0x0041A4E0` | `get_float_global_ptr` |
| 5 | `0x0041A670` | scalar deleting destructor |

Every candidate slot has a unique complete code owner and exactly its
pre-existing fixed original function identity. Targets are not inferred
from observed slot values during the consumer comparison. The metadata
proof grants no additional code credit to the slot callees. A callee that
also passes its own complete primary comparison is counted once there.

## Complete consumer results

| Primary owner | Original/candidate bytes | Result |
| --- | ---: | --- |
| `SptInf::SptInf`, `0x0041A530` | 99 / 99 | exact |
| `SptInf` scalar deleting destructor, `0x0041A670` | 93 / 93 | exact |
| `EnemyManager::initialize`, `0x0041AE70` | 459 / 459 | exact |
| `EclResourceInf::load_includes`, `0x0041B040` | 351 / 351 | exact |
| `EnemyManager::~EnemyManager`, `0x0041B1A0` | 414 / 414 | incomplete: one field |
| `EnemyInf::~EnemyInf`, `0x0041BA10` | 306 / 306 | incomplete: two fields |

The four original pass scopes independently contain 14/34/116/134 reachable
instructions, respectively. All direct branch targets, terminal paths and
following INT3 intervals are checked. Whole source/PDB owners, exhaustive
fields and relocations, all original/candidate bytes and standalone Oracle
replays are retained. Neither remaining destructor receives prefix credit.

The canonical report is **846 exact, 65 mismatch and 304 incomplete** among
1,215 annotations, covering **154,748 primary exact bytes and 911 units**.
The four passes add **1,002 bytes**. All previous 842 exact results,
65 complete mismatches and 907 unit definitions remain unchanged.

## Rejected ANM insertion contexts

The four original world/UI insertion owners contain 177/172/177/172 bytes,
each with 47 reachable instructions. They keep the manager in EDX and the
node in ECX, then read the fast ID before the discriminator while packing
its thirteen low and nineteen high bits. The current candidates allocate
those pointer registers differently and retain complete mismatches.

Two natural source contexts were built incrementally:

- Construct an `AnmId` value, assign it to the VM and return that same value.
- Write the high discriminator field before the low fast-ID field in the
  bitwise packed-ID expression.

Both contexts produce identical complete machine code for all four owners.
All 1,719 complete linked owner entries, extents and raw hashes remain
unchanged in both trials. Both contexts are rejected. Do not repeat them,
the earlier inline node-initialization helper, or force register/read order.
The source is restored byte for byte and freshly rebuilt, with all 192
incremental dependency stamps checked. The retained source input remains
`c2ac9cc0add85924f097edf2dc772148551601b302607cc480fba1867a1fcd5a`.

## Validation and evidence

**83 controls pass** across vftable identities (30), reviewed linkages (36),
strict Oracle (14) and focused audit (3). Existing mutation cases now include
the three ECL tables: shortened PDB tables, shortened original tables with
forged candidate extents, wrong slot targets and every missing table-pointer
relocation remain rejected.

Two older permission controls initially changed the entire candidate `.rdata`
section and reached the newer stage-table check before the intended vftable
check. They now select only their target vftable binding while preserving
the same permission mutation and exact rejection assertion. The failed run
is retained as `.analysis/ecl-vftable-vtable-identities-first-controls.log`.
The verifier and production admission rules are unchanged.

Original RTTI discovery and full graph evidence are
`.analysis/ecl-vftable-original-locations.json` and
`.analysis/ecl-vftable-graph-proof.json`, reproduced by
`.analysis/review-ecl-vftable-originals.py` and
`.analysis/review-ecl-vftable-graphs.py`. Original primary scopes and complete
caller replays are `.analysis/ecl-consumer-original-scopes.json` and
`.analysis/ecl-vftable-caller-scopes.json`. Canonical replay, controls and
regression evidence are `.analysis/ecl-vftable-full-audit.log`,
`.analysis/ecl-vftable-controls-summary.json` and
`.analysis/ecl-vftable-regression-check.json`.

ANM source trial originals and full outputs are
`.analysis/anm-insertion-original-scopes.json` and
`.analysis/anm-insertion-source-trials.json`, reproduced by
`.analysis/review-anm-insertion-originals.py` and
`.analysis/review-anm-insertion-trials.py`. Full snapshots remain under
`.analysis/anm-insertion-{id-baseline,value-id-artifacts,high-field-artifacts}/`.
Current source/graph restoration proof is
`.analysis/anm-insertion-restored-check.json`. No cold build, cleanup,
archived-output substitution, Factory submission or remote publication occurs.
