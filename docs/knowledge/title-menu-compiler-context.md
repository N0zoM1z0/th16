# Title menu address context

`TitleInf::do_difficulty_select` now passes the local strict comparison for
its complete 1,180-byte owner, 81 linked fields and reviewed switch table. The retained source
shares the cancellation paths' menu-pop exit. The final comparison covers
89 title/menu-helper/PauseMenu owners: 75 local passes, eleven incomplete and
three mismatches (`.analysis/title-compiler/difficulty-shared-exit-final-strict.json`).
All preceding passes survive. The broader roadmap remains in
[ROADMAP](../ROADMAP.md).

## The shorter load before the shared exit

The preceding candidate at 0x44fe20 already had the target's 1,180-byte PDB
extent. Its ordinary comparison stopped at switch ownership because the
candidate code was not completely decoded. Disassembly narrowed the cause
to a shorter operand before the final `MenuHelper::pop` call:

| Instruction at owner +0x429 | Target | Previous candidate |
| --- | --- | --- |
| Reload the current menu choice | `mov eax, [esi+0x24]` | `mov eax, [ecx]` |
| Size | Three bytes | Two bytes |

ESI holds the title object. ECX already holds the address of its MenuHelper
at +0x24. Both versions reload the selection after storing
`g_Globals.difficulty`, then write `g_last_difficulty` and call the same pop
provider. A diagnostic instruction diff with addresses abstracted finds no
other instruction change; branch and table destinations still require the
complete strict comparison.

The target code ends at +0x487 and has a one-byte NOP before its table at
+0x488. The previous candidate ended at +0x486 and used `66 90` there. The
reviewed 1,159-byte range therefore ended inside that two-byte NOP.
This explained the decoder failure without an unknown target boundary.
The independent switch record stays unchanged. The retained shared exit
restores the three-byte load and one-byte NOP. The complete owner now passes
with the existing reviewed decoding range.

## Source and provider controls

A const title receiver used for this final selection read does not change
the result. All 63 verdicts remain unchanged (`difficulty-read-owner`), and
the source is restored.

The private `pop-single-` control separates only `MenuHelper::pop` into a
second object, retaining the rest of MenuHelper.cpp under /GL. The pop
provider's 66 bytes equal the target in both the GL and native-COFF variants.
Neither variant changes the caller's shorter `[ecx]` read. The native link
is diagnostic rather than ordinary-source acceptance evidence. Its inputs,
source copies, maps and disassembly remain under `.analysis/title-compiler/`.

## Retained cancellation flow

The normal-game cancellation branch now jumps to `restore_previous_menu`.
The other cancellation paths retain their state and submenu cleanup, then
fall through to the same `menu.pop()` statement. Both continue to the
function's existing return value of one. The old branch had its own pop and
early return.

This source change preserves the runtime paths while changing the CFG that
C2 sees before it duplicates the shared exit. It restores the target's load
base under the existing compiler and provider recipe. The
initial 63-owner trial improves from 51 to 52 local passes
(`difficulty-shared-pop-strict.json`); the final 89-owner check additionally
covers the PauseMenu consumers of MenuHelper::pop.

The baseline read-only phase trace reproduces all 63 ordinary owners
(`difficulty-phases-control.json`). All eight walks finish. Before AddrModes,
the two menu reads and the pop argument share one address temporary; after
AddrModes that temporary remains a LEA rather than folding the title base
and +0x24 into each read. Both binaries reload the selection value. The
shared address lifetime led to testing the common cancellation exit.

## The shared exit changes lowering and tail duplication

The retained-source trace also exits normally and reproduces all 89 ordinary
owners (`difficulty-shared-exit-phases-control.json`). Its eight phase walks
complete. Both versions still use a menu-address temporary after Lower;
the shared source exit has not simply blocked initial address CSE.

At Lower return the shared source has one pop call at IR location 0x96.
PreEncode entry has two calls at that same source location: the exit has
been duplicated. The reload now uses `_this+0x24`, with a separate LEA for
the pop argument. The baseline still reads through the common menu temporary
at that phase. PreEncode then schedules the LEA ahead of the global store
but leaves the reload on the title base, yielding the target instruction.

