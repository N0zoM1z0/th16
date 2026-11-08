# TH16 reconstruction

Environment and analysis workspace for the original Japanese **TH16 v1.00a**.
The supplied executable is pinned in `config/target.toml`. This checkpoint
prepares the tools; it contains no reconstructed game functions.

The layout follows the local TH10 workspace:

| Path | Purpose |
| --- | --- |
| `resources/th16.exe` | Ignored canonical target |
| `config/` | Target identity, tool locks and provisional ledgers |
| `scripts/` | Target checks, compiler tools and Ghidra commands |
| `probes/` | Independent toolchain smoke inputs |
| `src/` | Future reconstructed source |
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
