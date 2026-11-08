# Reference import: recorded strict comparison

This record was generated from the final local strict audit of upstream commit
`2b846da735ac71f68b1dc74e8194c8c8d98e2869`. The current result is available through
`.venv/bin/python scripts/progress.py`. No upstream comparator result was used.

| Local result | Candidates |
| --- | ---: |
| exact | 332 |
| mismatch | 13 |
| incomplete | 869 |

The 332 passing complete owners cover 39,826 bytes.
164 passing owners contain explicitly enumerated, symbol-bound fields.
The cohort contains 1,207 function/synthetic annotations and seven library
annotations. Source-origin review remains open. The local Factory registration
is inventory-only; this work has not submitted Truth Kernel acceptance receipts.

## Incomplete evidence

| Reason | Candidates |
| --- | ---: |
| Unresolved symbol/addend bindings | 704 |
| complete candidate owner differs from the independent target boundary | 123 |
| symbol lacks one complete same-start PDB contribution | 40 |
| PDB object differs from the declared source owner | 1 |
| indirect jump requires reviewed switch/owned-data extents | 1 |

Incomplete entries remain undecided. They are not counted as byte mismatches.

## Complete comparisons with differences

| Target | Source function | Matched / compared bytes | First differing offset |
| --- | --- | ---: | --- |
| `0x00405390` | `ZunAngle::operator-` | 130 / 142 | `0xD` |
| `0x0040E490` | `AnmVm::world_pos` | 247 / 297 | `0x40` |
| `0x004185B0` | `EnemyManager::destroy_all` | 146 / 147 | `0x12` |
| `0x00418AF0` | `EffectManager::create_effect` | 161 / 171 | `0x76` |
| `0x00431950` | `LaserManager::cancel_in_rectangle` | 66 / 142 | `0x3` |
| `0x00431A70` | `LaserManager::cancel_in_radius` | 114 / 119 | `0x33` |
| `0x0046D1C0` | `AnmManager::load_next_entry` | 467 / 485 | `0xE6` |
| `0x0046E7D0` | `AnmManager::insert_in_world_list_back` | 139 / 177 | `0x5` |
| `0x0046E890` | `AnmManager::insert_in_world_list_front` | 134 / 172 | `0x5` |
| `0x0046E940` | `AnmManager::insert_in_ui_list_back` | 139 / 177 | `0x5` |
| `0x0046EA00` | `AnmManager::insert_in_ui_list_front` | 134 / 172 | `0x5` |
| `0x0046F270` | `AnmManager::disable_vms_from_anm_file` | 105 / 112 | `0x19` |
| `0x00474330` | `EclRunContext::get_int_arg_ptr` | 97 / 98 | `0x45` |

Every difference remains after replaying all declared linkage fields. The full
byte differences and field bindings are retained in `.analysis/reference-audit.json`.

## Reproduction and retained identity

```sh
.venv/bin/python scripts/build.py --clean
.venv/bin/python scripts/audit-reference.py --write-units
.venv/bin/python scripts/progress.py
```

The cold-build receipt is `build/reference-candidate/build-receipt.json`.

- `th16.exe` SHA-256: `9780f0b48ae6315c7ad5f6be6ca62d872e0519000d6df622843c57acb90b60ae`
- `th16.map` SHA-256: `202131af567cdc18970978804882a6387ee4996b888e525d108ee4e3fc1a76d6`
- `th16.pdb` SHA-256: `fbeb6be80453205f1e9809e2a4f8fd8f2b6449ce6ab93a53547285c79e8174b3`
- `functions.txt` SHA-256: `29b9c998093e37333c40a9682de3f1c8630c2b111db8bc313e064354f1388e5c`

The Oracle controls cover bound calls/globals, missing fields, wrong addends,
overlapping target owners, partial extents and unlinked trailing data. Real
PE/PDB GUID and PE/MAP timestamp mutations were also rejected.
