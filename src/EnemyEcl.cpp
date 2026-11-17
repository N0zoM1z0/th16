// The enemy-specific ECL instructions (300 and up). Instruction names are
// ExpHP's (th-re-data labels.json).
#include "Enemy.h"
#include "AnmManager.h"
#include "CriticalSections.h"
#include "EffectManager.h"
#include "EnemyManager.h"
#include "Globals.h"
#include "Gui.h"
#include "PopupManager.h"
#include "SoundManager.h"
#include "BulletManager.h"
#include "Camera.h"
#include "Fog.h"
#include "GameThread.h"
#include "Laser.h"
#include <intrin.h>
#include <new>
#include "Player.h"
#include "Rng.h"
#include "ScreenEffect.h"
#include "Spellcard.h"
#include "Stage.h"
#include "Supervisor.h"
#include "ZunAngle.h"
#include "ZunAsm.h"
#include "ZunMath.h"

static_assert(offsetof(EnemyData, anm_ids) == 0x124, "ECL ANM id array offset");
static_assert(sizeof(BulletEx) == 0x2c, "ECL transform stride");
static_assert(sizeof(EnemyBulletShooter) == 0x380, "ECL shooter stride");
static_assert(offsetof(EnemyBulletShooter, ex) == 0x28, "ECL transform array offset");
static_assert(offsetof(EnemyData, bullet_props) + offsetof(EnemyBulletShooter, ex) == 0x5c0,
              "ECL transform array base");

static const f32 ecl_origin_threshold = 0.9f;
static const f32 ecl_die_distance_squared = 0.2f * 0.2f;
static const f32 ecl_die_default_angle = -ZUN_PI / 2;
static const f32 ecl_move_rand_quarter = 0.25f;
static const f32 ecl_move_rand_third = 3.0f;
static const f32 ecl_move_rand_pi = ZUN_PI;
static const f32 ecl_move_rand_half_pi = ZUN_PI / 2;
static const f32 ecl_move_rand_five_cents = 0.05f;
static const double ecl_move_rand_five_cents_double = 0.05;
static const f32 ecl_move_rand_neg_half_pi = -ZUN_PI / 2;
static const f32 ecl_move_rand_neg_half_pi_low = -ZUN_PI / 2 - 0.05f;
static const f32 ecl_move_rand_neg_half_pi_high = -ZUN_PI / 2 + 0.05f;
static const f32 ecl_move_rand_pos_half_pi_low = ZUN_PI / 2 - 0.05f;
static const f32 ecl_move_rand_pos_half_pi_high = ZUN_PI / 2 + 0.05f;
// create_vm, inserted at the front of the world list like create_vm_front
// (0x426160, which is a copy with pos and rotation folded). LTCG inlined
// this into the anmPlay instructions.
static __forceinline AnmId create_vm_front_at(AnmLoaded *file, i32 script, Float3 *pos, f32 rotation)
{
    ENTER_CS(CS_ANM_MANAGER);
    file->vm_count++;
    AnmVm *vm = g_AnmManager->allocate_vm();
    file->copy_vm(vm, script);
    vm->flags_hi |= ANM_VM_CREATED_BY_GAME;
    if (pos == NULL)
    {
        vm->entity_pos = D3DXVECTOR3(0.0f, 0.0f, 0.0f);
    }
    else
    {
        vm->entity_pos = *pos;
    }
    vm->rotation.z = rotation;
    vm->run();
    vm->mode_of_create_child = 2;
    AnmId id;
    id = g_AnmManager->insert_in_world_list_front(vm);
    LEAVE_CS(CS_ANM_MANAGER);
    return id;
}

// pi - angle, wrapped: the direction mirrored about the vertical axis, for
// mirrored enemies (ENEMY_FLAG_MIRRORED).
static __forceinline f32 mirror_angle(f32 angle)
{
    return normalize_angle(ZUN_PI / 2 - normalize_angle(angle - ZUN_PI / 2));
}

// The argument for the current difficulty, out of four starting at first:
// one get_*_arg call per difficulty (the binary pushes each index in its
// own branch before one shared call).
#define ECL_DIFF_ARG(get, first)                                                                                   \
    (g_Globals.difficulty == DIFFICULTY_EASY     ? get(first)                                                      \
     : g_Globals.difficulty == DIFFICULTY_NORMAL ? get((first) + 1)                                                \
     : g_Globals.difficulty == DIFFICULTY_HARD   ? get((first) + 2)                                                \
                                                 : get((first) + 3))

#define ECL_DIFF_FLOAT_ARG(first)                                                                                   \
    (g_Globals.difficulty == DIFFICULTY_EASY     ? get_float_arg(EclFloatArgIndex{first})                        \
     : g_Globals.difficulty == DIFFICULTY_NORMAL ? get_float_arg(EclFloatArgIndex{(first) + 1})                  \
     : g_Globals.difficulty == DIFFICULTY_HARD   ? get_float_arg(EclFloatArgIndex{(first) + 2})                  \
                                                 : get_float_arg(EclFloatArgIndex{(first) + 3}))

// The bitfields of EnemyLife::is_spell that ECL assigns.
struct EnemyLifeSpellBits
{
    u32 active : 1;
    u32 unk_1 : 31;
};

// The bitfields of Spellcard::flags that ECL assigns (xor/and/xor).
struct SpellcardFlagBits
{
    u32 unk_0 : 8;
    u32 text_at_bottom : 1;
    u32 unk_9 : 23;
};

extern EnemyFuncSetFunc const g_ecl_func_sets[3];
int __fastcall ecl_ext_damage_stored(EnemyData *enemy, int damage);
int __fastcall ecl_ext_damage_anm_hurtbox(EnemyData *enemy, int damage);

// The damage hooks ECL's flagExtDmg installs.
// GLOBAL: TH16 0x490eb4
extern EnemyExtDamageFunc const g_ecl_ext_damage_funcs[3] = {NULL, ecl_ext_damage_stored, ecl_ext_damage_anm_hurtbox};

// The hooks ECL 634 installs; only entry 0 (NULL).
// GLOBAL: TH16 0x4a6dc4
void *g_ecl_unknown_634_funcs[1];

// This file's copy of sincosmul (ZunAsm.h; TH16 keeps one per object
// file).
// FUNCTION: TH16 0x426260
static void __fastcall enemy_ecl_sincosmul(Float3 *dst, f32 angle, f32 radius)
{
    ZUN_ASM_SINCOSMUL(dst, angle, radius);
}

// The line, infinite and curve laser constructors test the origin before
// copying the transform array; the beam constructor copies it first. Keep
// those target instruction orders in separate typed helpers.
static __forceinline void get_shot_origin_and_copy_ex_branch_first(
    EnemyData *enemy, i32 i, D3DXVECTOR3 *out, BulletEx *ex)
{
    f32 x;
    f32 y;
    f32 z;
    if (enemy->bullet_mgr_origins[i].z > 0.9f)
    {
        memcpy(ex, enemy->bullet_props[i].ex, sizeof(enemy->bullet_props[i].ex));
        y = enemy->bullet_mgr_offsets[i].xy.y;
        x = enemy->bullet_mgr_origins[i].xy.x + enemy->bullet_mgr_offsets[i].xy.x;
        y += enemy->bullet_mgr_origins[i].xy.y;
        z = 0.0f;
    }
    else
    {
        memcpy(ex, enemy->bullet_props[i].ex, sizeof(enemy->bullet_props[i].ex));
        y = enemy->bullet_mgr_offsets[i].xy.y;
        z = enemy->bullet_mgr_offsets[i].z + enemy->final_pos.pos.z;
        x = enemy->bullet_mgr_offsets[i].xy.x + enemy->final_pos.pos.x;
        y += enemy->final_pos.pos.y;
    }
    *out = D3DXVECTOR3(x, y, z);
}

static __forceinline void copy_ex_and_get_shot_origin(
    EnemyData *enemy, i32 i, D3DXVECTOR3 *out, BulletEx *ex)
{
    bool has_origin = enemy->bullet_mgr_origins[i].z > 0.9f;
    memcpy(ex, enemy->bullet_props[i].ex, sizeof(enemy->bullet_props[i].ex));
    f32 x;
    f32 y;
    f32 z;
    if (has_origin)
    {
        x = enemy->bullet_mgr_origins[i].xy.x + enemy->bullet_mgr_offsets[i].xy.x;
        y = enemy->bullet_mgr_origins[i].xy.y + enemy->bullet_mgr_offsets[i].xy.y;
        z = 0.0f;
    }
    else
    {
        z = enemy->bullet_mgr_offsets[i].z + enemy->final_pos.pos.z;
        x = enemy->bullet_mgr_offsets[i].xy.x + enemy->final_pos.pos.x;
        y = enemy->bullet_mgr_offsets[i].xy.y + enemy->final_pos.pos.y;
    }
    *out = D3DXVECTOR3(x, y, z);
}

// setNext: the life at which interrupt index fires and, unless the life is
// negative, its time and subroutine.
static inline void set_next(EnemyInf *enemy, int index, int life, int time, const char *sub)
{
    enemy->enemy.interrupts[index].life = life;
    if (life >= 0)
    {
        enemy->set_interrupt(index, time, sub);
    }
}

// The fog instruction's `new Fog(0, 0x11, 0)`. Inlined: the original
// constructs the fog in ecl_run_over_300 itself, which gives that function
// its EH frame. (Earlier, with less of the program decompiled, that frame
// made LTCG stop inlining the UCRT math into several callees; it no longer
// does.)
static __forceinline Fog *new_enemy_fog()
{
    return new Fog(0, 0x11, 0);
}

// anmPlay's extra steps go through this helper, like the original: a
// direct AnmVm::run call in a loop would make ecl_run_over_300 realign its
// frame for run's aligned-stack need.
static inline void ecl_run_vm(AnmVm *vm)
{
    vm->run();
}

// The laser instructions and angleToPlayer, as forceinline helpers: the
// original has them inline in ecl_run_over_300.

static_assert(sizeof(EnemyBulletShooter) == 0x380, "ECL shooter stride");
static_assert(sizeof(BulletEx) == 0x2c, "ECL transform stride");
static_assert(offsetof(EnemyData, bullet_props) + offsetof(EnemyBulletShooter, ex) +
                  offsetof(BulletEx, c) == 0x5d8,
              "ECL transform c field offset");
static_assert(offsetof(EnemyBulletShooter, ex) == 0x28, "ECL transform array offset");

// The original dispatcher reuses one stack slot for its mutually exclusive
// laser parameter records; the movement cases reuse that scratch area too.
struct EclMovementScratch
{
    PosVel *position;
    InterpStrange1 *position_interp;
    f32 goal_x;
    f32 goal_y;
};

union EclLaserParamsStorage
{
    LaserLineInner line;
    LaserInfiniteInner infinite;
    LaserBeamInner beam;
    LaserCurveInner curve;
    EclMovementScratch movement;

    EclLaserParamsStorage()
    {
    }
};

static_assert(sizeof(EclLaserParamsStorage) == sizeof(LaserInfiniteInner),
              "shared ECL laser parameter storage");
static_assert(sizeof(LaserLineInner) <= sizeof(EclLaserParamsStorage),
              "line laser fits shared parameter storage");
static_assert(sizeof(LaserBeamInner) <= sizeof(EclLaserParamsStorage),
              "beam laser fits shared parameter storage");
static_assert(sizeof(LaserCurveInner) <= sizeof(EclLaserParamsStorage),
              "curve laser fits shared parameter storage");
static_assert(sizeof(EclMovementScratch) <= sizeof(EclLaserParamsStorage),
              "movement scratch fits shared dispatcher storage");

