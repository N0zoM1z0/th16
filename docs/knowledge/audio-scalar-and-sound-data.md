# Complete sound data and bounded audio source trials

The current local strict report is 881 exact, 65 mismatch and 269 incomplete
among 1,215 annotated candidates, covering 167,359 primary exact bytes and
946 complete units. Two sound-queue entries now pass their complete owners:

| Original entry | Function | Complete bytes |
| --- | --- | ---: |
| 0x0045E150 | SoundManager::play_sound_centered | 145 |
| 0x0045E1F0 | SoundManager::play_sound_at_position | 168 |

An independently reviewed complete data contribution resolves their table
fields. Its 1,656 auxiliary bytes grant no primary exact credit. Two preceding
natural audio source trials fail and are restored byte for byte; the retained
game source is unchanged. Source-origin review remains open and Factory
acceptance is not submitted. No repository content is published or pushed.

## Complete sound-table and anchor contribution

The candidate g_sound_effect_table starts at 0x0049D6A0. Its same-start PDB
contribution owns 1,656 bytes, comprising three adjacent typed globals:

| Object | Offset | Complete typed size | Original address |
| --- | ---: | ---: | --- |
| g_sound_effect_table | 0 | 1,560 | 0x004A2A30 |
| g_anchor_corners_x | 1,560 | 48 | 0x004A3048 |
| g_anchor_corners_y | 1,608 | 48 | 0x004A3078 |

The producer is probes/reference-support/SoundData.cpp, compiled without /GL
in the existing support graph. It supplies initialized data, never primary game
code credit. The full PDB contribution, module, source object, all three public
names, all three typed extents, section permissions and every owned byte are
required. No internal name, duplicate contribution, overlapping owner or
foreign producer is admitted. Both full ranges are writable initialized raw
data with no pointer relocations, including crossing relocations. No literal
or immutability claim is made for this mutable storage.

Both original queue functions independently identify the first object's role.
Their complete 145/168-byte closed graphs have 43/51 reachable instructions.
The LEA at 0x0045E157/0x0045E20A computes five times the sound ID; the following
MOVSX at 0x0045E15A/0x0045E20D reads a signed word using scale four and displacement
0x004A2A3A. Together these establish a twenty-byte row and field offset ten.
Complete original hashes and independent boundaries anchor both instruction
starts. Candidate labels, sizes and matching outcomes do not choose the
original address.

All seventy-eight complete scalar rows are checked: IDs form a permutation of
0-77, file indices lie in 0-66, signed volumes and queue metadata retain their
reviewed ranges, and the two flag words are zero/one. The complete adjacent
anchor arrays retain all twenty-four fixed float values. Full byte comparison
then requires the entire 1,656-byte candidate contribution to equal the
original, including both anchor arrays. The 1,560-byte typed sound table is
not misrepresented as a standalone PDB contribution, and the anchors are not
omitted as padding.

The explicit sound-data-aggregate-v1 linkage profile exports only
?g_sound_effect_table@@3PAUSoundEffectData@@A. Ordinary primary fields must be
DIR32 points within its 1,560-byte typed table; local aliases, alternate field
types, one-past limits and addresses in the adjacent anchors are refused.
Neither anchor name receives a binding from this review. The verifier module
scripts/sound_data_identity.py is part of the Oracle fingerprint. No generic
aggregate or mutable-data admission is added.

The full canonical comparison also changes two incomplete records explicitly:
TitleInf::do_replay_save at 0x00453C10 loses its table field but still fails
complete extent equality; SoundManager::initialize at 0x0045D510 loses three
table fields and retains its private EH entry and the anchor-x-plus-four loop
limit. The latter is not an ordinary in-table address. Do not bind the adjacent
array or enlarge the typed table to make that limit pass without a separate
complete cursor/ownership review.

## Rejected natural scalar source contexts

CSound::SetVolume at 0x004711F0 owns 114 original bytes and 36 reachable
instructions, followed by fourteen INT3 bytes before the next entry. Its
baseline candidate owns 116 bytes. The original performs the COM call within
each branch, pushes -10000 directly on the zero-volume branch, and loads the
buffer earlier on the scaled branch.

The first trial preserves a used buffer pointer within the scaled branch and
returns each branch's actual COM result. It produces a complete 115-byte
candidate. The compiler hoists the shared buffer-array load above the branch
and reads the BGM setting through a compare plus a later memory MOVD. That
whole owner still differs from the independent 114-byte original and is
rejected. No one-byte prefix or equivalent register encoding receives credit.

The second trial adds a used BGM-setting snapshot for both the guard and float
conversion, with conversion before the used buffer snapshot. It produces
exactly the same complete 115-byte candidate, including the setting reload and
hoisted buffer load. It is also rejected. Do not repeat these snapshots or
force volatile accesses, registers, compiler barriers or an extra fake local.

