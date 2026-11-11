# Runtime callback and LZSS entry scopes

The 2026-11-11 original-only review establishes 13 previously missing entries
and replaces one unreviewed Ghidra aggregate with three complete LZSS owners.
All 14 complete annotated owners pass the strict Oracle, adding 1,305 primary
bytes. The checkpoint has 744 exact, 53 mismatch and 418 incomplete candidates,
with 119,217 exact primary bytes. The 730 previous exact results remain exact.

## Entry witnesses

Candidate annotations supply the names below after the original scope review.
They do not supply original entry roles, sizes or boundaries.

| Original entry | Complete bytes | Role | Original witness |
| --- | ---: | --- | --- |
| `0x0041A310` | 77 | Ending animation worker | `EndingScriptVm::run`, push at `0x0041A21A` |
| `0x004492E0` | 53 | ReplayStageData constructor | `ReplayManager::create`, push at `0x00447E5E` |
| `0x00449320` | 41 | ReplayStageData destructor | `ReplayManager::~ReplayManager`, push at `0x00447DF1` |
| `0x00451740` | 8 | Replay-list worker | `TitleInf::do_replay_menu`, push at `0x00451844` |
| `0x00457690` | 9 | ArcfileEntry constructor | `Arcfile::parse_directory`, push at `0x0045751F` |
| `0x00458370` | 84 | LZSS deletion root | compressor call at `0x00457DD8` |
| `0x004583D0` | 83 | LZSS contraction helper | deletion tail transfer at `0x00458393` |
| `0x00458430` | 121 | LZSS replacement helper | deletion tail transfer at `0x004583BD` |
| `0x0045C630` | 90 | ScreenEffect fade-in tick | `Stage::on_draw_03`, push at `0x0040A1E0` |
| `0x0045C9E0` | 214 | ScreenEffect flash tick | initializer push at `0x0045D24D` |
| `0x0045CAC0` | 131 | ScreenEffect hold tick | initializer push at `0x0045D28F` |
| `0x0045CBD0` | 231 | ScreenEffect pulse tick | initializer push at `0x0045D224` |
| `0x0045D4D0` | 57 | Sound initialization worker | WinMain push at `0x00459E2A` |
| `0x0045D7E0` | 106 | Sound-file loading worker | supervisor push at `0x0043B56B` |

Every witness has a recorded trap-free instruction path from its original
parent entry. Paths follow direct branch edges and ordinary call continuations;
they do not prove execution of callees or exactness of the parent.

Three parents reach witnesses through bounded switches. Their original guards,
dispatch operands, tables and every case destination are retained separately:
Ending compares ECX with 17 and uses 18 slots at `0x0041A2C0`; the replay menu
compares EAX with 5 and uses six slots at `0x00451D34`; the effect initializer
compares EBX with 9 and uses ten slots at `0x0045D338`. Each unsigned `ja`
precedes its dispatch without changing the index. Every slot targets a decoded
parent instruction start, and no direct branch bypasses the guard into the
dispatch sequence. These tables establish witness paths only. This review does
not accept complete switch ownership or exact parent comparisons for them.

### Thread entry roles

The original PE import directory identifies `0x0048B0E4` as
`KERNEL32.dll!CreateThread`. The two sound witnesses each push all six arguments:
null security and stack size, the worker, `0x004D9E10` as its argument, zero
flags and a thread-ID pointer. WinMain uses `0x004DF48C`; the supervisor uses
its local at EBP-4. The resulting handles are stored separately.

The Ending and replay-list workers go through the complete 61-byte original
ThreadInf wrapper at `0x00402FB0`. It forwards its function and parameter to
the CRT entry at `0x0047952B`. The complete 133-byte entry and 73-byte context
allocator at `0x00479456` show the function stored at context+0, its parameter
at +4, and the context passed to CreateThread with entry `0x0047934B`. That
entry's recorded prefix reaches a call through the stored function after
pushing the stored parameter. Only the entry-to-call prefix is claimed there;
it is not a complete runtime owner or a new runtime exact result.

The two sound worker bodies call Sleep through ESI. Their exact receiver loads
at `0x0045D4EA` and `0x0045D816` read the independently parsed Sleep import at
`0x0048B0A0`; the calls at `0x0045D4F2` and `0x0045D822` each push 1. Their
loops retain the receiver and return normally when the state changes. These
specific indirect calls have ordinary continuations. No indirect jump is
allowed in any of the 14 complete owners.

