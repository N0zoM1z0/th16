# Bootstrap evidence

This is the historical environment-only checkpoint. For the current source,
comparison results and next steps, see [NEXT_AGENT.md](NEXT_AGENT.md) and
[REFERENCE_IMPORT.md](REFERENCE_IMPORT.md).

## Original target

The user supplied a bilingual TH16 game ZIP archive. Its game files were
extracted into `../game_exe/`; `th16.exe` was copied to the ignored canonical
`resources/th16.exe`. The separate `th16c.exe` is not the selected target.

| File | Size | SHA-256 |
| --- | ---: | --- |
| `th16.exe` | 683520 | `c11776019f083978e66027e7394dafb1fb9543afca986f28049a49417e341929` |
| `th16c.exe` | 688640 | `099bf0edeef663c1001c6782d7c6de2aa22727526f314a98527c08dd99f06bc0` |

The selected hash is classified as original TH16 v1.00a in the
[pinned thcrap version database](https://github.com/thpatch/thcrap-tsa/blob/25acfe37f0bed5008eb8b94afc3d72679fd50384/base_tsa/versions.js).
The manifest records that commit and the downloaded database hash. Direct PE
parsing finds i386, image base `0x00400000`, entry `0x0047537B`, linker 14.10
and five sections. `.text` has virtual range `0x00401000` through `0x0048ACD9`.

## Compiler and reference

Rich records include 71 product-265 records at build 25017 and earlier 24723
and 40116 records. These select the early VS2017 compiler candidate; they do
not independently establish every unit's flags or ownership.

The user supplied [johnthreekay/th16](https://github.com/johnthreekay/th16) as a
reference. Its clone is `_reference/johnthreekay-th16`, pinned to
`2b846da735ac71f68b1dc74e8194c8c8d98e2869`. Its target SHA-256 is identical.
Its [`scripts/toolchain.json`](https://github.com/johnthreekay/th16/blob/2b846da735ac71f68b1dc74e8194c8c8d98e2869/scripts/toolchain.json)
provides the original Microsoft payload URLs and hashes, copied to
`config/toolchain-payloads.json`. Provisioning verifies each archive before
extraction. The local banners report compiler 19.10.25017, linker
14.10.25017.0 and resource compiler 6.1.7600.16385.

`scripts/provision-toolchain.py` adapts the reference project's CC0 setup
script to shared installations and game-local Wine. The Ghidra inventory and
attestation helpers derive from the local MIT-licensed TH10 workspace.
The reference's `v141_xp`, `/MT`, `/GL`, `/Oy-` and link-profile findings are
useful hypotheses for target-specific work. At this bootstrap checkpoint no
candidate source had been imported. The later import evaluates maintained
candidates independently and does not adopt upstream matching counts or
acceptance results.

## Analyzer and retained evidence

Ghidra 12.1.3 imported the target using the shared JDK and a fresh project.
The import's postscript verified executable hashes and mapped bytes before
exporting 1,761 provisional function candidates. Every origin started as
`unknown/review`. Source mappings, implemented functions, match rows and match
units were initially empty. Those initial analyzer spans were provisional;
subsequent comparison applies explicit boundary and ownership checks. The
source-origin ledger remains separate from local byte-comparison results.

The entry-function query returns `entry`, a ten-byte wrapper calling
`___security_init_cookie` and `__scrt_common_main_seh`. Logs and complete query
text are retained under `.analysis/ghidra/`. The Factory native provider query
result is `.analysis/factory-validation-result.json`.

The toolchain smoke result is retained in `.analysis/toolchain-verification.log`.
Disposable binaries were removed during handoff cleanup; rerun
`python3 scripts/verify-toolchain.py --execute` to recreate
`build/toolchain-smoke/`. The result covers tools and standalone test programs
only. Both normal COFF and LTCG C/C++ variants compiled, linked resources into a
PE32 image and ran under the dedicated Wine prefix, printing
`TH16 toolchain smoke: 42`. Component hashes were verified
before execution. The isolated Factory configuration exposed eleven native
Ghidra operations and completed an entry-function query. Wrong-target and
compiler-component mismatch checks reject altered inputs.

This section records the initial environment-only checkpoint. Subsequent
reference-candidate evaluation is documented separately.
