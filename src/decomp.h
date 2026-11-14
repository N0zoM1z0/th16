#pragma once

// Macros for reproducing what ZUN's whole-program build (/GL + /LTCG) did to
// individual functions. None of them is ZUN's; see docs/workflow.md,
// "Whole-program optimization".

// Link-time code generation decides inlining with the whole program in view,
// and our build does not always reach the original's decision (callers
// whose shape differs, functions kept alive with /INCLUDE). DECOMP_NOINLINE
// marks functions the original keeps out of line where ours would inline
// them, so that their callers match.
#define DECOMP_NOINLINE __declspec(noinline)

// A global the compiler must know to be 16-byte aligned, as the original's
// was as part of a larger struct (merged movaps stores). A plain name rather
// than __declspec(align(16)) on the annotated line: reccmp's GLOBAL parser
// would take __declspec for the variable's name.
#define DECOMP_ALIGN16 __declspec(align(16))

// Functions whose callers are all known get a custom calling convention from
// link-time code generation: the first arguments move into ecx/edx, while
// stack cleanup stays as declared (cdecl: caller pops; thiscall/stdcall:
// callee pops). A callee-popped function with its first two arguments in
// ecx/edx looks exactly like __fastcall; in ZUN's source it was most likely
// a member function whose unused `this` LTCG dropped. Our build keeps
// annotated functions alive with /INCLUDE, which blocks the conversion, so
// LTCG_FASTCALL states the result directly.
#define LTCG_FASTCALL __fastcall

// The same conversion for functions taking or returning floats: LTCG passes
// them in xmm registers and returns in xmm0, which __vectorcall reproduces.
#define LTCG_VECTORCALL __vectorcall

// Marks a function kept alive by its callers (and, where those are not
// enough, by stand-in callers in probes/reference-harness/) rather than by /INCLUDE. Only
// then does LTCG see every caller, and with every caller known it picks a
// custom calling convention the same way it did in ZUN's build (for example
// `this` in ecx and a float argument in xmm1, which no declarable convention
// produces). The function must stay out of line for that, hence noinline.
#define HARNESS_CALLED __declspec(noinline)

// Placeholders, not ZUN's code. LTCG's stack-alignment pass weighs double
// arithmetic before dead code is removed, and some original functions had
// double work that was deleted afterwards; nothing of it survives in the
// binary. These dead doubles restore that weight: in place they make the
// function itself want an 8-aligned stack (each multiply adds weight), and
// through decomp_want_aligned_stack, a call graph node of its own, they make
// it a caller of a function that wants one.
#define DECOMP_DEAD_DOUBLE_0 { double decomp_dead = 0.0; (void)decomp_dead; }
#define DECOMP_DEAD_DOUBLE_1 { double decomp_dead = 0.0; decomp_dead = decomp_dead * 2.0; (void)decomp_dead; }
#define DECOMP_DEAD_DOUBLE_2                                                                                         \
    {                                                                                                                \
        double decomp_dead = 0.0;                                                                                    \
        decomp_dead = decomp_dead * 2.0;                                                                             \
        decomp_dead = decomp_dead * 2.0;                                                                             \
        (void)decomp_dead;                                                                                           \
    }
#define DECOMP_DEAD_DOUBLE_3                                                                                         \
    {                                                                                                                \
        double decomp_dead = 0.0;                                                                                    \
        decomp_dead = decomp_dead * 2.0;                                                                             \
        decomp_dead = decomp_dead * 2.0;                                                                             \
        decomp_dead = decomp_dead * 2.0;                                                                             \
        (void)decomp_dead;                                                                                           \
    }
static inline void decomp_want_aligned_stack()
{
    double decomp_dead = 0.0;
    (void)decomp_dead;
}