// FUNCTION: TH16 0x41dcb0
int EnemyData::ecl_run_over_300()
{
    EclLaserParamsStorage laser_params_storage;
    // The target keeps the owning EnemyInf context in a frame local and
    // reuses it across the large switch rather than reloading this->full.
    EnemyInf *full_owner = full;
    register EclRawInstr *instr = full_owner->context.current_context->current_instr();
    switch ((i16)instr->opcode)
    {
    // enmCreateF and its variants: only without a boss.
    case ECL_OP_ENM_CREATE_F:
    case ECL_OP_ENM_CREATE_AF:
    case ECL_OP_ENM_CREATE_MF:
    case ECL_OP_ENM_CREATE_AMF:
        if (g_EnemyManager->get_boss(0) != NULL)
        {
            break;
        }
    // enmCreate, enmCreateA, enmCreateM, enmCreateAM, enmCreate321.
    case ECL_OP_ENM_CREATE:
    case ECL_OP_ENM_CREATE_A:
    case ECL_OP_ENM_CREATE_M:
    case ECL_OP_ENM_CREATE_AM:
    case ECL_OP_ENM_CREATE_321:
        ecl_enm_create();
        break;
    // anmSelect(file)
    case ECL_OP_ANM_SELECT:
        selected_anm_index = full->context.current_context->get_int_arg(0);
        break;
    // moveSetMirror(mirrored)
    case ECL_OP_MOVE_SET_MIRROR:
        ((EnemyFlagsLow *)&flags_low)->mirrored = full->context.current_context->get_int_arg(0);
        break;
    // lifeHide(hide)
    case ECL_OP_LIFE_HIDE:
        g_EnemyManager->inner.life_bar_hidden = full->context.current_context->get_int_arg(0);
        break;
    // zIndex(layer)
    case ECL_OP_Z_INDEX:
        anm_layers = full->context.current_context->get_int_arg(0);
        break;
    // hitSound(sound)
    case ECL_OP_HIT_SOUND:
        hit_sound = full->context.current_context->get_int_arg(0);
        break;
    // scoreAdd(points)
    case ECL_OP_SCORE_ADD:
    {
        i32 points = full->context.current_context->get_int_arg(0);
        g_Globals.add_to_score(points);
        g_PopupManager->generate_small_score_popup(&final_pos.pos, points, -1);
        break;
    }
    // anmSetSprite(slot, script)
    case ECL_OP_ANM_SET_SPRITE:
        ecl_anm_set_sprite();
        break;
    // anmMove(slot, x, y): the offset of a slot's VM.
    case ECL_OP_ANM_MOVE:
    {
        i32 slot = full->context.current_context->get_int_arg(0);
        anm_pos_array[slot].x = full->context.current_context->get_float_arg(EclFloatArgIndex{1});
        anm_pos_array[slot].y = full->context.current_context->get_float_arg(EclFloatArgIndex{2});
        anm_pos_array[slot].z = 0.0f;
        break;
    }
    // The instructions that change one of the enemy's VMs.
    case ECL_OP_ANM_ROTATE:
    case ECL_OP_ANM_COLOR:
    case ECL_OP_ANM_COLOR_TIME:
    case ECL_OP_ANM_ALPHA:
    case ECL_OP_ANM_ALPHA_TIME:
    case ECL_OP_ANM_SCALE:
    case ECL_OP_ANM_SCALE_TIME:
    case ECL_OP_ANM_ALPHA2:
    case ECL_OP_ANM_ALPHA2_TIME:
    case ECL_OP_ANM_POS_TIME:
    case ECL_OP_ANM_SCALE2:
    case ECL_OP_ANM_LAYER:
    case ECL_OP_ANM_BLEND_MODE:
        ecl_anm_vm_instr();
        break;
    // unknown566: dies now.
    case ECL_OP_DIE_NOW:
        if (full_owner->die())
        {
            return 1;
        }
        break;
    // enm323(file, script): the death animation.
    case ECL_OP_DEATH_ANM:
        death_anm_index = full->context.current_context->get_int_arg(0);
        death_anm_script = full->context.current_context->get_int_arg(1);
        break;
    // die: the death sound and animation without dying.
    case ECL_OP_DIE:
        if (death_sound >= 0)
        {
            g_SoundManager.play_sound_at_position(death_sound, final_pos.pos.x);
        }
        if (death_anm_script >= 0)
        {
            // A nearby hit uses the default downward angle. Otherwise point
            // the animation from the hit position toward the enemy.
            const Float3 *enemy_position = &final_pos.pos;
            f32 dy = last_damage_pos.y - enemy_position->y;
            f32 dx = last_damage_pos.x - enemy_position->x;
            f32 distance_squared = dy * dy + dx * dx;
            f32 angle;
            if (distance_squared < ecl_die_distance_squared)
            {
                angle = ecl_die_default_angle;
            }
            else
            {
                Float3 displacement = final_pos.pos - last_damage_pos;
                angle = zun_atan2f(displacement.y, displacement.x);
            }

            AnmLoaded *anm = g_EnemyManager->anim_statement_anms[death_anm_index];
            anm->create_vm(death_anm_script, &final_pos.pos, angle, 3, 0);
        }
        break;
    // enm322(index, value)
    case ECL_OP_ANM_PARENT:
        anm_parent_slot[full->context.current_context->get_int_arg(0)] = full->context.current_context->get_int_arg(1);
        break;
    // stageLogo
    case ECL_OP_STAGE_LOGO:
        show_stage_logo();
        break;
    // anmPlayPos(file, script, x, y, rotation)
    case ECL_OP_ANM_PLAY_POS:
    {
        // y is read before x as in the original (random variables draw from the replay RNG).
        f32 y = full->context.current_context->get_float_arg(EclFloatArgIndex{3});
        f32 x = full->context.current_context->get_float_arg(EclFloatArgIndex{2});
        Float3 pos = Float3(x, y, 0.0f) + final_pos.pos;
        g_EffectManager->track(create_vm_front_at(g_EnemyManager->anim_statement_anms[full->context.current_context->get_int_arg(0)], full->context.current_context->get_int_arg(1),
                                                  &pos, full->context.current_context->get_float_arg(EclFloatArgIndex{4})));
        break;
    }
    // anmPlay(file, script)
    case ECL_OP_ANM_PLAY:
    {
        i32 script = full_owner->context.current_context->get_int_arg(1);
        i32 file_index = full->context.current_context->get_int_arg(0);
        EnemyManager *enemy_manager = g_EnemyManager;
        AnmLoaded *file = enemy_manager->anim_statement_anms[file_index];
        g_EffectManager->track(create_vm_front_at(file, script, &final_pos.pos, 0.0f));
        break;
    }
    // anmPlayHigh(file, script): creates a VM at the enemy's current position.
    case ECL_OP_ANM_PLAY_HIGH:
    {
        i32 script = full->context.current_context->get_int_arg(1);
        i32 file_index = full->context.current_context->get_int_arg(0);
        AnmLoaded *file = g_EnemyManager->anim_statement_anms[file_index];
        g_EffectManager->track(file->create_vm(script, &final_pos.pos, 0.0f, -1, 0));
        break;
    }
    // anmPlayAbs(file, script): creates a VM at the origin on the front list.
    case ECL_OP_ANM_PLAY_ABS:
    {
        i32 file_index = full->context.current_context->get_int_arg(0);
        i32 script = full->context.current_context->get_int_arg(1);
        AnmLoaded *file = g_EnemyManager->anim_statement_anms[file_index];
        AnmId created = file->create_vm_front(script, -1, 0);
        g_EffectManager->track(created);
        break;
    }
    // anm339(file, script, frames): anmPlayAbs, then runs the VM for some
    // frames at once.
    case ECL_OP_ANM_339:
    {
        i32 file_index = full->context.current_context->get_int_arg(0);
        i32 script = full->context.current_context->get_int_arg(1);
        AnmLoaded *file = g_EnemyManager->anim_statement_anms[file_index];
        AnmId id = file->create_vm_front(script, -1, 0);
        g_EffectManager->track(id);
        AnmVm *vm = id.find_or_clear();
        for (i32 i = 0; i < full->context.current_context->get_int_arg(2); i++)
        {
            ecl_run_vm(vm);
        }
        break;
    }
    // anmPlayRotate(file, script, rotation)
    case ECL_OP_ANM_PLAY_ROTATE:
    {
        i32 script = full->context.current_context->get_int_arg(1);
        i32 file_index = full->context.current_context->get_int_arg(0);
        AnmId id = create_vm_front_at(g_EnemyManager->anim_statement_anms[file_index], script,
                                      &final_pos.pos, 0.0f);
        AnmVm *vm = id.find_or_clear();
        if (vm != NULL)
        {
            vm->entity_pos = final_pos.pos;
            vm->rotation.z = full->context.current_context->get_float_arg(EclFloatArgIndex{2});
            vm->flags_lo |= ANM_VM_ROTATION_CHANGED;
        }
        g_EffectManager->track(id);
        break;
    }
    // anm334(effect)
    case ECL_OP_ANM_334:
    {
        i32 effect = full->context.current_context->get_int_arg(0);
        g_EffectManager->create_tracked(effect, &final_pos.pos, 0);
        break;
    }
    // anmSetMain(slot, script): replace a slot and, for slot 0, establish
    // the directional main animation and its sprite bounds.
    case ECL_OP_ANM_SET_MAIN:
    {
        i32 slot = full->context.current_context->get_int_arg(0);
        i32 script = full->context.current_context->get_int_arg(1);
        AnmId &selected_vm = anm_ids[slot];

        g_AnmManager->delete_vm(selected_vm);
        selected_vm.id = 0;

        AnmLoaded *file = g_EnemyManager->anim_statement_anms[selected_anm_index];
        selected_vm = file->create_vm_front(script, anm_layers + 7, 0);
        AnmVm *vm = selected_vm.find_or_clear();

        if (slot == 0)
        {
            final_sprite_size.x = vm->sprite_size.y * vm->scale.y;
            final_sprite_size.y = vm->sprite_size.x * vm->scale.x;
        }
        if (flags_low & ENEMY_FLAG_INTANGIBLE)
        {
            selected_vm.hide_tree();
        }
        if (slot == 0)
        {
            flags_low |= ENEMY_FLAG_DIRECTIONAL_ANM;
            anm_set_main = script;
            anm_slot_0_script = script;
            anm_direction = 0;
            anm_slot_0_anm_index = selected_anm_index;
        }
        break;
    }
    // anmReset: restore the main script in slot 0 and stop directional
    // animation switching.
    case ECL_OP_ANM_RESET:
    {
        g_AnmManager->delete_vm(anm_ids[0]);
        anm_ids[0].id = 0;

        AnmLoaded *file = g_EnemyManager->anim_statement_anms[selected_anm_index];
        anm_ids[0] = file->create_vm_front(anm_set_main, anm_layers + 7, 0);

        flags_low &= ~ENEMY_FLAG_DIRECTIONAL_ANM;
        anm_slot_0_script = anm_set_main;
        anm_slot_0_anm_index = selected_anm_index;
        anm_direction = 0;
        break;
    }
    // anmSelectedPlay(slot): play the first alternate script of the current
    // main ANM, retaining the visibility state of the enemy.
    case ECL_OP_ANM_SELECTED_PLAY:
    {
        i32 slot = full->context.current_context->get_int_arg(0);
        AnmId &selected_vm = anm_ids[slot];
        g_AnmManager->delete_vm(selected_vm);
        selected_vm.id = 0;

        AnmLoaded *file = g_EnemyManager->anim_statement_anms[selected_anm_index];
        selected_vm = file->create_vm_front(anm_set_main + 5, anm_layers + 7, 0);
        AnmVm *vm = selected_vm.find_or_clear();
        if (slot == 0)
        {
            final_sprite_size.x = vm->sprite_size.y * vm->scale.y;
            final_sprite_size.y = vm->sprite_size.x * vm->scale.x;
        }
        if (flags_low & ENEMY_FLAG_INTANGIBLE)
        {
            selected_vm.hide_tree();
        }
        break;
    }
    // anm316(slot, n): play the saved main script when n is negative;
    // otherwise select its n-th alternate, starting at script + 5.
    case ECL_OP_ANM_316:
    {
        i32 slot = full->context.current_context->get_int_arg(0);
        i32 alternate = full->context.current_context->get_int_arg(1);
        AnmId *volatile selected = &anm_ids[slot];
        AnmId &anm_id = *selected;
        g_AnmManager->delete_vm(anm_id);
        anm_id.id = 0;

        AnmLoaded *file = g_EnemyManager->anim_statement_anms[selected_anm_index];
        i32 layer = anm_layers + 7;
        anm_id = file->create_vm_front(alternate >= 0 ? anm_set_main + alternate + 5 : anm_set_main,
                                       layer, 0);
        AnmVm *vm = anm_id.find_or_clear();
        if (slot == 0)
        {
            final_sprite_size.x = vm->sprite_size.y * vm->scale.y;
            final_sprite_size.y = vm->sprite_size.x * vm->scale.x;
        }
        if (flags_low & ENEMY_FLAG_INTANGIBLE)
        {
            anm_id.hide_tree();
        }
        break;
    }
    // anmSwitch(slot, interrupt): interrupt the VM and its direct children.
    case ECL_OP_ANM_SWITCH:
    {
        i32 slot = full->context.current_context->get_int_arg(0);
        i32 interrupt = full->context.current_context->get_int_arg(1);
        AnmManager::interrupt_tree(anm_ids[slot], (i16)interrupt);
        break;
    }
    // moveReset: folds rel_pos into abs_pos and stops all movement.
    case ECL_OP_MOVE_RESET:
        // Fold the first axis with the relative displacement first.
        abs_pos.pos.x = *(volatile f32 *)&rel_pos.pos.x + abs_pos.pos.x;
        abs_pos.pos.y += rel_pos.pos.y;
        abs_pos.pos.z += rel_pos.pos.z;
        rel_pos.pos = g_zero_vec;
        rel_pos.speed = 0.0f;
        abs_pos.speed = 0.0f;
        rel_pos.velocity = g_zero_vec;
        abs_pos.velocity = g_zero_vec;
        (*(volatile u32 *)&rel_pos.flags) &= ~0xf;
        abs_pos.flags &= ~0xf;
        abs_pos_i.end_time = 0;
        rel_pos_i.end_time = 0;
        abs_angle_i.end_time = 0;
        rel_angle_i.end_time = 0;
        abs_speed_i.end_time = 0;
        rel_speed_i.end_time = 0;
        abs_radial_dist_i.end_time = 0;
        rel_radial_dist_i.end_time = 0;
        abs_ellipse_i.end_time = 0;
        rel_ellipse_i.end_time = 0;
        break;
    // movePos(x, y), movePosRel(x, y): -999999 keeps a coordinate.
    case ECL_OP_MOVE_POS:
    case ECL_OP_MOVE_POS_REL:
    {
        PosVel *pos_vel = instr->opcode == ECL_OP_MOVE_POS ? &abs_pos : &rel_pos;
        f32 x = full_owner->context.current_context->get_float_arg(EclFloatArgIndex{0});
        f32 y = full->context.current_context->get_float_arg(EclFloatArgIndex{1});
        if (x > -999999.0)
        {
            pos_vel->pos.x = x;
        }
        if (y > -999999.0)
        {
            pos_vel->pos.y = y;
        }
        pos_vel->flags &= ~0xf;
        // The original combines relative displacement first, then absolute position.
        final_pos.pos = Float3(rel_pos.pos.x + abs_pos.pos.x,
                               rel_pos.pos.y + abs_pos.pos.y,
                               rel_pos.pos.z + abs_pos.pos.z);
        update_final_pos();
        break;
    }
    // movePos3d(x, y, z), movePos3dRel(x, y, z): moves by the offset.
    case ECL_OP_MOVE_POS_3D:
    case ECL_OP_MOVE_POS_3D_REL:
    {
        PosVel *pos_vel = instr->opcode == ECL_OP_MOVE_POS_3D ? &abs_pos : &rel_pos;
        f32 x = full_owner->context.current_context->get_float_arg(EclFloatArgIndex{0});
        f32 y = full->context.current_context->get_float_arg(EclFloatArgIndex{1});
        volatile f32 z = full->context.current_context->get_float_arg(EclFloatArgIndex{2});
        volatile f32 *position = &pos_vel->pos.x;
        position[0] += x;
        position[1] += y;
        position[2] = z + position[2];
        update_final_pos();
        break;
    }
    // movePosTime(time, mode, x, y) and movePosRelTime; 436/437 move by an
    // offset (mirrored with the enemy).
    case ECL_OP_MOVE_POS_TIME:
    case ECL_OP_MOVE_POS_REL_TIME:
    case ECL_OP_MOVE_POS_TIME_OFFSET:
    case ECL_OP_MOVE_POS_REL_TIME_OFFSET:
    {
        PosVel *pos_vel = (instr->opcode == ECL_OP_MOVE_POS_TIME ||
                           instr->opcode == ECL_OP_MOVE_POS_TIME_OFFSET) ? &abs_pos : &rel_pos;
        InterpStrange1 *position_interp = (instr->opcode == ECL_OP_MOVE_POS_TIME ||
                                            instr->opcode == ECL_OP_MOVE_POS_TIME_OFFSET) ? &abs_pos_i : &rel_pos_i;

        f32 goal_x = full_owner->context.current_context->get_float_arg(EclFloatArgIndex{2});
        f32 goal_y = full->context.current_context->get_float_arg(EclFloatArgIndex{3});
        if (full->context.current_context->get_int_arg(0) <= 0)
        {
            position_interp->end_time = 0;
            break;
        }

        if (instr->opcode == ECL_OP_MOVE_POS_TIME_OFFSET ||
            instr->opcode == ECL_OP_MOVE_POS_REL_TIME_OFFSET)
        {
            f32 current_x = pos_vel->pos.x;
            if (!(flags_low & ENEMY_FLAG_MIRRORED))
            {
                goal_x = current_x + goal_x;
            }
            else
            {
                goal_x = current_x - goal_x;
            }
            goal_y = pos_vel->pos.y + goal_y;
        }

        position_interp->end_time = full->context.current_context->get_int_arg(0);
        position_interp->bezier_1 = g_zero_vec;
        position_interp->bezier_2 = g_zero_vec;
        position_interp->method_for_3d = full->context.current_context->get_int_arg(1);
        position_interp->flag_1d &= ~1;
        position_interp->initial = pos_vel->pos;
        position_interp->goal = Float3(goal_x > -999999.0 ? goal_x : pos_vel->pos.x,
                                        goal_y > -999999.0 ? goal_y : pos_vel->pos.y, 0.0f);
        position_interp->reset_timer();
        pos_vel->flags &= ~0xf;
        break;
    }
    // moveCurve(time, mode_x, mode_y, x, y) and its variants: separate
    // modes for x and y.
    case ECL_OP_MOVE_CURVE:
    case ECL_OP_MOVE_CURVE_REL:
    case ECL_OP_MOVE_CURVE_OFFSET:
    case ECL_OP_MOVE_CURVE_REL_OFFSET:
    {
        i32 position_offset;
        InterpStrange1 *position_interp;
        f32 goal_x;
        f32 goal_y;
        {
            position_offset = (instr->opcode == ECL_OP_MOVE_CURVE ||
                               instr->opcode == ECL_OP_MOVE_CURVE_OFFSET)
                                  ? offsetof(EnemyData, abs_pos)
                                  : offsetof(EnemyData, rel_pos);
            position_interp = (instr->opcode == ECL_OP_MOVE_CURVE ||
                               instr->opcode == ECL_OP_MOVE_CURVE_OFFSET) ? &abs_pos_i : &rel_pos_i;
            goal_x = full->context.current_context->get_float_arg(EclFloatArgIndex{3});
            goal_y = full->context.current_context->get_float_arg(EclFloatArgIndex{4});
            i32 move_curve_duration = full->context.current_context->get_int_arg(0);
            if (move_curve_duration <= 0)
            {
                position_interp->end_time = 0;
                break;
            }

            if (instr->opcode == ECL_OP_MOVE_CURVE_OFFSET ||
                instr->opcode == ECL_OP_MOVE_CURVE_REL_OFFSET)
            {
                f32 current_x = ((PosVel *)((u8 *)this + position_offset))->pos.x;
                if (!(flags_low & ENEMY_FLAG_MIRRORED))
                {
                    goal_x = current_x + goal_x;
                }
                else
                {
                    goal_x = current_x - goal_x;
                }
                goal_y = ((PosVel *)((u8 *)this + position_offset))->pos.y + goal_y;
            }

            position_interp->end_time = full->context.current_context->get_int_arg(0);
            position_interp->bezier_1 = g_zero_vec;
            position_interp->bezier_2 = g_zero_vec;
            position_interp->method_for_1d = full->context.current_context->get_int_arg(1);
            position_interp->flag_1d |= 1;
            position_interp->move_curve_mode = full->context.current_context->get_int_arg(2);
            position_interp->flag_1d |= 1;
        }
        goto ecl_move_curve_finish;
    case ECL_OP_MOVE_BEZIER:
    case ECL_OP_MOVE_BEZIER_REL:
    {
        position_offset = instr->opcode == ECL_OP_MOVE_BEZIER ? offsetof(EnemyData, abs_pos)
                                                               : offsetof(EnemyData, rel_pos);
        position_interp = instr->opcode == ECL_OP_MOVE_BEZIER ? &abs_pos_i : &rel_pos_i;
        goal_x = full->context.current_context->get_float_arg(EclFloatArgIndex{3});
        goal_y = full->context.current_context->get_float_arg(EclFloatArgIndex{4});
        Float3 bezier_1;
        bezier_1.x = full->context.current_context->get_float_arg(EclFloatArgIndex{1});
        bezier_1.y = full->context.current_context->get_float_arg(EclFloatArgIndex{2});
        bezier_1.z = 0.0f;
        Float3 bezier_2;
        bezier_2.x = full->context.current_context->get_float_arg(EclFloatArgIndex{5});
        bezier_2.y = full->context.current_context->get_float_arg(EclFloatArgIndex{6});
        bezier_2.z = 0.0f;
        i32 duration = full->context.current_context->get_int_arg(0);

        position_interp->flag_1d &= ~1;
        position_interp->end_time = duration;
        position_interp->bezier_1 = bezier_1;
        position_interp->bezier_2 = bezier_2;
        position_interp->method_for_3d = INTERP_BEZIER;
        goto ecl_move_curve_finish;
    }
    ecl_move_curve_finish:
        position_interp->initial = ((PosVel *)((u8 *)this + position_offset))->pos;
        position_interp->goal = Float3(goal_x > -999999.0 ? goal_x : ((PosVel *)((u8 *)this + position_offset))->pos.x,
                                       goal_y > -999999.0 ? goal_y : ((PosVel *)((u8 *)this + position_offset))->pos.y,
                                       0.0f);
        position_interp->reset_timer();
        ((PosVel *)((u8 *)this + position_offset))->flags &= ~0xf;
        break;
    }
    // moveVel(angle, speed) and the relative and
    // no-mirror (428, 430) forms. -999999 keeps the current value.
    case ECL_OP_MOVE_VEL:
    case ECL_OP_MOVE_VEL_REL:
    case ECL_OP_MOVE_VEL_NM:
    case ECL_OP_MOVE_VEL_REL_NM:
    {
        PosVel *pv = (instr->opcode == ECL_OP_MOVE_VEL || instr->opcode == ECL_OP_MOVE_VEL_NM)
                         ? &abs_pos
                         : &rel_pos;
        f32 angle = get_float_arg(EclFloatArgIndex{0});
        f32 speed = get_float_arg(EclFloatArgIndex{1});
        if (angle > -999999.0)
        {
            if ((flags_low & ENEMY_FLAG_MIRRORED) &&
                (instr->opcode == ECL_OP_MOVE_VEL || instr->opcode == ECL_OP_MOVE_VEL_REL))
            {
                angle = mirror_angle(angle);
            }
            pv->set_angle(angle);
        }
        if (speed > -999999.0)
        {
            pv->speed = speed;
        }
        pv->flags &= ~0xf;
        break;
    }
    // moveVelTime(time, mode, angle, speed). With mode 7
    // (constant velocity) angle and speed are per-frame changes instead.
    case ECL_OP_MOVE_VEL_TIME:
    case ECL_OP_MOVE_VEL_REL_TIME:
    case ECL_OP_MOVE_VEL_TIME_NM:
    case ECL_OP_MOVE_VEL_REL_TIME_NM:
    {
        PosVel *pv = (instr->opcode == ECL_OP_MOVE_VEL_TIME ||
                      instr->opcode == ECL_OP_MOVE_VEL_TIME_NM) ? &abs_pos : &rel_pos;
        InterpFloat *angle_i = (instr->opcode == ECL_OP_MOVE_VEL_TIME ||
                                 instr->opcode == ECL_OP_MOVE_VEL_TIME_NM) ? &abs_angle_i : &rel_angle_i;
        InterpFloat *speed_i = (instr->opcode == ECL_OP_MOVE_VEL_TIME ||
                                 instr->opcode == ECL_OP_MOVE_VEL_TIME_NM) ? &abs_speed_i : &rel_speed_i;
        f32 angle = full_owner->context.current_context->get_float_arg(EclFloatArgIndex{2});
        f32 speed = full->context.current_context->get_float_arg(EclFloatArgIndex{3});
        if (full->context.current_context->get_int_arg(0) <= 0)
        {
            angle_i->end_time = 0;
            speed_i->end_time = 0;
            break;
        }
        i32 mode = full->context.current_context->get_int_arg(1);
        if (mode != INTERP_CONSTANT_VELOCITY)
        {
            if (angle > -999999.0)
            {
                if ((flags_low & ENEMY_FLAG_MIRRORED) &&
                    (instr->opcode == ECL_OP_MOVE_VEL_TIME ||
                     instr->opcode == ECL_OP_MOVE_VEL_REL_TIME))
                {
                    angle = mirror_angle(angle);
                }
            }
            else
            {
                angle = pv->angle.value;
            }
            if (!(speed > -999999.0))
            {
                speed = pv->speed;
            }
        }
        else
        {
            if (angle > -999999.0)
            {
                if ((flags_low & ENEMY_FLAG_MIRRORED) &&
                    (instr->opcode == ECL_OP_MOVE_VEL_TIME ||
                     instr->opcode == ECL_OP_MOVE_VEL_REL_TIME))
                {
                    angle = -angle;
                }
            }
            else
            {
                angle = 0.0f;
            }
            if (!(speed > -999999.0))
            {
                speed = 0.0f;
            }
        }

        f32 initial_angle = pv->angle.value;
        f32 initial_speed = pv->speed;
        if (zun_fabsf(initial_angle - angle) >= ZUN_PI)
        {
            if (!(angle > initial_angle))
            {
                angle += ZUN_2PI;
            }
            else
            {
                initial_angle += ZUN_2PI;
            }
        }

        // The two interpolators each read their own duration, then write
        // initial, duration, method, tangents and goal before resetting.
        i32 angle_duration = full->context.current_context->get_int_arg(0);
        angle_i->initial = initial_angle;
        angle_i->end_time = angle_duration;
        angle_i->method = mode;
        angle_i->bezier_1 = 0.0f;
        angle_i->bezier_2 = 0.0f;
        angle_i->goal = angle;
        angle_i->reset();

        i32 speed_duration = full->context.current_context->get_int_arg(0);
        speed_i->initial = initial_speed;
        speed_i->end_time = speed_duration;
        speed_i->method = mode;
        speed_i->bezier_1 = 0.0f;
        speed_i->bezier_2 = 0.0f;
        speed_i->goal = speed;
        speed_i->reset();

        pv->flags &= ~0xf;
        break;
    }
    // moveAngle(angle). Mirrored whenever the flag is set.
    case ECL_OP_MOVE_ANGLE:
    case ECL_OP_MOVE_ANGLE_REL:
    {
        PosVel *pv = instr->opcode == ECL_OP_MOVE_ANGLE ? &abs_pos : &rel_pos;
        f32 angle = get_float_arg(EclFloatArgIndex{0});
        if (flags_low & ENEMY_FLAG_MIRRORED)
        {
            angle = mirror_angle(angle);
        }
        pv->set_angle(angle);
        pv->flags &= ~0xf;
        break;
    }
    // moveAngleTime(time, mode, angle).
    case ECL_OP_MOVE_ANGLE_TIME:
    case ECL_OP_MOVE_ANGLE_REL_TIME:
    {
        PosVel *pv = instr->opcode == ECL_OP_MOVE_ANGLE_TIME ? &abs_pos : &rel_pos;
        InterpFloat *angle_i = instr->opcode == ECL_OP_MOVE_ANGLE_TIME ? &abs_angle_i : &rel_angle_i;
        f32 angle = get_float_arg(EclFloatArgIndex{2});
        if (get_int_arg(0) <= 0)
        {
            angle_i->end_time = 0;
            break;
        }
        i32 mode = get_int_arg(1);
        if (mode != INTERP_CONSTANT_VELOCITY)
        {
            if (angle > -999999.0)
            {
                if ((flags_low & ENEMY_FLAG_MIRRORED) && (instr->opcode == ECL_OP_MOVE_ANGLE_TIME || instr->opcode == ECL_OP_MOVE_ANGLE_REL_TIME))
                {
                    angle = mirror_angle(angle);
                }
            }
            else
            {
                angle = pv->angle.value;
            }
        }
        else
        {
            if (angle > -999999.0)
            {
                if ((flags_low & ENEMY_FLAG_MIRRORED) && (instr->opcode == ECL_OP_MOVE_ANGLE_TIME || instr->opcode == ECL_OP_MOVE_ANGLE_REL_TIME))
                {
                    angle = -angle;
                }
            }
            else
            {
                angle = 0.0f;
            }
        }
        f32 initial = pv->angle.value;
        // The goal as an offset from the current angle, the short way round.
        f32 delta;
        if (angle - initial > ZUN_PI)
        {
            delta = angle - (initial + ZUN_2PI);
        }
        else if (initial - angle > ZUN_PI)
        {
            delta = angle - (initial - ZUN_2PI);
        }
        else
        {
            delta = angle - initial;
        }
        angle_i->end_time = get_int_arg(0);
        angle_i->method = mode;
        angle_i->bezier_1 = 0.0f;
        angle_i->bezier_2 = 0.0f;
        angle_i->initial = initial;
        angle_i->goal = delta + initial;
        angle_i->reset();
        pv->flags &= ~0xf;
        break;
    }
    // moveSpeed(speed).
    case ECL_OP_MOVE_SPEED:
    case ECL_OP_MOVE_SPEED_REL:
    {
        PosVel *pv = instr->opcode == ECL_OP_MOVE_SPEED ? &abs_pos : &rel_pos;
        f32 speed = get_float_arg(EclFloatArgIndex{0});
        if (speed > -999999.0)
        {
            pv->speed = speed;
        }
        pv->flags &= ~0xf;
        break;
    }
    // moveSpeedTime(time, mode, speed).
    case ECL_OP_MOVE_SPEED_TIME:
    case ECL_OP_MOVE_SPEED_REL_TIME:
    {
        PosVel *pv = instr->opcode == ECL_OP_MOVE_SPEED_TIME ? &abs_pos : &rel_pos;
        InterpFloat *speed_i = instr->opcode == ECL_OP_MOVE_SPEED_TIME ? &abs_speed_i : &rel_speed_i;
        f32 speed = get_float_arg(EclFloatArgIndex{2});
        f32 initial = pv->speed;
        if (get_int_arg(0) <= 0)
        {
            speed_i->end_time = 0;
            break;
        }
        i32 mode = get_int_arg(1);
        if (mode != INTERP_CONSTANT_VELOCITY)
        {
            speed = speed > -999999.0 ? speed : pv->speed;
        }
        else
        {
            speed = speed > -999999.0 ? speed : 0.0f;
        }
        speed_i->start(get_int_arg(0), mode, initial, speed);
        pv->flags &= ~0xf;
        break;
    }
    // moveCircle(angle, angular speed, radius, radial speed),
    // around the current position unless already circling.
    case ECL_OP_MOVE_CIRCLE:
    case ECL_OP_MOVE_CIRCLE_REL:
    {
        PosVel *pv = instr->opcode == ECL_OP_MOVE_CIRCLE ? &abs_pos : &rel_pos;
        f32 angle = get_float_arg(EclFloatArgIndex{0});
        f32 speed = get_float_arg(EclFloatArgIndex{1});
        f32 radius = get_float_arg(EclFloatArgIndex{2});
        f32 radial_speed = get_float_arg(EclFloatArgIndex{3});
        if ((pv->flags & POSVEL_MODE_MASK) != POSVEL_MODE_CIRCLE)
        {
            pv->velocity = pv->pos;
        }
        if (angle > -999999.0)
        {
            pv->set_angle(angle);
        }
        if (speed > -999999.0)
        {
            pv->speed = speed;
        }
        if (radius > -999999.0)
        {
            pv->radial_dist = radius;
        }
        if (radial_speed > -999999.0)
        {
            pv->radial_speed = radial_speed;
        }
        pv->flags = pv->flags & ~0xf | POSVEL_MODE_CIRCLE;
        pv->step_from_center();
        update_final_pos();
        break;
    }
    // moveCircleTime(time, mode, angular speed, radius, radial
    // speed).
    case ECL_OP_MOVE_CIRCLE_TIME:
    case ECL_OP_MOVE_CIRCLE_REL_TIME:
    {
        PosVel *pv = instr->opcode == ECL_OP_MOVE_CIRCLE_TIME ? &abs_pos : &rel_pos;
        InterpFloat *speed_i = instr->opcode == ECL_OP_MOVE_CIRCLE_TIME ? &abs_speed_i : &rel_speed_i;
        InterpFloat2 *radial_i = instr->opcode == ECL_OP_MOVE_CIRCLE_TIME ? &abs_radial_dist_i : &rel_radial_dist_i;
        f32 speed = get_float_arg(EclFloatArgIndex{2});
        f32 radius = get_float_arg(EclFloatArgIndex{3});
        f32 radial_speed = get_float_arg(EclFloatArgIndex{4});
        speed = speed > -999999.0 ? speed : pv->speed;
        f32 initial_speed = pv->speed;
        volatile f32 goal_radial_speed = radial_speed > -999999.0 ? radial_speed : pv->radial_speed;
        volatile f32 goal_radius = radius > -999999.0 ? radius : pv->radial_dist;
        f32 initial_radius = pv->radial_dist;
        f32 initial_radial_speed = pv->radial_speed;
        i32 time = get_int_arg(0);
        i32 mode = get_int_arg(1);
        if (time <= 0)
        {
            speed_i->end_time = 0;
            radial_i->end_time = 0;
            break;
        }
        speed_i->start(time, mode, initial_speed, speed);
        radial_i->end_time = time;
        radial_i->bezier_1 = g_zero_vec2;
        radial_i->bezier_2 = g_zero_vec2;
        radial_i->method = mode;
        u32 radial_bits;
        memcpy(&radial_bits, &initial_radius, sizeof(radial_bits));
        *(volatile u32 *)&radial_i->initial.x = radial_bits;
        memcpy(&radial_bits, &initial_radial_speed, sizeof(radial_bits));
        *(volatile u32 *)&radial_i->initial.y = radial_bits;
        radial_bits = *(volatile u32 *)&goal_radius;
        *(volatile u32 *)&radial_i->goal.x = radial_bits;
        radial_bits = *(volatile u32 *)&goal_radial_speed;
        *(volatile u32 *)&radial_i->goal.y = radial_bits;
        radial_i->reset_timer();
        pv->flags = pv->flags & ~0xf | POSVEL_MODE_CIRCLE;
        pv->step_from_center();
        update_final_pos();
        break;
    }
    // moveAdd (ExpHP): sets the center of circular and elliptic
    // movement.
    case ECL_OP_MOVE_ADD:
    case ECL_OP_MOVE_ADD_REL:
    {
        PosVel *pv = instr->opcode == ECL_OP_MOVE_ADD ? &abs_pos : &rel_pos;
        f32 x = get_float_arg(EclFloatArgIndex{0});
        f32 y = get_float_arg(EclFloatArgIndex{1});
        if (x > -999999.0)
        {
            pv->velocity.x = x;
        }
        if (y > -999999.0)
        {
            pv->velocity.y = y;
        }
        pv->step_from_center();
        update_final_pos();
    }
    // No break in the original: 418 and 419 go on into moveEllipse.
    // moveEllipse(angle, angular speed, radius, radial speed,
    // ellipse angle, ellipse ratio).
    case ECL_OP_MOVE_ELLIPSE:
    case ECL_OP_MOVE_ELLIPSE_REL:
    {
        PosVel *pv = instr->opcode == ECL_OP_MOVE_ELLIPSE ? &abs_pos : &rel_pos;
        f32 angle = get_float_arg(EclFloatArgIndex{0});
        f32 speed = get_float_arg(EclFloatArgIndex{1});
        f32 radius = get_float_arg(EclFloatArgIndex{2});
        f32 radial_speed = get_float_arg(EclFloatArgIndex{3});
        f32 ellipse_angle = get_float_arg(EclFloatArgIndex{4});
        f32 ellipse_ratio = get_float_arg(EclFloatArgIndex{5});
        if ((pv->flags & POSVEL_MODE_MASK) != POSVEL_MODE_CIRCLE)
        {
            pv->velocity = pv->pos;
        }
        if (angle > -999999.0)
        {
            pv->set_angle(angle);
        }
        if (speed > -999999.0)
        {
            pv->speed = speed;
        }
        if (radius > -999999.0)
        {
            pv->radial_dist = radius;
        }
        if (radial_speed > -999999.0)
        {
            pv->radial_speed = radial_speed;
        }
        if (ellipse_angle > -999999.0)
        {
            pv->set_ellipse_angle(ellipse_angle);
        }
        if (ellipse_ratio > -999999.0)
        {
            pv->ellipse_ratio = ellipse_ratio;
        }
        pv->flags = pv->flags & ~0xf | POSVEL_MODE_ELLIPSE;
        pv->step_from_center();
        update_final_pos();
        break;
    }
    // moveEllipseTime(time, mode, angular speed, radius, radial
    // speed, ellipse angle, ellipse ratio). Always restarts around the
    // current position.
    case ECL_OP_MOVE_ELLIPSE_TIME:
    case ECL_OP_MOVE_ELLIPSE_REL_TIME:
    {
        PosVel *pv = instr->opcode == ECL_OP_MOVE_ELLIPSE_TIME ? &abs_pos : &rel_pos;
        InterpFloat *speed_i = instr->opcode == ECL_OP_MOVE_ELLIPSE_TIME ? &abs_speed_i : &rel_speed_i;
        InterpFloat2 *radial_i = instr->opcode == ECL_OP_MOVE_ELLIPSE_TIME ? &abs_radial_dist_i : &rel_radial_dist_i;
        InterpFloat2 *ellipse_i = instr->opcode == ECL_OP_MOVE_ELLIPSE_TIME ? &abs_ellipse_i : &rel_ellipse_i;
        f32 speed = get_float_arg(EclFloatArgIndex{2});
        f32 radius = get_float_arg(EclFloatArgIndex{3});
        f32 radial_speed = get_float_arg(EclFloatArgIndex{4});
        f32 ellipse_angle = get_float_arg(EclFloatArgIndex{5});
        f32 ellipse_ratio = get_float_arg(EclFloatArgIndex{6});
        speed = speed > -999999.0 ? speed : pv->speed;
        f32 initial_speed = pv->speed;
        volatile f32 goal_radial_speed;
        if (!(radial_speed > -999999.0))
        {
            goal_radial_speed = pv->radial_speed;
        }
        else
        {
            goal_radial_speed = radial_speed;
        }
        volatile f32 goal_radius = radius > -999999.0 ? radius : pv->radial_dist;
        f32 initial_radius = pv->radial_dist;
        f32 initial_radial_speed = pv->radial_speed;
        volatile f32 goal_ellipse_ratio = ellipse_ratio > -999999.0 ? ellipse_ratio : pv->ellipse_ratio;
        volatile f32 goal_ellipse_angle = ellipse_angle > -999999.0 ? ellipse_angle : pv->ellipse_angle.value;
        f32 initial_ellipse_angle = pv->ellipse_angle.value;
        f32 initial_ellipse_ratio = pv->ellipse_ratio;
        i32 time = get_int_arg(0);
        i32 mode = get_int_arg(1);
        if (time <= 0)
        {
            speed_i->end_time = 0;
            radial_i->end_time = 0;
            ellipse_i->end_time = 0;
            break;
        }
        speed_i->start(time, mode, initial_speed, speed);
        radial_i->end_time = time;
        radial_i->bezier_1 = g_zero_vec2;
        radial_i->bezier_2 = g_zero_vec2;
        radial_i->method = mode;
        u32 radial_bits;
        memcpy(&radial_bits, &initial_radius, sizeof(radial_bits));
        *(volatile u32 *)&radial_i->initial.x = radial_bits;
        memcpy(&radial_bits, &initial_radial_speed, sizeof(radial_bits));
        *(volatile u32 *)&radial_i->initial.y = radial_bits;
        radial_bits = *(volatile u32 *)&goal_radius;
        *(volatile u32 *)&radial_i->goal.x = radial_bits;
        radial_bits = *(volatile u32 *)&goal_radial_speed;
        *(volatile u32 *)&radial_i->goal.y = radial_bits;
        radial_i->reset_timer();

        ellipse_i->end_time = time;
        ellipse_i->bezier_1 = g_zero_vec2;
        ellipse_i->bezier_2 = g_zero_vec2;
        ellipse_i->method = mode;
        u32 ellipse_bits;
        memcpy(&ellipse_bits, &initial_ellipse_angle, sizeof(ellipse_bits));
        *(volatile u32 *)&ellipse_i->initial.x = ellipse_bits;
        memcpy(&ellipse_bits, &initial_ellipse_ratio, sizeof(ellipse_bits));
        *(volatile u32 *)&ellipse_i->initial.y = ellipse_bits;
        ellipse_bits = *(volatile u32 *)&goal_ellipse_angle;
        *(volatile u32 *)&ellipse_i->goal.x = ellipse_bits;
        ellipse_bits = *(volatile u32 *)&goal_ellipse_ratio;
        *(volatile u32 *)&ellipse_i->goal.y = ellipse_bits;
        ellipse_i->reset_timer();
        pv->velocity = pv->pos;
        pv->flags = pv->flags & ~0xf | POSVEL_MODE_ELLIPSE;
        pv->step_from_center();
        update_final_pos();
        break;
    }
    // moveBoss(): jumps to the boss.
    case ECL_OP_MOVE_BOSS:
        abs_pos.pos = g_EnemyManager->get_boss(0)->enemy.final_pos.pos;
        break;
    // moveBossRel().
    case ECL_OP_MOVE_BOSS_REL:
        rel_pos.pos = g_EnemyManager->get_boss(0)->enemy.final_pos.pos;
        break;
    // moveEnm(enemy id): jumps to another enemy.
    case ECL_OP_MOVE_ENM:
        abs_pos.pos = g_EnemyManager->find_enemy_by_id(get_int_arg(0))->enemy.final_pos.pos;
        break;
    // moveEnmRel(enemy id).
    case ECL_OP_MOVE_ENM_REL:
        rel_pos.pos = g_EnemyManager->find_enemy_by_id(get_int_arg(0))->enemy.final_pos.pos;
        break;
    // moveLimit(x, y, width, height): keeps final_pos inside the
    // rectangle (see update_final_pos).
    case ECL_OP_MOVE_LIMIT:
        flags_low |= ENEMY_FLAG_MOVE_LIMIT;
        move_limit_center.x = get_float_arg(EclFloatArgIndex{0});
        move_limit_center.y = get_float_arg(EclFloatArgIndex{1});
        move_limit_size.x = get_float_arg(EclFloatArgIndex{2});
        move_limit_size.y = get_float_arg(EclFloatArgIndex{3});
        break;
    // moveLimitReset().
    case ECL_OP_MOVE_LIMIT_RESET:
        flags_low &= ~ENEMY_FLAG_MOVE_LIMIT;
        break;
    // etProtectRange(radius), kept squared.
    case ECL_OP_ET_PROTECT_RANGE:
    {
        f32 range = get_float_arg(EclFloatArgIndex{0});
        et_protect_range = range * range;
        break;
    }

    // moveRand(time, mode, speed) and moveRandRel: choose a direction
    // that keeps the enemy inside its movement limit, then slow to a stop.
    case ECL_OP_MOVE_RAND:
    case ECL_OP_MOVE_RAND_REL:
    {
        PosVel *pv = instr->opcode == ECL_OP_MOVE_RAND ? &abs_pos : &rel_pos;
        InterpFloat *angle_i = instr->opcode == ECL_OP_MOVE_RAND ? &abs_angle_i : &rel_angle_i;
        InterpFloat *speed_i = instr->opcode == ECL_OP_MOVE_RAND ? &abs_speed_i : &rel_speed_i;

        f32 current_x = final_pos.pos.x;
        f32 center_x = move_limit_center.x;
        f32 half_width = move_limit_size.x * ecl_move_rand_quarter;
        f32 left = center_x - half_width;
        f32 right = center_x + half_width;
        f32 angle;
        if (left > current_x)
        {
            angle = g_replay_safe_rng.randf_neg_1_to_1_times_pi() / ecl_move_rand_third;
        }
        else
        {
            if (right < current_x)
            {
                angle = g_replay_safe_rng.randf_neg_1_to_1_times_pi() / ecl_move_rand_third;
                angle += ecl_move_rand_pi;
                angle = normalize_angle(angle);
            }
            else if (g_Player->inner.pos.x > current_x)
            {
                angle = g_replay_safe_rng.randf_neg_1_to_1_times_pi() * ecl_move_rand_quarter;
                if (g_replay_safe_rng.rand_u16() % 3 == 0)
                {
                    angle += ecl_move_rand_pi;
                }
            }
            else
            {
                angle = g_replay_safe_rng.randf_neg_1_to_1_times_pi() * ecl_move_rand_quarter;
                if (g_replay_safe_rng.rand_u16() % 3 != 0)
                {
                    angle += ecl_move_rand_pi;
                }
            }
        }

        f32 current_y = final_pos.pos.y;
        f32 half_height = move_limit_size.y * ecl_move_rand_quarter;
        f32 lower = move_limit_center.y - half_height;
        if (lower > current_y)
        {
            angle = zun_fabsf(angle);
        }
        else
        {
            f32 upper = move_limit_center.y + half_height;
            if (current_y > upper)
            {
                angle = -zun_fabsf(angle);
            }
        }

        f32 negative_vertical_distance = zun_fabsf(angle + ecl_move_rand_half_pi);
        if (negative_vertical_distance < ecl_move_rand_five_cents)
        {
            angle = (ecl_move_rand_neg_half_pi > angle) ? ecl_move_rand_neg_half_pi_low
                                                        : ecl_move_rand_neg_half_pi_high;
        }
        else
        {
            f32 positive_vertical_distance = zun_fabsf(angle - ecl_move_rand_half_pi);
            if ((double)positive_vertical_distance < ecl_move_rand_five_cents_double)
            {
                angle = (ecl_move_rand_half_pi > angle) ? ecl_move_rand_pos_half_pi_low
                                                        : ecl_move_rand_pos_half_pi_high;
            }
        }

        i32 mode = get_int_arg(1);
        f32 speed = get_float_arg(EclFloatArgIndex{2});

        angle_i->end_time = get_int_arg(0);
        angle_i->method = mode;
        angle_i->bezier_1 = 0.0f;
        angle_i->bezier_2 = 0.0f;
        angle_i->initial = angle;
        angle_i->goal = angle;
        angle_i->reset();

        speed_i->end_time = get_int_arg(0);
        speed_i->method = mode;
        speed_i->bezier_1 = 0.0f;
        speed_i->bezier_2 = 0.0f;
        speed_i->initial = speed;
        speed_i->goal = 0.0f;
        speed_i->reset();

        pv->flags &= ~0xf;
        break;
    }
    // lifeMarker(index, life, color): a marker on the boss life bar.
    case ECL_OP_LIFE_MARKER:
    {
        // The target loads life.maximum before fetching the color, ratio and
        // marker-life arguments, in that order.
        i32 maximum = life.maximum;
        i32 color = get_int_arg(2);
        f32 ratio = get_float_arg(EclFloatArgIndex{1}) / maximum;
        i32 marker_life = get_int_arg(0);
        g_Gui->set_boss_life_marker(own_boss_id, marker_life, ratio, color);
        break;
    }
    // funcSet(index): a per-frame hook (g_ecl_func_sets).
    case ECL_OP_FUNC_SET:
        func_from_ecl_func_set = (void *)g_ecl_func_sets[get_int_arg(0)];
        is_func_set_2 = 0;
        break;
    // funcSet2(index): the same, flagged as the second kind.
    case ECL_OP_FUNC_SET2:
        func_from_ecl_func_set = (void *)g_ecl_func_sets[get_int_arg(0)];
        is_func_set_2 = 1;
        break;
    // flagExtDmg(index): a damage hook.
    case ECL_OP_FLAG_EXT_DMG:
        func_from_ecl_flag_ext_dmg = (void *)g_ecl_ext_damage_funcs[get_int_arg(0)];
        break;
    // unknown634(index)
    case ECL_OP_UNKNOWN_634:
        func_from_ecl_unknown_634 = g_ecl_unknown_634_funcs[get_int_arg(0)];
        break;
    // funcCall(index): runs a hook of g_ecl_func_sets once.
    case ECL_OP_FUNC_CALL:
        g_ecl_func_sets[get_int_arg(0)](this);
        break;
    // setHurtbox(w, h). The first call also counts the enemy as spawned in
    // the chapter.
    case ECL_OP_SET_HURTBOX:
        hurtbox_size.x = get_float_arg(EclFloatArgIndex{0});
        hurtbox_size.y = get_float_arg(EclFloatArgIndex{1});
        if (chapter_count == 0)
        {
            chapter_count = 1;
            g_Globals.enemies_spawned_in_chapter++;
        }
        break;
    // setHitbox(w, h)
    case ECL_OP_SET_HITBOX:
        hitbox_size.x = get_float_arg(EclFloatArgIndex{0});
        hitbox_size.y = get_float_arg(EclFloatArgIndex{1});
        break;
    // unknown569(count): how many enemies this one counts as in the chapter
    // statistics.
    case ECL_OP_CHAPTER_COUNT:
        if (chapter_count == 0)
        {
            chapter_count = get_int_arg(0);
            if (chapter_count > 0)
            {
                g_Globals.enemies_spawned_in_chapter += chapter_count;
            }
        }
        else if (chapter_count == 1)
        {
            chapter_count = get_int_arg(0);
            g_Globals.enemies_spawned_in_chapter += chapter_count - 1;
        }
        break;
    // unknown570(): counts the enemy as destroyed now.
    case ECL_OP_COUNT_DESTROYED:
        if (chapter_count != 0 && own_chapter == g_Globals.chapter)
        {
            g_Globals.enemies_destroyed_in_chapter += chapter_count;
            chapter_count = 0;
        }
        break;
    // unknown563(on)
    case ECL_OP_RECT_HITBOX:
        ((EnemyFlagsLow *)&flags_low)->rect_hitbox = get_int_arg(0);
        break;
    // unknown564(angle): sets rotation.
    case ECL_OP_SET_ROTATION:
        rotation = get_float_arg(EclFloatArgIndex{0});
        break;
    // bombInvuln(multiplier): damage taken from bombs.
    case ECL_OP_BOMB_INVULN:
        bomb_damage_multiplier = get_float_arg(EclFloatArgIndex{0});
        break;
    // flagSet(flags)
    case ECL_OP_FLAG_SET:
        flags_low |= get_int_arg(0);
        if (flags_low & ENEMY_FLAG_INTANGIBLE)
        {
            for (i32 i = 0; i < 16; i++)
            {
                anm_ids[i].hide_tree();
            }
        }
        break;
    // flagClear(flags)
    case ECL_OP_FLAG_CLEAR:
        flags_low &= ~get_int_arg(0);
        if (!((EnemyFlagsLow *)&flags_low)->intangible)
        {
            for (i32 i = 0; i < 16; i++)
            {
                anm_ids[i].show_tree();
            }
        }
        break;
    // dropClear(): forgets the extra drops except the season items.
    case ECL_OP_DROP_CLEAR:
    {
        i32 season_items = drops.extra_counts[15];
        memset(drops.extra_counts, 0, sizeof(drops.extra_counts));
        drops.extra_counts[15] = season_items;
        break;
    }
    // dropExtra(item_type, count)
    case ECL_OP_DROP_EXTRA:
    {
        i32 type = get_int_arg(0);
        drops.extra_counts[type - 1] = get_int_arg(1);
        break;
    }
    // dropArea(w, h)
    case ECL_OP_DROP_AREA:
    {
        f32 w = get_float_arg(EclFloatArgIndex{0});
        f32 h = get_float_arg(EclFloatArgIndex{1});
        drops.area.x = w;
        drops.area.y = h;
        break;
    }
    // dropItems(): drops everything now (not in spell practice). Season
    // items shrink with the bonus timer, as in EnemyInf::die.
    case ECL_OP_DROP_ITEMS:
        if (g_Globals.game_mode == GAME_MODE_SPELL_PRACTICE)
        {
            break;
        }
        if (drop_season.bonus_timer.current <= 0)
        {
            drops.extra_counts[15] = drop_season.min_count;
        }
        else
        {
            drops.extra_counts[15] =
                (drops.extra_counts[15] - drop_season.min_count) * drop_season.bonus_timer.current /
                    drop_season.max_time +
                drop_season.min_count;
        }
    // unknown562(): drops everything now, in any mode.
    case ECL_OP_DROP_ITEMS_ANY_MODE:
        drops.eject_all_drops(&final_pos.pos);
        break;
    // dropMain(item_type)
    case ECL_OP_DROP_MAIN:
        drops.main_type = get_int_arg(0);
        break;
    // lifeSet(life)
    case ECL_OP_LIFE_SET:
    {
        i32 value = get_int_arg(0);
        life.current = value;
        life.maximum = value;
        life.remaining_for_cur_attack = value;
        if (flags_low & ENEMY_FLAG_BOSS)
        {
            ((EnemyFlagsLow *)&flags_low)->big_life = 1;
        }
        life.current_scaled_by_seven = value * 7;
        break;
    }
    // lifeNow(life)
    case ECL_OP_LIFE_NOW:
    {
        i32 value = get_int_arg(0);
        life.current = value;
        life.current_scaled_by_seven = value * 7;
        break;
    }
    // setBoss(id): makes this enemy boss id, or stops being a boss if id
    // is negative.
    case ECL_OP_SET_BOSS:
    {
        i32 boss_id = get_int_arg(0);
        g_EnemyManager->set_life_bar_hidden(0);
        if (boss_id < 0)
        {
            if (flags_low & ENEMY_FLAG_BOSS)
            {
                g_EnemyManager->inner.boss_ids[own_boss_id] = 0;
            }
            flags_low &= ~ENEMY_FLAG_BOSS;
        }
        else
        {
            flags_low |= ENEMY_FLAG_BOSS;
            g_EnemyManager->set_boss_id(boss_id, full);
            own_boss_id = boss_id;
        }
        break;
    }
    // setInvuln(time)
    case ECL_OP_SET_INVULN:
        set_invuln.set_value(get_int_arg(0));
        break;
    // unknown541(time): no hitbox for a while.
    case ECL_OP_NO_HITBOX_TIME:
        no_hitbox_dur.set_value(get_int_arg(0));
        break;
    // unknown551(value): kills the enemies whose kill_group is value.
    case ECL_OP_KILL_GROUP:
        EnemyManager::kill_all_in_group(get_int_arg(0));
        break;
    // unknown571(): kills every enemy without running set_death.
    case ECL_OP_KILL_ALL_NO_DEATH:
        EnemyManager::kill_all_no_set_death();
        break;
    // diffI(var, easy, normal, hard, lunatic)
    case ECL_OP_DIFF_I:
    {
        i32 easy = get_int_arg(1);
        i32 normal = get_int_arg(2);
        i32 hard = get_int_arg(3);
        i32 lunatic = get_int_arg(4);
        switch (g_Globals.difficulty)
        {
        case DIFFICULTY_EASY:
            *get_int_arg_ptr(0) = easy;
            break;
        case DIFFICULTY_NORMAL:
            *get_int_arg_ptr(0) = normal;
            break;
        case DIFFICULTY_HARD:
            *get_int_arg_ptr(0) = hard;
            break;
        case DIFFICULTY_LUNATIC:
            *get_int_arg_ptr(0) = lunatic;
            break;
        default:
            *get_int_arg_ptr(0) = lunatic;
            break;
        }
        break;
    }
    // diffF(var, easy, normal, hard, lunatic)
    case ECL_OP_DIFF_F:
    {
        f32 easy = get_float_arg(EclFloatArgIndex{1});
        f32 normal = get_float_arg(EclFloatArgIndex{2});
        f32 hard = get_float_arg(EclFloatArgIndex{3});
        f32 lunatic = get_float_arg(EclFloatArgIndex{4});
        switch (g_Globals.difficulty)
        {
        case DIFFICULTY_EASY:
            *get_float_arg_ptr(0) = easy;
            break;
        case DIFFICULTY_NORMAL:
            *get_float_arg_ptr(0) = normal;
            break;
        case DIFFICULTY_HARD:
            *get_float_arg_ptr(0) = hard;
            break;
        case DIFFICULTY_LUNATIC:
            *get_float_arg_ptr(0) = lunatic;
            break;
        default:
            *full->context.current_context->get_float_arg_ptr(0) = lunatic;
            break;
        }
        break;
    }
    // etNew(slot): resets a bullet shooter to one 2.0 speed bullet.
    case ECL_OP_ET_NEW:
    {
        i32 slot = get_int_arg(0);
        memset(&bullet_props[slot], 0, sizeof(EnemyBulletShooter));
        bullet_props[slot].ang_aim = 0.0f;
        bullet_props[slot].spd1 = 2.0f;
        bullet_props[slot].count = 1;
        bullet_props[slot].layers = 1;
        bullet_props[slot].shot_sfx = 21;
        bullet_props[slot].shot_transform_sfx = 38;
        bullet_props[slot].sfx_flags = 0x23;
        bullet_mgr_offsets[slot].xy.x = 0.0f;
        bullet_mgr_offsets[slot].xy.y = 0.0f;
        bullet_mgr_origins[slot].xy.x = 0.0f;
        bullet_mgr_origins[slot].xy.y = 0.0f;
        bullet_mgr_origins[slot].z = 0.0f;
        et_ex_index[slot] = 0;
        break;
    }
    // etCopy(dst, src)
    case ECL_OP_ET_COPY:
    {
        i32 dst = get_int_arg(0);
        i32 src = get_int_arg(1);
        bullet_props[dst] = bullet_props[src];
        bullet_mgr_offsets[dst] = bullet_mgr_offsets[src];
        bullet_mgr_origins[dst] = bullet_mgr_origins[src];
        break;
    }
    // etOn(slot): fires from an absolute origin when set, otherwise from
    // the enemy's final position; both forms include the slot offset.
    case ECL_OP_ET_ON:
    {
        i32 slot = get_int_arg(0);
        if (bullet_mgr_origins[slot].z > 0.9f)
        {
            bullet_props[slot].pos = D3DXVECTOR3(
                bullet_mgr_origins[slot].xy.x + bullet_mgr_offsets[slot].xy.x,
                bullet_mgr_origins[slot].xy.y + bullet_mgr_offsets[slot].xy.y, 0.0f);
        }
        else
        {
            bullet_props[slot].pos = D3DXVECTOR3(
                final_pos.pos.x + bullet_mgr_offsets[slot].xy.x,
                final_pos.pos.y + bullet_mgr_offsets[slot].xy.y,
                final_pos.pos.z + bullet_mgr_offsets[slot].z);
        }
        g_BulletManager->et_protect_range = et_protect_range;
        g_BulletManager->shoot_bullets(&bullet_props[slot]);
        g_BulletManager->et_protect_range = 0.0f;
        break;
    }
    // etSprite(slot, type, color)
    case ECL_OP_ET_SPRITE:
    {
        i32 slot = get_int_arg(0);
        bullet_props[slot].type = get_int_arg(1);
        bullet_props[slot].color = get_int_arg(2);
        break;
    }
    // etOffset(slot, x, y)
    case ECL_OP_ET_OFFSET:
    {
        i32 slot = get_int_arg(0);
        bullet_mgr_offsets[slot].xy.x = get_float_arg(EclFloatArgIndex{1});
        bullet_mgr_offsets[slot].xy.y = get_float_arg(EclFloatArgIndex{2});
        break;
    }
    // etOffsetRad(slot, angle, dist)
    case ECL_OP_ET_OFFSET_RAD:
    {
        i32 slot = get_int_arg(0);
        f32 angle = get_float_arg(EclFloatArgIndex{1});
        Float3 offset;
        enemy_ecl_sincosmul(&offset, angle, get_float_arg(EclFloatArgIndex{2}));
        bullet_mgr_offsets[slot].xy.x = offset.x;
        bullet_mgr_offsets[slot].xy.y = offset.y;
        break;
    }
    // etDist(slot, dist)
    case ECL_OP_ET_DIST:
    {
        i32 slot = get_int_arg(0);
        bullet_props[slot].distance = get_float_arg(EclFloatArgIndex{1});
        break;
    }
    // etOffsetAbs(slot, x, y): fire from an absolute position; x below
    // -990 goes back to firing from the enemy.
    case ECL_OP_ET_OFFSET_ABS:
    {
        i32 slot = get_int_arg(0);
        bullet_mgr_origins[slot].xy.x = get_float_arg(EclFloatArgIndex{1});
        bullet_mgr_origins[slot].xy.y = get_float_arg(EclFloatArgIndex{2});
        if (-990.0f > bullet_mgr_origins[slot].xy.x)
        {
            bullet_mgr_origins[slot].z = 0.0f;
        }
        else
        {
            bullet_mgr_origins[slot].z = 1.0f;
        }
        break;
    }
    // etAngle(slot, aim, spread)
    case ECL_OP_ET_ANGLE:
    {
        i32 slot = get_int_arg(0);
        bullet_props[slot].ang_aim = get_float_arg(EclFloatArgIndex{1});
        bullet_props[slot].ang_bullet_dist = get_float_arg(EclFloatArgIndex{2});
        break;
    }
    // etSpeed(slot, speed1, speed2)
    case ECL_OP_ET_SPEED:
    {
        i32 slot = get_int_arg(0);
        bullet_props[slot].spd1 = get_float_arg(EclFloatArgIndex{1});
        bullet_props[slot].spd2 = get_float_arg(EclFloatArgIndex{2});
        break;
    }
    // etCount(slot, count, layers)
    case ECL_OP_ET_COUNT:
    {
        i32 slot = get_int_arg(0);
        bullet_props[slot].count = get_int_arg(1);
        bullet_props[slot].layers = get_int_arg(2);
        break;
    }
    // etSpeedD(slot, speed1 x4, speed2 x4): etSpeed per difficulty.
    case ECL_OP_ET_SPEED_D:
    {
        i32 slot = get_int_arg(0);
        bullet_props[slot].spd1 = ECL_DIFF_FLOAT_ARG(1);
        bullet_props[slot].spd2 = ECL_DIFF_FLOAT_ARG(5);
        break;
    }
    // etCountD(slot, count x4, layers x4): etCount per difficulty.
    case ECL_OP_ET_COUNT_D:
    {
        i32 slot = get_int_arg(0);
        bullet_props[slot].count = ECL_DIFF_ARG((u16)get_int_arg, 1);
        bullet_props[slot].layers = ECL_DIFF_ARG((u16)get_int_arg, 5);
        break;
    }
    // etSpeedR3(slot, speed1, speed2 x3): etSpeed by rank (low, mid, high).
    case ECL_OP_ET_SPEED_R3:
    {
        i32 slot = get_int_arg(0);
        if (g_Globals.rank >= 512)
        {
            bullet_props[slot].spd1 = get_float_arg(EclFloatArgIndex{5});
            bullet_props[slot].spd2 = get_float_arg(EclFloatArgIndex{6});
        }
        else if (g_Globals.rank >= -512)
        {
            bullet_props[slot].spd1 = get_float_arg(EclFloatArgIndex{3});
            bullet_props[slot].spd2 = get_float_arg(EclFloatArgIndex{4});
        }
        else
        {
            bullet_props[slot].spd1 = get_float_arg(EclFloatArgIndex{1});
            bullet_props[slot].spd2 = get_float_arg(EclFloatArgIndex{2});
        }
        break;
    }
    // etSpeedR5(slot, speed1, speed2 x5): etSpeed by rank in five steps.
    case ECL_OP_ET_SPEED_R5:
    {
        i32 slot = get_int_arg(0);
        if (g_Globals.rank >= 600)
        {
            bullet_props[slot].spd1 = get_float_arg(EclFloatArgIndex{9});
            bullet_props[slot].spd2 = get_float_arg(EclFloatArgIndex{10});
        }
        else if (g_Globals.rank >= 200)
        {
            bullet_props[slot].spd1 = get_float_arg(EclFloatArgIndex{7});
            bullet_props[slot].spd2 = get_float_arg(EclFloatArgIndex{8});
        }
        else if (g_Globals.rank >= -200)
        {
            bullet_props[slot].spd1 = get_float_arg(EclFloatArgIndex{5});
            bullet_props[slot].spd2 = get_float_arg(EclFloatArgIndex{6});
        }
        else if (g_Globals.rank >= -600)
        {
            bullet_props[slot].spd1 = get_float_arg(EclFloatArgIndex{3});
            bullet_props[slot].spd2 = get_float_arg(EclFloatArgIndex{4});
        }
        else
        {
            bullet_props[slot].spd1 = get_float_arg(EclFloatArgIndex{1});
            bullet_props[slot].spd2 = get_float_arg(EclFloatArgIndex{2});
        }
        break;
    }
    // etSpeedR2(slot, speed1, speed2 at rank -1024, then at rank 1024):
    // interpolated by rank.
    case ECL_OP_ET_SPEED_R2:
    {
        i32 slot = get_int_arg(0);
        f32 low1 = get_float_arg(EclFloatArgIndex{1});
        f32 low2 = get_float_arg(EclFloatArgIndex{2});
        f32 high1 = get_float_arg(EclFloatArgIndex{3});
        f32 high2 = get_float_arg(EclFloatArgIndex{4});
        bullet_props[slot].spd1 = (high1 - low1) * (g_Globals.rank + 1024.0f) / 2048.0f + low1;
        bullet_props[slot].spd2 = (high2 - low2) * (g_Globals.rank + 1024.0f) / 2048.0f + low2;
        break;
    }
    // etCountR3(slot, count, layers x3)
    case ECL_OP_ET_COUNT_R3:
    {
        i32 slot = get_int_arg(0);
        if (g_Globals.rank >= 512)
        {
            bullet_props[slot].count = get_int_arg(5);
            bullet_props[slot].layers = get_int_arg(6);
        }
        else if (g_Globals.rank >= -512)
        {
            bullet_props[slot].count = get_int_arg(3);
            bullet_props[slot].layers = get_int_arg(4);
        }
        else
        {
            bullet_props[slot].count = get_int_arg(1);
            bullet_props[slot].layers = get_int_arg(2);
        }
        break;
    }
    // etCountR5(slot, count, layers x5)
    case ECL_OP_ET_COUNT_R5:
    {
        i32 slot = get_int_arg(0);
        if (g_Globals.rank >= 600)
        {
            bullet_props[slot].count = get_int_arg(9);
            bullet_props[slot].layers = get_int_arg(10);
        }
        else if (g_Globals.rank >= 200)
        {
            bullet_props[slot].count = get_int_arg(7);
            bullet_props[slot].layers = get_int_arg(8);
        }
        else if (g_Globals.rank >= -200)
        {
            bullet_props[slot].count = get_int_arg(5);
            bullet_props[slot].layers = get_int_arg(6);
        }
        else if (g_Globals.rank >= -600)
        {
            bullet_props[slot].count = get_int_arg(3);
            bullet_props[slot].layers = get_int_arg(4);
        }
        else
        {
            bullet_props[slot].count = get_int_arg(1);
            bullet_props[slot].layers = get_int_arg(2);
        }
        break;
    }
    // etCountR2(slot, count, layers at rank -1024, then at rank 1024)
    case ECL_OP_ET_COUNT_R2:
    {
        i32 slot = get_int_arg(0);
        i32 low_count = get_int_arg(1);
        i32 low_layers = get_int_arg(2);
        i32 high_count = get_int_arg(3);
        i32 high_layers = get_int_arg(4);
        bullet_props[slot].count = (high_count - low_count) * (g_Globals.rank + 1024) / 2048 + low_count;
        bullet_props[slot].layers = (high_layers - low_layers) * (g_Globals.rank + 1024) / 2048 + low_layers;
        break;
    }
    // etAim(slot, aim_type)
    case ECL_OP_ET_AIM:
    {
        i32 slot = get_int_arg(0);
        // Only the low 16 bits, as everywhere else (the original stores a word).
        *(u16 *)&bullet_props[slot].aim_type = get_int_arg(1);
        break;
    }
    // etSound(slot, shot_sfx, transform_sfx)
    case ECL_OP_ET_SOUND:
    {
        i32 slot = get_int_arg(0);
        bullet_props[slot].shot_sfx = get_int_arg(1);
        bullet_props[slot].shot_transform_sfx = get_int_arg(2);
        break;
    }

    // etEx(et, ex_index, slot, type, a, b, r, s), plus full and next
    // forms. NEXT uses the shooter's next free transform; FULL supplies
    // the additional c/d and m/n operands.
    case ECL_OP_ET_EX:
    case ECL_OP_ET_EX_FULL:
    case ECL_OP_ET_EX_NEXT:
    case ECL_OP_ET_EX_FULL_NEXT:
    {
        i32 et = get_int_arg(0);
        if (et >= 0x12 || et < 0)
        {
            et = 0;
        }

        i32 arg = 2;
        if (instr->opcode == ECL_OP_ET_EX_NEXT || instr->opcode == ECL_OP_ET_EX_FULL_NEXT)
        {
            arg = 1;
        }
        i32 ex_index;
        if (instr->opcode == ECL_OP_ET_EX_NEXT || instr->opcode == ECL_OP_ET_EX_FULL_NEXT)
        {
            ex_index = et_ex_index[et];
        }
        else
        {
            ex_index = get_int_arg(1);
        }
        // All transform fields share one flattened shooter/transform offset
        // across the argument reads below.
        volatile i32 ex_offset = et * sizeof(EnemyBulletShooter) + ex_index * sizeof(BulletEx);
        // Keep the member access typed while using the target's shared base.
#define ECL_EX_FIELD(field) (reinterpret_cast<BulletEx *>(reinterpret_cast<u8 *>(&bullet_props[0].ex[0]) + ex_offset)->field)
        ECL_EX_FIELD(slot) = get_int_arg(arg++);
        ECL_EX_FIELD(type) = get_int_arg(arg++);
        ECL_EX_FIELD(a) = get_int_arg(arg++);
        ECL_EX_FIELD(b) = get_int_arg(arg++);
        if (instr->opcode == ECL_OP_ET_EX_FULL || instr->opcode == ECL_OP_ET_EX_FULL_NEXT)
        {
            // The c word is part of the selected transform record.
            bullet_props[et].ex[ex_index].c = get_int_arg(arg++);
            ECL_EX_FIELD(d) = get_int_arg(arg++);
        }

        ECL_EX_FIELD(r) = get_float_arg(EclFloatArgIndex{arg++});
        ECL_EX_FIELD(s) = get_float_arg(EclFloatArgIndex{arg++});
        if (instr->opcode == ECL_OP_ET_EX_FULL || instr->opcode == ECL_OP_ET_EX_FULL_NEXT)
        {
            ECL_EX_FIELD(m) = get_float_arg(EclFloatArgIndex{arg++});
            ECL_EX_FIELD(n) = get_float_arg(EclFloatArgIndex{arg++});
        }
#undef ECL_EX_FIELD

        if (instr->opcode == ECL_OP_ET_EX_NEXT || instr->opcode == ECL_OP_ET_EX_FULL_NEXT)
        {
            et_ex_index[et]++;
        }
        else
        {
            et_ex_index[et] = ex_index + 1;
        }
        break;
    }
    // etExSubtract(et): steps the next free ex slot back.
    case ECL_OP_ET_EX_SUBTRACT:
    {
        i32 idx = get_int_arg(0);
        et_ex_index[idx]--;
        if (et_ex_index[idx] < 0)
        {
            et_ex_index[idx] = 0;
        }
        break;
    }
    // etExSub(et, ex_index, sub): the subroutine an ex transform calls.
    case ECL_OP_ET_EX_SUB:
    {
        i32 idx = get_int_arg(0);
        bullet_props[idx].ex[get_int_arg(1)].string = (char *)&instr->args[3];
        break;
    }
    // laserNew(et, a, b, c, d).
    case ECL_OP_LASER_NEW:
    {
        i32 idx = get_int_arg(0);
        bullet_props[idx].pos.x = get_float_arg(EclFloatArgIndex{1});
        bullet_props[idx].pos.y = get_float_arg(EclFloatArgIndex{2});
        bullet_props[idx].pos.z = get_float_arg(EclFloatArgIndex{3});
        bullet_props[idx].laser_new_arg_4 = get_float_arg(EclFloatArgIndex{4});
        break;
    }
    // laserTiming(et, start, expand, duration, shrink, flags): the infinite
    // laser phases (LaserInfiniteInner::start_time and on).
    case ECL_OP_LASER_TIMING:
    {
        i32 idx = get_int_arg(0);
        bullet_props[idx].laser_timing[0] = get_int_arg(1);
        bullet_props[idx].laser_timing[1] = get_int_arg(2);
        bullet_props[idx].laser_timing[2] = get_int_arg(3);
        bullet_props[idx].laser_timing[3] = get_int_arg(4);
        bullet_props[idx].flags = get_int_arg(5);
        break;
    }
    // setNext(index, life, time, sub). In spell practice the boss instead
    // ends its card when the interrupt fires, and escapes on timeout.
    case ECL_OP_SET_NEXT:
    {
        const char *sub = (const char *)&instr->args[4];
        if (g_Globals.game_mode == GAME_MODE_SPELL_PRACTICE && (flags_low & ENEMY_FLAG_BOSS))
        {
            if (own_boss_id == 0)
            {
                if (g_Globals.stage_num == 7 && g_Globals.chapter < 41)
                {
                    set_next(full, get_int_arg(0), 0, get_int_arg(2), "MBossDead");
                }
                else
                {
                    set_next(full, get_int_arg(0), 0, get_int_arg(2), "BossDead");
                }
            }
            else if (g_Globals.stage_num == 7 && g_Globals.chapter < 41)
            {
                set_next(full, get_int_arg(0), 0, get_int_arg(2), "MBossBDead");
            }
            else
            {
                set_next(full, get_int_arg(0), 0, get_int_arg(2), "BossDead");
            }
            full->set_timeout(get_int_arg(0), "BossEscape");
        }
        else
        {
            set_next(full, get_int_arg(0), get_int_arg(1), get_int_arg(2), sub);
        }
        break;
    }
    // setTimeout(index, sub).
    case ECL_OP_SET_TIMEOUT:
        full->set_timeout(get_int_arg(0), (const char *)&instr->args[2]);
        break;
    // setDeath(sub).
    case ECL_OP_SET_DEATH:
        strcpy(set_death, (const char *)&instr->args[1]);
        break;
    // etClearAll().
    case ECL_OP_ET_CLEAR_ALL:
        g_BulletManager->clear_all(0);
        g_LaserManager->clear_all(1, 0);
        break;
    // playSound(id).
    case ECL_OP_PLAY_SOUND:
        g_SoundManager.play_sound_at_position(get_int_arg(0), final_pos.pos.x);
        break;
    // setScreenShake(a, b, c).
    case ECL_OP_SET_SCREEN_SHAKE:
        ScreenEffect::create(SCREEN_EFFECT_SHAKE, get_int_arg(0), get_int_arg(1), get_int_arg(2), 0, 0x54);
        break;
    // dialogRead(script): also clears every bullet, laser and enemy.
    case ECL_OP_DIALOG_READ:
        g_Gui->start_dialogue(get_int_arg(0));
        g_BulletManager->clear_all(0);
        g_LaserManager->clear_all(0, 0);
        // fall through
    // enmKillAll().
    case ECL_OP_ENM_KILL_ALL:
        EnemyManager::kill_all();
        break;
    // dialogWait(): waits while dialogue runs and no enemy is expected.
    case ECL_OP_DIALOG_WAIT:
        if (g_Gui->msg != NULL && g_Gui->msg->ecl_resume_timer == 0)
        {
            return -1;
        }
        break;
    // Waits while any boss is alive.
    case ECL_OP_WAIT_BOSSES:
        if (g_EnemyManager->get_boss(0) != NULL || g_EnemyManager->get_boss(1) != NULL ||
            g_EnemyManager->get_boss(2) != NULL)
        {
            return -1;
        }
        break;
    // flagMirror(on).
    case ECL_OP_FLAG_MIRROR:
        ((EnemyFlagsLow *)&flags_low)->mirrored = get_int_arg(0);
        break;
    // spell(id, time_limit, boss_index, name) and its per-difficulty forms.
    // The script supplies encrypted name bytes directly after its arguments.
    case ECL_OP_SPELL:
    case ECL_OP_SPELL_528:
    case ECL_OP_SPELL_537:
    case ECL_OP_SPELL_538:
    case ECL_OP_SPELL_539:
    {
        char name[0x80];
        i32 name_length = instr->args[3].i;
        const u8 *encrypted_name = reinterpret_cast<const u8 *>(&instr->args[4]);
        u8 key = 0x77;
        u8 key_step = 7;
        // The encrypted input advances while the destination uses a frame
        // index; this also keeps the original loop's key-update order.
        char *dest = name;
        for (i32 i = 0; i < name_length; i++)
        {
            dest[i] = (char)(*encrypted_name++ ^ key);
            key = (u8)(key + key_step);
            key_step = (u8)(key_step + 0x10);
        }

        i32 spell_id = full->context.current_context->get_int_arg(0);
        switch ((i16)instr->opcode)
        {
        case ECL_OP_SPELL_537:
            spell_id += g_Globals.difficulty;
            break;
        case ECL_OP_SPELL_538:
            spell_id += g_Globals.difficulty - 1;
            break;
        case ECL_OP_SPELL_539:
            spell_id += g_Globals.difficulty - 2;
            break;
        }

        i32 time_limit = full->context.current_context->get_int_arg(2);
        i32 boss_index = full->context.current_context->get_int_arg(1);
        g_Spellcard->start(spell_id, name, time_limit, boss_index);
        *(volatile u32 *)&life.is_spell |= ENEMY_LIFE_SPELL;
        life.current_scaled_by_seven = life.current * 7;
    }
        // fall through
    // timerReset().
    case ECL_OP_TIMER_RESET:
        time_in_ecl.set_value(0);
        break;
    // spellMode(on).
    case ECL_OP_SPELL_MODE:
        ((EnemyLifeSpellBits *)&life.is_spell)->active = get_int_arg(0);
        break;
    // spellEnd().
    case ECL_OP_SPELL_END:
        g_Spellcard->end();
        life.is_spell &= ~ENEMY_LIFE_SPELL;
        break;
    // spellTimeout(): no bonus decay.
    case ECL_OP_SPELL_TIMEOUT:
        g_Spellcard->flags |= SPELLCARD_NO_BONUS_DECAY;
        break;
    // unknown543(): removes the boss effect.
    case ECL_OP_HIDE_BOSS_EFFECT:
    {
        Spellcard *spellcard = g_Spellcard;
        spellcard->flags |= SPELLCARD_FLAG_10;
        delete_vm_and_clear(spellcard->boss_anm_id);
        break;
    }
    // unknown567(on): the spell name at the bottom of the screen.
    case ECL_OP_SPELL_TEXT_AT_BOTTOM:
        ((SpellcardFlagBits *)&g_Spellcard->flags)->text_at_bottom = get_int_arg(0);
        break;
    // unknown544(on): ENEMY_FLAG_8000000.
    case ECL_OP_FLAG_8000000:
        ((EnemyFlagsLow *)&flags_low)->flag_8000000 = get_int_arg(0);
        break;
    // laserOn(et): a line laser from the shooter's settings.
    case ECL_OP_LASER_ON:
    {
        ::new (&laser_params_storage.line) LaserLineInner();
        i32 slot = get_int_arg(0);
        const volatile EnemyBulletShooter &shooter = bullet_props[slot];
        get_shot_origin_and_copy_ex_branch_first(
            this, slot, &laser_params_storage.line.start_pos, laser_params_storage.line.ex);
        i32 bullet_type = shooter.type;
        f32 ang_aim = shooter.ang_aim;
        i32 bullet_color = shooter.color;
        laser_params_storage.line.bullet_type = bullet_type;
        laser_params_storage.line.bullet_color = bullet_color;
        laser_params_storage.line.ang_aim = normalize_angle(ang_aim);
        laser_params_storage.line.flags = shooter.flags | 1;
        laser_params_storage.line.speed = shooter.spd1;
        laser_params_storage.line.laser_new_arg_1 = shooter.pos.x;
        laser_params_storage.line.laser_new_arg_2 = shooter.pos.y;
        laser_params_storage.line.shot_sfx = shooter.shot_sfx;
        laser_params_storage.line.laser_new_arg_3 = shooter.pos.z;
        laser_params_storage.line.shot_transform_sfx = shooter.shot_transform_sfx;
        laser_params_storage.line.laser_new_arg_4 = shooter.laser_new_arg_4;
        laser_params_storage.line.distance = shooter.distance;
        g_LaserManager->allocate_new_laser(LASER_LINE, &laser_params_storage.line);
        break;
    }
    // laserStOn(et, a): an infinite laser.
    case ECL_OP_LASER_ST_ON:
    {
        ::new (&laser_params_storage.infinite) LaserInfiniteInner();
        i32 slot = get_int_arg(0);
        const volatile EnemyBulletShooter &shooter = bullet_props[slot];
        get_shot_origin_and_copy_ex_branch_first(
            this, slot, &laser_params_storage.infinite.start_pos, laser_params_storage.infinite.ex);
        i32 type = shooter.type;
        f32 ang_aim = shooter.ang_aim;
        i32 color = shooter.color;
        laser_params_storage.infinite.type = type;
        laser_params_storage.infinite.color = color;
        laser_params_storage.infinite.ang_aim = normalize_angle(ang_aim);
        laser_params_storage.infinite.start_time = shooter.laser_timing[0];
        laser_params_storage.infinite.expand_time = shooter.laser_timing[1];
        laser_params_storage.infinite.speed = shooter.spd1;
        laser_params_storage.infinite.duration = shooter.laser_timing[2];
        laser_params_storage.infinite.laser_new_arg_1 = shooter.pos.x;
        laser_params_storage.infinite.shrink_time = shooter.laser_timing[3];
        laser_params_storage.infinite.flags = shooter.flags | 2;
        laser_params_storage.infinite.laser_new_arg_2 = shooter.pos.y;
        laser_params_storage.infinite.laser_new_arg_4 = shooter.laser_new_arg_4;
        laser_params_storage.infinite.shot_sfx = shooter.shot_sfx;
        laser_params_storage.infinite.distance = shooter.distance;
        laser_params_storage.infinite.shot_transform_sfx = shooter.shot_transform_sfx;
        laser_params_storage.infinite.laser_st_on_arg_1 = get_int_arg(1);
        g_LaserManager->allocate_new_laser(LASER_INFINITE, &laser_params_storage.infinite);
        break;
    }
    // A beam laser (ExpHP: unknown713).
    case ECL_OP_LASER_BEAM_ON:
    {
        ::new (&laser_params_storage.beam) LaserBeamInner();
        i32 slot = get_int_arg(0);
        const volatile EnemyBulletShooter &shooter = bullet_props[slot];
        copy_ex_and_get_shot_origin(
            this, slot, &laser_params_storage.beam.start_pos, laser_params_storage.beam.ex);
        i32 color = shooter.color;
        f32 ang_aim = shooter.ang_aim;
        laser_params_storage.beam.color = color;
        laser_params_storage.beam.ang_aim = normalize_angle(ang_aim);
        laser_params_storage.beam.timing = shooter.laser_timing[0];
        laser_params_storage.beam.laser_new_arg_4 = shooter.laser_new_arg_4;
        laser_params_storage.beam.length = shooter.pos.z;
        laser_params_storage.beam.distance = shooter.distance;
        laser_params_storage.beam.id = get_int_arg(1);
        g_LaserManager->allocate_new_laser(LASER_BEAM, &laser_params_storage.beam);
        break;
    }
    // laserCuOn(et): a curvy laser.
    case ECL_OP_LASER_CU_ON:
    {
        ::new (&laser_params_storage.curve) LaserCurveInner();
        i32 slot = get_int_arg(0);
        const volatile EnemyBulletShooter &shooter = bullet_props[slot];
        get_shot_origin_and_copy_ex_branch_first(
            this, slot, &laser_params_storage.curve.start_pos, laser_params_storage.curve.ex);
        i32 type = shooter.type;
        f32 ang_aim = shooter.ang_aim;
        i32 color = shooter.color;
        laser_params_storage.curve.type = type;
        laser_params_storage.curve.color = color;
        laser_params_storage.curve.ang_aim = normalize_angle(ang_aim);
        laser_params_storage.curve.segment_count = shooter.laser_timing[0];
        laser_params_storage.curve.unk_28 |= 1;
        laser_params_storage.curve.shot_sfx = shooter.shot_sfx;
        laser_params_storage.curve.speed = shooter.spd1;
        laser_params_storage.curve.shot_transform_sfx = shooter.shot_transform_sfx;
        laser_params_storage.curve.laser_new_arg_4 = shooter.laser_new_arg_4;
        laser_params_storage.curve.distance = shooter.distance;
        g_LaserManager->allocate_new_laser(LASER_CURVE, &laser_params_storage.curve);
        break;
    }
    // laserStEnd(id): cancels every laser with the id.
    case ECL_OP_LASER_ST_END:
    {
        i32 id = get_int_arg(0);
        LaserDataInf *laser = g_LaserManager->find_by_id(id, 0);
        while (laser != NULL)
        {
            laser->cancel(0, 0);
            laser->id = 0;
            id = get_int_arg(0);
            laser = g_LaserManager->find_by_id(id, 0);
        }
        break;
    }

    // laserOffset(id, x, y)
    case ECL_OP_LASER_OFFSET:
    {
        i32 id = get_int_arg(0);
        LaserDataInf *laser = g_LaserManager->find_by_id(id, 0);
        f32 x = get_float_arg(EclFloatArgIndex{1});
        f32 y = get_float_arg(EclFloatArgIndex{2});
        if (laser != NULL)
        {
            laser->position = Float3(x, y, 0.0f);
        }
        break;
    }
    // laserTrajectory(id, x, y): infinite lasers only.
    case ECL_OP_LASER_TRAJECTORY:
    {
        i32 id = get_int_arg(0);
        LaserDataInf *laser = g_LaserManager->find_by_id(id, 0);
        f32 x = get_float_arg(EclFloatArgIndex{1});
        f32 y = get_float_arg(EclFloatArgIndex{2});
        if (laser != NULL)
        {
            static_cast<LaserInfiniteInf *>(laser)->inner.velocity = Float3(x, y, 0.0f);
        }
        break;
    }
    // laserStLength(id, length)
    case ECL_OP_LASER_ST_LENGTH:
    {
        i32 id = get_int_arg(0);
        LaserDataInf *laser = g_LaserManager->find_by_id(id, 0);
        if (laser != NULL)
        {
            laser->length = get_float_arg(EclFloatArgIndex{1});
        }
        break;
    }
    // laserStWidth(id, width)
    case ECL_OP_LASER_ST_WIDTH:
    {
        i32 id = get_int_arg(0);
        LaserDataInf *laser = g_LaserManager->find_by_id(id, 0);
        if (laser != NULL)
        {
            laser->width = get_float_arg(EclFloatArgIndex{1});
        }
        break;
    }
    // laserStAngle(id, angle)
    case ECL_OP_LASER_ST_ANGLE:
    {
        i32 id = get_int_arg(0);
        LaserDataInf *laser = g_LaserManager->find_by_id(id, 0);
        if (laser != NULL)
        {
            laser->angle = get_float_arg(EclFloatArgIndex{1});
        }
        break;
    }
    // laserStRotation(id, rotation): infinite lasers only.
    case ECL_OP_LASER_ST_ROTATION:
    {
        i32 id = get_int_arg(0);
        LaserDataInf *laser = g_LaserManager->find_by_id(id, 0);
        if (laser != NULL)
        {
            static_cast<LaserInfiniteInf *>(laser)->inner.laser_st_rotation =
                get_float_arg(EclFloatArgIndex{1});
        }
        break;
    }
    // unknown714(id, value): laser method_8. Infinite lasers ignore
    // this instruction, but its second argument is still evaluated.
    case ECL_OP_LASER_714:
    {
        i32 id = get_int_arg(0);
        LaserDataInf *laser = g_LaserManager->find_by_id(id, 0);
        if (laser != NULL)
        {
            i32 value = get_int_arg(1);
            if (laser->kind != LASER_INFINITE)
            {
                laser->method_8(value);
            }
        }
        break;
    }
    // etCancel(radius): cancel nearby bullets and lasers in mode 1.
    case ECL_OP_ET_CANCEL:
    {
        f32 radius = get_float_arg(EclFloatArgIndex{0});
        g_BulletManager->cancel_radius(&final_pos.pos, radius, 1);
        g_LaserManager->cancel_in_radius(&final_pos.pos, radius, 1, 1);
        break;
    }
    // etClear(radius): same area, but no cancel items.
    case ECL_OP_ET_CLEAR:
    {
        f32 radius = get_float_arg(EclFloatArgIndex{0});
        g_BulletManager->cancel_radius(&final_pos.pos, radius, 0);
        g_LaserManager->cancel_in_radius(&final_pos.pos, radius, 0, 1);
        break;
    }
    // etCancel2(radius): use the bullet cancel-as-bomb path.
    case ECL_OP_ET_CANCEL2:
    {
        f32 radius = get_float_arg(EclFloatArgIndex{0});
        g_BulletManager->cancel_radius_as_bomb(&final_pos.pos, radius, 1);
        g_LaserManager->cancel_in_radius(&final_pos.pos, radius, 1, 1);
        break;
    }
    // etClear2(radius): protected-bullet variant without items.
    case ECL_OP_ET_CLEAR2:
    {
        f32 radius = get_float_arg(EclFloatArgIndex{0});
        g_BulletManager->cancel_radius_as_bomb(&final_pos.pos, radius, 0);
        g_LaserManager->cancel_in_radius(&final_pos.pos, radius, 0, 1);
        break;
    }
    // hitboxRect(w, h): rectangular cancellation rotated with the enemy's
    // main animation.
    case ECL_OP_HITBOX_RECT:
    {
        f32 width = get_float_arg(EclFloatArgIndex{0});
        f32 height = get_float_arg(EclFloatArgIndex{1});
        // Rectangle collision consumes width and height, not the Z component.
        Float3 size;
        size.x = width;
        size.y = height;
        AnmVm *main_vm = anm_ids[0].find_or_clear();
        g_BulletManager->cancel_rectangle_as_bomb(&final_pos.pos, &size,
                                                  main_vm->rotation.z, 1);
        break;
    }
    // setChapter(chapter)
    case ECL_OP_SET_CHAPTER:
    {
        i32 chapter = get_int_arg(0);
        g_Globals.chapter = chapter;
        g_GameThread->chapter = chapter;
        own_chapter = chapter;
        chapter_count = 0;
        break;
    }
    // rankF3(var, a, b, c): the middle tier also reads a (so the binary has
    // two copies; written as two tiers, LTCG hoists the pointer call).
    case ECL_OP_RANK_F3:
        if (g_Globals.rank >= 512)
        {
            *get_float_arg_ptr(0) = get_float_arg(EclFloatArgIndex{2});
        }
        else if (g_Globals.rank >= -512)
        {
            *get_float_arg_ptr(0) = get_float_arg(EclFloatArgIndex{0});
        }
        else
        {
            *get_float_arg_ptr(0) = get_float_arg(EclFloatArgIndex{0});
        }
        break;
    // rankF5(var, a, b, c, d, e)
    case ECL_OP_RANK_F5:
        if (g_Globals.rank >= 600)
        {
            *get_float_arg_ptr(0) = get_float_arg(EclFloatArgIndex{4});
        }
        else if (g_Globals.rank >= 200)
        {
            *get_float_arg_ptr(0) = get_float_arg(EclFloatArgIndex{3});
        }
        else if (g_Globals.rank >= -200)
        {
            *get_float_arg_ptr(0) = get_float_arg(EclFloatArgIndex{2});
        }
        else if (g_Globals.rank >= -400)
        {
            *get_float_arg_ptr(0) = get_float_arg(EclFloatArgIndex{1});
        }
        else
        {
            *get_float_arg_ptr(0) = get_float_arg(EclFloatArgIndex{0});
        }
        break;
    // rankF2(var, low, high): low at rank -1024, high at rank 1024.
    case ECL_OP_RANK_F2:
    {
        f32 low = get_float_arg(EclFloatArgIndex{1});
        f32 high = get_float_arg(EclFloatArgIndex{2});
        *get_float_arg_ptr(0) = (high - low) * (g_Globals.rank + 1024.0f) / 2048.0f + low;
        break;
    }
    // rankI3(var, a, b, c): the middle tier also reads a, as in rankF3.
    case ECL_OP_RANK_I3:
        if (g_Globals.rank >= 512)
        {
            *get_int_arg_ptr(0) = get_int_arg(2);
        }
        else if (g_Globals.rank >= -512)
        {
            *get_int_arg_ptr(0) = get_int_arg(0);
        }
        else
        {
            *get_int_arg_ptr(0) = get_int_arg(0);
        }
        break;
    // rankI5(var, a, b, c, d, e)
    case ECL_OP_RANK_I5:
        if (g_Globals.rank >= 600)
        {
            *get_int_arg_ptr(0) = get_int_arg(4);
        }
        else if (g_Globals.rank >= 200)
        {
            *get_int_arg_ptr(0) = get_int_arg(3);
        }
        else if (g_Globals.rank >= -200)
        {
            *get_int_arg_ptr(0) = get_int_arg(2);
        }
        else if (g_Globals.rank >= -400)
        {
            *get_int_arg_ptr(0) = get_int_arg(1);
        }
        else
        {
            *get_int_arg_ptr(0) = get_int_arg(0);
        }
        break;
    // rankI2(var, low, high)
    case ECL_OP_RANK_I2:
    {
        i32 low = get_int_arg(1);
        i32 high = get_int_arg(2);
        *get_int_arg_ptr(0) = (high - low) * (g_Globals.rank + 1024) / 2048 + low;
        break;
    }
    // stars(count): the boss's star count on the HUD.
    case ECL_OP_STARS:
        g_Gui->boss_star_count = get_int_arg(0);
        break;
    // reset: cancels every laser.
    case ECL_OP_RESET:
        LaserManager::cancel_all();
        break;
    // bombShield(on, anm_script)
    case ECL_OP_BOMB_SHIELD:
        ((EnemyFlagsLow *)&flags_low)->bombshield = get_int_arg(0);
        bombshield_on_anm_main = get_int_arg(1);
        flags_low &= ~(ENEMY_FLAG_BOMBSHIELD_UP | ENEMY_FLAG_NO_HURTBOX);
        bombshield_off_anm_main = anm_set_main;
        break;
    // unknown559(limit): the enemy limit.
    case ECL_OP_ENEMY_LIMIT:
        g_EnemyManager->inner.enemy_limit = get_int_arg(0);
        break;
    // gameSpeed(speed)
    case ECL_OP_GAME_SPEED:
        g_game_speed = get_float_arg(EclFloatArgIndex{0});
        break;
    // angleToPlayer(var, x, y)
    case ECL_OP_ANGLE_TO_PLAYER:
    {
        f32 player_x = g_Player->inner.pos.x;
        f32 player_y = g_Player->inner.pos.y;
        f32 x = get_float_arg(EclFloatArgIndex{1});
        f32 y = get_float_arg(EclFloatArgIndex{2});
        f32 angle = zun_atan2f(player_y - y, player_x - x);
        *get_float_arg_ptr(0) = angle;
        break;
    }
    // diffWait(easy, normal, hard, lunatic): waits the given number of
    // frames for the current difficulty.
    case ECL_OP_DIFF_WAIT:
    {
        i32 easy = get_int_arg(0);
        i32 normal = get_int_arg(1);
        i32 hard = get_int_arg(2);
        i32 lunatic = get_int_arg(3);
        i32 wait;
        if (g_Globals.difficulty == DIFFICULTY_EASY)
        {
            wait = easy;
        }
        else if (g_Globals.difficulty == DIFFICULTY_NORMAL)
        {
            wait = normal;
        }
        else if (g_Globals.difficulty == DIFFICULTY_HARD)
        {
            wait = hard;
        }
        else
        {
            wait = lunatic;
        }
        full->context.current_context->time -= wait;
        break;
    }
    // fog(radius, color): replaces the enemy's fog; radius 0 removes it.
    case ECL_OP_FOG:
        if (fog.fog_ptr != NULL)
        {
            delete (Fog *)fog.fog_ptr;
        }
        fog.fog_ptr = NULL;
        fog.fog_radius = get_float_arg(EclFloatArgIndex{0});
        fog.cur_radius = 16.0f;
        fog.fog_color = get_int_arg(1);
        *(ZunAngle *)&fog.wave_angle_x = 0.0f;
        *(ZunAngle *)&fog.wave_angle_y = 0.0f;
        if (fog.fog_radius > 0.0f)
        {
            fog.fog_ptr = new_enemy_fog();
        }
        break;
    // callSTD(label): jumps the stage script.
    case ECL_OP_CALL_STD:
        g_Stage->jump_to_label(get_int_arg(0));
        break;
    // unknown557(time, method, color, begin, end): interpolates the stage
    // fog (camera sky) towards the given distances and color.
    case ECL_OP_STAGE_FOG:
    {
        i32 time = get_int_arg(0);
        i32 method = get_int_arg(1);
        ZunColor color;
        color.d3d = get_int_arg(2);
        CameraSky sky(get_float_arg(EclFloatArgIndex{3}), get_float_arg(EclFloatArgIndex{4}), color.b, color.g, color.r, color.a);
        g_Stage->inner.set_sky_interp(time, method, &sky);
        break;
    }
    // unknown549(flag)
    case ECL_OP_MAGENTA_FLASH:
        ((EnemyFlagsLow *)&flags_low)->magenta_flash = get_int_arg(0);
        break;
    // unknown550(value)
    case ECL_OP_SET_KILL_GROUP:
        kill_group = get_int_arg(0);
        break;
    // enmAlive(var, id)
    case ECL_OP_ENM_ALIVE:
    {
        i32 alive = g_EnemyManager->is_enemy_alive(get_int_arg(1));
        *get_int_arg_ptr(0) = alive;
        break;
    }
    // enmPos(var_x, var_y, id)
    case ECL_OP_ENM_POS:
    {
        EnemyInf *enemy = g_EnemyManager->find_enemy_by_id(get_int_arg(2));
        *get_float_arg_ptr(0) = enemy->enemy.final_pos.pos.x;
        *get_float_arg_ptr(1) = enemy->enemy.final_pos.pos.y;
        break;
    }
    // unknown802(index): makes the other bosses jump to their interrupt
    // index's subroutine, if it has a life threshold.
    case ECL_OP_BOSSES_INTERRUPT:
    {
        i32 index = get_int_arg(0);
        for (i32 i = 0; i < 3; i++)
        {
            EnemyInf *boss = g_EnemyManager->get_boss(i);
            if (i != own_boss_id && boss != NULL)
            {
                if (boss->enemy.interrupts[index].life >= 0 &&
                    boss->enemy.interrupts[index].sub_for_set_next != NULL)
                {
                    boss->free_all_async();
                    boss->reset_run_context();
                    boss->load_sub_by_name(boss->enemy.interrupts[index].sub_for_set_next);
                }
            }
        }
        break;
    }
    // enmCall(id, sub): restarts another enemy at the named subroutine.
    case ECL_OP_ENM_CALL:
    {
        EnemyInf *enemy = g_EnemyManager->find_enemy_by_id(get_int_arg(0));
        if (enemy != NULL)
        {
            enemy->free_all_async();
            enemy->reset_run_context();
            enemy->load_sub_by_name((const char *)&instr->args[2]);
        }
        break;
    }
    // enm324(var_x, var_y, id): enmPos that falls back to this enemy.
    case ECL_OP_ENM_POS_OR_SELF:
    {
        EnemyInf *enemy = g_EnemyManager->find_enemy_by_id(get_int_arg(2));
        if (enemy != NULL)
        {
            *get_float_arg_ptr(0) = enemy->enemy.final_pos.pos.x;
            *get_float_arg_ptr(1) = enemy->enemy.final_pos.pos.y;
        }
        else
        {
            *get_float_arg_ptr(0) = final_pos.pos.x;
            *get_float_arg_ptr(1) = final_pos.pos.y;
        }
        break;
    }
    // unknown560(x, y)
    case ECL_OP_UNKNOWN_560:
    {
        BulletManager *mgr = g_BulletManager;
        f32 x = get_float_arg(EclFloatArgIndex{0});
        f32 y = get_float_arg(EclFloatArgIndex{1});
        mgr->ecl_unknown_560.x = x;
        mgr->ecl_unknown_560.y = y;
        break;
    }
    // spec0(max_time, count, min_count): the season item drop.
    case ECL_OP_SPEC0:
        drop_season.max_time = get_int_arg(0);
        drop_season.bonus_timer.set_value(drop_season.max_time);
        drops.extra_counts[15] = get_int_arg(1);
        drop_season.min_count = get_int_arg(2);
        break;
    // spec1(damage_per_drop)
    case ECL_OP_SPEC1:
        drop_season.damage_per_season_drop = get_int_arg(0);
        drop_season.damage_accounted_for_season_drops = life.total_damage_including_ignored;
        break;
    // anm340(id): sets flag 0x2000000 on another enemy.
    case ECL_OP_ENM_DELETE:
    {
        EnemyInf *enemy = g_EnemyManager->find_enemy_by_id(get_int_arg(0));
        if (enemy != NULL)
        {
            enemy->enemy.flags_low |= ENEMY_FLAG_DELETE;
        }
        break;
    }

    }
    return 0;
}
