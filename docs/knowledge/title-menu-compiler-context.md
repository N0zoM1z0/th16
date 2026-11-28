# Title menu address context

The current title/menu-helper comparison covers 63 complete owners. Its
baseline has 51 local passes, eleven incomplete and one mismatch
(`.analysis/title-compiler/difficulty-baseline-strict.json`). The broader
source roadmap remains in [ROADMAP](../ROADMAP.md).

## Difficulty selection's decoding gap

`TitleInf::do_difficulty_select` at 0x44fe20 has the same 1,180-byte PDB extent
as the independently reviewed target owner. Its ordinary comparison stops
at switch ownership because the candidate code is not completely decoded.
Disassembly narrows the cause to a shorter memory operand before the final
`MenuHelper::pop` call:

| Instruction at owner +0x429 | Target | Candidate |
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
+0x488. The candidate code ends at +0x486 and uses `66 90` there. The reviewed
1,159-byte code range therefore ends inside the candidate's two-byte NOP.
This explains the decoder failure without an unknown target boundary.
The independent switch record stays unchanged. Recover the load's address
provenance; the padding difference follows from that instruction choice.

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

Next, follow this final load through canonicalization, lowering and
PreEncode. Distinguish reusing the selection value from reusing the menu
address: both binaries perform the reload, and their differing base choice
changes its physical length. Keep the real pop call and global-store order
when testing the full carrier and affected menu-helper consumers.
