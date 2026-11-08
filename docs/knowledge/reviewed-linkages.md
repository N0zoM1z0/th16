# Reviewed shared linkage identities

These bindings apply to the original Japanese TH16 v1.00a target with SHA-256
`c11776019f083978e66027e7394dafb1fb9543afca986f28049a49417e341929`.
The machine inputs are `config/linkage-bindings.csv`.

## Runtime entry points

| Candidate symbol | Target | Complete extent | Identification evidence |
| --- | --- | ---: | --- |
| `@__security_check_cookie@4` | `0x0047499B` | 17 | ECX is compared with the PE load-configuration security cookie at `0x0049EA4C`; failure jumps to the identified GS failure routine. |
| `___report_gsfailure` | `0x00474F5D` | 251 | Independent Ghidra runtime identification and the complete failure-reporting entry used by the security check. |
| `??2@YAPAXI@Z` | `0x004749AC` | 51 | Ghidra identifies operator new; target disassembly contains allocation retry, new-handler and allocation-exception paths. |
| `??3@YAXPAXI@Z` | `0x004749DF` | 14 | Sized scalar delete forwards its pointer to the adjacent unsized-delete entry at `0x0047514B`; the unused size argument is preserved by the call contract. |
| `_memset` | `0x00477920` | 346 | Independent Ghidra library identification and target disassembly of the byte-fill implementation with ISA-dispatch paths. |
| `??3@YAXPAX@Z` | `0x0047514B` | 5 | The sized-delete call at `0x004749E5` reaches this unsized-delete thunk. |
| `_malloc` | `0x00477FA7` | 11 | The allocation call at `0x004749D3` in operator new reaches this entry. Its prologue precedes a tail jump to the base allocator. |
| `_free` | `0x00477FB2` | 5 | The unsized-delete jump at `0x0047514B` reaches this UCRT thunk. |
| `__free_base` | `0x0047BCB2` | 58 | The free jump at `0x00477FB2` reaches the null-checked HeapFree implementation with GetLastError and errno handling. |
| `__malloc_base` | `0x0047BCEC` | 78 | The malloc jump at `0x00477FAD` reaches the size-checked HeapAlloc implementation with new-mode retry and errno handling. |
| `_memcpy` | `0x00487130` | 1396 | The original reads destination/source/count from its three cdecl arguments, copies count bytes with scalar, SSE and `rep movsb` paths, handles overlap and returns the original destination. The pinned vcruntime candidate has a complete 1396-byte PDB contribution. |
| `??_L@YGXPAXIIP6EX0@Z1@Z` | `0x00474CA8` | 79 | Independent Ghidra EH vector constructor iterator; increments the object pointer by its stride, calls the constructor through argument four with the object in ECX, tracks constructed elements for unwind, and returns with `ret 0x14`. Candidate LIBCMT contribution: 105 bytes. |
| `??_M@YGXPAXIIP6EX0@Z@Z` | `0x00474D11` | 94 | Independent Ghidra EH vector destructor iterator; starts at array + stride * count, walks backward, calls the destructor with the object in ECX, and returns with `ret 0x10`. Candidate LIBCMT contribution: 122 bytes. |
| `__chdir` | `0x00479A65` | 11 | The entry tail-jumps to Ghidra-identified `common_chdir<char>` at `0x00479928` (229 bytes). Its callers include both directory selections in `Supervisor::load_game_config`. The candidate public belongs to the pinned UCRT library. |
| `__libm_sse2_cos_precise` | `0x00488300` | 440 | The SSE2 entry's fallback call at `0x004884A7` reaches `0x0048913F`, whose original instructions execute `fcos` at `0x0048915D` and `0x00489194`. The candidate PDB records the complete 440-byte UCRT contribution. |
| `__libm_sse2_sin_precise` | `0x004884C0` | 453 | The SSE2 entry's fallback call at `0x00488674` reaches `0x0048926F`, whose original instructions execute `fsin` at `0x0048928D` and `0x004892C4`. The candidate PDB records the complete 456-byte UCRT contribution. |
| `__libm_sse2_sqrt_precise` | `0x00488690` | 254 | Independent Ghidra identification and the complete SSE2 square-root implementation, including MXCSR/x87 environment checks and the fallback path. Its pinned UCRT candidate contribution is 256 bytes. |

