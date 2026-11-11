# Complete compound switch owners

## Result

Nine original functions now have complete independent code and trailing-data
scopes. Two existing candidates pass: `window_proc` at `0x0045A450`, 680 bytes,
and `AnmManager::draw_vm` at `0x00468490`, 1,896 bytes. Their complete owners
add **2,576 exact primary bytes**, including both dispatch tables and every
selector byte. No game source change is retained in this batch.

Full replay reports **805 exact, 61 mismatch and 349 incomplete**, covering
139,452 exact primary bytes. All 803 preceding exact results and all 864
previous comparison units remain identical. Two new units give 866 total;
every other audit result is unchanged. This is local code-comparison evidence.
Source-origin review remains open and Factory acceptance remains unsubmitted.

## Independent original derivation

`.analysis/review-compound-owner-scopes.py` reads the canonical original and
the preceding original inventory. It reads no candidate size, source or linked
artifact. It follows direct edges and each explicitly bounded dispatch from
the original entry, checks instruction boundaries and all table targets, and
accounts for every code byte, alignment interval, data component and following
INT3 byte up to the next inventory entry. All nine code intervals are reachable;
there is no unexplained executable island or overlap with another owner.

The original bytes, SHA-256 hashes, instructions, table/map layouts and refused
shapes are retained in `.analysis/compound-owner-original-scopes.json`.
This review supersedes eight multiple-dispatch exclusions in the preceding
[direct-table review](direct-owner-scopes.md), and additionally establishes the
main Anm interpreter's full original extent.

| Original entry | Function | Code bytes | Complete bytes | Dispatches | Candidate bytes / result |
| --- | --- | ---: | ---: | ---: | --- |
| `0x0040B3B0` | StageInner::run_std | 3,083 | 3,204 | 2 | 3,160; two unbound fields first |
| `0x00412CB0` | BulletManager::shoot_one | 2,887 | 2,984 | 2 | 3,024; extent refusal |
| `0x00413860` | Bullet::run_ex | 5,197 | 5,436 | 3 | 5,988; extent refusal |
| `0x0043CE10` | Supervisor::switch_gamemodes | 702 | 815 | 2 | 815; three unbound fields |
| `0x0043F980` | PauseMenu::tick_open | 4,586 | 4,676 | 2 | 4,676; one unbound field |
| `0x0044B5F0` | TitleInf::do_title_screen | 3,864 | 3,964 | 3 | 3,912; extent refusal |
| `0x0045A450` | window_proc | 609 | 680 | 2 | 680; exact |
| `0x0045F980` | AnmVm::run | 13,109 | 14,177 | 2 | 14,141; eight unbound fields first |
| `0x00468490` | AnmManager::draw_vm | 1,757 | 1,896 | 2 | 1,896; exact |

The nine owners include 20 target tables and six byte maps. Original scope
proof gives the other seven candidates no exact credit. Earlier field checks
can precede an established whole-owner extent difference.

The two exact layouts are:

| Owner | Code / alignment | Complete data components in order | Following INT3 |
| --- | --- | --- | ---: |
| window_proc | 609 code + 3 NOP bytes | five DWORD targets at `0x0045A6B4`; 24 map bytes at `0x0045A6C8`; six DWORD targets at `0x0045A6E0` | 8 |
| draw_vm | 1,757 code + 3 NOP bytes | 15 DWORD targets at `0x00468B70`; 28 map bytes at `0x00468BAC`; 12 DWORD targets at `0x00468BC8` | 8 |

Their 2,576 bytes comprise 2,366 code bytes, six alignment bytes, 152 target
bytes and 52 selector bytes. Neither unit needs a raw-data coverage declaration;
the existing replay already decodes its whole payload. Alignment remains raw
comparison input: an alternate valid NOP encoding gives a complete mismatch.

## Explicit compound profile

`compound-bounded-v1` is an explicit opt-in record in
`config/switch-owners.toml`. It declares the complete original size and hash,
code size, and every dispatch's guard site, dispatch site, target extent, case
mapping and optional full byte map. Unknown fields, partial components,
overlaps, unexplained gaps and undeclared indirect jumps are refused. The
single-table profile retains its existing rules.

Each dispatch requires adjacent `CMP register, bound`, unsigned `JA`, optional
`MOVZX` from the bounded byte index, and the declared DWORD-indexed `JMP`.
Every target must name an owned instruction start and match the original case
offset. No direct edge or any table's target may enter the guarded suffix of
any dispatch. This includes cross-table guard bypasses.

The Supervisor's second dispatch checks ECX, maps its bounded input into EAX,
then dispatches through EAX. The compound profile checks both register roles;
it does not require the output to overwrite its input. The old single-table
profile still requires its original same-register shape.

The main Anm interpreter's two byte maps have 215 and **313** entries, with
53 and 81 DWORD targets. A byte selector limits the target index to 255; it
does not limit the number of bounded input entries to 256. The second guard
compares against 312. The complete layout is 13,109 code bytes, three NOP
bytes, 212 target bytes, 215 map bytes, one NOP byte, 324 target bytes and
313 map bytes. Fifteen INT3 bytes follow the complete 14,177-byte owner.
Its earlier private-helper witness still checks the same 13,109 code bytes;
both private helpers remain exact. The parent candidate remains incomplete.

Original and candidate payloads are inspected independently. Every candidate
table slot and dispatch/map address operand requires its relocation. The
complete data region must contain exactly the declared table relocations,
including checks for crossing or extra fields in padding and maps. Full
source-qualified PDB ownership, independent linkage bindings and raw replay
remain required. No mask, raw replay rule, field-normalization rule, compiler
profile or game source changes are made.

## Shapes still refused

`AsciiInf::draw_string` at `0x00408650` has a nonadjacent memory bound and
reload before the indirect jump at `0x00408A89`. Its guard is separated by
local stores, and the index is reloaded from `[EDI+0x120]`. It needs explicit
alias/value-flow evidence rather than the adjacent register proof.

`EnemyData::ecl_run_over_300` at `0x0041DCB0` has a frame-local store between
the bounded remap and dispatch at `0x0041DD51`. It needs an explicit proof
of that bridge and its frame dependencies. Neither root receives a partial
profile or implicit traversal permission.

## Validation and retained evidence

All **187 controls across eight suites** pass: compound ownership (21), primary
switch ownership (40), private identities (33), strict Oracle (14), reviewed
linkages (26), focused audit (3), constructor EH (25) and empty EH (25).
The compound controls remove every required relocation, mutate every selector
byte on both sides of the two real owners, test cross-table guard bypasses,
signed bounds, instruction interiors, undeclared jumps, partial extents,
extra/crossing relocations and raw alignment differences. Structural fixtures
for the Supervisor and 313-byte map use original bytes only; they supply no
candidate PDB identity or exact credit. Five real different candidate extents
remain independently refused.

Evidence is `.analysis/compound-owner-focused.json`,
`.analysis/compound-owner-full-audit.log` and
`.analysis/compound-owner-regression-check.json`. Suite logs use
`.analysis/compound-owner-<suite>-controls.log`, where suite names match
`scripts/test-<suite>.py`. The preceding report, units and original inventory
are retained in `.analysis/compound-owner-baseline/`. All build inputs and
outputs recorded by the preceding audit are unchanged. No rebuild or cleanup
is needed for these ownership/configuration changes, and nothing is published.
