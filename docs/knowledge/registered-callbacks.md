# Registered callbacks and reachable original entries

Reviewed 2026-11-11 against the canonical Japanese v1.00a target. This review
continues the [manager callback investigation](manager-callbacks.md) from
`b32d469`. It establishes 27 missing original function scopes: 24 remaining
registered roots, one additional HelpManual worker, and two Replay callback
bodies. Candidate artifacts, sizes and matching labels are not inputs to the
original scope derivation. Source names below identify corresponding candidates;
original registration instructions establish the entries independently.

## Entry and complete-scope evidence

Update registration uses `create_func` at `0x00401730`, tick registration at
`0x00401300` and draw registration at `0x004013B0`. The callback argument is
stored at `UpdateFunc +0x24`; Supervisor stores its fixed singleton address
`0x004C10D0`. Inlined allocations store the callback at `+8` and clear the
registration and cleanup callbacks at `+0xC` and `+0x10` before registration.

| Candidate name | Original complete range | Bytes | Original entry witness |
| --- | --- | ---: | --- |
| `BombInf::on_tick_callback` | `0x40da60..0x40da64` | 5 | `0x40d600` at `0x40d606` |
| `Spellcard::on_tick_callback` | `0x417ee0..0x417ee4` | 5 | `0x417700` at `0x417702` |
| `Spellcard::on_draw_callback` | `0x417ef0..0x417ef4` | 5 | `0x417700` at `0x41771f` |
| `GameThread::thread_start_callback` | `0x42d1f0..0x42d1f4` | 5 | `0x42d700` at `0x42d75d` |
| `help_manual_load_anm` | `0x42e760..0x42e7b1` | 82 | `0x42e810` at `0x42e8a9` |
| `help_manual_read_file` | `0x42e7c0..0x42e802` | 67 | `0x42eab0` at `0x42ee08` |
| `HelpManual::on_tick_callback` | `0x42ef90..0x42ef94` | 5 | `0x42e810` at `0x42e816` |
| `HelpManual::on_draw_callback` | `0x42efa0..0x42efa5` | 6 | `0x42e810` at `0x42e882` |
| `LaserManager::on_draw_callback` | `0x431720..0x431750` | 49 | `0x431330` at `0x43137f` |
| `LoadingThread::on_tick_thunk` | `0x43b3b0..0x43b3b4` | 5 | `0x43af60` at `0x43af62` |
| `LoadingThread::on_draw_thunk` | `0x43b3c0..0x43b3c4` | 5 | `0x43af60` at `0x43af7f` |
| `Supervisor::on_draw_2c` | `0x43d640..0x43d6e6` | 167 | `0x43ba40` at `0x43bb38` |
| `Supervisor::on_draw_39` | `0x43d7c0..0x43d81d` | 94 | `0x43ba40` at `0x43bb72` |
| `Supervisor::on_draw_38` | `0x43d820..0x43d869` | 74 | `0x43ba40` at `0x43bb55` |
| `Supervisor::on_draw_55` | `0x43d870..0x43d8a8` | 57 | `0x43ba40` at `0x43bb8f` |
| `PauseMenu::on_tick_thunk` | `0x43e720..0x43e724` | 5 | `0x43e3f0` at `0x43e3f2` |
| `PauseMenu::on_draw_thunk` | `0x43ef10..0x43ef14` | 5 | `0x43e3f0` at `0x43e40f` |
| `ReplayManager::on_tick_record` | `0x447fd0..0x448120` | 337 | `0x448e20` at `0x448e20` |
| `ReplayManager::on_tick_playback` | `0x448130..0x4482e9` | 442 | `0x448e30` at `0x448e30` |
| `ReplayManager::on_tick_record_thunk` | `0x448e20..0x448e24` | 5 | `0x447760` at `0x44798e` |
| `ReplayManager::on_tick_playback_thunk` | `0x448e30..0x448e34` | 5 | `0x447760` at `0x447b98` |
| `ReplayManager::on_tick_fast_forward` | `0x448e40..0x448e82` | 67 | `0x447760` at `0x447a03`; `0x447760` at `0x447c02` |
| `ReplayManager::on_draw_fps` | `0x448e90..0x448eac` | 29 | `0x447760` at `0x447a7b`; `0x447760` at `0x447c28` |
| `PopupManager::on_tick_thunk` | `0x44a440..0x44a444` | 5 | `0x449cd0` at `0x449ce0` |
| `PopupManager::on_draw_thunk` | `0x44a450..0x44a454` | 5 | `0x449cd0` at `0x449cfe` |
| `TitleInf::thread_start` | `0x44abc0..0x44ac6c` | 173 | `0x44aee0` at `0x44af19`; `0x44aee0` at `0x44af24` |
| `ScreenEffect::on_tick_fade_out` | `0x45c900..0x45c983` | 132 | `0x40c0d0` at `0x40c0fd`; `0x42d7b0` at `0x42d817` |

