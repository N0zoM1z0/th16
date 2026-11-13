#pragma once

// Base of the game's task objects (AsciiInf, BombInf, TitleInf). The name is
// ZUN's, from RTTI. It has no virtual functions: each task class introduces
// its own vftable, so RTTI places this base after the vptr (displacement 4).
class TaskInf
{
};
