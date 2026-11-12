# Replay format linkage and pause label

The existing annotated replay format tables now have explicit external linkage.
Their types, dimensions, initializers and bytes are unchanged. A separately
reviewed fixed `Pause` PUSH resolves two complete menu entries. No Oracle,
compiler profile, owner extent or normalization rule changes.

## Complete original tables and replay owner

The original replay drawing entry at `0x00451D50` contains 1,500 bytes and
375 reachable instructions, ending in RET at `0x0045232B`. Four INT3 bytes
separate it from the next entry at `0x00452330`. Every direct branch target
is a decoded instruction start in this complete dense owner.

`g_replay_list_formats` at `0x00493700` contains four pointers, or 16 bytes.
The two rows select numbered/user replays and the two columns select
occupied/empty slots. Original PUSHes at `0x00451E76` and `0x004521AE`
read offset zero; `0x00451F6F` and `0x0045229B` read offset eight.
The empty-slot PUSH at `0x004522C4` reads base + 4 with an index scaled by eight.
Its immediately preceding SETNE materializes the nonzero page selection.
The complete string pointers are `0x004931EC`, `0x00493228`, `0x0049326C`
and `0x004932A4`.

`g_replay_spell_format` at `0x00493710` contains one pointer, or four bytes,
to the full format at `0x004932E4`. Original PUSHes at `0x00451ECC` and
`0x00452200` read that slot. All five strings, including NUL terminators,
are retained in the original-only evidence. The original has no PE base
relocations; this absence does not supply table-pointer relocation evidence.

Both definitions previously had internal linkage because the pointer arrays
are top-level const. Explicit `extern` makes their maintained GLOBAL annotations
resolvable without changing table access or adding a wrapper. It does not prove
that this was the original source's exact declaration spelling.

| Object | Candidate address | Complete PDB global type size | Candidate pointer relocations |
| --- | --- | ---: | --- |
| `g_replay_list_formats` | `0x00491AA0` | 16 | 0, 4, 8, 12 |
| `g_replay_spell_format` | `0x0049131C` | 4 | 0 |

Each object has one source-qualified MAP public from `MainMenuStates.obj` and
one named PDB global with the complete type size. Neither has a standalone
same-start physical PDB section contribution; both occupy larger CIL storage.
The typed object extents, complete read-only bytes, all five strings and all
five candidate PE relocations are independently checked. The table bytes remain
identical at the same candidate addresses as before this source change.

## Rejected replay index contexts

The existing complete replay candidate remains 1,501 bytes. Resolving its
seven format-table fields reveals the complete 1,500/1,501 extent refusal.
Its empty-slot selection uses MOV/NEG/SBB/AND and an unscaled pointer load;
the original uses XOR/CMP/SETNE and a scale-eight pointer load. The following
code is shifted by one byte. No partial range receives exact credit.

Two ordinary source contexts were evaluated with complete linked outputs:

- A direct `bool` cast for the table index retains the same 1,501-byte body
  and all 1,719 linked owner bytes.
- A used `user_replay` local shared by the occupied/empty selection gives
  1,509 bytes, changing 1,229 complete linked owner records through allocation
  and layout effects. It does not reproduce the original.

Both are rejected. The original replay function source is restored byte for
byte, while retaining only the two external-linkage declarations. A fresh
incremental build restores all 1,719 complete owner entries, extents and raw
hashes; all 192 dependency stamps validate. Do not repeat these contexts or
force a register, mask, padding instruction or table bound to obtain SETNE.

## Fixed pause label

The complete original `Pause` string is six bytes at `0x00492AC4`, including
NUL. Another raw read-only occurrence begins at `0x00492ABE`; the fixed PUSH
at `0x0043F186` independently selects the bound occurrence. Its complete
331-byte parent contains 84 reachable instructions and a terminal RET.
The other original callers have independently checked complete dense scopes:
267 bytes / 58 instructions at `0x0043F240`, and 428 bytes / 103 instructions
at `0x0043F350`. Their PUSH witnesses are `0x0043F2FD` and `0x0043F3FD`.

The unique candidate literal public is
`??_C@_05PEDNBBBD@Pause?$AA@` from `PauseMenu.obj`. It has a complete six-byte
same-start PDB contribution and the identical NUL-terminated payload. Existing
string-literal rules verify the fixed PUSH, full payload and storage extent.
The existing mutation table now also checks this literal's interior witness,
wrong mnemonic, duplicate original address, missing NUL, shortened contribution
and ambiguous contribution failures. The verifier itself is unchanged.

| Primary owner | Original bytes | Candidate bytes | Result |
| --- | ---: | ---: | --- |
| `PauseMenu::open`, `0x0043F0F0` | 331 | 331 | exact |
| `open_replay_end_menu`, `0x0043F240` | 267 | 267 | exact |
| `open_game_over_menu`, `0x0043F350` | 428 | 425 | incomplete extent refusal |
| `TitleInf::on_draw__replay`, `0x00451D50` | 1,500 | 1,501 | incomplete extent refusal |

The game-over candidate omits the original frame setup/teardown and adds loop
alignment. No source trial or artificial frame forcing is retained for it.

## Verification and retained evidence

The canonical strict audit reports **837 exact, 65 mismatch and 313 incomplete**
among 1,215 annotations, covering **152,600 primary exact bytes and 902 units**.
The two new passes add 598 primary bytes. All previous 835 exact results,
65 complete mismatches and 900 units remain unchanged, apart from attested
image hash/PDB age metadata. Sixty controls pass across the four relevant
suites: reviewed linkages (36), strict Oracle (14), focused audit (3) and
PDB types (7). No cold build, cleanup, archived-output substitution, Factory
submission or remote publication occurs.

The current incremental source input is
`c2ac9cc0add85924f097edf2dc772148551601b302607cc480fba1867a1fcd5a`.
Original proofs and reproducers are `.analysis/replay-format-original-review.json`,
`.analysis/review-replay-format-linkage.py`, `.analysis/pause-label-original-review.json`
and `.analysis/review-pause-label-originals.py`. Full source trial artifacts
are under `.analysis/replay-format-{linkage-baseline,linkage-artifacts,bool-index-artifacts,user-kind-artifacts}/`;
`.analysis/replay-format-source-trials.json` retains every affected complete
owner and is reproduced by `.analysis/review-replay-format-trials.py`.
Current source/table/graph proof is `.analysis/replay-format-linkage-check.json`,
reproduced by `.analysis/check-replay-format-linkage.py`. Complete caller bytes,
fields, relocations and successful Oracle replays are retained in
`.analysis/replay-format-pause-caller-scopes.json`, reproduced by
`.analysis/review-replay-format-pause-callers.py`. The canonical audit log is
`.analysis/replay-format-pause-full-audit.log`; control and regression summaries
are `.analysis/replay-format-controls-summary.json` and
`.analysis/replay-format-regression-check.json`.