Every entry checks its complete target extent and candidate PDB extent. The candidate
PDB must name the pinned Microsoft `LIBCMT.lib`, `libvcruntime.lib` or UCRT
`libucrt.lib`, as specified in the table input. UCRT ownership is checked against
the separately pinned Windows SDK library path. The target extent hash is
checked before use. These records
establish reviewed external linkage identities; they do not grant a separate
exact-code claim to each runtime implementation.

The square-root helper has separately recorded target and candidate sizes. Both
complete extents are mandatory: the original independent function is 254 bytes,
while the candidate PDB contribution includes a trailing two-byte `mov edi, edi`
after the final return. The `candidate_size` column records 256 rather than
truncating that contribution. The target hash covers all 254 declared bytes.
Tests reject either truncated extent. This entry identifies an external callee;
its differing physical extents do not receive a callee exact-code claim.

The memcpy implementation is identified from the whole copy algorithm and
cdecl contract, not from a presumed exact Crypt caller. Its original entry
loads source, count and destination at `0x00487132`, `0x00487136` and
`0x0048713A`. The overlap checks select a backward path at `0x004873E4`;
the forward `rep movsb` path at `0x0048717E` returns the original destination
from the argument slot. Other paths implement the same byte-counted copy.
The fixed incoming call in `zun_decrypt` is at `0x00402282`. Only `_memcpy`
is a public at the candidate's start; no interior alias is manufactured.

The vector iterators are independently named in the original Ghidra inventory.
Their constructor/destructor direction, stride/count arguments, indirect ECX
calls and callee stack cleanup agree with the mangled candidate contracts.
Their complete original extents differ from the pinned candidate contributions;
the differing sizes are explicit and do not grant exact runtime-code credit.
The internal unwind funclets and EH records are not separately bound by these
entries. An implicit game destructor still needs its own exception metadata
and handler proof even after its iterator destination is known.

The sine and cosine identities come from the original fallback instructions,
not from upstream labels or operands selected to match their consumers. Both
SSE2 entries use the table at `0x00497E10`; their index biases differ by 16
entries, consistent with a quarter-cycle phase shift. Their environment checks
and XMM0 double input/output contract agree with the candidate UCRT entries.
The game wrappers at `0x00405510` and `0x004054F0` widen float input, call sine
and cosine respectively, then narrow the result. These observations corroborate
the fixed identities. The sine candidate's complete 456 bytes are checked
separately from the original's 453; neither is shortened for an exact claim.

The ignored context evidence is `.analysis/math-fallback-context-function.txt`
and `.analysis/math-fallback-context-decompile.txt`; direct Capstone decode
confirms the hardware opcodes. A bounded numeric probe was attempted but refused
to execute because Wine's startup mappings occupied original addresses in this
non-relocatable target. It produced no numeric evidence and is retained only in
`.analysis/math-entry-identity.cpp` and its failure log. These bindings rely on
the static fallback proof above.

The directory-changing child is not a candidate public in this link. Its
independent name and directory-selection callers identify the eleven-byte root;
no public or exact claim is invented for the internal child.

The five allocator entries also carry fixed incoming call/jump witnesses. The
checker decodes the complete reviewed parent, requires the witness to start an
instruction, and requires its direct destination to equal the declared entry.
Mutation tests reject a different call, an interior instruction byte, a missing
parent and the wrong library. Complete five-byte free/delete thunks and the
eleven-byte malloc thunk are independently replayed with exhaustive REL32 fields.

The base allocator and deallocator both use the process-heap global at
`0x004A6D54`, but that observation does not create an automatic binding for the
heap or for their error-handling callees. Unreviewed fields remain incomplete.