### Array and registry roles

The complete original vector constructor iterator at `0x00474CA8` calls its
fourth argument with ECX pointing to an element, advances by its second
argument and repeats for the third. The replay allocation passes constructor
`0x004492E0`, eight elements of stride `0x28`, and the base at manager+`0xC4`.
The archive allocation passes constructor `0x00457690`, its dynamic ESI count,
stride `0x10` and the first element after the array count cookie.

The replay destructor witness independently passes `0x00449320`, count 8,
stride `0x28` and manager+`0xC4` to the complete original destructor iterator
at `0x00474D11`. That iterator moves backwards by the stride and calls its
fourth argument with ECX pointing to each element. Constructor exception
cleanup arguments do not substitute for this independent destruction witness.
The runtime iterators receive no new exact-code credit.

All four effect callbacks pass through the original 106-byte record factory
at `0x00401730`, then the tick registry at `0x00401300` with priority `0x13`.
The returned record remains in ESI and receives its manager argument at +`0x24`.
The review retains the complete factory and each registration sequence.

## Complete LZSS region partition

The initial Ghidra row at `0x00458370` spanned 313 bytes through `0x004584A8`.
Its entry returns at `0x004583C3`, or restores its saved registers and tail
transfers to the contraction/replacement helpers. A second contraction tail
transfer at `0x004583A3` is retained. Both helper entries start after INT3
padding, have independent dense control-flow graphs and return on every path.
The replacement root restores the parent/child links for both subtrees.

| Region | Bytes | Meaning |
| --- | ---: | --- |
| `0x00458370..0x004583C3` | 84 | deletion root |
| `0x004583C4..0x004583CF` | 12 | INT3 padding |
| `0x004583D0..0x00458422` | 83 | contraction helper |
| `0x00458423..0x0045842F` | 13 | INT3 padding |
| `0x00458430..0x004584A8` | 121 | replacement helper |

All 313 original bytes are accounted for. No candidate extent defines this
partition. Each complete owner is compared separately; the original aggregate
has not been retained as an overlapping owner or a partial comparison.

## Validation and retained evidence

The original-only reproducer excludes all selected roots from its inventory
boundary basis before deriving them. It reads the canonical original PE and
original inventory, with the fixed target hash, and no candidate artifacts.
Each owner requires a dense, nonoverlapping graph, reviewed external transfer
destinations, every return and call, no competing owner, and only INT3 bytes
between its end and the next independently established entry. Complete bytes,
hashes, disassembly, calls, exits, paths and padding are retained.

The focused audit passes all 14 owners. Full replay retains all 783 previous
comparison units unchanged and adds 14 units, for 797 complete units. All
730 previous exact results remain exact. Relevant strict Oracle and focused
audit controls pass. Game source, compiler profile, Oracle implementation,
binding rules and attested build outputs are unchanged; no rebuild is needed.
The preserved trial caches described in NEXT_AGENT.md still invalidate normally
on the next incremental source build.

Retained ignored evidence:

- `.analysis/review-runtime-entry-scopes.py` and
  `.analysis/reviewed-runtime-entry-scopes.json`: original-only derivation.
- `.analysis/runtime-entry-original-review.log` and
  `.analysis/runtime-entry-focused.json`: original review and focused passes.
- `.analysis/runtime-entry-full-audit.log` and
  `.analysis/runtime-entry-regression-check.json`: full replay and retained units.
- `.analysis/runtime-entry-{oracle,focused}-controls.log`: passing controls.
- `.analysis/runtime-entry-baseline/`: preceding report, units and inventories.

The 74 roots in the earlier missing-entry reference discovery now have reviewed
entry scopes. Twenty-two annotated entries still lack independent original
boundaries and need fresh entry witnesses, including table-based callbacks.
The new `.analysis/missing-entry-pointer-discovery.json` records 21 original
`.rdata` byte occurrences as discovery locators; their table types, counts and
dispatch roles remain unreviewed. Camera has no such occurrence. The original
PE has no base-relocation directory, so these are not relocation witnesses.
Source-origin review remains open and Factory acceptance remains unsubmitted.
