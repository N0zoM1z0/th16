# Registered manager wrappers and constructor context

Reviewed 2026-11-11 against the canonical original. Twenty original registry
witnesses and one registered callback's tail transfer establish 21 complete
owners. All 21 pass the strict linked-owner comparison, adding 604 exact primary
bytes. Candidate sizes and upstream exact labels do not enter the original
scope derivation. Names in the table below label the reviewed original roles;
reference source origin remains under review.

## Original entries and complete scopes

| Original entry | Complete end | Bytes | Role | Registry / priority |
| --- | --- | ---: | --- | --- |
| `0x00408090` | `0x00408097` | 8 | Ascii draw callback 1 | draw / `0x51` |
| `0x004080A0` | `0x004080A4` | 5 | Ascii draw callback 2 | draw / `0x35` |
| `0x004080B0` | `0x00408135` | 134 | Ascii draw callback 3 | draw / `0x42` |
| `0x00408EF0` | `0x00408FAA` | 187 | Ascii group-1 drawing | callback-2 tail transfer |
| `0x0040A7A0` | `0x0040A7A4` | 5 | Stage tick callback | tick / `0x11` |
| `0x0040A7B0` | `0x0040A7B4` | 5 | Stage draw callback 03 | draw / `0x03` |
| `0x0040A7C0` | `0x0040A7C7` | 8 | Stage draw callback 06 | draw / `0x06` |
| `0x004197A0` | `0x004197A4` | 5 | Ending tick callback | tick / `0x23` |
| `0x004197B0` | `0x004197B5` | 6 | Ending draw callback | draw / `0x43` |
| `0x0041B4F0` | `0x0041B526` | 55 | Enemy tick callback | tick / `0x1A` |
| `0x0041B530` | `0x0041B535` | 6 | Enemy draw callback | draw / `0x17` |
| `0x00426490` | `0x00426494` | 5 | FPS draw callback | draw / `0x4B` |
| `0x00429AF0` | `0x00429AF7` | 8 | GUI tick callback | tick / `0x20` |
| `0x00429B00` | `0x00429B05` | 6 | GUI draw callback 1 | draw / `0x33` |
| `0x00429B10` | `0x00429B14` | 5 | GUI draw callback 2 | draw / `0x30` |
| `0x0042DB70` | `0x0042DB74` | 5 | GameThread tick callback | tick / `0x0F` |
| `0x0042DB80` | `0x0042DBB2` | 51 | GameThread draw callback | draw / `0x02` |
| `0x00443720` | `0x00443727` | 8 | Player tick callback | tick / `0x16` |
| `0x00443730` | `0x00443781` | 82 | Player draw callback | draw / `0x1D` |
| `0x0044B5D0` | `0x0044B5D4` | 5 | Title tick callback | tick / `0x06` |
| `0x0044B5E0` | `0x0044B5E4` | 5 | Title draw callback | draw / `0x45` |

Nine independently inventoried parent entries provide the registry witnesses:
Ascii initialization `0x00407CB0`, Stage loading `0x004097C0`, Ending
initialization `0x004191F0`, Enemy initialization `0x0041AE70`, GUI
initialization `0x00426B00`, GameThread startup `0x0042CB60`, Supervisor
registration `0x0043B520`, Player initialization `0x00440FB0` and Title
initialization `0x0044AC70`. Their full original bytes, hashes, instruction
starts and concrete paths from entry to each witness are retained. A witness
path does not grant exact credit to its parent or establish every parent path.

Each pushed callback is passed to original `create_func` at `0x00401730`.
That complete 106-byte helper allocates a `0x28`-byte record, reads its callback
argument from `[ebp + 8]`, stores it at record offset eight, returns the record
in EAX and ends with `ret 4`. Its retained complete comparison already passes.
The wrapper witness follows the returned record into its saved register,
records the manager argument at `+0x24`, and passes the record and immediate
priority to tick registration `0x00401300` or draw registration `0x004013B0`.
For the three direct callback-field stores, the original allocation and record
register are checked before the same registry call. Ordinary call continuations
are recorded without granting callee credit.

Ascii callback 2 consists of one complete five-byte jump to `0x00408EF0`.
The destination is derived from that original instruction, then reviewed as a
separate complete 187-byte owner. It was absent from the initial reference
discovery index because its original caller had no inventory row yet. Its
calling convention remains unspecified in the inventory: the incoming object
is in ECX, but this alone does not distinguish thiscall from fastcall.

For every owner, traversal follows all conditional branches, fallthroughs,
returns and tail transfers. The resulting instruction coverage must be dense,
nonoverlapping and confined to the independently established original entry
region. Outgoing direct calls and tails require another original entry. All
bytes between the complete scope and the next independent entry must be INT3
padding. Unknown indirect jumps are rejected. The 55-byte Enemy, 51-byte
GameThread and 82-byte Player wrappers retain their complete tests, alternate
paths and return handling; none is reduced to an apparent jump stub.

## Ascii device calls

The two larger Ascii owners include four individually reviewed device calls:

