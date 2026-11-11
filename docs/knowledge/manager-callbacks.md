# Manager callback entry and scope review

Reviewed 2026-11-11 against the canonical Japanese v1.00a executable. Seven
existing source candidates lacked original function inventory rows. Their
complete original scopes are now independently established through callback
registration and dense, closed control flow. All seven pass the existing strict
linked-owner replay, adding 234 exact primary bytes. No game source, compiler
profile, comparison field or candidate extent is changed for this review.

## Entry identity

The original initializers register these entries with the update registry.
Each stores the manager as the callback argument. Tick registration calls
`0x00401300`; draw registration calls `0x004013B0`. Except for the inlined
Effect draw allocation, the callback address is passed to `create_func` at
`0x00401730`.

| Original parent | Callback address instruction | Callback | Registry priority |
| --- | --- | --- | --- |
| Bullet initialize, `0x00411A30` | `0x00411A72`, push `0x00412C50` | Bullet tick | Tick `0x1C` |
| Bullet initialize, `0x00411A30` | `0x00411A94`, push `0x00412C80` | Bullet draw | Draw `0x25` |
| Effect initialize, `0x004187D0` | `0x00418818`, push `0x00418AB0` | Effect tick | Tick `0x1F` |
| Effect initialize, `0x004187D0` | `0x00418882`, store `0x00418AE0` at callback offset `+8` | Effect draw | Draw `0x26` |
| Item initialize, `0x0042F260` | `0x0042F262`, push `0x004308F0` | Item tick | Tick `0x1D` |
| Item initialize, `0x0042F260` | `0x0042F27F`, push `0x00430920` | Item draw, layer one | Draw `0x21` |
| Item initialize, `0x0042F260` | `0x0042F29D`, push `0x00430940` | Item draw, layer zero | Draw `0x13` |

The Effect draw initializer builds the `UpdateFunc` directly: callback at `+8`,
null registration/cleanup functions at `+0xC/+0x10`, and manager argument at
`+0x24`, followed by draw registration. This identifies an actual callback
entry even though its body only returns one. The three complete initializer
scopes were already present in the independent inventory and already passed
strict replay before this batch. Their original hashes are:

```text
00411A30 315 8783549ca6e7458c09887cd99a9b6331b28decb714753e5c7b7b9375cd70a81b
004187D0 241 108d83fa22545555ea7667dd2f1fdbee36260ba1789c538b1b3ede505b4f27b0
0042F260 106 27255978ec40843411553f995fee46b3dad63bc01bd752159da5fe9e417751a7
```

## Complete original control flow

Starting only at the registered original addresses, the review follows every
conditional branch and fallthrough to returns or unconditional tail transfers
to independently inventoried function entries. Direct calls require known
original entries. No candidate PE, PDB, MAP or candidate size is read by this
scope derivation. The reachable instructions must cover a dense interval with
no overlapping instructions, branch targets inside instructions or holes. None overlaps
an existing original owner. Bytes between each terminal scope and its next
independent entry are exclusively INT3 alignment, where such a gap exists.

| Callback | Complete range | Bytes | Original behavior |
| --- | --- | ---: | --- |
| Bullet tick | `0x00412C50..0x00412C75` | 38 | Returns one during game-thread flags 0 or 2; otherwise tail-transfers to `0x00412860` |
| Bullet draw | `0x00412C80..0x00412CA0` | 33 | Returns one while loading; otherwise calls `0x00412A60` |
| Effect tick | `0x00418AB0..0x00418ADE` | 47 | Checks all `0x400` VM IDs at manager offset `+0x1C`, clearing IDs whose lookup at `0x0046EFA0` fails |
| Effect draw | `0x00418AE0..0x00418AE5` | 6 | Returns one |
| Item tick | `0x004308F0..0x0043091D` | 46 | Returns one for game-thread flags 0, 2 or 10; otherwise tail-transfers to `0x0042F4E0` |
| Item draw, layer one | `0x00430920..0x0043093F` | 32 | Returns one while loading; otherwise calls `0x004307A0` with layer one |
| Item draw, layer zero | `0x00430940..0x0043095F` | 32 | Returns one while loading; otherwise calls `0x004307A0` with layer zero |

Flag numbers above are bit indices in the word at game-thread offset `+0x88`;
loading is bit two. The Bullet draw callback's push/pop of ECX is included in
its complete scope. The two Item draw functions are immediately adjacent, with
no intervening padding. No first return, alignment boundary or next annotation
is used to truncate a reachable path.

Complete original payload hashes:

```text
00412C50 38 6fb285de7c9f04510ba2982160cd8dfec61ae9c0b35446b479af66a269018abd
00412C80 33 55f248bbe7616e929822a738c0ac1e3988badd061d0b9f6bd504d8ce468abe7d
00418AB0 47 af4f8b62079b5b1122d5d4a2b26ee3dd4a283b3de96ec42f522beba215001aab
00418AE0  6 2db31f4e09597946e56e859813bfdad7046d457c32332c3a882654d1e3ffdf67
004308F0 46 5d6ba941ab3905a70d135ebd7a70870b1f15d44e956beac257c8f9478034fad2
00430920 32 1660e5eafdc48085b1ed9bb361621c5c916d4645aac09710905dbcc5d7cba48a
00430940 32 537102900fb21d7cb7f3d3141c5f2508e6a49c5432c038f5c2913d9d91c8e7c1
```

The original Ghidra inventory has no entries at these seven addresses. A
read-only Ghidra function-context query at `0x004308F0` independently confirms
that it is not a pre-existing analyzer function. The new ledger rows explicitly
cite this native registration/CFG review; they do not claim a new Ghidra export.
Source-origin rows remain `unknown` and `review`.

## Candidate comparison and evidence

After fixing the original scopes, the ordinary Oracle selects each candidate's
unique same-start PDB contribution from its declared source object, requires
the complete extent, enumerates every relocation/call field, replays fixed
symbol identities and compares every byte. All seven original-derived sizes
happen to equal their complete candidate sizes. This agreement is an outcome
of the review, not an input to its scope calculation.

The diagnostic now distinguishes a missing independently reviewed original
boundary from a genuine candidate/target extent difference. Both still refuse
comparison. Two controls exercise this distinction through `Context.compare`;
no acceptance condition is relaxed.

Retained ignored evidence:

- `.analysis/item-callback-context.txt`: original read-only Ghidra query.
- `.analysis/callback-entry-inventory.json`: original registration instruction
  contexts, discovered within previously exact initializers.
- `.analysis/review-manager-callbacks.py` and
  `.analysis/reviewed-manager-callbacks.json`: original-only scope derivation,
  full disassembly, exits, calls, padding and payload hashes.
- `.analysis/manager-callbacks-focused.json`: seven complete strict replays.
- `.analysis/callback-boundary-full-audit.log` and
  `.analysis/callback-boundary-regression-check.json`: broad retained-pass audit.

These are local reconstruction results. Original source authorship and Factory
acceptance remain unproven; no acceptance receipt is submitted by this review.
