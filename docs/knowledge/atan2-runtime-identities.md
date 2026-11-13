# Exact projectile owners through complete x87 atan2 identity

Starting checkpoint: `5de0006`, with 894 exact owners. Independent complete
`__CIatan2` identity closes **nine existing game-source candidates**, totaling
**3,036 primary bytes**, **741 original instructions** and **89 linked fields**.
Game C++ source and compiler options are unchanged. Runtime support receives
zero primary exact credit. No game runtime, native fixture or emulation is used.
Source-origin review remains open; Factory acceptance is not submitted.

## Complete primary owners

Every row passes both the canonical strict audit and separate complete unit
replay. Original-only dense CFG traversal covers each complete original scope,
including every return; no case, prefix or instruction-equivalence comparison
is accepted. Original hashes, full byte packets, instructions and control-flow
edges are in `.analysis/atan2-runtime-work/new-exact-original-scopes.json` and
its accompanying per-address files.

| Original address | Complete function | Bytes | Instructions | Linked fields |
| --- | --- | ---: | ---: | ---: |
| `0x004052A0` | `zun_atan2f` | 57 | 18 | 1 |
| `0x00414DA0` | `BulletManager::shoot_bullets` | 279 | 81 | 6 |
| `0x00414FB0` | `Bullet::step_ex_02` | 555 | 122 | 13 |
| `0x004151E0` | `Bullet::step_ex_21` | 507 | 112 | 12 |
| `0x00432DC0` | `LaserLineInf::step_ex_accel` | 380 | 87 | 9 |
| `0x004395B0` | `LaserCurveInf::step_ex_accel` | 380 | 87 | 9 |
| `0x00443840` | `Player::angle_to_player` | 123 | 36 | 3 |
| `0x00444CF0` | `Player::do_graze` | 288 | 74 | 14 |
| `0x00445EE0` | `sht_on_tick_homing` | 467 | 124 | 22 |

These are independently verified existing candidates, not newly rewritten
C++ bodies. All complete bytes, extents and linked fields are required.

## Closed runtime proof

`__CIatan2` is offset 10 within a **20-byte** complete `87ctriga.obj` code
contribution. Its stack-argument entry is `_atan2`; both entries tail-transfer
to the previously verified complete `87cdisp.obj` dispatcher at fixed offsets
135 and zero. A ten-byte entry alone does not establish identity and is still
refused by the ordinary `runtime-function` binding mechanism.

The `msvc-x86-atan2-v1` profile compares these complete pinned UCRT regions:

| Region | Original address | Bytes | Candidate producer |
| --- | --- | ---: | --- |
| Both argument entries | `0x00487AA0` | 20 | `87ctriga.obj` |
| Assembler calculation and handler region | `0x00488B00` | 168 | `87triga.obj` |
| Read-only operation descriptor | `0x00494E50` | 80 | `87triga.obj` |

The 168-byte region is a complete assembler contribution containing several
entry fragments, not a fictitious single PDB function beginning at the
interior `__fFATN2` public. That public must be at offset 28; `__rtpiby2` must
be at offset 108. All 70 instructions and all unused fragments remain in
comparison scope. Original read-only pointers identify offsets 28, 117 and
152. Traversal also retains fragment starts after terminal instructions;
these are not claimed to be reachable from the atan2 intrinsic. The first
read-only-roots-only diagnostic left unused fragment entries at offsets 9,
18 and 145; no bytes were removed to make that diagnostic pass.

Original boundaries are independently anchored by dense original instruction
regions and surrounding INT3 runs: 9/12 bytes around the argument entries,
3/8 around the calculation region. The latter begins after the already
reviewed complete 253-byte floor entry and its three padding bytes. Candidate
contribution sizes do not select the original boundaries. See
`review-originals.py` and `original-runtime-scopes.json` in the evidence folder.

The verifier requires each complete code/data PDB contribution, its unique
pinned library/module producer, and fixed MAP-public offsets. The descriptor
header and all sixteen code pointers are checked, including exactly sixteen
DIR32 relocations. Its handlers must lie in the verified calculation region
or shared dispatcher. Entry code requires exactly two DIR32 relocations;
calculation code requires exactly one, pointing to the verified dispatcher
pool's pi/2 constant at offset 10. All code fields are enumerated; all other
bytes remain raw. Internal relative branches remain raw as well.

The proof reuses the existing closed fmod family's complete 500-byte and
645-byte dispatcher bodies, both constant pools, typed flag storage and
independently verified external runtime identities. The atan2 profile cannot
exist without that verified family. No new dispatcher aliases or global
bindings are exposed. Only `__CIatan2` at offset 10 is added through the
existing `runtime-interior-v1` E8 REL32 call-field rule.

