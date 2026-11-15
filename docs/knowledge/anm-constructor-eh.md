# AnmManager constructor EH aggregate

The later shared constructor source reconstruction
closes this complete 5,071-byte parent as exact. The EH profile and original
scope proofs below remain unchanged; the mismatch describes this earlier review.

Reviewed 2026-11-11 against the canonical original and the retained incremental
MSVC 19.10.25017 candidate. The complete private EH graph now has an explicit
Oracle profile. This makes the entire 5,071-byte constructor comparable. Its
result is **mismatch: 5,054 matching bytes and 17 differing bytes**. Neither
the constructor nor its auxiliary graph receives new exact credit.

## Original scope and roles

The parent entry is `0x0046A3A0`, ending at `0x0046B76E`. Its independently
reviewed WinMain call and complete normal control flow are recorded in
[the callback scope review](anm-callback-scopes.md). The registration prologue
pushes the private handler `0x0048AB0D` at parent offset five; its four-byte
operand is the offset-six DIR32 field. This is the only newly bound primary
field. All other parent bytes and linkages still use ordinary full-owner replay.

The original metadata directly establishes these five actions. Counts, strides
and object offsets come from the complete original instructions, before any
candidate contribution is selected.

| State | Next state | Original action | Bytes | Cleanup role |
| ---: | ---: | --- | ---: | --- |
| 0 | -1 | `0x0048AAA0` | 8 | `ThreadInf::~ThreadInf(this)` |
| 1 | 0 | `0x0048AAA8` | 30 | `fast_array`: offset `0xEC`, count `0x1FFF`, stride `0x614`, `AnmFastVm` destructor |
| 2 | 1 | `0x0048AAC6` | 30 | `snapshot_fast_array`: offset `0xC27AF0`, same count, stride and destructor |
| 3 | 2 | `0x0048AAE4` | 14 | `unused_vm`: offset `0x184F5AC`, `AnmVm` destructor |
| 4 | 3 | `0x0048AAF2` | 27 | `layer_list_dummy_heads`: offset `0x1C6FC30`, count `0x2B`, stride `0x5FC`, `AnmVm` destructor |

Actions 0 and 3 tail-transfer to their destructors. The three array actions
call the independently reviewed vector-destructor iterator at `0x00474D11`
and return. The original destructor entries are `ThreadInf` at `0x00402F20`
(11 bytes), `AnmFastVm` at `0x0046B790` (61 bytes) and `AnmVm` at `0x004093B0`
(61 bytes). The Thread destructor reinstalls its vftable and tails to
`join_if_running`; each VM destructor conditionally frees its owned allocation
and clears the same member fields. Their complete target hashes and actual
source-qualified candidate owners are checked. These entries already have
complete strict comparisons; this graph grants no additional callee credit.

The handler follows the five actions without a gap. All 27 bytes implement:

```text
mov edx, [esp + 8]
lea eax, [edx + 12]
mov ecx, [edx - 24]
xor ecx, eax
call @__security_check_cookie@4
mov eax, <this parent's FuncInfo>
jmp ___CxxFrameHandler3
```

The cookie displacement is `-0x18`, distinct from the existing empty-EH3
profile's `-4`. The complete code graph is `0x0048AAA0..0x0048AB27`, 136 bytes.
The five original inventory entries agree exactly with the complete action
scopes. The verifier reconciles those entries explicitly; it does not treat
the actions as separate candidate PDB owners. Any missing, shifted, shortened
or conflicting inventory scope is refused.

FuncInfo at `0x0049B654` has nine 32-bit words:

```text
19930522 00000005 0049B678 00000000 00000000
00000000 00000000 00000000 00000001
```

The following five eight-byte unwind-map entries encode the complete state
chain in the table above. The complete metadata owner is 76 bytes, ending at
`0x0049B69F`. No try-block, IP-map or exception-specification table is present.
Raw flags remain `0x1`; no wider interpretation is needed. The complete original
parent, code and metadata hashes are pinned in `config/eh-handlers.toml`.

## Complete candidate ownership and relocation proof

The constructor's source is `src/AnmRender.cpp`, with decorated symbol
`??0AnmManager@@QAE@XZ`. The candidate has one complete 5,071-byte parent
contribution at `0x0040B3F0`. Its actual PDB module is also the producer of
both private aggregates:

| Complete candidate contribution | Observed address | Bytes | Permitted private names and offsets |
| --- | --- | ---: | --- |
| Action/handler code | `0x0048A370` | 136 | `__unwindfunclet$<parent>$0..$4` at `0, 8, 38, 68, 82`; `__ehhandler$<parent>` at `109` |
| FuncInfo/unwind map | `0x0049ACE4` | 76 | `__ehfuncinfo$<parent>` at `0`; `__unwindtable$<parent>` at `36` |