CSound::Unpause at 0x00471380 owns 103 original bytes and 35 reachable
instructions, followed by nine INT3 bytes. The original subtracts pause time
from the returned runtime in XMM0, then adds the accumulated pause total directly
from memory. The 107-byte candidate instead loads the total into XMM1 and uses
a register addition. A natural compound assignment,
m_paused_total += get_runtime() - m_pause_time, produces exactly the baseline
107-byte machine code. It is rejected and restored. Earlier addend reversal
and a named pause-duration trial also remain excluded; see the earlier repair
log. Used BGM snapshots and compound accumulation do not recover the missing
source/type/calling context.

Five calls to SetVolume are independently covered by existing complete exact
Play/fade callers. The complete original sound worker at 0x0045E330 adds the
sixth SetVolume call at 0x0045E3B0 and Unpause's call at 0x0045E626. Its existing
bounded switch record covers 1,428 bytes: 1,390 code bytes, two alignment bytes
and nine target slots. All 368 instructions are reached through the reviewed
normal edges and case entries. This establishes original call-site identity;
it gives no exact credit to the worker's unequal 1,420-byte candidate.

## Restoration, regression and controls

Only DSUtil.cpp is compiled for each trial and the final restoration, followed
by the normal incremental LTCG link. All sources are restored byte for byte.
All 1,719 complete linked function records, including addresses, sizes,
producer metadata and full payload hashes, are identical to the initial
checkpoint. All 192 dependency stamps validate. Source input remains
`356af008e8064e7f8080f6c112145362eea142d1955f371a989e5b65034aca5f`.
PDB age changes from 121 to 124 and EXE/MAP/PDB fingerprints refresh; these
metadata changes are retained rather than replacing fresh outputs with old
artifacts. The function-list hash remains identical.

All preceding 879 exact results, 65 complete mismatches and 944 unit definitions
are retained. Earlier complete comparison details differ only in image hash
and PDB age. Every other incomplete record is identical apart from the two
explicit table-field deltas above. The two new primary owners add exactly
313 bytes; the auxiliary aggregate adds none. The canonical report and all
946 unit hashes validate against the restored current build.

One hundred thirty-five controls pass across seven relevant suites: sound data
(18), reviewed linkages (43), strict Oracle (14), focused audit (3), stage/time
identities (20), ISA storage (16) and aligned audio EH (21). New controls mutate
every candidate aggregate byte, require all original witnesses and all complete
PDB/typed owners, reject wrong storage/relocations/aliases, enforce the narrow
primary field gate and replay both complete primary owners. An unrelated queue
body mutation leaves its data proof intact but still fails primary comparison.

Retained evidence includes:

- `.analysis/audio-scalar-baseline/`: original sources, compiler artifacts,
  receipt, complete linked records, canonical report, bindings and units.
- `.analysis/inspect-audio-scalar.py`,
  `.analysis/audio-scalar-original-scopes.json`: both complete original and
  baseline candidate scalar scopes and existing exact caller fields.
- `.analysis/audio-scalar-context-artifacts/` and
  `.analysis/audio-scalar-setting-snapshot-artifacts/`: both complete trial
  source/output sets; their focused reports use the same filename stems.
- `.analysis/audio-scalar-trial-records.json`: whole-owner refusals and exact
  equality of the two trial outputs and baseline Unpause.
- `.analysis/review-audio-scalar-parent.py`,
  `.analysis/audio-scalar-parent-witnesses.json`: full original worker graph
  and both direct calls, with zero primary credit.
- `.analysis/audio-sound-data-original-witnesses.json`: complete original queue
  owners, instruction starts, signed field reads and full hashes.
- `.analysis/review-audio-sound-data.py`,
  `.analysis/audio-sound-data-graph-proof.json`: the final full contribution,
  typed members, witness identities and both full primary comparisons.
- `.analysis/check-audio-scalar-artifacts.py`,
  `.analysis/audio-scalar-artifact-check.json`: byte-for-byte restoration and
  all complete owner/dependency checks.
- `.analysis/audio-sound-data-<suite>-controls.log`,
  `.analysis/audio-sound-data-controls.log` and
  `.analysis/audio-sound-data-controls-summary.json`: all 135 controls.
- `.analysis/check-audio-sound-data-regression.py`,
  `.analysis/audio-sound-data-regression-check.json`: complete unit/report
  retention and both explicit incomplete deltas.
- `.analysis/audio-sound-data-next-inventory.json`: remaining audio scopes,
  extents, fields and reasons, with missing ownership left explicit.

Focused reproduction:

```sh
.venv/bin/python scripts/audit-reference.py --address 0x45e150 --address 0x45e1f0 --json .analysis/audio-sound-data-focused.json
.venv/bin/python scripts/test-sound-data-identities.py
.venv/bin/python scripts/progress.py
```

Do not run ledger readers/tests concurrently with audit-reference.py --write-units.
