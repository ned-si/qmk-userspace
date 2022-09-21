#include "combos.h"
#include "action_tapping.h"

uint8_t mod_state;

enum combo_events {
    JK,
    JL,
    MCOMMA,
    COMMADOT,
    FD,
    FS,
    CV,
    COMBO_LENGTH
};


int COMBO_LEN = COMBO_LENGTH;

const uint16_t PROGMEM J_K_COMBO[] = {HOME_J, HOME_K, COMBO_END};
const uint16_t PROGMEM J_L_COMBO[] = {HOME_J, HOME_L, COMBO_END};
const uint16_t PROGMEM M_COMMA_COMBO[] = {KC_M, KC_COMMA, COMBO_END};
const uint16_t PROGMEM COMMA_DOT_COMBO[] = {KC_COMMA, KC_DOT, COMBO_END};
const uint16_t PROGMEM F_D_COMBO[] = {HOME_F, HOME_D, COMBO_END};
const uint16_t PROGMEM F_S_COMBO[] = {HOME_F, HOME_S, COMBO_END};
const uint16_t PROGMEM C_V_COMBO[] = {KC_C, KC_V, COMBO_END};

combo_t key_combos[] = {
    [JK] = COMBO_ACTION(J_K_COMBO),
    [JL] = COMBO_ACTION(J_L_COMBO),
    [MCOMMA] = COMBO_ACTION(M_COMMA_COMBO),
    [COMMADOT] = COMBO_ACTION(COMMA_DOT_COMBO),
    [FD] = COMBO_ACTION(F_D_COMBO),
    [FS] = COMBO_ACTION(F_S_COMBO),
    [CV] = COMBO_ACTION(C_V_COMBO),
};


void process_combo_event(uint16_t combo_index, bool pressed) {
    // Process mod-taps before the combo is fired,
    // this helps making modifier-aware combos,
    // like UY_PRN or SPCN_NOT, more fluid
    // when I use them with home row mods.
    action_tapping_process((keyrecord_t){});
    mod_state = get_mods();
    switch(combo_index) {
        case JK:
            if (pressed) {
                tap_code16(KC_BSPC);
            }
        break;

        case JL:
            if (pressed) {
                tap_code16(KC_DEL);
            }
        break;

        case MCOMMA:
            if (pressed) {
                tap_code16(KC_QUOT);
            }
        break;

        case COMMADOT:
            if (pressed) {
                tap_code16(KC_ENT);
            }
        break;

        case FD:
            if (pressed) {
                tap_code16(KC_ESC);
            }
        break;

        case FS:
            if (pressed) {
                tap_code16(CAPSWRD);
            }
        break;

        case CV:
            if (pressed) {
                tap_code16(KC_MINS);
            }
        break;
    }
};
