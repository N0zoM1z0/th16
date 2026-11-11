# Complete special-vertices code and table scope

The original `AnmVm::update_special_vertices` at `0x004632F0` owns **2,101
bytes**, through `0x00463B24`. The preceding 2,068-byte inventory described
only its executable code. Original-only traversal now accounts for that code
and both immediately following tables. The complete candidate PDB contribution
is 2,097 bytes, so this function remains incomplete and receives no exact
credit. The original boundary is not resized to the candidate.

## Original-only derivation

`.analysis/review-special-vertices-scope.py` reads the canonical original and
the preceding original inventory, without candidate source, PE, MAP or PDB.
The next independent entry, `0x00463B30`, is only a ceiling. The reproducer
derives the actual end from decoded control flow and the bounded dispatch's
operands. Evidence is `.analysis/special-vertices-original-scope.json`.

| Span | Role | Bytes |
| --- | --- | ---: |
| `0x004632F0..0x00463B03` | Complete code, including internal NOPs | 2,068 |
| `0x00463B04..0x00463B13` | Four absolute case targets | 16 |
| `0x00463B14..0x00463B24` | Seventeen byte remap entries | 17 |
| `0x00463B25..0x00463B2F` | INT3 padding before the next independent entry | 11 |

The 501 reachable instructions end in three returns at `0x004635EC`,
`0x004638D9` and `0x00463B03`. Every code byte is covered; no unreachable
instruction or unexplained gap is excluded. Direct branches stay at decoded
owned instruction starts. The only indirect dispatch follows adjacent CMP,
unsigned JA, MOVZX and JMP instructions. Its bound derives all 17 byte entries;
their maximum index derives all four target slots. Their relative case offsets
are `[67,765,1514,2059]`. Every case target is a decoded owned instruction start.
The guard cannot be bypassed through a direct or table edge. Both tables are
contiguous with the code, and no independent inventory entry overlaps the
result. All 11 following bytes are INT3 padding and remain outside the owner.

The full 2,101-byte original hash is
`bc7e0bef80ac250eea3c5c9d2524948e33e9b5e0854cd3f07e9fa4f8cf9e27f0`.
This supersedes the earlier code-context extent for this entry. It does not
resolve the main interpreter's additional tables or eight unbound fields.

## Strict ownership profile

The existing single-table switch verifier now also accepts an explicitly
reviewed trailing byte-remap table. A record must describe the complete code,
alignment, target table and contiguous byte map. Both original and candidate
must have the same reviewed unsigned bound, adjacent index-preserving remap,
table operands, case offsets and every map byte. Each case destination must be
an owned instruction start, and no direct CALL/JUMP or table edge may enter the
guard's suffix. The complete original hash remains required.

The candidate must retain a relocation for every target slot and both table
address operands. Extra or crossing relocations anywhere in the complete data
span, including the byte map, are rejected. No map byte is a normalization
field or excluded span. The complete code and both tables belong to the primary
comparison extent. Public ownership, complete PDB producer identity and all
other Oracle checks remain required. Unreviewed dispatches remain refused.

The private helper witness verifier now recognizes the parent's reviewed full
owner, checks that full payload and its hash, and then decodes its explicit
code portion for the existing call-path proof. This prevents the corrected
inventory from treating table bytes as parent instructions. Missing table
bytes, altered table values or a shortened parent boundary invalidate the
helper proof. The helper's own complete 32-byte scope is unchanged.

## Rejected countdown source context

The original's three vertex loops check the initial count for positivity and
then subtract one and repeat while nonzero. The preceding source instead tests
`n > 0` after each iteration. A natural guarded do/while countdown expresses the
original termination structure for all initially positive counts, while still
performing no iterations for nonpositive counts. It changes register allocation
but leaves the complete candidate at 2,097 bytes, against the independently
derived 2,101-byte original. The source trial is rejected and restored; no
instruction ordering, registers, spills or padding are forced.

The baseline's executable body is 2,062 bytes followed by two alignment bytes
and 33 table bytes; the trial has the same complete size. The original code is
2,068 bytes with no code/table alignment gap. Equal table byte counts do not
justify comparing shortened code or granting partial similarity credit.
Sources, full PE/MAP/PDB/function maps and receipts are retained under
`.analysis/special-vertices-{baseline,countdown-artifacts}/`; the trial build
and focused logs are `.analysis/special-vertices-countdown-build.log` and
`.analysis/special-vertices-countdown-focused.json`.

The restored source is rebuilt incrementally. Current full build-input identity
equals the baseline, all artifact hashes match the fresh receipt and all 192
dependency stamps validate. Evidence is
`.analysis/special-vertices-restored-check.json` and
`.analysis/special-vertices-restored-build.log`. No archived output substitution
or clean build is used.

## Validation

Full replay retains 790 exact, 61 mismatch and 364 incomplete candidates,
covering 126,050 exact primary bytes. All 790 preceding exact results and all
851 comparison units remain unchanged. This batch adds no exact credit.

All 156 controls pass across seven relevant suites: private identities (33),
primary switch ownership (30), strict Oracle (14), reviewed linkages (26),
focused audit (3), constructor EH (25) and empty EH (25). The new structural
fixture checks the full original remap shape and relocation requirements; it
supplies no candidate PDB identity. A separate control verifies that the real
candidate remains refused for its different complete extent. Map mutations,
case mappings, guard bypass, shortened/expanded records and extra/crossing
data relocations are rejected. Parent witness tests also reject omitted or
altered table bytes.

Full scope diagnostics are `.analysis/special-vertices-source-trial.json`.
Replay and retained-unit evidence are `.analysis/special-vertices-full-audit.log`
and `.analysis/special-vertices-regression-check.json`. Control logs use
`.analysis/special-vertices-{static-controls,oracle-controls,linkage-controls,focused-controls,switch-controls,constructor-eh-controls,empty-eh-controls}.log`.
Source-origin review remains open, Factory acceptance remains unsubmitted and
nothing is published.
