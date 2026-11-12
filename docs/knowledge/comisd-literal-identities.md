# COMISD double-width evidence and complete consumers

The later [conversion-runtime review](conversion-runtime.md) supersedes the
unbound conversion-entry finding below and records the remaining timer mismatch.

## Result

Three fixed double bindings and a guarded correction to literal-witness
decoding resolve three existing complete source candidates:

| Original entry | Function | Complete primary bytes |
| --- | --- | ---: |
| `0x004262F0` | FpsCounter::update | 235 |
| `0x0045AC50` | GameWindow::do_frame_frameskip | 416 |
| `0x0045AF80` | GameWindow::update_window | 246 |

These add **897 exact primary bytes**. Canonical replay reports **827 exact,
64 mismatch and 324 incomplete**, covering 148,572 exact primary bytes and
891 retained units. All 824 preceding exact results, all 64 complete mismatches
and all 888 previous units remain identical. Game source, compiler/linker
profiles, the build receipt and current artifacts remain unchanged.

## Decoder issue and guarded witness

Capstone 5.0.7 decodes the legacy `66 0F 2F /r` instruction as COMISD but
reports its memory operand as 16 bytes. The actual scalar double memory read
is eight bytes, as specified in the
[Intel instruction manual](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2a-manual.pdf).
An independent GNU objdump 2.42 probe also reports QWORD memory for the same
synthetic eight-byte instruction. This discrepancy previously prevented
eight-byte symbols from satisfying the literal profile's operand-width check.

`literal_memory_witness` supports the specific observed form: an eight-byte
encoding with prefix/opcode `66 0F 2F`, ModRM mod=00 and r/m=101, an XMM
destination matching the encoded register, and an absolute disp32 matching
both decoded memory address and configured original storage. The literal must
own eight bytes. A decoder operand size of eight or sixteen is accepted only
after those encoding checks. The witness must also be an instruction start
in one uniquely containing, fully decoded original inventory owner.

Base/index addressing, SIB, segment or extra prefixes, register-only operands,
changed encoded addresses/registers, ambiguous or shortened parent scopes,
and four- or sixteen-byte literal claims remain refused by this correction.
Other literal instructions retain their existing width checks. No instruction,
register, displacement or branch byte is normalized by this witness check;
the complete linked-owner replay still compares all bytes and fields.

## Independent original identities

| Candidate symbol | Value / width | Original storage | Fixed original witness |
| --- | --- | --- | --- |
| `__real@3ff0000000000000` | 1.0 / 8 | `0x00494540` | `0x0042631C`, COMISD |
| `__real@0000000000000000` | 0.0 / 8 | `0x004943C8` | `0x0042DBF2`, COMISD |
| `__real@3ff8000000000000` | 1.5 / 8 | `0x00494550` | `0x0045AC95`, COMISD |

All three values have other raw read-only occurrences, including thousands of
zero-filled or embedded patterns. None selects storage by whichever destination
makes a candidate pass. Original-only derivation establishes complete dense
235/142/416-byte witness owners, all 57/34/91 reachable instructions, all
inter-entry INT3 padding, exact instruction starts, encoded scalar reads and
complete eight-byte values. Candidate artifacts do not enter that derivation.

The three accepted consumers are independently reviewed and replayed over
their full source-qualified PDB owners, every linked field and every PE
relocation. The 246-byte window-update owner includes its explicit tail exit
to `0x00417BC0`; the callee is not appended to its extent. The preceding
[timing identity review](timing-literal-identities.md) retains that tail proof.

GameThread::update_play_time remains incomplete with one unbound `__dtoul3`
CALL. Its candidate public at `0x004878A0` is an interior entry of the complete
887-byte `__ftoui3` PDB contribution from pinned `LIBCMT:_ftol3_.obj`, rather
than a complete same-start owner. The original call at `0x0042DC0A` reaches
`0x00487910`, with a provisional 286-byte inventory entry. Do not bind the
interior label as an ordinary complete runtime function. Any aggregate/runtime
identity needs its own independent complete-scope review.

## Validation and evidence

All **215 controls across nine suites** pass. Reviewed-linkage controls increase
from 29 to 34. New cases cover all eight XMM destination registers, the exact
eight-byte footprint, unsupported prefix/address forms, missing/ambiguous/
shortened original parents, encoded/decoded address and register disagreement,
and mutations of each fixed binding's witness, mnemonic, extent and duplicate
storage. The sixteen-byte decoder report never authorizes a sixteen-byte read.

Decoder evidence is `.analysis/comisd-decoder-probe.{bin,json}` and
`.analysis/comisd-objdump-probe.log`. Original scopes, instructions, encoding
proofs, typed values and raw read-only occurrences are in
`.analysis/comisd-original-identities.json`, reproduced by
`.analysis/review-comisd-originals.py`. Full original/candidate consumer
payloads, producers, fields, relocations, units and strict outcomes are in
`.analysis/comisd-literal-consumer-scopes.json`, reproduced by
`.analysis/review-comisd-consumer-scopes.py`. The deferred conversion identity is
`.analysis/comisd-time-conversion-unresolved.json`.

Canonical and regression evidence is `.analysis/comisd-literal-focused.json`,
`.analysis/comisd-literal-full-audit.log`,
`.analysis/comisd-literal-regression-check.json` and
`.analysis/comisd-literal-controls-summary.json`. The regression reproducer is
`.analysis/check-comisd-literal-regression.py`; baseline reports, configuration,
Oracle source and the unchanged build receipt are retained in
`.analysis/comisd-literal-baseline/`. Control logs use
`.analysis/comisd-literal-<suite>-controls.log`.

Source-origin review remains open and Factory acceptance remains unsubmitted.
Nothing is published.
