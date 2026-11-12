# Reviewed shared linkage identities

These bindings apply to the original Japanese TH16 v1.00a target with SHA-256
`c11776019f083978e66027e7394dafb1fb9543afca986f28049a49417e341929`.
The machine inputs are `config/linkage-bindings.csv`.

The subsequent [stage/time review](stage-time-identities.md) adds the complete
66-byte current-time entry and an explicit complete 1,696-byte stage-table
identity. Table initialization and every string/relocation are independently
checked; no generic mutable-data binding is enabled.

The subsequent [numeric storage review](menu-literal-identities.md) adds seven
fixed typed literal witnesses for values with duplicate original payloads. It
also records complete consumer outcomes and rejected music-room source trials.

The subsequent [replay/numeric review](replay-literal-identities.md) adds fixed
176.0f/512.0f reads and a complete `%3d` format with an original PUSH witness.
It preserves refusals for private exception-handling code and differing owners.

The subsequent [timing/collision/audio review](timing-literal-identities.md)
adds eight original scalar reads and nine complete passes. The
[COMISD review](comisd-literal-identities.md) adds three double reads and a
guarded correction for the decoder's m128 report of an encoded m64 read.

The subsequent [conversion-runtime review](conversion-runtime.md) establishes
the complete 887-byte code and 130-byte data contributions behind two fixed
internal CALL entries. The ordinary 206-byte `__except1` identity is also
reviewed. These bindings grant no primary credit to runtime code or data.

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
| `_strrchr` | `0x00476B20` | 311 | Scalar fallback finds the NUL, then scans backward with `std`/`repne scasb` and clears DF before returning; SSE paths retain the last match. Both slash searches in `file_read_all` call this root. Pinned vcruntime contribution: 311 bytes. |
| `_strchr` | `0x00476C60` | 299 | Scalar paths return the first matching byte or NULL at the terminator; SSE combines match/NUL masks and selects the first bit. Dialogue comma parsing calls this root. Pinned vcruntime contribution: 299 bytes. |
| `__stricmp` | `0x0047A60A` | 72 | Independent Ghidra identification; the no-locale tail reaches `___ascii_stricmp`, folding ASCII A-Z and comparing bytes until NUL or difference. Pinned UCRT contribution: 72 bytes. |
| `__localtime64` | `0x0047A36A` | 39 | Root obtains thread-local tm storage and calls `0x0047A0E0`. That complete 649-byte child reads both words of the time, calls `___tzset`, applies timezone/DST and fills nine tm fields. Pinned UCRT contribution: 39 bytes. |
| `??_U@YAPAXI@Z` | `0x00475142` | 9 | Array-allocation root tail-jumps to the reviewed scalar operator new at `0x004749AC`; archive allocation computes an array size with a count cookie before calling it. Pinned LIBCMT contribution: 9 bytes. |
| `__chdir` | `0x00479A65` | 11 | The entry tail-jumps to Ghidra-identified `common_chdir<char>` at `0x00479928` (229 bytes). Its callers include both directory selections in `Supervisor::load_game_config`. The candidate public belongs to the pinned UCRT library. |
| `__libm_sse2_cos_precise` | `0x00488300` | 440 | The SSE2 entry's fallback call at `0x004884A7` reaches `0x0048913F`, whose original instructions execute `fcos` at `0x0048915D` and `0x00489194`. The candidate PDB records the complete 440-byte UCRT contribution. |
| `__libm_sse2_sin_precise` | `0x004884C0` | 453 | The SSE2 entry's fallback call at `0x00488674` reaches `0x0048926F`, whose original instructions execute `fsin` at `0x0048928D` and `0x004892C4`. The candidate PDB records the complete 456-byte UCRT contribution. |
| `__libm_sse2_sqrt_precise` | `0x00488690` | 254 | Independent Ghidra identification and the complete SSE2 square-root implementation, including MXCSR/x87 environment checks and the fallback path. Its pinned UCRT candidate contribution is 256 bytes. |
| `__chkstk` | `0x00487100` | 45 | Ghidra independently identifies `__alloca_probe`. The complete routine takes the allocation size in EAX, touches each descending 4096-byte stack page, moves ESP and preserves the return address. Candidate `LIBCMT:chkstk.obj` has same-start `__chkstk` and `__alloca_probe` aliases in one complete 45-byte contribution. |
| `__beginthreadex` | `0x0047952B` | 133 | Independent Ghidra identification; validates the user entry, allocates a CRT thread context, calls the imported `CreateThread` with a CRT startup wrapper, copies out the thread ID and releases context ownership on success. Pinned UCRT `thread.obj` contribution: 133 bytes. |

