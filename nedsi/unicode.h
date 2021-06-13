#pragma once
#include "quantum.h"

// clang-format off
#define FOREACH_UNICODE(M) \
    M(DED__CIR,  0x0302)\
    M(DED__UML,  0x0308)\
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


#define DED_CIR X(DED__CIR)
#define DED_UML X(DED__UML)
