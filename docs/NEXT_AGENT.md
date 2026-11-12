# Current handoff

Updated 2026-11-12 after complete Stage/ItemManager single-member constructor EH graphs.
This file describes current state; the repair log records historical batches.

## Constraints

- Do not push branches or tags, mirror the repository or publish its contents.
  Local commits are allowed. Only the user can revoke the publication restriction.
- Maintained code, comments, documents and commit messages must be English,
  except for the Japanese game title. Do not use REA.
- Use our Factory/TH10-style strict Oracle. Upstream similarity scores,
  comparison scripts and exact labels have no acceptance authority.
- Write natural C/C++ and compare complete owners. Do not restore dead locals,
  padding helpers, byte masks or truncated ranges to recover a match.
- Use incremental builds and focused complete-owner comparisons for iterations.
  Reserve a clean build and broad replay for a milestone or a cache problem.

## Verified checkpoint

The current report is **860 exact, 65 mismatch and 290 incomplete** among
1215 annotated candidates, covering 160,619 exact owned bytes and 925 units.
An explicit single-member constructor profile independently validates complete
Stage/ItemManager 38-byte code and 44-byte metadata aggregates. The original
stores FuncInfo before its map; the candidate's complete PDB owner stores the
map first. Both layouts and every byte/field/relocation are checked. Fixed
member offsets, complete destructor roles, saved-this/cookie frames and the
sole live state are mandatory. Stage construction (249) and ItemManager
construction (160) now pass all 409 primary bytes. Auxiliary graphs grant no
extra credit. All previous 858 exact results, 65 complete mismatches and 923
units remain identical; every other incomplete record also remains identical.
The verifier lives in `scripts/eh_member_constructor.py`, explicitly included
in the Oracle fingerprint. Empty and AnmManager constructor profiles retain
their existing restrictions. Allocation cleanups in Stage/ItemManager create
methods and array cleanups still need separate complete graph review.
No game source or compiler artifact changes and no build occurs; all 1,719
complete linked owner records and 192 dependency stamps validate. See
[the member constructor review](knowledge/member-constructor-eh.md).

The preceding EBX/ESI checkpoint reported 858 exact, 65 mismatch and 292 incomplete,
covering 160,210 exact owned bytes and 923 units.
An explicit empty-EH3 EBX/ESI profile derives cookie node-16 from its complete
37-byte registration and 17-byte restoration. Full private handler/descriptor
owners resolve BulletManager destruction (292), EffectManager destruction
(345) and LaserManager destruction (228), adding 865 primary bytes. The earlier
EBX/ESI/EDI, legacy empty and nonempty constructor profiles retain their rules.
Bomb and Spellcard have the same cookie displacement but different complete
frames and remain excluded. All prior 855 exact results, 65 complete mismatches
and 920 unit definitions remain retained; only the fresh image fingerprint and
PDB age change in prior comparison records. Every other comparison detail and
all other incomplete records remain identical.
A used update-function pointer snapshot in ReplayManager destruction produces
437 bytes against the complete 416-byte original and is rejected. Source is
restored byte for byte and freshly rebuilt incrementally; all 1,719 complete
linked owner records and 192 dependency stamps validate. The retained candidate
is again 415 bytes. Do not repeat this pointer snapshot or force its register
allocation. See [the frame/source review](knowledge/ebx-esi-empty-eh.md).

The preceding six-parent checkpoint reported 855 exact, 65 mismatch and 295
incomplete, covering 159,345 exact owned bytes and 920 units.
The existing saved-register EH profile independently validates six more
complete private graphs: Fog destruction (273), EndingScriptVm destruction
(181), Ending destruction (496), GuiMsgVm destruction (729), LoadingThread
destruction (518) and Player destruction (519). All 2,716 primary bytes pass;
the complete 162-byte auxiliary code and 216-byte metadata receive no extra
credit. All previous 849 exact results, 65 complete mismatches and 914 units
remain identical. No game source, admission rule or compiler artifact changes
and no build occurs; all 1,719 linked owners and 192 dependency stamps validate.
The saved-register mutation suite now covers all eight reviewed parents.
ReplayManager destruction remains incomplete: its original owner is 416 bytes
with a final RET immediately before the next entry, while its candidate owner
is 415 bytes. Do not truncate the original or bypass equal complete extents to
bind its private graph. See [the six-parent review](knowledge/shared-empty-eh-frames.md).

The preceding Enemy checkpoint reported 849 exact, 65 mismatch and 301 incomplete,
covering 156,629 exact owned bytes and 914 units.
An explicit empty-EH3 saved-EBX/ESI/EDI profile independently derives the node-20
cookie slot from each complete parent frame. It checks full private 27-byte
handlers and 36-byte descriptors, the 38-byte registration and 18-byte restore
sequences, reserved frame uses and complete pointer relocations. The legacy
node-4 and nonempty constructor profiles retain their existing restrictions.
Original RTTI also identifies EnemyInf's complete six-slot table and ten-object
base graph. EnemyManager destruction (414), EnemyInf construction (1,161) and
EnemyInf destruction (306) now pass all 1,881 bytes. All previous 846 exact
results, 65 complete mismatches and 911 unit definitions remain identical;
three whole passes give 914 units. No game source, artifact or build change
occurs; all 1,719 complete linked owners and 192 dependency stamps validate.
See [the Enemy frame/table review](knowledge/enemy-empty-eh.md).

The preceding ECL checkpoint reported 846 exact, 65 mismatch and 304 incomplete,
covering 154,748 exact primary bytes and 911 units.
Original RTTI independently identifies complete EclResourceInf, SptResourceInf
and SptInf primary tables. All eleven fixed function slots, eighteen complete
candidate metadata objects (346 bytes) and all 36 pointer relocations are
checked. Existing admission rules resolve SptInf construction (99), its scalar
deleting destructor (93), EnemyManager initialization (459) and ECL include
loading (351), adding 1,002 primary exact bytes. The two remaining destructors
retain one/two unbound fields. All previous 842 exact results, 65 complete
mismatches and 907 unit definitions remain unchanged; four new units give 911.
Used ID values and reversed high/low field expressions leave all four complete
ANM insertion owners unchanged and are rejected. Source is restored byte for
byte and freshly rebuilt; all 1,719 complete linked owners and 192 dependency
stamps validate. No game source or admission-rule change is retained. See
[the ECL vftable review](knowledge/ecl-vftable-identities.md).

The preceding loader checkpoint reported 842 exact, 65 mismatch and 308
incomplete, with 153,746 exact primary bytes and 907 units.
A fixed original PUSH identifies complete 23-byte loader-failure storage
among seven identical original copies. Its unique complete candidate string
contribution resolves ASCII initialization (326), GUI initialization (258),
stage-file loading (337), shared-ANM loading (60) and title initialization
(165), adding 1,146 exact primary bytes. Ending/ECL loading retain two/one
unresolved fields. All previous 837 exact results, 65 complete mismatches and
902 unit definitions remain unchanged; five whole passes give 907 units.
A named half-width/height/width context leaves the complete Bullet wrap owner
at the same 515/519 mismatch and is rejected. Source is restored byte for
byte and freshly rebuilt; all 1,719 complete linked owner entries/extents/raw
hashes and 192 dependency stamps validate. No game source or admission-rule
change is retained. See [the loader/wrap review](knowledge/loader-error-identities.md).

The preceding snapshot-ID/x87 checkpoint reported 837 exact, 65 mismatch and
313 incomplete, with 152,600 exact primary bytes and 902 units.
A used snapshot-ID local in AnmManager::restore_snapshot gives 122 bytes
against the complete 128-byte original and is rejected. Only that complete
linked owner changes. The source is restored byte for byte and freshly
rebuilt; all 1,719 linked owner entries/extents/raw hashes and 192 dependency
stamps validate. All prior function results and 902 unit definitions remain
identical. No source or admission-rule change is retained in this batch.

