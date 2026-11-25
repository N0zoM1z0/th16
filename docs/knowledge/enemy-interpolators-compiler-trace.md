# Enemy interpolation stack packing and camera operands

`EnemyData::step_interpolators` at `0x41bb50` now passes the complete local
strict comparison: 1,692 bytes, 421 instructions and 48 independently bound
linked fields. The retained camera update uses ordinary scalar additions and
a real reference to its Y destination field, without volatile reads. The
focused final report also preserves both completed curve owners:
`.analysis/enemy-interpolators-compiler/enemy-interpolators-final-strict.json`.

At starting source checkpoint `fa2eb92`, the owner matched 1,668 bytes.
Every one of the 24 differing bytes was a frame allocation or stack
displacement. The candidate reserved 0x48 bytes; the target reserved 0x38.

The investigation uses the pinned v141 C2 compiler, version 14.10.25017,
SHA-256 `3ca2a4f245e00b4535e6b6845274ea064a68f68d89b0339a71f2f0f73e0d7458`.
Private traces, disassemblies, source controls and complete comparisons are
under `.analysis/enemy-interpolators-compiler/`. These local comparisons do
not constitute Factory acceptance; the current shared snapshot is inventory-only.

## A later volatile read prevents earlier temporaries from sharing

The baseline camera helper has two volatile scalar reads: the camera Y delta
and the destination Z component. They enforce the intended component operand
order locally, but also affect the stack allocator elsewhere in this owner.
The two radial-result locals and the absolute/relative position-return buffers
therefore need to be investigated together with the later camera update.

`StackPack::StkStackAlloc` (RVA `0x1dc019`) enumerates 15 objects. Vertices
7 and 8 are the two 8-byte radial results. Vertices 13 and 14 are the two
12-byte return buffers for `InterpStrange1::step`; the position interpolators
are not `InterpFloat3`. Vertex 6 is an anonymous 4-byte object whose semantic
role has not been established. The baseline interference matrix makes these
five vertices mutually incompatible. The radial pair gets separate colors,
and the relative position return needs another 12-byte color.

A hardware watch on the sparse bit-vector masks catches the edge creation in
`SbvOr` (RVA `0xb65b0`, low-mask write at `0xb65f5`). Its caller is
`StackPack::ComputeLiveOnDef`, with the call at `0x1da634`. Inspecting that
caller's current IR tuple identifies a float move (`0x125`) reading the
volatile destination Z field. Its memory flags are `0x50` and PAS ID is
`0x11c`. The later camera expression thus causes an observable earlier-buffer
packing constraint; changing the radial declarations alone does not address it.

Removing only the Z volatile cast removes one direction of the relation, but
the remaining volatile Y read still creates other edges. That complete trial
matches 1,658 / 1,692 bytes and keeps the 0x48 frame. The interference matrix
can be asymmetric, so the absence of a single directed edge is insufficient
proof that two objects can share.

Removing both casts removes the cross-edges among vertices 7, 8, 13 and 14.
Each radial result now uses ESP+0x18 and both position-return buffers use
ESP+0x20. The frame is 0x38 and every original stack difference disappears.
The complete comparison improves to 1,682 / 1,692 bytes; only the camera Y
addition's input order differs. Ordinary native body SHA-256 is
`9f0bf7107844e188184724f7504132e2535b80b8e5a23df14642c7b717fb60d6`.

Read-only debugger replays reproduce the entire ordinary owner for the
baseline, Z-only and both-plain controls. Preserve `baseline-stackpack-*`,
`baseline-edge-watch-*`, `baseline-edge-source-*`,
`plain-camera-z-stackpack-*`, `plain-camera-z-edge-source-*` and
`plain-camera-all-stackpack-*`, including their control JSON and normal-exit
GDB logs. The baseline body SHA-256 is
`44eaf66622a42ca7fdbdb6715ac2c0e9d0138e0be782cb2921caaa0b63313a35`;
the Z-only body is
`939446a324880283afddea36993c079dc3b013a52eb57c60eb5372a0a977ddf2`.

## Reading the compiler structures correctly

For this compiler, StackPack+0x0c holds the element count, +0x10 the matrix
row-pointer array and +0x34 the symbol array. Each sparse bit vector starts
with a node pointer; a node contains base index, low mask, high mask and next
pointer. The base index is a multiple of 64. Mode byte +0x18 is zero in this
owner, selecting the local-liveness/LiveOnDef path.

A backend symbol's +0x20 is its ordinal, +0x24 its byte size and +0x40 its
vertex index. After coloring, +0x1c points to a color record, not another
backend symbol. These automatic objects are kind 4: their final stack offset
is at frontend-symbol+0x18, reached through backend-symbol+4. Backend+0x2c
is the offset for kind 3 temporaries and remains zero for these objects.
Reading it would falsely suggest that no offsets had been allocated.

