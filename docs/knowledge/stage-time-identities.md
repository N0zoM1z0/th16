# Complete stage-table and current-time identities

## Result

Two independent bindings resolve four existing whole candidates:

| Original entry | Candidate | Complete primary bytes |
| --- | --- | ---: |
| `0x0042E150` | stage_clear | 896 |
| `0x0043CE10` | Supervisor::switch_gamemodes | 815 |
| `0x0043E250` | ScorefileChara::insert_score | 246 |
| `0x004483B0` | ReplayManager::set_end_stage | 78 |

These add **2,035 exact primary bytes**. Full replay reports **809 exact,
61 mismatch and 345 incomplete**, covering 141,487 exact primary bytes. All
805 preceding exact results and all 866 previous comparison units remain
identical; four new complete units give 870 total. No game source, build profile
or artifact changes occur. The table and runtime identity checks receive no
separate primary exact credit. Source-origin review remains open and Factory
acceptance remains unsubmitted.

## Original stage table

The complete table starts at `0x004A22D0`, covers 1,696 bytes and has eight
212-byte rows. An original-only scan of initialized writable data finds one
complete table with stage numbers 0 through 7, STD/ECL/dialogue/logo file roles
and paired music IDs. The first row is the test stage; it uses `st00.ecl` and
`st00a.msg`, with the other file roles shared with stage one. Each row includes
nine string pointers, two music IDs, one unused word and four complete 40-byte
boss records. All 352 scalar DWORDs and 72 complete string pointees are retained
in `.analysis/stage-time-original-identities.json`. The table hash is
`56a416a4dea17b011b0e709cbf78aed0dca7cf04455c22c41da3c1bffc7f62ce`.

The independent original indexed use at `0x0043CFD3` multiplies the stage
number by `0xD4`; the adjacent ADD at `0x0043CFD9` adds the table base. Two more
Supervisor paths and stage_clear use the same stride/base. This corroborates
the data-derived identity rather than choosing a destination from a compared
operand. The reproducer `.analysis/review-stage-time-originals.py` reads no
candidate artifacts or consumer comparison results.

The existing candidate has a complete 1,696-byte typed `g_stage_table` PDB
global and one same-start data contribution from
`obj/probes/reference-support/Opaque.obj`. Its whole initialization matches
the original after checking each pointer against its complete original string.
The strings each have one complete same-start NUL-terminated PDB contribution
in read-only storage. Every other table byte compares directly. All 72 pointer
slots require candidate PE relocations; missing, extra or crossing relocations
are refused. The whole table must lie in initialized writable non-executable
storage, and every pointee in initialized read-only non-executable storage.

`stage-table-v1` is a dedicated explicit linkage profile for this complete
symbol, size, source producer, original hash and indexed witness. It is not a
generic mutable-data fallback. The imported table remains in its existing
non-LTCG support context; this review neither removes that context hypothesis
nor claims source-origin acceptance. Raw replay and field normalization are
unchanged.

## Original current-time entry

The root at `0x0047A09E` has a complete 66-byte body ending at `0x0047A0DF`.
It zeroes a local time structure, requests time base 1 from the 127-byte child
at `0x0047A01F`, and returns its seconds in EDX:EAX. On failure it returns
64-bit minus one. If the optional first argument is non-null, it writes both
32-bit words there. All branches target owned instruction starts and every
path remains inside this complete root.

The child obtains Windows file time through the complete 86-byte wrapper at
`0x0047DD44`. Its fallback calls the original PE import
`KERNEL32!GetSystemTimeAsFileTime` through slot `0x0048B1AC`. The conversion
subtracts `0x019DB1DED53E8000`, divides by 10,000,000 and stores a 64-bit seconds
value and nanosecond remainder. It validates the requested base and supported
time range. The original Ghidra names corroborate the ABI; the conversion,
return width and optional output store establish the identity independently
of those labels and consumer comparisons.

The pinned SDK UCRT candidate public `__time64` has a complete 66-byte
`time.obj` contribution owned by `libucrt.lib`. The existing runtime profile
checks both full extents, the original payload hash and the pinned library
path. Internal conversion/wrapper helpers receive no inferred candidate
bindings. Original root, child and wrapper bytes/instructions are retained in
`.analysis/stage-time-original-identities.json`.

The new complete score/replay consumer scopes also have independent original
checks: dense reachable CFGs, all branch targets, terminal returns, ten/two
following INT3 bytes and original inbound calls at `0x0043F877` and
`0x004406B1`. See `.analysis/stage-time-consumer-scopes.json` and its
original-only reproducer `.analysis/review-stage-time-consumer-scopes.py`.
The other two consumers already have complete original switch profiles.

## Remaining refusals

PauseMenu::tick_open now passes linkage binding but fails its original case
mapping. Both full owners are 4,676 bytes. Four slots in its first table differ:

| Slot | Original case offset | Candidate case offset |
| ---: | ---: | ---: |
| 7 | 1,392 | 1,420 |
| 9 | 1,392 | 1,420 |
| 10 | 1,982 | 1,988 |
| 11 | 3,207 | 3,206 |

The second table retains all five case offsets. Complete bytes and both maps
are saved in `.analysis/pause-open-case-layout.json`. No case offset, table
scope or relocation addend is changed to hide the layout difference.

Six menu candidates now expose whole-extent refusals after binding their table
fields. TitleInf::on_tick still lacks one independent field. These entries
receive no exact credit; the full reason changes are retained in
`.analysis/stage-time-regression-check.json`.

## Validation

All **207 controls across nine suites** pass. Twenty stage/time controls cover
every scalar DWORD on both sides, every pointer relocation, every distinct
candidate string byte and terminator, complete typed/source PDB ownership,
partial/extra/crossing extents, writable pointees, the indexed witness, whole
original hash, both runtime extents and pinned UCRT ownership. They also replay
both complete stage consumers. The preceding 187 controls remain unchanged.

Evidence includes `.analysis/stage-time-full-audit.log`,
`.analysis/stage-time-regression-check.json` and
`.analysis/stage-time-<suite>-controls.log`, matching `scripts/test-<suite>.py`.
The preceding report, units, inventory and bindings are preserved in
`.analysis/stage-time-baseline/`. Build input/artifact identities remain equal
to that checkpoint. No rebuild, cleanup, Factory deployment or publication
occurs.
