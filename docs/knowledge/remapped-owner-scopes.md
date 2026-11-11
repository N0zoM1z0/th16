# Further complete remapped-switch owners

The 2026-11-11 original-only review establishes ten complete code/table scopes.
Six existing C++ candidates pass their entire independent original scopes,
adding **2,622 exact primary bytes**. Full replay reports **796 exact, 61
mismatch and 358 incomplete**, covering 128,672 exact primary bytes. All 790
preceding exact results and all 851 preceding comparison units remain unchanged;
six new units give 857 total. No game source change is retained in this batch.

## Original code and both complete tables

| Original entry | Owner | Code | Alignment | Target entries | Map bytes | Full bytes |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `0x0041AA70` | EnemyManager::allocate_new_enemy | 749 | 3 | 8 | 92 | 876 |
| `0x00423F80` | EnemyInf::get_int_global_ptr | 263 | 1 | 16 | 63 | 391 |
| `0x00424C10` | EnemyInf::get_float_global_ptr | 368 | 0 | 25 | 81 | 549 |
| `0x00431FE0` | LaserLineInf::run_ex | 1,550 | 2 | 5 | 16 | 1,588 |
| `0x00438CB0` | LaserCurveInf::run_ex | 1,512 | 0 | 5 | 16 | 1,548 |
| `0x0045F610` | AnmVm::get_int_var | 254 | 2 | 18 | 36 | 364 |
| `0x0045F780` | AnmVm::get_float_var_ptr | 176 | 0 | 16 | 32 | 272 |
| `0x0045F890` | AnmVm::get_int_var_ptr | 108 | 0 | 8 | 30 | 170 |
| `0x0046C0D0` | AnmManager::convert_texture | 1,964 | 0 | 5 | 30 | 2,014 |
| `0x00472030` | EclRunContext::ecl_run | 6,683 | 1 | 67 | 94 | 7,046 |

The preceding inventory ends at the executable code and omits the owned data.
The complete scopes are derived by
`.analysis/review-remapped-owner-scopes.py`, using only the canonical original
and `.analysis/remapped-owner-baseline/functions.csv`. Neither candidate sizes
nor artifacts enter the derivation. All ten original bounded patterns are
retained, including the four whose candidates still do not pass.

Each entry has one adjacent unsigned CMP/JA/MOVZX/JMP dispatch. The original
bound derives the complete byte-map count; its maximum remapped index and the
two table operands establish the contiguous complete target table. Recursive
traversal follows direct branches and only the mapped indirect destinations.
Every code instruction is reached; no unexplained unreachable block or tail
transfer is omitted. All targets are decoded owned instruction starts, and
guard bypass is rejected. No independent inventory entry overlaps the result.
Every byte through the complete map is owned; following INT3 padding ends at
the next independent entry and receives no credit.

Full bytes, hashes, instructions, all case offsets/map values, traversal counts,
padding and explicit ownership records are in
`.analysis/remapped-owner-original-scopes.json`. Original inventories now retain
those complete extents. The new records reuse the existing bounded-remap
profile; they do not permit arbitrary indirect dispatches.

## Complete comparison results

The enemy allocator, both enemy global-pointer getters and all three listed
Anm variable getters pass. Their 2,622 primary bytes comprise 1,918 code bytes,
six alignment bytes, 364 absolute target bytes and 334 map bytes. Each candidate
has the complete same-start PDB contribution and declared source producer.
All external fields retain independent bindings; both table-address operands
and every target slot retain authoritative PE relocations. Whole raw maps and
case mappings remain required by the ownership profile. There is no shortened
code-only comparison or additional table-only credit.

The two laser candidates remain 1,748 and 1,720 bytes against their independent
1,588/1,548-byte originals. Texture conversion remains 1,822 against 2,014.
The ECL interpreter candidate is 7,462 bytes against its 7,046-byte original and
still exposes three unbound fields before the audit reaches its extent check.
These four complete original reviews grant no candidate exact credit. Do not
resize originals to candidates or infer missing bindings from equal-looking
addresses.

## Alignment and raw selector coverage

Original alignment includes the complete encodings `66 90` and `0F 1F 00`.
The verifier now decodes each entire zero-to-three-byte alignment interval,
requiring only NOP or INT3 instructions and no undecoded byte. Arbitrary code
remains rejected. A different valid NOP encoding still changes raw primary
bytes and produces a mismatch.

Capstone stops within the byte-map suffix of five otherwise complete candidates.
The existing Oracle data-coverage contract handles these unlinked raw bytes.
The audit now explicitly records only the undecoded suffix of an independently
reviewed complete map and serializes that declaration into the retained unit.
The suffix must be trailing, nonoverlapping and fully covered; code, absolute
table entries and every map byte remain in the full comparison. Neither
`oracle_fields.py` nor the raw replay algorithm changes.

These declarations classify data for coverage; they do not normalize or mask
it. The complete ownership check first requires every map value. A separate
raw-replay control changes an undecoded selector byte in the real 391-byte PDB
owner and obtains 390/391 matching bytes. Normal complete-owner validation
also rejects that altered mapping. Missing, shortened or expanded coverage
declarations remain refused.

## Rejected circle/rectangle source trial

The complete 400-byte circle/rectangle collision helper has 243 matching bytes.
A natural trial writes the two rotation products as matrix coefficients times
coordinates, reversing the multiplication operands. It builds incrementally
but leaves the complete result at 243/400; the trial is rejected and restored.
Full original and baseline/trial/restored owners, instructions and receipts are
retained in `.analysis/circle-rect-source-trial.json` and
`.analysis/circle-rect-{source-baseline,matrix-products-artifacts}/`.

Current source and full build-input identity equal the baseline. Restored outputs
are freshly rebuilt, all four artifact hashes match their receipt and all 192
dependency stamps validate. See `.analysis/circle-rect-restored-check.json` and
`.analysis/circle-rect-restored-build.log`. No clean build or archived-output
substitution is used.

## Validation

All 162 controls pass across seven relevant suites: primary switch ownership
(36), private identities (33), strict Oracle (14), reviewed linkages (26),
focused audit (3), constructor EH (25) and empty EH (25). New controls compare
all six full owners, mutate every map byte on both sides, check multibyte
alignment and raw selector replay, and refuse the four different candidate
extents. Existing relocation, guard, case, ownership and byte-coverage refusals
remain in force.

Evidence includes `.analysis/remapped-owner-{focused,complete-focused}.json`,
`.analysis/remapped-owner-full-audit.log`,
`.analysis/remapped-owner-regression-check.json` and
`.analysis/remapped-owner-{switch,static,oracle,linkage,focused,constructor-eh,empty-eh}-controls.log`.
Source-origin review remains open; Factory acceptance remains unsubmitted.
Nothing is published.
