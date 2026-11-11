# AnmManager callback registration and complete scopes

Reviewed 2026-11-11 from the `efb48b8` checkpoint against the canonical
Japanese v1.00a target. The original constructor registers 39 draw callbacks
and two tick callbacks. All 41 complete source candidates now pass ordinary
strict owner replay, adding 1,182 exact primary bytes. No game source, compiler
profile, Oracle implementation or comparison field is changed in this batch.

## Original roots and constructor evidence

Original WinMain at `0x00459830` directly calls the constructor at
`0x00459E70`, after allocating `0x1C7FD90` bytes and moving the result to ECX.
The following instructions store the returned object in `0x004C0F48`. The
constructor is the existing independent original entry `0x0046A3A0`, with a
complete 5,071-byte normal body ending at `0x0046B76E`. Its SHA-256 is
`91f810dee2b3445e0e0e8b1dbc9750bc9aeb3ed0fa06e2ad5702ec6e970e9d1f`.

Every constructor instruction is decoded, and every normal branch and
fallthrough is followed from the entry. All decoded bytes are reachable;
none of its four conditional branch sites is an indirect dispatch. All 41
registration witnesses are therefore established instruction starts on
constructor paths, rather than incidental immediate values in data. Calls
have their ordinary continuation in this analysis; exception paths require
the separate EH investigation described below.

Each original registration stores a callback at `UpdateFunc +8`, clears
`+0xC` and `+0x10`, stores the manager argument at `+0x24`, then calls tick
registration `0x00401300` or draw registration `0x004013B0`. The preceding
allocation/registration block contains exactly the priority and record pushes.
The reproducer derives all roots and priorities from these original blocks,
without reading source annotations, candidate PE/PDB/MAP files or candidate
sizes. Current ledger rows for these 41 roots are excluded from its boundary
basis before re-deriving their scopes.

## Complete callback scopes

The review follows all normal paths to returns or independently inventoried
tail destinations. Reachable instructions cover each complete dense interval,
without overlapping instructions, branch targets inside instructions or holes.
No scope overlaps an existing owner or another reviewed root. Every gap to
the next independent entry consists entirely of INT3 alignment bytes.

