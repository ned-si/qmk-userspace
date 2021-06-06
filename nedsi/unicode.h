#pragma once
#include "quantum.h"

// clang-format off
#define FOREACH_UNICODE(M) \
    M(e__ACUT,   0x00E9)\
    M(E__ACUT__U,    0x00C9)\
    M(u__ACUT,   0x00F9)\
    M(U__ACUT__U,    0x00D9)\
    M(a__GRAV,   0x00E0)\
    M(A__GRAV__U,    0x00C0)\
    M(e__GRAV,   0x00E8)\
    M(E__GRAV__U,    0x00C8)\
    M(u__GRAV,   0x00F9)\
    M(U__GRAV__U,    0x00D9)\
    M(a__CIRC,   0x00E2)\
    M(A__CIRC__U,    0x00C2)\
    M(e__CIRC,   0x00EA)\
    M(E__CIRC__U,    0x00CA)\
    M(i__CIRC,   0x00EE)\
    M(I__CIRC__U,    0x00CE)\
    M(o__CIRC,   0x00F4)\
    M(O__CIRC__U,    0x00D4)\
    M(u__CIRC,   0x00FB)\
    M(U__CIRC__U,    0x00DB)\
    M(i__UML,    0x00EF)\
    M(I__UML__U, 0x00CF)\
    M(o__UML,   0x00F6)\
    M(O__UML__U, 0x00DC)\
    M(c__CDIL,   0x00E7)\
    M(C__CDIL__U,    0x00C7)\
    M(DED__CIR,  0x0302)\
    M(DED__UML,  0x0308)\
    M(DEGREE,    0x00B0)
// clang-format on

#define UC_KEYCODE(name, code)  name = UC(code),        // LALP = UC(0x03B1),

#define UCM_NAME(name, code)    UCM_ ## name,           // UCM_LALP,
#define UCM_ENTRY(name, code)   [UCM_ ## name] = code,  // [UCM_LALP] = 0x03B1,
#define UCM_KEYCODE(name, code) name = X(UCM_ ## name), // LALP = X(UCM_LALP)

#if defined(UNICODE_ENABLE)
enum unicode_keycodes {
    FOREACH_UNICODE(UC_KEYCODE)
};
#elif defined(UNICODEMAP_ENABLE)
enum unicode_names {
    FOREACH_UNICODE(UCM_NAME)
};

extern const uint32_t PROGMEM unicode_map[];

enum unicode_keycodes {
    FOREACH_UNICODE(UCM_KEYCODE)
};
#endif


#define E_ACUTE XP(e__ACUT, E__ACUT__U)
#define U_ACUTE XP(u__ACUT, U__ACUT__U)
#define A_GRAVE XP(a__GRAV, A__GRAV__U)
#define E_GRAVE XP(e__GRAV, E__GRAV__U)
#define U_GRAVE XP(u__GRAV, U__GRAV__U)
#define A_CIRCU XP(a__CIRC, A__CIRC__U)
#define E_CIRCU XP(e__CIRC, E__CIRC__U)
#define I_CIRCU XP(i__CIRC, I__CIRC__U)
#define O_CIRCU XP(o__CIRC, O__CIRC__U)
#define U_CIRCU XP(u__CIRC, U__CIRC__U)
#define I_UMLAU XP(i__UML ,  I__UML__U)
#define O_UMLAU XP(o__UML ,  O__UML__U)
#define C_CDILA XP(c__CDIL, C__CDIL__U)
#define DED_CIR X(DED__CIR)
#define DED_UML X(DED__UML)
#define DEGR X(DEGREE)
