// UCRT functions that are defined inline in the CRT headers, with C linkage.
// The original kept one out-of-line copy of each, in the object file that
// first used it; each copy is annotated, by linker symbol, in the file that
// provides it here (Supervisor.cpp, PosVel.cpp, GameErrorContext.cpp,
// AsciiManager.cpp), because the definitions live in the SDK headers.
