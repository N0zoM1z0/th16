#pragma once

#include <stddef.h>

#include "AnmVm.h"

// These values are selected by mask interrupt handlers. Only the full
// screen and arcade modes composite the overlay in anm_on_draw_masked;
// both other observed modes draw the mask VMs without the overlay.
enum AnmMaskMode : i32
{
    ANM_MASK_FULL_SCREEN = 0,
    ANM_MASK_WITHOUT_OVERLAY_1 = 1,
    ANM_MASK_ARCADE = 2,
    ANM_MASK_WITHOUT_OVERLAY_3 = 3,
};
static_assert(sizeof(AnmMaskMode) == sizeof(i32), "masked effect mode is a 32-bit field");

// Extra data shared by the masked effect's tick, switch and draw callbacks.
// Four VMs form the alpha mask; the fifth is the overlay drawn through it.
// The frame counter is advanced by on_tick, even when the draw path does not
// inspect it. Keep this complete allocation layout in both call sites.
struct AnmMaskedEffectData
{
    AnmVm vms[4];
    AnmVm overlay;
    AnmMaskMode mode;
    i32 frame_count;
};

static_assert(offsetof(AnmMaskedEffectData, overlay) == 4 * sizeof(AnmVm),
              "masked effect overlay follows its four mask VMs");
static_assert(offsetof(AnmMaskedEffectData, mode) == 5 * sizeof(AnmVm),
              "masked effect mode follows the overlay VM");
static_assert(offsetof(AnmMaskedEffectData, frame_count) == 5 * sizeof(AnmVm) + sizeof(i32),
              "masked effect frame counter layout");
static_assert(sizeof(AnmMaskedEffectData) == 5 * sizeof(AnmVm) + 2 * sizeof(i32),
              "masked effect allocation includes the frame counter");
