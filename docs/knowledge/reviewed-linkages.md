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

Every entry has matching complete target and candidate PDB extents. The candidate
PDB must name the pinned Microsoft `LIBCMT.lib`, `libvcruntime.lib` or UCRT
`libucrt.lib`, as specified in the table input. UCRT ownership is checked against
the separately pinned Windows SDK library path. The target extent hash is
checked before use. These records
establish reviewed external linkage identities; they do not grant a separate
exact-code claim to each runtime implementation.

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
