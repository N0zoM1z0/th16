# Current handoff

The requested work is environment setup only. Do not begin function exact
reconstruction until the user requests it.

- The canonical original Japanese v1.00a target is `resources/th16.exe`.
- Shared Ghidra/JDK/Wine selectors are attached. Prefix, project, Java caches
  and build outputs belong to this game.
- Historical Microsoft payloads are selected through `.tools/toolchain`.
  Both normal COFF and LTCG C/C++ smoke programs passed resource compilation,
  PE32 linking and Wine execution. Run
  `python3 scripts/verify-toolchain.py --execute` for the bounded smoke.
- Ghidra import and mapped-byte attestation passed. The entry context query
  and provisional inventory are retained in `.analysis/ghidra/`.
- `_reference/johnthreekay-th16` is pinned to
  `2b846da735ac71f68b1dc74e8194c8c8d98e2869`. It supplies toolchain download
  provenance and later research material; none of its reconstruction progress
  has been imported.
- Factory's PE inventory whitelist now supports `th16`; its focused tests pass.
  Private registration and validation files are in `.analysis/`. Activation of
  the live shared MCP remains a separate operator step.

See `BOOTSTRAP.md` for target provenance and retained evidence. No game functions
have been reconstructed or accepted as exact in this repository.