| Entry | Complete end | Bytes | Priority | Draw layer or tick body | Constructor witness |
| --- | --- | ---: | --- | --- | --- |
| `0046DD90` | `0046DD97` | 8 | `05` | 0 | `0046A7B4` |
| `0046DDA0` | `0046DDA7` | 8 | `07` | 1 | `0046A819` |
| `0046DDB0` | `0046DDB7` | 8 | `09` | 2 | `0046A884` |
| `0046DDC0` | `0046DDC7` | 8 | `0B` | 4 | `0046A8EC` |
| `0046DDD0` | `0046DE51` | 130 | `0A` | 3 | `0046A954` |
| `0046DE60` | `0046DE67` | 8 | `0D` | 5 | `0046A9B5` |
| `0046DE70` | `0046DE77` | 8 | `10` | 6 | `0046AA24` |
| `0046DE80` | `0046DE87` | 8 | `12` | 7 | `0046AA8C` |
| `0046DE90` | `0046DE97` | 8 | `14` | 8 | `0046AAF4` |
| `0046DEA0` | `0046DEA7` | 8 | `15` | 9 | `0046AB5C` |
| `0046DEB0` | `0046DEB7` | 8 | `16` | 10 | `0046ABC4` |
| `0046DEC0` | `0046DEC7` | 8 | `18` | 11 | `0046AC2C` |
| `0046DED0` | `0046DED7` | 8 | `1C` | 13 | `0046ACFC` |
| `0046DEE0` | `0046DEE7` | 8 | `1F` | 14 | `0046AD64` |
| `0046DEF0` | `0046DEF7` | 8 | `20` | 15 | `0046ADCC` |
| `0046DF00` | `0046DF07` | 8 | `22` | 16 | `0046AE34` |
| `0046DF10` | `0046DF17` | 8 | `24` | 17 | `0046AE9C` |
| `0046DF20` | `0046DF27` | 8 | `27` | 18 | `0046AF04` |
| `0046DF30` | `0046DF37` | 8 | `1B` | 12 | `0046AC94` |
| `0046DF40` | `0046DF47` | 8 | `2A` | 19 | `0046AF6C` |
| `0046DF50` | `0046DF57` | 8 | `2E` | 21 | `0046B03C` |
| `0046DF60` | `0046DF67` | 8 | `34` | 22 | `0046B0A4` |
| `0046DF70` | `0046DF77` | 8 | `36` | 23 | `0046B10C` |
| `0046DF80` | `0046DF87` | 8 | `4F` | 30 | `0046B2AC` |
| `0046DF90` | `0046DF97` | 8 | `52` | 31 | `0046B311` |
| `0046DFA0` | `0046DFA7` | 8 | `4D` | 29 | `0046B244` |
| `0046DFB0` | `0046DFB7` | 8 | `3D` | 26 | `0046B174` |
| `0046DFC0` | `0046DFC7` | 8 | `3E` | 27 | `0046B1DC` |
| `0046DFD0` | `0046DFD7` | 8 | `3B` | 25 | `0046B37C` |
| `0046DFE0` | `0046DFE7` | 8 | `3C` | 37 | `0046B51C` |
| `0046DFF0` | `0046DFF7` | 8 | `3F` | 38 | `0046B584` |
| `0046E000` | `0046E007` | 8 | `4E` | 40 | `0046B654` |
| `0046E010` | `0046E017` | 8 | `50` | 41 | `0046B6BC` |
| `0046E020` | `0046E027` | 8 | `53` | 42 | `0046B724` |
| `0046E030` | `0046E0C4` | 149 | `2D` | 20 | `0046AFD4` |
| `0046E0D0` | `0046E17D` | 174 | `3A` | 24 | `0046B3E4` |
| `0046E180` | `0046E205` | 134 | `40` | 28 | `0046B44C` |
| `0046E210` | `0046E2A4` | 149 | `37` | 36 | `0046B4AD` |
| `0046E2B0` | `0046E335` | 134 | `41` | 39 | `0046B5EC` |
| `0046E710` | `0046E73A` | 43 | `21` | World list | `0046A6E4` |
| `0046E740` | `0046E744` | 5 | `09` | UI list | `0046A74C` |

Thirty-three draw callbacks consist of a complete eight-byte push/call/return
owner selecting one layer through `render_layer` at `0x0046E750`. The six
larger draw callbacks include every camera change, conditional state flush,
device call, layer render and restoration. Layers 0 through 31 and 36 through
42 have registered draw entries; this does not invent callbacks for layers
32 through 35.

The world tick callback tests the game-thread flags, including its conditional
early return, before tail-transferring to `0x0046E340`. The UI callback is the
complete five-byte tail transfer to `0x0046E490`. The existing list bodies and
`render_layer` receive no additional credit through these callbacks.

Fifteen individually reviewed virtual calls have ordinary continuations:
eight use the device at `0x004C10D8` through vtable offset `+0xBC` and seven
use the same device through `+0xE4`. Their exact sites, instruction bytes,
receiver chains and following instructions are retained. The scope reproducer
checks an explicit site/operand list; it continues to reject every indirect
jump and every other unreviewed indirect call. This does not bind static
callee ownership or grant device methods exact credit.

The six larger draw entries correspond to camera/state transitions:
`0x0046DDD0` selects camera three and disables fog; `0x0046E030` selects
camera one and disables depth testing; `0x0046E0D0` and `0x0046E210` select
camera two and disable depth testing, with the former also clearing the 2D
camera offset. `0x0046E180` and `0x0046E2B0` render using camera zero, then
restore camera two while preserving the layer-render result.

Complete original scope SHA-256 values:

