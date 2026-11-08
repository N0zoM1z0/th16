# TH16 reconstruction

Environment and analysis workspace for the original Japanese **TH16 v1.00a**.
The supplied executable is pinned in `config/target.toml`. Imported reconstruction
candidates are evaluated independently using the Factory/TH10 strict Oracle
method. Upstream similarity scores and exact labels are not acceptance results.

The layout follows the local TH10 workspace:

| Path | Purpose |
| --- | --- |
| `resources/th16.exe` | Ignored canonical target |
| `config/` | Target identity, tool locks and provisional ledgers |
| `scripts/` | Target checks, compiler tools and Ghidra commands |
| `probes/` | Toolchain smoke inputs and separate compiler-context support |
| `src/` | Imported reconstruction candidates and subsequent maintained source |
| `docs/` | Setup findings and handoff |
| `_reference/johnthreekay-th16/` | Ignored upstream reference checkout |
| `.tools/` | Ignored shared-tool selectors and game-owned Wine prefix |
| `ghidra-project/`, `.analysis/`, `build/` | Ignored project, evidence and outputs |

`../game_exe/` contains the files extracted from the user-supplied archive,
including the separate Chinese launcher. Tools select `resources/th16.exe`.

## Use the configured environment

```sh
python3 scripts/verify-target.py
python3 scripts/verify-toolchain.py --execute
python3 scripts/ghidra.py check
python3 scripts/ghidra.py function_context .analysis/entry.txt 0x0047537B
python3 scripts/compile-probe.py probes/toolchain-smoke.c -o build/probe.obj
python3 scripts/compile-probe.py probes/toolchain-smoke.cpp -o build/probe-ltcg.obj --ltcg
python3 scripts/msvc.py link /?
.venv/bin/reccmp-reccmp --version
.tools/objdiff/objdiff-cli-linux-x86_64 --version
```

To rebuild and evaluate the imported candidates:

```sh
.venv/bin/python scripts/build.py
.venv/bin/python scripts/audit-reference.py --write-units
.venv/bin/python scripts/progress.py
```

Incremental builds reuse objects by their source, included-header and compiler
flag hashes, then perform a full LTCG link. Use `--clean` for a milestone or a
demonstrated cache/dependency problem. Focused comparison also accepts
`--require-cold` when that additional requirement is needed.

Game source lives in `src/`; imported compiler-context callers and opaque support
are kept separately under `probes/reference-harness/` and
`probes/reference-support/`. See [reference evaluation](docs/REFERENCE_IMPORT.md)
for the exact comparison scope and retained evidence. Source-origin review and
Factory acceptance remain separate from local comparison results.
The [recorded import audit](docs/evidence/reference-import-20261108/README.md)
lists the complete comparisons with differences and the outstanding evidence.
Subsequent source fixes and retained failed experiments are recorded in
[reference repairs](docs/knowledge/reference-repairs.md). Use `scripts/progress.py`
for current results.

The selected historical tools are MSVC **19.10.25017**, linker
**14.10.25017.0**, Windows **7.1A** SDK, UCRT **10.0.10240.0** and DirectX SDK
**June 2010**. Ghidra **12.1.3**, Temurin JDK **21.0.12.1+1** and system Wine
use Factory's shared launcher with game-local mutable state.

`verify-toolchain.py --execute` builds and runs separate normal COFF and LTCG
smoke programs, including a C unit, C++/STL, Win32/DirectX headers, resources and
PE32 linking. These are tool availability checks. Per-unit production flags
and exact comparison recipes remain future reconstruction work.

See [setup evidence](docs/BOOTSTRAP.md), [shared tools](docs/SHARED_TOOLS.md)
and [handoff](docs/NEXT_AGENT.md). The reference project's own scripts and
documentation are credited in the setup notes.

## Credits

This project imports candidate C++ source, names, structures, build-context
harnesses and historical toolchain research from
[johnthreekay/th16](https://github.com/johnthreekay/th16), pinned to commit
`2b846da735ac71f68b1dc74e8194c8c8d98e2869`. Credit belongs to johnthreekay and
the upstream contributors. Their original project work is dedicated under
[CC0 1.0](docs/licenses/johnthreekay-th16-CC0.txt). The game, its data and strings
remain the work of ZUN / Team Shanghai Alice; upstream also identifies its
`DSUtil.cpp` as an adaptation of a Microsoft DirectX SDK sample.

Our strict PE/MAP/PDB readers and Oracle method derive from the local
MIT-licensed TH10 reconstruction and Touhou Reconstruction Factory series.
The upstream comparison scripts are not used by the strict Oracle.