The x87 investigation independently establishes the complete original
645-byte dispatcher aggregate (209 instructions across seven scopes) and its
full 48-byte pool from six fixed x87 reads. The full 80-byte atan2 descriptor
contains sixteen pointers into complete 168/500-byte producers. Complete
candidate payloads, fields and relocations are retained, and both ten-byte
MASM stub records partition the entire 20-byte candidate contribution.
Original companion ownership and external field roles remain open, so no
__CIatan2 binding or runtime exact credit is added. See
[the dependency review](knowledge/atan2-runtime-dependencies.md).

The annotated replay list/spell format tables now have explicit external
linkage and complete 16/4-byte named PDB global types. Their five full strings
match the originals, and all five candidate pointer relocations are checked.
The complete replay drawing owner remains 1,500/1,501; direct-bool and used
replay-kind contexts give 1,501/1,509 and are rejected. The function source
is restored and freshly rebuilt, retaining only the two linkage declarations.
A fixed six-byte `Pause` PUSH resolves PauseMenu::open (331) and the replay-end
menu entry (267), adding 598 exact primary bytes. The game-over entry retains
its complete 428/425 extent refusal. All 835 prior exact results, 65 complete
mismatches and 900 units are retained; two new units give 902. All 1,719 linked
owner entries/extents/raw hashes remain unchanged and all 192 dependency
stamps validate. See [replay/pause evidence](knowledge/replay-format-linkage.md).

The preceding season-table checkpoint reported 835 exact, 65 mismatch and
315 incomplete among
1215 annotated candidates, covering 152,002 exact owned bytes and 900 units.
The annotated readonly season-name table now has explicit external linkage,
preserving its bytes while providing a unique public and complete 20-byte
PDB global type. All five strings and five pointer relocations match the
original. A fixed 58.0f read and complete unsigned-division identity resolve
the remaining fields of player-data drawing (698) and score-name drawing
(861), adding 1,559 exact primary bytes. All 833 prior exact results,
65 complete mismatches and 898 units remain retained; two new units give 900.
All 1,719 complete function entries/extents/raw hashes remain unchanged and
all 192 incremental dependency stamps validate. No admission-rule changes
occur. See [season-table linkage](knowledge/season-name-linkage.md).

The preceding failure/format checkpoint reported 833 exact, 65 mismatch and
317 incomplete, covering 150,443 exact owned bytes and 898 units.
Complete range-check/tangent runtime identities and fixed `%s`/space/underscore
PUSHes resolve five whole source candidates: tangent wrapper (23), keyboard
drawing (394), replay-save drawing (997), LZSS initialization (68) and ANM
entry loading (247). These add 1,729 exact primary bytes. All 828 prior exact
results, 65 complete mismatches and 893 units remain retained; five new units
give 898 total. No runtime callee credit or admission-rule change occurs.
The complete spell-page original remains 1,011 bytes against baseline 1,016;
index and index-plus-character contexts give 1,012/994 and are rejected.
Source is freshly restored with all 1,719 complete linked owners and 192
dependency stamps checked. See
[runtime/format and spell-page evidence](knowledge/failure-tangent-runtime.md).

The preceding conversion-runtime checkpoint reported 828 exact, 65 mismatch
and 322 incomplete, covering 148,714 exact owned bytes and 893 units.
Complete 887-byte code and 130-byte data contributions from pinned LIBCMT
establish two explicit interior CALL identities, with all 24 fields, 23 candidate
PE relocations, original relocation absence and complete byte replay checked.
GameThread::update_play_time now passes all 142 bytes. get_runtime is a complete
330/332 mismatch at two spill/reload displacement bytes. All 827 previous exact
results, 64 complete mismatches and 891 units remain retained; two new units
give 893 total. No auxiliary runtime primary credit is taken. Two ordinary
timer source contexts are rejected and baseline GameWindow.cpp is freshly
restored, with all 1,719 complete linked owners and 192 dependency stamps checked.
See [conversion-runtime evidence](knowledge/conversion-runtime.md).

The preceding COMISD checkpoint reported 827 exact, 64 mismatch and 324
incomplete, covering 148,572 exact owned bytes and 891 units.
Three fixed doubles and a guarded correction for Capstone's COMISD memory
width report resolve complete FPS update (235), frame-skipping (416) and
window update (246). These add 897 exact primary bytes. All 824 preceding
exact results, 64 complete mismatches and 888 units remain identical; three
new units give 891 total. The correction requires the exact eight-byte legacy
absolute m64 encoding and one containing original parent instruction start;
it never authorizes the decoder's reported 16-byte read. Game source, build
receipt and artifacts remain unchanged. See
[COMISD identities](knowledge/comisd-literal-identities.md).

The preceding timing checkpoint reported 824 exact, 64 mismatch and 327
incomplete, covering 147,675 exact owned bytes and 888 units.
Eight fixed original scalar reads resolve nine complete source candidates:
RNG normalization (64), jagged-line animation (455), Reimu orb start (263),
bullet step_ex_00 (227), line-laser graze/hit (514), sleeping window update
(597), resolution selection (174), audio track switch (199) and audio play
time (178). These add 2,671 exact primary bytes. All 815 preceding exact
results, 63 complete mismatches and 878 units remain identical; ten new units
give 888 total. Supervisor surface setup now compares fully at 682/693;
Marisa cancellation retains a complete 621/595 extent refusal. No game source,
verifier, build artifact or compiler profile changes. See
[timing/collision/audio identities](knowledge/timing-literal-identities.md).

The preceding Bullet collision checkpoint reported 815 exact, 63 mismatch and
337 incomplete, covering 145,004 exact owned bytes and 878 units.
Six natural Bullet collision contexts are rejected. The independently bounded
448-byte original remains a complete extent refusal against 449-byte baseline
source. Vector operand order, in-place scaling, coordinate assignment,
coordinate construction, a hit-branch return and a named VM ID produce
449/458/449/449/452/451-byte candidates respectively. No source change or exact
credit is retained. BulletManager.cpp is restored byte for byte and freshly
rebuilt; all 1,719 complete linked owners and 192 dependency stamps validate.
Do not repeat these contexts or force vector scheduling, stack locations or
shared-return destinations. See
[Bullet collision findings](knowledge/bullet-collision-contexts.md).

The preceding four natural Player source contexts are rejected; source is
restored byte for byte and freshly rebuilt. Used item-origin pointers give 4,504/4,508-byte
update candidates against 4,540. A Float2 displacement gives a 261-byte circle
check against 258; a combined rejection guard remains a 190/258 mismatch.
No source change or exact credit is retained. Every prior comparison result
and unit is retained. See
[Player source-context findings](knowledge/player-context-trials.md).

The preceding replay/numeric checkpoint reported 815 exact, 63 mismatch and
337 incomplete, covering 145,004 exact owned bytes and 878 units.
Fixed 176.0f/512.0f identities and the complete replay FPS format resolve four
existing whole candidates: Cirno update (585), Cirno cancellation (174), Marisa
update (857) and replay FPS drawing (180). These add 1,796 primary exact bytes.
All 811 preceding exact results, 63 mismatches and all 874 units remain
identical; four new units give 878 total. The player body retains its complete
4,540-versus-4,508 extent difference. No game source, verifier or build artifact
change occurs. See
[replay/numeric identities](knowledge/replay-literal-identities.md).

