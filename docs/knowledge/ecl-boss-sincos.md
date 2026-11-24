# ECL boss sincos helper identity

The original private `enemy_ecl_sincosmul` entry at `0x00426260` is a complete
32-byte x87 `fsincos` helper. The maintained source expresses the same XY
calculation naturally as `radius * cosf(angle)` followed by
`radius * sinf(angle)`. With the pinned candidate toolchain that source has a
73-byte private owner which calls `__libm_sse2_cos_precise` and
`__libm_sse2_sin_precise` in that order, multiplying each result by the radius
and writing `dst->x` then `dst->y`.

The private identity review keeps the original 32-byte target extent and its
original witness path, separately checks the complete 73-byte candidate PDB
owner and its two named math calls, and binds the boss's direct call to the
original helper entry. This is a semantic helper identity, not a claim that
the helper's x87 and SSE2 machine code is byte-identical. The helper is not
part of the `ecl_run_over_300` owner being compared.
