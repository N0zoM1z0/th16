#pragma once

#include <stddef.h>

#include "AnmVm.h"

// Extra data shared by the masked effect's tick, switch and draw callbacks.
// Four VMs form the alpha mask; the fifth is the overlay drawn through it.
// The frame counter is advanced by on_tick, even when the draw path does not
// inspect it. Keep this complete allocation layout in both call sites.
struct AnmMaskedEffectData
{
    AnmVm vms[4];
    AnmVm overlay;
    i32 mode;
    i32 frame_count;
};

static_assert(offsetof(AnmMaskedEffectData, overlay) == 4 * sizeof(AnmVm),
              "masked effect overlay follows its four mask VMs");
static_assert(offsetof(AnmMaskedEffectData, mode) == 5 * sizeof(AnmVm),
              "masked effect mode follows the overlay VM");
static_assert(offsetof(AnmMaskedEffectData, frame_count) == 5 * sizeof(AnmVm) + sizeof(i32),
              "masked effect frame counter layout");