The preceding numeric checkpoint reported 811 exact, 63 mismatch and 341
incomplete, covering 143,208 exact owned bytes and 874 units.
Seven fixed numeric identities resolve complete EnemyData::update_fog (1,547)
and FpsCounter::draw (174) passes, adding 1,721 primary exact bytes. Player's
complete 258-byte circle check and the complete 3,136-byte music-room owner
become mismatches with 181/3,133 matching bytes. All 809 preceding exact
results and all 870 preceding units remain retained; four new units give 874
total. Three ordinary music-room initialization contexts are rejected and
source is restored byte for byte and freshly rebuilt. No game source or
verifier change is retained in this batch. See
[fixed numeric identities and music-room trials](knowledge/menu-literal-identities.md).

The preceding replay-slot checkpoint reported 809 exact, 61 mismatch and 345
incomplete, covering 141,487 exact owned bytes and 870 units.
PauseMenu::tick_open now snapshots the selected replay slot before creating its
replacement, recovering the original index-read order and replay-name copy
path. Both whole owners remain 4,676 bytes. Full diagnostic replay improves
from 3,345 to 4,067 matching bytes, but three original case offsets still differ;
no exact credit is granted. Only this owner changes among 1,719 complete linked
owners. All previous exact results and all 870 units remain retained. Two
ordinary exit-form trials are rejected. See
[the replay-slot source review](knowledge/pause-replay-slot.md).

The preceding identity review established complete original stage-table and
current-time identities and resolved four existing candidates:
stage_clear (896), Supervisor::switch_gamemodes (815), ScorefileChara::insert_score
(246) and ReplayManager::set_end_stage (78). These add 2,035 primary exact bytes.
All 805 preceding exact results and all 866 units remain identical; four new
units give 870 total. PauseMenu::tick_open now exposes its reviewed case-map
mismatch, and six menu candidates retain whole-extent refusals. See
[stage/time identities](knowledge/stage-time-identities.md).

The preceding compound checkpoint reported 805 exact, 61 mismatch and 349 incomplete.
Nine compound
switch originals now include every dispatch, target table, byte map and
alignment interval. Existing window_proc and AnmManager::draw_vm candidates
pass their full 680/1,896-byte owners, adding 2,576 primary bytes. All 803
preceding exact results and all 864 units remain identical; two new units give
866 total. Seven other complete originals receive no candidate credit. Ascii
drawing and the large enemy ECL body retain unreviewed nonadjacent guards. See
[complete compound ownership](knowledge/compound-owner-scopes.md).

The preceding direct-table checkpoint reported 803 exact, 61 mismatch and 351
incomplete. Thirty-seven
further original direct-table scopes now include all code, alignment and target
slots. Seven existing C++ candidates pass their complete independent scopes,
adding 8,204 primary bytes. All 796 exact results and all 857 units at `6e55a25`
remain unchanged; seven new units give 864 total. Thirty other reviewed
originals receive no candidate exact credit, and ten additional/multiple
dispatch roots are explicitly excluded from the single-table profile. See
[further complete direct-table scopes](knowledge/direct-owner-scopes.md).

The preceding remap review establishes ten complete originals; six candidates
pass their full owners, adding 2,622 bytes. All 790 earlier exact results and
851 earlier units remain unchanged. See
[further complete remap scopes](knowledge/remapped-owner-scopes.md).

The preceding special-vertices review corrects its 2,068-byte code context to
a complete 2,101-byte code/table owner. Its candidate is 2,097 bytes and remains
incomplete. A guarded countdown trial is rejected and restored. That batch
adds no exact credit. See
[the complete special-vertices scope](knowledge/special-vertices-scope.md).

The preceding private-helper batch establishes two complete AnmVmRun helpers,
adding 71 exact bytes and two units. Their original paths cross explicitly
reviewed bounded byte-remap dispatches; tables receive no exact credit. See
[Anm private dispatch review](knowledge/anm-private-dispatch.md). The complete
special-vertices scope review now supersedes that batch's partial parent
context. The compound review also establishes the main interpreter's complete
14,177-byte original; its 14,141-byte candidate remains incomplete.

The preceding eight-helper review reports 788 exact, 61 mismatch and 366
incomplete. Eight further original helper entries and their complete private
PDB owners pass the existing profile. Those helpers and the complete 641-byte
fan initializer add nine exact owners and 897 bytes. Three formerly incomplete
callers become complete mismatches. All 837 preceding units remain unchanged,
with 12 new units, for 849 total. See
[further scopes and laser trials](knowledge/further-sincos-scopes.md).

The preceding review establishes three explicitly reviewed complete 32-byte
private helpers now have qualified source/MAP/PDB identities. Their callers
retain exact whole-entry CALL bindings without public-symbol promotion.
Twelve complete exact owners add 4,470 bytes; five formerly incomplete owners
become complete mismatches. All 820 preceding units remain unchanged, with
17 new complete units, for 837 total. See
[private sincos ownership](knowledge/static-sincos-ownership.md).

The preceding original-only review establishes
24 callback-table/startup owners, including the Camera entry and the global
initializer which calls it. Twenty-two complete owners pass. The independently
reviewed `300.0f` binding also resolves Stage::load_data's final field, allowing
its complete 473-byte owner to pass. These 23 additions cover 1,395 primary
bytes. All 797 preceding comparison units remain identical, alongside 23 new
units, for 820 total. See [table entry scopes](knowledge/table-entry-scopes.md).

The preceding original-only review establishes
13 missing runtime callback/helper entries and partitions the unreviewed
313-byte LZSS aggregate into three complete owners plus all 25 INT3 bytes.
All 14 complete owners pass, adding 1,305 bytes. See
[runtime entry scopes](knowledge/runtime-entry-scopes.md). All 783 preceding
comparison units remain identical, alongside 14 new units, for 797 total.

The preceding original-only review establishes
20 registered manager callbacks and one Ascii drawing helper reached by a
registered callback's tail transfer. All 21 complete owners pass, adding
604 bytes. See [manager wrapper scopes](knowledge/manager-wrapper-scopes.md).
All 762 previous comparison units remain identical, alongside 21 new units.

The original AnmManager constructor independently
establishes 39 draw registrations and two tick registrations. All 41 complete
callbacks pass, adding 1,182 bytes. See
[AnmManager callback evidence](knowledge/anm-callback-scopes.md). The constructor
entry also has an original WinMain direct-call witness. Neither candidate sizes
nor artifacts enter the original callback scope derivation.

The constructor's nonempty EH graph now has an explicit complete-owner profile:
136 code bytes and 76 metadata bytes, with all interior names, relocations,
state edges, frame dependencies and cleanup/runtime entries checked. Its entire
5,071-byte primary owner now compares as a mismatch, with 5,054 matching bytes
and 17 differences in one UpdateFunc constructor store-order interval. See
[the aggregate review](knowledge/anm-constructor-eh.md). No new exact credit
is granted by the EH review. Its complete constructor mismatch unit is retained.

The preceding 26 passes, including the 442-byte Replay playback body, remain
exact; see [registered callbacks](knowledge/registered-callbacks.md). The seven
earlier Bullet, Effect and Item callbacks also remain exact; see
[manager callbacks](knowledge/manager-callbacks.md). PosVel remains a 696/700-byte
mismatch after its earlier source improvement.

The preceding EH review established complete passes for the 70-byte
`ItemManagerInner::~ItemManagerInner` and 73-byte `StageInner::~StageInner`.
Their complete private graphs remain checked; see
[EH ownership evidence](knowledge/eh-handlers.md). Auxiliary handlers and runtime
bindings receive no additional primary exact credit.

The preceding batch established six passes with complete bounded switch tables
and a seventh masked-effect initialization pass using its reviewed `240.0f`
literal. See [switch ownership evidence](knowledge/switch-ownership.md).

