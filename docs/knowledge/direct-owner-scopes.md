# Further complete direct-table owners

The 2026-11-11 review establishes 37 complete original single-table scopes.
Seven existing C++ candidates pass their entire independent original owners,
adding **8,204 exact primary bytes**. Full replay reports **803 exact, 61
mismatch and 351 incomplete**, covering 136,876 exact primary bytes. All 796
preceding exact results and all 857 preceding comparison units remain unchanged;
seven new units give 864 total. No verifier rule or game source change is
retained in this batch.

## Original-only ownership

`.analysis/review-direct-owner-scopes.py` reads the canonical original and the
preceding inventory/profile snapshots under `.analysis/direct-owner-baseline/`.
It does not read candidate sizes, source, PE, MAP or PDB. Original instruction
patterns identify adjacent CMP/unsigned JA/indexed JMP dispatches. Existing
reviewed owners and entries without maintained source associations are excluded
from this game-source batch; remaining single-table patterns are all evaluated,
including those whose candidates still fail.

For each accepted scope, the original bound derives every table slot. Recursive
traversal follows all bounded case destinations and direct branches, decoding
the code independently of a candidate extent. Every reachable instruction must
agree with the complete linear code decode. No unexplained unreachable code,
gap or additional indirect edge is accepted. All case targets are owned
instruction starts, and guard bypass remains rejected. Every original byte from
entry through the final table slot is owned; only complete NOP/INT3 alignment
instructions may separate code and table. All following bytes up to the next
independent entry are INT3, and no other inventory entry overlaps the scope.

The reproducer retains all full bytes, hashes, instructions, table mappings,
traversal counts, padding and explicit records in
`.analysis/direct-owner-original-scopes.json`. The 37 records reuse the existing
direct-table profile in `config/switch-owners.toml`. The corresponding original
inventory boundaries now include the complete code, alignment and table.
No primary range is shortened or resized to a candidate.

## Seven complete passes

| Original entry | Owner | Code | Alignment | Table entries | Full bytes |
| --- | --- | ---: | ---: | ---: | ---: |
| `0x00415570` | Bullet::step_ex_04 | 504 | 0 | 7 | 532 |
| `0x00423810` | EnemyInf::get_int_global | 1,507 | 1 | 98 | 1,900 |
| `0x00424110` | EnemyInf::get_float_global | 2,413 | 3 | 98 | 2,808 |
| `0x00459240` | draw_text | 831 | 1 | 9 | 868 |
| `0x0045C110` | resolution_dialog_proc | 371 | 1 | 6 | 396 |
| `0x0045F2D0` | AnmVm::get_float_var | 679 | 1 | 36 | 824 |
| `0x00464F10` | AnmManager::setup_render_state_for_vm | 836 | 0 | 10 | 876 |

The 8,204 bytes comprise 7,141 code bytes, seven alignment bytes and 1,056
absolute table bytes. Every candidate has its complete same-start PDB owner
and declared source producer. Every table slot and dispatch address retains
its authoritative PE relocation. All external fields retain independent
bindings. Whole raw code/alignment and all relocated table slots are compared;
there is no table-only credit or code-only similarity acceptance.

## Original scopes which do not pass

Thirty further reviewed originals receive no candidate exact credit. Twenty-five
have different complete candidate PDB extents. Four equal-size candidates still
lack bindings: BombInf::create (460 bytes, nine fields), EndingScriptVm::run
(2,328 bytes, six), stage_clear (896 bytes, one) and TitleInf::do_music_room
(3,136 bytes, seven). These unresolved fields are not inferred from nearby
addresses or matching annotations.

The easing baseline below is superseded by the
[complete exact source reconstruction](easing-dispatch-exact.md): its full
1,692-byte owner and all 131 fields now pass without changing this scope record.

`interp_common_methods` has a complete 1,692-byte original: 1,566 bytes of code,
two alignment bytes and 31 target slots. The baseline candidate has the same
complete size but a different case mapping, so it remains incomplete under
the existing strict profile. In particular, nine later case starts are three
bytes earlier in the baseline candidate. The reviewed mapping is not changed
to fit that layout and no relocation addend is used to hide it.

