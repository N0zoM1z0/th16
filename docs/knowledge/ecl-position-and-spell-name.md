# ECL position setup and spell-name decoding

This source investigation starts at `8eb77c0`, with 885 exact owners. It retains
changes in the large `EnemyData::ecl_run_over_300` dispatcher at `0x0041dcb0`.
The function remains incomplete. No Oracle implementation, comparison profile,
binding or accepted scope is changed. Preserve `.analysis/ecl-dispatch-work/`.

## Retained source

Position interpolation instructions 401/403/436/437 and per-axis curve
instructions 434/435/438/439 now share their initial/goal/timer setup. The
original curve handler jumps to `0x0041eb98`, inside the ordinary position
handler's common finish. The previous candidate duplicated that finish.
Both instruction families now prepare the same live position, interpolator and
coordinate variables, then use one initialization path. The offset calculation
starts with the origin's X component before adding or subtracting the offset.
The early nonpositive-time exits and both mode-setting sequences remain intact.

Spell instructions 522/528/537/538/539 now advance a destination pointer while
counting decoded bytes forward. This recovers the original loop's pointer
displacement and increasing counter shape. The source pointer remains indexed;
advancing both pointers instead produces a countdown loop absent from the
original. Registers, frame slots and the surrounding argument scheduling still
differ. The stream starts with key `0x77` and increment 7, increasing that
increment by `0x10` after each byte, with byte-width wraparound.

The integer and float difficulty selectors, instructions 535/536, now retain
separate explicit Lunatic and default branches. This restores both original
four-entry jump tables. Combining those source labels generated branch chains
and omitted both tables. Defaults still select the Lunatic value, including
Extra and negative difficulty values; no gameplay behavior is changed here.

These are natural source changes to substantial instruction handling. No dead
locals, alignment directives, register assignments, padding or byte masks were
introduced to force a match.

## Whole diagnostic scope

The original's unsigned bound covers 702 opcode positions, 300 through 1001.
Its byte map selects 174 main target slots. The two nested difficulty switches
add eight more slots. All 182 entries point to decoded instruction starts, and
every main selector occurs in the complete byte map. Original and retained
candidate both have three guarded indirect jumps, with no direct edge entering
their protected guard/dispatch interiors. Their main selector maps agree. The
diagnostic packets retain code, all table/map storage, SHA-256 hashes and
relocation lists.

| Image or source form | Code bytes | Target slots | Map bytes | Alignment | Total bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original | 19,976 | 182 / 728 bytes | 702 | 2 | 21,408 |
| Starting candidate | 20,188 | 174 / 696 bytes | 702 | 0 | 21,586 |
| Shared position finish | 19,980 | 174 / 696 bytes | 702 | 0 | 21,378 |
| Finish and destination traversal | 19,964 | 174 / 696 bytes | 702 | 0 | 21,362 |
| Retained source with difficulty switches | 19,952 | 182 / 728 bytes | 702 | 2 | 21,384 |

The target table is at `0x00422ab8`, followed by the map at `0x00422d70`.
The nested tables are at `0x00423030` and `0x00423040`, after the complete map
and a two-byte `66 90` alignment instruction. The diagnostic ends at the next
independent function at `0x00423050`. The retained candidate packet agrees with
its complete PDB procedure extent. It has 379 base relocations in the packet,
including all 182 target-table entries; the original image supplies none. Case
slices are spatial diagnostic aids, not independent function owners or exact-credit units.
The 24-byte total difference does not describe the amount of remaining
incorrect code: different block sizes can cancel. The candidate frame remains
`0x490` against the original's `0x478`; register lifetimes and block layout
still differ.

An early packet stopped after the main map and reported 21,374 target bytes.
An exhaustive indirect-jump census rejected its assumed single dispatch and
found the two omitted tables. That packet is incomplete; keep its warning in
`final-scope/INCOMPLETE-SCOPE.txt` and use `complete-scope/`. The initial padding
check also refused the legitimate multibyte NOP; it now decodes padding fully.
No accepted owner or exact credit was based on either incomplete diagnostic.

The strict audit still reports the dispatcher incomplete. Unresolved fields
and incidental operands decoded from owned data are not acceptance evidence.
Unreviewed destinations include the EH handler, six references
to the zero-vector components, the private sin/cos helper and the `BossDead`
literal. They are not bound from convenient operands in this comparison.