Every entry checks its complete target extent and candidate PDB extent. The candidate
PDB must name the pinned Microsoft `LIBCMT.lib`, `libvcruntime.lib` or UCRT
`libucrt.lib`, as specified in the table input. UCRT ownership is checked against
the separately pinned Windows SDK library path. The target extent hash is
checked before use. These records
establish reviewed external linkage identities; they do not grant a separate
exact-code claim to each runtime implementation.

The stack-probe entry subtracts the EAX allocation request from the incoming
stack position, saturating underflow to zero. The loop at `0x00487124` descends
by `0x1000` and touches each page with `test [eax], eax`. At `0x0048711C` it
exchanges ESP with the computed destination, transfers the saved return address
and returns on the allocated stack. This distinguishes the entry from the
separately bounded 8-byte and 16-byte alignment wrappers at `0x00487026` and
`0x00487010`. The two candidate aliases share the same start; neither is an
interior entry. Their single PDB contribution and the original independent
boundary both cover all 45 bytes. The original large-frame prologue at
`0x004029D3` requests `0x2008` bytes and calls the entry at `0x004029D8`, which
corroborates the EAX allocation contract.

The thread entry calls the original PE import `KERNEL32!CreateThread` through
IAT slot `0x0048B0E4` at `0x00479574`. Its six arguments include the CRT wrapper
at `0x0047934B` and a context produced from the user's entry and argument by
`0x00479456`. A null user entry sets errno to `0x16`; failed thread creation
retrieves `GetLastError` through IAT slot `0x0048B08C` and releases the context.
On success it writes the thread ID through argument six and transfers context
ownership to the new thread. The original Ghidra name corroborates this full
ABI and control flow. Internal context helpers and the startup wrapper are not
assigned candidate bindings by this entry.

The original `floor` root at `0x00488A00` remains unbound. Its independent
Ghidra extent is 2991 bytes, including distant fallback code and other runtime
entries, while the candidate `floor_pentium4.obj` contribution is 253 bytes.
The apparent fast-path return at `0x00488AFC` does not establish a complete
253-byte original boundary: the root branches to `0x004894F6`. Do not truncate
the original extent or infer a replacement boundary from the candidate.

The square-root helper has separately recorded target and candidate sizes. Both
complete extents are mandatory: the original independent function is 254 bytes,
while the candidate PDB contribution includes a trailing two-byte `mov edi, edi`
after the final return. The `candidate_size` column records 256 rather than
truncating that contribution. The target hash covers all 254 declared bytes.
Tests reject either truncated extent. This entry identifies an external callee;
its differing physical extents do not receive a callee exact-code claim.

The two byte-search routines are independently distinguished by their complete
algorithms. In the reverse entry, `0x00476C36` finds the terminator and
`0x00476C43` sets backward direction for the search; `0x00476C53` restores
forward direction. Its SSE2 path uses the last set match bit, whereas the
forward entry uses the first match/terminator bit and rejects a terminator
that differs from the requested character. Neither identity comes from choosing
a destination that would pass a consumer. Original calls `0x00402478` and
`0x00402488` search for backslash and slash. The comma-search call at
`0x0042A544` was decoded from its independent original owner start, rather than
from an arbitrary instruction-interior address.

The case-insensitive root's ASCII child is independently named at `0x0047A5CF`
(59 bytes). Instructions at `0x0047A5E0` and `0x0047A5EF` test the A-Z range,
adding 0x20 before comparing. The root retains locale dispatch and null/error
handling; its complete extent is not reduced to this child.

The time wrapper was auto-labelled `FID_conflict:common_gmtime<long>`. That label
is not used as authority. Its actual child at `0x0047A0E0` reads both 32-bit
words, checks the 64-bit supported range, calls `___tzset`, applies timezone
and daylight-saving offsets, and sets `tm_isdst`. This establishes local 64-bit
time conversion, with secure output validation. The root calls this child at
`0x0047A37F`; its allocation/error handling converts the child's status to a tm
pointer or NULL. The child and ASCII-comparison context are retained in
`.analysis/time-string-runtime-context-function.txt` and
`.analysis/time-string-runtime-context-decompile.txt`. The 649-byte child is
not separately granted a runtime exact claim or a fabricated candidate public.

The array-new entry preserves the size argument and returns through the scalar
allocator's ABI. The original archive call at `0x00457500` allocates
`(count + 1) * 16 + 4`, including overflow checks and the array count cookie,
before invoking element construction. This corroborates its array-allocation
role. Its separate fixed entry is retained, even though its implementation
forwards to an already reviewed allocator.

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