These are local code-comparison results. Source-origin review remains open;
`config/implemented.csv` has no implemented entries. Factory registration is
inventory-only, has not been activated on the live service, and no Truth Kernel
acceptance receipts have been submitted.

The current build receipt is incremental. Its PE, MAP, PDB, function map, object
cache and non-LTCG symbol-discovery cache are retained. Retained source changes
include the used replay-slot local in PauseMenu.cpp and explicit external
linkage for the existing readonly season-name and replay-format tables in
MainMenuStates.cpp.
The preceding spell-page, GameWindow, Bullet and Player function trials remain
restored. The current source input is unchanged from the ANM insertion trial
baseline and retains the preceding two replay-format linkage definitions.
Both replay index trials, the snapshot-ID trial, wrap bounds trial and two
ANM insertion ID contexts and the Replay destructor pointer snapshot are restored.
All 1,719 complete linked owner
entries/extents/payloads remain
unchanged, current artifacts match their fresh incremental receipt and all
192 dependency stamps validate. No further build is needed for the current EH
review; identical artifacts and current dependency keys are checked in
`.analysis/member-constructor-artifact-check.json`. The preceding source restoration is
`.analysis/replay-destructor-source-trial.json`. The preceding callback
batch added 41 original inventory rows and unknown/review source-origin rows.
The preceding batch extended the EH verifier with one explicitly reviewed
aggregate profile. The preceding callback-table batch adds a fixed literal
binding. The preceding private-ownership batch adds `scripts/static_identity.py` and
`config/static-functions.toml`, with explicit private primary/callee selection
in the strict Oracle and audit. Default public ownership, unreviewed static
names and EH profiles retain their refusal behavior. All whole private bytes,
producer identity, annotation identity, original witness paths and absence of
linked fields/relocations are required. Game source, compiler/linker profiles
were unchanged in that batch. The preceding batch extends the private set to
thirteen records and adds a complete 39-byte XY-output profile and an original-witness dispatch
profile.
The preceding batches extend primary switch ownership with an explicit complete
trailing byte map and fully decoded NOP/INT3 alignment. The audit uses the
existing raw trailing-data contract for undecoded map suffixes; declarations
never mask or normalize bytes. The preceding batch adds 37 direct-table records
under existing rules. The compound batch adds nine explicit compound records
and a complete multi-dispatch verifier, with cross-register remaps, bounded
maps longer than 256 entries, cross-table guard protection and exhaustive data
relocations. Raw replay and field normalization are unchanged. That ownership
batch retained no game source change. Every whole table, source-qualified
complete PDB owner and exhaustive relocation/binding contract remains required. Unreviewed indirect edges remain refused.
Two earlier interpolation source trials were rejected and restored. That
checkpoint freshly rebuilt baseline source and validated all 192 dependency
stamps; see `.analysis/interp-methods-restored-check.json`. Current outputs
include the retained PauseMenu slot snapshot. No clean build or archived-output
substitution is used.

An ordinary out-of-line UpdateFunc constructor was built incrementally as a
source-context experiment. It removes redundant initialization stores and
changes eight complete linked owner extents, including create_func 106 to 77
bytes and AnmManager 5071 to 4046. It does not reproduce the original. Trial
sources and complete outputs are retained under
`.analysis/updatefunc-ordinary-out-of-line-artifacts/`. Baseline sources and
attested outputs were restored after checking the full source-input identity
and every artifact hash; see `.analysis/updatefunc-context-restore-check.json`.
That checkpoint retained the baseline incremental receipt and invalidated 104
trial dependency stamps naturally. The earlier piercing-source batch rebuilt those
dependencies incrementally, tried two PlayerShot source contexts and rebuilt
the restored source. Those artifacts and receipt were freshly produced;
all 192 object dependency stamps validated at that checkpoint. See
`.analysis/piercing-restored-cache-check.json`. No archived outputs were
substituted and no clean build was run.

The piercing hit callback at `0x004474A0` has a complete 39-byte original and
40-byte baseline candidate. An element pointer gives 37 bytes; a bullet-array
base pointer gives 41 bytes. Both natural contexts fail complete-owner
comparison and are restored. Their full outputs, source and instructions are
retained under `.analysis/piercing-{element-pointer,array-base}-artifacts/` and
`.analysis/piercing-source-context-trials.json`. Do not repeat these trials or
force registers/accesses to reproduce the original operand allocation.
The preceding Replay local cleanup remains: its ordinary recorded-input local
produces a complete 281-byte candidate against the 337-byte original. The body
is incomplete. Do not restore forced accesses to imitate its unexplained spill.
PosVel retains its direct wave vector addition and indexed circle/drift-center
forms. Other recent source trials were restored; read the repair log before
repeating them. WinMain's earlier natural cleanup remains; its complete 2919-byte
extent still mismatches.

