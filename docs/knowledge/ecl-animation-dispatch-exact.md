# Exact ECL animation instruction dispatcher

`EnemyData::ecl_anm_vm_instr` at `0x004233A0` now passes the strict Oracle over
its complete **1,124 bytes and 62 linked fields**. The scope includes **1,047
code bytes, one compiler alignment byte and a complete 76-byte jump table**.
Original-only CFG review covers all **333 code instructions**, all 19 table
entries and their 14 distinct destinations. The preceding candidate was 1,100
bytes and failed the complete-boundary check.

The source repair changes `src/Enemy.cpp` and adds two inline argument accessors
to `SptInf` in `src/Ecl.h`. Compiler flags, original extents, linkage identities,
switch admission and the Oracle remain unchanged.

## Argument lifetime and owner boundaries

The original interpolation branches evaluate their target values, then the
interpolation mode, and finally time. Their outgoing argument staging preserves
targets across the mode getter. The previous nested method calls pushed some
values earlier and kept a different VM register throughout the function.

The retained source makes those live values explicit:

- Scale interpolation reads Y and X before mode, then resolves time.
- Both alpha interpolation cases retain the alpha integer across mode lookup.
- Color interpolation builds the RGB target, then reads mode and time.
- Position interpolation reads Y/X, captures the origin VM, then reads mode
  and time before calling the animation method.

Each time read selects its owner after mode resolution. These are live source
values and owner snapshots, with no added stack storage solely for padding.
The resulting code restores the original EDI enemy pointer, EBX VM pointer,
VM spill and twenty-byte local frame. All repeated owner/context reads remain.
Caching the owner or active context throughout the entire dispatcher remains
the previously rejected approach: it removes original reads.

Mode snapshots bring the candidate to 1,120 bytes. Explicit final-time owner
selection also restores the address-preparation order in the color and position
branches. A diagnostic comparison then finds all 14 distinct switch arms equal
after masking linked addresses. This is only a locator: its shifted entry and
table still fail complete exact acceptance.

The new `SptInf::get_int_arg` and `get_float_arg` accessors resolve each argument
through `context.current_context`. Using the owner interface restores the
original entry sequence: retain the owner while locating the instruction,
then read its selected context again for slot zero. The accessors inline into
the complete dispatcher and receive no separate exact units.

That form produces 1,128 bytes because the blend-mode bitfield uses a different
update sequence. Retaining its input as a genuine `u8` local before the bitfield
assignment restores the original byte truncation and update instructions. The
complete 1,124-byte owner then passes every byte, field and relocation check.
No explicit instruction sequence or arithmetic rewrite implements the merge.

These source forms explain the successful compiler output. Original source
spelling and compilation partition remain unproven; source-origin review stays
open.

## Complete code and table ownership

The unchanged original span ends at `0x00423803`, including the full table.
The final code RET is at offset `0x416`; the owned NOP is at `0x417`, and the
19-entry table begins at `0x418`. Twelve following INT3 bytes are outside the
owner, before the next function at `0x00423810`.

All code instructions are reachable through the entry or independently reviewed
switch dispatch. Every table destination is a valid instruction start. The
complete original SHA-256 is
`4ccf48d686372a882d646ead2a82c20adbe37212200dec7552c586dc2adf6e80`.
The existing switch declaration already records this scope and case map.

The retained candidate is the complete 1,124-byte PDB owner at `0x0042C650`.
Ordinary replay compares the entire code, alignment byte and table, including
all 62 independently bound fields. The generic field decoder's `decoded_bytes`
is not a code-size measurement: it also attempts to decode table bytes. The
separate code/table packet and existing switch validator establish code and
data ownership; the whole-owner comparison establishes exactness.

## Regression and retained evidence

The final incremental build has PDB age **384**, with source input
`eb7dbf25d10b6a3ca0880708e8e2a40ad60c81d1c30e69e1bc664de4e965d725`.
Full canonical replay reports **889 exact, 65 mismatch and 261 incomplete**
among 1,215 annotations: **173,694 exact primary bytes and 954 retained units**.
All previous 888 exact owners and all 953 previous unit definitions remain
semantically unchanged; 531 candidate addresses move. Only this dispatcher's
classification changes.

A separate complete candidate-image regression covers all 1,719 linked public
owners. The other **1,718 owners**, totaling **526,009 owner bytes**, preserve
their complete bytes and relocation records after independently mapping 20,539
linked fields. Of those owners, 1,206 move during linking. The comparer uses
qualified MAP entries, bounded PDB types and full same-anchor PDB data
contributions whose entire loader payload and relocation graph agree. A data
contribution is not the C++ object at its first symbol. Two PE-header-relative
references use identical complete DOS headers. These candidate mappings add no
original bindings or exact credit and are outside the Oracle.

Preserve `.analysis/boss-vm-work/`: the PDB 374 baseline, first exact PDB 383
image, final PDB 384 image, all source/header trials, build and audit logs,
complete code/table packets, original CFG review, diagnostic arm comparisons,
failed and corrected image-comparison scripts/reports, `TRIALS.md`, canonical
regression and final audit/progress records. Early dump padding assumptions,
unresolved data mappings and the refused raw read of a virtual zero-fill
contribution are retained as failed evidence.

Validation is entirely static. No game runtime, dynamic fixture, cold build,
cleanup, deployment or publication occurs. Factory acceptance is not submitted.
The 2,207-byte Boss update and other substantial incomplete owners remain open.
