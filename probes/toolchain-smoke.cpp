#include <windows.h>
#include <d3dx9.h>
#include <stdio.h>
#include <vector>

extern "C" int th16_smoke_c(int);

int main()
{
    char text[64] = {};
    if (!LoadStringA(GetModuleHandleA(NULL), 1, text, sizeof(text)))
        return 1;
    std::vector<int> values(2, 20);
    D3DXVECTOR3 position(1.0f, 2.0f, 3.0f);
    const int value = th16_smoke_c(values[0] + values[1]);
    printf("%s: %d\n", text, value);
    return value == 42 && position.z == 3.0f ? 0 : 2;
}