The `0x0042D1F0`, `0x0042E760` and `0x0042E7C0` roots are passed to
`Supervisor::start_thread` at `0x0043C5B0`. The Title root at `0x0044ABC0` is
both stored at object offset `+0x18` and passed to the thread runtime at
`0x0047952B`. The Replay initializer registers `0x00448E20` and `0x00448E30`;
their complete bodies are unconditional five-byte jumps to `0x00447FD0` and
`0x00448130`, establishing the two otherwise uninventoried body entries.

Tick/draw priorities are `0x1E/0x0C` for Spellcard, `0x0B/0x48` for HelpManual,
`0x03/0x44` for LoadingThread, `0x0A/0x4A` for PauseMenu and `0x14/0x2F` for
PopupManager. Laser draw uses `0x23`; Supervisor draw uses `0x2C`, `0x39`,
`0x38` and `0x55` at the corresponding named entries. Replay record/playback
uses tick priority `0x10`, fast forward uses `0x22`, and FPS draw uses `0x47`.
Fade-out registration uses tick priority `0x13` in both original callers.
Bomb tick priority is the initializer argument plus `0x18`.

Every reachable instruction is decoded from its original root. Conditional
branches and fallthroughs are followed to all returns or reviewed tail
destinations. The resulting intervals contain no holes, overlapping instructions
or branch destinations inside instructions. No scope overlaps an existing
inventory owner. Every gap to the next independent original entry consists
entirely of INT3 bytes. All roots under review are excluded from the input
boundary ledger, so re-running the derivation cannot use their declared sizes
as its own proof. The reproducer checks those declared rows only after deriving
the complete ranges again.

The HelpManual load worker initially failed the padding check: a second body
begins at `0x0042E7C0`. Its independent thread registration is present in the
already inventoried `0x0042EAB0` body at `0x0042EE08`. Reviewing that worker
closes the gap without truncating or absorbing it into the load worker. The
Replay record and playback bodies are separately reviewed before accepting
the wrapper tail destinations.

## Indirect calls and behavior

Ten original call instructions use virtual or imported targets. Their exact
sites and operand bytes are recorded; all have ordinary fallthrough
continuations. No indirect jump is accepted by this scope proof.

| Sites | Original receiver and slot |
| --- | --- |
| `0x00431741` | Laser object vtable slot `+0x14`, in the linked-list draw loop |
| `0x0043D65C`, `0x0043D66E`, `0x0043D69E`, `0x0043D6DB`, `0x0043D7D5`, `0x0043D812` | Device at `0x004C10D8`, vtable slot `+0xE4` |
| `0x0043D83B`, `0x0043D85E` | Same device, vtable slots `+0x94` and `+0xAC` |
| `0x0044AC0E` | ESI loaded from IAT `0x0048B0A0`, independently identified as `KERNEL32.dll!Sleep` by the original PE import table |

These call operands do not establish static callee ownership or add exact
credit for any callee. The strict candidate replay still checks the complete
owners and every encoded field under its unchanged rules.

The Laser callback skips loading and visits each noncancelled laser, saving
its next pointer before dispatch. HelpManual load/read workers update the
global manual object and publish thread-completion state. Replay playback
includes the negative-frame path, end marker, normal input restoration, FPS
cursor advancement and every return. Fast forward checks game/loading/mode
and held-input conditions before returning one or six. FPS draw skips loading
and otherwise tail-transfers to the existing draw body. Title startup includes
its initialization failure path, sleep loop, cleanup and final state publish.
Fade-out includes both alpha clamps, all exits and its conditional timer step.

## Original payload identities

Complete scope SHA-256 values, excluding the independently checked INT3 gaps:

