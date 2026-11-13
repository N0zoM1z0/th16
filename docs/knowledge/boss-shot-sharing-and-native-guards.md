# Boss shot sharing and native rejection guards

Starting checkpoint: `a9c0a41`. This continuation investigates the complete Boss
logic, enemy-motion and enemy-shot owners. Every game-source trial is restored.
There is **no new retained game-source change or exact credit**. The useful new
evidence is a native 978-condition shot suite and an executable rejection control
for a source draft that has the correct sharing graph but wrong NaN results.

The canonical result remains **885 exact, 65 mismatch, 265 incomplete**, with
**169,575 exact primary bytes and 950 units**. Source-origin review is open;
Factory acceptance is not submitted. The restored incremental build has source
input `fdd04a2fec8a0c8faf41c88ff6f126d68bd243d79f1bb13c0c1a93557456051d`
and PDB age **296**. Evidence is in `.analysis/boss-accounting-work/`.

## Complete owners and restored forms

| Owner | Original bytes | Restored candidate bytes |
| --- | ---: | ---: |
| `EnemyData::step_logic`, `0x0041c330` | 2,207 | 2,222 |
| `EnemyData::step_interpolators`, `0x0041bb50` | 1,692 | 1,691 |
| `BulletManager::shoot_one`, `0x00412cb0` | 2,984 | 3,024 |

The first two original boundaries retain their existing independent evidence.
The shot boundary remains the existing provisional complete span. Its packet
separates 2,888 original code/padding bytes from two target tables of 52 and 44
bytes. Both guarded dispatches, all 24 destinations and every owned byte are
retained. The restored shot has 2,928 code/padding bytes and the same table sizes.
The three restored candidate binaries are byte-identical to their starting
complete owners. No profile, original geometry or Oracle rule changes.

Restored trials:

- A Boss damage-accounting helper produces 2,156 bytes but introduces an extra
  private call. A smaller dialogue-suppression helper produces 2,220 bytes and
  a conditional move, while exchanging the damage registers. Neither recovers
  the original statistics and life-restart sequence.
- D3DXVec3Add for camera displacement leaves the complete 1,691-byte motion
  owner byte-identical to baseline. Earlier scalar, indexed and vector forms
  were reviewed before this new API trial; they were not repeated.
- Sharing shot ring-angle and layer exits produces 2,924 bytes. Sharing only
  the layer exit produces 3,004 bytes. Both introduce 48 native NaN differences.
- A separate layer-offset scratch still produces 3,004 bytes, retaining the
  wrong angle addition. It also changes the nonzero-distance X addition; the
  protected-shot matrix uses distance zero and does not validate that change.
- An ordinary inline layer-angle helper reproduces the complete baseline
  3,024-byte shot owner exactly. It does not recover the missing sharing.

All source snapshots and build/scope logs are preserved. No failed draft is
retained because of its smaller extent or its passing finite subset.

## Ring sharing and arithmetic operands

The original modes 2/3 (ordinary rings) and 4/5 (half-step rings) share their
layer multiply/add. Mode 7, the random-speed ring, retains its own copy. Baseline
has three groups: 2/3, 4/5 and 7. The first trial incorrectly shares all five
modes. A diagnostic initially assumes mode 7 also joins in the original; it
refuses that assumption on the original. Preserve that failed prototype.

The corrected `ring-sharing-diagnostic.json` verifies the actual original and
baseline groups and the second trial's structurally correct two groups. This
is a source-shape diagnostic, not acceptance. That second trial still fails
48 native conditions: its final layer sum is the left operand of ADDSS, whereas
the original retains the incoming angle as the left operand. A representative
mode-2 input supplies distinct NaN payloads for the aim, layer spacing and player
angle. The original keeps player payload `0x7fc03333`; the draft returns spacing
payload `0x7fc02222`. Speed remains 2.5 in both.

The retained `invalid-ring-image/` contains the complete later scratch draft,
its source, PE, MAP, PDB and receipt. A one-condition native replay first passes
the original and historical baseline, then rejects that invalid image on the
same payload. It is independently authenticated by `shot-negative-controls.json`.
The first two full failing drafts retain their complete owner packets, source
snapshots, fixture/output files and image hashes; their full PE images were not
saved. Do not present them as retained executable replays.

Future source work must retain the incoming angle operand while recovering the
normal-ring sharing and keeping mode 7 separate. Repeating these goto, scratch
or helper forms without new type/call-context evidence is unlikely to help.
Accumulator/wrap registers, block placement and later stores remain different.

## Complete native shot calls

`native-shot-restored/` passes **978 complete calls per image** on the original,
receipt-authenticated PDB-288 baseline and restored PDB-296 candidate. These are
direct `shoot_one` calls through their real ABI after CRT startup. No game
instruction or callee is patched, stubbed or emulated.

There are 975 calls that take a bullet from its intrusive free list, insert it
into the tick list, calculate the shot, then reject it within the protection
radius and execute the real `Bullet::release`. Three calls have an empty free
list and return one without changing storage. The rejection calls return -1
and restore the free/tick topology. Nonzero `unk_c` head markers receive their
observed conditional updates; the ownership meaning of that field remains
unknown. The driver's `cached` selector only chooses zero/nonzero markers.

The matrix covers all 13 aim modes, odd/even and negative counts/layer counts,
zero count, varied bullet/layer indices, three x87 precision settings, two list
marker configurations, signed zeros, small values, large angles, infinities and
distinct signed quiet/signaling NaNs. The first 468 arithmetic result pairs and
three empty-list result pairs are independently modeled. All other 507 raw
speed/angle pairs remain in complete cross-image comparisons. Every condition
also checks the remaining observed storage independently.

Checked storage includes the complete typed 5,240-byte Bullet, 896-byte shooter
and Player, the 0x9c-byte manager prefix, neighboring list nodes, both RNG
objects, disabled critical-section storage, global manager/player pointers and
fixture canaries. Return value, stack cleanup and floating controls are checked.
The full 20,986,664-byte manager and accepted-spawn resource path are not observed.
There is no claim about ANM setup, live resource allocation, velocity creation,
transform execution or complete shipped Boss firing programs. Enabled locking
is also untested.

The first five-condition smoke passes the first wrong sharing draft and misses
its NaN regression. The first full model also predicts nine wrong random-speed
results because it adds the speed endpoint before rounding the RNG product.
The original stores that product as f32 before the SSE addition. Its actual
sequence corrects the model; the versioned first model and refused full report
remain preserved. With the corrected model, original and historical baseline
pass every independent expectation; both shared-exit drafts still fail the raw
48-condition comparison. The restored image passes all conditions.

Two expectation controls reject on the original before candidate execution:
a wrong ring angle and an omitted nonzero head-marker update. The invalid-image
control separately demonstrates that the original passes before the real wrong
source draft fails. All three controls retain their logs, reports and hashes.

The isolated full strict replay and `progress.py` pass after restoration. The
canonical ledger, units, source inputs and classifications are unchanged.
`final-regression.json` authenticates the restored owners, current image, native
observations and controls. No cold build, broad unrelated gameplay replay,
cleanup, service deployment or repository publication is performed.