```text
0046DD90   8 2b5bdc6a3f63c70ea8ec784214d9f5218303980a4e740eae68d49df61b6726a6
0046DDA0   8 0445e837bb2e8354b0a758c476b039cf1ace28d62cdff48361015ebc93e67ee2
0046DDB0   8 f0372aaa7e2e4c70e6a316fce2bfd3c434aa44fc969aa1cdcdbc7d1f8955a54d
0046DDC0   8 32b7ce1660957caddf6ff2c64efacba2da98f1807da5f7595e8ad67c4d50252c
0046DDD0 130 e8d5f883cc0bd9343fd42c4746db11e724715fa34cf70651a2639692818f7b61
0046DE60   8 8fb96e0e12a043b5f19d42594977c922d95c23592de8c149a02feb75956898f2
0046DE70   8 daaa265d81a6d0b5b430c36c274d754bf261f442674cc1417afb23eac9f226c1
0046DE80   8 5da2b9d11bc7141f0a1711adf03ec886630efab2db03f4dc9d341781c645850f
0046DE90   8 d6242d7612d61968c3c2e1807e6628e70eacaa271c4189e50fe801f37965d745
0046DEA0   8 e36deb9b49dd378961776a43865ae225d329309ca4b60110ff80e10d53657324
0046DEB0   8 3d352fe4aa6837581c7adc5f7bf1c12656e6e0c51984cd53bc712053ac441de7
0046DEC0   8 60186861ceb0acb9b15ce9fb34fbeb7a06094b13018edaca679cd48c0766cb95
0046DED0   8 ba2e4789019f531ecd6fefb37fe91b398e6ddbf1ee22259d8732cda10efdc6f0
0046DEE0   8 5625e3bb56583a52df02b3defc249672216c5b8fde3a703e184e8252b632cc7e
0046DEF0   8 f02234bc2eb814d5d1da87e5f61dd547eb37ad0ef58b7d40096903ec101fa15b
0046DF00   8 514813f9bddf7b90b47f5e9ee598c6361203bccbc3fe821f72902f5f00ffad13
0046DF10   8 10b892edd9abb5d7fd84a5a72bb84acca69b113f0c5aff4fba9e8f099fdbff84
0046DF20   8 4cfc4032462b483700df1e3e4bdc2d9c353b61b638c6f5b0b18562b2feda439f
0046DF30   8 8e418b78ae4e141d2b6c91b3e4cbc34b0e9c102724d76ffbfe08e151d3c7f577
0046DF40   8 9881969d12876e6205a40ec8b2efafc02d42b65fdf6a7bd47a1e5ac0f691261b
0046DF50   8 3beccb3e3b38c719dc27c1d4f52628293888137f057587b2a194e4c06ceaf61d
0046DF60   8 cfb948afcabad4c01d536ccaac865d64c7592bdf77225c3349691097ee253af9
0046DF70   8 c7a490baa52ea0bef3ea047e49b87a4e8b31b57a5a3c4d20233d2c2edaf5f8cb
0046DF80   8 91c96e8dc758ce34429858a45f530d12758fcaea33034455ca4b5def1f6eea3a
0046DF90   8 4e981731a1186886e8deaffc2006044fe02d2b0164d0cee477fddb2f7edc636f
0046DFA0   8 c0da6645da2f5f97411115c23cfacbcab123ddd72dec08bd1a371cc5884d05d8
0046DFB0   8 d24600168789b4d5483ff0ce7661d1683092e864bd6c3c9de96ffe4db60c3164
0046DFC0   8 b97af013ed343099760c2ede978a41fc551bd43cfb8b908e00c996a7bd6ea9e1
0046DFD0   8 bd2ad9517174c298ee34678fa55c0d2b052258e61806bf8d8e426ef332c6e02a
0046DFE0   8 05bf5bf3afa8dfc0c94a0f213379854136d79b2d81eb04da764a67d0ba5dc26b
0046DFF0   8 08c0817824f5cabb9c6df572aa16253f5e88234d2e0e1c2a7f7252824fd10f19
0046E000   8 1ff7435218270ebabe7820e05868a8f5fea5b35f3cb07013cab21fc5ffc3bcc2
0046E010   8 f6915f570989b6e03c796825a2f93556b60f1ce2c4b5369e21f6bec28cafb4ac
0046E020   8 db01848d6ff29a77ee693af74fc4933b922911312a2438236ef2355af131d30a
0046E030 149 91274c731b09003b02203b8423cb034c5707154536b8db4f573317ce1fce3724
0046E0D0 174 83c169c0da9916617fd54cf3049e3c88b3e99ab6fe9282ac9ba8969380d69f2f
0046E180 134 828ec20c349679dec736cd825022929b4b830686f07ce79d2a5295e09c09244f
0046E210 149 1021ceb89fc0e709322d90937e8ee4ee0cf576d68ba18932d6553036ba023166
0046E2B0 134 abc0c13ec6f642baf5653346951bca9fe477c574eaa602aee5ee2b146a9bf9f2
0046E710  43 5b9e28a862ebf2f9bdca57800324241e24f2b1b765e1937984660ba4bec7e7ed
0046E740   5 a8842acdd0a1f6c074327d35f1ca76ed2769b864a1d340331c361e1a897f7c70
```