The decisive split therefore occurs between Lower return and PreEncode
entry, alongside exit duplication. The
trace does not identify the individual intervening pass that rebases the
read. For other owners, inspect shared tails and resulting live ranges in
the complete carrier.

## Title-screen storage families

`TitleInf::do_title_screen` at 0x44b5f0 remains a complete 3,964-byte local
mismatch, with 3,899 matching bytes. Both binaries align ESP to eight bytes,
reserve 0x10 bytes and save ESI/EDI. A diagnostic diff using the ordinary
report's linked fields finds 53 stack-displacement changes and one reordered
instruction pair: the final item-confirmation path loads its comment-line
interrupt argument before clearing animation 0x65, where the target clears
first. The stack gap is not a larger frame allocation.

The following offsets are relative to ESP after the saved registers, before
pushing call arguments:

| Stored value | Target | Candidate |
| --- | --- | --- |
| Loop counter and related spills | +0x08 | +0x0c |
| VM pointer spills | +0x0c | +0x10 |
| First-show animation 0x61 and state-1 animation 0 return areas | +0x0c | +0x10 |
| Other three title-file creation return areas | +0x10 | +0x10 |
| Vertical-title comment animation return area | +0x14 | +0x14 |

The uncached `title-screen-stackpack.jsonl` trace records 27 storage objects
packed into three colors. Its guard reproduces all 89 ordinary menu owners
(`title-screen-stackpack-control.json`). The candidate's VM spills and first
five return areas share a color; the loop spills use another, and the final
comment-animation return area uses the third. The target uses four distinct
slots for the values above. Uniformly shifting the candidate's stack operands
would therefore corrupt the already correct three title-file creation arguments.

The separate `title-screen-liveness.jsonl` observation completes two
1,601-tuple walks after local liveness and live-on-definition computation.
Both terminate normally, and its terminal guard reproduces the same 89 owners
(`title-screen-liveness-control.json`). The first four return objects appear
only around their creation and assignment; the fifth and sixth also occur in
later call alias lists. This differs from `take_snapshot`, whose returned
handle remains in later surface-copy alias sets. Use the uncached stackpack
trace for color facts: the liveness observer's cached enumeration/color
snapshots were stale and are excluded from this finding.

## Title-screen source and shared-provider controls

All controls below use incremental ordinary builds and complete related-owner
comparisons. None repairs the title-screen owner:

- Named `const AnmId` values for the two differently placed return areas
  retain the 3,964-byte extent but change the return load and reduce matching
  bytes to 3,829 (`title-screen-named-ids-strict.json`).
  Extending the first background result with a const reference also changes
  the return load and fails the reviewed switch mapping without fixing the
  stack layout (`title-background-ref-strict.json`).
- Direct initialization in the shared world-effect creator changes its
  previously exact 236-byte owner to 222 bytes. A 395-owner reverse-call and
  complete-TU scope finds that regression without a title-screen improvement
  (`world-direct-init-strict.json`). Restoring the provider restores its pass
  and all preceding verdicts (`title-screen-restored-strict.json`).
- Reusing `interrupt_and_clear` for the eight item-confirmation cases leaves
  a 3,952-byte owner (`title-clear-helper-strict.json`). Resetting the handle
  with `AnmId()` instead leaves the original 3,899/3,964 result
  (`title-clear-value-strict.json`).
- Reusing the existing `TitleInf::create_effect` member for all five title
  creations changes the alignment prologue to the EBX-based form and leaves
  3,976 bytes (`title-create-helper-strict.json`). Reusing it only for the
  first-show background and state-1 root preserves the original mismatch
  (`title-initial-create-helper-strict.json`).
- Combining the eight identical confirmation case bodies leaves 3,956 bytes
  (`title-shared-confirm-strict.json`). Preserve their current
  separate source bodies until their earlier control-flow effects are traced.

The next useful comparison is storage-family assignment and allocation order,
including the producer's return summary. The title-screen evidence does not
support carrying over the snapshot's escaped-return explanation or adding an
unused local to occupy the missing slot.

All source controls are restored. The final complete 89-owner comparison is
`title-storage-final-strict.json`: 75 local passes, eleven incomplete and
three mismatches. The difficulty-selection pass survives; this storage study
adds no newly exact owner. The roadmap next checks the title tick caller and
practice-stage selector's alignment context before returning to this packing
question.