The existing dispatch proof refuses the original remap/store/jump sequence:
after the byte remap, a ten-byte instruction stores `0x88` to frame slot
`EBP-0x438` before dispatch. The existing proof requires adjacency. The actual
refusal is retained in `scope-profile-refusal.json`; no acceptance rule is
relaxed to bypass it. Complete formal scope review, these identities and source
differences remain open.

## Complete native movement calls

A historical-compiler layout probe checks the Win32 enemy, ECL context,
interpolator, instruction and Globals offsets against actual target accesses.
The debugger method follows
[the native boss and laser diagnostics](native-boss-and-laser-diagnostics.md).
The host now also checks that complete function returns restore the thread's
original exception chain. It never patches game instructions or internal
callees.

All **1,157 complete native calls** agree between original and candidate:

- Eight absolute, relative and offset movement instructions, with times -1, 0,
  1 and 38, mirrored and ordinary movement, and three x87 precisions.
- Ordinary goals, the exact keep-coordinate sentinel, values below it,
  infinities, NaNs and signed zero, with initialized and uninitialized timers.
- Five default exits, including opcode values below, above and outside the
  signed instruction range.

Each call compares the whole enemy object, adjacent canaries, complete active
ECL context, file manager, subroutine table and script storage. It also checks
the return, stack cleanup, preserved registers, floating controls and exception
chain. An independent expected-object calculation checks the active mode,
initial and goal coordinates, cleared tangents, timer reset, flags and untouched
storage. The actual argument getter and timer-reset callees execute.

Another **108 complete native calls** exercise both difficulty selectors, nine
signed/default difficulty values, three x87 precisions and two value sets for
each type. They check integer extrema, signed zero, infinity and NaN payloads.
The destination is a real positive-offset ECL stack variable; the actual pointer
getter runs. The whole expected context differs only at that selected word,
and enemy, script, Globals, floating controls, ABI and exception chain agree.

Movement inputs and selector values are constant; difficulty destinations are
positive-offset locals. Other variable reads, global destinations, stack
references, resource-backed handlers, other movement instructions and execution
through the full ECL frame loop remain outside the fixtures.

## Native spell prefixes

All **140 prefix cases** agree for the five spell opcodes, four difficulties
and name lengths -1, 0, 1, 7, 31, 127 and 128. Independently encrypted inputs
decode to the expected full 128-byte buffer. The actual four stack arguments
at the call site agree, including the name pointer and difficulty-adjusted
spell ID. Enemy, active context, script and Globals storage are checked too.

A hardware execution breakpoint stops immediately before the actual
`Spellcard::start` call. That callee, resource loading and the remainder of the
dispatcher do not run. The debugger cancels the stopped frame and restores the
saved exception-chain head before the next fixture. This is a prefix snapshot,
not a completed function call, exception-unwind test or spell-start validation.

A negative control supplies a default opcode instead. It returns normally
without reaching the spell call, and is rejected as a prefix result in both
images. Do not treat an arbitrary normal return as proof of reaching the
observation boundary.

## Restored alternatives and verification

An origin-based offset calculation alone leaves 21,570 bytes. An extracted
inline finish helper grows to 21,682 bytes and does not recover the shared
path. Sharing only coordinate declarations also leaves 21,570 bytes. Advancing
both cipher pointers produces the wrong countdown loop and a 21,426-byte
candidate. These source alternatives, build logs and candidate/case diagnostics
are retained. The shared finish, indexed-source/destination-pointer loop and
explicit difficulty branches remain.

The first block locator assumed fixed dispatch instruction offsets. The
destination-pointer source changed the prefix layout, so it failed closed with
`StopIteration`. The corrected diagnostic identifies the bounded byte remap
and indexed dispatch instructions, checks the actual 701 bound and complete
table/map contents, and records every case slice. Keep the failed log. An
initial attempt to use the compound profile was also refused because that
schema requires multiple dispatch sites; the final probe checks the actual
main dispatch's unsupported adjacency directly. Neither attempt changes
maintained acceptance configuration.

The final full strict replay preserves every one of the preceding **885 exact
owners**, all comparison classifications, **169,575 exact primary bytes** and
**950 units**. Native movement, difficulty, prefix and negative-control records
fingerprint the same final PE/MAP/PDB/receipt preserved in `final-image/`.
PDB age is 195.
Source-origin review remains open; Factory acceptance is not submitted. This
checkpoint adds source progress and scoped evidence, with no new exact credit.
