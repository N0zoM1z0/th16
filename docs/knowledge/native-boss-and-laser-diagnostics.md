# Native boss and laser diagnostics

This investigation starts at `291be6e`. It adds native execution evidence for
six substantial gameplay owners, without changing the retained reconstruction,
Oracle, compiler profiles or exact-credit totals. All rejected source trials
are restored. Keep `.analysis/laser-core-work/`, including failed prototypes.

## Native execution method

The historical compiler builds a Win32 debugger host. It starts each actual PE
as a suspended debug child, verifies the preferred image base `0x00400000`, and
lets the loader reach its initial breakpoint before redirecting the main
thread. The loader reserves the image before fixture allocation, avoiding the
earlier host-mapping collision at the preferred game base.

The host supplies fixture data, stack arguments, ECX, XMM3 where required,
x87 precision, MXCSR and sentinel values for preserved registers. An INT3 on a
separate allocated return page stops execution after the real function returns.
It checks stack cleanup and preserved registers. Original and candidate game
instructions, internal callees and imports are neither replaced nor patched.
Fixture generation rejects writes outside allocated data and writable,
non-executable image sections. Wine runs through the shared Factory entrypoint
with this game's prefix on the x86 host.

Two hardware execution breakpoints observe laser parameter construction. One
records the parameter base; the other reads all 856 bytes before the manager
capacity test. They do not patch game instructions. The straight-laser REP
copy observer records EDI only with ECX equal to 214, before the copy advances
either register. Missing or out-of-stack parameter bases fail the diagnostic.

The parent brackets execution with `strict_oracle.Context`, validates input
and output lengths, and compares complete memory observations, return values,
floating controls and parameter captures. Native observations also agree with
the independently executed Unicorn observations for every case. These are
fixture-based diagnostics, not whole-game validation or exactness credit.

## Checked scopes and results

| Original entry | Owner | Cases |
| --- | --- | ---: |
| `0x0041c330` | `EnemyData::step_logic` | 278 |
| `0x00445a30` | `Player::compute_damage_to_enemy` | 118 |
| `0x00434730` | Straight-laser circle cutting | 149 |
| `0x00433860` | Straight-laser rectangle cutting | 149 |
| `0x00436670` | Infinite-laser circle cutting | 149 |
| `0x00435880` | Infinite-laser rectangle cutting | 149 |

All **992 cases** agree between original and candidate, with no execution or
observation faults. The laser cases include **140 complete parameter captures**:
33 straight-circle, 28 straight-rectangle, 42 infinite-circle and 37
infinite-rectangle. The first native baseline remains in `native-first-baseline/`;
the final report fingerprints the restored build and final debugger host.

Boss and damage coverage is the same partial scope described in
[boss damage and hit feedback](boss-damage-and-hit-feedback.md), now executed
as native instructions. Actual timer and sound-queue callees run. Allocation,
resource-backed effects, replacement shields, death and ECL transitions remain
outside those fixtures.

Laser cases cover lengths around 16 and 32, empty and long segments, positions,
angles, rectangle rotations, invulnerability guards, three x87 precisions,
flags, signed and non-finite dimensions, and seeded random inputs. They compare
the whole laser object, an adjacent canary, the whole fixture manager, RNG and
complete new-segment parameters. The head sample at length 16 is included by
both rectangle cutters and the straight-circle cutter; the infinite-circle
cutter excludes it until the length is greater than 16.

Items are disabled, bullet type 35 skips effect creation, and manager length
512 declines allocation. Straight-laser child parameters retain the seeded
792-byte extension sequence; infinite-laser children clear it. Infinite-circle
children have flags zero; infinite-rectangle children derive bit zero from the
parent's bit one. These controls do not test real new-laser allocation, item
creation, effect resources or normal gameplay scheduling.

## Observation controls and failed prototypes

The parameter schema independently checks the complete extension sequence,
type, color, depth and expected flags. Unicorn controls reject an out-of-stack
base, a missing base and a REP observer shifted by one element. Native controls
accept a nonzero cutting case with one complete capture, reject an out-of-stack
observer, detect a missing capture, and reject the shifted REP observer.

The first Unicorn observer ran on each REP iteration and overwrote the initial
EDI base. Unicorn also swallowed callback exceptions. Its superficial equality
result is invalid; preserve `observer-prototype/` and its explanation. The
corrected observer catches and reports every callback error, and the parent
rejects child stderr. Both corrected 596-case runs and all schema controls pass.

The first native negative-control attempt returned failure without flushing
its diagnostic before `ExitProcess`. It could not authenticate the failure
reason, so it is not a passing control suite. Keep `native-buffered-failure/`.
The final host flushes before terminating; all four native controls pass.

An earlier native smoke redirected the thread at process creation, then stopped
at the loader breakpoint before executing the requested function. Only the
subsequent loader-breakpoint redirection reaches the separate return marker,
returns one and clears the laser length. The failed output is transcribed in
`loader-redirection-failure.txt`; its raw logs were overwritten during the fix.
Current smoke logs belong to the successful rerun. Do not reinterpret the first
loader stop as game execution.

## Rejected source and calling-context trials

No source trial in this investigation is retained:

- Hoisting straight-laser cancellation positions changes the 678-byte candidate
  to 673 bytes against 657 original bytes. Swapping infinite-laser cancellation
  operand order changes its 633-byte owner to 624 bytes. Neither recovers the
  original dataflow.
- Planar temporaries in infinite rectangle cutting leave 1,906 candidate bytes
  against 1,922 original bytes. Moving the circle cutter's point declaration
  leaves 1,527 against 1,531. These declaration changes do not fix the frame.
- Keeping line/infinite initialization through existing harness annotations
  leaves 1,126/665 bytes against 1,132/671. Their six-byte extent differences
  involve frame realignment and stack operand encodings. Do not force alignment.
- Caching the owner or active-context address in the animation ECL dispatcher
  shrinks its 1,100-byte candidate to 920 against 1,124 original bytes, removing
  original context reloads. Drop-vector scaling forms either introduce another
  call or change floating operand scheduling; the 455/500 baseline is restored.
- The compiler call graph identifies a second damage caller,
  `ecl_ext_damage_anm_hurtbox`, in addition to boss step logic. Retaining that
  existing callback explicitly does not change the 285-byte callback, 769-byte
  damage owner or 2,196-byte boss owner. Graph rooting alone does not explain
  the opposite original/candidate alignment choices. The diagnostic graph has
  no alignment properties and is not an alignment proof.

The large `EnemyData::ecl_run_over_300` candidate is 21,586 bytes. Caching its
owner throughout produces 21,402 bytes, but removes original owner reloads
after calls; it is rejected. The target boundary table lists 19,976 primary
bytes provisionally, and its switch tables still need independent scope review.
The focused Oracle stops first at unresolved linked fields, so its reported
candidate size does not establish an accepted target extent. Ghidra's retained
context also warns about switch recovery; use the actual instructions when
reviewing individual cases. Do not accept that dispatcher by binding nine
fields and assuming the remaining body matches.

The useful next source work is the actual reload and local-object lifetimes
inside the large ECL dispatcher, boss logic and laser loops. The retained native
fixtures can detect behavioral regressions during those iterations; the strict
Oracle must still compare complete independent owners and all linked fields.