## Constructor EH investigation remains separate

At this callback checkpoint, the constructor lacked one independently accepted
handler binding at parent offset six and received no new exact credit. The
subsequent [complete aggregate review](anm-constructor-eh.md) binds that graph
and establishes a full 5,054/5,071-byte mismatch. The investigation below records
the original evidence that led to that separate profile. Its original GS handler
uses cookie displacement `-0x18` and a nonempty FuncInfo with five unwind
states and flags `0x1`. The default empty-EH3 proof supports neither shape.

Original FuncInfo at `0x0049B654` is 36 bytes followed immediately by a complete
40-byte unwind map at `0x0049B678`. The entries unwind states 0 through 4 to
`-1, 0, 1, 2, 3`. Their actions begin at `0x0048AAA0`, `0x0048AAA8`,
`0x0048AAC6`, `0x0048AAE4` and `0x0048AAF2`; the handler begins at
`0x0048AB0D`. The five complete action scopes are 8, 30, 30, 14 and 27 bytes;
the handler is 27 bytes. Together they form a contiguous 136-byte code bundle.
The metadata graph is a complete 76-byte bundle. Original bundle hashes are:

```text
code 136 5a98fd7a383032180c4bdc87c95fc48e8ffa88dac2cdef8928f1d17193f62ad3
data  76 e3da070b0ed9eb2ce2fc3a7a1d713135264e2b42a71d31b8d2f7a0e0409a2e3c
```

The existing original Ghidra inventory already has all five `Unwind@` action
entries. Every one agrees exactly with its independently derived action scope.
These original subscopes must be reconciled explicitly with any future aggregate
graph proof; they do not establish separate candidate PDB owners.

The candidate PDB independently owns one complete 136-byte code contribution
and one complete 76-byte metadata contribution in `AnmRender.obj`. All five
`__unwindfunclet$` symbols and the handler share the code contribution; the
FuncInfo and unwind-table symbols share the metadata contribution. The handler
is therefore an interior entry, and its 27 bytes cannot be selected as a
standalone complete PDB owner. Supporting this graph required reviewing both
whole contributions, every permitted interior symbol, state transition,
relocation, action destination, parent frame dependency and runtime binding.
Do not reuse the empty-descriptor selector or shorten either owner. The
investigation was diagnostic only; the subsequent binding is documented in
the separate aggregate review linked above.

## Replay and retained evidence

The callback batch's full replay retains all 668 exact results at `efb48b8`,
totaling **709 exact, 52 mismatch and 454 incomplete**, with 117,308 exact primary bytes among 1215
annotated candidates. Missing original boundaries fall from 97 to 56. All 720
prior comparison units remain identical, alongside 41 new complete units.
All 17 relevant focused-audit and strict-Oracle controls pass.

- `.analysis/review-anm-layer-scopes.py` and
  `.analysis/reviewed-anm-layer-scopes.json`: original-only registration and
  complete-scope reproducer, full original bytes, disassembly and hashes.
- `.analysis/anm-layer-boundary-baseline-audit.json`: report at `efb48b8`.
- `.analysis/anm-layer-scope-focused.json`: all 41 complete passes.
- `.analysis/anm-layer-boundary-full-audit.log`: broad replay.
- `.analysis/anm-layer-boundary-regression-check.json`: all prior exact results
  and comparison units retained.
- `.analysis/anm-layer-{focused,oracle}-controls.log`: 17 passing controls.
- `.analysis/anm-constructor-eh-investigation.json`: complete original graph
  bytes, disassembly, state map and candidate aggregate PDB ownership.
- `.analysis/review-anm-constructor-eh.py`: diagnostic graph reproducer; it
  derives the original graph before inspecting candidate contributions.

Original Ghidra analysis is preserved. New ledger rows cite this native review;
source-origin rows remain `unknown` and `review`. These are local reconstruction
results; Factory acceptance remains unsubmitted.
