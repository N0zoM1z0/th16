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
// TODO: recover the original stack context; the recursive temporary currently
// introduces a GS cookie absent from the original function.
// FUNCTION: TH16 0x40e490
D3DXVECTOR3 AnmVm::world_pos()
{
    D3DXVECTOR3 result;
    result = entity_pos + pos + pos_2;
    if (root_vm != NULL && !(flags_hi & ANM_VM_NO_PARENT_POS))
    {
        if (flags_hi & ANM_VM_ROTATE_WITH_PARENT)
        {
            f32 s = zun_sinf(root_vm->rotation.z);
            f32 c = zun_cosf(root_vm->rotation.z);
            f32 x = result.x;
            f32 y = result.y;
            result.x = x * c - y * s;
            result.y = y * c + x * s;
        }
        result += root_vm->world_pos();
    }
    return result;
}

// Creates a game-owned effect VM, optionally returning its allocated pointer.
// TODO: recover the original stack-alignment context from real calls.
// FUNCTION: TH16 0x406380
DECOMP_NOINLINE AnmId AnmLoaded::create_effect(i32 script, i32 layer, AnmVm **out)
{
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