The current batch passes **164 controls across seven relevant suites**:
member constructor EH (24), saved-register EH (37), legacy empty EH (25),
AnmManager constructor EH (25), reviewed linkages (36), strict Oracle (14) and
focused audit (3). New controls exercise both entire aggregates, every code/data
byte, forged original hashes, parent state lifetime, source/module ownership,
interior roles, independent cookie storage and all pointer relocations. Logs
use `.analysis/member-constructor-<suite>-controls.log`; the summary is
`.analysis/member-constructor-controls-summary.json`.
The preceding EBX/ESI batch passed **140 controls across six relevant suites**:
saved-register EH (37), legacy empty EH (25), constructor EH (25), reviewed
linkages (36), strict Oracle (14) and focused audit (3). Both explicit
saved-register profiles exercise eleven complete graphs, wrong-profile reuse
and two same-displacement unsupported frame shapes. Logs use
`.analysis/ebx-esi-eh-<suite>-controls.log`; the summary is
`.analysis/ebx-esi-eh-controls-summary.json`.
The preceding six-parent batch passed **120 controls across six relevant suites**:
saved-register EH (17), legacy empty EH (25), constructor EH (25), reviewed
linkages (36), strict Oracle (14) and focused audit (3). The saved-register suite
exercises all eight reviewed parents; its cross-parent mutation also crosses
source modules. Logs use `.analysis/shared-empty-eh-<suite>-controls.log`;
the summary is `.analysis/shared-empty-eh-controls-summary.json`.
The preceding Enemy batch passed **150 controls across seven relevant suites**:
saved-register EH (17), legacy empty EH (25), constructor EH (25), vftables
(30), reviewed linkages (36), strict Oracle (14) and focused audit (3).
Logs use `.analysis/enemy-eh-<suite>-controls.log`; the summary is
`.analysis/enemy-eh-controls-summary.json`.
The preceding ECL batch passed **83 controls across four suites**:
vftable identities (30), reviewed linkages (36), strict Oracle (14) and focused
audit (3). Logs use `.analysis/ecl-vftable-<suite>-controls.log`; the summary
is `.analysis/ecl-vftable-controls-summary.json`. Two older permission tests
now isolate their target vftable after unrelated stage-table preemption; their
exact rejection assertions remain intact.
The preceding loader batch passed **53 controls across three suites**:
reviewed linkages (36), strict Oracle (14) and focused audit (3). Logs use
`.analysis/loader-error-<suite>-controls.log`; the summary is
`.analysis/loader-error-controls-summary.json`.
The preceding snapshot-ID restoration batch passed **17 controls across two suites**:
strict Oracle (14) and focused audit (3). Logs use
`.analysis/snapshot-id-<suite>-controls.log`. The complete regression proof is
`.analysis/snapshot-atan2-regression-check.json`.
The preceding replay-format batch passed **60 controls across four suites**:
reviewed linkages (36), strict Oracle (14), focused audit (3) and PDB types (7).
Logs use `.analysis/replay-format-<suite>-controls.log`; the summary is
`.analysis/replay-format-controls-summary.json`.
The preceding season-table batch passed **246 controls across eleven suites**:
stage/time identities (20), compound switch ownership (21), primary switch
ownership (40), private identities (33), strict Oracle (14), reviewed linkages
(36), focused audit (3), constructor EH (25), empty EH (25) and runtime
interiors (22) and PDB types (7). Logs use
`.analysis/season-name-<suite>-controls.log`, matching `scripts/test-<suite>.py`.
The preceding failure/format batch passed 239 controls across ten suites;
its logs use `.analysis/failure-format-runtime-*controls.log`.
The preceding conversion-runtime batch passed 237 controls across ten suites;
its logs use `.analysis/conversion-runtime-*controls.log`.
The preceding COMISD batch passed 215 controls across nine suites;
its logs use `.analysis/comisd-literal-*controls.log`.
The preceding timing batch passed 210 controls;
its logs use `.analysis/timing-literal-*controls.log`.
The preceding Bullet collision and Player batches passed 209 controls each;
their logs use `.analysis/{bullet-collision,player-context}-*controls.log`.
The preceding replay/numeric batch also passed 209 controls across nine suites;
its logs use `.analysis/replay-literal-*controls.log`.
The preceding numeric batch passed 208 controls across nine suites;
its logs use `.analysis/menu-literal-*controls.log`.
The preceding replay-slot batch passed 207 controls across nine suites;
its logs use `.analysis/pause-open-*controls.log`.
The preceding stage/time batch also passed 207 controls across nine suites;
its logs use `.analysis/stage-time-*controls.log`.
The preceding compound batch passed 187 controls across eight suites;
its logs use `.analysis/compound-owner-*controls.log`.
The preceding direct-table batch passed 166 controls across seven suites;
its logs use `.analysis/direct-owner-*controls.log`.
The preceding remap batch passed 162 controls across seven suites;
its logs use `.analysis/remapped-owner-*controls.log`.
The preceding special-vertices batch passed 156 controls across seven suites;
its logs use `.analysis/special-vertices-*controls.log`.
The preceding bounded-dispatch batch passed 143 controls across seven suites;
its logs use `.analysis/anm-private-dispatch-*controls.log`.
The preceding eight-helper batch passed 38 controls across three suites.
The preceding private-ownership milestone passes 114 controls across six suites:
private identities (21), strict Oracle (14), reviewed linkages (26), focused audit (3),
constructor EH (25) and empty EH (25). Logs use
`.analysis/static-sincos-{controls,oracle-controls,linkage-controls,focused-controls}.log`
and `.analysis/static-sincos-{constructor,empty}-eh-controls.log`. The preceding
callback-table batch passes 43 controls; its logs use
`.analysis/table-entry-{linkage,oracle,focused}-controls.log`. The preceding
runtime entry batch passed 17 controls; its logs use
`.analysis/runtime-entry-{oracle,focused}-controls.log`. The manager wrapper
checkpoint's corresponding logs use
`.analysis/manager-wrapper-{oracle,focused}-controls.log`. The preceding EH
checkpoint passed 92 controls across five suites; its logs use
`.analysis/anm-constructor-{eh,empty-eh,oracle,linkage,focused}-controls.log`.
The earlier full control checkpoint passed 140 controls across nine suites.
Original scope derivation and disassembly are in
`.analysis/reviewed-anm-layer-scopes.json`; its original-only
reproducer is `.analysis/review-anm-layer-scopes.py`. The manager wrapper
reproducer and scopes are `.analysis/review-manager-wrapper-scopes.py` and
`.analysis/reviewed-manager-wrapper-scopes.json`. The preceding original-only
runtime derivation is `.analysis/review-runtime-entry-scopes.py` and
`.analysis/reviewed-runtime-entry-scopes.json`. The latest original-only
table derivation is `.analysis/review-table-entry-scopes.py` and
`.analysis/reviewed-table-entry-scopes.json`. Original-only private scope evidence includes
`.analysis/static-sincos-original-scopes.json`,
`.analysis/additional-sincos-original-scopes.json` and
`.analysis/anm-private-dispatch-original-scopes.json`; the maintained verifier
rechecks the full originals and paths. Current replay and retained-pass evidence
are `.analysis/enemy-eh-full-audit.log` and
`.analysis/enemy-eh-regression-check.json`. Current private graphs and full callers
are `.analysis/enemy-eh-caller-scopes.json`; original-only roles/scopes are
`.analysis/enemy-eh-original-scopes.json` and
`.analysis/enemy-constructor-original-scope.json`. The new table graph is
`.analysis/enemy-vftable-graph-proof.json`. Preceding RTTI/slot evidence is
`.analysis/ecl-vftable-graph-proof.json`; complete primary scopes and callers
are `.analysis/ecl-consumer-original-scopes.json` and
`.analysis/ecl-vftable-caller-scopes.json`. The rejected ID contexts are
`.analysis/anm-insertion-source-trials.json`. Preceding complete callers and
original-only scopes are `.analysis/loader-error-caller-scopes.json` and
`.analysis/loader-error-original-review.json`; the rejected wrap context is
`.analysis/bullet-wrap-bounds-source-trial.json`. Preceding source-trial evidence
is `.analysis/snapshot-id-source-trial.json`; full x87 research is
`.analysis/atan2-original-dispatcher-scope.json` and
`.analysis/atan2-complete-dependencies.json`. Preceding complete caller evidence
is `.analysis/replay-format-pause-caller-scopes.json`; original proofs and
rejected index contexts are `.analysis/replay-format-original-review.json`,
`.analysis/pause-label-original-review.json` and
`.analysis/replay-format-source-trials.json`. Preceding original/caller proofs
are `.analysis/season-name-original-review.json`,
`.analysis/season-menu-player-original-scope.json`,
`.analysis/season-menu-division-review.json` and
`.analysis/season-name-caller-scopes.json`. The preceding season-table declaration,
complete typed table and incremental graph were checked in
`.analysis/season-name-linkage-check.json`, reproduced by
`.analysis/check-season-name-linkage.py`. Preceding original and
caller proofs are `.analysis/failure-tangent-runtime-original-review.json`,
`.analysis/failure-format-original-identities.json` and
`.analysis/failure-format-runtime-caller-scopes.json`. Source trials are
`.analysis/failure-format-spell-source-trials.json`; reproducers are
`.analysis/review-failure-tangent-runtime.py`,
`.analysis/review-failure-format-originals.py` and
`.analysis/review-failure-spell-trials.py`. Preceding runtime/caller
proofs are `.analysis/conversion-runtime-original-review.json`,
`.analysis/conversion-runtime-profile-proof.json` and
`.analysis/conversion-runtime-caller-scopes.json`; source trials are
`.analysis/conversion-runtime-source-trials.json`. Reproducers are
`.analysis/review-conversion-runtime.py` and
`.analysis/review-runtime-source-trials.py`. Preceding original identities and
complete consumer proofs are `.analysis/comisd-original-identities.json` and
`.analysis/comisd-literal-consumer-scopes.json`, reproduced by
`.analysis/review-comisd-originals.py` and
`.analysis/review-comisd-consumer-scopes.py`. The decoder probe and deferred
runtime contribution are `.analysis/comisd-decoder-probe.json` and
`.analysis/comisd-time-conversion-unresolved.json`.
Preceding original identities and complete consumer proofs are
`.analysis/timing-literal-original-identities.json` and
`.analysis/timing-literal-consumer-scopes.json`; original-only and complete-replay
reproducers are `.analysis/review-timing-literal-originals.py` and
`.analysis/review-timing-consumer-scopes.py`. Latest full source/payload/field
trial evidence is `.analysis/bullet-collision-source-trials.json`, reproduced by
`.analysis/review-bullet-collision-trials.py`. Preceding Player
trial evidence is `.analysis/player-context-source-trials.json`, reproduced by
`.analysis/review-player-context-trials.py`. Complete instruction alignment is
in `.analysis/player-tick-baseline-layout.json` and
`.analysis/player-tick-{drop-pointer,call-origin}-layout.json`; its diagnostic
reproducer `.analysis/review-player-tick-layout.py` grants no exact credit.
The preceding original identities and
complete scopes are `.analysis/replay-literal-original-identities.json` and
`.analysis/bomb-update-original-scopes.json`, reproduced by
`.analysis/review-replay-literal-originals.py` and
`.analysis/review-bomb-update-original-scopes.py`. Earlier numeric identities and scopes
are `.analysis/menu-literal-original-identities.json`,
`.analysis/additional-literal-original-identities.json` and
`.analysis/enemy-fog-original-scope.json`, with original-only reproducers named
`review-menu-literal-originals.py`, `review-additional-literal-originals.py` and
`review-enemy-fog-original-scope.py` beneath `.analysis/`. Music-room trials and
all complete payloads/fields are in `.analysis/music-room-source-trials.json`.
The preceding replay-slot source trials, whole payloads and all actual linked
fields remain in `.analysis/pause-open-source-trials.json`;
retained case/instruction layout is `.analysis/pause-open-retained-layout.json`.
The preceding original identity and consumer
scope evidence is `.analysis/stage-time-original-identities.json` and
`.analysis/stage-time-consumer-scopes.json`, reproduced by
`.analysis/review-stage-time-originals.py` and
`.analysis/review-stage-time-consumer-scopes.py`. The preceding original-only
reproducer and complete layouts/refusals are `.analysis/review-compound-owner-scopes.py`
and `.analysis/compound-owner-original-scopes.json`. The preceding direct-table
evidence remains `.analysis/review-direct-owner-scopes.py` and
`.analysis/direct-owner-original-scopes.json`. The preceding remap reproducer
and scopes remain `.analysis/review-remapped-owner-scopes.py` and
`.analysis/remapped-owner-original-scopes.json`. Current unchanged compiler artifacts and
incremental graph are checked in `.analysis/enemy-eh-artifact-check.json`.
Preceding source-restoration evidence is `.analysis/anm-insertion-restored-build.log`
and `.analysis/anm-insertion-restored-check.json`. The current source input includes
the retained season/replay table declarations; all complete function bytes remain
unchanged. Preceding source-trial evidence is `.analysis/failure-format-runtime-restored-build.log`,
`.analysis/failure-format-runtime-restored-check.json` and
`.analysis/failure-format-spell-source-trials.json`. That restoration used a
fresh incremental receipt before the current declaration change.
The preceding music-room evidence
remains `.analysis/music-room-restored-build.log`,
`.analysis/menu-literal-restored-context-check.json` and
`.analysis/music-room-source-trials.json`. The preceding replay-slot evidence
remains `.analysis/pause-open-retained-build.log`,
`.analysis/pause-open-retained-build-check.json` and
`.analysis/pause-open-source-trials.json`. The preceding interpolation evidence
remains `.analysis/interp-methods-restored-build.log`,
`.analysis/interp-methods-restored-check.json` and
`.analysis/interp-methods-source-trials.json`. Earlier countdown/circle contexts
remain in `.analysis/special-vertices-source-trial.json`,
`.analysis/circle-angle-source-trials.json` and
`.analysis/circle-rect-source-trial.json`.