## Literal storage witnesses

Equal payloads elsewhere do not make storage interchangeable. The following
locations were reviewed through fixed instructions in separate target functions:

| Symbol / value | Storage | Instruction witness | Source meaning |
| --- | --- | --- | --- |
| `__real@3f800000` / 1.0f | `0x004944D8` | `0x00402CDC`: `subss xmm0, [0x004944D8]` | `Rng::randf_neg_1_to_1` subtracts 1.0f after scaling its random integer. |
| `__real@3f000000` / 0.5f | `0x0049449C` | `0x004034D2`: `mulss xmm3, [0x0049449C]` | The interpolation helper applies the half-scale term of its in/out curves. |
| `__real@41800000` / 16.0f | `0x004945E0` | `0x00406564`: `addss xmm0, [0x004945E0]` | The jagged-line initializer adds the 16-pixel vertical offset. |
| `__real@00000000` / 0.0f | `0x004943C0` | `0x00403199`: `addss xmm0, [0x004943C0]` | PosVel's polar-position update adds the helper's zero z component. |
| `__real@40000000` / 2.0f | `0x00494558` | `0x004034E1`: `movss xmm1, [0x00494558]` | The quadratic interpolation curve loads its 2.0 term. |
| `__real@40400000` / 3.0f | `0x00494584` | `0x0040703C`: `movss xmm0, [0x00494584]` | `InterpFloat3::step` loads the cubic interpolation coefficient. |
| `__real@43000000` / 128.0f | `0x00494644` | `0x00407473`: `movss xmm3, [0x00494644]` | `anm_on_draw_masked` constructs the masked rectangle. |
| `__real@3c000000` / 1/128 | `0x004943F4` | `0x0040E7CC`: `mulss xmm0, [0x004943F4]` | `BombAyaAInf::begin` scales the player's horizontal movement for bomb angle and speed. |
| `__real@43e00000` / 448.0f | `0x004946B0` | `0x0040AB51`: `addss xmm7, [0x004946B0]` | `StdObject::is_culled` adds the vertical playfield extent. |
| `__real@42c80000` / 100.0f | `0x00494638` | `0x00403379`: `mulss xmm0, [0x00494638]` | `PosVel::step` scales a coordinate before floor/division to snap it to hundredths. |
| `__real@43600000` / 224.0f | `0x00494670` | `0x00415A2C`: `movss xmm0, [0x00494670]` | `Bullet::bounce_top` constructs the top limit as playfield midpoint minus half the bounce height. |
| `__real@43f00000` / 480.0f | `0x004946BC` | `0x0042D27C`: `movss xmm1, [0x004946BC]` | `GameThread::~GameThread` positions the now-loading indicator at x = 480. |
| `__real@41200000` / 10.0f | `0x004945CC` | `0x00408722`: `movss xmm6, [0x004945CC]` | `AsciiInf::draw_string` selects the small font's ten-pixel line height. |
| `__xmm@7fffffffffffffff7fffffffffffffff` / two double sign masks | `0x00494880` | `0x0040524A`: `andps xmm0, [0x00494880]` | `zun_fabsf` clears the widened floating-point sign bit. The witness reads the entire 16-byte literal. |

The loader checks each entire typed payload in both images, the fixed target
instruction mnemonic, absolute operand, operand width and payload hash. It does
not select a different equal-valued location for another caller. Every consumer
still undergoes complete PDB-owner and byte/relocation replay.

The decimal format literal `%d` (including its terminating NUL, three bytes) is
bound separately to `0x00491C7C`. Its candidate public is
`??_C@_02DPKJAMEF@?$CFd?$AA@`. The fixed push at `0x004082DD` in
`AsciiInf::create_number` witnesses the target storage address. The checker also
requires exactly one same-start, non-code PDB contribution of three bytes, an
MSVC narrow-string public, a final NUL with no interior NUL, and equal complete
payloads in both images. This avoids treating other occurrences or suffixes of
`%d` as interchangeable. Truncating the storage proof or changing the push
witness is rejected.