```text
0040DA60   5 339a3db5717c3887bd2452c4028dc6814211165a63a0599ed367a6074dc70904
00417EE0   5 5b28dee2ad2a99243faaad068bc68422c963319c14c5a17b220b8e599b057c21
00417EF0   5 eb72e10f67211e5f72d92e31162c41f3df54056a9e5c05187a44cb2f1ca45f08
0042D1F0   5 fd6f727337b0d30127b6baa9606fcb6c43ba58761a911f3c945c5732f401928b
0042E760  82 2686545a46b529405e8ba90cc8fd4ab1514a4023605d536c447d43cda859dc6c
0042E7C0  67 b47af02d462e6475afc6455bdebccd8fb7ac8cd5137087bdb68d3417b71bad66
0042EF90   5 7b58fd031198ae1848386614cd09046ecddce3dbe9095903a55b1658deb9de64
0042EFA0   6 2db31f4e09597946e56e859813bfdad7046d457c32332c3a882654d1e3ffdf67
00431720  49 2f2ef2ab48a2d2874b2c081901621193c934664eac99b6bbf0fb375e330404e8
0043B3B0   5 412279360b9430cc27040cf0fe92f68f519fe505107253bb184a6441ece3f15b
0043B3C0   5 0873af1117bd7228ee29e0b904b306310d0b12e225a6dd1bb9836b1a2e9ddb6c
0043D640 167 d49ed1b6204249a71b1e47d67b3b63c90a57f8c8de81c2b4ed54ca316c3afeb9
0043D7C0  94 6516c2de7b8d7c2c08e202e8053fd87913c5033c117833e372266ee7e177a4d4
0043D820  74 7a5f4da22848fef85db1147d7a20d808106904936a0feec6c6e4ccfccc7935aa
0043D870  57 d6f72e4dc1468deaa76a394c2ca516b38dcdde51a12c142eb2b236a312a0e215
0043E720   5 c725f1ffc4866dc8e56464e46807229df68ddc4f8841e92cc1332f3533a4c976
0043EF10   5 e1e3fe15f117a2c2ac11edf9a6664f6954b8a253b8434d780e99ac4b2955309f
00447FD0 337 d086815c80d38e074379be29ffb168071901d234f09250be7c6b3205ad62d827
00448130 442 409e4a818cae53b1e4583fdda924b80fa2e2bbd4df2ea2d9b70ab5b758a5afed
00448E20   5 ce555552bc13600710af56d37813a12c4dae73dd798da506d187123be64d4a00
00448E30   5 2dc59db5b717bede91d4aa5ffa397568ce92f35ab19500f262a24937a06fc5e4
00448E40  67 c8bd5b17566cba8012084d293cc965678bff80c670864201c4cdc9c0d9c29fbb
00448E90  29 66e87aa8ab2c92fe452f8088f2940e4b9279aaa425856819775ce18071acc8e0
0044A440   5 f20391c1ec10cb06eb3ed532411fcc84ac1b08ec60b307f1f8a5af2fe8080ab0
0044A450   5 56987c0876eedb1aedfba724b87416d221e2d7f7561017f4c8d627741b71441b
0044ABC0 173 69de15bc113aa66683fe0d9062facb0e688a12936218eac37204fa4e42a87567
0045C900 132 afd1c7ec873ddf34fbe81cda60537eacc15dc3b8f430eea342de8d76bf403e5d
```

Original registration parents retain their complete bytes and hashes in the
private evidence JSON. The two newly reviewed Replay wrappers are five-byte
parents for their own body-entry witnesses; their original registrations are
also retained. The original Ghidra inventory is preserved without analyzer
mutation. New native-review ledger rows cite this document; origin rows remain
`unknown` and `review`.

## Candidate replay and retained evidence

The initial focused replay passes 26 complete owners, totaling 1,504 bytes.
The 337-byte original Replay record body initially differs in extent from its
298-byte candidate and remains incomplete. Reviewing its boundary grants no
exact credit by itself.

The record candidate contained a `volatile` local explicitly justified as a
stand-in for an unexplained original stack spill. That qualifier has no
recovered semantic basis and is removed, together with its upstream percentage
comment. The ordinary local retains the input-selection and recording logic.
An incremental build produces a complete 281-byte candidate, still different
from the original 337 bytes. This cleanup earns no exact credit and does not
claim better code generation. Recover the original frame alignment and local
lifetime from additional source/type/context evidence instead of restoring
forced stack accesses. All 26 newly reviewed passes remain exact in the focused
replay after this change.

The full replay retains all 642 exact results at `b32d469` and adds those 26
complete owners: **668 exact, 52 mismatch and 495 incomplete**, totaling 116,126
exact primary bytes among 1215 candidates. There are now 97 missing original
boundaries and 113 actual extent differences. The 337-byte record body changes
its refusal category only; its reviewed boundary earns no exact credit.
All 21 relevant build-context, focused-audit and strict-Oracle controls pass.
No Oracle or binding implementation changes in this batch.

- `.analysis/review-registered-callbacks.py`: original-only scope reproducer.
- `.analysis/reviewed-registered-callbacks.json`: all complete original scopes,
  disassembly, exits, call sites, registration parents, hashes and padding.
- `.analysis/registered-callback-baseline-audit.json`: report at `b32d469`.
- `.analysis/registered-callback-focused.json`: first complete focused replay.
- `.analysis/registered-callback-focused.log`: invocation output.
- `.analysis/record-input-cleanup-build.log`: incremental source build.
- `.analysis/registered-callback-cleanup-focused.json`: focused replay after
  removing the unsupported local qualifier.
- `.analysis/record-input-cleanup-disassembly.txt`: complete current record
  candidate disassembly, diagnostic only.
- `.analysis/registered-callback-full-audit.log` and
  `.analysis/registered-callback-regression-check.json`: broad replay and all
  prior exact results retained.
- `.analysis/registered-{build,focused,oracle}-controls.log`: 21 passing controls.

These are local comparison results. Source-origin review and Factory acceptance
remain open; this review submits no acceptance receipt.