```sh
.venv/bin/python scripts/progress.py
```

Run this first: it checks source, artifact, report and retained-unit freshness.
The current report is `.analysis/reference-audit.json`; complete retained units
are in `config/match-units.toml`. See [REFERENCE_IMPORT.md](REFERENCE_IMPORT.md)
for the comparison contract and [reviewed linkage evidence](knowledge/reviewed-linkages.md)
for fixed runtime, literal and vftable identities.

## Environment and workflow

- Canonical target: `resources/th16.exe`, original Japanese v1.00a, SHA-256
  `c11776019f083978e66027e7394dafb1fb9543afca986f28049a49417e341929`.
- Shared historical MSVC 19.10.25017, SDKs, Ghidra/JDK/Wine and the pinned Wine
  NTLM helper are configured. Prefix, analyzer project and runtime state are
  game-local. See [SHARED_TOOLS.md](SHARED_TOOLS.md).
- Game code is under `src/`; separate compiler-context callers and opaque support
  are under `probes/reference-harness/` and `probes/reference-support/`.
- `_reference/johnthreekay-th16` is unchanged at
  `2b846da735ac71f68b1dc74e8194c8c8d98e2869`. Provenance is recorded in
  `config/reference-sources.csv`; README retains upstream credits and CC0.

For a source iteration:

```sh
.venv/bin/python scripts/build.py
.venv/bin/python scripts/compare-linked-function.py reference-00408260
```

Choose a retained unit relevant to the change. For an annotated owner with no
retained unit, or after an extent/linkage change, run a focused diagnostic:

```sh
.venv/bin/python scripts/audit-reference.py --address 0x407900 --json .analysis/masked-switch-focused.json
```

Repeat `--address` for a bounded batch. This retains all independent symbol
bindings and compares full owners, while writing only a separate ignored
report. It cannot update canonical reports, units or ledgers. A changed source
or header makes the previous audit stale; after a coherent batch, regenerate
units and results:

```sh
.venv/bin/python scripts/audit-reference.py --write-units
.venv/bin/python scripts/progress.py
```

No rebuild is needed for prose edits. Oracle/binding edits require a new audit
because their content is fingerprinted; they do not inherently require a new
compile. Do not run checks that read generated ledgers concurrently with an
audit writing those ledgers.

## Outstanding work

The 301 incomplete candidates comprise 132 with unresolved fields, 132
candidate/original-inventory extent refusals, 27 without a same-start
contribution, six with source-object ownership differences, two requiring
reviewed switch or owned-data extents and two with reviewed case-map mismatches.
The extent category includes original code contexts with unreviewed owned data;
it does not establish a genuine
source-size difference in every case. None is currently refused specifically
for a missing original boundary. Other evidence can precede boundary checks;
this does not prove every annotation has a complete original scope review.

The private profile now has thirteen explicit records: the preceding eleven
32-byte helpers plus the ordinary AnmVmRun helper and its different complete
39-byte XY-output body. It requires full profile bytes, source-qualified private
MAP names, unique complete PDB producers and exact annotation/witness identities.
Primary units and direct CALL fields opt in explicitly with `reviewed_static`;
no interior/addend, public alias, generic fallback or tail transfer is permitted.
Consumed source/name metadata is fingerprinted. Existing wrappers remain source
context hypotheses. No game source or assembly change is retained.

The ordinary AnmVmRun helper at `0x00464D60` and XY helper at `0x00464930`
pass their entire 32/39-byte private owners. The parent at `0x004632F0` now has
a complete independent scope: 2,068 bytes of code, a 16-byte target table and a
17-byte remap table, for **2,101 bytes through `0x00463B24`**. Eleven INT3 bytes
separate it from the next independent entry. See
[the complete scope review](knowledge/special-vertices-scope.md). Its candidate
owns 2,062 code bytes, two alignment bytes and the 33 table bytes, for 2,097
bytes. This four-byte whole-owner difference is now established independently;
do not trim or resize either owner to make it compare. The complete original
remap profile does not grant the parent or tables any exact credit.

