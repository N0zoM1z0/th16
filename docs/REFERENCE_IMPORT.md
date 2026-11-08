# Reference candidate import and strict comparison

Candidate source comes from
[johnthreekay/th16](https://github.com/johnthreekay/th16/tree/2b846da735ac71f68b1dc74e8194c8c8d98e2869).
The pinned target is the same original Japanese v1.00a executable. Source paths
and upstream SHA-256 hashes are recorded in `config/reference-sources.csv`.
The original clone remains unchanged under `_reference/`.

## Local layout and build

Game C++ and headers live in `src/`. Stand-in callers live in
`probes/reference-harness/`, and opaque compiler-context support lives in
`probes/reference-support/`. These support files are not game implementations.
The source manifest preserves the upstream translation-unit order. Relative
includes in moved support files were adjusted; Japanese diagnostic comments
were translated to English. Binary string payloads remain escaped source data.

`scripts/build.py` adapts the upstream build and symbol-discovery logic to our
shared historical tools and game-owned Wine prefix. It does not import either
upstream comparator. The candidate graph retains its LTCG, non-LTCG support,
stand-in callers and `/INCLUDE` choices so their effects remain visible. This
graph is an experiment, not a recovered production translation-unit partition.

```sh
.venv/bin/python scripts/build.py --clean
.venv/bin/python scripts/audit-reference.py --write-units
.venv/bin/python scripts/compare-linked-function.py reference-00401300
.venv/bin/python scripts/test-strict-oracle.py
```

The individual unit name is an example; select one actually retained in
`config/match-units.toml`. Build outputs live in `build/reference-candidate/`.
The build receipt binds source inputs, profiles and PE/MAP/PDB/function-map
hashes and records whether the full output graph was cleaned.

## Independent Oracle

The Oracle reuses PE/MAP/PDB readers, complete decode coverage and linkage-field
replay from the local TH10 reconstruction, commit
`54fbd717d78537c773c8663470115cf93c558ff3`. It does not use upstream similarity,
instruction-text normalization or upstream exact labels.

The strict path requires:

- the canonical target SHA-256 and a build current with its recorded inputs;
- matching PE CodeView/PDB GUID and age, MAP timestamp and image base;
- one same-start PDB contribution belonging to the selected source object;
- the complete independent target candidate extent, dense control flow and
  no conflicting function entry inside it;
- every PE relocation and external relative branch/call field, with a unique
  symbol, fixed target address and preserved addend;
- complete byte/decode coverage, including explicitly declared trailing data.

The local link adds `/FIXED:NO` because the upstream link strips relocations.
Without the relocation table, absolute fields cannot be exhaustively identified.
This diagnostic setting is recorded in the build profile.

Function/global annotations provide explicit candidate address bindings, fixed
independently of each compared operand. Imports are bound by DLL and import
name. Literal storage requires either a unique complete payload or an explicit
reviewed fixed instruction witness with its full storage proof. Runtime
identities require complete extents, pinned library ownership and reviewed
target evidence. See [shared linkage evidence](knowledge/reviewed-linkages.md).
Unknown or ambiguous destinations are incomplete. The
Oracle never selects a target destination merely because it would make the
current operand match.

`exact` means the complete declared owner passed this local strict byte
comparison. `mismatch` means that complete comparison found a difference.
`incomplete` means ownership, boundary, decode or linkage evidence is missing.
These local results do not establish original source authorship, physical
storage ownership, whole-product closure or Factory Truth Kernel acceptance.
The current Factory registration is inventory-only and no acceptance receipt
has been submitted.

Full per-function findings, missing fields and artifact identities are retained
in `.analysis/reference-audit.json`. Canonical source mappings and local match
rows are organized separately from the origin-review ledger. Source origins
remain under review even when a local code comparison passes.

## Wine PDB dependency

Full `/DEBUG` linking requires Wine's NTLM RPC helper. Without `ntlm_auth`, this
Wine 9/MSVC 14.10 combination reports `LNK1101: incorrect MSPDB140.DLL version`
even though all compiler DLL versions are correct. Supplying the helper fixed
the link and produced a readable PDB.

On this host the Ubuntu packages in `config/wine-auth-packages.csv` were
downloaded with APT and extracted without root into Factory's shared tools.
`.tools/wine-auth` selects that installation; its `bin/ntlm_auth` wrapper adds
the private extracted library directories. The helper and extracted payload
hashes are pinned in `config/tools.lock.toml`. No system service was installed
or started. The game compiler prefix uses Wine's null graphics driver.

## Attribution

Credit for the imported candidates, annotations, readable types, build-context
experiments and toolchain package research belongs to johnthreekay and the
upstream contributors. Their CC0 dedication is retained in
`docs/licenses/johnthreekay-th16-CC0.txt`. Game data and strings remain ZUN's
work; the upstream project identifies its DirectX sample-derived code separately.
The local TH10-derived Oracle tooling remains covered by the repository MIT
license. README includes the upstream project link and credit.
