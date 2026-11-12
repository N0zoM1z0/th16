# ECL ring precision and active interpolation

Starting checkpoint: `a088cca`. This continuation restores the single-precision
interpolation boundary in random-ring instruction 93 inside the large ECL
interpreter. It removes 120 historical native position differences. The complete
interpreter remains incomplete; no new exact credit is claimed.

The strict result remains **885 exact, 65 mismatch, 265 incomplete**, with
**169,575 exact primary bytes and 950 retained units**. Source-origin review is
open and Factory acceptance is not submitted. The incremental final build has
source input `fdd04a2fec8a0c8faf41c88ff6f126d68bd243d79f1bb13c0c1a93557456051d`
and PDB age **288**. Evidence is retained in `.analysis/ecl-float-work/`.

## Random-ring radius

At `0x00473896`, the original reads the two radius arguments, generates an angle
with the replay-safe RNG, then obtains a second signed random sample. After
subtracting the radius endpoints, it stores the sample as a 32-bit float before
an SSE multiply and add. The old candidate keeps that multiply and add in x87.
A named float local and compound radius assignments still produce x87 code.

The retained source passes the signed sample and endpoints through an ordinary
inline linear-interpolation function. ANM already has the same mathematical
helper for its random-ring instruction. The float parameter boundary recovers
the sample store and SSE arithmetic without changing compiler flags, adding
volatile storage or forcing registers. The angle calculation remains the
original x87 multiplication by pi.

The original holds the endpoint difference in XMM1 and multiplies it by the
sample in XMM0. The candidate holds the difference in XMM0 and multiplies the
sample from memory. Stack slots also differ. The observed precision and payload
repair therefore does not establish exact instruction matching or original
source identity.

`ring-lerp-order/` retains the complete original, baseline and final candidate
owners: **7,046 / 6,950 / 6,942 bytes**. The target span remains the existing
provisional boundary. All 268 switch-target bytes and 94 opcode-remap bytes are
retained separately from decoded code and padding; every table destination and
remap index is checked. Three linked fields remain unbound.

`ring-flow-diagnostic.json` verifies the sample store and arithmetic sequence.
`surrounding-code-diagnostic.json` checks all 1,575 surrounding executable
instructions against the baseline, including mapped internal destinations,
same-named external callees and both switch-data addresses. Compiler-generated
padding is recorded separately: the new interpolation-loop alignment and final
padding explain why a single constant offset cannot describe every tail
instruction. Both complete binary scopes retain those bytes. This diagnostic
does not add an Oracle normalization rule or grant exact credit.

## Complete native calls

The final image passes **3,288 complete Boss/ECL conditions** through the real
`EnemyData::step_logic` time-interrupt path, with CRT startup and actual callees.
Each condition runs on the original and final candidate. Arithmetic and ring
conditions also run on the authenticated historical baseline image.

| Matrix | Conditions | Result |
| --- | ---: | --- |
| Floating stack arithmetic | 672 | All three images agree, including raw special-value results |
| Active float interpolation | 1,344 | Original and candidate agree with the complete independent state model |
| Random-ring position | 1,272 | Original and candidate agree; baseline differs in 120 conditions |

The ring matrix uses 24 seeds, eight finite radius pairs, local/global
outputs, three initial x87 precision settings, 48 special-value cases and 72
shared-output cases. The two output arguments can designate the same variable,
which checks that Y overwrites X. The RNG model checks every seed transition,
four generation increments across wraparound, untouched padding and the unused
RNG. RNG calls execute their real FINIT, so the expected final x87 control word
is 0x037f for every initial precision setting.

All 1,224 finite ring outputs match an independent arithmetic model on the
original and final candidate. The baseline has 96 finite output differences
and another 24 special-value differences. The 48 special-value outputs are
compared as complete raw words between images; their mathematical results are
not independently modeled. No native result bits are excluded from comparison.
The 672-case arithmetic matrix independently models 282 results; the other 390
raw results remain in full cross-image comparisons. Its first generator draft
attempts Python division by a converted integer zero and fails before game
execution. The corrected driver and initial version are preserved.

Active interpolation covers instructions 91/92, positive/zero/negative duration,
local and F0-F7 global destinations, slots 0/3/7, several simultaneously active
slots, shared destinations, and eight interpolation methods. Programs configure
slots in a different order from the final ascending-slot traversal. The model
checks complete interpolation records, timers, destination variables and saved
instruction locations. These are single-call configurations; repeated frames,
reconfiguration of a live slot and RNG-valued arguments remain untested.

Every fixture checks the complete typed EnemyInf, Player, Gui and Spellcard
objects, the 0x190-byte manager region, script arena and observed Globals region,
with existing canaries, return value, stack cleanup and floating controls. Ring fixtures also
check both complete RNG objects and the critical-section storage. Locks are
disabled in this pre-WinMain fixture state; enabled locking and full game-loop,
resource and allocation behavior are not proved.

Three negative controls reject the original before candidate execution: missing
interpolation instructions, reversed interpolation visit order and a missing
ring instruction. The ring control starts with 64-bit x87 precision, so a
missing FINIT alone cannot satisfy its rejection check; actual memory-state
differences are required. See `negative-controls.json` and its retained logs.

## Restored trials and remaining work

Pointer/countdown, destination-local, inline destination lookup and guard-clause
interpolation loops fail to recover the original register arrangement. The
original retains the destination in ESI across `InterpFloat::step`, with the
interpolation pointer spilled; the candidate retains the interpolation pointer
in ESI and spills the destination. The original reloads the VM on every active
iteration, so caching it for the entire loop would change the observed flow.

Explicit add/subtract and multiply/divide float exits, including a shared typed
VM-cell result, also fail to recover the original exit partition. Every rejected
form is restored. Only the ring interpolation helper and its call remain as
game-source changes. Driver snapshots, all trials and failed diagnostic
assumptions are retained in `TRIALS.md` and the evidence directory.

The strict replay changes no function classification or acceptance rule. One
upper-dispatch diagnostic reason changes from eight unbound fields back to
seven. The disappearing incidental field is offset 20,986, bytes `9f a0`, within
the unchanged 702-byte opcode remap. Complete 21,408-byte original and
21,316-byte baseline/final candidate scopes, all three tables and a relink check
are in `enemy-dispatch-final/` and `dispatch-relink-diagnostic.json`. All changed
upper-dispatch bytes are existing relocation/direct-branch fields. The formal
refusal remains. Generated units only rebind candidate addresses.

`final-regression.json` authenticates the final image, receipt, native evidence,
complete scopes, negative controls and canonical strict replay. Earlier Boss,
curve and expression evidence retains its own image identities; those broad
matrices are not rerun for this focused change. The repository remains local.