A guarded do/while countdown now tests the original's positive-entry and
nonzero-backedge structure. It changes register allocation but leaves the full
candidate at 2,097 bytes and is rejected. Source is restored byte for byte and
freshly rebuilt. Full sources, outputs and diagnostic scopes are retained in
`.analysis/special-vertices-{baseline,countdown-artifacts}/` and
`.analysis/special-vertices-source-trial.json`. Do not repeat this context or
force scheduling, spills or registers. The main interpreter's complete original
now owns 14,177 bytes, including two target tables and 215/313-byte maps. Its
14,141-byte candidate differs by 36 bytes and still exposes eight unbound fields
first. See [the compound review](knowledge/compound-owner-scopes.md). Other
private wrappers still need independent original entry/path and producer
reviews.

Ten further original remap scopes are now independently complete. The enemy
allocator, both EnemyInf global-pointer getters and AnmVm integer/value pointer
getters pass all code, both tables and alignment, totaling 2,622 bytes. See
[the new scopes](knowledge/remapped-owner-scopes.md). LaserLineInf::run_ex
remains 1,748 against 1,588 bytes; LaserCurveInf::run_ex is 1,720 against 1,548;
texture conversion is 1,822 against 2,014. EclRunContext::ecl_run is 7,462 against
7,046 and still exposes three unbound fields first. Do not resize these roots
to the candidates. Original complete scope review and candidate exact acceptance
remain separate requirements.

Thirty-seven further direct-table original scopes are independently complete.
The full 532-byte Bullet::step_ex_04, 1,900/2,808-byte EnemyInf integer/float
global getters, 868-byte draw_text, 396-byte resolution dialog, 824-byte AnmVm
float-variable getter and 876-byte render-state setup all pass. See
[the new direct scopes](knowledge/direct-owner-scopes.md). Twenty-five reviewed
candidates have different whole extents; four equal-size candidates lacked
bindings at that checkpoint. Stage_clear now passes after the complete stage-table
review. BombInf::create (nine) and EndingScriptVm::run (six) remain unresolved.
Music-room bindings now resolve, exposing a complete 3,133/3,136 mismatch.
Its only differences are zero-store displacement bytes at +0x174, +0x17C and
+0x184: the candidate initializes position X/Y before the loop index, while
the original initializes the index first. Declaring the used counter earlier
retains the same mismatch; assigning one zero Float3 gives a 3,152-byte owner;
initializing X/Y per comment line gives 3,105/3,136. All three contexts are
rejected and source is restored. See
[the review](knowledge/menu-literal-identities.md) and
`.analysis/music-room-source-trials.json`. Do not repeat these contexts or
force stores/registers to recover the order.

Seven newly reviewed typed numeric bindings include the music-room values
20.0f/8.0/40.0f and further 50.0f/60.0f/30.0f/2.5f. Original dense witness
owners and all duplicate read-only copies are retained; only a fixed original
typed read selects storage. Complete enemy fog and FPS drawing pass; the
complete player circle check remains 181/258. Gather's complete original is
1,973 bytes against 1,993, and stage fog is 2,156 against 2,172. The sound
thread exposes an extent refusal after its last field resolves. Other callers
retain unresolved fields. No scope or field-normalization rule changes.

The subsequent fixed 176.0f/512.0f values and complete `%3d` format add full
Cirno update/cancellation, Marisa update and replay FPS passes. The original
player update's complete switch profile remains 4,540 bytes (4,519 code,
one alignment byte and five targets), against a 4,508-byte candidate. All
fields now bind and the extent refusal remains. The player laser tick also
exposes an extent refusal; masked Anm drawing, Reimu orb update and GUI drawing
retain one/three/eight unresolved fields. The remaining STD destination is
private exception-handling code, requiring its own complete frame/metadata
review. See [the identity review](knowledge/replay-literal-identities.md).

The full Player update differs in the item-drop pointer/power path, two
inlined timer decrements, afterimage mode-word handling and scaled box
scheduling. Four source contexts are now excluded. A used pointer for both
coordinate reads and item creation gives 4,504 bytes; limiting it to item
creation gives 4,508. Both fail the independent 4,540-byte owner. A Float2
circle displacement gives 261 against 258. Combining equivalent dialogue and
non-graze state guards gives 190/258, still a complete mismatch, and is rejected.
The Float2 context also expands the separate Bullet::check_player_collision
caller from 449 to 460 bytes. Its original is now independently complete at
448 bytes: 130 reachable instructions and a contiguous next entry. Full
caller evidence is `.analysis/player-secondary-original-scope.json`;
restoration returns the caller to 449. No prefix receives credit.
Baseline source is freshly restored with all 1,719 complete linked owner
entries/extents/payloads and all 192 dependency stamps checked. See
[Player source contexts](knowledge/player-context-trials.md). Do not repeat
these forms, retain a change for one matching stack slot, force timer identity
multiplications, or normalize registers/branch placement. The underlying type,
alias and timer context remains open.

The original interp_common_methods at `0x004033F0` now owns 1,692 bytes:
1,566 code, two alignment bytes and 31 table slots. Its baseline candidate is
also 1,692 bytes, but nine case starts are three bytes earlier. The original
profile refuses the case mapping; do not change its reviewed offsets or hide
them with relocation addends. Two ordinary source contexts are rejected:
a shared quadratic scaling return plus direct sine returns stays 1,692 bytes
but retains layout differences; reflected-coordinate assignments plus
constant-first sine addition gives 1,696 bytes. Source is restored byte for
byte and freshly rebuilt. Full owners, actual candidate table locations,
receipts and source are retained under
`.analysis/interp-methods-{source-baseline,return-flow-artifacts,reflected-curve-artifacts}/`
and `.analysis/interp-methods-source-trials.json`. Do not repeat these contexts
or force allocation.

The compound review supersedes eight of the preceding ten multiple-dispatch
exclusions. Original STD, bullet shooting/run_ex, supervisor switching,
pause/title flows, window_proc and draw_vm now have complete scope records.
The two exact candidates are retained. Supervisor now passes after complete
stage-table binding. Pause has no unbound fields left but retains a complete
4,676-byte case-map refusal: slots 7/9 start at 1,420 rather than 1,392, slot 10
at 1,988 rather than 1,982. Slot 11 now matches 3,207 after explicitly saving
the replay slot before the factory call; the complete replay-name-save path
also recovers its original copy loop. Its second five-slot table matches.
See `.analysis/pause-open-retained-layout.json` and
[the source review](knowledge/pause-replay-slot.md). The complete diagnostic
replay improves from 3,345/4,676 to 4,067/4,676, with all 306 fields processed,
but the original profile still refuses it. Resume-to-switch-exit and
quit-shortcut early-return forms produce no code improvement and are rejected.
Do not repeat these forms or force registers, base/index encodings, case offsets
or layout to hide the remaining differences. Other candidates
have different whole extents, with STD now exposing one
unbound field first. Ascii drawing at `0x00408A89` needs memory-bound/reload
alias evidence; the large enemy ECL dispatch at `0x0041DD51` has an interposed
frame store. Both remain unreviewed. Locators and reasons are in
`.analysis/compound-owner-original-scopes.json`. Do not infer a full owner
from one table or traverse undeclared indirect edges.

The circle/rectangle collision trial reverses rotation multiplication operands
into matrix-coefficient-first form. It leaves the full owner at 243/400 matching
bytes and is rejected. Full original and baseline/trial/restored candidate
owners are in `.analysis/circle-rect-source-trial.json`; complete source/output
sets are `.analysis/circle-rect-{source-baseline,matrix-products-artifacts}/`.
Do not repeat this context or force operand registers.

