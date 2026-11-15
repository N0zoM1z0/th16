# TH16 reconstruction workspace

Prioritize useful reconstruction and reusable knowledge with minimal workflow.
Inspect the current worktree and `docs/NEXT_AGENT.md` before editing. Preserve
dirty work and required ignored evidence. See `docs/ARTIFACTS.md` before cleaning
local outputs; retain the current build graph for incremental work. Write code,
documentation and commit messages in English. The Japanese game title is the
only non-English exception in maintained code, comments and documentation.
Use ordinary Markdown for findings.

## Publication

On 2026-11-15 the user published this repository as the public
`github.com/N0zoM1z0/th16`. Keep coherent checkpoints as local commits and push
`main` only when the user asks for it. Never commit private inputs: the target,
game data, Ghidra projects, build outputs, tools and `.analysis/` stay ignored.

The user has authorized importing the pinned reference candidates and evaluating
them using this repository's Factory/TH10-style strict Oracle. Upstream matching
tools, percentages and exact labels have no acceptance authority. Do not use REA
in this workspace.

## Target and tools

The canonical private target is `resources/th16.exe`, original Japanese v1.00a,
SHA-256 `c11776019f083978e66027e7394dafb1fb9543afca986f28049a49417e341929`.
Run `scripts/repo-python scripts/verify-target.py` when explicitly checking target identity.
`../game_exe/` retains the supplied game files; normal tools use the canonical
WSL-local target and do not depend on a Windows game directory.

Factory owns the shared Ghidra, JDK, Wine entrypoint and historical compiler/SDK
payload. This game owns `.tools/wine`, `ghidra-project/`, `.analysis/`, `.venv/`
and `build/`. Never borrow another game's prefix or analyzer project.

Useful commands from this directory:

```sh
scripts/repo-python scripts/verify-target.py
scripts/repo-python scripts/verify-toolchain.py --execute
scripts/repo-python scripts/ghidra.py check
scripts/repo-python scripts/ghidra.py function_context .analysis/context.txt 0x0047537B
scripts/repo-python scripts/compile-probe.py probes/toolchain-smoke.c -o build/probe.obj
scripts/repo-python scripts/msvc.py cl /?
./scripts/shared_runtime.py --describe wine
scripts/repo-python scripts/check-frontier.py    # after audit-reference.py
scripts/repo-python scripts/run-tests.py         # tooling controls, about 2 min
```

For future reconstruction, write natural C/C++ source and compare the complete
affected scope, including extents and relocations. Builds, analyzer output,
reference annotations and similarity scores grant no exact credit. Keep unknown
flags, ownership and boundaries explicit. Run only relevant checks; prose edits
need diff review, not compiler, analyzer or receipt refreshes.

Use incremental builds and focused complete-owner comparisons for reconstruction
iterations. The user explicitly prioritizes exact source progress over repeated
full cold builds. Reserve a clean build and broad replay for a meaningful
milestone or a demonstrated dependency/cache problem. Keep diagnostic evidence
and formal Factory acceptance requirements distinct.

## Reference and Factory

`_reference/johnthreekay-th16` is an ignored, independently cloned reference at
commit `2b846da735ac71f68b1dc74e8194c8c8d98e2869`. Its target hash matches ours.
Its source and reported progress remain reference material until independently
reviewed. Preserve its original checkout.

Use the one shared Factory service when deployment is requested. The staged
registration is `.analysis/factory-registration.toml`; local validation uses
`.analysis/factory-validation.toml`. The bootstrap does not activate or restart
the live service. See `docs/SHARED_TOOLS.md` and `docs/BOOTSTRAP.md`.
