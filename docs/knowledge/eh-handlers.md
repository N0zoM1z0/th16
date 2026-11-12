# Empty x86 EH3 handler ownership

Reviewed 2026-11-11 against the canonical Japanese v1.00a target and the pinned
MSVC 19.10.25017 candidate. The two complete parent destructors pass the strict
linked-owner comparison after their private EH graphs are independently bound.
The handlers, descriptors and runtime binding grant no additional primary
function or byte credit.

A later [Enemy destructor review](enemy-empty-eh.md) adds an explicit empty-EH3
profile for a saved EBX/ESI/EDI frame, with cookie displacement minus twenty
independently derived from the complete parent. The default minus-four profile
and its restrictions below remain unchanged.

The [six-parent follow-up](shared-empty-eh-frames.md) applies that unchanged
saved-register profile to Fog, EndingScriptVm, Ending, GuiMsgVm, LoadingThread
and Player destruction. ReplayManager retains its unequal complete extents
and remains excluded.

The [EBX/ESI review](ebx-esi-empty-eh.md) adds one explicit node-16 frame profile
for BulletManager, EffectManager and LaserManager destruction. The complete
registration/save/restore sequence determines its cookie slot; Bomb and
Spellcard frames sharing the displacement remain excluded.

## Original roles and complete scopes

| Parent | Complete parent | Private handler | Complete FuncInfo |
| --- | --- | --- | --- |
| `ItemManagerInner::~ItemManagerInner` | `0x0042F150`, 70 bytes | `0x0048A7E0`, 27 bytes | `0x0049B388`, 36 bytes |
| `StageInner::~StageInner` | `0x00409770`, 73 bytes | `0x0048A430`, 27 bytes | `0x0049AFEC`, 36 bytes |

The Item parent passes the incoming object address, element size `0xC78`, count
`0x1258` and destructor entry `0x0042F1E0` to the complete array-destructor
iterator at `0x00474D11`. This is the `items[0x1258]` member of
`ItemManagerInner`; its two free lists and slowdown scalar require no destructor.
The Stage parent passes `this + 0x310`, size `0x5FC`, count eight and the
`AnmVm` destructor at `0x004093B0` to that same iterator. This identifies
`StageInner::anm_vms[8]`. Both element destructors already have independently
bound, complete comparisons. The iterator already has a reviewed runtime
binding; its differing original/candidate extents remain 94/122 bytes.

Each parent starts with a frame-pointer prologue, state `-1`, its private handler
address, and registration through `fs:[0]`. The handler operand is exactly the
four-byte DIR32 field at parent offset six. The remaining parent linkages are
the security-cookie storage, element destructor and destructor iterator. All
four fields and every other parent byte remain subject to ordinary exhaustive
replay. The complete original parent hashes are pinned in
`config/eh-handlers.toml`, alongside the handler and descriptor hashes.

Both private handlers contain exactly these instructions, ending at the tail
transfer before INT3 alignment padding:

```text
+00 mov edx, [esp + 8]
+04 lea eax, [edx + 12]
+07 mov ecx, [edx - 4]
+10 xor ecx, eax
+12 call @__security_check_cookie@4
+17 mov eax, <this parent's FuncInfo>
+22 jmp ___CxxFrameHandler3
```

The direct call and tail jump have four-byte operands at offsets 13 and 23;
the absolute descriptor operand at offset 18 is the sole PE base relocation.
No instruction, tail or metadata suffix is omitted. These original handler
ranges do not overlap any function in the independent boundary inventory.

The complete descriptors contain nine little-endian 32-bit words:

```text
19930522 00000000 00000000 00000000 00000000
00000000 00000000 00000000 00000005
```

