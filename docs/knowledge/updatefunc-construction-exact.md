# Shared callback construction and exact AnmManager initialization

Starting checkpoint: `132f12a`, with the preceding source trials restored at
PDB age 489. The complete **5,071-byte** `AnmManager::AnmManager` at
`0x0046A3A0` is now **exact**, improving from 5,054 matching bytes. This covers
VM pool construction, rendering defaults, all 41 callback registrations and
the existing private EH dependency graph. No game runtime or emulation runs.

## Uniform source context

The shared `UpdateFunc` constructor previously wrote every initialized field
through a volatile copy of the whole object. That preserved otherwise
overwritten initialization, but fixed the wrong order in one inlined instance:
the original clears `function` and `on_registration` before clearing heap bit
zero. The candidate cleared the flag first.

The retained constructor uses an ordinary member-initializer list for those
two callbacks. Callback, flag and priority accesses are ordinary; the four
existing volatile list-node writes retain their qualification through a
pointer to the node. No data-member declaration, layout, mask or argument
initialization is changed.

```cpp
UpdateFunc() : function(NULL), on_registration(NULL)
{
    flags &= ~UPDATE_FUNC_HEAP_ALLOCATED;
    on_cleanup = NULL;
    priority = 0;
    volatile UpdateFuncList *v = &list_node;
    v->entry = this;
    v->next = NULL;
    v->prev = NULL;
    v->unk_c = NULL;
}
```

Narrowing the qualification alone preserves all 1,719 complete native owners
byte for byte and leaves the 17-byte mismatch. The member-initializer list then
changes only 17 bytes in the constructor's interval `[0xABE,0xAD0)`. That full
18-byte interval now matches the original. The same shared constructor is used
everywhere: there is no callback-priority branch or manager-only special case.
No new volatile access, barrier, register/alignment constraint, padding,
compiler option or Oracle allowance is introduced.

This is reconstruction source organization, not proof of ZUN's original
spelling or volatile declarations. Source-origin review remains open.

## Complete static acceptance

Focused, canonical and standalone comparisons pass all **5,071 primary bytes**
and **164 fields: 75 DIR32 and 89 REL32**. The unchanged
[constructor EH profile](anm-constructor-eh.md) independently checks the whole
136-byte action/handler aggregate and 76-byte metadata aggregate, their
five-state unwind graph, producer ownership, relocations and parent frame.
These dependencies add no separate primary exact credit.

Canonical totals are **892 exact, 64 mismatch and 259 incomplete** among 1,215
annotations, with **181,107 exact primary bytes** and **956 units**. All prior
891 exact results, the other 1,214 annotation results/diagnostics and every
unit definition/address remain unchanged. All original boundaries are intact.

All other **1,718 native owners** remain raw-identical (**522,065 bytes**),
with unchanged addresses/extents. All image base relocations and every raw
`.text` byte outside the 5,071-byte constructor are unchanged. The retained
constructor is raw-identical to the first exact PDB-491 build. The final
incremental build is **PDB age 492**, source input
`326e30f1f12bd961bebf860a20069050474879caa1d4526c49690076d945d317`.
Only `UpdateFunc.h` changes generated code; `AnmRender.cpp` removes its stale
TODO. Factory acceptance is not submitted.

Preserve `.analysis/updatefunc-node-context-work/`: baseline/node-context/
first-exact/final five-artifact sets, all header snapshots, build logs, complete
PDB-owner inventories, focused/canonical/standalone reports and final regression.

## Preceding restored trials

Five complete music-room forms and one Boss overkill-credit result form fail
before this shared-constructor work. They are restored, with no exact credit;
see [music-room contexts](menu-literal-identities.md) and
[Boss hit-effect/statistics work](boss-hit-effect-flag-width.md). Keep
`.analysis/music-comment-join-work/`, including the complete original-only
768-instruction music-room CFG, all four table entries, full focused reports,
source snapshots and the PDB-489 restoration regression. An additional
conditional-selection source was prepared but never built; it is not a trial
result.
