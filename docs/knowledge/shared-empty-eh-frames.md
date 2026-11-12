# Six further complete empty EH3 destructor graphs

The existing `empty-eh3-saved-ebx-esi-edi-v1` profile validates six further
source-qualified destructor graphs without changing any admission rule or game
source. All six complete parents now pass, adding 2,716 primary exact bytes.
The [Enemy frame review](enemy-empty-eh.md) documents the profile's derivation.

## Original scopes and private roles

| Parent | Complete original parent | Reachable instructions | Private handler | FuncInfo |
| --- | --- | ---: | --- | --- |
| `Fog::~Fog` | `0x00409550`, 273 bytes | 93 | `0x0048A3E0` | `0x0049AF9C` |
| `EndingScriptVm::~EndingScriptVm` | `0x004190B0`, 181 bytes | 59 | `0x0048A5D0` | `0x0049B18C` |
| `Ending::~Ending` | `0x00419450`, 496 bytes | 124 | `0x0048A620` | `0x0049B1DC` |
| `GuiMsgVm::~GuiMsgVm` | `0x004264A0`, 729 bytes | 211 | `0x0048A6F0` | `0x0049B2A0` |
| `LoadingThread::~LoadingThread` | `0x0043AFE0`, 518 bytes | 133 | `0x0048A8A0` | `0x0049B45C` |
| `Player::~Player` | `0x00441A50`, 519 bytes | 124 | `0x0048A8C0` | `0x0049B480` |

Original-only review decodes every byte, traverses every instruction from the
entry, checks all branch destinations and terminal paths, excludes interior
inventory entries and accounts for all following INT3 alignment. Each parent's
fixed registration PUSH selects its own handler. Each complete 27-byte handler
ends before five INT3 bytes and selects its own complete 36-byte descriptor.
All six descriptors contain exactly `19930522 0 0 0 0 0 0 0 5`.

Each original and candidate parent has the exact 38-byte registration sequence
and 18-byte restoration sequence required by the existing profile. The node is
EBP-12; one local word and saved EBX/ESI/EDI place the encoded cookie at EBP-32.
The handler therefore reads node-20. The PE load configuration independently
identifies cookie storage. Whole-parent checks retain the restrictions on
direct reserved-slot uses, FS references, EBP writes and the final return.

## Complete candidate ownership

| Source object | Candidate parent | Private handler | FuncInfo |
| --- | --- | --- | --- |
| `Stage.obj` | `0x00469F90` | `0x0048AA60` | `0x0049B34C` |
| `Ending.obj` | `0x004271C0` | `0x0048A620` | `0x0049AF10` |
| `Ending.obj` | `0x00426E50` | `0x0048A600` | `0x0049AEEC` |
| `Gui.obj` | `0x00436A60` | `0x0048A740` | `0x0049B024` |
| `LoadingThread.obj` | `0x0044C2B0` | `0x0048A8D0` | `0x0049B1BC` |
| `Player.obj` | `0x0045D710` | `0x0048A950` | `0x0049B230` |

The candidate parents have unique, same-size, complete source-object PDB owners
and public entries. Their parent-qualified private MAP names select complete
27/36-byte handler/descriptor PDB contributions in the same module. Interior
labels, ambiguous ownership and overlap remain forbidden. Identical empty
descriptors do not establish interchangeable private roles.

Every handler instruction is checked, including the independently bound cookie
checker and `___CxxFrameHandler3` transfers. The complete candidate handler has
exactly one PE relocation at offset 18; its descriptor has none. The parent
registration has exactly the handler/cookie relocations at offsets 6/22, and
the restoration has none. All 162 auxiliary code bytes and 216 metadata bytes
receive no additional primary credit. Every primary body byte, field and
relocation still undergoes complete ordinary replay.

## ReplayManager remains excluded

The same cookie displacement alone does not admit ReplayManager destruction.
Its complete original owner is 416 bytes at `0x00447C80`, with 120 reachable
instructions and its final RET at `0x00447E1F`. The next function starts directly
at `0x00447E20`. Its complete candidate PDB owner at `0x004648F0` is 415 bytes.
Both full frame sequences separately fit the profile, but the required equal
complete-parent extent does not. A diagnostic record is refused with
`EH parent lacks one complete candidate PDB owner`; it is not installed.
Its existing incomplete result remains identical. Other cookie displacements
and nonempty graphs also retain their existing refusal behavior.

## Replay, controls and retained evidence

Canonical replay reports **855 exact, 65 mismatch and 295 incomplete** among
1,215 annotations, with **159,345 exact primary bytes and 920 units**. All
previous 849 exact results, 65 complete mismatches and 914 unit definitions
remain identical. Six new whole passes account for all 2,716 added bytes.

**120 controls pass**: saved-register EH (17), legacy empty EH (25), constructor
EH (25), reviewed linkages (36), strict Oracle (14) and focused audit (3).
The saved-register suite now exercises all eight reviewed parents, including
cross-module reuse of identical descriptors. Frame/cookie/state mutations,
forged hashes, incomplete private extents, wrong relocations and source-scope
overrides remain rejected. Ordinary body mutations still fail complete byte
comparison after successful EH validation.

No game source, admission rule or compiler artifact changes and no build occurs.
The source input remains
`c2ac9cc0add85924f097edf2dc772148551601b302607cc480fba1867a1fcd5a`.
All 1,719 complete linked owners and 192 dependency stamps validate. The
incremental build graph and ignored evidence remain retained. Source-origin
review and formal Factory acceptance remain open.

Retained ignored evidence and reproducers:

- `.analysis/shared-empty-eh-original-scopes.json`, reproduced by
  `.analysis/review-shared-empty-eh-originals.py`: original-only complete scopes,
  raw payloads, control flow, handler roles and descriptors.
- `.analysis/shared-empty-eh-caller-scopes.json`, reproduced by
  `.analysis/review-shared-empty-eh-callers.py`: complete private owners,
  original/candidate payloads, fields, relocations and six standalone replays.
- `.analysis/shared-empty-eh-replay-complete-exclusion.json`, reproduced by
  `.analysis/review-shared-empty-eh-replay-exclusion.py`: unequal complete
  ReplayManager scopes and the unchanged refusal.
- `.analysis/shared-empty-eh-artifact-check.json` and
  `.analysis/shared-empty-eh-regression-check.json`, reproduced by the matching
  `check-*.py` files: unchanged compiler artifacts, dependency stamps, prior
  results/units, exact-byte totals and control summaries.
- `.analysis/shared-empty-eh-{focused,full-audit}.log`,
  `.analysis/shared-empty-eh-<suite>-controls.log` and
  `.analysis/shared-empty-eh-controls-summary.json`: terminal audit/control runs.