The complete original 57-byte `zun_atan2f` wrapper independently witnesses the
intrinsic through its fixed E8 CALL at `0x004052C4`. Primary call fields must
still resolve to that exact unique candidate public, without an addend.
The primary replay and normalization rules are unchanged.

## Refusals and remaining substantial owners

All **117 static controls pass**: 16 atan2 controls, 18 fmod controls, 22
runtime-interior controls, 47 reviewed-linkage controls and 14 strict-Oracle
controls. New controls mutate every one of the 188 candidate code bytes and
80 descriptor bytes, all required/extra relocations, original hashes/padding,
producers, complete PDB extents, public offsets and the original witness.
Wrong actual calls to parent offsets 0, 9 or 11, an altered wrapper byte and
a shortened 56-byte wrapper are refused or mismatch. These controls operate
on static representations and never execute or emulate target code.

The binding also exposes four complete mismatches. None receives exact credit:

| Complete function | Original/candidate bytes | Matching bytes |
| --- | ---: | ---: |
| `BombReimuAOrb::update` | 1,148 | 959 |
| `Bullet::step_ex_17` | 597 | 541 |
| `LaserCurveNode::step_back` | 986 | 982 |
| `sht_on_hit_laser` | 1,409 | 910 |

`LaserCurveNode::get_state` remains incomplete: its complete candidate has
1,168 bytes against 1,164 original bytes. `EclRunContext::ecl_run` remains
incomplete with two unresolved fields; resolving its atan2 call does not
close its complete owner. These six diagnostics and the nine new exact rows
are the only annotation changes. All other **1,200 results and diagnostics**
are unchanged, excluding current image/PDB identities.

The complete reverse-step original has 248 instructions and returns at offsets
447, 586, 875 and 983. Its SHA-256 is
`b54e71cef659050a342cad8a31ac12ca2f53b50649d68b18adef647856d3567e`.
Its four differing bytes, at offsets 770, 779, 787 and 791, select different
X/Y squaring registers and the operands of the squared-length sum. They are
real code differences and remain unaccepted.

## Rejected complete source trials

All game-source trials are restored. Keep their original/candidate packets,
source snapshots, focused strict reports, incremental logs and trial images.
Do not repeat these as new hypotheses.

| Owner and source form | Complete candidate outcome | Evidence directory |
| --- | --- | --- |
| Reimu bomb update: orb-array reference with member reload for `finish_all` | 1,129 bytes against 1,145 original; changes pointer load and stack-slot assignment | `.analysis/reimu-orb-array-work/` |
| Reimu bomb update: captured owning-object reference | 1,145 bytes; same timer-register, pointer-reload and stack-slot differences | `.analysis/reimu-orb-array-work/` |
| Full ANM interpreter: value-first integer add/multiply result expressions | 14,141 bytes against 14,177; does not recover destination EAX and changes camera X floating operand order | `.analysis/anm-integer-result-work/` |
| Curve reverse step: two named scalar squares | 986 bytes, 545 matching; broader register and scheduling differences | `.analysis/curve-square-result-work/` |
| Curve reverse step: ordinary scalar magnitude helper | 986 bytes, same 982 matching bytes | `.analysis/curve-square-result-work/` |
| Curve reverse step: ordinary scalar angle helper | 986 bytes, same 982 matching bytes | `.analysis/curve-square-result-work/` |
| Curve reverse step: accumulated squared speed | 987 bytes; complete extent refused | `.analysis/curve-square-result-work/` |
| Curve reverse step: squared speed computed before position writeback | 987 bytes; sentinel multiplication also changes and the square-register mismatch remains | `.analysis/curve-square-result-work/` |

## Final static checkpoint

The canonical audit reports **903 exact / 67 mismatch / 245 incomplete**,
**185,784 exact primary bytes**, and **970 comparison units**. All previous
894 exact owners and 957 unit definitions are unchanged. Thirteen new units
cover the nine exact and four mismatch owners; the latter add no exact bytes.

Final regression preserves all **1,719 native candidate owners (527,136 bytes)**,
all addresses/extents, all image base relocations and the entire raw `.text`
against the restored baseline. All experimental game-source changes are gone.
The incremental build has **PDB age 579**, source input
`80da752f1d593ebbb54bc5fecf92210566c8ba0ed0acb6e05ce1e4659e99259d`.

Preserve `.analysis/atan2-runtime-work/`: the original-only review scripts and
packets, full pinned-contribution inventory, baseline/final five-artifact
images, `atan2-support.json`, all five control logs, focused/canonical reports,
`standalone-new-units.json` and `final-regression.json`. Preserve the three
source-trial directories above and the current incremental build graph.
Nothing is pushed or published. Boss logic, the large ANM interpreter and the
remaining curve/shot mismatches remain open source-reconstruction work.