Ten other discovered roots are excluded from this single-table batch:

| Original root | Reason |
| --- | --- |
| `0x00408650` AsciiInf::draw_string | Three bounded direct tables |
| `0x0040B3B0` StageInner::run_std | Two bounded direct tables |
| `0x00412CB0` BulletManager::shoot_one | Two bounded direct tables |
| `0x00413860` Bullet::run_ex | Two bounded direct tables |
| `0x0041DCB0` EnemyData::ecl_run_over_300 | Two located direct tables; complete dispatch graph still needs review |
| `0x0043CE10` Supervisor::switch_gamemodes | Additional indirect jump at `0x0043CEAA` |
| `0x0043F980` PauseMenu::tick_open | Two bounded direct tables |
| `0x0044B5F0` TitleInf::do_title_screen | Three bounded direct tables |
| `0x0045A450` window_proc | Additional indirect jump at `0x0045A480` |
| `0x00468490` AnmManager::draw_vm | Additional indirect jump at `0x004684FD` |

The subsequent [compound ownership review](compound-owner-scopes.md)
supersedes eight of these exclusions and additionally establishes the main Anm
interpreter's full scope. Ascii drawing and the large enemy ECL body remain
unreviewed because their bounds are nonadjacent to the dispatch sequence.

At that checkpoint, these entries required separate complete compound ownership
reviews. Locating one table does not prove the whole parent or permit arbitrary indirect
traversal. The reproducer records each refusal explicitly and does not add
partial primary profiles for these roots.

## Rejected natural interpolation source contexts

Two source contexts were built incrementally against the complete interpolation
owner. The first makes the quadratic in-out curve share its final scaling
return and makes both out-in sine branches return directly. Its full candidate
remains 1,692 bytes, but case offsets still differ from the original. The
original complete profile refuses it; no partial similarity credit is taken.

The second expresses the quadratic reflection as two ordinary assignments and
places the constant half first in the sine branch's final addition. The whole
candidate becomes 1,696 bytes against the independent 1,692-byte original and
is refused. Diagnostic tables are located from the candidate's actual dispatch
operand, without assuming the original table offset after this extent change.
Neither trial uses dead locals, forced accesses, registers, assembly or padding.

Both contexts are rejected and baseline Interp.cpp is restored byte for byte.
Full original and baseline/trial/restored candidate owners, actual table
locations, all case mappings, instructions, receipts and strict outcomes are
in `.analysis/interp-methods-source-trials.json`. Complete source/output sets
remain under `.analysis/interp-methods-{source-baseline,return-flow-artifacts,reflected-curve-artifacts}/`.
Do not repeat these contexts or force the remaining register allocation.

Restored outputs are freshly built. Full build-input identity equals baseline,
all four artifact hashes match the receipt and all 192 dependency stamps
validate. See `.analysis/interp-methods-restored-check.json` and
`.analysis/interp-methods-restored-build.log`. No clean build or archived-output
substitution is used.

## Validation

All 166 controls pass across seven suites: primary switch ownership (40),
private identities (33), strict Oracle (14), reviewed linkages (26), focused
audit (3), constructor EH (25) and empty EH (25). New controls replay all seven
whole owners, independently retain 25 different-candidate-extent refusals,
remove every one of the two enemy getters' 98 target relocations, and exclude
all ten additional/multiple-dispatch roots. All 56 reviewed original code/data
payloads are rechecked, including the newly complete ItemManager parent used
by an existing private helper witness.

Full replay and unchanged-unit evidence are `.analysis/direct-owner-full-audit.log`
and `.analysis/direct-owner-regression-check.json`; focused original-scope
comparisons are `.analysis/direct-owner-focused.json`. Logs use
`.analysis/direct-owner-{switch,static,oracle,linkage,focused,constructor-eh,empty-eh}-controls.log`.
Source-origin review remains open and Factory acceptance remains unsubmitted.
Nothing is published.