The x86 EH3 layout comprises the magic number, state count, unwind-map pointer,
try-block count and pointer, IP-map count and pointer, exception-specification
pointer, and flags. LLVM's primary
[EH3 table emitter](https://github.com/llvm/llvm-project/blob/main/llvm/lib/CodeGen/AsmPrinter/WinException.cpp)
documents this layout, including the additional unwind-help field for other
architectures. It is format context, not acceptance evidence. Here all counts
and pointers are zero, so there are no unreviewed table tails. The observed raw
flags are preserved as `0x5`; this proof does not require a broader interpretation
of their semantics. Both complete descriptors have SHA-256
`deefb3473c3645d1b0e64473dc4d9122bd804dbeee0601d27662e64da29238e5`.

## Candidate identity

Each parent has one complete same-start public/PDB owner from its actual source
object. Each auxiliary owner must instead be selected from the actual MAP
**Static symbols** section by both its decorated parent-derived name and source
object:

```text
__ehhandler$<parent decorated symbol>
__ehfuncinfo$<parent decorated symbol>
```

The current Item addresses are parent `0x004403E0`, handler `0x0048A820`,
descriptor `0x0049B0E8`; the Stage addresses are parent `0x0046A1C0`, handler
`0x0048AAC0`, descriptor `0x0049B39C`. These candidate addresses are observations,
not fixed selectors. The selectors derive `Item.obj` and `Stage.obj` from
`src/Item.cpp` and `src/Stage.cpp`. The absolute PDB object path must equal this
producer's `build/reference-candidate/obj/src/<name>.obj`, and all three graph
owners must share the same module. MAP section/offset and VA must agree with
the PE. Each handler has one complete 27-byte executable contribution and each
descriptor one complete 36-byte read-only, non-code contribution. Other
contributions and colliding/interior MAP symbols are rejected. Missing,
duplicate, extra and crossing relocation records are rejected.

The two descriptors have identical contents. A content match alone cannot bind
one to a parent: the handler's EAX operand must point to that parent's exact
qualified `__ehfuncinfo$` owner. A mutation redirecting it to the other identical
descriptor is rejected. Both original and candidate handlers must also contain
the complete reviewed runtime-call graph and parent registration pattern.

## Runtime entry review

The new `___CxxFrameHandler3` binding selects the complete original 54-byte
function at `0x00475D37` and one complete 54-byte candidate contribution at
`0x00475D46`. The candidate comes from `libvcruntime.lib`, module
`trnsctrl.obj`, in the pinned MSVC library directory. The original boundary was
already present in `config/functions.csv`; no extent was shortened.

The pinned local CRT source
`.tools/toolchain/vs/VC/Tools/MSVC/14.10.25017/crt/src/i386/trnsctrl.cpp`
defines the naked `__CxxFrameHandler3` entry, receiving `FuncInfo` in EAX.
Both complete native bodies save EAX, pass it with the four frame/exception
arguments and three zero arguments to the internal frame handler, restore the
saved registers, and return. Both full 54-byte payloads have SHA-256
`21fe2a7f37efbf61d3db3eb3a8717d0d67da0bb83b178064e1b3064249338b88`.
The internal runtime implementation is not awarded exact credit. The cookie
check entry is covered by its existing reviewed binding.

## Oracle limits and controls

The default profile in `scripts/eh_identity.py` supports only explicitly
reviewed empty EH3 descriptors and this complete 27-byte GS handler. These two
records are parent/source scoped.
The manifest field must exactly equal the reviewed offset-six DIR32 binding,
with zero addend and `eh_handler = true`. It cannot substitute a local, an
interior pointer, another parent, another source, a storage override, or an
arbitrary private symbol. Static owners are never inserted into the public
symbol list or the audit's global binding map. Other descriptor or handler
shapes are not accepted by this default profile. Configuration and verifier
source are part of the Oracle input fingerprint.

The later [AnmManager constructor review](anm-constructor-eh.md) adds a separate,
explicit five-state profile with complete 136-byte code and 76-byte metadata
PDB owners. The empty-EH3 profile retains its standalone-owner restrictions;
it does not accept that aggregate. The complete constructor now compares as a
5,054/5,071-byte mismatch, with no additional exact credit. No generic nonempty
unwind, try-block or interior-entry support is implied.

The 25 controls in `scripts/test-eh-identities.py` cover both positive complete
parent replays, all target hashes, PDB ownership and extent failures, MAP
ambiguity, section permissions, handler instructions, identical foreign
descriptors, every descriptor word, relocations, parent registration, runtime
dependencies and field-scope overrides. Changing the Item count byte still
produces a full 70-byte mismatch after successful EH review. There are no
masks, hand-authored handler bytes in game source, artificial locals or
shortened owners.

Retained ignored evidence:

- `.analysis/eh-reviewed-graph-evidence.json`: full native parent/handler bytes,
  disassembly, complete descriptor payloads, runtime owner and Oracle identity.
- `.analysis/eh-focused.json`: two complete primary comparisons and auxiliary
  ownership proofs.
- `.analysis/eh-identity-controls.log`: mutation-control results.
- `.analysis/eh-full-audit.log` and `.analysis/eh-regression-check.json`: broad
  replay and retained-pass comparison.

These are local reconstruction results. Source-origin review remains open,
`config/implemented.csv` has no implemented entries, and Factory acceptance
has not been submitted or activated.
