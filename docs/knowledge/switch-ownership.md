# Bounded switch ownership

## Original extent evidence

The 2026-11-11 review found code-only Ghidra extents that omit compiler-owned
absolute jump tables. The original executable establishes each table's scope:
a register comparison against the maximum unsigned index, an adjacent `ja`
default branch, and `jmp dword ptr [index * 4 + table]`. The table starts at the
encoded absolute address and has exactly maximum-index + 1 four-byte slots.
Every slot points to a decoded instruction start within the same code owner.
The complete extent includes the code, zero to three alignment bytes and every
table slot. No independent function starts within these extended extents.

| Original start | Owner | Code | Padding | Slots | Complete bytes |
| --- | --- | ---: | ---: | ---: | ---: |
| `0x00401460` | `UpdateFuncRegistry::run_all_on_tick` | 272 | 0 | 9 | 308 |
| `0x004015A0` | `UpdateFuncRegistry::run_all_on_draw` | 235 | 1 | 6 | 260 |
| `0x00402FF0` | `PosVel::update_secondary_fields` | 255 | 1 | 5 | 276 |
| `0x00403110` | `PosVel::step` | 679 | 1 | 5 | 700 |
| `0x00407900` | `anm_masked_effect_on_switch` | 296 | 0 | 10 | 336 |
| `0x0040DA90` | `BombInf::destroy_all` | 127 | 1 | 4 | 144 |
| `0x0044B530` | `TitleInf::on_draw` | 108 | 0 | 12 | 156 |
| `0x00468C00` | `AnmVm::write_sprite_corners` | 84 | 0 | 4 | 100 |

`config/switch-owners.toml` pins each complete original extent hash, guard and
dispatch instruction offsets, code/table boundary and every case destination.
These records were derived from the original, separately from candidate byte
comparison. The original-review diagnostic is
`.analysis/bounded-switch-original-review.json`. Candidate PDB contributions
supply the independently required complete candidate sizes; they do not define
original table bounds.

For example, the corners owner compares EAX with 3 at `0x00468C12`, branches
above the range, and dispatches at `0x00468C17` through `0x00468C54`. Its four
slots point to offsets `0x39`, `0x1E`, `0x39`, `0x39`. The old 84-byte code
extent omitted all 16 table bytes. The next independent function starts at
`0x00468C70`, outside the complete 100-byte owner.

## Strict comparison contract

`scripts/switch_ownership.py` validates the original and candidate structures.
It requires the unsigned guard and adjacent branch to use the dispatch index,
all slots to target owned instruction starts, and the full reviewed mapping.
Direct and table edges cannot bypass the comparison by entering its branch or
dispatch. Alignment bytes must be NOP or INT3 and the table must be aligned.
The candidate dispatch operand and every complete table slot require PE base
relocations. Partial, extra or crossing table relocations are refused.

`Context.check_boundary` decodes the reviewed code portion for control-flow
checks and retains full-extent overlap checks. It permits only that specific
reviewed indirect dispatch. Other indirect dispatches remain incomplete.
The existing exhaustive field enumeration and replay then compare every byte
of the complete PDB contribution, including padding and every table entry.
This adds no masks, shortened contributions, inferred external identities or
upstream matching authority. Both the proof module and records participate in
the Oracle fingerprint.

Nineteen controls cover all reviewed original extents, alignment
padding, partial/expanded ownership, target hashes, signed/wrong bounds,
index disagreement, table-address interiors, every case mapping, invalid case
destinations, missing/extra/crossing relocations, bypassing the guard, overlapping owners and
unreviewed indirect jumps. Complete replays also verify every table field and
reject changed code and alignment bytes. See `.analysis/switch-ownership-controls.log`.

## Screen-center literal

The masked-effect callback's source initializes position to `(320, 240, 0)`.
The original instruction at `0x004079C6` loads a four-byte `240.0f` from
`0x00494678`; its complete bytes are `00 00 70 43`. This establishes the
`__real@43700000` binding independently of comparison operands. The adjacent
instruction at `0x004079CE` loads `320.0f` from `0x00494690` and cannot witness
the 240 binding. The existing typed-literal validation checks the value, width,
candidate bytes and fixed original instruction witness. New negative controls
reject the adjacent read, a wrong load mnemonic and a wrong width.