## Primary vftable identities

The following address points are independently identified through original RTTI and
complete virtual-function contracts:

| Class | Original address point | Slot bytes | Complete candidate object |
| --- | --- | ---: | ---: |
| `ThreadInf` | `0x00491C34` | 4 | 8 bytes, including its locator pointer |
| `Pbg::File` | `0x00493768` | 36 | 40 bytes, including its locator pointer |
| `LaserDataInf` | `0x00492490` | 104 | 108 bytes, including its locator pointer |
| `LaserLineInf` | `0x00492424` | 104 | 108 bytes, including its locator pointer |
| `LaserInfiniteInf` | `0x004923B8` | 104 | 108 bytes, including its locator pointer |
| `LaserCurveInf` | `0x004922E0` | 104 | 108 bytes, including its locator pointer |
| `LaserBeamInf` | `0x0049234C` | 104 | 108 bytes, including its locator pointer |

These are `vftable` records in the linkage table. Their hashes cover every
original slot byte. The preceding locator pointer and all supporting RTTI
records are separately parsed and validated; the four-byte prefix is included
in the complete candidate PDB storage extent, not discarded as padding.

ThreadInf's sole slot is its scalar deleting destructor at `0x00402EF0`.
Pbg::File's nine slots are open (`0x00457700`), close (`0x00457850`), read
(`0x00457880`), write (`0x004578C0`), tell (`0x00457900`), get_size
(`0x00457920`), seek (`0x00457940`), scalar deleting destructor (`0x004576B0`)
and read_whole (`0x00457970`). These fixed function identities are checked
against the original entries and candidate PDB owners; the checker does not
select a target from the operand of the constructor being compared.

The five laser tables each have 26 callable slots and no virtual destructor
slot. Their layout is independently corroborated by the original RTTI and the
full class contract: point sampling, ex execution, method_8, initialization,
tick/draw/destroy, rectangle damage, rectangle/circle/full cancellation,
method_2c, circle contact, graze handling, eleven ex-step methods, and cloning.
Derived classes override their corresponding slots and inherit the others.
Every one of the 130 pointers is checked against a complete candidate function
owner and its previously fixed original identity. The per-slot original address
and symbol inventory is `.analysis/laser-vtable-slots.csv`. Original callable
end witnesses and full candidate contributions agree at 104 slot bytes plus the
four-byte locator pointer; no extent is inferred merely from the next class's
address. The existing proof and comparison rules needed no change for these
five records.

The proof supports PE32 primary tables with a zero-signature, zero-offset,
non-construction CompleteObjectLocator. It reads the entire 20-byte locator,
16-byte class hierarchy descriptors and 28-byte base descriptors. Class names
include their namespace. Single-inheritance graphs, base containment counts,
the `(0, -1, 0)` non-virtual base-displacement form and attributes are checked
across both images. Cyclic, multiple and virtual inheritance remain unsupported.

Every parsed candidate RTTI record needs one complete same-start non-code PDB
contribution. TypeDescriptor storage includes the entire header and terminated
name. The base-class arrays have complete `4 * count + 1` contributions in this
compiler: the extra zero byte is validated, not truncated. All pointer-table
storage is readable and read-only, with a DIR32 relocation for its locator
pointer and every slot. TypeDescriptor caches must be uninitialized.

Every slot must point to a unique complete candidate code contribution and an
independent original function entry, with one pre-existing fixed function
identity. Unknown slots are incomplete. An executable pointer immediately after
the declared original table rejects a shortened extent. Together with the
reviewed one/nine-slot layouts and original RTTI, this bounds the supported
original callable tables independently of their consumers.

The result binds only the exact address point in a DIR32 field. Nonzero addends
and REL32 calls to the data address are rejected. It grants no exact-data claim
to a vftable/RTTI object and no exact-code claim to a slot's callee. Game consumers
still require complete owner, boundary, decode and exhaustive field/byte replay.
The new proof module is included in the Oracle input identity, so changing it
invalidates an in-flight or retained report. These records extend independent
linkage evidence; they do not lower the code-comparison requirements.

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
For the reviewed absolute legacy COMISD form, an explicit eight-byte encoding,
matching register/disp32 and unique original instruction-start proof establish
the architectural m64 footprint. The decoder's reported 16-byte operand does
not authorize a 16-byte literal. See [the encoding evidence](comisd-literal-identities.md).

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
