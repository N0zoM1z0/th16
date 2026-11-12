# Timing, collision and audio scalar identities

## Complete results

Eight independently witnessed numeric bindings resolve nine existing whole
source candidates:

| Original entry | Function | Complete primary bytes |
| --- | --- | ---: |
| `0x00402CB0` | Rng::randf_neg_1_to_1 | 64 |
| `0x00406690` | anm_jagged_line_on_tick | 455 |
| `0x004109D0` | BombReimuAOrb::start | 263 |
| `0x00414EC0` | Bullet::step_ex_00 | 227 |
| `0x00433510` | LaserLineInf::check_graze_or_kill | 514 |
| `0x0045A9F0` | GameWindow::update_window_sleeping | 597 |
| `0x0045B280` | GameWindow::set_resolution_from_config | 174 |
| `0x00471B00` | CStreamingSound::switch_track | 199 |
| `0x00471BD0` | CStreamingSound::get_play_time | 178 |

These add **2,671 exact primary bytes**. Canonical replay reports **824 exact,
64 mismatch and 327 incomplete**, covering 147,675 exact primary bytes. All
815 preceding exact results, all 63 preceding complete mismatches and all 878
previous units remain identical. Nine new exact units and one new complete
mismatch give 888 retained units. Game source, compiler/linker profiles, build
receipt and every current artifact remain unchanged. No compilation is needed.

## Independent original storage

| Candidate symbol | Value / width | Original storage | Fixed original witness |
| --- | --- | --- | --- |
| `__real@30000000` | 2^-31 / 4 | `0x004943D4` | `0x00402CD4`, MULSS |
| `__real@40a00000` | 5.0 / 4 | `0x004945B0` | `0x00414EDD`, MOVSS |
| `__real@3fc00000` | 1.5 / 4 | `0x00494524` | `0x0045B2AC`, MOVSS |
| `__real@3fc0000000000000` | 0.125 / 8 | `0x00494528` | `0x00471C29`, MULSD |
| `__real@4004000000000000` | 2.5 / 8 | `0x00494560` | `0x0045AA2C`, SUBSD |
| `__real@400c000000000000` | 3.5 / 8 | `0x00494568` | `0x0045AFD0`, SUBSD |
| `__real@42400000` | 48.0 / 4 | `0x0049460C` | `0x0040FEE2`, MULSS |
| `__real@42600000` | 56.0 / 4 | `0x00494614` | `0x00410A5A`, MOVSS |

Every selected value occurs elsewhere in original read-only data. Some raw
occurrences are unaligned or embedded in other values; the upper four bytes
of the 0.125 double also encode the 1.5 float. A fixed original instruction's
actual typed read selects storage. Candidate operands, passing comparisons
and nearest duplicate addresses do not select the original destination.
The existing literal profile checks encoded symbol value, complete bytes,
payload hash, witness mnemonic, memory address and operand width.

Original-only scope derivation checks full decoding and reachable control
flow, instruction starts, absence of overlapping inventory owners and every
inter-entry INT3 byte. The 246-byte update_window witness owner has an explicit
tail exit at `0x0045B06F` to the independently inventoried Spellcard entry
`0x00417BC0`, after restoring ESI. Its other path reaches the owned RET; the
tail edge is recorded separately and does not extend into its callee.

All ten newly decidable consumer owners have complete independent dense
original scopes, including the 693-byte Supervisor owner. Their full
source-qualified candidate PDB owners, all linked fields and all PE relocations
are replayed without shortening either side. No ownership, normalization or
acceptance rule changes.

## Remaining differences

Supervisor::setup_special_anms now compares completely at **682/693**. At
`+0x292`, the original pops EDI and ESI before clearing the VM filter bit;
the candidate clears it before those pops. This changes 11 bytes through
`+0x29D`. The imported TODO describes the reverse scheduling relative to
these current artifacts; use the complete instruction evidence. No exact
credit is given and no forced access or return layout is introduced.

BombMarisaAInf::cancel_bullets exposes a complete **621-byte original versus
595-byte candidate** refusal after its last field resolves. Its witness proof
checks all 150 reachable original instructions and three following INT3 bytes.
Do not shorten its original to the candidate. BombReimuAOrb::update retains
two unresolved atan2 fields, and GameWindow::update_window retains one
unbound double-comparison constant. These remain incomplete.

## Validation and retained evidence

All **210 controls across nine suites** pass. The reviewed-linkage suite has
29 controls. The new control mutates each of the eight bindings: instruction
interior, wrong instruction, changed mnemonic, expanded typed extent and an
identical read-only payload at a different original address all fail. Existing
complete-owner and relocation controls retain their behavior.

Original full payloads, scope/flow evidence, typed reads, hashes and every raw
read-only occurrence are in `.analysis/timing-literal-original-identities.json`,
reproduced by `.analysis/review-timing-literal-originals.py`. Complete original
and candidate consumer payloads, PDB identities, fields, relocations, units
and strict outcomes are in `.analysis/timing-literal-consumer-scopes.json`,
reproduced by `.analysis/review-timing-consumer-scopes.py`.

Canonical and retained-pass evidence is `.analysis/timing-literal-focused.json`,
`.analysis/timing-literal-full-audit.log`,
`.analysis/timing-literal-regression-check.json` and
`.analysis/timing-literal-controls-summary.json`. The regression reproducer is
`.analysis/check-timing-literal-regression.py`. Baseline reports, configuration
and the unchanged build receipt remain in `.analysis/timing-literal-baseline/`.
Control logs use `.analysis/timing-literal-<suite>-controls.log`.

Source-origin review remains open and Factory acceptance remains unsubmitted.
Nothing is published.
