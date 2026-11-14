#include <math.h>

#include "AnmManager.h"
#include "CriticalSections.h"

// FUNCTION: TH16 0x40d460
void AnmLoaded::copy_vm_and_run(AnmVm *vm, i32 script)
{
    copy_vm(vm, script);
    vm->parent_vm = NULL;
    vm->root_vm = NULL;
    vm->run();
}

// The VM's position plus its root VM's, rotated with the root's rotation if
// the VM asks for it.
// world_pos's body. The original recurses through an inline helper like
// this one: a direct recursion keeps LTCG from proving the 12-byte
// temporary safe and adds a GS cookie the original lacks. Writing through
// the caller's pointer makes it reload root_vm for the recursion, as the
// original does.
// TODO: the y component of the parent's position is added in the other
// operand order.
static __forceinline D3DXVECTOR3 *anm_vm_world_pos(AnmVm *vm, D3DXVECTOR3 *out)
{
    *out = vm->entity_pos + vm->pos + vm->pos_2;
    AnmVm *root = vm->root_vm;
    if (root != NULL && !(vm->flags_hi & ANM_VM_NO_PARENT_POS))
    {
        if (vm->flags_hi & ANM_VM_ROTATE_WITH_PARENT)
        {
            f32 s = zun_sinf(root->rotation.z);
            f32 c = zun_cosf(root->rotation.z);
            f32 x = out->x;
            f32 y = out->y;
            out->x = x * c - y * s;
            out->y = y * c + x * s;
        }
        D3DXVECTOR3 parent_pos;
        vm->root_vm->world_pos(&parent_pos);
        *out += parent_pos;
    }
    return out;
}

// FUNCTION: TH16 0x40e490
DECOMP_NOINLINE D3DXVECTOR3 *AnmVm::world_pos(D3DXVECTOR3 *out)
{
    return anm_vm_world_pos(this, out);
}

// Creates a game-owned effect VM, optionally returning its allocated pointer.
// The dead doubles (decomp.h) give it the original's aligned frame.
// FUNCTION: TH16 0x406380
DECOMP_NOINLINE AnmId AnmLoaded::create_effect(i32 script, i32 layer, AnmVm **out)
{
    DECOMP_DEAD_DOUBLE_3;
    ENTER_CS(CS_ANM_MANAGER);
    vm_count++;
    AnmVm *vm = g_AnmManager->allocate_vm();
    if (out != NULL)
    {
        *out = vm;
    }
    copy_vm(vm, script);
    vm->flags_hi |= ANM_VM_CREATED_BY_GAME;
    if (layer >= 0)
    {
        vm->layer = layer;
        if (layer <= ANM_LAYER_HUD_LAST)
        {
            vm->flags_hi &= ~ANM_VM_ORIGIN_HUD;
            vm->flags_hi |= ANM_VM_ORIGIN_GAME;
        }
    }
    vm->entity_pos = D3DXVECTOR3(0.0f, 0.0f, 0.0f);
    vm->rotation.z = 0.0f;
    vm->run();
    vm->mode_of_create_child = ANM_CREATE_WORLD_BACK;
    AnmId id;
    id = g_AnmManager->insert_in_world_list_back(vm);
    LEAVE_CS(CS_ANM_MANAGER);
    return id;
}

// FUNCTION: TH16 0x40e5c0
HARNESS_CALLED AnmId AnmLoaded::create_vm(i32 script, D3DXVECTOR3 *pos, f32 rotation, i32 layer, i32 unused)
{
    ENTER_CS(CS_ANM_MANAGER);
    vm_count++;
    AnmVm *vm = g_AnmManager->allocate_vm();
    copy_vm(vm, script);
    vm->flags_hi |= ANM_VM_CREATED_BY_GAME;
    if (layer >= 0)
    {
        vm->layer = layer;
        if (layer <= ANM_LAYER_HUD_LAST)
        {
            vm->flags_hi &= ~ANM_VM_ORIGIN_HUD;
            vm->flags_hi |= ANM_VM_ORIGIN_GAME;
        }
    }
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
    vm->mode_of_create_child = ANM_CREATE_WORLD_BACK;
    AnmId id;
    id = g_AnmManager->insert_in_world_list_back(vm);
    LEAVE_CS(CS_ANM_MANAGER);
    return id;
}