| Owner | Call instruction | Complete encoded instruction | Receiver / slot |
| --- | --- | --- | --- |
| callback 3 | `0x004080DC` | `ff96bc000000` | device at `0x004C10D8`, `+0xBC` |
| callback 3 | `0x00408121` | `ff96bc000000` | same device and slot |
| group-1 drawing | `0x00408F1C` | `ff96bc000000` | same device and slot |
| group-1 drawing | `0x00408F93` | `ff92bc000000` | same device and slot |

Each is a virtual CALL with an ordinary continuation, rather than an indirect
jump. Full receiver loads, viewport arguments, camera selection/restoration,
VM flags, sprite flushes and return-value handling remain within their owners.
The verifier uses exact original call sites and instruction bytes; this does
not authorize other virtual calls or bind a static device method address.

## Ordinary UpdateFunc constructor experiment

At this checkpoint the shared constructor wrote through a volatile copy of
`this` to retain otherwise overwritten initialization stores. Its original
source spelling remains unproved. The later
shared constructor reconstruction
narrows existing volatile accesses and uses ordinary callback member initializers,
closing the complete AnmManager owner. The earlier experiment below instead
removed that qualification and moved the ordinary constructor body from the
header into `UpdateFunc.cpp`.
Fields, masks, order and layouts were otherwise retained. The pinned compiler
and link profiles were unchanged, and the existing build graph was rebuilt
incrementally. The complete build succeeded.

This source-placement hypothesis does not reproduce the original. Eight
complete linked owners change extent:

| Owner | Baseline bytes | Ordinary constructor bytes |
| --- | ---: | ---: |
| `UpdateFuncRegistry::create_func` | 106 | 77 |
| `EffectManager::initialize` | 241 | 212 |
| `Ending::initialize` | 593 | 570 |
| `EnemyManager::initialize` | 459 | 430 |
| `Gui::initialize` | 258 | 229 |
| `HelpManual::initialize` | 243 | 214 |
| `ReplayManager::initialize` | 1309 | 1193 |
| `AnmManager::AnmManager` | 5071 | 4046 |

All candidate PDB owners were inspected, not a shortened instruction interval.
The ordinary constructor no longer has a retained standalone linked owner.
Redundant initialization writes disappear from the affected callers. The
AnmManager EH profile correctly refuses the changed complete parent extent;
the diagnostic build receives no strict acceptance credit. This trial rules
out source placement alone, not every ordinary C++ source or compiler context.
Do not replace the missing evidence with barriers, call-site special cases,
dead locals, forced instruction ordering or relaxed owner checks.

The trial sources and all five linked output/receipt files are preserved in
`.analysis/updatefunc-ordinary-out-of-line-artifacts/`. The baseline counterparts
are preserved in `.analysis/updatefunc-context-baseline/`. After restoring both
original source files, the complete source-input identity and every baseline
artifact hash were verified before restoring those attested outputs. The build
receipt is identical to the baseline incremental receipt; no new clean build
is claimed. Trial object/dependency caches remain intact. Their 104 affected
stamps will invalidate normally on the next incremental build; no cleanup or
forced cache reuse is needed. See `.analysis/updatefunc-context-restore-check.json`.

## Results and retained evidence

The full replay reports **730 exact, 53 mismatch and 432 incomplete**, totaling
117,912 exact primary bytes among 1215 annotated candidates. All 709 exact
results at `f89675d` remain exact. All 762 previous comparison units are
identical, alongside 21 new complete units. Missing original boundaries fall
from 56 to 35. Twenty roots from the preceding discovery index are reviewed;
13 referenced roots and 22 roots without an indexed witness remain unreviewed.
The Ascii drawing helper is the additional newly discovered entry.

All 17 relevant strict-Oracle and focused-audit controls pass. The comparison
engine, binding rules and compiler profile are unchanged. Maintained source is
identical to the baseline; the trial produces reusable negative evidence.
The AnmManager constructor remains the complete 5,054/5,071-byte mismatch.

Retained ignored evidence:

- `.analysis/review-manager-wrapper-scopes.py` and
  `.analysis/reviewed-manager-wrapper-scopes.json`: original-only reproducer,
  full parent bytes, witness paths, registrations, complete owner bytes,
  disassembly, hashes, exits and padding.
- `.analysis/manager-wrapper-original-review.log` and
  `.analysis/manager-wrapper-focused.json`: scope review and all 21 passes.
- `.analysis/manager-wrapper-full-audit.log` and
  `.analysis/manager-wrapper-regression-check.json`: full replay and retained
  results/units.
- `.analysis/manager-wrapper-{oracle,focused}-controls.log`: passing controls.
- `.analysis/updatefunc-ordinary-out-of-line-build.log`,
  `.analysis/updatefunc-ordinary-out-of-line-extents.json` and
  `.analysis/updatefunc-ordinary-out-of-line-owner-differences.json`: successful
  diagnostic build and complete linked owner observations.

Source-origin rows remain unknown/review, implemented entries remain absent,
and Factory acceptance remains unsubmitted. Nothing is published.