The unsigned-conversion table is bound at `0x00494850`:
the two doubles are 0.0 and 4294967296.0. In `Rng::randf_0_to_1`, the fixed
instruction at `0x00402C87` reads one eight-byte element with `eax * 8` after
`shr eax, 31`. The candidate symbol is
`__xmm@41f00000000000000000000000000000`. Its `indexed-literal` proof requires
the complete encoded 16-byte value in both images and one complete candidate
PDB storage contribution. The checker decodes from the unique independent
target owner, requires a preceding adjacent 32-bit logical shift by 31 into the
same index register, an eight-byte operand, an eight-byte stride and no base
register. Thus either possible index selects exactly one complete double in
the declared storage. The supported operation is specifically `addsd`.

Mutation tests reject a shift by 30 (four possible elements), arithmetic shift,
different shifted/index registers, four-byte stride, an instruction-interior
witness, a truncated value and an incomplete PDB storage contribution. This
adds a bounded table proof; it does not make arbitrary indexed operands eligible.

## PDB global-object ranges

MSVC's DBI section contributions may group several global objects. That does not
provide a same-start extent for an interior access to `g_Supervisor` or
`g_CriticalSections`. The new reader uses the PDB's S_GDATA32 TypeIndex and TPI
records to establish the actual complete global-variable storage size.

The current PDB contains 334 supported typed global records. Structure sizes for
67 records were independently cross-checked against LLVM 18's PDB dump, including
Supervisor (2624), CriticalSections (352), Globals (1120), InputGlobals (564) and
GameWindow (8420). Unknown leaves and forward declarations remain unsupported.

Each interior binding records its exact type name and size. The strict checker
re-reads the PDB, requires a unique matching public and type record, checks the
addend against that storage, and checks mapped non-code target storage. Removing
the proof or changing its size is rejected. This supplies the missing storage
evidence without masking unknown addresses or expanding a global to the next
convenient symbol.

## Derived field-cursor limits

`AnmManager::draw_sprite_fog` at `0x00467200` walks the alpha bytes of the four
28-byte vertices in `g_sprite_temp_buffer`. The independent target base is
`0x004DF830`; the PDB establishes 112 bytes of candidate storage. The cursor
starts at byte 19, advances by 28, and compares against base + 112 + 19.
Its final comparison immediate is `0x004DF8B3`. That computed limit is not
dereferenced.

In the candidate layout this address coincides with `g_arcfiles + 3`, while the
original globals are unrelated. Choosing the nearest preceding public therefore
bound the comparison to the wrong target global. Its two differing address
bytes were a binding error rather than an instruction difference.

The producer now recognizes this bounded cursor form from candidate code and
the previously bound, typed initializer. It derives the limit from the original
initializer's fixed object base, complete PDB storage size and field offset;
it never chooses the original comparison operand to make a match. The manifest
records `pointer_limit = true`, and the checker independently re-derives it.

The supported proof requires a nonvolatile register initialized by a bound
immediate, one positive constant increment, a signed-less-than backedge, an
acyclic loop body, no edge bypassing initialization and no escaped cursor.
Every cursor-relative memory operand must fit inside the real object for all
iterations. The old cursor must be discarded or reset after the loop. Calls
must have a supported preservation contract: decorated
stdcall imports or the specifically reviewed SSE2 square-root helper. Counted
secondary loops, unknown callees and implicit cursor uses are rejected.

Ordinary data addends still must remain inside their typed storage. A computed
limit is eligible only as the proven comparison immediate; putting the flag on
a memory access does not authorize it. Thirteen controls include complete
522-byte replay, the wrong-neighbor mismatch, missing proof, wrong addend,
wrong stride, wrong backedge, bypassing initialization or the limit, escaped
cursor, out-of-bounds store and missing callee preservation evidence. No candidate or
target extent is truncated or expanded for this result.