The public-symbol JSON stores RVAs. Derive addresses from that metadata and
the actual loaded C2 base. An initial probe accidentally used `0x165b0` for
SbvOr instead of `0xb65b0`; its lack of events says nothing about edge
creation. That failed probe is retained separately as `baseline-edge-origin`.

## Camera Y ordering after the stack repair

The target loads the global Y delta before adding the destination Y field.
The plain candidate loads the destination first. This exchanges ten encoded
bytes at offsets 879 through 888 without changing the owner extent. X and Z
already have the correct destination-first order.

A used Y accumulator inside the inline helper is byte-neutral. Moving the
camera calculation into the caller with explicit position/delta pointers and
a caller-owned Y accumulator is also byte-neutral. These controls preserve
the repaired stack frame but fail to close the owner; the later
canonicalization and lowering determine the emitted order.

The caller-accumulator trace explains that failure. At the second
canonicalization, Y is a memory load through temporary base `0x3ea` with key
`0x18008`; the global Y leaf has key `0x10620`. Descending order puts the
position first. The earlier caller-local key `0x10220` is no longer used.
X keeps the named position base (ordinal `0xf`, memory key `0x1e008`); Z uses
temporary `0x3f1`, key `0x14008`, also above its global key `0x10640`.

Unlike the non-temporary symbol case in the curve investigation, a kind-3
temporary address hashes its ordinal shifted left six bits (`OptHashNode`,
RVA `0xd7e2e`). The zero-offset memory case then shifts that hash another eight
bits and retains 16 bits. Its key is therefore
`0x10000 | ((8 + (ordinal << 14)) & 0xffff)`. Only two low ordinal bits survive.
This accounts for the measured Y and Z keys and identifies the later address
temporary, rather than the earlier accumulator name, as the relevant object.
Keep `caller-camera-y-canonical.jsonl` and its complete normal-exit control;
they reproduce the same 1,692-byte body as the ordinary candidate.

The three direct scalar `+=` updates remove the separate Y accumulator but
produce the same body. Their traced Y address ordinal is `0x3ca`, 32 below
`0x3ea`, retaining the same `0x18008` key. The completed read-only replay
reproduces all ordinary bytes. A standard SDK vector `operator+=` control
instead matches 1,673 / 1,692: it also reverses X, while preserving the frame.
Neither control is an improvement. Preserve `caller-camera-components-*`
and `sdk-camera-compound-*`.

This follows the useful distinction in TH10's ECL VM investigation: source
symbol ordering and later temporary ordering can cross different hash wraps.
TH09's movement study likewise follows the replacement load through allocation
and scheduling instead of assuming an early source read survives. TH075's
Meiling Advance controls demonstrate why later source paths must remain in
the compared owner: a later continuation changes the scratch-register cursor
at an earlier reload. These are methodological references; their VC7.1
addresses and thresholds do not apply to this v141 compiler.

## Closing with an actual field reference

The retained camera branch binds its position pointer, then a reference to
the destination Y field, then the delta pointer. Each component is updated
with ordinary scalar `+=`. The reference is read and written by the real Y
addition; it is not an extra stack buffer or a volatile access.

In the final read-only trace, the Y memory operand retains named address
`_y`, ordinal `0x10`, through lowering. Its key is `0x10008`, below the global
Y leaf's `0x10620`, so the global sorts first. The named position pointer
still has ordinal `0xf` and key `0x1e008`, keeping X destination-first.
Z uses kind-3 temporary `0x3d1` with key `0x14008`, also retaining its correct
order. This replaces the problematic temporary Y address with a named field
address whose surviving hash bits predict the target order.

The same completed replay records no cross-edges among stack vertices
7, 8, 13 and 14. The radial pair both have frame offset -40, and the
position-return pair both have -32, giving the target ESP+0x18 and ESP+0x20
slots after the 0x38 allocation and two saved registers. The reference does
not undo the stack-sharing repair.

`camera-y-reference-final-control.json` verifies that this unmodified-compiler
replay exited normally and reproduces the entire ordinary 1,692-byte owner,
SHA-256 `6523c2fbc670da7c86475a5f52090dd338be404d14bb3f2f649a1d95f8c32ed9`.
Preserve `camera-y-reference-canonical.jsonl`,
`camera-y-reference-stackpack.jsonl`, the final debugger image/map/log and
`Enemy.cpp.camera-y-reference`. The final focused strict report passes the
interpolation owner and both previously closed curve owners. No cold build
or broad replay was needed.