A natural circle source trial splitting angle advancement from normalization
leaves its complete result at 514/588 matching bytes and is restored. Full
baseline/trial scopes and outputs are retained; do not repeat that context or
force scheduling. Ring remains 428/558 and fan tick 583/639. The function at
`0x00469890` is triangle-fan drawing (349/355), not a circle outline.

The new full 412-byte LaserLine/LaserCurve angle units each differ in 11 bytes
at +0x33..+0x3D, where a float load and completed-round memory increment have
different order. This is an INC, not an argument push.
Their unit names are reference-00432c20 and reference-004392c0. The curve angle
acceleration unit reference-00439460 differs in 14 bytes around +0x83..+0x90.
These are useful source-context targets; preserve complete extents and avoid
forcing instruction order. Two other newly retained laser owners also mismatch.

Two natural laser contexts have now been tested and rejected. Folding the
completed-round increment into the final condition retains each full 412-byte
owner but increases its differences from 11 to 91. Computing next length
before committing angle/length changes the curve acceleration candidate from
323 to 315 bytes; it remains incomplete. Both sources and complete outputs
are retained under `.analysis/laser-angle-{completion,next-values}-artifacts/`,
with `.analysis/laser-angle-source-trials.json` and focused reports. Baseline
source is restored byte for byte and freshly rebuilt; its full input identity,
all artifact hashes and all 192 dependency stamps validate in
`.analysis/laser-angle-restored-check.json`. Do not repeat these contexts or
force ordering, spills or registers.

The complete AnmManager constructor is now a retained 5,054/5,071-byte mismatch.
Its EH profile checks both whole 136/76-byte contributions; the handler remains
an explicitly scoped interior entry rather than a standalone PDB owner. See
[the aggregate review](knowledge/anm-constructor-eh.md). Its 17 differing bytes
are within `+0xABE..+0xACF`: the original clears two callback fields before flag
bit zero, whereas the candidate clears the flag first. All 164 primary linkages
are compared. The retained volatile-this accesses in the shared UpdateFunc
constructor remain a source/context hypothesis. Recover that context rather
than special-casing one registration or forcing the instruction order. Other
nonempty EH graphs, apart from the separately reviewed Stage/ItemManager
single-member constructors, still need independent complete-owner review; do not
generalize this explicit profile to arbitrary tables or interior symbols.
Moving an ordinary constructor definition to UpdateFunc.cpp alone has now
been tested and rejected against complete owners; do not repeat that trial.

The 35 original references in `.analysis/callback-entry-inventory.json` have
reviewed roots. A second discovery index,
`.analysis/missing-entry-reference-discovery.json`, records 84 instruction
references to 74 formerly missing entries. The 41 AnmManager entries and 20
further registered callbacks are now reviewed. That review also derives
the Ascii drawing helper from its registered caller's tail transfer. The latest
review establishes the other 13 referenced roots through worker creation,
array constructor/destructor iteration, registry insertion and LZSS tail
transfers. All 74 roots in that discovery index now have reviewed scopes.
The 21 data-address locators in `.analysis/missing-entry-pointer-discovery.json`
now have reviewed original callback-cell roles and complete scopes. The review
also derives the gather switch entry at `0x00405F20`, which had been hidden
behind an unresolved-field refusal. Camera has an original relative-call
witness at `0x004010B8`; the caller is reached through the complete bounded
16-cell CRT initializer interval. Its complete 194-byte original scope is also
reviewed, but its candidate still lacks a complete same-start PDB contribution.
The original PE has no base-relocation directory; raw occurrences are not
relocation evidence. Event callback cell windows do not prove complete global
array extents or arbitrary selector validity. No table data exact credit or
generic indirect-jump allowance is added. Continue from unresolved fields and
source/context differences, retaining all unknown ownership and bounds.

The LZSS deletion row at `0x00458370` is now 84 bytes through `0x004583C3`.
The independently reached tail helpers at `0x004583D0` and `0x00458430` own
83 and 121 bytes. All 313 bytes in the superseded Ghidra region are accounted
for by those owners and 25 INT3 bytes. Do not restore the overlapping aggregate.
The earlier runtime-entry review uses three bounded parent switches only for
witness paths. Those proofs alone grant no complete primary comparison credit.

The eight imported alignment helpers and 86 explicitly artificial standalone
locals were removed. The latter cleanup withdrew 23 earlier exact results;
all 600 passes after cleanup remain exact. Recover real types and calling
context rather than restoring the artificial inputs. Other compiler-context
helpers, forced accesses and type hypotheses still need source review.

Sixty-five reviewed bounded switch scopes include complete code and owned data:
45 direct-table, eleven byte-remap and nine compound owners. Twenty-six have
complete retained comparison units (23 exact and three mismatch). The remaining
39 original reviews grant no candidate credit. Music-room's full owner is now
a complete mismatch.
`PosVel::step` and `anm_masked_effect_on_switch` remain complete mismatches with
four and 45 differing bytes. Two candidates are refused specifically for
unreviewed indirect dispatches; additional unresolved graphs can be hidden
behind earlier field or extent checks. Multiple dispatches require an explicit
complete compound record. Nonadjacent/memory bounds and undeclared or unbounded
tables remain refused.
Read the final repair-log section before retrying PosVel vector-expression
variants, VM deletion aliases, precomputed render limits or shake timer helpers.
The circle constructor has now been simplified in isolation: this regresses
the complete owner and also changes wave scheduling. The current 696/700 result
retains the indexed circle form. Remaining circle
operand order needs better source/type/context evidence; do not normalize it.

The two legacy and eleven saved-register empty-EH3 graphs are complete. Their
selectors require the exact parent-derived private MAP names, full source-object PDB ownership and
complete 27/36-byte handler/descriptor extents. Do not extend this proof to
nonempty unwind/try tables or another handler shape. Identical metadata from
another parent is explicitly rejected. Continue from unresolved-field reasons
or the remaining source/type differences; the isolated PosVel circle trial is
complete and rejected.

`draw_line` is a complete 569-byte pass. `world_pos` has a GS-cookie/extent
difference. Int3 interpolation at `0x00464590` differs in one SIB byte. Float2
interpolation, points-in-rectangle and ECL argument-pointer trials also remain
unresolved. Read [reference-repairs.md](knowledge/reference-repairs.md) before
repeating their failed expression, temporary-variable or helper variants.

The latest bounded trials also reject source/count-scope changes in
`AnmVm::load_from`, carrying the Float2 timer/vector repair into Float3, and
indexed scalar additions in the bullet cancellation half step. See the final
repair-log section before repeating them. The original `floor` root has a
2991-byte Ghidra extent with a distant fallback, not the candidate's 253-byte
contribution; it remains unbound.

`__CIatan2` is a promising evidence investigation, not an accepted runtime
binding. Its two explicit MASM procedure records share one complete 20-byte
contribution. The [investigation note](knowledge/reference-repairs.md#unfinished-atan2-entry-investigation)
records the earlier native evidence and withdrawn draft. The subsequent
[complete dependency review](knowledge/atan2-runtime-dependencies.md) now
establishes the original 645-byte dispatcher aggregate, complete 48-byte pool,
full 80-byte descriptor and nonadjacent 500-byte candidate producer. Original
companion ownership and all external field identities remain open. Do not
infer an interior entry from a public label or shorten a contribution to obtain
exact credit. The extracted research parser remains outside the Oracle and
must not be installed as a production proof without negative controls.

## Local artifacts

See [ARTIFACTS.md](ARTIFACTS.md) before cleanup. Historical reports and large
unused dumps are compressed; the current report remains plain JSON. The cleanup
manifest is `.analysis/cleanup-20261108.json`. Keep current build objects, PDBs,
receipts, the private target, reference checkout, Wine prefix and Ghidra project.
