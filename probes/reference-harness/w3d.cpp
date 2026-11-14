// Stand-in callers for ReplayManager::set_end_stage.
//
// Not ZUN's code and never run: it gives link-time code generation calls
// or address uses the decompiled code does not have, so that it compiles
// the real functions as in the original (see docs/workflow.md, "Placeholders and
// stand-in callers"). The harness files are split the way the work was;
// regrouping them changes LTCG's choices for unrelated functions.
#include "../../src/AnmManager.h"
#include "../../src/MainMenu.h"
#include "../../src/Player.h"
#include "../../src/Supervisor.h"
#include "../../src/ReplayManager.h"
#include "../../src/Scorefile.h"
#include "../../src/ZunMath.h"

// Stands for the pause menu (0x4406b1) and the replay save menu (0x453dda),
// the callers of ReplayManager::set_end_stage (0x4483b0). Both pass 1, which
// our LTCG folds into the function and the original's did not.
i32 harness_w3d_replay_end_stage(i32 stage)
{
    return g_ReplayManager->set_end_stage(stage);
}