Addresses are observations, not selectors. Selection requires the exact
parent-derived private names in the MAP Static symbols section, source object,
section/offset/VA agreement, the complete same-start PDB contribution, absolute
producer object path, module agreement, section permissions and absence of
overlapping contributions. Every listed interior name is required exactly once.
Unknown aliases, public replacements, duplicate names and other interior offsets
are refused. The interior handler is recorded as offset 109 within its whole
136-byte owner; no standalone 27-byte candidate owner is invented.

All 136 code bytes are serialized from the reviewed instruction shapes and
their proven destinations, then compared. Counts, strides, object/frame
displacements, opcodes and terminators are literal requirements. All 76 metadata
bytes are likewise checked against the entire five-state graph. The code's
complete relocation layout is:

```text
DIR32: 9, 39, 83, 127
REL32: 4, 33, 63, 78, 104, 122, 132
```

The metadata's complete DIR32 layout is `8, 40, 48, 56, 64, 72`. Missing, extra,
duplicate and boundary-crossing PE relocations are refused. Complete code
decoding must reproduce every expected operand. There are no byte masks.

The three runtime entries retain their existing independently reviewed complete
bindings: the vector-destructor iterator, security-cookie check and
`___CxxFrameHandler3`. Each game destructor requires its reviewed original role,
complete original boundary and hash, unique candidate public, complete candidate
PDB owner and canonical producer source object. Private names are never added
to the public symbol list or the global linkage map.

## Parent frame dependencies and remaining difference

The first 45 parent bytes establish the registration, eight-byte local area,
saved nonvolatile registers, GS cookie, frame link and saved incoming `this`
at `[ebp - 0x14]`. The cookie is pushed at `[ebp - 0x24]`; the handler's incoming
frame pointer is `ebp - 0xC`, explaining its `-0x18` cookie displacement and
`+0xC` frame address. Original and candidate cookie identities must agree with
their respective PE32 load-config directories. The candidate cookie additionally
requires its unique `LIBCMT:gs_cookie.obj` public storage role.

All frame-pointer uses and `fs:` accesses are scanned over the entire parent
and compared at the same offsets. The state writes are explicitly fixed:
32-bit state 0 at `+0x69`, then byte states 1, 3 and 4 at `+0x90`, `+0xBC`
and `+0xCD`. State 2 is still needed by the unwind chain after state 3; it is
not a separately written parent state. The prologue relocation layout is
exactly `6, 24`. This proof does not replace the comparison of the full parent.

The actual remaining difference is inside the allocation preceding draw
priority `0x24`, layer 17. At parent offset `0xABE`, the original clears the
function and registration callback fields before clearing flag bit zero.
The candidate clears that flag first. The three instructions occupy the same
18-byte interval, `+0xABE..+0xACF`, with 17 differing bytes. All 5,071 bytes
and all 164 parent linkages are compared. There is no new primary exact result.

The retained `UpdateFunc` constructor's volatile-this accesses remain an
unresolved source/context hypothesis. This review changes no game source and
does not establish that hypothesis as authentic. Do not special-case this
registration, force an instruction order, add artificial locals or shorten
the constructor to obtain a pass.

## Controls and retained evidence

`scripts/test-eh-constructor.py` has 25 controls, including mutations of every
one of the 212 candidate auxiliary bytes, every private name, PDB extents and
ownership, section roles, relocation records, original action inventory,
cleanup/runtime dependencies, cookie identity, frame setup, state writes and
field scope. Rehashed original action/state mutations are also refused. A
changed ordinary member initializer still produces a complete parent mismatch
after successful EH review. The existing 25 empty-EH3 controls continue to pass
with their strict standalone-owner behavior intact.

The five relevant suites pass 92 controls: constructor EH, empty EH, strict
Oracle, reviewed linkage and focused audit. Retained ignored evidence includes:

- `.analysis/anm-constructor-eh-investigation.json` and
  `.analysis/review-anm-constructor-eh.py`: the preceding original-first graph
  derivation and complete candidate contribution observations.
- `.analysis/anm-constructor-eh-focused.json`: current complete parent replay,
  all linkages, exact differing offsets and both auxiliary owner proofs.
- `.analysis/anm-eh-baseline-audit.json`: report at `0f46eaf`.
- `.analysis/anm-constructor-eh-full-audit.log` and
  `.analysis/anm-constructor-eh-regression-check.json`: broad replay and retained
  primary results/units.
- `.analysis/anm-constructor-{eh,empty-eh,oracle,linkage,focused}-controls.log`:
  passing control logs.

This EH checkpoint's report has **709 exact, 53 mismatch and 453 incomplete**, with
the same 117,308 exact primary bytes. All 709 earlier exact results and all
761 earlier complete comparison units are retained unchanged. One new complete
constructor mismatch unit is retained. No rebuild or analyzer mutation is
needed. Source-origin review remains open; Factory acceptance is unsubmitted.
