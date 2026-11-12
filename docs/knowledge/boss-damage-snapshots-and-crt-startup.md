# Boss damage snapshots and initialized native execution

This continuation starts at `d6faeac` and retains two source changes in
`Player::compute_damage_to_enemy` at `0x00445a30`. The function remains
incomplete over 769 candidate / 774 original bytes. Preserve
`.analysis/boss-damage-work/`, including rejected source forms, failed protocols,
the final image and its complete owner packets. No original extent, compiler
profile, linked identity or Oracle rule changes.

## Source advancement and the impact snapshot

The source walk now advances `source` before decrementing its bounded remaining
count. The compiler advances both source and timer pointers, subtracts one from
the count, saves it and branches directly on the subtraction flags, as in the
original. The previous form decremented first, advanced the pointers and then
needed another TEST before JNE. A do/while trial produced the same retained
instructions; the simpler for loop keeps the intended order in its iterator.
Exactly 256 sources are visited, with entry 256 still excluded.

The impact position is copied through a local `Float3` value. This recovers the
original load sequence: read X/Y, read Z, then publish X/Y and Z to the output.
The previous direct assignment stored X/Y before reading Z. The retained copy
uses the original MOVQ and integer Z transfer; it adds no floating arithmetic,
conversion, alignment requirement or artificial storage.

The ordering is distinguishable in native execution. If an output points four
bytes after a source position `(1, 2, 3)`, the original publishes `(1, 2, 3)`;
the preceding candidate publishes `(1, 2, 2)` after overwriting its own later Z
read. The retained snapshot agrees with the original. These overlapping-storage
fixtures are machine-level stress cases. They do not establish that real game
callers use such pointers or that partially overlapping C++ objects have a
defined language-level alias contract.

The original keeps enemy ID in ESI and rereads position/size parameters. The
candidate still retains size differently, and loop placement and frame alignment
remain different. The original Boss logic realigns its frame and its damage
callee does not; the candidate still has the opposite arrangement. Do not force
either frame or infer exactness from the five-byte extent difference.

## Executable startup before native fixtures

The direct geometry matrix exposed a missing runtime precondition: the original
faulted on a nonfinite-angle CRT path when entered immediately after the loader
breakpoint. That failed matrix has no passing-suite credit. After actual
executable startup, the same cases complete successfully.

The local debugger's new input protocol runs the real executable startup and
stops at a hardware breakpoint at the existing WinMain entry. This executes CRT
initialization and static initializers before redirecting the main thread to a
fixture. WinMain itself does not execute. The final regression authenticates
18 such startup observations against target, current and historical WinMain
addresses and the actual debug logs. Instructions, imports and callees are not
patched or replaced. The exception-chain baseline is captured after startup.

The protocol also supplies XMM0 through XMM3 explicitly. Original and candidate
instructions establish that rectangle/rectangle collision takes its first four
floats there, with six remaining floats on the stack. The point-array helper
takes its array pointer in ECX, four floats in XMM registers and angle on the
stack. The initial pointer-on-stack attempt faulted on the original before
candidate execution; preserve its `INVALID.txt` note.

Controls replay one existing version-1 damage call and compare all declared
memory with its preserved expected output. Another control changes only the
version-3 width-register input to zero; the original returns zero and the
independent positive-overlap expectation refuses it before candidate execution.
Existing SEH-frame prefix mode 4 and unchanged-chain mode 5 retain their guards:
an actual ECL frame is accepted in mode 4 and rejected in mode 5.

## Native results and limits

The same final image passes **2,196 complete paired calls**:

- **384 impact-output calls**, with full Player, output arena and Globals
  expectations. They cover source indices 0/1/127/255, separate output and seven
  source-relative locations including exact self-alias, three precisions, and normal,
  signed-zero, quiet-NaN and signaling-NaN Z bits. All target and retained states
  agree with the snapshot model. The preserved `d6faeac` image fails 96 cases;
  the retained image fails none.
- **1,164 direct geometry calls**, including axis-aligned and rotated rectangles,
  point arrays, seeded random orientations, zero/negative/nonfinite dimensions,
  nonfinite angles, subnormals and three x87 precisions. All returns, declared
  input storage, calling conventions, x87 control words and MXCSR values agree.
  Independently calculated axis-aligned expectations cover 324 of these cases;
  the remaining cases use the unmodified original as their reference.
- The preceding **278 Boss**, **118 damage**, **126 collision** and **126 shield
  calls without transitions**, replayed after actual executable startup. The
  existing emulation and independent observation controls also pass.

The **204 previous prefixes** also pass: 126 collision and 78 shield transitions.
The older `52ec72d` collision control retains its 27 expected payload failures;
the current image retains none. The shield prefixes stop before actual animation
replacement, so they do not test its resource or allocation effects.

The impact fixtures disable scoring and callbacks and use one active circular
source. The geometry fixtures compare returns, input storage, calling convention
and measured floating state; they do not inspect CRT thread-local error storage.
The complete Boss fixtures still exclude due ECL interrupts, real death and
resource startup. These results do not validate whole Boss scripts or grant
exact credit to an incomplete owner.

## Restored trials

Rotation temporaries, coefficient/term order, a vector temporary and a counted
do/while form were evaluated in `Collision.cpp`. None recovered the complete
original rotation layout. The do/while form grew the 661-byte point helper to
664 bytes and added a preserved register. All collision-source trials are
restored. The existing point owner remains mismatch over 661 bytes; the large
rectangle owner remains 2,002 candidate / 2,168 original bytes with unbound
fields. Their behavior in the new matrix is diagnostic evidence only.

Direct sinf/cosf calls in Boss logic generated the same complete body and did
not change the alignment arrangement, so that trial is restored. An explicit
initial bomb-hit conditional likewise generated unchanged damage code and was
restored. Keep the source snapshots and complete packet diagnostics rather than
repeating those forms based on their apparent simplicity.

## Checkpoint

The final incremental build uses PDB age **227** and source input
`232ebb9faea0ff50a81d55437a8c16e86e08e1fbb91361875a4a3e110a42f609`.
The isolated strict replay preserves all classifications: **885 exact, 66
mismatch, 264 incomplete**, with **169,575 exact primary bytes and 951 units**.
The four generated comparison/boundary ledgers are byte-identical to `d6faeac`.
The damage owner remains incomplete; no new exact credit is claimed.
Source-origin review is open and Factory acceptance is not submitted.

Use `final-regression.json`, `complete-scope/`, `final-image/`,
`native-impact-final/`, `native-geometry-final/`, `native-focused-report.json`,
the final collision/shield reports and `native-protocol-controls.json`.
The regression check verifies their common final PE/MAP/PDB/receipt identities,
both historical-image receipts and actual startup stops. Preserve
`rotation-both-native-smoke/` and `rotation-y-sum-native/` as failed protocol and
incomplete-startup evidence; use the final suites for current results.
